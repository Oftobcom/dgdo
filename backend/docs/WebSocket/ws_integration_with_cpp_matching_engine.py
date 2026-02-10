# ws/ README
"""
Full WebSocket module for DG Do Matching Engine (MVP)
This package implements:
 - WebSocketManager (connections manager)
 - FastAPI websocket router
 - Event schema / protocol
 - Handlers for passenger, driver and admin
 - Bridge between C++ Matching Engine and Python gateway using ZeroMQ PUB/SUB

Dependencies (python):
 - fastapi
 - uvicorn[standard]
 - pyzmq
 - pydantic

Install:
    pip install fastapi uvicorn pyzmq pydantic

Run API gateway (example):
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

C++ side: example publisher using cppzmq (C++ ZeroMQ binding) is included at the bottom.

Folder layout (inside ws/):
 - __init__.py
 - manager.py
 - protocol.py
 - events.py
 - router.py
 - handlers.py
 - zmq_bridge.py
 - utils.py

Notes:
 - This code is designed for the MVP and is synchronous/asynchronous mixed using asyncio.
 - The C++ publisher publishes JSON messages on a ZeroMQ PUB socket. Python subscribes and dispatches to WS clients.

"""

# ---------------------------
# ws/__init__.py
# ---------------------------

# empty initializer

# ---------------------------
# ws/protocol.py
# ---------------------------

from typing import Literal, TypedDict, Optional
from pydantic import BaseModel

# Pydantic models for WS messages
class BaseMessage(BaseModel):
    type: str
    payload: dict

class DriverLocationPayload(BaseModel):
    driver_id: int
    lat: float
    lon: float
    speed: Optional[float]
    heading: Optional[float]

class OrderUpdatePayload(BaseModel):
    order_id: int
    status: Literal['requested','accepted','en_route','started','completed','canceled']
    driver_id: Optional[int]
    eta_seconds: Optional[int]

class NewOrderPayload(BaseModel):
    order_id: int
    passenger_id: int
    from_lat: float
    from_lon: float
    to_lat: float
    to_lon: float
    created_at: Optional[str]

# Convenience factory
def make_message(type: str, payload: dict) -> dict:
    return {"type": type, "payload": payload}

# ---------------------------
# ws/events.py
# ---------------------------

# Event type constants (centralized)
DRIVER_LOCATION = "driver_location"
ORDER_UPDATE = "order_update"
NEW_ORDER = "new_order"
CANCEL_ORDER = "cancel_order"
SYSTEM_STATS = "system_stats"

# ---------------------------
# ws/utils.py
# ---------------------------

import json
from typing import Any

def json_dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)

# ---------------------------
# ws/manager.py
# ---------------------------

import asyncio
from typing import Dict, Optional, Set
from fastapi import WebSocket
from collections import defaultdict

