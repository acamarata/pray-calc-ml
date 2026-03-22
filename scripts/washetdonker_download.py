"""
Download SQM .dat files from the washetdonker.nl network.

The site exposes ~90 stations across the Netherlands, Germany, and nearby islands.
Each station has daily files at:
  https://www.washetdonker.nl/data/{StationName}/{YYYY}/{MM}/{YYYYMMDD}_120000_SQM-{StationName}.dat

Station metadata (lat, lng) is embedded in each file header.

Usage:
    python scripts/washetdonker_download.py [--year 2023] [--station Texel] [--all]
    python scripts/washetdonker_download.py --sample   # 1 year for all stations
    python scripts/washetdonker_download.py --full     # all years for all stations

Files are saved to:
    data/raw/washetdonker/{StationName}/{YYYY}/{MM}/{filename}.dat
"""
from __future__ import annotations

import argparse
import logging
import re
import time
from datetime import date, timedelta
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_URL = "https://www.washetdonker.nl/data"
REPO_ROOT = Path(__file__).parent.parent
OUT_ROOT = REPO_ROOT / "data" / "raw" / "washetdonker"

# All known stations enumerated from the washetdonker.nl index
# Ordered roughly north to south / by known data quality
ALL_STATIONS = [
    "Texel", "Texel-Waalenburg", "Texel-puur",
    "Vlieland-Oost", "Vliehors",
    "Terschelling", "Natuurschuur-Terschelling",
    "Ameland-Natuurcentrum-Nes",
    "Schiermonnikoog", "Schiermonnikoog-centrum", "Schiermonnikoog-dorp",
    "Griend",
    "Spitsbergen",
    "Marker-Wadden",
    "Mandoe",
    "WEC-Lauwersoog", "Lauwersoog", "Lauwersoog-haven", "Lauwersmeer-extra",
    "Noordpolderzijl",
    "Roodeschool", "Oudeschip", "Termunten", "Farmsum", "Eemshaven",
    "Groningen-ZernikeCampus", "Groningen-Selwerd", "Groningen-DeHeld",
    "ZwarteHaan", "Zuidbroek", "Sappemeer",
    "Holwerd-1", "Holwerd-2", "Moddergat",
    "Bartlehiem", "Burgum", "Aldeboarn", "Akkrum",
    "Heerenveen01", "Heerenveen-Station",
    "Gorredijk", "Katlijk",
    "tZandt",
    "Hornhuizen", "Boerakker", "Tolbert",
    "Reitdiep",
    "Sellingen", "Erica",
    "Lemmer",
    "DenHelder", "Hippolytushoef",
    "Harlingen-Noord",
    "Radio-Kootwijk", "Kootwijk-dorp",
    "Hulshorst",
    "Haaksbergen", "Lochem",
    "Delft", "Rijswijk",
    "Artis-Amsterdam", "Westpoort",
    "Leiden-Sterrewacht",
    "DeZilk", "Oostkapelle",
    "Weerribben",
    "Westhoek",
    "Solarcity",
    "ObsonWheels",
    # German stations
    "Borkum", "Borkum-hafen", "Borkum-Ostland",
    "Emden", "Norddeich-eins", "Norddeich-zwei", "Norddeich-Flugplatz",
    "Oldenburg",
    "Spiekeroog", "Burlage",
    # Danish
    "Ribe",
    # Rankings page (not a station — skip)
    # "ranking",
]


def build_url(station: str, year: int, month: int, day: int) -> str:
    d = date(year, month, day)
    filename = f"{d.strftime('%Y%m%d')}_120000_SQM-{station}.dat"
    return f"{BASE_URL}/{station}/{year}/{month:02d}/{filename}"


def out_path(station: str, year: int, month: int, day: int) -> Path:
    d = date(year, month, day)
    filename = f"{d.strftime('%Y%m%d')}_120000_SQM-{station}.dat"
    return OUT_ROOT / station / str(year) / f"{month:02d}" / filename


def download_file(url: str, dest: Path, session: requests.Session) -> bool:
    """Download url to dest. Returns True if file written, False on skip/error."""
    if dest.exists() and dest.stat().st_size > 500:
        return False  # already downloaded

    try:
        resp = session.get(url, timeout=30)
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.debug("  FAIL %s: %s", url, exc)
        return False

    # Sanity: must start with our known header marker
    content = resp.content
    if not content.startswith(b"# Definition"):
        log.debug("  SKIP (bad content): %s", url)
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return True


def iter_dates(year: int):
    """Yield every date in the given year."""
    d = date(year, 1, 1)
    end = date(year + 1, 1, 1)
    while d < end:
        yield d
        d += timedelta(days=1)


def download_station_year(station: str, year: int, session: requests.Session) -> int:
    """Download all daily files for one station+year. Returns count of new files."""
    new = 0
    for d in iter_dates(year):
        url = build_url(station, year, d.month, d.day)
        dest = out_path(station, year, d.month, d.day)
        if download_file(url, dest, session):
            new += 1
            log.debug("  + %s", dest.name)
        time.sleep(0.05)  # polite crawl — 20 req/s max
    return new


def main():
    ap = argparse.ArgumentParser(description="Download washetdonker.nl SQM data")
    ap.add_argument("--station", help="Single station name (e.g. Texel)")
    ap.add_argument("--year", type=int, help="Single year (e.g. 2023)")
    ap.add_argument("--all", dest="all_years", action="store_true",
                    help="Download all years (2020-2026) for all stations")
    ap.add_argument("--sample", action="store_true",
                    help="Download 2024 for all stations (quick sample)")
    ap.add_argument("--since", type=int, default=2022,
                    help="Download from this year onwards (default: 2022)")
    args = ap.parse_args()

    stations = [args.station] if args.station else ALL_STATIONS

    if args.year:
        years = [args.year]
    elif args.sample:
        years = [2024]
    elif args.all_years:
        years = list(range(2020, 2027))
    else:
        years = list(range(args.since, 2027))

    log.info("Stations: %d  Years: %s", len(stations), years)

    session = requests.Session()
    session.headers["User-Agent"] = (
        "pray-calc-ml/1.0 (academic research; twilight data; "
        "contact: alisalaah@gmail.com)"
    )

    total_new = 0
    for station in stations:
        for year in years:
            log.info("Downloading %s / %d ...", station, year)
            new = download_station_year(station, year, session)
            total_new += new
            if new:
                log.info("  -> %d new files", new)

    log.info("Done. Total new files: %d", total_new)
    log.info("Output: %s", OUT_ROOT)


if __name__ == "__main__":
    main()
