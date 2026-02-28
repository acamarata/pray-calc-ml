"""
PDF text and table extraction for academic papers.

Uses pdfminer.six (already installed) to extract text from PDFs.
Heuristic table parsing looks for rows containing prayer times, angles,
dates, and coordinates.

For each paper PDF we extract:
1. Raw full text
2. Candidate data rows (lines that look like observation tables)
3. Metadata (title, abstract, site info)
"""

from __future__ import annotations

import io
import logging
import re
from typing import Optional

log = logging.getLogger(__name__)


def extract_text(pdf_bytes: bytes) -> Optional[str]:
    """
    Extract all text from a PDF. Returns None if extraction fails.
    """
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams

        buf = io.BytesIO(pdf_bytes)
        out = io.StringIO()
        laparams = LAParams(line_margin=0.5, word_margin=0.1)
        extract_text_to_fp(buf, out, laparams=laparams)
        text = out.getvalue()
        log.info("extracted %d chars from PDF", len(text))
        return text
    except Exception as e:
        log.warning("pdfminer extraction failed: %s", e)
        return None


# Patterns for parsing extracted table rows from academic papers
# These match lines that look like prayer observation records.

# A time in HH:MM or H:MM format
RE_TIME = re.compile(r'\b(\d{1,2}:\d{2})\b')

# A date: various formats
RE_DATE = re.compile(
    r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{1,2}\s+\w+\s+\d{4})\b'
)

# An angle: typically 10.0–25.0 degrees
RE_ANGLE = re.compile(r'\b(1[0-9]|2[0-5])\.\d{1,4}\b')

# Latitude and longitude
RE_LAT = re.compile(r'\b([+-]?\d{1,2}\.\d{2,6})[°\s]*(N|S|north|south)?\b', re.IGNORECASE)
RE_LNG = re.compile(r'\b([+-]?\d{1,3}\.\d{2,6})[°\s]*(E|W|east|west)?\b', re.IGNORECASE)


def find_table_candidates(text: str) -> list[str]:
    """
    Return lines from extracted PDF text that look like they could contain
    prayer time observation data (date + time + angle).
    """
    candidates = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        has_time = bool(RE_TIME.search(line))
        has_date = bool(RE_DATE.search(line))
        has_angle = bool(RE_ANGLE.search(line))
        # A candidate line has at least 2 of the 3 indicators
        score = int(has_time) + int(has_date) + int(has_angle)
        if score >= 2 and len(line) > 10:
            candidates.append(line)
    return candidates


def parse_prayer_time_line(
    line: str,
    *,
    default_lat: Optional[float] = None,
    default_lng: Optional[float] = None,
    default_utc_offset: float = 0.0,
    prayer: str = "fajr",
    source: str = "",
    year: Optional[int] = None,
) -> Optional[dict]:
    """
    Try to parse a single text line into a prayer sighting record.

    Returns a dict with keys: prayer, date_local, time_local, utc_offset,
    lat, lng, elevation_m, source, notes — or None if parsing fails.
    """
    times = RE_TIME.findall(line)
    dates = RE_DATE.findall(line)
    if not times:
        return None

    # Pick first plausible Fajr time (before 08:00 local) or Isha time (after 18:00 local)
    time_str = None
    for t in times:
        h = int(t.split(":")[0])
        if prayer == "fajr" and h < 8:
            time_str = t
            break
        elif prayer == "isha" and h >= 18:
            time_str = t
            break
    if not time_str and times:
        time_str = times[0]

    # Pick first date
    date_str = None
    if dates:
        raw = dates[0]
        # Normalize various formats to YYYY-MM-DD
        date_str = _normalize_date(raw, year_hint=year)

    if not date_str or not time_str:
        return None

    return {
        "prayer": prayer,
        "date_local": date_str,
        "time_local": time_str,
        "utc_offset": default_utc_offset,
        "lat": default_lat or 0.0,
        "lng": default_lng or 0.0,
        "elevation_m": 0,
        "source": source,
        "notes": f"parsed from PDF table line: {line[:120]}",
    }


def _normalize_date(raw: str, year_hint: Optional[int] = None) -> Optional[str]:
    """Attempt to normalize a raw date string to YYYY-MM-DD."""
    import datetime

    raw = raw.strip()

    # Already ISO: 2022-03-15 or 2022/03/15
    m = re.match(r'^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$', raw)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime.date(y, mo, d).isoformat()
        except ValueError:
            return None

    # DD/MM/YYYY or DD-MM-YYYY
    m = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$', raw)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime.date(y, mo, d).isoformat()
        except ValueError:
            return None

    # "15 January 2022" or "15 Jan 2022"
    for fmt in ("%d %B %Y", "%d %b %Y"):
        try:
            return datetime.datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass

    return None
