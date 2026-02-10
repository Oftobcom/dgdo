Here’s exactly what should go into your `ws/` folder for the DG Do Matching Engine MVP — keeping it clean, modular, and scalable.

---

# ✅ Purpose of the `ws/` folder

This folder should contain **all WebSocket-related logic** for real-time communication between:

* Passenger apps
* Driver apps
* Admin panel
* Back-end (FastAPI gateway + C++ matching engine events)

Since you're using **FastAPI** for the API Gateway, the WebSocket layer also lives there (or in a dedicated microservice if you want to scale later).

---

# 📁 Recommended folder structure

```
ws/
 ├── __init__.py
 ├── connections.py      # Store/manage active WS connections
 ├── events.py           # Define event types + payload schemas
 ├── manager.py          # WebSocketManager class (broadcast, send_to_user, etc.)
 ├── router.py           # FastAPI WebSocket endpoints
 ├── driver_handlers.py  # Send updates to drivers
 ├── passenger_handlers.py # Send updates to passengers
 ├── admin_handlers.py   # For admin panel subscriptions
 ├── protocol.py         # Unified WS message format
 └── utils.py            # Helpers
```

---

# 🌐 What the WebSockets should do in the MVP

### **1. Real-time driver location updates**

Drivers will send periodic GPS coordinates via WebSocket:

```json
{
  "type": "driver_location",
  "driver_id": "d123",
  "lat": 38.56,
  "lon": 68.78
}
```

The server stores it → pushes to passengers searching for nearby drivers.

---

### **2. Real-time ride status updates**

Passenger must instantly see:

* driver accepted
* driver is coming
* ride started
* ride completed

WebSocket event:

```json
{
  "type": "order_update",
  "order_id": 1001,
  "status": "accepted"
}
```

---

### **3. WebSockets for the Admin Panel**

Admin panel watches:

* driver statuses
* active trips
* assignments
* logging

WebSockets push metrics rather than polling REST.

---

### **4. Communication between Python (FastAPI) and C++ matching engine**

MVP approach:

* C++ matching engine emits events:

  * "new_order_assigned"
  * "order_canceled"
  * "driver_position_update"
* Python gateway receives them (via stdout/REST/ZeroMQ)
* Python pushes them to the WebSocket layer

This logic lives in:

```
ws/driver_handlers.py  
ws/passenger_handlers.py
```

---

# 🧠 Core file examples

### **manager.py**

The central connection manager:

```python
from typing import Dict, List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_passengers: Dict[int, WebSocket] = {}
        self.active_drivers: Dict[int, WebSocket] = {}

    async def connect_passenger(self, passenger_id: int, ws: WebSocket):
        await ws.accept()
        self.active_passengers[passenger_id] = ws

    async def connect_driver(self, driver_id: int, ws: WebSocket):
        await ws.accept()
        self.active_drivers[driver_id] = ws

    async def send_to_passenger(self, passenger_id: int, message: dict):
        ws = self.active_passengers.get(passenger_id)
        if ws:
            await ws.send_json(message)

    async def send_to_driver(self, driver_id: int, message: dict):
        ws = self.active_drivers.get(driver_id)
        if ws:
            await ws.send_json(message)
```

---

### **router.py**

Your WebSocket endpoints:

```python
from fastapi import APIRouter, WebSocket
from .manager import manager

router = APIRouter()

@router.websocket("/ws/passenger/{passenger_id}")
async def passenger_ws(ws: WebSocket, passenger_id: int):
    await manager.connect_passenger(passenger_id, ws)
    while True:
        data = await ws.receive_json()
        # handle passenger messages

@router.websocket("/ws/driver/{driver_id}")
async def driver_ws(ws: WebSocket, driver_id: int):
    await manager.connect_driver(driver_id, ws)
    while True:
        data = await ws.receive_json()
        # handle driver updates (GPS, etc.)
```

---

# 🧱 Minimal required WebSocket events (for MVP)

### For passengers:

| Event             | Purpose                              |
| ----------------- | ------------------------------------ |
| `order_update`    | driver accepted, en route, completed |
| `driver_location` | real-time marker on the map          |
| `estimate_update` | ETA updates                          |

### For drivers:

| Event          | Purpose                    |
| -------------- | -------------------------- |
| `new_order`    | assignment from C++ engine |
| `cancel_order` | passenger canceled         |

### For admin:

| Event           | Purpose                             |
| --------------- | ----------------------------------- |
| `system_stats`  | matching latency, orders per minute |
| `active_orders` | real-time monitoring                |

---

# 🧱 Summary — What should be inside `ws/`

Your `ws/` folder must contain:

### ✔ WebSocket connection manager

### ✔ WebSocket routes

### ✔ Handler functions for passenger/driver/admin

### ✔ Unified protocol (schema for all WS messages)

### ✔ Event dispatcher for C++ → WebSocket communication

### ✔ Real-time driver location processing

This is more than enough for the MVP — clean, scalable, and ready for high-load parts later.
