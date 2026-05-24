# C++ Tutorial 02 — Структурированный сервис с моделями (приближаемся к DG Do)

Теперь мы делаем **важный шаг** ближе к реальной архитектуре **DG Do**.  
В этом уроке мы создадим **структурированный C++ проект**, имитирующий часть backend-сервиса (например, `TripRequestService` или `PricingService`).

---

## 1. Цель урока

Научиться:
- Организовывать код в современном C++ стиле (как будет в `dgdo/backend/cpp-services/`)
- Создавать **модели данных** (аналог Pydantic-схем)
- Использовать CMake для сборки
- Реализовать базовый сервис с бизнес-логикой создания `TripRequest`
- Подготовиться к интеграции с `PricingConfig` и gRPC

---

## 2. Создание структуры проекта

```bash
cd dgdo/backend

mkdir -p cpp-services/trip-request-service
cd cpp-services/trip-request-service

# Создаём структуру папок
mkdir -p src/models src/services src/utils include

touch CMakeLists.txt
touch src/main.cpp
touch src/models/Location.h src/models/TripRequest.h
touch src/services/TripRequestService.h src/services/TripRequestService.cpp
```

---

## 3. Установка инструментов

```bash
sudo apt update
sudo apt install build-essential cmake libyaml-cpp-dev -y
```

---

## 4. Модели данных (`src/models/`)

**`src/models/Location.h`**
```cpp
#pragma once
#include <iostream>

struct Location {
    double lat;
    double lon;

    void print() const {
        std::cout << "(" << lat << ", " << lon << ")";
    }
};
```

**`src/models/TripRequest.h`**
```cpp
#pragma once
#include "Location.h"
#include <string>
#include <chrono>

struct TripRequest {
    std::string id;
    std::string passenger_id;
    Location origin;
    Location destination;
    std::string status = "CREATED";
    std::chrono::system_clock::time_point created_at;

    TripRequest(const std::string& pid, const Location& o, const Location& d)
        : id("tr_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count() % 100000)),
          passenger_id(pid), origin(o), destination(d),
          created_at(std::chrono::system_clock::now()) {}
};
```

---

## 5. Сервис (`src/services/TripRequestService.h` + `.cpp`)

**`src/services/TripRequestService.h`**
```cpp
#pragma once
#include "../models/TripRequest.h"
#include <vector>
#include <memory>

class TripRequestService {
private:
    std::vector<std::shared_ptr<TripRequest>> trip_requests;

public:
    std::shared_ptr<TripRequest> createTripRequest(
        const std::string& passenger_id,
        const Location& origin,
        const Location& destination
    );

    std::shared_ptr<TripRequest> getTripRequest(const std::string& id) const;
};
```

**`src/services/TripRequestService.cpp`**
```cpp
#include "TripRequestService.h"

std::shared_ptr<TripRequest> TripRequestService::createTripRequest(
    const std::string& passenger_id,
    const Location& origin,
    const Location& destination
) {
    auto trip = std::make_shared<TripRequest>(passenger_id, origin, destination);
    trip_requests.push_back(trip);
    std::cout << "✅ TripRequest created: " << trip->id << std::endl;
    return trip;
}

std::shared_ptr<TripRequest> TripRequestService::getTripRequest(const std::string& id) const {
    for (const auto& t : trip_requests) {
        if (t->id == id) return t;
    }
    return nullptr;
}
```

---

## 6. Главный файл (`src/main.cpp`)

```cpp
#include <iostream>
#include "models/Location.h"
#include "models/TripRequest.h"
#include "services/TripRequestService.h"

int main() {
    std::cout << "🚕 DG Do — TripRequestService (C++)\n";
    std::cout << "Market: Khujand | Version: 0.2.0\n";
    std::cout << "======================================\n\n";

    TripRequestService service;

    Location origin{40.2825, 69.6220};   // Центр Худжанда
    Location destination{40.2950, 69.6350};

    auto trip = service.createTripRequest("passenger_rahmatjon_001", origin, destination);

    std::cout << "\n📍 Детали поездки:\n";
    std::cout << "ID: " << trip->id << std::endl;
    std::cout << "Passenger: " << trip->passenger_id << std::endl;
    std::cout << "From: "; trip->origin.print(); std::cout << std::endl;
    std::cout << "To:   "; trip->destination.print(); std::cout << std::endl;
    std::cout << "Status: " << trip->status << std::endl;

    std::cout << "\n🎯 Готов к интеграции с PricingConfig, gRPC и PostgreSQL!\n";

    return 0;
}
```

---

## 7. CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.16)
project(DGDoTripRequestService VERSION 0.2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Находим yaml-cpp (для будущих уроков)
find_package(yaml-cpp QUIET)

add_executable(dgdo_trip_request 
    src/main.cpp
    src/services/TripRequestService.cpp
)

target_include_directories(dgdo_trip_request PRIVATE src)

if(yaml-cpp_FOUND)
    target_link_libraries(dgdo_trip_request PRIVATE yaml-cpp)
    target_compile_definitions(dgdo_trip_request PRIVATE HAS_YAML)
endif()

# В следующих уроках добавим gRPC, pqxx и т.д.
```

---

## 8. Сборка и запуск

```bash
mkdir build && cd build
cmake ..
make -j4
./dgdo_trip_request
```

**Ожидаемый вывод:**

```
🚕 DG Do — TripRequestService (C++)
Market: Khujand | Version: 0.2.0
======================================

✅ TripRequest created: tr_xxxxxxxxx

📍 Детали поездки:
ID: tr_xxxxxxxxx
Passenger: passenger_rahmatjon_001
From: (40.2825, 69.622)
To:   (40.295, 69.635)
Status: CREATED

🎯 Готов к интеграции с PricingConfig, gRPC и PostgreSQL!
```

---

## 9. Что дальше?

В `cpp_tutorial_03.md` мы:
- Добавим загрузку `pricing_config_khujand_v1.yaml`
- Создадим `PricingCalculator`
- Подготовим gRPC сервер
- Начнём интеграцию с PostGIS

---

**Отлично!** Теперь у вас есть структурированный C++ сервис, который повторяет архитектурные принципы DG Do.

Запустите проект и переходите к следующему уроку, когда будете готовы.

Удачи в разработке DG Do! 🚀
