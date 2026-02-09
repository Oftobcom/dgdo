Perfect, let’s lock this down cleanly and **in English**, with a true **MVP mindset**: minimum surface area, maximum viability.

Below is a **production-sane Passenger API** for the **DG Do ride-hailing MVP**.

---

# 🚕 Passenger — MVP API Endpoints (DG Do)

## 1. Authentication & Session

> Passenger identity in MVP is **lightweight** (no KYC).

```
POST   /passenger/register
POST   /passenger/login
POST   /passenger/logout
POST   /passenger/refresh-token
```

**Minimal inputs**

* phone OR email
* OTP / verification code
* device_id (optional but recommended)

---

## 2. Passenger Profile

```
GET    /passenger/profile
PUT    /passenger/profile
```

**MVP fields**

* full_name
* phone
* email
* default_payment_method (stub)
* rating (read-only)

---

## 3. Trip Request (Core MVP Flow)

```
POST   /trips/request
GET    /trips/{trip_id}
POST   /trips/{trip_id}/cancel
```

**Request payload**

```json
{
  "from": { "lat": 40.283, "lon": 69.622 },
  "to":   { "lat": 40.311, "lon": 69.651 }
}
```

---

## 4. Trip Status & Driver Info

```
GET    /trips/{trip_id}/status
GET    /trips/{trip_id}/driver
```

**Trip states (formal FSM subset)**

```
CREATED
MATCHING
DRIVER_ASSIGNED
IN_PROGRESS
COMPLETED
CANCELLED
NO_DRIVERS
```

---

## 5. Ride Execution (Read-only for Passenger)

> In MVP these actions are triggered by the **Driver app**,
> Passenger only observes state changes.

```
POST   /trips/{trip_id}/start
POST   /trips/{trip_id}/finish
```

---

## 6. Payments (MVP Stub)

```
POST   /payments/estimate
POST   /payments/confirm
```

**MVP simplifications**

* fixed rate or distance × rate
* no real payment gateway
* no refunds

---

## 7. Ratings & Feedback

```
POST   /ratings/driver
```

```json
{
  "trip_id": "uuid",
  "rating": 1-5,
  "comment": "optional"
}
```

---

## 8. Notifications

```
GET    /notifications
POST   /notifications/{notification_id}/ack
```

**Events**

* driver assigned
* driver arrived
* trip started
* trip completed
* driver cancelled

---

## 9. Passenger Runtime State (Debug / Admin)

```
GET    /passenger/state
```

> Useful for debugging FSM consistency.

---

# 📦 Passenger MVP API — Compact View

```
Auth:
  POST /passenger/register
  POST /passenger/login
  POST /passenger/logout

Profile:
  GET  /passenger/profile
  PUT  /passenger/profile

Trips:
  POST /trips/request
  GET  /trips/{id}
  POST /trips/{id}/cancel

Matching:
  GET  /trips/{id}/status
  GET  /trips/{id}/driver

Ride:
  POST /trips/{id}/start
  POST /trips/{id}/finish

Payments:
  POST /payments/estimate
  POST /payments/confirm

Ratings:
  POST /ratings/driver

Notifications:
  GET  /notifications
```

---

## 🚫 Explicitly Out of MVP Scope

* scheduled rides
* promo codes
* ride history filters
* passenger-driver chat
* live map animations
* multi-stop trips

---

## 🧠 Architectural Principle (Important)

**Passenger API is not authoritative.**

Source of truth:

* `TripService`
* `MatchingService`

Passenger endpoints must be:

* thin
* idempotent
* stateless
* event-driven friendly
