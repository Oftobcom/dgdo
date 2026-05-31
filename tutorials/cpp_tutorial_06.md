# C++ Tutorial 06 — Полноценный Production-Ready TripWorkflow (DG Do Final)

Это **заключительный продвинутый** урок серии по C++ в проекте **DG Do**.  
Мы собираем всё вместе в **полноценный production-grade** `TripWorkflow` с compensation, соответствующим реальной архитектуре из `trip_workflow_4.py` и схеме базы данных.

---

## 1. Цель урока

Научиться реализовывать:
- **Полноценный `TripWorkflow`** с compensation и idempotency
- JWT авторизацию
- PostGIS гео-запросы для Matching
- gRPC + Server Streaming (realtime обновления)
- Загрузку `pricing_config_khujand_v1.yaml` + surge multipliers
- Экономические guardrails
- Structured observability (spdlog + telemetry)

---

## 2. Структура проекта (Production)

```bash
cpp-services/trip-workflow-service/
├── src/
│   ├── main.cpp
│   ├── config/PricingConfig.h/cpp
│   ├── auth/JwtAuth.h/cpp
│   ├── db/PostgisClient.h/cpp
│   ├── clients/              # Matching, Pricing, DriverStatus
│   ├── workflow/TripWorkflow.h/cpp
│   ├── models/               # Trip, Location, etc.
│   ├── utils/                # telemetry, retry
│   └── proto/                # protobuf
├── config/pricing_config_khujand_v1.yaml
└── CMakeLists.txt
```

---

## 3. Ключевые компоненты

### PricingConfig (с hot-reload поддержкой)

```cpp
// src/config/PricingConfig.h
struct PricingConfig {
    double base_fare_tjs = 2.0;
    double per_km_rate_tjs = 2.0;
    double commission_percent = 20.0;
    double surge_multiplier = 1.0;
    std::string zone = "central_khujand";

    static PricingConfig load(const std::string& path);
    void applySurge(int hour, const std::string& zone);
};
```

### JWT Auth

```cpp
// src/auth/JwtAuth.h
std::string JwtAuth::validateToken(const std::string& token) {
    auto decoded = jwt::decode(token);
    // Проверка подписи и expiration...
    return decoded.get_subject(); // passenger_id
}
```

### PostGIS Client (гео-запросы)

```cpp
// src/db/PostgisClient.cpp
std::vector<std::string> PostgisClient::findNearbyDrivers(const Location& loc, double radius_km) {
    pqxx::work txn(*conn);
    auto result = txn.exec_params(
        R"(
        SELECT driver_id 
        FROM driver_status 
        WHERE is_available = true 
        AND ST_DWithin(location, ST_MakePoint($1, $2)::geography, $3 * 1000)
        ORDER BY ST_Distance(location, ST_MakePoint($1, $2)::geography)
        LIMIT 5;
        )", loc.lon, loc.lat, radius_km);
    
    std::vector<std::string> drivers;
    for (auto row : result) drivers.push_back(row[0].c_str());
    return drivers;
}
```

### Полноценный TripWorkflow с Compensation

```cpp
// src/workflow/TripWorkflow.cpp
std::shared_ptr<Trip> TripWorkflow::createFullTrip(
    const std::string& token,
    const Location& origin,
    const Location& destination
) {
    std::string passenger_id = JwtAuth::validateToken(token);
    std::string workflow_id = "trip:" + passenger_id + ":" + std::to_string(time(nullptr));

    // Idempotency (Redis или in-memory)
    if (checkIdempotency(workflow_id)) return getExistingTrip(workflow_id);

    std::string trip_request_id, driver_id;
    std::shared_ptr<Trip> trip = nullptr;

    try {
        // 1. Create TripRequest + PostGIS
        trip_request_id = createTripRequest(passenger_id, origin, destination);

        // 2. Matching via gRPC + PostGIS
        auto candidates = matchingClient.getCandidates(trip_request_id, origin);
        if (candidates.empty()) throw std::runtime_error("No drivers");
        driver_id = candidates[0];

        // 3. Pricing with YAML config + surge
        PricingConfig cfg = PricingConfig::load("config/pricing_config_khujand_v1.yaml");
        cfg.applySurge(getCurrentHour(), "central_khujand");

        double fare = pricingClient.calculatePrice(trip_request_id, passenger_id, driver_id, 
                                                   calculateDistance(origin, destination), cfg.surge_multiplier);

        // 4. Economic Guardrail
        double payout = fare * (1.0 - cfg.commission_percent / 100.0);
        checkEconomicGuardrail(fare, payout);

        // 5. Assign Driver + Create Trip
        driverStatusClient.assignDriver(driver_id);
        trip = tripServiceClient.createTrip(trip_request_id, passenger_id, driver_id);

        logTelemetry("TripCreated", trip->id, {{"fare", fare}, {"driver", driver_id}});

        saveToIdempotency(workflow_id, trip->id);
        return trip;

    } catch (const std::exception& e) {
        logTelemetry("TripFailed", trip_request_id, {{"error", e.what()}});
        
        // Compensation
        if (!trip_request_id.empty()) cancelTripRequest(trip_request_id);
        if (!driver_id.empty()) driverStatusClient.releaseDriver(driver_id);
        
        throw;
    }
}
```

---

## 4. gRPC Streaming (Realtime Status)

```cpp
// В gRPC сервисе
grpc::Status TripWorkflowService::StreamTripStatus(...) {
    while (true) {
        TripStatusUpdate update;
        update.set_status("EN_ROUTE");
        writer->Write(update);
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }
}
```

---

## 5. main.cpp

```cpp
int main() {
    spdlog::info("🚕 DG Do TripWorkflow Service started | Khujand | v0.6.0");

    TripWorkflow workflow;

    Location origin{40.2825, 69.6220};
    Location dest{40.2950, 69.6350};

    try {
        auto trip = workflow.createFullTrip("eyJ...", origin, dest);
        spdlog::info("✅ Поездка создана успешно | ID: {}", trip->id);
    } catch (const std::exception& e) {
        spdlog::error("❌ Workflow failed: {}", e.what());
    }

    return 0;
}
```

---

## 6. CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20)
project(DGDoTripWorkflow VERSION 0.6.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

find_package(PQXX REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(gRPC REQUIRED)
find_package(spdlog REQUIRED)
find_package(jwt-cpp REQUIRED)

add_executable(dgdo_trip_workflow src/main.cpp 
    src/config/PricingConfig.cpp
    src/workflow/TripWorkflow.cpp
    # ... другие файлы
)

target_link_libraries(dgdo_trip_workflow 
    PRIVATE pqxx yaml-cpp gRPC::grpc++ spdlog::spdlog jwt-cpp::jwt-cpp
)
```

---

## 7. Запуск

```bash
mkdir build && cd build
cmake ..
make -j4
./dgdo_trip_workflow
```
