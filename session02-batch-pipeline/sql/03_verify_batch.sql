SELECT source_month, COUNT(*) AS rows
FROM urban_curated.traffic
GROUP BY source_month
ORDER BY source_month;

SELECT
  COUNT_IF(observation_date IS NULL) AS missing_date,
  COUNT_IF(intersection_name IS NULL) AS missing_intersection,
  COUNT_IF(vehicle_count IS NULL) AS missing_vehicle_count
FROM urban_curated.traffic
WHERE source_month = '2026-06';
