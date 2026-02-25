# Guide: Collecting Observations

This guide covers how to build a dataset of observed prayer times suitable for calibration.

## What you need

Each observation is a date, location, UTC offset, and one or both of (Fajr, Isha) as local times. You do not need Dhuhr, Asr, or Maghrib — those times do not depend on twilight depression angles.

```ts
interface Observation {
  date:    Date;
  lat:     number;   // decimal degrees
  lng:     number;   // decimal degrees
  tz:      number;   // UTC offset in hours
  fajr?:   number;   // fractional hours (e.g. 4.75 = 4:45 AM)
  isha?:   number;   // fractional hours (e.g. 21.5 = 9:30 PM)
  weight?: number;   // default 1.0
}
```

## Converting HH:MM to fractional hours

```ts
function hmsToFrac(h: number, m: number, s = 0): number {
  return h + m / 60 + s / 3600;
}

// 4:32 AM
const fajr = hmsToFrac(4, 32);   // 4.5333...

// 9:15 PM
const isha = hmsToFrac(21, 15);  // 21.25
```

## How many observations?

**Minimum:** 2 per prayer. Below 2, the calibration cannot distinguish the angle from the default.

**Recommended:** 8-12 observations spread across at least two seasons (e.g. winter and summer). Seasonal spread is important because solar declination varies — an angle fit only to summer observations may drift by 1-2 minutes in winter.

**Optimal dataset properties:**
- Dates spread across all four seasons or at least two solstice/equinox periods
- If the mosque is at a middle latitude (30-55°N/S), 8 observations is usually enough
- High-latitude locations (above 55°) benefit from more observations in summer, when twilight geometry changes rapidly day-to-day

## Sources of data

**Printed mosque schedules.** Most mosques print a monthly or yearly timetable. Photographing or scanning this is the fastest way to build a dataset.

**Mosque apps and websites.** Many mosque websites publish annual prayer calendars. Scrape one column for Fajr and one for Isha.

**Adhan systems.** If you operate the mosque software, you can log each call to prayer.

**Islamic centers (ISNA, MWL, etc.).** If the mosque explicitly follows a known method (e.g. ISNA 15°/15°), `scoreAngles` will confirm this — no need to calibrate.

## Consistency

Use times from the same source throughout a dataset. Mixing an automated system with hand-adjusted times adds noise.

If the mosque rounds times to the nearest 5 minutes, the minimum achievable RMS is around 1.5 minutes (half of 5). This is normal. An RMS below 2 minutes is a good result for real-world data.

## Weighting

Use the `weight` field to de-emphasize less reliable observations:

```ts
// Older records you're less confident about
{ date: new Date('2022-06-01'), ..., fajr: 3.75, weight: 0.5 },

// Recent, verified observations
{ date: new Date('2024-06-01'), ..., fajr: 3.75, weight: 1.0 },
```

Weights are relative, not absolute. Setting all weights to 2.0 produces the same result as all 1.0.

## Example dataset (8 observations, New York)

```ts
const observations = [
  // Winter
  { date: new Date('2024-01-15'), lat: 40.71, lng: -74.01, tz: -5, fajr: 5.97, isha: 18.42 },
  { date: new Date('2024-02-15'), lat: 40.71, lng: -74.01, tz: -5, fajr: 5.62, isha: 18.92 },
  // Spring
  { date: new Date('2024-04-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 5.12, isha: 20.37 },
  { date: new Date('2024-05-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 4.52, isha: 20.87 },
  // Summer
  { date: new Date('2024-06-21'), lat: 40.71, lng: -74.01, tz: -4, fajr: 3.65, isha: 21.78 },
  { date: new Date('2024-08-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 4.15, isha: 21.17 },
  // Autumn
  { date: new Date('2024-10-01'), lat: 40.71, lng: -74.01, tz: -4, fajr: 5.28, isha: 19.45 },
  { date: new Date('2024-11-01'), lat: 40.71, lng: -74.01, tz: -5, fajr: 5.62, isha: 18.12 },
];
```

Note: New York uses UTC-5 (EST) in winter and UTC-4 (EDT) in summer. Always use the actual UTC offset in effect on each date.

---

*[Home](Home) | [API Reference](API-Reference) | [Architecture](Architecture) | [Guide: Integrating with pray-calc](Guide-Integrating-with-pray-calc)*
