# C++ Tutorial 01 — Минимальный "Hello DG Do" для начинающих

Это **первый** урок серии по C++ в контексте проекта **DG Do**.  
Мы начнём с самого простого: создадим консольное приложение на C++, которое выводит приветствие и базовую информацию о поездке (имитируя будущие компоненты Pricing / Matching Service).

Цель — быстро запуститься и почувствовать структуру, близкую к реальному backend'у DG Do (Khujand).

---

## 1. Цель урока

Научиться:
- Создавать минимальное C++ приложение
- Использовать современный C++ (C++17/20)
- Подготовить структуру папок, похожую на `dgdo/backend/`
- Выводить данные, которые в будущем будут приходить из PostgreSQL + PostGIS

---

## 2. Создание структуры проекта

```bash
cd dgdo/backend

mkdir -p cpp-services/hello-service
cd cpp-services/hello-service

# Основные файлы
touch main.cpp CMakeLists.txt
```

---

## 3. Установка инструментов (Ubuntu / WSL)

```bash
sudo apt update
sudo apt install build-essential cmake -y
```

---

## 4. Код (`main.cpp`)

```cpp
#include <iostream>
#include <string>
#include <iomanip>

struct Location {
    double lat;
    double lon;
};

struct TripInfo {
    std::string trip_id;
    std::string passenger_id;
    Location origin;
    Location destination;
    double base_fare_tjs = 2.0;
    double per_km_rate_tjs = 2.0;
};

int main() {
    std::cout << "🚕 DG Do — C++ Backend Service (Khujand)" << std::endl;
    std::cout << "Version: 0.1.0" << std::endl;
    std::cout << "Market: Khujand" << std::endl;
    std::cout << "================================" << std::endl;

    // Пример данных поездки (в будущем придёт из gRPC / DB)
    TripInfo trip = {
        "trip_" + std::to_string(12345),
        "passenger_rahmatjon_001",
        {40.2825, 69.6220},   // origin (Khujand center)
        {40.2950, 69.6350}    // destination
    };

    double distance_km = 2.5; // заглушка

    double fare = trip.base_fare_tjs + (distance_km * trip.per_km_rate_tjs);

    std::cout << "\n📍 Новая поездка создана!" << std::endl;
    std::cout << "Trip ID: " << trip.trip_id << std::endl;
    std::cout << "Passenger: " << trip.passenger_id << std::endl;
    std::cout << "From: (" << trip.origin.lat << ", " << trip.origin.lon << ")" << std::endl;
    std::cout << "To:   (" << trip.destination.lat << ", " << trip.destination.lon << ")" << std::endl;
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Стоимость: " << fare << " TJS" << std::endl;

    std::cout << "\n✅ Готов к интеграции с PricingConfig и gRPC!" << std::endl;

    return 0;
}
```

---

## 5. CMake конфигурация (`CMakeLists.txt`)

```cmake
cmake_minimum_required(VERSION 3.14)
project(DGDoHelloService VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(dgdo_hello main.cpp)

# В следующих уроках добавим:
# target_link_libraries(dgdo_hello ... )
```

---

## 6. Сборка и запуск

```bash
mkdir build && cd build
cmake ..
make -j4
./dgdo_hello
```

**Ожидаемый вывод:**

```
🚕 DG Do — C++ Backend Service (Khujand)
Version: 0.1.0
Market: Khujand
================================

📍 Новая поездка создана!
Trip ID: trip_12345
Passenger: passenger_rahmatjon_001
From: (40.2825, 69.6220)
To:   (40.2950, 69.6350)
Стоимость: 7.00 TJS

✅ Готов к интеграции с PricingConfig и gRPC!
```

---

## 7. Что дальше?

В следующих уроках (`cpp_tutorial_02.md` и далее) мы:
- Добавим загрузку `pricing_config_khujand_v1.yaml`
- Создадим класс `PricingCalculator`
- Подключим gRPC сервер
- Интегрируем с PostGIS (через `pqxx` + PostGIS)
- Сделаем микросервис Matching / Pricing

---

**Готово!** Запустите команду выше и убедитесь, что программа работает.

Это ваш первый шаг к написанию **высокопроизводительных** компонентов DG Do на C++ (особенно для Matching Engine и реального времени). 

Если всё запустилось — переходите к `cpp_tutorial_02.md`. 

Удачи в проекте DG Do! 🚀