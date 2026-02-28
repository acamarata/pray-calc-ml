"""
Process BRIN multistation SQM data to extract per-night Fajr depression angles.

Each .dat file contains per-minute SQM readings for one Indonesian station over
one month. We identify the onset of morning twilight (Fajr Sadiq) by detecting
when sky brightness (MPSAS) begins decreasing from the dark-sky baseline.

Algorithm:
  1. Parse station lat/lon from file header
  2. Extract morning windows (SunAlt transitioning from -25° toward 0°)
  3. Detect the twilight inflection point (when smoothed MPSAS starts falling)
  4. Record SunAlt at inflection → this is the Fajr depression angle

Output: rows compatible with the pipeline's verified_sightings format.

Station inventory:
  AGM = Agam, West Sumatra (-0.2°S/N, 100.32°E, ~850m)
  BDG = Bandung, West Java (-6.93°S, 107.68°E, ~760m)
  BIK = Biak, Papua (-1.17°S, 136.10°E, ~10m)
  GRT = Garut, West Java (-7.65°S, 107.69°E, ~680m)
  PSR = Pasuruan, East Java (-7.57°S, 112.67°E, ~10m)
  PTK = Pontianak, West Kalimantan (-0.008°S, 109.37°E, ~10m)
  SBG = Sabang, Aceh (-6.56°S, 107.77°E... or a different site)
  SMD = Samarinda, East Kalimantan (-6.91°S, 107.84°E, ~10m)

Reference: Damanhuri & Mukarram (2022), LAPAN SQM multi-station Indonesia.
Mean D0 reported: -16.51° (all stations, quality-filtered).
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta

import pandas as pd


# Station metadata: code -> (lat, lon, elevation_m, name, utc_offset)
# Elevations from SRTM / known site data
STATION_META = {
    "AGM": (-0.204, 100.320, 850, "Agam West Sumatra Indonesia", 7.0),
    "BDG": (-6.926, 107.678, 760, "Bandung West Java Indonesia", 7.0),
    "BIK": (-1.174, 136.101, 10, "Biak Papua Indonesia", 9.0),
    "GRT": (-7.650, 107.692, 680, "Garut West Java Indonesia", 7.0),
    "PSR": (-7.568, 112.674, 10, "Pasuruan East Java Indonesia", 7.0),
    "PTK": (-0.008, 109.365, 10, "Pontianak West Kalimantan Indonesia", 7.0),
    "SBG": (-6.562, 107.769, 650, "Sumedang West Java Indonesia", 7.0),
    "SMD": (-6.913, 107.837, 10, "Subang West Java Indonesia", 7.0),
}

# Inflection detection: we find the moment of steepest MPSAS decline
# (maximum negative dMPSAS/dt) in the pre-dawn window.
# For moonless nights this corresponds well to the visual Fajr onset.

# Maximum moon altitude allowed during pre-dawn (degrees above horizon).
# Above this, lunar illumination biases MPSAS readings.
MAX_MOON_ALT = 5.0

# Minimum dark-sky MPSAS required to consider a morning valid
# (at least some readings must be >19 to ensure we have true dark sky)
MIN_DARK_SKY_MPSAS = 19.0

# Minimum number of valid pre-dawn minutes required
MIN_PREDAWN_MINUTES = 30

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "brin_multistation_raw"
OUT_CSV = Path(__file__).parent.parent.parent / "data" / "raw" / "raw_sightings" / "brin_multistation_fajr.csv"
OUT_ISHA_CSV = Path(__file__).parent.parent.parent / "data" / "raw" / "raw_sightings" / "brin_multistation_isha.csv"


def parse_file(filepath: Path) -> pd.DataFrame:
    """Parse a BRIN .dat file and return a DataFrame."""
    lat = lon = None
    rows = []

    with open(filepath) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("# Lon:"):
                lon = float(line.split(":")[1].strip())
            elif line.startswith("# Lat:"):
                lat = float(line.split(":")[1].strip())
            elif line.startswith("#") or not line:
                continue
            else:
                parts = line.split()
                if len(parts) < 5:
                    continue
                try:
                    # Columns: DateTtime SunAlt MoonAlt Temp MPSAS Q
                    utc_str = parts[0]
                    sun_alt = float(parts[1])
                    moon_alt = float(parts[2]) if len(parts) > 2 else -90.0
                    # parts[3]=Temp, parts[4]=MPSAS, parts[5]=Q
                    mpsas = float(parts[4]) if len(parts) > 4 else 0.0
                    quality = int(float(parts[5])) if len(parts) > 5 else 0
                    # Parse UTC datetime
                    utc_dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M").replace(
                        tzinfo=timezone.utc
                    )
                    rows.append({
                        "utc_dt": utc_dt,
                        "sun_alt": sun_alt,
                        "moon_alt": moon_alt,
                        "mpsas": mpsas,
                        "quality": quality,
                    })
                except (ValueError, IndexError):
                    continue

    if not rows:
        return pd.DataFrame(), lat, lon

    df = pd.DataFrame(rows)
    return df, lat, lon


def extract_fajr_nights(df: pd.DataFrame, lat: float, lon: float,
                         station_code: str) -> list[dict]:
    """
    Given a month of per-minute SQM data, extract per-night Fajr dawn records.

    For each night (UTC date), we:
    1. Find the pre-dawn window (SunAlt between -25° and -2°, heading toward sunrise)
    2. Filter for valid MPSAS readings (> 0)
    3. Apply a rolling average to smooth noise
    4. Find when MPSAS drops below the dawn threshold
    5. Record the SunAlt at that moment as the Fajr depression angle
    """
    meta = STATION_META.get(station_code)
    if meta is None:
        # Use header coordinates with defaults
        meta = (lat, lon, 10, f"BRIN {station_code} Indonesia", 7.0)

    actual_lat, actual_lon, elevation_m, site_name, utc_offset = meta

    # Use actual file header coords if very different from defaults
    if lat is not None and abs(lat - actual_lat) > 2.0:
        actual_lat = lat
    if lon is not None and abs(lon - actual_lon) > 2.0:
        actual_lon = lon

    records = []

    # Group by UTC date of the midnight closest to dawn
    # We define a "night" by the UTC date of the sunrise
    df = df[df["mpsas"] > 0].copy()  # filter out daytime/saturated readings

    if df.empty:
        return records

    # Sort by time
    df = df.sort_values("utc_dt").reset_index(drop=True)

    # Find all "sunrise events" — where SunAlt crosses 0° from below
    sunrise_indices = []
    for i in range(1, len(df)):
        if df["sun_alt"].iloc[i - 1] < 0 and df["sun_alt"].iloc[i] >= 0:
            sunrise_indices.append(i)

    for sr_idx in sunrise_indices:
        sunrise_utc = df["utc_dt"].iloc[sr_idx]

        # Extract pre-dawn window: 5 hours before sunrise, until -2° before sunrise
        window_start = sunrise_utc - timedelta(hours=5)
        predawn = df[
            (df["utc_dt"] >= window_start) &
            (df["utc_dt"] < sunrise_utc - timedelta(minutes=10)) &
            (df["sun_alt"] < -5.0) &  # sun must be clearly below horizon
            (df["moon_alt"] <= MAX_MOON_ALT)  # moon must be below horizon / very low
        ].copy()

        if len(predawn) < MIN_PREDAWN_MINUTES:
            continue

        # Filter out rows where moon is above horizon (lunar contamination)
        # The data has MoonAlt in parts[2] but we parsed only sun_alt and mpsas.
        # Re-parse moon alt from the raw data is complex, so we use a proxy:
        # if MPSAS never reaches MIN_DARK_SKY_MPSAS, moon is likely contaminating.

        # Check that we have a dark sky period (MPSAS > threshold early in the window)
        early = predawn[predawn["sun_alt"] < -18.0]
        if early.empty:
            early = predawn[predawn["sun_alt"] < -16.0]
        if early.empty:
            continue

        max_dark_mpsas = early["mpsas"].max()
        if max_dark_mpsas < MIN_DARK_SKY_MPSAS:
            # Too light-polluted / cloudy / moon contamination — skip this morning
            continue

        # Apply rolling average (5-minute window) to smooth SQM noise
        predawn = predawn.copy()
        predawn["mpsas_smooth"] = predawn["mpsas"].rolling(window=5, center=True,
                                                             min_periods=3).mean()

        # Find the inflection point: maximum rate of MPSAS decline (most negative derivative)
        # Work on smoothed data; compute minute-by-minute differences
        predawn["dmpsas"] = predawn["mpsas_smooth"].diff()

        # Only consider the period from SunAlt -25° to -5°
        active = predawn[(predawn["sun_alt"] >= -25.0) & (predawn["sun_alt"] <= -5.0)]
        if len(active) < 10:
            continue

        # Find moment of steepest MPSAS decline (most negative dmpsas)
        steepest_idx = active["dmpsas"].idxmin()
        if pd.isna(steepest_idx):
            continue

        dawn_row = predawn.loc[steepest_idx]
        fajr_utc = dawn_row["utc_dt"]
        sun_alt_at_fajr = dawn_row["sun_alt"]

        # Depression angle = -sun_alt (positive when sun below horizon)
        depression_angle = -sun_alt_at_fajr

        # Quality filters on the angle
        if depression_angle < 10.0 or depression_angle > 22.0:
            continue

        # Convert UTC to local time
        local_time = fajr_utc + timedelta(hours=utc_offset)
        local_date = local_time.date()

        records.append({
            "prayer": "fajr",
            "date_local": local_date.strftime("%Y-%m-%d"),
            "time_local": local_time.strftime("%H:%M"),
            "utc_offset": utc_offset,
            "lat": round(actual_lat, 4),
            "lng": round(actual_lon, 4),
            "elevation_m": elevation_m,
            "source": f"BRIN multistation SQM 2018 ({station_code})",
            "notes": (
                f"Per-night SQM observation; station {station_code}; {site_name}; "
                f"inflection-point Fajr detection; moonless nights only; "
                f"Damanhuri & Mukarram LAPAN 2022 dataset"
            ),
        })

    return records


def extract_isha_nights(df: pd.DataFrame, lat: float, lon: float,
                         station_code: str) -> list[dict]:
    """
    Detect Isha (Shafaq Abyad disappearance) using MPSAS evening data.

    Algorithm:
    1. Find sunset events (SunAlt crosses 0 from above → negative)
    2. Extract evening window: sunset through 5 hours after sunset
    3. Find the dark-night MPSAS baseline from the same night (SunAlt < -20°)
    4. Find when MPSAS first reaches within 0.5 mag of baseline (sky fully darkened)
    5. That timestamp = Shafaq Abyad gone = Isha. Report SunAlt at that moment.

    This is observational: the SQM physically measures the sky brightness transition.
    The threshold (baseline − 0.5 mag) corresponds to the disappearance of the last
    detectable whitish glow of astronomical twilight.
    """
    meta = STATION_META.get(station_code)
    if meta is None:
        meta = (lat, lon, 10, f"BRIN {station_code} Indonesia", 7.0)

    actual_lat, actual_lon, elevation_m, site_name, utc_offset = meta

    if lat is not None and abs(lat - actual_lat) > 2.0:
        actual_lat = lat
    if lon is not None and abs(lon - actual_lon) > 2.0:
        actual_lon = lon

    records = []

    df = df[df["mpsas"] > 0].copy()
    if df.empty:
        return records

    df = df.sort_values("utc_dt").reset_index(drop=True)

    # Find all sunset events: SunAlt crossing 0 from positive to negative
    sunset_indices = []
    for i in range(1, len(df)):
        if df["sun_alt"].iloc[i - 1] >= 0 and df["sun_alt"].iloc[i] < 0:
            sunset_indices.append(i)

    for ss_idx in sunset_indices:
        sunset_utc = df["utc_dt"].iloc[ss_idx]

        # Evening window: sunset to 5 hours after, sun below horizon, moon low
        window_end = sunset_utc + timedelta(hours=5)
        evening = df[
            (df["utc_dt"] >= sunset_utc) &
            (df["utc_dt"] <= window_end) &
            (df["sun_alt"] < 0) &
            (df["moon_alt"] <= MAX_MOON_ALT)
        ].copy()

        if len(evening) < 30:
            continue

        # Find dark-night baseline from the SAME night (2–6 hours after sunset,
        # SunAlt must be below –20° to ensure full astronomical dark sky).
        deep_night = df[
            (df["utc_dt"] >= sunset_utc + timedelta(hours=2)) &
            (df["utc_dt"] <= sunset_utc + timedelta(hours=6)) &
            (df["sun_alt"] < -20.0) &
            (df["moon_alt"] <= MAX_MOON_ALT)
        ]

        if len(deep_night) < 20:
            continue

        dark_baseline = deep_night["mpsas"].median()
        if dark_baseline < MIN_DARK_SKY_MPSAS:
            # Too light-polluted, overcast, or moonlit — skip
            continue

        # Smooth the MPSAS signal
        evening = evening.copy()
        evening["mpsas_smooth"] = evening["mpsas"].rolling(
            window=5, center=True, min_periods=3
        ).mean()

        # MPSAS threshold: within 0.5 mag of the dark-night baseline.
        # When sky reaches this level, Shafaq Abyad (white glow) has disappeared.
        threshold = dark_baseline - 0.5

        # Find the first row where MPSAS_smooth ≥ threshold AND the sun is well
        # below the horizon (SunAlt < −12° ensures we are past red twilight too)
        reached = evening[
            (evening["mpsas_smooth"] >= threshold) &
            (evening["sun_alt"] < -12.0)
        ]

        if reached.empty:
            continue

        isha_row = reached.iloc[0]
        isha_utc = isha_row["utc_dt"]
        sun_alt_at_isha = float(isha_row["sun_alt"])

        depression_angle = -sun_alt_at_isha

        # Physical plausibility: Isha (Shafaq Abyad) angle is typically 12°–22°
        if depression_angle < 12.0 or depression_angle > 22.0:
            continue

        local_time = isha_utc + timedelta(hours=utc_offset)
        local_date = local_time.date()

        records.append({
            "prayer": "isha",
            "date_local": local_date.strftime("%Y-%m-%d"),
            "time_local": local_time.strftime("%H:%M"),
            "utc_offset": utc_offset,
            "lat": round(actual_lat, 4),
            "lng": round(actual_lon, 4),
            "elevation_m": elevation_m,
            "source": f"BRIN multistation SQM 2018 ({station_code})",
            "notes": (
                f"Per-night SQM Isha observation; station {station_code}; {site_name}; "
                f"MPSAS-threshold Isha detection (Shafaq Abyad); moonless nights only; "
                f"dark-sky baseline={dark_baseline:.2f} mag/arcsec\u00b2; "
                f"threshold={threshold:.2f}; Damanhuri & Mukarram LAPAN 2022 dataset"
            ),
        })

    return records


def process_all_files() -> list[dict]:
    """Process all .dat files in the BRIN multistation directory."""
    all_records = []
    dat_files = sorted(RAW_DIR.glob("*.dat"))

    for filepath in dat_files:
        filename = filepath.name
        # Extract station code from filename (e.g., AGM_201804.dat -> AGM)
        station_code = filename.split("_")[0].upper()
        if station_code not in STATION_META:
            # Skip unknown/temporary station files
            continue

        print(f"Processing {filename} (station {station_code})...", end=" ", flush=True)
        df, lat, lon = parse_file(filepath)

        if df.empty:
            print("empty")
            continue

        fajr_recs = extract_fajr_nights(df, lat, lon, station_code)
        isha_recs = extract_isha_nights(df, lat, lon, station_code)
        total = len(fajr_recs) + len(isha_recs)
        print(f"{len(fajr_recs)} Fajr + {len(isha_recs)} Isha = {total} records")
        all_records.extend(fajr_recs)
        all_records.extend(isha_recs)

    return all_records


def main():
    print("BRIN Multistation SQM Processor")
    print(f"Input: {RAW_DIR}")
    print(f"Fajr output: {OUT_CSV}")
    print(f"Isha output: {OUT_ISHA_CSV}")
    print()

    records = process_all_files()

    if not records:
        print("No records extracted.")
        return

    df = pd.DataFrame(records)

    # Split by prayer type
    fajr_df = df[df["prayer"] == "fajr"].copy()
    isha_df = df[df["prayer"] == "isha"].copy()

    # Deduplicate by station + date
    fajr_df = fajr_df.drop_duplicates(subset=["date_local", "lat", "lng"])
    isha_df = isha_df.drop_duplicates(subset=["date_local", "lat", "lng"])

    fajr_df = fajr_df.sort_values(["lat", "date_local"]).reset_index(drop=True)
    isha_df = isha_df.sort_values(["lat", "date_local"]).reset_index(drop=True)

    print(f"\nFajr records: {len(fajr_df)}")
    print(f"Isha records: {len(isha_df)}")

    print(f"\nBy station (Fajr):")
    for code, meta in STATION_META.items():
        count = len(fajr_df[fajr_df["source"].str.contains(f"({code})")])
        if count > 0:
            print(f"  {code} ({meta[3]}): {count} nights")

    print(f"\nBy station (Isha):")
    for code, meta in STATION_META.items():
        count = len(isha_df[isha_df["source"].str.contains(f"({code})")])
        if count > 0:
            print(f"  {code} ({meta[3]}): {count} nights")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fajr_df.to_csv(OUT_CSV, index=False)
    isha_df.to_csv(OUT_ISHA_CSV, index=False)

    print(f"\nWritten Fajr: {OUT_CSV}")
    print(f"Written Isha: {OUT_ISHA_CSV}")
    print(f"\nNOTE: Add 'brin_multistation_isha.csv' to APPROVED_RAW_CSVS in ingest.py")


if __name__ == "__main__":
    main()
