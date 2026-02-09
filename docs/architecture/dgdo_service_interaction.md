Below is an **ideal MVP-level Service Interaction Diagram** for the **DG Do project**, expressed as **one Mermaid diagram**, showing **who talks to whom, why, and in what direction**.

This diagram is **architecture-correct**, avoids circular dependencies, and matches the class → microservice mapping we already defined.

---

## DG Do — Service Interaction Diagram (MVP)

```mermaid
sequenceDiagram
    autonumber

    participant PassengerApp
    participant DriverApp
    participant IdentityService
    participant TripService
    participant PricingService
    participant MatchingService
    participant DriverService
    participant TelemetryService

    %% =========================
    %% Authentication
    %% =========================
    PassengerApp->>IdentityService: Authenticate (phone / token)
    IdentityService-->>PassengerApp: Auth OK (JWT)

    DriverApp->>IdentityService: Authenticate
    IdentityService-->>DriverApp: Auth OK (JWT)

    %% =========================
    %% Passenger creates trip request
    %% =========================
    PassengerApp->>TripService: Create TripRequest
    TripService->>PricingService: Calculate price snapshot
    PricingService-->>TripService: Pricing snapshot
    TripService->>TelemetryService: TripRequested event

    %% =========================
    %% Matching flow
    %% =========================
    TripService->>MatchingService: Request matching (TripRequest)
    MatchingService->>DriverService: Query available drivers
    DriverService-->>MatchingService: DriverStatus list

    loop Offer drivers sequentially
        MatchingService->>DriverApp: Trip offer
        DriverApp-->>MatchingService: Accept / Reject / Timeout
    end

    alt Match success
        MatchingService-->>TripService: MatchingSucceeded (driver_id)
        TripService->>TelemetryService: TripMatched event
    else Match failed
        MatchingService-->>TripService: MatchingFailed
        TripService->>TelemetryService: TripCancelled (no drivers)
    end

    %% =========================
    %% Trip execution
    %% =========================
    DriverApp->>TripService: Driver arrived
    TripService->>TelemetryService: TripStarted event

    DriverApp->>TripService: Trip finished
    TripService->>TelemetryService: TripCompleted event
```

---

## How to read this diagram

### 🔹 Authority boundaries

* **TripService is authoritative**
* **MatchingService decides, but does not persist trips**
* **DriverService owns realtime availability**
* **PricingService is snapshot-based**
* **TelemetryService is write-only**

---

## Why this interaction model is correct

### ✅ No circular dependencies

* Matching never updates Trip directly
* DriverService never touches Trip state

### ✅ Failure-tolerant

* Matching failure ≠ system failure
* Driver timeouts are isolated

### ✅ Realtime-ready

* DriverApp ↔ MatchingService via WebSocket
* Everything else can be async (Kafka later)

---

## MVP simplifications (intentional)

* Pricing called **once**
* Matching is sequential (no auctions yet)
* Telemetry is fire-and-forget
* No ML feedback loop inline

All of this can be upgraded **without breaking contracts**.
