"""
Extract per-night Fajr and Isha records from the BRIN Timau National Observatory
SQM_2020_2021.dat dataset.

Source: Priyatikanto, Rhorom (2022). Site characteristics: Timau National Observatory.
BRIN RIN Dataverse. hdl:20.500.12690/RIN/A5XCJB. CC0 1.0 (Public Domain).

Dataset: 470 nights (2020-05-20 to 2021-12-22), 1-minute SQM readings.
Site: Mount Timau, Kupang, East Nusa Tenggara, Indonesia
Coordinates: 8.65°S, 124.08°E, 1600m elevation, UTC+8
Sky quality: 21.86 ± 0.38 mag/arcsec² (pristine dark site)

Method: For each night, interpolate to find the UTC time when SunAlt crosses
the target depression angle (18° for Fajr, 18° for Isha). The SunAlt column is
the computed sun altitude (negative = below horizon); depression angle = -SunAlt.

Quality filter: Discard nights where the median dark-sky MPSAS is below 19.5
(cloud interference lowers sky brightness below instrumental noise).

Output: CSV rows compatible with ingest.py schema.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# Site constants
LAT = -8.65
LNG = 124.08
ELEVATION_M = 1600.0
UTC_OFFSET = 8.0
SOURCE_CITATION = (
    "Priyatikanto R. (2022). Site characteristics: Timau National Observatory. "
    "BRIN RIN Dataverse. hdl:20.500.12690/RIN/A5XCJB. CC0 1.0."
)

# Depression angle for Fajr/Isha at this pristine site
# Established in: Zodiacal light and astronomical twilight measurement at Timau
# National Observatory (2024 BRIN study). True Fajr at ~18°-20°; using 18.0° for
# SQM brightness-method Fajr (Q2 flag threshold), 18.0° for Isha.
FAJR_ANGLE = 18.0
ISHA_ANGLE = 18.0

# Clear-sky quality threshold: median MPSAS during deep night > this value
CLEAR_SKY_MIN_MPSAS = 19.5

# Window for morning twilight detection (hours from midnight, local time)
FAJR_HOURS_WINDOW = (3.0, 6.5)

# Window for evening twilight detection (hours from midnight, negative = evening)
ISHA_HOURS_WINDOW = (-4.5, -1.0)


def _interpolate_crossing(
    df_window: pd.DataFrame,
    target_sunalt: float,
    direction: str,  # "rising" (Fajr) or "falling" (Isha)
) -> Optional[tuple[datetime, float]]:
    """
    Find the UTC time when SunAlt crosses target_sunalt.

    Returns (utc_datetime, mpsas_at_crossing) or None if no crossing found.
    """
    if direction == "rising":
        # Sun altitude increasing toward zero (morning)
        # Find transition: SunAlt goes from < target to > target
        below = df_window["SunAlt"] < target_sunalt
        above = df_window["SunAlt"] >= target_sunalt
        if not (below.any() and above.any()):
            return None
        # Find first row where SunAlt >= target
        idx_cross = df_window[above].index[0]
        idx_before = idx_cross - 1
        if idx_before not in df_window.index:
            return None
    else:
        # Sun altitude decreasing away from zero (evening)
        # Find transition: SunAlt goes from > target to < target
        above = df_window["SunAlt"] > target_sunalt
        below = df_window["SunAlt"] <= target_sunalt
        if not (above.any() and below.any()):
            return None
        # Find first row where SunAlt <= target
        idx_cross = df_window[below].index[0]
        idx_before = idx_cross - 1
        if idx_before not in df_window.index:
            return None

    # Linear interpolation between the two bracketing rows
    row_before = df_window.loc[idx_before]
    row_cross = df_window.loc[idx_cross]

    alt_before = float(row_before["SunAlt"])
    alt_cross = float(row_cross["SunAlt"])
    t_before = pd.Timestamp(row_before["Datetime"])
    t_cross = pd.Timestamp(row_cross["Datetime"])

    if abs(alt_cross - alt_before) < 0.001:
        return None

    frac = (target_sunalt - alt_before) / (alt_cross - alt_before)
    dt_interp = t_before + (t_cross - t_before) * frac

    mpsas_interp = (
        float(row_before["MPSAS"])
        + (float(row_cross["MPSAS"]) - float(row_before["MPSAS"])) * frac
    )

    return dt_interp.to_pydatetime(), mpsas_interp


def _is_clear_night(df_night: pd.DataFrame) -> bool:
    """
    Return True if this night has clear enough skies.
    Uses the deep-night rows (|SunAlt| > 40°) as the quality reference.
    """
    deep_night = df_night[df_night["SunAlt"] < -40.0]
    if len(deep_night) < 10:
        return False
    median_mpsas = deep_night["MPSAS"].median()
    return float(median_mpsas) >= CLEAR_SKY_MIN_MPSAS


def _utc_to_local_time(utc_dt: datetime) -> tuple[str, str]:
    """Return (date_local YYYY-MM-DD, time_local HH:MM) for UTC+8."""
    local_dt = utc_dt + timedelta(hours=UTC_OFFSET)
    return local_dt.strftime("%Y-%m-%d"), local_dt.strftime("%H:%M")


def extract_from_sqm_file(dat_path: Path) -> list[dict]:
    """
    Process the full BRIN Timau SQM_2020_2021.dat file.

    Returns a list of raw sighting records (one per night per twilight type)
    in the schema expected by ingest.py.
    """
    log.info("Loading %s ...", dat_path)
    df = pd.read_csv(dat_path)
    df["Datetime"] = pd.to_datetime(df["Datetime"])

    records: list[dict] = []
    dates = sorted(df["Date"].unique())
    log.info("Processing %d nights from BRIN Timau SQM data", len(dates))

    clear_count = 0
    fajr_count = 0
    isha_count = 0

    for date_str in dates:
        night_df = df[df["Date"] == date_str].sort_values("Hours").reset_index(drop=True)

        if not _is_clear_night(night_df):
            continue
        clear_count += 1

        # --- Fajr (morning, sun rising) ---
        fajr_mask = (
            (night_df["Hours"] >= FAJR_HOURS_WINDOW[0]) &
            (night_df["Hours"] <= FAJR_HOURS_WINDOW[1]) &
            (night_df["SunAlt"] < 0)
        )
        fajr_window = night_df[fajr_mask].copy()
        if not fajr_window.empty:
            result = _interpolate_crossing(
                fajr_window,
                target_sunalt=-FAJR_ANGLE,
                direction="rising",
            )
            if result is not None:
                utc_dt, mpsas = result
                date_local, time_local = _utc_to_local_time(utc_dt)
                records.append({
                    "prayer": "fajr",
                    "date_local": date_local,
                    "time_local": time_local,
                    "utc_offset": UTC_OFFSET,
                    "lat": LAT,
                    "lng": LNG,
                    "elevation_m": ELEVATION_M,
                    "source": SOURCE_CITATION,
                    "notes": (
                        f"BRIN CC0 SQM per-minute time series; "
                        f"SunAlt interpolated to {-FAJR_ANGLE:.1f}° depression; "
                        f"MPSAS at crossing={mpsas:.3f}; "
                        f"pristine dark site (median {CLEAR_SKY_MIN_MPSAS}+ mag/arcsec²)"
                    ),
                })
                fajr_count += 1

        # --- Isha (evening, sun setting) ---
        isha_mask = (
            (night_df["Hours"] >= ISHA_HOURS_WINDOW[0]) &
            (night_df["Hours"] <= ISHA_HOURS_WINDOW[1]) &
            (night_df["SunAlt"] < 0)
        )
        isha_window = night_df[isha_mask].copy()
        if not isha_window.empty:
            result = _interpolate_crossing(
                isha_window,
                target_sunalt=-ISHA_ANGLE,
                direction="falling",
            )
            if result is not None:
                utc_dt, mpsas = result
                date_local, time_local = _utc_to_local_time(utc_dt)
                records.append({
                    "prayer": "isha",
                    "date_local": date_local,
                    "time_local": time_local,
                    "utc_offset": UTC_OFFSET,
                    "lat": LAT,
                    "lng": LNG,
                    "elevation_m": ELEVATION_M,
                    "source": SOURCE_CITATION,
                    "notes": (
                        f"BRIN CC0 SQM per-minute time series; "
                        f"SunAlt interpolated to {-ISHA_ANGLE:.1f}° depression (Shafaq Abyad); "
                        f"MPSAS at crossing={mpsas:.3f}; "
                        f"pristine dark site"
                    ),
                })
                isha_count += 1

    log.info(
        "Timau extraction: %d clear nights → %d Fajr + %d Isha records",
        clear_count, fajr_count, isha_count,
    )
    return records


def write_raw_csv(records: list[dict], output_path: Path) -> None:
    """Write extracted records to a raw CSV for ingestion by pipeline."""
    df = pd.DataFrame(records)
    if df.empty:
        log.warning("No records to write to %s", output_path)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    log.info("Wrote %d records to %s", len(df), output_path)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    dat_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/timau_sqm_2020_2021.dat")
    out_file = Path(__file__).parent.parent.parent / "data" / "raw" / "raw_sightings" / "timau_sqm_full_2020_2021.csv"

    records = extract_from_sqm_file(dat_file)
    write_raw_csv(records, out_file)
    print(f"\nExtracted {len(records)} total records")
    fajr = [r for r in records if r["prayer"] == "fajr"]
    isha = [r for r in records if r["prayer"] == "isha"]
    print(f"  Fajr: {len(fajr)}")
    print(f"  Isha: {len(isha)}")
    print(f"Output: {out_file}")
