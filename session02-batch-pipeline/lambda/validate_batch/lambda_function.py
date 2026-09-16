import boto3
import csv
import io

s3 = boto3.client("s3")

REQUIRED_COLUMNS = {
    "source_month",
    "observation_date",
    "intersection_name",
    "road_name",
    "time_period_code",
    "period_total_calc",
    "source_file",
    "data_provenance",
}

REQUIRED_VALUES = {
    "observation_date",
    "intersection_name",
    "road_name",
    "time_period_code",
    "period_total_calc",
}


def expected_month_from_batch_id(batch_id: str) -> str:
    """
    Teaching convention:
      2026-06      -> 2026-06
      2026-06-bad  -> 2026-06
    """
    return batch_id[:7]


def lambda_handler(event, context):
    """
    Reads one CSV object from S3 and returns PASS/FAIL plus evidence.
    """

    bucket = event["bucket"]
    key = event["key"]
    batch_id = event["batch_id"]
    expected_month = expected_month_from_batch_id(batch_id)

    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(body))
    fieldnames = reader.fieldnames or []
    rows = list(reader)

    errors = []

    missing_columns = sorted(REQUIRED_COLUMNS - set(fieldnames))
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    if not rows:
        errors.append("Dataset is empty")

    missing_required_values = 0
    negative_counts = 0
    wrong_month_rows = 0
    non_numeric_counts = 0

    for row in rows:
        if any(not (row.get(col) or "").strip() for col in REQUIRED_VALUES):
            missing_required_values += 1

        count_value = (row.get("period_total_calc") or "").strip()

        if count_value:
            try:
                if float(count_value) < 0:
                    negative_counts += 1
            except ValueError:
                non_numeric_counts += 1

        source_month = (row.get("source_month") or "").strip()
        if source_month != expected_month:
            wrong_month_rows += 1

    if missing_required_values:
        errors.append(
            f"Rows with missing required values: {missing_required_values}"
        )

    if negative_counts:
        errors.append(
            f"Rows with negative traffic counts: {negative_counts}"
        )

    if non_numeric_counts:
        errors.append(
            f"Rows with non-numeric traffic counts: {non_numeric_counts}"
        )

    if wrong_month_rows:
        errors.append(
            f"Rows with unexpected source_month: {wrong_month_rows}"
        )

    validation_status = "PASS" if not errors else "FAIL"

    return {
        **event,
        "validation_status": validation_status,
        "expected_month": expected_month,
        "row_count": len(rows),
        "missing_required_values": missing_required_values,
        "negative_counts": negative_counts,
        "non_numeric_counts": non_numeric_counts,
        "wrong_month_rows": wrong_month_rows,
        "validation_errors": errors,
    }
