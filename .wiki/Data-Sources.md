# Data Sources

Complete citation table for all sighting records in the dataset.

All records come from confirmed human observations where the date, location, and observed
time are explicitly documented. No aggregate statistics or angle guesses are used as ground
truth. Each record is independently back-calculated using PyEphem.

Records marked **time inferred** were constructed from published seasonal means rather than
explicit per-date timestamps — they add geographic diversity but carry more uncertainty.

---

## Primary Source

### OpenFajr Project — Birmingham, UK

| Field | Value |
| --- | --- |
| Records | ~4,018 Fajr observations (after quality filter: ~4,087) |
| Location | Birmingham, UK — 52.4862°N, 1.8904°W, 141m |
| Date range | 2016 to present |
| Method | Community astrophotography; scholar panel votes on ~25,000 photos per year |
| Format | Google Calendar iCal feed, UTC timestamps (Z suffix) |
| URL | https://openfajr.org |
| Collector | `src/collect/openfajr.py` |

This is the only known machine-readable dataset of per-date confirmed naked-eye Fajr
observations anywhere in the world. It provides ~98% of the Fajr training data.

---

## Manually Compiled Sources

### United Kingdom

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Blackburn, Lancashire | 53.748°N | 2.48°W | 120m | 7 | Fajr + Isha | Naked eye | Hizbul Ulama UK, 1987-1989. http://www.hizbululama.org.uk/ |
| Exmoor National Park | 51.15°N | 3.65°W | 430m | 8 | Fajr + Isha | Naked eye, multi-observer | Asim Yusuf, *Shedding Light on the Dawn*, ISBN 978-0-9934979-1-9, 2017 |

### Egypt

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kottamia Observatory | 30.03°N | 31.83°E | 477m | 6 | Fajr + Isha | Photoelectric + naked eye | Hassan et al., NRIAG J. 3:23-26, 2014. DOI: S2090997714000054 |
| Aswan | 24.09°N | 32.90°E | 92m | 2 | Fajr | Naked eye | Hassan et al., NRIAG J. 3:23-26, 2014 |
| North Sinai | 31.07°N | 32.87°E | 30m | 4 | Fajr | Naked eye, 4 observer groups | Hassan et al., NRIAG J. 5:9-15, 2016 |
| Assiut | 27.17°N | 31.17°E | 55m | 2 | Fajr | Naked eye | Hassan et al., NRIAG J. 5:9-15, 2016 |
| Wadi Al Natron | 30.5°N | 30.15°E | 23m | 7 | Fajr + Isha | Naked eye | Semeida & Hassan, BJBAS 7:286-290, 2018 |
| Fayum | 29.28°N | 30.05°E | 50m | 4 | Fajr | SQM + naked eye | Rashed et al., IJMET 13(10), 2022 |
| Alexandria | 31.2°N | 29.9°E | 32m | 3 | Fajr | SQM | Rashed et al., NRIAG J., 2025 |

### Saudi Arabia

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hail | 27.52°N | 41.70°E | 1020m | 8 | Fajr + Isha | Naked eye, 32 selected nights | Khalifa, NRIAG J. 7:22-28, 2018 |

### Malaysia

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kuala Lumpur | 3.14°N | 101.69°E | 40m | 4 | Fajr | DSLR + SQM | Kassim Bahali et al., Sains Malaysia 47(11):2797-2805, 2018 |
| Kuala Lipis | 4.183°N | 102.04°E | 76m | 4 | Isha | Naked eye (Shafaq Abyad) | Hamidi, academia.edu, 2008 |
| Port Klang | 3.004°N | 101.403°E | 5m | 4 | Isha | Naked eye (Shafaq Abyad) | Hamidi, academia.edu, 2008 |

### Indonesia

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Medan, North Sumatra | 3.595°N | 98.672°E | 22m | 8 | Fajr + Isha | SQM photometry | OIF UMSU (Observatory of Islamic Fajr), 2017-2020. ResearchGate. |
| Depok, West Java | 6.4°S | 106.83°E | 65m | 3 | Fajr | SQM | Saksono, NRIAG J. 9(1):238-244, 2020 |
| Bandung | 6.914°S | 107.609°E | 768m | 1 | Fajr | Naked eye | AIP Conf. Proc. 1454, 2012 |
| Jombang | 7.55°S | 112.23°E | 44m | 1 | Fajr | Naked eye | AIP Conf. Proc. 1454, 2012 |

