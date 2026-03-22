"""
Process Madrid Night Sky Evolution SQM data.

Station: UCM Physics building, Madrid, Spain
Coordinates: 40.4189°N, 3.6919°W
Elevation: 650m
Timezone: Europe/Madrid (UTC+1/+2)
Format: semicolon-separated, UTC timestamps
  col0: "Time(UTC)" or "[xN] YYYY-MM-DD HH:MM:SS" (duplicate marker)
  col1: "Magnitude" MSAS value (mag/arcsec²)

Coverage: 2012-10-10 to 2020-02-05

Source: https://zenodo.org/records/4633001
DOI: 10.5281/zenodo.4633001

Note: This is single-station, ~1-minute cadence.
Low MSAS values (~16-17) suggest significant light pollution — not
ideal dark-sky readings, but the twilight transitions are valid for
extracting solar depression at MSAS inflection points.

Processing:
- Parse all rows, strip [xN] prefix, parse UTC timestamp + MSAS
- Group by calendar date
- For each night, compute solar depression for each reading
- Find morning/evening twilight window (depression 10°-20°)
- Find inflection point (max |dMSAS/dt|)
- Output one row per event
"""

import re
import datetime
import ephem
import pandas as pd
import numpy as np

LAT = 40.4189
LON = -3.6919
ELEV = 650.0

SRC_CSV = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/madrid_sqm_evol/SQM_evol.csv"
OUT_CSV = "/Volumes/X9/Sites/acamarata/pray-calc-ml/data/raw/raw_sightings/madrid_sqm_evol.csv"
SOURCE = "Madrid_SQM_evol_UCM_Zenodo4633001"

DEP_MIN = 10.0
DEP_MAX = 20.0

# Strip the [xN] duplicate marker
DUP_RE = re.compile(r"^\[x\d+\]\s*")


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


def parse_csv() -> pd.DataFrame:
    rows = []
    with open(SRC_CSV, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue  # skip header
            line = line.strip()
            if not line:
                continue
            # Strip duplicate marker
            line = DUP_RE.sub("", line)
            parts = line.split(";")
            if len(parts) < 2:
                continue
            try:
                utc_dt = datetime.datetime.strptime(parts[0].strip(), "%Y-%m-%d %H:%M:%S")
                msas = float(parts[1].strip())
                rows.append({"utc_dt": utc_dt, "msas": msas})
            except (ValueError, IndexError):
                continue

    print(f"Parsed {len(rows):,} rows from SQM_evol.csv")
    df = pd.DataFrame(rows)
    df = df.sort_values("utc_dt").reset_index(drop=True)
    return df


def find_twilight_events_for_night(night_df: pd.DataFrame) -> list:
    if len(night_df) < 5:
        return []

    df = night_df.copy()

    # Compute solar depression for each reading (expensive — do only for twilight candidates)
    # Quick pre-filter: Madrid twilight (10°-20° depression) happens roughly:
    # Evening: 19:00-22:00 UTC in winter, 19:00-23:00 UTC in summer
    # Morning: 03:00-07:00 UTC roughly
    # Filter to those hours first to reduce computation
    hours = df["utc_dt"].dt.hour
    pre_mask = ((hours >= 3) & (hours <= 8)) | ((hours >= 17) & (hours <= 23))
    twi_candidates = df[pre_mask].copy()
    if len(twi_candidates) < 5:
        return []

    depressions = []
    for _, row in twi_candidates.iterrows():
        dep = compute_solar_depression(row["utc_dt"])
        depressions.append(dep)
    twi_candidates["depression"] = depressions

    # Filter to actual twilight window
    mask = (
        (twi_candidates["depression"] >= DEP_MIN)
        & (twi_candidates["depression"] <= DEP_MAX)
        & (twi_candidates["msas"] > 8.0)  # not pure day (0) and not noise
    )
    twi = twi_candidates[mask].copy()
    if len(twi) < 4:
        return []

    twi = twi.sort_values("utc_dt").reset_index(drop=True)
    twi["dmsas"] = twi["msas"].diff()
    twi["ddep"] = twi["depression"].diff()

    events = []

    # Morning: depression decreasing (sun rising), MSAS dropping
    morning = twi[twi["ddep"] < -0.01].copy()
    # Evening: depression increasing (sun setting), MSAS rising
    evening = twi[twi["ddep"] > 0.01].copy()

    def extract_event(segment: pd.DataFrame, prayer: str, utc_off: int) -> dict | None:
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
            "lat": LAT,
            "lng": LON,
            "elevation_m": ELEV,
            "source": SOURCE,
            "notes": f"sqm_msas={peak_row['msas']:.2f},solar_dep={dep:.2f}deg,inflection_method",
        }

    # Get representative UTC offset from the reading
    sample_dt = twi.iloc[0]["utc_dt"]
    month = sample_dt.month
    utc_off = 2 if 4 <= month <= 10 else 1

    e = extract_event(morning, "fajr", utc_off)
    if e:
        events.append(e)
    e = extract_event(evening, "isha", utc_off)
    if e:
        events.append(e)

    return events


def main():
    df = parse_csv()
    if df.empty:
        print("No data parsed.")
        return

    # Add date column for grouping (use UTC date)
    df["utc_date"] = df["utc_dt"].dt.date

    all_events = []
    dates = sorted(df["utc_date"].unique())
    print(f"Processing {len(dates)} unique dates...")

    for i, date in enumerate(dates):
        night_df = df[df["utc_date"] == date].copy()
        events = find_twilight_events_for_night(night_df)
        all_events.extend(events)
        if i % 100 == 0:
            print(f"  {i}/{len(dates)} dates processed, {len(all_events)} events so far...")

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
