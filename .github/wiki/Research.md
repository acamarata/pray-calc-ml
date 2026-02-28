# Research

A running log of academic papers, discussions, and findings relevant to understanding Islamic
twilight angle data. This page documents what we know, what we are uncertain about, and what
questions remain open as we build the dataset.

For per-source citations, see [Data Sources](Data-Sources).
For detailed per-paper notes and regional summaries, see [Research Notes](Research-Notes).
For the complete list of sources searched, see [Data](Data).

---

## What the Data Measures

### The Two Twilight Thresholds

**Fajr (True Dawn / Subh Sadiq):** The moment when the false dawn (zodiacal light band) gives way
to the true dawn, a white-pink horizontal brightening along the eastern horizon that spreads.
This is a sky brightness threshold event, not a discrete astronomical event. Different observers
may disagree by 1-3 minutes on the same night.

The solar depression angle at this moment varies by latitude, season, elevation, and atmospheric
conditions. It is NOT a fixed 18, 15, or any other single value. That is the central finding
of the entire dataset.

**Isha (True Dusk / Shafaq al-Abyad):** The moment when the last remnant of white twilight
disappears in the west after sunset. The criterion is Shafaq al-Abyad (white twilight), not
Shafaq al-Ahmar (red twilight), which disappears earlier at a shallower depression angle.

Most instruments used in the literature measure when sky brightness crosses a threshold, which
corresponds to the human observation criterion.

### What "Solar Depression Angle" Means

The solar depression angle is the angle of the sun's centre below the geometric horizon, measured
in degrees. Positive values = sun below horizon. At civil twilight (6 degrees), there is enough light
for outdoor activity without artificial lighting. At astronomical twilight (18 degrees), the sky is
fully dark. True Fajr falls somewhere in between.

The pipeline back-calculates this angle using PyEphem given the UTC time of the observation and
the observer's coordinates. The result is what the sun's position was at the exact moment the
human reported seeing true dawn or dusk.

### Instruments Used in the Literature

**Naked eye:** The observer reports the moment they visually detect the onset of true dawn (Fajr)
or the disappearance of dusk light (Isha). Highly observer-dependent but matches the fiqh
(Islamic jurisprudence) definition. Inter-observer variation on clear nights is typically 2-5 min.

**SQM (Sky Quality Meter):** Measures sky brightness in magnitudes per square arcsecond (mpsas).
A threshold of 15-17 mpsas is used to define twilight onset. The exact threshold is calibrated
differently in different studies, which explains some inter-study variation in reported D0.

**DSLR astrophotography:** Camera captures the sky at timed intervals. A scholar panel or
algorithm identifies the frame where true dawn is visible. Used by OpenFajr Birmingham and
Kassim Bahali. Most objective and reproducible of the three methods.

**Photoelectric photometer:** Scientific instrument used at observatories (Kottamia Egypt,
NRIAG series). Highly accurate but not portable; limited to observatory sites.

---

## Key Finding: Latitude vs. Angle

The most counter-intuitive finding in the dataset is that equatorial sites show *higher*
depression angles than mid-latitude sites. The relationship is roughly:

| Latitude band | Mean Fajr angle | Representative sources |
| --- | --- | --- |
| 50-55 N (UK) | 12-14 degrees | OpenFajr Birmingham, Hizbul Ulama, Asim Yusuf |
| 30-40 N (Egypt, Saudi) | 13-15 degrees | NRIAG series, Khalifa 2018 Hail, Taha 2025 |
| 20-30 N (Pakistan, Mauritania) | 14-15 degrees | Moonsighting.com, Taha 2025 Mauritania |
| 0-10 N/S (Malaysia, Indonesia) | 12-20 degrees | Basthoni 2022, Kassim Bahali, BRIN |

The wide range at equatorial sites (12-20 degrees) is driven almost entirely by light pollution.
Basthoni 2022 documents this gradient across 1,621 per-night SQM observations at 46 Indonesian sites:

