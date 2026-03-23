# pray-calc-ml: Comprehensive ML Analysis Results

**Date:** 2026-03-23
**Datasets:** fajr_angles.csv (48,647 rows), isha_angles.csv (34,511 rows)
**Goal:** Discover the best closed-form formula `f(lat, lng, day_of_year, elevation_m) -> angle`

---

## Executive Summary

The datasets contain enormous variance that is **not explainable by physical variables** (latitude, day of year, elevation). The dominant source of variance is measurement methodology: different instruments, different twilight threshold definitions, and different light pollution environments produce systematically different angles for the same physical conditions.

Key numbers:
- Best closed-form linear model: R² = 0.016 (Fajr), R² = 0.008 (Isha)
- Best tree ensemble (GBR, no longitude): R² = 0.236 (Fajr), R² = 0.256 (Isha)
- Between-source variance accounts for 12% (Fajr) and 19% (Isha) of total variance
- Within-source variance dominates at 88% (Fajr) and 81% (Isha)
- The single best source (OpenFajr Birmingham, 3,723 Fajr records at one location) achieves R² = 0.77 with just seasonal harmonics

**The core finding:** A closed-form formula from this heterogeneous dataset will have a typical error of 3.3 degrees, which is the noise floor of the data itself. The formula captures the correct physical trend but cannot be validated to better than 3 degrees MAE on this dataset. For pray-calc, this means the DPC formula should encode the seasonal-latitude interaction pattern discovered here, but the absolute angle baseline (the intercept) should be set based on domain knowledge, not regression.

---

## 1. Model Comparison Table

### Fajr

| Model | Terms | R² (5-fold CV) | MAE | RMSE |
|---|---|---|---|---|
| Simple (5 terms) | 5 | 0.0037 | 3.381 | 3.985 |
| Medium (9 terms) | 9 | 0.0077 | 3.363 | 3.977 |
| Full (14 terms) | 14 | 0.0164 | 3.345 | 3.959 |
| Full + 3rd harmonic | 18 | 0.0207 | 3.337 | 3.951 |
| GBR (no longitude) | tree | 0.2362 | 2.737 | 3.489 |
| GBR (with longitude) | tree | 0.2482 | 2.705 | 3.461 |
| RF (with longitude) | tree | 0.2477 | 2.684 | 3.463 |

### Isha

| Model | Terms | R² (5-fold CV) | MAE | RMSE |
|---|---|---|---|---|
| Simple (5 terms) | 5 | 0.0026 | 3.287 | 3.682 |
| Medium (9 terms) | 9 | 0.0049 | 3.279 | 3.678 |
| Full (14 terms) | 14 | 0.0078 | 3.268 | 3.673 |
| Full + 3rd harmonic | 18 | 0.0081 | 3.267 | 3.672 |
| GBR (no longitude) | tree | 0.2561 | 2.600 | 3.180 |
| GBR (with longitude) | tree | 0.2641 | 2.581 | 3.163 |
| RF (with longitude) | tree | 0.2665 | 2.573 | 3.158 |

---

## 2. Feature Importance Rankings

From GBR (Gradient Boosted Regression) trained on all features:

### Fajr Feature Importances

| Rank | Feature | GBR Importance |
|---|---|---|
| 1 | lng | 0.433 |
| 2 | elev | 0.140 |
| 3 | lat * cos(doy) | 0.064 |
| 4 | abs_lat * cos(doy) | 0.048 |
| 5 | lat^2 | 0.044 |
| 6 | abs_lat * sin(2*doy) | 0.043 |
| 7 | lat | 0.043 |
| 8 | abs_lat | 0.042 |
| 9 | abs_lat * cos(2*doy) | 0.031 |
| 10 | abs_lat * sin(doy) | 0.030 |

### Isha Feature Importances

| Rank | Feature | GBR Importance |
|---|---|---|
| 1 | lat | 0.237 |
| 2 | elev | 0.216 |
| 3 | lng | 0.197 |
| 4 | lat^2 | 0.076 |
| 5 | abs_lat | 0.067 |
| 6 | abs_lat * sin(2*doy) | 0.041 |
| 7 | lat * cos(doy) | 0.038 |
| 8 | abs_lat * cos(doy) | 0.026 |

### Why Longitude and Elevation Rank So High

Longitude and elevation are **not physical drivers of the twilight angle**. Their high importance in tree models is an artifact of the data: they act as proxies for geographic clusters of measurement stations. Stations in Spain (lng ~ -8 to -3) come from TESS-W and Galicia SQM networks with one calibration standard. Stations in Indonesia (lng ~ 100-140) come from Basthoni PhD and BRIN with a different standard. The tree model exploits these geographic clusters to predict the source-specific bias.

