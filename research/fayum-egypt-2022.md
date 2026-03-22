# Determination of the True Dawn by Several Different Ways at Fayum in Egypt

**Authors:** M.G. Rashed, Yasser A. Abdel-Hadi, M.S. El-Nawawy, M.Y. Amin, U.A. Rahoma, M.A. Semeida, A. Abul-Wafa, G.A. Goma, M. Sedek, M.M. Hussien, A.A. Elminawy, M.A. Shahat, A.H. Ibrahim, A.R. Mouner, A.H. Hassan, and Hussein M. Farid
**Year:** 2022
**Journal:** International Journal of Mechanical Engineering and Technology (IJMET), 13(10): 8-24
**DOI:** https://doi.org/10.17605/OSF.IO/9K3MJ
**URL:** https://iaeme.com/Home/article_id/IJMET_13_10_002
**Sites studied:** Wadi al Hitan, Fayum, Egypt (29 17'N, 30 03'E, 50m elevation)
**Observation method:** SQM (LU-DL, Unihedron) in horizontal (H) and zenith (Z) directions, plus naked eye by groups of 9+ astronomers
**Date range:** December 9-11, 2018 (Group 1) and December 19, 2019 (Group 2)
**Records:** 4 nights of SQM data, 2 separate naked-eye group observations
**Mean angle (Fajr):** D0 = 14.0 to 14.8 depending on method

## Location Details

- Wadi al Hitan, Fayum desert, Egypt
- 29 17'N, 30 03'E, 50m elevation
- Desert area far from urban light pollution
- Chosen specifically for astronomical observation quality

## Summary

A multi-method study combining SQM photometry and naked-eye observations over 4 nights at Fayum desert. The paper applies four different criteria to determine true dawn:

1. Eye threshold method (0.83 mag from full night): D0 = 14.7 degrees
2. Naked eye group observation (9+ trained observers, tayakkun): D0 = 14.8 degrees
3. Kocifaj relation H = pi*Z: D0 = 14.0 degrees
4. Luminance threshold 0.015 cd/m2 (mesopic region): D0 = 13.75 degrees (clear), 10 degrees (cloudy)

Key SQM findings:
- Full night illuminance: 18.76 mag (east direction), 16.92 mag (zenith) for clear nights
- Full night illuminance: 22 mag for cloudy night
- The H/Z ratio equals pi at D0 = 14 degrees (Kocifaj criterion)
- Clear vs cloudy comparison shows clouds delay apparent dawn by ~4 degrees

Table 4 provides SQM readings at D0 = 6, 12, 14, 14.8, 18 degrees for Dec 19, 2019 in both east and zenith directions. This is valuable calibration data.

Clouds absorb 19% of the night sky energy during full night and 2.5% during twilight.

## Data Availability

**LIMITED PER-NIGHT DATA.** The paper presents:
- SQM curves as figures for 4 nights (Dec 9, 10, 11 2018 + Dec 19 2019)
- Table 4: SQM readings at specific D0 values for Dec 19, 2019
- Tables 2-3: Statistical values of twilight luminance energy per degree for Dec 10-11, 2018
- No per-minute time series data published

The SQM curves in the figures could be digitized to extract approximate readings at specific D0 values, but the paper does not provide raw time-stamped SQM data.

For ML training, the useful data points are:
- Dec 9, 2018: clear night, SQM threshold at D0 = 14.6 degrees
- Dec 10, 2018: clear night, mesopic threshold at D0 = 13.75 degrees
- Dec 11, 2018: cloudy night, threshold at D0 = 10 degrees (excluded from ML, clouds)
- Dec 19, 2019: clear night, D0 = 14.0 (H=piZ method), D0 = 14.8 (naked eye group)

## Comprehensive Literature Table

Table 1 (page 12) provides an excellent summary of all published twilight studies chronologically from 1909 to 2022, covering Egypt, Libya, Saudi Arabia, Yemen, Indonesia, and Malaysia. This is a useful cross-reference for the aggregate D0 database.

## For ML Training

Can extract 4 data points (one per clear night) with SQM-derived D0 values. The naked-eye group observation on Dec 19, 2019 gives D0 = 14.8 degrees. Only useful as aggregate/representative data since exact dawn times are not given (only D0 values derived from SQM threshold analysis).