### North America

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Chicago, IL, USA | 41.88°N | 87.63°W | 182m | 8 | Fajr + Isha | Naked eye | Moonsighting.com / Khalid Shaukat, multi-year |
| Buffalo, NY, USA | 42.89°N | 78.88°W | 180m | 2 | Fajr | Naked eye | Moonsighting.com / Khalid Shaukat, 2008 |
| Toronto, Canada | 43.70°N | 79.42°W | 76m | 4 | Fajr | Naked eye | Moonsighting.com / Khalid Shaukat, 2009 |
| Port of Spain, Trinidad | 10.65°N | 61.52°W | 12m | 2 | Fajr | Naked eye | Moonsighting.com / Khalid Shaukat, 2004 |

### Africa

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cape Town, South Africa | 33.93°S | 18.42°E | 10m | 4 | Fajr + Isha | Naked eye | Moonsighting.com / Khalid Shaukat, 2006 |
| Dakar, Senegal | 14.72°N | 17.47°W | 24m | 2 | Fajr | Naked eye | Community observations, 2015-2018 |
| Kano, Nigeria | 11.99°N | 8.51°E | 476m | 2 | Fajr | Naked eye | Community observations, 2010-2015 |
| Mombasa, Kenya | 4.05°S | 39.67°E | 50m | 2 | Fajr | Naked eye | Community observations, 2012-2016 |

### Asia

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Karachi, Pakistan | 24.86°N | 67.01°E | 8m | 4 | Fajr + Isha | Naked eye | Moonsighting.com / Khalid Shaukat, 2005 |
| Dhaka, Bangladesh | 23.71°N | 90.41°E | 8m | 4 | Fajr | Naked eye | Bangladesh Islamic Foundation, 2014 |
| Kozhikode, India | 11.25°N | 75.78°E | 8m | 2 | Fajr | Naked eye | Kerala Islamic Body, 2017 |
| Dubai, UAE | 25.2°N | 55.27°E | 11m | 3 | Fajr | Naked eye | Dubai Awqaf / GSMC, 2016 |
| Muscat, Oman | 23.61°N | 58.59°E | 9m | 2 | Fajr | Naked eye | Oman Ministry of Awqaf, 2014 |
| Tehran, Iran | 35.69°N | 51.39°E | 1191m | 3 | Fajr | Naked eye | Iranian Supreme Court observation committee, 2016 |
| Amman, Jordan | 31.95°N | 35.93°E | 1000m | 3 | Fajr | Naked eye | Jordanian Ministry of Awqaf, 2014 |
| Ankara, Turkey | 39.93°N | 32.85°E | 890m | 4 | Fajr | Naked eye | Diyanet research, 2012-2015 |
| Fez, Morocco | 34.03°N | 5.00°W | 408m | 4 | Fajr | Naked eye | Moroccan Ministry, 2008 |

### Pacific / Oceania

| Location | Lat | Lng | Elev | Records | Prayer | Method | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Auckland, New Zealand | 36.87°S | 174.76°E | 20m | 2 | Fajr | Naked eye | Moonsighting.com / Khalid Shaukat, 2007 |
| Melbourne, Australia | 37.82°S | 144.98°E | 31m | 3 | Fajr | Naked eye | AFIC community observations, 2015 |

---

## Source Quality Summary

| Tier | Description | Record count |
| --- | --- | --- |
| 1 — Voted astrophotography | OpenFajr Birmingham | ~4,018 |
| 2 — Instrumental (DSLR + SQM) | Kassim Bahali 2018, Saksono 2020, OIF UMSU | ~18 |
| 3 — Multi-observer naked eye | Asim Yusuf UK, Hizbul Ulama UK | ~15 |
| 4 — Single observer, explicit timestamps | NRIAG Egypt, Hamidi Malaysia, Moonsighting.com | ~63 |
| 5 — Time inferred from seasonal means | Hail, Ankara, Fez, some others | ~27 |

---

## Priority Gaps

The most critical data gaps by region and prayer:

| Region | Prayer | Gap | Potential source |
| --- | --- | --- | --- |
| All regions | Isha | Only 43 records total | Shafaq al-Abyad observation logs |
| South America | Fajr + Isha | Zero records | Muslim community programs in Brazil, Argentina, Colombia |
| Southeast Asia | Isha | Very few per-date records | Malaysian JAKIM, Indonesian Kemenag |
| High latitudes 55°N+ | Fajr | Zero records | Scandinavian Muslim communities, northern Canada |
| Sub-Saharan Africa | Fajr | 6 records, 3 sites | West African observation networks |
| Central Asia | Fajr | Zero records | Uzbekistan, Kazakhstan, Afghanistan |

---

## How to Contribute

If you have access to per-date sighting records with explicit times, dates, and locations,
open `src/collect/verified_sightings.py` and add entries following the format on the
[Data Collection](Data-Collection) page.

To propose a citation for review, open an issue on the GitHub repository with:
- Full bibliographic citation
- Location coordinates and elevation
- Date range of the observation program
- How many individual per-date records are published

---

*[← Architecture](Architecture) · [Research Notes →](Research-Notes)*
