# Dataset Schema: Verified Twilight Sightings

Documents all columns in the processed verified-sightings CSV files used for ML training.

**Files covered:**
- `data/processed/fajr_angles.csv` — Fajr (pre-dawn) twilight observations
- `data/processed/isha_angles.csv` — Isha (post-dusk) twilight observations

**Row count (as of latest build):**
- fajr_angles.csv: 48,668 rows
- isha_angles.csv: 34,529 rows

---

## Column Definitions

### `date`

- **Type:** string (ISO 8601 date)
- **Format:** `YYYY-MM-DD`
- **Example:** `2024-02-02`
- **Description:** Calendar date of the observation in UTC. Used for time-aware train/test splitting. Not used directly as a model feature.
- **Null policy:** Never null. Every row has a valid date.
- **Units:** N/A (date string)

---

### `utc_dt`

- **Type:** string (ISO 8601 datetime with UTC timezone)
- **Format:** `YYYY-MM-DD HH:MM:SS+00:00`
- **Example:** `2024-02-02 00:12:00+00:00`
- **Description:** UTC timestamp of the twilight event. The time component captures the moment of observation, used when computing solar position at the exact instant. Not used directly as a model feature to avoid timestamp leakage.
- **Null policy:** Never null.
- **Units:** N/A (timestamp)

---

### `lat`

- **Type:** float
- **Range:** -90.0 to 90.0
- **Example:** `-62.59334`
- **Description:** Geographic latitude of the observation site in decimal degrees. Negative values are south of the equator.
- **Null policy:** Never null.
- **Units:** Decimal degrees

---

### `lng`

- **Type:** float
- **Range:** -180.0 to 180.0
- **Example:** `15.46875`
- **Description:** Geographic longitude of the observation site in decimal degrees. Negative values are west of the prime meridian.
- **Null policy:** Never null.
- **Units:** Decimal degrees

---

### `elevation_m`

- **Type:** float
- **Range:** Unconstrained (negative values occur over ocean; positive values over land)
- **Example:** `-5007.54` (ocean), `432.0` (land station)
- **Description:** Elevation of the observation site in meters above sea level. Negative values are artifacts from ocean-based sky brightness sensors where the bathymetric elevation was used. Elevation affects the optical path through the atmosphere, which in turn affects the apparent twilight depression angle.
- **Null policy:** Never null.
- **Units:** Meters

---

### `day_of_year`

- **Type:** integer
- **Range:** 1 to 365 (366 in leap years)
- **Example:** `33`
- **Description:** Julian day of the year for the observation date. Day 1 is January 1. Used as a cyclic feature in the ML pipeline (encoded as sin/cos pair to avoid the year-boundary discontinuity). Correlated with solar declination.
- **Null policy:** Never null.
- **Units:** Day number (dimensionless)

---

### `fajr_angle` (fajr_angles.csv only)

- **Type:** float
- **Range:** Typically 5.0 to 25.0 degrees (outliers possible)
- **Example:** `9.508`
- **Description:** Computed solar depression angle below the horizon at the moment of Fajr (pre-dawn astronomical twilight onset). This is the target variable (y) for Fajr ML training. Positive values indicate degrees below the horizon. Computed by back-calculating the sun's altitude at the recorded twilight timestamp using NREL SPA.
- **Null policy:** Never null. Rows with uncomputable angles are excluded during cleaning.
- **Units:** Degrees (below horizon, positive)

---

### `isha_angle` (isha_angles.csv only)

- **Type:** float
- **Range:** Typically 5.0 to 25.0 degrees (outliers possible)
- **Example:** `16.074`
- **Description:** Computed solar depression angle below the horizon at the moment of Isha (post-dusk astronomical twilight end). This is the target variable (y) for Isha ML training. Same convention as fajr_angle: positive values are degrees below the horizon.
- **Null policy:** Never null.
- **Units:** Degrees (below horizon, positive)

---

### `source`

- **Type:** string (categorical)
- **Values:** `globe_at_night`, `bsrn`, `surfrad`, `galicia_sqm`, `madrid_sqm`, `india_twilight`, `majadahonda_sqm`, `gan_mn`, `tess`, `washetdonker`
- **Example:** `globe_at_night`
- **Description:** Data source identifier. Identifies which collection pipeline produced this row. Not used as a model feature (categorical with potential label-leakage). Used for stratified analysis and debugging.
- **Null policy:** Never null.
- **Units:** N/A (categorical label)

---

### `notes`

- **Type:** string (free text)
- **Example:** `""` (empty string is most common)
- **Description:** Optional annotation attached during data cleaning or manual curation. May contain flags like `high_elevation`, `coastal`, or quality notes from the source dataset. Not used in ML training.
- **Null policy:** May be empty string. Treat as optional metadata.
- **Units:** N/A (free text)

---

## Derived Features Used in Training

The following columns are computed during training and are not stored in the CSV:

| Derived feature | Formula | Purpose |
|---|---|---|
| `sin_doy` | sin(2π × day_of_year / 365) | Cyclic seasonal encoding |
| `cos_doy` | cos(2π × day_of_year / 365) | Cyclic seasonal encoding pair |
| `abs_lat` | abs(lat) | Polar proximity (symmetric across equator) |

These are constructed by `src/evaluate.py` at training time. See `docs/ml-training-plan.md`
for the full feature engineering rationale.
