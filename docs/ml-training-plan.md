# ML Training Plan: Solar Depression Angle Prediction

## 1. Problem Statement

The pray-calc Dynamic Prayer Calculation (DPC) algorithm uses a solar depression angle to
determine Fajr and Isha prayer times. The canonical fixed angles (Fajr: 18°, Isha: 17°) do
not account for geographic variation, seasonal shifts, or atmospheric conditions. This pipeline
back-calculates empirical depression angles from verified twilight observations and trains a
regression model to predict the appropriate angle given location and date parameters.

The model output is a continuous regression value: the solar depression angle in degrees below
the horizon at which astronomical twilight (Fajr onset or Isha end) is observed. This feeds the
DPC coefficient table in pray-calc.

## 2. Dataset Description

Two processed CSVs in `data/processed/`:

- `fajr_angles.csv` — 48,668 verified Fajr observations
- `isha_angles.csv` — 34,529 verified Isha observations

Sources include GLOBE at Night sky-brightness readings, BSRN solar radiation stations, SURFRAD
network measurements, and SQM (Sky Quality Meter) deployments in Galicia, Madrid, and India.
Each row represents one twilight event with computed solar depression angle.

Full column documentation is in `data/SCHEMA.md`.

## 3. Feature Engineering

Input features used as model inputs:

| Feature | Derivation | Rationale |
|---|---|---|
| `lat` | Direct from CSV | Latitude affects solar arc and atmospheric path length |
| `lng` | Direct from CSV | Longitude affects local horizon geometry |
| `elevation_m` | Direct from CSV | Higher elevation reduces atmospheric scattering |
| `day_of_year` | Direct from CSV (1-365) | Seasonal variation in solar declination |
| `sin_doy` | sin(2π × day_of_year / 365) | Cyclic encoding to avoid Dec 31/Jan 1 discontinuity |
| `cos_doy` | cos(2π × day_of_year / 365) | Cyclic encoding pair |
| `abs_lat` | abs(lat) | Polar proximity is symmetric; captures high-latitude behavior |

Features deliberately excluded: `utc_dt` as a raw timestamp (leaks future information),
`source` (categorical noise), `notes` (free text).

No imputation is needed: the CSVs have no null values in the feature columns.

## 4. Model Architecture Options

**Option A: Ridge Regression (baseline)**
Interpretable, fast to train, no hyperparameter sensitivity. Establishes a performance floor.
Expected MAE: ~1.5-2.5°. Use as the primary baseline.

**Option B: Gradient Boosting Regressor (recommended)**
Captures nonlinear geographic and seasonal interactions without manual feature crosses.
scikit-learn `GradientBoostingRegressor` with 200 estimators, learning rate 0.05, max depth 4.
Expected MAE: ~0.8-1.5°.

**Option C: Neural Network**
Multi-layer perceptron with 2 hidden layers (64, 32 units), ReLU activations, dropout 0.1.
Higher capacity but adds training complexity with limited benefit on tabular data of this size.
Consider in P2 if gradient boosting does not reach the 0.5° MAE target.

The evaluate.py script implements Options A and B and reports metrics for both.

## 5. Cross-Validation Strategy

Time-aware split to avoid look-ahead bias. The dataset spans 2019-2024. Split:

- Training set: observations with `date < 2023-01-01` (~80%)
- Test set: observations with `date >= 2023-01-01` (~20%)

Standard random shuffle is not used because a random split would allow future observations
to inform past predictions — unrealistic for deployment. The time cutoff simulates the
model being deployed on data it has never seen.

No k-fold cross-validation is applied to the test set. A single time-aware holdout is
sufficient for this dataset size and avoids the complexity of time-series cross-validation
folds.

## 6. Evaluation Metrics

| Metric | Formula | Target |
|---|---|---|
| MAE | mean(abs(predicted - actual)) | < 1.0° for gradient boosting |
| RMSE | sqrt(mean((predicted - actual)²)) | < 1.5° |
| Precision at 0.5° | fraction where abs error < 0.5° | > 40% |
| R² | 1 - SS_res / SS_tot | > 0.5 |

MAE is the primary metric because pray-calc tolerates angle errors up to 1° before prayer
time offset exceeds one minute at mid-latitudes.

## 7. Training Pipeline Steps

1. Load `data/processed/fajr_angles.csv` and `isha_angles.csv`.
2. Construct cyclic features (`sin_doy`, `cos_doy`) and `abs_lat`.
3. Split on date cutoff (2023-01-01).
4. Fit a `StandardScaler` on the training set; transform both sets.
5. Train Ridge Regression baseline. Compute metrics on test set.
6. Train Gradient Boosting Regressor. Compute metrics on test set.
7. Print structured output: one block per prayer type (Fajr/Isha), one row per model.

## 8. Expected Outputs

Running `python src/evaluate.py` produces structured text to stdout:

```
=== Fajr angle prediction ===
Model              MAE    RMSE   R²    Prec@0.5°
Ridge              2.14   2.89   0.21  28.3%
GradientBoosting   0.91   1.32   0.63  42.1%

=== Isha angle prediction ===
Model              MAE    RMSE   R²    Prec@0.5°
Ridge              1.98   2.71   0.19  29.7%
GradientBoosting   0.85   1.24   0.67  44.6%
```

These numbers are illustrative. Actual values depend on dataset distribution. The script
exits with code 0 on success and 1 on any error.
