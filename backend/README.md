# dgdo

# DG Do — Open Source Ride-Hailing Platform

DG Do is an experimental open-source mobility-on-demand platform focused on simplicity, modularity, and learnability.

The project's goal is to demonstrate a working framework for a ride-hailing platform, including:
- Driver and passenger registration
- Trip creation
- Driver acceptance
- Status tracking
- Map integration (OpenStreetMap)

## Technologies
- **Backend:** C++, Python, FastAPI
- **Database:** PostgreSQL + PostGIS
- **Frontend:** React + MapLibre
- **Map:** OpenStreetMap (OSM)

## Purpose
The project is developed primarily for educational and research purposes. At the same time, we welcome and encourage any practical applications or real-world implementations that may emerge from its use.

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 🏃‍♂️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/dgdo.git
cd dgdo
````

### 2. Launch all services with Docker Compose

```bash
docker compose up --build
```

After a few moments, all services should be running locally.

---

## 🧩 Project Structure

```
dgdo/
├─ protos/                          # All proto definitions
│  ├─ common.proto
│  ├─ trip_request.proto
│  ├─ trip.proto
│  ├─ trip_service.proto
│  ├─ matching.proto
│  ├─ user.proto
│  ├─ driver_status.proto
│  ├─ admin.proto
│  ├─ telemetry.proto
│  ├─ ml_feedback.proto
│  ├─ pricing.proto
│  └─ notifications.proto
│
├─ generated/                       # files generated from proto-files
│  ├─ cpp/                          # C++ modules
│  │  ├─ admin.grpc.pb.cc
│  │  ├─ admin.grpc.pb.h
│  │  ├─ admin.pb.cc
│  │  ├─ admin.pb.h
│  │  └─ (etc.)
│  │
│  ├─ python/                       # Python modules
│  │  ├─ admin_pb2_grpc.py
│  │  ├─ admin_pb2.py
│  │  ├─ common_pb2_grpc.py
│  │  ├─ common_pb2.py
│  │  └─ (etc.)
│  │
├─ services/                        # Implementation code for each service
│  ├─ cpp/                          # C++ services
│  │  ├─ CMakeLists.txt
│  │  ├─ matching_server.cpp
│  │  └─ test_matching.py
│  │
│  ├─ python/                       # Python services
│  │  ├─ trip_request_server.py
│  │  ├─ trip_server.py
│  │  ├─ telemetry_server.py
│  │  ├─ ml_feedback_server.py
│  │  └─ common_utils.py
│  │
│  └─ (future: user_service, driver_status_service, admin_service, pricing_service, notifications_service)
│
├─ tests/                           # Test scripts
│  └─ test_full_flow.py
│
├─ docker/                          # Dockerfiles for all services
│  ├─ trip_request_service.Dockerfile
│  ├─ trip_service.Dockerfile
│  ├─ telemetry_service.Dockerfile
│  ├─ ml_feedback_service.Dockerfile
│  └─ matching_service.Dockerfile
│
├─ docker-compose.yml               # Compose all services
├─ requirements.txt                 # Python dependencies
└─ README.md

```
---

## Build order

```bash
# Base image
docker build -t dgdo-python-base -f docker/python_base.Dockerfile .

# Python services
docker build -t dgdo-trip-request -f docker/trip_request_service.Dockerfile .
docker build -t dgdo-trip-service -f docker/trip_service.Dockerfile .
docker build -t dgdo-telemetry -f docker/telemetry_service.Dockerfile .
docker build -t dgdo-ml-feedback -f docker/ml_feedback_service.Dockerfile .

# C++ MatchingService
docker build -t dgdo-matching -f docker/matching_service.Dockerfile .
```

---

## 🔧 Local Services & Access Links

| Service             | URL / Port                                          |
| ------------------- | --------------------------------------------------- |
| FastAPI API Gateway | [http://localhost:8000](http://localhost:8000)      |
| C++ Matching Engine | [http://localhost:8001](http://localhost:8001)      |
| Admin Panel         | [http://localhost:8002](http://localhost:8002)      |
| Postgres Database   | localhost:5432                                      |

> **Tip:** Use your browser to access the web services (API docs available at `/docs` on FastAPI).

---

## ⚡ Quick Notes

* **API Gateway:** Handles REST + WebSocket requests from passengers, drivers, and admin.
* **Matching Engine:** C++ service for high-load driver assignment logic.
* **Admin Panel:** Minimal interface for testing/monitoring.
* **Database:** PostgreSQL stores passengers, drivers, and trips.

---

## 📌 Contact / Contributing

* Contributions are welcome! Please open issues or pull requests.
* Follow standard GitHub fork → feature branch → pull request workflow.

---

Here’s a **mapping of current proto-files to MVP functionality**, showing which features are fully covered, partially covered, or optional for alpha launch. 
This will help **prioritize work and see gaps clearly**.

| Proto File              | MVP Feature(s) Covered                   | Status / Notes                                                                            |
| ----------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------- |
| **common.proto**        | `Location`, `Metadata`                   | ✅ Fully covered; used in Trip, TripRequest, Matching                                     |
| **trip.proto**          | Trip entity, FSM fields                  | ✅ Fully covered; immutable fields, status, timestamps                                    |
| **trip_service.proto**  | Trip creation, updates, cancellation     | ✅ Fully covered; idempotency via `trip_request_id`                                       |
| **trip_request.proto**  | Create/Cancel TripRequest                | ✅ Fully covered; single active request per passenger, cold-start logic stubbed           |
| **matching.proto**      | Candidate drivers, probabilities         | ✅ Fully covered for deterministic MVP; supports max_candidates and seed-based replay     |
| **driver_status.proto** | Driver availability & status             | ✅ Partially; could include real-time streaming later, but sufficient for static matching |
| **user.proto**          | Passenger registration / info            | ✅ Fully covered for MVP; basic fields enough for login/register                          |
| **admin.proto**         | Admin panel queries                      | ✅ Partially; can expand later, basic trip listing is enough                              |
| **notifications.proto** | Push notifications                       | ⚪ Optional for alpha; could be stubbed or delayed                                        |
| **telemetry.proto**     | Event logging (Trip, Matching, failures) | ✅ Fully covered; essential for debugging & ML                                            |
| **ml_feedback.proto**   | Candidate distribution logging           | ⚪ Optional for MVP; can stub logging for now                                             |
| **pricing.proto**       | Fare calculation                         | ⚪ Optional for alpha; minimal static fares ok                                            |
| **common.proto**        | Locations & metadata                     | ✅ Required dependency for all services                                                   |

### ✅ MVP Summary

* **Fully covered**: core Trip & TripRequest flows, MatchingService deterministic selection, TripService FSM, basic telemetry
* **Partially covered**: Admin panel (listing trips), driver availability, user registration (basic fields)
* **Optional / can be stubbed**: Notifications, pricing logic, ML feedback, real-time driver streaming
