"""
SURFRAD processor — reads already-downloaded files in DRA/ and TBL/ dirs.
Also downloads remaining missing days.
"""

import math
import requests
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path("/Volumes/X9/Sites/acamarata/pray-calc-ml")
RAW_BSRN = BASE / "data/raw/bsrn"
RAW_SIGHTINGS = BASE / "data/raw/raw_sightings"
THRESHOLDS = [0.5, 1.0, 2.0, 5.0, 10.0]
SURFRAD_BASE = "https://gml.noaa.gov/aftp/data/radiation/surfrad"

STATIONS = {
    "dra": {"name": "Desert Rock",   "lat": 36.626,  "lon": -116.018, "dir_code": "DRA", "file_prefix": "dra"},
    "tbl": {"name": "TableMountain", "lat": 40.125,  "lon": -105.237, "dir_code": "TBL", "file_prefix": "tbl"},
}
YEARS = [2018, 2019, 2020]


def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 200:
        return True
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return False
        dest.write_bytes(r.content)
        return True
    except Exception:
        return False


def parse_surfrad_dat(fpath: Path) -> pd.DataFrame:
    lines = fpath.read_bytes().decode("utf-8", errors="replace").splitlines()
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
            dt   = datetime(yr, 1, 1, hr, mn, tzinfo=timezone.utc) + timedelta(days=jday - 1)
            records.append({
                "times_utc": dt,
                "sza":  None if zen < -900 else zen,
                "ghi":  None if ghi < -900 else max(0.0, ghi),
                "dif":  None if dif < -900 else max(0.0, dif),
            })
        except (ValueError, IndexError):
            continue
    return pd.DataFrame(records)


def extract_events(df, lat, lon, code, name, source):
    events = []
    df = df.copy()
    df["times_utc"] = pd.to_datetime(df["times_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["times_utc"]).sort_values("times_utc").reset_index(drop=True)
    df["irr"] = pd.to_numeric(df.get("dif", pd.Series(dtype=float)), errors="coerce")
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
                        and not np.isnan(sza[i]) and sza[i] > 90.0
                        and all((np.isnan(v) or v < threshold) for v in irr[max(0,i-3):i])):
                    dawn_idx = i
                    break
            dusk_idx = None
            for i in range(n-3, -1, -1):
                if (not np.isnan(irr[i]) and irr[i] >= threshold
                        and not np.isnan(sza[i]) and sza[i] > 90.0
                        and all((np.isnan(v) or v < threshold) for v in irr[i+1:min(n,i+4)])):
                    dusk_idx = i
                    break
            for idx, etype in [(dawn_idx, "dawn"), (dusk_idx, "dusk")]:
                if idx is None:
                    continue
                sza_val = float(sza[idx])
                if sza_val <= 90.0:
                    continue
                dep = round(sza_val - 90.0, 4)
                if dep < 0.3 or dep > 20.0:
                    continue
                utc_ts = pd.Timestamp(ts[idx])
                ghi_at = float(grp["ghi"].iloc[idx]) if "ghi" in grp.columns else float("nan")
                dif_at = float(grp["dif"].iloc[idx]) if "dif" in grp.columns else float("nan")
                events.append({
                    "date": str(day), "event_type": etype,
                    "utc_time": utc_ts.strftime("%H:%M:%S"),
                    "sza_deg": round(sza_val, 4),
                    "solar_depression_deg": dep,
                    "irr_wm2": round(float(irr[idx]), 2),
                    "ghi_wm2": round(ghi_at, 2) if not math.isnan(ghi_at) else None,
                    "dif_wm2": round(dif_at, 2)  if not math.isnan(dif_at) else None,
                    "threshold_wm2": threshold,
                    "lat": lat, "lon": lon,
                    "station_code": code, "station_name": name, "source": source,
                })
    return events


def main():
    print("SURFRAD Processor v2 — using cached downloads + filling gaps")
    all_events = []

    for code, meta in STATIONS.items():
        print(f"\n{meta['name']} ({code})")
        dir_code   = meta["dir_code"]
        prefix     = meta["file_prefix"]
        dest_root  = RAW_BSRN / "surfrad" / dir_code

        for year in YEARS:
            yy = str(year)[2:]
            days_in_year = 366 if calendar.isleap(year) else 365
            dest_dir = dest_root / str(year)
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Download any missing days
            missing = 0
            for doy in range(1, days_in_year + 1):
                fname = f"{prefix}{yy}{doy:03d}.dat"
                dest  = dest_dir / fname
                if dest.exists() and dest.stat().st_size > 200:
                    continue
                url = f"{SURFRAD_BASE}/{prefix}/{year}/{fname}"
                if download_file(url, dest):
                    missing += 1

            # Parse all available files
            day_dfs = []
            for fpath in sorted(dest_dir.glob(f"{prefix}{yy}*.dat")):
                day_df = parse_surfrad_dat(fpath)
                if not day_df.empty:
                    day_dfs.append(day_df)

            if not day_dfs:
                print(f"  {year}: no data files found")
                continue

            df_year = pd.concat(day_dfs, ignore_index=True)
            evts = extract_events(df_year, meta["lat"], meta["lon"],
                                  code, meta["name"], f"surfrad_{year}")
            print(f"  {year}: {len(day_dfs)} days, {len(df_year):,} records → {len(evts)} events (downloaded {missing} new files)")
            all_events.extend(evts)

    out = RAW_SIGHTINGS / "surfrad_twilight.csv"
    if all_events:
        df = pd.DataFrame(all_events).sort_values(
            ["station_code", "date", "event_type", "threshold_wm2"])
        df.to_csv(out, index=False)
        print(f"\nSaved {len(df):,} rows → {out}")

        prim = df[df["threshold_wm2"] == 1.0]
        print(f"\nSummary at 1 W/m²: {len(prim):,} events")
        for etype in ["dawn", "dusk"]:
            sub = prim[prim["event_type"] == etype]
            if not sub.empty:
                d = sub["solar_depression_deg"]
                print(f"  {etype}: {len(sub):,} | mean={d.mean():.2f}° "
                      f"p10={d.quantile(0.1):.2f}° p90={d.quantile(0.9):.2f}°")

        # Update combined file
        combined = RAW_SIGHTINGS / "bsrn_all_twilight.csv"
        if combined.exists():
            df_all = pd.read_csv(combined)
            df_all = df_all[~df_all["source"].str.startswith("surfrad", na=False)]
            df_all = pd.concat([df_all, pd.DataFrame(all_events)], ignore_index=True)
            df_all = df_all.sort_values(["station_code", "date", "event_type", "threshold_wm2"])
            df_all.to_csv(combined, index=False)
            print(f"Updated bsrn_all_twilight.csv → {len(df_all):,} total rows")
    else:
        print("No events.")

    print("\nDone.")


if __name__ == "__main__":
    main()
