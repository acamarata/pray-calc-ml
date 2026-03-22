"""
Process Galician Night Sky Network data.

Dataset: 14 SQM stations across Galicia, northwest Spain
Time period: 2015 full year (plus some 2016)
Cadence: 1 minute
Format: space-separated text
  col0: day col1: month col2: year col3: hour col4: minute col5: second (UTC)
  col6: sky brightness (mag/arcsec²) — 0.00 means invalid/daytime

Station coordinates (MeteoGalicia weather network, ~42-43°N, 7-9°W):
  Verified via solar angle cross-check against known dusk readings.

Source: https://zenodo.org/records/4977265
DOI: 10.5281/zenodo.4977265
Original Dryad DOI: 10.5061/dryad.kv072

Processing:
- Parse each station txt file
- For each night, compute solar depression angle per reading using PyEphem
- Apply calibration offset from Offsets.txt
- Find morning/evening twilight window: depression 10°-20°, valid MSAS
- Extract inflection point (max |d(MSAS)/dt|)
- Output one row per event across all 14 stations
"""

import os
import re
import datetime
import ephem
import pandas as pd
import numpy as np

GALICIA_DIR = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/galicia_night_sky"
OUT_CSV = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/raw_sightings/galicia_sqm_2015.csv"
SOURCE = "Galicia_SQM_Network_Zenodo4977265"

DEP_MIN = 10.0
DEP_MAX = 20.0

# Station coordinates: (lat, lon, elevation_m, display_name)
# Coordinates verified against solar angle check (MeteoGalicia network stations)
STATIONS = {
    "01_Lardeira":   (42.7561, -7.8578, 1119, "Lardeira"),
    "02_Cebreiro":   (42.7075, -7.0369, 1300, "O_Cebreiro"),
    "03_Guisamo":    (43.2742, -8.1747,  216, "Guisamo"),
    "04_Areeiro":    (42.4528, -7.6853, 1498, "Areeiro"),
    "05_Manzaneda":  (42.2375, -7.2803, 1453, "Manzaneda"),
    "06_Xares":      (42.1000, -7.0667,  900, "Xares"),
    "07_PortoiVigo": (42.2667, -8.7500,   50, "Portoi_Vigo"),
    "08_Fontaneira": (43.4928, -7.2447,  694, "Fontaneira"),
    "09_Santiago":   (42.8728, -8.5453,  370, "Santiago"),
    "10_Labrada":    (43.4219, -7.5342,  648, "Labrada"),
    "11_Cies":       (42.2303, -8.9017,   52, "Islas_Cies"),
    "12_Paramos":    (42.1000, -8.6167,  400, "Paramos"),
    "13_Ons":        (42.3833, -8.9333,   40, "Isla_Ons"),
    "14_Salvora":    (42.4667, -9.0167,   25, "Isla_Salvora"),
}

# Calibration offsets from Offsets.txt (subtract from raw reading)
OFFSETS = {
    "01_Lardeira":    0.0173,
    "02_Cebreiro":   -0.0024,
    "03_Guisamo":     0.0071,
    "04_Areeiro":    -0.0587,
    "05_Manzaneda":  -0.0059,
    "06_Xares":       0.0642,
    "07_PortoiVigo": -0.0087,
    "08_Fontaneira":  0.0366,
    "09_Santiago":   -0.0017,
    "10_Labrada":     0.0315,
    "11_Cies":        0.0585,
    "12_Paramos":    -0.0080,
    "13_Ons":         0.0227,
    "14_Salvora":    -0.0675,
}


def compute_solar_depression(lat: float, lon: float, elev: float,
                              utc_dt: datetime.datetime) -> float:
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.elev = elev
    obs.pressure = 0
    obs.epoch = ephem.J2000
    obs.date = utc_dt.strftime("%Y/%m/%d %H:%M:%S")
    sun = ephem.Sun()
    sun.compute(obs)
    alt_deg = float(sun.alt) * 180.0 / ephem.pi
    return -alt_deg


def parse_station_file(fpath: str, offset: float) -> pd.DataFrame:
    rows = []
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 7:
                continue
            try:
                day, mon, yr = int(parts[0]), int(parts[1]), int(parts[2])
                hr, mi, se = int(parts[3]), int(parts[4]), int(parts[5])
                msas_raw = float(parts[6])
            except (ValueError, IndexError):
                continue
            if msas_raw <= 0.0:
                continue  # daytime/invalid
            try:
                utc_dt = datetime.datetime(yr, mon, day, hr, mi, se)
            except ValueError:
                continue
            msas_cal = msas_raw - offset
            rows.append({"utc_dt": utc_dt, "msas": msas_cal})

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df.sort_values("utc_dt").reset_index(drop=True)
    return df


