# Academic Best Formula: Solar Depression Angle at True Fajr and Isha

**Date:** 2026-03-23
**Dataset:** pray-calc-ml (48,668 Fajr + 34,529 Isha raw records)
**Method:** Filtered to Tier 1+2 sources only, source-weighted harmonic regression

---

## 1. Source Tier Classification

Each source in the dataset was classified by how closely its methodology matches the Islamic astronomical definitions:

- **Fajr Sadiq**: horizontal white light band appears on the eastern horizon, visible to a trained naked eye at a dark site. Not zodiacal light. Not instrument-detected pre-dawn glow.
- **Shafaq al-Abyad**: white twilight glow disappears from the western horizon. Not red glow (ahmar, which ends earlier at ~14 degrees).

### Tier 1: Directly measures the definition

Naked-eye observers at dark sites watching the horizon, or CCD cameras pointed at the horizon.

| Source | Records (Fajr) | Mean Angle | Latitude |
| --- | --- | --- | --- |
| OpenFajr Birmingham (CCD horizon camera) | 3,723 | 13.36 | 52.5N |
| Shaukat/Miftahi 2007 (naked eye, Blackburn UK) | 29 | 13.55 | 53.8N |
| Abed 2015 (naked eye group, Jordan desert) | 18 | 16.94 | 31.5N |
| Taha 2025 (naked eye, Mauritania + Riyadh desert) | 23 | 14.60 | 20-26N |
| Omar Afzal (naked eye, Ithaca NY) | 2 | 11.48 | 42.4N |
| Ouared (camera, Pampigny Switzerland) | 1 | 13.25 | 46.6N |
| Asim Yusuf 2017 (naked eye, Exmoor UK) | 4 | 14.65 | 51.1N |
| Ludhianvi 1975 (naked eye, 11 ulama, Sindh Pakistan) | 2 | 15.38 | 25.8N |
| **TOTAL** | **3,804** | **13.38** | |

### Tier 2: Good proxy

SQM at dark sites (MPSAS >= 21.3), DSLR photometry pointed at the horizon, per-night observations.

| Source | Records (Fajr) | Mean Angle | Latitude |
| --- | --- | --- | --- |
| Basthoni 2022 PhD, dark sites only (MPSAS >= 21.3) | 590 | 15.77 | 0-10S |
| Kassim Bahali 2018-2019 (DSLR, Malaysia/Indonesia) | 90 | 17.30 | 1-7N |
| BRIN multistation SQM 2018 | 34 | 17.61 | 1-7S |
| Khalifa 2018 (deep desert, Saudi) | 11 | 14.59 | 22N |
| Marzouk 2025 (DSLR, Egypt desert) | 11 | 14.41 | 24-30N |
| Various Indonesian SQM/DSLR studies | ~30 | 16-19 | 0-10S |
| Hidayatulloh 2023 (SQM+SOOF, Bortle 1) | 10 | 18.17 | 5S |
| **TOTAL** | **1,109** | **15.77** | |

### Tier 3: Loose proxy (excluded from formula fitting)

SQM at light-polluted sites (MPSAS < 21.3), citizen science with approximate timestamps. Records: 3,702 (Fajr). Mean: 12.40 degrees. These systematically read shallower angles because light pollution masks the true dawn signal.

### Tier 4: Wrong definition (excluded from formula fitting)

TESS-W zenith SQM network, Globe at Night citizen science, Madrid UCM zenith SQM. Records: 40,054 (Fajr). These measure zenith sky brightness, not horizon light. The inflection point in zenith brightness occurs at a different depression angle than the onset of visible light on the horizon.

---

## 2. Fajr Formula: Tier 1+2 Source-Weighted Medium-9

### Model specification

```
angle = base
      + a1 * |lat|
      + a2 * sin(D) + a3 * cos(D) + a4 * sin(2D) + a5 * cos(2D)
      + a6 * |lat| * sin(D) + a7 * |lat| * cos(D)
      + a8 * |lat| * sin(2D) + a9 * |lat| * cos(2D)

where D = 2 * pi * day_of_year / 365.25
      |lat| = absolute latitude in degrees
```

### Weighting scheme

Tier 1 sources receive 3x weight. Per-source weight is scaled by 1/sqrt(n) to prevent OpenFajr's 3,723 records from overwhelming the 80 non-OpenFajr Tier 1 records and the 1,109 Tier 2 records.

