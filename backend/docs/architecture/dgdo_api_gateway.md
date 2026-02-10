## What this API Gateway must do (MVP rules)

**It must:**

1. Be a **single entry point** for mobile app
2. Forward requests to backend services
3. Stay **thin** (NO business logic)
4. Be easy to delete or refactor later

**It must NOT (yet):**

* Contain complex auth logic
* Aggregate responses
* Cache
* Do rate limiting
* Do orchestration

👉 Think of it as a **smart reverse proxy with a brain the size of a peanut**.

---

## Technology choice (correct for DG Do)

* **Python 3.11+**
* **FastAPI**
* **httpx (async)**
* **Uvicorn**

This aligns perfectly with your existing stack and avoids future pain.

---

## Minimal project structure

```
api-gateway/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── trip.py
│   │   └── user.py
│   └── clients/
│       ├── trip_service.py
│       └── user_service.py
├── requirements.txt
└── Dockerfile
```

Nothing more. Nothing less.

---

## `requirements.txt`

```txt
fastapi
uvicorn
httpx
```

---

## `config.py`

Single place for service URLs.

```python
import os

TRIP_SERVICE_URL = os.getenv("TRIP_SERVICE_URL", "http://trip-service:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
```

---

## HTTP clients (key rule: gateway talks only via clients)

### `clients/trip_service.py`

```python
import httpx
from app.config import TRIP_SERVICE_URL

async def get_trip(trip_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TRIP_SERVICE_URL}/trips/{trip_id}")
        response.raise_for_status()
        return response.json()
```

---

### `clients/user_service.py`

```python
import httpx
from app.config import USER_SERVICE_URL

async def get_user(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        response.raise_for_status()
        return response.json()
```

---

## Routes = dumb forwarding only

### `routes/trip.py`

```python
from fastapi import APIRouter
from app.clients.trip_service import get_trip

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.get("/{trip_id}")
async def trip_details(trip_id: str):
    return await get_trip(trip_id)
```

---

### `routes/user.py`

```python
from fastapi import APIRouter
from app.clients.user_service import get_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}")
async def user_details(user_id: str):
    return await get_user(user_id)
```

---

## `main.py`

```python
from fastapi import FastAPI
from app.routes import trip, user

app = FastAPI(
    title="DG Do API Gateway",
    version="0.1.0"
)

app.include_router(trip.router)
app.include_router(user.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

---

## Dockerfile (minimal & correct)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Why this skeleton is safe (important)

✔ No premature abstractions
✔ No framework lock-in
✔ Easy to:

* add auth later
* add logging
* add rate limiting
* split into BFF if needed

✔ Easy to **throw away** if architecture evolves

This is exactly what you want at MVP stage.

---

## Clear “STOP POINT” for diagrams

In **all DG Do architecture diagrams**:

> **API Gateway is the STOP POINT for Mobile App**

Mobile App
→ **API Gateway (STOP)**
→ Internal Services

The mobile app **must never know** what happens after the gateway.
