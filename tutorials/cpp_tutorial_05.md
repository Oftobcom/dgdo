# C++ Tutorial 05 — Production-Ready Trip Creation (JWT, gRPC Streaming, PostGIS, Observability)

Это **финальный** практический урок серии по C++ в проекте **DG Do**.  
Мы реализуем **полноценный production-like** компонент backend-сервиса (аналог `API Gateway` + `TripWorkflow`), максимально приближенный к реальной архитектуре проекта.

---

## 1. Цель урока

Научиться:
- JWT-подобной авторизации
- gRPC Streaming (realtime обновления статуса поездки)
- Интеграции с **PostGIS** (географические запросы)
- Rate Limiting и Observability (структурированные логи)
- Полноценному `TripWorkflow` с compensation и guardrails

---

## 2. Финальная структура проекта

```bash
cpp-services/trip-service/
├── src/
│   ├── main.cpp
│   ├── config/
│   ├── models/
│   ├── clients/          # gRPC клиенты
│   ├── workflow/
│   ├── auth/             # JWT
│   ├── db/               # PostGIS
│   ├── utils/            # logging, rate limit
│   └── proto/
├── CMakeLists.txt
└── config/pricing_config_khujand_v1.yaml
```

---

## 3. Установка зависимостей

```bash
sudo apt install -y libpqxx-dev libyaml-cpp-dev \
    libgrpc++-dev libprotobuf-dev \
    nlohmann-json3-dev spdlog
```

---

## 4. JWT Auth (`src/auth/JwtAuth.h`)

```cpp
#pragma once
#include <string>
#include <jwt-cpp/jwt.h>

class JwtAuth {
public:
    static std::string createToken(const std::string& user_id);
    static std::string validateToken(const std::string& token);
};
```

**Пример реализации:**
```cpp
std::string JwtAuth::createToken(const std::string& user_id) {
    auto token = jwt::create()
        .set_issuer("dgdo-khujand")
        .set_subject(user_id)
        .set_expires_at(std::chrono::system_clock::now() + std::chrono::minutes{60})
        .sign(jwt::algorithm::hs256{"dgdo-khujand-secret-key-change-in-production"});
    return token;
}
```

---

## 5. PostGIS Интеграция (`src/db/PostgisClient.h`)

```cpp
#pragma once
#include <pqxx/pqxx>
#include "../models/Location.h"

class PostgisClient {
    std::unique_ptr<pqxx::connection> conn;

public:
    PostgisClient();
    
    // Найти ближайших водителей
    std::vector<std::string> findNearbyDrivers(const Location& loc, double radius_km = 5.0);
    
    // Сохранить TripRequest с геометрией
    void saveTripRequest(const std::string& id, const Location& origin, const Location& dest);
};
```

---

## 6. TripWorkflow — Production Version (`src/workflow/TripWorkflow.h/cpp`)

```cpp
#pragma once
#include "../config/PricingConfig.h"
#include "../db/PostgisClient.h"
#include "../clients/*"
#include <spdlog/spdlog.h>

class TripWorkflow {
    PricingConfig config;
    PostgisClient db;
    // gRPC клиенты...

public:
    std::shared_ptr<Trip> createFullTrip(
        const std::string& passenger_id,
        const Location& origin,
        const Location& destination,
        const std::string& token
    );

private:
    void checkEconomicGuardrail(double fare, double payout);
    void logTelemetry(const std::string& event, const std::string& entity_id, const nlohmann::json& meta);
};
```

**Ключевые шаги в `createFullTrip`:**
1. JWT валидация
2. Создание `TripRequest` + сохранение в PostGIS
3. Matching (gRPC) → ближайшие водители
4. Pricing с surge из config
5. Economic guardrail
6. gRPC streaming обновлений статуса

---

## 7. gRPC Streaming (Realtime) 

```cpp
// В сервисе
grpc::Status StreamTripStatus(grpc::ServerContext* context, 
                             const TripStatusRequest* request,
                             grpc::ServerWriter<TripStatusUpdate>* writer);
```

---

## 8. Rate Limiting & Observability

Используем `spdlog` + простую in-memory rate limit (или `redis++` в production).

```cpp
spdlog::info("trip_created", "trip_id={}", trip->id);
```

---

## 9. `main.cpp` (Production Entry Point)

```cpp
int main() {
    spdlog::info("🚕 DG Do Trip Service started | Market: Khujand | v0.5.0");

    PricingConfig cfg = PricingConfig::load();
    TripWorkflow workflow;

    // Запуск gRPC сервера
    // ...

    std::cout << "✅ Сервис готов к обработке реальных поездок!\n";
    return 0;
}
```

---

## 10. Сборка (`CMakeLists.txt`)

```cmake
cmake_minimum_required(VERSION 3.16)
project(DGDoTripService VERSION 0.5.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

find_package(PQXX REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(gRPC REQUIRED)
find_package(spdlog REQUIRED)

add_executable(dgdo_trip_service src/main.cpp ...)

target_link_libraries(dgdo_trip_service 
    PRIVATE 
    pqxx yaml-cpp gRPC::grpc++ spdlog::spdlog nlohmann_json::nlohmann_json
)
```

---

## 11. Запуск и тестирование

```bash
mkdir build && cd build
cmake ..
make -j4
./dgdo_trip_service
```

**Тестовый сценарий:**
- Создать JWT токен
- Отправить запрос на создание поездки
- Получить realtime обновления по gRPC streaming

---

**Удачи в разработке DG Do!** 🚀🇹🇯
