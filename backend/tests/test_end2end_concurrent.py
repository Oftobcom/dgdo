import sys
import os
import grpc
import random
import threading
import time
from datetime import datetime
from math import sqrt
from google.protobuf.timestamp_pb2 import Timestamp

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
from matching_pb2 import DriverProbability

from trip_service_pb2_grpc import TripServiceStub
from trip_service_pb2 import (
    CreateTripCommand,
    UpdateTripStatusCommand,
    CancelTripCommand,
    GetTripByIdRequest,
    GetTripByRequestIdRequest,
    TripStatus,
)
from common_pb2 import Location

# -----------------------------
# Configuration
# -----------------------------
TRIP_REQUEST_SERVICE_ADDR = "localhost:50052"
MATCHING_SERVICE_ADDR = "localhost:50051"
TRIP_SERVICE_ADDR = "localhost:50053"

SEED = 42
random.seed(SEED)

NUM_CONCURRENT_REQUESTS = 5
MAX_CANDIDATES = 3

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
def distance(lat1, lon1, lat2, lon2):
    return sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

def simulate_driver_movement(driver, dest_lat, dest_lon, step=0.001):
    # Move driver slightly toward destination
    if abs(driver["lat"] - dest_lat) > step:
        driver["lat"] += step if driver["lat"] < dest_lat else -step
    if abs(driver["lon"] - dest_lon) > step:
        driver["lon"] += step if driver["lon"] < dest_lon else -step

def match_drivers(origin_lat, origin_lon):
    candidates = []
    for driver in drivers:
        prob = max(0.0, 1.0 - distance(origin_lat, origin_lon, driver["lat"], driver["lon"]))
        candidates.append(DriverProbability(driver_id=driver["driver_id"], probability=prob))
    candidates.sort(key=lambda d: d.probability, reverse=True)
    return candidates[:MAX_CANDIDATES]

# -----------------------------
# Worker function for each trip
# -----------------------------
def simulate_trip(trip_number):
    tr_channel = grpc.insecure_channel(TRIP_REQUEST_SERVICE_ADDR)
    tr_stub = TripRequestServiceStub(tr_channel)

    match_channel = grpc.insecure_channel(MATCHING_SERVICE_ADDR)
    match_stub = MatchingServiceStub(match_channel)

    trip_channel = grpc.insecure_channel(TRIP_SERVICE_ADDR)
    trip_stub = TripServiceStub(trip_channel)

    # -----------------------------
    # Create Trip Request
    # -----------------------------
    origin_lat = 39.6 + 0.01 * trip_number
    origin_lon = 67.8 + 0.01 * trip_number
    dest_lat = origin_lat + 0.05
    dest_lon = origin_lon + 0.05

    trip_request_cmd = CreateTripRequestCommand(
        passenger_id=f"passenger_{trip_number+1}",
        origin=Location(lat=origin_lat, lon=origin_lon),
        destination=Location(lat=dest_lat, lon=dest_lon),
    )
    trip_request = tr_stub.CreateTripRequest(trip_request_cmd)
    print(f"[Trip {trip_number}] ✅ TripRequest created: {trip_request.id}")

    # -----------------------------
    # Matching
    # -----------------------------
    matched_candidates = match_drivers(trip_request.origin.lat, trip_request.origin.lon)
    if not matched_candidates:
        print(f"[Trip {trip_number}] ❌ No drivers available")
        return
    driver_id = matched_candidates[0].driver_id
    print(f"[Trip {trip_number}] 🔍 Matched driver: {driver_id}")

    # -----------------------------
    # Create Trip
    # -----------------------------
    create_trip_cmd = CreateTripCommand(
        trip_request_id=trip_request.id,
        passenger_id=trip_request.passenger_id,
        driver_id=driver_id,
        origin=trip_request.origin,
        destination=trip_request.destination,
    )
    trip = trip_stub.CreateTrip(create_trip_cmd)
    print(f"[Trip {trip_number}] 🚗 Trip created: {trip.id}")

    # -----------------------------
    # FSM Updates
    # -----------------------------
    for new_status in [TripStatus.EN_ROUTE, TripStatus.COMPLETED]:
        simulate_driver_movement(
            next(d for d in drivers if d["driver_id"] == driver_id),
            trip.destination.lat,
            trip.destination.lon,
        )
        update_cmd = UpdateTripStatusCommand(
            trip_id=trip.id,
            new_status=new_status,
            expected_version=trip.version,
        )
        trip = trip_stub.UpdateTripStatus(update_cmd)
        print(f"[Trip {trip_number}] 🔄 Status updated to {TripStatus.Name(new_status)}")

    # -----------------------------
    # Cancel Trip (if even number)
    # -----------------------------
    if trip_number % 2 == 0:
        cancel_cmd = CancelTripCommand(
            trip_id=trip.id,
            reason=TripStatus.CANCELLED,
            expected_version=trip.version,
        )
        trip = trip_stub.CancelTrip(cancel_cmd)
        print(f"[Trip {trip_number}] ❌ Trip cancelled")

# -----------------------------
# Run multiple concurrent trips
# -----------------------------
def run_concurrent_trips():
    threads = []
    for i in range(NUM_CONCURRENT_REQUESTS):
        t = threading.Thread(target=simulate_trip, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    run_concurrent_trips()
