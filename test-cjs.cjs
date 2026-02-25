/**
 * pray-calc-ml — CJS test suite
 * Focused subset verifying CommonJS imports work correctly.
 */
'use strict';

const assert = require('assert');
const { calibrateAngles, scoreAngles, predictFajr, predictIsha } = require('./dist/index.cjs');

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

console.log('\n[CJS] Exports and basic functionality');

test('all exports are functions', () => {
  assert.strictEqual(typeof calibrateAngles, 'function');
  assert.strictEqual(typeof scoreAngles, 'function');
  assert.strictEqual(typeof predictFajr, 'function');
  assert.strictEqual(typeof predictIsha, 'function');
});

// Makkah, summer, UTC+3, ISNA 15°
const MK = { date: new Date('2024-06-21'), lat: 21.4225, lng: 39.8262, tz: 3 };

test('predictFajr returns finite number', () => {
  const t = predictFajr(MK.date, MK.lat, MK.lng, MK.tz, 15);
  assert(isFinite(t), `got ${t}`);
});

test('predictIsha returns finite number', () => {
  const t = predictIsha(MK.date, MK.lat, MK.lng, MK.tz, 15);
  assert(isFinite(t), `got ${t}`);
});

// Build 4 synthetic observations for NY at 15°
const NY = { lat: 40.7128, lng: -74.006, tz: -4 };
const dates = [
  new Date('2024-01-15'),
  new Date('2024-04-15'),
  new Date('2024-07-15'),
  new Date('2024-10-15'),
];
const obs = dates.map(d => ({
  date: d, lat: NY.lat, lng: NY.lng, tz: NY.tz,
  fajr: predictFajr(d, NY.lat, NY.lng, NY.tz, 15),
  isha: predictIsha(d, NY.lat, NY.lng, NY.tz, 15),
}));

test('calibrateAngles recovers 15° angles', () => {
  const r = calibrateAngles(obs);
  assert(Math.abs(r.angles.fajrAngle - 15) < 0.1, `Fajr: ${r.angles.fajrAngle}°`);
  assert(Math.abs(r.angles.ishaAngle - 15) < 0.1, `Isha: ${r.angles.ishaAngle}°`);
});

test('scoreAngles perfect score < 0.01 min RMS', () => {
  const s = scoreAngles(obs, 15, 15);
  assert(s.rmsMinutes < 0.01, `rms=${s.rmsMinutes}`);
});

test('calibrateAngles result has all expected fields', () => {
  const r = calibrateAngles(obs);
  assert('angles' in r && 'rmsMinutes' in r && 'observationCount' in r && 'residuals' in r);
});

console.log('\n' + '─'.repeat(50));
console.log(`${passed}/${passed + failed} CJS tests passed`);
if (failed > 0) process.exit(1);
