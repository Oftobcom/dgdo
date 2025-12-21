import sys
import os
import grpc
import random
from datetime import datetime

# Add generated Python modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

from matching_pb2 import MatchingRequest
from matching_pb2_grpc import MatchingServiceStub
from common_pb2 import Location

# -----------------------------
# Simulated driver pool
# -----------------------------
SIMULATED_DRIVERS = [
    {"driver_id": "driver_1", "location": Location(lat=39.6, lon=67.8)},
    {"driver_id": "driver_2", "location": Location(lat=39.61, lon=67.81)},
    {"driver_id": "driver_3", "location": Location(lat=39.62, lon=67.82)},
    {"driver_id": "driver_4", "location": Location(lat=39.63, lon=67.83)},
    {"driver_id": "driver_5", "location": Location(lat=39.64, lon=67.84)},
]

def generate_deterministic_candidates(max_candidates: int, seed: int):
    """
    Generate deterministic candidate drivers from the simulated pool.
    """
    random.seed(seed)
    drivers = SIMULATED_DRIVERS.copy()
    random.shuffle(drivers)
    candidates = drivers[:max_candidates]

    # Assign normalized probabilities
    prob = 1.0 / max_candidates if max_candidates > 0 else 0
    for driver in candidates:
        driver["probability"] = prob
    return candidates

def test_matching():
    # Connect to gRPC server
    channel = grpc.insecure_channel("localhost:50051")
    stub = MatchingServiceStub(channel)

    # -----------------------------
    # Example MatchingRequest
    # -----------------------------
    request = MatchingRequest(
        trip_request_id="trip_req_123",
        origin=Location(lat=39.6, lon=67.8),
        destination=Location(lat=39.65, lon=67.85),
        max_candidates=3,
        seed=42
    )

    # -----------------------------
    # Simulate deterministic matching locally
    # -----------------------------
    candidates = generate_deterministic_candidates(request.max_candidates, request.seed)

    print(f"[{datetime.now()}] TripRequest ID: {request.trip_request_id}")
    print("Simulated Matching Candidates (deterministic):")
    for c in candidates:
        print(f"Driver ID: {c['driver_id']}, Probability: {c['probability']:.2f}, "
              f"Location: ({c['location'].lat}, {c['location'].lon})")

    # -----------------------------
    # Call actual MatchingService gRPC
    # -----------------------------
    try:
        response = stub.GetCandidates(request)
        print("\n[From gRPC server] Matching Response:")
        if not response.candidates:
            print("No candidates returned. Reason code:", response.reason_code)
        for candidate in response.candidates:
            print(f"Driver ID: {candidate.driver_id}, "
                  f"Probability: {candidate.probability:.2f}")
        if response.reason_code:
            print("Reason code:", response.reason_code)
    except grpc.RpcError as e:
        print("gRPC Error:", e)

if __name__ == "__main__":
    test_matching()
