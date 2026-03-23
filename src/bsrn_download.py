"""
BSRN Data Downloader and Twilight Extractor

Downloads BSRN irradiance data from:
1. Zenodo 5-site dataset (quick, 58.5 MB parquet)
2. CAELUS Zenodo dataset (54 stations, prioritizing 20-45°N)

For each station-year, extracts twilight events:
- Dawn: moment GHI first exceeds threshold after midnight
- Dusk: last moment GHI exceeds threshold before midnight

Computes solar depression angle at each event.
Outputs CSV rows suitable for pray-calc fajr/isha angle analysis.
"""

import os
import sys
import math
import zipfile
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from io import BytesIO

# ── paths ────────────────────────────────────────────────────────────────────
BASE = Path("/Volumes/X9/Sites/acamarata/pray-calc-ml")
RAW_BSRN = BASE / "data/raw/bsrn"
RAW_SIGHTINGS = BASE / "data/raw/raw_sightings"
RAW_BSRN.mkdir(parents=True, exist_ok=True)
RAW_SIGHTINGS.mkdir(parents=True, exist_ok=True)

# ── thresholds ────────────────────────────────────────────────────────────────
# GHI threshold in W/m² to call "detectable irradiance"
# 0.5 W/m² ~ starlight. 1 W/m² is typical first-light threshold.
# We extract events at multiple thresholds.
THRESHOLDS = [0.5, 1.0, 2.0, 5.0, 10.0]
PRIMARY_THRESHOLD = 1.0  # used for the main sightings CSV

# ── station priority list (CAELUS dataset) ────────────────────────────────────
# Prioritize stations in 20-45°N, especially Muslim-majority/relevant regions
PRIORITY_STATIONS = {
    "sbo": {"name": "Sede Boqer",       "lat": 30.8597, "lon": 34.7794,  "country": "Israel/Negev"},
    "tam": {"name": "Tamanrasset",      "lat": 22.7903, "lon": 5.5292,   "country": "Algeria"},
    "xia": {"name": "Xianghe",          "lat": 39.754,  "lon": 116.962,  "country": "China"},
    "gur": {"name": "Gurgaon",          "lat": 28.4249, "lon": 77.156,   "country": "India"},
    "iza": {"name": "Izana",            "lat": 28.3093, "lon": -16.4993, "country": "Spain/Canary"},
    "ish": {"name": "Ishigakijima",     "lat": 24.3367, "lon": 124.1644, "country": "Japan"},
    "lln": {"name": "Lulin",            "lat": 23.4686, "lon": 120.8736, "country": "Taiwan"},
    "dra": {"name": "Desert Rock",      "lat": 36.626,  "lon": -116.018, "country": "USA/Nevada"},
    "e13": {"name": "SouthernGreatPlains","lat": 36.605, "lon": -97.485, "country": "USA/Oklahoma"},
    "tat": {"name": "Tateno",           "lat": 36.0581, "lon": 140.1258, "country": "Japan"},
    "fua": {"name": "Fukuoka",          "lat": 33.5822, "lon": 130.3764, "country": "Japan"},
    "gcr": {"name": "GoodwinCreek",     "lat": 34.2547, "lon": -89.8729, "country": "USA/Mississippi"},
    "bil": {"name": "Billings",         "lat": 36.605,  "lon": -97.516,  "country": "USA/Oklahoma"},
}

# Years available in CAELUS per station (approximate; we'll try 2007-2017)
CAELUS_YEAR_RANGE = list(range(2007, 2018))

# ── solar geometry ────────────────────────────────────────────────────────────

def solar_declination(day_of_year: int) -> float:
    """Solar declination in degrees (Spencer 1971)."""
    B = 2 * math.pi * (day_of_year - 1) / 365
    return (180 / math.pi) * (
        0.006918
        - 0.399912 * math.cos(B)
        + 0.070257 * math.sin(B)
        - 0.006758 * math.cos(2 * B)
        + 0.000907 * math.sin(2 * B)
        - 0.002697 * math.cos(3 * B)
        + 0.00148  * math.sin(3 * B)
    )


