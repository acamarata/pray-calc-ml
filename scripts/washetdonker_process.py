"""
Process washetdonker.nl SQM .dat files to extract twilight events.

Each .dat file covers one night (noon-to-noon UTC) for one station.
The SQM measures sky brightness in MSAS (mag/arcsec^2):
  - Day/bright sky: MSAS = -0.000 (saturated, unusable)
  - Twilight: MSAS rises from -0.000 to ~5-8 (civil), ~10-12 (nautical), ~17-19 (astro)
  - Dark night: MSAS ~19-21 at pristine sites, ~17-19 in the Netherlands

Twilight event extraction strategy
-----------------------------------
For morning twilight (Fajr territory):
  1. Find the dark-night plateau after midnight UTC.
  2. Detect when MSAS begins monotonically declining after the plateau.
  3. The first sustained drop is astronomical twilight.
  4. We record the time when MSAS crosses several thresholds and compute the
     solar depression angle at each threshold.

We do NOT attempt to identify true Fajr from SQM data alone — that requires
human observation. Instead, we extract:
  - The time when the sky starts brightening (astronomical twilight onset)
  - The solar depression angle at that moment
  - Times and angles at MSAS = 17.0, 15.0, 12.0, 10.0, 8.0, 6.0, 4.0

These become calibration points: if a human says "Fajr was at 12°", we can look
at what the SQM was reading at that location on nearby nights at 12° depression
and see if the brightness threshold is consistent.

Output CSVs
-----------
  data/raw/washetdonker/events_morning.csv  — morning twilight events
  data/raw/washetdonker/events_evening.csv  — evening twilight events
  data/raw/raw_sightings/washetdonker_astronomical_morning.csv  — pipeline-ready

Usage:
    python scripts/washetdonker_process.py [--station Texel] [--year 2024]
    python scripts/washetdonker_process.py --all
"""
from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.angle_calc import depression_angle  # noqa: E402

RAW_ROOT = REPO_ROOT / "data" / "raw" / "washetdonker"
SIGHTINGS_DIR = REPO_ROOT / "data" / "raw" / "raw_sightings"

# MSAS thresholds at which we record a crossing event.
# Lower MSAS = brighter sky. Morning = sky gets brighter = MSAS decreasing.
MSAS_THRESHOLDS = [18.0, 17.0, 16.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 9.0, 8.0, 6.0]

# Minimum MSAS for a "valid dark night" reading (filters daytime saturation)
MSAS_MIN_VALID = 4.0

# Dark-night plateau: readings must reach this to be a genuine astronomical night
MSAS_DARK_THRESHOLD = 14.0

# A twilight event is real if MSAS changes by at least this much from plateau
MSAS_SIGNIFICANT_CHANGE = 2.0


