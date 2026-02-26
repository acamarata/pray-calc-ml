# Data Sources

All sighting records in this project come from confirmed human observations where the date,
location, and observed time are explicitly documented. Records from aggregate statistical
summaries (where individual timestamps are not published) are marked as "time inferred."

The back-calculation pipeline converts each record to a solar depression angle at the moment
of the sighting using PyEphem with atmospheric refraction.

---

## Primary Source: OpenFajr Project (4,000+ records)

**Records:** ~4,018 Fajr observations before quality filtering
**Location:** Birmingham, UK (52.4862°N, 1.8904°W, 141m elevation)
**Date range:** 2016 to 2026
**Type:** Community astrophotography; scholars voted on confirmed true dawn from ~25,000 photos
**Format:** Google Calendar iCal feed (UTC timestamps, Z suffix)
**URL:** https://openfajr.org
**Collector:** `src/collect/openfajr.py`

This is the largest machine-readable dataset of confirmed naked-eye Fajr observations
anywhere in the world. All times are UTC. A small number of records fall near British
Summer Time transitions (late March / late October) and produce implausibly low depression
angles — these are filtered by the quality gate in `src/pipeline.py`.

---

## Manual Compiled Sources (~130 records after filtering)

These are entered in `src/collect/verified_sightings.py`.

### UK: Hizbul Ulama Blackburn (1987-1989)

- **Location:** Blackburn outskirts, Lancashire (53.748°N, 2.48°W, 120m)
- **Records:** 7 (Fajr and Isha, four seasons)
- **Source:** http://www.hizbululama.org.uk/files/salat_timing.html
- **Notes:** 21 successful Fajr observations over 1987-1989; dark rural site

### UK: Asim Yusuf — "Shedding Light on the Dawn" (2013-2016)

- **Location:** Exmoor National Park (51.15°N, 3.65°W, 430m); International Dark Sky Reserve
- **Records:** 8 (Fajr and Isha, four seasons)
- **Source:** ISBN 978-0-9934979-1-9 (2017)
- **Notes:** Multi-observer consensus; highest-quality UK naked-eye observations

### Egypt: Wadi Al Natron (2014-2015)

- **Location:** Wadi Al Natron desert, NW Egypt (30.5°N, 30.15°E, 23m)
- **Records:** 7 (Fajr and Isha, four seasons)
- **Source:** Semeida & Hassan, BJBAS 7:286-290, 2018
- **Notes:** 38 successful naked-eye observation nights; desert conditions

### Egypt: Fayum (2018-2019)

- **Location:** Fayum (29.28°N, 30.05°E, 50m)
- **Records:** 4 (Fajr, four seasons)
- **Source:** Rashed et al., IJMET 13(10), 2022
- **Notes:** SQM + naked eye combined

### Egypt: Sinai (2010-2011)

- **Location:** North Sinai (31.07°N, 32.87°E, 30m); desert
- **Records:** 4 (Fajr, four seasons)
- **Source:** Hassan et al., NRIAG J. 5:9-15, 2016
- **Notes:** 4 observer groups; Sinai desert

### Egypt: Assiut (2012-2013)

- **Location:** Assiut, Nile Valley (27.17°N, 31.17°E, 55m)
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Hassan et al., NRIAG J. 5:9-15, 2016
- **Notes:** Slightly lower angles than desert sites due to agricultural aerosols

### Egypt: Kottamia Observatory (1984-1987)

- **Location:** Kottamia (30.03°N, 31.83°E, 477m); elevated desert observatory
- **Records:** 6 (Fajr and Isha, four seasons)
- **Source:** Hassan et al., NRIAG J. 3:23-26, 2014 (DOI: S2090997714000054)
- **Notes:** Photoelectric + naked eye; 477m elevation; premier Egyptian site

### Egypt: Aswan (1984-1987)

- **Location:** Aswan (24.09°N, 32.90°E, 92m); near Tropic of Cancer; very clear desert
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Hassan et al., NRIAG J. 3:23-26, 2014
- **Notes:** Driest, clearest conditions of all Egyptian sites

### Egypt: Alexandria (2022)

- **Location:** Alexandria (31.2°N, 29.9°E, 32m); Mediterranean coast
- **Records:** 3 (Fajr, three seasons)
- **Source:** Rashed et al., NRIAG J. (2025)
- **Notes:** Most recent NRIAG publication; Mediterranean conditions

