"""
Process Globe at Night citizen science observation data.

Filters for twilight observations (solar depression 6°-22°) across all
available yearly CSVs (2006-2024) and computes solar depression angles
using PyEphem for each observation.

Output: data/raw/raw_sightings/globe_at_night_twilight.csv
"""

import math
import os
import sys
from datetime import datetime, timezone

import ephem
import numpy as np
import pandas as pd

RAW_DIR = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/globe_at_night"
OUT_DIR = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/raw_sightings"
OUT_FILE = os.path.join(OUT_DIR, "globe_at_night_twilight.csv")

# Solar depression angle range for twilight (degrees below horizon)
TWILIGHT_MIN = 6.0
TWILIGHT_MAX = 22.0


def solar_depression_angle(utc_dt: datetime, lat: float, lon: float) -> float:
    """
    Compute solar depression angle (degrees below horizon) at a given UTC
    datetime and geographic position.

    Returns positive values for sun below horizon, negative for above.
    """
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.elevation = 0
    obs.pressure = 0  # disable refraction for geometric angle
    obs.date = utc_dt.strftime("%Y/%m/%d %H:%M:%S")

    sun = ephem.Sun()
    sun.compute(obs)

    # sun.alt is in radians, positive = above horizon
    alt_deg = math.degrees(float(sun.alt))
    return -alt_deg  # positive = below horizon (depression angle)


def parse_ut_datetime(ut_date: str, ut_time: str):
    """
    Parse UTDate + UTTime into a UTC datetime. Returns None on failure.
    Expected formats: '2024-07-27' + '20:33' or '20:33:00'
    """
    if not ut_date or not ut_time:
        return None
    ut_date = str(ut_date).strip()
    ut_time = str(ut_time).strip()
    if not ut_date or not ut_time or ut_date == "nan" or ut_time == "nan":
        return None
    try:
        # Normalize time to HH:MM
        parts = ut_time.split(":")
        if len(parts) < 2:
            return None
        hh = int(parts[0])
        mm = int(parts[1])
        ss = int(parts[2]) if len(parts) > 2 else 0
        date_parts = ut_date.split("-")
        if len(date_parts) != 3:
            return None
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        return datetime(year, month, day, hh, mm, ss, tzinfo=timezone.utc)
    except (ValueError, IndexError):
        return None


def load_year(csv_path: str) -> pd.DataFrame:
    """Load a single yearly CSV, returning a cleaned DataFrame."""
    try:
        df = pd.read_csv(csv_path, dtype=str, low_memory=False)
    except Exception as e:
        print(f"  ERROR reading {csv_path}: {e}", file=sys.stderr)
        return pd.DataFrame()

    # Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    required = {"Latitude", "Longitude", "UTDate", "UTTime"}
    if not required.issubset(set(df.columns)):
        print(
            f"  SKIP {os.path.basename(csv_path)}: missing columns {required - set(df.columns)}",
            file=sys.stderr,
        )
        return pd.DataFrame()

    return df


