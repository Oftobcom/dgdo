# FastAPI Tutorial 03 — Интеграция с gRPC сервисами DG Do

Теперь мы делаем **ещё один важный шаг** к реальной архитектуре проекта **DG Do**.  
В этом уроке мы научимся, как **API Gateway** (FastAPI) общается с внутренними gRPC-сервисами (`TripRequestService`, `MatchingService`, `TripService`).

---

## 1. Цель урока

Научиться:
- Создавать **клиенты** для gRPC-сервисов
- Вызывать реальные backend-сервисы из FastAPI
- Использовать `httpx` + gRPC (гибридный подход)
- Обрабатывать ошибки и таймауты
- Приближаться к настоящей структуре `api-gateway/`

---

## 2. Обновление структуры

```bash
cd dgdo/backend/api-gateway

mkdir -p app/clients
mkdir -p app/grpc

# Скопировать сгенерированные protobuf-клиенты (если они есть)
cp -r ../generated/python/* app/grpc/ 2>/dev/null || echo "Protobuf файлы будут добавлены позже"
```

---

## 3. Установка зависимостей

```bash
pip install fastapi uvicorn pydantic python-dotenv httpx grpcio grpcio-tools
```

---

## 4. Клиент для gRPC (`app/clients/trip_request_client.py`)

```python
import grpc
from app.grpc import trip_request_pb2, trip_request_pb2_grpc
from app.schemas.trip_request import TripRequestCreate, TripRequestResponse
from uuid import uuid4
from datetime import datetime

class TripRequestClient:
    def __init__(self, channel: str = "localhost:50052"):
        self.channel = grpc.insecure_channel(channel)
        self.stub = trip_request_pb2_grpc.TripRequestServiceStub(self.channel)

    async def create_trip_request(self, request: TripRequestCreate) -> TripRequestResponse:
        """Вызов gRPC сервиса для создания TripRequest"""
        grpc_request = trip_request_pb2.CreateTripRequestCommand(
            passenger_id=request.passenger_id,
            origin=trip_request_pb2.Location(lat=request.origin.lat, lon=request.origin.lon),
            destination=trip_request_pb2.Location(lat=request.destination.lat, lon=request.destination.lon)
        )
        
        try:
            response = self.stub.CreateTripRequest(grpc_request)
            return TripRequestResponse(
                id=response.id,
                passenger_id=response.passenger_id,
                origin={"lat": response.origin.lat, "lon": response.origin.lon},
                destination={"lat": response.destination.lat, "lon": response.destination.lon},
                status="CREATED",
                created_at=datetime.utcnow(),
                version=response.version
            )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")
```

---

## 5. Обновлённый роутер (`app/api/v1/trip_request.py`)

```python
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.trip_request import TripRequestCreate, TripRequestResponse
from app.clients.trip_request_client import TripRequestClient

router = APIRouter()
client = TripRequestClient()   # В production используйте dependency injection

@router.post("/trip-requests/", response_model=TripRequestResponse)
async def create_trip_request(request: TripRequestCreate):
    """Создание запроса на поездку через gRPC"""
    try:
        trip = await client.create_trip_request(request)
        return trip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trip-requests/{trip_request_id}", response_model=TripRequestResponse)
async def get_trip_request(trip_request_id: str):
    """Получение TripRequest (пока заглушка — позже gRPC)"""
    # Здесь будет вызов TripRequestService.GetTripRequestById
    raise HTTPException(status_code=501, detail="Not implemented yet")
```

---

## 6. Обновлённый `app/main.py`

```python
from fastapi import FastAPI
from app.api.v1 import trip_request
from dotenv import load_dotenv
import logging

load_dotenv()

app = FastAPI(
    title="DG Do API Gateway",
    description="Единая точка входа для мобильных приложений DG Do (Худжанд)",
    version="0.3.0"
)

# Подключаем роутеры
app.include_router(trip_request.router, prefix="/api/v1", tags=["Trips"])

@app.get("/")
def root():
    return {
        "service": "DG Do API Gateway",
        "status": "running",
        "version": "0.3.0",
        "market": "Khujand",
        "connected_services": ["TripRequestService (gRPC)"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## 7. Запуск

```bash
cd dgdo/backend/api-gateway

# Запустить TripRequestService (если ещё не запущен)
# docker compose up trip_request_service -d

uvicorn app.main:app --reload --port 8000
```

---

## 8. Тестирование в Postman

**POST** `http://localhost:8000/api/v1/trip-requests/`

Body:
```json
{
  "passenger_id": "passenger_rahmatjon_001",
  "origin": { "lat": 40.2825, "lon": 69.6220 },
  "destination": { "lat": 40.2950, "lon": 69.6350 }
}
```

---

## Что мы приблизили к реальному проекту DG Do

- Использование **Pydantic** моделей, совместимых с protobuf
- Вызов **реального gRPC** сервиса из API Gateway
- Структура `app/clients/` — как в архитектурной документации
- Обработка ошибок gRPC
- Подготовка к добавлению `MatchingService` и `PricingService`
