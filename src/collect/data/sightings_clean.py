"""
sightings_clean -- quality filtering and deduplication for sightings DataFrames.

Purpose:
    Provides functions that remove non-genuine records (computed/aggregate/
    timetable-sourced), deduplicate cross-source overlaps, and apply geographic
    and temporal quality filters. These routines were extracted from
    src/pipeline.py to isolate data-cleaning concerns.

Input DataFrame schema (expected from load_verified_sightings or equivalent):
    prayer      - str, "fajr" or "isha"
    date        - str or datetime.date, local calendar date
    utc_dt      - datetime (timezone-aware UTC)
    lat         - float, decimal degrees
    lng         - float, decimal degrees
    elevation_m - float, metres above sea level
    source      - str, citation string
    notes       - str, observer notes
    angle       - float (optional, needed for apply_quality_filters)

Output DataFrame schema:
    Same columns as input, with invalid/duplicate rows removed.

Key functions:
    filter_non_genuine(df)  -- drop records computed from angles, not observed
    deduplicate_sightings(df) -- drop same prayer+date+location duplicates
    apply_quality_filters(df) -- drop future dates, polar lats, implausible angles

SPORT: .opencode/phases/sport/packages.md -- pray-calc-ml row
"""

from __future__ import annotations

import logging
from datetime import date as date_type

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Markers that identify non-genuine records.
# A record whose notes OR source field contains any of these strings (case-
# insensitive) is dropped before angle computation because its time was not
# directly observed but inferred from a published mean angle or taken from
# a government timetable.
# ---------------------------------------------------------------------------
BAD_NOTE_MARKERS = (
    # Time-computation markers
    "time inferred",
    "aggregate representative",
    "seasonal representative",
    "representative date",
    "time computed",
    "back-calculated from",
    # Government timetable sources
    "JAKIM official",
    "Diyanet official",
    "Diyanet Turkey",
    "Diyanet research",
    "Ministry of Awqaf",
    "Ministry of Habous",
    "Moroccan Ministry",
    "Iranian Supreme Court",
    "Bangladesh Islamic Foundation",
    "Nigeria Islamic astronomy consensus",
    "MJC South Africa standard",
    "Umm al-Qura standard",
    "Pakistan astronomical estimates",
    "Dubai Awqaf",
    "Oman Ministry",
    "Kerala Islamic Body",
    "Jordanian Ministry",
    # Community aggregate sources
    "AFIC community observations",
    "Community observations",
    # Khalid Shaukat seasonal aggregates
    "Moonsighting.com / Khalid Shaukat",
    # Per-source exclusions of known synthetic datasets
    "Hamidi 2007-2008 Isha",
    "OIF UMSU 2017-2020",
    "Kassim Bahali 2018, Sains Malaysia 47(11)",
    "Rashed et al. 2025, NRIAG J., Alexandria",
    "Bandung/Jombang study 2012",
    "urban LP mean",
    "Saksono & Fulazzaky 2020",
    "Saksono 2020, NRIAG J.",
    "Hassan et al. 2016, NRIAG J. 5:9-15",
    "Rashed et al. 2022, IJMET",
    "Pinem et al. 2024",
    # Generic note-pattern filters
    "equinox aggregate",
    "solstice aggregate",
    "equinox inferred",
    "solstice inferred",
    "rep date",
    # Wrong Isha criterion (shafaq ahmar is not the dataset criterion)
    "Shafaq Ahmar",
    "shafaq ahmar",
    "red dusk twilight",
)

# Angle plausibility bounds (degrees).
# No confirmed genuine sighting falls outside these ranges.
FAJR_MIN_DEG = 7.0
ISHA_MIN_DEG = 10.0
MAX_DEG = 22.0

# Geographic filter: drop polar latitudes (no meaningful Fajr/Isha).
POLAR_LAT_THRESHOLD = 70.0