def equation_of_time_minutes(day_of_year: int) -> float:
    """Equation of time in minutes (Spencer 1971)."""
    B = 2 * math.pi * (day_of_year - 1) / 365
    return (180 / math.pi) * (
        0.000075
        + 0.001868 * math.cos(B)
        - 0.032077 * math.sin(B)
        - 0.014615 * math.cos(2 * B)
        - 0.04089  * math.sin(2 * B)
    ) * (180 / 15)  # convert to minutes


def solar_hour_angle(utc_hour_frac: float, lon_deg: float, day_of_year: int) -> float:
    """Solar hour angle in degrees at given UTC fractional hour and longitude."""
    eot = equation_of_time_minutes(day_of_year)
    # Local solar time in hours
    lst = utc_hour_frac + lon_deg / 15.0 + eot / 60.0
    # Hour angle (0 at solar noon)
    return 15.0 * (lst - 12.0)


def solar_elevation(lat_deg: float, lon_deg: float, utc_dt: datetime) -> float:
    """Solar elevation angle in degrees (positive above horizon)."""
    doy = utc_dt.timetuple().tm_yday
    utc_frac = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    decl = math.radians(solar_declination(doy))
    lat  = math.radians(lat_deg)
    ha   = math.radians(solar_hour_angle(utc_frac, lon_deg, doy))
    sin_elev = (
        math.sin(lat) * math.sin(decl)
        + math.cos(lat) * math.cos(decl) * math.cos(ha)
    )
    sin_elev = max(-1.0, min(1.0, sin_elev))
    return math.degrees(math.asin(sin_elev))


def solar_depression_angle(lat_deg: float, lon_deg: float, utc_dt: datetime) -> float:
    """Solar depression angle = negative elevation (positive below horizon)."""
    return -solar_elevation(lat_deg, lon_deg, utc_dt)


# ── download helpers ──────────────────────────────────────────────────────────

