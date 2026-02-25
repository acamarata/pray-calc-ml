# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-02-25

### Added

- `calibrateAngles()` — fit optimal Fajr/Isha depression angles to observed mosque announcement data via weighted least-squares (golden-section search)
- `scoreAngles()` — evaluate fixed depression angles against observations, returning RMS error and signed bias per prayer
- `predictFajr()` / `predictIsha()` — predict prayer times from a depression angle using an internal Jean Meeus solar ephemeris (no pray-calc dependency at runtime)
- Full TypeScript source with strict mode and dual CJS/ESM build via tsup
- `CalibrationOptions` for solver bounds and convergence control
- Graceful handling of Fajr-only or Isha-only datasets
- 32-test ESM suite and 6-test CJS suite
- CI matrix: Node 20, 22, 24
