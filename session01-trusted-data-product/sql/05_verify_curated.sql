-- =====================================================
-- Session 01
-- Step 5: Verify the curated data product
-- =====================================================


-- -----------------------------------------------------
-- 1. Verify row count
-- -----------------------------------------------------

SELECT
    COUNT(*) AS curated_rows
FROM urban_curated.traffic;


-- Expected:
-- 1698


-- -----------------------------------------------------
-- 2. Verify monthly coverage
-- -----------------------------------------------------

SELECT
    year,
    month,
    COUNT(*) AS rows
FROM urban_curated.traffic
GROUP BY
    year,
    month
ORDER BY
    year,
    month;


-- Expected:
--
-- 12 months
-- 2025-06 through 2026-05


-- -----------------------------------------------------
-- 3. Verify required fields
-- -----------------------------------------------------

SELECT

    COUNT_IF(observation_date IS NULL)
        AS missing_date,

    COUNT_IF(intersection_name IS NULL)
        AS missing_intersection,

    COUNT_IF(vehicle_count IS NULL)
        AS missing_vehicle_count

FROM urban_curated.traffic;


-- Expected:
-- 0, 0, 0


-- -----------------------------------------------------
-- 4. Verify optional coordinates
-- -----------------------------------------------------

SELECT

    COUNT_IF(
        latitude IS NULL
        OR longitude IS NULL
    ) AS missing_coordinates

FROM urban_curated.traffic;


-- Expected:
-- 3


-- -----------------------------------------------------
-- 5. Compare an important total
-- -----------------------------------------------------

SELECT
    SUM(
        CAST(period_total_calc AS BIGINT)
    ) AS raw_vehicle_total
FROM urban_raw.traffic
WHERE
    observation_date IS NOT NULL
    AND intersection_name IS NOT NULL
    AND period_total_calc IS NOT NULL;


SELECT
    SUM(vehicle_count)
        AS curated_vehicle_total
FROM urban_curated.traffic;


-- Expected:
--
-- raw_vehicle_total = curated_vehicle_total
--
-- The exact equality is evidence that our transformation
-- preserved this important measure.

-- Remember:
--
-- "Query succeeded" only means the SQL executed.
--
-- It does NOT prove that the resulting dataset is correct.
--
-- Execution success != data correctness.
