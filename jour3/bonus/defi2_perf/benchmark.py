import re
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2] / "tp" / "allocine"
VALEURS = [1, 4, 8, 16]

resultats = []

for n in VALEURS:
    print(f"=== CONCURRENT_REQUESTS={n} ===")
    debut = time.perf_counter()
    proc = subprocess.run(
        [
            "scrapy",
            "crawl",
            "films",
            "-s",
            f"CONCURRENT_REQUESTS={n}",
            "-s",
            "CLOSESPIDER_ITEMCOUNT=100",
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
    received = re.search(r"response_received_count':\s*(\d+)", log)
    scraped = int(scraped.group(1)) if scraped else 0
    received = int(received.group(1)) if received else 0
    ratio = scraped / received if received else 0.0

    resultats.append(
        {
            "concurrent_requests": n,
            "duree_s": round(duree, 1),
            "items": scraped,
            "items_par_s": round(scraped / duree, 2) if duree else 0,
            "responses": received,
            "ratio_scraped_received": round(ratio, 2),
        }
    )
    print(resultats[-1])

print()
print(
    f"{'CONCURRENT_REQUESTS':>20} | {'temps (s)':>10} | {'items':>6} | {'items/s':>8} | {'ratio scraped/received':>22}"
)
for r in resultats:
    print(
        f"{r['concurrent_requests']:>20} | {r['duree_s']:>10} | {r['items']:>6} "
        f"| {r['items_par_s']:>8} | {r['ratio_scraped_received']:>22}"
    )
