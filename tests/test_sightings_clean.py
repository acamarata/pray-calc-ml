"""
Tests for src/collect/data/sightings_clean.py

Verifies filter_non_genuine, deduplicate_sightings, and apply_quality_filters
against known bad/good records and edge cases.
"""

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import pandas as pd
import pytest
from datetime import datetime, timezone, timedelta

from src.collect.data.sightings_clean import (
    filter_non_genuine,
    deduplicate_sightings,
    apply_quality_filters,
    BAD_NOTE_MARKERS,
    FAJR_MIN_DEG,
    ISHA_MIN_DEG,
    MAX_DEG,
)


def _make_row(prayer="fajr", date="2023-03-20", lat=40.0, lng=29.0,
              elevation_m=100.0, source="Test source", notes="naked eye"):
    """Build a minimal valid sighting row dict."""
    utc_dt = datetime(2023, 3, 20, 4, 0, 0, tzinfo=timezone.utc)
    return {
        "prayer": prayer,
        "date": date,
        "utc_dt": utc_dt,
        "lat": lat,
        "lng": lng,
        "elevation_m": elevation_m,
        "source": source,
        "notes": notes,
    }


class TestFilterNonGenuine:
    def test_genuine_record_is_kept(self):
        """A record with no bad markers should pass through unchanged."""
        df = pd.DataFrame([_make_row(notes="naked eye; per-night obs")])
        result = filter_non_genuine(df)
        assert len(result) == 1

    def test_bad_notes_marker_drops_row(self):
        """A record with 'time inferred' in notes must be dropped."""
        df = pd.DataFrame([
            _make_row(notes="time inferred from D0=14.5°"),
            _make_row(notes="naked eye observation"),
        ])
        result = filter_non_genuine(df)
        assert len(result) == 1
        assert "naked eye observation" in result.iloc[0]["notes"]

    def test_bad_source_marker_drops_row(self):
        """A record matching a bad marker in source must be dropped."""
        df = pd.DataFrame([
            _make_row(source="Umm al-Qura standard 18° Fajr, Makkah"),
            _make_row(source="Genuine researcher 2023"),
        ])
        result = filter_non_genuine(df)
        assert len(result) == 1

    def test_shafaq_ahmar_dropped(self):
        """Records with Shafaq Ahmar criterion must be dropped."""
        df = pd.DataFrame([
            _make_row(notes="Shafaq Ahmar (red dusk) observed"),
            _make_row(notes="Shafaq al-Abyad (white dusk)"),
        ])
        result = filter_non_genuine(df)
        assert len(result) == 1
        assert "al-Abyad" in result.iloc[0]["notes"]

    def test_case_insensitive_match(self):
        """Bad marker matching is case-insensitive."""
        df = pd.DataFrame([
            _make_row(notes="AGGREGATE REPRESENTATIVE date; 4 records"),
        ])
        result = filter_non_genuine(df)
        assert len(result) == 0

    def test_empty_dataframe(self):
        """Empty DataFrame returns empty DataFrame without error."""
        df = pd.DataFrame(columns=["prayer", "date", "lat", "lng", "notes", "source"])
        result = filter_non_genuine(df)
        assert len(result) == 0

    def test_bad_note_markers_is_nonempty(self):
        """BAD_NOTE_MARKERS must have at least 10 entries."""
        assert len(BAD_NOTE_MARKERS) >= 10


