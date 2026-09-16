# Session 02 Precheck

Complete this before the lab.

---

## 1. AWS Learner Lab

Confirm that the Learner Lab is running.

In Windows `cmd`, set your current temporary credentials:

```cmd
set AWS_ACCESS_KEY_ID=<your access key>
set AWS_SECRET_ACCESS_KEY=<your secret key>
set AWS_SESSION_TOKEN=<your session token>
```

Test:

```cmd
aws sts get-caller-identity
```

Expected: your AWS account/user information is returned.

---

## 2. Session 1 Raw Data

Confirm that the raw data still exists:

```cmd
aws s3 ls s3://<YOUR_BUCKET>/raw/traffic/ --recursive
```

---

## 3. Glue / Athena

In Athena, confirm that the Session 1 raw table works:

```sql
SELECT COUNT(*)
FROM urban_raw.traffic;
```

Expected:

```text
1698
```

---

## 4. Curated Table

Confirm that the Session 1 curated table exists:

```sql
SELECT COUNT(*)
FROM urban_curated.traffic;
```

Expected:

```text
1698
```

Also verify:

```sql
SELECT year, month, COUNT(*) AS rows
FROM urban_curated.traffic
GROUP BY year, month
ORDER BY year, month;
```

Expected coverage:

```text
2025-06 through 2026-05
```

---

## 5. Athena Query Result Location

You need an S3 prefix for Athena query results.

Example:

```text
s3://<YOUR_BUCKET>/athena-results/
```

The Lambda functions `transform_batch` and `verify_batch` use this location through the environment variable:

```text
ATHENA_OUTPUT
```

---

## 6. Session 2 Data Files

Confirm:

```text
data/valid/traffic_2026_06.csv
data/invalid/traffic_2026_06_bad.csv
```

Expected:

- both files: 25 columns
- valid file: no missing `observation_date`
- invalid file: exactly one missing `observation_date`

---

## 7. Python

Check:

```cmd
python --version
```

Then test the local validator:

```cmd
python scripts\validate_batch.py data\valid\traffic_2026_06.csv --expected-month 2026-06
```

Expected:

```text
PASS
```

---

## 8. Important Schema Assumption

The Session 2 Lambda/Athena code expects the Session 1 curated table to contain:

- `observation_date`
- `sequence_no`
- `intersection_name`
- `road_name`
- `time_period_code`
- `time_period_th`
- traffic count fields
- `vehicle_count`
- `latitude`
- `longitude`
- `source_month`
- `source_file`
- `data_provenance`
- `year`
- `month`

If your Session 1 curated schema is different, update the Session 2 transform query before continuing.

---

## Ready?

You are ready when:

- [ ] AWS credentials work
- [ ] raw table works
- [ ] curated table works
- [ ] curated row count = 1,698
- [ ] Athena output location is available
- [ ] valid and invalid June files are present
- [ ] local validation script runs
