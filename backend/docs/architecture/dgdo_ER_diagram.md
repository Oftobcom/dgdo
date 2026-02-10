**ER diagram** for the **DG Do (ride-hailing) project, MVP level**.

---

```mermaid
erDiagram

    USERS {
        uuid id PK
        varchar role "NOT NULL"  %% passenger | driver | admin
        varchar phone "NOT NULL UNIQUE"
        varchar email "UNIQUE"
        varchar password_hash "NOT NULL"
        boolean is_active "NOT NULL DEFAULT true"
        timestamp created_at "NOT NULL"
        timestamp updated_at
    }

    PASSENGERS {
        uuid user_id PK, FK
        varchar full_name
        numeric rating "DEFAULT 5.0"
        timestamp created_at "NOT NULL"
    }

    DRIVERS {
        uuid user_id PK, FK
        varchar full_name
        varchar license_number "NOT NULL UNIQUE"
        boolean is_verified "NOT NULL DEFAULT false"
        numeric rating "DEFAULT 5.0"
        timestamp created_at "NOT NULL"
    }

    ADMINS {
        uuid user_id PK, FK
        varchar full_name
        varchar admin_level "NOT NULL"
        timestamp created_at "NOT NULL"
    }

    VEHICLES {
        uuid id PK
        uuid driver_id FK
        varchar brand "NOT NULL"
        varchar model "NOT NULL"
        varchar plate_number "NOT NULL UNIQUE"
        varchar color
        boolean is_active "NOT NULL DEFAULT true"
        timestamp created_at "NOT NULL"
    }

    DRIVER_STATUS {
        uuid driver_id PK, FK
        varchar status "NOT NULL"  %% offline | available | on_trip
        geography current_location
        timestamp updated_at "NOT NULL"
    }

    TRIPS {
        uuid id PK
        uuid passenger_id FK
        uuid driver_id FK
        varchar status "NOT NULL"  %% requested | matched | accepted | completed | cancelled
        geography pickup_location "NOT NULL"
        geography dropoff_location "NOT NULL"
        numeric estimated_fare
        numeric final_fare
        timestamp requested_at "NOT NULL"
        timestamp accepted_at
        timestamp completed_at
        timestamp cancelled_at
    }

    MATCHING_EVENTS {
        uuid id PK
        uuid trip_id FK
        uuid driver_id FK
        varchar result "NOT NULL"  %% offered | accepted | rejected | timeout
        timestamp created_at "NOT NULL"
    }

    PAYMENTS {
        uuid id PK
        uuid trip_id FK
        numeric amount "NOT NULL"
        varchar currency "NOT NULL"
        varchar payment_method "NOT NULL"
        varchar status "NOT NULL"  %% pending | success | failed
        timestamp created_at "NOT NULL"
    }

    REVIEWS {
        uuid id PK
        uuid trip_id FK
        uuid reviewer_id FK
        uuid reviewee_id FK
        int rating "NOT NULL"
        varchar comment
        timestamp created_at "NOT NULL"
    }

    AUDIT_LOG {
        uuid id PK
        uuid user_id FK
        varchar action "NOT NULL"
        varchar entity_type "NOT NULL"
        uuid entity_id
        timestamp created_at "NOT NULL"
    }

    %% Relationships

    USERS ||--|| PASSENGERS : "is"
    USERS ||--|| DRIVERS : "is"
    USERS ||--|| ADMINS : "is"

    DRIVERS ||--o{ VEHICLES : owns
    DRIVERS ||--|| DRIVER_STATUS : has

    PASSENGERS ||--o{ TRIPS : requests
    DRIVERS ||--o{ TRIPS : serves

    TRIPS ||--o{ MATCHING_EVENTS : generates
    DRIVERS ||--o{ MATCHING_EVENTS : participates

    TRIPS ||--|| PAYMENTS : has
    TRIPS ||--o{ REVIEWS : produces

    USERS ||--o{ REVIEWS : writes
    USERS ||--o{ REVIEWS : receives

    USERS ||--o{ AUDIT_LOG : triggers

    %% Trigger logic (conceptual, documented)

    TRIPS }o--|| DRIVER_STATUS : "on accepted → set driver_status = on_trip"
    TRIPS }o--|| DRIVER_STATUS : "on completed/cancelled → set driver_status = available"
    PAYMENTS }o--|| TRIPS : "on payment success → set trip status = completed"
```

---

### Notes (concise)

* Designed for **PostgreSQL + PostGIS**
* Supports **Matching Service**, failure scenarios, and auditability
* Clean **Unified Identity Model**
* Ready for **microservice decomposition**
* Suitable for **MVP → production evolution**

---

Below is a **clean, ready-to-copy SQL schema** that matches the ER diagram exactly.

---

# DG Do — PostgreSQL DDL (MVP)

### Assumptions

* PostgreSQL ≥ 14
* PostGIS enabled
* UUIDs generated in DB
* One DB, multiple microservices (logical separation)

---

## 1. Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;
```

---

## 2. ENUMs (Explicit, Safe, Readable)

```sql
CREATE TYPE user_role AS ENUM ('passenger', 'driver', 'admin');

CREATE TYPE driver_status_type AS ENUM ('offline', 'available', 'on_trip');

