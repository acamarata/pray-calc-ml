"""
Extract prayer time observation data from academic papers and web pages.

Handles:
  - HTML pages: extract tables using BeautifulSoup
  - PDF files: extract text and tables using PyMuPDF (fitz)
  - iCal feeds: parse VEVENT blocks for prayer times
  - Plain text: regex-based extraction of time/date patterns

The extractor tries to identify tables that contain human-observed prayer
times by looking for characteristic column patterns:
  - Date columns (YYYY-MM-DD, DD/MM/YYYY, day-of-year)
  - Time columns (HH:MM, decimal hours)
  - Prayer type indicators (Fajr, Isha, Subuh, Isyak, dawn, dusk)
  - Angle columns (D0, depression, altitude, degrees)
  - Location columns (latitude, longitude, site name)

Only rows with enough information to back-calculate a solar depression angle
are kept. The minimum required set is: date + time + prayer type. Lat/lng
may already be known for the site.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

# HTTP session with appropriate headers
SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
)

# Time pattern: HH:MM or H:MM (24h)
TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")

# Date patterns
DATE_RE_YMD = re.compile(r"\b(20\d{2}|19\d{2})[-/](\d{1,2})[-/](\d{1,2})\b")
DATE_RE_DMY = re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](20\d{2}|19\d{2})\b")
DATE_MONTH_NAMES = re.compile(
    r"\b(\d{1,2})\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+"
    r"(20\d{2}|19\d{2})\b",
    re.IGNORECASE,
)

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Prayer type keywords
FAJR_WORDS = re.compile(
    r"\b(fajr|subuh|subh|fajr[- ]sadiq|true dawn|dawn|morning twilight|"
    r"astronomical morning|صبح|فجر|صلاة الفجر)\b",
    re.IGNORECASE,
)
ISHA_WORDS = re.compile(
    r"\b(isha|isyak|isya|shafaq|isha[\'']?|evening twilight|dusk|"
    r"astronomical dusk|عشاء)\b",
    re.IGNORECASE,
)

# Angle keywords (solar depression angle D0)
ANGLE_WORDS = re.compile(
    r"\b(D[0o]|depression|altitude|angle|degree|°|solar position)\b",
    re.IGNORECASE,
)

# Coordinate keywords
LAT_RE = re.compile(r"lat(?:itude)?[:\s=]*([+-]?\d+\.?\d*)[°\s]*([NS]?)", re.IGNORECASE)
LNG_RE = re.compile(r"lon(?:g(?:itude)?)?[:\s=]*([+-]?\d+\.?\d*)[°\s]*([EW]?)", re.IGNORECASE)
ELEV_RE = re.compile(r"elev(?:ation)?[:\s=]*(\d+\.?\d*)\s*m", re.IGNORECASE)


def fetch_url(url: str, timeout: int = 30) -> tuple[bytes | None, str]:
    """
    Fetch a URL and return (content_bytes, content_type).

    Returns (None, '') on failure.
    """
    try:
        resp = SESSION.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "").lower()
        return resp.content, ct
    except requests.RequestException as e:
        log.warning("fetch_url %s: %s", url, e)
        return None, ""


def extract_from_url(url: str) -> list[dict]:
    """
    Main entry point: fetch a URL and extract prayer time observations.

    Returns a list of raw record dicts with at least:
        prayer, date_local, time_local, source
    and optionally: lat, lng, elevation_m, utc_offset, notes.
    """
    content, ct = fetch_url(url)
    if content is None:
        return []

    time.sleep(1)  # polite rate limiting

    if "pdf" in ct or url.lower().endswith(".pdf"):
        return _extract_from_pdf(content, url)
    elif "text/calendar" in ct or "ical" in ct or url.lower().endswith(".ics"):
        return _extract_from_ical(content.decode("utf-8", errors="replace"), url)
    else:
        html = content.decode("utf-8", errors="replace")
        return _extract_from_html(html, url)


def _extract_from_html(html: str, source_url: str) -> list[dict]:
    """Extract prayer time observations from an HTML page."""
    soup = BeautifulSoup(html, "lxml")

    records: list[dict] = []

    # Extract site metadata from page text
    text = soup.get_text(" ", strip=True)
    site_meta = _extract_site_meta(text)

    # Try HTML tables first
    tables = soup.find_all("table")
    for table in tables:
        rows = _parse_html_table(table, source_url, site_meta)
        records.extend(rows)

    # If no table data, try paragraph-level extraction
    if not records:
        records.extend(_extract_from_text(text, source_url, site_meta))

    return records


def _parse_html_table(table_tag: Any, source_url: str, site_meta: dict) -> list[dict]:
    """Parse an HTML <table> element for prayer time observation rows."""
    rows = table_tag.find_all("tr")
    if len(rows) < 3:
        return []

    # Extract header row
    headers = []
    header_row = rows[0]
    for cell in header_row.find_all(["th", "td"]):
        headers.append(cell.get_text(" ", strip=True).lower())

    if not headers:
        return []

    # Classify columns
    col_date = _find_col(headers, ["date", "tarikh", "tanggal", "تاريخ", "day", "hari"])
    col_time_fajr = _find_col(headers, ["fajr", "subuh", "dawn", "fajar", "صبح", "فجر"])
    col_time_isha = _find_col(headers, ["isha", "isyak", "isya", "isha'", "dusk", "عشاء"])
    col_lat = _find_col(headers, ["lat", "latitude", "lintang"])
    col_lng = _find_col(headers, ["lon", "long", "longitude", "bujur"])
    col_elev = _find_col(headers, ["elev", "altitude", "height", "ketinggian"])
    col_angle = _find_col(headers, ["d0", "depression", "angle", "degree", "darjah"])

    # If no date or prayer column found, skip this table
    has_fajr_col = col_time_fajr is not None
    has_isha_col = col_time_isha is not None
    has_date = col_date is not None
    if not (has_date and (has_fajr_col or has_isha_col)):
        return []

    records: list[dict] = []
    for row in rows[1:]:
        cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue

        date_str = _safe_get(cells, col_date, "")
        date = _parse_date(date_str)
        if date is None:
            continue

        lat = site_meta.get("lat") or _parse_float(_safe_get(cells, col_lat))
        lng = site_meta.get("lng") or _parse_float(_safe_get(cells, col_lng))
        elev = site_meta.get("elevation_m") or _parse_float(_safe_get(cells, col_elev)) or 0.0

        if has_fajr_col:
            time_str = _normalize_time(_safe_get(cells, col_time_fajr))
            if time_str and lat and lng:
                records.append(
                    _make_record(
                        "fajr", date, time_str, lat, lng, elev,
                        site_meta.get("utc_offset", 0.0),
                        source_url, site_meta.get("notes", ""),
                    )
                )

        if has_isha_col:
            time_str = _normalize_time(_safe_get(cells, col_time_isha))
            if time_str and lat and lng:
                records.append(
                    _make_record(
                        "isha", date, time_str, lat, lng, elev,
                        site_meta.get("utc_offset", 0.0),
                        source_url, site_meta.get("notes", ""),
                    )
                )

    return records


def _extract_from_pdf(content: bytes, source_url: str) -> list[dict]:
    """Extract prayer time observations from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        log.warning("PyMuPDF not available — skipping PDF extraction")
        return []

    records: list[dict] = []
    try:
        doc = fitz.open(stream=content, filetype="pdf")
    except Exception as e:
        log.warning("PDF open error for %s: %s", source_url, e)
        return []

    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    doc.close()

    # Extract site metadata from full text
    site_meta = _extract_site_meta(full_text)

    # Try table extraction from text (PyMuPDF's get_text() includes table-like structures)
    records.extend(_extract_from_text(full_text, source_url, site_meta))

    return records


