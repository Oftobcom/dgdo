CREATE TABLE IF NOT EXISTS passengers (
  id UUID PRIMARY KEY,
  name TEXT,
  phone TEXT
);

CREATE TABLE IF NOT EXISTS drivers (
  id UUID PRIMARY KEY,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  status TEXT
);

CREATE TABLE IF NOT EXISTS trips (
  id UUID PRIMARY KEY,
  passenger_id UUID REFERENCES passengers(id),
  driver_id UUID REFERENCES drivers(id),
  origin_lat DOUBLE PRECISION,
  origin_lon DOUBLE PRECISION,
  dest_lat DOUBLE PRECISION,
  dest_lon DOUBLE PRECISION,
  status TEXT
);