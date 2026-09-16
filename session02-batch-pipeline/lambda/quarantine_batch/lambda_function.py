import boto3
from pathlib import PurePosixPath

s3 = boto3.client("s3")


def lambda_handler(event, context):
    """
    Copies a failed input object from incoming/ to quarantine/.
    The original object is kept for traceability.
    """

    bucket = event["bucket"]
    source_key = event["key"]
    batch_id = event["batch_id"]

    filename = PurePosixPath(source_key).name

    quarantine_key = (
        f"quarantine/traffic/batch_id={batch_id}/{filename}"
    )

    s3.copy_object(
        Bucket=bucket,
        CopySource={
            "Bucket": bucket,
            "Key": source_key,
        },
        Key=quarantine_key,
    )

    return {
        **event,
        "quarantine_status": "COPIED",
        "quarantine_key": quarantine_key,
    }
