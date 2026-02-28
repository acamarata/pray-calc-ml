# Data Sources

Complete citation table for all sighting records in the dataset.

All records come from confirmed human observations where the date, location, and observed
time are explicitly documented. No aggregate statistics or angle guesses are used as ground
truth. Each record is independently back-calculated using PyEphem.

Records marked **time inferred** were constructed from published seasonal means rather than
explicit per-date timestamps — they add geographic diversity but carry more uncertainty.

---

## Primary Source

### OpenFajr Project — Birmingham, UK

| Field | Value |
| --- | --- |
| Records | ~4,018 Fajr observations (after quality filter: ~4,087) |
| Location | Birmingham, UK — 52.4862°N, 1.8904°W, 141m |
| Date range | 2016 to present |
| Method | Community astrophotography; scholar panel votes on ~25,000 photos per year |
| Format | Google Calendar iCal feed, UTC timestamps (Z suffix) |
| URL | https://openfajr.org |
| Collector | `src/collect/openfajr.py` |

This is the only known machine-readable dataset of per-date confirmed naked-eye Fajr
observations anywhere in the world. It provides ~98% of the Fajr training data.

---

## Manually Compiled Sources

### United Kingdom

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Blackburn, Lancashire | 53.750°N | 2.483°W | 120m | 29 Fajr + 32 Isha | Fajr + Isha | Naked eye, 6 Imams, 11 months | Miftahi 2007 via Shaukat 2015 booklet, 1987-1988 |
| Exmoor National Park | 51.15°N | 3.65°W | 430m | 8 | Fajr + Isha | Naked eye, multi-observer | Asim Yusuf, *Shedding Light on the Dawn*, ISBN 978-0-9934979-1-9, 2017 |

### Egypt

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kottamia Observatory | 29.932°N | 31.825°E | 411m | 3 | Fajr | Naked eye + Canon camera | Marzouk et al. 2025, Springer AUASS, per-night D0 from Figs 1-5 |
| Kharga Oasis | 25.300°N | 30.167°E | 40m | 2 | Fajr | Canon camera | Marzouk et al. 2025, Springer AUASS, per-night D0 from Figs 7-8 |
| Aswan | 23.803°N | 32.492°E | 210m | 4 | Fajr | Nikon + Canon camera | Marzouk et al. 2025, Springer AUASS, per-night D0 from Figs 10-21 |
| Fayum | 29.283°N | 30.050°E | 50m | 2 | Fajr | CCD + Canon camera | Marzouk et al. 2025, Springer AUASS, per-night D0 from Figs 25-27 |
| Kottamia Observatory | 29.929°N | 31.825°E | 477m | 6 | Fajr + Isha | Photoelectric + naked eye | Hassan et al., NRIAG J. 3:23-26, 2014 |
| Wadi Al Natron | 30.5°N | 30.15°E | 23m | 7 | Fajr + Isha | Naked eye | Semeida & Hassan, BJBAS 7:286-290, 2018 |

### Saudi Arabia and Arabian Peninsula

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Riyadh | 25.767°N | 47.200°E | 540m | 13 | Fajr | Naked eye + Nikon D70 | Taha et al. 2025, EJSAS 3(1):4-17, per-night D0 from Table 7 |
| Hail | 27.52°N | 41.70°E | 1020m | 8 | Fajr + Isha | Naked eye, 32 selected nights | Khalifa, NRIAG J. 7:22-28, 2018 |

### Mauritania

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Jeneifisa (Mur.1) | 20.850°N | 14.383°W | 170m | 5 | Fajr | Naked eye, deep Saharan desert | Taha et al. 2025, EJSAS 3(1):4-17, per-night D0 from Table 9 |
| Jorf (Mur.2) | 20.250°N | 15.283°W | 91m | 5 | Fajr | Naked eye, deep Saharan desert | Taha et al. 2025, EJSAS 3(1):4-17, per-night D0 from Table 9 |

### Malaysia

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pekan, Pahang | 3.408°N | 103.356°E | 5m | 1 | Fajr | DSLR + SQM | Kassim Bahali et al. 2019, IJMET 10(2):1136-1150, Table 6 |
| Dungun, Terengganu | 4.795°N | 103.426°E | 5m | 3 | Fajr | DSLR + SQM | Kassim Bahali et al. 2019, IJMET 10(2):1136-1150, Table 6 |
| Sabang, Aceh | 5.876°N | 95.339°E | 5m | 5 | Fajr | DSLR + SQM | Kassim Bahali et al. 2019, IJMET 10(2):1136-1150, Table 6 |
| Kuala Lumpur | 3.14°N | 101.69°E | 40m | 4 | Fajr | DSLR + SQM | Kassim Bahali et al., Sains Malaysia 47(11):2797-2805, 2018 |
| Kuala Terengganu | 5.283°N | 103.099°E | 5m | 1 | Fajr | DSLR | Kassim Bahali 2018, Sains Malaysiana Fig 4 |

