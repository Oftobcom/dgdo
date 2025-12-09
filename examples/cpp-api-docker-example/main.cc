#include <drogon/drogon.h>

using namespace drogon;

int main() {
    // Create a simple Hello World handler
    app().registerHandler(
        "/",
        [](const HttpRequestPtr &,
           std::function<void(const HttpResponsePtr &)> &&callback) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setBody("Hello World from Drogon! Test");
            callback(resp);
        },
        {Get});

    // Run HTTP server on port 8080
    LOG_INFO << "Server running on 0.0.0.0:8080";
    app().addListener("0.0.0.0", 8080).run();

    return 0;
}