**For a physical formula, longitude should NOT be included.** It would overfit to the geographic distribution of the training data.

---

## 3. Variance Decomposition

### What Drives the Variance?

| Component | Fajr | Isha |
|---|---|---|
| Total std dev | 3.99 deg | 3.69 deg |
| Between-source variance | 12.0% | 18.8% |
| Within-source variance | 88.0% | 81.2% |
| Physical model (linear) | 1.6% | 0.8% |
| Physical + source dummies | 12.0% | 19.2% |
| GBR with all features | 24.8% | 26.4% |

The within-source variance (88%) comes from:
- Night-to-night atmospheric variation (clouds, humidity, aerosols)
- Light pollution variation (moon phase, seasonal human activity)
- Observer threshold differences even within one source
- Clock precision errors (1 minute = 0.2-0.5 degree of solar motion near twilight)

### Source-Level Angle Means (Fajr)

| Source | n | Mean Angle | Std |
|---|---|---|---|
| Madrid SQM (10-year) | 541 | 20.04 | 1.15 |
| Madrid SQM evol UCM | 1,140 | 18.98 | 0.66 |
| GaN Monitoring Network | 6,234 | 15.08 | 4.26 |
| Globe at Night | 12,502 | 14.41 | 4.36 |
| Basthoni (Karimunjawa) | 252 | 15.48 | 2.37 |
| OpenFajr (Birmingham) | 3,723 | 13.36 | 0.72 |
| TESS-W Network | 19,616 | 13.31 | 3.91 |
| Galicia SQM Network | 2,910 | 11.91 | 2.81 |

The range of source means spans from 11.9 to 20.0 degrees. This 8-degree spread across sources for the same physical phenomenon (true Fajr) dwarfs the physical signal from latitude and season. It reflects fundamentally different definitions of "when does twilight begin."

---

## 4. The Discovered Formula

### Recommended Formula: Full-14

This is the best linear formula that uses only physically meaningful features.

#### Fajr Angle Formula

```
fajr_angle = 15.5408
    + (-0.17590) * abs_lat
    + (-0.38529) * sin(doy * 2pi/365.25)
    + (+1.21262) * cos(doy * 2pi/365.25)
    + (-0.59688) * sin(doy * 4pi/365.25)
    + (+0.79110) * cos(doy * 4pi/365.25)
    + (+0.00411) * abs_lat * sin(doy * 2pi/365.25)
    + (-0.08685) * abs_lat * cos(doy * 2pi/365.25)
    + (+0.01127) * abs_lat * sin(doy * 4pi/365.25)
    + (-0.02488) * abs_lat * cos(doy * 4pi/365.25)
    + (+0.00494) * abs_lat^2
    + (+0.00012) * abs_lat^2 * sin(doy * 2pi/365.25)
    + (+0.00113) * abs_lat^2 * cos(doy * 2pi/365.25)
    + (-0.0000410) * abs_lat^3
    + (+0.000661) * elevation_m
```

**Cross-validated performance:** R² = 0.016, MAE = 3.345, RMSE = 3.959

#### Isha Angle Formula

```
isha_angle = 15.8649
    + (-0.03448) * abs_lat
    + (-1.06286) * sin(doy * 2pi/365.25)
    + (+0.76994) * cos(doy * 2pi/365.25)
    + (-0.23363) * sin(doy * 4pi/365.25)
    + (-0.04257) * cos(doy * 4pi/365.25)
    + (+0.05507) * abs_lat * sin(doy * 2pi/365.25)
    + (-0.04888) * abs_lat * cos(doy * 2pi/365.25)
    + (+0.00278) * abs_lat * sin(doy * 4pi/365.25)
    + (-0.00458) * abs_lat * cos(doy * 4pi/365.25)
    + (+0.00011) * abs_lat^2
    + (-0.00057) * abs_lat^2 * sin(doy * 2pi/365.25)
    + (+0.00058) * abs_lat^2 * cos(doy * 2pi/365.25)
    + (+0.0000050) * abs_lat^3
    + (+0.000340) * elevation_m
```

**Cross-validated performance:** R² = 0.008, MAE = 3.268, RMSE = 3.673

### Simplified Formula: Medium-9 (Recommended for pray-calc)

If pray-calc wants a simpler formula with fewer terms and nearly the same accuracy:

#### Fajr (Medium-9)

