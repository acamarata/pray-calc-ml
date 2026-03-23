"""
BSRN Twilight Extractor — corrected for actual file formats.

Dataset formats:
1. BSRN 5-site parquet (Zenodo 10593079):
   - Multi-index: (times_utc, site)
   - Columns: climate, longitude, latitude, sza, eth, ghicda, ghics, difcs, ghi, dif, sky_type
   - 'site' values like 'asp/bsrn', 'bon/bsrn', etc.

2. CAELUS ZIPs (Zenodo 7897639):
   - Each ZIP contains one CSV named {code}_bsrn_{year}.csv
   - Columns: times_utc, sza, eth, ghi, dif, ghics, ghicda, sky_type
   - sza = solar zenith angle (degrees). Depression = sza - 90 when sza > 90.

For twilight extraction we use BOTH ghi AND dif (diffuse horizontal irradiance).
Diffuse is more sensitive at twilight — it captures scattered skylight before direct beam arrives.

The `sza` column is authoritative for solar geometry — no need to recompute.
Depression angle = sza - 90° (valid when sza > 90°, i.e., sun below horizon).

Thresholds extracted (multi-threshold approach):
- 0.5, 1, 2, 5, 10 W/m² for both ghi and dif

Primary threshold for the main output: dif >= 1.0 W/m² (diffuse is more reliable at twilight).
"""

import os
import math
import zipfile
import requests
import re
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path
from io import BytesIO

# ── paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/Volumes/X9/Sites/acamarata/pray-calc-ml")
RAW_BSRN = BASE / "data/raw/bsrn"
RAW_SIGHTINGS = BASE / "data/raw/raw_sightings"
RAW_BSRN.mkdir(parents=True, exist_ok=True)
RAW_SIGHTINGS.mkdir(parents=True, exist_ok=True)

# ── thresholds ────────────────────────────────────────────────────────────────
THRESHOLDS = [0.5, 1.0, 2.0, 5.0, 10.0]
PRIMARY_THRESHOLD = 1.0  # W/m²

# ── station metadata ──────────────────────────────────────────────────────────
# For CAELUS: station codes and their coordinates
CAELUS_STATION_META = {
    "sbo": {"name": "Sede Boqer",         "lat": 30.8597, "lon": 34.7794,  "region": "Negev/Israel"},
    "tam": {"name": "Tamanrasset",         "lat": 22.7903, "lon": 5.5292,   "region": "Algeria"},
    "xia": {"name": "Xianghe",             "lat": 39.754,  "lon": 116.962,  "region": "China"},
    "iza": {"name": "Izana",               "lat": 28.3093, "lon": -16.4993, "region": "Canary Islands/Spain"},
    "ish": {"name": "Ishigakijima",        "lat": 24.3367, "lon": 124.1644, "region": "Japan"},
    "dra": {"name": "Desert Rock",         "lat": 36.626,  "lon": -116.018, "region": "Nevada/USA"},
    "e13": {"name": "SouthernGreatPlains", "lat": 36.605,  "lon": -97.485,  "region": "Oklahoma/USA"},
    "tat": {"name": "Tateno",              "lat": 36.0581, "lon": 140.1258, "region": "Japan"},
    "fua": {"name": "Fukuoka",             "lat": 33.5822, "lon": 130.3764, "region": "Japan"},
    "gcr": {"name": "GoodwinCreek",        "lat": 34.2547, "lon": -89.8729, "region": "Mississippi/USA"},
    "bil": {"name": "Billings/ARM",        "lat": 36.605,  "lon": -97.516,  "region": "Oklahoma/USA"},
    "abs": {"name": "Abashiri",            "lat": 44.0178, "lon": 144.2797, "region": "Japan"},
    "lyu": {"name": "Lanyu Island",        "lat": 22.037,  "lon": 121.5583, "region": "Taiwan"},
    "lln": {"name": "Lulin",               "lat": 23.4686, "lon": 120.8736, "region": "Taiwan"},
    "cnr": {"name": "Cener",               "lat": 42.816,  "lon": -1.601,   "region": "Spain/Navarra"},
    "flo": {"name": "Florina",             "lat": 40.78,   "lon": 21.38,    "region": "Greece"},
    "car": {"name": "Carpentras",          "lat": 44.0833, "lon": 5.0583,   "region": "France"},
}

