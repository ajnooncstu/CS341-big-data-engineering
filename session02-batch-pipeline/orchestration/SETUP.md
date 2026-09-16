# Create the Session 02 Step Functions Workflow

Complete `lambda/DEPLOYMENT.md` first.

You should already have five Lambda functions and their ARNs.

---

# 1. Open the State Machine Template

Open:

```text
orchestration/state-machine.json
```

The file contains placeholders:

```text
<CHECK_BATCH_LAMBDA_ARN>
<VALIDATE_BATCH_LAMBDA_ARN>
<TRANSFORM_BATCH_LAMBDA_ARN>
<VERIFY_BATCH_LAMBDA_ARN>
<QUARANTINE_BATCH_LAMBDA_ARN>
```

Replace each placeholder with the corresponding Lambda ARN.

---

# 2. Create the State Machine

AWS Console:

**Step Functions → State machines → Create state machine**

Choose a workflow creation option that allows you to edit the state machine definition.

Paste the completed JSON definition.

Suggested name:

```text
cs341-monthly-traffic-pipeline
```

Use the execution role available in the Learner Lab.

The role must be able to invoke the five Lambda functions.

---

# 3. Understand the Workflow Before Running

```text
CheckBatch
    |
AlreadyProcessed?
   /          \
 YES          NO
  |            |
 Stop       ValidateBatch
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

The Choice states inspect:

```text
$.status
```

and:

```text
$.validation_status
```

Because each Lambda returns the original event fields together with its result, the next state can continue using:

- `batch_id`
- `bucket`
- `key`

---

# 4. Run the Valid Batch

Choose:

**Start execution**

Input:

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
→ AlreadyProcessed?
→ ValidateBatch
→ Valid?
→ TransformBatch
→ VerifyBatch
```

Expected final verification:

```text
verify_status = PASS
```

After success, S3 should contain:

```text
processed/traffic/batch_id=2026-06/_SUCCESS.json
```

---

# 5. Run the Invalid Batch

Input:

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
→ ValidateBatch
→ Valid?
→ QuarantineBatch
```

Expected S3 destination:

```text
quarantine/traffic/batch_id=2026-06-bad/
```

---

# 6. Rerun the Valid Batch

Use the same input as Run 1.

Expected path:

```text
CheckBatch
→ AlreadyProcessed?
→ AlreadyProcessed
```

`TransformBatch` should not run again.

This demonstrates the lab's idempotency policy.

---

# 7. If the Workflow Fails

Use Step Functions execution history.

Identify:

- which state failed;
- state input;
- state output;
- error name;
- error cause.

Then decide whether it is:

- permissions;
- bad input;
- wrong S3 key;
- missing environment variable;
- Athena error;
- schema mismatch.

Do not rerun blindly.

---

# Checkpoint Questions

1. Which state makes the duplicate-batch decision?
2. Which field does the first Choice state inspect?
3. Which field does the validation Choice state inspect?
4. Why is verification after transformation?
5. Why is the success marker created only after verification passes?

---

# Key Principle

> **The state machine is the control flow, not the data-processing logic itself.**