def download_file(url: str, dest: Path, label: str = "") -> bool:
    """Download a file with progress. Returns True on success."""
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {label or dest.name} already downloaded")
        return True
    try:
        print(f"  [download] {label or dest.name} ...", end=" ", flush=True)
        r = requests.get(url, timeout=120, stream=True)
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
        mb = downloaded / 1_048_576
        print(f"OK ({mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        if dest.exists():
            dest.unlink()
        return False


# ── twilight extraction ───────────────────────────────────────────────────────

def extract_twilight_events(
    df: pd.DataFrame,
    lat: float,
    lon: float,
    station_code: str,
    station_name: str,
    source: str,
    threshold: float = PRIMARY_THRESHOLD,
) -> list[dict]:
    """
    Given a dataframe with columns [timestamp, ghi] (UTC timestamps),
    extract per-day dawn and dusk events.

    Dawn: first minute where GHI >= threshold after a run of zeros
    Dusk: last minute where GHI >= threshold before a run of zeros

    Returns a list of dicts with keys:
      date, event_type, utc_time, ghi_wm2, solar_depression_deg,
      lat, lon, station_code, station_name, source, threshold_wm2
    """
    events = []

    # Ensure UTC
    if df["timestamp"].dt.tz is None:
        df = df.copy()
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    else:
        df = df.copy()
        df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")

    # Sort and drop nulls
    df = df.dropna(subset=["ghi"]).sort_values("timestamp").reset_index(drop=True)
    df["ghi"] = pd.to_numeric(df["ghi"], errors="coerce")
    df = df.dropna(subset=["ghi"])

    # Group by UTC date (using the date of the timestamp)
    df["date"] = df["timestamp"].dt.date

    for day, group in df.groupby("date"):
        group = group.sort_values("timestamp").reset_index(drop=True)
        ghi = group["ghi"].values
        ts  = group["timestamp"].values  # numpy datetime64

        # Find dawn: first index where GHI crosses threshold from below
        # We require at least 3 consecutive sub-threshold readings before the crossing
        dawn_idx = None
        for i in range(3, len(ghi)):
            if ghi[i] >= threshold and all(g < threshold for g in ghi[max(0, i-3):i]):
                dawn_idx = i
                break

        # Find dusk: last index where GHI is >= threshold followed by sub-threshold
        dusk_idx = None
        for i in range(len(ghi) - 4, -1, -1):
            if ghi[i] >= threshold and all(g < threshold for g in ghi[i+1:min(len(ghi), i+4)]):
                dusk_idx = i
                break

        for idx, event_type in [(dawn_idx, "dawn"), (dusk_idx, "dusk")]:
            if idx is None:
                continue
            ts_val = pd.Timestamp(ts[idx])
            utc_dt = ts_val.to_pydatetime().replace(tzinfo=timezone.utc)
            dep = solar_depression_angle(lat, lon, utc_dt)
            ghi_val = float(ghi[idx])

            # Only record events where sun is clearly below horizon
            # (eliminates cloudy days where GHI is suppressed during daytime)
            if dep < 0:  # sun above horizon — skip, not a real twilight event
                continue
            if dep > 25:  # sun more than 25° below — likely data noise
                continue

            events.append({
                "date":                  str(day),
                "event_type":            event_type,
                "utc_time":              utc_dt.strftime("%H:%M"),
                "ghi_wm2":               round(ghi_val, 2),
                "solar_depression_deg":  round(dep, 4),
                "lat":                   lat,
                "lon":                   lon,
                "station_code":          station_code,
                "station_name":          station_name,
                "source":                source,
                "threshold_wm2":         threshold,
            })

    return events


# ── dataset 1: BSRN 5-site parquet ───────────────────────────────────────────

FIVE_SITE_URL = "https://zenodo.org/records/10593079/files/bsrn_valid_five_sites.parquet"
FIVE_SITE_PATH = RAW_BSRN / "bsrn_valid_five_sites.parquet"

FIVE_SITE_META = {
    "mnm": {"name": "Minamitorishima", "lat": 24.2833, "lon": 153.9667},
    "asp": {"name": "Alice Springs",   "lat": -23.7984, "lon": 133.8880},
    "car": {"name": "Carpentras",      "lat": 44.0833, "lon": 5.0583},
    "bon": {"name": "Bondville",       "lat": 40.0667, "lon": -88.3667},
    "son": {"name": "Sonnblick",       "lat": 47.0542, "lon": 12.9578},
}


def process_five_site() -> list[dict]:
    """Download and process the BSRN 5-site parquet dataset."""
    print("\n=== BSRN 5-site dataset (Zenodo 10593079) ===")
    ok = download_file(FIVE_SITE_URL, FIVE_SITE_PATH, "bsrn_valid_five_sites.parquet")
    if not ok:
        print("  ERROR: could not download 5-site dataset")
        return []

    print("  Loading parquet ...", end=" ", flush=True)
    df_all = pd.read_parquet(FIVE_SITE_PATH)
    print(f"OK — {len(df_all):,} rows, columns: {list(df_all.columns)}")

    all_events = []

    # Detect timestamp column
    ts_col = None
    for c in ["timestamp", "time", "datetime", "date_time", "Timestamp", "TIME"]:
        if c in df_all.columns:
            ts_col = c
            break
    if ts_col is None:
        # Use first datetime-like column
        for c in df_all.columns:
            if pd.api.types.is_datetime64_any_dtype(df_all[c]):
                ts_col = c
                break
    if ts_col is None:
        print(f"  WARNING: cannot find timestamp column. Columns: {list(df_all.columns)[:20]}")
        return []

    # Detect GHI column
    ghi_col = None
    for c in ["ghi", "GHI", "global_horizontal_irradiance", "SWD", "swd", "global"]:
        if c in df_all.columns:
            ghi_col = c
            break
    if ghi_col is None:
        print(f"  WARNING: cannot find GHI column. Columns: {list(df_all.columns)[:20]}")
        return []

    # Detect station column
    stn_col = None
    for c in ["station", "sta", "site", "STATION"]:
        if c in df_all.columns:
            stn_col = c
            break

    print(f"  Using ts_col='{ts_col}', ghi_col='{ghi_col}', station_col='{stn_col}'")

    if stn_col:
        groups = {stn: sub for stn, sub in df_all.groupby(stn_col)}
    else:
        # Single station file — infer from filename or use first meta entry
        groups = {"unknown": df_all}

    for stn_code, sub in groups.items():
        stn_key = str(stn_code).lower()
        meta = FIVE_SITE_META.get(stn_key, None)
        if meta is None:
            # Try to find lat/lon in data
            if "latitude" in sub.columns and "longitude" in sub.columns:
                lat = float(sub["latitude"].iloc[0])
                lon = float(sub["longitude"].iloc[0])
                name = stn_key
            else:
                print(f"  SKIP {stn_key}: no metadata")
                continue
        else:
            lat, lon, name = meta["lat"], meta["lon"], meta["name"]

        work = sub[[ts_col, ghi_col]].copy()
        work.columns = ["timestamp", "ghi"]
        work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True, errors="coerce")
        work = work.dropna(subset=["timestamp"])

        print(f"  Processing {name} ({stn_key}): {len(work):,} rows ...", end=" ", flush=True)
        evts = extract_twilight_events(work, lat, lon, stn_key, name, "bsrn_5site")
        print(f"{len(evts)} events")
        all_events.extend(evts)

    return all_events


