import requests

from config import URL


def tester_requests() -> bool:
    r = requests.get(
        URL, headers={"User-Agent": "IPSSI-scraper (+contact@ipssi.fr)"}, timeout=10
    )
    print(f"requests seul : HTTP {r.status_code}")
    return r.status_code == 200 and len(r.text) > 5000
