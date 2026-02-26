"""
Elevation lookup from the Open-Elevation API (free, no key required).
Falls back to zero if the API is unreachable.
"""

import time
import requests


OPEN_ELEVATION_URL = "https://api.open-elevation.com/api/v1/lookup"


def get_elevation(lat: float, lng: float, retries: int = 3) -> float:
    """
    Look up elevation in metres at (lat, lng) via Open-Elevation.

    Returns 0.0 on failure after `retries` attempts.
    """
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

    Sends up to `chunk_size` locations per request to stay within API limits.
    Returns a list of elevations in the same order as input.
    """
    results = []
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
        except Exception:
            results.extend(0.0 for _ in chunk)
        time.sleep(0.2)  # polite rate limit
    return results
