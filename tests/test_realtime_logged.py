import sys
import os
import grpc
import json
import time
import random
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
# Production-style logging setup
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # JSON will handle formatting
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
def to_timestamp(dt):
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts

def simulate_driver_movement(origin, destination, steps=5):
    """Simulate driver moving from origin to destination in steps"""
    lat_step = (destination.lat - origin.lat) / steps
    lon_step = (destination.lon - origin.lon) / steps
    positions = []
    for i in range(1, steps+1):
        positions.append(Location(lat=origin.lat + lat_step*i, lon=origin.lon + lon_step*i))
    return positions

# -----------------------------
# Real-time end-to-end simulation
# -----------------------------
def run_realtime_simulation():
    # Connect to gRPC servers
    trip_request_stub = TripRequestServiceStub(grpc.insecure_channel("localhost:50052"))
    matching_stub = MatchingServiceStub(grpc.insecure_channel("localhost:50051"))
    trip_stub = TripServiceStub(grpc.insecure_channel("localhost:50053"))

    # -----------------------------
    # 1. Create TripRequest
    # -----------------------------
    create_req = CreateTripRequestCommand(
        passenger_id="passenger_1",
        origin=Location(lat=39.6, lon=67.8),
        destination=Location(lat=39.65, lon=67.85)
    )
    trip_request = trip_request_stub.CreateTripRequest(create_req)
    log_event("TripRequestCreated", {"trip_request_id": trip_request.id, "passenger_id": trip_request.passenger_id})

    # -----------------------------
    # 2. Matching
    # -----------------------------
    seed = 42
    match_req = MatchingRequest(
        trip_request_id=trip_request.id,
        origin_lat=trip_request.origin.lat,
        origin_lon=trip_request.origin.lon,
        dest_lat=trip_request.destination.lat,
        dest_lon=trip_request.destination.lon,
        max_candidates=3,
        seed=seed
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
        passenger_id=trip_request.passenger_id,
        driver_id=assigned_driver,
        origin=trip_request.origin,
        destination=trip_request.destination
    )
    trip = trip_stub.CreateTrip(create_trip_cmd)
    log_event("TripCreated", {"trip_id": trip.id, "trip_request_id": trip.trip_request_id, "driver_id": trip.driver_id})

    # -----------------------------
    # 4. Real-time FSM simulation
    # -----------------------------
    fsm_sequence = [TripStatus.EN_ROUTE, TripStatus.COMPLETED]
    positions = simulate_driver_movement(trip.origin, trip.destination, steps=len(fsm_sequence))
    for status, pos in zip(fsm_sequence, positions):
        time.sleep(2)  # simulate real-time progress
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
    # 5. Dynamic cancellation simulation
    # -----------------------------
    create_req2 = CreateTripRequestCommand(
        passenger_id="passenger_2",
        origin=Location(lat=39.7, lon=67.9),
        destination=Location(lat=39.75, lon=67.95)
    )
    trip_request2 = trip_request_stub.CreateTripRequest(create_req2)
    log_event("TripRequestCreated", {"trip_request_id": trip_request2.id, "passenger_id": trip_request2.passenger_id})

    match_req2 = MatchingRequest(
        trip_request_id=trip_request2.id,
        origin_lat=trip_request2.origin.lat,
        origin_lon=trip_request2.origin.lon,
        dest_lat=trip_request2.destination.lat,
        dest_lon=trip_request2.destination.lon,
        max_candidates=2,
        seed=seed
    )
    match_res2 = matching_stub.GetCandidates(match_req2)
    if not match_res2.candidates:
        log_event("NoDriversAvailable", {"trip_request_id": trip_request2.id})
        return
    assigned_driver2 = match_res2.candidates[0].driver_id

    create_trip_cmd2 = CreateTripCommand(
        trip_request_id=trip_request2.id,
        passenger_id=trip_request2.passenger_id,
        driver_id=assigned_driver2,
        origin=trip_request2.origin,
        destination=trip_request2.destination
    )
    trip2 = trip_stub.CreateTrip(create_trip_cmd2)
    log_event("TripCreated", {"trip_id": trip2.id, "trip_request_id": trip2.trip_request_id, "driver_id": trip2.driver_id})

    # Cancel after a short delay
    time.sleep(3)
    cancel_cmd2 = CancelTripCommand(
        trip_id=trip2.id,
        reason=TripStatus.CANCELLED,
        expected_version=trip2.version
    )
    trip2 = trip_stub.CancelTrip(cancel_cmd2)
    log_event("TripCancelled", {"trip_id": trip2.id, "trip_request_id": trip2.trip_request_id, "status": trip2.status})

if __name__ == "__main__":
    run_realtime_simulation()
