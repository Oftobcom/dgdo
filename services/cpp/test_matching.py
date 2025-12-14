import sys
import os

# Add generated Python modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../generated/python"))

from matching_pb2 import MatchTripRequestCommand, DriverProbability, MatchDistribution
from matching_pb2_grpc import MatchingServiceStub
import grpc

def test_matching():
    # Connect to the gRPC server
    channel = grpc.insecure_channel("localhost:50051")
    stub = MatchingServiceStub(channel)

    # Example request (you can fill the TripRequest as needed)
    request = MatchTripRequestCommand(
        max_candidates=5
    )

    response = stub.MatchTripRequest(request)
    print("Matching result:", response)

if __name__ == "__main__":
    test_matching()
