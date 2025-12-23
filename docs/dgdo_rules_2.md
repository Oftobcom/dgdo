# DG Do — Canonical Domain Laws (v0.2, Production-Oriented)

> **Scope**
> These laws define **non-negotiable invariants** of the DG Do platform.
> Any violation is a **production-blocking defect**.
> Experimental behavior is allowed **only outside production**.

---

## 0. System Design Principles (Global)

These principles apply to **every service, API, and data model**.

### 0.1 Architectural Principles

* **Single Responsibility (SRP):** each service owns exactly one domain concern.
* **Explicit Contracts:** `.proto` files are the only source of truth.
* **Loose Coupling:** services interact only via versioned APIs/events.
* **High Cohesion:** domain logic never leaks across service boundaries.

### 0.2 Operational Principles

* **All operations are idempotent.**
* **All state transitions are explicit and auditable.**
* **All services are containerized and stateless** (except storage).
* **Failure is expected; undefined behavior is forbidden.**

---

## 1. TripRequest Domain Laws

### 1.1 Purpose

`TripRequest` represents **passenger intent**, not a financial or operational commitment.

### 1.2 Invariants

1. A `TripRequest` **may exist without a driver**.
2. A passenger may have **at most one ACTIVE TripRequest**.
3. Origin and destination **must be valid geo-locations**.
4. Requests outside serviceable regions **must fail fast** with explicit error codes.
5. Cancellation is allowed **until a Trip is created**.

### 1.3 Idempotency

* Idempotency key:

  ```
  trip_request:{passenger_id}
  ```
* Repeated creation attempts:

  * return existing active request, or
  * deterministically cancel + recreate (policy-driven).

### 1.4 Cold-Start Handling

* If no drivers are available:

  * TripRequest is **persisted and queued**
  * Passenger receives ETA or fallback options
* No synchronous retries or busy-waiting.

---

## 2. Trip Domain Laws (FSM-Enforced)

### 2.1 Purpose

`Trip` is a **binding operational contract** involving:

* passenger
* driver
* time
* money
* liability

### 2.2 Creation Rules

1. A `Trip` **MUST have a driver at creation**.
2. A `Trip` **MUST reference a valid TripRequest**.
3. `Trip` creation is **idempotent by TripRequest ID**.
4. Immutable fields:

   * passenger_id
   * driver_id
   * origin
   * destination
   * creation timestamp (UTC)

### 2.3 Trip Lifecycle (FSM — mandatory)

`Trip` **MUST** be implemented as a **Finite State Machine** inside `TripService`.

Allowed transitions only:

```
ACCEPTED → EN_ROUTE → COMPLETED
ACCEPTED → CANCELLED
EN_ROUTE → CANCELLED_BY_DRIVER
```

Any other transition:

* is rejected
* logged
* counted as a protocol violation

### 2.4 Failure Handling

* Driver drop-off:

  * transition → `CANCELLED_BY_DRIVER`
  * passenger notified
  * optional auto-reassignment (policy-controlled)
* All timestamps are immutable and UTC.

---

## 3. MatchingService Laws (Pure, Deterministic)

### 3.1 Responsibility

MatchingService is a **pure decision engine**.

It:

* computes candidate drivers
* assigns probabilities
* never mutates system state

### 3.2 Determinism

For identical inputs + seed:

* identical candidates
* identical probabilities
* identical ordering

### 3.3 Constraints

1. Only **available drivers** may be returned.
2. Candidate set size is bounded (`max_candidates`).
3. Probability distribution:

   * sum = 1 ± ε
   * immutable once computed

### 3.4 Failure Behavior

* Empty candidate set → explicit reason code.
* Crashes or timeouts → safe retry with same input and seed.

---

## 4. API Gateway / Orchestration Laws

### 4.1 Responsibilities

API Gateway:

* orchestrates calls
* performs sampling
* enforces idempotency
* logs decisions

### 4.2 Sampling

* Sampling occurs **only here**
* Uses **seed-based deterministic sampling**
* Probabilities are never modified

### 4.3 Reliability

* Retry-safe by design
* No direct Trip mutation
* Failed Trip creation:

  * retried idempotently, or
  * queued for async recovery

---

## 5. Driver & Passenger Laws

1. A driver may participate in **only one active Trip**.
2. Only drivers marked **AVAILABLE** may be matched.
3. Driver connectivity loss:

   * driver marked unavailable
   * in-progress trips handled by TripService FSM
4. Passenger state is **derived**, not inferred.

---

## 6. Eventing & Telemetry Laws

### 6.1 Event Model

* Events are **append-only**
* Events are **fail-safe**
* Event duplication is allowed; side effects are idempotent

### 6.2 Mandatory Telemetry

Logged for every critical operation:

* TripRequest lifecycle
* Matching results
* Sampling decisions
* Trip FSM transitions
* Failures, retries, cancellations

### 6.3 Replayability

* Any incident must be reproducible via event replay.
* Sampling seeds are persisted.

---

## 7. Probabilistic & ML Laws

1. Matching outputs are immutable training data.
2. All selections are replayable via seed.
3. Cold-start statistics are explicitly tracked.
4. Data drift is monitored continuously.
5. Retraining is triggered by **metric degradation**, not intuition.

---

## 8. High Availability & Risk Management Laws

### 8.1 Availability

* No single point of failure.
* Stateless services + replicated storage.
* Leader election and failover supported.

### 8.2 Data Safety

* Databases must support:

  * replication
  * backups
  * transactional guarantees
* Idempotency enforced at storage level (unique constraints).

### 8.3 Performance & SLAs

* Latency budgets defined per service.
* MatchingService must degrade gracefully under load.
* Slowdowns are observable before outages.

---

## 9. Deployment & Governance

1. Generated code is **never edited manually**.
2. Invariants are enforced by:

   * unit tests
   * integration tests
   * replay tests
3. Failed tests = **deployment blocked**.
4. Versioned APIs only; breaking changes require migration plans.
