# FastAPI Tutorial 05 — Production-Ready Trip Creation с Realtime, Rate Limiting и Observability

Это **финальный** практический урок серии.  
Мы реализуем **полноценный production-like** кусок **API Gateway** для DG Do, максимально приближенный к архитектурной документации проекта.

---

## 1. Цель урока

Научиться:
- Полноценному **Saga / Workflow** внутри Gateway
- Интеграции с `MatchingService`, `PricingService`, `DriverStatusService`
- **JWT-авторизации**
- **WebSocket** realtime обновлениям статуса поездки
- **Rate Limiting** и базовой observability (структурированные логи)
- Структуре, соответствующей `dgdo_api_gateway.md`

---

## 2. Финальная структура `api-gateway/`

```bash
api-gateway/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   ├── trip_workflow.py
│   │   └── middleware.py
│   ├── clients/
│   │   ├── trip_request_client.py
│   │   ├── matching_client.py
│   │   ├── pricing_client.py
│   │   └── driver_status_client.py
│   ├── schemas/
│   │   ├── trip.py
│   │   └── websocket.py
│   ├── api/v1/
│   │   ├── trips.py
│   │   └── websocket.py
│   └── utils/
│       └── logging.py
├── requirements.txt
└── Dockerfile
```

---

## 3. Ключевые зависимости (`requirements.txt`)

```txt
fastapi
uvicorn
pydantic
python-dotenv
httpx
grpcio
python-jose[cryptography]
passlib[bcrypt]
slowapi          # Rate Limiting
structlog
```

---

## 4. JWT + Rate Limiting (`app/core/middleware.py` + `security.py`)

```python
# app/core/security.py (расширенная версия)
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

# ... (create_access_token, get_current_user как в предыдущем уроке)

# Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Dependency
def get_current_passenger(current_user: str = Depends(get_current_user)):
    # Здесь можно проверить роль
    return current_user
```

---

## 5. Полноценный Workflow (`app/core/trip_workflow.py`)

```python
from app.clients import TripRequestClient, MatchingClient, PricingClient, DriverStatusClient
from app.schemas.trip import TripCreateRequest, TripResponse
import structlog
from datetime import datetime

logger = structlog.get_logger()

class TripWorkflow:
    def __init__(self):
        self.trip_req_client = TripRequestClient()
        self.matching_client = MatchingClient()
        self.pricing_client = PricingClient()
        self.driver_client = DriverStatusClient()

    async def create_full_trip(self, req: TripCreateRequest, passenger_id: str) -> TripResponse:
        try:
            # 1. TripRequest
            trip_req = await self.trip_req_client.create(req)

            # 2. Matching
            match_resp = self.matching_client.get_candidates(trip_req.id, req.origin, req.destination)
            if not match_resp.candidates:
                raise Exception("No available drivers")
            driver_id = match_resp.candidates[0].driver_id

            # 3. Pricing (с учётом surge из config)
            price_resp = self.pricing_client.calculate(trip_req.id, passenger_id, driver_id, req.origin, req.destination)

            # 4. Driver Status
            await self.driver_client.assign_driver(driver_id, trip_req.id)

            # 5. Create Trip
            trip = await self.trip_service_client.create_trip(...)  # вызов TripService

            logger.info("trip_created", trip_id=trip.id, driver_id=driver_id, passenger_id=passenger_id)
            return TripResponse(**trip.dict(), passenger_fare_total=price_resp.passenger_fare_total)

        except Exception as e:
            logger.error("trip_creation_failed", error=str(e), passenger_id=passenger_id)
            # Компенсация (вызвать rollback)
            raise
```

---

## 6. Главный эндпоинт (`app/api/v1/trips.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from slowapi import Limiter
from app.core.trip_workflow import TripWorkflow
from app.core.security import get_current_passenger
from app.schemas.trip import TripCreateRequest, TripResponse

router = APIRouter()
workflow = TripWorkflow()
limiter = Limiter(key_func=get_remote_address)

@router.post("/trips/create", response_model=TripResponse)
@limiter.limit("10/minute")   # Rate limiting
async def create_trip(
    request: TripCreateRequest,
    current_user: str = Depends(get_current_passenger)
):
    """Создание поездки — главный бизнес-эндпоинт DG Do"""
    if current_user != request.passenger_id:
        raise HTTPException(403, "Access denied")

    try:
        trip = await workflow.create_full_trip(request, current_user)
        return trip
    except Exception as e:
        raise HTTPException(500, detail=str(e))
```

---

## 7. WebSocket Realtime (`app/api/v1/websocket.py`)

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/trip/{trip_id}")
async def trip_status_websocket(websocket: WebSocket, trip_id: str):
    await manager.connect(websocket, trip_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Можно обрабатывать сообщения от клиента
            await manager.broadcast_to_trip(trip_id, f"Status update: {data}")
    except WebSocketDisconnect:
        manager.disconnect(trip_id)
```

---

## 8. Connection Manager (`app/core/connection_manager.py`)

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trip_id: str):
        await websocket.accept()
        if trip_id not in self.active_connections:
            self.active_connections[trip_id] = []
        self.active_connections[trip_id].append(websocket)

    def disconnect(self, trip_id: str):
        self.active_connections.pop(trip_id, None)

    async def broadcast_to_trip(self, trip_id: str, message: str):
        if trip_id in self.active_connections:
            for connection in self.active_connections[trip_id]:
                await connection.send_text(message)
```

---

## 9. Запуск и проверка

```bash
uvicorn app.main:app --reload --port 8000
```

**Тестирование:**
- Создание поездки (`POST /api/v1/trips/create`)
- Подключение по WebSocket: `ws://localhost:8000/api/v1/ws/trip/{trip_id}`
