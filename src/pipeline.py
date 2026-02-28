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
from src.collect.precomputed_angles import load_precomputed_angles
from src.collect.verified_sightings import load_verified_sightings
from src.elevation import get_elevations_batch
from src.ingest import ingest_all_raw_csvs


PROCESSED_DIR = ROOT / "data" / "processed"


def _raw_to_df(records: list[dict]) -> pd.DataFrame:
    """Convert a list of standardized raw record dicts to a DataFrame."""
    from datetime import datetime, timedelta
    rows = []
    for r in records:
        try:
            dt_local = datetime.strptime(
                f"{r['date_local']} {r['time_local']}", "%Y-%m-%d %H:%M"
            )
            utc_offset = float(r.get("utc_offset", 0))
            utc_dt = dt_local - timedelta(hours=utc_offset)
            rows.append({
                "prayer": r["prayer"],
                "date": r["date_local"],
                "utc_dt": utc_dt,
                "lat": float(r["lat"]),
                "lng": float(r["lng"]),
                "elevation_m": float(r.get("elevation_m") or 0),
                "source": r.get("source", ""),
                "notes": r.get("notes", ""),
            })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Skipping raw record: %s — %s", r, e)
    return pd.DataFrame(rows)


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

    # Quality gate: drop records whose times were INFERRED from a published mean
    # depression angle rather than actually observed.  These are circular — the
    # back-calculated angle would reproduce the very value used to compute the
    # time, providing no independent calibration signal.
    #
    # Markers that identify non-genuine records.
    # These patterns are checked in both the notes field and the source field.
    # A record matching ANY marker is dropped before angle computation.
    #
    # RULE: Only records with directly OBSERVED times qualify. "Observed" means
    # a human observer or calibrated instrument (SQM, DSLR, photoelectric) was
    # physically present on a SPECIFIC NIGHT and recorded the ACTUAL time of
    # Fajr (subh sadiq) or Isha (shafaq al-abyad disappearance). Any time
    # computed from a known angle, aggregated from multiple nights, or taken
    # from a government timetable is CIRCULAR or INVALID.
    BAD_NOTE_MARKERS = (
        # Time-computation markers — present in notes field on synthetic records
        "time inferred",
        "aggregate representative",
        "seasonal representative",
        "representative date",
        "time computed",
        "back-calculated from",
        # Government timetable sources — calculated, not observed
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
        # Community aggregate sources — collective aggregates, not per-night
        "AFIC community observations",
        "Community observations",
        # Khalid Shaukat seasonal aggregate records added by collect agent
        # (genuine moonsighting.com sighting reports are in approved raw CSVs;
        #  these verified_sightings entries are seasonal proxies, not per-night)
        "Moonsighting.com / Khalid Shaukat",
        # Per-source exclusions of known synthetic datasets
        "Hamidi 2007-2008 Isha",
        # OIF UMSU 2017-2020 — 4 Fajr records on exact solstice/equinox dates
        # with "proposed national angle" note; seasonal proxies, not per-night.
        # (The 4 Isha records are already excluded via "Shafaq Ahmar" in notes.)
        "OIF UMSU 2017-2020",
        # Kassim Bahali 2018 Sains Malaysia 47(11) KL records — note explicitly
        # says "mean depression ~16.67° across 64 days"; solstice/equinox dates.
        "Kassim Bahali 2018, Sains Malaysia 47(11)",
        # Rashed et al. 2025 NRIAG Alexandria — 3 records on solstice/equinox
        # dates, unverified paper, no per-night observation evidence.
        "Rashed et al. 2025, NRIAG J., Alexandria",
        # Bandung/Jombang 2012 AIP — both records fall on Jun 21 (summer
        # solstice); no per-night provenance confirmed.
        "Bandung/Jombang study 2012",
        # Lubis et al. 2025 urban LP mean — 4 records where times were inferred
        # from mean D0=13° (comment: "Using D0=13.0° for representative dates"),
        # not read directly from per-night SQM curves. Note marker is the tag
        # "(urban LP mean)" in the notes field.
        "urban LP mean",
        # Saksono & Fulazzaky 2020 NRIAG — confirmed aggregate-only paper
        # (26 Jun-Jul 2015 nights → single mean D0=14° ± 0.6°; no per-night data).
        "Saksono & Fulazzaky 2020",
        # Saksono 2020 NRIAG J. same paper, alternate citation — times cannot
        # be attributed to specific per-night SQM readings in this publication.
        "Saksono 2020, NRIAG J.",
        # Hassan et al. 2016 NRIAG J. 5:9-15 — confirmed aggregate-only paper
        # (Sinai Do=14.66°, Assiut Do=13.48°; ~80 cloudless obs each, no dates).
        "Hassan et al. 2016, NRIAG J. 5:9-15",
        # Rashed et al. 2022 IJMET — paper not found in any indexed database;
        # records mix unverified "actual obs dates" with explicit aggregate ones.
        "Rashed et al. 2022, IJMET",
        # Pinem et al. 2024 JMEA — all 8 records fall on exact solstice/equinox
        # dates with mean D0 in notes; seasonal proxy pattern.
        "Pinem et al. 2024",
        # Generic note-pattern filters — catch any record whose notes contain
        # these aggregate / representative / inferred tags regardless of source.
        "equinox aggregate",   # "spring equinox aggregate", "autumn equinox aggregate (SH)", …
        "solstice aggregate",  # "summer solstice aggregate (SH)", "winter solstice aggregate", …
        "equinox inferred",    # "spring equinox inferred", "autumn equinox inferred"
        "solstice inferred",   # "summer solstice inferred", "winter solstice inferred"
        "rep date",            # "rep date May 10 2013" — short for "representative date"
        # Wrong Isha criterion — shafaq ahmar (red dusk, ~14°) is NOT the
        # criterion used in this dataset. Only shafaq al-abyad (white dusk,
        # ~17-18°) qualifies. Drop any record explicitly labeled shafaq ahmar.
        "Shafaq Ahmar",
        "shafaq ahmar",
        "red dusk twilight",
    )
    bad_notes = manual_df["notes"].apply(
        lambda n: any(m in str(n) for m in BAD_NOTE_MARKERS)
    )
    bad_source = manual_df["source"].apply(
        lambda s: any(m in str(s) for m in BAD_NOTE_MARKERS)
    )
    non_genuine = bad_notes | bad_source
    if non_genuine.any():
        dropped = manual_df[non_genuine]
        print(
            f"  Dropping {non_genuine.sum()} non-genuine record(s) "
            f"(inferred/aggregate/timetable-sourced):"
        )
        for src, cnt in dropped["source"].value_counts().items():
            print(f"    {cnt:3d}  {src}")
        manual_df = manual_df[~non_genuine].copy()
    print(f"  {len(manual_df)} genuine manually compiled records (after quality filter)")

    print("Loading ingested raw CSV sightings...")
    raw_records = ingest_all_raw_csvs(lookup_elevation=False)
    raw_df = _raw_to_df(raw_records)
    if len(raw_df) > 0:
        print(f"  {len(raw_df)} records from raw CSVs")
    else:
        print("  0 raw CSV records found")

    all_df = pd.concat([openfajr_df, manual_df, raw_df], ignore_index=True)

    # Deduplicate: same prayer + same date + same lat/lng (rounded to 3 decimal
    # places, ~111m) should produce identical angles. Keep the first occurrence
    # and log any removed records so cross-source overlaps are visible.
    all_df["_lat_r"] = all_df["lat"].round(3)
    all_df["_lng_r"] = all_df["lng"].round(3)
    dup_mask = all_df.duplicated(subset=["prayer", "date", "_lat_r", "_lng_r"], keep="first")
    if dup_mask.any():
        print(f"  Deduplicating {dup_mask.sum()} cross-source duplicate(s) "
              f"(same prayer+date+location):")
        for _, row in all_df[dup_mask].iterrows():
            print(f"    {row['prayer'].upper()} {row['date']} "
                  f"lat={row['lat']:.3f} lng={row['lng']:.3f} — {row['source']}")
        all_df = all_df[~dup_mask].copy()
    all_df = all_df.drop(columns=["_lat_r", "_lng_r"])

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

    # ── Merge pre-computed angle records ──
    # These come from sources where the solar depression angle was measured
    # directly by instrument (SQM time-series + linear fitting) rather than
    # inferred from a clock time. They bypass back-calculation entirely.
    print("Loading pre-computed angle records (SQM instrument data)...")
    precomp_df = load_precomputed_angles()
    if len(precomp_df) > 0:
        print(f"  {len(precomp_df)} pre-computed angle records")
        all_df = pd.concat([all_df, precomp_df], ignore_index=True)
    else:
        print("  0 pre-computed angle records")

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
    dates = fajr_df["date"].astype(str)
    print(f"  Date range: {dates.min()} to {dates.max()}")


if __name__ == "__main__":
    main()
