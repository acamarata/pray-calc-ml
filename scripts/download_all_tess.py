"""
Download all available TESS/Stars4All monthly archives from Zenodo,
then process each with the existing tess_processor.py.

Records discovered via Zenodo API (communities/stars4all):
  - Sep 2016 through Aug 2020, with one gap (Aug 2018 not published)
  - Total: ~47 months of data

Usage:
    python scripts/download_all_tess.py [--skip-existing] [--process-only]
"""
from __future__ import annotations

import argparse
import csv
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Complete manifest of all TESS Zenodo records
# Columns: zenodo_id, month_label, filename, size_mb (approx)
# ---------------------------------------------------------------------------
TESS_RECORDS = [
    # 2016 — smaller network, fewer stations, lower data volume
    # (Sep 2016 is JSON format, not CSV — skipping)
    # ("163341", "sep2016", "tess-september-2016.json", 12),  # JSON, skip
    ("321291", "oct2016", "tess-october-2016.csv", 28),
    ("321292", "nov2016", "tess-november-2016.csv", 5),
    ("321305", "dec2016", "tess-december-2016.csv", 20),
    # 2017
    ("321318", "jan2017", "tess-january-2017.csv", 13),
    ("375804", "feb2017", "tess-february-2017.csv", 23),
    ("470930", "mar2017", "tess-march-2017.csv", 33),
    ("572613", "apr2017", "tess-april-2017.csv", 34),
    ("824124", "may2017", "tess-may-2017.csv", 30),
    ("824128", "jun2017", "tess-june-2017.csv", 46),
    ("996285", "jul2017", "tess-july-2017.csv", 46),
    # Aug 2017 not found on Zenodo
    ("1000545", "sep2017", "tess-sept-2017.csv", 64),
    ("1042903", "oct2017", "tess-oct-2017.csv", 88),
    ("1072485", "nov2017", "tess-nov-2017.csv", 96),
    ("1134692", "dec2017", "tess-dec-2017.csv", 97),
    # 2018
    ("1164632", "jan2018", "tess-january-2018.csv", 73),
    ("1215915", "feb2018", "tess-february-2018.csv", 89),
    ("1215546", "mar2018", "tess-march-2018.csv", 87),
    ("1240139", "apr2018", "tess-april-2018.csv", 88),
    ("1257445", "may2018", "tess-may-2018.csv", 94),
    ("1306765", "jun2018", "tess-june-2018.csv", 87),
    ("1332003", "jul2018", "tess-july-2018.csv", 92),
    # Aug 2018 — not published on Zenodo, skip
    ("1442525", "sep2018", "tess-september-2018.csv", 113),
    ("1479009", "oct2018", "tess-october-2018.csv", 133),
    ("1883080", "nov2018", "tess-november-2018.csv", 134),
    ("2536130", "dec2018", "tess-december-2018.csv", 151),
    # 2019
    ("2561327", "jan2019", "tess-january-2019.csv", 168),
    ("2620256", "feb2019", "tess-february-2019.csv", 152),
    ("2620261", "mar2019", "tess-march-2019.csv", 162),
    ("3377710", "apr2019", "tess-april-2019.csv", 159),
    ("3378310", "may2019", "tess-may-2019.csv", 141),
    # Jun 2019 already downloaded — still include for processing
    ("3378728", "jun2019", "tess-june-2019.csv", 147),
    ("3564263", "jul2019", "tess-july-2019.csv", 147),
    ("3564257", "aug2019", "tess-august-2019.csv", 155),
    ("3564221", "sep2019", "tess-september-2019.csv", 142),
    ("3564196", "oct2019", "tess-october-2019.csv", 144),
    ("3563539", "nov2019", "tess-november-2019.csv", 135),
    ("3758045", "dec2019", "tess-december-2019.csv", 144),
    # 2020
    ("4264883", "jan2020", "stars4all-january-2020.csv", 359),
    ("4264914", "feb2020", "stars4all-february-2020.csv", 358),
    ("4264946", "mar2020", "stars4all-march-2020.csv", 368),
    ("4264991", "apr2020", "stars4all-april-2020.csv", 338),
    ("4265020", "may2020", "stars4all-may-2020.csv", 318),
    ("4265108", "jun2020", "stars4all-june-2020.csv", 323),
    ("4265155", "jul2020", "stars4all-july-2020.csv", 323),
    ("4265171", "aug2020", "stars4all-august-2020.csv", 324),
]

REPO_ROOT = Path(__file__).parent.parent
RAW_TESS_DIR = REPO_ROOT / "data" / "raw" / "tess"
SIGHTINGS_DIR = REPO_ROOT / "data" / "raw" / "raw_sightings"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"


def zenodo_download_url(record_id: str, filename: str) -> str:
    return f"https://zenodo.org/records/{record_id}/files/{filename}?download=1"


