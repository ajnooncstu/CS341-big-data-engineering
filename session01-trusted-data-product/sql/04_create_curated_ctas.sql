-- =====================================================
-- Session 01
-- Step 4: Create the curated traffic data product
-- =====================================================


-- -----------------------------------------------------
-- Create curated database
-- -----------------------------------------------------

CREATE DATABASE IF NOT EXISTS urban_curated;


-- -----------------------------------------------------
-- Create curated Parquet dataset
--
-- IMPORTANT:
--
-- Replace <YOUR_BUCKET>
--
-- The S3 output location must be EMPTY before running
-- this CTAS query.
-- -----------------------------------------------------

CREATE TABLE urban_curated.traffic

WITH (

    format = 'PARQUET',

    external_location =
        's3://<YOUR_BUCKET>/curated/traffic/v1/',

    partitioned_by = ARRAY['year', 'month']

)

AS

SELECT

    CAST(observation_date AS DATE)
        AS observation_date,

    CAST(sequence_no AS INTEGER)
        AS sequence_no,

    intersection_name,

    road_name,

    time_period_code,

    time_period_th,

    CAST(passenger_car AS BIGINT)
        AS passenger_car,

    CAST(van_pickup AS BIGINT)
        AS van_pickup,

    CAST(large_bus AS BIGINT)
        AS large_bus,

    CAST(small_bus AS BIGINT)
        AS small_bus,

    CAST(truck AS BIGINT)
        AS truck,

    CAST(tuk_tuk AS BIGINT)
        AS tuk_tuk,

    CAST(period_total_calc AS BIGINT)
        AS vehicle_count,

    CAST(latitude AS DOUBLE)
        AS latitude,

    CAST(longitude AS DOUBLE)
        AS longitude,

    source_month,

    source_file,

    data_provenance,

    CAST(year AS INTEGER)
        AS year,

    LPAD(
        CAST(month AS VARCHAR),
        2,
        '0'
    ) AS month

FROM urban_raw.traffic

WHERE

    observation_date IS NOT NULL

    AND intersection_name IS NOT NULL

    AND period_total_calc IS NOT NULL;

-- =====================================================
-- What did this CTAS do?
--
-- 1. Selected the curated schema.
-- 2. Enforced data types.
-- 3. Renamed period_total_calc -> vehicle_count.
-- 4. Applied required-field quality rules.
-- 5. Retained lineage fields.
-- 6. Stored output as Parquet.
-- 7. Partitioned output by year and month.
--
-- Notice:
--
-- latitude / longitude are NOT included in the WHERE
-- condition.
--
-- Therefore records with missing coordinates remain.
--
-- Expected curated rows = 1698.
-- =====================================================