def parse_header(lines: list[str]) -> dict:
    """Extract lat, lng, elevation, station name, timezone from header lines."""
    meta = {"lat": None, "lng": None, "elevation_m": 0.0, "station": "", "utc_offset": 0.0}
    for line in lines:
        if not line.startswith("#"):
            break
        line = line[1:].strip()
        if line.startswith("Position:"):
            parts = line.split(":", 1)[1].strip().split(",")
            try:
                meta["lat"] = float(parts[0].strip())
                meta["lng"] = float(parts[1].strip())
                if len(parts) > 2:
                    meta["elevation_m"] = float(parts[2].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith("Location name:"):
            meta["station"] = line.split(":", 1)[1].strip()
        elif line.startswith("Local timezone:"):
            tz_str = line.split(":", 1)[1].strip()
            # e.g. "UTC+1" or "UTC+2" or "UTC+0"
            m = re.search(r"UTC([+-]\d+)", tz_str)
            if m:
                meta["utc_offset"] = float(m.group(1))
    return meta


def read_dat_file(path: Path) -> tuple[dict, list[tuple[datetime, float]]]:
    """
    Parse a washetdonker .dat file.

    Returns (metadata_dict, [(utc_datetime, msas_value), ...])
    Only rows with MSAS > MSAS_MIN_VALID are included (filters daylight saturation).
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    # Find header end
    header_lines = []
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith("#"):
            header_lines.append(line)
        else:
            data_start = i
            break

    meta = parse_header(header_lines)

    rows: list[tuple[datetime, float]] = []
    for line in lines[data_start:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split(";")
        if len(parts) < 6:
            continue
        try:
            utc_str = parts[0].strip()
            msas = float(parts[5].strip())
        except (ValueError, IndexError):
            continue

        if msas < MSAS_MIN_VALID:
            continue  # daytime saturation reading

        try:
            utc_dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S.%f").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            try:
                utc_dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                continue

        rows.append((utc_dt, msas))

    return meta, rows


def find_plateau(rows: list[tuple[datetime, float]]) -> Optional[float]:
    """
    Find the median MSAS of the dark-night plateau.
    Uses the darkest 30-minute window in the night.
    Returns None if no valid dark night.
    """
    if not rows:
        return None

    # Only look at readings with MSAS > MSAS_DARK_THRESHOLD
    dark_rows = [msas for _, msas in rows if msas >= MSAS_DARK_THRESHOLD]
    if len(dark_rows) < 5:
        return None

    dark_rows.sort(reverse=True)
    # Use 75th percentile of dark readings as plateau estimate
    idx = max(0, int(len(dark_rows) * 0.25))
    return dark_rows[idx]


def find_morning_twilight_events(
    rows: list[tuple[datetime, float]],
    meta: dict,
) -> list[dict]:
    """
    Find the morning twilight onset and threshold crossings.

    Strategy:
    1. Find the dark night plateau MSAS.
    2. Find the minimum-MSAS (darkest point) in the second half of the night.
    3. From there, scan forward to find when MSAS starts dropping.
    4. For each MSAS threshold, find the first crossing time and compute solar angle.
    """
    if not rows or meta["lat"] is None:
        return []

    plateau = find_plateau(rows)
    if plateau is None:
        return []

    # Only look at rows after midnight UTC (morning half)
    # The file covers one noon-to-noon period; morning is after UTC midnight
    midnight_rows = [(dt, msas) for dt, msas in rows if dt.hour >= 0 and dt.hour < 12]
    if len(midnight_rows) < 10:
        return []

    # Find the darkest point (highest MSAS) in morning half
    darkest_idx = max(range(len(midnight_rows)), key=lambda i: midnight_rows[i][1])
    darkest_msas = midnight_rows[darkest_idx][1]

    # If darkest MSAS is too low, cloudy/moon/bad night — skip
    if darkest_msas < MSAS_DARK_THRESHOLD:
        return []

    # Scan forward from darkest point to find threshold crossings
    events = []
    threshold_crossed = set()

    for i in range(darkest_idx, len(midnight_rows)):
        dt, msas = midnight_rows[i]
        for threshold in MSAS_THRESHOLDS:
            if threshold in threshold_crossed:
                continue
            if msas <= threshold <= darkest_msas:
                threshold_crossed.add(threshold)
                # Compute solar depression angle at this moment
                try:
                    angle = depression_angle(
                        dt.replace(tzinfo=None),
                        meta["lat"],
                        meta["lng"],
                        meta["elevation_m"],
                    )
                except Exception as exc:
                    log.debug("angle_calc error: %s", exc)
                    continue

                events.append({
                    "station": meta["station"],
                    "lat": meta["lat"],
                    "lng": meta["lng"],
                    "elevation_m": meta["elevation_m"],
                    "utc_dt": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "msas": round(msas, 3),
                    "msas_threshold": threshold,
                    "plateau_msas": round(darkest_msas, 3),
                    "solar_depression_deg": round(angle, 4),
                    "direction": "morning",
                    "source": f"washetdonker.nl/{meta['station']}",
                })

    return events


def find_evening_twilight_events(
    rows: list[tuple[datetime, float]],
    meta: dict,
) -> list[dict]:
    """
    Find evening twilight threshold crossings.

    The file starts at noon UTC. Evening twilight is in the first part,
    when MSAS rises from -0.000 (saturated) to dark values.
    We find the first time MSAS exceeds each threshold.
    """
    if not rows or meta["lat"] is None:
        return []

    plateau = find_plateau(rows)
    if plateau is None:
        return []

    # Evening half: from file start until midnight UTC
    evening_rows = [(dt, msas) for dt, msas in rows if dt.hour >= 12 or dt.hour < 0]
    # Actually the file noon-to-noon. Rows before midnight are evening.
    # UTC rows with hour 12-23 are evening.
    evening_rows = [(dt, msas) for dt, msas in rows if dt.hour >= 12]
    if len(evening_rows) < 10:
        return []

    darkest_msas = max(msas for _, msas in rows)
    if darkest_msas < MSAS_DARK_THRESHOLD:
        return []

    events = []
    threshold_crossed = set()

    # Evening: MSAS increasing (sky getting darker)
    # Find each threshold crossing from below (first time MSAS exceeds threshold)
    for dt, msas in evening_rows:
        for threshold in MSAS_THRESHOLDS:
            if threshold in threshold_crossed:
                continue
            if msas >= threshold:
                threshold_crossed.add(threshold)
                try:
                    angle = depression_angle(
                        dt.replace(tzinfo=None),
                        meta["lat"],
                        meta["lng"],
                        meta["elevation_m"],
                    )
                except Exception as exc:
                    log.debug("angle_calc error: %s", exc)
                    continue

                events.append({
                    "station": meta["station"],
                    "lat": meta["lat"],
                    "lng": meta["lng"],
                    "elevation_m": meta["elevation_m"],
                    "utc_dt": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "msas": round(msas, 3),
                    "msas_threshold": threshold,
                    "plateau_msas": round(darkest_msas, 3),
                    "solar_depression_deg": round(angle, 4),
                    "direction": "evening",
                    "source": f"washetdonker.nl/{meta['station']}",
                })

    return events


EVENT_FIELDNAMES = [
    "station", "lat", "lng", "elevation_m",
    "utc_dt", "msas", "msas_threshold", "plateau_msas",
    "solar_depression_deg", "direction", "source",
]

# Pipeline-compatible fieldnames for morning events at the 12.0 MSAS threshold
# (approximate astronomical twilight boundary)
PIPELINE_FIELDNAMES = [
    "prayer", "date_local", "time_local", "utc_offset",
    "lat", "lng", "elevation_m", "source", "notes",
]


def event_to_pipeline_row(event: dict, utc_offset: float) -> dict:
    """Convert an event dict to the pipeline CSV format."""
    utc_dt = datetime.strptime(event["utc_dt"], "%Y-%m-%dT%H:%M:%SZ")
    from datetime import timedelta
    local_dt = utc_dt + timedelta(hours=utc_offset)
    return {
        "prayer": "fajr",
        "date_local": local_dt.strftime("%Y-%m-%d"),
        "time_local": local_dt.strftime("%H:%M"),
        "utc_offset": utc_offset,
        "lat": event["lat"],
        "lng": event["lng"],
        "elevation_m": event["elevation_m"],
        "source": event["source"],
        "notes": (
            f"SQM MSAS={event['msas']} at threshold={event['msas_threshold']} "
            f"plateau={event['plateau_msas']} "
            f"solar_depression={event['solar_depression_deg']}deg "
            f"direction=morning"
        ),
    }


def process_all(station_filter: Optional[str], year_filter: Optional[int]) -> dict:
    """Process all downloaded .dat files. Returns counts dict."""
    morning_events: list[dict] = []
    evening_events: list[dict] = []

    dat_files = list(RAW_ROOT.rglob("*.dat"))
    if not dat_files:
        log.warning("No .dat files found in %s", RAW_ROOT)
        return {"files": 0, "morning": 0, "evening": 0}

    if station_filter:
        dat_files = [f for f in dat_files if station_filter in str(f)]
    if year_filter:
        dat_files = [f for f in dat_files if f"/{year_filter}/" in str(f)]

    log.info("Processing %d .dat files ...", len(dat_files))

    for i, path in enumerate(sorted(dat_files)):
        if i % 100 == 0 and i > 0:
            log.info("  %d / %d files  (morning=%d evening=%d)",
                     i, len(dat_files), len(morning_events), len(evening_events))
        try:
            meta, rows = read_dat_file(path)
        except Exception as exc:
            log.debug("Parse error %s: %s", path.name, exc)
            continue

        if not rows:
            continue

        m_events = find_morning_twilight_events(rows, meta)
        e_events = find_evening_twilight_events(rows, meta)
        morning_events.extend(m_events)
        evening_events.extend(e_events)

    log.info("Extraction complete. Morning events: %d  Evening events: %d",
             len(morning_events), len(evening_events))

    # Write full events CSVs
    RAW_ROOT.mkdir(parents=True, exist_ok=True)

    morning_out = RAW_ROOT / "events_morning.csv"
    with open(morning_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVENT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(morning_events)
    log.info("Written: %s", morning_out)

    evening_out = RAW_ROOT / "events_evening.csv"
    with open(evening_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVENT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(evening_events)
    log.info("Written: %s", evening_out)

    # Write pipeline-compatible CSV for morning events at the astronomical threshold
    # Pick the threshold closest to known astronomical twilight (~18°)
    # For Netherlands stations (high latitude, low MSAS ceilings), use MSAS=17.0
    # We export ALL threshold crossings for the pipeline to pick the best one
    SIGHTINGS_DIR.mkdir(parents=True, exist_ok=True)
    pipeline_out = SIGHTINGS_DIR / "washetdonker_morning.csv"

    # Use the MSAS=15.0 threshold as a reasonable proxy for deep twilight onset
    # (roughly maps to astronomical twilight at Dutch latitudes)
    pipeline_rows = []
    utc_offset_cache: dict[str, float] = {}

    for ev in morning_events:
        if ev["msas_threshold"] != 15.0:
            continue
        if ev["solar_depression_deg"] < 7.0:
            continue  # too close to horizon — unreliable

        # Use stored utc_offset from the station's most-recently-seen offset
        # (we don't store it in the event; approximate from known Netherlands offset)
        # Netherlands is UTC+1 (winter) / UTC+2 (summer). Approximate from date.
        utc_dt = datetime.strptime(ev["utc_dt"], "%Y-%m-%dT%H:%M:%SZ")
        month = utc_dt.month
        utc_offset = 2.0 if 3 <= month <= 10 else 1.0

        pipeline_rows.append(event_to_pipeline_row(ev, utc_offset))

    with open(pipeline_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PIPELINE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(pipeline_rows)
    log.info("Written pipeline CSV: %s (%d rows)", pipeline_out, len(pipeline_rows))

    return {
        "files": len(dat_files),
        "morning": len(morning_events),
        "evening": len(evening_events),
        "pipeline_rows": len(pipeline_rows),
    }


def main():
    ap = argparse.ArgumentParser(description="Process washetdonker SQM .dat files")
    ap.add_argument("--station", help="Filter to one station name")
    ap.add_argument("--year", type=int, help="Filter to one year")
    ap.add_argument("--all", dest="all", action="store_true",
                    help="Process all downloaded files")
    args = ap.parse_args()

    counts = process_all(args.station, args.year)
    print(f"\nSummary:")
    print(f"  Files processed: {counts['files']}")
    print(f"  Morning events:  {counts['morning']}")
    print(f"  Evening events:  {counts['evening']}")
    print(f"  Pipeline rows:   {counts.get('pipeline_rows', 0)}")


if __name__ == "__main__":
    main()
