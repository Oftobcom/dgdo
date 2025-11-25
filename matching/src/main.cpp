// Simple HTTP server using a tiny header-only server implementation.
// To keep the MVP self-contained we'll implement a minimal HTTP parser
// and JSON handling using nlohmann::json single header (if available).

#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <sstream>
#include "matcher.h"

// This is a stubbed HTTP server for the MVP. In production replace with
// Crow, Pistache, or cpp-httplib + full JSON parsing.

// For simplicity, we'll implement a tiny server using cpp-httplib single header.
// If not present in the base image, this file will compile only as a placeholder.

#include "httplib.h" // you need to add this header in production
#include "json.hpp" // nlohmann json

using json = nlohmann::json;

int main() {
    Matcher matcher;
    httplib::Server svr;

    svr.Post("/assign", [&](const httplib::Request &req, httplib::Response &res) {
        try {
            auto j = json::parse(req.body);
            // parse origin
            Location loc{0,0};
            if (j.contains("origin")) {
                loc.lat = j["origin"]["lat"].get<double>();
                loc.lon = j["origin"]["lon"].get<double>();
            }
            std::vector<Driver> drivers;
            if (j.contains("drivers")) {
                for (auto &d : j["drivers"]) {
                    Driver dr;
                    dr.id = d["id"].get<std::string>();
                    dr.lat = d["lat"].get<double>();
                    dr.lon = d["lon"].get<double>();
                    drivers.push_back(dr);
                }
            }
            std::string assigned = matcher.assign(loc, drivers);
            json resp = { {"driver_id", assigned} };
            res.set_content(resp.dump(), "application/json");
        } catch (const std::exception &e) {
            res.status = 500;
            json err = { {"error", e.what()} };
            res.set_content(err.dump(), "application/json");
        }
    });

    std::cout << "Matching engine listening on port 8001\n";
    svr.listen("0.0.0.0", 8001);
    return 0;
}