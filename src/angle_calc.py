"""
Back-calculate the solar depression angle at the moment of a verified sighting.

Given: date, lat, lng, elevation_m, observed_utc_time
Returns: depression angle in degrees (positive = sun below horizon)

Uses PyEphem for accurate solar position. Atmospheric refraction is included
because human observers see the sky with refraction — the angle we compute
matches what the sun physically was doing at that horizon.
"""

from datetime import datetime, timezone
import ephem
import math


def depression_angle(
    utc_dt: datetime,
    lat_deg: float,
    lng_deg: float,
    elevation_m: float = 0.0,
) -> float:
    """
    Return the solar depression angle in degrees at the given UTC datetime
    and location.

    Depression angle is positive when the sun is below the horizon.
    Returns a negative value if the sun is somehow above the horizon
    (which would indicate a data entry error in the sighting record).

    Parameters
    ----------
    utc_dt : datetime
        Observation datetime in UTC (timezone-aware or naive UTC).
    lat_deg : float
        Observer latitude in decimal degrees (north positive).
    lng_deg : float
        Observer longitude in decimal degrees (east positive).
    elevation_m : float
        Observer elevation above sea level in metres.

    Returns
    -------
    float
        Solar depression angle in degrees. Positive = sun below horizon.
    """
    obs = ephem.Observer()
    obs.lat = str(lat_deg)
    obs.lon = str(lng_deg)
    obs.elevation = elevation_m
    obs.pressure = 1013.25  # standard atmosphere — include refraction
    obs.temp = 15.0         # standard temperature

    # ephem expects UTC as a naive datetime
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.replace(tzinfo=None)
    obs.date = ephem.Date(utc_dt)

    sun = ephem.Sun(obs)
    altitude_rad = float(sun.alt)
    altitude_deg = math.degrees(altitude_rad)

    return -altitude_deg  # depression = negative altitude


def depression_angles_batch(records: list[dict]) -> list[float]:
    """
    Compute depression angles for a list of sighting records.

    Each record must have:
        utc_dt      : datetime (UTC)
        lat         : float (decimal degrees)
        lng         : float (decimal degrees)
        elevation_m : float (metres, default 0)

    Returns a list of depression angles in the same order.
    """
    return [
        depression_angle(
            r["utc_dt"],
            r["lat"],
            r["lng"],
            r.get("elevation_m", 0.0),
        )
        for r in records
    ]
