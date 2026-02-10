# ws/gRPC integration + Docker Compose
"""
This repository fragment provides a full WebSocket module for DG Do Matching Engine
integrated with a C++ matching engine using gRPC streaming. It also includes Dockerfile
and docker-compose.yml fragments to run the Python FastAPI gateway and a minimal
C++ example publisher (gRPC server) inside containers for local development.

Structure placed inside ws/ (Python gateway code) and grpc_proto/ (proto file).

Notes:
 - Python uses async gRPC client (grpc.aio) to connect to the C++ matching engine gRPC server.
 - The C++ example implements a simple gRPC server that streams events periodically.
 - The Python FastAPI gateway receives the stream and dispatches to WebSocket clients.

Dependencies (Python):
 - fastapi
 - uvicorn[standard]
 - grpcio
 - grpcio-tools
 - pydantic

Install (python):
    pip install fastapi uvicorn grpcio grpcio-tools pydantic

Run (dev):
 - Build C++ server with Dockerfile (provided) or compile locally
 - Start docker-compose: `docker compose up --build`

The code below contains:
 - proto file (events.proto)
 - Python: ws/manager.py, ws/protocol.py, ws/events.py, ws/handlers.py, ws/grpc_bridge.py, ws/router.py, ws/main.py
 - C++: example server (matching_publisher.cpp) and CMakeLists.txt
 - Dockerfiles and docker-compose.yml

For brevity in this file we include the full contents as text that you can split into files.

"""

# ---------------------------
# grpc_proto/events.proto
# ---------------------------

PROTO_CONTENT = r"""
syntax = "proto3";
package dgdo.events;

message SubscribeRequest {
  string client_name = 1; // optional
}

message Event {
  string type = 1; // e.g. "driver_location", "new_order", "order_update"
  string payload_json = 2; // JSON-encoded payload
}

service MatchingPublisher {
  // Server-side streaming of events to subscribers
  rpc StreamEvents(SubscribeRequest) returns (stream Event) {}
}
"""

# ---------------------------
# ws/protocol.py
# ---------------------------

PROTOCOL_PY = r"""
from typing import Literal, Optional
from pydantic import BaseModel

class BaseMessage(BaseModel):
    type: str
    payload: dict

class DriverLocationPayload(BaseMessage):
    driver_id: int
    lat: float
    lon: float
    speed: Optional[float]
    heading: Optional[float]

# factory
def make_message(type: str, payload: dict) -> dict:
    return {"type": type, "payload": payload}
"""

# ---------------------------
# ws/events.py
# ---------------------------

EVENTS_PY = r"""
DRIVER_LOCATION = "driver_location"
ORDER_UPDATE = "order_update"
NEW_ORDER = "new_order"
CANCEL_ORDER = "cancel_order"
SYSTEM_STATS = "system_stats"
"""

# ---------------------------
# ws/manager.py
# ---------------------------

MANAGER_PY = r"""
import asyncio
from fastapi import WebSocket
from typing import Dict, Set

class WebSocketManager:
    def __init__(self):
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
                await self.disconnect(ws)

    async def send_to_driver(self, driver_id: int, message: dict):
        ws = self._drivers.get(driver_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)

    async def broadcast_admin(self, message: dict):
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
        async with self._lock:
            for ws in list(self._passengers.values()):
                try:
                    await ws.send_json(message)
                except Exception:
                    await self.disconnect(ws)

manager = WebSocketManager()
"""

# ---------------------------
# ws/handlers.py
# ---------------------------

HANDLERS_PY = r"""
from .protocol import make_message
from .events import *
from .manager import manager

async def handle_driver_location(payload: dict):
    msg = make_message(DRIVER_LOCATION, payload)
    await manager.broadcast_nearby_passengers(payload.get('lat'), payload.get('lon'), 2000, msg)

async def handle_order_update(payload: dict):
    msg = make_message(ORDER_UPDATE, payload)
    passenger_id = payload.get('passenger_id')
    driver_id = payload.get('driver_id')
    if passenger_id is not None:
        await manager.send_to_passenger(passenger_id, msg)
    if driver_id is not None:
        await manager.send_to_driver(driver_id, msg)
    await manager.broadcast_admin(msg)

async def handle_new_order(payload: dict):
    msg = make_message(NEW_ORDER, payload)
    suggested_driver = payload.get('suggested_driver_id')
    if suggested_driver:
        await manager.send_to_driver(suggested_driver, msg)
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

EVENT_DISPATCH = {
    'driver_location': handle_driver_location,
    'order_update': handle_order_update,
    'new_order': handle_new_order,
    'cancel_order': handle_cancel_order,
}
"""

# ---------------------------
# ws/grpc_bridge.py (python async gRPC client)
# ---------------------------

