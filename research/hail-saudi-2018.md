# Hail, Saudi Arabia — Khalifa 2018

## Paper

Khalifa, A.S. "Astronomical determination of Fajr and Isha prayer times at Hail, Saudi Arabia."
*NRIAG Journal of Astronomy and Geophysics*, 7: 22-28, 2018.

## Location

Hail (27.52°N, 41.70°E, ~1020m elevation) — a city on the Najd plateau in central Saudi Arabia.
The high elevation and desert conditions produce excellent sky transparency.

## Method

80 total observation nights in 2014-2015. 32 nights selected for excellent atmospheric
visibility (no clouds, no dust). Naked-eye observation by trained observers.

## Results

- **Mean Fajr depression:** 14.4° (range 12.8°-16.1°)
- **Mean Isha depression (Shafaq Abyad):** 14.8° (range 13.2°-16.4°)
- **Seasonal variation:** Higher angles in winter, lower in summer (consistent with other studies)

## Significance

At 1020m elevation, Hail is the highest-elevation site in the Saudi/Gulf region with published
Fajr observations. The results show a slightly higher mean angle than sea-level desert sites
in Egypt (13.5°-14.5°), consistent with the hypothesis that elevation increases the apparent
depression angle at true dawn (the observer is above more of the atmosphere, so the first light
of dawn appears at a slightly steeper angle).

The Hail dataset is particularly useful for the elevation variable in the ML model — it is one
of the few high-altitude desert sites with per-season data.

## Note for ML Training

The per-season records in `verified_sightings.py` for Hail are constructed from the paper's
reported seasonal means, with observation times estimated from sunrise data. They are marked
as "time inferred" in `data/raw/sources.md`.
