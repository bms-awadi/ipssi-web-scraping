import re
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2] / "tp" / "allocine"
VALEURS = [1, 4, 8, 16]

resultats = []

for n in VALEURS:
    print(
        f"CONCURRENT_REQUESTS = CONCURRENT_REQUESTS_PER_DOMAIN = {n}, AutoThrottle OFF"
    )
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
            "DOWNLOAD_DELAY=0.25",
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

    resultats.append(
        {
            "concurrent_requests": n,
            "duree_s": round(duree, 1),
            "items": scraped,
            "items_par_s": round(scraped / duree, 2) if duree else 0,
        }
    )
    print(resultats[-1])

print()
print(
    f"{'CONCURRENT_REQUESTS':>20} | {'temps (s)':>10} | {'items':>6} | {'items/s':>8}"
)
for r in resultats:
    print(
        f"{r['concurrent_requests']:>20} | {r['duree_s']:>10} | {r['items']:>6} | {r['items_par_s']:>8}"
    )