def _extract_from_ical(text: str, source_url: str) -> list[dict]:
    """
    Parse iCal content for prayer time events.

    Looks for VEVENT blocks with SUMMARY containing Fajr or Isha keywords
    and a DTSTART timestamp.
    """
    records: list[dict] = []
    for block in text.split("BEGIN:VEVENT")[1:]:
        data: dict[str, str] = {}
        for line in block.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                data[k.strip()] = v.strip()

        summary = data.get("SUMMARY", "")
        prayer = None
        if FAJR_WORDS.search(summary):
            prayer = "fajr"
        elif ISHA_WORDS.search(summary):
            prayer = "isha"
        if prayer is None:
            continue

        dt_raw = data.get("DTSTART", "")
        if dt_raw.endswith("Z"):
            try:
                utc_dt = datetime.strptime(dt_raw, "%Y%m%dT%H%M%SZ").replace(
                    tzinfo=timezone.utc
                )
                records.append(
                    {
                        "prayer": prayer,
                        "date_local": utc_dt.strftime("%Y-%m-%d"),
                        "utc_dt": utc_dt,
                        "time_local": utc_dt.strftime("%H:%M"),
                        "utc_offset": 0.0,
                        "lat": None,
                        "lng": None,
                        "elevation_m": 0.0,
                        "source": source_url,
                        "notes": f"iCal: {summary}",
                    }
                )
            except ValueError:
                pass

    return records