### Fitted coefficients (source-weighted)

| Coefficient | Value | Feature |
| --- | --- | --- |
| base | **16.982** | Intercept (equatorial equinox angle) |
| a1 | -0.066561 | abs_lat |
| a2 | -0.080311 | sin(D) |
| a3 | -0.100276 | cos(D) |
| a4 | +0.150842 | sin(2D) |
| a5 | -0.662638 | cos(2D) |
| a6 | -0.004398 | abs_lat * sin(D) |
| a7 | +0.000249 | abs_lat * cos(D) |
| a8 | +0.003904 | abs_lat * sin(2D) |
| a9 | +0.002038 | abs_lat * cos(2D) |

### Fit statistics

| Metric | Value |
| --- | --- |
| Records | 4,912 (Tier 1 + Tier 2) |
| Weighted R-squared | 0.426 |
| Weighted MAE | 1.14 degrees |
| Baseline 95% CI | [16.733, 17.222] degrees |
| Night-to-night noise floor | ~0.35 degrees std (irreducible atmospheric variation, measured from OpenFajr) |

### Predictions vs literature

| Location | Day of Year | Formula | Literature / Observed | Source |
| --- | --- | --- | --- | --- |
| Equator, equinox | 80 | 17.55 | ~17-18 | MWL/Karachi convention |
| Equator, Jun solstice | 172 | 16.39 | ~17-18 | MWL/Karachi convention |
| Mecca (21.4N), equinox | 80 | 16.03 | 14.7 | Taha et al. 2025 |
| Riyadh (25N), equinox | 80 | 15.77 | 14.7 | Taha et al. 2025 |
| Cairo (30N), equinox | 80 | 15.42 | 14.4 | Marzouk et al. 2025 |
| Jordan (31.5N), equinox | 80 | 15.31 | 17.0 | Abed 2015 |
| Madrid (40.4N), equinox | 80 | 14.68 | 15-16 (est) | |
| Birmingham (52.5N), equinox | 80 | 13.81 | 13.73 | OpenFajr observed monthly |
| Birmingham, June solstice | 172 | 12.87 | 12.26 | OpenFajr observed monthly |
| Birmingham, Sep equinox | 265 | 14.45 | 14.42 | OpenFajr observed monthly |
| Birmingham, Dec solstice | 355 | 12.81 | 12.53 | OpenFajr observed monthly |

---

## 3. OpenFajr Birmingham: Purest Single-Source Analysis

OpenFajr is the single most controlled dataset: one CCD camera, one location (52.483N, -1.894W), community-voted true dawn timestamps, running since 2018.

### Single-location seasonal fit (4-parameter)

```
angle = 13.361
      - 0.308 * sin(D)
      - 0.085 * cos(D)
      + 0.350 * sin(2D)
      - 0.761 * cos(2D)
```

| Metric | Value |
| --- | --- |
| Records | 3,723 |
| R-squared | 0.767 |
| MAE | 0.240 degrees |
| Baseline | 13.361 degrees |
| Seasonal range | 12.26 (June) to 14.42 (September) |

### Monthly observed means

| Month | Observed Mean | Model Prediction | N |
| --- | --- | --- | --- |
| Jan | 12.96 | 13.02 | 341 |
| Feb | 13.12 | 13.57 | 311 |
| Mar | 13.73 | 13.82 | 327 |
| Apr | 14.05 | 13.54 | 300 |
| May | 12.75 | 13.00 | 310 |
| Jun | 12.26 | 12.82 | 300 |
| Jul | 13.18 | 13.30 | 310 |
| Aug | 14.14 | 14.10 | 310 |
| Sep | 14.42 | 14.47 | 300 |
| Oct | 13.92 | 14.10 | 304 |
| Nov | 13.29 | 13.30 | 300 |
| Dec | 12.53 | 12.83 | 310 |

Key finding: the seasonal pattern at 52.5N shows a DOUBLE peak (April and August/September), not the single summer-winter cycle many conventions assume. This is captured by the sin(2D) and cos(2D) terms. The deepest angles occur at equinoxes (~14 degrees) and the shallowest near solstices (~12.3-12.5 degrees).

---

## 4. Comparison with pray-calc's Current DPC

The current pray-calc DPC (v2.0) uses a three-layer model:

1. MSC piecewise seasonal base (Khalid Shaukat): 75 minutes at equator, latitude-scaled
2. Physics corrections: Earth-Sun distance, Fourier smoothing, atmospheric refraction
3. Environmental: elevation dip, pressure/temperature

