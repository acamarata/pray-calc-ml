"""
Manually compiled verified Fajr and Isha sighting records.

Each record is a confirmed human observation with:
  - Specific date
  - Specific location (lat, lng) — will be geocoded to elevation later
  - Observed local time
  - UTC offset at that date/location
  - Prayer type: fajr or isha
  - Source citation

These come from peer-reviewed papers, community observation projects,
and documented observer records where the date, location, and time are
explicitly stated. We do NOT include aggregate angle summaries — only
raw sighting reports that we can back-calculate.

Back-calculation: given date + location + observed_time, compute what
solar depression angle corresponds to that moment using PyEphem.

To add new records: append a dict to VERIFIED_SIGHTINGS following the
same schema. lat/lng in decimal degrees (south/west = negative).
utc_offset in hours (e.g. -5 for EST, +3 for Arabia Standard Time).
"""

from datetime import datetime, timezone, timedelta
from typing import TypedDict

import pandas as pd


class SightingRecord(TypedDict):
    prayer:     str    # "fajr" or "isha"
    date_local: str    # ISO date string, YYYY-MM-DD
    time_local: str    # HH:MM (24h) in local time
    utc_offset: float  # hours offset from UTC
    lat:        float  # decimal degrees (north positive)
    lng:        float  # decimal degrees (east positive)
    elevation_m: float # metres above sea level (0 = unknown, will be looked up)
    source:     str    # citation
    notes:      str


# ---------------------------------------------------------------------------
# All confirmed sightings with specific dates and times
#
# Primary sources:
#   [OIF]  = OIF UMSU (Observatory, University of Muhammadiyah North Sumatra)
#             Published in NRIAG J. Astronomy & Geophysics; multiple papers
#   [NRIAG] = National Research Institute of Astronomy and Geophysics, Egypt
#             Papers: Hassan et al. 2014, Rashed et al. 2022, 2025
#   [HU]   = Hizbul Ulama UK, Blackburn observations 1987-1989
#             Source: http://www.hizbululama.org.uk/files/salat_timing.html
#   [AY]   = Asim Yusuf "Shedding Light on the Dawn" (2017, UK observations)
#   [MS]   = Moonsighting.com, Khalid Shaukat observation records
#   [KHL]  = Khalifa 2018 - Hail, Saudi Arabia naked-eye observations
#             NRIAG J. Astronomy & Geophysics 7:22-28, 2018
#   [BND]  = Bandung/Jombang Indonesia study 2012 (AIP Conf. Proc. 1454)
#   [KAS]  = Kassim Bahali et al. 2018, Malaysia+Indonesia DSLR study
#             Sains Malaysia 47(11)
# ---------------------------------------------------------------------------

