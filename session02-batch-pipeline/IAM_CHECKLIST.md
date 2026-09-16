# IAM / Permission Checklist — Session 02

AWS Academy / Learner Lab may restrict IAM changes.

Use the role provided by your lab environment whenever possible.

The goal of this checklist is to identify what access is required conceptually.

---

# Step Functions Role

Step Functions needs permission to invoke the five Lambda functions:

- `cs341-check-batch`
- `cs341-validate-batch`
- `cs341-transform-batch`
- `cs341-verify-batch`
- `cs341-quarantine-batch`

Conceptually:

```text
lambda:InvokeFunction
```

---

# Lambda: check_batch

Needs to check whether this object exists:

```text
processed/traffic/batch_id=<BATCH_ID>/_SUCCESS.json
```

Required conceptual permission:

```text
s3:GetObject
```

or equivalent object metadata access.

---

# Lambda: validate_batch

Needs to read the incoming CSV.

Required conceptual permission:

```text
s3:GetObject
```

for:

```text
incoming/traffic/*
```

---

# Lambda: quarantine_batch

Needs:

- read incoming object
- write quarantine object

Conceptually:

```text
s3:GetObject
s3:PutObject
```

for incoming/quarantine prefixes.

---

# Lambda: transform_batch

Needs to:

- read incoming data
- run Athena queries
- use Glue Data Catalog
- write Athena result files
- write new curated Parquet data through Athena

Conceptual permissions include:

```text
s3:GetObject
s3:PutObject
athena:StartQueryExecution
athena:GetQueryExecution
athena:GetQueryResults
glue:GetDatabase
glue:GetTable
glue:CreateTable
glue:DeleteTable
```

Exact requirements may vary depending on the Learner Lab role.

---

# Lambda: verify_batch

Needs:

- run Athena query
- read Data Catalog metadata
- write Athena result files
- create the success marker in S3

Conceptually:

```text
athena:StartQueryExecution
athena:GetQueryExecution
athena:GetQueryResults
glue:GetDatabase
glue:GetTable
s3:GetObject
s3:PutObject
```

---

# Important for AWS Academy

Do not spend the lab building complex IAM policies unless your environment allows it.

If a function fails with:

```text
AccessDenied
```

record:

1. which function failed;
2. which AWS action was denied;
3. which resource it attempted to access.

Then check whether the Learner Lab provides a preconfigured role that should be used instead.

This is operational evidence, not merely a coding error.
