"""
Tests for src/collect/data/sightings_loader.py

Verifies that VERIFIED_SIGHTINGS has the expected structure, SightingRecord
TypedDict fields are consistent, and load_verified_sightings() returns a
correctly shaped DataFrame with UTC-aware timestamps.
"""

import pytest
from datetime import timezone

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from src.collect.data.sightings_loader import (
    VERIFIED_SIGHTINGS,
    SightingRecord,
    load_verified_sightings,
)


class TestVerifiedSightingsData:
    def test_sightings_list_is_nonempty(self):
        """VERIFIED_SIGHTINGS must contain at least one record."""
        assert len(VERIFIED_SIGHTINGS) > 0, "VERIFIED_SIGHTINGS is empty"

    def test_all_records_have_required_keys(self):
        """Every record must contain all SightingRecord fields."""
        required = {"prayer", "date_local", "time_local", "utc_offset", "lat", "lng",
                    "elevation_m", "source", "notes"}
        missing_any = []
        for i, rec in enumerate(VERIFIED_SIGHTINGS):
            missing = required - set(rec.keys())
            if missing:
                missing_any.append((i, missing))
        assert not missing_any, f"Records missing keys: {missing_any[:3]}"

    def test_prayer_values_are_fajr_or_isha(self):
        """Each record's prayer field must be 'fajr' or 'isha'."""
        invalid = [r for r in VERIFIED_SIGHTINGS if r["prayer"] not in ("fajr", "isha")]
        assert not invalid, f"{len(invalid)} records with invalid prayer value"

    def test_date_local_format(self):
        """date_local must be in YYYY-MM-DD format."""
        from datetime import datetime
        invalid = []
        for i, r in enumerate(VERIFIED_SIGHTINGS):
            try:
                datetime.strptime(r["date_local"], "%Y-%m-%d")
            except ValueError:
                invalid.append((i, r["date_local"]))
        assert not invalid, f"Invalid date_local formats (first 3): {invalid[:3]}"

    def test_time_local_format(self):
        """time_local must be HH:MM (24-hour)."""
        from datetime import datetime
        invalid = []
        for i, r in enumerate(VERIFIED_SIGHTINGS):
            try:
                datetime.strptime(r["time_local"], "%H:%M")
            except ValueError:
                invalid.append((i, r["time_local"]))
        assert not invalid, f"Invalid time_local formats (first 3): {invalid[:3]}"

    def test_lat_lng_are_numeric_and_in_range(self):
        """lat must be in [-90, 90], lng in [-180, 180]."""
        bad_lat = [r for r in VERIFIED_SIGHTINGS if not (-90 <= r["lat"] <= 90)]
        bad_lng = [r for r in VERIFIED_SIGHTINGS if not (-180 <= r["lng"] <= 180)]
        assert not bad_lat, f"{len(bad_lat)} records with lat out of range"
        assert not bad_lng, f"{len(bad_lng)} records with lng out of range"


class TestLoadVerifiedSightings:
    def setup_method(self):
        self.df = load_verified_sightings()

    def test_returns_dataframe(self):
        """load_verified_sightings must return a pandas DataFrame."""
        import pandas as pd
        assert isinstance(self.df, pd.DataFrame)

    def test_row_count_matches_list(self):
        """DataFrame must have the same number of rows as VERIFIED_SIGHTINGS."""
        assert len(self.df) == len(VERIFIED_SIGHTINGS)

    def test_required_columns_present(self):
        """All required output columns must be present."""
        required = {"date", "utc_dt", "lat", "lng", "elevation_m", "prayer", "source", "notes"}
        missing = required - set(self.df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_utc_dt_is_timezone_aware(self):
        """utc_dt column must contain timezone-aware datetimes in UTC."""
        for dt in self.df["utc_dt"].head(10):
            assert dt.tzinfo is not None, f"utc_dt {dt} is not timezone-aware"
            assert dt.tzinfo == timezone.utc, f"utc_dt {dt} is not UTC"

    def test_prayer_column_values(self):
        """prayer column must only contain 'fajr' or 'isha'."""
        unique = set(self.df["prayer"].unique())
        assert unique <= {"fajr", "isha"}, f"Unexpected prayer values: {unique}"

    def test_utc_conversion_blackburn_fajr(self):
        """Spot-check UTC conversion for a known Blackburn BST record.

        1987-09-21, 05:30 BST (UTC+1) should convert to 04:30 UTC.
        """
        blackburn = self.df[
            (self.df["date"].astype(str) == "1987-09-21")
            & (self.df["prayer"] == "fajr")
            & (self.df["lat"].round(2) == 53.75)
        ]
        assert len(blackburn) >= 1, "Could not find Blackburn 1987-09-21 fajr record"
        utc_dt = blackburn.iloc[0]["utc_dt"]
        assert utc_dt.hour == 4, f"Expected hour 4 (UTC), got {utc_dt.hour}"
        assert utc_dt.minute == 30, f"Expected minute 30, got {utc_dt.minute}"
