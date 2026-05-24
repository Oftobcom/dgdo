# C++ Tutorial 03 — Интеграция с gRPC сервисами DG Do

Теперь мы делаем **ещё один важный шаг** к реальной архитектуре проекта **DG Do**.  
В этом уроке мы научимся, как **C++ сервис** (например, `TripRequestService` или `PricingService`) общается с другими внутренними gRPC-сервисами.

---

## 1. Цель урока

Научиться:
- Создавать **gRPC клиенты** на C++
- Вызывать другие микросервисы DG Do (`TripRequestService`, `MatchingService`, `PricingService`)
- Обрабатывать ошибки, таймауты и retries
- Приближаться к production-структуре `dgdo/backend/cpp-services/`
- Готовиться к полноценному `TripWorkflow`

---

## 2. Обновление структуры проекта

```bash
cd dgdo/backend/cpp-services

mkdir -p trip-request-service
cd trip-request-service

mkdir -p src/clients src/grpc src/proto include

# Скопировать protobuf определения (в реальном проекте генерируются)
touch src/proto/trip_request.proto
```

---

## 3. Установка зависимостей (gRPC + Protobuf)

```bash
sudo apt update
sudo apt install -y build-essential cmake \
    libgrpc++-dev libgrpc-dev \
    libprotobuf-dev protobuf-compiler \
    libyaml-cpp-dev
```

---

## 4. Protobuf определение (пример)

**`src/proto/trip_request.proto`**
```proto
syntax = "proto3";

package dgdo.trip_request;

service TripRequestService {
  rpc CreateTripRequest(CreateTripRequestCommand) returns (TripRequest);
  rpc GetTripRequest(GetTripRequestRequest) returns (TripRequest);
}

message Location {
  double lat = 1;
  double lon = 2;
}

message CreateTripRequestCommand {
  string passenger_id = 1;
  Location origin = 2;
  Location destination = 3;
}

message TripRequest {
  string id = 1;
  string passenger_id = 2;
  Location origin = 3;
  Location destination = 4;
  string status = 5;
  int32 version = 6;
}

message GetTripRequestRequest {
  string trip_request_id = 1;
}
```

**Генерация кода:**
```bash
mkdir -p src/grpc
protoc -I src/proto \
  --cpp_out=src/grpc \
  --grpc_out=src/grpc \
  --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` \
  src/proto/trip_request.proto
```

---

## 5. gRPC Клиент (`src/clients/TripRequestClient.h` + `.cpp`)

**`src/clients/TripRequestClient.h`**
```cpp
#pragma once
#include "../grpc/trip_request.pb.h"
#include "../grpc/trip_request.grpc.pb.h"
#include <grpcpp/grpcpp.h>
#include <memory>

class TripRequestClient {
private:
    std::unique_ptr<dgdo::trip_request::TripRequestService::Stub> stub;

public:
    TripRequestClient(const std::string& target = "localhost:50052");

    std::shared_ptr<dgdo::trip_request::TripRequest> createTripRequest(
        const std::string& passenger_id,
        const dgdo::trip_request::Location& origin,
        const dgdo::trip_request::Location& destination
    );
};
```

**`src/clients/TripRequestClient.cpp`**
```cpp
#include "TripRequestClient.h"
#include <iostream>

TripRequestClient::TripRequestClient(const std::string& target) {
    auto channel = grpc::CreateChannel(target, grpc::InsecureChannelCredentials());
    stub = dgdo::trip_request::TripRequestService::NewStub(channel);
}

std::shared_ptr<dgdo::trip_request::TripRequest> TripRequestClient::createTripRequest(
    const std::string& passenger_id,
    const dgdo::trip_request::Location& origin,
    const dgdo::trip_request::Location& destination
) {
    dgdo::trip_request::CreateTripRequestCommand request;
    request.set_passenger_id(passenger_id);
    *request.mutable_origin() = origin;
    *request.mutable_destination() = destination;

    dgdo::trip_request::TripRequest response;
    grpc::ClientContext context;

    grpc::Status status = stub->CreateTripRequest(&context, request, &response);

    if (status.ok()) {
        std::cout << "✅ gRPC: TripRequest created successfully: " << response.id() << std::endl;
        return std::make_shared<dgdo::trip_request::TripRequest>(response);
    } else {
        std::cerr << "❌ gRPC error: " << status.error_message() << std::endl;
        return nullptr;
    }
}
```

---

## 6. Обновлённый `main.cpp`

```cpp
#include <iostream>
#include "models/Location.h"
#include "clients/TripRequestClient.h"

int main() {
    std::cout << "🚕 DG Do — TripRequestService + gRPC Client (C++)\n";
    std::cout << "Market: Khujand | Version: 0.3.0\n";
    std::cout << "======================================\n\n";

    TripRequestClient client("localhost:50052");

    dgdo::trip_request::Location origin;
    origin.set_lat(40.2825);
    origin.set_lon(69.6220);

    dgdo::trip_request::Location destination;
    destination.set_lat(40.2950);
    destination.set_lon(69.6350);

    auto trip = client.createTripRequest("passenger_rahmatjon_001", origin, destination);

    if (trip) {
        std::cout << "\n📍 TripRequest details:\n";
        std::cout << "ID: " << trip->id() << std::endl;
        std::cout << "Passenger: " << trip->passenger_id() << std::endl;
        std::cout << "Status: " << trip->status() << std::endl;
    }

    std::cout << "\n🎯 Готов к интеграции с MatchingService, PricingService и TripWorkflow!\n";

    return 0;
}
```

---

## 7. Обновление `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(DGDoTripRequestService VERSION 0.3.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

add_executable(dgdo_trip_request 
    src/main.cpp
    src/clients/TripRequestClient.cpp
    # Добавьте сгенерированные .pb.cc файлы
    src/grpc/trip_request.pb.cc
    src/grpc/trip_request.grpc.pb.cc
)

target_include_directories(dgdo_trip_request PRIVATE src src/grpc)

target_link_libraries(dgdo_trip_request 
    PRIVATE 
    gRPC::grpc++
    protobuf::libprotobuf
)
```

---

## 8. Сборка и запуск

```bash
mkdir -p build && cd build
cmake ..
make -j4
./dgdo_trip_request
```

---

**Отлично!** Теперь ваш C++ сервис умеет общаться по gRPC с другими компонентами DG Do — как в реальной микросервисной архитектуре.

Запустите и протестируйте. Когда будете готовы — переходите к следующему уроку.

Удачи в разработке высокопроизводительного backend'а DG Do! 🚀