# pray-calc-ml

Machine learning calibration for Islamic prayer times. Fits optimal Fajr/Isha depression angles to observed mosque announcement data using weighted least-squares regression.

Zero runtime dependencies. Works in Node.js, browsers, and any ESM/CJS bundler.

## Pages

- [API Reference](API-Reference) — full function signatures, parameters, return types
- [Architecture](Architecture) — solver design, solar ephemeris, accuracy analysis
- [Guide: Collecting Observations](Guide-Collecting-Observations) — how to record mosque times and build a dataset
- [Guide: Integrating with pray-calc](Guide-Integrating-with-pray-calc) — calibrate then use in a full prayer time app

## Quick start

```bash
npm install pray-calc-ml
```

```ts
import { calibrateAngles } from 'pray-calc-ml';

const result = calibrateAngles([
  { date: new Date('2024-06-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.75, isha: 21.58 },
  { date: new Date('2024-07-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.80, isha: 21.55 },
  { date: new Date('2024-08-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 4.12, isha: 21.15 },
  { date: new Date('2024-09-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 4.55, isha: 20.67 },
]);

console.log(result.angles);      // { fajrAngle: 15.2, ishaAngle: 14.8 }
console.log(result.rmsMinutes);  // 0.31
```

## Repository

[github.com/acamarata/pray-calc-ml](https://github.com/acamarata/pray-calc-ml)
