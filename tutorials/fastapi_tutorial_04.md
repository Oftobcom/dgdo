# FastAPI Tutorial 04 — Полноценный endpoint `/trips/create` с Workflow

Теперь мы приближаемся к **реальному production-коду** DG Do.  
В этом уроке мы создадим **главный эндпоинт** мобильного приложения — создание поездки с полным оркестрированием через `TripWorkflow`.

---

## 1. Цель урока

Научиться:
- Интегрировать несколько gRPC-сервисов (`TripRequest`, `Matching`, `Pricing`)
- Использовать `TripWorkflow` внутри API Gateway
- Добавлять JWT-авторизацию
- Создавать полноценный бизнес-эндпоинт `/trips/create`

---

## 2. Установка зависимостей

```bash
pip install fastapi uvicorn pydantic python-dotenv httpx grpcio python-jose[cryptography] passlib[bcrypt]
```

---

## 3. Pydantic модели (`app/schemas/trip.py`)

```python
from pydantic import BaseModel
from datetime import datetime
from app.schemas.trip_request import Location

class TripCreateRequest(BaseModel):
    passenger_id: str
    origin: Location
    destination: Location
    ab_test_group: str = None   # для тестирования surge

class TripResponse(BaseModel):
    trip_id: str
    trip_request_id: str
    driver_id: str
    status: str
    passenger_fare_total: float
    created_at: datetime
```

---

## 4. JWT Auth (`app/core/security.py`)

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "dgdo-khujand-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def create_access_token(subject: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

---

## 5. Клиенты gRPC (`app/clients/`)

```python
# app/clients/pricing_client.py
import grpc
from app.grpc import pricing_pb2, pricing_pb2_grpc

class PricingClient:
    def __init__(self, channel="localhost:50056"):
        self.channel = grpc.insecure_channel(channel)
        self.stub = pricing_pb2_grpc.PricingServiceStub(self.channel)

    def calculate_price(self, trip_request_id: str, passenger_id: str, driver_id: str, origin, destination):
        req = pricing_pb2.PriceCalculationRequest(
            trip_request_id=trip_request_id,
            passenger_id=passenger_id,
            matched_driver_id=driver_id,
            origin=pricing_pb2.Location(lat=origin.lat, lon=origin.lon),
            destination=pricing_pb2.Location(lat=destination.lat, lon=destination.lon),
            estimated_distance_meters=1200,
            estimated_duration_seconds=900,
            demand_multiplier=1.0,
        )
        return self.stub.CalculatePrice(req)
```

(Аналогично создайте `matching_client.py`)

---

## 6. Основной Workflow в Gateway (`app/core/trip_workflow_gateway.py`)

```python
from app.clients.trip_request_client import TripRequestClient
from app.clients.matching_client import MatchingClient
from app.clients.pricing_client import PricingClient
from app.schemas.trip import TripResponse

class TripWorkflowGateway:
    def __init__(self):
        self.trip_request_client = TripRequestClient()
        self.matching_client = MatchingClient()
        self.pricing_client = PricingClient()

    async def create_trip(self, passenger_id: str, origin, destination, ab_test_group=None):
        # 1. Создаём TripRequest
        trip_request = await self.trip_request_client.create_trip_request(...)

        # 2. Matching
        match_resp = self.matching_client.get_candidates(trip_request.id, origin, destination)

        if not match_resp.candidates:
            raise Exception("No drivers available")

        driver_id = match_resp.candidates[0].driver_id

        # 3. Pricing
        price_resp = self.pricing_client.calculate_price(
            trip_request.id, passenger_id, driver_id, origin, destination
        )

        # 4. Создаём Trip (через TripService)
        # ... (вызов TripService.CreateTrip)

        return TripResponse(
            trip_id="trip_" + trip_request.id[:8],
            trip_request_id=trip_request.id,
            driver_id=driver_id,
            status="ACCEPTED",
            passenger_fare_total=price_resp.passenger_fare_total,
            created_at=datetime.utcnow()
        )
```

---

## 7. Полноценный роутер (`app/api/v1/trips.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.trip import TripCreateRequest, TripResponse
from app.core.trip_workflow_gateway import TripWorkflowGateway
from app.core.security import get_current_user

router = APIRouter()
workflow = TripWorkflowGateway()

@router.post("/trips/create", response_model=TripResponse)
async def create_trip(
    request: TripCreateRequest,
    current_user: str = Depends(get_current_user)
):
    """Главный endpoint создания поездки"""
    if current_user != request.passenger_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        trip = await workflow.create_trip(
            passenger_id=request.passenger_id,
            origin=request.origin,
            destination=request.destination,
            ab_test_group=request.ab_test_group
        )
        return trip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 8. Обновление `app/main.py`

```python
from app.api.v1 import trip_request, trips   # добавили trips

app.include_router(trips.router, prefix="/api/v1", tags=["Trips"])
```

---

## 9. Запуск и тестирование

```bash
cd dgdo/backend/api-gateway
uvicorn app.main:app --reload --port 8000
```

**POST** `http://localhost:8000/api/v1/trips/create`

С заголовком:
```
Authorization: Bearer <your-jwt-token>
```

Body:
```json
{
  "passenger_id": "passenger_rahmatjon_001",
  "origin": {"lat": 40.2825, "lon": 69.6220},
  "destination": {"lat": 40.2950, "lon": 69.6350}
}
```