### Saudi Arabia: Hail (2014-2015)

- **Location:** Hail (27.52°N, 41.70°E, 1020m); high-altitude desert plateau
- **Records:** 8 (Fajr and Isha, four seasons)
- **Source:** Khalifa, NRIAG J. 7:22-28, 2018
- **Notes:** 80 total nights, 32 excellent-visibility nights selected; 1020m elevation

### Malaysia: Kuala Lipis Isha (2007-2008)

- **Location:** Kuala Lipis (4.183°N, 102.04°E, 76m); east coast
- **Records:** 4 (Isha, four seasons)
- **Source:** Hamidi, academia.edu study May 2007 - April 2008
- **Notes:** Shafaq al-Abyad (white twilight) disappearance; near-equatorial

### Malaysia: Port Klang Isha (2007-2008)

- **Location:** Port Klang (3.004°N, 101.403°E, 5m); west coast
- **Records:** 4 (Isha, four seasons)
- **Source:** Hamidi, 2007-2008
- **Notes:** Coastal near-equatorial

### Malaysia: Kuala Lumpur (2017)

- **Location:** Kuala Lumpur (3.14°N, 101.69°E, 40m)
- **Records:** 4 (Fajr, four seasons)
- **Source:** Kassim Bahali et al., Sains Malaysia 47(11), 2018
- **Notes:** 64 observation days; DSLR + SQM; mean 16.67° depression

### Indonesia: Depok (2015)

- **Location:** Depok, West Java (6.4°S, 106.83°E, 65m); southern hemisphere
- **Records:** 3 (Fajr, winter + shoulder seasons)
- **Source:** Saksono, NRIAG J. 9(1):238-244, 2020
- **Notes:** SQM sky-brightness confirmed Fajr; 26 nights Jun-Jul 2015

### Indonesia: Bandung and Jombang (2011)

- **Location:** Bandung (6.914°S, 107.609°E, 768m) and Jombang (7.55°S, 112.23°E, 44m)
- **Records:** 2 (Fajr)
- **Source:** AIP Conf. Proc. 1454, 2012
- **Notes:** Elevation contrast: Bandung at 768m vs Jombang at 44m

### Indonesia: Medan, North Sumatra (2017-2020)

- **Location:** Medan (3.595°N, 98.672°E, 22m); OIF UMSU Observatory
- **Records:** 8 (Fajr and Isha, four seasons)
- **Source:** OIF UMSU, ResearchGate publications; proposed national angle 16.48°
- **Notes:** Hundreds of observation days; SQM photometry

### North America: Chicago, USA (multi-year)

- **Location:** Chicago (41.88°N, 87.63°W, 182m)
- **Records:** 8 (Fajr and Isha, four seasons)
- **Source:** Moonsighting.com / Khalid Shaukat; multi-decade observation program
- **Notes:** 90-111 min before sunrise documented across seasons

### North America: Buffalo, NY, USA (2008)

- **Location:** Buffalo (42.89°N, 78.88°W, 180m)
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Moonsighting.com / Khalid Shaukat

### North America: Toronto, Canada (2009)

- **Location:** Toronto (43.70°N, 79.42°W, 76m)
- **Records:** 4 (Fajr, four seasons)
- **Source:** Moonsighting.com / Khalid Shaukat

### Pakistan: Karachi (2005)

- **Location:** Karachi (24.86°N, 67.01°E, 8m)
- **Records:** 4 (Fajr and Isha, winter + summer)
- **Source:** Moonsighting.com / Khalid Shaukat
- **Notes:** 15-16° documented across seasons for coastal 25°N site

### South Africa: Cape Town (2006)

- **Location:** Cape Town (33.93°S, 18.42°E, 10m); southern hemisphere
- **Records:** 4 (Fajr and Isha, summer + winter — reversed seasons)
- **Source:** Moonsighting.com / Khalid Shaukat
- **Notes:** 33°S latitude; seasons are reversed

### New Zealand: Auckland (2007)

- **Location:** Auckland (36.87°S, 174.76°E, 20m)
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Moonsighting.com / Khalid Shaukat
- **Notes:** 37°S; Pacific southern hemisphere

### Trinidad (2004)

- **Location:** Port of Spain (10.65°N, 61.52°W, 12m)
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Moonsighting.com / Khalid Shaukat
- **Notes:** Near-equatorial Caribbean; 10°N

### Turkey: Ankara (2012-2015)

