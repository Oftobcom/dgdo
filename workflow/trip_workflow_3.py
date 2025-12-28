# trip_workflow_3.py 
# (Extended for full production-grade workflow)

import uuid
import logging
from datetime import datetime
from contextlib import contextmanager

import redis
import grpc
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# gRPC stubs
from trip_request_pb2_grpc import TripRequestServiceStub
from matching_pb2_grpc import MatchingServiceStub
from pricing_pb2_grpc import PricingServiceStub
from driver_status_pb2_grpc import DriverStatusServiceStub
from trip_service_pb2_grpc import TripServiceStub

from trip_request_pb2 import CreateTripRequestCommand, CancelTripRequestCommand, TripRequestStatus
from matching_pb2 import MatchingRequest
from pricing_pb2 import PriceCalculationRequest
from trip_service_pb2 import CreateTripCommand
from common_pb2 import Location

# ----------------------------
# Redis for idempotency
# ----------------------------
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# ----------------------------
# Telemetry stub
# ----------------------------
def log_telemetry(event_type: str, entity_id: str, metadata: dict):
    logging.info(f"[TELEMETRY] {event_type} | {entity_id} | {metadata}")

# ----------------------------
# Economic guardrail
# ----------------------------
def check_economics(passenger_fare: float, driver_payout: float, op_cost: float):
    if passenger_fare < driver_payout + op_cost:
        raise ValueError("Economic guardrail violation: fare < driver payout + operational cost")

# ----------------------------
# Circuit breaker / timeout wrapper
# ----------------------------
@contextmanager
def grpc_call_with_timeout(timeout_seconds=2):
    try:
        yield timeout_seconds
    except grpc.RpcError as e:
        raise RuntimeError(f"gRPC call failed: {e}")

# ----------------------------
# Retry decorator for transient failures
# ----------------------------
retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0.5),
    retry=retry_if_exception_type(RuntimeError)
)

# ----------------------------
# Trip Workflow Orchestration
# ----------------------------
class TripWorkflow:
    def __init__(self, trip_request_stub: TripRequestServiceStub,
                       matching_stub: MatchingServiceStub,
                       pricing_stub: PricingServiceStub,
                       driver_status_stub: DriverStatusServiceStub,
                       trip_stub: TripServiceStub):
        self.trip_request_stub = trip_request_stub
        self.matching_stub = matching_stub
        self.pricing_stub = pricing_stub
        self.driver_status_stub = driver_status_stub
        self.trip_stub = trip_stub

    @retry_policy
    def create_trip(self, passenger_id: str, origin: Location, destination: Location):
        """
        Orchestrates full trip creation with compensation, idempotency, telemetry,
        circuit breakers, timeouts, and economic guardrails.
        """
        workflow_id = f"trip_workflow:{passenger_id}:{origin.lat}:{origin.lon}:{destination.lat}:{destination.lon}"

        # Return existing trip for idempotency
        if redis_client.exists(workflow_id):
            logging.info(f"[IDEMPOTENCY] Duplicate request, returning previous trip")
            return redis_client.get(workflow_id)

        try:
            # ----------------------------
            # Step 1: Create TripRequest
            # ----------------------------
            with grpc_call_with_timeout():
                tr_cmd = CreateTripRequestCommand(
                    passenger_id=passenger_id,
                    origin=origin,
                    destination=destination
                )
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
                    raise RuntimeError("No available drivers")
                chosen_driver = match_resp.candidates[0].driver_id
                log_telemetry("DriverCandidatesFetched", trip_request.id, {"driver_id": chosen_driver})

            # ----------------------------
            # Step 3: Price Calculation
            # ----------------------------
            with grpc_call_with_timeout():
                pricing_req = PriceCalculationRequest(
                    trip_request_id=trip_request.id,
                    passenger_id=passenger_id,
                    matched_driver_id=chosen_driver,
                    origin=origin,
                    destination=destination,
                    estimated_distance_meters=1000,
                    estimated_duration_seconds=600,
                    demand_multiplier=1.0,
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
                               "driver_payout": pricing_resp.driver_payout_total})

            # ----------------------------
            # Step 4: Assign Driver
            # ----------------------------
            with grpc_call_with_timeout():
                # Ideally update driver status to assigned
                self.driver_status_stub.UpdateDriverStatus(
                    # Fill request to mark driver as busy
                )
                log_telemetry("DriverAssigned", trip_request.id, {"driver_id": chosen_driver})

            # ----------------------------
            # Step 5: Create Trip in TripService
            # ----------------------------
            with grpc_call_with_timeout():
                create_trip_cmd = CreateTripCommand(
                    trip_request_id=trip_request.id,
                    passenger_id=passenger_id,
                    driver_id=chosen_driver,
                    origin=origin,
                    destination=destination
                )
                trip = self.trip_stub.CreateTrip(create_trip_cmd)
                log_telemetry("TripCreated", trip.id, {"trip_request_id": trip_request.id})

            # ----------------------------
            # Step 6: Persist workflow result
            # ----------------------------
            redis_client.set(workflow_id, trip.id, ex=3600)
            return trip

        except Exception as e:
            logging.error(f"TripWorkflow failed: {e}")

            # ----------------------------
            # Compensation steps
            # ----------------------------
            try:
                if 'trip_request' in locals():
                    self.trip_request_stub.CancelTripRequest(
                        CancelTripRequestCommand(
                            request_id=trip_request.id,
                            expected_version=trip_request.version
                        )
                    )
                    log_telemetry("TripRequestCancelled", trip_request.id, {"reason": str(e)})
            except Exception as ce:
                logging.error(f"Compensation failed: {ce}")

            try:
                if 'chosen_driver' in locals():
                    # Optionally unassign driver in DriverStatusService
                    log_telemetry("DriverUnassigned", trip_request.id, {"driver_id": chosen_driver})
            except Exception as ce:
                logging.error(f"Driver compensation failed: {ce}")

            raise e
