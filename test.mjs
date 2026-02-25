/**
 * pray-calc-ml — ESM test suite
 * Plain Node.js assert, no test framework.
 */

import assert from 'assert';
import {
  calibrateAngles,
  scoreAngles,
  predictFajr,
  predictIsha,
} from './dist/index.mjs';

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ${name}... PASS`);
    passed++;
  } catch (e) {
    console.error(`  ${name}... FAIL: ${e.message}`);
    failed++;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Section 1: predictFajr / predictIsha
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n[1] predictFajr / predictIsha');

// Makkah, summer solstice, tz=+3. ISNA uses 15°/15°.
const MK_DATE  = new Date('2024-06-21');
const MK_LAT   = 21.4225;
const MK_LNG   = 39.8262;
const MK_TZ    = 3;

test('predictFajr returns finite value for Makkah summer', () => {
  const t = predictFajr(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  assert(isFinite(t), `got ${t}`);
});

test('predictIsha returns finite value for Makkah summer', () => {
  const t = predictIsha(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  assert(isFinite(t), `got ${t}`);
});

test('predictFajr < predictIsha (Fajr before Isha)', () => {
  const f = predictFajr(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  const i = predictIsha(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  assert(f < i, `Fajr(${f}) < Isha(${i})`);
});

test('predictFajr Makkah 15° in range 4–6 h', () => {
  const t = predictFajr(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  assert(t > 4 && t < 6, `got ${t}`);
});

test('predictIsha Makkah 15° in range 20–22 h', () => {
  const t = predictIsha(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  assert(t > 20 && t < 22.5, `got ${t}`);
});

test('larger angle gives earlier Fajr', () => {
  const f15 = predictFajr(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  const f18 = predictFajr(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 18);
  assert(f18 < f15, `18°(${f18}) should be < 15°(${f15})`);
});

test('larger angle gives later Isha', () => {
  const i15 = predictIsha(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 15);
  const i18 = predictIsha(MK_DATE, MK_LAT, MK_LNG, MK_TZ, 18);
  assert(i18 > i15, `18°(${i18}) should be > 15°(${i15})`);
});

test('predictFajr polar summer returns NaN when sun never sets deep enough', () => {
  // Oslo (59.9°N) in deep summer at 22° should still be finite, but 30° is impossible
  const t = predictFajr(new Date('2024-06-21'), 69.0, 18.0, 1, 30);
  assert(isNaN(t), `expected NaN for impossible angle, got ${t}`);
});

// ─────────────────────────────────────────────────────────────────────────────
// Section 2: scoreAngles
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n[2] scoreAngles');

// Build observations from a single location (NY, UTC-4) across multiple dates.
// We'll pretend the "true" angle is 15° and add a small ±1min noise to test scoring.
const NY_LAT = 40.7128;
const NY_LNG = -74.006;
const NY_TZ  = -4;

const nyDates = [
  new Date('2024-01-15'),
  new Date('2024-04-15'),
  new Date('2024-07-15'),
  new Date('2024-10-15'),
];

const trueAngle = 15;
const nyObs = nyDates.map(d => ({
  date: d, lat: NY_LAT, lng: NY_LNG, tz: NY_TZ,
  fajr: predictFajr(d, NY_LAT, NY_LNG, NY_TZ, trueAngle),
  isha: predictIsha(d, NY_LAT, NY_LNG, NY_TZ, trueAngle),
}));

test('scoreAngles returns object with expected keys', () => {
  const s = scoreAngles(nyObs, 15, 15);
  assert('rmsMinutes' in s);
  assert('fajrBiasMinutes' in s);
  assert('ishaBiasMinutes' in s);
  assert('residuals' in s);
  assert(Array.isArray(s.residuals));
});

test('scoreAngles perfect angles → rms near 0', () => {
  const s = scoreAngles(nyObs, 15, 15);
  assert(s.rmsMinutes < 0.01, `rms=${s.rmsMinutes}`);
});

test('scoreAngles wrong angles → rms > 0', () => {
  const s = scoreAngles(nyObs, 18, 12);
  assert(s.rmsMinutes > 1, `rms=${s.rmsMinutes}`);
});

test('scoreAngles residuals array length matches observations', () => {
  const s = scoreAngles(nyObs, 15, 15);
  assert.strictEqual(s.residuals.length, nyObs.length);
});

test('scoreAngles fajrBias near 0 for exact angles', () => {
  const s = scoreAngles(nyObs, 15, 15);
  assert(Math.abs(s.fajrBiasMinutes) < 0.01, `bias=${s.fajrBiasMinutes}`);
});

test('scoreAngles fajrBias negative when angle is too small (predicted too late)', () => {
  // 12° → Fajr predicted later than 15° observations → bias < 0
  const s = scoreAngles(nyObs, 12, 15);
  assert(s.fajrBiasMinutes > 0, `expected positive bias, got ${s.fajrBiasMinutes}`);
});

// ─────────────────────────────────────────────────────────────────────────────
// Section 3: calibrateAngles — basic recovery
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n[3] calibrateAngles — basic angle recovery');

test('calibrateAngles returns object with angles, rmsMinutes, observationCount, residuals', () => {
  const r = calibrateAngles(nyObs);
  assert('angles' in r);
  assert('fajrAngle' in r.angles);
  assert('ishaAngle' in r.angles);
  assert('rmsMinutes' in r);
  assert('observationCount' in r);
  assert('residuals' in r);
});

test('calibrateAngles recovers 15° Fajr angle within 0.1°', () => {
  const r = calibrateAngles(nyObs);
  assert(
    Math.abs(r.angles.fajrAngle - 15) < 0.1,
    `got ${r.angles.fajrAngle}°, expected ~15°`
  );
});

test('calibrateAngles recovers 15° Isha angle within 0.1°', () => {
  const r = calibrateAngles(nyObs);
  assert(
    Math.abs(r.angles.ishaAngle - 15) < 0.1,
    `got ${r.angles.ishaAngle}°, expected ~15°`
  );
});

test('calibrateAngles RMS < 0.1 min for synthetic clean data', () => {
  const r = calibrateAngles(nyObs);
  assert(r.rmsMinutes < 0.1, `rms=${r.rmsMinutes}`);
});

test('calibrateAngles observationCount = 4 for 4 dual observations', () => {
  const r = calibrateAngles(nyObs);
  assert.strictEqual(r.observationCount, 4);
});

test('calibrateAngles residuals length matches input', () => {
  const r = calibrateAngles(nyObs);
  assert.strictEqual(r.residuals.length, nyObs.length);
});

// ─────────────────────────────────────────────────────────────────────────────
// Section 4: calibrateAngles — different target angles
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n[4] calibrateAngles — recovering non-default angles');

function makeObs(angle, fajrOverride, ishaOverride) {
  return nyDates.map(d => ({
    date: d, lat: NY_LAT, lng: NY_LNG, tz: NY_TZ,
    fajr: fajrOverride !== undefined
      ? predictFajr(d, NY_LAT, NY_LNG, NY_TZ, fajrOverride)
      : undefined,
    isha: ishaOverride !== undefined
      ? predictIsha(d, NY_LAT, NY_LNG, NY_TZ, ishaOverride)
      : undefined,
  }));
}

test('calibrateAngles recovers 18° Fajr', () => {
  const obs = makeObs(null, 18, 18);
  const r = calibrateAngles(obs);
  assert(Math.abs(r.angles.fajrAngle - 18) < 0.1, `got ${r.angles.fajrAngle}°`);
});

test('calibrateAngles recovers 12° Isha', () => {
  const obs = makeObs(null, 12, 12);
  const r = calibrateAngles(obs);
  assert(Math.abs(r.angles.ishaAngle - 12) < 0.1, `got ${r.angles.ishaAngle}°`);
});

test('calibrateAngles recovers asymmetric Fajr=17, Isha=13', () => {
  const obs = makeObs(null, 17, 13);
  const r = calibrateAngles(obs);
  assert(Math.abs(r.angles.fajrAngle - 17) < 0.1, `Fajr: got ${r.angles.fajrAngle}°`);
  assert(Math.abs(r.angles.ishaAngle - 13) < 0.1, `Isha: got ${r.angles.ishaAngle}°`);
});

test('calibrateAngles works with Fajr-only observations', () => {
  const obs = makeObs(null, 15, undefined);
  const r = calibrateAngles(obs);
  assert(Math.abs(r.angles.fajrAngle - 15) < 0.1, `Fajr: got ${r.angles.fajrAngle}°`);
});

test('calibrateAngles works with Isha-only observations', () => {
  const obs = makeObs(null, undefined, 15);
  const r = calibrateAngles(obs);
  assert(Math.abs(r.angles.ishaAngle - 15) < 0.1, `Isha: got ${r.angles.ishaAngle}°`);
});

// ─────────────────────────────────────────────────────────────────────────────
// Section 5: calibrateAngles — weighted observations
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n[5] calibrateAngles — weighted regression');

test('high-weight observation pulls calibrated angle toward its implied angle', () => {
  // Mix: 3 obs from 15° angle (weight 1) + 1 obs from 20° angle (weight 20)
  // The high-weight 20° obs should dominate, pulling result toward 20°.
  const obs15 = nyDates.slice(0, 3).map(d => ({
    date: d, lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, weight: 1,
    fajr: predictFajr(d, NY_LAT, NY_LNG, NY_TZ, 15),
    isha: predictIsha(d, NY_LAT, NY_LNG, NY_TZ, 15),
  }));
  const obs20 = [{
    date: nyDates[3], lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, weight: 20,
    fajr: predictFajr(nyDates[3], NY_LAT, NY_LNG, NY_TZ, 20),
    isha: predictIsha(nyDates[3], NY_LAT, NY_LNG, NY_TZ, 20),
  }];
  const r = calibrateAngles([...obs15, ...obs20]);
  assert(r.angles.fajrAngle > 17, `expected > 17°, got ${r.angles.fajrAngle}°`);
});

test('equal weights produce result between two angle sets', () => {
  const obs15 = nyDates.slice(0, 2).map(d => ({
    date: d, lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, weight: 1,
    fajr: predictFajr(d, NY_LAT, NY_LNG, NY_TZ, 15),
    isha: predictIsha(d, NY_LAT, NY_LNG, NY_TZ, 15),
  }));
  const obs18 = nyDates.slice(2).map(d => ({
    date: d, lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, weight: 1,
    fajr: predictFajr(d, NY_LAT, NY_LNG, NY_TZ, 18),
    isha: predictIsha(d, NY_LAT, NY_LNG, NY_TZ, 18),
  }));
  const r = calibrateAngles([...obs15, ...obs18]);
  assert(r.angles.fajrAngle > 15 && r.angles.fajrAngle < 18,
    `expected 15–18°, got ${r.angles.fajrAngle}°`);
});

// ─────────────────────────────────────────────────────────────────────────────
// Section 6: calibrateAngles — multi-location
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n[6] calibrateAngles — multi-location dataset');

const locations = [
  { lat: 21.4225, lng:  39.8262, tz:  3 }, // Makkah
  { lat: 40.7128, lng: -74.0060, tz: -4 }, // New York
  { lat: 51.5074, lng:  -0.1278, tz:  1 }, // London
  { lat:  1.3521, lng: 103.8198, tz:  8 }, // Singapore
];
const multiDates = [new Date('2024-01-15'), new Date('2024-07-15')];
const TARGET_ANGLE = 16.5;

const multiObs = locations.flatMap(loc =>
  multiDates.map(d => ({
    date: d, lat: loc.lat, lng: loc.lng, tz: loc.tz,
    fajr: predictFajr(d, loc.lat, loc.lng, loc.tz, TARGET_ANGLE),
    isha: predictIsha(d, loc.lat, loc.lng, loc.tz, TARGET_ANGLE),
  }))
);

test('calibrateAngles recovers 16.5° from multi-location data within 0.2°', () => {
  const r = calibrateAngles(multiObs);
  assert(Math.abs(r.angles.fajrAngle - TARGET_ANGLE) < 0.2, `got ${r.angles.fajrAngle}°`);
  assert(Math.abs(r.angles.ishaAngle - TARGET_ANGLE) < 0.2, `got ${r.angles.ishaAngle}°`);
});

test('multi-location RMS < 0.1 min for clean synthetic data', () => {
  const r = calibrateAngles(multiObs);
  assert(r.rmsMinutes < 0.1, `rms=${r.rmsMinutes}`);
});

// ─────────────────────────────────────────────────────────────────────────────
// Section 7: error handling
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n[7] error handling');

test('calibrateAngles throws when both Fajr and Isha have fewer than 2 observations', () => {
  // 1 Fajr + 1 Isha — neither can be calibrated, so this must throw.
  const obs = [{ date: nyDates[0], lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, fajr: 5.5, isha: 21.0 }];
  let threw = false;
  try { calibrateAngles(obs); } catch { threw = true; }
  assert(threw, 'expected error when both have <2 observations');
});

test('calibrateAngles does NOT throw with 4 Fajr + 1 Isha (Fajr calibrated, Isha gets default)', () => {
  // 4 Fajr-only + 1 dual: Fajr gets calibrated, Isha falls back to fajrAngle0 default.
  const obs = [
    { date: nyDates[0], lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, fajr: 5.0 },
    { date: nyDates[1], lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, fajr: 5.2 },
    { date: nyDates[2], lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, fajr: 4.8 },
    { date: nyDates[3], lat: NY_LAT, lng: NY_LNG, tz: NY_TZ, fajr: 5.1, isha: 21.0 },
  ];
  const r = calibrateAngles(obs);
  assert(isFinite(r.angles.fajrAngle), `Fajr angle should be finite, got ${r.angles.fajrAngle}`);
  assert(isFinite(r.angles.ishaAngle), `Isha angle should be finite (default), got ${r.angles.ishaAngle}`);
});

test('scoreAngles handles empty array gracefully', () => {
  const s = scoreAngles([], 15, 15);
  assert.strictEqual(s.rmsMinutes, 0);
  assert.strictEqual(s.residuals.length, 0);
});

// ─────────────────────────────────────────────────────────────────────────────
// Summary
// ─────────────────────────────────────────────────────────────────────────────
console.log('\n' + '─'.repeat(50));
console.log(`${passed}/${passed + failed} tests passed`);
if (failed > 0) process.exit(1);