| Sky Quality (mpsas) | Category | Mean Fajr D0 | Nights |
| --- | --- | --- | --- |
| >= 21.3 | Dark/pristine | 16.3 degrees | 594 |
| 20.2-21.2 | Somewhat dark | 14.1 degrees | 380 |
| 19.1-20.1 | Somewhat bright | 13.4 degrees | 418 |
| < 19.1 | Bright/urban | 12.8 degrees | 229 |

**Why equatorial sites show higher angles at dark sites:** At low latitudes, the sun rises at a
steep angle. A given depression angle below the horizon corresponds to a shorter time before
sunrise, so the twilight is "compressed" in time. At high latitudes, the sun's path is shallower.
The same 13 degree depression occurs much further before sunrise in London than in Kuala Lumpur.

**Implication for prayer time calculation:** Using a fixed 18 degrees (ISNA, MWL) for all latitudes
overstates the Fajr angle at virtually all documented sites. The DPC algorithm in pray-calc aims
to model this latitude and sky-quality dependence.

---

## Key Finding: Season Effect

At mid-to-high latitudes, Fajr angle shows clear seasonal variation:

- Birmingham (52 N): approximately 3 degree peak-to-trough sinusoidal pattern, higher in winter, lower in summer
- Hail, Saudi Arabia (27 N): approximately 1-2 degree seasonal variation
- Near-equatorial sites: minimal seasonal variation

This pattern is consistent with the changing angle of the sun's ecliptic relative to the horizon
across seasons. In summer at high northern latitudes, the sun's path is more oblique and twilight
is prolonged, resulting in a shallower depression angle at the same sky brightness threshold.

---

## Key Finding: Light Pollution is the Dominant Factor

Sky quality is the single strongest predictor of observed depression angle, stronger even than
latitude. The evidence:

- Egypt NRIAG studies show remarkable consistency (14.5-14.7 degrees) across desert and Mediterranean sites, all with similarly dark skies
- Indonesia has the widest range (11.9-19.9 degrees) because sites span pristine islands to dense urban Java
- Malaysian studies confirm: Putrajaya urban (11.5 degrees) versus Sabah pristine (17.5 degrees)
- Desert sites across Saudi Arabia, Mauritania, and Egypt cluster tightly around 14-15 degrees with low variance (SD 0.3-0.6 degrees)

This means the ML model needs a sky brightness or light pollution covariate. Possible proxies:
population density within 50km, VIIRS nighttime radiance, or SQM zenith readings where available.

---

## Key Finding: Elevation Effect

Sites significantly above sea level consistently show higher angles than sea-level sites at
similar latitudes. Evidence:

| Site | Elevation | Mean Fajr | Nearby sea-level comparison |
| --- | --- | --- | --- |
| Bosscha/Lembang | 1300m | 13.7 degrees | Depok (150m, same latitude): 13.6 degrees |
| Hail, Saudi Arabia | 1020m | 14.0 degrees | Egypt desert sites: 14.5 degrees |
| Amfoang/Kupang | 1282m | 14.4 degrees | Biak sea level (47m): 13.4 degrees |
| Agam, W. Sumatra | 855m | 16.7 degrees | Pontianak (10m, similar lat): 12.3 degrees |

The effect is secondary to latitude, season, and light pollution. Atmospheric conditions (LP,
humidity, aerosols) confound the pure elevation signal.

---

## Open Questions

### 1. Light Pollution Bias

How much of the inter-study variation is light pollution versus genuine astronomical/geographic
variation? Should the ML model include a sky darkness covariate? Possible proxy: population
density within 50km, or average nighttime luminance from VIIRS/DMSP.

### 2. Isha Data Scarcity

Only 46 verified Isha (Shafaq al-Abyad) records exist in the dataset, compared to 5,871 Fajr.
Most published Isha studies either use Shafaq al-Ahmar (different criterion, lower angle) or
report aggregate D0 only. The Isha model cannot be meaningfully trained without more data.

### 3. SQM Threshold Calibration

Different SQM-based studies use different brightness thresholds to define twilight onset:

- Basthoni 2022: linear fitting of SQM time-series
- Kassim Bahali 2018/2019: 12-13 mpsas threshold
- BRIN Mount Timau: 18.0 mpsas reference point
- OIF UMSU: 15-16 mpsas
- Setyanto 2021: zodiacal light baseline fitting

