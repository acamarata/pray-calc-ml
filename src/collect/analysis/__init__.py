"""
analysis -- descriptive statistics and visualizations for sightings DataFrames.

Modules:
  sightings_stats  -- summary stats, geographic coverage, and matplotlib/seaborn plots
"""

from .sightings_stats import (
    angle_summary,
    geographic_coverage,
    plot_angle_distribution,
    plot_angle_vs_latitude,
    plot_angle_vs_day_of_year,
    print_dataset_report,
)

__all__ = [
    "angle_summary",
    "geographic_coverage",
    "plot_angle_distribution",
    "plot_angle_vs_latitude",
    "plot_angle_vs_day_of_year",
    "print_dataset_report",
]
