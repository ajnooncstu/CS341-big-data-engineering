# Session 02 — Batch Data Pipelines and Orchestration

## Theme
**Automating Monthly Traffic Data Ingestion**

## Goal
In Session 1, we manually built a trustworthy curated traffic dataset.

This session asks:

> **What happens when a new monthly batch arrives?**

Workflow:

**New Batch → Validate → Decide → Transform → Publish / Quarantine → Verify**

## Key Question
> How can we process a new monthly batch repeatedly without publishing bad or duplicate data?

## Learning Outcomes
By the end of this lab, you should be able to:
1. Explain why a manual data workflow should be automated.
2. Design a repeatable monthly batch pipeline.
3. Define validation rules for a new incoming batch.
4. Explain why invalid data should be quarantined.
5. Explain the role of an orchestrator.
6. Explain idempotency and safe reruns.
7. Verify both pipeline execution and data correctness.

## Starting Point
You should already have the Session 1 environment:
- S3 bucket
- raw traffic data in S3
- Glue database `urban_raw`
- Glue table for historical traffic data
- Athena working
- curated traffic data from Session 1

Historical coverage: **June 2025 – May 2026**

New batch: **June 2026**

## Architecture

```text
New Monthly Batch
       |
       v
   S3 Incoming
       |
       v
    Validate
       |
     Choice
    /      \
 PASS      FAIL
  |          |
  v          v
Transform  Quarantine
  |
  v
Publish
  |
  v
Verify
```

## Part A — New Batch Arrives
Prepare two inputs:
- valid June 2026 batch
- invalid June 2026 batch

See `data/README.md`.

Upload the valid batch to:

```text
s3://<YOUR_BUCKET>/incoming/traffic/batch_id=2026-06/
```

Follow `scripts/upload_batch_cli.md`.

### Key Message
> **Arrival ≠ acceptance.**

## Part B — Define the Validation Gate
Suggested rules:
1. Input file exists.
2. Expected schema is present.
3. Row count > 0.
4. Required fields are not missing.
5. Batch month is correct.
6. Vehicle counts are not negative.

Validation should produce `PASS` or `FAIL` plus evidence.

### Key Message
> **Validation controls whether data may continue.**

## Part C — Valid and Invalid Batch Experiments
Valid input:
`data/valid/traffic_2026_06.csv`

Expected:
`Incoming → Validate → PASS → Transform → Publish → Verify`

See `tests/01_valid_batch.md`.

Invalid input:
`data/invalid/traffic_2026_06_bad.csv`

Expected:
`Incoming → Validate → FAIL → Quarantine`

See `tests/02_invalid_batch.md`.

### Key Message
> **Failed data should remain traceable.**

## Part D — Orchestration
New tool: **AWS Step Functions**

```text
Start
  |
Check Batch
  |
Already Processed?
   /          \
 YES          NO
  |            |
 Stop       Validate
               |
             Valid?
             /    \
           YES     NO
            |       |
       Transform  Quarantine
            |
          Verify
            |
          Success
```

See `orchestration/README.md`.

> **Transformation changes the data.**
>
> **Orchestration controls what runs, in what order, and what happens when something fails.**

## Part E — Rerun Safely
Use:

```text
batch_id = 2026-06
```

After a successful run, run the same batch again.

Preferred teaching behavior:

```text
ALREADY_PROCESSED
```

See `tests/03_rerun_same_batch.md`.

### Idempotency
> **Running the same batch again should not silently create duplicate or inconsistent results.**

### Key Message
> **Retry should not create duplicates.**

## Part F — Verify and Observe
Verify both:

### Pipeline evidence
- batch ID
- execution status
- validation result
- start/end time
- failure reason

### Data evidence
- June 2026 exists after success
- historical data remains
- required fields are valid
- no duplicate June batch
- failed batch does not appear in curated data

### Key Message
> **Execution success ≠ data correctness.**

## Checkpoints
1. Pipeline design
2. PASS vs FAIL
3. End-to-end successful run
4. Rerun same batch

## Final Engineering Cycle
Session 1:
**Understand → Validate → Define Contract → Curate → Verify**

Session 2:
**Detect New Batch → Validate → Decide → Transform → Publish / Quarantine → Verify → Record Evidence**

## Reflection
1. Which step was hardest to automate?
2. What evidence supports PASS/FAIL?
3. Why quarantine instead of delete?
4. What can happen if the same batch runs twice?
5. How does batch identity support idempotency?
6. Why is workflow success not enough to prove data correctness?

## AI Reflection
1. What did AI help you with?
2. Give one useful AI suggestion and how you verified it.
3. Give one incomplete/wrong suggestion.
4. What evidence did you use to correct it?

## Next Session
> What happens when already-published data needs to change?

**Session 03 — Lakehouse Data Management**
