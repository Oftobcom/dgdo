# trip_workflow_4.py 
# (Khujand-ready, multi-market, driver rollback, surge pricing)
import uuid
import logging
from datetime import datetime, time
from contextlib import contextmanager
import random

import redis
import grpc
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# gRPC stubs
from trip_request_pb2_grpc import TripRequestServiceStub
from matching_pb2_grpc import MatchingServiceStub
from pricing_pb2_grpc import PricingServiceStub
from driver_status_pb2_grpc import DriverStatusServiceStub
from trip_service_pb2_grpc import TripServiceStub

from trip_request_pb2 import CreateTripRequestCommand, CancelTripRequestCommand
from matching_pb2 import MatchingRequest
from pricing_pb2 import PriceCalculationRequest
from trip_service_pb2 import CreateTripCommand
from driver_status_pb2 import UpdateDriverStatusCommand
from common_pb2 import Location

# ----------------------------
# Redis for idempotency and replay
# ----------------------------
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# ----------------------------
# Telemetry
# ----------------------------
def log_telemetry(event_type: str, entity_id: str, metadata: dict):
    logging.info(f"[TELEMETRY] {event_type} | {entity_id} | {metadata}")

# ----------------------------
# Economic guardrails
# ----------------------------
def check_economics(passenger_fare: float, driver_payout: float, op_cost: float):
    if passenger_fare < driver_payout + op_cost:
        raise ValueError("Economic guardrail violation: fare < driver payout + operational cost")

# ----------------------------
# Circuit breaker / timeout
# ----------------------------
@contextmanager
def grpc_call_with_timeout(timeout_seconds=2):
    try:
        yield timeout_seconds
    except grpc.RpcError as e:
        raise RuntimeError(f"gRPC call failed: {e}")

# ----------------------------
# Retry decorator
# ----------------------------
retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0.5),
    retry=retry_if_exception_type(RuntimeError)
)

# ----------------------------
# Time-based surge for Khujand
# ----------------------------
def get_time_multiplier():
    now = datetime.utcnow().time()
    peak_morning = (time(7,0), time(9,0))
    peak_evening = (time(17,0), time(19,0))
    night = (time(23,0), time(5,0))
    
    if peak_morning[0] <= now <= peak_morning[1] or peak_evening[0] <= now <= peak_evening[1]:
        return 1.5
    if now >= night[0] or now <= night[1]:
        return 1.2
    return 1.0