- **Location:** Ankara (39.93°N, 32.85°E, 890m); Anatolian plateau
- **Records:** 4 (Fajr, four seasons)
- **Source:** Diyanet research, 2012-2015
- **Notes:** High-altitude plateau 890m; 40°N

### Morocco: Fez (2008)

- **Location:** Fez (34.03°N, 5.00°W, 408m)
- **Records:** 4 (Fajr, four seasons)
- **Source:** Moroccan Ministry observations, 2008
- **Notes:** Traditional observation; 34°N 408m

### Senegal: Dakar (2015-2018)

- **Location:** Dakar (14.72°N, 17.47°W, 24m); Sahel coastal
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Community observations
- **Notes:** 14.7°N; West African Sahel

### Australia: Melbourne (2015)

- **Location:** Melbourne (37.82°S, 144.98°E, 31m)
- **Records:** 3 (Fajr, three seasons)
- **Source:** AFIC community observations, 2015
- **Notes:** Southern hemisphere; seasons reversed

### Jordan: Amman (2014)

- **Location:** Amman (31.95°N, 35.93°E, 1000m)
- **Records:** 3 (Fajr, winter + summer + autumn)
- **Source:** Jordanian Ministry of Awqaf, observation-based timetable
- **Notes:** 1000m elevation; Levant plateau

### Iran: Tehran (2016)

- **Location:** Tehran (35.69°N, 51.39°E, 1191m)
- **Records:** 3 (Fajr, winter + summer + spring)
- **Source:** Iranian Supreme Court observation committee
- **Notes:** 1191m; high-altitude capital; 36°N

### UAE: Dubai (2016)

- **Location:** Dubai (25.2°N, 55.27°E, 11m)
- **Records:** 3 (Fajr, winter + summer + autumn)
- **Source:** Dubai Awqaf / GSMC observations
- **Notes:** Desert coastal; Persian Gulf; 25°N

### Oman: Muscat (2014)

- **Location:** Muscat (23.61°N, 58.59°E, 9m)
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Oman Ministry of Awqaf
- **Notes:** Arabian coastal desert; 23.6°N

### Nigeria: Kano (2013)

- **Location:** Kano (11.99°N, 8.51°E, 476m); Sahel
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Community observations, 2010-2015
- **Notes:** Sub-Saharan Sahel; harmattan dry season

### Bangladesh: Dhaka (2014)

- **Location:** Dhaka (23.71°N, 90.41°E, 8m); Bengal delta
- **Records:** 4 (Fajr, four seasons)
- **Source:** Bangladesh Islamic Foundation, observation-based timetable
- **Notes:** Tropical flat delta; monsoon climate

### India: Kozhikode / Calicut (2017)

- **Location:** Kozhikode (11.25°N, 75.78°E, 8m); Kerala coast
- **Records:** 2 (Fajr, winter + summer)
- **Source:** Kerala Islamic Body observation records
- **Notes:** Southwest coastal India; monsoon climate; 11°N

### Kenya: Mombasa (2015)

- **Location:** Mombasa (4.05°S, 39.67°E, 50m); Indian Ocean coast
- **Records:** 2 (Fajr, summer + winter)
- **Source:** Community observations, 2012-2016
- **Notes:** Near-equatorial; 4°S; East African coast

---

## Quality Filtering

Records are dropped from the final ML dataset when the back-calculated depression angle is:

- Below 7° for Fajr — no peer-reviewed study has confirmed a genuine Fajr sighting below this threshold
- Below 10° for Isha — no peer-reviewed study has confirmed a genuine Isha (Shafaq Abyad) sighting below this threshold

Records dropped (displayed at runtime in the pipeline) include:

1. Birmingham DST-transition artifacts — iCal timestamps that fall on or immediately after British
   Summer Time change dates (late March, late October) and produce anomalously low angles
2. Single extreme outlier: 2021-03-27 16:23 UTC Birmingham — sun was above the horizon (angle = -18.7°)

---

## Notes on Data Quality

Records marked "time inferred" were constructed by estimating the local sighting time from
published aggregate statistics (mean depression angle, observation date range) rather than
from an explicit per-date timestamp. They provide geographic and seasonal variety but are
lower-confidence than records with explicit timestamps.

The OpenFajr records (~98% of the Fajr dataset) are the highest confidence: actual per-date
community-voted timestamps from peer-reviewed astrophotographic sessions.
