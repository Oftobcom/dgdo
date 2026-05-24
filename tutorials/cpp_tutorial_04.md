# C++ Tutorial 04 — Полноценный TripWorkflow с gRPC и Pricing (DG Do)

Теперь мы приближаемся к **реальному production-коду** DG Do.  
В этом уроке мы реализуем **главный бизнес-процесс** — создание поездки (`Trip`) через полный `TripWorkflow` с использованием нескольких gRPC-сервисов.

---

## 1. Цель урока

Научиться:
- Создавать `PricingClient` и `MatchingClient`
- Реализовать **TripWorkflow** на C++ (оркестрация сервисов)
- Интегрировать `PricingConfig` (YAML) из `pricing_config_khujand_v1.yaml`
- Добавлять **экономические guardrails**
- Приближаться к архитектуре `dgdo/backend/cpp-services/`

---

## 2. Обновление структуры

```bash
cd dgdo/backend/cpp-services/trip-workflow-service

mkdir -p src/clients src/workflow src/config src/models

touch src/config/PricingConfig.h src/config/PricingConfig.cpp
touch src/clients/PricingClient.h src/clients/PricingClient.cpp
touch src/clients/MatchingClient.h src/clients/MatchingClient.cpp
touch src/workflow/TripWorkflow.h src/workflow/TripWorkflow.cpp
```

---

## 3. Установка зависимостей

```bash
sudo apt install -y libyaml-cpp-dev libgrpc++-dev libprotobuf-dev
```

---

## 4. Pricing Config (YAML) — `src/config/PricingConfig.h/cpp`

**`src/config/PricingConfig.h`**
```cpp
#pragma once
#include <string>
#include <yaml-cpp/yaml.h>

struct PricingConfig {
    double base_fare_tjs = 2.0;
    double per_km_rate_tjs = 2.0;
    double per_min_rate_tjs = 0.5;
    double commission_percent = 20.0;
    double surge_multiplier = 1.0;

    static PricingConfig load(const std::string& path = "config/pricing_config_khujand_v1.yaml");
    void applyTimeBasedMultiplier(int current_hour);
    void print() const;
};
```

**`src/config/PricingConfig.cpp`**
```cpp
#include "PricingConfig.h"
#include <iostream>
#include <chrono>

PricingConfig PricingConfig::load(const std::string& path) {
    PricingConfig cfg;
    try {
        YAML::Node config = YAML::LoadFile(path);
        auto def = config["default"];
        cfg.base_fare_tjs = def["base_fare_tjs"].as<double>();
        cfg.per_km_rate_tjs = def["per_km_rate_tjs"].as<double>();
        cfg.per_min_rate_tjs = def["per_min_rate_tjs"].as<double>();
        std::cout << "✅ Pricing config loaded for Khujand\n";
    } catch (...) {
        std::cerr << "⚠️ Using default pricing config\n";
    }
    return cfg;
}

void PricingConfig::applyTimeBasedMultiplier(int current_hour) {
    if (current_hour >= 7 && current_hour < 9) cfg.surge_multiplier = 1.2;
    else if (current_hour >= 17 && current_hour < 19) cfg.surge_multiplier = 1.2;
    else if (current_hour < 5 || current_hour >= 23) cfg.surge_multiplier = 1.1;
}

void PricingConfig::print() const {
    std::cout << "Base Fare: " << base_fare_tjs << " TJS | Per KM: " << per_km_rate_tjs << " TJS\n";
}
```

---

## 5. gRPC Клиенты

**`src/clients/MatchingClient.h/cpp`** (упрощённо)
```cpp
// MatchingClient.h
std::vector<std::string> getCandidates(const std::string& trip_request_id);
```

**`src/clients/PricingClient.h/cpp`**
```cpp
#pragma once
#include "../grpc/pricing.grpc.pb.h"  // предположим сгенерировано

class PricingClient {
    std::unique_ptr<dgdo::pricing::PricingService::Stub> stub;
public:
    PricingClient(const std::string& target = "localhost:50056");
    
    double calculatePrice(const std::string& trip_id, const std::string& passenger_id,
                         const std::string& driver_id, double distance_km, double surge);
};
```

