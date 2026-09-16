# Session 02 — Lambda Functions

This folder contains the five AWS Lambda functions used by the Session 02 Step Functions workflow.

```text
lambda/
├── README.md
├── check_batch/
│   └── lambda_function.py
├── validate_batch/
│   └── lambda_function.py
├── transform_batch/
│   └── lambda_function.py
├── verify_batch/
│   └── lambda_function.py
└── quarantine_batch/
    └── lambda_function.py
```

## Workflow

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

## Common Step Functions Input

Start a valid execution with input similar to:

```json
{
  "batch_id": "2026-06",
  "bucket": "YOUR-BUCKET",
  "key": "incoming/traffic/batch_id=2026-06/traffic_2026_06.csv"
}
```

For the invalid batch:

```json
{
  "batch_id": "2026-06-bad",
  "bucket": "YOUR-BUCKET",
  "key": "incoming/traffic/batch_id=2026-06-bad/traffic_2026_06_bad.csv"
}
```

Each Lambda returns the original input plus its own result fields so the next state can continue using `batch_id`, `bucket`, and `key`.

---

# 1. check_batch

AWS Lambda name:

```text
cs341-check-batch
```

Purpose:

- Check whether the logical batch already has a success marker in S3.
- Return either `NEW` or `ALREADY_PROCESSED`.

Success marker:

```text
processed/traffic/batch_id=<BATCH_ID>/_SUCCESS.json
```

No additional Python package is required.

---

# 2. validate_batch

AWS Lambda name:

```text
cs341-validate-batch
```

Purpose:

- Read the incoming CSV directly from S3.
- Check required columns.
- Check row count > 0.
- Check required field values.
- Check negative traffic counts.
- Check that `source_month` matches the expected batch month.

For `batch_id=2026-06-bad`, the function treats the expected month as `2026-06`.

Output contains:

```json
{
  "validation_status": "PASS",
  "row_count": 150,
  "missing_required_values": 0,
  "negative_counts": 0,
  "wrong_month_rows": 0
}
```

or `validation_status = FAIL`.

No additional Python package is required.

---

# 3. transform_batch

AWS Lambda name:

```text
cs341-transform-batch
```

Purpose:

- Create a temporary Athena external table over the incoming CSV.
- Insert only the accepted new batch into the existing `urban_curated.traffic` table.
- Keep the same curated schema used in Session 1.

This function uses Athena because the curated table from Session 1 is Parquet.

## Required environment variables

Set these in the Lambda configuration:

```text
ATHENA_OUTPUT=s3://YOUR-BUCKET/athena-results/
RAW_DATABASE=urban_raw
CURATED_DATABASE=urban_curated
CURATED_TABLE=traffic
```

The Lambda execution role needs permission to:

- read the incoming S3 object;
- read/write the curated S3 location used by Athena;
- write to `ATHENA_OUTPUT`;
- run Athena queries;
- create/drop the temporary Glue/Athena table;
- read the Data Catalog.

Recommended Lambda timeout for this teaching lab:

```text
120 seconds
```

or more if your Learner Lab is slow.

Important:

This teaching implementation waits for Athena queries to finish inside the Lambda. It is intentionally simple for the lab, not a production-scale pattern.

---

# 4. verify_batch

AWS Lambda name:

```text
cs341-verify-batch
```

Purpose:

- Query the curated table after transformation.
- Check that the new batch exists.
- Compare curated row count against the validated input row count.
- Check required fields.
- Create the `_SUCCESS.json` marker only after verification passes.

## Required environment variables

```text
ATHENA_OUTPUT=s3://YOUR-BUCKET/athena-results/
CURATED_DATABASE=urban_curated
CURATED_TABLE=traffic
```

The execution role needs Athena, Glue read, and S3 read/write permissions.

Recommended timeout:

```text
120 seconds
```

---

# 5. quarantine_batch

AWS Lambda name:

```text
cs341-quarantine-batch
```

Purpose:

- Copy a failed incoming file to a quarantine prefix.
- Keep the original incoming file by default so the failure remains traceable.

Destination:

```text
quarantine/traffic/batch_id=<BATCH_ID>/<filename>
```

If you later want a move instead of a copy, you can add `delete_object()` after a successful copy.

---

# Lambda Runtime

Use:

```text
Python 3.12
```

All functions use only the Python standard library and `boto3`, which is available in the AWS Lambda Python runtime.

No Lambda Layer is required.

---

# Suggested IAM Permissions

For a teaching lab, the exact IAM role depends on AWS Academy / Learner Lab restrictions.

Conceptually the Lambda functions need permission for:

- `s3:GetObject`
- `s3:PutObject`
- `s3:HeadObject`
- `s3:CopyObject` through normal S3 API permissions
- `athena:StartQueryExecution`
- `athena:GetQueryExecution`
- `athena:GetQueryResults`
- relevant Glue Data Catalog table/database actions for the temporary incoming table

Use the role supplied by the Learner Lab if your environment does not allow creating custom IAM roles.

---

# Step Functions Choice Fields

The state machine can branch on these fields.

After `check_batch`:

```text
$.status
```

Possible values:

```text
NEW
ALREADY_PROCESSED
```

After `validate_batch`:

```text
$.validation_status
```

Possible values:

```text
PASS
FAIL
```

---

# Teaching Notes

The important architectural separation is:

> **Step Functions = orchestration**

> **Lambda = small control/helper tasks**

> **Athena = data transformation and verification**

> **S3 = incoming, curated, quarantine, and processing evidence**

The purpose of Session 02 is not to master Lambda programming. The Lambda code is provided so students can focus on pipeline behavior, branching, failure handling, and idempotency.
