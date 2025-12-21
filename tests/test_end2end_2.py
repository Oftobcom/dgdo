import sys
import os
import grpc
import random
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from math import sqrt

# -----------------------------
# Add generated Python modules to path
# -----------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

# -----------------------------
# Import services
# -----------------------------
from trip_request_pb2_grpc import TripRequestServiceStub
from trip_request_pb2 import CreateTripRequestCommand, TripRequestStatus

from matching_pb2_grpc import MatchingServiceStub
from matching_pb2 import MatchingRequest, DriverProbability

from trip_service_pb2_grpc import TripServiceStub
from trip_service_pb2 import CreateTripCommand, UpdateTripStatusCommand, CancelTripCommand, GetTripByIdRequest, GetTripByRequestIdRequest, TripStatus

from common_pb2 import Location

# -----------------------------
# Configuration
# -----------------------------
TRIP_REQUEST_SERVICE_ADDR = "localhost:50052"
MATCHING_SERVICE_ADDR = "localhost:50051"
TRIP_SERVICE_ADDR = "localhost:50053"

SEED = 42
random.seed(SEED)

# -----------------------------
# Simulated driver pool
# -----------------------------
drivers = [
    {"driver_id": f"driver_{i+1}", "lat": 39.6 + random.uniform(-0.01, 0.01), "lon": 67.8 + random.uniform(-0.01, 0.01)}
    for i in range(5)
]

# -----------------------------
# Helper functions
# -----------------------------
def datetime_to_timestamp(dt: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts

def distance(lat1, lon1, lat2, lon2):
    return sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def simulate_driver_movement(driver, dest_lat, dest_lon, step=0.001):
    # Move driver slightly toward destination
    if abs(driver["lat"] - dest_lat) > step:
        driver["lat"] += step if driver["lat"] < dest_lat else -step
    if abs(driver["lon"] - dest_lon) > step:
        driver["lon"] += step if driver["lon"] < dest_lon else -step

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
    # 2. Matching simulation
    # -----------------------------
    def match_drivers(origin_lat, origin_lon, max_candidates=3):
        candidates = []
        for driver in drivers:
            # probability inversely proportional to distance
            prob = max(0.0, 1.0 - distance(origin_lat, origin_lon, driver["lat"], driver["lon"]))
            candidates.append(DriverProbability(driver_id=driver["driver_id"], probability=prob))
        # Sort by probability
        candidates.sort(key=lambda d: d.probability, reverse=True)
        return candidates[:max_candidates]

    matched_candidates = match_drivers(trip_request.origin.lat, trip_request.origin.lon)
    print("\n🔍 Matched candidates:")
    for c in matched_candidates:
        print(f"Driver: {c.driver_id}, probability: {c.probability:.3f}")

    if not matched_candidates:
        print("No drivers available. Exiting.")
        return

    # Pick the best driver
    driver_id = matched_candidates[0].driver_id

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
    # 4. FSM updates with driver movement
    # -----------------------------
    fsm_transitions = [TripStatus.EN_ROUTE, TripStatus.COMPLETED]
    for new_status in fsm_transitions:
        # Simulate driver moving toward destination
        simulate_driver_movement(
            next(d for d in drivers if d["driver_id"] == driver_id),
            trip.destination.lat,
            trip.destination.lon
        )
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
        print("\n❌ Invalid FSM transition caught:")
        print(e.code(), e.details())

    # -----------------------------
    # 6. Create and cancel another trip
    # -----------------------------
    trip_request_cmd2 = CreateTripRequestCommand(
        passenger_id="passenger_2",
        origin=Location(lat=39.7, lon=67.9),
        destination=Location(lat=39.75, lon=67.95)
    )
    trip_request2 = tr_stub.CreateTripRequest(trip_request_cmd2)
    print("\n✅ TripRequest 2 created:", trip_request2)

    matched_candidates2 = match_drivers(trip_request2.origin.lat, trip_request2.origin.lon)
    if not matched_candidates2:
        print("No drivers available for TripRequest 2. Exiting.")
        return

    driver_id2 = matched_candidates2[0].driver_id
    create_trip_cmd2 = CreateTripCommand(
        trip_request_id=trip_request2.id,
        passenger_id=trip_request2.passenger_id,
        driver_id=driver_id2,
        origin=trip_request2.origin,
        destination=trip_request2.destination
    )
    trip2 = trip_stub.CreateTrip(create_trip_cmd2)
    print("\n🚗 Trip 2 created:", trip2)

    cancel_cmd = CancelTripCommand(
        trip_id=trip2.id,
        reason=TripStatus.CANCELLED,
        expected_version=trip2.version
    )
    trip2 = trip_stub.CancelTrip(cancel_cmd)
    print("\n❌ Trip 2 cancelled:", trip2)

    # -----------------------------
    # 7. Fetch trips
    # -----------------------------
    fetched_trip = trip_stub.GetTripById(GetTripByIdRequest(trip_id=trip.id))
    print("\n🔍 Fetched Trip by ID:", fetched_trip)

    fetched_trip_req = trip_stub.GetTripByRequestId(GetTripByRequestIdRequest(trip_request_id=trip_request.id))
    print("\n🔍 Fetched Trip by TripRequest ID:", fetched_trip_req)


if __name__ == "__main__":
    test_end_to_end()
