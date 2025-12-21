import sys
import os
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

# -----------------------------
# Add generated Python modules to path
# -----------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

from trip_service_pb2_grpc import TripServiceStub
from trip_service_pb2 import (
    CreateTripCommand,
    UpdateTripStatusCommand,
    CancelTripCommand,
    GetTripByIdRequest,
    GetTripByRequestIdRequest,
)
from trip_pb2 import TripStatus
from common_pb2 import Location

# -----------------------------
# Helper to print trips
# -----------------------------
def print_trip(title, trip):
    print(f"\n=== {title} ===")
    print(f"ID: {trip.id}")
    print(f"TripRequest ID: {trip.trip_request_id}")
    print(f"Passenger: {trip.passenger_id}, Driver: {trip.driver_id}")
    print(f"Origin: ({trip.origin.lat}, {trip.origin.lon})")
    print(f"Destination: ({trip.destination.lat}, {trip.destination.lon})")
    print(f"Status: {TripStatus.Name(trip.status)}")
    print(f"Version: {trip.version}")
    print(f"Created: {trip.created_at.ToDatetime() if trip.created_at else 'N/A'}")
    print(f"Updated: {trip.updated_at.ToDatetime() if trip.updated_at else 'N/A'}")

# -----------------------------
# Test function
# -----------------------------
def test_trip_service():
    # Connect to TripService gRPC server
    channel = grpc.insecure_channel("localhost:50053")
    stub = TripServiceStub(channel)

    # -----------------------------
    # 1. Create Trip
    # -----------------------------
    create_cmd = CreateTripCommand(
        trip_request_id="req_001",
        passenger_id="passenger_1",
        driver_id="driver_1",
        origin=Location(lat=39.6, lon=67.8),
        destination=Location(lat=39.65, lon=67.85),
    )
    trip = stub.CreateTrip(create_cmd)
    print_trip("Created Trip", trip)

    # -----------------------------
    # 2. Get Trip by ID
    # -----------------------------
    fetched_by_id = stub.GetTripById(GetTripByIdRequest(trip_id=trip.id))
    print_trip("Fetched by ID", fetched_by_id)

    # -----------------------------
    # 3. Get Trip by TripRequest ID
    # -----------------------------
    fetched_by_request = stub.GetTripByRequestId(GetTripByRequestIdRequest(trip_request_id=trip.trip_request_id))
    print_trip("Fetched by TripRequest ID", fetched_by_request)

    # -----------------------------
    # 4. Update Trip: ACCEPTED -> EN_ROUTE
    # -----------------------------
    update_cmd = UpdateTripStatusCommand(
        trip_id=trip.id,
        new_status=TripStatus.EN_ROUTE,
        expected_version=trip.version
    )
    trip = stub.UpdateTripStatus(update_cmd)
    print_trip("Updated Trip status to EN_ROUTE", trip)

    # -----------------------------
    # 5. Update Trip: EN_ROUTE -> COMPLETED
    # -----------------------------
    update_cmd = UpdateTripStatusCommand(
        trip_id=trip.id,
        new_status=TripStatus.COMPLETED,
        expected_version=trip.version
    )
    trip = stub.UpdateTripStatus(update_cmd)
    print_trip("Updated Trip status to COMPLETED", trip)

    # -----------------------------
    # 6. Invalid FSM transition: COMPLETED -> ACCEPTED
    # -----------------------------
    try:
        invalid_update_cmd = UpdateTripStatusCommand(
            trip_id=trip.id,
            new_status=TripStatus.ACCEPTED,
            expected_version=trip.version
        )
        stub.UpdateTripStatus(invalid_update_cmd)
    except grpc.RpcError as e:
        print("\n❌ Invalid FSM transition error:")
        print(e.code(), e.details())

    # -----------------------------
    # 7. Create and cancel a second trip
    # -----------------------------
    create_cmd2 = CreateTripCommand(
        trip_request_id="req_002",
        passenger_id="passenger_2",
        driver_id="driver_2",
        origin=Location(lat=39.7, lon=67.9),
        destination=Location(lat=39.75, lon=67.95),
    )
    trip2 = stub.CreateTrip(create_cmd2)
    print_trip("Created Trip 2", trip2)

    cancel_cmd = CancelTripCommand(
        trip_id=trip2.id,
        reason=TripStatus.CANCELLED,
        expected_version=trip2.version
    )
    trip2 = stub.CancelTrip(cancel_cmd)
    print_trip("Cancelled Trip 2", trip2)


# -----------------------------
# Run test
# -----------------------------
if __name__ == "__main__":
    test_trip_service()
