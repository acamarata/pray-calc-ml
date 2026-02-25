# API Reference

## `calibrateAngles(observations, options?)`

Finds the Fajr and Isha depression angles that minimize the weighted sum of squared residuals across all observations.

```ts
function calibrateAngles(
  observations: Observation[],
  options?: CalibrationOptions,
): CalibrationResult
```

### Parameters

**`observations: Observation[]`**

An array of recorded prayer times. Each entry may supply a Fajr time, an Isha time, or both. Entries missing a field are ignored for the corresponding angle.

At least 2 observations are required per prayer. If one prayer has fewer than 2 observations, that angle falls back to the initial guess (`fajrAngle0` or `ishaAngle0`). If both prayers have fewer than 2, the function throws.

**`options?: CalibrationOptions`**

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `fajrAngle0` | `number` | `15.0` | Initial Fajr angle guess in degrees |
| `ishaAngle0` | `number` | `15.0` | Initial Isha angle guess in degrees |
| `fajrMin` | `number` | `10.0` | Minimum allowed Fajr angle |
| `fajrMax` | `number` | `22.0` | Maximum allowed Fajr angle |
| `ishaMin` | `number` | `10.0` | Minimum allowed Isha angle |
| `ishaMax` | `number` | `22.0` | Maximum allowed Isha angle |
| `maxIter` | `number` | `200` | Maximum solver iterations |
| `tol` | `number` | `1e-5` | Convergence tolerance in degrees |

### Returns `CalibrationResult`

| Field | Type | Description |
| --- | --- | --- |
| `angles` | `CalibratedAngles` | Best-fit `fajrAngle` and `ishaAngle` in degrees |
| `rmsMinutes` | `number` | Weighted RMS residual in minutes |
| `observationCount` | `number` | Effective count (dual=1, single=0.5) |
| `residuals` | `Array<{fajrMin, ishaMin}>` | Per-observation residuals in minutes |

Residuals are signed: positive means the model predicted later than the observation.

### Throws

- If neither Fajr nor Isha has at least 2 observations.

---

## `scoreAngles(observations, fajrAngle, ishaAngle)`

Evaluates a fixed pair of depression angles against observation data without fitting.

```ts
function scoreAngles(
  observations: Observation[],
  fajrAngle: number,
  ishaAngle: number,
): ScoreResult
```

### Returns `ScoreResult`

| Field | Type | Description |
| --- | --- | --- |
| `rmsMinutes` | `number` | Weighted RMS error in minutes |
| `fajrBiasMinutes` | `number` | Signed mean Fajr error (positive: angle predicts Fajr too late) |
| `ishaBiasMinutes` | `number` | Signed mean Isha error |
| `residuals` | `Array<{fajrMin, ishaMin}>` | Per-observation residuals |

Use this to compare multiple standard methods against your data:

```ts
import { scoreAngles } from 'pray-calc-ml';

const obs = [/* ... */];

const isna = scoreAngles(obs, 15, 15);  // ISNA
const mwl  = scoreAngles(obs, 18, 17);  // MWL
const uoif = scoreAngles(obs, 12, 12);  // UOIF

console.log('ISNA RMS:', isna.rmsMinutes.toFixed(2));
console.log('MWL RMS:',  mwl.rmsMinutes.toFixed(2));
console.log('UOIF RMS:', uoif.rmsMinutes.toFixed(2));
```

---

## `predictFajr(date, lat, lng, tz, fajrAngle)`

Predict the Fajr time for a given date, location, and depression angle.

```ts
function predictFajr(
  date: Date,
  lat: number,
  lng: number,
  tz: number,
  fajrAngle: number,
): number  // fractional hours, local time; NaN at polar extremes
```

---

## `predictIsha(date, lat, lng, tz, ishaAngle)`

Predict the Isha time for a given date, location, and depression angle.

```ts
function predictIsha(
  date: Date,
  lat: number,
  lng: number,
  tz: number,
  ishaAngle: number,
): number  // fractional hours, local time; NaN at polar extremes
```

---

## `Observation` type

```ts
interface Observation {
  date:    Date;    // local calendar date
  lat:     number;  // decimal degrees, south = negative
  lng:     number;  // decimal degrees, west = negative
  tz:      number;  // UTC offset in hours (e.g. -5 for EST, +3 for AST)
  fajr?:   number;  // fractional hours local time (e.g. 4.5 = 4:30 AM)
  isha?:   number;  // fractional hours local time (e.g. 21.25 = 9:15 PM)
  weight?: number;  // relative weight, default 1.0
}
```

---

## `CalibratedAngles` type

```ts
interface CalibratedAngles {
  fajrAngle: number;  // degrees below horizon (positive)
  ishaAngle: number;  // degrees below horizon (positive)
}
```

---

*[Home](Home) | [Architecture](Architecture) | [Guide: Collecting Observations](Guide-Collecting-Observations) | [Guide: Integrating with pray-calc](Guide-Integrating-with-pray-calc)*