def process_file(csv_path: str) -> pd.DataFrame:
    """
    Load one yearly CSV, filter for twilight observations, compute solar
    depression angles. Returns a DataFrame of twilight rows.
    """
    year = os.path.basename(csv_path).replace("GaN", "").replace(".csv", "")
    print(f"Processing {year}...")

    df = load_year(csv_path)
    if df.empty:
        return pd.DataFrame()

    total_rows = len(df)

    # Drop rows missing lat/lng or UT time
    df = df.dropna(subset=["Latitude", "Longitude", "UTDate", "UTTime"])
    df = df[
        (df["Latitude"] != "") & (df["Longitude"] != "") &
        (df["UTDate"] != "") & (df["UTTime"] != "")
    ]

    # Convert lat/lng
    try:
        df["lat"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["lng"] = pd.to_numeric(df["Longitude"], errors="coerce")
    except Exception:
        return pd.DataFrame()

    df = df.dropna(subset=["lat", "lng"])
    df = df[(df["lat"].between(-90, 90)) & (df["lng"].between(-180, 180))]

    # Parse UTC datetime
    df["utc_dt"] = df.apply(
        lambda r: parse_ut_datetime(r["UTDate"], r["UTTime"]), axis=1
    )
    df = df[df["utc_dt"].notna()]

    after_parse = len(df)

    # Compute solar depression angle for each row
    # This is the slow step — vectorized via apply
    def compute_depression(row):
        try:
            return solar_depression_angle(row["utc_dt"], row["lat"], row["lng"])
        except Exception:
            return float("nan")

    df["solar_depression_deg"] = df.apply(compute_depression, axis=1)
    df = df[df["solar_depression_deg"].notna()]

    # Filter: twilight range 6°-22° below horizon
    twilight = df[
        (df["solar_depression_deg"] >= TWILIGHT_MIN) &
        (df["solar_depression_deg"] <= TWILIGHT_MAX)
    ].copy()

    # Classify as Fajr (morning) or Isha (evening)
    # Morning twilight: sun is rising (hour < 12 UTC, roughly)
    # More precisely: check if UTTime hour is in AM vs PM relative to solar noon
    # We use a simple heuristic: if the sun is below horizon and time is before noon UTC = Fajr
    # For accuracy, use local hour from UTTime adjusted by longitude
    def classify_twilight(row):
        # Approximate solar time: UTC + (lng / 15) hours
        solar_hour = row["utc_dt"].hour + row["lng"] / 15.0
        solar_hour = solar_hour % 24
        # Morning if between 0-14 (captures pre-sunrise in all timezones)
        return "fajr" if solar_hour < 14 else "isha"

    twilight["twilight_type"] = twilight.apply(classify_twilight, axis=1)

    # Build output columns
    sqm_col = "SQMReading" if "SQMReading" in twilight.columns else None
    limiting_mag_col = "LimitingMag" if "LimitingMag" in twilight.columns else None
    cloud_col = "CloudCover" if "CloudCover" in twilight.columns else None
    country_col = "Country" if "Country" in twilight.columns else None
    elevation_col = "Elevation(m)" if "Elevation(m)" in twilight.columns else None

    out = pd.DataFrame({
        "source": "globe_at_night",
        "year": year,
        "id": twilight.get("ID", ""),
        "utc_datetime": twilight["utc_dt"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lat": twilight["lat"],
        "lng": twilight["lng"],
        "elevation_m": twilight[elevation_col].replace("", np.nan) if elevation_col else np.nan,
        "solar_depression_deg": twilight["solar_depression_deg"].round(4),
        "twilight_type": twilight["twilight_type"],
        "sqm_reading": twilight[sqm_col].replace("", np.nan) if sqm_col else np.nan,
        "limiting_mag": twilight[limiting_mag_col].replace("", np.nan) if limiting_mag_col else np.nan,
        "cloud_cover": twilight[cloud_col] if cloud_col else "",
        "country": twilight[country_col] if country_col else "",
    })

    n_twilight = len(out)
    n_fajr = (out["twilight_type"] == "fajr").sum()
    n_isha = (out["twilight_type"] == "isha").sum()

    print(
        f"  {year}: {total_rows} rows → {after_parse} with valid UT → "
        f"{n_twilight} twilight ({n_fajr} fajr, {n_isha} isha)"
    )

    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    years = list(range(2006, 2025))
    all_results = []

    for year in years:
        csv_path = os.path.join(RAW_DIR, f"GaN{year}.csv")
        if not os.path.exists(csv_path):
            print(f"Missing: {csv_path}", file=sys.stderr)
            continue
        result = process_file(csv_path)
        if not result.empty:
            all_results.append(result)

    if not all_results:
        print("No twilight observations found.", file=sys.stderr)
        sys.exit(1)

    combined = pd.concat(all_results, ignore_index=True)

    # Sort by UTC datetime
    combined = combined.sort_values("utc_datetime")

    combined.to_csv(OUT_FILE, index=False)

    total = len(combined)
    fajr = (combined["twilight_type"] == "fajr").sum()
    isha = (combined["twilight_type"] == "isha").sum()
    with_sqm = combined["sqm_reading"].notna().sum()

    print()
    print("=" * 60)
    print(f"Output: {OUT_FILE}")
    print(f"Total twilight observations: {total:,}")
    print(f"  Fajr (morning):  {fajr:,}")
    print(f"  Isha (evening):  {isha:,}")
    print(f"  With SQM:        {with_sqm:,}")
    print()
    print("Depression angle distribution:")
    bins = [6, 8, 10, 12, 14, 16, 18, 20, 22]
    for i in range(len(bins) - 1):
        n = ((combined["solar_depression_deg"] >= bins[i]) &
             (combined["solar_depression_deg"] < bins[i + 1])).sum()
        print(f"  {bins[i]:2d}°-{bins[i+1]:2d}°: {n:,}")
    print()
    print("Countries (top 10):")
    top_countries = combined["country"].value_counts().head(10)
    for country, count in top_countries.items():
        print(f"  {country}: {count:,}")


if __name__ == "__main__":
    main()
