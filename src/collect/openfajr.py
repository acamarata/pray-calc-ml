"""
Collect verified Fajr sightings from the OpenFajr project (Birmingham, UK).

OpenFajr is a year-long (and ongoing) astrophotography project in which
scholars and community members reviewed ~25,000 sky photographs and voted
on when true dawn appeared each day. The resulting Fajr times are published
as a Google Calendar iCal feed.

Source: https://openfajr.org/
Location: Birmingham, UK — 52.4862°N, 1.8904°W, elevation 141 m
"""

import io
from datetime import datetime, timezone

import pandas as pd
import requests

ICAL_URL = (
    "https://calendar.google.com/calendar/ical/"
    "qmho4v5896ki2mc5supv0ikgfs%40group.calendar.google.com/public/basic.ics"
)

# Fixed location for all Birmingham observations
BIRMINGHAM_LAT = 52.4862
BIRMINGHAM_LNG = -1.8904
BIRMINGHAM_ELEV_M = 141.0
BIRMINGHAM_SOURCE = "OpenFajr (openfajr.org)"


def fetch_openfajr(url: str = ICAL_URL) -> pd.DataFrame:
    """
    Download the OpenFajr iCal feed and return a DataFrame of confirmed Fajr
    sightings.

    Columns:
        date         : date (local calendar date in Europe/London)
        utc_dt       : datetime (UTC, timezone-aware)
        lat          : float
        lng          : float
        elevation_m  : float
        prayer       : str ("fajr")
        source       : str
        notes        : str
    """
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    text = resp.text

    records = []
    for block in text.split("BEGIN:VEVENT")[1:]:
        data: dict[str, str] = {}
        for line in block.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                data[k.strip()] = v.strip()

        summary = data.get("SUMMARY", "")
        if "Fajr" not in summary:
            continue

        dt_raw = data.get("DTSTART", "")
        if not dt_raw.endswith("Z"):
            continue  # skip local-time entries (there are none, but guard anyway)

        try:
            utc_dt = datetime.strptime(dt_raw, "%Y%m%dT%H%M%SZ").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue

        records.append(
            {
                "date": utc_dt.date(),
                "utc_dt": utc_dt,
                "lat": BIRMINGHAM_LAT,
                "lng": BIRMINGHAM_LNG,
                "elevation_m": BIRMINGHAM_ELEV_M,
                "prayer": "fajr",
                "source": BIRMINGHAM_SOURCE,
                "notes": "",
            }
        )

    df = pd.DataFrame(records)
    df = df.sort_values("utc_dt").reset_index(drop=True)
    return df
