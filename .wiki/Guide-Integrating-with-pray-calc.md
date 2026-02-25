# Guide: Integrating with pray-calc

`pray-calc-ml` fits angles from data. `pray-calc` uses those angles to generate prayer times. This guide shows how to connect them.

## Installation

```bash
npm install pray-calc pray-calc-ml
```

## Step 1: Collect observations

Build a dataset of recorded mosque times. See [Guide: Collecting Observations](Guide-Collecting-Observations) for details.

```ts
const observations = [
  { date: new Date('2024-06-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.75, isha: 21.58 },
  { date: new Date('2024-07-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.82, isha: 21.52 },
  { date: new Date('2024-08-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 4.15, isha: 21.12 },
  { date: new Date('2024-09-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 4.58, isha: 20.58 },
];
```

## Step 2: Calibrate

```ts
import { calibrateAngles } from 'pray-calc-ml';

const result = calibrateAngles(observations);
const { fajrAngle, ishaAngle } = result.angles;

console.log(`Fajr: ${fajrAngle.toFixed(2)}°, Isha: ${ishaAngle.toFixed(2)}°`);
console.log(`RMS error: ${result.rmsMinutes.toFixed(2)} min`);
```

## Step 3: Generate prayer times with pray-calc

Pass the calibrated angles to `pray-calc`'s `getTimes()` via the `angles` option:

```ts
import { getTimes } from 'pray-calc';

const today = new Date();
const lat = 40.71, lng = -74.01, tz = -4;

const times = getTimes(today, lat, lng, tz, { angles: { fajrAngle, ishaAngle } });

console.log(times.Fajr, times.Sunrise, times.Dhuhr, times.Asr, times.Maghrib, times.Isha);
```

## Step 4: Verify the fit

Before deploying, check the RMS and residuals to confirm the calibration quality:

```ts
import { scoreAngles } from 'pray-calc-ml';

// Compare ISNA standard against your observations
const isnaScore = scoreAngles(observations, 15, 15);
console.log(`ISNA RMS: ${isnaScore.rmsMinutes.toFixed(2)} min`);
console.log(`ISNA Fajr bias: ${isnaScore.fajrBiasMinutes.toFixed(1)} min`);

// Compare calibrated angles
const calibScore = scoreAngles(observations, fajrAngle, ishaAngle);
console.log(`Calibrated RMS: ${calibScore.rmsMinutes.toFixed(2)} min`);
```

If the calibrated RMS is more than 3 minutes, something is off — either the observations are inconsistent, the location coordinates are wrong, or the UTC offset changed mid-dataset.

## Caching the calibration

Run calibration once offline and store the resulting angles. There is no need to calibrate at runtime.

```ts
// Store in your config or database
const config = {
  fajrAngle: 15.2,
  ishaAngle: 14.8,
};

// At runtime, just use the stored angles
const times = getTimes(new Date(), lat, lng, tz, { angles: config });
```

## Handling seasonal drift

Depression angles are constants — they do not change with season. The calibration finds a single angle that minimizes error across your entire dataset. If you find that the calibrated angle gives a large error in one season (e.g. winter), you may need more observations from that season to stabilize the fit.

You can also run separate calibrations per season and check consistency:

```ts
const winterObs = observations.filter(o => {
  const m = o.date.getMonth();
  return m === 11 || m <= 1; // Dec, Jan, Feb
});

const summerObs = observations.filter(o => {
  const m = o.date.getMonth();
  return m >= 5 && m <= 7; // Jun, Jul, Aug
});

const winter = calibrateAngles(winterObs);
const summer = calibrateAngles(summerObs);

const diff = Math.abs(winter.angles.fajrAngle - summer.angles.fajrAngle);
if (diff > 0.5) {
  console.warn(`Seasonal inconsistency: ${diff.toFixed(2)}° spread. Check data quality.`);
}
```

---

*[Home](Home) | [API Reference](API-Reference) | [Architecture](Architecture) | [Guide: Collecting Observations](Guide-Collecting-Observations)*
