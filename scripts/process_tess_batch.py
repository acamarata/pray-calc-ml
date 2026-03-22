"""
Process all downloaded TESS monthly CSV files using the existing tess_processor.

Run this after download_all_tess.py has fetched the raw files.
Writes one output CSV per month to data/raw/raw_sightings/tess_{month}.csv

Usage:
    python scripts/process_tess_batch.py [--month jan2019] [--all]
"""
from __future__ import annotations

import csv
import logging
import sys
import time
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.collect.tess_processor import process_tess_csv  # noqa: E402

log = logging.getLogger(__name__)

RAW_TESS_DIR = REPO_ROOT / "data" / "raw" / "tess"
SIGHTINGS_DIR = REPO_ROOT / "data" / "raw" / "raw_sightings"
FIELDNAMES = ["prayer", "date_local", "time_local", "utc_offset",
              "lat", "lng", "elevation_m", "source", "notes"]


def process_month(csv_path: Path, output_path: Path) -> int:
    """Process one TESS monthly CSV. Returns event count."""
    log.info("Processing: %s", csv_path.name)
    t0 = time.time()
    try:
        records = process_tess_csv(csv_path)
    except Exception as e:
        log.error("Error processing %s: %s", csv_path.name, e)
        return 0

    elapsed = time.time() - t0
    log.info("  -> %d events in %.1fs", len(records), elapsed)

    if records:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(records)
        log.info("  -> Written: %s", output_path.name)

    return len(records)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", nargs="+", default=None, help="Process specific month(s) (e.g. jan2019 feb2019)")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip months already in raw_sightings/")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )

    SIGHTINGS_DIR.mkdir(parents=True, exist_ok=True)

    if args.month:
        files = [RAW_TESS_DIR / f"tess_{m}.csv" for m in args.month]
    else:
        files = sorted(RAW_TESS_DIR.glob("tess_*.csv"))

    if not files:
        log.error("No TESS CSV files found in %s", RAW_TESS_DIR)
        sys.exit(1)

    log.info("Found %d TESS CSV files to process", len(files))

    total_events = 0
    results = []

    for csv_path in files:
        if not csv_path.exists():
            log.warning("File not found: %s", csv_path)
            continue

        month_label = csv_path.stem.replace("tess_", "")
        output_path = SIGHTINGS_DIR / f"tess_{month_label}.csv"

        if args.skip_existing and output_path.exists():
            existing = sum(1 for _ in open(output_path)) - 1
            log.info("SKIP (exists): %s (%d rows)", output_path.name, existing)
            total_events += existing
            results.append((month_label, existing, "skipped"))
            continue

        n = process_month(csv_path, output_path)
        total_events += n
        results.append((month_label, n, "processed"))

    # Print summary table
    print("\n" + "=" * 55)
    print(f"{'Month':<12} {'Events':>8}  {'Status'}")
    print("-" * 55)
    for month, n, status in results:
        print(f"{month:<12} {n:>8}  {status}")
    print("-" * 55)
    print(f"{'TOTAL':<12} {total_events:>8}")
    print("=" * 55)


if __name__ == "__main__":
    main()