---

## 6. TripWorkflow — Главная оркестрация (`src/workflow/TripWorkflow.h/cpp`)

**`src/workflow/TripWorkflow.h`**
```cpp
#pragma once
#include "../config/PricingConfig.h"
#include "../models/Trip.h"

class TripWorkflow {
    PricingConfig config;
    // Клиенты: MatchingClient, PricingClient, DriverStatusClient...

public:
    TripWorkflow();

    std::shared_ptr<Trip> createTrip(
        const std::string& passenger_id,
        const Location& origin,
        const Location& destination
    );

private:
    void checkEconomicGuardrail(double passenger_fare, double driver_payout);
};
```

**`src/workflow/TripWorkflow.cpp`**
```cpp
#include "TripWorkflow.h"
#include "../clients/MatchingClient.h"
#include "../clients/PricingClient.h"
#include <iostream>

TripWorkflow::TripWorkflow() {
    config = PricingConfig::load();
    config.applyTimeBasedMultiplier(std::chrono::system_clock::now().tm_hour);
}

std::shared_ptr<Trip> TripWorkflow::createTrip(...) {
    // 1. Создать TripRequest
    // 2. Matching → получить driver_id
    std::string driver_id = "driver_123"; // из MatchingClient

    // 3. Pricing
    PricingClient pricingClient;
    double fare = pricingClient.calculatePrice("tr_xxx", passenger_id, driver_id, 2.5, config.surge_multiplier);

    // 4. Economic Guardrail
    double driver_payout = fare * (1 - config.commission_percent/100.0);
    checkEconomicGuardrail(fare, driver_payout);

    // 5. Создать Trip
    auto trip = std::make_shared<Trip>(/* params */);
    std::cout << "✅ Полноценная поездка создана! Fare: " << fare << " TJS\n";
    return trip;
}

void TripWorkflow::checkEconomicGuardrail(double passenger_fare, double driver_payout) {
    if (passenger_fare < driver_payout + 50.0) {
        throw std::runtime_error("Economic guardrail violation!");
    }
}
```

---

## 7. Модель Trip (`src/models/Trip.h`)

```cpp
#pragma once
#include "Location.h"

struct Trip {
    std::string id;
    std::string trip_request_id;
    std::string driver_id;
    std::string status = "ACCEPTED";
    double passenger_fare_total;
    // ...
};
```

---

## 8. `main.cpp`

```cpp
#include <iostream>
#include "workflow/TripWorkflow.h"

int main() {
    std::cout << "🚕 DG Do — TripWorkflow Service (C++)\n";
    std::cout << "Market: Khujand | Version: 0.4.0\n";
    std::cout << "======================================\n\n";

    TripWorkflow workflow;

    Location origin{40.2825, 69.6220};
    Location destination{40.2950, 69.6350};

    try {
        auto trip = workflow.createTrip("passenger_rahmatjon_001", origin, destination);
        std::cout << "\n🎉 Поездка успешно создана!\n";
        std::cout << "Trip ID: " << trip->id << "\n";
        std::cout << "Driver: " << trip->driver_id << "\n";
        std::cout << "Fare: " << trip->passenger_fare_total << " TJS\n";
    } catch (const std::exception& e) {
        std::cerr << "❌ Ошибка: " << e.what() << std::endl;
    }

    return 0;
}
```

---

## 9. CMakeLists.txt (обновлённый)

```cmake
# ... (предыдущие зависимости + yaml-cpp)
target_link_libraries(dgdo_trip_workflow PRIVATE yaml-cpp gRPC::grpc++ protobuf::libprotobuf)
```

---

## 10. Сборка и запуск

```bash
mkdir build && cd build
cmake ..
make -j4
./dgdo_trip_workflow
```

---

**Отлично!** Теперь у вас есть полноценный `TripWorkflow` на C++ с gRPC, конфигурацией и экономическими проверками — ключевой компонент DG Do.

Запустите и убедитесь, что workflow работает. Готовы к следующему уровню — production-ready features!

Удачи в проекте DG Do! 🚀
