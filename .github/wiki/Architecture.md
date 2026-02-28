# Architecture

This page explains how the pipeline works end-to-end: how raw sighting records become
training data, what each module does, and how the pieces fit together.

---

## Overview

```
Raw sighting data
  ↓
[openfajr.py]      OpenFajr iCal feed (Birmingham, UK, 2016-present)
[sightings.py]     Manually compiled records (35+ locations worldwide)
[geocode.py]       Geocoding: city/region names → lat/lng
  ↓
Standardized records: { date, lat, lng, elevation_m, local_time, utc_offset }
  ↓
[elevation.py]     Open-Elevation API: fill missing elevation_m values
  ↓
[angle_calc.py]    PyEphem back-calculation: UTC moment → solar depression angle
  ↓
[pipeline.py]      Quality filter: drop implausible angles (< 7° Fajr / < 10° Isha)
  ↓
data/processed/fajr_angles.csv
data/processed/isha_angles.csv
  ↓
[01_exploratory_analysis.ipynb]   EDA + linear baseline + gradient boosting
```

---

## Modules

### `src/pipeline.py`

The master script. Runs all steps in sequence.

```
python -m src.pipeline [--no-elevation-lookup]
```

Responsibilities:
1. Call `openfajr.load()` and `verified_sightings.load()` to get raw records
2. Call `elevation.enrich()` to fill missing elevation values
3. Call `angle_calc.compute()` for each record
4. Drop records with implausible angles
5. Write `fajr_angles.csv` and `isha_angles.csv`

### `src/angle_calc.py`

The back-calculation engine. Takes a confirmed sighting record and returns the solar
depression angle at the observed moment.

**Method:**
1. Convert local time to UTC: `utc = local_dt - timedelta(hours=utc_offset)`
2. Set up a `PyEphem.Observer` with:
   - `lat` / `lon` from the record
   - `elevation` in metres
   - `pressure = 1013.25` hPa (standard atmosphere)
   - `temp = 15.0` °C (standard atmosphere)
3. Set `observer.date` to the UTC datetime
4. Call `ephem.Sun(observer)` to get the Sun's position
5. `depression_angle = -math.degrees(sun.alt)` (negative because sun is below horizon)

Atmospheric refraction is applied automatically by PyEphem at the specified pressure
and temperature. This is important: near the horizon, refraction can lift the apparent
solar disk by 0.5°-1.0°.

### `src/collect/openfajr.py`

Fetches and parses the OpenFajr Birmingham iCal feed from `calendar.google.com`.

The feed contains one `VEVENT` per day. The `DTSTART` field uses a `Z` suffix indicating
UTC. The `SUMMARY` field identifies the prayer type.

Known issue: around BST transition dates (late March, late October), a small number of
records have UTC times that produce physically impossible depression angles (sun above
horizon, or angle < 7°). These are caught by the quality filter.

### `src/collect/verified_sightings.py`

A Python list of manually compiled sighting records. Each record is a dictionary with:

| Field | Type | Description |
| --- | --- | --- |
| `prayer` | `"fajr"` or `"isha"` | Which prayer the sighting confirms |
| `date_local` | `"YYYY-MM-DD"` | Calendar date at the sighting location |
| `time_local` | `"HH:MM"` | 24-hour local time |
| `utc_offset` | `float` | Hours from UTC |
| `lat` | `float` | Decimal degrees (north positive) |
| `lng` | `float` | Decimal degrees (east positive) |
| `elevation_m` | `float` | Metres ASL (0 = will be looked up) |
| `source` | `str` | Citation |
| `notes` | `str` | Observer notes |

### `src/geocode.py`

Geocoding module. Converts city or region names to lat/lng coordinates using the
Nominatim API (OpenStreetMap). Used during the data ingestion pipeline when records
are provided with location names rather than explicit coordinates.

Caches results in `data/raw/geocode_cache.json` to avoid redundant API calls.

### `src/elevation.py`

Queries the Open-Elevation API for records where `elevation_m == 0`.

Batches requests (max 100 per call). Writes results back to the record dict.

---

## Data Flow in Detail

### 1. Raw record format

Every sighting, regardless of source, must eventually become:

