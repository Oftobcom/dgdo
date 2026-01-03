# trip_server.py

import grpc
from concurrent import futures
import uuid
from datetime import datetime
from threading import Lock

from google.protobuf.timestamp_pb2 import Timestamp

from trip_service_pb2_grpc import TripServiceServicer, add_TripServiceServicer_to_server
from trip_service_pb2 import CreateTripCommand, UpdateTripStatusCommand, CancelTripCommand, GetTripByIdRequest, GetTripByRequestIdRequest
from trip_pb2 import Trip, TripStatus
from common_pb2 import Location

from pricing_pb2_grpc import PricingServiceStub
from pricing_pb2 import PriceCalculationRequest

# -----------------------------
# In-memory store
# -----------------------------
trips = {}
trips_lock = Lock()

# -----------------------------
# FSM transitions
# -----------------------------
FSM = {
    TripStatus.ACCEPTED: [TripStatus.EN_ROUTE, TripStatus.CANCELLED, TripStatus.CANCELLED_BY_DRIVER],
    TripStatus.EN_ROUTE: [TripStatus.COMPLETED, TripStatus.CANCELLED_BY_DRIVER],
    TripStatus.COMPLETED: [],
    TripStatus.CANCELLED: [],
    TripStatus.CANCELLED_BY_DRIVER: [],
}

# -----------------------------
# Helpers
# -----------------------------
def now_timestamp():
    ts = Timestamp()
    ts.FromDatetime(datetime.utcnow())
    return ts

def valid_fsm_transition(current_status, new_status):
    return new_status in FSM.get(current_status, [])

# -----------------------------
# TripService
# -----------------------------
class TripService(TripServiceServicer):

    def __init__(self, pricing_channel):
        self.pricing_stub = PricingServiceStub(pricing_channel)

    def CreateTrip(self, request: CreateTripCommand, context):
        with trips_lock:
            # Idempotency check
            for t in trips.values():
                if t.trip_request_id == request.trip_request_id:
                    return t

        # -----------------------------
        # Call PricingService
        # -----------------------------
        pricing_request = PriceCalculationRequest(
            trip_request_id=request.trip_request_id,
            passenger_id=request.passenger_id,
            matched_driver_id=request.driver_id,
            origin=request.origin,
            destination=request.destination,
            estimated_distance_meters=10000,  # placeholder for routing
            estimated_duration_seconds=900,   # placeholder
            demand_multiplier=1.0,
            supply_multiplier=1.0,
            pricing_seed=uuid.uuid4().int & (1<<32)-1,
        )

        try:
            pricing_resp = self.pricing_stub.CalculatePrice(pricing_request)
        except grpc.RpcError as e:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("Pricing failed, cannot create trip")
            return Trip()

        # -----------------------------
        # Positive unit economics enforced
        # -----------------------------
        if pricing_resp.driver_payout_total <= 0 or pricing_resp.passenger_fare_total <= pricing_resp.driver_payout_total:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("Trip pricing violates unit economics")
            return Trip()

        # -----------------------------
        # Create trip
        # -----------------------------
        with trips_lock:
            trip_id = str(uuid.uuid4())
            trip = Trip(
                id=trip_id,
                trip_request_id=request.trip_request_id,
                passenger_id=request.passenger_id,
                driver_id=request.driver_id,
                origin=request.origin,
                destination=request.destination,
                status=TripStatus.ACCEPTED,
                version=1,
                created_at=now_timestamp(),
                updated_at=now_timestamp(),
            )
            trips[trip_id] = trip

        print(f"[{datetime.utcnow()}] Created Trip {trip_id} with fare {pricing_resp.passenger_fare_total}")
        return trip

    # Remaining methods are same as before (GetTripById, UpdateTripStatus, CancelTrip)
    def GetTripById(self, request, context):
        with trips_lock:
            trip = trips.get(request.trip_id)
        if not trip:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Trip not found")
            return Trip()
        return trip

    def GetTripByRequestId(self, request, context):
        with trips_lock:
            for t in trips.values():
                if t.trip_request_id == request.trip_request_id:
                    return t
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Trip not found")
        return Trip()

    def UpdateTripStatus(self, request, context):
        with trips_lock:
            trip = trips.get(request.trip_id)
            if not trip:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Trip not found")
                return Trip()
            if trip.version != request.expected_version:
                context.set_code(grpc.StatusCode.ABORTED)
                context.set_details("Version mismatch")
                return Trip()
            if not valid_fsm_transition(trip.status, request.new_status):
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Invalid FSM transition")
                return Trip()
            trip.status = request.new_status
            trip.version += 1
            trip.updated_at.CopyFrom(now_timestamp())
        return trip

    def CancelTrip(self, request, context):
        with trips_lock:
            trip = trips.get(request.trip_id)
            if not trip:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Trip not found")
                return Trip()
            if trip.version != request.expected_version:
                context.set_code(grpc.StatusCode.ABORTED)
                context.set_details("Version mismatch")
                return Trip()
            trip.status = request.reason
            trip.version += 1
            trip.updated_at.CopyFrom(now_timestamp())
        return trip

# -----------------------------
# Server setup
# -----------------------------
def serve():
    channel = grpc.insecure_channel("localhost:50056")  # PricingService channel
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TripServiceServicer_to_server(TripService(channel), server)
    server.add_insecure_port("[::]:50053")
    server.start()
    print("TripService running on port 50053")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
