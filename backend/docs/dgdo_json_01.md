Below is a **clean, production-grade set of JSON event schemas** for a ride-hailing realtime system.

These are **events**, not API requests.
They are immutable facts, designed for **WebSockets + Kafka**.

---

# 📦 Common Event Envelope (ALL events)

Every event in the system **must** follow this envelope.

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "event_version": 1,
  "timestamp": "2026-02-04T12:34:56.789Z",
  "producer": "service-name",
  "correlation_id": "uuid",
  "payload": {}
}
```

### Why this matters

* replayable
* debuggable
* versionable
* traceable across services

---

# 🚕 Driver Events

## 1️⃣ Driver location update

```json
{
  "event_type": "driver.location.updated",
  "payload": {
    "driver_id": "uuid",
    "location": {
      "lat": 40.2834,
      "lon": 69.6225
    },
    "speed_kmh": 32.4,
    "heading_deg": 180,
    "accuracy_m": 5,
    "source": "gps"
  }
}
```

**Notes**

* high-frequency
* non-transactional
* acceptable to lose some events

---

## 2️⃣ Driver availability change

```json
{
  "event_type": "driver.status.changed",
  "payload": {
    "driver_id": "uuid",
    "status": "available",
    "reason": "trip_finished"
  }
}
```

---

# 👤 Passenger Events

## 3️⃣ Trip requested

```json
{
  "event_type": "trip.requested",
  "payload": {
    "trip_id": "uuid",
    "passenger_id": "uuid",
    "pickup_location": {
      "lat": 40.2851,
      "lon": 69.6249
    },
    "dropoff_location": {
      "lat": 40.3012,
      "lon": 69.6398
    },
    "requested_at": "2026-02-04T12:35:10Z"
  }
}
```

---

# 🧠 Matching Events

## 4️⃣ Match found

```json
{
  "event_type": "match.found",
  "payload": {
    "trip_id": "uuid",
    "driver_id": "uuid",
    "eta_seconds": 180,
    "distance_m": 1200,
    "match_score": 0.87
  }
}
```

---

## 5️⃣ Match rejected by driver

```json
{
  "event_type": "match.rejected",
  "payload": {
    "trip_id": "uuid",
    "driver_id": "uuid",
    "reason": "timeout"
  }
}
```

---

# 🧾 Trip Lifecycle Events (authoritative)

## 6️⃣ Trip accepted

```json
{
  "event_type": "trip.accepted",
  "payload": {
    "trip_id": "uuid",
    "driver_id": "uuid",
    "accepted_at": "2026-02-04T12:36:01Z"
  }
}
```

---

## 7️⃣ Trip started

```json
{
  "event_type": "trip.started",
  "payload": {
    "trip_id": "uuid",
    "started_at": "2026-02-04T12:38:15Z",
    "start_location": {
      "lat": 40.2852,
      "lon": 69.6250
    }
  }
}
```

---

## 8️⃣ Trip finished

```json
{
  "event_type": "trip.finished",
  "payload": {
    "trip_id": "uuid",
    "finished_at": "2026-02-04T12:52:33Z",
    "end_location": {
      "lat": 40.3011,
      "lon": 69.6397
    },
    "distance_km": 6.4,
    "duration_sec": 870,
    "fare": {
      "currency": "TJS",
      "amount": 42.50
    }
  }
}
```

---

# 💰 Pricing Events

## 9️⃣ Price calculated

```json
{
  "event_type": "price.calculated",
  "payload": {
    "trip_id": "uuid",
    "base_fare": 20.0,
    "distance_fare": 18.5,
    "time_fare": 4.0,
    "surge_multiplier": 1.1,
    "total_fare": 42.5,
    "currency": "TJS"
  }
}
```

---

# 📡 Telemetry / System Events

## 🔟 Client heartbeat

```json
{
  "event_type": "client.heartbeat",
  "payload": {
    "client_id": "uuid",
    "client_type": "driver",
    "status": "alive",
    "latency_ms": 45
  }
}
```

---

## 1️⃣1️⃣ Realtime connection state

```json
{
  "event_type": "connection.state.changed",
  "payload": {
    "client_id": "uuid",
    "state": "disconnected",
    "reason": "network_timeout"
  }
}
```

---

# 🔁 Error & Control Events

## 1️⃣2️⃣ Command rejected (important)

```json
{
  "event_type": "command.rejected",
  "payload": {
    "command_type": "trip.accept",
    "reason": "invalid_state_transition",
    "details": "Trip already accepted"
  }
}
```

---

# 🧠 Design rules (DO NOT break)

1. **Events are immutable**
2. **Never update or delete events**
3. **Add fields — never remove**
4. **Version on breaking change only**
5. **One event = one fact**
6. **No business logic in clients**

---

# 🔥 Why this schema will not break at scale

* supports replay
* supports fan-out
* supports ML pipelines
* supports auditing
* supports partial failures