# ── dataset 2: CAELUS ZIP files ───────────────────────────────────────────────

CAELUS_BASE_URL = "https://zenodo.org/api/records/7897639/files/{filename}/content"


def caelus_filename(station_code: str, year: int) -> str:
    return f"{station_code}_bsrn_{year}.zip"


def list_caelus_available() -> dict[str, list[int]]:
    """
    Probe Zenodo API to get available files, return dict of station -> [years].
    """
    print("\n  Querying CAELUS file list from Zenodo API ...", end=" ", flush=True)
    try:
        r = requests.get("https://zenodo.org/api/records/7897639", timeout=30)
        r.raise_for_status()
        data = r.json()
        available: dict[str, list[int]] = {}
        for f in data.get("files", []):
            fname = f.get("key", "")
            if fname.endswith(".zip") and "_bsrn_" in fname:
                parts = fname.replace(".zip", "").split("_bsrn_")
                if len(parts) == 2:
                    code = parts[0]
                    try:
                        year = int(parts[1])
                        available.setdefault(code, []).append(year)
                    except ValueError:
                        pass
        print(f"found {len(available)} stations")
        return available
    except Exception as e:
        print(f"FAILED: {e}")
        return {}


def process_caelus_zip(zip_path: Path, station_code: str, meta: dict, year: int) -> list[dict]:
    """Extract parquet from ZIP, parse, return events."""
    events = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            parquet_files = [n for n in zf.namelist() if n.endswith(".parquet")]
            if not parquet_files:
                print(f"    WARNING: no parquet in {zip_path.name}")
                return []
            for pf in parquet_files:
                with zf.open(pf) as f:
                    df = pd.read_parquet(BytesIO(f.read()))

                # Detect columns
                ts_col = None
                for c in ["timestamp", "time", "datetime", "Timestamp", "TIME"]:
                    if c in df.columns:
                        ts_col = c
                        break
                if ts_col is None:
                    for c in df.columns:
                        if pd.api.types.is_datetime64_any_dtype(df[c]):
                            ts_col = c
                            break
                if ts_col is None:
                    print(f"    WARNING: no timestamp in {pf}")
                    continue

                ghi_col = None
                for c in ["ghi", "GHI", "SWD", "swd", "global_horizontal_irradiance", "global"]:
                    if c in df.columns:
                        ghi_col = c
                        break
                if ghi_col is None:
                    # Use diffuse if available
                    for c in ["dhi", "DHI", "diffuse"]:
                        if c in df.columns:
                            ghi_col = c
                            break
                if ghi_col is None:
                    print(f"    WARNING: no GHI column in {pf}. cols={list(df.columns)[:15]}")
                    continue

                work = df[[ts_col, ghi_col]].copy()
                work.columns = ["timestamp", "ghi"]
                work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True, errors="coerce")
                work = work.dropna(subset=["timestamp"])

                evts = extract_twilight_events(
                    work,
                    meta["lat"], meta["lon"],
                    station_code, meta["name"],
                    f"caelus_{year}",
                )
                events.extend(evts)

    except zipfile.BadZipFile as e:
        print(f"    ERROR: bad zip {zip_path.name}: {e}")
    except Exception as e:
        print(f"    ERROR processing {zip_path.name}: {e}")

    return events


