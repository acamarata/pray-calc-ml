"""
data — sightings data loading and cleaning.

Modules:
  sightings_loader  — raw VERIFIED_SIGHTINGS list + SightingRecord schema + loader
  sightings_clean   — quality filtering and deduplication utilities
"""

from .sightings_loader import (
    SightingRecord,
    VERIFIED_SIGHTINGS,
    load_verified_sightings,
)
from .sightings_clean import (
    filter_non_genuine,
    deduplicate_sightings,
    apply_quality_filters,
    BAD_NOTE_MARKERS,
)

__all__ = [
    "SightingRecord",
    "VERIFIED_SIGHTINGS",
    "load_verified_sightings",
    "filter_non_genuine",
    "deduplicate_sightings",
    "apply_quality_filters",
    "BAD_NOTE_MARKERS",
]
