/**
 * Angle calibration via iterative weighted least-squares.
 *
 * Given a set of observed Fajr and/or Isha times, finds the depression angles
 * (fajrAngle, ishaAngle) that minimize the weighted sum of squared residuals
 * between predicted and observed times.
 *
 * The solver decouples the two parameters: Fajr observations constrain fajrAngle
 * independently from Isha observations, which constrain ishaAngle. Each is solved
 * via a 1D golden-section search over the allowed angle range.
 */

import { predictFajr, predictIsha } from './predict.js';
import type { Observation, CalibratedAngles, CalibrationResult, CalibrationOptions } from './types.js';

/** Golden-section search for the minimum of f(x) on [a, b]. */
function goldenSection(
  f: (x: number) => number,
  a: number,
  b: number,
  tol: number,
  maxIter: number,
): number {
  const phi = (Math.sqrt(5) - 1) / 2; // 1/φ ≈ 0.618
  let x1 = b - phi * (b - a);
  let x2 = a + phi * (b - a);
  let f1 = f(x1);
  let f2 = f(x2);
  for (let i = 0; i < maxIter && b - a > tol; i++) {
    if (f1 < f2) {
      b = x2; x2 = x1; f2 = f1;
      x1 = b - phi * (b - a); f1 = f(x1);
    } else {
      a = x1; x1 = x2; f1 = f2;
      x2 = a + phi * (b - a); f2 = f(x2);
    }
  }
  return (a + b) / 2;
}

/**
 * Calibrate Fajr and Isha depression angles to fit observed prayer time data.
 *
 * @param observations - Array of observed prayer times. Each entry may supply
 *   a Fajr time, an Isha time, or both. Entries missing a field are ignored for
 *   the corresponding angle.
 * @param options - Solver configuration and angle bounds.
 * @returns Calibrated angles and diagnostic information.
 *
 * @throws If fewer than 2 Fajr or 2 Isha observations are provided.
 *   (Two is the minimum for a meaningful fit.)
 */
export function calibrateAngles(
  observations: Observation[],
  options: CalibrationOptions = {},
): CalibrationResult {
  const {
    fajrMin = 10,
    fajrMax = 22,
    ishaMin = 10,
    ishaMax = 22,
    maxIter = 200,
    tol = 1e-5,
  } = options;

  const fajrObs = observations.filter(o => o.fajr !== undefined);
  const ishaObs = observations.filter(o => o.isha !== undefined);

  if (fajrObs.length < 2 && ishaObs.length < 2) {
    throw new Error(
      `calibrateAngles: need at least 2 Fajr or 2 Isha observations ` +
      `(got Fajr=${fajrObs.length}, Isha=${ishaObs.length})`
    );
  }

  const { fajrAngle0 = 15.0, ishaAngle0 = 15.0 } = options;

  // Weighted sum-of-squares for Fajr at a given angle
  function fajrLoss(angle: number): number {
    let wss = 0;
    for (const o of fajrObs) {
      const pred = predictFajr(o.date, o.lat, o.lng, o.tz, angle);
      if (!isFinite(pred)) continue; // polar day/night — skip
      const w = o.weight ?? 1;
      const diff = (pred - o.fajr!) * 60; // minutes
      wss += w * diff * diff;
    }
    return wss;
  }

  // Weighted sum-of-squares for Isha at a given angle
  function ishaLoss(angle: number): number {
    let wss = 0;
    for (const o of ishaObs) {
      const pred = predictIsha(o.date, o.lat, o.lng, o.tz, angle);
      if (!isFinite(pred)) continue;
      const w = o.weight ?? 1;
      const diff = (pred - o.isha!) * 60;
      wss += w * diff * diff;
    }
    return wss;
  }

  // Calibrate each angle independently. If there are fewer than 2 observations
  // for one angle, fall back to the initial guess (no data to fit against).
  const fajrAngle = fajrObs.length >= 2
    ? goldenSection(fajrLoss, fajrMin, fajrMax, tol, maxIter)
    : fajrAngle0;
  const ishaAngle = ishaObs.length >= 2
    ? goldenSection(ishaLoss, ishaMin, ishaMax, tol, maxIter)
    : ishaAngle0;

  // Compute residuals and RMS
  let totalWeightedSS = 0;
  let totalWeight = 0;

  const residuals = observations.map(o => {
    const w = o.weight ?? 1;
    let fajrMin: number | null = null;
    let ishaMin: number | null = null;

    if (o.fajr !== undefined) {
      const pred = predictFajr(o.date, o.lat, o.lng, o.tz, fajrAngle);
      if (isFinite(pred)) {
        fajrMin = (pred - o.fajr) * 60;
        totalWeightedSS += w * fajrMin * fajrMin;
        totalWeight += w;
      }
    }
    if (o.isha !== undefined) {
      const pred = predictIsha(o.date, o.lat, o.lng, o.tz, ishaAngle);
      if (isFinite(pred)) {
        ishaMin = (pred - o.isha) * 60;
        totalWeightedSS += w * ishaMin * ishaMin;
        totalWeight += w;
      }
    }
    return { fajrMin, ishaMin };
  });

  const rmsMinutes = totalWeight > 0 ? Math.sqrt(totalWeightedSS / totalWeight) : 0;
  const observationCount = (fajrObs.length + ishaObs.length) / 2;

  return {
    angles: { fajrAngle, ishaAngle },
    rmsMinutes,
    observationCount,
    residuals,
  };
}
