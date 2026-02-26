# OpenFajr Project (Birmingham, UK)

## Overview

OpenFajr is an ongoing community astrophotography project in Birmingham, UK, where a panel
of scholars and community members review daily sky photographs and vote on the moment of
true dawn. This is the largest dataset of per-date human-verified Fajr sightings in the world,
with over 4,000 records spanning 2016 to the present.

**URL:** https://openfajr.org
**Data format:** Google Calendar iCal feed (UTC)
**Location:** Birmingham (52.4862°N, 1.8904°W, 141m)

## Method

Each morning, a wide-field camera captures a continuous series of sky photographs from the
eastern horizon. After each session, an independent panel reviews and votes on the photographs
to identify the moment when the horizon first becomes distinguishable (true dawn / Subh Sadiq).
The voted time is published to the iCal feed.

## Findings

Birmingham is at 52°N, which produces interesting seasonal variation. The dataset covers over
10 years and shows:

- **Mean depression angle:** approximately 12.5°-13.5° (computed in this project via back-calculation)
- **Seasonal variation:** lower angles in summer (shorter, shallower twilight arc), higher in winter
- **Winter range:** typically 13.5°-15.0°
- **Summer range:** typically 11.5°-13.5° (sun moves at a shallower angle through the horizon zone)
- **Inter-year consistency:** very stable year-to-year

## Why Birmingham

Birmingham's latitude (52°N) is notable because it experiences significant seasonal variation in
both the angle and duration of twilight. At this latitude in summer, nights are very short and
twilight begins to overlap with morning civil dawn — the solar arc through the horizon zone is
much shallower, meaning false dawn and true dawn phenomena behave differently than at tropical
latitudes.

This makes Birmingham a particularly useful calibration anchor because:
1. It covers an extreme of the northern temperate zone
2. 10+ years of consistent data provides excellent statistical confidence
3. The scholarly review process provides strong validity guarantees

## DST Artifacts

The iCal feed contains a small number of records around British Summer Time transition dates
(last Sunday of March, last Sunday of October) with anomalous UTC timestamps. These appear to
result from timezone confusion in calendar software and produce depression angles of 3°-7°,
which are physically impossible for genuine Fajr sightings. The pipeline filters these out.

## Use in This Project

OpenFajr provides ~98% of the Fajr training data. The raw iCal is fetched at runtime by
`src/collect/openfajr.py`. No local caching is performed; run the pipeline with network access
to get the latest feed.
