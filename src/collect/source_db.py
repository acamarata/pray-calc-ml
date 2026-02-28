"""
Source registry — tracks every URL/source attempted during autonomous collection.

The manifest lives at data/raw/collection_manifest.json. Every entry records:
  - Unique source_id (slug)
  - URL
  - Type (paper, ical, csv, api, html, pdf)
  - Status (found, fetched, processed, empty, failed, blocked)
  - Record counts (raw and accepted after quality filtering)
  - Prayer types found
  - Location and date range
  - Fetch timestamp

This lets the autonomous collector skip already-processed sources and give a
complete audit trail of what was searched and what was found.
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = ROOT / "data" / "raw" / "collection_manifest.json"

SourceStatus = Literal["found", "fetched", "processed", "empty", "failed", "blocked"]
SourceType = Literal["paper", "ical", "csv", "api", "html", "pdf", "unknown"]


def _load() -> dict[str, dict]:
    """Load the manifest from disk. Returns dict keyed by source_id."""
    if MANIFEST_PATH.exists():
        try:
            data = json.loads(MANIFEST_PATH.read_text())
            if isinstance(data, list):
                # Legacy list format — convert to dict
                return {entry["source_id"]: entry for entry in data if "source_id" in entry}
            return data
        except Exception:
            return {}
    return {}


def _save(manifest: dict[str, dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def _slug(url: str) -> str:
    """Generate a stable slug from a URL for use as source_id."""
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"[^a-zA-Z0-9]+", "_", url)
    return url[:80].strip("_").lower()


def is_visited(url: str) -> bool:
    """Return True if this URL has already been processed (any status)."""
    manifest = _load()
    slug = _slug(url)
    return slug in manifest


def get_all_urls() -> set[str]:
    """Return the set of all URLs in the manifest."""
    manifest = _load()
    return {entry.get("url", "") for entry in manifest.values()}


def add_source(
    url: str,
    *,
    title: str = "",
    source_type: SourceType = "unknown",
    status: SourceStatus = "found",
    prayer_types: list[str] | None = None,
    records_raw: int = 0,
    records_accepted: int = 0,
    location: str = "",
    date_range: str = "",
    notes: str = "",
) -> str:
    """
    Add or update a source entry in the manifest.

    Returns the source_id (slug).
    """
    manifest = _load()
    source_id = _slug(url)

    manifest[source_id] = {
        "source_id": source_id,
        "url": url,
        "title": title,
        "type": source_type,
        "status": status,
        "prayer_types": prayer_types or [],
        "records_raw": records_raw,
        "records_accepted": records_accepted,
        "location": location,
        "date_range": date_range,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }
    _save(manifest)
    return source_id


def update_status(
    url: str,
    status: SourceStatus,
    records_raw: int | None = None,
    records_accepted: int | None = None,
    notes: str | None = None,
) -> None:
    """Update the status (and optionally record counts) for an existing source."""
    manifest = _load()
    source_id = _slug(url)
    if source_id not in manifest:
        add_source(url, status=status)
        return
    entry = manifest[source_id]
    entry["status"] = status
    entry["fetched_at"] = datetime.now(timezone.utc).isoformat()
    if records_raw is not None:
        entry["records_raw"] = records_raw
    if records_accepted is not None:
        entry["records_accepted"] = records_accepted
    if notes is not None:
        entry["notes"] = notes
    _save(manifest)


def summary() -> dict:
    """Return summary statistics about the manifest."""
    manifest = _load()
    total = len(manifest)
    by_status: dict[str, int] = {}
    total_raw = 0
    total_accepted = 0
    for entry in manifest.values():
        s = entry.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        total_raw += entry.get("records_raw", 0)
        total_accepted += entry.get("records_accepted", 0)
    return {
        "total_sources": total,
        "by_status": by_status,
        "total_records_raw": total_raw,
        "total_records_accepted": total_accepted,
    }


def get_failed_urls() -> list[str]:
    """Return URLs that failed so they can be retried."""
    manifest = _load()
    return [
        entry["url"]
        for entry in manifest.values()
        if entry.get("status") in ("failed",) and entry.get("url")
    ]
