import sys
import os
import grpc
from datetime import datetime

# -----------------------------
# Add generated Python modules to path
# -----------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

from trip_request_pb2_grpc import TripRequestServiceStub
from trip_request_pb2 import CreateTripRequestCommand, CancelTripRequestCommand, GetTripRequestById, TripRequestStatus
from common_pb2 import Location

# -----------------------------
# Test function
# -----------------------------
def test_trip_request_service():
    # Connect to the TripRequestService gRPC server
    channel = grpc.insecure_channel("localhost:50052")
    stub = TripRequestServiceStub(channel)

    # -----------------------------
    # 1. Create a TripRequest
    # -----------------------------
    create_cmd = CreateTripRequestCommand(
        passenger_id="passenger_1",
        origin=Location(lat=39.6, lon=67.8),
        destination=Location(lat=39.65, lon=67.85)
    )

    trip_request = stub.CreateTripRequest(create_cmd)
    print("✅ Created TripRequest:")
    print(trip_request)

    # -----------------------------
    # 2. Get the TripRequest by ID
    # -----------------------------
    get_cmd = GetTripRequestById(request_id=trip_request.id)
    fetched_request = stub.GetTripRequest(get_cmd)
    print("\n🔍 Fetched TripRequest by ID:")
    print(fetched_request)

    # -----------------------------
    # 3. Cancel the TripRequest
    # -----------------------------
    cancel_cmd = CancelTripRequestCommand(
        request_id=trip_request.id,
        expected_version=trip_request.version
    )
    cancelled_request = stub.CancelTripRequest(cancel_cmd)
    print("\n❌ Cancelled TripRequest:")
    print(cancelled_request)

    # -----------------------------
    # 4. Try to fetch cancelled TripRequest
    # -----------------------------
    fetched_after_cancel = stub.GetTripRequest(get_cmd)
    print("\n🔍 Fetched after cancellation:")
    print(fetched_after_cancel)

# -----------------------------
# Run test
# -----------------------------
if __name__ == "__main__":
    test_trip_request_service()
