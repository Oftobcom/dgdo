--- Real-time Candidate Lookup for a Trip Request
-- INSERT: Update driver location / status in real-time
INSERT INTO driver_status (driver_id, location, status, updated_at)
VALUES ('driver_123', ST_SetSRID(ST_MakePoint(69.6, 40.2), 4326), 'AVAILABLE', NOW())
ON CONFLICT (driver_id) DO UPDATE
SET location = EXCLUDED.location,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at;

-- SELECT: Find top N closest available drivers within a 5 km radius
WITH candidates AS (
    SELECT d.id AS driver_id,
           ST_Distance(d.location::geography, ST_SetSRID(ST_MakePoint(:trip_lon, :trip_lat), 4326)::geography) AS distance_meters,
           d.rating,
           ds.acceptance_rate
    FROM drivers d
    JOIN driver_status ds ON ds.driver_id = d.id
    WHERE ds.status = 'AVAILABLE'
)
SELECT driver_id, distance_meters, rating, acceptance_rate
FROM candidates
ORDER BY distance_meters ASC
LIMIT :max_candidates;

