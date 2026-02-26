"""
Geocoding module: city / region names → (lat, lng).

Uses OpenStreetMap Nominatim (free, no API key). Results are cached on disk
in data/raw/geocode_cache.json to avoid repeated API calls.

Usage:
    from src.geocode import geocode

    lat, lng = geocode("Birmingham, UK")
    lat, lng = geocode("Kottamia Observatory, Egypt")
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

log = logging.getLogger(__name__)

# Cache file location
CACHE_PATH = Path(__file__).parent.parent / "data" / "raw" / "geocode_cache.json"

# Nominatim endpoint — comply with their usage policy: 1 req/sec max, unique User-Agent
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "pray-calc-ml/1.0 (github.com/acamarata/pray-calc-ml)"

# Hardcoded fallback for known Islamic astronomical sites that Nominatim may mis-resolve
KNOWN_LOCATIONS: dict[str, tuple[float, float]] = {
    "kottamia observatory": (30.0285, 31.8262),
    "kottamia, egypt": (30.0285, 31.8262),
    "wadi al natron": (30.5, 30.15),
    "wadi el natrun": (30.5, 30.15),
    "oif umsu, medan": (3.595, 98.672),
    "lapan bandung": (6.8856, 107.6101),
    "bosscha observatory": (6.8256, 107.6111),
    "exmoor, uk": (51.15, -3.65),
    "exmoor national park": (51.15, -3.65),
    "tanjung aru, sabah": (5.933, 116.050),
    "teluk kemang, negeri sembilan": (2.460, 101.867),
    "kuala lipis": (4.183, 102.040),
    "port klang": (3.004, 101.403),
    "pantai cahaya bulan, kelantan": (6.148, 102.237),
}


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            with CACHE_PATH.open() as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w") as f:
        json.dump(cache, f, indent=2)


def geocode(location: str, *, country_hint: Optional[str] = None) -> Optional[tuple[float, float]]:
    """
    Return (lat, lng) for the given location string.

    Checks in order:
    1. KNOWN_LOCATIONS hardcoded table
    2. On-disk cache (data/raw/geocode_cache.json)
    3. Nominatim API (rate-limited to 1 req/sec)

    Returns None if the location cannot be resolved.
    """
    # Normalise key for lookup
    key = location.lower().strip()
    country_key = f"{key}, {country_hint.lower()}" if country_hint else key

    # 1. Hardcoded table
    for k in (country_key, key):
        if k in KNOWN_LOCATIONS:
            lat, lng = KNOWN_LOCATIONS[k]
            log.debug("geocode [hardcoded] %s → %.4f, %.4f", location, lat, lng)
            return lat, lng

    # 2. Cache
    cache = _load_cache()
    cache_key = country_key
    if cache_key in cache:
        entry = cache[cache_key]
        if entry is None:
            return None
        log.debug("geocode [cache] %s → %.4f, %.4f", location, entry[0], entry[1])
        return tuple(entry)

    # 3. Nominatim API
    query = f"{location}, {country_hint}" if country_hint else location
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
    }
    url = f"{NOMINATIM_URL}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": USER_AGENT})

    try:
        time.sleep(1.1)  # Nominatim: max 1 req/sec
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        log.warning("geocode API error for %r: %s", location, e)
        cache[cache_key] = None
        _save_cache(cache)
        return None

    if not data:
        log.warning("geocode: no results for %r", location)
        cache[cache_key] = None
        _save_cache(cache)
        return None

    lat = float(data[0]["lat"])
    lng = float(data[0]["lon"])
    log.info("geocode [API] %s → %.4f, %.4f (display: %s)", location, lat, lng, data[0].get("display_name", "")[:60])

    cache[cache_key] = [lat, lng]
    _save_cache(cache)
    return lat, lng


def geocode_batch(rows: list[dict]) -> list[dict]:
    """
    For each row dict that has 'location_name' but missing 'lat' or 'lng',
    fill in the coordinates via geocoding.

    Mutates the list in place and returns it.
    """
    for row in rows:
        if row.get("lat") and row.get("lng"):
            continue
        location = row.get("location_name") or row.get("city") or row.get("location")
        if not location:
            log.warning("geocode_batch: row has no location info, skipping: %s", row)
            continue
        country = row.get("country")
        result = geocode(location, country_hint=country)
        if result:
            row["lat"], row["lng"] = result
        else:
            log.warning("geocode_batch: could not geocode %r", location)
    return rows
