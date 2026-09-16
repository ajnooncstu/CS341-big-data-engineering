# Deploy the Session 02 Lambda Functions

The Lambda code is already provided.

You will create five AWS Lambda functions and paste/upload the supplied code.

Use runtime:

```text
Python 3.12
```

Handler:

```text
lambda_function.lambda_handler
```

---

# 1. Create `cs341-check-batch`

AWS Console:

**Lambda → Create function → Author from scratch**

Name:

```text
cs341-check-batch
```

Runtime:

```text
Python 3.12
```

Use the Learner Lab execution role available to you.

Upload or paste:

```text
lambda/check_batch/lambda_function.py
```

No environment variables are required.

Recommended timeout:

```text
30 seconds
```

Test input:

```json
{
  "batch_id": "2026-06",
  "bucket": "YOUR-BUCKET",
  "key": "incoming/traffic/batch_id=2026-06/traffic_2026_06.csv"
}
```

Before a successful pipeline run, expected:

```text
status = NEW
```

---

# 2. Create `cs341-validate-batch`

Name:

```text
cs341-validate-batch
```

Upload/paste:

```text
lambda/validate_batch/lambda_function.py
```

No environment variables are required.

Recommended timeout:

```text
30 seconds
```

Test it after the valid file has been uploaded to S3.

Expected:

```text
validation_status = PASS
```

For the bad file:

```text
validation_status = FAIL
```

---

# 3. Create `cs341-transform-batch`

Name:

```text
cs341-transform-batch
```

Upload/paste:

```text
lambda/transform_batch/lambda_function.py
```

Recommended timeout:

```text
120 seconds
```

Set environment variables:

```text
ATHENA_OUTPUT=s3://YOUR-BUCKET/athena-results/
RAW_DATABASE=urban_raw
CURATED_DATABASE=urban_curated
CURATED_TABLE=traffic
```

This function:

1. creates a temporary Athena external table over the incoming CSV;
2. inserts accepted rows into the existing curated table;
3. waits for Athena to finish.

This is a teaching implementation, not a production pattern.

---

# 4. Create `cs341-verify-batch`

Name:

```text
cs341-verify-batch
```

Upload/paste:

```text
lambda/verify_batch/lambda_function.py
```

Recommended timeout:

```text
120 seconds
```

Environment variables:

```text
ATHENA_OUTPUT=s3://YOUR-BUCKET/athena-results/
CURATED_DATABASE=urban_curated
CURATED_TABLE=traffic
```

This function verifies the batch and creates:

```text
processed/traffic/batch_id=<BATCH_ID>/_SUCCESS.json
```

only after verification succeeds.

---

# 5. Create `cs341-quarantine-batch`

Name:

```text
cs341-quarantine-batch
```

Upload/paste:

```text
lambda/quarantine_batch/lambda_function.py
```

Recommended timeout:

```text
30 seconds
```

No environment variables are required.

This function copies failed input to:

```text
quarantine/traffic/batch_id=<BATCH_ID>/
```

The original incoming object is kept for traceability.

---

# 6. Record the Function ARNs

After creating the five functions, record each ARN.

Example format:

```text
arn:aws:lambda:ap-southeast-1:123456789012:function:cs341-check-batch
```

You will need the ARNs when configuring:

```text
orchestration/state-machine.json
```

Record:

```text
CHECK_BATCH_LAMBDA_ARN=
VALIDATE_BATCH_LAMBDA_ARN=
TRANSFORM_BATCH_LAMBDA_ARN=
VERIFY_BATCH_LAMBDA_ARN=
QUARANTINE_BATCH_LAMBDA_ARN=
```

---

# 7. Quick Function Test Order

Before building Step Functions, test:

1. `check_batch`
2. `validate_batch`

These are the easiest to debug individually.

Then create the Step Functions workflow and test transform/verify in the integrated flow.

---

# Key Principle

Lambda is not the main learning objective.

The functions are intentionally provided so that the lab can focus on:

- validation gates
- branching
- orchestration
- quarantine
- idempotency
- verification
