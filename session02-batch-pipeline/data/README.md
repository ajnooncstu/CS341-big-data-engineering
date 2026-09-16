# Session 02 Test Data

- `valid/traffic_2026_06.csv`
  - teaching-simulated June 2026 batch
  - expected validation result: `PASS`

- `invalid/traffic_2026_06_bad.csv`
  - same schema
  - exactly one deliberately missing `observation_date`
  - expected validation result: `FAIL`

Both files use the 25-column Session 1 raw-file schema.
