import grpc
from concurrent import futures
import time

from protos import trip_request_pb2_grpc, trip_request_pb2

# In-memory store
trip_requests = {}

class TripRequestService(trip_request_pb2_grpc.TripRequestServiceServicer):

    def CreateTripRequest(self, request, context):
        if request.id in trip_requests:
            return trip_requests[request.id]  # idempotent
        trip_requests[request.id] = request
        print(f"Created TripRequest {request.id}")
        return request

    def CancelTripRequest(self, request, context):
        if request.id in trip_requests:
            req = trip_requests[request.id]
            req.status = trip_request_pb2.CANCELLED
            print(f"Cancelled TripRequest {request.id}")
            return req
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("TripRequest not found")
        return trip_request_pb2.TripRequest()

    def GetTripRequest(self, request, context):
        return trip_requests.get(request.id, trip_request_pb2.TripRequest())


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trip_request_pb2_grpc.add_TripRequestServiceServicer_to_server(TripRequestService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("TripRequestService running on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
