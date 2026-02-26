"""
Data ingestion and standardization pipeline.

Converts any incoming sighting record (from CSV, dict, or manual entry) to the
canonical format: { prayer, date_local, time_local, utc_offset, lat, lng, elevation_m, source, notes }

Input formats supported:
  - Dict with explicit lat/lng
  - Dict with location_name/city (geocoded via Nominatim)
  - CSV file with columns: prayer, date, time, location/lat/lng, utc_offset, source

Usage:
  from src.ingest import standardize_record, load_raw_csv

  records = load_raw_csv("data/raw/raw_sightings/new_source.csv")
"""

from __future__ import annotations

import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from src.geocode import geocode
from src.elevation import get_elevations_batch

log = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "raw_sightings"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

# Required fields after standardization
REQUIRED_FIELDS = {"prayer", "date_local", "time_local", "utc_offset", "lat", "lng"}

# Standard column aliases for CSV imports
COLUMN_ALIASES: dict[str, list[str]] = {
    "prayer":      ["prayer", "type", "salah", "salat"],
    "date_local":  ["date_local", "date", "obs_date", "observation_date"],
    "time_local":  ["time_local", "time", "obs_time", "local_time"],
    "utc_offset":  ["utc_offset", "tz_offset", "timezone_offset", "utc"],
    "lat":         ["lat", "latitude"],
    "lng":         ["lng", "lon", "longitude"],
    "elevation_m": ["elevation_m", "elevation", "elev", "elev_m", "alt_m"],
    "source":      ["source", "citation", "ref", "reference"],
    "notes":       ["notes", "note", "comments", "comment"],
    "city":        ["city", "location", "location_name", "place", "site"],
    "country":     ["country"],
}


def _resolve_column(header: str) -> Optional[str]:
    """Map a CSV column name to a canonical field name."""
    h = header.lower().strip()
    for canonical, aliases in COLUMN_ALIASES.items():
        if h in aliases:
            return canonical
    return None


def standardize_record(raw: dict) -> Optional[dict]:
    """
    Normalize a raw sighting record to the canonical format.

    If lat/lng are missing but a city/location_name is present, geocodes the location.
    If elevation_m is missing or 0, leaves it as 0 (pipeline will call Open-Elevation).

    Returns None if the record cannot be standardized (missing critical fields).
    """
    record = {}

    # Copy all fields, normalising keys
    for raw_key, value in raw.items():
        canonical = _resolve_column(raw_key) or raw_key.lower().strip()
        record[canonical] = str(value).strip() if value is not None else ""

    # Geocode if lat/lng missing
    lat = record.get("lat") or record.get("latitude")
    lng = record.get("lng") or record.get("longitude") or record.get("lon")

    if not lat or not lng or lat == "0" or lng == "0":
        city = record.get("city") or record.get("location") or record.get("location_name")
        if city:
            country = record.get("country")
            coords = geocode(city, country_hint=country)
            if coords:
                record["lat"] = str(coords[0])
                record["lng"] = str(coords[1])
                log.info("geocoded %r → %s, %s", city, record["lat"], record["lng"])
            else:
                log.warning("could not geocode %r — skipping record", city)
                return None
        else:
            log.warning("record missing both lat/lng and city: %s", raw)
            return None

    # Type coercion
    try:
        record["lat"] = float(record["lat"])
        record["lng"] = float(record["lng"])
    except (ValueError, TypeError):
        log.warning("invalid lat/lng in record: %s", raw)
        return None

    record["elevation_m"] = float(record.get("elevation_m") or 0)
    record["utc_offset"] = float(record.get("utc_offset") or 0)

    # Normalise prayer name
    prayer = (record.get("prayer") or "").lower().strip()
    if prayer in ("fajr", "subh", "subuh", "dawn"):
        record["prayer"] = "fajr"
    elif prayer in ("isha", "isya", "isha'", "ishaa", "dusk", "shafaq"):
        record["prayer"] = "isha"
    else:
        log.warning("unknown prayer type %r — skipping", prayer)
        return None

    # Validate date
    date_raw = record.get("date_local") or ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(date_raw, fmt)
            record["date_local"] = dt.strftime("%Y-%m-%d")
            break
        except ValueError:
            pass
    else:
        log.warning("could not parse date %r — skipping", date_raw)
        return None

    # Validate time
    time_raw = record.get("time_local") or ""
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p"):
        try:
            t = datetime.strptime(time_raw, fmt)
            record["time_local"] = t.strftime("%H:%M")
            break
        except ValueError:
            pass
    else:
        log.warning("could not parse time %r — skipping", time_raw)
        return None

    # Ensure required fields
    for field in REQUIRED_FIELDS:
        if field not in record:
            log.warning("missing required field %r — skipping", field)
            return None

    # Defaults for optional fields
    record.setdefault("source", "unspecified")
    record.setdefault("notes", "")

    return record


def load_raw_csv(path: str | Path) -> list[dict]:
    """
    Load a raw sighting CSV, standardize each row, and return valid records.

    The CSV can have column names in any supported alias format (see COLUMN_ALIASES).
    Rows that cannot be standardized are skipped with a warning.
    """
    path = Path(path)
    records = []
    skipped = 0

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            result = standardize_record(dict(row))
            if result:
                records.append(result)
            else:
                skipped += 1
                log.debug("row %d skipped from %s", i, path.name)

    log.info("loaded %d records from %s (%d skipped)", len(records), path.name, skipped)
    return records


def ingest_all_raw_csvs(lookup_elevation: bool = True) -> list[dict]:
    """
    Load and standardize all CSV files in data/raw/raw_sightings/.

    Optionally looks up elevation for records with elevation_m == 0.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        log.info("No raw CSV files found in %s", RAW_DIR)
        return []

    all_records: list[dict] = []
    for f in csv_files:
        records = load_raw_csv(f)
        all_records.extend(records)
        log.info("  %s: %d records", f.name, len(records))

    if lookup_elevation:
        missing = [r for r in all_records if r.get("elevation_m", 0) == 0]
        if missing:
            locs = [(r["lat"], r["lng"]) for r in missing]
            elevs = get_elevations_batch(locs)
            for r, elev in zip(missing, elevs):
                if elev is not None:
                    r["elevation_m"] = elev

    return all_records
