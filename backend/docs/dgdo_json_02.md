Below is a **production-grade JSON Schema setup** using **Draft 2020-12**, structured exactly how teams actually do it.

1. **Base Event Envelope schema**
2. **Reusable common definitions**
3. **Concrete schemas for key events**
4. **How validation works in practice (Gateway / Kafka)**

---

# 1️⃣ Base Event Envelope (required for ALL events)

📄 `schemas/event-envelope.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://dgdo.io/schemas/event-envelope.json",
  "type": "object",
  "required": [
    "event_id",
    "event_type",
    "event_version",
    "timestamp",
    "producer",
    "correlation_id",
    "payload"
  ],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "event_type": {
      "type": "string"
    },
    "event_version": {
      "type": "integer",
      "minimum": 1
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "producer": {
      "type": "string"
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid"
    },
    "payload": {
      "type": "object"
    }
  },
  "additionalProperties": false
}
```

**Invariant**

> If this schema fails — the event is rejected at the Gateway.

---

# 2️⃣ Shared Definitions (reused everywhere)

📄 `schemas/common-definitions.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://dgdo.io/schemas/common-definitions.json",
  "definitions": {
    "uuid": {
      "type": "string",
      "format": "uuid"
    },
    "geo_point": {
      "type": "object",
      "required": ["lat", "lon"],
      "properties": {
        "lat": {
          "type": "number",
          "minimum": -90,
          "maximum": 90
        },
        "lon": {
          "type": "number",
          "minimum": -180,
          "maximum": 180
        }
      },
      "additionalProperties": false
    },
    "currency_amount": {
      "type": "object",
      "required": ["currency", "amount"],
      "properties": {
        "currency": {
          "type": "string",
          "minLength": 3,
          "maxLength": 3
        },
        "amount": {
          "type": "number",
          "minimum": 0
        }
      },
      "additionalProperties": false
    }
  }
}
```

---

# 3️⃣ Concrete Event Schemas

Each event schema **extends the envelope** using `allOf`.

---

## 🚗 Driver location updated

📄 `schemas/driver.location.updated.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://dgdo.io/schemas/driver.location.updated.json",

  "allOf": [
    { "$ref": "event-envelope.schema.json" },
    {
      "properties": {
        "event_type": {
          "const": "driver.location.updated"
        },
        "payload": {
          "type": "object",
          "required": ["driver_id", "location"],
          "properties": {
            "driver_id": {
              "$ref": "common-definitions.schema.json#/definitions/uuid"
            },
            "location": {
              "$ref": "common-definitions.schema.json#/definitions/geo_point"
            },
            "speed_kmh": {
              "type": "number",
              "minimum": 0
            },
            "heading_deg": {
              "type": "number",
              "minimum": 0,
              "maximum": 360
            },
            "accuracy_m": {
              "type": "number",
              "minimum": 0
            },
            "source": {
              "type": "string",
              "enum": ["gps", "network", "manual"]
            }
          },
          "additionalProperties": false
        }
      }
    }
  ]
}
```

---

## 👤 Trip requested

📄 `schemas/trip.requested.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://dgdo.io/schemas/trip.requested.json",

  "allOf": [
    { "$ref": "event-envelope.schema.json" },
    {
      "properties": {
        "event_type": {
          "const": "trip.requested"
        },
        "payload": {
          "type": "object",
          "required": [
            "trip_id",
            "passenger_id",
            "pickup_location",
            "dropoff_location",
            "requested_at"
          ],
          "properties": {
            "trip_id": {
              "$ref": "common-definitions.schema.json#/definitions/uuid"
            },
            "passenger_id": {
              "$ref": "common-definitions.schema.json#/definitions/uuid"
            },
            "pickup_location": {
              "$ref": "common-definitions.schema.json#/definitions/geo_point"
            },
            "dropoff_location": {
              "$ref": "common-definitions.schema.json#/definitions/geo_point"
            },
            "requested_at": {
              "type": "string",
              "format": "date-time"
            }
          },
          "additionalProperties": false
        }
      }
    }
  ]
}
```

---

## 🧾 Trip finished

📄 `schemas/trip.finished.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://dgdo.io/schemas/trip.finished.json",

  "allOf": [
    { "$ref": "event-envelope.schema.json" },
    {
      "properties": {
        "event_type": {
          "const": "trip.finished"
        },
        "payload": {
          "type": "object",
          "required": [
            "trip_id",
            "finished_at",
            "distance_km",
            "duration_sec",
            "fare"
          ],
          "properties": {
            "trip_id": {
              "$ref": "common-definitions.schema.json#/definitions/uuid"
            },
            "finished_at": {
              "type": "string",
              "format": "date-time"
            },
            "distance_km": {
              "type": "number",
              "minimum": 0
            },
            "duration_sec": {
              "type": "integer",
              "minimum": 0
            },
            "fare": {
              "$ref": "common-definitions.schema.json#/definitions/currency_amount"
            }
          },
          "additionalProperties": false
        }
      }
    }
  ]
}
```

---

# 4️⃣ How validation is used in the system

## 🔐 Realtime Gateway

* validates **incoming WebSocket messages**
* rejects invalid events immediately
* returns `command.rejected` with reason

```
Client → Gateway → Schema validation → OK / Reject
```

---

## 🚌 Kafka producers

* validate **before publish**
* guarantees topic cleanliness

> One invalid event can poison a whole stream — schema stops that.

---

## 🔁 Consumers

* trust schema
* no defensive parsing
* simpler code
* faster processing

---

# 🔥 Non-negotiable rules

1. **Validation happens at the edge**
2. **Schemas are versioned**
3. **Breaking change → new event_version**
4. **Never accept `additionalProperties: true`**
5. **Schema repo is part of CI**

---

# 🎯 Why this matters (strategically)

With schemas:

* replay is safe
* ML pipelines don’t rot
* services evolve independently
* junior devs can’t break the system
* audits are trivial

This is the difference between:

> *“it works now”*
> and
> *“it still works in 3 years”*
