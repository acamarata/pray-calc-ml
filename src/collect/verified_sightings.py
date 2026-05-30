"""
verified_sightings -- compatibility shim.

This module now re-exports all public symbols from the split domain modules.
The canonical implementations live at:

    src/collect/data/sightings_loader.py   -- SightingRecord, VERIFIED_SIGHTINGS,
                                              load_verified_sightings
    src/collect/data/sightings_clean.py    -- filter_non_genuine, deduplicate_sightings,
                                              apply_quality_filters, BAD_NOTE_MARKERS
    src/collect/models/sightings_features.py -- add_day_of_year, build_feature_matrix,
                                               FEATURE_COLUMNS
    src/collect/analysis/sightings_stats.py  -- angle_summary, geographic_coverage,
                                               plot_angle_distribution, print_dataset_report

Existing consumers that import from this module continue to work unchanged.
New code should import directly from the domain modules above.

SPORT: .opencode/phases/sport/packages.md -- pray-calc-ml row
"""

from src.collect.data.sightings_loader import (
    SightingRecord,
    VERIFIED_SIGHTINGS,
    load_verified_sightings,
)
from src.collect.data.sightings_clean import (
    filter_non_genuine,
    deduplicate_sightings,
    apply_quality_filters,
    BAD_NOTE_MARKERS,
)
from src.collect.models.sightings_features import (
    add_day_of_year,
    add_seasonal_features,
    build_feature_matrix,
    FEATURE_COLUMNS,
)
from src.collect.analysis.sightings_stats import (
    angle_summary,
    geographic_coverage,
    plot_angle_distribution,
    plot_angle_vs_latitude,
    plot_angle_vs_day_of_year,
    print_dataset_report,
)

__all__ = [
    # Loader
    "SightingRecord",
    "VERIFIED_SIGHTINGS",
    "load_verified_sightings",
    # Clean
    "filter_non_genuine",
    "deduplicate_sightings",
    "apply_quality_filters",
    "BAD_NOTE_MARKERS",
    # Features
    "add_day_of_year",
    "add_seasonal_features",
    "build_feature_matrix",
    "FEATURE_COLUMNS",
    # Stats
    "angle_summary",
    "geographic_coverage",
    "plot_angle_distribution",
    "plot_angle_vs_latitude",
    "plot_angle_vs_day_of_year",
    "print_dataset_report",
]
