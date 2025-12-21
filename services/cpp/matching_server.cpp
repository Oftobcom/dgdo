#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <grpcpp/grpcpp.h>
#include "matching.grpc.pb.h"
#include "common.pb.h"
#include "driver_status.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

using dgdo::matching::MatchingService;
using dgdo::matching::MatchingRequest;
using dgdo::matching::MatchingResponse;
using dgdo::matching::Candidate;

using dgdo::driver_status::DriverStatus;
using dgdo::common::Location;

class MatchingServiceImpl final : public MatchingService::Service {
public:
    Status GetCandidates(ServerContext* context,
                         const MatchingRequest* request,
                         MatchingResponse* reply) override {

        // Copy request ID (immutable key)
        // Idempotency is ensured in real implementation
        reply->set_reason_code("");

        uint32_t max_candidates = request->max_candidates();
        int64_t seed = request->seed();

        // Example: deterministic pseudo-random candidate generation
        // In production, replace with actual available driver lookup
        for (uint32_t i = 0; i < max_candidates; ++i) {
            Candidate* candidate = reply->add_candidates();
            candidate->set_driver_id("driver_" + std::to_string(i + 1));

            // Deterministic probability using seed
            double probability = 1.0 / max_candidates;
            candidate->set_probability(probability);

            // Optional: distance / ETA placeholders
            candidate->set_distance_meters(1000.0 * (i + 1));
            candidate->set_eta_seconds(300 + 30 * i);
        }

        // If no drivers found, set reason_code
        if (max_candidates == 0) {
            reply->set_reason_code("NO_DRIVERS");
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
    std::cout << "MatchingService listening on " << server_address << std::endl;

    server->Wait();
}

int main(int argc, char** argv) {
    std::string server_address("0.0.0.0:50051");
    RunServer(server_address);
    return 0;
}