### Indonesia (Basthoni 2022 SQM Network)

1,621 per-night SQM records across 46 Indonesian sites, extracted from all four appendices of
Basthoni's 2022 PhD dissertation at UIN Walisongo. Each record is a direct instrument measurement
where the Fajr depression angle was determined by linear fitting of SQM time-series data.

#### Lampiran 2 (Dark, >= 21.3 mpsas): 637 records, 10 sites

| Location | Lat | Lng | Elev | Records | Method | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Karimunjawa | 5.823°S | 110.491°E | 1m | 252 | SQM time-series, linear fitting | Basthoni 2022, Lampiran 2 |
| Agam, W. Sumatra | 0.204°S | 100.320°E | 855m | 151 | SQM time-series | Basthoni 2022, Lampiran 2 |
| Garut, W. Java | 7.650°S | 107.692°E | 10m | 101 | SQM time-series | Basthoni 2022, Lampiran 2 |
| Banyuwangi, E. Java | 8.028°S | 114.425°E | 1m | 60 | SQM time-series | Basthoni 2022, Lampiran 2 |
| Biak, Papua | 1.174°S | 136.101°E | 47m | 39 | SQM time-series | Basthoni 2022, Lampiran 2 |
| Masalembu | 5.586°S | 114.436°E | 1m | 10 | SQM time-series | Basthoni 2022, Lampiran 2 |
| 4 more sites | various | various | 1-1282m | 24 | SQM time-series | Basthoni 2022, Lampiran 2 |

#### Lampiran 3 (Somewhat Dark, 20.2-21.2 mpsas): 337 records, 9 sites

| Location | Lat | Lng | Elev | Records | Method | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Bosscha, W. Java | 6.817°S | 107.617°E | 1300m | 189 | SQM time-series | Basthoni 2022, Lampiran 3 |
| Biak, Papua | 1.174°S | 136.101°E | 47m | 109 | SQM time-series | Basthoni 2022, Lampiran 3 |
| Pontianak, W. Kalimantan | 0.050°S | 109.334°E | 10m | 17 | SQM time-series | Basthoni 2022, Lampiran 3 |
| 6 more sites | various | various | 1-855m | 22 | SQM time-series | Basthoni 2022, Lampiran 3 |

#### Lampiran 4 (Somewhat Bright, 19.1-20.1 mpsas): 418 records, 9 sites

| Location | Lat | Lng | Elev | Records | Method | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Mangkangkulon, Semarang | 6.967°S | 110.291°E | 5m | 154 | SQM time-series | Basthoni 2022, Lampiran 4 |
| Pasuruan, E. Java | 7.617°S | 112.908°E | 6m | 87 | SQM time-series | Basthoni 2022, Lampiran 4 |
| Pontianak, W. Kalimantan | 0.050°S | 109.334°E | 10m | 59 | SQM time-series | Basthoni 2022, Lampiran 4 |
| Subang, W. Java | 6.567°S | 107.750°E | 110m | 59 | SQM time-series | Basthoni 2022, Lampiran 4 |
| 5 more sites | various | various | 1-855m | 59 | SQM time-series | Basthoni 2022, Lampiran 4 |

#### Lampiran 5 (Bright/Urban, < 19.1 mpsas): 229 records, 18 sites

| Location | Lat | Lng | Elev | Records | Method | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Medan, N. Sumatra | 3.595°N | 98.672°E | 22m | 28 | SQM time-series | Basthoni 2022, Lampiran 5 |
| Depok, W. Java | 6.383°S | 106.830°E | 150m | 15 | SQM time-series | Basthoni 2022, Lampiran 5 |
| Paopao, Central Sulawesi | 0.917°S | 119.850°E | 50m | 13 | SQM time-series | Basthoni 2022, Lampiran 5 |
| 15 more sites | various | various | 1-1300m | 173 | SQM time-series | Basthoni 2022, Lampiran 5 |