class TestDeduplicateSightings:
    def test_no_duplicates_unchanged(self):
        """DataFrame with no duplicates is returned unchanged."""
        rows = [
            _make_row(lat=40.0, lng=29.0, date="2023-01-01"),
            _make_row(lat=51.5, lng=-0.1, date="2023-01-01"),
        ]
        df = pd.DataFrame(rows)
        result = deduplicate_sightings(df)
        assert len(result) == 2

    def test_exact_duplicate_removed(self):
        """Two identical (prayer, date, lat, lng) rows: keep first, drop second."""
        rows = [
            _make_row(lat=40.0, lng=29.0, date="2023-06-15", source="Source A"),
            _make_row(lat=40.0, lng=29.0, date="2023-06-15", source="Source B"),
        ]
        df = pd.DataFrame(rows)
        result = deduplicate_sightings(df)
        assert len(result) == 1
        assert result.iloc[0]["source"] == "Source A"

    def test_near_duplicate_within_111m_removed(self):
        """Two records rounded to same 3dp lat/lng are duplicates."""
        rows = [
            _make_row(lat=40.001, lng=29.001, date="2023-06-15", source="Source A"),
            _make_row(lat=40.0009, lng=29.0009, date="2023-06-15", source="Source B"),
        ]
        df = pd.DataFrame(rows)
        result = deduplicate_sightings(df)
        assert len(result) == 1

    def test_same_location_different_prayer_both_kept(self):
        """Same lat/lng but different prayer type: both kept."""
        rows = [
            _make_row(prayer="fajr", lat=40.0, lng=29.0, date="2023-06-15"),
            _make_row(prayer="isha", lat=40.0, lng=29.0, date="2023-06-15"),
        ]
        df = pd.DataFrame(rows)
        result = deduplicate_sightings(df)
        assert len(result) == 2

    def test_same_location_different_date_both_kept(self):
        """Same lat/lng and prayer but different date: both kept."""
        rows = [
            _make_row(lat=40.0, lng=29.0, date="2023-06-15"),
            _make_row(lat=40.0, lng=29.0, date="2023-06-16"),
        ]
        df = pd.DataFrame(rows)
        result = deduplicate_sightings(df)
        assert len(result) == 2

    def test_no_lat_lng_temp_columns_in_output(self):
        """Deduplication must not leave _lat_r or _lng_r temp columns in output."""
        df = pd.DataFrame([_make_row()])
        result = deduplicate_sightings(df)
        assert "_lat_r" not in result.columns
        assert "_lng_r" not in result.columns


class TestApplyQualityFilters:
    def _df_with_angle(self, prayer="fajr", angle=14.0, lat=40.0,
                       date="2023-01-15", lng=29.0):
        utc_dt = datetime(2023, 1, 15, 4, 0, tzinfo=timezone.utc)
        return pd.DataFrame([{
            "prayer": prayer, "date": date, "utc_dt": utc_dt,
            "lat": lat, "lng": lng, "elevation_m": 100.0,
            "angle": angle, "source": "test", "notes": "test",
        }])

    def test_valid_fajr_angle_kept(self):
        df = self._df_with_angle(prayer="fajr", angle=14.0)
        assert len(apply_quality_filters(df)) == 1

    def test_valid_isha_angle_kept(self):
        df = self._df_with_angle(prayer="isha", angle=17.5)
        assert len(apply_quality_filters(df)) == 1

    def test_fajr_below_min_dropped(self):
        """Fajr angle below FAJR_MIN_DEG is dropped."""
        df = self._df_with_angle(prayer="fajr", angle=FAJR_MIN_DEG - 0.1)
        assert len(apply_quality_filters(df)) == 0

    def test_isha_below_min_dropped(self):
        """Isha angle below ISHA_MIN_DEG is dropped."""
        df = self._df_with_angle(prayer="isha", angle=ISHA_MIN_DEG - 0.1)
        assert len(apply_quality_filters(df)) == 0

    def test_angle_above_max_dropped(self):
        """Angle above MAX_DEG is dropped for both prayers."""
        df_fajr = self._df_with_angle(prayer="fajr", angle=MAX_DEG + 0.1)
        df_isha = self._df_with_angle(prayer="isha", angle=MAX_DEG + 0.1)
        assert len(apply_quality_filters(df_fajr)) == 0
        assert len(apply_quality_filters(df_isha)) == 0

    def test_polar_lat_dropped(self):
        """Records with |lat| > 70 are dropped."""
        df = self._df_with_angle(lat=71.0)
        assert len(apply_quality_filters(df)) == 0

    def test_null_island_dropped(self):
        """Records at lat~0, lng~0 are dropped."""
        utc_dt = datetime(2023, 1, 15, 4, 0, tzinfo=timezone.utc)
        df = pd.DataFrame([{
            "prayer": "fajr", "date": "2023-01-15", "utc_dt": utc_dt,
            "lat": 0.0, "lng": 0.0, "elevation_m": 0.0,
            "angle": 14.0, "source": "test", "notes": "test",
        }])
        assert len(apply_quality_filters(df)) == 0

    def test_future_date_dropped(self):
        """Records with dates in the future are dropped."""
        from datetime import date
        future = str(date(date.today().year + 1, 1, 1))
        utc_dt = datetime(date.today().year + 1, 1, 1, 4, 0, tzinfo=timezone.utc)
        df = pd.DataFrame([{
            "prayer": "fajr", "date": future, "utc_dt": utc_dt,
            "lat": 40.0, "lng": 29.0, "elevation_m": 100.0,
            "angle": 14.0, "source": "test", "notes": "test",
        }])
        assert len(apply_quality_filters(df)) == 0

    def test_nan_angle_dropped(self):
        """Records with NaN angle are dropped."""
        import math
        df = self._df_with_angle(angle=float("nan"))
        assert len(apply_quality_filters(df)) == 0
