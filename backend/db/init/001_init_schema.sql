-- Enable PostGIS for geographic queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- ----------------------------
-- 1. MARKETS
-- ----------------------------
CREATE TABLE market (
    market_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    currency CHAR(3) NOT NULL,             -- e.g., TJS
    min_fare NUMERIC(10,2) NOT NULL,
    surge_cap NUMERIC(5,2) NOT NULL,
    commission_rate NUMERIC(5,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ----------------------------
-- 2. USERS (Passengers & Drivers)
-- ----------------------------
CREATE TABLE "user" (
    user_id UUID PRIMARY KEY,
    market_id INT NOT NULL REFERENCES market(market_id),
    name TEXT,
    role SMALLINT NOT NULL,                -- 0=Passenger,1=Driver
    status SMALLINT NOT NULL,              -- 0=Inactive,1=Active
    phone TEXT,
    email TEXT,
    rating NUMERIC(3,2),
    location GEOGRAPHY(POINT, 4326),       -- for drivers
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_user_location ON "user" USING GIST(location);

-- ----------------------------
-- 3. VEHICLES
-- ----------------------------
CREATE TABLE vehicle (
    vehicle_id UUID PRIMARY KEY,
    driver_id UUID NOT NULL REFERENCES "user"(user_id),
    make TEXT,
    model TEXT,
    plate_number TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ----------------------------
-- 4. DRIVER STATUS (Realtime)
-- ----------------------------
CREATE TABLE driver_status (
    driver_status_id UUID PRIMARY KEY,
    driver_id UUID NOT NULL REFERENCES "user"(user_id),
    is_available BOOLEAN NOT NULL DEFAULT true,
    current_trip_id UUID REFERENCES trip(trip_id),
    location GEOGRAPHY(POINT, 4326),
    last_seen TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    version INT NOT NULL DEFAULT 1,
    metadata JSONB
);

CREATE INDEX idx_driver_status_location ON driver_status USING GIST(location);

-- ----------------------------
-- 5. TRIP REQUESTS
-- ----------------------------
CREATE TABLE trip_request (
    trip_request_id UUID PRIMARY KEY,
    market_id INT NOT NULL REFERENCES market(market_id),
    passenger_id UUID NOT NULL REFERENCES "user"(user_id),
    origin GEOGRAPHY(POINT, 4326) NOT NULL,
    destination GEOGRAPHY(POINT, 4326) NOT NULL,
    status SMALLINT NOT NULL DEFAULT 1,    -- 1=OPEN
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_trip_request_origin ON trip_request USING GIST(origin);
CREATE INDEX idx_trip_request_destination ON trip_request USING GIST(destination);

-- ----------------------------
-- 6. TRIPS
-- ----------------------------
CREATE TABLE trip (
    trip_id UUID PRIMARY KEY,
    trip_request_id UUID NOT NULL REFERENCES trip_request(trip_request_id),
    passenger_id UUID NOT NULL REFERENCES "user"(user_id),
    driver_id UUID NOT NULL REFERENCES "user"(user_id),
    origin GEOGRAPHY(POINT, 4326) NOT NULL,
    destination GEOGRAPHY(POINT, 4326) NOT NULL,
    status SMALLINT NOT NULL,             -- 0=ACCEPTED,1=EN_ROUTE,2=COMPLETED,3=CANCELLED,4=CANCELLED_BY_DRIVER
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_trip_origin ON trip USING GIST(origin);
CREATE INDEX idx_trip_destination ON trip USING GIST(destination);

-- ----------------------------
-- 7. MATCHING CANDIDATES (Replayable)
-- ----------------------------
CREATE TABLE matching_candidate (
    match_id UUID PRIMARY KEY,
    trip_request_id UUID NOT NULL REFERENCES trip_request(trip_request_id),
    driver_id UUID NOT NULL REFERENCES "user"(user_id),
    probability NUMERIC(5,4) NOT NULL,
    distance_meters NUMERIC,
    eta_seconds INT,
    seed BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_matching_candidate_trip ON matching_candidate(trip_request_id);

-- ----------------------------
-- 8. PRICING LOGS
-- ----------------------------
CREATE TABLE pricing (
    pricing_id UUID PRIMARY KEY,
    trip_request_id UUID NOT NULL REFERENCES trip_request(trip_request_id),
    calculation_id UUID NOT NULL,
    passenger_fare_total NUMERIC NOT NULL,
    driver_payout_total NUMERIC NOT NULL,
    platform_commission NUMERIC NOT NULL,
    passenger_breakdown JSONB,
    driver_breakdown JSONB,
    estimated_distance_meters INT,
    estimated_duration_seconds INT,
    demand_multiplier NUMERIC,
    pricing_model_version TEXT,
    pricing_tier TEXT,
    price_expires_at TIMESTAMP WITH TIME ZONE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    calculation_metadata JSONB
);

-- ----------------------------
-- 9. TELEMETRY EVENTS
-- ----------------------------
CREATE TABLE telemetry_event (
    event_id UUID PRIMARY KEY,
    entity_id UUID,                        -- trip_id, trip_request_id, driver_id
    event_type TEXT NOT NULL,
    metadata JSONB,
    reason_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_telemetry_entity ON telemetry_event(entity_id);

-- ----------------------------
-- 10. ML FEEDBACK
-- ----------------------------
CREATE TABLE ml_feedback (
    feedback_id UUID PRIMARY KEY,
    trip_request_id UUID NOT NULL REFERENCES trip_request(trip_request_id),
    matched_driver_id UUID NOT NULL REFERENCES "user"(user_id),
    candidate_list JSONB NOT NULL,
    success_flag BOOLEAN NOT NULL,
    driver_status_snapshot JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    metadata JSONB
);

-- ----------------------------
-- 11. A/B TESTING
-- ----------------------------
CREATE TABLE ab_test_allocation (
    allocation_id UUID PRIMARY KEY,
    trip_request_id UUID NOT NULL REFERENCES trip_request(trip_request_id),
    experiment_name TEXT NOT NULL,
    variant TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ----------------------------
-- 12. INDEXES FOR PERFORMANCE
-- ----------------------------
CREATE INDEX idx_driver_status_avail_loc ON driver_status(is_available) INCLUDE(location);
CREATE INDEX idx_trip_request_status ON trip_request(status);
CREATE INDEX idx_trip_status ON trip(status);
CREATE INDEX idx_pricing_trip_request ON pricing(trip_request_id);
