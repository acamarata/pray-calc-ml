"""
Download all GaN-MN monthly CSV files from Google Drive using direct export URLs,
then process each with the GaN-MN processor and write to data/raw/raw_sightings/.

Google Drive large-file download pattern:
  1. GET https://drive.google.com/uc?export=download&id=FILE_ID
     -> For large files, returns an HTML page with a confirmation token
  2. Parse the confirm token from the HTML
  3. GET https://drive.google.com/uc?export=download&confirm=TOKEN&id=FILE_ID
     -> Returns the actual file

Run from repo root:
    /Volumes/X9/Sites/acamarata/pray-calc-ml/.venv/bin/python \
        src/collect/download_gan_mn_gdrive.py
"""
from __future__ import annotations

import csv
import logging
import re
import sys
import time
from pathlib import Path

import requests

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

FIELDNAMES = [
    "prayer", "date_local", "time_local", "utc_offset",
    "lat", "lng", "elevation_m", "source", "notes",
]

# All monthly files with Google Drive file IDs (resolved from bit.ly links)
# Skipping Aug 2024, Jan 2025, Jun 2025 — already downloaded.
MONTHLY_FILES = [
    # 2025
    ("Sep_2025", "1LwqUwB21fHomX9gna5jd6LqRU3ylaXLk", "GaN-MN_September_2025.csv"),
    ("Aug_2025", "1Ix0-b_RqA5zJS5IXc66RLKjZe_PTOuOu", "GaN-MN_August_2025.csv"),
    ("Jul_2025", "1mG5vo8fulVh4UmNeaR4JENyy6nVKQNG9", "GaN-MN_July_2025.csv"),
    ("May_2025", "1NeUyLZjJuZqQGLKi38f-SxlnXLBcEYmQ", "GaN-MN_May_2025.csv"),
    ("Apr_2025", "1PvexXu17lI4sZsasz7OKPKIfXRJp5s6n", "GaN-MN_April_2025.csv"),
    ("Mar_2025", "1huje0wiSUBjzLugzbiAZIsRo7WR0OJc9", "GaN-MN_March_2025.csv"),
    ("Feb_2025", "1-OJznQAO0uXwzue85LRE41gP66TgodhZ", "GaN-MN_February_2025.csv"),
    # 2024
    ("Dec_2024", "1XY7tLEArcJ7K2zN5R8HfzfEGVDr6RwFA", "GaN-MN_December_2024.csv"),
    ("Nov_2024", "1gTi79Ea-5r94rJ9d2VOurKMVQX-N553k", "GaN-MN_November_2024.csv"),
    ("Oct_2024", "1yAMGSql_A8XurFzCHXUGoOcdg40vC7Iv", "GaN-MN_October_2024.csv"),
    ("Sep_2024", "1_yQe3v-sYpMKEjaYC4KVdqNLwzhOLHA8", "GaN-MN_September_2024.csv"),
    ("Jul_2024", "1LIvDTLYou6t58zaVC-MCRvA-wMEaC0Qn", "GaN-MN_July_2024.csv"),
    ("Jun_2024", "1y7UsA9TX3xJQ5hqIPjRiSSZBnwucQ-wo", "GaN-MN_June_2024.csv"),
    ("May_2024", "1DUJqDULsvCl9onAes6JtEg1wPUrQJhE0", "GaN-MN_May_2024.csv"),
    ("Apr_2024", "1v1_wEjbYMDi9khPqX7o4X4j5oZNL7xu-", "GaN-MN_April_2024.csv"),
    ("Mar_2024", "1flYpgRM1ZLEgN3QqSnEt1SUzBiDC9xXD", "GaN-MN_March_2024.csv"),
    ("Feb_2024", "1XjJ_8Rw7OVSLAmkkGQ91v_ykc4tHF-ea", "GaN-MN_February_2024.csv"),
    ("Jan_2024", "1H9bVf5wnvf3biosyqlXg9VERFhjya2Ii", "GaN-MN_January_2024.csv"),
    # 2023
    ("Dec_2023", "1ZhsdYeWgyPYcZUBHnUNGY0qZLy1B14Yz", "GaN-MN_December_2023.csv"),
    ("Nov_2023", "1qFvWJI1yjzTrbJmUO0vUWh9FCmVV7XSW", "GaN-MN_November_2023.csv"),
    ("Oct_2023", "1zErPqT2SHJ2vbrfk-n5JtZF-nPwVgKah", "GaN-MN_October_2023.csv"),
    ("Sep_2023", "1U6UPWj8i06kPIX_vrcYqdeqhGY3QfeOw", "GaN-MN_September_2023.csv"),
    ("Aug_2023", "1Czbu6U_4dSLc0LcJ-kppfiFGvLtk9stO", "GaN-MN_August_2023.csv"),
    ("Jul_2023", "145TbQIsXg2wRy3OJAjKp86wNN78v4vcN", "GaN-MN_July_2023.csv"),
    ("Jun_2023", "1yXlU75dIJ4KayIhB5VNaH4377VXhEu6O", "GaN-MN_June_2023.csv"),
    ("May_2023", "1Q_oZNmhIwyThXuMhpu39L6RD6bDz0DI7", "GaN-MN_May_2023.csv"),
    ("Apr_2023", "1F806N1DEJQw0teUyy38AmhQ7p8HVlspa", "GaN-MN_April_2023.csv"),
    ("Mar_2023", "1rYkFnB0OCl8T3Z9acruYBwSfQg79AfE6", "GaN-MN_March_2023.csv"),
    ("Feb_2023", "1uHjlXzUS9A1NBo3YN4cCEiRYgJhq0cfv", "GaN-MN_February_2023.csv"),
    ("Jan_2023", "1Ljcw0lopcTfQFN77W8VS2JmbSv6LHNoX", "GaN-MN_January_2023.csv"),
    # 2022
    ("Dec_2022", "16IvutO_Il3cHNRh0wUECNrUzY9VrQI5l", "GaN-MN_December_2022.csv"),
    ("Nov_2022", "1SoQaZbVL0eDz9gTYXaBJFi8wVd43lg_5", "GaN-MN_November_2022.csv"),
    ("Oct_2022", "1qlFASJP9dZcG_dApL2sRinIlM_AH_zBV", "GaN-MN_October_2022.csv"),
    ("Sep_2022", "1VepIBNf8nNuFuO8QSvEs3oCENDIviC6H", "GaN-MN_September_2022.csv"),
    ("Aug_2022", "1t5d_BE2gnrh_usEXnx9n1nrR7Jn1uZHc", "GaN-MN_August_2022.csv"),
    ("Jul_2022", "1bL1LW_FCnUqHWLGtN9savbQRHwLNX0z9", "GaN-MN_July_2022.csv"),
    ("Jun_2022", "1PN3rrCQ7z8f48tSm6QWEsfnd6tmcyBBo", "GaN-MN_June_2022.csv"),
    ("May_2022", "1Q9sRof7xHyz1inrtrrt5L_o8-rXcf979", "GaN-MN_May_2022.csv"),
    ("Apr_2022", "1nNt9mtBXg0UtrYoKe4S_BsALlaDFfJbW", "GaN-MN_April_2022.csv"),
    ("Mar_2022", "1H3yfzvUEXXukpJJWnw22HpTcWUnUMvSV", "GaN-MN_March_2022.csv"),
    ("Feb_2022", "1_KP17mnwUtSRxoQiwTvfKVX4bVsUCNN2", "GaN-MN_February_2022.csv"),
    ("Jan_2022", "1lpX51gPRiqna4NHzhkKWdFipKFJ-_0J2", "GaN-MN_January_2022.csv"),
]

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
})


