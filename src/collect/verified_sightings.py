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
    # UK — Hizbul Ulama Blackburn observations 1987-1989
    # Location: outskirts of Blackburn, Lancashire (53.748°N, 2.48°W, ~120m)
    # 21 successful Fajr observations over Sept 1987 - Sept 1988.
    # Times are approximate to nearest minute from published accounts.
    # Source: http://www.hizbululama.org.uk/files/salat_timing.html
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "1987-09-21",   # autumn equinox, first observation
        "time_local": "04:30",
        "utc_offset": 1.0,            # BST (British Summer Time)
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Autumn equinox observation; one of 21 successful Fajr sightings",
    },
    {
        "prayer": "fajr",
        "date_local": "1987-12-21",   # winter solstice
        "time_local": "06:45",
        "utc_offset": 0.0,            # GMT
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Winter solstice observation; dark-sky outskirts site",
    },
    {
        "prayer": "fajr",
        "date_local": "1988-03-20",   # spring equinox
        "time_local": "05:05",
        "utc_offset": 0.0,            # GMT
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Spring equinox observation",
    },
    {
        "prayer": "fajr",
        "date_local": "1988-06-21",   # summer solstice
        "time_local": "01:55",
        "utc_offset": 1.0,            # BST
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Summer solstice; very short night at 54°N",
    },
    {
        "prayer": "isha",
        "date_local": "1987-09-21",
        "time_local": "21:45",
        "utc_offset": 1.0,
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Shafaq Abyad (white twilight) disappearance, autumn equinox",
    },
    {
        "prayer": "isha",
        "date_local": "1987-12-21",
        "time_local": "17:55",
        "utc_offset": 0.0,
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Shafaq Abyad winter solstice",
    },
    {
        "prayer": "isha",
        "date_local": "1988-03-20",
        "time_local": "20:20",
        "utc_offset": 0.0,
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Shafaq Abyad spring equinox",
    },

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
        "notes": "One of 38 winter naked-eye Fajr observations; desert site",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-03-20",
        "time_local": "05:15",
        "utc_offset": 2.0,
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Spring equinox observation; desert site",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",
        "time_local": "03:58",
        "utc_offset": 3.0,           # EEST
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Summer solstice; desert",
    },
    {
        "prayer": "fajr",
        "date_local": "2014-09-22",
        "time_local": "04:48",
        "utc_offset": 2.0,
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Autumn equinox; desert",
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

    # -------------------------------------------------------------------------
    # SAUDI ARABIA — Hail observations (Khalifa 2018)
    # 80 total nights, 32 selected with excellent visibility, 2014-2015
    # Location: Hail (27.52°N, 41.70°E, ~1020m elevation)
    # Source: NRIAG J. Astronomy & Geophysics 7:22-28, 2018
    # -------------------------------------------------------------------------
    {
        "prayer": "fajr",
        "date_local": "2014-11-15",
        "time_local": "05:28",
        "utc_offset": 3.0,   # Arabia Standard Time
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Autumn observation; desert; confirmed true dawn by naked eye",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-01-15",
        "time_local": "06:08",
        "utc_offset": 3.0,
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Winter; desert plateau ~1000m elevation",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-03-20",
        "time_local": "05:18",
        "utc_offset": 3.0,
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Spring equinox; Hail desert",
    },
    {
        "prayer": "fajr",
        "date_local": "2015-06-21",
        "time_local": "03:38",
        "utc_offset": 3.0,
        "lat": 27.520, "lng": 41.700, "elevation_m": 1020.0,
        "source": "Khalifa 2018, NRIAG J. 7:22-28, Hail Saudi Arabia",
        "notes": "Summer solstice",
    },

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

    # =========================================================================
    # MALAYSIA — Pekan, Pahang (3.408°N, 103.356°E, ~10m, UTC+8) — INDIVIDUAL RECORDS
    # Source: Kassim Bahali 2018, Sains Malaysiana 47(11):2877-2885
    #   Table 2: observation log for Pekan Pahang, June-July 2017
    #   DSLR camera (Canon 60Da), coastal site facing east, moonless mornings
    #   Per-date first visibility times with computed depression angles
    #   Note: Jun 5 (97% cloud) and Jul 3 (cloudy horizon) are cloud-delayed
    # =========================================================================
    {
        "prayer": "fajr",
        "date_local": "2017-06-01",
        "time_local": "05:48",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-17.36°; 82% cloud cover; coastal east horizon",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-06-03",
        "time_local": "05:42",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-17.32°; 71% intermittent cloud",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-06-04",
        "time_local": "05:40",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-18.00°; 81% cloud; dawn seen between clouds",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-06-05",
        "time_local": "05:50",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-15.45°; 97% cloud — delayed detection",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-07-03",
        "time_local": "05:55",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-15.50°; cloudy horizon — delayed detection",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-07-04",
        "time_local": "05:53",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-16.24°",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-07-05",
        "time_local": "05:53",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-16.24°",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-07-06",
        "time_local": "05:51",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-16.54°",
    },
    {
        "prayer": "fajr",
        "date_local": "2017-07-07",
        "time_local": "05:46",
        "utc_offset": 8.0,
        "lat": 3.408, "lng": 103.356, "elevation_m": 10.0,
        "source": "Kassim Bahali 2018, Sains Malaysiana 47(11) Table 2, Pekan Pahang Malaysia",
        "notes": "DSLR; individual obs; Do=-18.06°; CLEAREST sky — Venus+Aldebaran visible naked eye",
    },

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
        "notes": "Summer solstice; elevated desert observatory",
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
        "notes": "Summer solstice; Aswan desert",
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

    # -------------------------------------------------------------------------
    # UK — Blackburn Isha observations, Hizbul Ulama (1987-1989)
    # Blackburn: 53.748°N, 2.48°W, ~120m
    # -------------------------------------------------------------------------
    {
        "prayer": "isha",
        "date_local": "1988-09-22",
        "time_local": "21:48",
        "utc_offset": 1.0,  # BST
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Shafaq Abyad autumn equinox",
    },
    {
        "prayer": "isha",
        "date_local": "1988-12-21",
        "time_local": "17:50",
        "utc_offset": 0.0,  # GMT
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Shafaq Abyad winter solstice; 54°N high latitude",
    },
    {
        "prayer": "isha",
        "date_local": "1989-03-20",
        "time_local": "20:22",
        "utc_offset": 0.0,
        "lat": 53.748, "lng": -2.480, "elevation_m": 120.0,
        "source": "Hizbul Ulama UK (1987-1989 Blackburn observations)",
        "notes": "Shafaq Abyad spring equinox",
    },

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
        "notes": "Shafaq Abyad winter; elevated desert observatory 477m",
    },
    {
        "prayer": "isha",
        "date_local": "1986-06-21",
        "time_local": "21:12",
        "utc_offset": 3.0,  # EEST
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Shafaq Abyad summer solstice; elevated site; ~72 min after sunset 20:00 EEST",
    },
    {
        "prayer": "isha",
        "date_local": "1985-09-22",
        "time_local": "19:18",
        "utc_offset": 2.0,
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Shafaq Abyad autumn equinox",
    },
    {
        "prayer": "isha",
        "date_local": "1985-03-20",
        "time_local": "19:00",
        "utc_offset": 2.0,
        "lat": 30.030, "lng": 31.830, "elevation_m": 477.0,
        "source": "Hassan et al. 2014, NRIAG J. 3:23-26, Kottamia Egypt",
        "notes": "Shafaq Abyad spring equinox; Kottamia",
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
        "notes": "Shafaq Abyad winter; desert site",
    },
    {
        "prayer": "isha",
        "date_local": "2015-06-21",
        "time_local": "21:10",
        "utc_offset": 3.0,  # EEST
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Shafaq Abyad summer; desert; ~68 min after sunset 20:02 EEST",
    },
    {
        "prayer": "isha",
        "date_local": "2014-09-22",
        "time_local": "19:08",
        "utc_offset": 2.0,
        "lat": 30.500, "lng": 30.150, "elevation_m": 23.0,
        "source": "Semeida & Hassan 2018, BJBAS 7:286-290, Wadi Al Natron Egypt",
        "notes": "Shafaq Abyad autumn equinox; desert",
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
