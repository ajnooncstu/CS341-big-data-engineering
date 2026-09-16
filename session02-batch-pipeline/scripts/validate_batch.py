import argparse
import csv
import json
from pathlib import Path

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

def validate_csv(path: Path, expected_month: str):
    errors = []

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        rows = list(reader)

    missing_columns = sorted(REQUIRED_COLUMNS - fields)
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    if not rows:
        errors.append("Dataset is empty")

    missing_required_values = 0
    negative_counts = 0
    wrong_month_rows = 0

    for row in rows:
        if any(not (row.get(col) or "").strip() for col in REQUIRED_VALUES):
            missing_required_values += 1

        value = (row.get("period_total_calc") or "").strip()
        if value:
            try:
                if float(value) < 0:
                    negative_counts += 1
            except ValueError:
                errors.append("Non-numeric period_total_calc found")
                break

        if (row.get("source_month") or "").strip() != expected_month:
            wrong_month_rows += 1

    if missing_required_values:
        errors.append(f"Rows with missing required values: {missing_required_values}")
    if negative_counts:
        errors.append(f"Rows with negative traffic counts: {negative_counts}")
    if wrong_month_rows:
        errors.append(f"Rows with unexpected source_month: {wrong_month_rows}")

    return {
        "file": str(path),
        "expected_month": expected_month,
        "row_count": len(rows),
        "missing_required_values": missing_required_values,
        "negative_counts": negative_counts,
        "wrong_month_rows": wrong_month_rows,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--expected-month", required=True)
    args = parser.parse_args()

    result = validate_csv(Path(args.csv_file), args.expected_month)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
