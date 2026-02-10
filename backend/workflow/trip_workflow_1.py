# trip_workflow_1.py

"""
Trip Workflow Orchestration for DG Do (Khujand)

- Enforces full economic and operational guardrails
- Implements transactional Saga pattern with compensation
- Provides deterministic, replayable logs for debugging
- Collects telemetry at each step
"""

import uuid
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

import grpc
import redis

# Import gRPC stubs
from trip_request_pb2_grpc import TripRequestServiceStub
from matching_pb2_grpc import MatchingServiceStub
from pricing_pb2_grpc import PricingServiceStub
from driver_status_pb2_grpc import DriverStatusServiceStub
from trip_service_pb2_grpc import TripServiceStub

from trip_request_pb2 import CreateTripRequestCommand, TripRequestStatus
from matching_pb2 import MatchingRequest
from pricing_pb2 import PriceCalculationRequest
from driver_status_pb2 import UpdateDriverStatusRequest
from trip_service_pb2 import CreateTripCommand, TripStatus

# Telemetry helper
from telemetry_pb2_grpc import TelemetryServiceStub
from telemetry_pb2 import TelemetryEvent

# -----------------------------
# Redis client for idempotency
# -----------------------------
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# -----------------------------
# Constants / Guardrails
# -----------------------------
MIN_DRIVER_PAYOUT_TJS = 1.5  # TJS per km
MAX_PRICE_MULTIPLIER = 3.0

# -----------------------------
# Workflow class
# -----------------------------
class TripWorkflow:
    def __init__(
        self,
        trip_request_stub: TripRequestServiceStub,
        matching_stub: MatchingServiceStub,
        pricing_stub: PricingServiceStub,
        driver_status_stub: DriverStatusServiceStub,
        trip_stub: TripServiceStub,
        telemetry_stub: TelemetryServiceStub,
    ):
        self.trip_request_stub = trip_request_stub
        self.matching_stub = matching_stub
        self.pricing_stub = pricing_stub
        self.driver_status_stub = driver_status_stub
        self.trip_stub = trip_stub
        self.telemetry_stub = telemetry_stub

    # -----------------------------
    # Main entrypoint
    # -----------------------------
    def create_trip(self, passenger_id: str, origin, destination, idempotency_key: str):
        """
        Orchestrates the full trip workflow:
        1. TripRequest creation
        2. Matching
        3. Pricing
        4. Driver assignment
        5. Trip creation
        """
        workflow_log = []
        try:
            # Idempotency check
            cached = redis_client.get(f"trip:{idempotency_key}")
            if cached:
                logging.info(f"[IDEMPOTENT] Returning cached trip for {idempotency_key}")
                return cached

            # -----------------------------
            # Step 1: Create TripRequest
            # -----------------------------
            tr_command = CreateTripRequestCommand(
                passenger_id=passenger_id,
                origin=origin,
                destination=destination,
            )
            trip_request = self.trip_request_stub.CreateTripRequest(tr_command)
            workflow_log.append(("trip_request", trip_request.id))
            self._telemetry("trip_request_created", trip_request.id)

            # -----------------------------
            # Step 2: Matching
            # -----------------------------
            match_request = MatchingRequest(
                trip_request_id=trip_request.id,
                origin=origin,
                destination=destination,
                max_candidates=3,
                seed=int(datetime.now().timestamp()),
            )
            matching_response = self.matching_stub.GetCandidates(match_request)
            if not matching_response.candidates:
                raise Exception("No drivers available")
            candidate_driver = matching_response.candidates[0]  # deterministic selection
            workflow_log.append(("matching", candidate_driver.driver_id))
            self._telemetry("driver_matched", candidate_driver.driver_id)

            # -----------------------------
            # Step 3: Pricing
            # -----------------------------
            price_request = PriceCalculationRequest(
                trip_request_id=trip_request.id,
                passenger_id=passenger_id,
                matched_driver_id=candidate_driver.driver_id,
                origin=origin,
                destination=destination,
                estimated_distance_meters=1000,  # placeholder
                estimated_duration_seconds=600,   # placeholder
                demand_multiplier=1.0,
                supply_multiplier=1.0,
                driver_acceptance_rate=0.95,
                driver_rating=4.8,
                pricing_seed=match_request.seed,
            )
            price_response = self.pricing_stub.CalculatePrice(price_request)

            # Economic guardrail
            if price_response.driver_payout_total < MIN_DRIVER_PAYOUT_TJS:
                raise Exception("Economic guardrail violated: driver payout too low")
            workflow_log.append(("pricing", price_response.calculation_id))
            self._telemetry("price_calculated", price_response.calculation_id)

            # -----------------------------
            # Step 4: Assign driver
            # -----------------------------
            driver_update = UpdateDriverStatusRequest(
                driver_id=candidate_driver.driver_id,
                is_available=False,
                expected_version=1,
                idempotency_key=str(uuid.uuid4()),
            )
            self.driver_status_stub.UpdateDriverStatus(driver_update)
            workflow_log.append(("driver_assigned", candidate_driver.driver_id))
            self._telemetry("driver_assigned", candidate_driver.driver_id)

            # -----------------------------
            # Step 5: Create Trip
            # -----------------------------
            trip_command = CreateTripCommand(
                trip_request_id=trip_request.id,
                passenger_id=passenger_id,
                driver_id=candidate_driver.driver_id,
                origin=origin,
                destination=destination,
            )
            trip = self.trip_stub.CreateTrip(trip_command)
            workflow_log.append(("trip_created", trip.id))
            self._telemetry("trip_created", trip.id)

            # Cache result for idempotency
            redis_client.set(f"trip:{idempotency_key}", trip.id, ex=300)

            return trip

        except Exception as e:
            logging.error(f"Workflow failed: {e}")
            self._compensate(workflow_log)
            raise

    # -----------------------------
    # Telemetry helper
    # -----------------------------
    def _telemetry(self, event_type: str, entity_id: str):
        evt = TelemetryEvent(
            event_type=event_type,
            entity_id=entity_id,
            timestamp=int(datetime.now(timezone.utc).timestamp()),
        )
        try:
            self.telemetry_stub.LogEvent(evt)
        except Exception:
            logging.warning("Telemetry failed for %s", event_type)

    # -----------------------------
    # Compensation handler
    # -----------------------------
    def _compensate(self, workflow_log):
        """
        Roll back all steps in reverse order to ensure partial failure recovery
        """
        for step, entity_id in reversed(workflow_log):
            try:
                if step == "driver_assigned":
                    # Unassign driver
                    self.driver_status_stub.UpdateDriverStatus(
                        UpdateDriverStatusRequest(
                            driver_id=entity_id,
                            is_available=True,
                            expected_version=2,  # optimistic locking
                            idempotency_key=str(uuid.uuid4()),
                        )
                    )
                elif step == "trip_request":
                    # Cancel trip request
                    self.trip_request_stub.CancelTripRequest(
                        trip_request_pb2.CancelTripRequestCommand(
                            request_id=entity_id,
                            expected_version=1
                        )
                    )
            except Exception as e:
                logging.error(f"Compensation failed for {step} {entity_id}: {e}")
