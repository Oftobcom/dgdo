import sys
import os
import grpc
import random
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# -----------------------------
# Add generated Python modules to path
# -----------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

# -----------------------------
# Import services
# -----------------------------
from trip_request_pb2_grpc import TripRequestServiceStub
from trip_request_pb2 import CreateTripRequestCommand, CancelTripRequestCommand, GetTripRequestById, TripRequestStatus

from matching_pb2_grpc import MatchingServiceStub
from matching_pb2 import MatchingRequest

from trip_service_pb2_grpc import TripServiceStub
from trip_service_pb2 import CreateTripCommand, UpdateTripStatusCommand, CancelTripCommand, GetTripByIdRequest, TripStatus

from common_pb2 import Location

# -----------------------------
# Configuration
# -----------------------------
TRIP_REQUEST_SERVICE_ADDR = "localhost:50052"
MATCHING_SERVICE_ADDR = "localhost:50051"
TRIP_SERVICE_ADDR = "localhost:50053"

SEED = 12345
random.seed(SEED)

# -----------------------------
# Helper: convert datetime to Timestamp
# -----------------------------
def datetime_to_timestamp(dt: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts

# -----------------------------
# End-to-end workflow
# -----------------------------
def test_end_to_end():
    # Connect to services
    tr_channel = grpc.insecure_channel(TRIP_REQUEST_SERVICE_ADDR)
    tr_stub = TripRequestServiceStub(tr_channel)

    match_channel = grpc.insecure_channel(MATCHING_SERVICE_ADDR)
    match_stub = MatchingServiceStub(match_channel)

    trip_channel = grpc.insecure_channel(TRIP_SERVICE_ADDR)
    trip_stub = TripServiceStub(trip_channel)

    # -----------------------------
    # 1. Create Trip Request
    # -----------------------------
    trip_request_cmd = CreateTripRequestCommand(
        passenger_id="passenger_1",
        origin=Location(lat=39.6, lon=67.8),
        destination=Location(lat=39.65, lon=67.85)
    )
    trip_request = tr_stub.CreateTripRequest(trip_request_cmd)
    print("✅ TripRequest created:", trip_request)

    # -----------------------------
    # 2. Call MatchingService
    # -----------------------------
    matching_cmd = MatchingRequest(
        trip_request_id=trip_request.id,
        origin_lat=trip_request.origin.lat,
        origin_lon=trip_request.origin.lon,
        dest_lat=trip_request.destination.lat,
        dest_lon=trip_request.destination.lon,
        max_candidates=3,
        seed=SEED
    )
    match_resp = match_stub.GetCandidates(matching_cmd)
    print("\n🔍 Matching candidates:")
    for c in match_resp.candidates:
        print(f"Driver: {c.driver_id}, probability: {c.probability}")

    if not match_resp.candidates:
        print("No drivers available. Exiting.")
        return

    # Pick the first candidate driver
    driver_id = match_resp.candidates[0].driver_id

    # -----------------------------
    # 3. Create Trip
    # -----------------------------
    create_trip_cmd = CreateTripCommand(
        trip_request_id=trip_request.id,
        passenger_id=trip_request.passenger_id,
        driver_id=driver_id,
        origin=trip_request.origin,
        destination=trip_request.destination
    )
    trip = trip_stub.CreateTrip(create_trip_cmd)
    print("\n🚗 Trip created:", trip)

    # -----------------------------
    # 4. FSM updates
    # -----------------------------
    fsm_transitions = [TripStatus.EN_ROUTE, TripStatus.COMPLETED]
    for new_status in fsm_transitions:
        update_cmd = UpdateTripStatusCommand(
            trip_id=trip.id,
            new_status=new_status,
            expected_version=trip.version
        )
        trip = trip_stub.UpdateTripStatus(update_cmd)
        print(f"\n🔄 Trip status updated to {TripStatus.Name(new_status)}:", trip)

    # -----------------------------
    # 5. Attempt invalid FSM transition
    # -----------------------------
    try:
        update_cmd = UpdateTripStatusCommand(
            trip_id=trip.id,
            new_status=TripStatus.ACCEPTED,
            expected_version=trip.version
        )
        trip = trip_stub.UpdateTripStatus(update_cmd)
    except grpc.RpcError as e:
        print("\n❌ Invalid FSM transition error caught:")
        print(e.code(), e.details())

    # -----------------------------
    # 6. Cancel a new TripRequest
    # -----------------------------
    trip_request_cmd2 = CreateTripRequestCommand(
        passenger_id="passenger_2",
        origin=Location(lat=39.7, lon=67.9),
        destination=Location(lat=39.75, lon=67.95)
    )
    trip_request2 = tr_stub.CreateTripRequest(trip_request_cmd2)
    print("\n✅ TripRequest 2 created:", trip_request2)

    # Create trip 2
    matching_cmd2 = MatchingRequest(
        trip_request_id=trip_request2.id,
        origin_lat=trip_request2.origin.lat,
        origin_lon=trip_request2.origin.lon,
        dest_lat=trip_request2.destination.lat,
        dest_lon=trip_request2.destination.lon,
        max_candidates=3,
        seed=SEED
    )
    match_resp2 = match_stub.GetCandidates(matching_cmd2)
    if not match_resp2.candidates:
        print("No drivers available for TripRequest 2. Exiting.")
        return

    driver_id2 = match_resp2.candidates[0].driver_id
    create_trip_cmd2 = CreateTripCommand(
        trip_request_id=trip_request2.id,
        passenger_id=trip_request2.passenger_id,
        driver_id=driver_id2,
        origin=trip_request2.origin,
        destination=trip_request2.destination
    )
    trip2 = trip_stub.CreateTrip(create_trip_cmd2)
    print("\n🚗 Trip 2 created:", trip2)

    # Cancel trip2
    cancel_cmd = CancelTripCommand(
        trip_id=trip2.id,
        reason=TripStatus.CANCELLED,
        expected_version=trip2.version
    )
    trip2 = trip_stub.CancelTrip(cancel_cmd)
    print("\n❌ Trip 2 cancelled:", trip2)

    # -----------------------------
    # 7. Fetch trips by ID and request_id
    # -----------------------------
    fetched_trip = trip_stub.GetTripById(GetTripByIdRequest(trip_id=trip.id))
    print("\n🔍 Fetched Trip by ID:", fetched_trip)

    fetched_trip_req = trip_stub.GetTripByRequestId(GetTripByRequestIdRequest(trip_request_id=trip_request.id))
    print("\n🔍 Fetched Trip by TripRequest ID:", fetched_trip_req)


if __name__ == "__main__":
    test_end_to_end()
