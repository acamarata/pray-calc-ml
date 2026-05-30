"""
Tests for src/collect/analysis/sightings_stats.py

Verifies angle_summary, geographic_coverage, and print_dataset_report
return correct types and values. Plot functions are tested for return type only
(no display).
"""

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import pytest
import pandas as pd
from datetime import datetime, timezone

from src.collect.analysis.sightings_stats import (
    angle_summary,
    geographic_coverage,
    plot_angle_distribution,
    plot_angle_vs_latitude,
    plot_angle_vs_day_of_year,
    print_dataset_report,
)


def _make_fajr_df(n=10):
    """Build a minimal Fajr DataFrame with day_of_year and fajr_angle."""
    rows = []
    for i in range(n):
        day = (i * 36) + 1  # spread across the year
        dt = datetime(2023, 1, 1, 4, 0, tzinfo=timezone.utc)
        rows.append({
            "date": f"2023-01-{i+1:02d}",
            "utc_dt": dt,
            "lat": 30.0 + i * 0.5,
            "lng": 29.0,
            "elevation_m": 100.0,
            "prayer": "fajr",
            "fajr_angle": 12.0 + i * 0.3,
            "day_of_year": day,
            "source": f"Source {i}",
            "notes": "test",
        })
    return pd.DataFrame(rows)


def _make_isha_df(n=5):
    """Build a minimal Isha DataFrame."""
    rows = []
    for i in range(n):
        rows.append({
            "date": f"2023-03-{i+1:02d}",
            "utc_dt": datetime(2023, 3, i+1, 19, 0, tzinfo=timezone.utc),
            "lat": 25.0 + i,
            "lng": 46.0,
            "elevation_m": 620.0,
            "prayer": "isha",
            "isha_angle": 17.0 + i * 0.2,
            "day_of_year": 60 + i,
            "source": f"Isha Source {i}",
            "notes": "test",
        })
    return pd.DataFrame(rows)


class TestAngleSummary:
    def test_returns_series(self):
        """angle_summary must return a pandas Series."""
        df = _make_fajr_df()
        result = angle_summary(df, "fajr_angle")
        assert isinstance(result, pd.Series)

    def test_count_is_correct(self):
        """count in summary must equal number of non-NaN angle rows."""
        df = _make_fajr_df(10)
        result = angle_summary(df, "fajr_angle")
        assert result["count"] == 10.0

    def test_mean_is_plausible(self):
        """Mean angle must be within the data range."""
        df = _make_fajr_df(10)
        result = angle_summary(df, "fajr_angle")
        assert df["fajr_angle"].min() <= result["mean"] <= df["fajr_angle"].max()

    def test_isha_angle_col(self):
        """Works correctly with isha_angle column."""
        df = _make_isha_df()
        result = angle_summary(df, "isha_angle")
        assert result["count"] == 5.0


class TestGeographicCoverage:
    def test_returns_dict(self):
        """geographic_coverage must return a dict."""
        df = _make_fajr_df()
        result = geographic_coverage(df)
        assert isinstance(result, dict)

    def test_required_keys_present(self):
        """All expected keys must be in the result dict."""
        df = _make_fajr_df()
        result = geographic_coverage(df)
        for key in ("lat_min", "lat_max", "unique_locs", "date_min", "date_max", "total_records"):
            assert key in result, f"Missing key: {key}"

    def test_total_records_correct(self):
        """total_records must equal len(df)."""
        df = _make_fajr_df(7)
        result = geographic_coverage(df)
        assert result["total_records"] == 7

    def test_lat_range_correct(self):
        """lat_min and lat_max must match DataFrame lat column bounds."""
        df = _make_fajr_df(10)
        result = geographic_coverage(df)
        assert abs(result["lat_min"] - df["lat"].min()) < 1e-6
        assert abs(result["lat_max"] - df["lat"].max()) < 1e-6

    def test_unique_locs_counts_groups(self):
        """unique_locs must count distinct (lat, lng) pairs."""
        df = _make_fajr_df(10)
        expected = len(df.groupby(["lat", "lng"]))
        result = geographic_coverage(df)
        assert result["unique_locs"] == expected


class TestPrintDatasetReport:
    def test_runs_without_error(self, capsys):
        """print_dataset_report must run to completion without exceptions."""
        fajr = _make_fajr_df(5)
        isha = _make_isha_df(3)
        print_dataset_report(fajr, isha)
        out = capsys.readouterr().out
        assert "Fajr dataset: 5" in out
        assert "Isha dataset: 3" in out

    def test_empty_datasets(self, capsys):
        """print_dataset_report handles empty DataFrames without crashing."""
        fajr = pd.DataFrame(columns=["fajr_angle"])
        isha = pd.DataFrame(columns=["isha_angle"])
        print_dataset_report(fajr, isha)
        out = capsys.readouterr().out
        assert "Fajr dataset: 0" in out
        assert "Isha dataset: 0" in out


class TestPlotFunctions:
    def test_plot_angle_distribution_returns_figure(self):
        """plot_angle_distribution must return a matplotlib Figure."""
        import matplotlib
        matplotlib.use("Agg")  # non-interactive backend for tests
        df = _make_fajr_df(10)
        fig = plot_angle_distribution(df, "fajr_angle")
        import matplotlib.figure
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_plot_angle_vs_latitude_returns_figure(self):
        """plot_angle_vs_latitude must return a matplotlib Figure."""
        import matplotlib
        matplotlib.use("Agg")
        df = _make_fajr_df(10)
        fig = plot_angle_vs_latitude(df, "fajr_angle")
        import matplotlib.figure
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_plot_angle_vs_day_of_year_returns_figure(self):
        """plot_angle_vs_day_of_year must return a matplotlib Figure."""
        import matplotlib
        matplotlib.use("Agg")
        df = _make_fajr_df(10)
        fig = plot_angle_vs_day_of_year(df, "fajr_angle")
        import matplotlib.figure
        assert isinstance(fig, matplotlib.figure.Figure)
