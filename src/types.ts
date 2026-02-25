/**
 * Types for pray-calc-ml — machine learning calibration for Islamic prayer times.
 */

/**
 * A single observed prayer time announcement.
 *
 * All times are fractional hours in local time (same convention as pray-calc's getTimes).
 * For example, 5.5 = 5:30 AM, 20.25 = 8:15 PM.
 */
export interface Observation {
  /** Observer's local date for this observation. */
  date: Date;
  /** Latitude in decimal degrees (south = negative). */
  lat: number;
  /** Longitude in decimal degrees (west = negative). */
  lng: number;
  /** UTC offset in hours (e.g. -5 for EST). */
  tz: number;
  /**
   * Observed Fajr time as fractional hours in local time.
   * Omit if this observation does not constrain Fajr.
   */
  fajr?: number;
  /**
   * Observed Isha time as fractional hours in local time.
   * Omit if this observation does not constrain Isha.
   */
  isha?: number;
  /**
   * Relative weight of this observation (default: 1.0).
   * Higher weight makes the calibration prioritize this data point.
   * Useful for down-weighting older or less reliable records.
   */
  weight?: number;
}

/**
 * Calibrated Fajr and Isha depression angles that best fit the observations.
 */
export interface CalibratedAngles {
  /** Calibrated Fajr depression angle in degrees (positive, measured below horizon). */
  fajrAngle: number;
  /** Calibrated Isha depression angle in degrees (positive, measured below horizon). */
  ishaAngle: number;
}

/**
 * Detailed report from a calibration run.
 */
export interface CalibrationResult {
  /** The calibrated angles. */
  angles: CalibratedAngles;
  /**
   * Root-mean-square error of the fit in minutes.
   * Lower is better. A value under 2 min is excellent for mosque data.
   */
  rmsMinutes: number;
  /**
   * Number of observations used in the fit.
   * Fajr-only and Isha-only observations each count as 0.5.
   */
  observationCount: number;
  /**
   * Per-observation residuals in minutes (positive = predicted later than observed).
   * Index matches the input observations array.
   */
  residuals: Array<{ fajrMin: number | null; ishaMin: number | null }>;
}

/**
 * Options for calibrateAngles().
 */
export interface CalibrationOptions {
  /**
   * Initial Fajr angle guess in degrees (default: 15.0).
   * The solver starts here and iterates toward the minimum.
   */
  fajrAngle0?: number;
  /**
   * Initial Isha angle guess in degrees (default: 15.0).
   */
  ishaAngle0?: number;
  /**
   * Minimum allowed Fajr angle (default: 10.0).
   * Physically, angles below 10° cannot produce astronomical twilight.
   */
  fajrMin?: number;
  /**
   * Maximum allowed Fajr angle (default: 22.0).
   */
  fajrMax?: number;
  /**
   * Minimum allowed Isha angle (default: 10.0).
   */
  ishaMin?: number;
  /**
   * Maximum allowed Isha angle (default: 22.0).
   */
  ishaMax?: number;
  /**
   * Maximum number of solver iterations (default: 100).
   */
  maxIter?: number;
  /**
   * Convergence tolerance in degrees (default: 1e-4).
   * The solver stops when the angle update is smaller than this.
   */
  tol?: number;
}
