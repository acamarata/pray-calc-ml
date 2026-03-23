"""
SURFRAD Downloader and Twilight Extractor — standalone.

Stations:
- dra: Desert Rock, Nevada (36.626°N, 116.018°W) — arid, excellent visibility
- tbl: Table Mountain, Colorado (40.125°N, 105.237°W) — high altitude (1689m)
- gwn: Goodwin Creek, Mississippi (34.255°N, 89.873°W) — humid subtropical

File naming: {code}{YY}{DDD}.dat
  YY  = 2-digit year
  DDD = day of year (001-366)

Column layout (SURFRAD standard format, v1):
  0: year
  1: jday (day of year)
  2: month
  3: day
  4: hour (UTC)
  5: min
  6: dt (time difference in minutes from standard time)
  7: zen (solar zenith angle, degrees)
  8: dw_solar (downwelling shortwave, W/m²) ← GHI
  9: dw_solar_sd
 10: direct (direct normal irradiance, W/m²)
 11: direct_sd
 12: diffuse (diffuse horizontal, W/m²) ← DIF
 13: diffuse_sd
 14+: other measurements

Missing value: -9999.9
"""

import re
import math
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

BASE = Path("/Volumes/X9/Sites/acamarata/pray-calc-ml")
RAW_BSRN = BASE / "data/raw/bsrn"
RAW_SIGHTINGS = BASE / "data/raw/raw_sightings"

THRESHOLDS = [0.5, 1.0, 2.0, 5.0, 10.0]
SURFRAD_BASE = "https://gml.noaa.gov/aftp/data/radiation/surfrad"

STATIONS = {
    "dra": {"name": "Desert Rock",   "lat": 36.626,  "lon": -116.018, "dir": "dra"},
    "tbl": {"name": "TableMountain", "lat": 40.125,  "lon": -105.237, "dir": "tbl"},
    "gwn": {"name": "GoodwinCreek",  "lat": 34.2547, "lon": -89.8729, "dir": "gwn"},
}


def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 500:
        return True
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return True
    except Exception:
        return False


def parse_surfrad_dat(content: bytes) -> pd.DataFrame:
    """
    Parse SURFRAD .dat file.
    Returns df with [times_utc, sza, ghi, dif].
    """
    lines = content.decode("utf-8", errors="replace").splitlines()

    # First 2 lines are headers; data starts line 2
    records = []
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 13:
            continue
        try:
            yr   = int(parts[0])
            jday = int(parts[1])
            hr   = int(parts[4])
            mn   = int(parts[5])
            zen  = float(parts[7])
            ghi  = float(parts[8])
            dif  = float(parts[12])

            dt = datetime(yr, 1, 1, hr, mn, tzinfo=timezone.utc) + timedelta(days=jday - 1)
            records.append({
                "times_utc": dt,
                "sza":       None if zen < -900 else zen,
                "ghi":       None if ghi < -900 else max(0.0, ghi),
                "dif":       None if dif < -900 else max(0.0, dif),
            })
        except (ValueError, IndexError):
            continue

    return pd.DataFrame(records)


