/**
 * pray-calc-ml — machine learning calibration for Islamic prayer times.
 *
 * Fits optimal Fajr/Isha depression angles to observed mosque announcement data
 * using weighted least-squares regression. Zero runtime dependencies.
 *
 * Main exports:
 *   calibrateAngles  - Fit depression angles to observed prayer times
 *   scoreAngles      - Evaluate fixed angles against observations
 *   predictFajr      - Predict Fajr time for a given angle
 *   predictIsha      - Predict Isha time for a given angle
 */

export { calibrateAngles } from './calibrate.js';
export { scoreAngles } from './score.js';
export { predictFajr, predictIsha } from './predict.js';

export type {
  Observation,
  CalibratedAngles,
  CalibrationResult,
  CalibrationOptions,
} from './types.js';

export type { ScoreResult } from './score.js';
