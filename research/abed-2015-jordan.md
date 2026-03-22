# Determining the Beginning of True Dawn (Al-Fajr Al-Sadek) Observationally by the Naked Eye in Jordan

**Authors:** Prof. Abdulkader M. Abed
**Year:** 2015
**Journal:** Jordan Journal for Islamic Studies, v. 11(2)
**URL:** https://astronomycenter.net/pdf/aabed_2015.pdf
**Sites studied:** 4 sites in Jordan: East Ariniyba (40km S Amman), East Sijn Sawaqa (75km S Amman), JAS camp near Azraq, Ashraqiyya Mosque (central Amman)
**Observation method:** Naked eye, group observation (Jordanian Astronomical Society members and scholars)
**Date range:** 28 Ramadan 1430 to 8 Shawwal 1431 (September 2009 to September 2010)
**Records:** 12 observation sessions, 10 usable for data extraction
**Mean angle (Fajr):** Approximately 16-17 degrees (fajr seen 4-5 minutes after 18-degree adhan)

## Location Details

- East Ariniyba: ~31.63N, 36.0E, ~750m, 40km south of Amman on desert highway, dark site with some village lights to the west
- East Sijn Sawaqa: ~31.37N, 36.3E, ~700m, 75km south of Amman, very dark desert site, no villages east
- JAS camp near Azraq: ~31.8N, 36.8E, ~530m, near Saudi border, affected by border checkpoint lights
- Ashraqiyya Mosque, central Amman: ~31.95N, 35.94E, ~800m, urban, heavy light pollution

## Summary

A one-year observational program by the Jordanian Astronomical Society (JAS) with 12 successful sessions across 4 desert sites in Jordan (plus one urban comparison). Each session involved a group of astronomers and Islamic scholars arriving 45-60 minutes before the official adhan.

Key methodology: observers noted (a) zodiacal light (false dawn) appearance and photographed it, (b) the exact time of first true fajr light visibility, (c) the time when all observers agreed on fajr visibility (tayakkun/confirmation). Digital photography with 30-second cadence documented the progression.

Key finding: True fajr was seen 4-5 minutes after the beginning of the official Amman adhan (which is at 18 degrees solar depression). In one session by the best observers, it was seen at the exact time of adhan start. The paper recommends keeping the current 18-degree standard for Jordan.

The urban session (Amman mosque rooftop) showed fajr was invisible until 30+ minutes after adhan, confirming that urban light pollution makes naked-eye dawn observation impossible.

## Data Extracted

10 sessions extracted to `data/raw/raw_sightings/abed_2015_jordan.csv`:
- Excluded session 8 (Amman urban, light pollution prevented observation)
- Excluded session 9 (Azraq, border checkpoint light pollution heavily affected results, 13-min delay)
- Session 4 included but noted as cloudy
- Times recorded are the "first fajr appearance" (bada' dhuhur al-fajr), not the "confirmation" time
- UTC offset: +3 (Jordan uses +3 in summer DST, +2 in winter standard; need verification per date)

## UTC Offset Note

Jordan switched between EET (+2) and EEST (+3):
- 2009: DST ended Oct 30 (sessions 1-4 are in +3 before Oct 30, session 5 Dec is +2)
- 2010: DST started March 26 (sessions 6-7 are +2, sessions 8-12 are +3 after March 26)

The CSV currently uses +3 for all. This needs correction for winter sessions (5, 6, 7).
