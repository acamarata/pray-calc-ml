"""
Elevation lookup — Open-Topo-Data (SRTM30m) primary, Open-Elevation fallback.

Open-Topo-Data is free, no key required, SRTM30m dataset covers -60° to +60° lat
(all regions relevant to Islamic prayer time research).
Open-Elevation is the fallback if Open-Topo-Data is unreachable.

Both services fall back to returning 0.0 on complete failure so callers always
get a numeric result.
"""

import logging
import time
import requests

log = logging.getLogger(__name__)

OPEN_TOPO_URL = "https://api.opentopodata.org/v1/srtm30m"
OPEN_ELEVATION_URL = "https://api.open-elevation.com/api/v1/lookup"


# ---------------------------------------------------------------------------
# Open-Topo-Data (primary)
# ---------------------------------------------------------------------------

def _get_elevations_opentopodata(
    locations: list[tuple[float, float]],
    chunk_size: int = 100,
) -> list[float | None]:
    """
    Batch elevation lookup via Open-Topo-Data SRTM30m.

    Returns a list parallel to `locations`. Each entry is a float elevation in
    metres, or None if the lookup failed for that location.
    """
    results: list[float | None] = []

    for i in range(0, len(locations), chunk_size):
        chunk = locations[i : i + chunk_size]
        # Pipe-separated lat,lng pairs as query string
        loc_str = "|".join(f"{lat},{lng}" for lat, lng in chunk)
        try:
            resp = requests.get(
                OPEN_TOPO_URL,
                params={"locations": loc_str},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") != "OK":
                log.warning("Open-Topo-Data non-OK status: %s", data.get("status"))
                results.extend(None for _ in chunk)
            else:
                for r in data["results"]:
                    elev = r.get("elevation")
                    results.append(float(elev) if elev is not None else None)
        except Exception as e:
            log.warning("Open-Topo-Data chunk failed: %s", e)
            results.extend(None for _ in chunk)

        if i + chunk_size < len(locations):
            time.sleep(0.3)  # polite rate limiting

    return results


# ---------------------------------------------------------------------------
# Open-Elevation (fallback)
# ---------------------------------------------------------------------------

def _get_elevations_open_elevation(
    locations: list[tuple[float, float]],
    chunk_size: int = 100,
) -> list[float]:
    """
    Batch elevation lookup via Open-Elevation (fallback).
    Returns 0.0 for any failed location.
    """
    results: list[float] = []

    for i in range(0, len(locations), chunk_size):
        chunk = locations[i : i + chunk_size]
        payload = {
            "locations": [{"latitude": lat, "longitude": lng} for lat, lng in chunk]
        }
        try:
            resp = requests.post(OPEN_ELEVATION_URL, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            results.extend(float(r["elevation"]) for r in data["results"])
        except Exception as e:
            log.warning("Open-Elevation chunk failed: %s", e)
            results.extend(0.0 for _ in chunk)

        if i + chunk_size < len(locations):
            time.sleep(0.2)

    return results


# ---------------------------------------------------------------------------
# Public API (unchanged signature)
# ---------------------------------------------------------------------------

def get_elevation(lat: float, lng: float, retries: int = 3) -> float:
    """
    Look up elevation in metres at (lat, lng).
    Returns 0.0 on failure.
    """
    # Try Open-Topo-Data first
    for attempt in range(retries):
        try:
            resp = requests.get(
                OPEN_TOPO_URL,
                params={"locations": f"{lat},{lng}"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "OK":
                elev = data["results"][0].get("elevation")
                if elev is not None:
                    return float(elev)
        except Exception:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))

    # Fallback: Open-Elevation
    payload = {"locations": [{"latitude": lat, "longitude": lng}]}
    for attempt in range(retries):
        try:
            resp = requests.post(OPEN_ELEVATION_URL, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return float(data["results"][0]["elevation"])
        except Exception:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))

    return 0.0


def get_elevations_batch(
    locations: list[tuple[float, float]],
    chunk_size: int = 100,
) -> list[float]:
    """
    Look up elevations for a list of (lat, lng) tuples.

    Tries Open-Topo-Data first; falls back to Open-Elevation for any
    chunk that fails entirely. Returns 0.0 for any location that fails both.
    """
    if not locations:
        return []

    # Primary: Open-Topo-Data
    primary = _get_elevations_opentopodata(locations, chunk_size=chunk_size)

    # Find any that returned None and retry with Open-Elevation
    failed_indices = [i for i, v in enumerate(primary) if v is None]
    if failed_indices:
        failed_locs = [locations[i] for i in failed_indices]
        log.info("Retrying %d elevation(s) via Open-Elevation fallback", len(failed_locs))
        fallback = _get_elevations_open_elevation(failed_locs, chunk_size=chunk_size)
        for idx, elev in zip(failed_indices, fallback):
            primary[idx] = elev

    # Replace any remaining None with 0.0
    return [float(v) if v is not None else 0.0 for v in primary]
