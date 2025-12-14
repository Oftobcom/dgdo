import grpc
from concurrent import futures
from protos import ml_feedback_pb2_grpc, ml_feedback_pb2

feedback_store = []

class MLFeedbackService(ml_feedback_pb2_grpc.MLFeedbackServiceServicer):

    def SendFeedback(self, request, context):
        feedback_store.append(request)
        print(f"ML Feedback received for TripRequest {request.trip_request_id}")
        return request

    def GetTrainingBatch(self, request, context):
        for f in feedback_store:
            yield f

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ml_feedback_pb2_grpc.add_MLFeedbackServiceServicer_to_server(MLFeedbackService(), server)
    server.add_insecure_port('[::]:50055')
    server.start()
    print("MLFeedbackService running on port 50055")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
