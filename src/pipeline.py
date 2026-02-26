"""
Master data pipeline.

Runs all collectors, back-calculates solar depression angles for each verified
sighting, optionally looks up missing elevations, and writes two clean CSVs:

  data/processed/fajr_angles.csv
  data/processed/isha_angles.csv

Each row represents ONE confirmed human-verified sighting.

Columns:
  date          - YYYY-MM-DD (local calendar date)
  utc_dt        - ISO 8601 UTC datetime of the sighting
  lat           - decimal degrees (north positive)
  lng           - decimal degrees (east positive)
  elevation_m   - metres above sea level
  fajr_angle    - solar depression angle at moment of Fajr sighting (degrees)
  isha_angle    - solar depression angle at moment of Isha sighting (degrees)
  day_of_year   - 1-366 (for seasonality / TOY analysis)
  source        - citation string
  notes         - observer notes

Usage:
  python -m src.pipeline [--no-elevation-lookup]

  --no-elevation-lookup : skip Open-Elevation API calls (use 0 for unknowns)
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import timezone

import pandas as pd

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.angle_calc import depression_angle
from src.collect.openfajr import fetch_openfajr
from src.collect.verified_sightings import load_verified_sightings
from src.elevation import get_elevations_batch


PROCESSED_DIR = ROOT / "data" / "processed"


def build_dataset(
    lookup_elevation: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run all collectors, compute depression angles, return (fajr_df, isha_df).
    """
    print("Loading OpenFajr Birmingham iCal feed...")
    openfajr_df = fetch_openfajr()
    print(f"  {len(openfajr_df)} Fajr records from OpenFajr")

    print("Loading manually verified sightings...")
    manual_df = load_verified_sightings()
    print(f"  {len(manual_df)} manually compiled records")

    all_df = pd.concat([openfajr_df, manual_df], ignore_index=True)

    # Elevation lookup for records with elevation_m == 0
    if lookup_elevation:
        missing_mask = all_df["elevation_m"] == 0.0
        n_missing = missing_mask.sum()
        if n_missing > 0:
            print(f"Looking up elevations for {n_missing} records...")
            locs = list(zip(
                all_df.loc[missing_mask, "lat"],
                all_df.loc[missing_mask, "lng"],
            ))
            elevations = get_elevations_batch(locs)
            all_df.loc[missing_mask, "elevation_m"] = elevations
            print(f"  Elevation lookup complete")
    else:
        print("Skipping elevation lookup (--no-elevation-lookup)")

    # Back-calculate depression angle for each sighting
    print("Computing solar depression angles...")
    angles = []
    for _, row in all_df.iterrows():
        try:
            angle = depression_angle(
                row["utc_dt"],
                row["lat"],
                row["lng"],
                row["elevation_m"],
            )
        except Exception as e:
            angle = float("nan")
        angles.append(angle)

    all_df["angle"] = angles

    # Drop records with implausible depression angles — data entry / timing errors.
    # Floor thresholds based on the full body of peer-reviewed sighting research:
    #   Fajr: no confirmed genuine sighting below 7° depression
    #   Isha: no confirmed genuine sighting below 10° depression
    # These also catch: sun-above-horizon (negative), DST clock-change artifacts,
    # and mis-estimated observation times that ended up too close to sunrise/sunset.
    FAJR_MIN_DEG = 7.0
    ISHA_MIN_DEG = 10.0

    fajr_bad = (all_df["prayer"] == "fajr") & (all_df["angle"] < FAJR_MIN_DEG)
    isha_bad  = (all_df["prayer"] == "isha") & (all_df["angle"] < ISHA_MIN_DEG)
    bad = fajr_bad | isha_bad | all_df["angle"].isna()

    if bad.any():
        print(f"  Dropping {bad.sum()} record(s) with implausible angles "
              f"(< {FAJR_MIN_DEG}° Fajr / < {ISHA_MIN_DEG}° Isha):")
        for _, row in all_df[bad].iterrows():
            print(f"    {row['prayer'].upper()} {row['date']} {row['utc_dt']} "
                  f"lat={row['lat']:.2f} angle={row['angle']:.2f}° — {row['source']}")
        all_df = all_df[~bad].copy()

    # Add seasonality feature
    all_df["day_of_year"] = all_df["utc_dt"].apply(
        lambda dt: dt.timetuple().tm_yday
    )

    # Split into Fajr and Isha datasets
    fajr_df = all_df[all_df["prayer"] == "fajr"].copy()
    isha_df  = all_df[all_df["prayer"] == "isha"].copy()

    fajr_df = fajr_df.rename(columns={"angle": "fajr_angle"})
    isha_df  = isha_df.rename(columns={"angle": "isha_angle"})

    # Final column order for ML
    fajr_cols = ["date", "utc_dt", "lat", "lng", "elevation_m",
                 "day_of_year", "fajr_angle", "source", "notes"]
    isha_cols  = ["date", "utc_dt", "lat", "lng", "elevation_m",
                  "day_of_year", "isha_angle", "source", "notes"]

    fajr_df = fajr_df[fajr_cols].sort_values(["lat", "day_of_year"])
    isha_df  = isha_df[isha_cols].sort_values(["lat", "day_of_year"])

    return fajr_df, isha_df


def main():
    parser = argparse.ArgumentParser(description="Build Fajr/Isha angle datasets")
    parser.add_argument(
        "--no-elevation-lookup",
        action="store_true",
        help="Skip Open-Elevation API calls",
    )
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    fajr_df, isha_df = build_dataset(
        lookup_elevation=not args.no_elevation_lookup,
    )

    fajr_path = PROCESSED_DIR / "fajr_angles.csv"
    isha_path  = PROCESSED_DIR / "isha_angles.csv"

    fajr_df.to_csv(fajr_path, index=False)
    isha_df.to_csv(isha_path, index=False)

    print(f"\nFajr dataset: {len(fajr_df)} records → {fajr_path}")
    print(f"Isha dataset:  {len(isha_df)} records → {isha_path}")

    print("\nFajr angle stats:")
    print(fajr_df["fajr_angle"].describe().to_string())

    print("\nIsha angle stats:")
    if len(isha_df) > 0:
        print(isha_df["isha_angle"].describe().to_string())

    print("\nFajr geographic coverage:")
    print(f"  Latitude range: {fajr_df['lat'].min():.1f}° to {fajr_df['lat'].max():.1f}°")
    print(f"  Unique locations: {len(fajr_df.groupby(['lat','lng']))}")
    print(f"  Date range: {fajr_df['date'].min()} to {fajr_df['date'].max()}")


if __name__ == "__main__":
    main()
