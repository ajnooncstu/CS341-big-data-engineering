import boto3
import json
import os
import time
from datetime import datetime, timezone

athena = boto3.client("athena")
s3 = boto3.client("s3")

ATHENA_OUTPUT = os.environ["ATHENA_OUTPUT"]
CURATED_DATABASE = os.environ.get("CURATED_DATABASE", "urban_curated")
CURATED_TABLE = os.environ.get("CURATED_TABLE", "traffic")


def run_query(sql: str):
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": CURATED_DATABASE},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )

    query_id = response["QueryExecutionId"]

    while True:
        execution = athena.get_query_execution(
            QueryExecutionId=query_id
        )["QueryExecution"]

        status = execution["Status"]
        state = status["State"]

        if state == "SUCCEEDED":
            return query_id

        if state in ("FAILED", "CANCELLED"):
            reason = status.get("StateChangeReason", "Unknown Athena error")
            raise RuntimeError(
                f"Athena query {state}: {reason}"
            )

        time.sleep(1)


def first_data_row(query_id: str):
    response = athena.get_query_results(QueryExecutionId=query_id)
    rows = response["ResultSet"]["Rows"]

    # Row 0 is the header.
    if len(rows) < 2:
        return []

    return [
        cell.get("VarCharValue")
        for cell in rows[1]["Data"]
    ]


def lambda_handler(event, context):
    bucket = event["bucket"]
    batch_id = event["batch_id"]
    expected_month = event["expected_month"]
    expected_rows = int(event["row_count"])

    sql = f"""
    SELECT
      COUNT(*) AS curated_rows,
      COUNT_IF(observation_date IS NULL) AS missing_date,
      COUNT_IF(intersection_name IS NULL) AS missing_intersection,
      COUNT_IF(vehicle_count IS NULL) AS missing_vehicle_count
    FROM {CURATED_DATABASE}.{CURATED_TABLE}
    WHERE source_month = '{expected_month}'
    """

    query_id = run_query(sql)
    values = first_data_row(query_id)

    if len(values) != 4:
        raise RuntimeError(
            f"Unexpected Athena verification result: {values}"
        )

    curated_rows = int(values[0])
    missing_date = int(values[1])
    missing_intersection = int(values[2])
    missing_vehicle_count = int(values[3])

    errors = []

    if curated_rows != expected_rows:
        errors.append(
            f"Expected {expected_rows} rows for {expected_month}, "
            f"found {curated_rows}"
        )

    if missing_date != 0:
        errors.append(f"Missing observation_date: {missing_date}")

    if missing_intersection != 0:
        errors.append(
            f"Missing intersection_name: {missing_intersection}"
        )

    if missing_vehicle_count != 0:
        errors.append(
            f"Missing vehicle_count: {missing_vehicle_count}"
        )

    if errors:
        raise RuntimeError(
            "Verification failed: " + "; ".join(errors)
        )

    marker_key = (
        f"processed/traffic/batch_id={batch_id}/_SUCCESS.json"
    )

    marker_body = {
        "batch_id": batch_id,
        "source_month": expected_month,
        "row_count": curated_rows,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "athena_query_id": query_id,
    }

    s3.put_object(
        Bucket=bucket,
        Key=marker_key,
        Body=json.dumps(marker_body, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    return {
        **event,
        "verify_status": "PASS",
        "curated_rows": curated_rows,
        "missing_date": missing_date,
        "missing_intersection": missing_intersection,
        "missing_vehicle_count": missing_vehicle_count,
        "success_marker": marker_key,
        "athena_verify_query_id": query_id,
    }
