import grpc
from concurrent import futures
from protos import trip_pb2_grpc, trip_pb2

trips = {}

class TripService(trip_pb2_grpc.TripServiceServicer):

    def CreateTrip(self, request, context):
        if request.id in trips:
            return trips[request.id]
        trips[request.id] = request
        print(f"Trip created: {request.id}")
        return request

    def UpdateTripStatus(self, request, context):
        if request.id in trips:
            trips[request.id].status = request.status
            return trips[request.id]
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return trip_pb2.Trip()

    def GetTrip(self, request, context):
        return trips.get(request.id, trip_pb2.Trip())

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trip_pb2_grpc.add_TripServiceServicer_to_server(TripService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("TripService running on port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