# ----------------------------
# Trip Workflow Orchestration
# ----------------------------
class TripWorkflow:
    def __init__(self, trip_request_stub: TripRequestServiceStub,
                       matching_stub: MatchingServiceStub,
                       pricing_stub: PricingServiceStub,
                       driver_status_stub: DriverStatusServiceStub,
                       trip_stub: TripServiceStub,
                       market: str = "khujand"):
        self.trip_request_stub = trip_request_stub
        self.matching_stub = matching_stub
        self.pricing_stub = pricing_stub
        self.driver_status_stub = driver_status_stub
        self.trip_stub = trip_stub
        self.market = market

    @retry_policy
    def create_trip(self, passenger_id: str, origin: Location, destination: Location, ab_test_group: str = None):
        """
        Full trip creation workflow with:
        - Idempotency
        - Economic guardrails
        - Multi-market pricing & A/B testing
        - Driver status assignment with rollback
        - Time-based surge multiplier
        - Telemetry
        """
        workflow_id = f"trip_workflow:{self.market}:{passenger_id}:{origin.lat}:{origin.lon}:{destination.lat}:{destination.lon}"

        # Idempotency
        if redis_client.exists(workflow_id):
            logging.info(f"[IDEMPOTENCY] Returning cached trip")
            return redis_client.get(workflow_id)

        driver_assigned = None
        trip_request = None
        trip = None

        try:
            # ----------------------------
            # Step 1: Create TripRequest
            # ----------------------------
            with grpc_call_with_timeout():
                tr_cmd = CreateTripRequestCommand(passenger_id=passenger_id, origin=origin, destination=destination)
                trip_request = self.trip_request_stub.CreateTripRequest(tr_cmd)
                log_telemetry("TripRequestCreated", trip_request.id, {"passenger_id": passenger_id})

            # ----------------------------
            # Step 2: Matching
            # ----------------------------
            with grpc_call_with_timeout():
                match_req = MatchingRequest(
                    trip_request_id=trip_request.id,
                    origin=origin,
                    destination=destination,
                    max_candidates=5,
                    seed=int(datetime.utcnow().timestamp())
                )
                match_resp = self.matching_stub.GetCandidates(match_req)
                if not match_resp.candidates:
                    raise RuntimeError("No drivers available")
                driver_assigned = match_resp.candidates[0].driver_id
                log_telemetry("DriverAssignedCandidate", trip_request.id, {"driver_id": driver_assigned})

            # ----------------------------
            # Step 3: Pricing with time & A/B multiplier
            # ----------------------------
            surge_multiplier = get_time_multiplier()
            if ab_test_group == "B":
                surge_multiplier *= 0.9  # Example A/B variant

            with grpc_call_with_timeout():
                pricing_req = PriceCalculationRequest(
                    trip_request_id=trip_request.id,
                    passenger_id=passenger_id,
                    matched_driver_id=driver_assigned,
                    origin=origin,
                    destination=destination,
                    estimated_distance_meters=1000,
                    estimated_duration_seconds=600,
                    demand_multiplier=surge_multiplier,
                    supply_multiplier=1.0,
                    driver_acceptance_rate=1.0,
                    driver_rating=5.0,
                    pricing_seed=int(datetime.utcnow().timestamp())
                )
                pricing_resp = self.pricing_stub.CalculatePrice(pricing_req)
                check_economics(pricing_resp.passenger_fare_total,
                                pricing_resp.driver_payout_total,
                                op_cost=50)
                log_telemetry("PriceCalculated", trip_request.id,
                              {"passenger_fare": pricing_resp.passenger_fare_total,
                               "driver_payout": pricing_resp.driver_payout_total,
                               "surge_multiplier": surge_multiplier})

            # ----------------------------
            # Step 4: Driver Status Update (assignment)
            # ----------------------------
            with grpc_call_with_timeout():
                self.driver_status_stub.UpdateDriverStatus(UpdateDriverStatusCommand(
                    driver_id=driver_assigned,
                    status="ASSIGNED"
                ))
                log_telemetry("DriverStatusUpdated", trip_request.id, {"driver_id": driver_assigned})

            # ----------------------------
            # Step 5: Create Trip
            # ----------------------------
            with grpc_call_with_timeout():
                create_trip_cmd = CreateTripCommand(
                    trip_request_id=trip_request.id,
                    passenger_id=passenger_id,
                    driver_id=driver_assigned,
                    origin=origin,
                    destination=destination
                )
                trip = self.trip_stub.CreateTrip(create_trip_cmd)
                log_telemetry("TripCreated", trip.id, {"trip_request_id": trip_request.id})

            # Persist workflow result for idempotency & replay
            redis_client.set(workflow_id, trip.id, ex=3600)
            return trip

        except Exception as e:
            logging.error(f"TripWorkflow failed: {e}")

            # ----------------------------
            # Compensation
            # ----------------------------
            try:
                if trip_request:
                    self.trip_request_stub.CancelTripRequest(
                        CancelTripRequestCommand(
                            request_id=trip_request.id,
                            expected_version=trip_request.version
                        )
                    )
                    log_telemetry("TripRequestCancelled", trip_request.id, {"reason": str(e)})
            except Exception as ce:
                logging.error(f"TripRequest compensation failed: {ce}")

            try:
                if driver_assigned:
                    self.driver_status_stub.UpdateDriverStatus(UpdateDriverStatusCommand(
                        driver_id=driver_assigned,
                        status="AVAILABLE"
                    ))
                    log_telemetry("DriverUnassigned", trip_request.id, {"driver_id": driver_assigned})
            except Exception as ce:
                logging.error(f"DriverStatus compensation failed: {ce}")

            raise e
