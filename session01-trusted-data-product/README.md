# Session 01 — Trusted Data Products

## Theme

**Build a Trusted Curated Traffic Dataset**

## Goal

In this session, you will take raw monthly traffic files and turn them into a curated data product that downstream users can use with confidence.

You will build this workflow:

**Local files → Amazon S3 → AWS Glue Data Catalog → Amazon Athena → Understand → Validate → Define Data Contract → Curate → Verify**

## Key Question

> What is the difference between data that is queryable and data that is trustworthy?

## Learning Outcomes

By the end of this lab, you should be able to:

1. Ingest files into Amazon S3 using AWS CLI or AWS SDK.
2. Create a Glue Data Catalog table for data stored in S3.
3. Query and profile raw data using Athena.
4. Identify the grain, coverage, and basic quality issues of a dataset.
5. Define basic rules for a curated data product.
6. Create a curated Parquet dataset using Athena CTAS.
7. Verify that the curated result is correct.

---

## Dataset

The dataset contains monthly Bangkok traffic observations.

**Coverage:** June 2025 – May 2026  
**Expected raw records:** 1,698 rows  
**Expected number of months:** 12

The prepared data is organized by year and month.

Example:

```text
raw/traffic/
├── year=2025/
│   ├── month=06/
│   │   └── traffic_2025_06.csv
│   ├── month=07/
│   │   └── traffic_2025_07.csv
│   └── ...
└── year=2026/
    ├── month=01/
    └── ...
```

---

## Architecture

```text
Local computer
      |
      | upload
      v
Amazon S3
      |
      | metadata discovery
      v
AWS Glue Data Catalog
      |
      | SQL
      v
Amazon Athena
      |
      | CTAS
      v
Curated Parquet Data
```

Remember:

> **S3 stores files.**  
> **Glue describes the data.**  
> **Athena queries and transforms the data.**

---

# Part A — Make the Data Queryable

## Step 1 — Prepare AWS Access

Make sure your AWS credentials/session are available.

Check:

```bash
aws sts get-caller-identity
```

If the command fails, first make sure your AWS Learner Lab session is running and that the AWS CLI is using the current temporary credentials for that session.

---

## Step 2 — Upload the Raw Traffic Files

Choose **one** method:

- AWS CLI
- AWS SDK

See:

- `scripts/upload_cli.md`
- `scripts/upload_sdk.py`

Upload the monthly files to:

```text
s3://<YOUR_BUCKET>/raw/traffic/
```

Verify that all expected files exist before continuing.

---

## Step 3 — Create a Glue Database

Create a Glue database named:

```text
urban_raw
```

You may create it from the AWS Glue console.

---

## Step 4 — Create and Run a Glue Crawler

Configure the crawler to scan:

```text
s3://<YOUR_BUCKET>/raw/traffic/
```

Target database:

```text
urban_raw
```

After the crawler finishes, inspect:

- table name
- columns
- inferred data types
- S3 location
- partitions

Record your actual table name.

For the SQL examples in this repository, we assume:

```text
urban_raw.traffic
```

If your table has a different name, update the SQL accordingly.

---

## Step 5 — Query the Raw Table

Open Athena and run the queries in:

```text
sql/01_preview_raw.sql
```

### Checkpoint

> Can you query the data successfully?

Important:

> **Queryable does not yet mean trustworthy.**

---

# Part B — Understand the Raw Data

Run:

```text
sql/02_profile_raw.sql
```

Answer:

1. How many rows are present?
2. How many months are present?
3. What is the month coverage?
4. What does one row represent?

Expected:

```text
1,698 rows
12 months
2025-06 through 2026-05
```

Think about the **grain** before checking duplicates, joining data, or performing aggregation.

### Key Message

> **Understand the data before judging its quality.**

---

# Part C — Validate the Data

Run:

```text
sql/03_quality_checks.sql
```

Expected results:

| Check | Expected |
|---|---:|
| Missing observation date | 0 |
| Missing intersection name | 0 |
| Missing vehicle count | 0 |
| Missing coordinate | 3 |

Discuss:

> Should a record with missing coordinates be rejected?

Consider two consumers:

### Traffic Reporting

Coordinates may be optional.

### GIS Analysis

Coordinates may be required.

### Key Principle

> **Data quality = fit for purpose.**

---

# Part D — Define the Data Contract

Before transforming the data, decide what downstream users can expect.

## Grain

One row represents:

> one intersection road/approach × one observation date × one traffic time period

## Required Fields

- `observation_date`
- `intersection_name`
- `road_name`
- `time_period_code`
- `vehicle_count`

## Optional Fields

- `latitude`
- `longitude`

## Quality Rules

- required fields must not be `NULL`
- vehicle count must be numeric
- vehicle count should not be negative
- missing coordinates are allowed for this common traffic product

## Lineage Fields

Keep:

- `source_month`
- `source_file`
- `data_provenance`

## Storage Format

Curated data will be stored as:

```text
Parquet
```

partitioned by:

```text
year
month
```

---

# Part E — Curate the Data

First create the curated database.

Then edit:

```text
sql/04_create_curated_ctas.sql
```

Replace:

```text
<YOUR_BUCKET>
```

with your own S3 bucket.

Important:

The CTAS output path must be empty.

Example:

```text
s3://<YOUR_BUCKET>/curated/traffic/v1/
```

Run the CTAS query.

### Key Idea

> **The CTAS implements the Data Contract.**

---

# Part F — Verify the Result

Run:

```text
sql/05_verify_curated.sql
```

Expected:

```text
Curated rows = 1,698
Months = 12
Coverage = 2025-06 through 2026-05
Missing required fields = 0
Missing coordinates = 3
```

Also compare an important total between raw and curated data.

The result should be equal.

### Key Principle

> **Execution success ≠ data correctness.**

---

# Final Engineering Cycle

You have completed:

**Raw Data → Understand → Validate → Define Contract → Curate → Verify**

The goal is not only to create a table.

The goal is:

> **Turn raw data into a data product that others can use with confidence.**

---

# Reflection

Answer briefly:

1. What was the most difficult part of making the local data queryable in AWS?
2. How do S3, Glue Data Catalog, and Athena work together?
3. Why does successful Athena querying not mean that the dataset is trustworthy?
4. Why did we keep the three records with missing coordinates?
5. If a new monthly batch arrives, which steps should be automated?

---

# AI Reflection

If you used an AI assistant during the lab, reflect on what actually happened.

1. What did you use AI for?
2. Give one example where the AI answer worked. How did you verify it?
3. Give one example where the AI answer was incomplete, incorrect, or misleading.
4. What evidence did you use to check or correct the answer?
5. Which types of AWS/Data Engineering questions are suitable for AI assistance, and which should be verified carefully?

Possible evidence includes:

- AWS Console
- command output
- Athena query results
- error messages
- official documentation

---

# Next Session

Session 02 asks:

> **What happens when a new monthly traffic file arrives?**

We will turn this manual workflow into a repeatable batch pipeline.

You will extend the workflow toward:

**New Batch → Validate → Decide → Transform → Publish / Quarantine → Verify**
