import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")


def lambda_handler(event, context):
    """
    Expected input:
    {
      "batch_id": "2026-06",
      "bucket": "YOUR-BUCKET",
      "key": "incoming/traffic/batch_id=2026-06/traffic_2026_06.csv"
    }
    """

    batch_id = event["batch_id"]
    bucket = event["bucket"]

    marker_key = f"processed/traffic/batch_id={batch_id}/_SUCCESS.json"

    try:
        s3.head_object(Bucket=bucket, Key=marker_key)
        status = "ALREADY_PROCESSED"

    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")

        if error_code in ("404", "NoSuchKey", "NotFound"):
            status = "NEW"
        else:
            raise

    return {
        **event,
        "status": status,
        "success_marker": marker_key
    }
