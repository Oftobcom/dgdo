import grpc
from concurrent import futures
import uuid
from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

from trip_service_pb2_grpc import TripServiceServicer, add_TripServiceServicer_to_server
from trip_service_pb2 import (
    CreateTripCommand,
    UpdateTripStatusCommand,
    CancelTripCommand,
    GetTripByIdRequest,
    GetTripByRequestIdRequest,
)
from trip_pb2 import Trip, TripStatus
from common_pb2 import Location

# -----------------------------
# In-memory store
# -----------------------------
trips = {}

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
    allowed = FSM.get(current_status, [])
    return new_status in allowed

# -----------------------------
# Service implementation
# -----------------------------
class TripService(TripServiceServicer):

    def CreateTrip(self, request: CreateTripCommand, context):
        # Idempotency: trip_request_id must be unique
        for t in trips.values():
            if t.trip_request_id == request.trip_request_id:
                return t

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
        print(f"[{datetime.utcnow()}] Created Trip {trip_id}")
        return trip

    def GetTripById(self, request: GetTripByIdRequest, context):
        trip = trips.get(request.trip_id)
        if not trip:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Trip not found")
            return Trip()
        return trip

    def GetTripByRequestId(self, request: GetTripByRequestIdRequest, context):
        for t in trips.values():
            if t.trip_request_id == request.trip_request_id:
                return t
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Trip not found")
        return Trip()

    def UpdateTripStatus(self, request: UpdateTripStatusCommand, context):
        trip = trips.get(request.trip_id)
        if not trip:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Trip not found")
            return Trip()

        # Optimistic locking
        if trip.version != request.expected_version:
            context.set_code(grpc.StatusCode.ABORTED)
            context.set_details(f"Version mismatch: expected {request.expected_version}, got {trip.version}")
            return Trip()

        # FSM validation
        if not valid_fsm_transition(trip.status, request.new_status):
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(f"Invalid FSM transition from {trip.status} to {request.new_status}")
            return Trip()

        # Update status
        trip.status = request.new_status
        trip.version += 1
        trip.updated_at.CopyFrom(now_timestamp())
        print(f"[{datetime.utcnow()}] Trip {trip.id} status updated to {trip.status}")
        return trip

    def CancelTrip(self, request: CancelTripCommand, context):
        trip = trips.get(request.trip_id)
        if not trip:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Trip not found")
            return Trip()

        # Optimistic locking
        if trip.version != request.expected_version:
            context.set_code(grpc.StatusCode.ABORTED)
            context.set_details(f"Version mismatch: expected {request.expected_version}, got {trip.version}")
            return Trip()

        # Cancel
        trip.status = request.reason
        trip.version += 1
        trip.updated_at.CopyFrom(now_timestamp())
        print(f"[{datetime.utcnow()}] Trip {trip.id} cancelled ({trip.status})")
        return trip

# -----------------------------
# Server setup
# -----------------------------
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TripServiceServicer_to_server(TripService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    print("TripService running on port 50053")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