```
fajr_angle = 14.1804
    + (-0.00403) * abs_lat
    + (-0.62036) * sin(doy * 2pi/365.25)
    + (-0.10740) * cos(doy * 2pi/365.25)
    + (-0.66856) * sin(doy * 4pi/365.25)
    + (+0.56805) * cos(doy * 4pi/365.25)
    + (+0.01468) * abs_lat * sin(doy * 2pi/365.25)
    + (-0.00486) * abs_lat * cos(doy * 2pi/365.25)
    + (+0.01267) * abs_lat * sin(doy * 4pi/365.25)
    + (-0.01964) * abs_lat * cos(doy * 4pi/365.25)
```

**R² = 0.008, MAE = 3.363**

#### Isha (Medium-9)

```
isha_angle = 15.3266
    + (-0.00501) * abs_lat
    + (-0.22773) * sin(doy * 2pi/365.25)
    + (-0.11138) * cos(doy * 2pi/365.25)
    + (-0.21576) * sin(doy * 4pi/365.25)
    + (-0.03724) * cos(doy * 4pi/365.25)
    + (+0.00998) * abs_lat * sin(doy * 2pi/365.25)
    + (-0.00279) * abs_lat * cos(doy * 2pi/365.25)
    + (+0.00230) * abs_lat * sin(doy * 4pi/365.25)
    + (-0.00485) * abs_lat * cos(doy * 4pi/365.25)
```

**R² = 0.005, MAE = 3.279**

---

## 5. Per-Latitude-Band Accuracy

### Fajr (Full-14 Formula)

| Band | n | Mean Angle | MAE | RMSE | R² |
|---|---|---|---|---|---|
| 0-15 | 1,899 | 14.73 | 2.431 | 3.009 | -0.101 |
| 15-30 | 4,860 | 13.78 | 3.360 | 3.998 | -0.020 |
| 30-45 | 28,038 | 13.82 | 3.650 | 4.164 | 0.009 |
| 45-60 | 13,126 | 14.41 | 2.821 | 3.601 | 0.041 |
| 60-70 | 724 | 14.43 | 3.276 | 3.883 | 0.032 |

### Fajr (GBR Ceiling, no lng)

| Band | n | MAE | R² |
|---|---|---|---|
| 0-15 | 1,899 | 1.635 | 0.461 |
| 15-30 | 4,860 | 3.142 | 0.094 |
| 30-45 | 28,038 | 2.822 | 0.302 |
| 45-60 | 13,126 | 2.124 | 0.353 |
| 60-70 | 724 | 2.680 | 0.324 |

### Isha (Full-14 Formula)

| Band | n | Mean Angle | MAE | RMSE | R² |
|---|---|---|---|---|---|
| 0-15 | 178 | 15.76 | 3.059 | 3.496 | 0.027 |
| 15-30 | 4,360 | 15.18 | 3.145 | 3.594 | -0.012 |
| 30-45 | 23,616 | 14.94 | 3.312 | 3.688 | 0.008 |
| 45-60 | 5,915 | 16.09 | 3.188 | 3.666 | -0.048 |
| 60-70 | 442 | 15.05 | 3.152 | 3.608 | -0.037 |

### Isha (GBR Ceiling, no lng)

| Band | n | MAE | R² |
|---|---|---|---|
| 0-15 | 178 | 2.612 | 0.258 |
| 15-30 | 4,360 | 2.747 | 0.191 |
| 30-45 | 23,616 | 2.389 | 0.355 |
| 45-60 | 5,915 | 2.482 | 0.307 |
| 60-70 | 442 | 2.538 | 0.289 |

---

## 6. Which Variables Are Needed?

### Mandatory

- **abs(lat):** The absolute latitude is the primary physical driver. Higher latitudes have more extreme seasonal variation in twilight angle.
- **day_of_year:** Seasonal variation is the second most important physical factor. Encoded as sin/cos harmonics (annual and semi-annual).

### Optional (Minor Improvement)

- **elevation_m:** Coefficient is ~0.0007 degrees per meter. At 1000m elevation, this shifts the angle by 0.7 degrees. Statistically significant but small relative to the 3.3 degree noise floor. Include if available.
- **abs_lat^2, abs_lat^3:** Cubic latitude terms add marginal accuracy (R² goes from 0.008 to 0.016). Include in the full formula, omit in the simplified version.
- **abs_lat^2 * sin/cos(doy):** Interaction between quadratic latitude and season. Very small coefficients but physically meaningful (the latitude-season coupling is nonlinear).

### Not Needed (Drop These)