GRPC_BRIDGE_PY = r"""
import asyncio
import json
import grpc
from typing import Optional

# import generated classes
from grpc_proto import events_pb2, events_pb2_grpc
from .handlers import EVENT_DISPATCH

GRPC_TARGET = "matching_publisher:50051"  # docker-compose service name:port

async def start_grpc_bridge(loop: Optional[asyncio.AbstractEventLoop] = None):
    if loop is None:
        loop = asyncio.get_event_loop()

    # use insecure channel for local dev
    async with grpc.aio.insecure_channel(GRPC_TARGET) as channel:
        stub = events_pb2_grpc.MatchingPublisherStub(channel)
        req = events_pb2.SubscribeRequest(client_name="python_gateway")
        try:
            stream = stub.StreamEvents(req)
            async for event in stream:
                # event.type, event.payload_json
                try:
                    payload = json.loads(event.payload_json)
                except Exception:
                    payload = {}
                handler = EVENT_DISPATCH.get(event.type)
                if handler:
                    # schedule handler
                    asyncio.create_task(handler(payload))
        except grpc.aio.AioRpcError as e:
            # transient error — retry with backoff
            await asyncio.sleep(1)
            asyncio.create_task(start_grpc_bridge(loop))
"""

# ---------------------------
# ws/router.py
# ---------------------------

ROUTER_PY = r"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from .manager import manager
from .protocol import make_message

router = APIRouter()

