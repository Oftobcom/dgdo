# ✅ **FULL ARCHITECTURE DIAGRAM — DG Do**

*(ASCII-диаграмма, читаема как на экране, так и в PDF/markdown)*

```
                                     ┌──────────────────────────────────────┐
                                     │              Mobile Apps             │
                                     │        iOS / Android / Web App       │
                                     └───────────────▲───────────────▲──────┘
                                                     │               │
                                                     │ HTTPS/REST    │
                                                     │               │
        ┌────────────────────────────────────────────┴───────────────┴────────────────────────────────────────────┐
        │                                        DG Do Backend (Modular Monolith)                                 │
        │                                               (Python FastAPI)                                          │
        │                                                                                                         │
        │  ┌──────────────────────────────┬───────────────────────────────┬────────────────────────────────────┐  │
        │  │ 1. Trip Lifecycle Module     │ 2. Driver State Module        │ 3. Passenger State Module          │  │
        │  │ ---------------------------- │ ----------------------------- │ ---------------------------------- │  │
        │  │ • create request             │ • online/offline              │ • passenger profiles               │  │
        │  │ • track trip stages          │ • current geolocation         │ • bans / rating                    │  │
        │  │ • cancellations              │ • availability window         │ • payment preferences              │  │
        │  └──────────────────────────────┴───────────────────────────────┴────────────────────────────────────┘  │
        │                                                                                                         │
        │  ┌──────────────────────────────┬───────────────────────────────┬────────────────────────────────────┐  │
        │  │ 4. ETA & Maps Adapter        │ 5. Pricing/Surge Module       │ 6. Analytics/Forecasting (optional)│  │
        │  │ ---------------------------- │ ----------------------------- │ ---------------------------------- │  │
        │  │ • external map providers     │ • dynamic price               │ • demand prediction (future)       │  │
        │  │ • distance/ETA               │ • surge zones                 │ • supply gaps                      │  │
        │  └──────────────────────────────┴───────────────────────────────┴────────────────────────────────────┘  │
        │                                                                                                         │
        │   ┌───────────────────────────────────────────┐              ┌───────────────────────────────────────┐  │
        │   │         gRPC Client (to C++ Engine)       │<────────────>│      gRPC Load Balancer (optional)    │  │
        │   └───────────────────────────────────────────┘              └───────────────────────────────────────┘  │
        │                                                                                                         │
        └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                              ▲
                                              │ gRPC
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DG Do Matching Engine (C++ High-Performance)                                 │
│─────────────────────────────────────────────────────────────────────────────────────────────────────────────────│
│  Core components:                                                                                               │
│  • KD-Tree / R-Tree spatial index for drivers                                                                   │
│  • ETA-aware scoring algorithm                                                                                  │
│  • Surge multipliers influence                                                                                  │
│  • Cancellation risk scoring                                                                                    │
│  • Priority queue for high-priority orders                                                                      │
│  • Multi-thread + lock-free queues                                                                              │
│                                                                                                                 │
│  Inputs via gRPC:                                                                                               │
│  • driver locations (stream)                                                                                    │
│  • passenger request                                                                                            │
│  • pricing/surge parameters                                                                                     │
│                                                                                                                 │
│  Output:                                                                                                        │
│  • best driver match (id, ETA, score)                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                              ▲
                                              │ Pub/Sub Updates
                                              │ (Redis Streams / Kafka later)
                                              ▼

                          ┌──────────────────────────┬──────────────────────────┬──────────────────────────┐
                          │        Redis Cache       │     Postgres SQL         │       Object Storage     │
                          │ ------------------------ │ ------------------------ │ ------------------------ │
                          │ • driver location cache  │ • rides                  │ • logs, backups          │
                          │ • surge zones            │ • cancellations history  │ • static data            │
                          │ • session management     │ • pricing                │ • map tiles (optional)   │
                          └──────────────────────────┴──────────────────────────┴──────────────────────────┘


                                               ┌────────────────────────────────────────────────────────────┐
                                               │                DevOps / Infrastructure                     │
                                               │ ---------------------------------------------------------- │
                                               │ • Docker / Docker Compose                                  │
                                               │ • WSL2 (Ubuntu 22.04)                                      │
                                               │ • CI/CD (GitHub Actions)                                   │
                                               │ • Central logs: Loki + Grafana                             │
                                               │ • Metrics: Prometheus                                      │
                                               │ • gRPC Load Balancer (Envoy)                               │
                                               └────────────────────────────────────────────────────────────┘
```

---

# ✅ **Explanation of the architecture**

Below is a quick interpretation of the diagram.

---

# **1. Mobile Apps → Backend (Monolith)**

Apps communicate via simple REST.

Backend contains **all business logic**:

* trip creation
* cancellations
* surge pricing
* ETA adapters
* state of drivers & passengers
* trip lifecycle

This allows rapid development.

---

# **2. Backend → Matching Engine (C++)**

Interaction is:

* backend collects request + context
* backend sends request to C++ engine via gRPC
* engine responds with best driver
* backend continues lifecycle

This isolates the **hi-load, low-latency hot path**.

---

# **3. C++ Engine internals**

* Multithreaded
* Lock-free queues
* Geospatial index (KD-Tree, R-Tree)
* Scoring model (ETA, surge, distance, driver score, etc.)
* Consistent handling of cancellations

---

# **4. Data Layer**

Redis: fast real-time data
Postgres: slow persistent storage
S3-like storage: logs, dumps

---

# **5. DevOps / Infra**

For local dev:

* Windows 10
* WSL2 Ubuntu
* Docker Desktop
* One-click run: `docker compose up --build`

---

# ✅ **Folders structure**

* dgdo/
*   backend/     ← modular monolith (Python)
*   matching/    ← C++ high-performance engine
*   grpc/        ← interface between backend and matching
*   data/        ← Postgres + Redis
*   infra/       ← Docker + WSL2 dev setup

