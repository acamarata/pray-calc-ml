# Data Sources Log

Comprehensive log of all data sources searched and their ingestion status.

For per-source citations, see [Data Sources](Data-Sources).

---

## Dataset Status

| Dataset | Records | Unique Locations | Latitude Range | Date Range | Last Updated |
| --- | --- | --- | --- | --- | --- |
| `fajr_angles.csv` | 5,871 | 110 | -9.6° to 53.8° | 1970-2026 | 2026-02-28 |
| `isha_angles.csv` | 46 | 5 | -33.9° to 53.8° | 1985-2022 | 2026-02-28 |

Target: 100,000 Fajr + 100,000 Isha records.

Only genuinely human-observed data is in the pipeline. Computed/circular data (Aladhan API,
JAKIM e-Solat, Diyanet fixed-angle schedules, bulk-generated CSVs from fixed D0 angles) has
been moved to `data/raw/excluded/` and is NOT ingested.

### Source Quality Tiers

| Tier | Description | Fajr | Isha |
| --- | --- | --- | --- |
| T1: DSLR verified | Per-night astrophotography reviewed by scholars (OpenFajr) | ~4,018 | 0 |
| T2: Per-night SQM | Instrument-measured depression angles (Basthoni 2022, BRIN) | ~1,621 | 0 |
| T3: Per-night observed | DSLR campaigns, naked-eye logs with individual dates | ~150 | ~46 |
| T4: Aggregate D0 | Times back-calculated from a published mean observed angle | ~80 | 0 |

---

## Ingested Sources

### A. Community Observation Feeds

| Source | Location | Records | Prayer | Tier | Status |
| --- | --- | --- | --- | --- | --- |
| OpenFajr | Birmingham, UK (52.49°N, 1.89°W) | ~4,018 | Fajr | T1 | INGESTED |

### B. Instrumental SQM Per-Night Data

| Source | Location | Records | Prayer | Tier | Status |
| --- | --- | --- | --- | --- | --- |
| Basthoni 2022 PhD, Lampiran 2 | 10 Indonesian dark-sky sites | 637 | Fajr | T2 | INGESTED |
| Basthoni 2022 PhD, Lampiran 3 | 9 Indonesian somewhat-dark sites | 337 | Fajr | T2 | INGESTED |
| Basthoni 2022 PhD, Lampiran 4 | 9 Indonesian somewhat-bright sites | 418 | Fajr | T2 | INGESTED |
| Basthoni 2022 PhD, Lampiran 5 | 18 Indonesian bright/urban sites | 229 | Fajr | T2 | INGESTED |
| BRIN Mt. Timau | NTT, Indonesia (9.6°S, 123.8°E) | 59 | Fajr | T2 | INGESTED |

### C. Academic Paper Per-Date Tables

| Source | Location | Records | Prayer | Tier | Status |
| --- | --- | --- | --- | --- | --- |
| Kassim Bahali 2019 JATMA | 21 Malaysian + Indonesian sites | ~78 | Fajr | T3 | INGESTED |
| Kassim Bahali 2018 Sains Mal. | Pekan, KT Malaysia | ~10 | Fajr | T3 | INGESTED |
| Kassim Bahali 2019 IJMET | Pekan, Dungun, Sabang | ~9 | Fajr | T3 | INGESTED |
| Abdel-Hadi & Hassan 2022 | 5 Malaysian sites | ~20 | Fajr + Isha | T3 | INGESTED |
| Taha et al. 2025 | Riyadh, Jeneifisa, Jorf | 23 | Fajr | T3 | INGESTED |
| Marzouk et al. 2025 | 4 Egyptian sites | 11 | Fajr | T3 | INGESTED |
| Khalifa et al. 2018 | Hail, Saudi Arabia | ~8 | Fajr | T3 | INGESTED |
| Hassan et al. 2014 | Kottamia, Baharia Egypt | ~6 | Fajr + Isha | T3 | INGESTED |
| Semeida & Hassan 2018 | Wadi Al Natron, Egypt | ~7 | Fajr + Isha | T3 | INGESTED |
| Miftahi/Shaukat 2015 | Blackburn, UK | 29 + 32 | Fajr + Isha | T3 | INGESTED |
| Asim Yusuf 2017 | Exmoor, UK | ~8 | Fajr + Isha | T3 | INGESTED |
| Moonsighting.com | Various | ~2 | Fajr | T3 | INGESTED |
| Walisongo 2022 | Sulawesi | ~10 | Fajr | T3 | INGESTED |

### D. Excluded Sources (in `data/raw/excluded/`)

These were collected but produce circular or computed data that would not train the ML model:

| Source | Why Excluded |
| --- | --- |
| Aladhan API (MWL, ISNA, HiLat) | Fixed-angle algorithm outputs (18°, 15°) |
| JAKIM e-Solat (waktusolat.app) | Fixed 20° Fajr / 18° Isha algorithm |
| Diyanet Turkey | Fixed-angle official schedule |
| Aggregate monthly CSVs (76 files) | Synthetic times from published mean D0 (circular) |
| BRIN Timau interpolated | Times at exactly -18° sun altitude (reference point, not observation) |
| OpenFajr CSV duplicates | Already fetched live by `fetch_openfajr()` |

---

## Source Search Results

### Repositories Searched

| Repository | Queries | Papers Found | Useful |
| --- | --- | --- | --- |
| Google Scholar | 20+ | 30+ papers | 12 with per-date data |
| ResearchGate | 15+ | 20+ papers | 8 with usable tables |
| Academia.edu | 10+ | 10+ papers | 4 with per-date data |
| Semantic Scholar | 10+ | 15+ papers | 3 usable |
| DuckDuckGo web | 39 rotating queries | 100+ URLs | 5 new datasets |
| data.brin.go.id | BRIN datasets | 2 datasets | Both ingested |
| UIN Walisongo eprints | Basthoni 2022 | 1 dissertation | 1,621 records |
| Globe at Night | 2024 CSV tested | 14,449 observations | 0 usable (evening only) |

### Confirmed Negative Results (Feb 2026)

No per-night Fajr/Isha observation data found for:

- Pakistan (Ruet-e-Hilal, moonsighting.com Pakistan)
- Sudan, East Africa
- Central Asia (Uzbekistan, Kazakhstan, Afghanistan)
- South America
- Scandinavia (above 54°N)
- Iran (per-night data)
- Faid et al. 2024 (84 observations, data unpublished)
- Herdiwijaya per-night tables (83 data points in scatter plots only, no extractable table)

---

## Ingestion Pipeline

All sources flow through:

```text
Source data --> data/raw/raw_sightings/{source}.csv  OR  src/collect/verified_sightings.py
    --> python -m src.pipeline --no-elevation-lookup
    --> data/processed/fajr_angles.csv
    --> data/processed/isha_angles.csv
```

CSV format for raw_sightings: `prayer, date_local, time_local, utc_offset, lat, lng, elevation_m, source, notes`

---

*[← Data Sources](Data-Sources) . [Research -->](Research) . [Home](Home)*