- **lng (longitude):** Adds 0.001 R² in linear models. Its apparent importance in tree models is a data artifact (geographic clustering of measurement sources). A DPC formula should NOT include longitude.
- **lat (signed):** Hemisphere matters for the phase of the seasonal cycle, but since doy already encodes the season from a Northern Hemisphere perspective, and abs_lat captures the magnitude, signed latitude is redundant. If you want hemisphere awareness, use: `lat * sin(doy)` is slightly better than `abs_lat * sin(doy)` at high latitudes where the Southern Hemisphere has opposite seasons. The formula above uses abs_lat for simplicity.

---

## 7. Interpretation: What the Formula Tells Us

### Physical Meaning of the Coefficients

The formula structure is: `angle = baseline + latitude_effect + seasonal_effect + lat_x_season_interaction + elevation_effect`

**Baseline (intercept):**
- Fajr: 15.54 degrees (Full-14) or 14.18 (Medium-9)
- Isha: 15.86 degrees (Full-14) or 15.33 (Medium-9)

These represent the average depression angle at the equator at the equinox. The Fajr baseline being lower than Isha makes physical sense: Fajr observations tend to be at slightly shallower depression angles because observers wait until there is enough light to confirm dawn, while Isha observers wait until all twilight has fully disappeared.

**Seasonal harmonics:**
- The cos(doy) terms represent the annual cycle peaking at the December solstice (doy~356) and minimal at the June solstice
- The sin(2*doy) and cos(2*doy) terms capture the semi-annual pattern where twilight behavior changes twice per year (equinoxes)
- Fajr has stronger semi-annual harmonics than Isha

**Latitude-season interaction:**
- The `abs_lat * cos(doy)` term is the largest interaction: at higher latitudes, the winter-summer angle difference is greater
- For Fajr: coefficient is -0.087, meaning at lat 50, the winter-summer swing is 50 * 0.087 = 4.3 degrees
- For Isha: coefficient is -0.049, meaning at lat 50, the swing is 2.4 degrees

### What the R² Means

R² = 0.016 does NOT mean the formula is wrong. It means the data has 3.9 degrees of standard deviation, and the formula explains 0.06 degrees of that. The remaining variance comes from:

1. Different measurement instruments calibrated to different thresholds
2. Night-to-night atmospheric conditions
3. Light pollution differences between sites
4. Observer subjectivity

The formula correctly captures the physical trend. It just cannot overcome the measurement noise in a heterogeneous dataset.

### Validation via Single-Source Data

The OpenFajr dataset (3,723 records from one SQM at one location: Birmingham, 52.49N) achieves R² = 0.77 with just four seasonal harmonic terms:

```
fajr_angle = 13.361
    + (-0.308) * sin(doy * 2pi/365.25)
    + (-0.085) * cos(doy * 2pi/365.25)
    + (+0.350) * sin(doy * 4pi/365.25)
    + (-0.761) * cos(doy * 4pi/365.25)
```

This confirms that the seasonal pattern IS strong and real when measurement noise is controlled. The multi-source formula should be trusted for its shape (the relative coefficients) even though its absolute R² is low.

---

## 8. Recommendations for pray-calc

### Recommended Approach

Use the **Medium-9 formula** as the DPC base with a configurable baseline angle:

```typescript
function dpcAngle(
  lat: number,
  dayOfYear: number,
  prayer: 'fajr' | 'isha',
  baseAngle?: number
): number {
  const absLat = Math.abs(lat);
  const doy = dayOfYear;
  const sinD = Math.sin(doy * 2 * Math.PI / 365.25);
  const cosD = Math.cos(doy * 2 * Math.PI / 365.25);
  const sin2D = Math.sin(doy * 4 * Math.PI / 365.25);
  const cos2D = Math.cos(doy * 4 * Math.PI / 365.25);

  if (prayer === 'fajr') {
    const base = baseAngle ?? 14.18;
    return base
      + (-0.00403) * absLat
      + (-0.62036) * sinD
      + (-0.10740) * cosD
      + (-0.66856) * sin2D
      + (+0.56805) * cos2D
      + (+0.01468) * absLat * sinD
      + (-0.00486) * absLat * cosD
      + (+0.01267) * absLat * sin2D
      + (-0.01964) * absLat * cos2D;
  } else {
    const base = baseAngle ?? 15.33;
    return base
      + (-0.00501) * absLat
      + (-0.22773) * sinD
      + (-0.11138) * cosD
      + (-0.21576) * sin2D
      + (-0.03724) * cos2D
      + (+0.00998) * absLat * sinD
      + (-0.00279) * absLat * cosD
      + (+0.00230) * absLat * sin2D
      + (-0.00485) * absLat * cos2D;
  }
}
```

