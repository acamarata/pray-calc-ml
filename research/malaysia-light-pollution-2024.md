# Alteration of Twilight Sky Brightness Profile by Light Pollution

**Authors:** Muhamad Syazwan Faid, Mohd Zambri Zainuddin, Nazri Muslim, Nor Hazmin Sabri, Zainol Abidin Ibrahim, Chong Hun Yih
**Year:** 2024
**Journal:** Scientific Reports, 14: 26237
**DOI:** 10.1038/s41598-024-76550-3
**PMID:** 39496720, **PMCID:** PMC11535048
**URL:** https://www.nature.com/articles/s41598-024-76550-3
**Sites studied:** 12 sites across Malaysia (urban/suburban/pristine) + 1 in Australia
**Observation method:** SQM (Sky Quality Meter)
**Date range:** 2008-2022 (84 total observations, 72 validated)
**Mean angle (Fajr):** Pristine: -17.49 deg, Suburban: -15.67 deg, Urban: -11.50 deg (brightness stability onset)

## Sites

| # | Location | Coordinates | Classification | Zenith mag/arcsec2 |
|---|----------|-------------|----------------|-------------------|
| 1 | Putrajaya | 2 54'N, 101 41'E | Urban | 17.11 |
| 2 | Teluk Kemang | 2 27'N, 101 51'E | Rural | 19.5 |
| 3 | Tanjung Balau | 1 48'N, 104 24'E | Rural | 19.78 |
| 4 | Pantai Masjid Tengku Zaharah | 5 24'N, 103 57'E | Rural | 19.85 |
| 5 | Pantai Batu Buruk | 5 19'N, 103 9'E | Rural | 19.23 |
| 6 | Coonabarabran, Australia | 31 15'S, 149 16'E | Pristine | 21.59 |
| 7 | Pantai Mek Mas | 6 19'N, 102 9'E | Pristine | 21.3 |
| 8 | Balai Cerap Unisza | 5 24'N, 102 35'E | Pristine | 20.08 |
| 9 | Pulau Bunting | 5 51'N, 100 20'E | Pristine | 18.94 (rejected) |
| 10 | Simpang Mengayau, Sabah | 7 12'N, 116 30'E | Pristine | 21.64 |
| 11 | Pantai Melawi Bachok | 5 24'N, 102 35'E | Pristine | - |
| 12 | Pantai Nenasi | 3 36'N, 103 30'E | Pristine | - (rejected) |

## Summary

A large-scale SQM study comparing twilight brightness profiles across urban, suburban, and pristine sites in Malaysia and Australia. 84 twilight SQM datasets collected from 2014-2022, with 72 validated (12 rejected: 2 sites with inconsistent data).

The key finding: light pollution shifts the "brightness stability point" (the solar depression angle at which twilight brightness becomes indistinguishable from the full-night baseline) dramatically:
- Pristine: -17.49 degrees (close to the classical 18 deg)
- Suburban: -15.67 degrees (shifted inward by ~2 deg)
- Urban: -11.50 degrees (shifted inward by ~6 deg!)

This means in heavily light-polluted areas, the SQM cannot detect dawn until the sun is much closer to the horizon, because the urban sky glow already exceeds the natural twilight brightness.

Teluk Kemang long-term data (2008-2016) shows progressive brightening correlating with population growth, with full-night brightness changing from 19.69 to 19.55 mag/arcsec2 over 8 years.

## Data Availability

**AGGREGATE ONLY.** The paper reports:
- Mean brightness stability parameters per classification (Table 3)
- Full-night zenith brightness per site (Table 2)
- Teluk Kemang historical trend (Table 4)
- NO per-night dates or individual SQM time series

The 72 validated data points are summarized as profiles, not individual observations. No supplementary data files with raw per-night data were published.

## For ML Training

This paper is primarily useful for understanding how light pollution affects apparent dawn angle. The aggregate brightness stability values can serve as calibration points:
- Pristine sites: dawn detection at ~17.5 deg (useful as SQM benchmark)
- The per-site zenith brightness values help classify observation quality

Cannot extract per-night training rows. Already partially covered by abdelhadi_2022_malaysia_sqm.csv in our dataset (same research group, overlapping sites).