# Five-site parquet station metadata (lat/lon stored in the file itself)
FIVE_SITE_MAP = {
    "mnm": {"name": "Minamitorishima", "region": "Japan"},
    "asp": {"name": "Alice Springs",   "region": "Australia"},
    "car": {"name": "Carpentras",      "region": "France"},
    "bon": {"name": "Bondville",       "region": "USA/Illinois"},
    "son": {"name": "Sonnblick",       "region": "Austria"},
}

CAELUS_BASE_URL = "https://zenodo.org/api/records/7897639/files/{filename}/content"
FIVE_SITE_URL   = "https://zenodo.org/records/10593079/files/bsrn_valid_five_sites.parquet"
FIVE_SITE_PATH  = RAW_BSRN / "bsrn_valid_five_sites.parquet"

# ── download helper ───────────────────────────────────────────────────────────

def download_file(url: str, dest: Path, label: str = "") -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [cached] {label or dest.name}")
        return True
    try:
        print(f"  [dl] {label or dest.name} ...", end=" ", flush=True)
        r = requests.get(url, timeout=180, stream=True)
        r.raise_for_status()
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=131072):
                f.write(chunk)
                downloaded += len(chunk)
        print(f"OK ({downloaded/1_048_576:.1f} MB)")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        if dest.exists():
            dest.unlink()
        return False


# ── twilight extraction ───────────────────────────────────────────────────────

