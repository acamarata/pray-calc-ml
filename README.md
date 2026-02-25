# pray-calc-ml

[![npm version](https://img.shields.io/npm/v/pray-calc-ml.svg)](https://www.npmjs.com/package/pray-calc-ml)
[![CI](https://github.com/acamarata/pray-calc-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/acamarata/pray-calc-ml/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Machine learning calibration for Islamic prayer times. Fits optimal Fajr/Isha depression angles to observed mosque announcement data using weighted least-squares regression. Zero runtime dependencies.

## The problem

Islamic prayer time software requires two depression angles below the horizon: one for Fajr (pre-dawn), one for Isha (post-dusk). These angles determine how early Fajr starts and how late Isha ends. The major juristic organizations each publish their own angles — ISNA uses 15°/15°, MWL uses 18°/17°, UOIF uses 12°/12° — but local mosque practice often differs.

If you have recorded announcement times from a mosque and want to know what angles they imply, this library fits those angles from data.

## Installation

```bash
npm install pray-calc-ml
# or
pnpm add pray-calc-ml
```

## Quick Start

```ts
import { calibrateAngles, predictFajr } from 'pray-calc-ml';

// Observed Fajr and Isha times from a mosque in New York (UTC-4, summer)
const observations = [
  { date: new Date('2024-06-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.75, isha: 21.58 },
  { date: new Date('2024-06-15'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.68, isha: 21.67 },
  { date: new Date('2024-07-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.80, isha: 21.55 },
  { date: new Date('2024-07-15'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.95, isha: 21.38 },
];

const result = calibrateAngles(observations);

console.log(result.angles);
// { fajrAngle: 15.2, ishaAngle: 14.8 }

console.log(`RMS error: ${result.rmsMinutes.toFixed(2)} min`);
// RMS error: 0.31 min

// Use the calibrated angles to predict times on a new date
const fajr = predictFajr(new Date('2024-08-01'), 40.71, -74.01, -4, result.angles.fajrAngle);
console.log(`Predicted Fajr: ${Math.floor(fajr)}:${String(Math.round((fajr % 1) * 60)).padStart(2, '0')}`);
// Predicted Fajr: 3:52
```

## API

### `calibrateAngles(observations, options?)`

Finds the Fajr and Isha depression angles that minimize weighted squared residuals across all observations.

**Parameters**

| Name | Type | Description |
| --- | --- | --- |
| `observations` | `Observation[]` | Recorded prayer times. Each entry may have `fajr`, `isha`, or both. |
| `options` | `CalibrationOptions` | Optional solver configuration. |

**Returns** `CalibrationResult`

| Field | Type | Description |
| --- | --- | --- |
| `angles` | `CalibratedAngles` | Best-fit `fajrAngle` and `ishaAngle` in degrees. |
| `rmsMinutes` | `number` | Root-mean-square residual across all observations, in minutes. |
| `observationCount` | `number` | Effective observation count (dual entries count as 1, single as 0.5). |
| `residuals` | `Array<{fajrMin, ishaMin}>` | Per-observation residuals in minutes (positive: predicted later than observed). |

**Throws** if neither Fajr nor Isha has at least 2 observations. One side can have fewer — it falls back to `fajrAngle0`/`ishaAngle0`.

---

### `scoreAngles(observations, fajrAngle, ishaAngle)`

Evaluates a known pair of angles (e.g. ISNA's 15°/15°) against your observation data without fitting.

**Returns** `ScoreResult`

| Field | Type | Description |
| --- | --- | --- |
| `rmsMinutes` | `number` | Weighted RMS error in minutes. |
| `fajrBiasMinutes` | `number` | Signed mean Fajr error (positive: angles predict Fajr too late). |
| `ishaBiasMinutes` | `number` | Signed mean Isha error. |
| `residuals` | `Array<{fajrMin, ishaMin}>` | Per-observation residuals. |

---

### `predictFajr(date, lat, lng, tz, fajrAngle)`

Predict the Fajr time (fractional hours, local) for a given depression angle.

Returns `NaN` at extreme latitudes where the sun never reaches the required depth.

---

### `predictIsha(date, lat, lng, tz, ishaAngle)`

Predict the Isha time (fractional hours, local) for a given depression angle.

---

### `Observation` type

```ts
interface Observation {
  date:   Date;    // local calendar date
  lat:    number;  // decimal degrees (south = negative)
  lng:    number;  // decimal degrees (west = negative)
  tz:     number;  // UTC offset in hours (e.g. -5 for EST)
  fajr?:  number;  // fractional hours local time (e.g. 4.5 = 4:30 AM)
  isha?:  number;  // fractional hours local time (e.g. 21.25 = 9:15 PM)
  weight?: number; // relative weight, default 1.0
}
```

---

### `CalibrationOptions` type

```ts
interface CalibrationOptions {
  fajrAngle0?: number;  // initial guess (default 15.0)
  ishaAngle0?: number;  // initial guess (default 15.0)
  fajrMin?:   number;   // angle lower bound (default 10.0)
  fajrMax?:   number;   // angle upper bound (default 22.0)
  ishaMin?:   number;   // angle lower bound (default 10.0)
  ishaMax?:   number;   // angle upper bound (default 22.0)
  maxIter?:   number;   // solver iterations (default 200)
  tol?:       number;   // convergence tolerance in degrees (default 1e-5)
}
```

## Architecture

The calibration uses golden-section search — a derivative-free optimizer for smooth unimodal functions — over each depression angle independently. Fajr and Isha do not interact in the solar geometry, so they can be solved separately, which avoids the complexity of 2D optimization while producing exact results for the least-squares objective.

The internal solar ephemeris uses Jean Meeus's low-precision formulas (same as `pray-calc`). Accuracy is within 1 minute for latitudes below 65° and dates between 1900 and 2100. No atmospheric refraction correction is applied — the calibration absorbs systematic offsets like refraction into the fitted angle, which is the correct approach when fitting to real-world observations.

See [Architecture](https://github.com/acamarata/pray-calc-ml/wiki/Architecture) in the wiki for a full discussion.

## Collecting observations

Times are fractional hours in local time — the same format `pray-calc`'s `getTimes()` returns. To convert HH:MM:SS from a mosque schedule: `h + m/60 + s/3600`.

```ts
function hmsToFrac(h: number, m: number, s = 0): number {
  return h + m / 60 + s / 3600;
}

// 4:32 AM = 4.533...
const fajr = hmsToFrac(4, 32);

// 9:15 PM = 21.25
const isha = hmsToFrac(21, 15);
```

At least 2 observations per prayer are required for a meaningful fit. More is better: 8-12 observations spread across seasons gives stable results for most locations.

## Compatibility

| Environment | Status |
| --- | --- |
| Node.js 20, 22, 24 | Tested in CI |
| ESM (import) | Supported (`dist/index.mjs`) |
| CommonJS (require) | Supported (`dist/index.cjs`) |
| Browsers / bundlers | Works (no Node built-ins used) |
| TypeScript | Full `.d.ts` and `.d.mts` included |

## Documentation

Full API reference, worked examples, and solver internals are in the [GitHub Wiki](https://github.com/acamarata/pray-calc-ml/wiki).

## Related

- [pray-calc](https://github.com/acamarata/pray-calc) — Islamic prayer times with a physics-grounded dynamic angle algorithm
- [nrel-spa](https://github.com/acamarata/nrel-spa) — NREL Solar Position Algorithm in pure JavaScript
- [moon-sighting](https://github.com/acamarata/moon-sighting) — lunar crescent visibility with JPL DE442S ephemeris

## License

MIT. See [LICENSE](LICENSE).