CREATE TYPE trip_status AS ENUM (
    'requested',
    'matched',
    'accepted',
    'completed',
    'cancelled'
);

CREATE TYPE matching_result AS ENUM (
    'offered',
    'accepted',
    'rejected',
    'timeout'
);

CREATE TYPE payment_status AS ENUM (
    'pending',
    'success',
    'failed'
);
```

---

## 3. Core Identity Tables

### USERS (Unified Identity)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role user_role NOT NULL,
    phone VARCHAR(32) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP
);
```

---

### PASSENGERS

```sql
CREATE TABLE passengers (
    user_id UUID PRIMARY KEY,
    full_name VARCHAR(255),
    rating NUMERIC(3,2) DEFAULT 5.0,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_passenger_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

### DRIVERS

```sql
CREATE TABLE drivers (
    user_id UUID PRIMARY KEY,
    full_name VARCHAR(255),
    license_number VARCHAR(64) NOT NULL UNIQUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    rating NUMERIC(3,2) DEFAULT 5.0,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_driver_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

### ADMINS

```sql
CREATE TABLE admins (
    user_id UUID PRIMARY KEY,
    full_name VARCHAR(255),
    admin_level VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_admin_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 4. Driver Domain

### VEHICLES

```sql
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id UUID NOT NULL,
    brand VARCHAR(64) NOT NULL,
    model VARCHAR(64) NOT NULL,
    plate_number VARCHAR(32) NOT NULL UNIQUE,
    color VARCHAR(32),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_vehicle_driver
        FOREIGN KEY (driver_id) REFERENCES drivers(user_id) ON DELETE CASCADE
);
```

---

### DRIVER STATUS (Realtime State)

```sql
CREATE TABLE driver_status (
    driver_id UUID PRIMARY KEY,
    status driver_status_type NOT NULL,
    current_location GEOGRAPHY(POINT, 4326),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_driver_status_driver
        FOREIGN KEY (driver_id) REFERENCES drivers(user_id) ON DELETE CASCADE
);
```

---

## 5. Trips & Matching

### TRIPS

```sql
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    passenger_id UUID NOT NULL,
    driver_id UUID,
    status trip_status NOT NULL,
    pickup_location GEOGRAPHY(POINT, 4326) NOT NULL,
    dropoff_location GEOGRAPHY(POINT, 4326) NOT NULL,
    estimated_fare NUMERIC(10,2),
    final_fare NUMERIC(10,2),
    requested_at TIMESTAMP NOT NULL DEFAULT now(),
    accepted_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,

    CONSTRAINT fk_trip_passenger
        FOREIGN KEY (passenger_id) REFERENCES passengers(user_id),

    CONSTRAINT fk_trip_driver
        FOREIGN KEY (driver_id) REFERENCES drivers(user_id)
);
```

---

### MATCHING EVENTS (Audit-Friendly)

```sql
CREATE TABLE matching_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    result matching_result NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_match_trip
        FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,

    CONSTRAINT fk_match_driver
        FOREIGN KEY (driver_id) REFERENCES drivers(user_id) ON DELETE CASCADE
);
```

---

## 6. Payments & Reviews

### PAYMENTS

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL UNIQUE,
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(8) NOT NULL,
    payment_method VARCHAR(32) NOT NULL,
    status payment_status NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_payment_trip
        FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);
```

---

### REVIEWS

```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL,
    reviewer_id UUID NOT NULL,
    reviewee_id UUID NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_review_trip
        FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,

    CONSTRAINT fk_review_reviewer
        FOREIGN KEY (reviewer_id) REFERENCES users(id),

    CONSTRAINT fk_review_reviewee
        FOREIGN KEY (reviewee_id) REFERENCES users(id)
);
```

---

## 7. Audit Log (Admin / Security / Compliance)

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    action VARCHAR(128) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 8. Critical Triggers (Business Logic in DB)

### Trip → Driver Status Sync

```sql
CREATE OR REPLACE FUNCTION sync_driver_status_from_trip()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'accepted' THEN
        UPDATE driver_status
        SET status = 'on_trip', updated_at = now()
        WHERE driver_id = NEW.driver_id;
    END IF;

    IF NEW.status IN ('completed', 'cancelled') THEN
        UPDATE driver_status
        SET status = 'available', updated_at = now()
        WHERE driver_id = NEW.driver_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

```sql
CREATE TRIGGER trg_trip_driver_status
AFTER UPDATE OF status ON trips
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION sync_driver_status_from_trip();
```

---

### Payment → Trip Completion

```sql
CREATE OR REPLACE FUNCTION complete_trip_on_payment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'success' THEN
        UPDATE trips
        SET status = 'completed',
            completed_at = now()
        WHERE id = NEW.trip_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

```sql
CREATE TRIGGER trg_payment_complete_trip
AFTER UPDATE OF status ON payments
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION complete_trip_on_payment();
```

---

## 9. Indexes (MVP-Critical)

```sql
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_passenger ON trips(passenger_id);
CREATE INDEX idx_trips_driver ON trips(driver_id);

CREATE INDEX idx_driver_status_location
    ON driver_status
    USING GIST (current_location);
```

---

## Final Assessment

✅ Matches ER diagram
✅ PostGIS-ready
✅ Event-friendly
✅ Microservice-safe
✅ MVP → scale-up ready