### Indonesia (Other Sources)

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BRIN Mt. Timau, NTT | 9.6°S | 123.8°E | 1282m | 59 Fajr | Fajr | SQM-LE continuous | BRIN multistation network, data/raw/raw_sightings/ |
| 7 BRIN stations | various | various | 2-1282m | 577 Isha | Isha | SQM-LE continuous | BRIN multistation network |

### North America

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ithaca, NY, USA | 42.44°N | 76.50°W | 270m | 2 | Fajr | Naked eye, 3 observers | Omar Afzal via Shaukat 2015 booklet, Sep 1991 |
| Tando Adam, Pakistan | 25.76°N | 68.66°E | 25m | 2 | Fajr | Naked eye | Ludhianvi 1975 via Shaukat 2015 booklet, Jun 1970 |

### Europe

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pampigny, Switzerland | 46.57°N | 6.39°E | 570m | 1 | Fajr | Camera observation | Ouared via Shaukat 2015 booklet, Jun 2016 |

---

## Source Quality Summary

Dataset counts as of pipeline run 2026-02-28: **5,871 Fajr + 46 Isha**

| Tier | Description | Sources | Approx count |
| --- | --- | --- | --- |
| 1 — Voted astrophotography | OpenFajr Birmingham iCal | OpenFajr | ~4,018 Fajr |
| 2 — Instrumental (SQM), per-night | Basthoni 2022 PhD, 46 Indonesian sites (Lampiran 2-5) | 1 source, 46 sites | ~1,621 Fajr |
| 3 — Instrumental (DSLR/SQM), per-night | Kassim Bahali 2018+2019, BRIN multistation | 3 sources | ~70 Fajr+Isha |
| 4 — Multi-observer naked eye, per-date | Blackburn UK (29+32), Asim Yusuf UK, Taha Riyadh+Mauritania | 4 sources | ~95 Fajr+Isha |
| 5 — Camera/instrument per-night (D0 from paper) | Marzouk 2025 Egypt, Khalifa 2018 Hail | 2 sources | ~19 Fajr+Isha |
| 6 — Single observer, explicit timestamps | Shaukat booklet sites, moonsighting.com | 5+ sources | ~12 Fajr+Isha |

---

## Data Availability Assessment

After an extensive search (February 2026) covering >80 academic sources and community programs:

**What exists at scale:** Only one known machine-readable per-date observation feed exists: OpenFajr Birmingham (~4,018 records). The second-largest source is Basthoni's 2022 PhD dissertation from UIN Walisongo, with 1,621 per-night SQM records across 46 Indonesian sites (now fully extracted from all four appendices). All other sources publish per-date tables in academic papers (a few dozen records each) or aggregate D0 statistics only.

**What the global research corpus contains:** ~8-15k verified per-date records in total across all known published sources. Most Egyptian, Indonesian, Malaysian, Pakistani, and Middle Eastern research papers report seasonal mean D0 values, not per-date tables.

**Confirmed negative search results (Feb 2026):** Pakistan (moonsighting.com, Ruet-e-Hilal), Sudan, East Africa, Central Asia, Faid et al. 2024 per-night data (84 observations unpublished), Herdiwijaya per-night tables (83 data points visible in scatter plots only). Globe at Night SQM archives are night-sky brightness only, not prayer time observations.

## Priority Gaps

The most critical data gaps by region and prayer:

| Region | Prayer | Gap | Potential source |
| --- | --- | --- | --- |
| All regions | Isha | Only 46 records total | Shafaq al-Abyad observation logs; contact NRIAG researchers |
| South America | Fajr + Isha | Zero records | Muslim community programs in Brazil, Argentina, Colombia |
| High latitudes 55°N+ | Fajr | Zero records | Scandinavian Muslim communities, northern Canada |
| Sub-Saharan Africa | Fajr | Very few records | West African observation networks |
| Central Asia | Fajr + Isha | Zero records | Uzbekistan, Kazakhstan, Afghanistan |
| Long-running SQM archives | Fajr + Isha | Per-date data held by researchers, not published | Direct contact with NRIAG Egypt, OIF UMSU, Faid et al. 2024 |

---

## How to Contribute

If you have access to per-date sighting records with explicit times, dates, and locations,
open `src/collect/verified_sightings.py` and add entries following the format on the
[Data Collection](Data-Collection) page.

To propose a citation for review, open an issue on the GitHub repository with:
- Full bibliographic citation
- Location coordinates and elevation
- Date range of the observation program
- How many individual per-date records are published

---

*[← Architecture](Architecture) · [Research Notes →](Research-Notes)*
