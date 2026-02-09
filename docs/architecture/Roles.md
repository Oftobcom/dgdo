Great question — this is exactly where DG Do becomes **architecturally clean** instead of “three separate apps glued together”.

Below is a **Unified Identity FSM** that governs **Passenger / Driver / Admin** as *roles on top of a single Identity*, followed by a **Mermaid Sequence Diagram** that shows how this works at runtime.

Everything is **MVP-level**, but future-proof.

---

# 1. Core Idea: Unified Identity

**One human = one Identity**

Roles are:

* *attached*
* *activated*
* *suspended*
* *revoked*

but **identity itself is singular**.

```
Identity
 ├── PassengerRole
 ├── DriverRole
 └── AdminRole
```

No duplicated users.
No “driver_user”, “passenger_user” tables.
Just **roles with states**.

---

# 2. Unified Identity FSM (Formal)

## Identity Lifecycle (Global)

```
UNREGISTERED
   ↓
REGISTERED
   ↓
VERIFIED
   ↓
ACTIVE
   ↓
SUSPENDED / DEACTIVATED
```

This applies to **everyone**.

---

## Role Lifecycle (Per Role)

Each role has its own FSM **attached to the same Identity**.

### Generic Role FSM

```
NOT_ASSIGNED
   ↓
REQUESTED
   ↓
ACTIVE
   ↓
SUSPENDED
   ↓
REVOKED
```

---

## Combined View (Identity + Roles)

```
IDENTITY: ACTIVE
 ├─ PassengerRole: ACTIVE
 ├─ DriverRole:    NOT_ASSIGNED / REQUESTED / ACTIVE
 └─ AdminRole:     NOT_ASSIGNED / ACTIVE
```

One identity can:

* be Passenger + Driver
* be Passenger + Admin
* be all three (internally)

---

# 3. Unified Identity State Machine (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> UNREGISTERED

    UNREGISTERED --> REGISTERED : register()
    REGISTERED --> VERIFIED : verify_otp()
    VERIFIED --> ACTIVE : activate_identity()

    ACTIVE --> SUSPENDED : policy_violation
    SUSPENDED --> ACTIVE : reinstate
    ACTIVE --> DEACTIVATED : delete_account

    state ACTIVE {
        [*] --> Roles

        state Roles {
            Passenger_NOT_ASSIGNED --> Passenger_ACTIVE : auto_assign
            Passenger_ACTIVE --> Passenger_SUSPENDED : abuse

            Driver_NOT_ASSIGNED --> Driver_REQUESTED : apply_driver
            Driver_REQUESTED --> Driver_ACTIVE : approve_driver
            Driver_ACTIVE --> Driver_SUSPENDED : violation

            Admin_NOT_ASSIGNED --> Admin_ACTIVE : grant_admin
            Admin_ACTIVE --> Admin_REVOKED : revoke_admin
        }
    }
```

---

# 4. Role Semantics (MVP Rules)

### Passenger

* auto-assigned on registration
* cannot be “unassigned”, only suspended

### Driver

* explicitly requested
* requires approval
* stronger suspension rules

### Admin

* manually granted
* zero self-service
* revocable at any time

---

# 5. Unified Identity — Mermaid Sequence Diagram (MVP)

This diagram shows:

* single registration
* role attachment
* role-based behavior

```mermaid
sequenceDiagram
    participant User
    participant API as Identity API
    participant Auth as Auth Service
    participant Role as Role Service
    participant DB as Identity DB

    User->>API: register(phone/email)
    API->>DB: create Identity (REGISTERED)
    API->>Auth: send OTP
    Auth-->>User: OTP code

    User->>API: verify OTP
    API->>DB: update Identity → VERIFIED
    API->>DB: activate PassengerRole
    API-->>User: Identity ACTIVE + PassengerRole ACTIVE

    User->>API: apply for Driver role
    API->>Role: create DriverRole (REQUESTED)
    Role->>DB: save role state

    Admin->>API: approve Driver
    API->>Role: DriverRole → ACTIVE
    Role->>DB: update role state
    API-->>User: Driver role activated

    Admin->>API: grant Admin role
    API->>Role: AdminRole → ACTIVE
    Role->>DB: update role
```

---

# 6. Why This Model Is Correct (and Scales)

### ❌ Bad Model

* separate user tables
* duplicated auth
* role-specific JWTs
* role switching hacks

### ✅ This Model

* one identity
* roles as FSMs
* stateless auth
* event-driven friendly
* perfect for:

  * Kafka
  * WebSockets
  * RBAC
  * audit logs

---

# 7. JWT / Auth Token Design (MVP)

```json
{
  "sub": "identity_id",
  "roles": {
    "passenger": "ACTIVE",
    "driver": "ACTIVE",
    "admin": "NOT_ASSIGNED"
  },
  "scope": ["trip:create", "trip:accept"],
  "exp": 1234567890
}
```
