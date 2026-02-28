# Data Collection

This page explains how to collect sighting data, run the pipeline, and add new records.

---

## What data we collect

Each record in the dataset represents one confirmed human sighting with:

| Field | Description |
| --- | --- |
| Date | The calendar date of the sighting (local date) |
| Location | Latitude, longitude, and elevation in metres |
| Observed time | The local time at which the sighting occurred |
| UTC offset | The hours offset from UTC at that date and location |

The pipeline converts each record into a solar depression angle by back-calculating the sun's
position at the UTC moment of the sighting using PyEphem with atmospheric refraction.

**Not included:** calculated prayer times, angle guesses, or aggregate statistics. Only records
where an actual human reported "I saw true dawn at this time on this date at this location."

---

## Running the pipeline

### Prerequisites

```bash
# Python 3.10+
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Full run (recommended)

```bash
python -m src.pipeline
```

This does three things in sequence:

1. **Fetches the OpenFajr iCal feed** from `calendar.google.com` — ~4,018 community-verified
   Fajr records from Birmingham, UK, 2016-2026. Requires network access.
2. **Loads manually compiled records** from `src/collect/verified_sightings.py` — ~141 records
   from peer-reviewed studies across 35 locations worldwide.
3. **Looks up missing elevations** via the [Open-Elevation API](https://open-elevation.com) for
   any record where `elevation_m == 0`.

Output:
```
data/processed/fajr_angles.csv   — ~4,105 Fajr records
data/processed/isha_angles.csv   — ~43 Isha records
```

### Without elevation lookup

```bash
python -m src.pipeline --no-elevation-lookup
```

Skips the Open-Elevation API calls. Use this when:
- You're offline
- You want faster iteration while adding new records
- All records in `verified_sightings.py` already have non-zero elevations

### Interpreting the pipeline output

```
Loading OpenFajr Birmingham iCal feed...
  4018 Fajr records from OpenFajr
Loading manually verified sightings...
  141 manually compiled records
Computing solar depression angles...
  Dropping 11 record(s) with implausible angles (< 7.0° Fajr / < 10.0° Isha):
    FAJR 2021-03-27 ... angle=-18.71° — OpenFajr (openfajr.org)
    ...

Fajr dataset: 4105 records → data/processed/fajr_angles.csv
Isha dataset:  43 records → data/processed/isha_angles.csv
```

Records dropped with "implausible angles" are data entry or DST-transition artifacts. The
quality filter (7° for Fajr, 10° for Isha) removes physically impossible values. All dropped
records are logged so you can investigate them.

---

## Data sources

### Primary: OpenFajr (Birmingham, UK)

The [OpenFajr Project](https://openfajr.org) runs a continuous community astrophotography
program in Birmingham. A panel of scholars reviews daily sky photos and votes on the moment of
true dawn. The voted times are published as a public Google Calendar iCal feed.

- ~4,018 records, 2016-2026
- Location: 52.4862°N, 1.8904°W, 141m elevation
- All times are UTC (Z suffix in iCal)
- Fetched live by the pipeline — no local cache needed

This is the highest-quality source: actual community-reviewed per-date timestamps at a single
well-documented location. It provides 98% of the Fajr training data.

### Secondary: Manually compiled records

Located in `src/collect/verified_sightings.py`. These come from:

- Peer-reviewed academic papers (NRIAG Egypt, Malaysia, Indonesia, Saudi Arabia)
- Community observation programs (Hizbul Ulama UK, Asim Yusuf UK, Moonsighting.com)
- National religious body publications (AFIC Australia, Jordanian Awqaf, etc.)

See [Data Sources](Data-Sources) for the full citation table.

---

## Adding new sighting records

Open `src/collect/verified_sightings.py` and append to the `VERIFIED_SIGHTINGS` list:

```python
{
    "prayer": "fajr",              # "fajr" or "isha"
    "date_local": "2024-06-21",    # ISO date, local calendar date
    "time_local": "04:38",         # HH:MM, 24-hour, local time at moment of sighting
    "utc_offset": 1.0,             # hours from UTC (e.g. 1.0 for BST, -5.0 for EST, 5.5 for IST)
    "lat": 51.150,                 # decimal degrees (south = negative)
    "lng": -3.650,                 # decimal degrees (west = negative)
    "elevation_m": 430.0,          # metres above sea level (0 = will be looked up by API)
    "source": "Your citation here",
    "notes": "Any relevant notes about conditions, method, observer count, etc.",
}
```

### UTC offset tips

| Region | UTC offset |
| --- | --- |
| UK (BST, summer) | +1.0 |
| UK (GMT, winter) | 0.0 |
| Egypt / Eastern Europe (EET) | +2.0 |
| Egypt / EE (summer, EEST) | +3.0 |
| Saudi Arabia / Arabia Standard | +3.0 |
| Iran (IRST) | +3.5 |
| Iran (IRDT, summer) | +4.5 |
| UAE / Oman (GST) | +4.0 |
| Pakistan (PKT) | +5.0 |
| India / Sri Lanka (IST) | +5.5 |
| Bangladesh (BST) | +6.0 |
| Malaysia / Singapore (MYT) | +8.0 |
| Indonesia West (WIB) | +7.0 |
| Indonesia East (WIT) | +9.0 |
| Australia East (AEST, winter) | +10.0 |
| Australia East (AEDT, summer) | +11.0 |
| New Zealand (NZST) | +12.0 |
| New Zealand (NZDT) | +13.0 |
| US Eastern (EST) | -5.0 |
| US Eastern (EDT) | -4.0 |
| US Central (CST) | -6.0 |
| US Central (CDT) | -5.0 |
| West Africa (WAT) | +1.0 |
| East Africa (EAT) | +3.0 |
| South Africa (SAST) | +2.0 |

### Verifying a new record

After adding records, run the pipeline and check the output. A correctly entered record should
produce an angle between 8° and 21° for Fajr, or 11° and 22° for Isha. If the pipeline drops
your record (angle below the threshold), the time is too close to sunrise/sunset — recheck the
UTC offset and local time.

```bash
python -m src.pipeline --no-elevation-lookup 2>&1 | grep -A5 "Dropping"
```

---

## Priority gaps to fill

The Isha dataset is the most critical gap at ~43 records. Fajr has excellent Birmingham coverage
but needs more geographic diversity:

| Gap | What to look for |
| --- | --- |
| Isha (all regions) | Shafaq al-Abyad disappearance logs with explicit per-date timestamps |
| South America | Any Muslim community observation records with coordinates and times |
| Southeast Asia | Additional Indonesian/Malaysian per-night SQM data files |
| High latitudes (55°N+) | Scandinavian or northern Canadian observation logs |
| Sub-Saharan Africa | Observation records from West Africa, East Africa, Southern Africa |

---

*[← Home](Home) · [ML Crunching →](ML-Crunching)*
