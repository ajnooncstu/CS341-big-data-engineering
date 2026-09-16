import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("batch_id")
parser.add_argument("--marker-root", default="processed")
args = parser.parse_args()

marker = Path(args.marker_root) / f"batch_id={args.batch_id}" / "_SUCCESS"

if marker.exists():
    print("ALREADY_PROCESSED")
    raise SystemExit(1)

print("NEW")