```
date       YYYY-MM-DD (local calendar date)
lat        float, decimal degrees, north positive
lng        float, decimal degrees, east positive
elevation_m float, metres above sea level
time_local  HH:MM, 24-hour local time at sighting
utc_offset  float, hours from UTC (e.g. 1.0 for BST)
prayer     "fajr" or "isha"
source     citation string
notes      observer notes
```

If a record has a city name but no lat/lng, `geocode.py` fills it in.
If a record has `elevation_m == 0`, `elevation.py` fills it via the Open-Elevation API.

### 2. UTC conversion

```
utc_datetime = date + time_local - utc_offset (hours)
```

This is the single most error-prone step. Common failure modes:
- Using the wrong UTC offset (e.g. forgetting summer/winter DST)
- Using the standard timezone offset when the sighting date was in the alternate season
- Using the nominal timezone when the actual location's offset differs (e.g. parts of India)

All manually compiled records in `verified_sightings.py` include explicit `utc_offset`
values per-date, not per-timezone-name. This avoids DST ambiguity.

### 3. Solar position calculation

PyEphem computes solar altitude using the VSOP87 planetary theory, accurate to
approximately 0.01°. Atmospheric refraction is the main source of uncertainty:
the standard atmosphere model (1013.25 hPa, 15°C) is a good average but actual
refraction varies with local conditions. For twilight observations near -12° altitude,
refraction contributes negligibly.

**Depression angle = -altitude.** When the sun is below the horizon, `ephem.Sun.alt`
is negative. The depression angle is the absolute value.

### 4. Quality filter

Records are dropped if:
- `fajr_angle < 7°` — physically impossible (sun would still be in night)
- `isha_angle < 10°` — same reasoning for Isha
- Angle is NaN — calculation failed

These thresholds are conservative. Genuine sighting records produce 8°-21° for Fajr
and 11°-22° for Isha. Values below 7° / 10° indicate a data entry error, most commonly
a UTC offset mistake or a DST clock-change artifact.

---

## Output Schema

Both output CSVs share this schema:

| Column | Type | Description |
| --- | --- | --- |
| `date` | string | YYYY-MM-DD local date |
| `utc_dt` | string | ISO 8601 UTC datetime |
| `lat` | float | Decimal degrees |
| `lng` | float | Decimal degrees |
| `elevation_m` | float | Metres ASL |
| `day_of_year` | int | 1-366 |
| `fajr_angle` or `isha_angle` | float | Solar depression angle (°) |
| `source` | string | Citation |
| `notes` | string | Observer notes |

---

## Source Hierarchy

Records are ranked by data quality:

| Tier | Source type | Example |
| --- | --- | --- |
| 1 | Community astrophotography, panel-voted | OpenFajr Birmingham |
| 2 | DSLR + SQM instrumental observation | Kassim Bahali 2018 Malaysia |
| 3 | SQM photometry only | Saksono 2020 Indonesia |
| 4 | Multi-observer naked-eye, documented | Asim Yusuf UK, Hizbul Ulama UK |
| 5 | Single trained observer, per-date log | NRIAG Egypt individual nights |
| 6 | Published mean per season, time inferred | Hail Saudi Arabia (seasonal means) |

Tier 6 records (inferred times) are marked in `notes`. They contribute to geographic
diversity but carry more uncertainty than direct observations.

---

## Known Limitations

1. **Birmingham dominance.** The OpenFajr dataset provides ~4,000 records but all from
   one location at 52.5°N. Any ML model trained on this data will extrapolate to all
   other latitudes. Geographic diversity is the primary gap.

2. **Isha data scarcity.** Only ~43 Isha records vs ~4,100 Fajr records. The Isha network
   depends on Shafaq al-Abyad observations, which are less systematically documented.

3. **Atmospheric variability.** The standard atmosphere model (1013.25 hPa, 15°C) does
   not capture day-to-day refraction variation. On cold clear nights, refraction is
   higher; on hot dry nights, lower. This introduces ~0.1°-0.3° uncertainty per record.

4. **Observer skill variation.** Naked-eye observations depend on the observer's dark
   adaptation, experience, and site conditions. The depression angle for a given
   "true dawn" varies across observers by up to 2°.

---

*[← ML Crunching](ML-Crunching) · [Data Sources →](Data-Sources)*
