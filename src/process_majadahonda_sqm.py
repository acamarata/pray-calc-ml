"""
Process Majadahonda SQM 2019 tesstractor data.

Station: Majadahonda, Madrid, Spain
Coordinates: 40.469°N, 3.863°W
Elevation: ~700m (Majadahonda suburb, 700m asl approx)
Timezone: Europe/Madrid (UTC+1/+2)
Format: ;-separated
  col0: UTC timestamp (ISO 8601)
  col1: local timestamp
  col2: integration time (99.0 = 5 min)
  col3: temperature °C
  col4: frequency Hz
  col5: MSAS magnitude (mag/arcsec²) — 0.00 means daylight/overexposed
  col6: calibration MSAS

Source: https://zenodo.org/records/5709962
DOI: 10.5281/zenodo.5709962

Processing:
- Parse all .dat files (5-minute cadence, tesstractor format)
- For each night, compute solar depression angle per reading using PyEphem
- Find morning twilight window: depression 10°-20°, MSAS dropping (sky brightening)
- Find evening twilight window: depression 10°-20°, MSAS rising (sky darkening)
- Extract inflection point (maximum |d(MSAS)/dt|) as the "twilight event"
- Output one row per event
"""

import os
import re
import datetime
import ephem
import pandas as pd
import numpy as np

LAT = 40.469
LON = -3.863
ELEV = 700.0
UTC_OFFSET_WINTER = 1  # CET
UTC_OFFSET_SUMMER = 2  # CEST

DAT_DIR = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/majadahonda_sqm_2019/tesstractor"
OUT_CSV = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/raw_sightings/majadahonda_2019_sqm.csv"
SOURCE = "Majadahonda_SQM_2019_Zenodo5709962"

DEP_MIN = 10.0
DEP_MAX = 20.0


def compute_solar_depression(utc_dt: datetime.datetime) -> float:
    obs = ephem.Observer()
    obs.lat = str(LAT)
    obs.lon = str(LON)
    obs.elev = ELEV
    obs.pressure = 0
    obs.epoch = ephem.J2000
    obs.date = utc_dt.strftime("%Y/%m/%d %H:%M:%S")
    sun = ephem.Sun()
    sun.compute(obs)
    alt_deg = float(sun.alt) * 180.0 / ephem.pi
    return -alt_deg


def parse_dat_file(fpath: str) -> pd.DataFrame:
    rows = []
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(";")
            if len(parts) < 7:
                continue
            try:
                utc_str = parts[0]
                msas_raw = float(parts[6])
                # Remove sub-second part for parsing
                utc_str_clean = re.sub(r"\.\d+$", "", utc_str)
                utc_dt = datetime.datetime.strptime(utc_str_clean, "%Y-%m-%dT%H:%M:%S")
                rows.append({"utc_dt": utc_dt, "msas": msas_raw})
            except (ValueError, IndexError):
                continue
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df.sort_values("utc_dt").reset_index(drop=True)
    return df


def find_twilight_events(df: pd.DataFrame) -> list:
    """
    For a night's data, find morning and evening twilight inflection points.
    Returns list of dicts with event details.
    """
    if df.empty:
        return []

    events = []

    # Compute solar depression for each row
    depressions = []
    for _, row in df.iterrows():
        dep = compute_solar_depression(row["utc_dt"])
        depressions.append(dep)
    df = df.copy()
    df["depression"] = depressions

    # Filter to twilight window only (valid MSAS > 5, depression in range)
    mask = (
        (df["depression"] >= DEP_MIN)
        & (df["depression"] <= DEP_MAX)
        & (df["msas"] > 5.0)
    )
    twi = df[mask].copy()
    if len(twi) < 4:
        return []

    # Compute rate of change of MSAS
    twi = twi.sort_values("utc_dt").reset_index(drop=True)
    twi["dmsas"] = twi["msas"].diff()

    # Separate morning (depression decreasing over time = sun rising)
    # and evening (depression increasing over time = sun setting)
    twi["ddep"] = twi["depression"].diff()

    # Morning: depression decreasing (sun rising), MSAS dropping (sky brightening)
    morning = twi[twi["ddep"] < 0].copy()
    evening = twi[twi["ddep"] > 0].copy()

    def extract_event(segment: pd.DataFrame, prayer: str) -> dict | None:
        if len(segment) < 3:
            return None
        # Find max absolute rate of change
        segment = segment.copy()
        segment["abs_dmsas"] = segment["dmsas"].abs()
        peak_idx = segment["abs_dmsas"].idxmax()
        peak_row = segment.loc[peak_idx]

        utc_dt = peak_row["utc_dt"]
        depression = peak_row["depression"]
        date_local = utc_dt.date()

        # Estimate local time offset (rough: Spain UTC+1 winter, +2 summer)
        month = utc_dt.month
        utc_off = UTC_OFFSET_SUMMER if 4 <= month <= 10 else UTC_OFFSET_WINTER
        local_dt = utc_dt + datetime.timedelta(hours=utc_off)

        return {
            "prayer": prayer,
            "date_local": local_dt.strftime("%Y-%m-%d"),
            "time_local": local_dt.strftime("%H:%M:%S"),
            "utc_offset": utc_off,
            "lat": LAT,
            "lng": LON,
            "elevation_m": ELEV,
            "source": SOURCE,
            "notes": f"sqm_msas={peak_row['msas']:.2f},solar_dep={depression:.2f}deg,inflection_method",
        }

    e = extract_event(morning, "fajr")
    if e:
        events.append(e)
    e = extract_event(evening, "isha")
    if e:
        events.append(e)

    return events


def main():
    all_events = []
    dat_files = sorted(
        f for f in os.listdir(DAT_DIR) if f.endswith(".dat")
    )
    print(f"Processing {len(dat_files)} .dat files...")

    for fname in dat_files:
        fpath = os.path.join(DAT_DIR, fname)
        df = parse_dat_file(fpath)
        if df.empty:
            continue
        events = find_twilight_events(df)
        all_events.extend(events)
        if events:
            print(f"  {fname}: {len(events)} events")

    if not all_events:
        print("No events found.")
        return

    out_df = pd.DataFrame(all_events, columns=[
        "prayer", "date_local", "time_local", "utc_offset",
        "lat", "lng", "elevation_m", "source", "notes"
    ])
    out_df = out_df.sort_values(["date_local", "prayer"]).reset_index(drop=True)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"\nWrote {len(out_df)} rows to {OUT_CSV}")
    print(out_df["prayer"].value_counts().to_string())


if __name__ == "__main__":
    main()
