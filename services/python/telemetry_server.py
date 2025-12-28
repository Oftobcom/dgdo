# telemetry_server.py

import grpc
from concurrent import futures
from protos import telemetry_pb2_grpc, telemetry_pb2

events = []

class TelemetryService(telemetry_pb2_grpc.TelemetryServiceServicer):

    def LogEvent(self, request, context):
        events.append(request)
        print(f"Telemetry logged: {request.event_type} for {request.entity_id}")
        return request

    def QueryMetrics(self, request, context):
        for e in events:
            yield e

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(TelemetryService(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    print("TelemetryService running on port 50054")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
