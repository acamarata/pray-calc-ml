# ML Crunching

This page explains how to run the machine learning analysis once you have a sufficient dataset.

---

## Prerequisites

### Software

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requirements include: `ephem`, `requests`, `pandas`, `numpy`, `scikit-learn`,
`matplotlib`, `jupyter`, `notebook`.

### Data

You need the processed CSV files in `data/processed/`:

```bash
python -m src.pipeline
```

This produces:
- `data/processed/fajr_angles.csv` — Fajr sightings with solar depression angles
- `data/processed/isha_angles.csv` — Isha sightings with solar depression angles

Without these files, the notebook will fail immediately. See [Data Collection](Data-Collection)
for the full pipeline guide.

---

## Step 1: Exploratory Analysis

Open the notebook:

```bash
jupyter notebook notebooks/01_exploratory_analysis.ipynb
```

Or run it headlessly and export:

```bash
jupyter nbconvert --to notebook --execute notebooks/01_exploratory_analysis.ipynb \
    --output notebooks/01_exploratory_analysis_executed.ipynb
```

The notebook covers nine analyses in sequence:

| Cell | Analysis | What to look for |
| --- | --- | --- |
| 1 | Load datasets | Record counts, column dtypes |
| 2 | Angle distributions | Histogram shape — should be roughly normal for Fajr |
| 3 | Latitude vs Fajr angle | The counter-intuitive equatorial-higher pattern |
| 4 | Birmingham seasonality | Sinusoidal pattern — confirms TOY effect |
| 5 | Latitude × Season interaction | Coloured scatter — should show lat × season interaction |
| 6 | Elevation vs Fajr angle | Weaker than lat/season but visible above 500m |
| 7 | Geographic coverage map | Reveals which regions are data-sparse |
| 8 | Linear regression baseline | R² and per-feature coefficients — sets the floor for ML |
| 9 | Isha analysis | Parallel analysis for Isha; currently sparse |

A well-populated dataset produces:
- Fajr angle distribution: mean ~13.5°, std ~1.8°, range roughly 8°-20°
- Fajr linear regression R² ≥ 0.35 (lat + doy + elevation)
- Latitude coefficient: negative (higher lat = lower angle at mid-latitudes)

If you see a flat distribution or R² < 0.1, check the pipeline output for dropped records.

---

## Step 2: Feature Engineering

The relevant features for predicting the solar depression angle at true dawn or dusk are:

| Feature | Column | Notes |
| --- | --- | --- |
| Latitude | `lat` | Decimal degrees |
| sin(day of year) | derived from `day_of_year` | Captures seasonality (365-day cycle) |
| cos(day of year) | derived from `day_of_year` | Paired with sin for full cycle encoding |
| Elevation | `elevation_m` | Metres above sea level |
| abs(lat) | derived | Symmetry across equator |

**Do not use longitude** as a feature. The depression angle at true dawn is independent of
longitude — it depends on which moment along the solar arc you are observing, not where you
are east/west.

**Do not use the observed time** as a feature. The angle is the prediction target; the time
is how you derived the angle. Using it as a feature would be data leakage.

Encode day of year as a unit circle pair:

```python
import numpy as np
df["doy_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
df["doy_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
```

---

## Step 3: Baseline Model

Before training any ML model, establish a linear baseline:

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
import numpy as np

features = ["lat", "doy_sin", "doy_cos", "elevation_m"]
X = df[features].values
y = df["fajr_angle"].values

lr = LinearRegression()
scores = cross_val_score(lr, X, y, cv=5, scoring="r2")
print(f"Linear baseline R²: {scores.mean():.3f} ± {scores.std():.3f}")
```

This gives the floor — any ML model should beat it. A linear model trained on the current
data produces approximately R² = 0.38.

---

## Step 4: Gradient Boosting (recommended)

Gradient boosting handles the non-linear lat × season interaction without explicit
feature crosses. It is the recommended first ML model for this dataset.

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_absolute_error
import numpy as np

features = ["lat", "doy_sin", "doy_cos", "elevation_m"]
X = df[features].values
y = df["fajr_angle"].values

model = GradientBoostingRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    random_state=42,
)

kf = KFold(n_splits=5, shuffle=True, random_state=42)
r2_scores = cross_val_score(model, X, y, cv=kf, scoring="r2")
mae_scores = -cross_val_score(model, X, y, cv=kf, scoring="neg_mean_absolute_error")

print(f"R²:  {r2_scores.mean():.3f} ± {r2_scores.std():.3f}")
print(f"MAE: {mae_scores.mean():.3f}° ± {mae_scores.std():.3f}°")
```

