#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>

#include "matching.grpc.pb.h"
#include "trip_request.pb.h"
#include "trip.pb.h"
#include "trip_service.pb.h"
#include "common.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

using dgdo::matching::MatchingService;
using dgdo::matching::MatchTripRequestCommand;
using dgdo::matching::MatchDistribution;
using dgdo::matching::DriverProbability;

using dgdo::triprequest::TripRequest;

class MatchingServiceImpl final : public MatchingService::Service {
public:
    Status MatchTripRequest(ServerContext* context,
                            const MatchTripRequestCommand* request,
                            MatchDistribution* reply) override {

        // Example: populate the reply with dummy probabilities
        reply->set_request_id(request->trip_request().id());

        uint32_t max_candidates = request->max_candidates();
        for (uint32_t i = 0; i < max_candidates; ++i) {
            DriverProbability* dp = reply->add_candidates();
            dp->set_driver_id("driver_" + std::to_string(i + 1));
            dp->set_probability(0.8 - 0.05 * i);
        }

        return Status::OK;
    }
};

void RunServer(const std::string& server_address) {
    MatchingServiceImpl service;

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;

    server->Wait();
}

int main(int argc, char** argv) {
    std::string server_address("0.0.0.0:50051");
    RunServer(server_address);
    return 0;
}