def _extract_from_text(text: str, source_url: str, site_meta: dict) -> list[dict]:
    """
    Extract prayer time data from plain text using regex patterns.

    Looks for lines that contain a date + time + prayer type keyword.
    """
    records: list[dict] = []
    lat = site_meta.get("lat")
    lng = site_meta.get("lng")
    elev = site_meta.get("elevation_m", 0.0)
    utc_offset = site_meta.get("utc_offset", 0.0)

    if not (lat and lng):
        return []  # Can't process without coordinates

    lines = text.split("\n")
    for line in lines:
        if len(line) < 8:
            continue

        # Look for lines with a date pattern
        date = _parse_date_from_line(line)
        if date is None:
            continue

        # Check for prayer type
        prayer = None
        if FAJR_WORDS.search(line):
            prayer = "fajr"
        elif ISHA_WORDS.search(line):
            prayer = "isha"
        if prayer is None:
            continue

        # Look for time
        times = TIME_RE.findall(line)
        if not times:
            continue

        # Use the last time match (usually the observed time)
        h, m = times[-1]
        time_str = f"{int(h):02d}:{int(m):02d}"

        records.append(
            _make_record(
                prayer, date, time_str, lat, lng, elev or 0.0,
                utc_offset, source_url,
                site_meta.get("notes", "text-extraction"),
            )
        )

    return records


def _extract_site_meta(text: str) -> dict:
    """Extract lat/lng/elevation/utc_offset from page text."""
    meta: dict = {}

    lat_m = LAT_RE.search(text)
    if lat_m:
        val = float(lat_m.group(1))
        if lat_m.group(2).upper() == "S":
            val = -val
        meta["lat"] = val

    lng_m = LNG_RE.search(text)
    if lng_m:
        val = float(lng_m.group(1))
        if lng_m.group(2).upper() == "W":
            val = -val
        meta["lng"] = val

    elev_m = ELEV_RE.search(text)
    if elev_m:
        meta["elevation_m"] = float(elev_m.group(1))

    # Try to detect UTC offset from text
    utc_m = re.search(r"UTC\s*([+-]\d+(?:\.\d+)?)", text)
    if utc_m:
        meta["utc_offset"] = float(utc_m.group(1))

    return meta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_col(headers: list[str], keywords: list[str]) -> int | None:
    for kw in keywords:
        for i, h in enumerate(headers):
            if kw in h:
                return i
    return None


def _safe_get(lst: list, idx: int | None, default: str = "") -> str:
    if idx is None or idx >= len(lst):
        return default
    return lst[idx]


def _parse_float(s: str | None) -> float | None:
    if not s:
        return None
    m = re.search(r"[+-]?\d+\.?\d*", s)
    if m:
        return float(m.group())
    return None


def _normalize_time(s: str) -> str | None:
    """Return HH:MM string or None."""
    if not s:
        return None
    m = TIME_RE.search(s)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"
    return None


def _parse_date(s: str) -> str | None:
    """
    Parse a date string into YYYY-MM-DD.

    Handles: YYYY-MM-DD, DD/MM/YYYY, DD Month YYYY.
    """
    if not s:
        return None

    m = DATE_RE_YMD.search(s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"

    m = DATE_RE_DMY.search(s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"

    m = DATE_MONTH_NAMES.search(s)
    if m:
        d = int(m.group(1))
        mo = MONTHS.get(m.group(2)[:3].lower())
        y = int(m.group(3))
        if mo and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"

    return None


def _parse_date_from_line(line: str) -> str | None:
    for pattern in [DATE_RE_YMD, DATE_RE_DMY]:
        m = pattern.search(line)
        if m:
            return _parse_date(m.group(0))
    m = DATE_MONTH_NAMES.search(line)
    if m:
        return _parse_date(m.group(0))
    return None


def _make_record(
    prayer: str,
    date: str,
    time_local: str,
    lat: float,
    lng: float,
    elevation_m: float,
    utc_offset: float,
    source: str,
    notes: str,
) -> dict:
    return {
        "prayer": prayer,
        "date_local": date,
        "time_local": time_local,
        "utc_offset": utc_offset,
        "lat": lat,
        "lng": lng,
        "elevation_m": elevation_m,
        "source": source,
        "notes": notes,
    }
