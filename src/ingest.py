"""
Data ingestion and standardization pipeline.

Converts any incoming sighting record (from CSV, dict, or manual entry) to the
canonical format: { prayer, date_local, time_local, utc_offset, lat, lng, elevation_m, source, notes }

Input formats supported:
  - Dict with explicit lat/lng
  - Dict with location_name/city (geocoded via Nominatim)
  - CSV file with columns: prayer, date, time, location/lat/lng, utc_offset, source

Usage:
  from src.ingest import standardize_record, load_raw_csv

  records = load_raw_csv("data/raw/raw_sightings/new_source.csv")
"""

from __future__ import annotations

import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from src.geocode import geocode
from src.elevation import get_elevations_batch

log = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "raw_sightings"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

# Required fields after standardization
REQUIRED_FIELDS = {"prayer", "date_local", "time_local", "utc_offset", "lat", "lng"}

# Explicit allowlist of approved raw CSV files.
# Only these filenames are ingested by ingest_all_raw_csvs().
# Any new file written by the collection agent is silently skipped until
# a human reviews and adds it here.
#
# STRICT RULE: Only files with GENUINE OBSERVED prayer times qualify.
# "Observed" means a human observer or calibrated instrument (SQM, DSLR photometer)
# was physically present on a specific night and recorded the actual time they
# detected Fajr (dawn) or Isha (dusk). Back-calculated times from published mean
# angles (aggregate_monthly_*.csv, aggregate_seasonal.csv) are NOT allowed —
# those times are computed, not observed, making the dataset circular.
#
# NEVER add: aggregate_monthly_*.csv, aggregate_seasonal.csv, aladhan_*.csv,
# waktusolat_*.csv, jakim_*.csv, or any file where times come from an algorithm.
APPROVED_RAW_CSVS: frozenset[str] = frozenset(
    {
        # Kassim & Bahali 2017 — 13 nights, DSLR photometry, east-coast Malaysia
        "kassim_bahali_2017_malaysia.csv",
        # Moonsighting.com — genuine human eye-sighting reports
        "moonsighting_com_sightings.csv",
        # Per-date records from specific papers — SQM instrument measurements
        # on specific calendar nights. Approved after manual review.
        #
        # EXCLUDED — abdelhadi_2022_malaysia_sqm.csv (Y.A.-F. Abdel-Hadi & A.H. Hassan 2022,
        # IJAA doi:10.4236/ijaa.2022.121002): Confirmed that Tables 3-11 provide only
        # solar depression angles (no local clock times). All 8 Fajr + 12 Isha times in
        # this CSV were reverse-engineered from published Do angles. Exact Do==back-calc
        # matches (to 3 d.p.) confirm circularity. Paper is valid research but cannot
        # provide genuine per-night observation times for our pipeline.
        "khalifa_2018_saudi_desert.csv",
        # Hidayatulloh 2023 UIN Walisongo thesis — 10 nights SOOF+SQM, 2 sites in South Sulawesi
        # Bulukumba (Bortle 1, dark sky) + Takalar (Bortle 4, suburban). Makassar excluded (Bortle 9, LP).
        # Time column is inferred from published SQM depression angle (per-night instrument reading).
        "walisongo_2022_sulawesi_sqm.csv",
        # BRIN multistation SQM 2018 — per-night SQM readings from 8 Indonesian stations
        # (Agam, Bandung, Biak, Garut, Pasuruan, Pontianak, Sumedang, Subang)
        # Extracted by brin_multistation_processor.py from raw .dat files.
        # Reference: Damanhuri & Mukarram LAPAN 2022.
        "brin_multistation_fajr.csv",
        # NOTE: Shaukat 2015 Fajr and Isha Booklet — Blackburn Lancashire UK (1987-88),
        # Tando Adam Pakistan (1970), and Ithaca NY (1991) observations are all already
        # in verified_sightings.py. Do NOT add shaukat_2015_blackburn_uk.csv or
        # shaukat_2015_other_sites.csv here — they would create duplicates.
        # EXCLUDED — brin_multistation_isha.csv
        # The MPSAS zenith-threshold method detects zenith darkness (~13° depression at
        # equatorial stations), not Shafaq Abyad horizon disappearance (~17-18°). The 4-5°
        # systematic offset is confirmed. File retained for reference.
        # Kassim Bahali et al. 2019 IJMET — 8 clear-sky nights from Dungun (Malaysia) + Sabang (Indonesia)
        "kassim_bahali_2019_ijmet.csv",
        # Add new approved files here — must be genuine per-night observations
        "batusangkar_2024_spectral.csv",
        "umsu_medan_2024.csv",
        # EXCLUDED — openfajr_94992898.csv: duplicates the iCal feed loaded by
        # openfajr.py (same Birmingham data, slightly different coords bypass dedup)
        "madrid_sqm_10yr.csv", # Madrid Zenodo 10-year SQM (2012-2022) converted to verified sightings via inflection
        # EXCLUDED — global_sqm_harvester_results.csv: empty file (header only)
        # TESS-W photometer network (Zamorano et al. 2019) — Zenodo monthly archives.
        # Multi-station Spain/Europe sky brightness, photometric inflection method.
        # NOTE: tess_june2019.csv was the original single-file entry (wrong name — corrected
        # below). All monthly files use abbreviated month format (jun, not june).
        "tess_jun2017.csv",
        "tess_jul2017.csv",
        "tess_sep2017.csv",
        "tess_oct2017.csv",
        "tess_nov2017.csv",
        "tess_dec2017.csv",
        "tess_jan2018.csv",
        "tess_feb2018.csv",
        "tess_mar2018.csv",
        "tess_apr2018.csv",
        "tess_may2018.csv",
        "tess_jun2018.csv",
        "tess_jul2018.csv",
        "tess_sep2018.csv",
        "tess_oct2018.csv",
        "tess_nov2018.csv",
        "tess_dec2018.csv",
        "tess_jan2019.csv",
        "tess_feb2019.csv",
        "tess_mar2019.csv",
        "tess_apr2019.csv",
        "tess_may2019.csv",
        "tess_jun2019.csv",
        "tess_jul2019.csv",
        "tess_aug2019.csv",
        "tess_sep2019.csv",
        "tess_oct2019.csv",
        "tess_nov2019.csv",
        "tess_dec2019.csv",
        "tess_jan2020.csv",
        "tess_feb2020.csv",
        "tess_mar2020.csv",
        "tess_apr2020.csv",
        "tess_may2020.csv",
        "tess_jun2020.csv",
        "tess_jul2020.csv",
        "tess_aug2020.csv",
        # GaN-MN (Globe at Night Monitoring Network) — continuous SQM-LE data.
        # Multi-station global network, photometric inflection method, per-night records.
        "gan_mn_jan_2022.csv", "gan_mn_feb_2022.csv", "gan_mn_mar_2022.csv",
        "gan_mn_apr_2022.csv", "gan_mn_may_2022.csv", "gan_mn_jun_2022.csv",
        "gan_mn_jul_2022.csv", "gan_mn_aug_2022.csv", "gan_mn_sep_2022.csv",
        "gan_mn_oct_2022.csv", "gan_mn_nov_2022.csv", "gan_mn_dec_2022.csv",
        "gan_mn_jan_2023.csv", "gan_mn_feb_2023.csv", "gan_mn_mar_2023.csv",
        "gan_mn_apr_2023.csv", "gan_mn_may_2023.csv", "gan_mn_jun_2023.csv",
        "gan_mn_jul_2023.csv", "gan_mn_aug_2023.csv", "gan_mn_sep_2023.csv",
        "gan_mn_oct_2023.csv", "gan_mn_nov_2023.csv", "gan_mn_dec_2023.csv",
        "gan_mn_jan_2024.csv", "gan_mn_feb_2024.csv", "gan_mn_mar_2024.csv",
        "gan_mn_apr_2024.csv", "gan_mn_may_2024.csv", "gan_mn_jun_2024.csv",
        "gan_mn_jul_2024.csv", "gan_mn_august_2024.csv", "gan_mn_sep_2024.csv",
        "gan_mn_oct_2024.csv", "gan_mn_nov_2024.csv", "gan_mn_dec_2024.csv",
        "gan_mn_january_2025.csv", "gan_mn_feb_2025.csv", "gan_mn_mar_2025.csv",
        "gan_mn_apr_2025.csv", "gan_mn_may_2025.csv", "gan_mn_june_2025.csv",
        "gan_mn_jul_2025.csv", "gan_mn_aug_2025.csv", "gan_mn_sep_2025.csv",
        # Majadahonda (Madrid) SQM 2019 — Zenodo 5709962, inflection method
        "majadahonda_2019_sqm.csv",
        # Madrid UCM SQM evolution 2012-2022 — Zenodo 4633001, inflection method
        "madrid_sqm_evol.csv",
        # Galicia SQM Network 2015 — Zenodo 4977265, 4 stations, inflection method
        "galicia_sqm_2015.csv",
        # India twilight photometer 2009 — Zenodo 5541367, photometric inflection
        "india_twilight_photometer.csv",
        # Globe at Night citizen science twilight observations 2006-2024
        "globe_at_night_twilight.csv",
        # Abed 2015 Jordan J Islamic Studies — naked eye group observations, 2 desert sites
        "abed_2015_jordan.csv",
        # Rashed et al. 2022 IJMET — Wadi al Hitan Fayum Egypt, SQM measurement
        "fayum_egypt_2022_sqm.csv",
        # EXCLUDED — washetdonker_morning.csv: uses fixed MSAS threshold=15.0 crossing,
        # not photometric inflection. Produces median 7.4° angles (civil twilight, not Fajr).
        # 93.8% of records cluster at 7-8° with outliers up to 49° from light pollution.
        # EXCLUDED — bsrn_5site_twilight.csv, bsrn_all_twilight.csv, bsrn_caelus_twilight.csv,
        # surfrad_twilight.csv: BSRN/SURFRAD irradiance data detects civil sunrise at ~2°
        # depression, not Fajr/Isha at 12-18° depression. Not suitable for this dataset.
        # EXCLUDED — web_1472771404.csv, web_2748406846.csv, web_4414092721.csv,
        # web_5613061948.csv, web_6807547173.csv: All 5 files contain the same single record
        # (fajr 2017-09-24, lat=0.0, lng=0.0) — no coordinates, PDF parse artifact, useless.
    }
)