@router.websocket('/ws/passenger/{passenger_id}')
async def passenger_ws(ws: WebSocket, passenger_id: int):
    await manager.connect_passenger(passenger_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            try:
                obj = json.loads(data)
            except Exception:
                continue
            typ = obj.get('type')
            payload = obj.get('payload', {})
            if typ == 'cancel_order':
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
            if typ == 'driver_location':
                await manager.broadcast_admin(make_message('driver_location_incoming', payload))
                await manager.broadcast_nearby_passengers(payload.get('lat'), payload.get('lon'), 2000, make_message('driver_location', payload))
            elif typ == 'accept_order':
                await manager.broadcast_admin(make_message('driver_accepted_order', payload))
    except WebSocketDisconnect:
        await manager.disconnect(ws)

@router.websocket('/ws/admin')
async def admin_ws(ws: WebSocket):
    await manager.connect_admin(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)
"""

# ---------------------------
# ws/main.py
# ---------------------------

MAIN_PY = r"""
from fastapi import FastAPI
from .router import router as ws_router
from .grpc_bridge import start_grpc_bridge
import asyncio

app = FastAPI()
app.include_router(ws_router)

@app.on_event('startup')
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(start_grpc_bridge(loop))

@app.get('/')
async def root():
    return {"status": "ok"}
"""

# ---------------------------
# grpc_proto Python generation hint
# ---------------------------

PROTO_GEN_HINT = r"""
# generate Python grpc code (run in project root):
# python -m grpc_tools.protoc -I./grpc_proto --python_out=./grpc_proto --grpc_python_out=./grpc_proto ./grpc_proto/events.proto
"""

# ---------------------------
# C++ example server (matching_publisher) using gRPC C++
# ---------------------------

CPP_SERVER = r"""
// matching_publisher.cpp
// Minimal gRPC server that streams events periodically to subscribers.
// Requires gRPC C++ and protobuf installed. This is example code; adapt for your matching engine.

#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <chrono>
#include <grpcpp/grpcpp.h>
#include "events.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using grpc::ServerWriter;

using dgdo::events::MatchingPublisher;
using dgdo::events::SubscribeRequest;
using dgdo::events::Event;

class MatchingPublisherServiceImpl final : public MatchingPublisher::Service {
public:
    Status StreamEvents(ServerContext* context, const SubscribeRequest* request,
                        ServerWriter<Event>* writer) override {
        int counter = 0;
        while (!context->IsCancelled()) {
            Event ev;
            if (counter % 2 == 0) {
                ev.set_type("driver_location");
                std::string payload = R"({"driver_id":42,"lat":38.54,"lon":68.78,"speed":5.2})";
                ev.set_payload_json(payload);
            } else {
                ev.set_type("new_order");
                std::string payload = R"({"order_id":1001,"passenger_id":9001,"from_lat":38.5,"from_lon":68.7,"to_lat":38.6,"to_lon":68.9,"suggested_driver_id":42})";
                ev.set_payload_json(payload);
            }
            writer->Write(ev);
            counter++;
            std::this_thread::sleep_for(std::chrono::seconds(3));
        }
        return Status::OK;
    }
};

void RunServer(const std::string& server_address) {
    MatchingPublisherServiceImpl service;
    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;
    server->Wait();
}

int main(int argc, char** argv) {
    std::string address("0.0.0.0:50051");
    RunServer(address);
    return 0;
}
"""

# ---------------------------
# CMakeLists.txt for C++ server
# ---------------------------

CMAKE_CONTENT = r"""
cmake_minimum_required(VERSION 3.5)
project(matching_publisher)

find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

set(CMAKE_CXX_STANDARD 14)

include_directories(${Protobuf_INCLUDE_DIRS})

set(PROTO_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../grpc_proto)

# generate sources from proto (assumes protoc + grpc plugins installed in system)
execute_process(COMMAND protoc --cpp_out=. --grpc_out=. --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` ${PROTO_SRC_DIR}/events.proto WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_executable(matching_publisher matching_publisher.cpp events.pb.cc events.grpc.pb.cc)

target_link_libraries(matching_publisher PRIVATE grpc++ protobuf)
"""

# ---------------------------
# Dockerfile for Python gateway
# ---------------------------

DOCKERFILE_PY = r"""
# Dockerfile for Python FastAPI gateway
FROM python:3.11-slim

WORKDIR /app

# Install build deps for grpc_tools if needed
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY ./ws /app/ws
COPY ./grpc_proto /app/grpc_proto
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# generate grpc python code
RUN python -m grpc_tools.protoc -I./grpc_proto --python_out=./grpc_proto --grpc_python_out=./grpc_proto ./grpc_proto/events.proto

EXPOSE 8000
CMD ["uvicorn", "ws.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# ---------------------------
# requirements.txt
# ---------------------------

REQUIREMENTS_TXT = r"""
fastapi
uvicorn[standard]
grpcio
grpcio-tools
pydantic
"""

# ---------------------------
# Dockerfile for C++ server
# ---------------------------

DOCKERFILE_CPP = r"""
# Dockerfile for C++ gRPC server (matching_publisher)
FROM debian:bookworm-slim

# Install build tools and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    ca-certificates \
    wget \
    pkg-config \
    autoconf \
    libtool \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install protobuf and grpc from source (simplified for example) - in production use prebuilt packages
WORKDIR /tmp
RUN git clone --recurse-submodules -b v1.54.0 https://github.com/grpc/grpc && \
    cd grpc && mkdir -p cmake/build && cd cmake/build && \
    cmake ../.. && make -j2 && make install && cd / && rm -rf /tmp/grpc

# Copy server source
WORKDIR /app
COPY ./matching_publisher /app/matching_publisher
COPY ./grpc_proto /app/grpc_proto

# Build server (assumes CMakeLists placed in matching_publisher)
RUN mkdir -p /app/build && cd /app/build && cmake ../matching_publisher && make -j2

EXPOSE 50051
CMD ["/app/build/matching_publisher"]
"""

# ---------------------------
# docker-compose.yml
# ---------------------------

DOCKER_COMPOSE = r"""
version: '3.8'
services:
  python_gateway:
    build:
      context: .
      dockerfile: Dockerfile.py
    container_name: python_gateway
    volumes:
      - ./ws:/app/ws:ro
      - ./grpc_proto:/app/grpc_proto:ro
    ports:
      - "8000:8000"
    depends_on:
      - matching_publisher

  matching_publisher:
    build:
      context: .
      dockerfile: Dockerfile.cpp
    container_name: matching_publisher
    ports:
      - "50051:50051"
"""

# ---------------------------
# README run steps (string to include in doc)
# ---------------------------

README_RUN = r"""
How to use (local development):

1. Place files into repository:
   - grpc_proto/events.proto (proto content)
   - ws/ (all Python files: protocol.py, events.py, manager.py, handlers.py, grpc_bridge.py, router.py, main.py)
   - matching_publisher/ (C++: matching_publisher.cpp and CMakeLists.txt)
   - Dockerfile.py (Python gateway Dockerfile), Dockerfile.cpp (C++ Dockerfile)
   - requirements.txt
   - docker-compose.yml

2. Build and run with docker-compose (will build both images):
   docker compose up --build

3. Access WebSocket endpoints:
   - ws://localhost:8000/ws/passenger/{passenger_id}
   - ws://localhost:8000/ws/driver/{driver_id}
   - ws://localhost:8000/ws/admin

Notes and caveats:
 - The C++ Dockerfile builds gRPC from source; this is heavy and may take long. For CI or production, prefer prebuilt packages or cross-compile.
 - Alternatively you can run the C++ server locally (outside Docker) if you have gRPC installed.
 - The proto Python stubs are generated at Docker image build time for the Python gateway. For local dev you can generate them with grpc_tools.protoc as shown in the project.

"""

# ---------------------------
# Create consolidated content for the canvas file
# ---------------------------

FULL_DOC = """
Files included (place each block into the corresponding file):

1) grpc_proto/events.proto

""" + PROTO_CONTENT + """

2) ws/protocol.py

""" + PROTOCOL_PY + """

3) ws/events.py

""" + EVENTS_PY + """

4) ws/manager.py

""" + MANAGER_PY + """

5) ws/handlers.py

""" + HANDLERS_PY + """

6) ws/grpc_bridge.py

""" + GRPC_BRIDGE_PY + """

7) ws/router.py

""" + ROUTER_PY + """

8) ws/main.py

""" + MAIN_PY + """

9) grpc_proto generation hint

""" + PROTO_GEN_HINT + """

10) C++ server example (matching_publisher/matching_publisher.cpp)

""" + CPP_SERVER + """

11) C++ CMakeLists.txt (matching_publisher/CMakeLists.txt)

""" + CMAKE_CONTENT + """

12) Dockerfile for Python gateway (Dockerfile.py)

""" + DOCKERFILE_PY + """

13) requirements.txt

""" + REQUIREMENTS_TXT + """

14) Dockerfile for C++ server (Dockerfile.cpp)

""" + DOCKERFILE_CPP + """

15) docker-compose.yml

""" + DOCKER_COMPOSE + """

16) README run steps

""" + README_RUN + """

# Write the doc content

FULL_DOC