def extract_events(df: pd.DataFrame, lat: float, lon: float,
                   station_code: str, station_name: str,
                   source: str) -> list[dict]:
    """Same logic as bsrn_process.py extract_events_from_df."""
    events = []
    df = df.copy()
    df["times_utc"] = pd.to_datetime(df["times_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["times_utc"]).sort_values("times_utc").reset_index(drop=True)

    # Use diffuse as primary signal, fall back to GHI
    df["irr"] = pd.to_numeric(df.get("dif", pd.Series()), errors="coerce")
    if "ghi" in df.columns:
        df["irr"] = df["irr"].combine_first(pd.to_numeric(df["ghi"], errors="coerce"))

    df["sza"] = pd.to_numeric(df["sza"], errors="coerce")
    df["date"] = df["times_utc"].dt.date

    for day, grp in df.groupby("date"):
        grp = grp.sort_values("times_utc").reset_index(drop=True)
        irr = grp["irr"].values
        sza = grp["sza"].values
        ts  = grp["times_utc"].values
        n   = len(irr)
        if n < 10:
            continue

        for threshold in THRESHOLDS:
            dawn_idx = None
            for i in range(2, n):
                if (not np.isnan(irr[i]) and irr[i] >= threshold
                        and not np.isnan(sza[i]) and sza[i] > 90.0):
                    prev_ok = all(
                        (np.isnan(v) or v < threshold)
                        for v in irr[max(0, i-3):i]
                    )
                    if prev_ok:
                        dawn_idx = i
                        break

            dusk_idx = None
            for i in range(n - 3, -1, -1):
                if (not np.isnan(irr[i]) and irr[i] >= threshold
                        and not np.isnan(sza[i]) and sza[i] > 90.0):
                    after_ok = all(
                        (np.isnan(v) or v < threshold)
                        for v in irr[i+1:min(n, i+4)]
                    )
                    if after_ok:
                        dusk_idx = i
                        break

            for idx, event_type in [(dawn_idx, "dawn"), (dusk_idx, "dusk")]:
                if idx is None:
                    continue
                sza_val = float(sza[idx])
                if sza_val <= 90.0:
                    continue
                dep = round(sza_val - 90.0, 4)
                if dep < 0.3 or dep > 20.0:
                    continue
                utc_ts   = pd.Timestamp(ts[idx])
                irr_val  = float(irr[idx])
                ghi_at   = float(grp["ghi"].iloc[idx]) if "ghi" in grp.columns else float("nan")
                dif_at   = float(grp["dif"].iloc[idx]) if "dif" in grp.columns else float("nan")

                events.append({
                    "date":                 str(day),
                    "event_type":           event_type,
                    "utc_time":             utc_ts.strftime("%H:%M:%S"),
                    "sza_deg":              round(sza_val, 4),
                    "solar_depression_deg": dep,
                    "irr_wm2":              round(irr_val, 2),
                    "ghi_wm2":              round(ghi_at, 2) if not math.isnan(ghi_at) else None,
                    "dif_wm2":              round(dif_at, 2)  if not math.isnan(dif_at) else None,
                    "threshold_wm2":        threshold,
                    "lat":                  lat,
                    "lon":                  lon,
                    "station_code":         station_code,
                    "station_name":         station_name,
                    "source":               source,
                })

    return events


def process_station(code: str, meta: dict, years: list[int]) -> list[dict]:
    print(f"\n  {meta['name']} ({code}) lat={meta['lat']} lon={meta['lon']}")
    dir_code = meta["dir"]
    dest_root = RAW_BSRN / "surfrad" / dir_code
    dest_root.mkdir(parents=True, exist_ok=True)

    all_events = []
    for year in years:
        yy = str(year)[2:]  # 2-digit year
        # Build list of days
        import calendar
        days_in_year = 366 if calendar.isleap(year) else 365

        dest_dir = dest_root / str(year)
        dest_dir.mkdir(parents=True, exist_ok=True)

        day_dfs = []
        success_count = 0
        for doy in range(1, days_in_year + 1):
            fname = f"{dir_code}{yy}{doy:03d}.dat"
            dest  = dest_dir / fname
            url   = f"{SURFRAD_BASE}/{dir_code}/{year}/{fname}"

            ok = download_file(url, dest)
            if not ok:
                continue
            with open(dest, "rb") as f:
                day_df = parse_surfrad_dat(f.read())
            if not day_df.empty:
                day_dfs.append(day_df)
                success_count += 1

        if not day_dfs:
            print(f"    {year}: 0 days downloaded")
            continue

        df_year = pd.concat(day_dfs, ignore_index=True)
        evts = extract_events(df_year, meta["lat"], meta["lon"],
                              code, meta["name"], f"surfrad_{year}")
        print(f"    {year}: {success_count} days → {len(evts)} twilight events "
              f"({len(df_year):,} 1-min records)")
        all_events.extend(evts)

    return all_events


def main():
    print("SURFRAD Twilight Extractor")
    years = [2018, 2019, 2020]
    print(f"Years: {years}")
    print(f"Stations: {list(STATIONS.keys())}")

    all_events = []
    for code, meta in STATIONS.items():
        evts = process_station(code, meta, years)
        all_events.extend(evts)
        print(f"  → {len(evts)} total events for {code}")

    # Save
    out = RAW_SIGHTINGS / "surfrad_twilight.csv"
    if all_events:
        df = pd.DataFrame(all_events)
        df = df.sort_values(["station_code", "date", "event_type", "threshold_wm2"])
        df.to_csv(out, index=False)
        print(f"\nSaved {len(df):,} rows → {out}")

        prim = df[df["threshold_wm2"] == 1.0]
        print(f"\nSUMMARY (1.0 W/m² threshold):")
        print(f"  Total: {len(prim):,} events")
        for evt in ["dawn", "dusk"]:
            sub = prim[prim["event_type"] == evt]
            if sub.empty:
                continue
            d = sub["solar_depression_deg"]
            print(f"  {evt.upper()}: {len(sub):,} | "
                  f"mean={d.mean():.2f}° p10={d.quantile(0.1):.2f}° "
                  f"p90={d.quantile(0.9):.2f}°")
    else:
        print("No events extracted.")

    # Merge into bsrn_all_twilight.csv
    all_file = RAW_SIGHTINGS / "bsrn_all_twilight.csv"
    if all_file.exists() and all_events:
        df_existing = pd.read_csv(all_file)
        # Remove old surfrad rows if any
        df_existing = df_existing[~df_existing["source"].str.startswith("surfrad", na=False)]
        df_new = pd.concat([df_existing, pd.DataFrame(all_events)], ignore_index=True)
        df_new = df_new.sort_values(["station_code", "date", "event_type", "threshold_wm2"])
        df_new.to_csv(all_file, index=False)
        print(f"\nUpdated bsrn_all_twilight.csv → {len(df_new):,} total rows")

    print("\nDone.")


if __name__ == "__main__":
    main()