# Standard column aliases for CSV imports
COLUMN_ALIASES: dict[str, list[str]] = {
    "prayer":      ["prayer", "type", "salah", "salat", "twilight_type", "event_type"],
    "date_local":  ["date_local", "date", "obs_date", "observation_date"],
    "time_local":  ["time_local", "time", "obs_time", "local_time"],
    "utc_offset":  ["utc_offset", "tz_offset", "timezone_offset", "utc"],
    "lat":         ["lat", "latitude"],
    "lng":         ["lng", "lon", "longitude"],
    "elevation_m": ["elevation_m", "elevation", "elev", "elev_m", "alt_m"],
    "source":      ["source", "citation", "ref", "reference"],
    "notes":       ["notes", "note", "comments", "comment"],
    "city":        ["city", "location", "location_name", "place", "site"],
    "country":     ["country"],
    "utc_datetime": ["utc_datetime", "utc_dt", "datetime_utc"],
}


def _resolve_column(header: str) -> Optional[str]:
    """Map a CSV column name to a canonical field name."""
    h = header.lower().strip()
    for canonical, aliases in COLUMN_ALIASES.items():
        if h in aliases:
            return canonical
    return None


def standardize_record(raw: dict) -> Optional[dict]:
    """
    Normalize a raw sighting record to the canonical format.

    If lat/lng are missing but a city/location_name is present, geocodes the location.
    If elevation_m is missing or 0, leaves it as 0 (pipeline will call Open-Elevation).

    Returns None if the record cannot be standardized (missing critical fields).
    """
    record = {}

    # Copy all fields, normalising keys
    for raw_key, value in raw.items():
        canonical = _resolve_column(raw_key) or raw_key.lower().strip()
        record[canonical] = str(value).strip() if value is not None else ""

    # Geocode if lat/lng missing
    lat = record.get("lat") or record.get("latitude")
    lng = record.get("lng") or record.get("longitude") or record.get("lon")

    if not lat or not lng or lat == "0" or lng == "0":
        city = record.get("city") or record.get("location") or record.get("location_name")
        if city:
            country = record.get("country")
            coords = geocode(city, country_hint=country)
            if coords:
                record["lat"] = str(coords[0])
                record["lng"] = str(coords[1])
                log.info("geocoded %r → %s, %s", city, record["lat"], record["lng"])
            else:
                log.warning("could not geocode %r — skipping record", city)
                return None
        else:
            log.warning("record missing both lat/lng and city: %s", raw)
            return None

    # Type coercion
    try:
        record["lat"] = float(record["lat"])
        record["lng"] = float(record["lng"])
    except (ValueError, TypeError):
        log.warning("invalid lat/lng in record: %s", raw)
        return None

    record["elevation_m"] = float(record.get("elevation_m") or 0)
    record["utc_offset"] = float(record.get("utc_offset") or 0)

    # If utc_datetime is present but date_local/time_local are missing, derive them.
    # Treat the UTC time as the local time with utc_offset=0.
    utc_dt_raw = record.get("utc_datetime") or ""
    if utc_dt_raw and not record.get("date_local"):
        cleaned = utc_dt_raw.replace("+00:00", "").rstrip("Z").strip()
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
            try:
                dt = datetime.strptime(cleaned, fmt)
                record["date_local"] = dt.strftime("%Y-%m-%d")
                record["time_local"] = dt.strftime("%H:%M")
                record["utc_offset"] = 0.0
                break
            except ValueError:
                pass

    # Normalise prayer name — also map dawn/dusk event_type values
    prayer = (record.get("prayer") or "").lower().strip()
    if prayer in ("fajr", "subh", "subuh", "dawn"):
        record["prayer"] = "fajr"
    elif prayer in ("isha", "isya", "isha'", "ishaa", "dusk", "shafaq"):
        record["prayer"] = "isha"
    else:
        log.warning("unknown prayer type %r — skipping", prayer)
        return None

    # Validate date
    date_raw = record.get("date_local") or ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(date_raw, fmt)
            record["date_local"] = dt.strftime("%Y-%m-%d")
            break
        except ValueError:
            pass
    else:
        log.warning("could not parse date %r — skipping", date_raw)
        return None

    # Validate time
    time_raw = record.get("time_local") or ""
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p"):
        try:
            t = datetime.strptime(time_raw, fmt)
            record["time_local"] = t.strftime("%H:%M")
            break
        except ValueError:
            pass
    else:
        log.warning("could not parse time %r — skipping", time_raw)
        return None

    # Ensure required fields
    for field in REQUIRED_FIELDS:
        if field not in record:
            log.warning("missing required field %r — skipping", field)
            return None

    # Defaults for optional fields
    record.setdefault("source", "unspecified")
    record.setdefault("notes", "")

    return record