Target performance with a well-populated dataset (10k+ records):
- R² ≥ 0.55
- MAE ≤ 0.9°

---

## Step 5: Evaluating the Model

### Residual analysis

```python
from sklearn.model_selection import cross_val_predict
import matplotlib.pyplot as plt

model.fit(X, y)
y_pred = cross_val_predict(model, X, y, cv=5)
residuals = y - y_pred

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.scatter(y_pred, residuals, alpha=0.3, s=10)
plt.axhline(0, color="red")
plt.xlabel("Predicted angle (°)")
plt.ylabel("Residual (°)")
plt.title("Residuals vs Predicted")

plt.subplot(1, 2, 2)
plt.scatter(df["lat"], residuals, alpha=0.3, s=10)
plt.axhline(0, color="red")
plt.xlabel("Latitude")
plt.ylabel("Residual (°)")
plt.title("Residuals vs Latitude")
plt.tight_layout()
plt.show()
```

Watch for:
- Systematic residuals at high latitudes (55°N+) — the model may underfit
- Residuals correlated with season at a single location — the model may underfit seasonality
- Outliers > 3° from the line — these may be data entry errors or unusual atmospheric events

### Leave-location-out cross-validation

Standard k-fold mixes records from the same location across train/test splits, making the
model look better than it generalises to new locations. For this dataset, location-aware
CV is more informative:

```python
from sklearn.model_selection import LeaveOneGroupOut
import numpy as np

# Group by location (round lat/lng to 1 decimal for grouping)
groups = (df["lat"].round(1).astype(str) + "," + df["lng"].round(1).astype(str))

logo = LeaveOneGroupOut()
scores = cross_val_score(model, X, y, cv=logo, groups=groups, scoring="r2")
print(f"Leave-location-out R²: {scores.mean():.3f} ± {scores.std():.3f}")
```

This tests whether the model generalises to locations it has never seen.

---

## Step 6: Feature Importance

```python
model.fit(X, y)
importances = model.feature_importances_

for name, imp in zip(features, importances):
    print(f"  {name}: {imp:.3f}")
```

Expected order: `doy_sin` or `doy_cos` highest, then `lat`, then `elevation_m` lowest.
If `elevation_m` ranks above season features, the elevation records may be overrepresented.

---

## Step 7: Exporting the Model

Once satisfied with validation performance:

```python
import joblib
import json
import numpy as np

model.fit(X, y)

joblib.dump(model, "models/fajr_gbm.pkl")

# Export feature ranges for the pray-calc DPC algorithm
meta = {
    "features": features,
    "lat_range": [float(df["lat"].min()), float(df["lat"].max())],
    "elevation_range": [float(df["elevation_m"].min()), float(df["elevation_m"].max())],
    "angle_mean": float(y.mean()),
    "angle_std": float(y.std()),
    "n_records": int(len(df)),
    "r2_cv": float(r2_scores.mean()),
    "mae_cv": float(mae_scores.mean()),
}
with open("models/fajr_gbm_meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"Saved fajr_gbm.pkl ({len(df)} training records, R²={r2_scores.mean():.3f})")
```

---

## Current Model Status

The current dataset has:
- Fajr: ~4,100 records, but 98% are from Birmingham, UK. The model heavily reflects one location.
- Isha: ~43 records. Not enough to train a reliable ML model.

**The priority is data collection before further ML work.** A model trained only on Birmingham
Fajr data will predict Birmingham well and generalise poorly. The notebook's exploratory
analysis and linear baseline are meaningful now, but gradient boosting should wait for
broader geographic coverage.

Target before training a production model:
- Fajr: 10,000+ records from 100+ locations across all latitude bands
- Isha: 500+ records from 30+ locations

See [Data Collection](Data-Collection) for how to contribute new sighting records.

---

## Connecting to pray-calc

The output of the ML model feeds the DPC (Dynamic Prayer Calc) algorithm in
[pray-calc](https://github.com/acamarata/pray-calc). The DPC algorithm takes:

- Latitude
- Day of year
- Elevation

And returns a recommended depression angle for that location and date.

The current DPC implementation uses a simplified physics model. The ML model will replace
or calibrate the seasonal and latitude correction factors once sufficient data is available.

---

*[← Data Collection](Data-Collection) · [Architecture →](Architecture)*
