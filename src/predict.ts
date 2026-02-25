/**
 * Predict Fajr and Isha times given depression angles.
 *
 * Uses the internal solar module to avoid requiring pray-calc at calibration time.
 * Accuracy matches pray-calc within ~0.5 min for most locations (no atmospheric
 * refraction correction here — the calibration absorbs that into the fitted angle).
 */

import { jdn, horizonCrossing } from './solar.js';

/**
 * Predict Fajr time (fractional hours, local) for a given depression angle.
 * Returns NaN if the sun never reaches that depth below the horizon.
 */
export function predictFajr(
  date: Date,
  lat: number,
  lng: number,
  tz: number,
  fajrAngle: number,
): number {
  const jd = jdn(new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), 12)));
  const altDeg = -(fajrAngle); // depression → negative altitude
  const [rise] = horizonCrossing(jd, lat, lng, tz, altDeg);
  return rise;
}

/**
 * Predict Isha time (fractional hours, local) for a given depression angle.
 * Returns NaN if the sun never reaches that depth below the horizon.
 */
export function predictIsha(
  date: Date,
  lat: number,
  lng: number,
  tz: number,
  ishaAngle: number,
): number {
  const jd = jdn(new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), 12)));
  const altDeg = -(ishaAngle);
  const [, set] = horizonCrossing(jd, lat, lng, tz, altDeg);
  return set;
}
