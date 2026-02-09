Perfect — now we complete the triangle.
Below is a **clean, role-aware, MVP-level Driver API** that fits **DG Do’s unified identity model** and does **not leak passenger logic into the driver app**.

No fluff. No Uber bloat. Only what makes the system run.

---

# 🚗 Driver — MVP API Endpoints (DG Do)

> Assumption:
> Driver is **a role attached to a unified Identity**
> (`Identity = ACTIVE`, `DriverRole = ACTIVE`)

---

## 1. Driver Role Onboarding

```http
POST   /driver/apply
GET    /driver/application/status
```

### `POST /driver/apply`

Minimal MVP payload:

```json
{
  "vehicle_type": "sedan",
  "vehicle_plate": "ABC123"
}
```

State transition:

```
NOT_ASSIGNED → REQUESTED
```

Approval is done by **Admin**.

---

## 2. Driver Profile

```http
GET    /driver/profile
PUT    /driver/profile
```

**MVP fields**

* full_name
* vehicle_type
* vehicle_plate
* rating (read-only)
* status (ACTIVE / SUSPENDED)

---

## 3. Driver Availability (Critical)

```http
POST   /driver/online
POST   /driver/offline
GET    /driver/status
```

This controls whether the driver:

* participates in matching
* receives trip offers

---

## 4. Location Updates (Realtime Core)

```http
POST   /driver/location
```

```json
{
  "lat": 40.283,
  "lon": 69.622,
  "heading": 180,
  "speed": 12.5
}
```

> In MVP this may be HTTP polling;
> WebSocket / UDP comes later.

---

## 5. Trip Offer & Matching

```http
GET    /driver/trips/offers
POST   /driver/trips/{trip_id}/accept
POST   /driver/trips/{trip_id}/reject
```

### Matching FSM fragment

```
OFFERED → ACCEPTED → ASSIGNED
        ↘ REJECTED
```

---

## 6. Active Trip Control

```http
POST   /driver/trips/{trip_id}/arrived
POST   /driver/trips/{trip_id}/start
POST   /driver/trips/{trip_id}/finish
```

Passenger observes these transitions.

---

## 7. Driver-Initiated Cancellation

```http
POST   /driver/trips/{trip_id}/cancel
```

**Reasons (MVP enum)**

* passenger_no_show
* vehicle_issue
* emergency

---

## 8. Earnings (Stub for MVP)

```http
GET    /driver/earnings/today
GET    /driver/earnings/summary
```

> No payouts, no banking, just visibility.

---

## 9. Notifications

```http
GET    /driver/notifications
POST   /driver/notifications/{id}/ack
```

Events:

* new trip offer
* passenger cancelled
* admin suspension

---

## 10. Driver Runtime State (Debug)

```http
GET    /driver/state
```

Shows:

* online/offline
* current trip
* FSM consistency

---

# 📦 Driver MVP API — Compact View

```
Onboarding:
  POST /driver/apply
  GET  /driver/application/status

Profile:
  GET  /driver/profile
  PUT  /driver/profile

Availability:
  POST /driver/online
  POST /driver/offline
  GET  /driver/status

Location:
  POST /driver/location

Matching:
  GET  /driver/trips/offers
  POST /driver/trips/{id}/accept
  POST /driver/trips/{id}/reject

Trip:
  POST /driver/trips/{id}/arrived
  POST /driver/trips/{id}/start
  POST /driver/trips/{id}/finish
  POST /driver/trips/{id}/cancel

Earnings:
  GET  /driver/earnings/today
  GET  /driver/earnings/summary

Notifications:
  GET  /driver/notifications
```

---

## 🚫 Explicitly Out of MVP Scope

* driver chat
* heatmaps
* surge pricing UI
* smart repositioning
* payouts & withdrawals
* multi-vehicle drivers

---

## 🧠 Architectural Rules (Non-Negotiable)

1. **Driver cannot mutate Passenger state**
2. **Driver actions emit events, not direct writes**
3. **Matching is authoritative, Driver only responds**
4. **Location updates must be fire-and-forget**

---

## 🔁 Event Examples (for later Kafka/WebSocket)

* `DriverOnline`
* `DriverLocationUpdated`
* `TripOfferedToDriver`
* `TripAcceptedByDriver`
* `TripFinishedByDriver`