The DPC is documented as producing ~18 degrees at the equator and ~12-14 degrees at 50-55N in summer.

### How our empirical formula compares

| Latitude Band | DPC Claims | Our Formula (equinox) | Agreement |
| --- | --- | --- | --- |
| Equator (0) | ~18 | 17.6 | Close. DPC may be ~0.5 degrees high |
| Low (21-30N) | ~16-18 | 15.4-16.0 | Our formula 1-2 degrees lower. Field data (Taha, Marzouk) confirms lower values around 14.5 degrees |
| Mid (40N) | ~14-17 | 14.7 | Reasonable agreement |
| High (52.5N) | ~12-14 | 13.8 (equinox), 12.9 (solstice) | Good agreement |
| Very high (55N) | ~11-15 | 12.7 (solstice) | Good agreement |

### Key discrepancies

1. **At 20-30N (Saudi, Egypt, Mauritania):** Our empirical data (Taha 2025, Marzouk 2025, Khalifa 2018) consistently shows 14.4-14.7 degrees. The formula predicts 15.4-16.0 because it is pulled upward by Indonesian Tier 2 SQM data (mean 15.8 at similar latitudes). The pray-calc DPC likely overestimates at these latitudes by 1-3 degrees relative to human-perceived Fajr Sadiq.

2. **At 31.5N (Jordan):** Abed 2015 reports 17.0 degrees from naked-eye group observation, but the formula predicts 15.3. This is a conflict. Abed's observers may be reporting a slightly different threshold than OpenFajr's CCD, or atmospheric conditions in Jordan differ systematically from Mauritania/Egypt.

3. **At the equator:** The formula predicts 17.6 degrees, consistent with the traditional 18-degree convention. However, this is extrapolated, as we have no Tier 1 equatorial data. The Tier 2 Indonesian data ranges widely (13-20 degrees), suggesting SQM inflection at tropical sites has high variance.

---

## 5. Isha: Insufficient Data

### Available Tier 1+2 Isha records: 45 total

| Source | Records | Mean Angle | Latitude |
| --- | --- | --- | --- |
| Shaukat/Miftahi 2007 (naked eye, Blackburn UK) | 32 | 13.33 | 53.8N |
| Asim Yusuf 2017 (naked eye, Exmoor UK) | 6 | 16.78 | 51.1N |
| Khalifa 2018 (desert, Hail Saudi) | 3 | 14.14 | 27.5N |
| Niri & Zainuddin (Sabah Malaysia) | 3 | 17.84 | 6.0N |
| Tayebi (naked eye, Michigan USA) | 1 | 11.63 | 42.1N |

With only 45 records across 4 latitudes, no reliable multi-latitude formula is possible. The bootstrapped 95% CI on the intercept spans from -161 to +322 degrees (meaningless).

**Tentative findings for Isha (NOT suitable for production use):**
- Shafaq al-Abyad at 53-54N: ~13.3 degrees (Shaukat/Miftahi, n=32)
- Shafaq al-Abyad at equator: ~17.8 degrees (Niri, n=3, single site)
- These are consistent with Fajr findings (deeper angle near equator, shallower at high lat)
- Isha needs its own dedicated data collection campaign before a formula can be produced

---

## 6. Recommended Coefficients for pray-calc

### Fajr: ready for adoption (with caveats)