Different thresholds produce different back-calculated depression angles. The notes column
documents the threshold used for each SQM source.

### 4. Aggregate vs. Per-Date Uncertainty

Approximately 5% of records are seasonal representative aggregates (4 per site, one per
equinox/solstice) computed from a published mean D0 angle. The uncertainty on these is
typically +/- 0.5 degrees but up to +/- 1 degree for older or less documented sources.

Per-date records from SQM or DSLR campaigns are more reliable. The ML model should weight
per-date records higher than aggregate records.

---

## Methodology: Back-Calculating the Angle

Every record in the dataset is produced by this calculation:

```python
import ephem
import math

def depression_angle(utc_dt, lat, lng, elevation_m):
    """
    Returns the solar depression angle in degrees at a given UTC datetime
    and observer position. Positive = sun below horizon.
    Uses PyEphem for high-precision solar position calculation.
    """
    sun = ephem.Sun()
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lng)
    obs.elevation = elevation_m
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')
    obs.pressure = 0  # no atmospheric refraction
    sun.compute(obs)
    alt_deg = math.degrees(float(sun.alt))
    return -alt_deg  # negative altitude = positive depression
```

The key design choice is `obs.pressure = 0`, which disables atmospheric refraction correction.
The returned angle is the true geometric depression angle, not the apparent angle as seen through
the atmosphere. This is consistent with how published D0 values are typically reported.

Basthoni 2022 SQM records bypass this calculation entirely. Those angles were measured directly
from SQM time-series data using linear fitting, loaded by `src/collect/precomputed_angles.py`.

---

## Academic Consensus

The published literature broadly agrees on these points:

1. **18 degrees is too high for most of the world.** The NRIAG Egypt series (13-14 degrees), UK
   observations (12-14 degrees), and desert sites (14-15 degrees) consistently show true Fajr at
   angles well below 18 degrees at mid-to-high latitudes.

2. **Malaysian/Indonesian standard of 20 degrees is too high.** The major SQM studies (Basthoni 2022,
   Kassim Bahali, OIF UMSU, BRIN Mount Timau) converge on 16-17 degrees for pristine equatorial
   sites, not 20 degrees.

3. **A latitude-dependent model is better than a fixed angle.** The pattern is clear: angle
   increases as latitude decreases toward the equator (at dark-sky sites).

4. **Light pollution is the strongest confound.** Urban sites consistently produce angles 3-5 degrees
   lower than dark-sky sites at the same latitude. Any predictive model must account for this.

---

## Data Gaps by Region

As of 2026-02-28 (5,871 Fajr / 46 Isha across 114 locations):

| Region | Observed Coverage | Priority |
| --- | --- | --- |
| South America | Zero records | High |
| Scandinavia (above 54 N) | Zero records | High |
| Sub-Saharan Africa | Zero per-night records | High |
| South Asia (Pakistan, Bangladesh, India) | 2 records (Tando Adam) | High |
| Central Asia | Zero records | Medium |
| Isha globally | Only 46 records total | Critical |
| Pacific Islands | Zero records | Low |

---

## Finding New Sources

Best strategies for expanding high-quality records:

1. **OpenFajr expansion:** Currently covers Birmingham only. Additional UK cities (Bradford,
   Leicester, Sheffield, Glasgow) would add 200-400 T1 records per year per city.

2. **Direct researcher outreach:** Outreach emails drafted in `research/outreach/` for 14
   institutions. The key contacts are: OIF UMSU Medan, Bosscha Observatory, NRIAG Egypt,
   Kassim Bahali (UTM), Herdiwijaya (ITB), BRIN/LAPAN, Faid (UNISZA).

3. **University thesis databases:** Indonesian and Malaysian Islamic universities publish theses
   with per-date SQM observation tables. IAIN/UIN repositories are searchable in Bahasa Indonesia.

4. **SQM data repositories:** Zenodo, Figshare, and institutional repositories. Search terms:
   "sky quality meter twilight", "SQM fajar subuh", "SQM astronomical twilight".

---

*[<-- Data](Data) . [Research Notes -->](Research-Notes) . [Home](Home)*