def gdrive_download(file_id: str, dest: Path) -> bool:
    """
    Download a Google Drive file to dest, handling the virus-scan confirmation
    page that Google shows for large files.

    Returns True on success.
    """
    if dest.exists() and dest.stat().st_size > 10_000_000:
        log.info("Already have %s (%.0f MB) — skipping", dest.name, dest.stat().st_size / 1e6)
        return True

    base_url = "https://drive.google.com/uc"
    params = {"export": "download", "id": file_id}

    log.info("Fetching %s (id=%s) ...", dest.name, file_id)
    try:
        # First request — may return a confirmation page for large files
        resp = SESSION.get(base_url, params=params, stream=True, timeout=60)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")

        if "text/html" in content_type:
            # Parse confirmation token from HTML
            html = resp.text
            # Modern Google Drive uses a different confirmation mechanism
            # Look for the download link in the HTML
            token_match = re.search(r'confirm=([0-9A-Za-z_\-]+)', html)
            uuid_match = re.search(r'uuid=([0-9A-Za-z_\-]+)', html)

            if token_match:
                confirm = token_match.group(1)
                params2 = {"export": "download", "id": file_id, "confirm": confirm}
                if uuid_match:
                    params2["uuid"] = uuid_match.group(1)
                log.info("  Got confirmation token, re-requesting ...")
                resp = SESSION.get(base_url, params=params2, stream=True, timeout=300)
                resp.raise_for_status()
            else:
                # Try the newer Google Drive export URL format
                # https://drive.usercontent.google.com/download?id=FILE_ID&export=download&authuser=0&confirm=t
                log.info("  No confirm token found, trying usercontent endpoint ...")
                resp.close()
                resp = SESSION.get(
                    "https://drive.usercontent.google.com/download",
                    params={"id": file_id, "export": "download", "authuser": "0", "confirm": "t"},
                    stream=True, timeout=300
                )
                resp.raise_for_status()
                content_type = resp.headers.get("content-type", "")
                if "text/html" in content_type:
                    log.error("  Still got HTML after confirm attempt — file may require auth")
                    return False

        # Stream to disk
        downloaded = 0
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                if chunk:
                    fh.write(chunk)
                    downloaded += len(chunk)

        size_mb = downloaded / 1e6
        log.info("  Downloaded %.1f MB -> %s", size_mb, dest.name)

        # Validate it looks like a CSV (not HTML)
        if downloaded < 1_000_000:
            # Read first line to check
            with open(dest) as fh:
                first = fh.read(500)
            if "<html" in first.lower() or "<!doctype" in first.lower():
                log.error("  %s appears to be HTML (%d bytes), removing", dest.name, downloaded)
                dest.unlink()
                return False

        return True

    except Exception as exc:
        log.error("  Failed: %s", exc)
        if dest.exists():
            dest.unlink()
        return False


