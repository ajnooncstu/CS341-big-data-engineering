import boto3
import os
import re
import time

athena = boto3.client("athena")

ATHENA_OUTPUT = os.environ["ATHENA_OUTPUT"]
RAW_DATABASE = os.environ.get("RAW_DATABASE", "urban_raw")
CURATED_DATABASE = os.environ.get("CURATED_DATABASE", "urban_curated")
CURATED_TABLE = os.environ.get("CURATED_TABLE", "traffic")


def run_query(sql: str, database: str):
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )

    query_id = response["QueryExecutionId"]

    while True:
        status = athena.get_query_execution(
            QueryExecutionId=query_id
        )["QueryExecution"]["Status"]

        state = status["State"]

        if state == "SUCCEEDED":
            return query_id

        if state in ("FAILED", "CANCELLED"):
            reason = status.get("StateChangeReason", "Unknown Athena error")
            raise RuntimeError(
                f"Athena query {state}: {reason}"
            )

        time.sleep(1)


def safe_table_suffix(batch_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", batch_id)


def lambda_handler(event, context):
    """
    Creates a temporary external table over the incoming CSV and inserts
    the accepted batch into the existing curated Parquet table.
    """

    bucket = event["bucket"]
    key = event["key"]
    batch_id = event["batch_id"]
    expected_month = event["expected_month"]

    # The external table LOCATION must be a prefix, not the individual file.
    prefix = key.rsplit("/", 1)[0] + "/"
    location = f"s3://{bucket}/{prefix}"

    temp_table = f"traffic_incoming_{safe_table_suffix(batch_id)}"

    drop_sql = f"DROP TABLE IF EXISTS {RAW_DATABASE}.{temp_table}"

    create_sql = f"""
    CREATE EXTERNAL TABLE {RAW_DATABASE}.{temp_table} (
      source_month string,
      observation_date string,
      sequence_no string,
      intersection_name string,
      road_name string,
      time_period_code string,
      time_period_th string,
      passenger_car string,
      van_pickup string,
      large_bus string,
      small_bus string,
      truck string,
      tuk_tuk string,
      period_total_source string,
      period_total_calc string,
      road_total_source string,
      road_total_calc string,
      intersection_total_source string,
      intersection_total_calc string,
      latitude string,
      longitude string,
      source_file string,
      source_sheet string,
      source_row string,
      data_provenance string
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
    WITH SERDEPROPERTIES (
      'separatorChar' = ',',
      'quoteChar' = '"',
      'escapeChar' = '\\\\'
    )
    STORED AS TEXTFILE
    LOCATION '{location}'
    TBLPROPERTIES ('skip.header.line.count'='1')
    """

    year_value, month_value = expected_month.split("-")

    insert_sql = f"""
    INSERT INTO {CURATED_DATABASE}.{CURATED_TABLE}
    SELECT
      CAST(observation_date AS DATE) AS observation_date,
      CAST(sequence_no AS INTEGER) AS sequence_no,
      intersection_name,
      road_name,
      time_period_code,
      time_period_th,
      CAST(passenger_car AS BIGINT) AS passenger_car,
      CAST(van_pickup AS BIGINT) AS van_pickup,
      CAST(large_bus AS BIGINT) AS large_bus,
      CAST(small_bus AS BIGINT) AS small_bus,
      CAST(truck AS BIGINT) AS truck,
      CAST(tuk_tuk AS BIGINT) AS tuk_tuk,
      CAST(period_total_calc AS BIGINT) AS vehicle_count,
      TRY_CAST(NULLIF(latitude, '') AS DOUBLE) AS latitude,
      TRY_CAST(NULLIF(longitude, '') AS DOUBLE) AS longitude,
      source_month,
      source_file,
      data_provenance,
      CAST('{year_value}' AS INTEGER) AS year,
      '{month_value}' AS month
    FROM {RAW_DATABASE}.{temp_table}
    WHERE observation_date IS NOT NULL
      AND TRIM(observation_date) <> ''
      AND intersection_name IS NOT NULL
      AND TRIM(intersection_name) <> ''
      AND period_total_calc IS NOT NULL
      AND TRIM(period_total_calc) <> ''
    """

    # Make rerunning this Lambda safer during debugging by ensuring the
    # temporary table is recreated from the current incoming prefix.
    run_query(drop_sql, RAW_DATABASE)
    run_query(create_sql, RAW_DATABASE)
    insert_query_id = run_query(insert_sql, CURATED_DATABASE)

    return {
        **event,
        "transform_status": "SUCCEEDED",
        "temporary_table": f"{RAW_DATABASE}.{temp_table}",
        "athena_insert_query_id": insert_query_id,
    }
