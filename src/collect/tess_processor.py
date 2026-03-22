"""
Extract per-night Fajr and Isha depression angles from TESS-IDA photometer data.

Source: TESS (Stars4All / UCM) network — all-sky night sky brightness monitors.
Data format: flat CSV with columns:
    name, tamb, tsky, mag, tstamp, latitude, longitude

where:
    name      - station identifier (e.g. "stars9")
    tamb      - ambient temperature (°C)
    tsky      - sky temperature (°C)
    mag       - MSAS (magnitudes per arcsecond squared, sky brightness)
                higher = darker sky; invalid readings recorded as 0
    tstamp    - UTC ISO-8601 timestamp
    latitude  - decimal degrees (north positive)
    longitude - decimal degrees (east positive)

Data files are available from the Zenodo TESS monthly archives. June 2019 record:
    https://zenodo.org/records/3378728

Method
------
For each station in the input files:

1. Load and filter: drop mag=0 (sensor saturated or invalid), drop daytime readings
   (solar altitude >= -2°, computed via PyEphem).

2. Group by local night. A "night" runs from local sunset to next local sunrise,
   identified by grouping around the solar midnight (the UTC moment of minimum
   solar altitude for that calendar day).

3. Characterise the night baseline: compute the median MSAS across the darkest
   portion (solar depression > 10°). Skip nights with fewer than MIN_DARK_ROWS
   valid readings.

4. Find the twilight inflection point using the maximum rate of MSAS change
   (|dMSAS/dt|) during each twilight window. The inflection occurs at the moment
   sky brightness transitions most rapidly — this is the sharpest photometric
   signal of twilight onset/end.

5. Compute the solar depression angle at that inflection moment via PyEphem.
   Record it as a Fajr sighting (dawn inflection) or Isha sighting (dusk inflection).

6. Quality filters:
   - Reject nights where the dark-window MSAS median < MIN_DARK_MSAS (heavily
     light-polluted, sky never gets dark enough to track astronomical twilight).
   - Reject if the inflection MSAS is > MSAS_INFLECTION_MAX from the night median
     (likely cloud passage, not real twilight transition).
   - Reject if the computed depression angle is outside ANGLE_MIN to ANGLE_MAX
     (would indicate a sensor anomaly or extreme atmospheric conditions).

Output
------
List of raw sighting dicts matching the pray-calc-ml raw sightings CSV schema:
    prayer, date_local, time_local, utc_offset, lat, lng, elevation_m, source, notes

Limitations
-----------
- TESS stations report no sky quality flags (unlike BRIN data which has Q codes).
  Cloud rejection is inferred from MSAS variability and night baseline consistency.
- Station elevation is not in the CSV. Defaults to 0 m (minor effect on angle calc).
- The inflection-point method captures the steepest brightness change, which
  corresponds closely to the transition from civil/nautical to astronomical twilight.
  It does NOT identify Shafaq al-Ahmar (red twilight). The captured angle typically
  falls in the 10°-18° depression range depending on season and latitude.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import ephem
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# --- Configuration -------------------------------------------------------

# Minimum number of valid dark-sky readings required to accept a night.
# At 1-minute cadence, this requires at least 20 minutes of darkness.
MIN_DARK_ROWS = 20

# Minimum MSAS to accept a station night as "dark enough" to extract twilight.
# Sites with median MSAS below this are too light-polluted for reliable twilight
# detection. Rough Bortle correlation: 18.0 ~ Bortle 7 (suburban).
MIN_DARK_MSAS = 17.5

# Solar depression angle band for twilight classification.
# The inflection should fall somewhere in this range. Readings outside it are
# rejected as sensor artifacts or extreme conditions.
ANGLE_MIN = 6.0
ANGLE_MAX = 22.0

# Solar depression angle below which we consider it "nighttime" for baseline
# computation. 10° = nautical twilight well established.
DARK_DEPRESSION_THRESHOLD = 10.0

# Half-width in hours of the twilight search window around astronomical
# dawn/dusk times. Searching +/- 2.5 h around predicted 18° crossing.
TWILIGHT_WINDOW_HALF_H = 2.5

# Smoothing window (rows) for the MSAS series before computing derivatives.
# At 1-min cadence this is a 5-minute rolling window — reduces single-reading
# noise without blurring the ~20-minute twilight transition.
SMOOTH_WINDOW = 5

# Maximum MSAS deviation (mag) from night median allowed at the inflection.
# If the inflection reading is more than this below the night median,
# the night is likely cloudy or the sensor is suspect.
MSAS_INFLECTION_MAX_DROP = 2.5

SOURCE_CITATION = (
    "Zamorano J. et al. (2019). TESS-W sky brightness network. "
    "Zenodo monthly archives. https://zenodo.org/records/3378728. CC0 1.0."
)

ELEVATION_DEFAULT = 0.0


# --- PyEphem helpers -------------------------------------------------------


def _make_observer(lat: float, lng: float, elevation_m: float = 0.0) -> ephem.Observer:
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lng)
    obs.elevation = float(elevation_m)
    obs.pressure = 1013.25
    obs.temp = 15.0
    return obs


def _solar_depression(utc_dt: datetime, obs: ephem.Observer) -> float:
    """Return solar depression angle (degrees, positive = sun below horizon)."""
    if utc_dt.tzinfo is not None:
        utc_naive = utc_dt.replace(tzinfo=None)
    else:
        utc_naive = utc_dt
    obs.date = ephem.Date(utc_naive)
    sun = ephem.Sun(obs)
    sun.compute(obs)
    return -math.degrees(float(sun.alt))


def _solar_midnight_utc(date: datetime.date, lat: float, lng: float) -> datetime:
    """
    Return the UTC time of solar midnight (minimum solar altitude) for the
    given local calendar date at the given coordinates.

    Uses a simple search over the 24-hour window centred on the date's midnight.
    """
    obs = _make_observer(lat, lng)
    sun = ephem.Sun()

    # Search in 1-minute increments across the day to find minimum altitude
    base = datetime(date.year, date.month, date.day, 12, 0, 0)  # UTC noon as anchor
    best_time = base
    best_alt = 1e9

    for offset_min in range(-12 * 60, 12 * 60):
        candidate = base + timedelta(minutes=offset_min)
        obs.date = ephem.Date(candidate)
        sun.compute(obs)
        alt = float(sun.alt)
        if alt < best_alt:
            best_alt = alt
            best_time = candidate

    return best_time


# --- MSAS processing -------------------------------------------------------


def _compute_solar_depression_series(df: pd.DataFrame, obs: ephem.Observer) -> pd.Series:
    """
    Compute solar depression angle for every row in df.
    df must have 'tstamp' as UTC-aware timestamps.
    """
    depressions = []
    for ts in df["tstamp"]:
        dep = _solar_depression(ts.to_pydatetime(), obs)
        depressions.append(dep)
    return pd.Series(depressions, index=df.index)


def _find_inflection(
    df_window: pd.DataFrame,
    direction: str,  # "fajr" (mag drops) or "isha" (mag rises)
) -> Optional[tuple[datetime, float, float]]:
    """
    Find the inflection point (maximum rate of sky-brightness change) in a
    twilight window.

    Parameters
    ----------
    df_window : pd.DataFrame
        Subset of readings during the twilight window. Must have:
        'tstamp', 'msas_smooth', 'solar_dep'.
    direction : str
        "fajr" = morning (MSAS decreasing as sun rises)
        "isha" = evening (MSAS increasing as sun sets)

    Returns
    -------
    (utc_datetime, solar_depression_at_inflection, msas_at_inflection) or None
    """
    if len(df_window) < 10:
        return None

    df_w = df_window.copy().reset_index(drop=True)
    df_w = df_w.sort_values("tstamp").reset_index(drop=True)

    # Compute |dMSAS/dt| using central differences on the smoothed series
    msas = df_w["msas_smooth"].values
    dt_seconds = df_w["tstamp"].diff().dt.total_seconds().fillna(60).values

    # Use central differences; endpoints use forward/backward difference
    dmdt = np.gradient(msas, dt_seconds)

    if direction == "fajr":
        # Dawn: MSAS is decreasing (sky brightening). Look for most negative slope.
        # Restrict search to rows where MSAS is actually falling (dmdt < 0) and
        # solar depression is in the 6-20° band.
        valid_mask = (dmdt < 0) & (df_w["solar_dep"] >= ANGLE_MIN) & (df_w["solar_dep"] <= ANGLE_MAX)
        if not valid_mask.any():
            return None
        # Find the most negative derivative (steepest drop)
        idx = int(np.argmin(np.where(valid_mask, dmdt, 0)))
    else:
        # Dusk: MSAS is increasing (sky darkening). Look for most positive slope.
        valid_mask = (dmdt > 0) & (df_w["solar_dep"] >= ANGLE_MIN) & (df_w["solar_dep"] <= ANGLE_MAX)
        if not valid_mask.any():
            return None
        idx = int(np.argmax(np.where(valid_mask, dmdt, 0)))

    row = df_w.iloc[idx]
    if pd.isna(row["msas_smooth"]) or pd.isna(row["solar_dep"]):
        return None

    return (
        row["tstamp"].to_pydatetime(),
        float(row["solar_dep"]),
        float(row["msas_smooth"]),
    )


# --- Per-night processing --------------------------------------------------


def _process_night(
    df_night: pd.DataFrame,
    lat: float,
    lng: float,
    station_name: str,
    local_date: datetime.date,
    utc_offset_h: float,
    obs: ephem.Observer,
) -> list[dict]:
    """
    Extract Fajr and/or Isha records from one station night.

    df_night: rows spanning the full night (from ~2h before sunset to ~2h after
    sunrise), filtered to mag > 0, sorted by tstamp ascending.

    Returns a list of 0-2 raw sighting dicts.
    """
    if len(df_night) < MIN_DARK_ROWS:
        return []

    # Compute solar depression for all rows
    df_night = df_night.copy().reset_index(drop=True)
    df_night["solar_dep"] = _compute_solar_depression_series(df_night, obs)

    # Night baseline: median MSAS when solar depression > DARK_DEPRESSION_THRESHOLD
    dark_mask = df_night["solar_dep"] > DARK_DEPRESSION_THRESHOLD
    n_dark = dark_mask.sum()
    if n_dark < MIN_DARK_ROWS:
        log.debug("Night %s %s: only %d dark rows, skipping", station_name, local_date, n_dark)
        return []

    night_median = float(df_night.loc[dark_mask, "mag"].median())
    if night_median < MIN_DARK_MSAS:
        log.debug(
            "Night %s %s: median MSAS %.2f < threshold %.2f (light pollution), skipping",
            station_name, local_date, night_median, MIN_DARK_MSAS,
        )
        return []

    # Smooth the MSAS series to reduce single-sample noise
    df_night["msas_smooth"] = (
        df_night["mag"].rolling(SMOOTH_WINDOW, center=True, min_periods=1).median()
    )

    records: list[dict] = []

    # --- Dusk (Isha) window ---------------------------------------------------
    # Find readings where solar depression is between ANGLE_MIN and ANGLE_MAX
    # and MSAS is rising (sun setting, sky darkening).
    # Dusk precedes midnight, so take the first half of the night.
    night_mid = df_night["tstamp"].mean()
    dusk_mask = (
        (df_night["tstamp"] <= night_mid)
        & (df_night["solar_dep"] >= ANGLE_MIN - 2)
        & (df_night["solar_dep"] <= ANGLE_MAX + 2)
    )
    df_dusk = df_night[dusk_mask]

    isha_result = _find_inflection(df_dusk, "isha")
    if isha_result is not None:
        utc_dt, dep_angle, msas_val = isha_result
        if abs(night_median - msas_val) <= MSAS_INFLECTION_MAX_DROP:
            local_dt = utc_dt + timedelta(hours=utc_offset_h)
            records.append({
                "prayer": "isha",
                "date_local": local_dt.strftime("%Y-%m-%d"),
                "time_local": local_dt.strftime("%H:%M"),
                "utc_offset": utc_offset_h,
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "elevation_m": ELEVATION_DEFAULT,
                "source": SOURCE_CITATION,
                "notes": (
                    f"TESS station {station_name}; photometric inflection method; "
                    f"night median MSAS={night_median:.2f}; "
                    f"MSAS at inflection={msas_val:.2f}; "
                    f"depression={dep_angle:.2f}°; "
                    f"smoothing={SMOOTH_WINDOW}-pt median; dark rows={n_dark}"
                ),
            })
        else:
            log.debug(
                "Isha night %s %s: inflection MSAS %.2f too far from median %.2f, rejected",
                station_name, local_date, msas_val, night_median,
            )

    # --- Dawn (Fajr) window --------------------------------------------------
    dawn_mask = (
        (df_night["tstamp"] >= night_mid)
        & (df_night["solar_dep"] >= ANGLE_MIN - 2)
        & (df_night["solar_dep"] <= ANGLE_MAX + 2)
    )
    df_dawn = df_night[dawn_mask]

    fajr_result = _find_inflection(df_dawn, "fajr")
    if fajr_result is not None:
        utc_dt, dep_angle, msas_val = fajr_result
        if abs(night_median - msas_val) <= MSAS_INFLECTION_MAX_DROP:
            local_dt = utc_dt + timedelta(hours=utc_offset_h)
            records.append({
                "prayer": "fajr",
                "date_local": local_dt.strftime("%Y-%m-%d"),
                "time_local": local_dt.strftime("%H:%M"),
                "utc_offset": utc_offset_h,
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "elevation_m": ELEVATION_DEFAULT,
                "source": SOURCE_CITATION,
                "notes": (
                    f"TESS station {station_name}; photometric inflection method; "
                    f"night median MSAS={night_median:.2f}; "
                    f"MSAS at inflection={msas_val:.2f}; "
                    f"depression={dep_angle:.2f}°; "
                    f"smoothing={SMOOTH_WINDOW}-pt median; dark rows={n_dark}"
                ),
            })
        else:
            log.debug(
                "Fajr night %s %s: inflection MSAS %.2f too far from median %.2f, rejected",
                station_name, local_date, msas_val, night_median,
            )

    return records


# --- Top-level processor --------------------------------------------------


def _estimate_utc_offset(lng: float) -> float:
    """
    Estimate UTC offset from longitude (integer hours, ±12).
    This is a rough heuristic used only when a timezone database is unavailable.
    Actual local time offset may differ by up to ±2 hours from this estimate.
    """
    raw = lng / 15.0
    return round(raw)  # nearest whole hour


def process_tess_csv(
    csv_path: Path,
    station_filter: Optional[set[str]] = None,
    elevation_m: float = ELEVATION_DEFAULT,
) -> list[dict]:
    """
    Process a TESS monthly flat CSV (all stations interleaved).

    Parameters
    ----------
    csv_path : Path
        Path to CSV file with columns: name, tamb, tsky, mag, tstamp, latitude, longitude
    station_filter : set[str] or None
        If given, process only these station names (e.g. {"stars9", "stars201"}).
        If None, process all stations found in the file.
    elevation_m : float
        Station elevation in metres. Applied to all stations (TESS CSVs do not
        include elevation). Default 0 m.

    Returns
    -------
    list of raw sighting dicts (pray-calc-ml schema)
    """
    log.info("Loading TESS CSV: %s", csv_path)
    # Peek at header to determine format (early files lack lat/lng columns).
    with open(csv_path, encoding="utf-8", errors="replace") as _f:
        _header = _f.readline().strip()
    _cols = [c.strip() for c in _header.split(",")]
    _has_latlon = "latitude" in _cols and "longitude" in _cols

    if not _has_latlon:
        log.warning("File %s has no latitude/longitude columns — skipping", csv_path.name)
        return []

    # Read with explicit column names and usecols to handle rows with extra
    # comma-separated fields (e.g. station metadata embedded in lat/lng cells).
    _col_names = ["name", "tamb", "tsky", "mag", "tstamp", "latitude", "longitude"]
    df = pd.read_csv(
        csv_path,
        names=_col_names,
        header=0,
        usecols=list(range(len(_col_names))),
        on_bad_lines="skip",
        low_memory=False,
    )
    df["tstamp"] = pd.to_datetime(df["tstamp"], utc=True, errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
    df = df.dropna(subset=["tstamp", "mag", "latitude", "longitude"])
    df = df[df["mag"] > 0].copy()  # drop invalid/saturated readings

    if station_filter:
        df = df[df["name"].isin(station_filter)]

    if df.empty:
        log.warning("No valid rows found in %s", csv_path)
        return []

    stations = df["name"].unique()
    log.info("Processing %d stations in %s", len(stations), csv_path.name)

    all_records: list[dict] = []

    for station_name in sorted(stations):
        df_sta = df[df["name"] == station_name].sort_values("tstamp").reset_index(drop=True)

        # Station coordinates (constant across all rows for a fixed station)
        lat = float(df_sta["latitude"].iloc[0])
        lng = float(df_sta["longitude"].iloc[0])
        utc_offset_h = _estimate_utc_offset(lng)

        log.info(
            "Station %s: lat=%.4f lng=%.4f utc_offset=%+.0f  rows=%d",
            station_name, lat, lng, utc_offset_h, len(df_sta),
        )

        obs = _make_observer(lat, lng, elevation_m)

        # Group by calendar UTC date, then extract each night spanning date/date+1
        # Dates present in the dataset
        dates = sorted(df_sta["tstamp"].dt.date.unique())

        processed_nights: set = set()

        for local_date in dates:
            # Build local night: 12h before solar midnight to 12h after
            try:
                sol_mid = _solar_midnight_utc(local_date, lat, lng)
            except Exception as e:
                log.warning("solar_midnight failed for %s %s: %s", station_name, local_date, e)
                continue

            night_key = (station_name, local_date)
            if night_key in processed_nights:
                continue
            processed_nights.add(night_key)

            night_start = sol_mid - timedelta(hours=12)
            night_end = sol_mid + timedelta(hours=12)

            # Add timezone info for comparison
            ns = pd.Timestamp(night_start, tz="UTC")
            ne = pd.Timestamp(night_end, tz="UTC")

            df_night = df_sta[
                (df_sta["tstamp"] >= ns) & (df_sta["tstamp"] <= ne)
            ].copy()

            if len(df_night) < MIN_DARK_ROWS:
                continue

            night_records = _process_night(
                df_night, lat, lng, station_name, local_date, utc_offset_h, obs,
            )
            all_records.extend(night_records)
            if night_records:
                log.debug(
                    "Night %s %s: extracted %d records",
                    station_name, local_date, len(night_records),
                )

    log.info("Total twilight events extracted: %d", len(all_records))
    return all_records


def process_tess_station_csv(
    csv_path: Path,
    elevation_m: float = ELEVATION_DEFAULT,
) -> list[dict]:
    """
    Process a single-station TESS CSV (as produced by the extraction scripts that
    filter one station from the full monthly download).

    The file must have columns: name, tamb, tsky, mag, tstamp, latitude, longitude
    All rows are assumed to belong to the same station.
    """
    station_name = csv_path.stem.split("_")[0]  # e.g. "stars9" from "stars9_june2019.csv"
    return process_tess_csv(csv_path, station_filter={station_name}, elevation_m=elevation_m)


def process_tess_directory(
    data_dir: Path,
    pattern: str = "*.csv",
    elevation_m: float = ELEVATION_DEFAULT,
) -> list[dict]:
    """
    Process all TESS CSV files matching pattern in data_dir.

    Returns combined list of all twilight event records.
    """
    csv_files = sorted(data_dir.glob(pattern))
    if not csv_files:
        log.warning("No CSV files found in %s matching %s", data_dir, pattern)
        return []

    all_records: list[dict] = []
    for csv_path in csv_files:
        records = process_tess_csv(csv_path, elevation_m=elevation_m)
        all_records.extend(records)

    log.info("Grand total from %d files: %d twilight events", len(csv_files), len(all_records))
    return all_records


# --- CLI -------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import csv
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Extract Fajr/Isha twilight events from TESS photometer data"
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="Input CSV file(s) or directory containing TESS CSVs",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output CSV path. Defaults to stdout.",
    )
    parser.add_argument(
        "--stations",
        nargs="*",
        default=None,
        help="Station names to process (e.g. stars9 stars201). Default: all.",
    )
    parser.add_argument(
        "--elevation",
        type=float,
        default=ELEVATION_DEFAULT,
        help="Station elevation in metres (applied to all stations). Default: 0.",
    )
    args = parser.parse_args()

    station_filter = set(args.stations) if args.stations else None
    all_records: list[dict] = []

    for inp in args.input:
        p = Path(inp)
        if p.is_dir():
            records = process_tess_directory(p, elevation_m=args.elevation)
        else:
            records = process_tess_csv(p, station_filter=station_filter, elevation_m=args.elevation)
        all_records.extend(records)

    if not all_records:
        log.warning("No twilight events extracted.")
        sys.exit(0)

    fieldnames = [
        "prayer", "date_local", "time_local", "utc_offset",
        "lat", "lng", "elevation_m", "source", "notes",
    ]

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_records)
    if args.output:
        out.close()
        log.info("Wrote %d records to %s", len(all_records), args.output)
    else:
        log.info("Wrote %d records to stdout", len(all_records))
