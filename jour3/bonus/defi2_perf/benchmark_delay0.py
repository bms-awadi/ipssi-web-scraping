import re
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2] / "tp" / "allocine"
VALEURS = [1, 4, 8, 16]

for n in VALEURS:
    debut = time.perf_counter()
    proc = subprocess.run(
        [
            "scrapy",
            "crawl",
            "films",
            "-s",
            f"CONCURRENT_REQUESTS={n}",
            "-s",
            f"CONCURRENT_REQUESTS_PER_DOMAIN={n}",
            "-s",
            "AUTOTHROTTLE_ENABLED=False",
            "-s",
            "DOWNLOAD_DELAY=0",
            "-L",
            "INFO",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    duree = time.perf_counter() - debut
    log = proc.stderr
    scraped = re.search(r"item_scraped_count':\s*(\d+)", log)
    scraped = int(scraped.group(1)) if scraped else 0
    print(n, round(duree, 1), scraped, round(scraped / duree, 2) if duree else 0)
