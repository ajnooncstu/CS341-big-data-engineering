-- Optional Athena-side validation after incoming data is exposed as a table.

SELECT
  COUNT(*) AS row_count,
  COUNT_IF(observation_date IS NULL) AS missing_date,
  COUNT_IF(intersection_name IS NULL) AS missing_intersection,
  COUNT_IF(period_total_calc IS NULL) AS missing_vehicle_count
FROM urban_raw.traffic_incoming;
