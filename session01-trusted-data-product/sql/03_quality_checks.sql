-- =====================================================
-- Session 01
-- Step 3: Validate the raw dataset
-- =====================================================


-- -----------------------------------------------------
-- Check important missing values
-- -----------------------------------------------------

SELECT
    COUNT_IF(observation_date IS NULL)
        AS missing_date,

    COUNT_IF(intersection_name IS NULL)
        AS missing_intersection,

    COUNT_IF(period_total_calc IS NULL)
        AS missing_vehicle_count,

    COUNT_IF(latitude IS NULL OR longitude IS NULL)
        AS missing_coordinates

FROM urban_raw.traffic;


-- Expected:
--
-- missing_date          = 0
-- missing_intersection  = 0
-- missing_vehicle_count = 0
-- missing_coordinates   = 3
