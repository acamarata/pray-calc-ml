import requests
import os
import re
from pathlib import Path
import time

PAPERS_DIR = Path("research/downloaded_papers")
PAPERS_DIR.mkdir(parents=True, exist_ok=True)

# Queries targeting Islamic twilight observations
QUERIES = [
    "fajr twilight observation angle",
    "subuh sky brightness meter",
    "shafaq twilight measurement isha",
    "depression angle fajr isha",
    "true dawn observation measurements"
]

def fetch_openalex_papers(query):
    url = f"https://api.openalex.org/works?search={query}&per-page=50&filter=has_pdf_url:true"
    print(f"Querying OpenAlex: {query}")
    try:
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            return []
        data = res.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        return []

def sanitize_filename(title):
    return re.sub(r"[^a-zA-Z0-9]+", "_", title).strip("_")

def main():
    seen_titles = set()
    total_downloaded = 0
    
    # Check existing files to avoid duplicates
    existing_files = list(PAPERS_DIR.glob("*.pdf"))
    for file in existing_files:
        name_no_ext = file.stem.lower()
        seen_titles.add(name_no_ext)
        
    for query in QUERIES:
        works = fetch_openalex_papers(query)
        for work in works:
            title = work.get("title")
            if not title:
                continue
            
            clean_title = sanitize_filename(title).lower()
            
            # Simple duplicate check
            if any(clean_title[:30] in seen[:30] for seen in seen_titles):
                print(f"Skipping duplicate/known: {title}")
                continue
                
            pdf_url = work.get("open_access", {}).get("oa_url")
            if not pdf_url or not pdf_url.endswith(".pdf"):
                continue
                
            year = work.get("publication_year", "0000")
            filename = f"{year}_{clean_title[:60]}.pdf"
            filepath = PAPERS_DIR / filename
            
            if filepath.exists():
                print(f"Already downloaded: {filename}")
                continue
                
            print(f"Downloading: {title} ({year})")
            print(f"  URL: {pdf_url}")
            try:
                # Add headers to mimic browser
                headers = {'User-Agent': 'Mozilla/5.0'}
                pdf_res = requests.get(pdf_url, headers=headers, timeout=20)
                if pdf_res.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(pdf_res.content)
                    print(f"  -> Saved as {filename}")
                    seen_titles.add(clean_title)
                    total_downloaded += 1
                else:
                    print(f"  -> Failed with status {pdf_res.status_code}")
            except Exception as e:
                print(f"  -> Download failed: {e}")
            
            time.sleep(1) # Be nice to servers
            
    print(f"\nTotal new papers downloaded: {total_downloaded}")

if __name__ == "__main__":
    main()
