"""
Train and evaluate regression models for solar depression angle prediction.

Inputs:  data/processed/fajr_angles.csv, data/processed/isha_angles.csv
Outputs: precision/recall/MAE structured report to stdout

Uses a time-aware 80/20 train/test split (cutoff 2023-01-01) to avoid
look-ahead bias. Evaluates two models: Ridge Regression (baseline) and
Gradient Boosting Regressor (recommended). See docs/ml-training-plan.md
for feature engineering rationale and architecture decisions.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


# ── Path resolution ────────────────────────────────────────────────────────────

def _repo_root() -> Path:
    """Walk up from this file until we find the data/processed/ directory."""
    candidate = Path(__file__).resolve().parent
    for _ in range(5):
        if (candidate / "data" / "processed").is_dir():
            return candidate
        candidate = candidate.parent
    raise FileNotFoundError(
        "Cannot locate data/processed/ directory. "
        "Run this script from within the pray-calc-ml repository."
    )


# ── Feature construction ───────────────────────────────────────────────────────

FEATURES = ["lat", "lng", "elevation_m", "day_of_year", "sin_doy", "cos_doy", "abs_lat"]

TRAIN_CUTOFF = "2023-01-01"  # time-aware split boundary


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add cyclic day-of-year encoding and absolute latitude.

    Cyclic sin/cos encoding prevents the year-boundary discontinuity
    (day 365 → day 1) that a raw integer would introduce.
    abs_lat captures the symmetric effect of polar proximity without
    forcing the model to learn it from signed latitude.
    """
    df = df.copy()
    radians = 2 * math.pi * df["day_of_year"] / 365
    df["sin_doy"] = np.sin(radians)
    df["cos_doy"] = np.cos(radians)
    df["abs_lat"] = df["lat"].abs()
    return df


def split_data(
    df: pd.DataFrame,
    target_col: str,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Time-aware train/test split on the TRAIN_CUTOFF boundary.

    Returns (X_train, y_train, X_test, y_test).
    A random shuffle would allow future observations to inform past predictions,
    which is unrealistic for deployment. Temporal split avoids this.
    """
    mask_train = df["date"] < TRAIN_CUTOFF
    train = df[mask_train]
    test = df[~mask_train]

    if train.empty or test.empty:
        raise ValueError(
            f"Train/test split produced an empty set "
            f"(train={len(train)}, test={len(test)}). "
            f"Check TRAIN_CUTOFF={TRAIN_CUTOFF!r} against the dataset date range."
        )

    X_train = train[FEATURES]
    y_train = train[target_col]
    X_test = test[FEATURES]
    y_test = test[target_col]
    return X_train, y_train, X_test, y_test


# ── Evaluation helpers ─────────────────────────────────────────────────────────

def precision_at_threshold(y_true: np.ndarray, y_pred: np.ndarray, thr: float = 0.5) -> float:
    """Fraction of predictions within `thr` degrees of the true value."""
    return float(np.mean(np.abs(y_pred - y_true) < thr))


def evaluate_model(
    model,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    scaler: StandardScaler,
) -> dict:
    """
    Fit `model` on scaled training data, score on scaled test data.

    Returns a dict with MAE, RMSE, R², and precision at 0.5°.
    The scaler is fit on training data only; test data is transformed, not fit.
    """
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = math.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    prec = precision_at_threshold(y_test.to_numpy(), y_pred, thr=0.5)

    return {"mae": mae, "rmse": rmse, "r2": r2, "prec_0_5": prec}


# ── Reporting ──────────────────────────────────────────────────────────────────

def print_results(prayer: str, results: dict[str, dict]) -> None:
    """Print a structured results table to stdout."""
    header = f"=== {prayer} angle prediction ==="
    print(header)
    print(f"{'Model':<22} {'MAE':>6} {'RMSE':>6} {'R²':>6} {'Prec@0.5°':>10}")
    print("-" * 55)
    for model_name, m in results.items():
        print(
            f"{model_name:<22} "
            f"{m['mae']:>6.2f} "
            f"{m['rmse']:>6.2f} "
            f"{m['r2']:>6.2f} "
            f"{m['prec_0_5']:>9.1%}"
        )
    print()


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run_pipeline(csv_path: Path, target_col: str, prayer_label: str) -> None:
    """
    Full train/evaluate loop for one prayer dataset.

    Loads the CSV, builds features, splits on the time boundary, scales,
    then trains and scores both Ridge and GradientBoosting models.
    """
    df = pd.read_csv(csv_path, dtype={"date": str})
    df = build_features(df)

    X_train, y_train, X_test, y_test = split_data(df, target_col)

    # Fit scaler on training data only — no data leakage from test set
    scaler = StandardScaler()
    scaler.fit(X_train[FEATURES])

    models = {
        "Ridge": Ridge(alpha=1.0),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            random_state=42,
        ),
    }

    results = {}
    for name, model in models.items():
        results[name] = evaluate_model(model, X_train, y_train, X_test, y_test, scaler)

    print_results(prayer_label, results)


def main() -> None:
    root = _repo_root()
    processed = root / "data" / "processed"

    fajr_csv = processed / "fajr_angles.csv"
    isha_csv = processed / "isha_angles.csv"

    for path in (fajr_csv, isha_csv):
        if not path.exists():
            print(f"ERROR: dataset not found: {path}", file=sys.stderr)
            sys.exit(1)

    run_pipeline(fajr_csv, target_col="fajr_angle", prayer_label="Fajr")
    run_pipeline(isha_csv, target_col="isha_angle", prayer_label="Isha")


if __name__ == "__main__":
    main()