def process_caelus(max_stations: int = 8, max_years_per_station: int = 5) -> list[dict]:
    """Download and process CAELUS priority stations."""
    print("\n=== CAELUS dataset (Zenodo 7897639) ===")
    available = list_caelus_available()

    all_events = []

    processed_count = 0
    for code, meta in PRIORITY_STATIONS.items():
        if processed_count >= max_stations:
            break

        if code not in available:
            print(f"  SKIP {code} ({meta['name']}): not in CAELUS dataset")
            continue

        years = sorted(available[code])
        years_to_use = years[:max_years_per_station]
        print(f"\n  Station: {meta['name']} ({code}) | lat={meta['lat']} lon={meta['lon']} | years: {years_to_use}")

        station_events = []
        for year in years_to_use:
            fname = caelus_filename(code, year)
            url = CAELUS_BASE_URL.format(filename=fname)
            dest = RAW_BSRN / fname

            ok = download_file(url, dest, fname)
            if not ok:
                continue

            print(f"    Processing {fname} ...", end=" ", flush=True)
            evts = process_caelus_zip(dest, code, meta, year)
            print(f"{len(evts)} events")
            station_events.extend(evts)

        print(f"  Total events for {code}: {len(station_events)}")
        all_events.extend(station_events)
        processed_count += 1

    return all_events


# ── SURFRAD download ──────────────────────────────────────────────────────────

SURFRAD_STATIONS = {
    "dra": {
        "name": "Desert Rock",
        "lat": 36.626, "lon": -116.018,
        "ftp_dir": "DRA",
    },
    "tbl": {
        "name": "Table Mountain",
        "lat": 40.125, "lon": -105.237,
        "ftp_dir": "TBL",
    },
}
SURFRAD_BASE = "https://gml.noaa.gov/aftp/data/radiation/surfrad"


def parse_surfrad_file(content: bytes, station_meta: dict) -> pd.DataFrame:
    """
    Parse SURFRAD dat file format.
    Returns dataframe with [timestamp, ghi] columns.
    """
    lines = content.decode("utf-8", errors="replace").splitlines()

    # Skip header (first line is site info, second is column header)
    # Format: year jday hour min dt zen dw_solar dw_solar_stdev ...
    records = []
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            yr   = int(parts[0])
            jday = int(parts[1])
            hr   = int(parts[2])
            mn   = int(parts[3])
            # GHI is column index 6 (dw_solar = downwelling shortwave)
            ghi_raw = float(parts[6])

            # Build datetime
            dt = datetime(yr, 1, 1, hr, mn, tzinfo=timezone.utc) + timedelta(days=jday - 1)

            # SURFRAD uses -9999 for missing
            ghi = None if ghi_raw < -900 else max(0.0, ghi_raw)
            records.append({"timestamp": dt, "ghi": ghi})
        except (ValueError, IndexError):
            continue

    return pd.DataFrame(records)


def process_surfrad(years: list[int] | None = None) -> list[dict]:
    """Download and process SURFRAD Desert Rock and Table Mountain."""
    print("\n=== SURFRAD dataset (NOAA GML FTP) ===")
    if years is None:
        years = [2018, 2019, 2020]  # 3 recent years

    all_events = []

    for code, meta in SURFRAD_STATIONS.items():
        station_dir = meta["ftp_dir"]
        print(f"\n  Station: {meta['name']} ({code}) | lat={meta['lat']} lon={meta['lon']}")

        for year in years:
            print(f"    Year {year}:")
            station_events = []

            # SURFRAD stores one file per day: DRA/YYYY/draYYYjjj.dat
            # where jjj = day of year (001-365)
            # We'll try to get the full year index
            year_dir_url = f"{SURFRAD_BASE}/{station_dir}/{year}/"
            try:
                r = requests.get(year_dir_url, timeout=30)
                if r.status_code != 200:
                    print(f"      Cannot access {year_dir_url}: {r.status_code}")
                    continue
                # Parse file listing (Apache directory index)
                import re
                files = re.findall(rf'{code.lower()}\d{{5}}\.dat', r.text)
                files = sorted(set(files))
                print(f"      Found {len(files)} daily files")

                dest_dir = RAW_BSRN / "surfrad" / station_dir / str(year)
                dest_dir.mkdir(parents=True, exist_ok=True)

                day_records = []
                for fname in files:
                    dest = dest_dir / fname
                    file_url = f"{year_dir_url}{fname}"
                    ok = download_file(file_url, dest, fname)
                    if not ok:
                        continue
                    with open(dest, "rb") as f:
                        content = f.read()
                    day_df = parse_surfrad_file(content, meta)
                    if not day_df.empty:
                        day_records.append(day_df)

                if day_records:
                    df_year = pd.concat(day_records, ignore_index=True)
                    print(f"      {len(df_year):,} 1-min records loaded", end=" ")
                    evts = extract_twilight_events(
                        df_year, meta["lat"], meta["lon"],
                        code, meta["name"], f"surfrad_{year}",
                    )
                    print(f"→ {len(evts)} twilight events")
                    station_events.extend(evts)

            except Exception as e:
                print(f"      ERROR: {e}")
                continue

        all_events.extend(station_events)

    return all_events


