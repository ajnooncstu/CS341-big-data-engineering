-- =====================================================
-- Session 01
-- Step 2: Understand the raw dataset
-- =====================================================


-- -----------------------------------------------------
-- 1. Total number of rows
-- -----------------------------------------------------

SELECT
    COUNT(*) AS row_count
FROM urban_raw.traffic;


-- Expected:
-- 1698


-- -----------------------------------------------------
-- 2. Monthly coverage
-- -----------------------------------------------------

SELECT
    year,
    month,
    COUNT(*) AS rows
FROM urban_raw.traffic
GROUP BY
    year,
    month
ORDER BY
    year,
    month;


-- Expected:
-- 12 months
-- 2025-06 through 2026-05


-- -----------------------------------------------------
-- 3. Inspect several records
-- -----------------------------------------------------

SELECT
    observation_date,
    intersection_name,
    road_name,
    time_period_code,
    period_total_calc,
    latitude,
    longitude
FROM urban_raw.traffic
LIMIT 30;

-- Question:
--
-- What does one row represent?
--
-- Suggested interpretation:
--
-- One intersection road/approach
-- x one observation date
-- x one traffic time period.
