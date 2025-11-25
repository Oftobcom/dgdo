#include <crow.h>
#include "matcher.h"

int main() {
    crow::SimpleApp app;
    Matcher matcher;

    CROW_ROUTE(app, "/assign").methods("POST"_method)
    ([&matcher](const crow::request& req) {
        // TODO: parse JSON, call matcher.assign()
        return crow::response("{\"driver_id\": \"todo\"}");
    });

    app.port(8001).multithreaded().run();
}
