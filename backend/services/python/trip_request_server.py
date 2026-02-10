# trip_request_server.py

import grpc
from concurrent import futures
import uuid
from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

from trip_request_pb2_grpc import (
    TripRequestServiceServicer,
    add_TripRequestServiceServicer_to_server,
)
from trip_request_pb2 import (
    TripRequest,
    TripRequestStatus,
    CreateTripRequestCommand,
    CancelTripRequestCommand,
    GetTripRequestById,
)

# -----------------------------
# In-memory store (DEV ONLY)
# -----------------------------
trip_requests = {}

# -----------------------------
# Helpers
# -----------------------------
def now_ts() -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(datetime.utcnow())
    return ts

# -----------------------------
# Service implementation
# -----------------------------
class TripRequestService(TripRequestServiceServicer):

    def CreateTripRequest(self, request: CreateTripRequestCommand, context):
        # Idempotency: only 1 OPEN request per passenger
        for tr in trip_requests.values():
            if tr.passenger_id == request.passenger_id and tr.status == TripRequestStatus.OPEN:
                return tr

        trip_request_id = str(uuid.uuid4())

        trip_request = TripRequest(
            id=trip_request_id,
            passenger_id=request.passenger_id,
            origin=request.origin,
            destination=request.destination,
            status=TripRequestStatus.OPEN,
            version=1,
            created_at=now_ts(),
            updated_at=now_ts(),
        )

        trip_requests[trip_request_id] = trip_request
        print(f"[CREATE] TripRequest {trip_request_id}")
        return trip_request

    def CancelTripRequest(self, request: CancelTripRequestCommand, context):
        tr = trip_requests.get(request.request_id)
        if not tr:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("TripRequest not found")
            return TripRequest()

        tr.status = TripRequestStatus.CANCELLED
        tr.version += 1
        tr.updated_at.CopyFrom(now_ts())

        print(f"[CANCEL] TripRequest {request.request_id}")
        return tr

    def GetTripRequest(self, request: GetTripRequestById, context):
        tr = trip_requests.get(request.request_id)
        if not tr:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("TripRequest not found")
            return TripRequest()
        return tr

# -----------------------------
# Server
# -----------------------------
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TripRequestServiceServicer_to_server(TripRequestService(), server)

    port = server.add_insecure_port("0.0.0.0:50052")
    if port == 0:
        raise RuntimeError("Failed to bind port 50052")

    server.start()
    print("✅ TripRequestService running on port 50052")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
