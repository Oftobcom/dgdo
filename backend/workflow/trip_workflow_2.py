# trip_workflow.py

import uuid
import logging
from datetime import datetime, timedelta

# gRPC clients (stubs) for your services
from trip_request_pb2_grpc import TripRequestServiceStub
from matching_pb2_grpc import MatchingServiceStub
from pricing_pb2_grpc import PricingServiceStub
from driver_status_pb2_grpc import DriverStatusServiceStub
from trip_service_pb2_grpc import TripServiceStub

# Protobuf messages
from trip_request_pb2 import CreateTripRequestCommand, TripRequestStatus
from matching_pb2 import MatchingRequest
from pricing_pb2 import PriceCalculationRequest
from trip_service_pb2 import CreateTripCommand
from common_pb2 import Location

# Redis or similar for idempotency
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Telemetry function (stub)
def log_telemetry(event_type: str, entity_id: str, metadata: dict):
    logging.info(f"[TELEMETRY] {event_type} | {entity_id} | {metadata}")

# Economic guardrail function
def check_economics(passenger_fare: float, driver_payout: float, op_cost: float):
    if passenger_fare < driver_payout + op_cost:
        raise ValueError("Economic guardrail violation: fare < driver payout + cost")

# ----------------------------
# Orchestration
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

    def create_trip(self, passenger_id: str, origin: Location, destination: Location):
        """
        Orchestrates a full trip creation with compensation and telemetry.
        """
        # Idempotency key for this workflow
        workflow_id = f"trip_workflow:{passenger_id}:{origin.lat}:{origin.lon}:{destination.lat}:{destination.lon}"
        if redis_client.exists(workflow_id):
            logging.info(f"Duplicate request detected, returning previous result")
            return redis_client.get(workflow_id)

        try:
            # ----------------------------
            # Step 1: Create TripRequest
            # ----------------------------
            tr_cmd = CreateTripRequestCommand(passenger_id=passenger_id,
                                             origin=origin,
                                             destination=destination)
            trip_request = self.trip_request_stub.CreateTripRequest(tr_cmd)
            log_telemetry("TripRequestCreated", trip_request.id, {"passenger_id": passenger_id})

            # ----------------------------
            # Step 2: Get Matching Candidates
            # ----------------------------
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
            # Step 3: Calculate Price
            # ----------------------------
            pricing_req = PriceCalculationRequest(
                trip_request_id=trip_request.id,
                passenger_id=passenger_id,
                matched_driver_id=chosen_driver,
                origin=origin,
                destination=destination,
                estimated_distance_meters=1000,  # replace with actual routing
                estimated_duration_seconds=600,   # replace with actual routing
                demand_multiplier=1.0,
                supply_multiplier=1.0,
                driver_acceptance_rate=1.0,
                driver_rating=5.0,
                pricing_seed=int(datetime.utcnow().timestamp())
            )
            pricing_resp = self.pricing_stub.CalculatePrice(pricing_req)
            check_economics(pricing_resp.passenger_fare_total,
                            pricing_resp.driver_payout_total,
                            op_cost=50)  # placeholder operational cost
            log_telemetry("PriceCalculated", trip_request.id,
                          {"passenger_fare": pricing_resp.passenger_fare_total,
                           "driver_payout": pricing_resp.driver_payout_total})

            # ----------------------------
            # Step 4: Assign Driver (DriverStatus)
            # ----------------------------
            # Here you would call driver_status_stub to mark driver as assigned
            # e.g., self.driver_status_stub.AssignDriver(...)
            log_telemetry("DriverAssigned", trip_request.id, {"driver_id": chosen_driver})

            # ----------------------------
            # Step 5: Create Trip in TripService
            # ----------------------------
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
            # Step 6: Store workflow result for idempotency
            # ----------------------------
            redis_client.set(workflow_id, trip.id, ex=3600)  # expire in 1 hour

            return trip

        except Exception as e:
            logging.error(f"TripWorkflow failed: {e}")

            # ----------------------------
            # Compensation logic
            # ----------------------------
            try:
                # Cancel TripRequest
                if 'trip_request' in locals():
                    self.trip_request_stub.CancelTripRequest(
                        trip_request_pb2.CancelTripRequestCommand(
                            request_id=trip_request.id,
                            expected_version=trip_request.version
                        )
                    )
                    log_telemetry("TripRequestCancelled", trip_request.id, {"reason": str(e)})
            except Exception as ce:
                logging.error(f"Compensation failed: {ce}")

            raise e
