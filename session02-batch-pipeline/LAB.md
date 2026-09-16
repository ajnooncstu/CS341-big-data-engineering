# Session 02 Lab — Batch Data Pipelines and Orchestration

## Theme

**Automating Monthly Traffic Data Ingestion**

## Main Question

> How can we process a new monthly batch repeatedly without publishing bad or duplicate data?

The lab uses three experiments:

1. valid batch → `PASS` → publish
2. invalid batch → `FAIL` → quarantine
3. rerun valid batch → `ALREADY_PROCESSED`

---

# Part 0 — Precheck

Before starting, complete:

`PRECHECK.md`

You should already have:

- Session 1 S3 bucket
- `urban_raw`
- `urban_curated.traffic`
- Athena working
- current AWS Learner Lab credentials

---

# Part 1 — Upload the Valid Batch

Set current AWS Learner Lab credentials in Windows `cmd`.

Then verify:

```cmd
aws sts get-caller-identity
```

From the `session02-batch-pipeline` folder, upload:

```cmd
aws s3 cp data\valid\traffic_2026_06.csv s3://<YOUR_BUCKET>/incoming/traffic/batch_id=2026-06/
```

Verify:

```cmd
aws s3 ls s3://<YOUR_BUCKET>/incoming/traffic/batch_id=2026-06/
```

## Checkpoint 1

Confirm:

- batch ID = `2026-06`
- file exists in incoming
- file has not yet reached curated data

Key principle:

> **Arrival ≠ acceptance.**

---

# Part 2 — Run Local Validation

Run:

```cmd
python scripts\validate_batch.py data\valid\traffic_2026_06.csv --expected-month 2026-06
```

Expected:

```text
"status": "PASS"
```

Record:

- row count
- missing required values
- negative counts
- wrong-month rows

Ask:

> What evidence supports the PASS decision?

---

# Part 3 — Test the Invalid Batch

Run:

```cmd
python scripts\validate_batch.py data\invalid\traffic_2026_06_bad.csv --expected-month 2026-06
```

Expected:

```text
"status": "FAIL"
```

The prepared bad file contains one missing required `observation_date`.

Upload it only when instructed:

```cmd
aws s3 cp data\invalid\traffic_2026_06_bad.csv s3://<YOUR_BUCKET>/incoming/traffic/batch_id=2026-06-bad/
```

Key principle:

> **Failed data should remain traceable.**

---

# Part 4 — Deploy Lambda Functions

Follow:

`lambda/DEPLOYMENT.md`

Create these functions:

- `cs341-check-batch`
- `cs341-validate-batch`
- `cs341-transform-batch`
- `cs341-verify-batch`
- `cs341-quarantine-batch`

Do not write them from scratch. Use the provided code.

---

# Part 5 — Create the Step Functions Workflow

Follow:

`orchestration/SETUP.md`

Workflow:

```text
CheckBatch
    |
AlreadyProcessed?
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

Key distinction:

> **Transformation changes the data.**

> **Orchestration controls what runs, in what order, and what happens when something fails.**

---

# Part 6 — Experiment 1: Valid Batch

Start the Step Functions execution with:

```json
{
  "batch_id": "2026-06",
  "bucket": "YOUR-BUCKET",
  "key": "incoming/traffic/batch_id=2026-06/traffic_2026_06.csv"
}
```

Expected path:

```text
CheckBatch
→ NEW
→ ValidateBatch
→ PASS
→ TransformBatch
→ VerifyBatch
→ SUCCESS
```

Record:

- execution name
- batch ID
- validation result
- transform result
- verification result

Then verify in Athena and S3.

Use:

- `sql/03_verify_batch.sql`
- `sql/04_check_duplicate_batch.sql`

## Checkpoint 2

Show:

- Step Functions execution path
- June 2026 in curated data
- evidence that historical data remains

Key principle:

> **Execution success ≠ data correctness.**

---

# Part 7 — Experiment 2: Invalid Batch

Start another execution:

```json
{
  "batch_id": "2026-06-bad",
  "bucket": "YOUR-BUCKET",
  "key": "incoming/traffic/batch_id=2026-06-bad/traffic_2026_06_bad.csv"
}
```

Expected path:

```text
CheckBatch
→ NEW
→ ValidateBatch
→ FAIL
→ QuarantineBatch
```

Verify:

```cmd
aws s3 ls s3://<YOUR_BUCKET>/quarantine/traffic/batch_id=2026-06-bad/
```

The invalid batch should not be published to curated data.

## Checkpoint 3

Show:

- failure evidence
- quarantine location
- curated data unchanged

---

# Part 8 — Experiment 3: Rerun the Valid Batch

Run the same valid input again:

```json
{
  "batch_id": "2026-06",
  "bucket": "YOUR-BUCKET",
  "key": "incoming/traffic/batch_id=2026-06/traffic_2026_06.csv"
}
```

Expected:

```text
CheckBatch
→ ALREADY_PROCESSED
→ Stop
```

The workflow should not transform or publish June again.

Verify that the June row count did not double.

Key principle:

> **Retry should not create duplicates.**

---

# Part 9 — Final Reflection

Answer:

1. Why do we separate `incoming`, `quarantine`, and `curated`?
2. Which validation rule stopped the bad batch?
3. Why is retry useful for some failures but not for bad data?
4. Why does the pipeline need a `batch_id`?
5. What evidence proves that the valid batch was processed correctly?
6. How does the `_SUCCESS.json` marker help with idempotency?

---

# Session Summary

Session 1:

**Understand → Validate → Define Contract → Curate → Verify**

Session 2:

**Detect New Batch → Validate → Decide → Transform → Publish / Quarantine → Verify → Record Evidence**

The goal is:

> **Correct once is not enough. A data pipeline should be repeatable, safe, and observable.**
