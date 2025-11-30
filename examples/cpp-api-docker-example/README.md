I'll help you create a minimal Docker-based C++ API project using Drogon. Here's a clean, minimal setup:

## Project Structure
```
drogon-api/
├── Dockerfile
├── docker-compose.yml
├── CMakeLists.txt
├── main.cpp
└── README.md
```

## 1. Dockerfile
```dockerfile
FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libjsoncpp-dev \
    libssl-dev \
    libz-dev \
    uuid-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and build Drogon
WORKDIR /tmp
RUN git clone https://github.com/drogonframework/drogon.git
RUN cd drogon && \
    git checkout v1.9.4 && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# Set up project directory
WORKDIR /app
COPY . .

# Build the project
RUN mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc)

EXPOSE 8080

CMD ["./build/drogon_api"]
```

## 2. docker-compose.yml
```yaml
version: '3.8'

services:
  drogon-api:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - .:/app
    restart: unless-stopped
```

## 3. CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.5)
project(drogon_api)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Drogon REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Drogon::Drogon)
```

## 4. main.cpp
```cpp
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
```

## 5. README.md
```markdown
# Minimal Drogon C++ API

A simple Docker-based C++ REST API using Drogon framework.

## Quick Start

1. Build and run:
```bash
docker-compose up --build
```

2. Test the API:
```bash
curl http://localhost:8080/
curl http://localhost:8080/api/hello
curl http://localhost:8080/api/hello/John
```

## Endpoints

- `GET /` - Simple text response
- `GET /api/hello` - JSON response
- `GET /api/hello/{name}` - Personalized JSON response

## Development

The project is set up with hot-reload via volume mounting. Code changes will require rebuilding the container.
```

## Usage

1. **Create the project directory:**
```bash
mkdir drogon-api && cd drogon-api
```

2. **Create all the files above in the directory**

3. **Build and run:**
```bash
docker-compose up --build
```

4. **Test the API:**
```bash
curl http://localhost:8080/
# Output: Hello from Drogon API!

curl http://localhost:8080/api/hello
# Output: {"message":"Hello World","status":"success"}

curl http://localhost:8080/api/hello/Alice
# Output: {"message":"Hello, Alice!","status":"success"}
```

## Key Features

- **Minimal**: Only essential dependencies and code
- **Dockerized**: Consistent development and deployment environment
- **Drogon Framework**: High-performance C++ web framework
- **RESTful**: Simple JSON API endpoints
- **Ubuntu 24.04**: Matches your target environment

The API will be available at `http://localhost:8080` with the three endpoints defined. The container runs in the foreground, so you can see the logs directly.