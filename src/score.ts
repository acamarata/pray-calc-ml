/**
 * Score an existing set of angles against observations.
 *
 * Use this to evaluate how well a known method (e.g. ISNA's 15°/15°)
 * fits a collection of observed mosque announcements before calibrating.
 */

import { predictFajr, predictIsha } from './predict.js';
import type { Observation } from './types.js';

export interface ScoreResult {
  /** Weighted RMS error across all observations, in minutes. */
  rmsMinutes: number;
  /** Mean signed error for Fajr in minutes (positive = predicted late). */
  fajrBiasMinutes: number;
  /** Mean signed error for Isha in minutes. */
  ishaBiasMinutes: number;
  /** Per-observation residuals in minutes. */
  residuals: Array<{ fajrMin: number | null; ishaMin: number | null }>;
}

/**
 * Evaluate fixed depression angles against observed prayer times.
 *
 * @param observations - Observed Fajr/Isha times.
 * @param fajrAngle    - Fajr depression angle in degrees.
 * @param ishaAngle    - Isha depression angle in degrees.
 */
export function scoreAngles(
  observations: Observation[],
  fajrAngle: number,
  ishaAngle: number,
): ScoreResult {
  let totalWeightedSS = 0;
  let totalWeight = 0;
  let fajrWeightedBias = 0, fajrWeightCount = 0;
  let ishaWeightedBias = 0, ishaWeightCount = 0;

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
        fajrWeightedBias += w * fajrMin;
        fajrWeightCount += w;
      }
    }
    if (o.isha !== undefined) {
      const pred = predictIsha(o.date, o.lat, o.lng, o.tz, ishaAngle);
      if (isFinite(pred)) {
        ishaMin = (pred - o.isha) * 60;
        totalWeightedSS += w * ishaMin * ishaMin;
        totalWeight += w;
        ishaWeightedBias += w * ishaMin;
        ishaWeightCount += w;
      }
    }
    return { fajrMin, ishaMin };
  });

  return {
    rmsMinutes: totalWeight > 0 ? Math.sqrt(totalWeightedSS / totalWeight) : 0,
    fajrBiasMinutes: fajrWeightCount > 0 ? fajrWeightedBias / fajrWeightCount : 0,
    ishaBiasMinutes: ishaWeightCount > 0 ? ishaWeightedBias / ishaWeightCount : 0,
    residuals,
  };
}
