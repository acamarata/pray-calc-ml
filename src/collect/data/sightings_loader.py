"""
sightings_loader -- raw verified sightings data and loader function.

Purpose:
    Provides the canonical VERIFIED_SIGHTINGS list (manually compiled
    human-observed Fajr and Isha sightings), the SightingRecord TypedDict
    schema, and load_verified_sightings() which converts the list to a
    timezone-aware DataFrame.

Input:
    verified_sightings_data.json in the same directory -- 661 records
    compiled from primary sources listed below. To add records, append
    to the JSON file; the structure matches SightingRecord exactly.

Output DataFrame schema (from load_verified_sightings):
    date        - datetime.date, local calendar date
    utc_dt      - datetime (timezone-aware UTC), computed from date_local +
                  time_local + utc_offset
    lat         - float, decimal degrees (north positive)
    lng         - float, decimal degrees (east positive)
    elevation_m - float, metres above sea level (0 = unknown, to be looked up)
    prayer      - str, "fajr" or "isha"
    source      - str, citation string
    notes       - str, observer notes

Key functions:
    load_verified_sightings() -> pd.DataFrame
        Converts VERIFIED_SIGHTINGS to a timezone-aware DataFrame.

Primary sources (see verified_sightings_data.json for per-record citations):
    [OIF]  = OIF UMSU (Observatory, University of Muhammadiyah North Sumatra)
             Published in NRIAG J. Astronomy & Geophysics; multiple papers
    [NRIAG] = National Research Institute of Astronomy and Geophysics, Egypt
             Papers: Hassan et al. 2014, Rashed et al. 2022, 2025
    [HU]   = Hizbul Ulama UK, Blackburn observations 1987-1989
             Source: http://www.hizbululama.org.uk/files/salat_timing.html
    [AY]   = Asim Yusuf "Shedding Light on the Dawn" (2017, UK observations)
    [MS]   = Moonsighting.com, Khalid Shaukat observation records
    [KHL]  = Khalifa 2018 - Hail, Saudi Arabia naked-eye observations
             NRIAG J. Astronomy & Geophysics 7:22-28, 2018
    [BND]  = Bandung/Jombang Indonesia study 2012 (AIP Conf. Proc. 1454)
    [KAS]  = Kassim Bahali et al. 2018, Malaysia+Indonesia DSLR study
             Sains Malaysia 47(11)

SPORT: .opencode/phases/sport/packages.md -- pray-calc-ml row
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import TypedDict

import pandas as pd


class SightingRecord(TypedDict):
    prayer:      str    # "fajr" or "isha"
    date_local:  str    # ISO date string, YYYY-MM-DD
    time_local:  str    # HH:MM (24h) in local time
    utc_offset:  float  # hours offset from UTC
    lat:         float  # decimal degrees (north positive)
    lng:         float  # decimal degrees (east positive)
    elevation_m: float  # metres above sea level (0 = unknown, will be looked up)
    source:      str    # citation
    notes:       str


# ---------------------------------------------------------------------------
# Load VERIFIED_SIGHTINGS from the companion JSON file.
#
# The data lives in verified_sightings_data.json (same directory) to keep
# this module under the 1600-line budget while allowing the dataset to grow
# beyond 600+ records without bloating Python source files.
#
# To add new records: append a SightingRecord-shaped dict to the JSON array.
# Run `python -m src.pipeline --no-elevation-lookup` after adding records.
# ---------------------------------------------------------------------------

_DATA_FILE = Path(__file__).parent / "verified_sightings_data.json"


def _load_data() -> list[SightingRecord]:
    """Load VERIFIED_SIGHTINGS from the companion JSON file at import time."""
    with _DATA_FILE.open(encoding="utf-8") as fh:
        raw: list[dict] = json.load(fh)
    # Cast to SightingRecord -- JSON gives us float/str/int natively.
    # Ensure elevation_m is float (JSON may store integers).
    for rec in raw:
        rec["utc_offset"] = float(rec["utc_offset"])
        rec["lat"] = float(rec["lat"])
        rec["lng"] = float(rec["lng"])
        rec["elevation_m"] = float(rec["elevation_m"])
    return raw  # type: ignore[return-value]


# Module-level constant: load once on import.
VERIFIED_SIGHTINGS: list[SightingRecord] = _load_data()


def load_verified_sightings() -> pd.DataFrame:
    """
    Return all manually compiled verified sightings as a DataFrame with
    utc_dt (timezone-aware UTC) computed from date_local + time_local + utc_offset.

    Output columns: date, utc_dt, lat, lng, elevation_m, prayer, source, notes

    Returns:
        pd.DataFrame with one row per sighting. utc_dt is timezone-aware UTC.
    """
    rows = []
    for s in VERIFIED_SIGHTINGS:
        offset = timedelta(hours=s["utc_offset"])
        local_dt = datetime.strptime(
            f"{s['date_local']} {s['time_local']}", "%Y-%m-%d %H:%M"
        )
        utc_dt = (local_dt - offset).replace(tzinfo=timezone.utc)
        rows.append(
            {
                "date": local_dt.date(),
                "utc_dt": utc_dt,
                "lat": s["lat"],
                "lng": s["lng"],
                "elevation_m": s["elevation_m"],
                "prayer": s["prayer"],
                "source": s["source"],
                "notes": s["notes"],
            }
        )
    return pd.DataFrame(rows)
