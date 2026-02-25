# Architecture

## Problem formulation

The library's job is angle recovery: given a set of (date, location, observed_time) triples, find the depression angle `θ` such that the predicted twilight time best matches the observations in a weighted least-squares sense.

For Fajr:

```
minimize  Σ w_i · (predict_fajr(date_i, lat_i, lng_i, tz_i, θ) - fajr_i)²
   θ∈[θ_min, θ_max]
```

Isha uses an identical objective. The two angles are independent in the underlying solar geometry, so the 2D problem separates into two independent 1D minimizations.

## Solver: golden-section search

The objective is smooth and unimodal over the physically meaningful angle range [10°, 22°]. Solar twilight times are monotone functions of the depression angle (larger angle → earlier Fajr, later Isha), so the squared-residual sum is strictly convex in `θ` for well-distributed observations.

Golden-section search finds the minimum of a unimodal function on a closed interval without computing derivatives. It works by maintaining a bracket `[a, b]` and evaluating two interior points at each step, shrinking the bracket by a factor of `1/φ ≈ 0.618` per iteration. After `n` iterations, the bracket width is `(b-a) / φⁿ`. With the default tolerance of `1e-5°` on a starting interval of `[10, 22]` (width 12°), convergence takes at most 60 iterations.

This is correct and efficient. There is no need for gradient computation or Jacobians, and the solver never diverges. The implementation is 15 lines.

## Solar ephemeris

The internal ephemeris implements Jean Meeus's low-precision solar position formulas from *Astronomical Algorithms* (2nd ed., Chapter 25). It computes:

- Solar declination (degrees) for a given Julian Day Number
- Equation of time (hours)

From these, the local hour angle `H` at which the sun reaches altitude `h` is:

```
cos(H) = (sin(h) - sin(lat)·sin(dec)) / (cos(lat)·cos(dec))
```

where `h = -θ` (depression angle as negative altitude). The sunrise and sunset times (in local hours) are then:

```
rise = noon - H/15
set  = noon + H/15
```

**Accuracy.** The Meeus low-precision formulas are accurate to approximately 0.01° in solar longitude, translating to roughly 0.5-1 min in twilight time prediction for latitudes below 65°. This is more than adequate for calibration, where the fitted angle absorbs any systematic offset (atmospheric refraction, altitude above sea level, observer conventions).

No atmospheric refraction correction is applied, unlike `pray-calc`'s `getTimes()` which applies a standard refraction model. The calibration absorbs the refraction correction into the fitted angle, which is the right behavior when fitting to observed announcements.

## Why not use pray-calc directly?

`pray-calc` is listed as a peer dependency, not a runtime dependency. The calibration process only needs to map an angle to a predicted time — a lightweight operation covered by the internal ephemeris. This avoids a circular dependency problem and keeps the calibration bundle lean.

When using calibrated angles in production, you pass `fajrAngle` and `ishaAngle` directly to `pray-calc`'s `getTimes()` via the `angles` option. The `predict*` functions in this library are for internal calibration use and quick sanity checks, not for production time generation.

## Convergence and stability

Golden-section search is guaranteed to converge on any continuous function. The objective is strictly convex for any dataset with variance in date (seasonal variation) or latitude. The only degenerate case is all observations from the same date at the same location, which produces a perfectly flat loss function in one dimension — the returned angle is then the initial guess, which is benign.

The solver returns `NaN`-guarded predictions: polar-extreme observations where the sun never reaches the required depth are silently skipped in the loss computation. This prevents a handful of high-latitude winter observations from dominating the residual.

## Numerical precision

All computations use standard 64-bit IEEE 754 floating-point. The golden-section search uses exact arithmetic throughout (no numerical differentiation, no matrix inversions). The final angle is accurate to within `tol` degrees, which at `tol=1e-5` translates to sub-millisecond time error.

---

*[Home](Home) | [API Reference](API-Reference) | [Guide: Collecting Observations](Guide-Collecting-Observations) | [Guide: Integrating with pray-calc](Guide-Integrating-with-pray-calc)*