def process_and_save(label: str, csv_path: Path) -> int:
    """
    Run the GaN-MN processor on csv_path. Write to raw_sightings/gan_mn_{slug}.csv.
    Returns count of records written (0 if already done or failed).
    """
    slug = label.lower()
    out_path = SIGHTINGS_DIR / f"gan_mn_{slug}.csv"

    if out_path.exists():
        with open(out_path) as fh:
            n = sum(1 for _ in fh) - 1
        log.info("Already processed %s (%d rows) — skipping", out_path.name, n)
        return n

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

    log.info("  -> %d records to %s", len(records), out_path.name)
    return len(records)


def count_existing_sightings() -> int:
    """Count rows in the 3 pre-existing monthly sightings CSVs."""
    total = 0
    for slug in ("august_2024", "january_2025", "june_2025"):
        p = SIGHTINGS_DIR / f"gan_mn_{slug}.csv"
        if p.exists():
            with open(p) as fh:
                n = sum(1 for _ in fh) - 1
            log.info("Pre-existing %s: %d rows", p.name, n)
            total += n
    return total


def main() -> None:
    results = []
    failed = []

    for label, file_id, filename in MONTHLY_FILES:
        dest = RAW_DIR / filename
        ok = gdrive_download(file_id, dest)
        if not ok:
            log.warning("Skipping processing for %s (download failed)", label)
            failed.append(label)
            continue

        count = process_and_save(label, dest)
        results.append((label, count))
        time.sleep(0.2)

    # Tally
    new_records = sum(c for _, c in results)
    pre_existing = count_existing_sightings()
    grand_total = new_records + pre_existing

    log.info("")
    log.info("=" * 60)
    log.info("COMPLETE")
    log.info("  Months processed this run: %d", len(results))
    log.info("  Twilight events from new months: %d", new_records)
    log.info("  Twilight events from 3 pre-existing months: %d", pre_existing)
    log.info("  GRAND TOTAL twilight events: %d", grand_total)
    if failed:
        log.warning("  Failed downloads (%d): %s", len(failed), ", ".join(failed))

    log.info("")
    log.info("Per-file breakdown:")
    for label, count in results:
        log.info("  %-15s %5d", label, count)


if __name__ == "__main__":
    main()