def download_file(url: str, dest: Path, size_mb: int) -> bool:
    """Download url to dest using curl. Returns True on success."""
    log.info("Downloading %s -> %s (~%d MB)", url, dest.name, size_mb)
    tmp = dest.with_suffix(".tmp")
    cmd = [
        "curl", "-L", "--retry", "3", "--retry-delay", "5",
        "--connect-timeout", "30", "--max-time", "3600",
        "-o", str(tmp), url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log.error("Download failed: %s", result.stderr[:500])
        tmp.unlink(missing_ok=True)
        return False
    # Sanity check: file must be at least 1 MB
    if tmp.stat().st_size < 1_000_000:
        log.error("Downloaded file too small (%d bytes), likely an error page", tmp.stat().st_size)
        tmp.unlink(missing_ok=True)
        return False
    tmp.rename(dest)
    log.info("Downloaded %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)
    return True


def process_month(csv_path: Path, output_path: Path) -> int:
    """
    Run the TESS processor on csv_path, write results to output_path.
    Returns number of twilight events extracted.
    """
    script = f"""
import sys, csv
sys.path.insert(0, '{REPO_ROOT}')
from src.collect.tess_processor import process_tess_csv
from pathlib import Path

csv_path = Path('{csv_path}')
records = process_tess_csv(csv_path)
print(f'RECORDS_COUNT: {{len(records)}}', flush=True)

if records:
    output_path = Path('{output_path}')
    fieldnames = ['prayer', 'date_local', 'time_local', 'utc_offset',
                  'lat', 'lng', 'elevation_m', 'source', 'notes']
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f'Written to {{output_path}}', flush=True)
"""
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", script],
        capture_output=True, text=True, timeout=7200,
        cwd=str(REPO_ROOT),
    )
    # Extract record count from output
    count = 0
    for line in result.stdout.splitlines():
        if line.startswith("RECORDS_COUNT:"):
            count = int(line.split(":")[1].strip())
    if result.returncode != 0:
        log.error("Processor error for %s: %s", csv_path.name, result.stderr[-1000:])
        return 0
    log.info("Processed %s: %d twilight events", csv_path.name, count)
    return count


def main():
    parser = argparse.ArgumentParser(description="Download and process all TESS monthly archives")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip download if raw CSV already exists")
    parser.add_argument("--process-only", action="store_true",
                        help="Skip downloads, only process existing CSVs")
    parser.add_argument("--download-only", action="store_true",
                        help="Only download, do not process")
    parser.add_argument("--months", nargs="+", default=None,
                        help="Only process these month labels (e.g. jan2019 feb2019)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )

    RAW_TESS_DIR.mkdir(parents=True, exist_ok=True)
    SIGHTINGS_DIR.mkdir(parents=True, exist_ok=True)

    records_to_process = TESS_RECORDS
    if args.months:
        records_to_process = [r for r in TESS_RECORDS if r[1] in args.months]
        log.info("Filtered to %d months: %s", len(records_to_process), args.months)

    total_downloaded = 0
    total_processed = 0
    total_events = 0
    results = []

    for zenodo_id, month_label, filename, size_mb in records_to_process:
        raw_path = RAW_TESS_DIR / f"tess_{month_label}.csv"
        output_path = SIGHTINGS_DIR / f"tess_{month_label}.csv"

        log.info("=== %s (Zenodo %s) ===", month_label, zenodo_id)

        # --- Download ---
        if not args.process_only:
            if raw_path.exists() and args.skip_existing:
                log.info("Skipping download (exists): %s", raw_path.name)
            elif raw_path.exists() and raw_path.stat().st_size > 1_000_000:
                log.info("File already present: %s (%.1f MB)", raw_path.name,
                         raw_path.stat().st_size / 1e6)
            else:
                url = zenodo_download_url(zenodo_id, filename)
                ok = download_file(url, raw_path, size_mb)
                if not ok:
                    log.error("FAILED to download %s, skipping processing", month_label)
                    results.append((month_label, "download_failed", 0))
                    continue
                total_downloaded += 1

        # --- Process ---
        if not args.download_only:
            if not raw_path.exists():
                log.warning("Raw file missing, cannot process: %s", raw_path)
                results.append((month_label, "no_file", 0))
                continue

            n_events = process_month(raw_path, output_path)
            total_processed += 1
            total_events += n_events
            results.append((month_label, "ok", n_events))
        else:
            results.append((month_label, "download_only", 0))

    # Summary
    print("\n" + "=" * 70)
    print(f"SUMMARY: {total_downloaded} downloaded, {total_processed} processed, "
          f"{total_events} total twilight events")
    print("=" * 70)
    print(f"{'Month':<12} {'Status':<18} {'Events':>8}")
    print("-" * 40)
    for month, status, count in results:
        print(f"{month:<12} {status:<18} {count:>8}")
    print("-" * 40)
    print(f"{'TOTAL':<12} {'':<18} {total_events:>8}")


if __name__ == "__main__":
    main()