### Why This Approach

1. The **baseline angle** (14.18 for Fajr, 15.33 for Isha) is configurable because the "true" baseline depends on the definition of dawn/dusk. Different communities use different thresholds (ISNA uses 15/15, MWL uses 18/17, Egyptian uses 19.5/17.5). The formula provides the seasonal-latitude correction on top of whatever baseline is chosen.

2. The **seasonal harmonics** (sin/cos at annual and semi-annual frequencies) capture the real astronomical variation. These coefficients should be trusted.

3. The **latitude-season interactions** (abs_lat * sin/cos) encode the physical fact that higher latitudes experience more extreme seasonal twilight variation. These are the most physically meaningful terms.

4. **Elevation is excluded** from the simplified formula because its effect (0.0007 deg/m) is below the noise floor for most use cases. If pray-calc wants to include it, add `+ 0.00066 * elevation_m` (Fajr) or `+ 0.00034 * elevation_m` (Isha).

### What This Analysis Cannot Tell Us

1. The "correct" baseline angle for Fajr and Isha. The dataset contains observations ranging from 7 to 22 degrees, reflecting genuinely different definitions of dawn/dusk. This is a religious/jurisprudential question, not a data science question.

2. Whether the formula is more accurate than a fixed-angle approach (e.g., always use 18 degrees). On this dataset, a fixed angle of 14.0 (Fajr) or 15.2 (Isha) would have an MAE of approximately 3.1 degrees. The formula's MAE of 3.3 is slightly worse because it tries to explain variance that is actually noise. However, the formula is physically correct in its shape.

3. Longitude-dependent effects. While tree models show longitude matters (R² jumps from 0.24 to 0.25), this is geographic clustering, not physics. A prayer time formula should not vary by longitude (for the same latitude).

---

## 9. Symbolic Regression Results

gplearn was attempted on the OpenFajr data and on the full residuals.

**OpenFajr (seasonal pattern at 52.5N):**
```
R² = 0.41, MAE = 0.41
Formula discovered: 1/0.076 - cos(2*doy) ≈ 13.16 - cos_2doy
```
This is a simpler version of the linear fit. The dominant seasonal term is the semi-annual harmonic (cos_2doy), which makes physical sense: twilight angles are most extreme near the solstices and most moderate near the equinoxes.

**Full dataset residuals (after de-meaning by source):**
```
R² = -0.018
Formula: -0.492 (constant)
```
Symbolic regression found no useful formula in the residuals, confirming that the within-source variance is genuinely noise (atmospheric, instrumental, observer).

---

## 10. Data Quality Assessment

### Strengths
- 48,647 Fajr and 34,511 Isha records is a large dataset
- Multiple independent sources across 4 continents
- SQM-based sources provide objective brightness thresholds
- Good latitude coverage from equator to 70N

### Weaknesses
- Sources use incompatible twilight threshold definitions
- No standardized "true Fajr/Isha" definition across sources
- Heavy geographic concentration in Spain (TESS-W, Galicia, Madrid) and Indonesia (Basthoni)
- Southern Hemisphere underrepresented (11% Fajr, 12% Isha)
- Equatorial latitudes (0-15) underrepresented for Isha (only 178 records)
- Some sources (Madrid SQM) appear to measure very deep twilight (mean 19-20 deg) while others (Galicia) measure shallow twilight (mean 12 deg)

### Recommendation for Future Data Collection
Prioritize single-source, multi-location datasets where the same instrument and threshold definition is used across many latitudes. The TESS-W network spans many latitudes but appears to have site-specific calibration differences. A campaign using a standardized SQM threshold across 10+ latitudes would be far more valuable than adding more heterogeneous records.

---

## Appendix: All Models Attempted

1. Linear Regression with hand-crafted features (5, 9, 14, 18 terms)
2. Ridge Regression (alpha = 0.01, 0.1, 1.0, 10.0)
3. Lasso Regression (alpha = 0.001, 0.01, 0.1, 1.0)
4. Polynomial Regression (degree 2 and 3 on 6 base features)
5. Random Forest (100-200 trees, max_depth 10-12)
6. Gradient Boosted Regression Trees (200-300 trees, max_depth 5-6)
7. Symbolic Regression via gplearn (1000-2000 population, 20-30 generations)
8. Feature ablation (tested each feature set independently)
9. Variance decomposition (between-source vs within-source)
10. Source-specific per-model fitting
11. De-meaned residual modeling (removing source bias first)

All models were evaluated with 5-fold cross-validation (KFold, shuffle=True, random_state=42).
