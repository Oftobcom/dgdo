#include <drogon/drogon.h>

using namespace drogon;

int main() {
    // Set HTTP server address and port
    app().addListener("0.0.0.0", 8080);
    
    // Register simple GET endpoint
    app().registerHandler("/",
        [](const HttpRequestPtr &req,
           std::function<void(const HttpResponsePtr &)> &&callback) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setBody("Hello from Drogon API!");
            callback(resp);
        });
    
    // Register JSON API endpoint
    app().registerHandler("/api/hello",
        [](const HttpRequestPtr &req,
           std::function<void(const HttpResponsePtr &)> &&callback) {
            Json::Value json;
            json["message"] = "Hello World";
            json["status"] = "success";
            
            auto resp = HttpResponse::newHttpJsonResponse(json);
            callback(resp);
        },
        {Get});
    
    // Register endpoint with path parameter
    app().registerHandler("/api/hello/{name}",
        [](const HttpRequestPtr &req,
           std::function<void(const HttpResponsePtr &)> &&callback,
           const std::string &name) {
            Json::Value json;
            json["message"] = "Hello, " + name + "!";
            json["status"] = "success";
            
            auto resp = HttpResponse::newHttpJsonResponse(json);
            callback(resp);
        },
        {Get});
    
    // Disable verbose logging for minimal output
    app().setLogLevel(trantor::Logger::kWarn);
    
    LOG_INFO << "Server running on http://0.0.0.0:8080";
    LOG_INFO << "Available endpoints:";
    LOG_INFO << "  GET /";
    LOG_INFO << "  GET /api/hello";
    LOG_INFO << "  GET /api/hello/{name}";
    
    app().run();
    
    return 0;
}