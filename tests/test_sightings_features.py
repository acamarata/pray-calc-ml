"""
Tests for src/collect/models/sightings_features.py

Verifies add_day_of_year, add_seasonal_features, and build_feature_matrix
produce correct outputs with the expected shapes and value ranges.
"""

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import math
import pytest
import pandas as pd
from datetime import datetime, timezone

from src.collect.models.sightings_features import (
    add_day_of_year,
    add_seasonal_features,
    build_feature_matrix,
    FEATURE_COLUMNS,
)


def _make_df(utc_dts, lats):
    """Build a minimal DataFrame for feature testing."""
    rows = []
    for dt, lat in zip(utc_dts, lats):
        rows.append({
            "utc_dt": dt,
            "lat": lat,
            "lng": 30.0,
            "elevation_m": 100.0,
        })
    return pd.DataFrame(rows)


class TestAddDayOfYear:
    def test_march_equinox(self):
        """March 20 should be day 79 (non-leap year)."""
        df = _make_df([datetime(2023, 3, 20, 4, 0, tzinfo=timezone.utc)], [40.0])
        result = add_day_of_year(df)
        assert "day_of_year" in result.columns
        assert result.iloc[0]["day_of_year"] == 79

    def test_jan1_is_day_1(self):
        """January 1 must be day 1."""
        df = _make_df([datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc)], [0.0])
        result = add_day_of_year(df)
        assert result.iloc[0]["day_of_year"] == 1

    def test_dec31_is_day_365_nonleap(self):
        """Dec 31 in a non-leap year must be day 365."""
        df = _make_df([datetime(2023, 12, 31, 0, 0, tzinfo=timezone.utc)], [0.0])
        result = add_day_of_year(df)
        assert result.iloc[0]["day_of_year"] == 365

    def test_dec31_is_day_366_leap(self):
        """Dec 31 in a leap year must be day 366."""
        df = _make_df([datetime(2024, 12, 31, 0, 0, tzinfo=timezone.utc)], [0.0])
        result = add_day_of_year(df)
        assert result.iloc[0]["day_of_year"] == 366

    def test_original_columns_preserved(self):
        """add_day_of_year must not remove any existing columns."""
        df = _make_df([datetime(2023, 6, 21, 0, 0, tzinfo=timezone.utc)], [50.0])
        result = add_day_of_year(df)
        for col in df.columns:
            assert col in result.columns


class TestAddSeasonalFeatures:
    def setup_method(self):
        dt = datetime(2023, 6, 21, 0, 0, tzinfo=timezone.utc)
        self.df = add_day_of_year(_make_df([dt], [45.0]))

    def test_all_feature_columns_added(self):
        """All five new seasonal feature columns must be present."""
        result = add_seasonal_features(self.df)
        for col in ("lat_rad", "sin_doy", "cos_doy", "lat_sin_doy", "lat_cos_doy"):
            assert col in result.columns, f"Missing: {col}"

    def test_sin_cos_unit_circle(self):
        """sin_doy^2 + cos_doy^2 must equal 1.0 (unit circle)."""
        result = add_seasonal_features(self.df)
        for _, row in result.iterrows():
            magnitude = math.sqrt(row["sin_doy"] ** 2 + row["cos_doy"] ** 2)
            assert abs(magnitude - 1.0) < 1e-9, f"Not on unit circle: {magnitude}"

    def test_lat_rad_conversion(self):
        """lat_rad must equal lat * pi/180."""
        df = add_day_of_year(_make_df(
            [datetime(2023, 3, 20, 0, 0, tzinfo=timezone.utc)], [45.0]
        ))
        result = add_seasonal_features(df)
        expected = 45.0 * (math.pi / 180.0)
        assert abs(result.iloc[0]["lat_rad"] - expected) < 1e-10

    def test_latitude_zero_gives_zero_interactions(self):
        """At lat=0, lat_sin_doy and lat_cos_doy must be 0."""
        df = add_day_of_year(_make_df(
            [datetime(2023, 6, 21, 0, 0, tzinfo=timezone.utc)], [0.0]
        ))
        result = add_seasonal_features(df)
        assert result.iloc[0]["lat_sin_doy"] == 0.0
        assert result.iloc[0]["lat_cos_doy"] == 0.0


class TestBuildFeatureMatrix:
    def test_all_feature_columns_present(self):
        """build_feature_matrix must add all FEATURE_COLUMNS."""
        dt = datetime(2023, 9, 22, 0, 0, tzinfo=timezone.utc)
        df = _make_df([dt], [30.0])
        result = build_feature_matrix(df)
        for col in FEATURE_COLUMNS:
            assert col in result.columns, f"Missing feature: {col}"

    def test_original_columns_preserved(self):
        """build_feature_matrix must not remove original columns."""
        dt = datetime(2023, 9, 22, 0, 0, tzinfo=timezone.utc)
        df = _make_df([dt], [30.0])
        result = build_feature_matrix(df)
        for col in ("utc_dt", "lat", "lng", "elevation_m"):
            assert col in result.columns

    def test_multi_row_input(self):
        """build_feature_matrix must handle multiple rows correctly."""
        dts = [
            datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2023, 6, 21, 0, 0, tzinfo=timezone.utc),
            datetime(2023, 12, 31, 0, 0, tzinfo=timezone.utc),
        ]
        lats = [10.0, 40.0, -30.0]
        df = _make_df(dts, lats)
        result = build_feature_matrix(df)
        assert len(result) == 3
        assert result.iloc[0]["day_of_year"] == 1
        assert result.iloc[2]["day_of_year"] == 365

    def test_feature_columns_constant(self):
        """FEATURE_COLUMNS list must have exactly 6 elements."""
        assert len(FEATURE_COLUMNS) == 6
