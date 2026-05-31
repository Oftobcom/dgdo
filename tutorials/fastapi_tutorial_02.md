# FastAPI Tutorial 02 — Приближаемся к DG Do API Gateway

Теперь мы сделаем шаг ближе к реальному проекту **DG Do**.  
Мы создадим **структурированный FastAPI-сервис**, который имитирует часть **API Gateway** — точку входа для мобильного приложения.

---

## 1. Цель урока

Научиться:
- Использовать Pydantic модели, соответствующие protobuf-схемам проекта
- Создавать организованную структуру папок (как будет в `api-gateway/`)
- Делать эндпоинты для основных сущностей (`TripRequest`)
- Готовить сервис к будущей интеграции с gRPC-сервисами

---

## 2. Создание структуры

```bash
cd dgdo/backend

mkdir -p api-gateway/app/api/v1
mkdir -p api-gateway/app/core
mkdir -p api-gateway/app/schemas

cd api-gateway
```

---

## 3. Установка зависимостей

```bash
pip install fastapi uvicorn pydantic python-dotenv
```

---

## 4. Код (`app/main.py`)

```python
from fastapi import FastAPI
from app.api.v1 import trip_request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="DG Do API Gateway",
    description="Единая точка входа для мобильных приложений DG Do (Худжанд)",
    version="0.2.0"
)

# Подключаем роутеры
app.include_router(trip_request.router, prefix="/api/v1", tags=["Trip Requests"])

@app.get("/")
def root():
    return {
        "service": "DG Do API Gateway",
        "status": "running",
        "version": "0.2.0",
        "market": "Khujand"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## 5. Pydantic-схемы (`app/schemas/trip_request.py`)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Location(BaseModel):
    lat: float
    lon: float

class TripRequestCreate(BaseModel):
    passenger_id: str
    origin: Location
    destination: Location
    # Можно добавить: preferred_vehicle_type, payment_method и т.д.

class TripRequestResponse(BaseModel):
    id: str
    passenger_id: str
    origin: Location
    destination: Location
    status: str
    created_at: datetime
    version: int
```

---

## 6. Роутер (`app/api/v1/trip_request.py`)

```python
from fastapi import APIRouter, HTTPException
from app.schemas.trip_request import TripRequestCreate, TripRequestResponse
from uuid import uuid4
from datetime import datetime

router = APIRouter()

# Временное in-memory хранилище (позже будет gRPC-клиент)
trip_requests = {}

@router.post("/trip-requests/", response_model=TripRequestResponse)
async def create_trip_request(request: TripRequestCreate):
    """Создание нового запроса на поездку"""
    trip_id = str(uuid4())
    
    trip = TripRequestResponse(
        id=trip_id,
        passenger_id=request.passenger_id,
        origin=request.origin,
        destination=request.destination,
        status="CREATED",
        created_at=datetime.utcnow(),
        version=1
    )
    
    trip_requests[trip_id] = trip
    return trip


@router.get("/trip-requests/{trip_request_id}", response_model=TripRequestResponse)
async def get_trip_request(trip_request_id: str):
    """Получение информации о запросе"""
    if trip_request_id not in trip_requests:
        raise HTTPException(status_code=404, detail="Trip request not found")
    return trip_requests[trip_request_id]
```

---

## 7. Запуск сервиса

```bash
cd dgdo/backend/api-gateway
uvicorn app.main:app --reload --port 8000
```

Сервер будет доступен по адресу: **http://localhost:8000**

---

## 8. Проверка в Postman / curl

### Создать TripRequest
**POST** `http://localhost:8000/api/v1/trip-requests/`

Body (raw → JSON):
```json
{
  "passenger_id": "passenger_rahmatjon_001",
  "origin": { "lat": 40.2825, "lon": 69.6220 },
  "destination": { "lat": 40.2950, "lon": 69.6350 }
}
```

### Получить TripRequest
**GET** `http://localhost:8000/api/v1/trip-requests/{id}`

