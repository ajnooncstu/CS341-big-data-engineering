-- Teaching template: process only the new accepted batch.

SELECT
  CAST(observation_date AS DATE) AS observation_date,
  CAST(sequence_no AS INTEGER) AS sequence_no,
  intersection_name,
  road_name,
  time_period_code,
  time_period_th,
  CAST(passenger_car AS BIGINT) AS passenger_car,
  CAST(van_pickup AS BIGINT) AS van_pickup,
  CAST(large_bus AS BIGINT) AS large_bus,
  CAST(small_bus AS BIGINT) AS small_bus,
  CAST(truck AS BIGINT) AS truck,
  CAST(tuk_tuk AS BIGINT) AS tuk_tuk,
  CAST(period_total_calc AS BIGINT) AS vehicle_count,
  CAST(latitude AS DOUBLE) AS latitude,
  CAST(longitude AS DOUBLE) AS longitude,
  source_month,
  source_file,
  data_provenance
FROM urban_raw.traffic_incoming
WHERE source_month = '2026-06'
  AND observation_date IS NOT NULL
  AND intersection_name IS NOT NULL
  AND period_total_calc IS NOT NULL;
