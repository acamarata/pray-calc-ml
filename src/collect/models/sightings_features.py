"""
sightings_features -- feature engineering for DPC solar depression angle prediction.

Purpose:
    Derives model-ready input features from a sightings DataFrame. The target
    variable is the solar depression angle (fajr_angle or isha_angle). These
    features inform the pray-calc Dynamic Prayer Calculation (DPC) formula and
    any downstream ML model that replaces or calibrates it.

Input DataFrame schema:
    utc_dt      - datetime (timezone-aware UTC)
    lat         - float, decimal degrees (north positive)
    lng         - float, decimal degrees (east positive)
    elevation_m - float, metres above sea level

Output DataFrame schema (from build_feature_matrix):
    All input columns PLUS the columns listed in FEATURE_COLUMNS:
    day_of_year   - int, 1-366, derived from utc_dt (seasonality proxy)
    lat_rad       - float, latitude in radians
    sin_doy       - float, sin(2*pi*day_of_year/365.25), circular seasonal encoding
    cos_doy       - float, cos(2*pi*day_of_year/365.25), circular seasonal encoding
    lat_sin_doy   - float, interaction: lat * sin_doy
    lat_cos_doy   - float, interaction: lat * cos_doy

Key functions:
    add_day_of_year(df) -> pd.DataFrame
        Adds day_of_year column from utc_dt.
    add_seasonal_features(df) -> pd.DataFrame
        Adds circular sin/cos encodings and lat interactions.
    build_feature_matrix(df) -> pd.DataFrame
        Applies both transforms; returns df with all FEATURE_COLUMNS present.

SPORT: .opencode/phases/sport/packages.md -- pray-calc-ml row
"""

from __future__ import annotations

import math

import pandas as pd

# The complete set of feature columns added by build_feature_matrix.
# ML models consuming these features should select from FEATURE_COLUMNS plus
# lat, lng, elevation_m as their X matrix.
FEATURE_COLUMNS = [
    "day_of_year",
    "lat_rad",
    "sin_doy",
    "cos_doy",
    "lat_sin_doy",
    "lat_cos_doy",
]

_TWO_PI = 2.0 * math.pi
_DAYS_PER_YEAR = 365.25


def add_day_of_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ``day_of_year`` (1-366) derived from the ``utc_dt`` column.

    ``day_of_year`` is the primary seasonality feature for the DPC angle
    prediction: the solar depression angle at Fajr/Isha varies systematically
    across the year at any given latitude.

    Parameters:
        df: DataFrame with a timezone-aware ``utc_dt`` column.

    Returns:
        Copy of df with ``day_of_year`` (int) added.
    """
    df = df.copy()
    df["day_of_year"] = df["utc_dt"].apply(lambda dt: dt.timetuple().tm_yday)
    return df


def add_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add circular seasonal encodings and latitude interaction terms.

    Circular encoding avoids the discontinuity at day 1 / day 365 that a raw
    ``day_of_year`` integer would introduce for models that treat features as
    continuous. The interaction terms capture the fact that seasonal variation
    in the depression angle is stronger at higher latitudes.

    Requires ``day_of_year`` and ``lat`` columns (call add_day_of_year first
    if ``day_of_year`` is not already present).

    New columns added:
        lat_rad      - latitude converted to radians
        sin_doy      - sin(2*pi*day_of_year/365.25)
        cos_doy      - cos(2*pi*day_of_year/365.25)
        lat_sin_doy  - lat * sin_doy
        lat_cos_doy  - lat * cos_doy

    Parameters:
        df: DataFrame with ``day_of_year`` (int) and ``lat`` (float) columns.

    Returns:
        Copy of df with the five new feature columns added.
    """
    df = df.copy()
    doy = df["day_of_year"]
    lat = df["lat"]

    df["lat_rad"] = lat * (math.pi / 180.0)
    df["sin_doy"] = (doy * _TWO_PI / _DAYS_PER_YEAR).apply(math.sin)
    df["cos_doy"] = (doy * _TWO_PI / _DAYS_PER_YEAR).apply(math.cos)
    df["lat_sin_doy"] = lat * df["sin_doy"]
    df["lat_cos_doy"] = lat * df["cos_doy"]
    return df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering transforms and return the complete feature
    matrix.

    Convenience wrapper that calls add_day_of_year then add_seasonal_features.
    After this call, df contains all columns in FEATURE_COLUMNS.

    Parameters:
        df: DataFrame with ``utc_dt`` (timezone-aware datetime) and ``lat``
            (float) columns.

    Returns:
        Copy of df with all FEATURE_COLUMNS added. Original columns are
        preserved unchanged.
    """
    df = add_day_of_year(df)
    df = add_seasonal_features(df)
    return df