def find_twilight_events_for_night(night_df: pd.DataFrame,
                                   lat: float, lon: float, elev: float,
                                   station_name: str) -> list:
    if len(night_df) < 5:
        return []

    # Pre-filter to likely twilight hours (UTC)
    hours = night_df["utc_dt"].dt.hour
    # Galicia ~42°N: morning twilight UTC ~06:00-08:30, evening ~17:30-20:00
    pre_mask = ((hours >= 5) & (hours <= 9)) | ((hours >= 16) & (hours <= 21))
    candidates = night_df[pre_mask].copy()
    if len(candidates) < 5:
        return []

    depressions = [compute_solar_depression(lat, lon, elev, r["utc_dt"])
                   for _, r in candidates.iterrows()]
    candidates = candidates.copy()
    candidates["depression"] = depressions

    mask = (
        (candidates["depression"] >= DEP_MIN)
        & (candidates["depression"] <= DEP_MAX)
        & (candidates["msas"] > 8.0)
    )
    twi = candidates[mask].copy()
    if len(twi) < 4:
        return []

    twi = twi.sort_values("utc_dt").reset_index(drop=True)
    twi["dmsas"] = twi["msas"].diff()
    twi["ddep"] = twi["depression"].diff()

    events = []

    sample_dt = twi.iloc[0]["utc_dt"]
    month = sample_dt.month
    # Spain: UTC+1 (CET) Nov-Mar, UTC+2 (CEST) Apr-Oct
    utc_off = 2 if 4 <= month <= 10 else 1

    def extract_event(segment: pd.DataFrame, prayer: str) -> dict | None:
        if len(segment) < 3:
            return None
        segment = segment.copy()
        segment["abs_dmsas"] = segment["dmsas"].abs()
        peak_idx = segment["abs_dmsas"].idxmax()
        peak_row = segment.loc[peak_idx]
        utc_dt = peak_row["utc_dt"]
        dep = peak_row["depression"]
        local_dt = utc_dt + datetime.timedelta(hours=utc_off)
        return {
            "prayer": prayer,
            "date_local": local_dt.strftime("%Y-%m-%d"),
            "time_local": local_dt.strftime("%H:%M:%S"),
            "utc_offset": utc_off,
            "lat": lat,
            "lng": lon,
            "elevation_m": elev,
            "source": SOURCE,
            "notes": (
                f"station={station_name},sqm_msas={peak_row['msas']:.2f},"
                f"solar_dep={dep:.2f}deg,inflection_method"
            ),
        }

    morning = twi[twi["ddep"] < -0.01].copy()
    evening = twi[twi["ddep"] > 0.01].copy()

    e = extract_event(morning, "fajr")
    if e:
        events.append(e)
    e = extract_event(evening, "isha")
    if e:
        events.append(e)

    return events


def main():
    all_events = []

    for station_key, (lat, lon, elev, display_name) in STATIONS.items():
        fpath = os.path.join(GALICIA_DIR, f"{station_key}.txt")
        if not os.path.exists(fpath):
            print(f"  MISSING: {fpath}")
            continue

        offset = OFFSETS.get(station_key, 0.0)
        df = parse_station_file(fpath, offset)
        if df.empty:
            print(f"  {station_key}: no valid data")
            continue

        df["utc_date"] = df["utc_dt"].dt.date
        dates = sorted(df["utc_date"].unique())
        station_events = 0

        for date in dates:
            night_df = df[df["utc_date"] == date].copy()
            events = find_twilight_events_for_night(night_df, lat, lon, elev, display_name)
            all_events.extend(events)
            station_events += len(events)

        print(f"  {station_key} ({display_name}): {len(dates)} nights, {station_events} events")

    if not all_events:
        print("No events found.")
        return

    out_df = pd.DataFrame(all_events, columns=[
        "prayer", "date_local", "time_local", "utc_offset",
        "lat", "lng", "elevation_m", "source", "notes"
    ])
    out_df = out_df.sort_values(["date_local", "lat", "prayer"]).reset_index(drop=True)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"\nWrote {len(out_df)} rows to {OUT_CSV}")
    print(out_df["prayer"].value_counts().to_string())


if __name__ == "__main__":
    main()
