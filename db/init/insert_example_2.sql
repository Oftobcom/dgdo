--- ML Feature Extraction
-- INSERT: Example: store features per driver-trip combination for training
INSERT INTO ml_features (trip_request_id, driver_id, distance_meters, eta_seconds, surge_multiplier, created_at)
SELECT tr.id AS trip_request_id,
       d.id AS driver_id,
       ST_Distance(d.location::geography, tr.origin::geography) AS distance_meters,
       ST_Distance(d.location::geography, tr.origin::geography)/15 AS eta_seconds,  -- assume 15 m/s avg speed
       p.demand_multiplier AS surge_multiplier,
       NOW() AS created_at
FROM trip_requests tr
JOIN driver_status ds ON ds.status = 'AVAILABLE'
JOIN drivers d ON d.id = ds.driver_id
JOIN pricing p ON p.trip_request_id = tr.id
WHERE tr.status = 'OPEN';

-- SELECT: Extract features for training ML model
SELECT trip_request_id,
       driver_id,
       distance_meters,
       eta_seconds,
       surge_multiplier,
       driver_rating,
       driver_acceptance_rate
FROM ml_features
WHERE created_at > NOW() - INTERVAL '1 day';