# ── save results ──────────────────────────────────────────────────────────────

def save_sightings(events: list[dict], filename: str) -> Path:
    """Save events list to CSV."""
    if not events:
        print(f"  WARNING: no events to save to {filename}")
        return RAW_SIGHTINGS / filename
    df = pd.DataFrame(events)
    df = df.sort_values(["station_code", "date", "event_type"]).reset_index(drop=True)
    out = RAW_SIGHTINGS / filename
    df.to_csv(out, index=False)
    print(f"  Saved {len(df)} events → {out}")
    return out


def print_summary(events: list[dict], label: str):
    if not events:
        print(f"\n{label}: no events")
        return
    df = pd.DataFrame(events)
    print(f"\n{'='*60}")
    print(f"SUMMARY: {label}")
    print(f"  Total events:    {len(df)}")
    print(f"  Dawn events:     {(df['event_type']=='dawn').sum()}")
    print(f"  Dusk events:     {(df['event_type']=='dusk').sum()}")
    print(f"  Stations:        {df['station_code'].nunique()} — {sorted(df['station_code'].unique())}")
    print(f"  Date range:      {df['date'].min()} to {df['date'].max()}")
    dep = df["solar_depression_deg"]
    print(f"  Depression angle: mean={dep.mean():.2f}° std={dep.std():.2f}° "
          f"min={dep.min():.2f}° max={dep.max():.2f}°")
    if "event_type" in df.columns:
        for evt_type in ["dawn", "dusk"]:
            sub = df[df["event_type"] == evt_type]
            if not sub.empty:
                d = sub["solar_depression_deg"]
                print(f"  {evt_type.upper()} depression: mean={d.mean():.2f}° "
                      f"p10={d.quantile(0.1):.2f}° p90={d.quantile(0.9):.2f}°")
    print(f"{'='*60}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("BSRN Twilight Extractor")
    print(f"Output dir: {RAW_SIGHTINGS}")
    print(f"Raw data:   {RAW_BSRN}")
    print(f"GHI threshold: {PRIMARY_THRESHOLD} W/m²\n")

    all_events = []

    # 1. BSRN 5-site (quick, 58.5 MB)
    five_site_events = process_five_site()
    save_sightings(five_site_events, "bsrn_5site_twilight.csv")
    print_summary(five_site_events, "BSRN 5-site dataset")
    all_events.extend(five_site_events)

    # 2. CAELUS (priority stations, up to 8 stations × 5 years)
    caelus_events = process_caelus(max_stations=8, max_years_per_station=5)
    save_sightings(caelus_events, "bsrn_caelus_twilight.csv")
    print_summary(caelus_events, "CAELUS dataset")
    all_events.extend(caelus_events)

    # 3. SURFRAD (Desert Rock + Table Mountain)
    surfrad_events = process_surfrad(years=[2018, 2019, 2020])
    save_sightings(surfrad_events, "surfrad_twilight.csv")
    print_summary(surfrad_events, "SURFRAD dataset")
    all_events.extend(surfrad_events)

    # Combined
    save_sightings(all_events, "bsrn_all_twilight.csv")
    print_summary(all_events, "ALL SOURCES COMBINED")

    print("\nDone.")


if __name__ == "__main__":
    main()
