# ============================================================

# DG Do — Production PostgreSQL + PostGIS Schema

# ============================================================

Perfect. Here’s a **ready-to-run Docker + PostGIS setup** with migration scripts for DGDO. This setup will automatically create the database, extensions, tables, enums, triggers, and indexes from the schema we designed. You can run it on Ubuntu 22.04 in WSL or any Linux host.

---

## 1️⃣ Create Project Folder Structure

```
dgdo-postgis/
├── docker-compose.yml
├── init-db/
│   ├── 01_extensions.sql
│   ├── 02_types.sql
│   ├── 03_tables.sql
│   ├── 04_triggers.sql
```

All `.sql` scripts will be executed automatically on container startup.

---

## 2️⃣ `docker-compose.yml`

```yaml
version: "3.9"

services:
  dgdo-postgis:
    image: postgis/postgis:15-3.4
    container_name: dgdo-postgis
    environment:
      POSTGRES_USER: dgdo
      POSTGRES_PASSWORD: dgdo123
      POSTGRES_DB: dgdo
    ports:
      - "5432:5432"
    volumes:
      - ./init-db:/docker-entrypoint-initdb.d
    restart: unless-stopped
```

> All scripts in `init-db/` ending with `.sql` will be executed automatically when the container first starts.

---

## 3️⃣ `init-db/01_extensions.sql`

```sql
-- Create required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

---

## 4️⃣ `init-db/02_types.sql`

```sql
-- TripRequest Status
CREATE TYPE trip_request_status AS ENUM (
    'CREATED', 'MATCHING', 'MATCHED', 'CANCELLED', 'EXPIRED'
);

-- Trip Status
CREATE TYPE trip_status AS ENUM (
    'CREATED', 'ACCEPTED', 'EN_ROUTE', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
);

-- Driver Status
CREATE TYPE driver_status AS ENUM (
    'OFFLINE', 'IDLE', 'ASSIGNED', 'EN_ROUTE', 'ON_TRIP'
);
```

---

## 5️⃣ `init-db/03_tables.sql`

```sql
-- Drivers table
CREATE TABLE drivers (
    driver_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    status driver_status NOT NULL DEFAULT 'IDLE',
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    available BOOLEAN NOT NULL DEFAULT true,
    rating DOUBLE PRECISION DEFAULT 5.0,
    fatigue DOUBLE PRECISION DEFAULT 0.0,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_drivers_location ON drivers USING GIST(location);

-- Trip Requests table
CREATE TABLE trip_requests (
    trip_request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id TEXT NOT NULL,
    pickup_lat DOUBLE PRECISION NOT NULL,
    pickup_lng DOUBLE PRECISION NOT NULL,
    dropoff_lat DOUBLE PRECISION NOT NULL,
    dropoff_lng DOUBLE PRECISION NOT NULL,
    pickup_geom GEOGRAPHY(POINT, 4326) NOT NULL,
    dropoff_geom GEOGRAPHY(POINT, 4326) NOT NULL,
    status trip_request_status NOT NULL DEFAULT 'CREATED',
    matched_driver_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_trip_requests_pickup_geom ON trip_requests USING GIST(pickup_geom);

-- Trips table
CREATE TABLE trips (
    trip_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_request_id UUID UNIQUE NOT NULL,
    passenger_id TEXT NOT NULL,
    driver_id UUID NOT NULL,
    origin_geom GEOGRAPHY(POINT, 4326) NOT NULL,
    destination_geom GEOGRAPHY(POINT, 4326) NOT NULL,
    status trip_status NOT NULL DEFAULT 'CREATED',
    version INTEGER NOT NULL DEFAULT 1,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_trip_request FOREIGN KEY (trip_request_id) REFERENCES trip_requests(trip_request_id),
    CONSTRAINT fk_trip_driver FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- Trip Events table
CREATE TABLE trip_events (
    event_id BIGSERIAL PRIMARY KEY,
    trip_id UUID NOT NULL,
    old_status trip_status,
    new_status trip_status,
    actor TEXT,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_trip_events_trip FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
);

-- Driver Positions table
CREATE TABLE driver_positions (
    id BIGSERIAL PRIMARY KEY,
    driver_id UUID NOT NULL,
    position GEOGRAPHY(POINT, 4326) NOT NULL,
    speed_mps DOUBLE PRECISION,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_driver_positions_driver FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);
CREATE INDEX idx_driver_positions_geom ON driver_positions USING GIST(position);
```

---

## 6️⃣ `init-db/04_triggers.sql`

```sql
-- Sync driver location
CREATE OR REPLACE FUNCTION sync_driver_geom()
RETURNS trigger AS $$
BEGIN
    NEW.location := ST_SetSRID(ST_MakePoint(NEW.lng, NEW.lat), 4326);
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_driver_geom
BEFORE INSERT OR UPDATE ON drivers
FOR EACH ROW
EXECUTE FUNCTION sync_driver_geom();

-- Sync trip request geometry
CREATE OR REPLACE FUNCTION sync_trip_request_geom()
RETURNS trigger AS $$
BEGIN
    NEW.pickup_geom := ST_SetSRID(ST_MakePoint(NEW.pickup_lng, NEW.pickup_lat), 4326);
    NEW.dropoff_geom := ST_SetSRID(ST_MakePoint(NEW.dropoff_lng, NEW.dropoff_lat), 4326);
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_trip_request_geom
BEFORE INSERT OR UPDATE ON trip_requests
FOR EACH ROW
EXECUTE FUNCTION sync_trip_request_geom();
```

---

## 7️⃣ Run the Docker Container

```bash
cd dgdo-postgis
docker-compose up -d
```

* PostgreSQL will be exposed on **localhost:5432**.
* Database: `dgdo`, user: `dgdo`, password: `dgdo123`.
* The PostGIS extension and all tables, triggers, enums, and indexes are automatically created.

---

## 8️⃣ Connect from Windows Host (HeidiSQL)

* **Hostname/IP:** `127.0.0.1`
* **Port:** `5432`
* **User:** `dgdo`
* **Password:** `dgdo123`
* **Database:** `dgdo`
* **SSL:** disabled (if using WSL)

---

This setup gives you **production-ready Postgres + PostGIS**, fully compatible with your current proto-files and services.

It’s ready for:

* **MatchingService** (nearest-driver queries with PostGIS)
* **TripRequestService** (pickup/dropoff management)
* **TripService** (FSM trip lifecycle)
* **Driver simulations / telemetry**
