Excellent — this completes the **control plane** of DG Do.

Below is a **strict, no-nonsense MVP API for Administrator**, designed to:

* control the system
* approve roles
* resolve failures
* **never participate in realtime flows**

Admin is **out-of-band governance**, not an active actor in trips.

---

# 🛠️ Administrator — MVP API Endpoints (DG Do)

> Assumption:
> Admin is a **role on top of Unified Identity**
> (`Identity = ACTIVE`, `AdminRole = ACTIVE`)

---

## 1. Admin Authentication & Session

> Reuses the same identity/auth system.

```
POST   /admin/login
POST   /admin/logout
GET    /admin/me
```

⚠️ No self-registration.
Admin role is **granted by another Admin** or via bootstrap.

---

## 2. Identity & Role Management (Core Admin Power)

### View Identities

```
GET    /admin/identities
GET    /admin/identities/{identity_id}
```

### Role Control

```
POST   /admin/roles/{identity_id}/grant
POST   /admin/roles/{identity_id}/revoke
POST   /admin/roles/{identity_id}/suspend
POST   /admin/roles/{identity_id}/reinstate
```

Example payload:

```json
{
  "role": "driver"
}
```

---

## 3. Driver Application Review

```
GET    /admin/driver-applications
POST   /admin/driver-applications/{id}/approve
POST   /admin/driver-applications/{id}/reject
```

Driver FSM:

```
REQUESTED → ACTIVE / REJECTED
```

---

## 4. Trip Oversight & Intervention

```
GET    /admin/trips
GET    /admin/trips/{trip_id}
POST   /admin/trips/{trip_id}/force-cancel
```

**Force cancel reasons**

* safety
* fraud
* system_error

---

## 5. System State & Health (MVP)

```
GET    /admin/system/status
GET    /admin/system/metrics
```

Metrics (minimal):

* active trips
* online drivers
* matching queue size

---

## 6. Incident & Dispute Handling (MVP-lite)

```
GET    /admin/incidents
POST   /admin/incidents/{id}/resolve
```

> In MVP incidents are mostly **driver cancellations & passenger complaints**.

---

## 7. Notifications & Audit

```
GET    /admin/notifications
GET    /admin/audit-log
```

Audit includes:

* role grants
* suspensions
* trip interventions

---

## 8. Admin Runtime State (Debug)

```
GET    /admin/state
```

Used for:

* RBAC validation
* FSM consistency
* debugging privileges

---

# 📦 Administrator MVP API — Compact View

```
Auth:
  POST /admin/login
  POST /admin/logout
  GET  /admin/me

Identity:
  GET  /admin/identities
  GET  /admin/identities/{id}

Roles:
  POST /admin/roles/{id}/grant
  POST /admin/roles/{id}/revoke
  POST /admin/roles/{id}/suspend
  POST /admin/roles/{id}/reinstate

Drivers:
  GET  /admin/driver-applications
  POST /admin/driver-applications/{id}/approve
  POST /admin/driver-applications/{id}/reject

Trips:
  GET  /admin/trips
  GET  /admin/trips/{id}
  POST /admin/trips/{id}/force-cancel

System:
  GET  /admin/system/status
  GET  /admin/system/metrics

Audit:
  GET  /admin/audit-log
```

---

## 🚫 Explicitly Out of MVP Scope

* fare configuration UI
* surge controls
* refunds & payments
* content moderation tools
* multi-admin approval workflows

---

## 🧠 Architectural Rules (Critical)

1. **Admin never participates in realtime flows**
2. **Admin actions are authoritative overrides**
3. **Every admin action emits an audit event**
4. **Admin APIs are rate-limited & IP-restricted**

---

## 🔁 Admin Events (for Kafka / Audit)

* `AdminRoleGranted`
* `AdminRoleRevoked`
* `DriverApproved`
* `DriverRejected`
* `TripForceCancelled`
* `IdentitySuspended`
