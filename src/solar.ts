/**
 * Minimal solar ephemeris used internally by pray-calc-ml.
 *
 * Provides the solar declination and equation-of-time needed to compute
 * sunrise/sunset/twilight times without requiring pray-calc at build time.
 * The same Jean Meeus formulas used in pray-calc's getSolarEphemeris.ts.
 */

/** Julian Day Number for a Date at UT noon. */
export function jdn(date: Date): number {
  const y = date.getUTCFullYear();
  const m = date.getUTCMonth() + 1;
  const d = date.getUTCDate();
  const a = Math.floor((14 - m) / 12);
  const yr = y + 4800 - a;
  const mo = m + 12 * a - 3;
  return d + Math.floor((153 * mo + 2) / 5) + 365 * yr + Math.floor(yr / 4) - Math.floor(yr / 100) + Math.floor(yr / 400) - 32045;
}

interface SolarData {
  /** Solar declination in radians. */
  declRad: number;
  /** Equation of time in hours (positive = sun transits early). */
  eqtHours: number;
}

/** Jean Meeus solar declination and equation of time for a given JDN. */
export function solar(jd: number): SolarData {
  const T = (jd - 2451545.0) / 36525.0;
  const L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360;
  const M  = (357.52911 + T * (35999.05029 - T * 0.0001537)) % 360;
  const Mrad = (M * Math.PI) / 180;
  const C = Math.sin(Mrad) * (1.914602 - T * (0.004817 + 0.000014 * T))
          + Math.sin(2 * Mrad) * (0.019993 - 0.000101 * T)
          + Math.sin(3 * Mrad) * 0.000289;
  const sunLon = L0 + C;
  const omega = 125.04 - 1934.136 * T;
  const lambda = sunLon - 0.00569 - 0.00478 * Math.sin((omega * Math.PI) / 180);
  const eps0 = 23 + 26 / 60 + 21.448 / 3600 - T * (46.8150 / 3600 + T * (0.00059 / 3600 - T * 0.001813 / 3600));
  const eps = eps0 + 0.00256 * Math.cos((omega * Math.PI) / 180);
  const epsRad = (eps * Math.PI) / 180;
  const lambdaRad = (lambda * Math.PI) / 180;
  const declRad = Math.asin(Math.sin(epsRad) * Math.sin(lambdaRad));

  // Equation of time (minutes)
  const y = Math.tan(epsRad / 2) ** 2;
  const L0rad = (L0 * Math.PI) / 180;
  const eqtMin = (4 / Math.PI) * (
    y * Math.sin(2 * L0rad)
    - 2 * Math.sin(Mrad)
    + 4 * Math.sin(Mrad) * y * Math.cos(2 * L0rad)
    - 0.5 * y * y * Math.sin(4 * L0rad)
    - 1.25 * Math.sin(2 * Mrad)
  ) * (180 / Math.PI);
  const eqtHours = eqtMin / 60;

  return { declRad, eqtHours };
}

/**
 * Compute the time (fractional hours, local time) when the sun reaches a given
 * altitude (degrees) before/after solar noon.
 *
 * @param jd         Julian Day Number (UT noon)
 * @param lat        Latitude in decimal degrees
 * @param lng        Longitude in decimal degrees
 * @param tz         UTC offset in hours
 * @param altDeg     Target altitude in degrees (negative for depression below horizon)
 * @returns [rise, set] as fractional hours in local time, or NaN if sun never reaches alt
 */
export function horizonCrossing(
  jd: number,
  lat: number,
  lng: number,
  tz: number,
  altDeg: number,
): [number, number] {
  const { declRad, eqtHours } = solar(jd);
  const latRad = (lat * Math.PI) / 180;
  const altRad = (altDeg * Math.PI) / 180;

  const cosH = (Math.sin(altRad) - Math.sin(latRad) * Math.sin(declRad))
    / (Math.cos(latRad) * Math.cos(declRad));

  if (cosH < -1 || cosH > 1) return [NaN, NaN]; // polar day/night

  const H = (Math.acos(cosH) * 180) / Math.PI; // hour angle in degrees

  // Solar noon in local time
  const noon = 12 - eqtHours - lng / 15 + tz;

  const rise = noon - H / 15;
  const set  = noon + H / 15;
  return [rise, set];
}