def load_raw_csv(path: str | Path) -> list[dict]:
    """
    Load a raw sighting CSV, standardize each row, and return valid records.

    The CSV can have column names in any supported alias format (see COLUMN_ALIASES).
    Rows that cannot be standardized are skipped with a warning.
    """
    path = Path(path)
    records = []
    skipped = 0

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            result = standardize_record(dict(row))
            if result:
                records.append(result)
            else:
                skipped += 1
                log.debug("row %d skipped from %s", i, path.name)

    log.info("loaded %d records from %s (%d skipped)", len(records), path.name, skipped)
    return records


def ingest_all_raw_csvs(lookup_elevation: bool = True) -> list[dict]:
    """
    Load and standardize approved CSV files from data/raw/raw_sightings/.

    Only files listed in APPROVED_RAW_CSVS are ingested. Any other files
    present in the directory are logged as warnings but skipped — this
    prevents the collection agent from accidentally poisoning the dataset
    with circular or computed data.

    Optionally looks up elevation for records with elevation_m == 0.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        log.info("No raw CSV files found in %s", RAW_DIR)
        return []

    approved = [f for f in csv_files if f.name in APPROVED_RAW_CSVS]
    skipped = [f.name for f in csv_files if f.name not in APPROVED_RAW_CSVS]
    if skipped:
        log.warning(
            "Skipping %d non-approved file(s) in raw_sightings/: %s",
            len(skipped),
            ", ".join(sorted(skipped)[:10]) + (f" ... (+{len(skipped)-10} more)" if len(skipped) > 10 else ""),
        )

    all_records: list[dict] = []
    for f in approved:
        records = load_raw_csv(f)
        all_records.extend(records)
        log.info("  %s: %d records", f.name, len(records))

    if lookup_elevation:
        missing = [r for r in all_records if r.get("elevation_m", 0) == 0]
        if missing:
            locs = [(r["lat"], r["lng"]) for r in missing]
            elevs = get_elevations_batch(locs)
            for r, elev in zip(missing, elevs):
                if elev is not None:
                    r["elevation_m"] = elev

    return all_records
