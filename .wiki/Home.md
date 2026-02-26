# pray-calc-ml

A Python data science project that compiles human-verified Islamic prayer sighting records and
back-calculates solar depression angles. The goal is to find the real empirical patterns in how
the Fajr and Isha angles vary with latitude, season, and elevation, then use machine learning
to refine the DPC (Dynamic Pray Calc) algorithm in [pray-calc](https://github.com/acamarata/pray-calc).

## Pages

- [Data Collection](Data-Collection) — how to run the pipeline, add new sources, and expand the dataset
- [ML Crunching](ML-Crunching) — how to run the analysis notebook and train ML models
- [Architecture](Architecture) — how the pipeline works, data schema, quality filters
- [Data Sources](Data-Sources) — full citation table for all sighting records
- [Research Notes](Research-Notes) — academic paper summaries (not training data)

## Quick start

```bash
git clone https://github.com/acamarata/pray-calc-ml.git
cd pray-calc-ml
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Generate datasets (requires network for OpenFajr iCal + elevation API)
python -m src.pipeline

# Or skip the elevation API:
python -m src.pipeline --no-elevation-lookup
```

Output: `data/processed/fajr_angles.csv` and `data/processed/isha_angles.csv`

## Current dataset

| Dataset | Records | Locations | Latitude range | Date range |
| --- | --- | --- | --- | --- |
| Fajr | ~4,105 | 35 | -37.8° to 53.7° | 1985-2026 |
| Isha | ~43 | 20+ | -33.9° to 53.7° | 1985-2019 |

## Key finding

Near-equatorial sites (Malaysia, Indonesia, 2°-7°) show mean Fajr angles of 16°-17°, while
high-latitude sites (Birmingham, UK, 52°N) average ~13°. Seasonality is a significant second
factor — at 52°N, the Fajr angle has a ~3° peak-to-trough seasonal swing. Elevation shows a
smaller but real positive correlation.

The 18° fixed angle commonly used by ISNA and MWL overstates the observed true dawn angle at
virtually all well-documented sites.

---

*Part of the [acamarata](https://github.com/acamarata) Islamic computing library suite.*
