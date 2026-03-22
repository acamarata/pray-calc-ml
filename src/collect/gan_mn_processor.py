"""
Extract per-night Fajr and Isha depression angles from Globe at Night Monitoring
Network (GaN-MN) continuous SQM-LE data.

Source: Globe at Night Sky Brightness Monitoring Network.
Data page: https://globeatnight.org/gan-mn/
Station registry: http://globeatnight-network.org/global-at-night-monitoring-network.html

Data format: CSV with columns:
    id                  - row identifier
    created             - record creation timestamp (UTC)
    received_utc        - UTC timestamp of SQM reading
    received_adjusted   - local time at station (UTC + station offset)
    sqmle_serial_number - SQM-LE device serial number
    nsb                 - night sky brightness (MSAS, mag/arcsec^2); 0 = invalid
    sensor_frequency    - SQM sensor frequency
    sensor_period_count - sensor period count
    sensor_period_second - sensor period in seconds
    temperature         - ambient temperature (°C)
    device_code         - station identifier (e.g. "TBT", "Dal", "Nrnr")

NOTE: The CSV does not include latitude/longitude. Coordinates are taken from the
station registry compiled below (STATION_REGISTRY dict). Stations with unknown
coordinates are skipped.

The UTC offset for each station is inferred from received_adjusted minus received_utc.

Method
------
Identical to the TESS processor (tess_processor.py). For each station:

1. Load and filter: drop nsb=0 (sensor saturated or invalid), drop daytime readings
   (solar altitude >= -2°, computed via PyEphem).

2. Group by local night. A "night" runs from local sunset to next local sunrise,
   identified by grouping around the solar midnight (the UTC moment of minimum
   solar altitude for that calendar day).

3. Characterise the night baseline: compute the median MSAS across the darkest
   portion (solar depression > 10°). Skip nights with fewer than MIN_DARK_ROWS
   valid readings.

4. Find the twilight inflection point using the maximum rate of MSAS change
   (|dMSAS/dt|) during each twilight window. The inflection occurs at the moment
   sky brightness transitions most rapidly — this is the sharpest photometric
   signal of twilight onset/end.

5. Compute the solar depression angle at that inflection moment via PyEphem.
   Record it as a Fajr sighting (dawn inflection) or Isha sighting (dusk inflection).

6. Quality filters:
   - Reject nights where the dark-window MSAS median < MIN_DARK_MSAS (heavily
     light-polluted, sky never gets dark enough to track astronomical twilight).
   - Reject if the inflection MSAS is > MSAS_INFLECTION_MAX_DROP from night median
     (likely cloud passage, not real twilight transition).
   - Reject if the computed depression angle is outside ANGLE_MIN to ANGLE_MAX
     (would indicate sensor anomaly or extreme atmospheric conditions).

Output
------
List of raw sighting dicts matching the pray-calc-ml raw sightings CSV schema:
    prayer, date_local, time_local, utc_offset, lat, lng, elevation_m, source, notes
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import ephem
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# --- Configuration -----------------------------------------------------------

MIN_DARK_ROWS = 20
MIN_DARK_MSAS = 17.5
ANGLE_MIN = 6.0
ANGLE_MAX = 22.0
DARK_DEPRESSION_THRESHOLD = 10.0
TWILIGHT_WINDOW_HALF_H = 2.5
SMOOTH_WINDOW = 5
MSAS_INFLECTION_MAX_DROP = 2.5

SOURCE_CITATION = (
    "Globe at Night Monitoring Network (GaN-MN). Continuous SQM-LE sky brightness "
    "data. https://globeatnight.org/gan-mn/. "
    "Station registry: http://globeatnight-network.org/"
)

ELEVATION_DEFAULT = 0.0


# --- Station registry --------------------------------------------------------
# Coordinates compiled from the GaN-MN station registry at:
# http://globeatnight-network.org/global-at-night-monitoring-network.html
# (retrieved 2026-03-22)
#
# Format: device_code -> (location_name, lat_deg, lng_deg, elevation_m_approx)
# elevation_m_approx is from public geographic data; 0.0 where unknown.

STATION_REGISTRY: dict[str, tuple[str, float, float, float]] = {
    "TAM":   ("Taipei, Taiwan",                              25.0478,  121.5318,  50.0),
    "NAOJ":  ("Tokyo, Japan",                                35.6762,  139.6503,  40.0),
    "HKU":   ("Pokfulam, Hong Kong",                         22.2838,  114.1337,  70.0),
    "NTHU":  ("Hsinchu, Taiwan",                             24.7963,  120.9918,  30.0),
    "YFAO":  ("Yeongyang, Korea",                            36.6673,  129.1133, 200.0),
    "CNUO":  ("Cheongju, Korea",                             36.6419,  127.4890,  60.0),
    "LUO":   ("Lulin Observatory, Taiwan",                   23.4688,  120.8742, 2862.0),
    "HKn":   ("Ho Koon, Tsuen Wan, Hong Kong",               22.3719,  114.1133,  80.0),
    "SAAO":  ("Cape Town, South Africa",                    -33.9353,   18.4768,  25.0),
    "KuO":   ("Kanagawa, Japan",                             35.5195,  139.7109,  20.0),
    "NUM":   ("Ulaanbaatar, Mongolia",                       47.9077,  106.8832, 1350.0),
    "ZSSP":  ("Zselic Starry Sky Park, Hungary",             46.1942,   17.8783, 250.0),
    "Bar":   ("Bárduvarnok, Hungary",                        46.3333,   16.7333, 200.0),
    "ELO":   ("South-Brandenburg, Germany",                  51.7667,   13.7667,  90.0),
    "NNO":   ("Nagasaki, Japan",                             32.7503,  129.8777,  40.0),
    "DAO":   ("Daejeon, Korea",                              36.3504,  127.3845,  75.0),
    "YBAO":  ("Yeongwol, Korea",                             37.1870,  128.4579, 800.0),
    "CHSMO": ("Cheonan, Korea",                              36.8151,  127.1139,  50.0),
    "CGAO":  ("Chungcheongbuk-do, Korea",                    36.9910,  127.9259, 200.0),
    "GSAO":  ("Jeollanam-do, Korea",                         35.0000,  127.0000, 100.0),
    "Mac":   ("Macau Peninsula, Macau",                      22.1994,  113.5486,  10.0),
    "Tai":   ("Taipa, Macau",                                22.1607,  113.5585,  15.0),
    "Col":   ("Coloane, Macau",                              22.1167,  113.5667,  30.0),
    "TST":   ("Kowloon, Hong Kong Space Museum",             22.2974,  114.1737,   5.0),
    "NEO":   ("Chiang Mai, Thailand",                        18.7904,   98.9847, 300.0),
    "TNO":   ("Doi Inthanon, Chiang Mai, Thailand",          18.5834,   98.4868, 2565.0),
    "ISTC":  ("Inthanon Mountain, Thailand",                 18.5490,   98.4870, 2565.0),
    "CEOU":  ("Seoul National University, Korea",            37.4560,  126.9522,  80.0),
    "SNUO":  ("Seoul National University Observatory, Korea",37.4560,  126.9522,  80.0),
    "GYTI":  ("Busan, Korea",                                35.1796,  129.0756,  15.0),
    "AP":    ("Hong Kong Astropark, Sai Kung",               22.3755,  114.2707,  10.0),
    "iObs":  ("Sai Kung iObservatory, Hong Kong",            22.3767,  114.2700,  10.0),
    "UiTM":  ("Shah Alam, Malaysia",                          3.0738,  101.5183,  40.0),
    "MFAO":  ("Muju-gun, Korea",                             35.9083,  127.6917, 700.0),
    "Wux":   ("Yixing, China",                               31.3614,  119.8237,  10.0),
    "KHG":   ("Kaohsiung, Taiwan",                           22.6273,  120.2986,  30.0),
    "Heh":   ("Taroko National Park, Taiwan",                24.1488,  121.3239, 2800.0),
    "BhD":   ("Wuxi, China",                                 31.5712,  120.3119,   5.0),
    "KP":    ("King's Park, Hong Kong Observatory",          22.3125,  114.1753,  65.0),
    "Gdh":   ("Groningen-DeHeld, Netherlands",               53.2194,    6.5665,   5.0),
    "Gzc":   ("Groningen Zernike Campus, Netherlands",       53.2401,    6.5360,   5.0),
    "PAOF":  ("Ouro Fino, MG, Brazil",                      -22.2803,  -46.3647, 870.0),
    "Roo":   ("Roodeschool, Netherlands",                    53.3833,    6.9167,   2.0),
    "Sel":   ("Sellingen, Netherlands",                      52.9333,    7.1333,  20.0),
    "Lau":   ("Lauwersoog, Netherlands",                     53.4097,    6.2017,   2.0),
    "Hor":   ("Hornhuizen, Netherlands",                     53.4333,    6.4667,   2.0),
    "Lei":   ("Leiden, Netherlands",                         52.1601,    4.4970,   0.0),
    "Ame":   ("Ameland, Netherlands",                        53.4500,    5.7167,   2.0),
    "SH":    ("Shek Pik, Lantau Island, Hong Kong",          22.2328,  113.9007,  15.0),
    "Dez":   ("De Zilk, Netherlands",                        52.3000,    4.5500,   5.0),
    "Loc":   ("Lochem, Netherlands",                         52.1597,    6.4200,  20.0),
    "Hee":   ("Heerenveen, Netherlands",                     52.9603,    5.9236,   5.0),
    "Cap":   ("Cape D'Aguilar, Hong Kong",                   22.2083,  114.2569,  40.0),
    "Zwi":   ("Zwiesel, Germany",                            49.0167,   13.2333, 590.0),
    "Wad":   ("Warmond, Netherlands",                        52.2125,    4.5344,   2.0),
    "AHO":   ("Almendra HackLab, Buenos Aires, Argentina",  -34.6037,  -58.3816,  25.0),
    "Arl":   ("Arlington, Virginia, USA",                    38.8816,  -77.0910,  55.0),
    "GMARS": ("Landers, California, USA",                    34.2994, -116.5056, 1325.0),
    "TSO":   ("Tierra del Sol, San Diego, California, USA",  32.6736, -116.5311, 1220.0),
    "TBT":   ("Tsim Bei Tsui, Yuen Long, Hong Kong",         22.4806,  114.0194,   5.0),
    "Dal":   ("Promiod, Aosta Valley, Italy",                45.6667,    7.5167, 1490.0),
    "UO":    ("Utanå Observatory, Väddö, Sweden",            59.9167,   18.8333,   5.0),
    "GUT":   ("Gdansk University of Technology, Poland",     54.3520,   18.6466,   5.0),
    "MP":    ("Mai Po Nature Reserve, Hong Kong",            22.4958,  114.0322,   3.0),
    "FKYC":  ("Fanling, Hong Kong",                          22.4924,  114.1393,  20.0),
    "Oam":   ("Oamaru, South Island, New Zealand",          -45.0966,  170.9694,  30.0),
    "MBD":   ("Buffalo National River, Arkansas, USA",       36.1094,  -92.9497, 250.0),
    "LBD":   ("Buffalo National River, Arkansas, USA",       36.1094,  -92.9497, 260.0),
    "Tura":  ("Merimbula, New South Wales, Australia",      -36.8983,  149.9044,  30.0),
    "UBD":   ("Buffalo National River, Arkansas, USA",       36.1094,  -92.9497, 240.0),
    "DNSM":  ("Daegu National Science Museum, Korea",        35.8714,  128.6014,  55.0),
    "Nrnr":  ("NamibRand Nature Reserve, Namibia",          -24.9667,   15.9500, 1250.0),
    "BMCO":  ("Big Music Creek, Arkansas, USA",              35.9500,  -92.5833, 220.0),
    "SkO":   ("Skynet Observatory, Lima, Peru",             -12.0464,  -77.0428, 160.0),
    "TSU":   ("Texas State Univ, Freeman Center, TX, USA",   29.8944,  -97.9397, 190.0),
    "Cre":   ("Crestone, Colorado, USA",                     37.9958, -105.6972, 2474.0),
    "SR":    ("Shield Ranch, Texas, USA",                    29.9889,  -97.9208, 200.0),
    "Jub":   ("Jubilee, Texas, USA",                         29.8722,  -97.9625, 195.0),
    "KO":    ("Kolstugan Observatory, Katrineholm, Sweden",  59.0028,   16.2068,  50.0),
    "POB":   ("Public Observatory Belgrade, Serbia",         44.8178,   20.4569,  95.0),
    "LASO":  ("Louisville Astronomical Society, Indiana, USA",38.3361,  -86.4656, 200.0),
    "OCO":   ("Onion Creek Observatory, Texas, USA",         30.1303,  -97.7861, 165.0),
    "HCMN":  ("Dripping Springs, Texas, USA",                30.1900,  -98.0861, 380.0),
    "WODC":  ("Westcave Outdoor Discovery Center, TX, USA",  30.3333,  -98.1333, 400.0),
    "BC01":  ("Blanco, Texas, USA",                          30.0986,  -98.4267, 370.0),
    "BO":    ("Bettrath Observatory, Mönchengladbach, Germany",51.1953,   6.4578,  80.0),
    "ReO":   ("Reimers Ranch Park, Texas, USA",              30.3647,  -98.0672, 330.0),
    "LHY":   ("Siu Sai Wan, Hong Kong",                      22.2833,  114.2444,  25.0),
    "SZMS":  ("Shenzhen Middle School, Shenzhen, China",      22.5431,  114.0579,  20.0),
}


# --- PyEphem helpers ---------------------------------------------------------


def _make_observer(lat: float, lng: float, elevation_m: float = 0.0) -> ephem.Observer:
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lng)
    obs.elevation = float(elevation_m)
    obs.pressure = 1013.25
    obs.temp = 15.0
    return obs


def _solar_depression(utc_dt: datetime, obs: ephem.Observer) -> float:
    """Return solar depression angle (degrees, positive = sun below horizon)."""
    utc_naive = utc_dt.replace(tzinfo=None) if utc_dt.tzinfo is not None else utc_dt
    obs.date = ephem.Date(utc_naive)
    sun = ephem.Sun(obs)
    sun.compute(obs)
    return -math.degrees(float(sun.alt))


def _solar_midnight_utc(date: datetime.date, lat: float, lng: float) -> datetime:
    """
    Return the UTC time of solar midnight (minimum solar altitude) for the
    given local calendar date at the given coordinates.
    """
    obs = _make_observer(lat, lng)
    sun = ephem.Sun()

    base = datetime(date.year, date.month, date.day, 12, 0, 0)
    best_time = base
    best_alt = 1e9

    for offset_min in range(-12 * 60, 12 * 60):
        candidate = base + timedelta(minutes=offset_min)
        obs.date = ephem.Date(candidate)
        sun.compute(obs)
        alt = float(sun.alt)
        if alt < best_alt:
            best_alt = alt
            best_time = candidate

    return best_time


# --- MSAS processing ---------------------------------------------------------


def _compute_solar_depression_series(df: pd.DataFrame, obs: ephem.Observer) -> pd.Series:
    depressions = []
    for ts in df["received_utc"]:
        dep = _solar_depression(ts.to_pydatetime(), obs)
        depressions.append(dep)
    return pd.Series(depressions, index=df.index)


def _find_inflection(
    df_window: pd.DataFrame,
    direction: str,  # "fajr" (mag drops) or "isha" (mag rises)
) -> Optional[tuple[datetime, float, float]]:
    """
    Find the inflection point (maximum rate of sky-brightness change) in a
    twilight window.

    Returns (utc_datetime, solar_depression_at_inflection, msas_at_inflection) or None.
    """
    if len(df_window) < 10:
        return None

    df_w = df_window.copy().reset_index(drop=True)
    df_w = df_w.sort_values("received_utc").reset_index(drop=True)

    msas = df_w["nsb_smooth"].values
    dt_seconds = df_w["received_utc"].diff().dt.total_seconds().fillna(60).values
    dmdt = np.gradient(msas, dt_seconds)

    if direction == "fajr":
        valid_mask = (dmdt < 0) & (df_w["solar_dep"] >= ANGLE_MIN) & (df_w["solar_dep"] <= ANGLE_MAX)
        if not valid_mask.any():
            return None
        idx = int(np.argmin(np.where(valid_mask, dmdt, 0)))
    else:
        valid_mask = (dmdt > 0) & (df_w["solar_dep"] >= ANGLE_MIN) & (df_w["solar_dep"] <= ANGLE_MAX)
        if not valid_mask.any():
            return None
        idx = int(np.argmax(np.where(valid_mask, dmdt, 0)))

    row = df_w.iloc[idx]
    if pd.isna(row["nsb_smooth"]) or pd.isna(row["solar_dep"]):
        return None

    return (
        row["received_utc"].to_pydatetime(),
        float(row["solar_dep"]),
        float(row["nsb_smooth"]),
    )


# --- Per-night processing ----------------------------------------------------


def _process_night(
    df_night: pd.DataFrame,
    lat: float,
    lng: float,
    station_code: str,
    station_name: str,
    local_date: datetime.date,
    utc_offset_h: float,
    elevation_m: float,
    obs: ephem.Observer,
) -> list[dict]:
    """
    Extract Fajr and/or Isha records from one station night.

    df_night: rows spanning the full night, filtered to nsb > 0, sorted ascending.
    Returns a list of 0-2 raw sighting dicts.
    """
    if len(df_night) < MIN_DARK_ROWS:
        return []

    df_night = df_night.copy().reset_index(drop=True)
    df_night["solar_dep"] = _compute_solar_depression_series(df_night, obs)

    dark_mask = df_night["solar_dep"] > DARK_DEPRESSION_THRESHOLD
    n_dark = dark_mask.sum()
    if n_dark < MIN_DARK_ROWS:
        log.debug("Night %s %s: only %d dark rows, skipping", station_code, local_date, n_dark)
        return []

    night_median = float(df_night.loc[dark_mask, "nsb"].median())
    if night_median < MIN_DARK_MSAS:
        log.debug(
            "Night %s %s: median MSAS %.2f < %.2f (light pollution), skipping",
            station_code, local_date, night_median, MIN_DARK_MSAS,
        )
        return []

    df_night["nsb_smooth"] = (
        df_night["nsb"].rolling(SMOOTH_WINDOW, center=True, min_periods=1).median()
    )

    records: list[dict] = []
    night_mid = df_night["received_utc"].mean()

    # --- Dusk (Isha) ----------------------------------------------------------
    dusk_mask = (
        (df_night["received_utc"] <= night_mid)
        & (df_night["solar_dep"] >= ANGLE_MIN - 2)
        & (df_night["solar_dep"] <= ANGLE_MAX + 2)
    )
    df_dusk = df_night[dusk_mask]

    isha_result = _find_inflection(df_dusk, "isha")
    if isha_result is not None:
        utc_dt, dep_angle, msas_val = isha_result
        if abs(night_median - msas_val) <= MSAS_INFLECTION_MAX_DROP:
            local_dt = utc_dt + timedelta(hours=utc_offset_h)
            records.append({
                "prayer": "isha",
                "date_local": local_dt.strftime("%Y-%m-%d"),
                "time_local": local_dt.strftime("%H:%M"),
                "utc_offset": utc_offset_h,
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "elevation_m": elevation_m,
                "source": SOURCE_CITATION,
                "notes": (
                    f"GaN-MN station {station_code} ({station_name}); "
                    f"photometric inflection method; "
                    f"night median MSAS={night_median:.2f}; "
                    f"MSAS at inflection={msas_val:.2f}; "
                    f"depression={dep_angle:.2f}°; "
                    f"smoothing={SMOOTH_WINDOW}-pt median; dark rows={n_dark}"
                ),
            })
        else:
            log.debug(
                "Isha %s %s: inflection MSAS %.2f too far from median %.2f",
                station_code, local_date, msas_val, night_median,
            )

    # --- Dawn (Fajr) ---------------------------------------------------------
    dawn_mask = (
        (df_night["received_utc"] >= night_mid)
        & (df_night["solar_dep"] >= ANGLE_MIN - 2)
        & (df_night["solar_dep"] <= ANGLE_MAX + 2)
    )
    df_dawn = df_night[dawn_mask]

    fajr_result = _find_inflection(df_dawn, "fajr")
    if fajr_result is not None:
        utc_dt, dep_angle, msas_val = fajr_result
        if abs(night_median - msas_val) <= MSAS_INFLECTION_MAX_DROP:
            local_dt = utc_dt + timedelta(hours=utc_offset_h)
            records.append({
                "prayer": "fajr",
                "date_local": local_dt.strftime("%Y-%m-%d"),
                "time_local": local_dt.strftime("%H:%M"),
                "utc_offset": utc_offset_h,
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "elevation_m": elevation_m,
                "source": SOURCE_CITATION,
                "notes": (
                    f"GaN-MN station {station_code} ({station_name}); "
                    f"photometric inflection method; "
                    f"night median MSAS={night_median:.2f}; "
                    f"MSAS at inflection={msas_val:.2f}; "
                    f"depression={dep_angle:.2f}°; "
                    f"smoothing={SMOOTH_WINDOW}-pt median; dark rows={n_dark}"
                ),
            })
        else:
            log.debug(
                "Fajr %s %s: inflection MSAS %.2f too far from median %.2f",
                station_code, local_date, msas_val, night_median,
            )

    return records


# --- Top-level processor -----------------------------------------------------


def _infer_utc_offset(df_station: pd.DataFrame) -> float:
    """
    Infer UTC offset (hours) from the difference between received_adjusted and
    received_utc. GaN-MN stores the local time in received_adjusted, so the
    offset is simply (adjusted - utc) in hours, rounded to nearest integer.

    received_utc is tz-aware (UTC); received_adjusted is tz-naive (local wall clock).
    Strip the timezone from received_utc before subtracting.
    """
    utc_naive = df_station["received_utc"].dt.tz_localize(None)
    diffs = (df_station["received_adjusted"] - utc_naive).dt.total_seconds()
    median_diff = float(diffs.median())
    return round(median_diff / 3600)


def process_gan_mn_csv(
    csv_path: Path,
    station_filter: Optional[set[str]] = None,
) -> list[dict]:
    """
    Process a GaN-MN monthly or annual CSV file.

    Parameters
    ----------
    csv_path : Path
        Path to CSV with columns:
        id, created, received_utc, received_adjusted, sqmle_serial_number,
        nsb, sensor_frequency, sensor_period_count, sensor_period_second,
        temperature, device_code
    station_filter : set[str] or None
        If given, process only these device_code values.
        If None, process all stations that have coordinates in STATION_REGISTRY.

    Returns
    -------
    list of raw sighting dicts (pray-calc-ml schema)
    """
    log.info("Loading GaN-MN CSV: %s", csv_path)

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        on_bad_lines="skip",
        low_memory=False,
        usecols=["received_utc", "received_adjusted", "sqmle_serial_number",
                 "nsb", "temperature", "device_code"],
    )

    df["received_utc"] = pd.to_datetime(df["received_utc"], utc=True, errors="coerce")
    df["received_adjusted"] = pd.to_datetime(df["received_adjusted"], errors="coerce")
    df["nsb"] = pd.to_numeric(df["nsb"], errors="coerce")
    df = df.dropna(subset=["received_utc", "nsb", "device_code"])
    df = df[df["nsb"] > 0].copy()

    if station_filter:
        df = df[df["device_code"].isin(station_filter)]
    else:
        known_codes = set(STATION_REGISTRY.keys())
        unknown = set(df["device_code"].unique()) - known_codes
        if unknown:
            log.info(
                "Skipping %d stations with no coordinates in registry: %s",
                len(unknown), sorted(unknown),
            )
        df = df[df["device_code"].isin(known_codes)]

    if df.empty:
        log.warning("No usable rows after filtering: %s", csv_path)
        return []

    stations = df["device_code"].unique()
    log.info("Processing %d stations from %s", len(stations), csv_path.name)

    all_records: list[dict] = []

    for station_code in sorted(stations):
        reg = STATION_REGISTRY.get(station_code)
        if reg is None:
            log.warning("No registry entry for %s — skipping", station_code)
            continue

        station_name, lat, lng, elevation_m = reg

        df_sta = df[df["device_code"] == station_code].sort_values("received_utc").reset_index(drop=True)

        # Need received_adjusted as datetime for offset calculation
        df_sta["received_adjusted"] = pd.to_datetime(df_sta["received_adjusted"], errors="coerce")
        df_sta = df_sta.dropna(subset=["received_adjusted"])

        utc_offset_h = _infer_utc_offset(df_sta)

        log.info(
            "Station %s (%s): lat=%.4f lng=%.4f utc_offset=%+.0f rows=%d",
            station_code, station_name, lat, lng, utc_offset_h, len(df_sta),
        )

        obs = _make_observer(lat, lng, elevation_m)
        dates = sorted(df_sta["received_utc"].dt.date.unique())
        processed_nights: set = set()

        for local_date in dates:
            night_key = (station_code, local_date)
            if night_key in processed_nights:
                continue
            processed_nights.add(night_key)

            try:
                sol_mid = _solar_midnight_utc(local_date, lat, lng)
            except Exception as exc:
                log.warning("solar_midnight failed for %s %s: %s", station_code, local_date, exc)
                continue

            night_start = sol_mid - timedelta(hours=12)
            night_end = sol_mid + timedelta(hours=12)

            ns = pd.Timestamp(night_start, tz="UTC")
            ne = pd.Timestamp(night_end, tz="UTC")

            df_night = df_sta[
                (df_sta["received_utc"] >= ns) & (df_sta["received_utc"] <= ne)
            ].copy()

            if len(df_night) < MIN_DARK_ROWS:
                continue

            night_records = _process_night(
                df_night, lat, lng, station_code, station_name,
                local_date, utc_offset_h, elevation_m, obs,
            )
            all_records.extend(night_records)
            if night_records:
                log.debug(
                    "Night %s %s: %d records", station_code, local_date, len(night_records)
                )

    log.info("Total twilight events from %s: %d", csv_path.name, len(all_records))
    return all_records


def process_gan_mn_directory(
    data_dir: Path,
    pattern: str = "GaN-MN_*.csv",
    station_filter: Optional[set[str]] = None,
) -> list[dict]:
    """
    Process all GaN-MN CSV files matching pattern in data_dir.

    Returns combined list of all twilight event records.
    """
    csv_files = sorted(data_dir.glob(pattern))
    if not csv_files:
        log.warning("No CSV files found in %s matching %s", data_dir, pattern)
        return []

    all_records: list[dict] = []
    for csv_path in csv_files:
        records = process_gan_mn_csv(csv_path, station_filter=station_filter)
        all_records.extend(records)

    log.info(
        "Grand total from %d file(s): %d twilight events",
        len(csv_files), len(all_records),
    )
    return all_records


# --- CLI ---------------------------------------------------------------------


if __name__ == "__main__":
    import argparse
    import csv
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Extract Fajr/Isha twilight events from GaN-MN SQM-LE data"
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="Input CSV file(s) or directory containing GaN-MN CSVs",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output CSV path. Defaults to stdout.",
    )
    parser.add_argument(
        "--stations",
        nargs="*",
        default=None,
        help="Station device_code values to process (e.g. TBT Dal Oam). Default: all known.",
    )
    parser.add_argument(
        "--list-stations",
        action="store_true",
        help="Print all stations in the registry and exit.",
    )
    args = parser.parse_args()

    if args.list_stations:
        print(f"{'Code':<8} {'Lat':>8} {'Lng':>9} {'Elev':>6}  Location")
        print("-" * 70)
        for code, (name, lat, lng, elev) in sorted(STATION_REGISTRY.items()):
            print(f"{code:<8} {lat:>8.4f} {lng:>9.4f} {elev:>6.0f}  {name}")
        sys.exit(0)

    station_filter = set(args.stations) if args.stations else None
    all_records: list[dict] = []

    for inp in args.input:
        p = Path(inp)
        if p.is_dir():
            records = process_gan_mn_directory(p, station_filter=station_filter)
        else:
            records = process_gan_mn_csv(p, station_filter=station_filter)
        all_records.extend(records)

    if not all_records:
        log.warning("No twilight events extracted.")
        sys.exit(0)

    fieldnames = [
        "prayer", "date_local", "time_local", "utc_offset",
        "lat", "lng", "elevation_m", "source", "notes",
    ]

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_records)
    if args.output:
        out.close()
        log.info("Wrote %d records to %s", len(all_records), args.output)
    else:
        log.info("Wrote %d records to stdout", len(all_records))
