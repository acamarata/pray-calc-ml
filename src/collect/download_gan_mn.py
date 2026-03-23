"""
Download all GaN-MN monthly and annual CSV files, then process each one
with the GaN-MN processor and save results to data/raw/raw_sightings/.

Run from repo root:
    /Volumes/X9/Sites/acamarata/pray-calc-ml/.venv/bin/python \
        src/collect/download_gan_mn.py
"""
from __future__ import annotations

import csv
import logging
import sys
import time
from pathlib import Path

import requests

# Add repo root to path so we can import the processor
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.collect.gan_mn_processor import process_gan_mn_csv  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

RAW_DIR = REPO_ROOT / "data" / "raw" / "gan_mn"
SIGHTINGS_DIR = REPO_ROOT / "data" / "raw" / "raw_sightings"
RAW_DIR.mkdir(parents=True, exist_ok=True)
SIGHTINGS_DIR.mkdir(parents=True, exist_ok=True)

# All monthly files, 2022-2025 (skip already-downloaded ones)
# Format: (label, bit.ly URL, local filename)
MONTHLY_FILES = [
    # 2025 (skip Jun 2025 and Jan 2025 — already have them)
    ("Aug_2025",  "https://bit.ly/4a9aXIP",  "GaN-MN_August_2025.csv"),
    ("Sep_2025",  "https://bit.ly/4sm4pxY",  "GaN-MN_September_2025.csv"),
    ("Jul_2025",  "https://bit.ly/4jlEQtz",  "GaN-MN_July_2025.csv"),
    ("May_2025",  "https://bit.ly/47w5sCA",  "GaN-MN_May_2025.csv"),
    ("Apr_2025",  "https://bit.ly/4nxs6Bm",  "GaN-MN_April_2025.csv"),
    ("Mar_2025",  "https://bit.ly/47mPHzx",  "GaN-MN_March_2025.csv"),
    ("Feb_2025",  "https://bit.ly/4lbwPXg",  "GaN-MN_February_2025.csv"),
    # 2024 (skip Aug 2024 — already have it)
    ("Dec_2024",  "https://bit.ly/4mHSBno",  "GaN-MN_December_2024.csv"),
    ("Nov_2024",  "https://bit.ly/4lVwidL",  "GaN-MN_November_2024.csv"),
    ("Oct_2024",  "https://bit.ly/449h3ay",  "GaN-MN_October_2024.csv"),
    ("Sep_2024",  "https://bit.ly/4hUE458",  "GaN-MN_September_2024.csv"),
    ("Jul_2024",  "https://bit.ly/4fAjvJi",  "GaN-MN_July_2024.csv"),
    ("Jun_2024",  "https://bit.ly/3ZvT1DR",  "GaN-MN_June_2024.csv"),
    ("May_2024",  "https://bit.ly/4f3veR8",  "GaN-MN_May_2024.csv"),
    ("Apr_2024",  "https://bit.ly/4etfYg0",  "GaN-MN_April_2024.csv"),
    ("Mar_2024",  "https://bit.ly/3Z69pLy",  "GaN-MN_March_2024.csv"),
    ("Feb_2024",  "https://bit.ly/46wtyfJ",  "GaN-MN_February_2024.csv"),
    ("Jan_2024",  "https://bit.ly/4cMztz7",  "GaN-MN_January_2024.csv"),
    # 2023
    ("Dec_2023",  "https://bit.ly/45dEDl3",  "GaN-MN_December_2023.csv"),
    ("Nov_2023",  "https://bit.ly/4ajnV4v",  "GaN-MN_November_2023.csv"),
    ("Oct_2023",  "https://bit.ly/3PKzryD",  "GaN-MN_October_2023.csv"),
    ("Sep_2023",  "https://bit.ly/3ww3T8K",  "GaN-MN_September_2023.csv"),
    ("Aug_2023",  "https://bit.ly/3So1UKV",  "GaN-MN_August_2023.csv"),
    ("Jul_2023",  "https://bit.ly/3S3mG3u",  "GaN-MN_July_2023.csv"),
    ("Jun_2023",  "https://bit.ly/46Es4OL",  "GaN-MN_June_2023.csv"),
    ("May_2023",  "https://bit.ly/46WbF9m",  "GaN-MN_May_2023.csv"),
    ("Apr_2023",  "https://bit.ly/3rxWWSy",  "GaN-MN_April_2023.csv"),
    ("Mar_2023",  "https://bit.ly/3OW45nv",  "GaN-MN_March_2023.csv"),
    ("Feb_2023",  "https://bit.ly/3rSY2br",  "GaN-MN_February_2023.csv"),
    ("Jan_2023",  "https://bit.ly/3JGJpy1",  "GaN-MN_January_2023.csv"),
    # 2022
    ("Dec_2022",  "https://bit.ly/43CelXB",  "GaN-MN_December_2022.csv"),
    ("Nov_2022",  "https://bit.ly/429RdyR",  "GaN-MN_November_2022.csv"),
    ("Oct_2022",  "https://bit.ly/3m1onBm",  "GaN-MN_October_2022.csv"),
    ("Sep_2022",  "http://bit.ly/3SHQJN5",   "GaN-MN_September_2022.csv"),
    ("Aug_2022",  "http://bit.ly/40hFpdP",   "GaN-MN_August_2022.csv"),
    ("Jul_2022",  "https://bit.ly/3Z487OD",  "GaN-MN_July_2022.csv"),
    ("Jun_2022",  "https://bit.ly/3H5CsWS",  "GaN-MN_June_2022.csv"),
    ("May_2022",  "https://bit.ly/3fnFCJT",  "GaN-MN_May_2022.csv"),
    ("Apr_2022",  "https://bit.ly/3E8flJr",  "GaN-MN_April_2022.csv"),
    ("Mar_2022",  "https://bit.ly/3B76VAq",  "GaN-MN_March_2022.csv"),
    ("Feb_2022",  "http://bit.ly/3BCkXe1",   "GaN-MN_February_2022.csv"),
    ("Jan_2022",  "http://bit.ly/3IgfkU4",   "GaN-MN_January_2022.csv"),
]