def filter_non_genuine(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove records whose time was computed from a known angle rather than
    directly observed by a human or calibrated instrument.

    Checks both the ``notes`` and ``source`` columns against BAD_NOTE_MARKERS
    (case-insensitive). Any match in either column causes the row to be dropped.

    Parameters:
        df: DataFrame with at least ``notes`` and ``source`` columns.

    Returns:
        Filtered DataFrame with non-genuine rows removed. Index is reset.
    """
    bad_notes = df["notes"].apply(
        lambda n: any(m.lower() in str(n).lower() for m in BAD_NOTE_MARKERS)
    )
    bad_source = df["source"].apply(
        lambda s: any(m.lower() in str(s).lower() for m in BAD_NOTE_MARKERS)
    )
    mask = bad_notes | bad_source
    n_dropped = mask.sum()
    if n_dropped > 0:
        dropped = df[mask]
        logger.info(
            "filter_non_genuine: dropping %d non-genuine record(s) "
            "(inferred/aggregate/timetable-sourced):",
            n_dropped,
        )
        for src, cnt in dropped["source"].value_counts().items():
            logger.info("  %3d  %s", cnt, src)
    return df[~mask].copy().reset_index(drop=True)


def deduplicate_sightings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate records that refer to the same sighting published in
    multiple sources.

    Two rows are considered duplicates when they share the same (prayer, date,
    lat rounded to 3 dp, lng rounded to 3 dp). The first occurrence is kept;
    later occurrences are dropped. Rounding to 3 decimal places corresponds to
    ~111 m spatial resolution, which is sufficient to identify same-location
    cross-source overlaps.

    Parameters:
        df: DataFrame with ``prayer``, ``date``, ``lat``, ``lng`` columns.

    Returns:
        Deduplicated DataFrame. Index is reset.
    """
    df = df.copy()
    df["_lat_r"] = df["lat"].round(3)
    df["_lng_r"] = df["lng"].round(3)
    dup_mask = df.duplicated(subset=["prayer", "date", "_lat_r", "_lng_r"], keep="first")
    n_dups = dup_mask.sum()
    if n_dups > 0:
        logger.info(
            "deduplicate_sightings: removing %d cross-source duplicate(s) "
            "(same prayer+date+location):",
            n_dups,
        )
        for _, row in df[dup_mask].iterrows():
            logger.info(
                "  %s %s lat=%.3f lng=%.3f -- %s",
                row["prayer"].upper(),
                row["date"],
                row["lat"],
                row["lng"],
                row["source"],
            )
    df = df[~dup_mask].copy()
    df = df.drop(columns=["_lat_r", "_lng_r"])
    return df.reset_index(drop=True)


def apply_quality_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply geographic, temporal, and angle plausibility filters.

    Removes:
    - Future-dated records (OpenFajr publishes predictions for the full year;
      these are not yet-observed, so they must be excluded from the dataset).
    - Polar latitudes (|lat| > 70°): Fajr and Isha have no well-defined
      twilight boundary at extreme latitudes.
    - Null Island coordinates (lat~0, lng~0): GPS default / missing coordinates.
    - Records with implausible solar depression angles:
        Fajr: outside [FAJR_MIN_DEG, MAX_DEG]
        Isha: outside [ISHA_MIN_DEG, MAX_DEG]
    - Records where ``angle`` is NaN (angle computation failed).

    Parameters:
        df: DataFrame with ``date``, ``lat``, ``lng``, ``prayer``, and ``angle``
            columns. ``date`` may be a string ("YYYY-MM-DD") or datetime.date.

    Returns:
        Filtered DataFrame. Index is reset.
    """
    df = df.copy()
    today_str = str(date_type.today())

    # Drop future-dated records
    future = df["date"].astype(str) > today_str
    if future.any():
        logger.info(
            "apply_quality_filters: dropping %d future-dated record(s)", future.sum()
        )
        df = df[~future].copy()

    # Drop polar stations
    polar = df["lat"].abs() > POLAR_LAT_THRESHOLD
    if polar.any():
        logger.info(
            "apply_quality_filters: dropping %d polar record(s) (|lat| > %g°)",
            polar.sum(),
            POLAR_LAT_THRESHOLD,
        )
        df = df[~polar].copy()

    # Drop Null Island
    null_island = (df["lat"].abs() < 0.01) & (df["lng"].abs() < 0.01)
    if null_island.any():
        logger.info(
            "apply_quality_filters: dropping %d Null Island record(s)", null_island.sum()
        )
        df = df[~null_island].copy()

    # Drop implausible angles (requires "angle" column present)
    if "angle" in df.columns:
        fajr_bad = (df["prayer"] == "fajr") & (
            (df["angle"] < FAJR_MIN_DEG) | (df["angle"] > MAX_DEG)
        )
        isha_bad = (df["prayer"] == "isha") & (
            (df["angle"] < ISHA_MIN_DEG) | (df["angle"] > MAX_DEG)
        )
        bad = fajr_bad | isha_bad | df["angle"].isna()
        if bad.any():
            logger.info(
                "apply_quality_filters: dropping %d record(s) with implausible "
                "angles (Fajr: <%.0f° or >%.0f° / Isha: <%.0f° or >%.0f°)",
                bad.sum(),
                FAJR_MIN_DEG,
                MAX_DEG,
                ISHA_MIN_DEG,
                MAX_DEG,
            )
            df = df[~bad].copy()

    return df.reset_index(drop=True)
