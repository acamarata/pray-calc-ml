"""
sightings_stats -- descriptive statistics and plots for the sightings dataset.

Purpose:
    Provides summary statistics, geographic coverage reports, and matplotlib/
    seaborn visualizations for the processed Fajr and Isha sightings DataFrames.
    These functions are used in exploratory analysis and to validate the dataset
    after pipeline runs.

Input DataFrame schema (Fajr):
    date        - str or datetime.date
    utc_dt      - datetime (timezone-aware UTC)
    lat         - float, decimal degrees
    lng         - float, decimal degrees
    elevation_m - float, metres above sea level
    day_of_year - int (optional, added by build_feature_matrix)
    fajr_angle  - float, solar depression angle in degrees
    source      - str
    notes       - str

Input DataFrame schema (Isha):
    Same as above but with ``isha_angle`` instead of ``fajr_angle``.

Key functions:
    angle_summary(df, angle_col)          -> pd.Series  (describe() stats)
    geographic_coverage(df)               -> dict        (lat range, unique locs, date range)
    plot_angle_distribution(df, angle_col) -> matplotlib Figure
    plot_angle_vs_latitude(df, angle_col)  -> matplotlib Figure
    plot_angle_vs_day_of_year(df, angle_col) -> matplotlib Figure
    print_dataset_report(fajr_df, isha_df)  -> None (prints to stdout)

SPORT: .opencode/phases/sport/packages.md -- pray-calc-ml row
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def angle_summary(df: pd.DataFrame, angle_col: str) -> pd.Series:
    """
    Return descriptive statistics for the named angle column.

    Parameters:
        df:         DataFrame containing ``angle_col``.
        angle_col:  Column name, e.g. "fajr_angle" or "isha_angle".

    Returns:
        pd.Series from DataFrame.describe() — count, mean, std, min, quartiles, max.
    """
    return df[angle_col].describe()


def geographic_coverage(df: pd.DataFrame) -> dict[str, Any]:
    """
    Return a summary of the geographic and temporal coverage of the dataset.

    Parameters:
        df: DataFrame with ``lat``, ``lng``, and ``date`` columns.

    Returns:
        dict with keys:
          lat_min       - float, southernmost latitude
          lat_max       - float, northernmost latitude
          unique_locs   - int, number of distinct (lat, lng) pairs
          date_min      - str, earliest date ("YYYY-MM-DD")
          date_max      - str, latest date ("YYYY-MM-DD")
          total_records - int
    """
    dates = df["date"].astype(str)
    return {
        "lat_min": float(df["lat"].min()),
        "lat_max": float(df["lat"].max()),
        "unique_locs": int(len(df.groupby(["lat", "lng"]))),
        "date_min": str(dates.min()),
        "date_max": str(dates.max()),
        "total_records": len(df),
    }


def plot_angle_distribution(df: pd.DataFrame, angle_col: str):
    """
    Plot a histogram and KDE of the named angle column.

    Requires matplotlib and seaborn. If seaborn is unavailable, falls back
    to a plain matplotlib histogram.

    Parameters:
        df:         DataFrame containing ``angle_col``.
        angle_col:  Column name, e.g. "fajr_angle" or "isha_angle".

    Returns:
        matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4))
    try:
        import seaborn as sns
        sns.histplot(df[angle_col].dropna(), kde=True, ax=ax, bins=30)
    except ImportError:
        ax.hist(df[angle_col].dropna(), bins=30, edgecolor="black")
    ax.set_xlabel("Solar depression angle (°)")
    ax.set_ylabel("Count")
    ax.set_title(f"{angle_col} distribution (n={len(df[angle_col].dropna())})")
    fig.tight_layout()
    return fig


def plot_angle_vs_latitude(df: pd.DataFrame, angle_col: str):
    """
    Scatter plot: solar depression angle vs geographic latitude.

    Shows how the depression angle varies with observer latitude. High-latitude
    sites tend to have lower effective depression angles due to shallow twilight
    geometry.

    Parameters:
        df:         DataFrame with ``lat`` and ``angle_col`` columns.
        angle_col:  Column name.

    Returns:
        matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    valid = df[[angle_col, "lat"]].dropna()
    ax.scatter(valid["lat"], valid[angle_col], alpha=0.4, s=15)
    ax.set_xlabel("Latitude (°)")
    ax.set_ylabel("Solar depression angle (°)")
    ax.set_title(f"{angle_col} vs latitude")
    fig.tight_layout()
    return fig


def plot_angle_vs_day_of_year(df: pd.DataFrame, angle_col: str):
    """
    Scatter plot: solar depression angle vs day of year.

    Requires a ``day_of_year`` column (add with build_feature_matrix). Shows
    seasonal variation in the observed depression angle.

    Parameters:
        df:         DataFrame with ``day_of_year`` and ``angle_col`` columns.
        angle_col:  Column name.

    Returns:
        matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    valid = df[[angle_col, "day_of_year"]].dropna()
    ax.scatter(valid["day_of_year"], valid[angle_col], alpha=0.4, s=15)
    ax.set_xlabel("Day of year")
    ax.set_ylabel("Solar depression angle (°)")
    ax.set_title(f"{angle_col} vs day of year")
    ax.set_xlim(1, 366)
    fig.tight_layout()
    return fig


def print_dataset_report(fajr_df: pd.DataFrame, isha_df: pd.DataFrame) -> None:
    """
    Print a concise text report of both datasets to stdout.

    Mirrors the summary output produced by src/pipeline.py main(). Useful for
    quick sanity checks after pipeline runs.

    Parameters:
        fajr_df:  Fajr angles DataFrame with ``fajr_angle`` column.
        isha_df:  Isha angles DataFrame with ``isha_angle`` column.
    """
    print(f"\nFajr dataset: {len(fajr_df)} records")
    if len(fajr_df) > 0:
        print("\nFajr angle stats:")
        print(angle_summary(fajr_df, "fajr_angle").to_string())
        cov = geographic_coverage(fajr_df)
        print("\nFajr geographic coverage:")
        print(f"  Latitude range: {cov['lat_min']:.1f}° to {cov['lat_max']:.1f}°")
        print(f"  Unique locations: {cov['unique_locs']}")
        print(f"  Date range: {cov['date_min']} to {cov['date_max']}")

    print(f"\nIsha dataset: {len(isha_df)} records")
    if len(isha_df) > 0:
        print("\nIsha angle stats:")
        print(angle_summary(isha_df, "isha_angle").to_string())