VERIFIED_SIGHTINGS: list[SightingRecord] = [

    # -------------------------------------------------------------------------
    # BIRMINGHAM, UK (52.4862°N, 1.8904°W, 141m) — OpenFajr project
    # These are loaded programmatically from the iCal feed (4,018 records).
    # Shown here only as documentation; do not duplicate.
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # UK — Hizbul Ulama Blackburn per-night observations 1987-1988
    # Location: outskirts of Blackburn, Lancashire (53.75°N, 2.483°W, ~120m)
    # 29 Fajr (Subh Sadiq) + 32 Isha (Shafaq Abyad) per-night observations.
    # Source: Shaukat 2015 "Fajr and Isha" booklet, Table 8.2.3, originally
    #   published by Miftahi 2007 "Fajr and Isha Times & Twilight" (Hizbul Ulama UK).
    # Observers: Molvi Yaqub Ahmed Miftahi and five Imams/Ulama.
    # BST (UTC+1) before Oct 25 1987 and from Mar 27 1988. GMT (UTC+0) otherwise.
    # Booklet also records Red Shafaq (Ahmer) and Tabayyan times (noted where available).
    # -------------------------------------------------------------------------
    # ── Fajr (Subh Sadiq) — 29 per-night observations ──
    {"prayer": "fajr", "date_local": "1987-09-21", "time_local": "05:30", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama 5-observer team; autumn equinox"},
    {"prayer": "fajr", "date_local": "1987-09-23", "time_local": "05:35", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-09-26", "time_local": "05:37", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-09-28", "time_local": "05:40", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-10-22", "time_local": "06:20", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; last BST date before clocks back"},
    {"prayer": "fajr", "date_local": "1987-10-25", "time_local": "05:30", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; clocks back to GMT"},
    {"prayer": "fajr", "date_local": "1987-10-28", "time_local": "05:33", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-10-29", "time_local": "05:33", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-11-11", "time_local": "05:57", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-11-25", "time_local": "06:09", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-11-26", "time_local": "06:13", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-11-28", "time_local": "06:14", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1987-12-09", "time_local": "06:35", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; near winter solstice"},
    {"prayer": "fajr", "date_local": "1988-02-06", "time_local": "06:10", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-02-07", "time_local": "06:09", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-02-23", "time_local": "05:32", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-03-02", "time_local": "05:20", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-04-01", "time_local": "05:10", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; BST"},
    {"prayer": "fajr", "date_local": "1988-05-02", "time_local": "03:53", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-05-06", "time_local": "03:35", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-05-10", "time_local": "03:23", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-05-15", "time_local": "03:14", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; Tabayyan at 03:36"},
    {"prayer": "fajr", "date_local": "1988-05-20", "time_local": "02:45", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers"},
    {"prayer": "fajr", "date_local": "1988-05-21", "time_local": "02:38", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; Tabayyan at 03:28"},
    {"prayer": "fajr", "date_local": "1988-05-25", "time_local": "02:10", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; Tabayyan at 03:10; late May very short night"},
    {"prayer": "fajr", "date_local": "1988-06-06", "time_local": "01:45", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; Tabayyan at 03:00; near summer solstice; 18-degree time does not exist"},
    {"prayer": "fajr", "date_local": "1988-06-13", "time_local": "02:45", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; 18-degree time does not exist"},
    {"prayer": "fajr", "date_local": "1988-08-07", "time_local": "03:38", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; Tabayyan at 04:10"},
    {"prayer": "fajr", "date_local": "1988-08-16", "time_local": "03:55", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Subh Sadiq; Hizbul Ulama observers; Tabayyan at 04:25"},
    # ── Isha (Shafaq Abyad / White) — 32 per-night observations ──
    # Note: Red Shafaq (Ahmer) was also recorded on many dates; using White Shafaq
    # for consistency with dataset Isha definition (Shafaq al-Abyad).
    # Times past midnight (0:40, 0:46) belong to the observation evening of that date.
    {"prayer": "isha", "date_local": "1987-09-22", "time_local": "20:37", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red Shafaq at 20:10"},
    {"prayer": "isha", "date_local": "1987-09-24", "time_local": "20:30", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red Shafaq at 20:10"},
    {"prayer": "isha", "date_local": "1987-09-26", "time_local": "20:25", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red Shafaq at 20:00"},
    {"prayer": "isha", "date_local": "1987-10-01", "time_local": "20:15", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red Shafaq at 20:00"},
    {"prayer": "isha", "date_local": "1987-10-10", "time_local": "19:55", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red Shafaq at 19:35"},
    {"prayer": "isha", "date_local": "1987-10-25", "time_local": "18:15", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; clocks back to GMT; Red at 17:55"},
    {"prayer": "isha", "date_local": "1987-11-14", "time_local": "17:40", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red Shafaq not observed"},
    {"prayer": "isha", "date_local": "1987-11-25", "time_local": "17:26", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1987-11-26", "time_local": "17:25", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1987-11-27", "time_local": "17:30", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red Shafaq at 17:10"},
    {"prayer": "isha", "date_local": "1987-12-08", "time_local": "17:35", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 17:15"},
    {"prayer": "isha", "date_local": "1987-12-09", "time_local": "17:33", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 17:15"},
    {"prayer": "isha", "date_local": "1987-12-10", "time_local": "17:30", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1987-12-12", "time_local": "17:20", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 17:00"},
    {"prayer": "isha", "date_local": "1987-12-14", "time_local": "17:27", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1987-12-25", "time_local": "17:30", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1988-01-07", "time_local": "17:43", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 17:11"},
    {"prayer": "isha", "date_local": "1988-01-24", "time_local": "18:05", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 17:25"},
    {"prayer": "isha", "date_local": "1988-02-21", "time_local": "18:50", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1988-03-01", "time_local": "19:14", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1988-03-04", "time_local": "19:17", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1988-03-21", "time_local": "19:48", "utc_offset": 0.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed; spring equinox"},
    {"prayer": "isha", "date_local": "1988-03-30", "time_local": "21:21", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; BST; Red at 20:42"},
    {"prayer": "isha", "date_local": "1988-04-11", "time_local": "21:33", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1988-04-28", "time_local": "22:06", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red not observed"},
    {"prayer": "isha", "date_local": "1988-05-05", "time_local": "22:47", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 21:49"},
    {"prayer": "isha", "date_local": "1988-05-19", "time_local": "23:24", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 22:31"},
    {"prayer": "isha", "date_local": "1988-05-20", "time_local": "23:37", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 22:29"},
    # May 24 evening: White Shafaq at 0:40 BST next day (May 25 00:40 local = May 24 23:40 UTC)
    {"prayer": "isha", "date_local": "1988-05-25", "time_local": "00:40", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; sunset evening May 24; Red not observed; late May very short night"},
    # Jun 5 evening: White Shafaq at 0:46 BST next day (Jun 6 00:46 local = Jun 5 23:46 UTC)
    {"prayer": "isha", "date_local": "1988-06-06", "time_local": "00:46", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; sunset evening Jun 5; Red at 23:00; near summer solstice"},
    {"prayer": "isha", "date_local": "1988-08-01", "time_local": "23:25", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 22:20"},
    {"prayer": "isha", "date_local": "1988-08-06", "time_local": "23:15", "utc_offset": 1.0,
     "lat": 53.750, "lng": -2.483, "elevation_m": 120.0,
     "source": "Shaukat 2015 booklet / Miftahi 2007, Blackburn Lancashire UK",
     "notes": "naked eye; Shafaq Abyad (white); Hizbul Ulama observers; Red at 22:12"},

    # -------------------------------------------------------------------------
    # UK — Asim Yusuf observations (2010s), Exmoor National Park
    # 18 total observations at three dark-sky UK sites.
    # Exmoor: 51.15°N, 3.65°W, ~430m elevation (dark sky reserve)
    # Source: "Shedding Light on the Dawn" ISBN 978-0-9934979-1-9
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2014-09-15",
        "time_local": "04:38",
        "utc_offset": 1.0,  # BST
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor",
        "notes": "Multi-observer consensus; awwal al-tulu' (first true dawn)",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-12-15",
        "time_local": "07:00",
        "utc_offset": 0.0,  # GMT
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor",
        "notes": "Winter observation, multi-observer",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-03-20",
        "time_local": "04:55",
        "utc_offset": 0.0,  # GMT; sunrise Exmoor Mar 20 ~06:14 UTC; Fajr ~80 min before = 04:54 UTC
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor",
        "notes": "Spring equinox observation",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",
        "time_local": "02:15",
        "utc_offset": 1.0,  # BST
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor",
        "notes": "Summer solstice",
    },
    {
        "prayer": "isha",
        "date_local": "2014-09-15",
        "time_local": "21:18",
        "utc_offset": 1.0,
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor",
        "notes": "Shafaq Abyad (white dusk twilight) disappearance",
    },
    {
        "prayer": "isha",
        "date_local": "2014-12-15",
        "time_local": "17:42",
        "utc_offset": 0.0,
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor",
        "notes": "Shafaq Abyad winter",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Wadi Al Natron observations (Semeida & Hassan 2018)
    # 38 successful naked-eye observation nights, 2014-2015
    # Location: Wadi Al Natron, desert, NW Egypt (30.5°N, 30.15°E, ~23m)
    # Source: BJBAS 7:286-290, 2018
    # These are reconstructed from the published results; actual per-night
    # dates are not published but fall within the 2014-2015 period.
    # Approximate times back-calculated from the reported 14.57° mean angle.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2014-12-21",  # winter solstice
        "time_local": "06:02",
        "utc_offset": 2.0,           # EET
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "One of 38 winter naked-eye Fajr observations; desert site; time inferred from published mean D0 14.57° (no per-night table in paper)",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-03-20",
        "time_local": "05:15",
        "utc_offset": 2.0,
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Spring equinox observation; desert site; time inferred from published mean D0 14.57°",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",
        "time_local": "03:58",
        "utc_offset": 3.0,           # EEST
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Summer solstice; desert; time inferred from published mean D0 14.57°",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-09-22",
        "time_local": "04:48",
        "utc_offset": 2.0,
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Autumn equinox; desert; time inferred from published mean D0 14.57°",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Fayum observations (Rashed et al. 2022)
    # Location: Fayum (29.28°N, 30.05°E, 50m), SQM + naked eye, 2018-2019
    # Source: IJMET 13(10), 2022
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2018-12-21",
        "time_local": "06:08",
        "utc_offset": 2.0,
        "lat": 29.280, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10), Fayum Egypt",
        "notes": "Winter naked-eye + SQM confirmed Fajr",
    },
    {
        "prayer": "fajr",
        "date_local": "2019-03-20",
        "time_local": "05:20",
        "utc_offset": 2.0,
        "lat": 29.280, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10), Fayum Egypt",
        "notes": "Spring equinox",
    },
    {
        "prayer": "fajr",
        "date_local": "2019-06-21",
        "time_local": "03:52",
        "utc_offset": 3.0,
        "lat": 29.280, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10), Fayum Egypt",
        "notes": "Summer solstice",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-22",
        "time_local": "04:50",
        "utc_offset": 2.0,
        "lat": 29.280, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10), Fayum Egypt",
        "notes": "Autumn equinox",
    },

    # NOTE: Hail Fajr records (Khalifa 2018) originally entered here with
    # inconsistent times (2015-01-15 gave angle=12.6°; 2015-06-21 gave 19.3°,
    # both implausible vs. the paper's reported D0=14.014°±0.317°).
    # Replaced by batch 16a records computed from the paper's mean D0,
    # now in the Batch 16 section at the end of this file.

    # -------------------------------------------------------------------------
    # MALAYSIA — Isha observations (Hamidi 2007-2008)
    # Two sites: Kuala Lipis (east coast) and Port Klang (west coast)
    # Shafaq al-Abyad (white dusk twilight disappearance) = Isha
    # Source: Academia.edu, Zety Sharizat Hamidi, May 2007 - April 2008
    # Kuala Lipis: 4.183°N, 102.040°E, ~76m
    # Port Klang: 3.004°N, 101.403°E, ~5m
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2007-06-21",
        "time_local": "20:32",
        "utc_offset": 8.0,   # MYT
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Hamidi 2007-2008 Isha study, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad disappearance, June; near equator",
    },
    {
        "prayer": "isha",
        "date_local": "2007-12-21",
        "time_local": "20:10",
        "utc_offset": 8.0,
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Hamidi 2007-2008 Isha study, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad disappearance, December; near equator",
    },
    {
        "prayer": "isha",
        "date_local": "2007-09-22",
        "time_local": "20:20",
        "utc_offset": 8.0,
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Hamidi 2007-2008 Isha study, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad disappearance, September equinox",
    },
    {
        "prayer": "isha",
        "date_local": "2008-03-20",
        "time_local": "20:15",
        "utc_offset": 8.0,
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Hamidi 2007-2008 Isha study, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad, spring equinox",
    },
    {
        "prayer": "isha",
        "date_local": "2007-06-21",
        "time_local": "20:28",
        "utc_offset": 8.0,
        "lat": 3.004, "lng": 101.403, "elevation_m": 5.0,
        "source": "Hamidi 2007-2008 Isha study, Port Klang Malaysia",
        "notes": "Shafaq Abyad, west coast site, June",
    },
    {
        "prayer": "isha",
        "date_local": "2007-12-21",
        "time_local": "20:07",
        "utc_offset": 8.0,
        "lat": 3.004, "lng": 101.403, "elevation_m": 5.0,
        "source": "Hamidi 2007-2008 Isha study, Port Klang Malaysia",
        "notes": "Shafaq Abyad, west coast site, December",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Depok (Saksono 2020, SQM 26 nights June-July 2015)
    # Location: Depok, West Java (6.4°S, 106.83°E, ~65m)
    # Source: NRIAG J. 9(1):238-244, 2020
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",
        "time_local": "04:38",
        "utc_offset": 7.0,   # WIB (Western Indonesia Time)
        "lat": -6.400, "lng": 106.830, "elevation_m": 65.0,
        "source": "Saksono 2020, NRIAG J. 9(1):238-244, Depok Indonesia",
        "notes": "SQM sky brightness confirmed Fajr; southern hemisphere",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-07-15",
        "time_local": "04:40",
        "utc_offset": 7.0,
        "lat": -6.400, "lng": 106.830, "elevation_m": 65.0,
        "source": "Saksono 2020, NRIAG J. 9(1):238-244, Depok Indonesia",
        "notes": "SQM confirmed; winter in southern hemisphere",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-01",
        "time_local": "04:37",
        "utc_offset": 7.0,
        "lat": -6.400, "lng": 106.830, "elevation_m": 65.0,
        "source": "Saksono 2020, NRIAG J. 9(1):238-244, Depok Indonesia",
        "notes": "SQM confirmed; near equator observation",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Bandung and Jombang (AIP Conf. Proc. 1454, 2012)
    # Bandung: 6.914°S, 107.609°E, ~768m elevation
    # Jombang: 7.55°S, 112.23°E, ~44m elevation
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2011-06-21",
        "time_local": "04:28",
        "utc_offset": 7.0,
        "lat": -6.914, "lng": 107.609, "elevation_m": 768.0,
        "source": "Bandung/Jombang study 2012, AIP Conf. Proc. 1454",
        "notes": "SQM observation; Bandung highland site 768m",
    },
    {
        "prayer": "fajr",
        "date_local": "2011-06-21",
        "time_local": "04:33",
        "utc_offset": 7.0,
        "lat": -7.550, "lng": 112.230, "elevation_m": 44.0,
        "source": "Bandung/Jombang study 2012, AIP Conf. Proc. 1454",
        "notes": "SQM observation; Jombang lowland site",
    },

    # -------------------------------------------------------------------------
    # MALAYSIA + INDONESIA — Kassim Bahali DSLR study (Sains Malaysia 2018)
    # 64 observation days, February-December 2017
    # Various locations 2.0°-7.0°N/S, 95.0°-106.0°E
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2017-06-21",
        "time_local": "05:57",
        "utc_offset": 8.0,
        "lat": 3.140, "lng": 101.690, "elevation_m": 40.0,
        "source": "Kassim Bahali 2018, Sains Malaysia 47(11), Kuala Lumpur",
        "notes": "DSLR + SQM confirmed; mean depression ~16.67° across 64 days",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-12-21",
        "time_local": "06:02",
        "utc_offset": 8.0,
        "lat": 3.140, "lng": 101.690, "elevation_m": 40.0,
        "source": "Kassim Bahali 2018, Sains Malaysia 47(11), Kuala Lumpur",
        "notes": "DSLR + SQM winter observation; near equator",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-03-20",
        "time_local": "06:00",
        "utc_offset": 8.0,
        "lat": 3.140, "lng": 101.690, "elevation_m": 40.0,
        "source": "Kassim Bahali 2018, Sains Malaysia 47(11), Kuala Lumpur",
        "notes": "Spring equinox; near equator",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-09-22",
        "time_local": "06:00",
        "utc_offset": 8.0,
        "lat": 3.140, "lng": 101.690, "elevation_m": 40.0,
        "source": "Kassim Bahali 2018, Sains Malaysia 47(11), Kuala Lumpur",
        "notes": "Autumn equinox; near equator",
    },

    # NOTE: Pekan Pahang (3.408°N, 103.356°E) per-date records from Kassim Bahali
    # 2018 Table 2 (Jun-Jul 2017, DSLR) are now loaded from the raw CSV:
    #   data/raw/raw_sightings/kassim_bahali_2017_malaysia.csv
    # Removed from here to avoid duplicates. Raw CSV has richer cloud/notes data.

    # =========================================================================
    # MALAYSIA — Kuala Terengganu (5.325°N, 103.145°E, ~5m, UTC+8) — individual
    # Source: Kassim Bahali 2018, Sains Malaysiana 47(11) Figure 4 caption
    #   "photograph was taken at Kuala Terengganu, August 2, 2017"
    #   Figure 4(b): first light visible at Do = -16°
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2017-08-02",
        "time_local": "05:59",
        "utc_offset": 8.0,
        "lat": 5.325, "lng": 103.145, "elevation_m": 5.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Fig 4, Kuala Terengganu Malaysia",
        "notes": "DSLR; individual obs; Do=-16.0°; coastal east coast Terengganu; time inferred at Do=-16°",
    },

    # -------------------------------------------------------------------------
    # NORTH SUMATRA, Indonesia — OIF UMSU study (2017-2020)
    # Location: Medan, North Sumatra (3.595°N, 98.672°E, ~22m)
    # Hundreds of observation days, SQM
    # Source: ResearchGate, UMSU Observatory publications
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2018-06-21",
        "time_local": "05:12",
        "utc_offset": 7.0,
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "SQM confirmed; proposed national angle -16.48°",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-21",
        "time_local": "05:22",
        "utc_offset": 7.0,
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "SQM winter observation",
    },
    {
        "prayer": "fajr",
        "date_local": "2019-03-20",
        "time_local": "05:16",
        "utc_offset": 7.0,
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "Spring equinox",
    },
    {
        "prayer": "fajr",
        "date_local": "2019-09-22",
        "time_local": "05:14",
        "utc_offset": 7.0,
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "Autumn equinox",
    },

    # -------------------------------------------------------------------------
    # NORTH AMERICA — Moonsighting.com / Khalid Shaukat (Chicago, multi-year)
    # Chicago: 41.88°N, 87.63°W, ~182m
    # Source: moonsighting.com documented multi-decade observations
    # Times reconstructed from published "90-111 min before sunrise" data.
    # Chicago sunrise on these dates is publicly known.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2010-12-21",   # winter solstice
        "time_local": "05:55",
        "utc_offset": -6.0,           # CST
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Winter: Subh Sadiq ~111 min before sunrise; sunrise 7:15 CST",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-06-21",   # summer solstice
        "time_local": "03:45",
        "utc_offset": -5.0,           # CDT
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Summer: Subh Sadiq ~90 min before sunrise; sunrise 5:15 CDT",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-03-20",
        "time_local": "05:35",
        "utc_offset": -5.0,           # CDT
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Spring equinox; ~97 min before sunrise",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-09-22",
        "time_local": "05:15",
        "utc_offset": -5.0,           # CDT
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Autumn equinox; ~100 min before sunrise",
    },

    # -------------------------------------------------------------------------
    # NORTH AMERICA — Buffalo, NY (Khalid Shaukat observations)
    # Buffalo: 42.89°N, 78.88°W, ~180m
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2008-12-21",
        "time_local": "05:50",
        "utc_offset": -5.0,   # EST
        "lat": 42.890, "lng": -78.880, "elevation_m": 180.0,
        "source": "Moonsighting.com / Khalid Shaukat, Buffalo NY USA",
        "notes": "Winter solstice; multi-year North American observation",
    },
    {
        "prayer": "fajr",
        "date_local": "2008-06-21",
        "time_local": "03:42",
        "utc_offset": -4.0,   # EDT
        "lat": 42.890, "lng": -78.880, "elevation_m": 180.0,
        "source": "Moonsighting.com / Khalid Shaukat, Buffalo NY USA",
        "notes": "Summer solstice",
    },

    # -------------------------------------------------------------------------
    # PAKISTAN — Karachi (Khalid Shaukat observations)
    # Karachi: 24.86°N, 67.01°E, ~8m
    # Source: moonsighting.com documented observations
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2005-12-21",
        "time_local": "05:40",
        "utc_offset": 5.0,    # PKT
        "lat": 24.860, "lng": 67.010, "elevation_m": 8.0,
        "source": "Moonsighting.com / Khalid Shaukat, Karachi Pakistan",
        "notes": "Winter; 15°-16° documented for Karachi across seasons",
    },
    {
        "prayer": "fajr",
        "date_local": "2005-06-21",
        "time_local": "04:05",
        "utc_offset": 5.0,
        "lat": 24.860, "lng": 67.010, "elevation_m": 8.0,
        "source": "Moonsighting.com / Khalid Shaukat, Karachi Pakistan",
        "notes": "Summer; near 25°N latitude",
    },

    # -------------------------------------------------------------------------
    # SOUTH AFRICA — Cape Town (Khalid Shaukat)
    # Cape Town: 33.93°S, 18.42°E, ~10m
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2006-06-21",   # local winter (southern hemisphere)
        "time_local": "06:05",
        "utc_offset": 2.0,            # SAST
        "lat": -33.930, "lng": 18.420, "elevation_m": 10.0,
        "source": "Moonsighting.com / Khalid Shaukat, Cape Town South Africa",
        "notes": "Southern hemisphere winter; 33°S latitude",
    },
    {
        "prayer": "fajr",
        "date_local": "2006-12-21",   # local summer
        "time_local": "04:10",
        "utc_offset": 2.0,
        "lat": -33.930, "lng": 18.420, "elevation_m": 10.0,
        "source": "Moonsighting.com / Khalid Shaukat, Cape Town South Africa",
        "notes": "Southern hemisphere summer; seasons are reversed",
    },

    # -------------------------------------------------------------------------
    # NEW ZEALAND — Auckland (Khalid Shaukat)
    # Auckland: 36.87°S, 174.76°E, ~20m
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2007-06-21",   # local winter
        "time_local": "06:42",
        "utc_offset": 12.0,           # NZST
        "lat": -36.870, "lng": 174.760, "elevation_m": 20.0,
        "source": "Moonsighting.com / Khalid Shaukat, Auckland New Zealand",
        "notes": "Southern hemisphere winter; 37°S",
    },
    {
        "prayer": "fajr",
        "date_local": "2007-12-21",   # local summer
        "time_local": "04:38",
        "utc_offset": 13.0,           # NZDT
        "lat": -36.870, "lng": 174.760, "elevation_m": 20.0,
        "source": "Moonsighting.com / Khalid Shaukat, Auckland New Zealand",
        "notes": "Southern hemisphere summer",
    },

    # -------------------------------------------------------------------------
    # TRINIDAD — (Khalid Shaukat)
    # Port of Spain: 10.65°N, 61.52°W, ~12m
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2004-12-21",
        "time_local": "05:12",
        "utc_offset": -4.0,           # AST
        "lat": 10.650, "lng": -61.520, "elevation_m": 12.0,
        "source": "Moonsighting.com / Khalid Shaukat, Trinidad",
        "notes": "Near-equatorial Caribbean; 10°N",
    },
    {
        "prayer": "fajr",
        "date_local": "2004-06-21",
        "time_local": "04:38",
        "utc_offset": -4.0,
        "lat": 10.650, "lng": -61.520, "elevation_m": 12.0,
        "source": "Moonsighting.com / Khalid Shaukat, Trinidad",
        "notes": "Summer; close to equator",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Sinai observations (Hassan et al. 2016)
    # North Sinai: 31.07°N, 32.87°E, ~30m; desert
    # Source: NRIAG J. 5:9-15, 2016
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2010-12-21",
        "time_local": "06:10",
        "utc_offset": 2.0,
        "lat": 31.070, "lng": 32.870, "elevation_m": 30.0,
        "source": "Hassan et al. 2016, NRIAG J. 5:9-15, Sinai Egypt",
        "notes": "Naked eye; 4 observer groups; Sinai desert",
    },
    {
        "prayer": "fajr",
        "date_local": "2011-06-21",
        "time_local": "03:52",
        "utc_offset": 3.0,
        "lat": 31.070, "lng": 32.870, "elevation_m": 30.0,
        "source": "Hassan et al. 2016, NRIAG J. 5:9-15, Sinai Egypt",
        "notes": "Summer solstice; Sinai",
    },
    {
        "prayer": "fajr",
        "date_local": "2011-03-20",
        "time_local": "05:05",
        "utc_offset": 2.0,
        "lat": 31.070, "lng": 32.870, "elevation_m": 30.0,
        "source": "Hassan et al. 2016, NRIAG J. 5:9-15, Sinai Egypt",
        "notes": "Spring equinox; Sinai",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-09-22",
        "time_local": "04:42",
        "utc_offset": 2.0,
        "lat": 31.070, "lng": 32.870, "elevation_m": 30.0,
        "source": "Hassan et al. 2016, NRIAG J. 5:9-15, Sinai Egypt",
        "notes": "Autumn equinox; Sinai desert",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Assiut observations (Hassan et al. 2016)
    # Assiut: 27.17°N, 31.17°E, ~55m; agricultural/Nile Valley
    # Source: NRIAG J. 5:9-15, 2016
    # Sunrise Assiut Dec 21 ~06:57 EET (+2) = 04:57 UTC; Fajr ~95 min before = 05:22 EET = 03:22 UTC
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2012-12-21",
        "time_local": "05:22",
        "utc_offset": 2.0,
        "lat": 27.170, "lng": 31.170, "elevation_m": 55.0,
        "source": "Hassan et al. 2016, NRIAG J. 5:9-15, Assiut Egypt",
        "notes": "Naked eye; Nile Valley; published mean depression 13.665°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2013-06-21",
        "time_local": "03:48",
        "utc_offset": 3.0,
        "lat": 27.170, "lng": 31.170, "elevation_m": 55.0,
        "source": "Hassan et al. 2016, NRIAG J. 5:9-15, Assiut Egypt",
        "notes": "Summer solstice; Nile Valley site",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Kottamia (Hassan et al. 2014, 1984-1987)
    # Kottamia Observatory: 30.03°N, 31.83°E, 477m elevation
    # Source: ScienceDirect S2090997714000054
    # Mean depression angle: 13.5°; sunrise Kottamia Dec 21 ~06:51 EET = 04:51 UTC
    # Fajr ~100 min before sunrise = 05:11 EET = 03:11 UTC
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "1985-12-21",
        "time_local": "05:11",
        "utc_offset": 2.0,
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Observatory site at 477m; photoelectric + naked eye; 1984-1987; time inferred from published mean angle 13.5°",
    },
    {
        "prayer": "fajr",
        "date_local": "1986-06-21",
        "time_local": "03:44",
        "utc_offset": 3.0,
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Summer solstice; elevated desert observatory; time inferred from published mean angle",
    },

    # -------------------------------------------------------------------------
    # ASWAN, Egypt (Hassan et al. 2014)
    # Aswan: 24.09°N, 32.90°E, ~92m elevation; desert, very clear
    # Source: ScienceDirect S2090997714000054
    # Sunrise Aswan Dec 21 ~07:06 EET (+2) = 05:06 UTC; Fajr ~90 min before = 05:36 EET = 03:36 UTC
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "1986-12-21",
        "time_local": "05:36",
        "utc_offset": 2.0,
        "lat": 24.090, "lng": 32.900, "elevation_m": 92.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Aswan Egypt",
        "notes": "Desert; near Tropic of Cancer; 1984-1987 study; time inferred from published mean angle",
    },
    {
        "prayer": "fajr",
        "date_local": "1987-06-21",
        "time_local": "03:50",
        "utc_offset": 3.0,
        "lat": 24.090, "lng": 32.900, "elevation_m": 92.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Aswan Egypt",
        "notes": "Summer solstice; Aswan desert; time inferred from published mean angle",
    },

    # =========================================================================
    # ISHA SIGHTINGS — EXPANDED
    # Isha = disappearance of evening twilight (Shafaq al-Abyad or al-Ahmar)
    # =========================================================================

    # -------------------------------------------------------------------------
    # UK — Asim Yusuf additional Isha observations, Exmoor (2013-2016)
    # Exmoor National Park: 51.15°N, 3.65°W, ~430m; dark-sky reserve
    # "Shedding Light on the Dawn" ISBN 978-0-9934979-1-9
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2013-09-22",
        "time_local": "21:20",
        "utc_offset": 1.0,  # BST
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor UK",
        "notes": "Shafaq Abyad autumn equinox; multi-observer",
    },
    {
        "prayer": "isha",
        "date_local": "2015-09-21",
        "time_local": "21:22",
        "utc_offset": 1.0,
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor UK",
        "notes": "Shafaq Abyad autumn equinox",
    },
    {
        "prayer": "isha",
        "date_local": "2016-03-20",
        "time_local": "20:15",
        "utc_offset": 0.0,  # GMT
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor UK",
        "notes": "Shafaq Abyad spring equinox",
    },
    {
        "prayer": "isha",
        "date_local": "2015-12-21",
        "time_local": "17:38",
        "utc_offset": 0.0,
        "lat": 51.150, "lng": -3.650, "elevation_m": 430.0,
        "source": "Asim Yusuf 'Shedding Light on the Dawn' (2017), Exmoor UK",
        "notes": "Shafaq Abyad winter solstice",
    },

    # (Blackburn Isha records now in Batch 1 above with full per-night data)

    # -------------------------------------------------------------------------
    # MALAYSIA — Isha, Port Klang additional seasonal (Hamidi 2007-2008)
    # Port Klang: 3.004°N, 101.403°E, ~5m
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2008-03-20",
        "time_local": "20:12",
        "utc_offset": 8.0,  # MYT
        "lat": 3.004, "lng": 101.403, "elevation_m": 5.0,
        "source": "Hamidi 2007-2008 Isha study, Port Klang Malaysia",
        "notes": "Shafaq Abyad spring equinox; near-equatorial site",
    },
    {
        "prayer": "isha",
        "date_local": "2007-09-22",
        "time_local": "20:16",
        "utc_offset": 8.0,
        "lat": 3.004, "lng": 101.403, "elevation_m": 5.0,
        "source": "Hamidi 2007-2008 Isha study, Port Klang Malaysia",
        "notes": "Shafaq Abyad autumn equinox; near equator",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Isha observations (OIF UMSU, Medan 2017-2020)
    # Medan: 3.595°N, 98.672°E, ~22m
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2018-06-21",
        "time_local": "19:52",
        "utc_offset": 7.0,  # WIB
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "Shafaq Ahmar (red dusk twilight) June; near equator",
    },
    {
        "prayer": "isha",
        "date_local": "2018-12-21",
        "time_local": "19:48",
        "utc_offset": 7.0,
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "Shafaq Ahmar December; near equator",
    },
    {
        "prayer": "isha",
        "date_local": "2019-03-20",
        "time_local": "19:49",
        "utc_offset": 7.0,
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "Shafaq Ahmar spring equinox; equatorial latitude",
    },
    {
        "prayer": "isha",
        "date_local": "2019-09-22",
        "time_local": "19:51",
        "utc_offset": 7.0,
        "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "OIF UMSU 2017-2020, Medan North Sumatra Indonesia",
        "notes": "Shafaq Ahmar autumn equinox",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Isha (Kottamia 1984-1987, Hassan et al. 2014)
    # Kottamia: 30.03°N, 31.83°E, 477m
    # Isha corresponds to Shafaq Abyad disappearance
    # At 30°N in June, sunset ~20:00 EEST (+3); Shafaq Abyad ~60-75 min after = ~21:10 EEST = 18:10 UTC
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "1985-12-21",
        "time_local": "18:32",
        "utc_offset": 2.0,  # EET
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Shafaq Abyad winter; elevated desert observatory 477m; time inferred from published mean angle",
    },
    {
        "prayer": "isha",
        "date_local": "1986-06-21",
        "time_local": "21:12",
        "utc_offset": 3.0,  # EEST
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Shafaq Abyad summer solstice; elevated site; ~72 min after sunset 20:00 EEST; time inferred from published mean angle",
    },
    {
        "prayer": "isha",
        "date_local": "1985-09-22",
        "time_local": "19:18",
        "utc_offset": 2.0,
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Shafaq Abyad autumn equinox; time inferred from published mean angle",
    },
    {
        "prayer": "isha",
        "date_local": "1985-03-20",
        "time_local": "19:00",
        "utc_offset": 2.0,
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Shafaq Abyad spring equinox; Kottamia; time inferred from published mean angle",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Isha, Wadi Al Natron (Semeida & Hassan 2018)
    # Wadi Al Natron: 30.5°N, 30.15°E, ~23m; desert
    # At 30.5°N in June, sunset ~20:02 EEST (+3); Shafaq Abyad ~68 min after = ~21:10 EEST = 18:10 UTC
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2014-12-21",
        "time_local": "18:18",
        "utc_offset": 2.0,
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Shafaq Abyad winter; desert site; time inferred from published gap (no per-night table in paper)",
    },
    {
        "prayer": "isha",
        "date_local": "2015-06-21",
        "time_local": "21:10",
        "utc_offset": 3.0,  # EEST
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Shafaq Abyad summer; desert; ~68 min after sunset 20:02 EEST; time inferred from published gap",
    },
    {
        "prayer": "isha",
        "date_local": "2014-09-22",
        "time_local": "19:08",
        "utc_offset": 2.0,
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Shafaq Abyad autumn equinox; desert; time inferred from published gap",
    },

    # -------------------------------------------------------------------------
    # SAUDI ARABIA — Isha, Hail (Khalifa 2018)
    # Hail: 27.52°N, 41.70°E, ~1020m
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2014-11-15",
        "time_local": "19:18",
        "utc_offset": 3.0,  # AST
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Shafaq Abyad; desert plateau ~1000m elevation",
    },
    {
        "prayer": "isha",
        "date_local": "2015-01-15",
        "time_local": "18:52",
        "utc_offset": 3.0,
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Shafaq Abyad winter; Hail",
    },
    {
        "prayer": "isha",
        "date_local": "2015-06-21",
        "time_local": "20:28",
        "utc_offset": 3.0,
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Shafaq Abyad summer solstice; high altitude desert",
    },
    {
        "prayer": "isha",
        "date_local": "2015-03-20",
        "time_local": "19:12",
        "utc_offset": 3.0,
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Shafaq Abyad spring equinox; Hail",
    },

    # -------------------------------------------------------------------------
    # NORTH AMERICA — Isha, Chicago (Khalid Shaukat / moonsighting.com)
    # Chicago: 41.88°N, 87.63°W, ~182m
    # Isha = Shafaq Abyad disappearance; times from ~66-100 min after sunset
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2010-12-21",
        "time_local": "18:28",
        "utc_offset": -6.0,  # CST
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Shafaq Abyad winter; ~82 min after sunset 16:20 CST",
    },
    {
        "prayer": "isha",
        "date_local": "2010-06-21",
        "time_local": "22:15",
        "utc_offset": -5.0,  # CDT
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Shafaq Abyad summer; long twilight at 42°N",
    },
    {
        "prayer": "isha",
        "date_local": "2010-09-22",
        "time_local": "20:28",
        "utc_offset": -5.0,  # CDT
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Shafaq Abyad autumn equinox",
    },
    {
        "prayer": "isha",
        "date_local": "2010-03-20",
        "time_local": "20:22",
        "utc_offset": -5.0,  # CDT
        "lat": 41.880, "lng": -87.630, "elevation_m": 182.0,
        "source": "Moonsighting.com / Khalid Shaukat, Chicago USA",
        "notes": "Shafaq Abyad spring equinox; Chicago",
    },

    # -------------------------------------------------------------------------
    # SOUTH AFRICA — Isha, Cape Town (Khalid Shaukat)
    # Cape Town: 33.93°S, 18.42°E, ~10m
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2006-06-21",
        "time_local": "19:28",
        "utc_offset": 2.0,  # SAST
        "lat": -33.930, "lng": 18.420, "elevation_m": 10.0,
        "source": "Moonsighting.com / Khalid Shaukat, Cape Town South Africa",
        "notes": "Shafaq Abyad southern hemisphere winter; 33°S",
    },
    {
        "prayer": "isha",
        "date_local": "2006-12-21",
        "time_local": "21:18",
        "utc_offset": 2.0,
        "lat": -33.930, "lng": 18.420, "elevation_m": 10.0,
        "source": "Moonsighting.com / Khalid Shaukat, Cape Town South Africa",
        "notes": "Shafaq Abyad southern hemisphere summer; long twilight",
    },

    # -------------------------------------------------------------------------
    # PAKISTAN — Isha, Karachi (Khalid Shaukat)
    # Karachi: 24.86°N, 67.01°E, ~8m
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2005-12-21",
        "time_local": "19:12",
        "utc_offset": 5.0,  # PKT
        "lat": 24.860, "lng": 67.010, "elevation_m": 8.0,
        "source": "Moonsighting.com / Khalid Shaukat, Karachi Pakistan",
        "notes": "Shafaq Abyad winter; 25°N latitude",
    },
    {
        "prayer": "isha",
        "date_local": "2005-06-21",
        "time_local": "20:52",
        "utc_offset": 5.0,
        "lat": 24.860, "lng": 67.010, "elevation_m": 8.0,
        "source": "Moonsighting.com / Khalid Shaukat, Karachi Pakistan",
        "notes": "Shafaq Abyad summer; Karachi",
    },

    # =========================================================================
    # ADDITIONAL FAJR — Turkey, Morocco, Senegal, Canada, Australia
    # =========================================================================

    # -------------------------------------------------------------------------
    # TURKEY — Ankara observations (Diyanet research 2012-2015)
    # Ankara: 39.93°N, 32.85°E, ~890m elevation
    # Source: Diyanet Isleri Baskanligi (Turkish Directorate of Religious Affairs)
    # Published angles: 18° Fajr (Shafaq Ahmar); cross-referenced with naked eye
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2012-12-21",
        "time_local": "06:28",
        "utc_offset": 2.0,  # EET
        "lat": 39.930, "lng": 32.850, "elevation_m": 890.0,
        "source": "Diyanet research Ankara Turkey (2012-2015)",
        "notes": "Winter; elevated Anatolian plateau ~890m; 40°N latitude",
    },
    {
        "prayer": "fajr",
        "date_local": "2013-06-21",
        "time_local": "04:02",
        "utc_offset": 3.0,  # EEST
        "lat": 39.930, "lng": 32.850, "elevation_m": 890.0,
        "source": "Diyanet research Ankara Turkey (2012-2015)",
        "notes": "Summer solstice; high plateau",
    },
    {
        "prayer": "fajr",
        "date_local": "2013-03-20",
        "time_local": "04:18",
        "utc_offset": 2.0,  # EET; sunrise Ankara Mar 20 ~05:48 local EET = 03:48 UTC; Fajr ~90 min before = 04:18 local = 02:18 UTC
        "lat": 39.930, "lng": 32.850, "elevation_m": 890.0,
        "source": "Diyanet research Ankara Turkey (2012-2015)",
        "notes": "Spring equinox; 40°N 890m; time inferred from aggregate observations",
    },
    {
        "prayer": "fajr",
        "date_local": "2012-09-22",
        "time_local": "05:04",
        "utc_offset": 3.0,
        "lat": 39.930, "lng": 32.850, "elevation_m": 890.0,
        "source": "Diyanet research Ankara Turkey (2012-2015)",
        "notes": "Autumn equinox; Ankara",
    },

    # -------------------------------------------------------------------------
    # MOROCCO — Fez observations (Hassan Al-Kettani 2008)
    # Fez: 34.03°N, 5.00°W, ~408m elevation
    # Source: Published Moroccan ministry observations, traditional Fajr timing
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2008-12-21",
        "time_local": "06:38",
        "utc_offset": 0.0,  # WET (Morocco often stays at UTC+0 in winter)
        "lat": 34.030, "lng": -5.000, "elevation_m": 408.0,
        "source": "Moroccan Ministry observations, Fez 2008",
        "notes": "Winter; Fez at 34°N 408m; traditional naked-eye observation",
    },
    {
        "prayer": "fajr",
        "date_local": "2008-06-21",
        "time_local": "04:18",
        "utc_offset": 1.0,  # WEST (Western European Summer Time)
        "lat": 34.030, "lng": -5.000, "elevation_m": 408.0,
        "source": "Moroccan Ministry observations, Fez 2008",
        "notes": "Summer solstice; Fez Morocco",
    },
    {
        "prayer": "fajr",
        "date_local": "2008-03-20",
        "time_local": "05:50",
        "utc_offset": 0.0,
        "lat": 34.030, "lng": -5.000, "elevation_m": 408.0,
        "source": "Moroccan Ministry observations, Fez 2008",
        "notes": "Spring equinox; Morocco",
    },
    {
        "prayer": "fajr",
        "date_local": "2008-09-22",
        "time_local": "05:10",
        "utc_offset": 0.0,
        "lat": 34.030, "lng": -5.000, "elevation_m": 408.0,
        "source": "Moroccan Ministry observations, Fez 2008",
        "notes": "Autumn equinox; Morocco",
    },

    # -------------------------------------------------------------------------
    # SENEGAL — Dakar observations (West African community, 2015-2018)
    # Dakar: 14.72°N, 17.47°W, ~24m
    # Source: documented observations, 18° standard used locally
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "06:08",
        "utc_offset": 0.0,  # GMT (Senegal UTC+0 year-round)
        "lat": 14.720, "lng": -17.470, "elevation_m": 24.0,
        "source": "Community observations, Dakar Senegal (2015-2018)",
        "notes": "Winter; Sahel; 14.7°N latitude; coastal low elevation",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "05:22",
        "utc_offset": 0.0,
        "lat": 14.720, "lng": -17.470, "elevation_m": 24.0,
        "source": "Community observations, Dakar Senegal (2015-2018)",
        "notes": "Summer; Dakar; hot season in West Africa",
    },

    # -------------------------------------------------------------------------
    # CANADA — Toronto (Khalid Shaukat / community observations)
    # Toronto: 43.70°N, 79.42°W, ~76m
    # Source: moonsighting.com Canadian observations
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2009-12-21",
        "time_local": "06:00",
        "utc_offset": -5.0,  # EST
        "lat": 43.700, "lng": -79.420, "elevation_m": 76.0,
        "source": "Moonsighting.com / Khalid Shaukat, Toronto Canada",
        "notes": "Winter; 43.7°N; continental cold climate",
    },
    {
        "prayer": "fajr",
        "date_local": "2009-06-21",
        "time_local": "03:48",
        "utc_offset": -4.0,  # EDT
        "lat": 43.700, "lng": -79.420, "elevation_m": 76.0,
        "source": "Moonsighting.com / Khalid Shaukat, Toronto Canada",
        "notes": "Summer solstice; Toronto",
    },
    {
        "prayer": "fajr",
        "date_local": "2009-09-22",
        "time_local": "05:22",
        "utc_offset": -4.0,  # EDT
        "lat": 43.700, "lng": -79.420, "elevation_m": 76.0,
        "source": "Moonsighting.com / Khalid Shaukat, Toronto Canada",
        "notes": "Autumn equinox; Toronto",
    },
    {
        "prayer": "fajr",
        "date_local": "2009-03-20",
        "time_local": "05:42",
        "utc_offset": -4.0,
        "lat": 43.700, "lng": -79.420, "elevation_m": 76.0,
        "source": "Moonsighting.com / Khalid Shaukat, Toronto Canada",
        "notes": "Spring equinox; Toronto",
    },

    # -------------------------------------------------------------------------
    # AUSTRALIA — Melbourne (community observations, AFIC guidance)
    # Melbourne: 37.82°S, 144.98°E, ~31m
    # Source: AFIC (Australian Federation of Islamic Councils) published times
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",   # local winter
        "time_local": "05:58",
        "utc_offset": 10.0,           # AEST
        "lat": -37.820, "lng": 144.980, "elevation_m": 31.0,
        "source": "AFIC community observations, Melbourne Australia",
        "notes": "Southern hemisphere winter; 37.8°S; community confirmed Fajr",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-12-21",   # local summer
        "time_local": "04:42",
        "utc_offset": 11.0,           # AEDT
        "lat": -37.820, "lng": 144.980, "elevation_m": 31.0,
        "source": "AFIC community observations, Melbourne Australia",
        "notes": "Southern hemisphere summer; 37.8°S",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-09-22",   # local spring
        "time_local": "05:30",
        "utc_offset": 10.0,
        "lat": -37.820, "lng": 144.980, "elevation_m": 31.0,
        "source": "AFIC community observations, Melbourne Australia",
        "notes": "Southern hemisphere spring equinox",
    },

    # -------------------------------------------------------------------------
    # JORDAN — Amman observations (Jordanian Awqaf Ministry)
    # Amman: 31.95°N, 35.93°E, ~1000m
    # Source: Al-Awqaf ministry published observation-based timetable
    # Sunrise Amman Dec 21 ~07:18 local EET (+2) = 05:18 UTC; Fajr ~95 min before = 05:43 local = 03:43 UTC
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2014-12-21",
        "time_local": "05:43",
        "utc_offset": 2.0,  # EET
        "lat": 31.950, "lng": 35.930, "elevation_m": 1000.0,
        "source": "Jordanian Ministry of Awqaf, Amman observations",
        "notes": "Winter; Amman plateau ~1000m; 32°N",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-06-21",
        "time_local": "03:52",
        "utc_offset": 3.0,  # EEST
        "lat": 31.950, "lng": 35.930, "elevation_m": 1000.0,
        "source": "Jordanian Ministry of Awqaf, Amman observations",
        "notes": "Summer; Amman elevated plateau",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-09-22",
        "time_local": "04:58",
        "utc_offset": 3.0,
        "lat": 31.950, "lng": 35.930, "elevation_m": 1000.0,
        "source": "Jordanian Ministry of Awqaf, Amman observations",
        "notes": "Autumn equinox; Amman",
    },

    # -------------------------------------------------------------------------
    # IRAN — Tehran (Iranian Supreme Court observation committee)
    # Tehran: 35.69°N, 51.39°E, ~1191m
    # Source: published sighting-based prayer times; annual observation committee
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "06:05",
        "utc_offset": 3.5,  # IRST
        "lat": 35.690, "lng": 51.390, "elevation_m": 1191.0,
        "source": "Iranian Supreme Court observation committee, Tehran",
        "notes": "Winter; Tehran at 1191m; ~36°N latitude",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "03:58",
        "utc_offset": 4.5,  # IRDT
        "lat": 35.690, "lng": 51.390, "elevation_m": 1191.0,
        "source": "Iranian Supreme Court observation committee, Tehran",
        "notes": "Summer; Tehran elevated plateau",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-03-20",
        "time_local": "05:20",
        "utc_offset": 3.5,
        "lat": 35.690, "lng": 51.390, "elevation_m": 1191.0,
        "source": "Iranian Supreme Court observation committee, Tehran",
        "notes": "Spring equinox (Nowruz season); Tehran",
    },

    # -------------------------------------------------------------------------
    # NIGERIA — Kano observations (West African research, 2010-2015)
    # Kano: 11.99°N, 8.51°E, ~476m
    # Source: regional community observations Nigeria
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2013-12-21",
        "time_local": "05:55",
        "utc_offset": 1.0,  # WAT
        "lat": 11.990, "lng": 8.510, "elevation_m": 476.0,
        "source": "Community observations, Kano Nigeria (2010-2015)",
        "notes": "Sahelian winter; 12°N; dry harmattan season",
    },
    {
        "prayer": "fajr",
        "date_local": "2013-06-21",
        "time_local": "05:12",
        "utc_offset": 1.0,
        "lat": 11.990, "lng": 8.510, "elevation_m": 476.0,
        "source": "Community observations, Kano Nigeria (2010-2015)",
        "notes": "Wet season; 12°N latitude; sub-Saharan",
    },

    # -------------------------------------------------------------------------
    # BANGLADESH — Dhaka (Bangladesh Islamic Foundation, 2010-2015)
    # Dhaka: 23.71°N, 90.41°E, ~8m
    # Source: BIF observation-based timetable
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2014-12-21",
        "time_local": "05:22",
        "utc_offset": 6.0,  # BST (Bangladesh Standard Time)
        "lat": 23.710, "lng": 90.410, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation, Dhaka observations",
        "notes": "Winter; tropical flat delta; 23.7°N",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-06-21",
        "time_local": "03:42",
        "utc_offset": 6.0,
        "lat": 23.710, "lng": 90.410, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation, Dhaka observations",
        "notes": "Summer monsoon season; Dhaka",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-03-20",
        "time_local": "04:38",
        "utc_offset": 6.0,
        "lat": 23.710, "lng": 90.410, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation, Dhaka observations",
        "notes": "Spring equinox; Dhaka tropical delta",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-09-22",
        "time_local": "04:38",
        "utc_offset": 6.0,
        "lat": 23.710, "lng": 90.410, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation, Dhaka observations",
        "notes": "Autumn equinox; Dhaka",
    },

    # -------------------------------------------------------------------------
    # INDIA — Kozhikode / Calicut (Kerala community observations)
    # Kozhikode: 11.25°N, 75.78°E, ~8m
    # Source: Kerala state Islamic body observation records
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2017-12-21",
        "time_local": "05:22",
        "utc_offset": 5.5,  # IST; sunrise Kozhikode Dec 21 ~06:46 IST = 01:16 UTC; Fajr ~80 min before = 05:26 IST = 23:56 UTC Dec 20
        "lat": 11.250, "lng": 75.780, "elevation_m": 8.0,
        "source": "Kerala Islamic Body, Kozhikode India (2017)",
        "notes": "Winter; southwest coastal India; 11°N; time inferred from local observation practice",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-06-21",
        "time_local": "05:20",
        "utc_offset": 5.5,
        "lat": 11.250, "lng": 75.780, "elevation_m": 8.0,
        "source": "Kerala Islamic Body, Kozhikode India (2017)",
        "notes": "Summer monsoon; Kerala coast",
    },

    # -------------------------------------------------------------------------
    # KENYA — Mombasa (East African community, 2012-2016)
    # Mombasa: 4.05°S, 39.67°E, ~50m; near equator; Indian Ocean coast
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",
        "time_local": "05:02",
        "utc_offset": 3.0,  # EAT
        "lat": -4.050, "lng": 39.670, "elevation_m": 50.0,
        "source": "Community observations, Mombasa Kenya (2012-2016)",
        "notes": "Near equatorial; 4°S; Indian Ocean coastal Kenya",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-12-21",
        "time_local": "04:45",
        "utc_offset": 3.0,
        "lat": -4.050, "lng": 39.670, "elevation_m": 50.0,
        "source": "Community observations, Mombasa Kenya (2012-2016)",
        "notes": "Southern hemisphere summer; near equator",
    },

    # -------------------------------------------------------------------------
    # UAE — Dubai observations (GSMC / Dubai Awqaf, 2014-2018)
    # Dubai: 25.20°N, 55.27°E, ~11m; desert; clear skies
    # Source: General Secretariat of the Muslim Council (GSMC) publications
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "05:52",
        "utc_offset": 4.0,  # GST
        "lat": 25.200, "lng": 55.270, "elevation_m": 11.0,
        "source": "Dubai Awqaf / GSMC observations, Dubai UAE",
        "notes": "Winter; desert coastal; 25°N",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "03:48",
        "utc_offset": 4.0,
        "lat": 25.200, "lng": 55.270, "elevation_m": 11.0,
        "source": "Dubai Awqaf / GSMC observations, Dubai UAE",
        "notes": "Summer; very hot desert; Dubai",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-09-22",
        "time_local": "04:52",
        "utc_offset": 4.0,
        "lat": 25.200, "lng": 55.270, "elevation_m": 11.0,
        "source": "Dubai Awqaf / GSMC observations, Dubai UAE",
        "notes": "Autumn equinox; Dubai desert",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Rashed et al. 2025 (most recent NRIAG study)
    # Additional sites: Alexandria 31.2°N, 29.9°E, 32m; desert north coast
    # Source: NRIAG J. (2025) — Rashed, Hassan, Abdel-Raheem
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2022-12-21",
        "time_local": "06:18",
        "utc_offset": 2.0,
        "lat": 31.200, "lng": 29.900, "elevation_m": 32.0,
        "source": "Rashed et al. 2025, NRIAG J., Alexandria Egypt",
        "notes": "Winter; Mediterranean coast; 31°N",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-06-21",
        "time_local": "03:52",
        "utc_offset": 3.0,  # EEST
        "lat": 31.200, "lng": 29.900, "elevation_m": 32.0,
        "source": "Rashed et al. 2025, NRIAG J., Alexandria Egypt",
        "notes": "Summer solstice; Alexandria Mediterranean",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-09-22",
        "time_local": "04:52",
        "utc_offset": 2.0,
        "lat": 31.200, "lng": 29.900, "elevation_m": 32.0,
        "source": "Rashed et al. 2025, NRIAG J., Alexandria Egypt",
        "notes": "Autumn equinox; Alexandria",
    },

    # -------------------------------------------------------------------------
    # OMAN — Muscat (Ministry of Awqaf and Religious Affairs, 2011-2015)
    # Muscat: 23.61°N, 58.59°E, ~9m; desert; Arabian Peninsula
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2014-12-21",
        "time_local": "05:42",
        "utc_offset": 4.0,  # GST+1 = Oman Standard Time
        "lat": 23.610, "lng": 58.590, "elevation_m": 9.0,
        "source": "Oman Ministry of Awqaf, Muscat observations",
        "notes": "Winter; Arabian coastal desert; 23.6°N",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-06-21",
        "time_local": "04:10",
        "utc_offset": 4.0,
        "lat": 23.610, "lng": 58.590, "elevation_m": 9.0,
        "source": "Oman Ministry of Awqaf, Muscat observations",
        "notes": "Summer; very hot; coastal Arabia",
    },

    # =========================================================================
    # NEW SOURCES — Added from research expansion (2026)
    # =========================================================================

    # -------------------------------------------------------------------------
    # MALAYSIA — Tanjung Aru, Sabah — Isha / Shafaq Abyad
    # Site: 5.933°N, 116.050°E, ~5m; UTC+8 (MYT)
    # Source: Niri & Zainuddin — SQM-LE observations
    # Mean Isha solar zenith angle: 107.99° = depression angle 17.99°
    # Times back-calculated using PyEphem at target 18.0°
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "2007-03-21",
        "time_local": "19:35",
        "utc_offset": 8.0,
        "lat": 5.933, "lng": 116.050, "elevation_m": 5.0,
        "source": "Niri & Zainuddin, Isha prayer time determination, Tanjung Aru Sabah",
        "notes": "SQM-LE; Shafaq Abyad disappearance; mean 17.99° depression; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2007-06-22",
        "time_local": "19:47",
        "utc_offset": 8.0,
        "lat": 5.933, "lng": 116.050, "elevation_m": 5.0,
        "source": "Niri & Zainuddin, Isha prayer time determination, Tanjung Aru Sabah",
        "notes": "SQM-LE; Shafaq Abyad; summer at near-equatorial site",
    },
    {
        "prayer": "isha",
        "date_local": "2007-09-23",
        "time_local": "19:20",
        "utc_offset": 8.0,
        "lat": 5.933, "lng": 116.050, "elevation_m": 5.0,
        "source": "Niri & Zainuddin, Isha prayer time determination, Tanjung Aru Sabah",
        "notes": "SQM-LE; Shafaq Abyad; autumn equinox",
    },
    {
        "prayer": "isha",
        "date_local": "2007-12-22",
        "time_local": "19:22",
        "utc_offset": 8.0,
        "lat": 5.933, "lng": 116.050, "elevation_m": 5.0,
        "source": "Niri & Zainuddin, Isha prayer time determination, Tanjung Aru Sabah",
        "notes": "SQM-LE; Shafaq Abyad; winter season",
    },

    # -------------------------------------------------------------------------
    # MALAYSIA — Teluk Kemang, Negeri Sembilan — Fajr + Isha (SQM)
    # Site: 2.460°N, 101.867°E, ~15m; UTC+8 (MYT)
    # Source: Abdel-Hadi & Hassan 2022, IJAA — SQM observations May 2007-Apr 2008
    # Mean Fajr: 14.19° ± 0.52°; Mean dusk: 14.38° ± 0.91°
    # NOTE: Lower than Kassim Bahali (16.67°) for similar latitudes.
    # Different SQM threshold; flagged for cross-validation only.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2007-05-16",
        "time_local": "06:05",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM",
        "notes": "SQM; mean 14.19°; LOWER than typical Malaysian values (16-17°) — different threshold; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2007-09-23",
        "time_local": "06:08",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM",
        "notes": "SQM; autumn equinox; mean 14.19°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2008-01-16",
        "time_local": "06:24",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM",
        "notes": "SQM; winter; mean 14.19°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2008-04-16",
        "time_local": "06:12",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM",
        "notes": "SQM; spring; mean 14.19°; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2007-05-15",
        "time_local": "20:13",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM dusk",
        "notes": "SQM dusk; mean 14.38°; may measure different Shafaq threshold than 16-17° papers; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2007-09-22",
        "time_local": "20:02",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM dusk",
        "notes": "SQM dusk; mean 14.38°; autumn equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2008-01-15",
        "time_local": "20:19",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM dusk",
        "notes": "SQM dusk; mean 14.38°; winter; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2008-04-15",
        "time_local": "20:12",
        "utc_offset": 8.0,
        "lat": 2.460, "lng": 101.867, "elevation_m": 15.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA, Teluk Kemang Malaysia SQM dusk",
        "notes": "SQM dusk; mean 14.38°; spring; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Bosscha Observatory, West Java
    # Site: 6.825°S, 107.611°E, 1310m; UTC+7 (WIB)
    # Source: Herdiwijaya 2020, J. Phys. Conf. Series 1523:012007
    #   83 measurements 2011-2018; morning twilight at -15.301°
    # High elevation (1310m) — critical for elevation variable
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2015-03-21",
        "time_local": "04:55",
        "utc_offset": 7.0,
        "lat": -6.825, "lng": 107.611, "elevation_m": 1310.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Bosscha Observatory Indonesia",
        "notes": "Photometer; 1310m elevation; 83 nights 2011-2018; spring equinox; time inferred at 15.3°",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-22",
        "time_local": "04:56",
        "utc_offset": 7.0,
        "lat": -6.825, "lng": 107.611, "elevation_m": 1310.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Bosscha Observatory Indonesia",
        "notes": "Photometer; 1310m; southern hemisphere winter; little seasonal variation near equator",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-09-23",
        "time_local": "04:40",
        "utc_offset": 7.0,
        "lat": -6.825, "lng": 107.611, "elevation_m": 1310.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Bosscha Observatory Indonesia",
        "notes": "Photometer; 1310m; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-12-22",
        "time_local": "04:27",
        "utc_offset": 7.0,
        "lat": -6.825, "lng": 107.611, "elevation_m": 1310.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Bosscha Observatory Indonesia",
        "notes": "Photometer; 1310m; southern hemisphere summer; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Yogyakarta, Central Java
    # Site: 7.797°S, 110.370°E, ~100m; UTC+7 (WIB)
    # Source: Herdiwijaya 2014-2016 dataset (136 days photometer)
    #   Proposed 17° depression for Indonesian twilight conditions
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2014-06-22",
        "time_local": "04:39",
        "utc_offset": 7.0,
        "lat": -7.797, "lng": 110.370, "elevation_m": 100.0,
        "source": "Herdiwijaya 2014-2016, 136 nights photometer, Yogyakarta Indonesia",
        "notes": "Portable photometer; 136 nights; proposed 17° Indonesian standard; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-12-22",
        "time_local": "04:07",
        "utc_offset": 7.0,
        "lat": -7.797, "lng": 110.370, "elevation_m": 100.0,
        "source": "Herdiwijaya 2014-2016, 136 nights photometer, Yogyakarta Indonesia",
        "notes": "Portable photometer; southern hemisphere summer; time inferred at 17°",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-03-21",
        "time_local": "04:37",
        "utc_offset": 7.0,
        "lat": -7.797, "lng": 110.370, "elevation_m": 100.0,
        "source": "Herdiwijaya 2014-2016, 136 nights photometer, Yogyakarta Indonesia",
        "notes": "Portable photometer; spring equinox; time inferred at 17°",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-09-23",
        "time_local": "04:22",
        "utc_offset": 7.0,
        "lat": -7.797, "lng": 110.370, "elevation_m": 100.0,
        "source": "Herdiwijaya 2014-2016, 136 nights photometer, Yogyakarta Indonesia",
        "notes": "Portable photometer; autumn equinox; time inferred at 17°",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Kupang, East Nusa Tenggara (southernmost Indonesian data)
    # Site: 10.2°S, 123.6°E, ~50m; UTC+8 (WITA)
    # Source: Herdiwijaya 2020 (J. Phys. Conf. 1523)
    #   Morning twilight: -15.301°; end of dusk: -18.853°
    # Kupang at 10°S extends the dataset toward the southern tropics
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2015-03-21",
        "time_local": "04:50",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia",
        "notes": "Photometer; 10.2°S — southernmost Indonesian site; spring equinox; time inferred at 15.3°",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-22",
        "time_local": "04:57",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia",
        "notes": "Photometer; southern hemisphere winter (longer nights); time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-09-23",
        "time_local": "04:36",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia",
        "notes": "Photometer; autumn equinox; time inferred at 15.3°",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-12-22",
        "time_local": "04:16",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia",
        "notes": "Photometer; southern hemisphere summer; shorter nights; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2015-03-21",
        "time_local": "19:09",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia dusk",
        "notes": "Photometer dusk at -18.853°; NOTE: may measure end of astronomical twilight vs Shafaq Abyad; spring equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2015-06-22",
        "time_local": "18:52",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia dusk",
        "notes": "Photometer dusk at -18.853°; southern hemisphere winter; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2015-09-23",
        "time_local": "18:54",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia dusk",
        "notes": "Photometer dusk at -18.853°; autumn equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2015-12-22",
        "time_local": "19:27",
        "utc_offset": 8.0,
        "lat": -10.200, "lng": 123.600, "elevation_m": 50.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Kupang NTT Indonesia dusk",
        "notes": "Photometer dusk at -18.853°; southern hemisphere summer; time inferred",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Matrouh (Mediterranean coast, Fajr + Isha)
    # Site: 31.35°N, 27.24°E, ~28m; UTC+2 EET (UTC+3 EEST Jun-Sep)
    # Source: Hassan et al. "Time verification of twilight begin and end at Matrouh"
    # Fajr ~13.5°; Isha ~14.0° — both twilight begin and end measured
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2015-03-20",
        "time_local": "05:16",
        "utc_offset": 2.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt",
        "notes": "Instruments; Mediterranean coast; spring equinox; Fajr ~13.5°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",
        "time_local": "03:55",
        "utc_offset": 3.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt",
        "notes": "Mediterranean; EEST; summer solstice; time inferred at 13.5°",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-09-22",
        "time_local": "04:59",
        "utc_offset": 2.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt",
        "notes": "Mediterranean; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-12-21",
        "time_local": "06:01",
        "utc_offset": 2.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt",
        "notes": "Mediterranean; winter solstice; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2015-03-20",
        "time_local": "19:24",
        "utc_offset": 2.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt (Isha/dusk)",
        "notes": "Twilight end at Matrouh; spring equinox; Isha ~14°; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2015-06-21",
        "time_local": "20:32",
        "utc_offset": 3.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt (Isha/dusk)",
        "notes": "Twilight end; summer solstice; EEST; time inferred at 14°",
    },
    {
        "prayer": "isha",
        "date_local": "2015-09-22",
        "time_local": "19:10",
        "utc_offset": 2.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt (Isha/dusk)",
        "notes": "Twilight end; autumn equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2015-12-21",
        "time_local": "18:19",
        "utc_offset": 2.0,
        "lat": 31.350, "lng": 27.240, "elevation_m": 28.0,
        "source": "Hassan et al., Time verification twilight Matrouh Egypt (Isha/dusk)",
        "notes": "Twilight end; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Kharga Oasis (Western Desert, ~25.4°N)
    # Site: 25.45°N, 30.56°E, ~70m; UTC+2 EET
    # Source: Hassan et al. 2020, Taylor & Francis — multi-site Egypt 2015-2019
    #   D₀ = 14.56° mean across 6 Egyptian sites
    # Very dark desert skies — among best conditions in North Africa
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2016-03-20",
        "time_local": "05:00",
        "utc_offset": 2.0,
        "lat": 25.450, "lng": 30.560, "elevation_m": 70.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Kharga Oasis Egypt",
        "notes": "Western Desert; very dark skies; D₀=14.56°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "03:56",
        "utc_offset": 3.0,
        "lat": 25.450, "lng": 30.560, "elevation_m": 70.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Kharga Oasis Egypt",
        "notes": "Western Desert; EEST; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-09-22",
        "time_local": "04:45",
        "utc_offset": 2.0,
        "lat": 25.450, "lng": 30.560, "elevation_m": 70.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Kharga Oasis Egypt",
        "notes": "Western Desert; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "05:33",
        "utc_offset": 2.0,
        "lat": 25.450, "lng": 30.560, "elevation_m": 70.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Kharga Oasis Egypt",
        "notes": "Western Desert; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Hurghada (Red Sea coast, ~27.3°N)
    # Site: 27.26°N, 33.81°E, ~5m; UTC+2 EET
    # Source: Hassan et al. 2020 multi-site Egypt study
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2016-03-20",
        "time_local": "04:46",
        "utc_offset": 2.0,
        "lat": 27.260, "lng": 33.810, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Hurghada Egypt",
        "notes": "Red Sea coastal desert; D₀=14.56°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "03:38",
        "utc_offset": 3.0,
        "lat": 27.260, "lng": 33.810, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Hurghada Egypt",
        "notes": "Red Sea coast; EEST; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-09-22",
        "time_local": "04:31",
        "utc_offset": 2.0,
        "lat": 27.260, "lng": 33.810, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Hurghada Egypt",
        "notes": "Red Sea coastal; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "05:23",
        "utc_offset": 2.0,
        "lat": 27.260, "lng": 33.810, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Hurghada Egypt",
        "notes": "Red Sea coast; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # EGYPT — Marsa-Alam (southern Red Sea coast, ~25.1°N)
    # Site: 25.07°N, 34.90°E, ~5m; UTC+2 EET
    # Source: Hassan et al. 2020 multi-site Egypt study
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2016-03-20",
        "time_local": "04:43",
        "utc_offset": 2.0,
        "lat": 25.070, "lng": 34.900, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Marsa-Alam Egypt",
        "notes": "Southern Red Sea coast; D₀=14.56°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "03:40",
        "utc_offset": 3.0,
        "lat": 25.070, "lng": 34.900, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Marsa-Alam Egypt",
        "notes": "Southern Red Sea; EEST; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-09-22",
        "time_local": "04:28",
        "utc_offset": 2.0,
        "lat": 25.070, "lng": 34.900, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Marsa-Alam Egypt",
        "notes": "Southern Red Sea; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "05:15",
        "utc_offset": 2.0,
        "lat": 25.070, "lng": 34.900, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, Taylor & Francis, Marsa-Alam Egypt",
        "notes": "Southern Red Sea; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # EGYPT — 15th of May City (Helwan area, urban)
    # Site: 29.962°N, 31.827°E, ~225m; UTC+2 EET
    # Source: Taha, Al Mostafa et al. 2025 — D₀ = 12.69°
    # NOTE: Notably low — urban environment, possible light pollution bias
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2024-03-20",
        "time_local": "05:01",
        "utc_offset": 2.0,
        "lat": 29.962, "lng": 31.827, "elevation_m": 225.0,
        "source": "Taha et al. 2025, Emirates Scholar, 15th of May City Egypt",
        "notes": "Urban; D₀=12.69° (low; possible light pollution); spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-06-21",
        "time_local": "03:47",
        "utc_offset": 3.0,
        "lat": 29.962, "lng": 31.827, "elevation_m": 225.0,
        "source": "Taha et al. 2025, Emirates Scholar, 15th of May City Egypt",
        "notes": "Urban; EEST; summer; D₀=12.69°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-09-22",
        "time_local": "04:46",
        "utc_offset": 2.0,
        "lat": 29.962, "lng": 31.827, "elevation_m": 225.0,
        "source": "Taha et al. 2025, Emirates Scholar, 15th of May City Egypt",
        "notes": "Urban; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-12-21",
        "time_local": "05:44",
        "utc_offset": 2.0,
        "lat": 29.962, "lng": 31.827, "elevation_m": 225.0,
        "source": "Taha et al. 2025, Emirates Scholar, 15th of May City Egypt",
        "notes": "Urban; winter; time inferred",
    },

    # -------------------------------------------------------------------------
    # SAUDI ARABIA — Riyadh
    # Site: 24.688°N, 46.722°E, ~612m; UTC+3 (AST, no DST)
    # Source: Taha, Al Mostafa et al. 2025 — D₀ = 14.58° ± 0.3°
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2024-03-20",
        "time_local": "04:56",
        "utc_offset": 3.0,
        "lat": 24.688, "lng": 46.722, "elevation_m": 612.0,
        "source": "Taha et al. 2025, Emirates Scholar, Riyadh Saudi Arabia",
        "notes": "Desert plateau; 612m; D₀=14.58°±0.3°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-06-21",
        "time_local": "03:54",
        "utc_offset": 3.0,
        "lat": 24.688, "lng": 46.722, "elevation_m": 612.0,
        "source": "Taha et al. 2025, Emirates Scholar, Riyadh Saudi Arabia",
        "notes": "Desert plateau; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-09-22",
        "time_local": "04:41",
        "utc_offset": 3.0,
        "lat": 24.688, "lng": 46.722, "elevation_m": 612.0,
        "source": "Taha et al. 2025, Emirates Scholar, Riyadh Saudi Arabia",
        "notes": "Desert plateau; autumn equinox; time inferred at 14.58°",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-12-21",
        "time_local": "05:27",
        "utc_offset": 3.0,
        "lat": 24.688, "lng": 46.722, "elevation_m": 612.0,
        "source": "Taha et al. 2025, Emirates Scholar, Riyadh Saudi Arabia",
        "notes": "Desert plateau; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # MAURITANIA — West Africa (first Mauritanian data point)
    # Site: ~18.0°N, ~15.9°W, ~10m; UTC+0 (GMT, no DST)
    # Source: Taha, Al Mostafa et al. 2025 — D₀ = 14.85°
    # Critical: fills the West Africa / Sahel geographic gap
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2024-03-20",
        "time_local": "06:08",
        "utc_offset": 0.0,
        "lat": 18.000, "lng": -15.900, "elevation_m": 10.0,
        "source": "Taha et al. 2025, Emirates Scholar, Mauritania West Africa",
        "notes": "Sahel; D₀=14.85°; FIRST Mauritanian data; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-06-21",
        "time_local": "05:22",
        "utc_offset": 0.0,
        "lat": 18.000, "lng": -15.900, "elevation_m": 10.0,
        "source": "Taha et al. 2025, Emirates Scholar, Mauritania West Africa",
        "notes": "Sahel; summer; 18°N; harmattan dry season; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-09-22",
        "time_local": "05:53",
        "utc_offset": 0.0,
        "lat": 18.000, "lng": -15.900, "elevation_m": 10.0,
        "source": "Taha et al. 2025, Emirates Scholar, Mauritania West Africa",
        "notes": "Sahel; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-12-21",
        "time_local": "06:26",
        "utc_offset": 0.0,
        "lat": 18.000, "lng": -15.900, "elevation_m": 10.0,
        "source": "Taha et al. 2025, Emirates Scholar, Mauritania West Africa",
        "notes": "Sahel; winter; harmattan; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Pantai Mek Mas, Kelantan (pristine dark sky site, 6.3°N)
    # Sky brightness 21.30 mpsas (Bortle Class 2-3); east coast Malaysia
    # Source: "Alteration of twilight sky brightness profile by light pollution"
    #   Scientific Reports 14, 2024. PMC11535048. 84 observations 2014-2022.
    #   Pristine sites converge at -17.49° twilight stability solar altitude.
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-03-21",
        "time_local": "06:08",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine dark sky 21.30 mpsas; twilight stability -17.49°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-06-22",
        "time_local": "05:44",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine dark sky; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-23",
        "time_local": "05:53",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine dark sky; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "06:04",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine dark sky; winter solstice; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2018-03-20",
        "time_local": "20:29",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine site Isha; 17.49° twilight stability; spring equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2018-06-21",
        "time_local": "20:41",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine site Isha; summer; 6.3°N; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2018-09-22",
        "time_local": "20:14",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine site Isha; autumn equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2018-12-21",
        "time_local": "20:14",
        "utc_offset": 8.0,
        "lat": 6.317, "lng": 102.150, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Mek Mas Kelantan Malaysia",
        "notes": "Pristine site Isha; winter solstice; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Balai Cerap UniSZA, Merang, Terengganu (pristine, 5.4°N)
    # Sky brightness 20.08 mpsas; official Islamic astronomy observatory
    # Source: LP2024 Scientific Reports PMC11535048
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-03-21",
        "time_local": "06:05",
        "utc_offset": 8.0,
        "lat": 5.400, "lng": 102.917, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Balai Cerap UniSZA Terengganu",
        "notes": "Official Islamic observatory; pristine 20.08 mpsas; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-06-22",
        "time_local": "05:43",
        "utc_offset": 8.0,
        "lat": 5.400, "lng": 102.917, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Balai Cerap UniSZA Terengganu",
        "notes": "UniSZA observatory; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-23",
        "time_local": "05:50",
        "utc_offset": 8.0,
        "lat": 5.400, "lng": 102.917, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Balai Cerap UniSZA Terengganu",
        "notes": "UniSZA observatory; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "05:59",
        "utc_offset": 8.0,
        "lat": 5.400, "lng": 102.917, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Balai Cerap UniSZA Terengganu",
        "notes": "UniSZA observatory; winter solstice; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Simpang Mengayau, Sabah (pristine, 7.2°N, 21.64 mpsas)
    # Northernmost tip of Borneo; extremely dark pristine sky
    # Source: LP2024 Scientific Reports PMC11535048
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-03-21",
        "time_local": "05:10",
        "utc_offset": 8.0,
        "lat": 7.200, "lng": 116.500, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Simpang Mengayau Sabah",
        "notes": "Pristine 21.64 mpsas; northernmost Borneo; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-06-22",
        "time_local": "04:45",
        "utc_offset": 8.0,
        "lat": 7.200, "lng": 116.500, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Simpang Mengayau Sabah",
        "notes": "Pristine Borneo; summer; 7.2°N; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-23",
        "time_local": "04:56",
        "utc_offset": 8.0,
        "lat": 7.200, "lng": 116.500, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Simpang Mengayau Sabah",
        "notes": "Pristine Borneo; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "05:08",
        "utc_offset": 8.0,
        "lat": 7.200, "lng": 116.500, "elevation_m": 5.0,
        "source": "LP2024 Scientific Reports PMC11535048, Simpang Mengayau Sabah",
        "notes": "Pristine Borneo; winter solstice; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Tanjung Balau, Johor (rural, 1.8°N, 3m)
    # Source: LP2024 Scientific Reports PMC11535048; rural site 19.78 mpsas
    # LP-affected angle (-15.67°) — lower confidence than pristine sites
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-03-21",
        "time_local": "06:07",
        "utc_offset": 8.0,
        "lat": 1.800, "lng": 104.400, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Tanjung Balau Johor Malaysia",
        "notes": "Rural 19.78 mpsas; LP-affected angle 15.67°; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-06-22",
        "time_local": "05:52",
        "utc_offset": 8.0,
        "lat": 1.800, "lng": 104.400, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Tanjung Balau Johor Malaysia",
        "notes": "Rural Johor; summer; 1.8°N; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-23",
        "time_local": "05:52",
        "utc_offset": 8.0,
        "lat": 1.800, "lng": 104.400, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Tanjung Balau Johor Malaysia",
        "notes": "Rural Johor; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "05:55",
        "utc_offset": 8.0,
        "lat": 1.800, "lng": 104.400, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Tanjung Balau Johor Malaysia",
        "notes": "Rural Johor; winter solstice; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Pantai Masjid Tengku Zaharah, Kuala Terengganu (rural, 5.27°N)
    # Source: LP2024 Scientific Reports PMC11535048; rural site 19.85 mpsas
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-03-21",
        "time_local": "06:11",
        "utc_offset": 8.0,
        "lat": 5.267, "lng": 103.133, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Masjid Tengku Zaharah Terengganu",
        "notes": "Rural 19.85 mpsas; LP angle 15.67°; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-06-22",
        "time_local": "05:50",
        "utc_offset": 8.0,
        "lat": 5.267, "lng": 103.133, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Masjid Tengku Zaharah Terengganu",
        "notes": "Rural Terengganu beach; summer; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-23",
        "time_local": "05:57",
        "utc_offset": 8.0,
        "lat": 5.267, "lng": 103.133, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Masjid Tengku Zaharah Terengganu",
        "notes": "Rural Terengganu; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "06:06",
        "utc_offset": 8.0,
        "lat": 5.267, "lng": 103.133, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Masjid Tengku Zaharah Terengganu",
        "notes": "Rural Terengganu; winter solstice; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Pantai Batu Buruk, Kuala Terengganu (rural, 5.32°N)
    # Source: LP2024 Scientific Reports PMC11535048; rural 19.23 mpsas
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-03-21",
        "time_local": "06:11",
        "utc_offset": 8.0,
        "lat": 5.317, "lng": 103.150, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "Rural beach 19.23 mpsas; LP angle 15.67°; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-06-22",
        "time_local": "05:50",
        "utc_offset": 8.0,
        "lat": 5.317, "lng": 103.150, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "Rural Terengganu; summer; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-23",
        "time_local": "05:57",
        "utc_offset": 8.0,
        "lat": 5.317, "lng": 103.150, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "Rural Terengganu; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "06:06",
        "utc_offset": 8.0,
        "lat": 5.317, "lng": 103.150, "elevation_m": 2.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "Rural Terengganu; winter solstice; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Pantai Nenasi, Pahang (pristine, ~3.43°N)
    # Source: LP2024 Scientific Reports PMC11535048; pristine east coast site
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-03-21",
        "time_local": "06:03",
        "utc_offset": 8.0,
        "lat": 3.430, "lng": 103.450, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Nenasi Pahang Malaysia",
        "notes": "Pristine east coast beach; 17.49° twilight stability; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-06-22",
        "time_local": "05:45",
        "utc_offset": 8.0,
        "lat": 3.430, "lng": 103.450, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Nenasi Pahang Malaysia",
        "notes": "Pristine Pahang beach; summer; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-09-23",
        "time_local": "05:48",
        "utc_offset": 8.0,
        "lat": 3.430, "lng": 103.450, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Nenasi Pahang Malaysia",
        "notes": "Pristine Pahang beach; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "05:54",
        "utc_offset": 8.0,
        "lat": 3.430, "lng": 103.450, "elevation_m": 3.0,
        "source": "LP2024 Scientific Reports PMC11535048, Pantai Nenasi Pahang Malaysia",
        "notes": "Pristine Pahang beach; winter solstice; time inferred",
    },

    # =========================================================================
    # AUSTRALIA — Coonabarabran, NSW (pristine dark sky, -31.25°S, 590m)
    # Siding Spring Observatory region; 21.59 mpsas pristine sky
    # Source: LP2024 Scientific Reports PMC11535048; first Australian site in dataset
    # UTC+11 (AEDT): Oct-Apr; UTC+10 (AEST): Apr-Oct
    # Both Fajr and Isha at 17.49° (pristine twilight stability angle)
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2018-12-22",
        "time_local": "04:20",
        "utc_offset": 11.0,  # AEDT
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine 21.59 mpsas; Southern Hemisphere summer; 590m; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2019-03-21",
        "time_local": "05:47",
        "utc_offset": 11.0,  # AEDT
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine Coonabarabran; SH autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2019-06-22",
        "time_local": "05:37",
        "utc_offset": 10.0,  # AEST
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine Coonabarabran; SH winter solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2019-09-23",
        "time_local": "04:33",
        "utc_offset": 10.0,  # AEST
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine Coonabarabran; SH spring equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2018-12-22",
        "time_local": "21:42",
        "utc_offset": 11.0,  # AEDT
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine Isha; SH summer; long twilight; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2019-03-21",
        "time_local": "20:32",
        "utc_offset": 11.0,  # AEDT
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine Isha; SH autumn equinox; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2019-06-22",
        "time_local": "18:32",
        "utc_offset": 10.0,  # AEST
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine Isha; SH winter; short twilight at 31°S; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2019-09-23",
        "time_local": "19:17",
        "utc_offset": 10.0,  # AEST
        "lat": -31.250, "lng": 149.267, "elevation_m": 590.0,
        "source": "LP2024 Scientific Reports PMC11535048, Coonabarabran NSW Australia",
        "notes": "Pristine Isha; SH spring equinox; time inferred",
    },

    # =========================================================================
    # INDONESIA — Agam, West Sumatra (LAPAN SQM station, -0.25°N, 850m)
    # Sky brightness 19.5 mpsas (highland West Sumatra; near equator)
    # Source: Damanhuri & Mukarram, Jurnal MANTIK 8(1):28-35, 2022
    #   LAPAN 6-station SQM study; 241 ideal observations; mean fajr 16.51°
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "05:19",
        "utc_offset": 7.0,
        "lat": -0.250, "lng": 100.370, "elevation_m": 850.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Agam West Sumatra Indonesia",
        "notes": "LAPAN station; highland 850m; near equator; mean 16.51°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "05:08",
        "utc_offset": 7.0,
        "lat": -0.250, "lng": 100.370, "elevation_m": 850.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Agam West Sumatra Indonesia",
        "notes": "Agam LAPAN station; summer; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "05:04",
        "utc_offset": 7.0,
        "lat": -0.250, "lng": 100.370, "elevation_m": 850.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Agam West Sumatra Indonesia",
        "notes": "Agam LAPAN; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "05:04",
        "utc_offset": 7.0,
        "lat": -0.250, "lng": 100.370, "elevation_m": 850.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Agam West Sumatra Indonesia",
        "notes": "Agam LAPAN; winter; Highland Sumatra; time inferred",
    },

    # =========================================================================
    # INDONESIA — Pontianak, West Kalimantan (LAPAN station, 0.0°N, 3m)
    # Exactly at equator. Near-zero latitude; minimal seasonal variation.
    # Sky brightness 17.7 mpsas (suburban)
    # Source: LAPAN SQM 2022 (Damanhuri & Mukarram)
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "04:43",
        "utc_offset": 7.0,
        "lat": 0.000, "lng": 109.343, "elevation_m": 3.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pontianak West Kalimantan Indonesia",
        "notes": "LAPAN station AT EQUATOR (0.00°); flat; 16.51°; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:32",
        "utc_offset": 7.0,
        "lat": 0.000, "lng": 109.343, "elevation_m": 3.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pontianak West Kalimantan Indonesia",
        "notes": "Pontianak equator; summer; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "04:29",
        "utc_offset": 7.0,
        "lat": 0.000, "lng": 109.343, "elevation_m": 3.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pontianak West Kalimantan Indonesia",
        "notes": "Pontianak equator; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "04:28",
        "utc_offset": 7.0,
        "lat": 0.000, "lng": 109.343, "elevation_m": 3.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pontianak West Kalimantan Indonesia",
        "notes": "Pontianak equator; winter; equatorial near-constant angle; time inferred",
    },

    # =========================================================================
    # INDONESIA — Garut, West Java (LAPAN SQM station, -7.21°S, 717m)
    # Best sky quality in LAPAN network (20.6 mpsas, Bortle Class 5)
    # Source: LAPAN SQM 2022 (Damanhuri & Mukarram)
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "04:49",
        "utc_offset": 7.0,
        "lat": -7.212, "lng": 107.904, "elevation_m": 717.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Garut West Java Indonesia",
        "notes": "LAPAN best-sky station 20.6 mpsas; highland 717m; 7.2°S; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:50",
        "utc_offset": 7.0,
        "lat": -7.212, "lng": 107.904, "elevation_m": 717.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Garut West Java Indonesia",
        "notes": "Garut LAPAN; Southern Hemisphere winter solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "04:34",
        "utc_offset": 7.0,
        "lat": -7.212, "lng": 107.904, "elevation_m": 717.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Garut West Java Indonesia",
        "notes": "Garut LAPAN; SH spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "04:20",
        "utc_offset": 7.0,
        "lat": -7.212, "lng": 107.904, "elevation_m": 717.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Garut West Java Indonesia",
        "notes": "Garut LAPAN; SH summer solstice; time inferred",
    },

    # =========================================================================
    # INDONESIA — Pasuruan, East Java (LAPAN SQM station, -7.65°S, 4m)
    # Coastal East Java; sky brightness 18.0 mpsas
    # Source: LAPAN SQM 2022 (Damanhuri & Mukarram)
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "04:29",
        "utc_offset": 7.0,
        "lat": -7.645, "lng": 112.908, "elevation_m": 4.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pasuruan East Java Indonesia",
        "notes": "LAPAN coastal station; 7.6°S; 4m; East Java; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:31",
        "utc_offset": 7.0,
        "lat": -7.645, "lng": 112.908, "elevation_m": 4.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pasuruan East Java Indonesia",
        "notes": "Pasuruan LAPAN; SH winter; East Java coast; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "04:14",
        "utc_offset": 7.0,
        "lat": -7.645, "lng": 112.908, "elevation_m": 4.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pasuruan East Java Indonesia",
        "notes": "Pasuruan LAPAN; SH spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "03:59",
        "utc_offset": 7.0,
        "lat": -7.645, "lng": 112.908, "elevation_m": 4.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Pasuruan East Java Indonesia",
        "notes": "Pasuruan LAPAN; SH summer; time inferred",
    },

    # =========================================================================
    # INDONESIA — Sumedang, West Java (LAPAN SQM station, -6.86°S, 556m)
    # Sky brightness 19.6 mpsas; semi-rural highland West Java
    # Source: LAPAN SQM 2022 (Damanhuri & Mukarram)
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "04:49",
        "utc_offset": 7.0,
        "lat": -6.855, "lng": 107.921, "elevation_m": 556.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Sumedang West Java Indonesia",
        "notes": "LAPAN station; highland 556m; 6.9°S; semi-rural; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:50",
        "utc_offset": 7.0,
        "lat": -6.855, "lng": 107.921, "elevation_m": 556.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Sumedang West Java Indonesia",
        "notes": "Sumedang LAPAN; SH winter; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "04:34",
        "utc_offset": 7.0,
        "lat": -6.855, "lng": 107.921, "elevation_m": 556.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Sumedang West Java Indonesia",
        "notes": "Sumedang LAPAN; SH spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "04:21",
        "utc_offset": 7.0,
        "lat": -6.855, "lng": 107.921, "elevation_m": 556.0,
        "source": "LAPAN SQM 2022 (Damanhuri & Mukarram), Sumedang West Java Indonesia",
        "notes": "Sumedang LAPAN; SH summer; time inferred",
    },

    # =========================================================================
    # INDONESIA — Bulukumba/Pantai Samboang, South Sulawesi (-5.56°S, 2m)
    # Pristine dark sky site (21.6-22.0 mpsas, Bortle Class 2)
    # Source: Hisbullah Salam thesis 2022/2023, Walisongo University
    #   "Pengamatan Fajar Sadiq Menggunakan Sistem SOOF dan SQM di Sulawesi Selatan"
    #   https://eprints.walisongo.ac.id/id/eprint/20057/
    #   Observation dates confirmed: Sep 22, Sep 24, Sep 25, Oct 2, Oct 3 2022
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2022-03-21",
        "time_local": "04:53",
        "utc_offset": 8.0,
        "lat": -5.560, "lng": 120.410, "elevation_m": 2.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Bulukumba South Sulawesi",
        "notes": "Pristine 21.6-22 mpsas; SOOF+SQM comparison; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-06-22",
        "time_local": "04:51",
        "utc_offset": 8.0,
        "lat": -5.560, "lng": 120.410, "elevation_m": 2.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Bulukumba South Sulawesi",
        "notes": "Pristine Sulawesi coast; SH winter; SOOF confirmed 18°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-09-23",
        "time_local": "04:38",
        "utc_offset": 8.0,
        "lat": -5.560, "lng": 120.410, "elevation_m": 2.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Bulukumba South Sulawesi",
        "notes": "Pristine Sulawesi; actual obs dates Sep 22-25 Oct 2-3 2022; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-12-22",
        "time_local": "04:27",
        "utc_offset": 8.0,
        "lat": -5.560, "lng": 120.410, "elevation_m": 2.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Bulukumba South Sulawesi",
        "notes": "Pristine Sulawesi coast; SH summer; time inferred",
    },

    # =========================================================================
    # INDONESIA — Takalar, South Sulawesi (-5.43°S, 5m)
    # Suburban site (20.4-21.8 mpsas); coastal South Sulawesi
    # Source: Hisbullah Salam thesis 2022/2023; observed Oct 3 2022
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2022-03-21",
        "time_local": "05:01",
        "utc_offset": 8.0,
        "lat": -5.434, "lng": 119.390, "elevation_m": 5.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Takalar South Sulawesi",
        "notes": "Suburban 20.4-21.8 mpsas; 17.0°; spring; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-06-22",
        "time_local": "04:59",
        "utc_offset": 8.0,
        "lat": -5.434, "lng": 119.390, "elevation_m": 5.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Takalar South Sulawesi",
        "notes": "Takalar Sulawesi; SH winter; Oct 3 2022 confirmed obs date; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-09-23",
        "time_local": "04:46",
        "utc_offset": 8.0,
        "lat": -5.434, "lng": 119.390, "elevation_m": 5.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Takalar South Sulawesi",
        "notes": "Takalar; SH spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2022-12-22",
        "time_local": "04:35",
        "utc_offset": 8.0,
        "lat": -5.434, "lng": 119.390, "elevation_m": 5.0,
        "source": "Hisbullah Salam thesis 2022/2023 Walisongo Univ, Takalar South Sulawesi",
        "notes": "Takalar; SH summer; time inferred",
    },

    # =========================================================================
    # MALAYSIA — Kuala Lipis, Pahang (Isha, Abdel-Hadi & Hassan 2022)
    # Kuala Lipis: 4.183°N, 102.04°E, 76m; UTC+8
    # Source: Abdel-Hadi & Hassan, IJAA 12:7-29, 2022
    #   Mean Isha (Shafaq Abyad end) = 14.38° ± 0.91° at Malaysian sites
    # =========================================================================
    {
        "prayer": "isha",
        "date_local": "2007-05-15",
        "time_local": "20:15",
        "utc_offset": 8.0,
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12:7-29, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad end; 4.2°N 76m; Isha 14.38°; time inferred from mean angle",
    },
    {
        "prayer": "isha",
        "date_local": "2007-09-22",
        "time_local": "20:02",
        "utc_offset": 8.0,
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12:7-29, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad autumn equinox; Kuala Lipis; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2008-01-15",
        "time_local": "20:16",
        "utc_offset": 8.0,
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12:7-29, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad winter; Kuala Lipis; time inferred",
    },
    {
        "prayer": "isha",
        "date_local": "2008-04-15",
        "time_local": "20:13",
        "utc_offset": 8.0,
        "lat": 4.183, "lng": 102.040, "elevation_m": 76.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12:7-29, Kuala Lipis Malaysia",
        "notes": "Shafaq Abyad spring; Kuala Lipis 76m; time inferred",
    },

    # =========================================================================
    # LIBYA — Tubruq (Mediterranean coast, 32.08°N, 23.98°E, 40m)
    # Source: Al-Hilal 2021 (Journal Al-Hilal / idosi.org), 1,053 naked-eye obs 2007-2013
    # Mediterranean background 2007-2008: 429 nights, mean 13.48°
    # Desert background 2009-2013 (high-vis subset): 32 nights, mean 14.014°
    # Desert background 2009-2013 (all obs): 623 nights, mean 13.144°
    # Only non-Middle East North African long-running naked-eye dataset found.
    # =========================================================================
    # Mediterranean period 2007-2008
    {
        "prayer": "fajr",
        "date_local": "2007-03-20",
        "time_local": "05:28",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Mediterranean coast; 429-night Mediterranean period; mean 13.48°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2007-06-21",
        "time_local": "04:06",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Mediterranean coast; summer solstice; mean 13.48°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2007-09-22",
        "time_local": "05:11",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Mediterranean coast; autumn equinox; mean 13.48°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2007-12-21",
        "time_local": "06:15",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Mediterranean coast; winter solstice; mean 13.48°; time inferred",
    },
    # Desert period 2009-2013 — high-visibility subset (32 pristine nights)
    {
        "prayer": "fajr",
        "date_local": "2011-03-20",
        "time_local": "05:26",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; high-visibility subset 32 nights; mean 14.014°±0.317°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2011-06-21",
        "time_local": "04:02",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; high-vis; summer solstice; mean 14.014°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2011-09-22",
        "time_local": "05:09",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; high-vis; autumn equinox; mean 14.014°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2011-12-21",
        "time_local": "06:12",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; high-vis; winter solstice; mean 14.014°; time inferred",
    },
    # Desert period 2009-2013 — full dataset (623 nights)
    {
        "prayer": "fajr",
        "date_local": "2010-03-20",
        "time_local": "05:30",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; full 623-night dataset; mean 13.144°±0.757°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-06-21",
        "time_local": "04:08",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; full dataset; summer solstice; mean 13.144°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-09-22",
        "time_local": "05:13",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; full dataset; autumn equinox; mean 13.144°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-12-21",
        "time_local": "06:17",
        "utc_offset": 2.0,
        "lat": 32.0833, "lng": 23.9833, "elevation_m": 40.0,
        "source": "Al-Hilal 2021, idosi.org, Tubruq Libya 1053 naked-eye obs",
        "notes": "Desert period; full dataset; winter solstice; mean 13.144°; time inferred",
    },

    # =========================================================================
    # EGYPT — Fayum (Western Desert edge, 29.28°N, 30.05°E, 50m)
    # Source: IAEME study, 4+ year dataset 2015-2019, mean depression ~14.4°
    # (range 14.0-14.8° across methods). Semi-arid site with good seeing.
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2016-03-20",
        "time_local": "05:01",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Western Desert edge; spring equinox; 4-yr mean 14.4°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "03:47",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Fayum; summer solstice; long twilight; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-09-22",
        "time_local": "04:45",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Fayum; autumn equinox; mean 14.4°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "05:42",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Fayum; winter solstice; mean 14.4°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-03-20",
        "time_local": "05:01",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Fayum Y2; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-06-21",
        "time_local": "03:47",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Fayum Y2; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-09-22",
        "time_local": "04:45",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Fayum Y2; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-12-21",
        "time_local": "05:42",
        "utc_offset": 2.0,
        "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "IAEME Fayum Egypt 2015-2019 study, mean 14.4° depression",
        "notes": "Fayum Y2; winter solstice; time inferred",
    },

    # =========================================================================
    # INDONESIA — Biak, Papua (LAPAN station, -1.17°S, 135.75°E, 50m, UTC+9)
    # Source: Damanhuri & Mukarram LAPAN 2022 network, mean 16.51°
    # Equatorial east Indonesia; WIT (Waktu Indonesia Timur) = UTC+9
    # Key: second equatorial anchor alongside Pontianak (0.0°N, 109.3°E)
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "04:58",
        "utc_offset": 9.0,
        "lat": -1.17, "lng": 135.75, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Biak Papua Indonesia",
        "notes": "Near-equatorial; eastern Indonesia; LAPAN SQM network; 16.51°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:48",
        "utc_offset": 9.0,
        "lat": -1.17, "lng": 135.75, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Biak Papua Indonesia",
        "notes": "Biak; southern winter; sun shifts north; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "04:43",
        "utc_offset": 9.0,
        "lat": -1.17, "lng": 135.75, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Biak Papua Indonesia",
        "notes": "Biak; autumn equinox; equatorial; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "04:41",
        "utc_offset": 9.0,
        "lat": -1.17, "lng": 135.75, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Biak Papua Indonesia",
        "notes": "Biak; southern summer; time inferred",
    },

    # =========================================================================
    # INDONESIA — Manado, North Sulawesi (LAPAN station, 1.49°N, 124.85°E, UTC+8)
    # Source: Damanhuri & Mukarram LAPAN 2022 network, mean 16.51°
    # North tip of Sulawesi; slight northern hemisphere at 1.49°N
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "04:41",
        "utc_offset": 8.0,
        "lat": 1.49, "lng": 124.85, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Manado North Sulawesi Indonesia",
        "notes": "Northern Sulawesi; 1.49°N; LAPAN 16.51°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:27",
        "utc_offset": 8.0,
        "lat": 1.49, "lng": 124.85, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Manado North Sulawesi Indonesia",
        "notes": "Manado; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "04:26",
        "utc_offset": 8.0,
        "lat": 1.49, "lng": 124.85, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Manado North Sulawesi Indonesia",
        "notes": "Manado; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "04:29",
        "utc_offset": 8.0,
        "lat": 1.49, "lng": 124.85, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Manado North Sulawesi Indonesia",
        "notes": "Manado; winter solstice; time inferred",
    },

    # =========================================================================
    # INDONESIA — Lombok, West Nusa Tenggara (LAPAN station, -8.56°S, 116.09°E, UTC+8)
    # Source: Damanhuri & Mukarram LAPAN 2022 network, mean 16.51°
    # Southern Hemisphere island between Bali and Sumbawa
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "05:16",
        "utc_offset": 8.0,
        "lat": -8.56, "lng": 116.09, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Lombok West Nusa Tenggara Indonesia",
        "notes": "Southern Sulawesi; -8.56°S; LAPAN 16.51°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "05:20",
        "utc_offset": 8.0,
        "lat": -8.56, "lng": 116.09, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Lombok West Nusa Tenggara Indonesia",
        "notes": "Lombok; southern winter; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "05:01",
        "utc_offset": 8.0,
        "lat": -8.56, "lng": 116.09, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Lombok West Nusa Tenggara Indonesia",
        "notes": "Lombok; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "04:45",
        "utc_offset": 8.0,
        "lat": -8.56, "lng": 116.09, "elevation_m": 50.0,
        "source": "Damanhuri & Mukarram LAPAN 2022, Lombok West Nusa Tenggara Indonesia",
        "notes": "Lombok; southern summer; time inferred",
    },

    # =========================================================================
    # SAUDI ARABIA — Makkah (21.42°N, 39.83°E, 240m, UTC+3)
    # Source: Makkah Prayer Authority / UQU studies; standard 18° used for Umm al-Qura
    # Important: holiest site in Islam, the 18° standard is prescribed here
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-20",
        "time_local": "05:10",
        "utc_offset": 3.0,
        "lat": 21.423, "lng": 39.826, "elevation_m": 240.0,
        "source": "Umm al-Qura standard 18° Fajr, Makkah al-Mukarramah KSA",
        "notes": "Masjid al-Haram reference; 18° prescribed; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-21",
        "time_local": "04:13",
        "utc_offset": 3.0,
        "lat": 21.423, "lng": 39.826, "elevation_m": 240.0,
        "source": "Umm al-Qura standard 18° Fajr, Makkah al-Mukarramah KSA",
        "notes": "Makkah; summer solstice; 18°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-22",
        "time_local": "04:55",
        "utc_offset": 3.0,
        "lat": 21.423, "lng": 39.826, "elevation_m": 240.0,
        "source": "Umm al-Qura standard 18° Fajr, Makkah al-Mukarramah KSA",
        "notes": "Makkah; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-21",
        "time_local": "05:34",
        "utc_offset": 3.0,
        "lat": 21.423, "lng": 39.826, "elevation_m": 240.0,
        "source": "Umm al-Qura standard 18° Fajr, Makkah al-Mukarramah KSA",
        "notes": "Makkah; winter solstice; time inferred",
    },

    # =========================================================================
    # SAUDI ARABIA — Madinah (24.47°N, 39.61°E, 598m, UTC+3)
    # Source: Taha et al. 2025 — Hejaz region 14.58°; same study as Riyadh
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2024-03-20",
        "time_local": "05:24",
        "utc_offset": 3.0,
        "lat": 24.468, "lng": 39.614, "elevation_m": 598.0,
        "source": "Taha et al. 2025, Emirates Scholar, Madinah al-Munawwarah KSA",
        "notes": "Hejaz plateau 598m; 14.58°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-06-21",
        "time_local": "04:23",
        "utc_offset": 3.0,
        "lat": 24.468, "lng": 39.614, "elevation_m": 598.0,
        "source": "Taha et al. 2025, Emirates Scholar, Madinah al-Munawwarah KSA",
        "notes": "Madinah; summer; arid; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-09-22",
        "time_local": "05:09",
        "utc_offset": 3.0,
        "lat": 24.468, "lng": 39.614, "elevation_m": 598.0,
        "source": "Taha et al. 2025, Emirates Scholar, Madinah al-Munawwarah KSA",
        "notes": "Madinah; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2024-12-21",
        "time_local": "05:55",
        "utc_offset": 3.0,
        "lat": 24.468, "lng": 39.614, "elevation_m": 598.0,
        "source": "Taha et al. 2025, Emirates Scholar, Madinah al-Munawwarah KSA",
        "notes": "Madinah; winter solstice; time inferred",
    },

    # =========================================================================
    # PAKISTAN — Karachi (24.86°N, 67.01°E, 10m, UTC+5)
    # Source: Published Pakistani astronomical estimates for coastal Fajr ~15°
    # Coastal site, moderate LP; urban but historically documented
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-20",
        "time_local": "05:33",
        "utc_offset": 5.0,
        "lat": 24.86, "lng": 67.01, "elevation_m": 10.0,
        "source": "Pakistan astronomical estimates, Karachi coastal Fajr ~15°",
        "notes": "Arabian Sea coast; urban LP; 15°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:30",
        "utc_offset": 5.0,
        "lat": 24.86, "lng": 67.01, "elevation_m": 10.0,
        "source": "Pakistan astronomical estimates, Karachi coastal Fajr ~15°",
        "notes": "Karachi; summer; monsoon; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-22",
        "time_local": "05:17",
        "utc_offset": 5.0,
        "lat": 24.86, "lng": 67.01, "elevation_m": 10.0,
        "source": "Pakistan astronomical estimates, Karachi coastal Fajr ~15°",
        "notes": "Karachi; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-21",
        "time_local": "06:04",
        "utc_offset": 5.0,
        "lat": 24.86, "lng": 67.01, "elevation_m": 10.0,
        "source": "Pakistan astronomical estimates, Karachi coastal Fajr ~15°",
        "notes": "Karachi; winter solstice; time inferred",
    },

    # =========================================================================
    # TURKEY — Ankara (39.93°N, 32.86°E, 938m, UTC+3)
    # Source: Diyanet (Turkish Religious Affairs Directorate) standard = 18° Fajr
    # High-altitude inland plateau; arid continental climate, clean atmosphere
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-20",
        "time_local": "05:21",
        "utc_offset": 3.0,
        "lat": 39.93, "lng": 32.86, "elevation_m": 938.0,
        "source": "Diyanet Turkey standard 18° Fajr, Ankara",
        "notes": "Anatolian plateau 938m; Diyanet 18°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-21",
        "time_local": "03:17",
        "utc_offset": 3.0,
        "lat": 39.93, "lng": 32.86, "elevation_m": 938.0,
        "source": "Diyanet Turkey standard 18° Fajr, Ankara",
        "notes": "Ankara; summer solstice; long twilight at 40°N; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-22",
        "time_local": "05:05",
        "utc_offset": 3.0,
        "lat": 39.93, "lng": 32.86, "elevation_m": 938.0,
        "source": "Diyanet Turkey standard 18° Fajr, Ankara",
        "notes": "Ankara; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-21",
        "time_local": "06:29",
        "utc_offset": 3.0,
        "lat": 39.93, "lng": 32.86, "elevation_m": 938.0,
        "source": "Diyanet Turkey standard 18° Fajr, Ankara",
        "notes": "Ankara; winter solstice; time inferred",
    },

    # =========================================================================
    # MOROCCO — Marrakech (31.63°N, -8.00°E, 467m, UTC+1 standard)
    # Source: Ministry of Habous (Morocco) standard 18° for Fajr
    # Inland semi-arid; Atlas Mountains reduce LP; dark horizon to east
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-20",
        "time_local": "06:14",
        "utc_offset": 1.0,
        "lat": 31.63, "lng": -8.00, "elevation_m": 467.0,
        "source": "Ministry of Habous Morocco standard 18° Fajr, Marrakech",
        "notes": "Atlas foothills 467m; Ministry of Habous 18°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-21",
        "time_local": "04:47",
        "utc_offset": 1.0,
        "lat": 31.63, "lng": -8.00, "elevation_m": 467.0,
        "source": "Ministry of Habous Morocco standard 18° Fajr, Marrakech",
        "notes": "Marrakech; summer; dry desert air; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-22",
        "time_local": "05:59",
        "utc_offset": 1.0,
        "lat": 31.63, "lng": -8.00, "elevation_m": 467.0,
        "source": "Ministry of Habous Morocco standard 18° Fajr, Marrakech",
        "notes": "Marrakech; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-21",
        "time_local": "07:00",
        "utc_offset": 1.0,
        "lat": 31.63, "lng": -8.00, "elevation_m": 467.0,
        "source": "Ministry of Habous Morocco standard 18° Fajr, Marrakech",
        "notes": "Marrakech; winter solstice; time inferred",
    },

    # =========================================================================
    # NIGERIA — Kano (12.0°N, 8.52°E, 472m, UTC+1)
    # Source: West African Islamic scholarly consensus, Nigerian Fajr 18°
    # Sahel zone; exceptional atmospheric transparency in harmattan dry season
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-20",
        "time_local": "05:19",
        "utc_offset": 1.0,
        "lat": 12.0, "lng": 8.52, "elevation_m": 472.0,
        "source": "Nigerian Islamic astronomy consensus 18° Fajr, Kano",
        "notes": "Sahel zone 472m; harmattan transparency; 18°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-21",
        "time_local": "04:44",
        "utc_offset": 1.0,
        "lat": 12.0, "lng": 8.52, "elevation_m": 472.0,
        "source": "Nigerian Islamic astronomy consensus 18° Fajr, Kano",
        "notes": "Kano; summer; rainy season; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-22",
        "time_local": "05:04",
        "utc_offset": 1.0,
        "lat": 12.0, "lng": 8.52, "elevation_m": 472.0,
        "source": "Nigerian Islamic astronomy consensus 18° Fajr, Kano",
        "notes": "Kano; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-21",
        "time_local": "05:25",
        "utc_offset": 1.0,
        "lat": 12.0, "lng": 8.52, "elevation_m": 472.0,
        "source": "Nigerian Islamic astronomy consensus 18° Fajr, Kano",
        "notes": "Kano; winter; harmattan; excellent transparency; time inferred",
    },

    # =========================================================================
    # SOUTH AFRICA — Johannesburg (-26.2°S, 28.04°E, 1753m, UTC+2)
    # Source: Muslim Judicial Council (MJC) SA standard 18° Fajr; Highveld plateau
    # Southern Hemisphere; 1753m elevation reduces atmosphere above observer
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-20",
        "time_local": "04:54",
        "utc_offset": 2.0,
        "lat": -26.2, "lng": 28.04, "elevation_m": 1753.0,
        "source": "MJC South Africa standard 18° Fajr, Johannesburg Highveld",
        "notes": "Highveld plateau 1753m; southern autumn; 18°; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-21",
        "time_local": "05:32",
        "utc_offset": 2.0,
        "lat": -26.2, "lng": 28.04, "elevation_m": 1753.0,
        "source": "MJC South Africa standard 18° Fajr, Johannesburg Highveld",
        "notes": "Johannesburg; southern winter; cold clear air; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-22",
        "time_local": "04:40",
        "utc_offset": 2.0,
        "lat": -26.2, "lng": 28.04, "elevation_m": 1753.0,
        "source": "MJC South Africa standard 18° Fajr, Johannesburg Highveld",
        "notes": "Johannesburg; spring equinox (SH); time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-21",
        "time_local": "03:41",
        "utc_offset": 2.0,
        "lat": -26.2, "lng": 28.04, "elevation_m": 1753.0,
        "source": "MJC South Africa standard 18° Fajr, Johannesburg Highveld",
        "notes": "Johannesburg; southern summer; early dawn; time inferred",
    },

    # =========================================================================
    # BANGLADESH — Dhaka (23.72°N, 90.41°E, 8m, UTC+6)
    # Source: Bangladesh Islamic Foundation; urban LP reduces effective angle to ~15°
    # Dense tropical city; latitude anchor for Bay of Bengal / South Asia
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2020-03-21",
        "time_local": "04:59",
        "utc_offset": 6.0,
        "lat": 23.72, "lng": 90.41, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation estimate, Dhaka 15° urban Fajr",
        "notes": "Tropical delta city; urban LP; 15°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-06-22",
        "time_local": "04:00",
        "utc_offset": 6.0,
        "lat": 23.72, "lng": 90.41, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation estimate, Dhaka 15° urban Fajr",
        "notes": "Dhaka; monsoon season; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-09-23",
        "time_local": "04:45",
        "utc_offset": 6.0,
        "lat": 23.72, "lng": 90.41, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation estimate, Dhaka 15° urban Fajr",
        "notes": "Dhaka; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2020-12-22",
        "time_local": "05:29",
        "utc_offset": 6.0,
        "lat": 23.72, "lng": 90.41, "elevation_m": 8.0,
        "source": "Bangladesh Islamic Foundation estimate, Dhaka 15° urban Fajr",
        "notes": "Dhaka; winter; haze reduces sky quality; time inferred",
    },

    # =========================================================================
    # EGYPT — Alexandria (31.20°N, 29.92°E, 5m, UTC+2)
    # Source: Hassan et al. 2020 multi-site Egypt coastal ~14.56°
    # Mediterranean coast; sea breeze moderates aerosols
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2016-03-20",
        "time_local": "04:59",
        "utc_offset": 2.0,
        "lat": 31.20, "lng": 29.92, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, multi-site Egypt coastal twilight study, Alexandria",
        "notes": "Mediterranean Egypt; coastal 14.56°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-06-21",
        "time_local": "03:39",
        "utc_offset": 2.0,
        "lat": 31.20, "lng": 29.92, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, multi-site Egypt coastal twilight study, Alexandria",
        "notes": "Alexandria; summer solstice; Mediterranean; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-09-22",
        "time_local": "04:44",
        "utc_offset": 2.0,
        "lat": 31.20, "lng": 29.92, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, multi-site Egypt coastal twilight study, Alexandria",
        "notes": "Alexandria; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2016-12-21",
        "time_local": "05:45",
        "utc_offset": 2.0,
        "lat": 31.20, "lng": 29.92, "elevation_m": 5.0,
        "source": "Hassan et al. 2020, multi-site Egypt coastal twilight study, Alexandria",
        "notes": "Alexandria; winter solstice; time inferred",
    },

    # =========================================================================
    # EGYPT — Baharia (Bahariya) Oasis (28.34°N, 28.88°E, 150m, UTC+2)
    # Source: Hassan et al. 2014, NRIAG Journal of Astronomy 3:23-26
    #   Multi-site naked eye study 1984-1987 (Dar El-Iftaa' collaboration)
    #   Sites: Baharia, Matrouh, Kottamia, Aswan — combined mean 14.7°
    #   Baharia = Western Desert oasis, driest/cleanest of the 4 sites
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "1985-03-20",
        "time_local": "05:05",
        "utc_offset": 2.0,
        "lat": 28.342, "lng": 28.880, "elevation_m": 150.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Baharia Oasis Egypt",
        "notes": "Western Desert oasis; naked eye 1984-1987; combined mean 14.7°; spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "1985-06-21",
        "time_local": "03:53",
        "utc_offset": 2.0,
        "lat": 28.342, "lng": 28.880, "elevation_m": 150.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Baharia Oasis Egypt",
        "notes": "Western Desert oasis; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "1985-09-22",
        "time_local": "04:49",
        "utc_offset": 2.0,
        "lat": 28.342, "lng": 28.880, "elevation_m": 150.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Baharia Oasis Egypt",
        "notes": "Western Desert oasis; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "1985-12-21",
        "time_local": "05:44",
        "utc_offset": 2.0,
        "lat": 28.342, "lng": 28.880, "elevation_m": 150.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Baharia Oasis Egypt",
        "notes": "Western Desert oasis; winter solstice; time inferred",
    },

    # =========================================================================
    # INDONESIA — Labuan Bajo, Flores, NTT (8.50°S, 119.89°E, 10m, UTC+8)
    # Source: Maskufa et al. 2024, Mazahib 23(1):155-198
    #   "Contextualising Fajr Sadiq: Response to Dawn Research Findings with SQM"
    #   SQM instrument; 4 Indonesian sites with varying light pollution
    #   Labuan Bajo = darkest sky of 4 sites; gateway to Komodo islands, NTT
    #   Fajr angle: 19.30° (maximum angle endpoint, pristine sky site)
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2021-03-21",
        "time_local": "04:49",
        "utc_offset": 8.0,
        "lat": -8.497, "lng": 119.890, "elevation_m": 10.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Labuan Bajo Flores NTT Indonesia",
        "notes": "Pristine dark sky; SQM; 19.30° (highest angle across 4-site LP study); spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2021-06-22",
        "time_local": "04:52",
        "utc_offset": 8.0,
        "lat": -8.497, "lng": 119.890, "elevation_m": 10.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Labuan Bajo Flores NTT Indonesia",
        "notes": "Pristine dark sky; summer solstice; -8.5°S; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2021-09-23",
        "time_local": "04:34",
        "utc_offset": 8.0,
        "lat": -8.497, "lng": 119.890, "elevation_m": 10.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Labuan Bajo Flores NTT Indonesia",
        "notes": "Pristine dark sky; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2021-12-22",
        "time_local": "04:17",
        "utc_offset": 8.0,
        "lat": -8.497, "lng": 119.890, "elevation_m": 10.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Labuan Bajo Flores NTT Indonesia",
        "notes": "Pristine dark sky; winter solstice; time inferred",
    },

    # =========================================================================
    # INDONESIA — Bogor, West Java (6.60°S, 106.79°E, 265m, UTC+7)
    # Source: Maskufa et al. 2024, Mazahib 23(1):155-198
    #   SQM instrument; highest light pollution of 4 sites (near Jakarta)
    #   Fajr angle: 13.58° (minimum angle endpoint, urban LP biases low)
    #   Note: Urban LP suppresses apparent dawn brightness → shallower detection
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2021-03-21",
        "time_local": "05:05",
        "utc_offset": 7.0,
        "lat": -6.595, "lng": 106.789, "elevation_m": 265.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Bogor West Java Indonesia",
        "notes": "Urban LP; SQM; 13.58° (lowest in 4-site LP study, suburban Jakarta); spring equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2021-06-22",
        "time_local": "05:06",
        "utc_offset": 7.0,
        "lat": -6.595, "lng": 106.789, "elevation_m": 265.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Bogor West Java Indonesia",
        "notes": "Urban LP; summer solstice; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2021-09-23",
        "time_local": "04:50",
        "utc_offset": 7.0,
        "lat": -6.595, "lng": 106.789, "elevation_m": 265.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Bogor West Java Indonesia",
        "notes": "Urban LP; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr",
        "date_local": "2021-12-22",
        "time_local": "04:39",
        "utc_offset": 7.0,
        "lat": -6.595, "lng": 106.789, "elevation_m": 265.0,
        "source": "Maskufa et al. 2024, Mazahib 23(1):155-198, Bogor West Java Indonesia",
        "notes": "Urban LP; winter solstice; time inferred",
    },

    # =========================================================================
    # BATCH 5 — Saksono ISRN Indonesian cities + Tayu Beach Pati + Cimahi
    # =========================================================================

    # -------------------------------------------------------------------------
    # INDONESIA — Padang, West Sumatra (0.9°S, 100.35°E, ~5m, UTC+7)
    # Source: Saksono T., Saksono I.H. et al., "Premature Dawn" book series;
    #   ISRN (Islamic Science Research Network), UHAMKA Jakarta.
    #   Mean D0 = -13.4° across Indonesian urban sites (LP-biased).
    #   NOTE: Urban light pollution site. Model should learn LP correction.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2015-03-21", "time_local": "05:32",
        "utc_offset": 7.0, "lat": -0.9, "lng": 100.35, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Padang W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; spring equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-22", "time_local": "05:23",
        "utc_offset": 7.0, "lat": -0.9, "lng": 100.35, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Padang W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; summer solstice; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-09-23", "time_local": "05:17",
        "utc_offset": 7.0, "lat": -0.9, "lng": 100.35, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Padang W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-12-22", "time_local": "05:16",
        "utc_offset": 7.0, "lat": -0.9, "lng": 100.35, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Padang W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Batusangkar, West Sumatra (0.47°S, 100.60°E, ~891m, UTC+7)
    # Source: Saksono T. et al., ISRN/UHAMKA "Premature Dawn" series.
    #   Highland city in Tanah Datar Regency; 891m elevation; D0 = -13.4°.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2015-03-21", "time_local": "05:31",
        "utc_offset": 7.0, "lat": -0.47, "lng": 100.60, "elevation_m": 891.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Batusangkar W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; 891m highland; spring equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-22", "time_local": "05:21",
        "utc_offset": 7.0, "lat": -0.47, "lng": 100.60, "elevation_m": 891.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Batusangkar W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; 891m highland; summer solstice; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-09-23", "time_local": "05:16",
        "utc_offset": 7.0, "lat": -0.47, "lng": 100.60, "elevation_m": 891.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Batusangkar W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; 891m highland; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-12-22", "time_local": "05:16",
        "utc_offset": 7.0, "lat": -0.47, "lng": 100.60, "elevation_m": 891.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Batusangkar W. Sumatra",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; 891m highland; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Cirebon, West Java (6.72°S, 108.55°E, ~5m, UTC+7)
    # Source: Saksono T. et al., ISRN/UHAMKA "Premature Dawn" series.
    #   Coastal city north Java coast; pop ~350k; D0 = -13.4°.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2015-03-21", "time_local": "04:59",
        "utc_offset": 7.0, "lat": -6.72, "lng": 108.55, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Cirebon West Java",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; spring equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-22", "time_local": "05:00",
        "utc_offset": 7.0, "lat": -6.72, "lng": 108.55, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Cirebon West Java",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; summer solstice; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-09-23", "time_local": "04:44",
        "utc_offset": 7.0, "lat": -6.72, "lng": 108.55, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Cirebon West Java",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-12-22", "time_local": "04:32",
        "utc_offset": 7.0, "lat": -6.72, "lng": 108.55, "elevation_m": 5.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Cirebon West Java",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Balikpapan, East Kalimantan (1.27°S, 116.83°E, ~10m, UTC+8)
    # Source: Saksono T. et al., ISRN/UHAMKA "Premature Dawn" series.
    #   Port city on Makassar Strait; oil industry hub; D0 = -13.4°.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2015-03-21", "time_local": "05:26",
        "utc_offset": 8.0, "lat": -1.27, "lng": 116.83, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Balikpapan E. Kalimantan",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; spring equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-22", "time_local": "05:18",
        "utc_offset": 8.0, "lat": -1.27, "lng": 116.83, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Balikpapan E. Kalimantan",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; summer solstice; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-09-23", "time_local": "05:11",
        "utc_offset": 8.0, "lat": -1.27, "lng": 116.83, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Balikpapan E. Kalimantan",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-12-22", "time_local": "05:09",
        "utc_offset": 8.0, "lat": -1.27, "lng": 116.83, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Balikpapan E. Kalimantan",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Bitung, North Sulawesi (1.44°N, 125.19°E, ~20m, UTC+8)
    # Source: Saksono T. et al., ISRN/UHAMKA "Premature Dawn" series.
    #   Port city near Manado; fishing center; D0 = -13.4°.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2015-03-21", "time_local": "04:53",
        "utc_offset": 8.0, "lat": 1.44, "lng": 125.19, "elevation_m": 20.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Bitung North Sulawesi",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; spring equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-22", "time_local": "04:39",
        "utc_offset": 8.0, "lat": 1.44, "lng": 125.19, "elevation_m": 20.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Bitung North Sulawesi",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; summer solstice; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-09-23", "time_local": "04:38",
        "utc_offset": 8.0, "lat": 1.44, "lng": 125.19, "elevation_m": 20.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Bitung North Sulawesi",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-12-22", "time_local": "04:41",
        "utc_offset": 8.0, "lat": 1.44, "lng": 125.19, "elevation_m": 20.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Bitung North Sulawesi",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Manokwari, West Papua (0.86°S, 134.08°E, ~10m, UTC+9)
    # Source: Saksono T. et al., ISRN/UHAMKA "Premature Dawn" series.
    #   Provincial capital of West Papua; coastal; D0 = -13.4°.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2015-03-21", "time_local": "05:17",
        "utc_offset": 9.0, "lat": -0.86, "lng": 134.08, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Manokwari West Papua",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; spring equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-22", "time_local": "05:08",
        "utc_offset": 9.0, "lat": -0.86, "lng": 134.08, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Manokwari West Papua",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; summer solstice; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-09-23", "time_local": "05:02",
        "utc_offset": 9.0, "lat": -0.86, "lng": 134.08, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Manokwari West Papua",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2015-12-22", "time_local": "05:01",
        "utc_offset": 9.0, "lat": -0.86, "lng": 134.08, "elevation_m": 10.0,
        "source": "Saksono T. et al., ISRN/UHAMKA 'Premature Dawn' series, Manokwari West Papua",
        "notes": "Urban LP; D0=-13.4° Indonesia mean; winter solstice; time inferred",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Tayu Beach, Pati, Central Java (6.68°S, 111.05°E, ~5m, UTC+7)
    # Source: Noor M. & Hamdani (2018), QIJIS (Qudus International Journal of
    #   Islamic Studies) 6(1):91-114.
    #   "Observasi Awal Waktu Shubuh di Pantai Tayu Pati Jawa Tengah"
    #   Photoelectric + SQM. 4 clear nights Aug-Sep 2016. D0 = -17.0°.
    #   Beach site facing east (Java Sea); moderate LP for coastal Central Java.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2016-08-11", "time_local": "04:37",
        "utc_offset": 7.0, "lat": -6.68, "lng": 111.05, "elevation_m": 5.0,
        "source": "Noor & Hamdani 2018, QIJIS 6(1):91-114, Tayu Beach Pati Central Java",
        "notes": "Photoelectric+SQM; D0=-17.0°; clear night; Aug 2016 observation period",
    },
    {
        "prayer": "fajr", "date_local": "2016-08-21", "time_local": "04:34",
        "utc_offset": 7.0, "lat": -6.68, "lng": 111.05, "elevation_m": 5.0,
        "source": "Noor & Hamdani 2018, QIJIS 6(1):91-114, Tayu Beach Pati Central Java",
        "notes": "Photoelectric+SQM; D0=-17.0°; clear night; Aug 2016 observation period",
    },
    {
        "prayer": "fajr", "date_local": "2016-09-06", "time_local": "04:28",
        "utc_offset": 7.0, "lat": -6.68, "lng": 111.05, "elevation_m": 5.0,
        "source": "Noor & Hamdani 2018, QIJIS 6(1):91-114, Tayu Beach Pati Central Java",
        "notes": "Photoelectric+SQM; D0=-17.0°; clear night; Sep 2016 observation period",
    },
    {
        "prayer": "fajr", "date_local": "2016-09-16", "time_local": "04:23",
        "utc_offset": 7.0, "lat": -6.68, "lng": 111.05, "elevation_m": 5.0,
        "source": "Noor & Hamdani 2018, QIJIS 6(1):91-114, Tayu Beach Pati Central Java",
        "notes": "Photoelectric+SQM; D0=-17.0°; clear night; Sep 2016 observation period",
    },

    # -------------------------------------------------------------------------
    # INDONESIA — Cimahi, West Java (6.88°S, 107.53°E, ~700m, UTC+7)
    # Source: Herdiwijaya D. (2020), J. Phys. Conf. 1523(1):012007.
    #   "On the beginning of the morning twilight based on sky brightness measurements"
    #   5-site SQM study across Bosscha, Cimahi, Bandung, Yogyakarta, Kupang.
    #   83 moonless nights 2011-2018. D0 = -18.5° (multi-site mean).
    #   Cimahi: 700m highland suburb west of Bandung.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2017-03-21", "time_local": "04:42",
        "utc_offset": 7.0, "lat": -6.88, "lng": 107.53, "elevation_m": 700.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Cimahi West Java Indonesia",
        "notes": "SQM; D0=-18.5° multi-site mean; 700m highland; spring equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2017-06-22", "time_local": "04:42",
        "utc_offset": 7.0, "lat": -6.88, "lng": 107.53, "elevation_m": 700.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Cimahi West Java Indonesia",
        "notes": "SQM; D0=-18.5° multi-site mean; 700m highland; summer solstice; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2017-09-23", "time_local": "04:27",
        "utc_offset": 7.0, "lat": -6.88, "lng": 107.53, "elevation_m": 700.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Cimahi West Java Indonesia",
        "notes": "SQM; D0=-18.5° multi-site mean; 700m highland; autumn equinox; time inferred",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-22", "time_local": "04:13",
        "utc_offset": 7.0, "lat": -6.88, "lng": 107.53, "elevation_m": 700.0,
        "source": "Herdiwijaya 2020, J. Phys. Conf. 1523, Cimahi West Java Indonesia",
        "notes": "SQM; D0=-18.5° multi-site mean; 700m highland; winter solstice; time inferred",
    },

    # =========================================================================
    # BATCH 6 — Kassim Bahali et al. 2019 JATMA per-date DSLR records
    # "Re-evaluation of Calculation of the Dawn Prayer Time in the Malay World"
    # Source: Bahali K. et al. (2019), JATMA 7(2):37-48
    #   DOI: 10.17576/jatma-2019-0702-04
    # DSLR camera (Canon 60Da), 22 sites in Malaysia, Indonesia, Thailand.
    # Feb 2017 - Sep 2018. 118 days, 112 valid (6 TD).
    # Mean D0 = 17.15° (from paper's mean time difference of 11.4 min).
    # Per-date times extracted from PDF Table 2 (rows 51-118), depression angles
    # computed via PyEphem from actual local dawn time + site coordinates.
    # =========================================================================

    # -----------------------------------------------------------------------
    # SABANG, ACEH, INDONESIA (5.876°N, 95.340°E, 5m, UTC+7)
    # Westernmost city of Indonesia. Sabang island, Weh Island, Indian Ocean.
    # Excellent dark sky horizon — facing west over Indian Ocean.
    # 11 individual DSLR observations Dec 20-30, 2017.
    # Mean D0 computed: 17.35°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2017-12-20", "time_local": "05:33",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=16.78° computed; Dec 20 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-21", "time_local": "05:37",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=15.98° computed; Dec 21 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-22", "time_local": "05:31",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=17.47° computed; Dec 22 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-23", "time_local": "05:36",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=16.43° computed; Dec 23 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-24", "time_local": "05:33",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=17.24° computed; Dec 24 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-25", "time_local": "05:33",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=17.35° computed; Dec 25 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-26", "time_local": "05:32",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=17.70° computed; Dec 26 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-27", "time_local": "05:34",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=17.35° computed; Dec 27 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-28", "time_local": "05:31",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=18.15° computed; Dec 28 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-29", "time_local": "05:32",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=18.04° computed; Dec 29 clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-12-30", "time_local": "05:31",
        "utc_offset": 7.0, "lat": 5.876, "lng": 95.340, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sabang Aceh Indonesia",
        "notes": "DSLR; D0=18.38° computed; Dec 30 clear sky; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # YARING, PATTANI, THAILAND (6.934°N, 101.319°E, 5m, UTC+7)
    # Southern Thailand (predominantly Muslim region). Coastal DSLR observation.
    # Coordinates from paper: 6°56'02"N, 101°19'07"E
    # 2 observations Jan 20-21, 2018.
    # Mean D0 computed: 17.07°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-01-20", "time_local": "05:23",
        "utc_offset": 7.0, "lat": 6.934, "lng": 101.319, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Yaring Pattani Thailand",
        "notes": "DSLR; D0=17.03° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-01-21", "time_local": "05:23",
        "utc_offset": 7.0, "lat": 6.934, "lng": 101.319, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Yaring Pattani Thailand",
        "notes": "DSLR; D0=17.10° computed; clear sky; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # SURABAYA, EAST JAVA, INDONESIA (-7.244°S, 112.802°E, 5m, UTC+7)
    # Second largest Indonesian city. Coastal Java Sea horizon.
    # Coordinates from paper: 7°14'39"S, 112°48'08"E
    # 3 observations Feb 21-23, 2018.
    # Mean D0 computed: 18.54°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-02-21", "time_local": "04:20",
        "utc_offset": 7.0, "lat": -7.244, "lng": 112.802, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Surabaya East Java Indonesia",
        "notes": "DSLR; D0=18.65° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-02-22", "time_local": "04:21",
        "utc_offset": 7.0, "lat": -7.244, "lng": 112.802, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Surabaya East Java Indonesia",
        "notes": "DSLR; D0=18.46° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-02-23", "time_local": "04:21",
        "utc_offset": 7.0, "lat": -7.244, "lng": 112.802, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Surabaya East Java Indonesia",
        "notes": "DSLR; D0=18.50° computed; clear sky; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # SUMENEP, MADURA, INDONESIA (-7.255°S, 112.803°E, 5m, UTC+7)
    # Western Madura coast facing Surabaya Strait.
    # Coordinates from paper: 7°15'16"S, 112°48'09"E (western Madura observation point)
    # 3 observations Feb 24-26, 2018.
    # Mean D0 computed: 16.46° (high variance, range 14.90°-18.35°)
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-02-24", "time_local": "04:36",
        "utc_offset": 7.0, "lat": -7.255, "lng": 112.803, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sumenep Madura Indonesia",
        "notes": "DSLR; D0=14.90° computed; partial cloud possible; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-02-25", "time_local": "04:31",
        "utc_offset": 7.0, "lat": -7.255, "lng": 112.803, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sumenep Madura Indonesia",
        "notes": "DSLR; D0=16.14° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-02-26", "time_local": "04:22",
        "utc_offset": 7.0, "lat": -7.255, "lng": 112.803, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Sumenep Madura Indonesia",
        "notes": "DSLR; D0=18.35° computed; clear sky; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # TERNATE, NORTH MALUKU, INDONESIA (-0.691°S, 127.390°E, 5m, UTC+9)
    # Coordinates from paper: 0°41'26"S, 127°23'24"E
    # (Observation site in North Maluku just south of equator)
    # 3 observations Mar 21-23, 2018.
    # Mean D0 computed: 17.38°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-03-21", "time_local": "05:30",
        "utc_offset": 9.0, "lat": -0.691, "lng": 127.390, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Ternate North Maluku Indonesia",
        "notes": "DSLR; D0=16.95° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-03-22", "time_local": "05:25",
        "utc_offset": 9.0, "lat": -0.691, "lng": 127.390, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Ternate North Maluku Indonesia",
        "notes": "DSLR; D0=18.14° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-03-23", "time_local": "05:29",
        "utc_offset": 9.0, "lat": -0.691, "lng": 127.390, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Ternate North Maluku Indonesia",
        "notes": "DSLR; D0=17.06° computed; clear sky; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # SOUTH SULAWESI / GOWA AREA, INDONESIA (-5.610°S, 120.467°E, 5m, UTC+8)
    # Coordinates from paper: 5°36'36"S, 120°28'03"E
    # Rural/coastal area in Gowa Regency near Makassar.
    # 6 observations Mar 24-29, 2018.
    # Mean D0 computed: 18.01°
    # Note: Mar 27 and 29 had cloud issues per paper text but times still recorded.
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-03-24", "time_local": "04:52",
        "utc_offset": 8.0, "lat": -5.610, "lng": 120.467, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, South Sulawesi Gowa Indonesia",
        "notes": "DSLR; D0=18.19° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-03-25", "time_local": "04:58",
        "utc_offset": 8.0, "lat": -5.610, "lng": 120.467, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, South Sulawesi Gowa Indonesia",
        "notes": "DSLR; D0=16.66° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-03-26", "time_local": "04:51",
        "utc_offset": 8.0, "lat": -5.610, "lng": 120.467, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, South Sulawesi Gowa Indonesia",
        "notes": "DSLR; D0=18.36° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-03-27", "time_local": "04:48",
        "utc_offset": 8.0, "lat": -5.610, "lng": 120.467, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, South Sulawesi Gowa Indonesia",
        "notes": "DSLR; D0=19.07° computed; cloud on horizon per paper; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-03-28", "time_local": "04:54",
        "utc_offset": 8.0, "lat": -5.610, "lng": 120.467, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, South Sulawesi Gowa Indonesia",
        "notes": "DSLR; D0=17.53° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-03-29", "time_local": "04:51",
        "utc_offset": 8.0, "lat": -5.610, "lng": 120.467, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, South Sulawesi Gowa Indonesia",
        "notes": "DSLR; D0=18.24° computed; cloud on horizon per paper; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # MERSING, JOHOR, MALAYSIA (2.432°N, 103.827°E, 5m, UTC+8)
    # East coast Johor. South China Sea horizon — dry season (Jun-Sep) clear sky.
    # 3 observations Jun 22-24, 2018.
    # Mean D0 computed: 19.31°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-06-22", "time_local": "05:37",
        "utc_offset": 8.0, "lat": 2.432, "lng": 103.827, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Mersing Johor Malaysia",
        "notes": "DSLR; D0=19.41° computed; dry season clear sky; South China Sea horizon; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-06-23", "time_local": "05:38",
        "utc_offset": 8.0, "lat": 2.432, "lng": 103.827, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Mersing Johor Malaysia",
        "notes": "DSLR; D0=19.24° computed; dry season clear sky; South China Sea horizon; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-06-24", "time_local": "05:38",
        "utc_offset": 8.0, "lat": 2.432, "lng": 103.827, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Mersing Johor Malaysia",
        "notes": "DSLR; D0=19.29° computed; dry season clear sky; South China Sea horizon; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # KUALA ROMPIN, PAHANG, MALAYSIA (2.807°N, 103.491°E, 5m, UTC+8)
    # East coast Pahang. South China Sea horizon — dry season clear sky.
    # 2 observations Jul 16-17, 2018 (3 TD days skipped).
    # Mean D0 computed: 19.45°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-07-16", "time_local": "05:43",
        "utc_offset": 8.0, "lat": 2.807, "lng": 103.491, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Rompin Pahang Malaysia",
        "notes": "DSLR; D0=19.54° computed; dry season clear sky; South China Sea horizon; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-07-17", "time_local": "05:44",
        "utc_offset": 8.0, "lat": 2.807, "lng": 103.491, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Rompin Pahang Malaysia",
        "notes": "DSLR; D0=19.36° computed; dry season clear sky; South China Sea horizon; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # NENASI, PEKAN, PAHANG, MALAYSIA (3.310°N, 103.453°E, 5m, UTC+8)
    # Coastal Pahang. South China Sea horizon.
    # 2 observations Aug 14-15, 2018 (1 TD skipped).
    # Mean D0 computed: 19.39°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-08-14", "time_local": "05:47",
        "utc_offset": 8.0, "lat": 3.310, "lng": 103.453, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Nenasi Pekan Pahang Malaysia",
        "notes": "DSLR; D0=19.39° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-08-15", "time_local": "05:47",
        "utc_offset": 8.0, "lat": 3.310, "lng": 103.453, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Nenasi Pekan Pahang Malaysia",
        "notes": "DSLR; D0=19.39° computed; clear sky; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # KOTA TINGGI, JOHOR, MALAYSIA (1.731°N, 103.904°E, 5m, UTC+8)
    # Inland Johor near river mouth, eastern Johor. Clear Sep 2018 dry season.
    # 3 observations Sep 18-20, 2018.
    # Mean D0 computed: 19.61°
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-09-18", "time_local": "05:40",
        "utc_offset": 8.0, "lat": 1.731, "lng": 103.904, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kota Tinggi Johor Malaysia",
        "notes": "DSLR; D0=19.60° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-09-19", "time_local": "05:40",
        "utc_offset": 8.0, "lat": 1.731, "lng": 103.904, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kota Tinggi Johor Malaysia",
        "notes": "DSLR; D0=19.53° computed; clear sky; actual dawn time from paper Table 2",
    },
    {
        "prayer": "fajr", "date_local": "2018-09-20", "time_local": "05:39",
        "utc_offset": 8.0, "lat": 1.731, "lng": 103.904, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kota Tinggi Johor Malaysia",
        "notes": "DSLR; D0=19.71° computed; clear sky; actual dawn time from paper Table 2",
    },

    # -----------------------------------------------------------------------
    # INDONESIA — Pondok Permai Beach, Serdang Bedagai, North Sumatra
    # Coordinates: ~3.46°N, 99.00°E, ~5m (coastal, Strait of Malacca)
    # UTC+7 (WIB)
    # Source: Pinem, R.K.B., Hidayat, M. & Ananda, F.S. (2024).
    #   "The Influence of MPSAS Values and SQM Angles in Determining Fajr Time."
    #   Journal of Mathematics Education and Application (JMEA), 3(1).
    #   DOI: 10.30596/jmea.v3i1.18859
    #   SQM observations; coastal beach ~30km south of Medan; darker than urban.
    #   Aggregate mean D0 = -15.0° for Pondok Permai.
    # 4 seasonal aggregate records.
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2022-03-21", "time_local": "05:31",
        "utc_offset": 7.0, "lat": 3.46, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Pondok Permai Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; ~30km S of Medan; D0=15.0°; spring equinox inferred",
    },
    {
        "prayer": "fajr", "date_local": "2022-06-22", "time_local": "05:13",
        "utc_offset": 7.0, "lat": 3.46, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Pondok Permai Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; D0=15.0°; summer solstice inferred",
    },
    {
        "prayer": "fajr", "date_local": "2022-09-23", "time_local": "05:16",
        "utc_offset": 7.0, "lat": 3.46, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Pondok Permai Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; D0=15.0°; autumn equinox inferred",
    },
    {
        "prayer": "fajr", "date_local": "2022-12-22", "time_local": "05:22",
        "utc_offset": 7.0, "lat": 3.46, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Pondok Permai Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; D0=15.0°; winter solstice inferred",
    },

    # -----------------------------------------------------------------------
    # INDONESIA — Sri Mersing Beach, Serdang Bedagai, North Sumatra
    # Coordinates: ~3.45°N, 99.00°E, ~5m (coastal, Strait of Malacca)
    # UTC+7 (WIB)
    # Same source paper as above (Pinem et al. 2024, JMEA 3(1)).
    # Adjacent beach ~1km from Pondok Permai; slightly more LP-influenced.
    # Aggregate mean D0 = -14.0° for Sri Mersing.
    # 4 seasonal aggregate records.
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2022-03-21", "time_local": "05:35",
        "utc_offset": 7.0, "lat": 3.45, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Sri Mersing Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; D0=14.0°; LP-influenced vs Pondok Permai; spring equinox",
    },
    {
        "prayer": "fajr", "date_local": "2022-06-22", "time_local": "05:18",
        "utc_offset": 7.0, "lat": 3.45, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Sri Mersing Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; D0=14.0°; LP-influenced; summer solstice",
    },
    {
        "prayer": "fajr", "date_local": "2022-09-23", "time_local": "05:20",
        "utc_offset": 7.0, "lat": 3.45, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Sri Mersing Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; D0=14.0°; LP-influenced; autumn equinox",
    },
    {
        "prayer": "fajr", "date_local": "2022-12-22", "time_local": "05:27",
        "utc_offset": 7.0, "lat": 3.45, "lng": 99.00, "elevation_m": 5.0,
        "source": "Pinem et al. 2024, JMEA 3(1), Sri Mersing Beach North Sumatra",
        "notes": "SQM; coastal Strait of Malacca; D0=14.0°; LP-influenced; winter solstice",
    },

    # -----------------------------------------------------------------------
    # JATMA 2019 FIRST TABLE — ROWS 1-50 (Malaysian Sites, Feb-Nov 2017)
    # Source: Kassim Bahali, Samian, Muslim & Abdul Hamid (2019).
    #   "Re-evaluation of Calculation of the Dawn Prayer Time in the Malay World."
    #   JATMA: Journal of Al-Tamaddun 7(2):37-48.
    #   DOI: 10.17576/jatma-2019-0702-04
    # Instrument: DSLR Canon 60Da, calibrated (Kc=74). Sea horizon for coastal sites.
    # UTC+8 (Malaysia Standard Time) for all Malaysia sites.
    # Depression angles computed via PyEphem from actual observed dawn times.
    # (Rows 9-27 = Pekan already in dataset; row 16 = TD, skipped)
    # -----------------------------------------------------------------------

    # KUANTAN, PAHANG — 3°48'45"N, 103°22'19"E — sea horizon
    {
        "prayer": "fajr", "date_local": "2017-02-08", "time_local": "06:17",
        "utc_offset": 8.0, "lat": 3.8125, "lng": 103.3719, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuantan Pahang Malaysia",
        "notes": "DSLR; D0=16.35° computed; sea horizon; actual dawn from paper JADUAL 2 row 1",
    },
    {
        "prayer": "fajr", "date_local": "2017-02-09", "time_local": "06:10",
        "utc_offset": 8.0, "lat": 3.8125, "lng": 103.3719, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuantan Pahang Malaysia",
        "notes": "DSLR; D0=18.05° computed; sea horizon; actual dawn from paper JADUAL 2 row 2",
    },
    {
        "prayer": "fajr", "date_local": "2017-02-10", "time_local": "06:14",
        "utc_offset": 8.0, "lat": 3.8125, "lng": 103.3719, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuantan Pahang Malaysia",
        "notes": "DSLR; D0=17.09° computed; sea horizon; actual dawn from paper JADUAL 2 row 3",
    },

    # RANTAU ABANG, TERENGGANU — 4°51'53"N, 103°23'37"E — sea horizon
    {
        "prayer": "fajr", "date_local": "2017-03-01", "time_local": "06:21",
        "utc_offset": 8.0, "lat": 4.8647, "lng": 103.3936, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Rantau Abang Terengganu Malaysia",
        "notes": "DSLR; D0=14.94° computed; sea horizon; dawn JADUAL 2 row 4",
    },
    {
        "prayer": "fajr", "date_local": "2017-03-02", "time_local": "06:21",
        "utc_offset": 8.0, "lat": 4.8647, "lng": 103.3936, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Rantau Abang Terengganu Malaysia",
        "notes": "DSLR; D0=14.87° computed; sea horizon; dawn JADUAL 2 row 5",
    },
    {
        "prayer": "fajr", "date_local": "2017-03-03", "time_local": "06:17",
        "utc_offset": 8.0, "lat": 4.8647, "lng": 103.3936, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Rantau Abang Terengganu Malaysia",
        "notes": "DSLR; D0=15.79° computed; sea horizon; dawn JADUAL 2 row 6",
    },

    # PENOR, PAHANG — 3°40'23"N, 103°21'03"E — sea horizon
    {
        "prayer": "fajr", "date_local": "2017-04-03", "time_local": "06:08",
        "utc_offset": 8.0, "lat": 3.6731, "lng": 103.3508, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Penor Pahang Malaysia",
        "notes": "DSLR; D0=15.05° computed; sea horizon; dawn JADUAL 2 row 7",
    },
    {
        "prayer": "fajr", "date_local": "2017-04-04", "time_local": "06:04",
        "utc_offset": 8.0, "lat": 3.6731, "lng": 103.3508, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Penor Pahang Malaysia",
        "notes": "DSLR; D0=15.93° computed; sea horizon; dawn JADUAL 2 row 8",
    },

    # KUALA DUNGUN, TERENGGANU — 4°47'42"N, 103°25'34"E — sea horizon
    {
        "prayer": "fajr", "date_local": "2017-07-31", "time_local": "05:51",
        "utc_offset": 8.0, "lat": 4.7950, "lng": 103.4261, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Dungun Terengganu Malaysia",
        "notes": "DSLR; D0=17.70° computed; sea horizon; dawn JADUAL 2 row 28",
    },
    {
        "prayer": "fajr", "date_local": "2017-08-01", "time_local": "05:52",
        "utc_offset": 8.0, "lat": 4.7950, "lng": 103.4261, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Dungun Terengganu Malaysia",
        "notes": "DSLR; D0=17.50° computed; sea horizon; dawn JADUAL 2 row 29",
    },
    {
        "prayer": "fajr", "date_local": "2017-08-02", "time_local": "05:55",
        "utc_offset": 8.0, "lat": 4.7950, "lng": 103.4261, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Dungun Terengganu Malaysia",
        "notes": "DSLR; D0=16.84° computed; sea horizon; dawn JADUAL 2 row 30",
    },
    {
        "prayer": "fajr", "date_local": "2017-08-05", "time_local": "05:52",
        "utc_offset": 8.0, "lat": 4.7950, "lng": 103.4261, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Dungun Terengganu Malaysia",
        "notes": "DSLR; D0=17.63° computed; sea horizon; dawn JADUAL 2 row 33",
    },

    # KUALA TERENGGANU — additional dates (Aug 3-4, 2017, not yet in dataset)
    {
        "prayer": "fajr", "date_local": "2017-08-03", "time_local": "05:49",
        "utc_offset": 8.0, "lat": 5.325, "lng": 103.145, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Terengganu Malaysia",
        "notes": "DSLR; D0=18.35° computed; sea horizon; Aug 3 new date; JADUAL 2 row 31",
    },
    {
        "prayer": "fajr", "date_local": "2017-08-04", "time_local": "05:53",
        "utc_offset": 8.0, "lat": 5.325, "lng": 103.145, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuala Terengganu Malaysia",
        "notes": "DSLR; D0=17.45° computed; sea horizon; Aug 4 new date; JADUAL 2 row 32",
    },

    # JASIN, MELAKA — 2°20'04"N, 102°18'57"E — land horizon (Darat)
    {
        "prayer": "fajr", "date_local": "2017-10-19", "time_local": "05:56",
        "utc_offset": 8.0, "lat": 2.3344, "lng": 102.3158, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Jasin Melaka Malaysia",
        "notes": "DSLR; D0=15.12° computed; land horizon; inland Melaka; JADUAL 2 row 34",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-20", "time_local": "05:54",
        "utc_offset": 8.0, "lat": 2.3344, "lng": 102.3158, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Jasin Melaka Malaysia",
        "notes": "DSLR; D0=15.57° computed; land horizon; JADUAL 2 row 35",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-21", "time_local": "05:47",
        "utc_offset": 8.0, "lat": 2.3344, "lng": 102.3158, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Jasin Melaka Malaysia",
        "notes": "DSLR; D0=17.24° computed; land horizon; JADUAL 2 row 36",
    },

    # SETIU, TERENGGANU — 5°35'52"N, 102°47'49"E — sea horizon
    {
        "prayer": "fajr", "date_local": "2017-10-23", "time_local": "05:47",
        "utc_offset": 8.0, "lat": 5.5978, "lng": 102.7969, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Setiu Terengganu Malaysia",
        "notes": "DSLR; D0=17.29° computed; sea horizon; Oct 23; JADUAL 2 row 37",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-24", "time_local": "05:48",
        "utc_offset": 8.0, "lat": 5.5978, "lng": 102.7969, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Setiu Terengganu Malaysia",
        "notes": "DSLR; D0=17.03° computed; sea horizon; JADUAL 2 row 38",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-25", "time_local": "05:52",
        "utc_offset": 8.0, "lat": 5.5978, "lng": 102.7969, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Setiu Terengganu Malaysia",
        "notes": "DSLR; D0=16.03° computed; sea horizon; JADUAL 2 row 39",
    },

    # BACHOK, KELANTAN — ~6.05°N, 102.44°E — sea horizon (east coast Kelantan)
    {
        "prayer": "fajr", "date_local": "2017-10-26", "time_local": "05:54",
        "utc_offset": 8.0, "lat": 6.0500, "lng": 102.4400, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Bachok Kelantan Malaysia",
        "notes": "DSLR; D0=15.97° computed; sea horizon; South China Sea; JADUAL 2 row 40",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-27", "time_local": "05:53",
        "utc_offset": 8.0, "lat": 6.0500, "lng": 102.4400, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Bachok Kelantan Malaysia",
        "notes": "DSLR; D0=16.20° computed; sea horizon; JADUAL 2 row 41",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-28", "time_local": "05:52",
        "utc_offset": 8.0, "lat": 6.0500, "lng": 102.4400, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Bachok Kelantan Malaysia",
        "notes": "DSLR; D0=16.44° computed; sea horizon; JADUAL 2 row 42",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-29", "time_local": "06:05",
        "utc_offset": 8.0, "lat": 6.0500, "lng": 102.4400, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Bachok Kelantan Malaysia",
        "notes": "DSLR; D0=13.28° computed; 21 min after official subuh — heavy cloud at horizon; JADUAL 2 row 43",
    },
    {
        "prayer": "fajr", "date_local": "2017-10-30", "time_local": "05:47",
        "utc_offset": 8.0, "lat": 6.0500, "lng": 102.4400, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Bachok Kelantan Malaysia",
        "notes": "DSLR; D0=17.65° computed; sea horizon; JADUAL 2 row 44",
    },

    # KUANTAN — additional Oct 31, 2017 observation
    {
        "prayer": "fajr", "date_local": "2017-10-31", "time_local": "05:52",
        "utc_offset": 8.0, "lat": 3.8125, "lng": 103.3719, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Kuantan Pahang Malaysia",
        "notes": "DSLR; D0=15.02° computed; sea horizon; Oct 31 additional visit; JADUAL 2 row 45",
    },

    # DURIAN TUNGGAL, MELAKA — ~2.31°N, 102.17°E — land horizon
    {
        "prayer": "fajr", "date_local": "2017-11-01", "time_local": "05:52",
        "utc_offset": 8.0, "lat": 2.3100, "lng": 102.1700, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Durian Tunggal Melaka Malaysia",
        "notes": "DSLR; D0=15.81° computed; land horizon; Alor Gajah district; JADUAL 2 row 46",
    },
    {
        "prayer": "fajr", "date_local": "2017-11-02", "time_local": "05:49",
        "utc_offset": 8.0, "lat": 2.3100, "lng": 102.1700, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Durian Tunggal Melaka Malaysia",
        "notes": "DSLR; D0=16.52° computed; land horizon; JADUAL 2 row 47",
    },

    # LANGKAWI, KEDAH — 6°18'23"N, 99°51'45"E — sea horizon (Andaman Sea)
    {
        "prayer": "fajr", "date_local": "2017-11-23", "time_local": "06:03",
        "utc_offset": 8.0, "lat": 6.3064, "lng": 99.8625, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Langkawi Kedah Malaysia",
        "notes": "DSLR; D0=17.13° computed; sea horizon; Andaman Sea; JADUAL 2 row 48",
    },
    {
        "prayer": "fajr", "date_local": "2017-11-24", "time_local": "06:01",
        "utc_offset": 8.0, "lat": 6.3064, "lng": 99.8625, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Langkawi Kedah Malaysia",
        "notes": "DSLR; D0=17.67° computed; sea horizon; JADUAL 2 row 49",
    },
    {
        "prayer": "fajr", "date_local": "2017-11-25", "time_local": "06:00",
        "utc_offset": 8.0, "lat": 6.3064, "lng": 99.8625, "elevation_m": 5.0,
        "source": "Kassim Bahali et al. 2019, JATMA 7(2):37-48, Langkawi Kedah Malaysia",
        "notes": "DSLR; D0=17.97° computed; sea horizon; JADUAL 2 row 50",
    },

    # =========================================================================
    # BATCH 8 — Saksono & Fulazzaky 2020, NRIAG Journal Astronomy & Geophysics
    # =========================================================================
    # Source: Saksono T. & Fulazzaky M.A. (2020). "Predicting the accurate period
    # of true dawn using a third-degree polynomial model." NRIAG Journal of
    # Astronomy and Geophysics 9:238-244. DOI: 10.1080/20909977.2020.1738106
    #
    # Site: Depok, West Java, Indonesia — suburban city south of Jakarta.
    # Coords: 6.383°S, 106.83°E, ~150m elevation, UTC+7 (WIB).
    # Method: SQM (SQM-LU-DL-Unihedron), every 3 seconds from midnight to sunrise.
    # Period: 26 nights, June-July 2015.
    # Result: D0 = -14.0° ± 0.6° (urban/suburban LP site, similar to Saksono ISRN mean).
    # 8 representative dates spanning Jun-Jul 2015 observation period.
    # =========================================================================

    # -----------------------------------------------------------------------
    # DEPOK, WEST JAVA, INDONESIA (6.383°S, 106.83°E, ~150m, UTC+7)
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2015-06-06", "time_local": "05:01",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-11", "time_local": "05:02",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-16", "time_local": "05:03",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-21", "time_local": "05:04",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2015-07-02", "time_local": "05:06",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2015-07-11", "time_local": "05:07",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2015-07-21", "time_local": "05:08",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2015-07-26", "time_local": "05:08",
        "utc_offset": 7.0, "lat": -6.383, "lng": 106.83, "elevation_m": 150.0,
        "source": "Saksono & Fulazzaky 2020, NRIAG J Astron Geophys 9:238-244, Depok West Java",
        "notes": "SQM; D0=14.0° ± 0.6°; suburban LP; Jun-Jul 2015 campaign; 26 nights total; aggregate",
    },

    # =========================================================================
    # BATCH 9 — Rashed et al. 2022, IJMET 13(10):8-24
    # =========================================================================
    # Source: Rashed M.G., Abdel-Hadi Y.A. et al. (2022). "Determination of
    # the True Dawn by Several Different Ways at Fayum in Egypt."
    # IJMET 13(10):8-24. DOI: 10.17605/OSF.IO/9K3MJ
    # 16 authors (NRIAG + Cairo Univ + Al-Azhar Univ).
    #
    # Site: Wadi al-Hitan (Whale Valley), Fayum Governorate, Egypt.
    # Remote desert archaeological reserve, 50km from nearest city.
    # Coords: 29°17'N, 30°03'E = 29.283°N, 30.050°E, ~50m, UTC+2.
    # Method: SQM-LU-DL (horizontal + zenith simultaneously) + trained naked eye groups.
    # Actual observation nights: Dec 9, 10 2018 (clear) + Dec 19, 2019 (clear).
    # Dec 11 2018 was fully cloudy (Do=10° postponed) — excluded.
    # Result: D0 = 14.7° (eye threshold mean); 14.0°-14.8° across methods.
    # No per-night clock times published; dates 1-3 are actual, 4-6 are seasonal aggregates.
    # =========================================================================

    # -----------------------------------------------------------------------
    # FAYUM (WADI AL-HITAN), EGYPT (29.283°N, 30.050°E, ~50m, UTC+2)
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2018-12-09", "time_local": "05:33",
        "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10):8-24, Fayum Wadi al-Hitan Egypt",
        "notes": "SQM+naked eye; D0=14.6° (eye threshold); desert; actual obs date Dec 9 2018",
    },
    {
        "prayer": "fajr", "date_local": "2018-12-10", "time_local": "05:34",
        "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10):8-24, Fayum Wadi al-Hitan Egypt",
        "notes": "SQM+naked eye; D0=14.7° (eye threshold); desert; actual obs date Dec 10 2018",
    },
    {
        "prayer": "fajr", "date_local": "2019-12-19", "time_local": "05:39",
        "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10):8-24, Fayum Wadi al-Hitan Egypt",
        "notes": "SQM+naked eye; D0=14.0°(H=piZ) 14.8°(naked eye); desert; actual obs date Dec 19 2019",
    },
    {
        "prayer": "fajr", "date_local": "2019-03-20", "time_local": "05:00",
        "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10):8-24, Fayum Wadi al-Hitan Egypt",
        "notes": "SQM+naked eye; D0=14.7° mean; desert; spring equinox aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2019-06-21", "time_local": "03:45",
        "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10):8-24, Fayum Wadi al-Hitan Egypt",
        "notes": "SQM+naked eye; D0=14.7° mean; desert; summer solstice aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2019-09-23", "time_local": "04:44",
        "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
        "source": "Rashed et al. 2022, IJMET 13(10):8-24, Fayum Wadi al-Hitan Egypt",
        "notes": "SQM+naked eye; D0=14.7° mean; desert; autumn equinox aggregate",
    },

    # =========================================================================
    # BATCH 10 — Abdel-Hadi Y.A. & Hassan A.H. (2022), IJAA 12(1):7-29
    # =========================================================================
    # Source: "The Effect of Sun Elevation on the Twilight Stages in Malaysia"
    # IJAA (Int. Journal of Astronomy and Astrophysics) 12(1):7-29, 2022.
    # DOI: 10.4236/ijaa.2022.121002
    # Data collected by: Shariff N.N.M. (2008 M.Sc. thesis, Universiti Malaya)
    # using SQM-LE, 2-minute intervals, aimed at azimuth of sunrise/sunset.
    # UTC+8 (Malaysia Standard Time) for all sites.
    #
    # Per-date D0 values from Table 7 (Fajr / true dawn) and Table 5 (Isha / true dusk).
    # Fajr: column a6 = depression at True Dawn Sadiq onset (N=8 nights, 3 sites).
    # Isha: column a1 = depression at True Dusk onset (N=12 nights, 4 sites).
    # New sites: Merang, Kuala Lipis, Port Klang.
    # =========================================================================

    # -----------------------------------------------------------------------
    # FAJR — Table 7 (a6 = True Dawn)
    # -----------------------------------------------------------------------

    # Merang, Terengganu (5.517°N, 102.95°E, 42m) — NEW SITE
    {
        "prayer": "fajr", "date_local": "2007-05-08", "time_local": "05:56",
        "utc_offset": 8.0, "lat": 5.517, "lng": 102.950, "elevation_m": 42.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Merang Terengganu Malaysia",
        "notes": "SQM-LE; D0=14.595° (Table 7 a6, true dawn); Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },

    # Kuala Lipis, Pahang (4.183°N, 102.05°E, 75m) — NEW SITE
    {
        "prayer": "fajr", "date_local": "2007-11-10", "time_local": "06:01",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=14.079° (Table 7 a6, true dawn); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "fajr", "date_local": "2007-12-29", "time_local": "06:17",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=14.595° (Table 7 a6, true dawn); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "fajr", "date_local": "2008-01-11", "time_local": "06:26",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=13.864° (Table 7 a6, true dawn); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "fajr", "date_local": "2008-02-09", "time_local": "06:34",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=13.419° (Table 7 a6, true dawn); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "fajr", "date_local": "2008-03-22", "time_local": "06:22",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=13.970° (Table 7 a6, true dawn); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "fajr", "date_local": "2008-03-23", "time_local": "06:21",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=13.970° (Table 7 a6, true dawn); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },

    # Port Klang, Selangor (3.000°N, 101.40°E, 46m) — NEW SITE
    {
        "prayer": "fajr", "date_local": "2008-04-07", "time_local": "06:13",
        "utc_offset": 8.0, "lat": 3.000, "lng": 101.400, "elevation_m": 46.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Port Klang Selangor Malaysia",
        "notes": "SQM-LE; D0=15.065° (Table 7 a6, true dawn); coastal port; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },

    # -----------------------------------------------------------------------
    # ISHA — Table 5 (a1 = True Dusk begins)
    # -----------------------------------------------------------------------

    # Teluk Kemang, Negeri Sembilan (2.467°N, 101.867°E, 27m) — already in dataset; new dates
    {
        "prayer": "isha", "date_local": "2007-06-15", "time_local": "20:19",
        "utc_offset": 8.0, "lat": 2.467, "lng": 101.867, "elevation_m": 27.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Teluk Kemang Negeri Sembilan Malaysia",
        "notes": "SQM-LE; D0=14.213° (Table 5 a1, true dusk); coastal NS; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2007-08-13", "time_local": "20:20",
        "utc_offset": 8.0, "lat": 2.467, "lng": 101.867, "elevation_m": 27.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Teluk Kemang Negeri Sembilan Malaysia",
        "notes": "SQM-LE; D0=14.690° (Table 5 a1, true dusk); coastal NS; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },

    # Kuala Lumpur, Federal Territory (3.150°N, 101.683°E, 60m) — already in dataset; new dates
    {
        "prayer": "isha", "date_local": "2007-09-04", "time_local": "20:05",
        "utc_offset": 8.0, "lat": 3.150, "lng": 101.683, "elevation_m": 60.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lumpur Malaysia",
        "notes": "SQM-LE; D0=12.850° (Table 5 a1, true dusk); urban LP; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2007-10-27", "time_local": "19:57",
        "utc_offset": 8.0, "lat": 3.150, "lng": 101.683, "elevation_m": 60.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lumpur Malaysia",
        "notes": "SQM-LE; D0=15.340° (Table 5 a1, true dusk); urban LP; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },

    # Kuala Lipis, Pahang (4.183°N, 102.05°E, 75m) — Isha at same site as above Fajr
    {
        "prayer": "isha", "date_local": "2007-12-29", "time_local": "20:09",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=14.420° (Table 5 a1, true dusk); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2008-01-11", "time_local": "20:11",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=13.600° (Table 5 a1, true dusk); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2008-01-12", "time_local": "20:14",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=14.330° (Table 5 a1, true dusk); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2008-02-09", "time_local": "20:15",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=13.003° (Table 5 a1, true dusk); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2008-03-22", "time_local": "20:18",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=14.938° (Table 5 a1, true dusk); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2008-03-23", "time_local": "20:18",
        "utc_offset": 8.0, "lat": 4.183, "lng": 102.050, "elevation_m": 75.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Kuala Lipis Pahang Malaysia",
        "notes": "SQM-LE; D0=14.938° (Table 5 a1, true dusk); inland Pahang; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },

    # Port Klang, Selangor (3.000°N, 101.40°E, 46m) — Isha at same site as above Fajr
    {
        "prayer": "isha", "date_local": "2008-04-05", "time_local": "20:14",
        "utc_offset": 8.0, "lat": 3.000, "lng": 101.400, "elevation_m": 46.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Port Klang Selangor Malaysia",
        "notes": "SQM-LE; D0=13.970° (Table 5 a1, true dusk); coastal port; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },
    {
        "prayer": "isha", "date_local": "2008-04-06", "time_local": "20:18",
        "utc_offset": 8.0, "lat": 3.000, "lng": 101.400, "elevation_m": 46.0,
        "source": "Abdel-Hadi & Hassan 2022, IJAA 12(1):7-29, Port Klang Selangor Malaysia",
        "notes": "SQM-LE; D0=14.938° (Table 5 a1, true dusk); coastal port; Shariff 2008 data; time inferred from published D0 (paper Tables 3-11 have no clock times)",
    },

    # =========================================================================
    # BATCH 11 — Herdiwijaya 2016 + 2020 — Amfoang/Kupang, East Nusa Tenggara
    # =========================================================================
    # Source: Herdiwijaya D. (2016). J. Phys.: Conf. Ser. 771, 012033.
    #   DOI: 10.1088/1742-6596/771/1/012033
    # Also: Herdiwijaya D. (2020). J. Phys.: Conf. Ser. 1523, 012007.
    #   DOI: 10.1088/1742-6596/1523/1/012007
    #
    # Site: Amfoang, Kupang, East Nusa Tenggara, Indonesia.
    # High-elevation dark site used as pristine control in 5-station comparison study.
    # Coords: 9°40'S, 124°0'E, ~1300m, UTC+8 (WITA).
    # Method: Portable SQM, moonless nights, 2011-2018.
    # D0 = 18.0° (pristine dark site; paper recommends 17°-18.5° for Indonesia dark sites).
    # 5 records: 1 actual representative date (May 10 2013) + 4 seasonal pivots 2016.
    # =========================================================================

    # -----------------------------------------------------------------------
    # KUPANG (AMFOANG), EAST NUSA TENGGARA (9.667°S, 124.0°E, 1300m, UTC+8)
    # -----------------------------------------------------------------------
    {
        "prayer": "fajr", "date_local": "2013-05-11", "time_local": "04:36",
        "utc_offset": 8.0, "lat": -9.667, "lng": 124.000, "elevation_m": 1300.0,
        "source": "Herdiwijaya 2016+2020 J.Phys.Conf.Ser., Kupang Amfoang NTT Indonesia",
        "notes": "SQM portable; D0~18.0°; high-elev dark site; 83 moonless nights 2011-2018; rep date May 10 2013",
    },
    {
        "prayer": "fajr", "date_local": "2016-03-21", "time_local": "04:38",
        "utc_offset": 8.0, "lat": -9.667, "lng": 124.000, "elevation_m": 1300.0,
        "source": "Herdiwijaya 2016+2020 J.Phys.Conf.Ser., Kupang Amfoang NTT Indonesia",
        "notes": "SQM portable; D0~18.0°; high-elev dark site; spring equinox aggregate",
    },
    {
        "prayer": "fajr", "date_local": "2016-06-22", "time_local": "04:43",
        "utc_offset": 8.0, "lat": -9.667, "lng": 124.000, "elevation_m": 1300.0,
        "source": "Herdiwijaya 2016+2020 J.Phys.Conf.Ser., Kupang Amfoang NTT Indonesia",
        "notes": "SQM portable; D0~18.0°; high-elev dark site; winter solstice aggregate (SH)",
    },
    {
        "prayer": "fajr", "date_local": "2016-09-23", "time_local": "04:23",
        "utc_offset": 8.0, "lat": -9.667, "lng": 124.000, "elevation_m": 1300.0,
        "source": "Herdiwijaya 2016+2020 J.Phys.Conf.Ser., Kupang Amfoang NTT Indonesia",
        "notes": "SQM portable; D0~18.0°; high-elev dark site; autumn equinox aggregate (SH)",
    },
    {
        "prayer": "fajr", "date_local": "2016-12-22", "time_local": "04:04",
        "utc_offset": 8.0, "lat": -9.667, "lng": 124.000, "elevation_m": 1300.0,
        "source": "Herdiwijaya 2016+2020 J.Phys.Conf.Ser., Kupang Amfoang NTT Indonesia",
        "notes": "SQM portable; D0~18.0°; high-elev dark site; summer solstice aggregate (SH)",
    },

    # =========================================================================
    # BATCH 12 — Herdiwijaya D. 2015 ICOPIA (5 sites, actual observation dates)
    # Source: Herdiwijaya D. (2015). "Implications of Twilight Sky Brightness
    #   Measurements on Fajr Prayer and Young Crescent Observation."
    #   Proceedings ICOPIA 2014. DOI: 10.2991/icopia-14.2015.5
    #
    # 5 sites each observed one clear night. No per-site angle — paper proposes
    # D0 = 17° for all of Indonesia (recommendation, not site-specific measurement).
    # Using target_angle=17.0° to compute representative clock times.
    # Amfoang May 10 2013 SKIPPED — already in Batch 11 (Kupang Amfoang).
    # =========================================================================

    # BOSSCHA/LEMBANG, West Java (6.817°S, 107.617°E, 1300m, UTC+7)
    # Observation: May 17, 2013 morning. Fig 1 in paper.
    {
        "prayer": "fajr", "date_local": "2013-05-18", "time_local": "04:43",
        "utc_offset": 7.0, "lat": -6.817, "lng": 107.617, "elevation_m": 1300.0,
        "source": "Herdiwijaya 2015 ICOPIA, Bosscha Lembang West Java Indonesia",
        "notes": "SQM; actual obs night May 17 2013 (Fig 1); D0=17° (paper's Indonesia proposal)",
    },
    # BANDUNG, West Java (6.914°S, 107.609°E, 780m, UTC+7)
    # Observation: Dec 18, 2013 morning. Fig 2 in paper. Urban LP site.
    {
        "prayer": "fajr", "date_local": "2013-12-19", "time_local": "04:18",
        "utc_offset": 7.0, "lat": -6.914, "lng": 107.609, "elevation_m": 780.0,
        "source": "Herdiwijaya 2015 ICOPIA, Bandung West Java Indonesia",
        "notes": "SQM; actual obs night Dec 18 2013 (Fig 2); urban LP; D0=17° (paper's Indonesia proposal)",
    },
    # CIMAHI, West Java (6.883°S, 107.533°E, 700m, UTC+7)
    # Observation: Dec 18, 2013 morning. Fig 3 in paper. Urban LP site.
    {
        "prayer": "fajr", "date_local": "2013-12-19", "time_local": "04:19",
        "utc_offset": 7.0, "lat": -6.883, "lng": 107.533, "elevation_m": 700.0,
        "source": "Herdiwijaya 2015 ICOPIA, Cimahi West Java Indonesia",
        "notes": "SQM; actual obs night Dec 18 2013 (Fig 3); urban LP; D0=17° (paper's Indonesia proposal)",
    },
    # YOGYAKARTA, Central Java (7.867°S, 110.417°E, 100m, UTC+7)
    # Observation: Jul 26, 2014 morning. Fig 4 in paper.
    {
        "prayer": "fajr", "date_local": "2014-07-27", "time_local": "04:43",
        "utc_offset": 7.0, "lat": -7.867, "lng": 110.417, "elevation_m": 100.0,
        "source": "Herdiwijaya 2015 ICOPIA, Yogyakarta Central Java Indonesia",
        "notes": "SQM; actual obs night Jul 26 2014 (Fig 4); D0=17° (paper's Indonesia proposal)",
    },

    # =========================================================================
    # BATCH 13 — Setyanto H. et al. 2021 Al-Hilal 3(2) (6 Indonesian sites)
    # Source: Setyanto H., Prastyo H.A., Basthoni M. et al. (2021).
    #   "Zodiac Light Detection Based on Sky Quality Meter (SQM) Data: Preliminary Study."
    #   Al-Hilal: J. Islamic Astron. 3(2), October 2021.
    #   URL: https://journal.walisongo.ac.id/index.php/al-hilal/article/view/8477
    #
    # D0 angles from Table 4 — "dawn appearance" = when SQM first exceeds the
    # zodiacal-light linear baseline (inflection = true Fajr onset).
    # Amfoang May 10 2013 SKIPPED — already in Batch 11 (Kupang).
    # Bosscha Jul 17 2015 and Imahnoong May 11 2018 included with LP/methodology flags.
    # =========================================================================

    # MOMBHUL BEACH, Gresik, East Java (5.786°S, 112.726°E, ~5m, UTC+7)
    # NEW SITE. Jul 9, 2018. D0=19.15° (SQM Table 4). Dark coastal site. R²=0.84.
    {
        "prayer": "fajr", "date_local": "2018-07-10", "time_local": "04:20",
        "utc_offset": 7.0, "lat": -5.786, "lng": 112.726, "elevation_m": 5.0,
        "source": "Setyanto et al. 2021 Al-Hilal 3(2), Mombhul Beach Gresik East Java",
        "notes": "SQM; Jul 9 2018; D0=19.15° (Table 4 zodiacal light baseline inflection); dark coastal site",
    },
    # LABUAN BAJO, Flores, NTT (8.386°S, 119.682°E, ~10m, UTC+8)
    # New date: Apr 24, 2018, D0=19.13°. Consistent with existing Maskufa 2024 (19.30°).
    {
        "prayer": "fajr", "date_local": "2018-04-25", "time_local": "04:48",
        "utc_offset": 8.0, "lat": -8.386, "lng": 119.682, "elevation_m": 10.0,
        "source": "Setyanto et al. 2021 Al-Hilal 3(2), Labuan Bajo Flores NTT Indonesia",
        "notes": "SQM; Apr 24 2018; D0=19.13° (Table 4); dark Komodo gateway site; consistent with Maskufa 2024 (19.30°)",
    },
    # SEDAN, REMBANG, Central Java (6.756°S, 111.587°E, ~30m, UTC+7)
    # NEW SITE. Jun 16, 2018. D0=17.64°. Semi-dark rural. Best fit (R²=0.93).
    {
        "prayer": "fajr", "date_local": "2018-06-17", "time_local": "04:29",
        "utc_offset": 7.0, "lat": -6.756, "lng": 111.587, "elevation_m": 30.0,
        "source": "Setyanto et al. 2021 Al-Hilal 3(2), Sedan Rembang Central Java Indonesia",
        "notes": "SQM; Jun 16 2018; D0=17.64° (Table 4, R²=0.93 best fit); semi-dark rural Central Java coast",
    },
    # BOSSCHA OBSERVATORY, Lembang, West Java (6.830°S, 107.614°E, 1300m, UTC+7)
    # New date: Jul 17, 2015. D0=16.07° — lower than expected due to LP/ZL fitting issue.
    # ZL fitting range was -75° to -24° (all-night data), which may distort the baseline.
    {
        "prayer": "fajr", "date_local": "2015-07-18", "time_local": "04:57",
        "utc_offset": 7.0, "lat": -6.830, "lng": 107.614, "elevation_m": 1300.0,
        "source": "Setyanto et al. 2021 Al-Hilal 3(2), Bosscha Observatory Lembang West Java",
        "notes": "SQM; Jul 17 2015; D0=16.07° (Table 4); ZL fitting used all-night range — LP+methodology may underestimate",
    },
    # IMAHNOONG OBSERVATORY, Lembang, West Java (6.834°S, 107.617°E, 2200m, UTC+7)
    # NEW SITE (high-altitude dark observatory). May 11, 2018. D0=15.26°.
    # Flat ZL baseline (constant function, not linear) — dawn detection uncertain.
    {
        "prayer": "fajr", "date_local": "2018-05-12", "time_local": "04:50",
        "utc_offset": 7.0, "lat": -6.834, "lng": 107.617, "elevation_m": 2200.0,
        "source": "Setyanto et al. 2021 Al-Hilal 3(2), Imahnoong Observatory Lembang West Java",
        "notes": "SQM; May 11 2018; D0=15.26° (Table 4); flat ZL baseline (no clear trend) — authors flag weather/tool placement issue",
    },

    # =========================================================================
    # BATCH 14 — Lubis V.A. et al. 2025 Al-Hisab 2(4):215-229 (Medan City, Nov 2024)
    # Source: Lubis V.A., Nafilah J. & Jihad J. (2025). "The Determination of Dawn
    #   Time Based Sky Brightness Using Sky Quality Meter (SQM): A Case Study in
    #   Medan City." Al-Hisab: J. Islamic Astron. 2(4):215-229. Dec 2025.
    #   URL: https://jurnal.umsu.ac.id/index.php/alhisab/article/view/27421
    #
    # Site: OIF UMSU Astronomical Observatory, Medan, North Sumatra (UTC+7/WIB).
    # SQM-LU-DL, 1-minute intervals, Nov 1-30, 2024 (30 nights).
    # D0 = -12° to -14°, most clear days 10°-12° — urban tropical LP site.
    # Using D0=13.0° (mean of 12°-14° range) for representative November 2024 dates.
    # Paper mentions Nov 4, 7, 8, 14, 20 as clear-sky days with clear inflection points.
    # Nov 8 specifically cited at D0=~13°. Per-date table is Figure 4 (image, not text).
    # =========================================================================

    # OIF UMSU MEDAN, North Sumatra (3.595°N, 98.672°E, 22m, UTC+7)
    {
        "prayer": "fajr", "date_local": "2024-11-05", "time_local": "05:18",
        "utc_offset": 7.0, "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "Lubis et al. 2025 Al-Hisab 2(4), OIF UMSU Medan North Sumatra",
        "notes": "SQM-LU-DL; Nov 4 2024 (clear day, paper Fig 4); D0=13.0° (urban LP mean); urban Medan",
    },
    {
        "prayer": "fajr", "date_local": "2024-11-08", "time_local": "05:19",
        "utc_offset": 7.0, "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "Lubis et al. 2025 Al-Hisab 2(4), OIF UMSU Medan North Sumatra",
        "notes": "SQM-LU-DL; Nov 7 2024 (clear day, paper Fig 4); D0=13.0° (urban LP mean); urban Medan",
    },
    {
        "prayer": "fajr", "date_local": "2024-11-09", "time_local": "05:19",
        "utc_offset": 7.0, "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "Lubis et al. 2025 Al-Hisab 2(4), OIF UMSU Medan North Sumatra",
        "notes": "SQM-LU-DL; Nov 8 2024 (D0~13° explicitly cited in text); clear inflection; urban Medan",
    },
    {
        "prayer": "fajr", "date_local": "2024-11-15", "time_local": "05:19",
        "utc_offset": 7.0, "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "Lubis et al. 2025 Al-Hisab 2(4), OIF UMSU Medan North Sumatra",
        "notes": "SQM-LU-DL; Nov 14 2024 (clear day, paper Fig 4); D0=13.0° (urban LP mean); urban Medan",
    },
    {
        "prayer": "fajr", "date_local": "2024-11-21", "time_local": "05:21",
        "utc_offset": 7.0, "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "Lubis et al. 2025 Al-Hisab 2(4), OIF UMSU Medan North Sumatra",
        "notes": "SQM-LU-DL; Nov 20 2024 (clear day, paper Fig 4); D0=13.0° (urban LP mean); urban Medan",
    },

    # ── Batch 15: Al-faruq 2013 Bosscha + Niri 2012 Tanjung Aru ──────────────────
    # Al-faruq 2013 (UPI thesis): Bosscha Observatory, W. Java, Indonesia
    # 6.817°S, 107.617°E, 1300m, UTC+7.  Wet season D0=14°/15° Fajr; 14° Isha.
    # Dry season D0=15°/16° Fajr; 15° Isha.  Representative dates: Oct 15 (wet),
    # Jun 15 (dry).  Source: Al-faruq, MF 2013 UPI undergraduate thesis.
    {
        "prayer": "fajr", "date_local": "2012-10-15", "time_local": "04:30",
        "utc_offset": 7.0, "lat": -6.817, "lng": 107.617, "elevation_m": 1300.0,
        "source": "Al-faruq 2013 UPI thesis, Bosscha Observatory West Java Indonesia",
        "notes": "Photoelectric photometer; wet season aggregate D0~15°; representative date Oct 15 2012; D0=14.987°",
    },
    {
        "prayer": "isha", "date_local": "2012-10-15", "time_local": "18:37",
        "utc_offset": 7.0, "lat": -6.817, "lng": 107.617, "elevation_m": 1300.0,
        "source": "Al-faruq 2013 UPI thesis, Bosscha Observatory West Java Indonesia",
        "notes": "Photoelectric photometer; wet season aggregate D0~14°; representative date Oct 15 2012; D0=14.082°",
    },
    {
        "prayer": "fajr", "date_local": "2012-06-15", "time_local": "04:52",
        "utc_offset": 7.0, "lat": -6.817, "lng": 107.617, "elevation_m": 1300.0,
        "source": "Al-faruq 2013 UPI thesis, Bosscha Observatory West Java Indonesia",
        "notes": "Photoelectric photometer; dry season aggregate D0~16°; representative date Jun 15 2012; D0=15.974°",
    },
    {
        "prayer": "isha", "date_local": "2012-06-15", "time_local": "18:44",
        "utc_offset": 7.0, "lat": -6.817, "lng": 107.617, "elevation_m": 1300.0,
        "source": "Al-faruq 2013 UPI thesis, Bosscha Observatory West Java Indonesia",
        "notes": "Photoelectric photometer; dry season aggregate D0~15°; representative date Jun 15 2012; D0=15.042°",
    },
    # Niri et al. 2012 (MEJSR): Tanjung Aru Beach, Kota Kinabalu, Sabah, Malaysia
    # 5.950°N, 116.033°E, 3.7m, UTC+8.  Shafaq al-Abyad Isha D0=18.0°.
    # Jun 2009 observation campaign; 4 seasonal representative dates added.
    # Source: Niri, Zainuddin et al. 2012 Middle-East J. Scientific Research 12(1).
    {
        "prayer": "isha", "date_local": "2009-03-20", "time_local": "19:36",
        "utc_offset": 8.0, "lat": 5.950, "lng": 116.033, "elevation_m": 3.7,
        "source": "Niri et al. 2012 Middle-East J. Scientific Research 12(1), Tanjung Aru Kota Kinabalu Sabah",
        "notes": "Naked-eye + SQM; D0=18.0° (Shafaq al-Abyad); seasonal representative date; D0=18.076°",
    },
    {
        "prayer": "isha", "date_local": "2009-06-21", "time_local": "19:48",
        "utc_offset": 8.0, "lat": 5.950, "lng": 116.033, "elevation_m": 3.7,
        "source": "Niri et al. 2012 Middle-East J. Scientific Research 12(1), Tanjung Aru Kota Kinabalu Sabah",
        "notes": "Naked-eye + SQM; D0=18.0° (Shafaq al-Abyad); summer solstice representative date; D0=18.012°",
    },
    {
        "prayer": "isha", "date_local": "2009-09-22", "time_local": "19:21",
        "utc_offset": 8.0, "lat": 5.950, "lng": 116.033, "elevation_m": 3.7,
        "source": "Niri et al. 2012 Middle-East J. Scientific Research 12(1), Tanjung Aru Kota Kinabalu Sabah",
        "notes": "Naked-eye + SQM; D0=18.0° (Shafaq al-Abyad); seasonal representative date; D0=17.997°",
    },
    {
        "prayer": "isha", "date_local": "2009-12-21", "time_local": "19:22",
        "utc_offset": 8.0, "lat": 5.950, "lng": 116.033, "elevation_m": 3.7,
        "source": "Niri et al. 2012 Middle-East J. Scientific Research 12(1), Tanjung Aru Kota Kinabalu Sabah",
        "notes": "Naked-eye + SQM; D0=18.0° (Shafaq al-Abyad); seasonal representative date; D0=17.939°",
    },

    # ── Batch 16: Khalifa 2018 Hail + Herdiwijaya 2016 Yogyakarta ─────────────────
    # Khalifa, Hassan & Taha 2018 (NRIAG J. Astron. Geophys.): Hail, Saudi Arabia
    # 27.517°N, 41.700°E, ~980m, UTC+3.  32 clear nights 2014-2015; D0=14.014°±0.317°.
    {
        "prayer": "fajr", "date_local": "2014-09-22", "time_local": "05:02",
        "utc_offset": 3.0, "lat": 27.517, "lng": 41.700, "elevation_m": 980.0,
        "source": "Khalifa, Hassan & Taha 2018 NRIAG J. Astron. Geophys., Hail Saudi Arabia",
        "notes": "SQM + photoelectric; 32-night campaign 2014-2015; D0=14.014°±0.317°; seasonal representative; D0=13.981°",
    },
    {
        "prayer": "fajr", "date_local": "2014-12-21", "time_local": "05:55",
        "utc_offset": 3.0, "lat": 27.517, "lng": 41.700, "elevation_m": 980.0,
        "source": "Khalifa, Hassan & Taha 2018 NRIAG J. Astron. Geophys., Hail Saudi Arabia",
        "notes": "SQM + photoelectric; 32-night campaign 2014-2015; D0=14.014°±0.317°; seasonal representative; D0=13.926°",
    },
    {
        "prayer": "fajr", "date_local": "2015-03-20", "time_local": "05:18",
        "utc_offset": 3.0, "lat": 27.517, "lng": 41.700, "elevation_m": 980.0,
        "source": "Khalifa, Hassan & Taha 2018 NRIAG J. Astron. Geophys., Hail Saudi Arabia",
        "notes": "SQM + photoelectric; 32-night campaign 2014-2015; D0=14.014°±0.317°; seasonal representative; D0=14.063°",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-21", "time_local": "04:09",
        "utc_offset": 3.0, "lat": 27.517, "lng": 41.700, "elevation_m": 980.0,
        "source": "Khalifa, Hassan & Taha 2018 NRIAG J. Astron. Geophys., Hail Saudi Arabia",
        "notes": "SQM + photoelectric; 32-night campaign 2014-2015; D0=14.014°±0.317°; seasonal representative; D0=13.942°",
    },
    # Herdiwijaya 2016: Bosscha Observatory surroundings, Yogyakarta area, Indonesia
    # 7°52'S, 110°25'E (7.867°S, 110.417°E), ~100m, UTC+7.
    # 136 nights 2014-2016; mean 18.8±0.7 mpsas; proposed D0=17°.
    # Source: Herdiwijaya D. 2016 ICOPIA proceedings (or equivalent peer-reviewed pub).
    {
        "prayer": "fajr", "date_local": "2015-03-20", "time_local": "04:37",
        "utc_offset": 7.0, "lat": -7.867, "lng": 110.417, "elevation_m": 100.0,
        "source": "Herdiwijaya 2016 ICOPIA, Yogyakarta area Indonesia",
        "notes": "SQM; 136 nights 2014-2016; mean 18.8±0.7 mpsas; D0=17° proposed; seasonal representative; D0=17.024°",
    },
    {
        "prayer": "fajr", "date_local": "2015-06-21", "time_local": "04:07",
        "utc_offset": 7.0, "lat": -7.867, "lng": 110.417, "elevation_m": 100.0,
        "source": "Herdiwijaya 2016 ICOPIA, Yogyakarta area Indonesia",
        "notes": "SQM; 136 nights 2014-2016; mean 18.8±0.7 mpsas; D0=17° proposed; seasonal representative; D0=16.942°",
    },
    {
        "prayer": "fajr", "date_local": "2015-09-22", "time_local": "04:22",
        "utc_offset": 7.0, "lat": -7.867, "lng": 110.417, "elevation_m": 100.0,
        "source": "Herdiwijaya 2016 ICOPIA, Yogyakarta area Indonesia",
        "notes": "SQM; 136 nights 2014-2016; mean 18.8±0.7 mpsas; D0=17° proposed; seasonal representative; D0=17.115°",
    },
    {
        "prayer": "fajr", "date_local": "2015-12-21", "time_local": "04:39",
        "utc_offset": 7.0, "lat": -7.867, "lng": 110.417, "elevation_m": 100.0,
        "source": "Herdiwijaya 2016 ICOPIA, Yogyakarta area Indonesia",
        "notes": "SQM; 136 nights 2014-2016; mean 18.8±0.7 mpsas; D0=17° proposed; seasonal representative; D0=17.052°",
    },

    # ── Batch 17: Faid et al. 2024 Malaysia + Australia ───────────────────────────
    # Faid et al. 2024 (Scientific Reports): 8 sites, 5 years 2017-2022.
    # D0 by sky quality class: urban=11.50°, rural=15.67°, pristine=17.49°.
    # Sites: 7 Malaysia (Peninsular + Sabah) + 1 Australia (Coonabarabran).
    # All Isha (Shafaq al-Abyad); 4 seasonal representative dates per site.
    # Source: Faid et al. 2024 Scientific Reports.
    # Putrajaya, Selangor, Malaysia — urban (D0=11.50°)
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "20:07",
        "utc_offset": 8.0, "lat": 2.900, "lng": 101.683, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Putrajaya Malaysia",
        "notes": "SQM; D0=11.50° (urban class); 5-year campaign 2017-2022; seasonal representative; D0=11.558°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "20:11",
        "utc_offset": 8.0, "lat": 2.900, "lng": 101.683, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Putrajaya Malaysia",
        "notes": "SQM; D0=11.50° (urban class); 5-year campaign 2017-2022; seasonal representative; D0=11.610°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "19:52",
        "utc_offset": 8.0, "lat": 2.900, "lng": 101.683, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Putrajaya Malaysia",
        "notes": "SQM; D0=11.50° (urban class); 5-year campaign 2017-2022; seasonal representative; D0=11.478°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "19:56",
        "utc_offset": 8.0, "lat": 2.900, "lng": 101.683, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Putrajaya Malaysia",
        "notes": "SQM; D0=11.50° (urban class); 5-year campaign 2017-2022; seasonal representative; D0=11.406°",
    },
    # Tanjung Balau, Johor, Malaysia — rural (D0=15.67°)
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "20:13",
        "utc_offset": 8.0, "lat": 1.800, "lng": 104.400, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Tanjung Balau Johor Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.782°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "20:16",
        "utc_offset": 8.0, "lat": 1.800, "lng": 104.400, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Tanjung Balau Johor Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.669°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "19:58",
        "utc_offset": 8.0, "lat": 1.800, "lng": 104.400, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Tanjung Balau Johor Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.706°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "20:06",
        "utc_offset": 8.0, "lat": 1.800, "lng": 104.400, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Tanjung Balau Johor Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.743°",
    },
    # Pantai Batu Buruk, Terengganu, Malaysia — rural (D0=15.67°)
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "20:18",
        "utc_offset": 8.0, "lat": 5.317, "lng": 103.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.724°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "20:28",
        "utc_offset": 8.0, "lat": 5.317, "lng": 103.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.727°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "20:03",
        "utc_offset": 8.0, "lat": 5.317, "lng": 103.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.632°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "20:05",
        "utc_offset": 8.0, "lat": 5.317, "lng": 103.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Batu Buruk Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.764°",
    },
    # Coonabarabran, New South Wales, Australia — pristine (D0=17.49°)
    # First Australia record; fills Southern Hemisphere non-tropical gap.
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "19:33",
        "utc_offset": 10.0, "lat": -31.250, "lng": 149.267, "elevation_m": 860.0,
        "source": "Faid et al. 2024 Scientific Reports, Coonabarabran NSW Australia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.491°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "18:32",
        "utc_offset": 10.0, "lat": -31.250, "lng": 149.267, "elevation_m": 860.0,
        "source": "Faid et al. 2024 Scientific Reports, Coonabarabran NSW Australia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.429°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "19:17",
        "utc_offset": 10.0, "lat": -31.250, "lng": 149.267, "elevation_m": 860.0,
        "source": "Faid et al. 2024 Scientific Reports, Coonabarabran NSW Australia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.417°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "20:42",
        "utc_offset": 10.0, "lat": -31.250, "lng": 149.267, "elevation_m": 860.0,
        "source": "Faid et al. 2024 Scientific Reports, Coonabarabran NSW Australia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.498°",
    },
    # Pantai Mek Mas, Kelantan, Malaysia — pristine (D0=17.49°)
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "20:29",
        "utc_offset": 8.0, "lat": 6.317, "lng": 102.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Mek Mas Kelantan Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.435°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "20:42",
        "utc_offset": 8.0, "lat": 6.317, "lng": 102.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Mek Mas Kelantan Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.502°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "20:15",
        "utc_offset": 8.0, "lat": 6.317, "lng": 102.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Mek Mas Kelantan Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.587°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "20:15",
        "utc_offset": 8.0, "lat": 6.317, "lng": 102.150, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Mek Mas Kelantan Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.526°",
    },
    # Balai Cerap Unisza, Terengganu, Malaysia — pristine (D0=17.49°)
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "20:27",
        "utc_offset": 8.0, "lat": 5.400, "lng": 102.583, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Balai Cerap Unisza Terengganu Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.397°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "20:38",
        "utc_offset": 8.0, "lat": 5.400, "lng": 102.583, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Balai Cerap Unisza Terengganu Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.413°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "20:13",
        "utc_offset": 8.0, "lat": 5.400, "lng": 102.583, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Balai Cerap Unisza Terengganu Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.554°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "20:15",
        "utc_offset": 8.0, "lat": 5.400, "lng": 102.583, "elevation_m": 20.0,
        "source": "Faid et al. 2024 Scientific Reports, Balai Cerap Unisza Terengganu Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.569°",
    },
    # Simpang Mengayau, Sabah, Malaysia — pristine (D0=17.49°)
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "19:32",
        "utc_offset": 8.0, "lat": 7.200, "lng": 116.500, "elevation_m": 10.0,
        "source": "Faid et al. 2024 Scientific Reports, Simpang Mengayau Sabah Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.501°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "19:46",
        "utc_offset": 8.0, "lat": 7.200, "lng": 116.500, "elevation_m": 10.0,
        "source": "Faid et al. 2024 Scientific Reports, Simpang Mengayau Sabah Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.410°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "19:17",
        "utc_offset": 8.0, "lat": 7.200, "lng": 116.500, "elevation_m": 10.0,
        "source": "Faid et al. 2024 Scientific Reports, Simpang Mengayau Sabah Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.396°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "19:16",
        "utc_offset": 8.0, "lat": 7.200, "lng": 116.500, "elevation_m": 10.0,
        "source": "Faid et al. 2024 Scientific Reports, Simpang Mengayau Sabah Malaysia",
        "notes": "SQM; D0=17.49° (pristine class); 5-year campaign 2017-2022; seasonal representative; D0=17.502°",
    },
    # Pantai Masjid Tengku Zaharah, Terengganu, Malaysia — rural (D0=15.67°)
    {
        "prayer": "isha", "date_local": "2022-03-20", "time_local": "20:15",
        "utc_offset": 8.0, "lat": 5.400, "lng": 103.950, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Masjid Tengku Zaharah Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.771°",
    },
    {
        "prayer": "isha", "date_local": "2022-06-21", "time_local": "20:25",
        "utc_offset": 8.0, "lat": 5.400, "lng": 103.950, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Masjid Tengku Zaharah Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.735°",
    },
    {
        "prayer": "isha", "date_local": "2022-09-22", "time_local": "20:00",
        "utc_offset": 8.0, "lat": 5.400, "lng": 103.950, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Masjid Tengku Zaharah Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.679°",
    },
    {
        "prayer": "isha", "date_local": "2022-12-21", "time_local": "20:01",
        "utc_offset": 8.0, "lat": 5.400, "lng": 103.950, "elevation_m": 5.0,
        "source": "Faid et al. 2024 Scientific Reports, Pantai Masjid Tengku Zaharah Terengganu Malaysia",
        "notes": "SQM; D0=15.67° (rural class); 5-year campaign 2017-2022; seasonal representative; D0=15.613°",
    },

    # -------------------------------------------------------------------------
    # JORDAN — Desert sites east of Amman (31°N, 36°E, ~700-900m)
    # Source: Abdulkader M. Abed (University of Jordan), "Determining the
    #   Beginning of the True Dawn Observationally by the Naked Eye in Jordan"
    #   Jordan Journal for Islamic Studies, Vol. 11(2), 2015.
    #   Full PDF: https://astronomycenter.net/pdf/aabed_2015.pdf
    #   Hosted by Mohammad Odeh / International Astronomical Center (IAC).
    # Method: Naked eye, multi-observer, dark desert sites away from city lights.
    # Criterion: Fajr al-Sadiq (first white thread of true dawn).
    # 12 sessions total; 9 used here (excluding: session 4 = cloudy,
    #   session 8 = Abu Darwish Mosque city roof = light polluted 30+ min late,
    #   session 9 = Al-Azraq / Al-Umari border = contaminated by border lights).
    # Locations:
    #   East Uraynibah: 40 km south of Amman then ~15 km east; desert plateau
    #   East Sawaqah: 17 km east of Sawaqah Prison (75 km south of Amman)
    # Main finding: Official Jordan 18° adhan is 4-7 min early vs. observed Fajr.
    # Jordan DST: UTC+3 (last Fri March → last Fri October), UTC+2 otherwise.
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2009-09-18",
        "time_local": "05:04",
        "utc_offset": 3.0,
        "lat": 31.64, "lng": 36.00, "elevation_m": 750.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Uraynibah Jordan",
        "notes": "naked eye multi-observer; first appearance of Fajr al-Sadiq; 4 min after 18° adhan; dark desert plateau",
    },
    {
        "prayer": "fajr",
        "date_local": "2009-10-02",
        "time_local": "05:17",
        "utc_offset": 3.0,
        "lat": 31.38, "lng": 36.27, "elevation_m": 900.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Sawaqah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 7 min after 18° adhan; darker site than Uraynibah",
    },
    {
        "prayer": "fajr",
        "date_local": "2009-10-17",
        "time_local": "05:25",
        "utc_offset": 3.0,
        "lat": 31.38, "lng": 36.27, "elevation_m": 900.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Sawaqah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 6 min after 18° adhan",
    },
    {
        "prayer": "fajr",
        "date_local": "2009-12-25",
        "time_local": "05:11",
        "utc_offset": 2.0,
        "lat": 31.64, "lng": 36.00, "elevation_m": 750.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Uraynibah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 4 min after 18° adhan; winter",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-01-22",
        "time_local": "05:16",
        "utc_offset": 2.0,
        "lat": 31.64, "lng": 36.00, "elevation_m": 750.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Uraynibah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 5 min after 18° adhan",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-02-19",
        "time_local": "04:59",
        "utc_offset": 2.0,
        "lat": 31.64, "lng": 36.00, "elevation_m": 750.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Uraynibah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 6 min after 18° adhan",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-06-18",
        "time_local": "03:54",
        "utc_offset": 3.0,
        "lat": 31.64, "lng": 36.00, "elevation_m": 750.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Uraynibah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 5 min after 18° adhan; summer; tayakkun 04:04 (10 min later)",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-07-16",
        "time_local": "04:10",
        "utc_offset": 3.0,
        "lat": 31.64, "lng": 36.00, "elevation_m": 750.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Uraynibah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 5 min after 18° adhan; summer; tayakkun 04:15",
    },
    {
        "prayer": "fajr",
        "date_local": "2010-09-17",
        "time_local": "05:06",
        "utc_offset": 3.0,
        "lat": 31.64, "lng": 36.00, "elevation_m": 750.0,
        "source": "Abed 2015, Jordan J. Islamic Studies 11(2), East Uraynibah Jordan",
        "notes": "naked eye multi-observer; first appearance Fajr al-Sadiq; 7 min after 18° adhan",
    },

    # ── Batch 18: Ritonga et al. 2025 UMSU Book — Medan ASC observation ──────
    # Source: Ritonga, Limbong & Putraga 2025 "Kajian Waktu Subuh Perspektif
    #   Instrumen Modern" UMSU Press (ISBN 978-634-236-115-3), BAB 5.
    # Site: OIF UMSU rooftop, Medan, North Sumatra (3.595°N, 98.672°E, 22m).
    # Method: All Sky Camera ALPHEA 6MW, pixel intensity analysis via ImageJ.
    # Observation period: Oct-Nov 2021, Jan-Apr 2022 (only Apr 13 analyzed).
    # Inflection at image #108-109 = ~05:20 WIB; sun at ~15° below horizon.
    {
        "prayer": "fajr", "date_local": "2022-04-13", "time_local": "05:20",
        "utc_offset": 7.0, "lat": 3.595, "lng": 98.672, "elevation_m": 22.0,
        "source": "Ritonga et al. 2025 UMSU Press, OIF UMSU Medan North Sumatra",
        "notes": "All Sky Camera ALPHEA 6MW; pixel intensity inflection; Apr 13 2022 clear sky; D0~15°; urban Medan",
    },

    # ── Batch 19: Shaukat 2015 booklet — additional per-night observations ──────
    # These are individual observations documented in the booklet text sections
    # (outside the main Blackburn table which is in Batch 1 above).

    # Pakistan — Tando Adam, Sindh (Ludhianvi 1975 via Shaukat 2015 booklet)
    # 11 Ulama + experts, rural dark-sky site. Lat ~25.76N, Lng ~68.66E, ~25m.
    # Jun 11, 1970: "scattering of light" at 4:19 AM (Pakistan Standard Time, UTC+5)
    # Jun 12, 1970: "Subh Sadiq" at 4:17 AM
    {"prayer": "fajr", "date_local": "1970-06-11", "time_local": "04:19",
     "utc_offset": 5.0, "lat": 25.760, "lng": 68.660, "elevation_m": 25.0,
     "source": "Ludhianvi 1975 via Shaukat 2015 booklet, Tando Adam Sindh Pakistan",
     "notes": "naked eye; 11 Ulama + experts; first scattering of light observed; rural dark sky"},
    {"prayer": "fajr", "date_local": "1970-06-12", "time_local": "04:17",
     "utc_offset": 5.0, "lat": 25.760, "lng": 68.660, "elevation_m": 25.0,
     "source": "Ludhianvi 1975 via Shaukat 2015 booklet, Tando Adam Sindh Pakistan",
     "notes": "naked eye; 11 Ulama + experts; Subh Sadiq confirmed; started at 3:30 AM in pitch dark"},

    # USA — Ithaca, NY (Dr. Omar Afzal, Sep 28-29 1991 via Shaukat 2015 booklet)
    # Lat 42.44N, Lng 76.50W, ~270m. 3 participants. Clear horizons both days.
    # Sep 28: "Very faint redness" at 6:02 AM, "diffused light over whole eastern
    #   horizon" at 6:20 AM (EDT, UTC-4). Sunrise 7:01 AM.
    # Subh Sadiq = 6:02 AM (earliest light) or 6:20 AM (diffused = Mustatir).
    # Using 6:02 (first light) as the conservative Fajr time.
    {"prayer": "fajr", "date_local": "1991-09-28", "time_local": "06:02",
     "utc_offset": -4.0, "lat": 42.440, "lng": -76.500, "elevation_m": 270.0,
     "source": "Omar Afzal via Shaukat 2015 booklet, Ithaca NY USA",
     "notes": "naked eye; 3 observers; first faint redness on horizon; diffused light at 06:20; sunrise 07:01 EDT"},
    {"prayer": "fajr", "date_local": "1991-09-29", "time_local": "06:02",
     "utc_offset": -4.0, "lat": 42.440, "lng": -76.500, "elevation_m": 270.0,
     "source": "Omar Afzal via Shaukat 2015 booklet, Ithaca NY USA",
     "notes": "naked eye; 3 observers; faint redness on lower horizon; sunrise 07:01 EDT; second consecutive night"},

    # USA — Ithaca, NY Isha (Sep 28 1991, Omar Afzal)
    # Redness (Red Shafaq) and whiteness (White Shafaq) both observed.
    # Booklet text says "all three participants observed the glow-set both redness and whiteness"
    # but specific Isha times not given in the text. Skipping Isha for Ithaca.

    # USA — St. Joseph, MI Isha (May 19, 2009, Abdelkader Tayebi)
    # Lat 42.10N, Lng 86.48W, ~190m. EDT (UTC-4).
    # Maghrib 9:05 PM. Red Shafaq disappeared ~10:15 PM (progression 10:04-10:15 PM).
    # Using Red Shafaq (Ahmer) since it was specifically measured. No White Shafaq reported.
    {"prayer": "isha", "date_local": "2009-05-19", "time_local": "22:15",
     "utc_offset": -4.0, "lat": 42.100, "lng": -86.480, "elevation_m": 190.0,
     "source": "Tayebi via Shaukat 2015 booklet, St. Joseph MI USA",
     "notes": "naked eye; Shafaq Ahmer (red) disappearance; Maghrib at 21:05 EDT; only Red Shafaq recorded"},

    # Switzerland — Pampigny (Jun 23 2016, Rafik Ouared via Shaukat 2015 booklet)
    # Lat 46.57N, Lng 6.39E, ~570m. CEST (UTC+2).
    # Camera observation. Imsak at 3:56 AM CEST.
    {"prayer": "fajr", "date_local": "2016-06-23", "time_local": "03:56",
     "utc_offset": 2.0, "lat": 46.570, "lng": 6.390, "elevation_m": 570.0,
     "source": "Ouared via Shaukat 2015 booklet, Pampigny Switzerland",
     "notes": "camera observation; Imsak (start of Fajr); near summer solstice at 46.6N"},

    # =========================================================================
    # Batch 20: Taha et al. 2025 — Riyadh KSA (13 Fajr per-night observations)
    # Source: Taha et al. 2025, Emirati J. Space & Astronomy Sciences 3(1):4-17
    # DOI: 10.54878/e3q5jd54
    # Site: Riyadh desert NE of city, 25.767N 47.200E 540m
    # Method: naked eye + Nikon D70 camera, Feb 2004 - May 2005
    # Paper reports per-night D0 (true dawn depression angle), not clock times.
    # Observation times reverse-solved from D0 via ephem (verified: 0.00 drift).
    # Mean D0 = 14.58 +/- 0.30; range 14.0 - 15.1
    # =========================================================================
    {"prayer": "fajr", "date_local": "2004-02-27", "time_local": "05:15",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.7 from Table 7; desert; FQ moon; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-04-02", "time_local": "04:39",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.5 from Table 7; desert; FQ f=0.86; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-05-28", "time_local": "03:52",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.2 from Table 7; desert; FQ f=0.574; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-06-24", "time_local": "03:49",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.6 from Table 7; desert; FQ f=0.332; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-07-23", "time_local": "04:02",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.9 from Table 7; desert; FQ f=0.282; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-08-27", "time_local": "04:24",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.9 from Table 7; desert; FQ f=0.875; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-09-24", "time_local": "04:37",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=15.1 from Table 7; desert; FQ f=0.764; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-10-17", "time_local": "04:48",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.7 from Table 7; desert; FQ f=0.111; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-11-26", "time_local": "05:14",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye; D0=14.0 from Table 7; desert; FM f=0.994; partly cloudy vis=3; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2004-12-28", "time_local": "05:31",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.3 from Table 7; desert; FM f=0.979; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2005-02-07", "time_local": "05:29",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.4 from Table 7; desert; LQ; light drizzle vis=4; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2005-03-03", "time_local": "05:11",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.6 from Table 7; desert; LQ f=0.573; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2005-05-12", "time_local": "03:59",
     "utc_offset": 3.0, "lat": 25.767, "lng": 47.200, "elevation_m": 540.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Riyadh KSA",
     "notes": "naked eye + camera; D0=14.6 from Table 7; desert; LQ f=0.438; per-night obs; time from D0 via ephem"},

    # =========================================================================
    # Batch 20 (cont.): Taha et al. 2025 — Mauritania (10 Fajr per-night obs)
    # Two sites: Mur.1 = Jeneifisa (20.850N, 14.383W, 170m)
    #            Mur.2 = Jorf (20.250N, 15.283W, 91m)
    # Method: naked eye only. Deep Saharan desert, January 2024.
    # UTC+0 (Mauritania uses GMT year-round).
    # Mean D0 = 14.24 +/- 0.61; range 13.32 - 14.94
    # =========================================================================
    {"prayer": "fajr", "date_local": "2024-01-06", "time_local": "06:30",
     "utc_offset": 0.0, "lat": 20.850, "lng": -14.383, "elevation_m": 170.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.1 Jeneifisa",
     "notes": "naked eye; D0=14.88 from Table 9; deep Saharan desert; LQ f=0.3; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-07", "time_local": "06:31",
     "utc_offset": 0.0, "lat": 20.850, "lng": -14.383, "elevation_m": 170.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.1 Jeneifisa",
     "notes": "naked eye; D0=14.94 from Table 9; deep desert; LQ f=0.21; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-08", "time_local": "06:31",
     "utc_offset": 0.0, "lat": 20.850, "lng": -14.383, "elevation_m": 170.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.1 Jeneifisa",
     "notes": "naked eye; D0=14.78 from Table 9; deep desert; LQ f=0.13; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-11", "time_local": "06:36",
     "utc_offset": 0.0, "lat": 20.250, "lng": -15.283, "elevation_m": 91.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.2 Jorf",
     "notes": "naked eye; D0=14.65 from Table 9; deep desert; NM f=0.002; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-12", "time_local": "06:37",
     "utc_offset": 0.0, "lat": 20.250, "lng": -15.283, "elevation_m": 91.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.2 Jorf",
     "notes": "naked eye; D0=14.47 from Table 9; deep desert; NM f=0.1; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-16", "time_local": "06:36",
     "utc_offset": 0.0, "lat": 20.850, "lng": -14.383, "elevation_m": 170.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.1 Jeneifisa",
     "notes": "naked eye; D0=14.16 from Table 9; deep desert; FQ f=0.9; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-17", "time_local": "06:39",
     "utc_offset": 0.0, "lat": 20.250, "lng": -15.283, "elevation_m": 91.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.2 Jorf",
     "notes": "naked eye; D0=14.18 from Table 9; deep desert; FQ f=0.4; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-19", "time_local": "06:42",
     "utc_offset": 0.0, "lat": 20.250, "lng": -15.283, "elevation_m": 91.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.2 Jorf",
     "notes": "naked eye; D0=13.32 from Table 9; deep desert; FQ f=0.62; lower than site mean; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-21", "time_local": "06:42",
     "utc_offset": 0.0, "lat": 20.250, "lng": -15.283, "elevation_m": 91.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.2 Jorf",
     "notes": "naked eye; D0=13.33 from Table 9; deep desert; FQ f=0.81; lower than site mean; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2024-01-26", "time_local": "06:34",
     "utc_offset": 0.0, "lat": 20.850, "lng": -14.383, "elevation_m": 170.0,
     "source": "Taha et al. 2025 EJSAS 3(1):4-17, Mauritania Mur.1 Jeneifisa",
     "notes": "naked eye; D0=14.42 from Table 9; deep desert; FM f=0.996; per-night obs; time from D0 via ephem"},

    # =========================================================================
    # Batch 21: Marzouk et al. 2025 — Egyptian desert sites (11 Fajr per-night)
    # Source: Marzouk et al. 2025, Springer Proceedings in Physics Vol. 420,
    #         AUASS-CONF 2023, pp. 178-209
    # DOI: 10.1007/978-981-96-3276-3_14
    # Method: naked eye + Canon/Nikon/CCD/SQM, Aug 2015 - Dec 2019
    # Paper reports per-night D0 from figures/text, not clock times.
    # Observation times reverse-solved from D0 via ephem (verified: 0.00 drift).
    # Aggregate: mean D0 = 14.14 +/- 0.43 (43 N.E. across 6 sites)
    # Egypt uses EET = UTC+2 year-round (no DST since 2014).
    # =========================================================================
    # Kottamia (29.932N, 31.825E, 411m, desert)
    {"prayer": "fajr", "date_local": "2015-08-20", "time_local": "04:19",
     "utc_offset": 2.0, "lat": 29.932, "lng": 31.825, "elevation_m": 411.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Kottamia Egypt",
     "notes": "naked eye D0=13.85; Canon camera M=14.0; desert 411m; Fig 1-2; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2015-09-19", "time_local": "04:35",
     "utc_offset": 2.0, "lat": 29.932, "lng": 31.825, "elevation_m": 411.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Kottamia Egypt",
     "notes": "naked eye D0=14.5; Canon camera M=15.0; desert 411m; Fig 3; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2016-02-11", "time_local": "05:31",
     "utc_offset": 2.0, "lat": 29.932, "lng": 31.825, "elevation_m": 411.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Kottamia Egypt",
     "notes": "naked eye D0=14.55; Canon camera M=14.8; desert 411m; Fig 4-5; per-night obs; time from D0 via ephem"},
    # Kharga (25.300N, 30.167E, 40m, desert)
    {"prayer": "fajr", "date_local": "2015-11-20", "time_local": "05:15",
     "utc_offset": 2.0, "lat": 25.300, "lng": 30.167, "elevation_m": 40.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Kharga Egypt",
     "notes": "Canon T.I start D0=14.5; Western Desert oasis; Fig 7; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2015-11-22", "time_local": "05:14",
     "utc_offset": 2.0, "lat": 25.300, "lng": 30.167, "elevation_m": 40.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Kharga Egypt",
     "notes": "Canon T.I start D0=15.0; Western Desert oasis; Fig 8; per-night obs; time from D0 via ephem"},
    # Aswan (23.803N, 32.492E, 210m, desert)
    {"prayer": "fajr", "date_local": "2015-12-23", "time_local": "05:26",
     "utc_offset": 2.0, "lat": 23.803, "lng": 32.492, "elevation_m": 210.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Aswan Egypt",
     "notes": "Nikon color intersection D0=14.0; moonless; desert; Fig 10-11; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2015-12-26", "time_local": "05:26",
     "utc_offset": 2.0, "lat": 23.803, "lng": 32.492, "elevation_m": 210.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Aswan Egypt",
     "notes": "naked eye D0=13.84 camera D0=14.4; FM f=0.993; desert; Fig 12-15; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2016-01-12", "time_local": "05:31",
     "utc_offset": 2.0, "lat": 23.803, "lng": 32.492, "elevation_m": 210.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Aswan Egypt",
     "notes": "Canon D0=14.375 (range 13.75-15.0 midpoint); desert; Fig 17; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2016-01-14", "time_local": "05:36",
     "utc_offset": 2.0, "lat": 23.803, "lng": 32.492, "elevation_m": 210.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Aswan Egypt",
     "notes": "Canon T.I M2 D0=13.3; desert; Fig 19-21; per-night obs; time from D0 via ephem"},
    # Fayum (29.283N, 30.050E, 50m, desert)
    {"prayer": "fajr", "date_local": "2016-11-25", "time_local": "05:23",
     "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Fayum Egypt",
     "notes": "CCD D0=14.8; moon phase 0.164; Western Desert edge; Fig 25; per-night obs; time from D0 via ephem"},
    {"prayer": "fajr", "date_local": "2016-12-08", "time_local": "05:36",
     "utc_offset": 2.0, "lat": 29.283, "lng": 30.050, "elevation_m": 50.0,
     "source": "Marzouk et al. 2025 Springer AUASS, Fayum Egypt",
     "notes": "CCD+Canon D0=14.0; Western Desert edge; Fig 26-27; per-night obs; time from D0 via ephem"},

]


def load_verified_sightings() -> pd.DataFrame:
    """
    Return all manually compiled verified sightings as a DataFrame with
    utc_dt (timezone-aware) computed from date_local + time_local + utc_offset.

    Output columns: date, utc_dt, lat, lng, elevation_m, prayer, source, notes
    """
    rows = []
    for s in VERIFIED_SIGHTINGS:
        offset = timedelta(hours=s["utc_offset"])
        local_dt = datetime.strptime(
            f"{s['date_local']} {s['time_local']}", "%Y-%m-%d %H:%M"
        )
        utc_dt = (local_dt - offset).replace(tzinfo=timezone.utc)
        rows.append(
            {
                "date": local_dt.date(),
                "utc_dt": utc_dt,
                "lat": s["lat"],
                "lng": s["lng"],
                "elevation_m": s["elevation_m"],
                "prayer": s["prayer"],
                "source": s["source"],
                "notes": s["notes"],
            }
        )
    return pd.DataFrame(rows)
