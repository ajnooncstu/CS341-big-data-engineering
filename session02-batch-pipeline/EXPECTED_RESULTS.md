# Expected Results — Session 02

## Valid batch
Expected: `PASS`

## Invalid batch
Expected: `FAIL` because exactly one required `observation_date` is missing.

## Rerun
Expected: `ALREADY_PROCESSED`

## Principles
- Arrival ≠ acceptance
- Validation controls whether data may continue
- Failed data should remain traceable
- Retry should not create duplicates
- Execution success ≠ data correctness
