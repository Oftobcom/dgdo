import sys
import os
import grpc
import json
import time
import random
import threading
from datetime import datetime
from collections import defaultdict

# -----------------------------
# Add generated Python modules to path
# -----------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

from trip_request_pb2_grpc import TripRequestServiceStub
from trip_request_pb2 import CreateTripRequestCommand

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
# Global driver state
# -----------------------------
driver_locations = {}
driver_lock = threading.Lock()

# Initialize a fleet of drivers (driver_id -> Location)
fleet_size = 5
for i in range(fleet_size):
    driver_id = f"driver_{i+1}"
    driver_locations[driver_id] = Location(
        lat=39.6 + random.random() * 0.1,
        lon=67.8 + random.random() * 0.1
    )

# -----------------------------
# Helper functions
# -----------------------------
def distance(loc1, loc2):
    """Approximate Euclidean distance"""
    return ((loc1.lat - loc2.lat)**2 + (loc1.lon - loc2.lon)**2) ** 0.5

def assign_driver_nearest(trip_origin):
    """Pick the nearest available driver"""
    with driver_lock:
        nearest_driver = None
        min_dist = float("inf")
        for driver_id, loc in driver_locations.items():
            d = distance(loc, trip_origin)
            if d < min_dist:
                min_dist = d
                nearest_driver = driver_id
        return nearest_driver

def simulate_driver_movement(driver_id, path, steps=5):
    """Move driver along path in steps"""
    with driver_lock:
        lat_step = (path.lat - driver_locations[driver_id].lat) / steps
        lon_step = (path.lon - driver_locations[driver_id].lon) / steps
        positions = []
        for i in range(1, steps+1):
            positions.append(Location(
                lat=driver_locations[driver_id].lat + lat_step*i,
                lon=driver_locations[driver_id].lon + lon_step*i
            ))
        driver_locations[driver_id] = positions[-1]  # update final position
    return positions

# -----------------------------
# Trip simulation
# -----------------------------
def run_single_trip(passenger_id, trip_request_stub, matching_stub, trip_stub):
    # Create TripRequest
    origin = Location(lat=39.6 + random.random()*0.1, lon=67.8 + random.random()*0.1)
    destination = Location(lat=origin.lat + 0.05, lon=origin.lon + 0.05)
    create_req = CreateTripRequestCommand(
        passenger_id=passenger_id,
        origin=origin,
        destination=destination
    )
    trip_request = trip_request_stub.CreateTripRequest(create_req)
    log_event("TripRequestCreated", {"trip_request_id": trip_request.id, "passenger_id": passenger_id})

    # Matching (pick nearest driver)
    assigned_driver = assign_driver_nearest(trip_request.origin)
    if not assigned_driver:
        log_event("NoDriversAvailable", {"trip_request_id": trip_request.id})
        return

    log_event("DriverAssigned", {"trip_request_id": trip_request.id, "driver_id": assigned_driver})

    # Create Trip
    create_trip_cmd = CreateTripCommand(
        trip_request_id=trip_request.id,
        passenger_id=passenger_id,
        driver_id=assigned_driver,
        origin=trip_request.origin,
        destination=trip_request.destination
    )
    trip = trip_stub.CreateTrip(create_trip_cmd)
    log_event("TripCreated", {"trip_id": trip.id, "driver_id": assigned_driver})

    # FSM simulation
    fsm_sequence = [TripStatus.EN_ROUTE, TripStatus.COMPLETED]
    for status in fsm_sequence:
        time.sleep(random.uniform(0.5, 2.0))
        positions = simulate_driver_movement(assigned_driver, trip.destination, steps=3)
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
                "driver_position": {"lat": positions[-1].lat, "lon": positions[-1].lon}
            })
        except grpc.RpcError as e:
            log_event("FSMError", {"trip_id": trip.id, "error": e.details()})

    # Random cancellation
    if random.random() < 0.2:
        time.sleep(random.uniform(0.2, 1.0))
        cancel_cmd = CancelTripCommand(
            trip_id=trip.id,
            reason=TripStatus.CANCELLED,
            expected_version=trip.version
        )
        trip = trip_stub.CancelTrip(cancel_cmd)
        log_event("TripCancelled", {"trip_id": trip.id, "driver_id": assigned_driver})

# -----------------------------
# Run multiple concurrent trips
# -----------------------------
def run_fleet_simulation(num_trips=10):
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
        time.sleep(random.uniform(0.1, 0.5))  # staggered creation

    for t in threads:
        t.join()

if __name__ == "__main__":
    run_fleet_simulation(num_trips=15)
