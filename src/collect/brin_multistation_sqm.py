"""
Extract per-night Fajr and Isha records from the BRIN/LAPAN multi-station
sky brightness dataset "Zenith sky brightness over Indonesia".

Source: Priyatikanto, Rhorom (2025). Zenith sky brightness over Indonesia.
BRIN RIN Dataverse. hdl:20.500.12690/RIN/USTNXB. CC0 1.0 (Public Domain).

Dataset: 57 monthly files across 8 stations (2018-04 to 2018-12).
Stations: AGM, BDG, BIK, GRT, MOVSMD1, PSR, PTK, SBG, SMD.
Format: Datetime(UTC), SunAlt, MoonAlt, Temp, MPSAS, Q

Q quality flags: 0=peculiar, 1=overcast, 2=cloudy, 3=clear,
                 4=moonlit-cloudy, 5=moonlit-clear.

Method: Group rows by UTC date. For each date find the evening Isha
crossing (SunAlt falls through -18°) and morning Fajr crossing
(SunAlt rises through -18°). Only use rows with Q in {3, 5} (clear).

Output: CSV rows compatible with ingest.py schema.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd

log = logging.getLogger(__name__)

# Depression angle to detect (matches standard 18° for Fajr / Isha)
FAJR_ANGLE = 18.0
ISHA_ANGLE = 18.0

# Only use Q=3 (clear) or Q=5 (moonlit-clear) rows
CLEAR_Q_FLAGS = {3, 5}

# Minimum clear rows in the night window to accept a night
MIN_CLEAR_ROWS = 10

SOURCE_CITATION = (
    "Priyatikanto R. (2025). Zenith sky brightness over Indonesia. "
    "BRIN RIN Dataverse. hdl:20.500.12690/RIN/USTNXB. CC0 1.0."
)

# UTC offsets per station code prefix
# Most Indonesian stations are WIB (UTC+7).
# BIK (Biak, Papua) is WIT (UTC+9).
STATION_UTC_OFFSETS: dict[str, float] = {
    "AGM": 7.0,   # Agam/Kototabang, West Sumatra
    "BDG": 7.0,   # Bandung, West Java
    "BIK": 9.0,   # Biak, Papua
    "GRT": 7.0,   # Garut, West Java
    "MOV": 7.0,   # Moving SQM at Sumedang (MOVSMD1)
    "PSR": 7.0,   # Pasuruan/Watukosek, East Java
    "PTK": 7.0,   # Pontianak, West Kalimantan
    "SBG": 7.0,   # Subang, West Java
    "SMD": 7.0,   # Sumedang, West Java
}

# UTC hour windows for Isha and Fajr crossing detection.
# These are intentionally wide — the actual crossing is found via interpolation.
# For UTC+7: Isha ~19:00 local = 12:00 UTC; Fajr ~05:00 local = 22:00 UTC.
# For UTC+9: Isha ~19:00 local = 10:00 UTC; Fajr ~05:00 local = 20:00 UTC.
_UTC_WINDOWS = {
    7.0: {"isha_utc": (9.5, 14.5), "fajr_utc": (19.5, 23.5)},
    9.0: {"isha_utc": (7.5, 12.5), "fajr_utc": (17.5, 21.5)},
}


def _parse_station_file(dat_path: Path) -> tuple[dict, pd.DataFrame]:
    """
    Parse a single BRIN multi-station .dat file.

    Returns (metadata_dict, dataframe). The metadata dict has 'lat' and 'lon'.
    The dataframe has columns: Datetime, SunAlt, MoonAlt, Temp, MPSAS, Q.
    """
    with open(dat_path) as f:
        lines = f.readlines()

    meta: dict = {}
    data_lines: list[str] = []
    for line in lines:
        if line.startswith("# Lon:"):
            meta["lon"] = float(line.split(":")[1].strip())
        elif line.startswith("# Lat:"):
            meta["lat"] = float(line.split(":")[1].strip())
        elif not line.startswith("#"):
            data_lines.append(line)

    if not data_lines:
        return meta, pd.DataFrame()

    df = pd.read_csv(
        StringIO("".join(data_lines)),
        sep=r"\s+",
        names=["Datetime", "SunAlt", "MoonAlt", "Temp", "MPSAS", "Q"],
        parse_dates=["Datetime"],
    )
    # Drop rows that failed to parse
    df = df.dropna(subset=["Datetime", "SunAlt"])
    df["Q"] = pd.to_numeric(df["Q"], errors="coerce").fillna(0).astype(int)
    df["MPSAS"] = pd.to_numeric(df["MPSAS"], errors="coerce").fillna(0.0)
    return meta, df


def _interpolate_crossing(
    df_window: pd.DataFrame,
    target_sunalt: float,
    direction: str,  # "rising" (Fajr) or "falling" (Isha)
) -> Optional[tuple[datetime, float]]:
    """
    Find the UTC time when SunAlt crosses target_sunalt.
    Returns (utc_datetime, mpsas_at_crossing) or None.
    """
    df_window = df_window.reset_index(drop=True)
    if len(df_window) < 2:
        return None

    if direction == "rising":
        below = df_window["SunAlt"] < target_sunalt
        above = df_window["SunAlt"] >= target_sunalt
        if not (below.any() and above.any()):
            return None
        idx_cross = df_window[above].index[0]
        idx_before = idx_cross - 1
        if idx_before < 0:
            return None
    else:  # falling
        above = df_window["SunAlt"] > target_sunalt
        below = df_window["SunAlt"] <= target_sunalt
        if not (above.any() and below.any()):
            return None
        idx_cross = df_window[below].index[0]
        idx_before = idx_cross - 1
        if idx_before < 0:
            return None

    row_before = df_window.iloc[idx_before]
    row_cross = df_window.iloc[idx_cross]
    alt_before = float(row_before["SunAlt"])
    alt_cross = float(row_cross["SunAlt"])

    if abs(alt_cross - alt_before) < 0.001:
        return None

    t_before = pd.Timestamp(row_before["Datetime"])
    t_cross = pd.Timestamp(row_cross["Datetime"])
    frac = (target_sunalt - alt_before) / (alt_cross - alt_before)
    dt_interp = t_before + (t_cross - t_before) * frac
    mpsas_interp = float(row_before["MPSAS"]) + (
        float(row_cross["MPSAS"]) - float(row_before["MPSAS"])
    ) * frac

    return dt_interp.to_pydatetime(), mpsas_interp


def _has_enough_clear_rows(df_night: pd.DataFrame, windows_utc: dict) -> bool:
    """Check if the night has clear rows in both Isha and Fajr windows."""
    utc_h = df_night["Datetime"].dt.hour + df_night["Datetime"].dt.minute / 60
    for key in ("isha_utc", "fajr_utc"):
        lo, hi = windows_utc[key]
        clear_in_window = df_night[
            (utc_h >= lo) & (utc_h <= hi) & (df_night["Q"].isin(CLEAR_Q_FLAGS))
        ]
        if len(clear_in_window) < MIN_CLEAR_ROWS:
            return False
    return True


def extract_from_station_files(
    dat_files: list[Path],
    station_code: str,
) -> list[dict]:
    """
    Process all monthly .dat files for one station.

    Returns a list of raw sighting records (one per night per twilight type).
    """
    utc_offset = STATION_UTC_OFFSETS.get(station_code[:3], 7.0)
    windows = _UTC_WINDOWS.get(utc_offset, _UTC_WINDOWS[7.0])

    # Load and concatenate all monthly files for this station
    frames = []
    metas = []
    for f in sorted(dat_files):
        meta, df = _parse_station_file(f)
        if not df.empty:
            frames.append(df)
            metas.append(meta)

    if not frames:
        log.warning("No data loaded for station %s", station_code)
        return []

    df_all = pd.concat(frames, ignore_index=True).sort_values("Datetime").reset_index(drop=True)

    # Use coordinates from the first file that has them
    lat = None
    lon = None
    for m in metas:
        if "lat" in m and "lon" in m:
            lat = m["lat"]
            lon = m["lon"]
            break
    if lat is None:
        log.warning("No coordinates found for station %s — skipping", station_code)
        return []

    log.info(
        "Station %s: %d rows, lat=%.4f, lon=%.4f, UTC+%.0f",
        station_code, len(df_all), lat, lon, utc_offset,
    )

    # Group by UTC date
    df_all["utc_date"] = df_all["Datetime"].dt.date
    unique_dates = sorted(df_all["utc_date"].unique())
    log.info("Station %s: %d UTC dates", station_code, len(unique_dates))

    records: list[dict] = []
    fajr_count = 0
    isha_count = 0
    clear_count = 0

    isha_lo, isha_hi = windows["isha_utc"]
    fajr_lo, fajr_hi = windows["fajr_utc"]

    for utc_date in unique_dates:
        night_df = df_all[df_all["utc_date"] == utc_date].copy()
        utc_h = night_df["Datetime"].dt.hour + night_df["Datetime"].dt.minute / 60

        # Check clear sky in both windows
        isha_clear = night_df[
            (utc_h >= isha_lo) & (utc_h <= isha_hi) & (night_df["Q"].isin(CLEAR_Q_FLAGS))
        ]
        fajr_clear = night_df[
            (utc_h >= fajr_lo) & (utc_h <= fajr_hi) & (night_df["Q"].isin(CLEAR_Q_FLAGS))
        ]
        if len(isha_clear) < MIN_CLEAR_ROWS and len(fajr_clear) < MIN_CLEAR_ROWS:
            continue
        clear_count += 1

        # --- Isha crossing ---
        if len(isha_clear) >= MIN_CLEAR_ROWS:
            isha_win = night_df[
                (utc_h >= isha_lo) & (utc_h <= isha_hi) & (night_df["SunAlt"] < 0)
            ].copy()
            if not isha_win.empty:
                result = _interpolate_crossing(
                    isha_win, target_sunalt=-ISHA_ANGLE, direction="falling"
                )
                if result is not None:
                    utc_dt, mpsas = result
                    local_dt = utc_dt + timedelta(hours=utc_offset)
                    date_local = local_dt.strftime("%Y-%m-%d")
                    time_local = local_dt.strftime("%H:%M")
                    records.append({
                        "prayer": "isha",
                        "date_local": date_local,
                        "time_local": time_local,
                        "utc_offset": utc_offset,
                        "lat": lat,
                        "lng": lon,
                        "elevation_m": 0,
                        "source": SOURCE_CITATION,
                        "notes": (
                            f"BRIN CC0 multi-station SQM; station={station_code}; "
                            f"SunAlt interpolated to {-ISHA_ANGLE:.1f}° depression (Shafaq Abyad); "
                            f"MPSAS at crossing={mpsas:.3f}; Q-filtered (clear nights)"
                        ),
                    })
                    isha_count += 1

        # --- Fajr crossing ---
        if len(fajr_clear) >= MIN_CLEAR_ROWS:
            fajr_win = night_df[
                (utc_h >= fajr_lo) & (utc_h <= fajr_hi) & (night_df["SunAlt"] < 0)
            ].copy()
            if not fajr_win.empty:
                result = _interpolate_crossing(
                    fajr_win, target_sunalt=-FAJR_ANGLE, direction="rising"
                )
                if result is not None:
                    utc_dt, mpsas = result
                    local_dt = utc_dt + timedelta(hours=utc_offset)
                    date_local = local_dt.strftime("%Y-%m-%d")
                    time_local = local_dt.strftime("%H:%M")
                    records.append({
                        "prayer": "fajr",
                        "date_local": date_local,
                        "time_local": time_local,
                        "utc_offset": utc_offset,
                        "lat": lat,
                        "lng": lon,
                        "elevation_m": 0,
                        "source": SOURCE_CITATION,
                        "notes": (
                            f"BRIN CC0 multi-station SQM; station={station_code}; "
                            f"SunAlt interpolated to {-FAJR_ANGLE:.1f}° depression; "
                            f"MPSAS at crossing={mpsas:.3f}; Q-filtered (clear nights)"
                        ),
                    })
                    fajr_count += 1

    log.info(
        "Station %s: %d clear dates → %d Fajr + %d Isha records",
        station_code, clear_count, fajr_count, isha_count,
    )
    return records


def download_and_extract_all(output_dir: Path) -> list[dict]:
    """
    Download all 57 files from BRIN Dataverse and extract records.
    Caches downloaded files to output_dir/brin_multistation_raw/.
    """
    from urllib.request import urlopen, Request

    # File ID → filename mapping from BRIN Dataverse API
    FILE_IDS: dict[str, int] = {
        "AGM_201804.dat": 732868,
        "AGM_201805.dat": 732855,
        "AGM_201806.dat": 732861,
        "AGM_201808.dat": 732869,
        "AGM_201809.dat": 732889,
        "AGM_201810.dat": 732892,
        "AGM_201811.dat": 732850,
        "BDG_201804.dat": 732873,
        "BDG_201805.dat": 732886,
        "BDG_201806.dat": 732846,
        "BIK_201804.dat": 732871,
        "BIK_201805.dat": 732899,
        "BIK_201806.dat": 732849,
        "BIK_201807.dat": 732891,
        "BIK_201808.dat": 732884,
        "BIK_201809.dat": 732857,
        "BIK_201810.dat": 732879,
        "BIK_201811.dat": 732883,
        "GRT_201804.dat": 732875,
        "GRT_201805.dat": 732860,
        "GRT_201806.dat": 732872,
        "GRT_201807.dat": 732848,
        "GRT_201808.dat": 732894,
        "GRT_201809.dat": 732847,
        "GRT_201810.dat": 732901,
        "GRT_201811.dat": 732881,
        "MOVSMD1.dat":    732887,
        "PSR_201804.dat": 732866,
        "PSR_201805.dat": 732870,
        "PSR_201806.dat": 732900,
        "PSR_201807.dat": 732890,
        "PSR_201808.dat": 732858,
        "PSR_201809.dat": 732853,
        "PSR_201810.dat": 732880,
        "PSR_201811.dat": 732878,
        "PSR_201812.dat": 732854,
        "PTK_201804.dat": 732882,
        "PTK_201805.dat": 732852,
        "PTK_201806.dat": 732867,
        "PTK_201807.dat": 732897,
        "PTK_201808.dat": 732902,
        "PTK_201809.dat": 732895,
        "PTK_201810.dat": 732877,
        "PTK_201811.dat": 732896,
        "SBG_201804.dat": 732898,
        "SBG_201805.dat": 732862,
        "SBG_201806.dat": 732885,
        "SBG_201807.dat": 732865,
        "SMD_201804.dat": 732863,
        "SMD_201805.dat": 732876,
        "SMD_201806.dat": 732864,
        "SMD_201807.dat": 732893,
        "SMD_201808.dat": 732888,
        "SMD_201809.dat": 732851,
        "SMD_201810.dat": 732856,
        "SMD_201811.dat": 732874,
        "SMD_201812.dat": 732859,
    }

    cache_dir = output_dir / "brin_multistation_raw"
    cache_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://data.brin.go.id/api/access/datafile/{fid}"
    headers = {
        "User-Agent": (
            "pray-calc-ml/1.0 research bot "
            "(github.com/acamarata/pray-calc-ml; Islamic prayer data; "
            "contact: alisalaah@gmail.com)"
        )
    }

    # Group files by station code
    station_files: dict[str, list[Path]] = {}
    for filename, fid in FILE_IDS.items():
        station_code = filename.split("_")[0].rstrip("0123456789")
        if filename == "MOVSMD1.dat":
            station_code = "MOVSMD1"

        cached = cache_dir / filename
        if not cached.exists():
            url = base_url.format(fid=fid)
            log.info("Downloading %s (id=%d)...", filename, fid)
            try:
                req = Request(url, headers=headers)
                with urlopen(req, timeout=60) as resp:
                    cached.write_bytes(resp.read())
                log.info("  → saved %d bytes", cached.stat().st_size)
            except Exception as e:
                log.warning("Failed to download %s: %s", filename, e)
                continue
        else:
            log.debug("Cache hit: %s", filename)

        if station_code not in station_files:
            station_files[station_code] = []
        station_files[station_code].append(cached)

    # Extract records for each station
    all_records: list[dict] = []
    for station_code, files in sorted(station_files.items()):
        if station_code == "MOVSMD1":
            log.info("Skipping MOVSMD1 (moving SQM — no fixed coordinates)")
            continue
        records = extract_from_station_files(files, station_code)
        all_records.extend(records)

    log.info(
        "Multi-station total: %d records (%d Fajr, %d Isha)",
        len(all_records),
        sum(1 for r in all_records if r["prayer"] == "fajr"),
        sum(1 for r in all_records if r["prayer"] == "isha"),
    )
    return all_records


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    repo_root = Path(__file__).parent.parent.parent
    out_dir = repo_root / "data" / "raw" / "raw_sightings"
    cache_dir = repo_root / "data" / "raw"

    records = download_and_extract_all(cache_dir)

    out_file = out_dir / "brin_multistation_2018.csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    df = pd.DataFrame(records)
    if df.empty:
        print("No records extracted.")
        sys.exit(0)
    df.to_csv(out_file, index=False)
    print(f"\nExtracted {len(df)} total records")
    fajr = df[df["prayer"] == "fajr"]
    isha = df[df["prayer"] == "isha"]
    print(f"  Fajr: {len(fajr)}")
    print(f"  Isha: {len(isha)}")
    print(f"  Unique stations:")
    for code in df["notes"].str.extract(r"station=(\w+)")[0].unique():
        sub = df[df["notes"].str.contains(f"station={code}")]
        f_count = (sub["prayer"] == "fajr").sum()
        i_count = (sub["prayer"] == "isha").sum()
        print(f"    {code}: {f_count} Fajr + {i_count} Isha")
    print(f"\nOutput: {out_file}")