```typescript
// Solar depression angle at true Fajr (Subh Sadiq)
// Source: pray-calc-ml Tier 1+2 source-weighted harmonic regression
// 4,912 records from CCD, naked-eye, SQM dark-site, and DSLR horizon observations
//
// Caveats:
//   - Equatorial prediction (17.6 deg) is extrapolated; no Tier 1 tropical data
//   - 15-30N prediction (15-16 deg) may be ~1 deg high vs field data (Taha, Marzouk ~14.5)
//   - 45-55N predictions are well-calibrated by OpenFajr (R^2 = 0.77)
//   - Night-to-night atmospheric noise: ~0.35 deg std (irreducible)

const FAJR_BASE = 16.982;
const FAJR_COEF = {
  abs_lat:     -0.066561,
  sinD:        -0.080311,
  cosD:        -0.100276,
  sin2D:       +0.150842,
  cos2D:       -0.662638,
  lat_sinD:    -0.004398,
  lat_cosD:    +0.000249,
  lat_sin2D:   +0.003904,
  lat_cos2D:   +0.002038,
};

function fajrAngle(lat: number, dayOfYear: number): number {
  const absLat = Math.abs(lat);
  const D = (2 * Math.PI * dayOfYear) / 365.25;
  const sinD = Math.sin(D);
  const cosD = Math.cos(D);
  const sin2D = Math.sin(2 * D);
  const cos2D = Math.cos(2 * D);

  return FAJR_BASE
    + FAJR_COEF.abs_lat * absLat
    + FAJR_COEF.sinD * sinD
    + FAJR_COEF.cosD * cosD
    + FAJR_COEF.sin2D * sin2D
    + FAJR_COEF.cos2D * cos2D
    + FAJR_COEF.lat_sinD * absLat * sinD
    + FAJR_COEF.lat_cosD * absLat * cosD
    + FAJR_COEF.lat_sin2D * absLat * sin2D
    + FAJR_COEF.lat_cos2D * absLat * cos2D;
}
```

### Isha: NOT ready

Do not replace the current pray-calc Isha algorithm. The dataset has only 45 Tier 1+2 records. The current MSC-based approach (shafaq abyad mode) remains the best available estimate until a dedicated Isha observation campaign is completed.

---

## 7. Per-Latitude-Band Validation Summary

| Band | Lat Range | N (T1+2) | Observed Mean | Predicted Mean | MAE | R-squared |
| --- | --- | --- | --- | --- | --- | --- |
| Equatorial | 0-15 | 1,083 | 15.78 | 15.81 | 2.14 | 0.073 |
| Subtropical | 15-30 | 51 | 14.97 | 14.38 | 0.91 | -0.342 |
| Mid-latitude | 30-45 | 20 | 16.39 | 14.63 | 2.46 | -1.546 |
| High-latitude | 45-60 | 3,758 | 13.36 | 13.37 | 0.25 | 0.737 |

The formula performs well at high latitudes (R-squared = 0.74, MAE = 0.25 degrees) where we have dense, high-quality data. Performance degrades significantly at equatorial and mid-latitudes where the Tier 2 Indonesian SQM data has high variance (std > 2 degrees) and the mid-latitude band has only 20 records.

---

## 8. Data Gaps and Next Steps

### Critical data needed

1. **Equatorial Tier 1 data.** Need naked-eye or CCD horizon observations at 0-15 degree latitudes. No such data currently exists in the dataset.

2. **15-30N data density.** Only 51 Tier 1+2 records. Need at least 200-500 per-night observations from Saudi, Egypt, Pakistan, or North Africa to constrain the subtropical Fajr angle.

3. **Mid-latitude Tier 1 data.** Only 20 records from Jordan. Need observations from Turkey (39-41N), Iran (32-36N), or southern Europe.

4. **Isha dedicated campaign.** The 45-record Isha dataset is useless for modeling. Need the same source types as Fajr: CCD horizon cameras, naked-eye expert panels, and dark-site SQM series.

### What would change the formula

- If equatorial Tier 1 data shows 15-16 degrees instead of 17-18, the baseline would drop by 1-2 degrees, bringing it closer to the Taha/Marzouk mid-latitude values. This would imply the traditional 18-degree convention is too deep.
- If equatorial Tier 1 data confirms 17-18 degrees, the current formula is approximately correct and the low-latitude field studies (Taha, Marzouk) may reflect atmospheric or site-specific factors.
- Either outcome is scientifically significant. The equatorial Fajr angle is the single most important measurement still missing.

---

## Appendix: Tier 1 Only Formula (for reference)

This formula is fitted to Tier 1 data alone (3,804 records, 97.9% from OpenFajr). It should be viewed as the "OpenFajr-anchored" formula, extrapolated to other latitudes using only 80 non-OpenFajr records.

```
base    = 17.657
abs_lat = -0.081784
sinD    = -0.760861
cosD    = -1.468562
sin2D   = +0.317475
cos2D   = +0.677708
lat_sinD  = +0.008716
lat_cosD  = +0.026438
lat_sin2D = +0.000662
lat_cos2D = -0.027300
```

R-squared = 0.723, MAE = 0.259 degrees. The higher R-squared (vs 0.43 for T1+2 weighted) reflects that 98% of the data is at one location, so the seasonal model captures the seasonal signal very well. It should not be interpreted as indicating a better formula for global use.