def extract_events_from_df(
    df: pd.DataFrame,
    lat: float,
    lon: float,
    station_code: str,
    station_name: str,
    source: str,
) -> list[dict]:
    """
    df must have columns: times_utc (datetime64[ns] UTC), sza (float), ghi (float), dif (float).

    For each day:
      dawn = first minute where dif (or ghi if dif is null) crosses PRIMARY_THRESHOLD
             AND sza > 90 (sun still below horizon)
      dusk = last minute where dif (or ghi) >= PRIMARY_THRESHOLD
             AND sza > 90

    Records depression angle = sza - 90.0 at the event moment.
    Also records raw threshold-by-threshold data for all THRESHOLDS.
    """
    events = []

    df = df.copy()
    df["times_utc"] = pd.to_datetime(df["times_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["times_utc"]).sort_values("times_utc").reset_index(drop=True)

    # Build irradiance signal: prefer dif (diffuse) which is more sensitive at twilight
    # Fall back to ghi if dif is all NaN
    if "dif" in df.columns:
        df["irr"] = pd.to_numeric(df["dif"], errors="coerce")
    else:
        df["irr"] = float("nan")

    if "ghi" in df.columns:
        ghi_vals = pd.to_numeric(df["ghi"], errors="coerce")
        # Fill irr NaN with ghi
        df["irr"] = df["irr"].combine_first(ghi_vals)

    df["sza"] = pd.to_numeric(df["sza"], errors="coerce")
    df["date"] = df["times_utc"].dt.date

    for day, grp in df.groupby("date"):
        grp = grp.sort_values("times_utc").reset_index(drop=True)

        irr  = grp["irr"].values
        sza  = grp["sza"].values
        ts   = grp["times_utc"].values

        n = len(irr)
        if n < 10:
            continue

        # For each threshold, extract dawn/dusk
        for threshold in THRESHOLDS:
            # Dawn: first index where irr >= threshold AND sza > 90
            # Require at least 2 consecutive sub-threshold readings immediately before
            dawn_idx = None
            for i in range(2, n):
                if (
                    not np.isnan(irr[i])
                    and irr[i] >= threshold
                    and not np.isnan(sza[i])
                    and sza[i] > 90.0
                ):
                    # Confirm at least 2 prior readings were sub-threshold
                    prev_ok = all(
                        (np.isnan(v) or v < threshold)
                        for v in irr[max(0, i-3):i]
                    )
                    if prev_ok:
                        dawn_idx = i
                        break

            # Dusk: last index where irr >= threshold AND sza > 90
            # Require at least 2 consecutive sub-threshold readings immediately after
            dusk_idx = None
            for i in range(n - 3, -1, -1):
                if (
                    not np.isnan(irr[i])
                    and irr[i] >= threshold
                    and not np.isnan(sza[i])
                    and sza[i] > 90.0
                ):
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
                # sza must be > 90 (sun below horizon) — extra safety check
                if sza_val <= 90.0:
                    continue
                # Depression angle in degrees
                dep = round(sza_val - 90.0, 4)
                # Only record plausible twilight depression (0.5° to 20°)
                if dep < 0.3 or dep > 20.0:
                    continue

                utc_ts = pd.Timestamp(ts[idx])
                irr_val = float(irr[idx])

                # Also grab ghi/dif individually at this moment
                ghi_at = float(grp["ghi"].iloc[idx]) if "ghi" in grp.columns else float("nan")
                dif_at  = float(grp["dif"].iloc[idx])  if "dif" in grp.columns else float("nan")

                events.append({
                    "date":                  str(day),
                    "event_type":            event_type,
                    "utc_time":              utc_ts.strftime("%H:%M:%S"),
                    "sza_deg":               round(sza_val, 4),
                    "solar_depression_deg":  dep,
                    "irr_wm2":               round(irr_val, 2),
                    "ghi_wm2":               round(ghi_at, 2) if not math.isnan(ghi_at) else None,
                    "dif_wm2":               round(dif_at, 2)  if not math.isnan(dif_at) else None,
                    "threshold_wm2":         threshold,
                    "lat":                   lat,
                    "lon":                   lon,
                    "station_code":          station_code,
                    "station_name":          station_name,
                    "source":                source,
                })

    return events


# ── 5-site dataset ────────────────────────────────────────────────────────────

def process_five_site() -> list[dict]:
    print("\n=== BSRN 5-site parquet (Zenodo 10593079) ===")
    ok = download_file(FIVE_SITE_URL, FIVE_SITE_PATH, "bsrn_valid_five_sites.parquet")
    if not ok:
        return []

    print("  Loading ...", end=" ", flush=True)
    df_raw = pd.read_parquet(FIVE_SITE_PATH)
    df_raw = df_raw.reset_index()  # brings times_utc and site into columns
    print(f"OK — {len(df_raw):,} rows")
    print(f"  Columns: {list(df_raw.columns)}")

    all_events = []
    for site_val, grp in df_raw.groupby("site"):
        # site_val is like 'asp/bsrn'
        code = str(site_val).split("/")[0].lower()
        meta = FIVE_SITE_MAP.get(code, {"name": code, "region": "unknown"})

        # Get lat/lon from the data itself
        lat = float(grp["latitude"].iloc[0])
        lon = float(grp["longitude"].iloc[0])

        # Rename columns to standard
        sub = grp[["times_utc", "sza", "ghi", "dif"]].copy()

        print(f"  {meta['name']} ({code}) lat={lat:.3f} lon={lon:.3f}: "
              f"{len(sub):,} rows ...", end=" ", flush=True)

        evts = extract_events_from_df(sub, lat, lon, code, meta["name"], "bsrn_5site")
        print(f"{len(evts)} events")
        all_events.extend(evts)

    return all_events


# ── CAELUS dataset ─────────────────────────────────────────────────────────────

def list_caelus_files() -> dict[str, list[int]]:
    """Return dict of station_code -> sorted list of available years."""
    print("  Querying Zenodo API ...", end=" ", flush=True)
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
        for k in available:
            available[k] = sorted(available[k])
        print(f"{len(available)} stations found")
        return available
    except Exception as e:
        print(f"FAILED: {e}")
        return {}


def process_caelus_zip(zip_path: Path, station_code: str, meta: dict, year: int) -> list[dict]:
    events = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            csv_files = [n for n in zf.namelist() if n.endswith(".csv")]
            if not csv_files:
                print(f"    WARNING: no CSV in {zip_path.name}")
                return []
            with zf.open(csv_files[0]) as f:
                df = pd.read_csv(f)

        # Validate expected columns
        required = {"times_utc", "sza", "ghi"}
        missing = required - set(df.columns)
        if missing:
            print(f"    WARNING: missing columns {missing} in {zip_path.name}")
            return []

        evts = extract_events_from_df(
            df, meta["lat"], meta["lon"],
            station_code, meta["name"], f"caelus_{year}",
        )
        return evts

    except zipfile.BadZipFile:
        print(f"    ERROR: corrupt zip {zip_path.name}")
        return []
    except Exception as e:
        print(f"    ERROR {zip_path.name}: {e}")
        return []


def process_caelus(priority_codes: list[str] | None = None, max_years: int = 5) -> list[dict]:
    print("\n=== CAELUS dataset (Zenodo 7897639) ===")
    available = list_caelus_files()
    if not available:
        return []

    if priority_codes is None:
        # All known stations, sorted by relevance
        priority_codes = list(CAELUS_STATION_META.keys())

    all_events = []

    for code in priority_codes:
        if code not in available:
            print(f"  SKIP {code}: not in CAELUS")
            continue

        meta = CAELUS_STATION_META.get(code)
        if meta is None:
            print(f"  SKIP {code}: no metadata")
            continue

        years = available[code][:max_years]
        print(f"\n  {meta['name']} ({code}) "
              f"lat={meta['lat']} lon={meta['lon']} region={meta['region']}")
        print(f"  Years: {years}")

        station_events = []
        for year in years:
            fname = f"{code}_bsrn_{year}.zip"
            url   = CAELUS_BASE_URL.format(filename=fname)
            dest  = RAW_BSRN / fname

            ok = download_file(url, dest, fname)
            if not ok:
                continue

            print(f"    {fname} ...", end=" ", flush=True)
            evts = process_caelus_zip(dest, code, meta, year)
            print(f"{len(evts)} events ({year})")
            station_events.extend(evts)

        print(f"  → {len(station_events)} events total for {code}")
        all_events.extend(station_events)

    return all_events


# ── SURFRAD ───────────────────────────────────────────────────────────────────

SURFRAD_STATIONS = {
    "dra": {"name": "Desert Rock",  "lat": 36.626, "lon": -116.018, "dir": "DRA"},
    "tbl": {"name": "TableMountain","lat": 40.125, "lon": -105.237, "dir": "TBL"},
}
SURFRAD_BASE = "https://gml.noaa.gov/aftp/data/radiation/surfrad"


def parse_surfrad_day(content: bytes) -> pd.DataFrame:
    """Parse a SURFRAD daily .dat file to a dataframe with [times_utc, sza, ghi, dif]."""
    lines = content.decode("utf-8", errors="replace").splitlines()
    records = []
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 10:
            continue
        try:
            yr   = int(parts[0])
            jday = int(parts[1])
            hr   = int(parts[2])
            mn   = int(parts[3])
            zen  = float(parts[5])   # solar zenith angle (degrees)
            ghi  = float(parts[6])   # downwelling shortwave (W/m²)
            dif  = float(parts[9])   # diffuse shortwave (W/m²)

            dt = datetime(yr, 1, 1, hr, mn, tzinfo=timezone.utc) + timedelta(days=jday - 1)

            # -9999 = missing
            records.append({
                "times_utc": dt,
                "sza":       None if zen < -900 else zen,
                "ghi":       None if ghi < -900 else max(0.0, ghi),
                "dif":       None if dif < -900 else max(0.0, dif),
            })
        except (ValueError, IndexError):
            continue
    return pd.DataFrame(records)


def process_surfrad(years: list[int] | None = None) -> list[dict]:
    print("\n=== SURFRAD (NOAA GML) ===")
    if years is None:
        years = [2018, 2019, 2020]

    all_events = []

    for code, meta in SURFRAD_STATIONS.items():
        print(f"\n  {meta['name']} ({code}) lat={meta['lat']} lon={meta['lon']}")
        dest_root = RAW_BSRN / "surfrad" / meta["dir"]
        dest_root.mkdir(parents=True, exist_ok=True)

        for year in years:
            year_url = f"{SURFRAD_BASE}/{meta['dir']}/{year}/"
            try:
                r = requests.get(year_url, timeout=30)
                if r.status_code != 200:
                    print(f"    {year}: HTTP {r.status_code} — skipping")
                    continue
                # Parse file listing
                files = sorted(set(re.findall(rf'{code}\d{{5}}\.dat', r.text)))
                print(f"    {year}: {len(files)} daily files", end=" ")
            except Exception as e:
                print(f"    {year}: ERROR listing: {e}")
                continue

            dest_dir = dest_root / str(year)
            dest_dir.mkdir(parents=True, exist_ok=True)

            day_dfs = []
            for fname in files:
                dest = dest_dir / fname
                furl = f"{year_url}{fname}"
                ok = download_file(furl, dest, fname)
                if not ok:
                    continue
                with open(dest, "rb") as f:
                    day_df = parse_surfrad_day(f.read())
                if not day_df.empty:
                    day_dfs.append(day_df)

            if not day_dfs:
                print("→ 0 events")
                continue

            df_year = pd.concat(day_dfs, ignore_index=True)
            evts = extract_events_from_df(
                df_year, meta["lat"], meta["lon"],
                code, meta["name"], f"surfrad_{year}",
            )
            print(f"→ {len(evts)} events")
            all_events.extend(evts)

    return all_events


# ── save / summarise ──────────────────────────────────────────────────────────

def save_events(events: list[dict], filename: str) -> Path:
    out = RAW_SIGHTINGS / filename
    if not events:
        print(f"  (no events for {filename})")
        return out
    df = pd.DataFrame(events)
    df = df.sort_values(["station_code", "date", "event_type", "threshold_wm2"])
    df.to_csv(out, index=False)
    print(f"  Saved {len(df):,} rows → {out}")
    return out


def summarise(events: list[dict], label: str):
    print(f"\n{'='*65}")
    print(f"SUMMARY: {label}")
    if not events:
        print("  (no events)")
        print("=" * 65)
        return
    df = pd.DataFrame(events)
    # Focus summary on primary threshold
    prim = df[df["threshold_wm2"] == PRIMARY_THRESHOLD]
    print(f"  All threshold events:    {len(df):,}")
    print(f"  At {PRIMARY_THRESHOLD} W/m² threshold:  {len(prim):,}")
    print(f"  Stations:  {df['station_code'].nunique()} — {sorted(df['station_code'].unique())}")
    if not prim.empty:
        print(f"  Date range: {prim['date'].min()} to {prim['date'].max()}")
        for evt_type in ["dawn", "dusk"]:
            sub = prim[prim["event_type"] == evt_type]
            if sub.empty:
                continue
            d = sub["solar_depression_deg"]
            print(f"  {evt_type.upper()} events: {len(sub):,} | "
                  f"mean dep={d.mean():.2f}° std={d.std():.2f}° "
                  f"p10={d.quantile(0.1):.2f}° p90={d.quantile(0.9):.2f}°")
    print("=" * 65)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("BSRN Twilight Extractor v2")
    print(f"Primary threshold: {PRIMARY_THRESHOLD} W/m²")
    print(f"All thresholds: {THRESHOLDS}")
    print()

    all_events = []

    # 1. BSRN 5-site
    five_events = process_five_site()
    save_events(five_events, "bsrn_5site_twilight.csv")
    summarise(five_events, "BSRN 5-site")
    all_events.extend(five_events)

    # 2. CAELUS — priority stations in 20-45°N
    priority = ["sbo", "tam", "xia", "iza", "ish", "dra", "e13", "tat", "fua",
                "gcr", "bil", "abs", "lyu", "cnr", "flo"]
    caelus_events = process_caelus(priority_codes=priority, max_years=5)
    save_events(caelus_events, "bsrn_caelus_twilight.csv")
    summarise(caelus_events, "CAELUS")
    all_events.extend(caelus_events)

    # 3. SURFRAD — Desert Rock (arid, 36.6°N) + Table Mountain
    surfrad_events = process_surfrad(years=[2018, 2019, 2020])
    save_events(surfrad_events, "surfrad_twilight.csv")
    summarise(surfrad_events, "SURFRAD")
    all_events.extend(surfrad_events)

    # Combined output
    save_events(all_events, "bsrn_all_twilight.csv")
    summarise(all_events, "ALL SOURCES")

    print("\nDone.")


if __name__ == "__main__":
    main()
