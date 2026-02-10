import sys
import os
import grpc
import json
import time
import random
import threading
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# -----------------------------
# Add generated Python modules to path
# -----------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

from trip_request_pb2_grpc import TripRequestServiceStub
from trip_request_pb2 import CreateTripRequestCommand, GetTripRequestById

from matching_pb2_grpc import MatchingServiceStub
from matching_pb2 import MatchingRequest

from trip_service_pb2_grpc import TripServiceStub
from trip_service_pb2 import CreateTripCommand, UpdateTripStatusCommand, CancelTripCommand
from trip_service_pb2 import TripStatus

from common_pb2 import Location

import logging
import sys

# -----------------------------
# Production-style logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DGDo")

def log_event(event_type, data):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "data": data
    }
    logger.info(json.dumps(log_entry))

# -----------------------------
# Helper functions
# -----------------------------
def simulate_driver_movement(origin, destination, steps=5):
    lat_step = (destination.lat - origin.lat) / steps
    lon_step = (destination.lon - origin.lon) / steps
    positions = []
    for i in range(1, steps+1):
        positions.append(Location(lat=origin.lat + lat_step*i, lon=origin.lon + lon_step*i))
    return positions

def run_single_trip(passenger_id, trip_request_stub, matching_stub, trip_stub):
    """Simulate a single trip from request → matching → trip creation → FSM → optional cancel"""
    # -----------------------------
    # 1. Create TripRequest
    # -----------------------------
    origin_lat = 39.6 + random.random() * 0.1
    origin_lon = 67.8 + random.random() * 0.1
    dest_lat = origin_lat + 0.05
    dest_lon = origin_lon + 0.05

    create_req = CreateTripRequestCommand(
        passenger_id=passenger_id,
        origin=Location(lat=origin_lat, lon=origin_lon),
        destination=Location(lat=dest_lat, lon=dest_lon)
    )
    trip_request = trip_request_stub.CreateTripRequest(create_req)
    log_event("TripRequestCreated", {"trip_request_id": trip_request.id, "passenger_id": passenger_id})

    # -----------------------------
    # 2. Matching
    # -----------------------------
    match_req = MatchingRequest(
        trip_request_id=trip_request.id,
        origin_lat=trip_request.origin.lat,
        origin_lon=trip_request.origin.lon,
        dest_lat=trip_request.destination.lat,
        dest_lon=trip_request.destination.lon,
        max_candidates=3,
        seed=random.randint(1, 1000)
    )
    match_res = matching_stub.GetCandidates(match_req)
    if not match_res.candidates:
        log_event("NoDriversAvailable", {"trip_request_id": trip_request.id})
        return
    assigned_driver = match_res.candidates[0].driver_id
    log_event("DriverAssigned", {"trip_request_id": trip_request.id, "driver_id": assigned_driver})

    # -----------------------------
    # 3. Create Trip
    # -----------------------------
    create_trip_cmd = CreateTripCommand(
        trip_request_id=trip_request.id,
        passenger_id=passenger_id,
        driver_id=assigned_driver,
        origin=trip_request.origin,
        destination=trip_request.destination
    )
    trip = trip_stub.CreateTrip(create_trip_cmd)
    log_event("TripCreated", {"trip_id": trip.id, "trip_request_id": trip.trip_request_id, "driver_id": trip.driver_id})

    # -----------------------------
    # 4. FSM simulation
    # -----------------------------
    fsm_sequence = [TripStatus.EN_ROUTE, TripStatus.COMPLETED]
    positions = simulate_driver_movement(trip.origin, trip.destination, steps=len(fsm_sequence))
    for status, pos in zip(fsm_sequence, positions):
        time.sleep(random.uniform(1.0, 3.0))  # random real-time step
        update_cmd = UpdateTripStatusCommand(
            trip_id=trip.id,
            new_status=status,
            expected_version=trip.version
        )
        try:
            trip = trip_stub.UpdateTripStatus(update_cmd)
            log_event("TripStatusUpdated", {
                "trip_id": trip.id,
                "new_status": trip.status,
                "version": trip.version,
                "driver_position": {"lat": pos.lat, "lon": pos.lon}
            })
        except grpc.RpcError as e:
            log_event("FSMError", {"trip_id": trip.id, "error": e.details()})

    # -----------------------------
    # 5. Random dynamic cancellation (simulate 30% chance)
    # -----------------------------
    if random.random() < 0.3:
        time.sleep(random.uniform(0.5, 2.0))
        cancel_cmd = CancelTripCommand(
            trip_id=trip.id,
            reason=TripStatus.CANCELLED,
            expected_version=trip.version
        )
        trip = trip_stub.CancelTrip(cancel_cmd)
        log_event("TripCancelled", {"trip_id": trip.id, "trip_request_id": trip.trip_request_id, "status": trip.status})

# -----------------------------
# Main simulation
# -----------------------------
def run_concurrent_trips(num_trips=5):
    trip_request_stub = TripRequestServiceStub(grpc.insecure_channel("localhost:50052"))
    matching_stub = MatchingServiceStub(grpc.insecure_channel("localhost:50051"))
    trip_stub = TripServiceStub(grpc.insecure_channel("localhost:50053"))

    threads = []
    for i in range(num_trips):
        t = threading.Thread(
            target=run_single_trip,
            args=(f"passenger_{i+1}", trip_request_stub, matching_stub, trip_stub)
        )
        threads.append(t)
        t.start()
        time.sleep(random.uniform(0.2, 0.5))  # stagger trip creation

    # Wait for all trips to complete
    for t in threads:
        t.join()

if __name__ == "__main__":
    run_concurrent_trips(num_trips=10)
