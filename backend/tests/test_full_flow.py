import grpc
from datetime import datetime
from protos import trip_request_pb2, trip_request_pb2_grpc
from protos import trip_pb2, trip_pb2_grpc
from protos import matching_pb2, matching_pb2_grpc
from protos import telemetry_pb2, telemetry_pb2_grpc
from protos import ml_feedback_pb2, ml_feedback_pb2_grpc

# Helper function to create gRPC channel and stub
def create_stub(channel_address, stub_class):
    channel = grpc.insecure_channel(channel_address)
    return stub_class(channel)

def main():
    # --- 1. Connect to services ---
    trip_request_stub = create_stub('localhost:50051', trip_request_pb2_grpc.TripRequestServiceStub)
    trip_stub = create_stub('localhost:50052', trip_pb2_grpc.TripServiceStub)
    matching_stub = create_stub('localhost:50053', matching_pb2_grpc.MatchingServiceStub)
    telemetry_stub = create_stub('localhost:50054', telemetry_pb2_grpc.TelemetryServiceStub)
    ml_stub = create_stub('localhost:50055', ml_feedback_pb2_grpc.MLFeedbackServiceStub)

    # --- 2. Create a TripRequest ---
    trip_request = trip_request_pb2.TripRequest(
        id="req_001",
        passenger_id="passenger_001",
        origin=trip_request_pb2.Location(lat=37.6, lng=68.8),
        destination=trip_request_pb2.Location(lat=37.65, lng=68.85),
        status=trip_request_pb2.PENDING,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )

    trip_request_resp = trip_request_stub.CreateTripRequest(trip_request)
    print("TripRequest created:", trip_request_resp)

    # --- 3. Get driver candidates from MatchingService ---
    matching_req = matching_pb2.MatchingRequest(
        trip_request_id=trip_request.id,
        origin=trip_request.origin,
        destination=trip_request.destination,
        requested_at=datetime.utcnow().isoformat(),
        max_candidates=3
    )
    matching_resp = matching_stub.GetDriverCandidates(matching_req)
    print("Driver candidates:", matching_resp.candidates)

    if not matching_resp.candidates:
        print("No drivers available. Test ends.")
        return

    # --- 4. Create a Trip with the first driver ---
    selected_driver = matching_resp.candidates[0].driver_id
    trip = trip_pb2.Trip(
        id="trip_001",
        trip_request_id=trip_request.id,
        passenger_id=trip_request.passenger_id,
        driver_id=selected_driver,
        origin=trip_request.origin,
        destination=trip_request.destination,
        status=trip_pb2.ACCEPTED,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )

    trip_resp = trip_stub.CreateTrip(trip)
    print("Trip created:", trip_resp)

    # --- 5. Log telemetry for TripRequest and Trip ---
    telemetry_stub.LogEvent(telemetry_pb2.TelemetryEvent(
        event_type="TripRequestCreated",
        timestamp=datetime.utcnow().isoformat(),
        entity_id=trip_request.id
    ))
    telemetry_stub.LogEvent(telemetry_pb2.TelemetryEvent(
        event_type="TripCreated",
        timestamp=datetime.utcnow().isoformat(),
        entity_id=trip.id
    ))

    # --- 6. Send ML feedback ---
    ml_feedback = ml_feedback_pb2.Feedback(
        trip_request_id=trip_request.id,
        candidate_list=matching_resp.candidates,
        matched_driver=selected_driver,
        success_flag=True,
        timestamp=datetime.utcnow().isoformat()
    )
    ml_resp = ml_stub.SendFeedback(ml_feedback)
    print("ML feedback sent:", ml_resp)

    # --- 7. Update Trip status to EN_ROUTE and COMPLETED ---
    trip.status = trip_pb2.EN_ROUTE
    trip_resp = trip_stub.UpdateTripStatus(trip)
    print("Trip updated to EN_ROUTE:", trip_resp)

    trip.status = trip_pb2.COMPLETED
    trip_resp = trip_stub.UpdateTripStatus(trip)
    print("Trip updated to COMPLETED:", trip_resp)

    # --- 8. Query telemetry events ---
    print("Telemetry events:")
    for event in telemetry_stub.QueryMetrics(telemetry_pb2.Metadata()):
        print(event)

    print("Full flow test completed successfully.")

if __name__ == "__main__":
    main()
