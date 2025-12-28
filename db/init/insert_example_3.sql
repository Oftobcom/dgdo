--- Zone Coverage and Driver Supply Analytics
-- INSERT: Optional pre-computation of zone supply
INSERT INTO zone_supply (zone_id, available_drivers, snapshot_time)
SELECT z.id AS zone_id,
       COUNT(ds.driver_id) AS available_drivers,
       NOW() AS snapshot_time
FROM zones z
LEFT JOIN driver_status ds
  ON ST_Contains(z.polygon, ds.location)
  AND ds.status = 'AVAILABLE'
GROUP BY z.id;

-- SELECT: Current driver supply per zone
SELECT z.id AS zone_id,
       z.name AS zone_name,
       COUNT(ds.driver_id) AS available_drivers,
       MIN(ST_Distance(ds.location::geography, ST_Centroid(z.polygon)::geography)) AS min_distance_to_center,
       MAX(ST_Distance(ds.location::geography, ST_Centroid(z.polygon)::geography)) AS max_distance_to_center
FROM zones z
LEFT JOIN driver_status ds
  ON ST_Contains(z.polygon, ds.location)
  AND ds.status = 'AVAILABLE'
GROUP BY z.id, z.name
ORDER BY available_drivers ASC;

-- SELECT: Historical coverage trends (last 7 days)
SELECT zone_id,
       DATE(snapshot_time) AS day,
       AVG(available_drivers) AS avg_drivers,
       MIN(available_drivers) AS min_drivers,
       MAX(available_drivers) AS max_drivers
FROM zone_supply
WHERE snapshot_time >= NOW() - INTERVAL '7 days'
GROUP BY zone_id, DATE(snapshot_time)
ORDER BY zone_id, day;