# Annual file for 2021 (one representative year)
ANNUAL_FILES = [
    ("2021", "https://bit.ly/44vtt9T", "GaN-MN_Annual_2021.csv"),
]

FIELDNAMES = [
    "prayer", "date_local", "time_local", "utc_offset",
    "lat", "lng", "elevation_m", "source", "notes",
]


def resolve_and_download(label: str, url: str, dest: Path) -> bool:
    """
    Follow bit.ly redirect and download the file to dest.
    Returns True on success.
    """
    if dest.exists():
        log.info("Already have %s — skipping download", dest.name)
        return True

    log.info("Downloading %s from %s ...", label, url)
    try:
        # bit.ly does a redirect; requests follows by default
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
        with requests.get(url, headers=headers, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            with open(dest, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=1 << 20):  # 1 MB chunks
                    if chunk:
                        fh.write(chunk)
                        downloaded += len(chunk)
            mb = downloaded / (1 << 20)
            log.info("Downloaded %s: %.1f MB", dest.name, mb)
            return True
    except Exception as exc:
        log.error("Failed to download %s: %s", label, exc)
        if dest.exists():
            dest.unlink()
        return False


def process_and_save(label: str, csv_path: Path) -> int:
    """
    Run the GaN-MN processor on csv_path and write results to
    data/raw/raw_sightings/gan_mn_{label_lower}.csv.
    Returns count of records written.
    """
    slug = label.lower().replace(" ", "_")
    out_path = SIGHTINGS_DIR / f"gan_mn_{slug}.csv"

    if out_path.exists():
        # Count existing rows
        with open(out_path) as fh:
            existing = sum(1 for _ in fh) - 1  # subtract header
        log.info("Already processed %s (%d rows) — skipping", out_path.name, existing)
        return existing

    log.info("Processing %s ...", csv_path.name)
    try:
        records = process_gan_mn_csv(csv_path)
    except Exception as exc:
        log.error("Processing failed for %s: %s", csv_path.name, exc)
        return 0

    if not records:
        log.warning("No records extracted from %s", csv_path.name)
        return 0

    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)

    log.info("Wrote %d records to %s", len(records), out_path.name)
    return len(records)


def main() -> None:
    all_files = MONTHLY_FILES + ANNUAL_FILES
    total_downloaded = 0
    total_records = 0
    skipped_download = 0
    failed_download = []
    results = []

    for label, url, filename in all_files:
        dest = RAW_DIR / filename
        ok = resolve_and_download(label, url, dest)
        if not ok:
            failed_download.append(label)
            continue
        if dest.stat().st_size < 1000:
            log.error("%s appears too small (%d bytes), skipping processing", filename, dest.stat().st_size)
            failed_download.append(label)
            continue

        total_downloaded += 1
        count = process_and_save(label, dest)
        total_records += count
        results.append((label, count))

        # Brief pause between files to avoid hammering the network
        time.sleep(0.5)

    # Also count already-existing sightings from the 3 pre-downloaded months
    pre_existing = ["august_2024", "january_2025", "june_2025"]
    pre_total = 0
    for slug in pre_existing:
        p = SIGHTINGS_DIR / f"gan_mn_{slug}.csv"
        if p.exists():
            with open(p) as fh:
                n = sum(1 for _ in fh) - 1
            pre_total += n
            log.info("Pre-existing %s: %d rows", p.name, n)

    log.info("=" * 60)
    log.info("Download summary:")
    log.info("  Files newly processed: %d", total_downloaded)
    log.info("  Records from new files: %d", total_records)
    log.info("  Records from pre-existing 3 months: %d", pre_total)
    log.info("  Grand total twilight events: %d", total_records + pre_total)
    if failed_download:
        log.warning("  Failed downloads: %s", ", ".join(failed_download))

    log.info("Per-file breakdown:")
    for label, count in results:
        log.info("  %-15s %d", label, count)


if __name__ == "__main__":
    main()