class WebSocketManager:
    def __init__(self):
        # maps id -> websocket
        self._passengers: Dict[int, WebSocket] = {}
        self._drivers: Dict[int, WebSocket] = {}
        self._admins: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect_passenger(self, passenger_id: int, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._passengers[passenger_id] = ws

    async def connect_driver(self, driver_id: int, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._drivers[driver_id] = ws

    async def connect_admin(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._admins.add(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            # remove from passengers/drivers/admin sets if present
            for k, v in list(self._passengers.items()):
                if v == ws:
                    del self._passengers[k]
            for k, v in list(self._drivers.items()):
                if v == ws:
                    del self._drivers[k]
            if ws in self._admins:
                self._admins.remove(ws)

    async def send_to_passenger(self, passenger_id: int, message: dict):
        ws = self._passengers.get(passenger_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                # best-effort disconnect
                await self.disconnect(ws)

    async def send_to_driver(self, driver_id: int, message: dict):
        ws = self._drivers.get(driver_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)

    async def broadcast_admin(self, message: dict):
        # send to all admin sockets
        to_remove = []
        async with self._lock:
            for ws in list(self._admins):
                try:
                    await ws.send_json(message)
                except Exception:
                    to_remove.append(ws)
            for ws in to_remove:
                self._admins.discard(ws)

    async def broadcast_nearby_passengers(self, lat: float, lon: float, radius_m: int, message: dict):
        # MVP: naive broadcast to all passengers. In production, index passengers by geohash or use spatial DB
        async with self._lock:
            for ws in list(self._passengers.values()):
                try:
                    await ws.send_json(message)
                except Exception:
                    await self.disconnect(ws)

# create single manager instance for import
manager = WebSocketManager()

# ---------------------------
# ws/handlers.py
# ---------------------------

from .protocol import make_message
from .events import DRIVER_LOCATION, ORDER_UPDATE, NEW_ORDER, CANCEL_ORDER, SYSTEM_STATS
from .manager import manager

# Handlers that will be called by the ZMQ bridge when C++ emits events

async def handle_driver_location(payload: dict):
    # payload: {driver_id, lat, lon, ...}
    msg = make_message(DRIVER_LOCATION, payload)
    # broadcast to nearby passengers — simplified: broadcast to all for MVP
    await manager.broadcast_nearby_passengers(payload['lat'], payload['lon'], radius_m=2000, message=msg)

async def handle_order_update(payload: dict):
    # payload: {order_id, status, driver_id?, passenger_id?}
    msg = make_message(ORDER_UPDATE, payload)
    passenger_id = payload.get('passenger_id')
    driver_id = payload.get('driver_id')
    # send to passenger
    if passenger_id is not None:
        await manager.send_to_passenger(passenger_id, msg)
    # send to driver
    if driver_id is not None:
        await manager.send_to_driver(driver_id, msg)
    # send a copy to admin panel
    await manager.broadcast_admin(msg)

async def handle_new_order(payload: dict):
    # payload: new order from C++ matching or dispatcher
    msg = make_message(NEW_ORDER, payload)
    # For MVP, send 'new_order' to the specific driver suggested
    suggested_driver = payload.get('suggested_driver_id')
    if suggested_driver:
        await manager.send_to_driver(suggested_driver, msg)
    # notify admins
    await manager.broadcast_admin(msg)

async def handle_cancel_order(payload: dict):
    msg = make_message(CANCEL_ORDER, payload)
    passenger_id = payload.get('passenger_id')
    driver_id = payload.get('driver_id')
    if passenger_id:
        await manager.send_to_passenger(passenger_id, msg)
    if driver_id:
        await manager.send_to_driver(driver_id, msg)
    await manager.broadcast_admin(msg)

async def handle_system_stats(payload: dict):
    msg = make_message(SYSTEM_STATS, payload)
    await manager.broadcast_admin(msg)

# event dispatcher map
EVENT_DISPATCH = {
    'driver_location': handle_driver_location,
    'order_update': handle_order_update,
    'new_order': handle_new_order,
    'cancel_order': handle_cancel_order,
    'system_stats': handle_system_stats,
}

# ---------------------------
# ws/zmq_bridge.py
# ---------------------------

# ZeroMQ bridge: subscribes to the matching engine and dispatches events to handlers

import asyncio
import json
import zmq
import zmq.asyncio
from .events import *
from .handlers import EVENT_DISPATCH

ZMQ_SUB_URL = "tcp://127.0.0.1:5556"  # C++ matching engine must PUB here

async def zmq_subscriber(loop: asyncio.AbstractEventLoop):
    ctx = zmq.asyncio.Context.instance()
    socket = ctx.socket(zmq.SUB)
    socket.connect(ZMQ_SUB_URL)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")  # subscribe to all

    while True:
        try:
            raw = await socket.recv()
            try:
                msg = json.loads(raw.decode('utf-8'))
            except Exception as e:
                # malformed message
                continue
            evt_type = msg.get('type')
            payload = msg.get('payload', {})
            handler = EVENT_DISPATCH.get(evt_type)
            if handler:
                # call handler but do not block loop — schedule a task
                asyncio.create_task(handler(payload))
        except Exception:
            await asyncio.sleep(0.1)

# helper to start bridge (to be called from main)

def start_zmq_bridge(loop: asyncio.AbstractEventLoop):
    loop.create_task(zmq_subscriber(loop))

# ---------------------------
# ws/router.py
# ---------------------------

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
from .manager import manager
from .protocol import make_message
import json

router = APIRouter()

@router.websocket('/ws/passenger/{passenger_id}')
async def passenger_ws(ws: WebSocket, passenger_id: int):
    await manager.connect_passenger(passenger_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            # Expect JSON text messages from passenger
            try:
                obj = json.loads(data)
            except Exception:
                continue
            # Basic passenger-originated messages
            typ = obj.get('type')
            payload = obj.get('payload', {})
            # Example: passenger requests cancel
            if typ == 'cancel_order':
                # In MVP, publish to C++ matching via HTTP or Redis. Here we forward to admin for inspection
                await manager.broadcast_admin(make_message('passenger_cancel_request', payload))
    except WebSocketDisconnect:
        await manager.disconnect(ws)

@router.websocket('/ws/driver/{driver_id}')
async def driver_ws(ws: WebSocket, driver_id: int):
    await manager.connect_driver(driver_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            try:
                obj = json.loads(data)
            except Exception:
                continue
            typ = obj.get('type')
            payload = obj.get('payload', {})
            # Handle driver-originated events: location updates, accept order
            if typ == 'driver_location':
                # Option A: forward to C++ engine via a REST API (not included) or to local redis/pubsub.
                # For MVP we'll publish to admin and also send to nearby passengers via manager
                await manager.broadcast_admin(make_message('driver_location_incoming', payload))
                # Also update passengers
                await manager.broadcast_nearby_passengers(payload.get('lat'), payload.get('lon'), 2000, make_message('driver_location', payload))
            elif typ == 'accept_order':
                # driver accepted; usually driver sends accept to C++ engine
                await manager.broadcast_admin(make_message('driver_accepted_order', payload))
    except WebSocketDisconnect:
        await manager.disconnect(ws)

@router.websocket('/ws/admin')
async def admin_ws(ws: WebSocket):
    await manager.connect_admin(ws)
    try:
        while True:
            # admin may not send much; keep alive
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)

# ---------------------------
# main.py (entrypoint for FastAPI app)
# ---------------------------

# Example FastAPI app wiring everything together

from fastapi import FastAPI
from .router import router as ws_router
from .zmq_bridge import start_zmq_bridge
import asyncio

app = FastAPI()
app.include_router(ws_router)

@app.on_event('startup')
async def startup_event():
    loop = asyncio.get_event_loop()
    start_zmq_bridge(loop)

@app.get('/')
async def root():
    return {"status": "ok", "ws": "/ws"}

# ---------------------------
# Example C++ matching engine publisher (minimal) - save as matching_publisher.cpp
# ---------------------------

# Paste this C++ example in a file named matching_publisher.cpp
# Requires cppzmq and zmq installed. This is a minimal example which publishes JSON events.

/*
#include <zmq.hpp>
#include <nlohmann/json.hpp>
#include <thread>
#include <chrono>

using json = nlohmann::json;

int main(){
    zmq::context_t ctx{1};
    zmq::socket_t pub{ctx, zmq::socket_type::pub};
    pub.bind("tcp://127.0.0.1:5556");

    int order_id = 1000;
    while(true){
        // Publish driver location
        json loc;
        loc["type"] = "driver_location";
        loc["payload"] = {
            {"driver_id", 42},
            {"lat", 38.54},
            {"lon", 68.78},
            {"speed", 5.2}
        };
        std::string s = loc.dump();
        zmq::message_t msg(s.begin(), s.end());
        pub.send(msg, zmq::send_flags::none);

        // publish new_order every 5 seconds
        json ord;
        ord["type"] = "new_order";
        ord["payload"] = {
            {"order_id", order_id++},
            {"passenger_id", 9001},
            {"from_lat", 38.5},
            {"from_lon", 68.7},
            {"to_lat", 38.6},
            {"to_lon", 68.9},
            {"suggested_driver_id", 42}
        };
        std::string s2 = ord.dump();
        zmq::message_t msg2(s2.begin(), s2.end());
        pub.send(msg2, zmq::send_flags::none);

        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
    return 0;
}
*/

# Build notes for the C++ example:
# - Use nlohmann/json (https://github.com/nlohmann/json) and cppzmq wrapper.
# - Example build (on linux):
#   g++ matching_publisher.cpp -o matching_publisher -lzmq

# ---------------------------
# Quick usage summary
# ---------------------------
# 1) Start Python FastAPI gateway (uvicorn main:app --reload)
# 2) Start matching_publisher (C++), it will PUB messages on tcp://127.0.0.1:5556
# 3) Connect passenger/driver/admin via WebSocket endpoints
#    - ws://localhost:8000/ws/passenger/9001
#    - ws://localhost:8000/ws/driver/42
#    - ws://localhost:8000/ws/admin
# 4) Messages from C++ will be routed to matching WS clients.

# ---------------------------
# END
# ---------------------------
