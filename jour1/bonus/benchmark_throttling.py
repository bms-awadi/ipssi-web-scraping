"""Defi 3 - Benchmark honnete du throttling (sur Numerama, meme site que le defi 1).

Fichier autonome : sa propre fonction de requete, pas d'import depuis
jour1/td/ ni jour1/tp/.

DEMO : pour rester civil envers le site pendant cette demonstration, seule
une partie de la grille (2 et 5 pages) a ete mesuree reellement ici, pas les
10 pages x 3 delais complets. Voir BONUS.md pour l'extrapolation et la
formule permettant de remplir la grille complete.
"""

import time

import requests

HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}
BASE_URL = "https://www.numerama.com/page/{n}/"


def get_page(url: str) -> None:
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()


def benchmark(pages: int, delay: float) -> float:
    t0 = time.time()
    for n in range(1, pages + 1):
        url = "https://www.numerama.com/" if n == 1 else BASE_URL.format(n=n)
        get_page(url)
        time.sleep(delay)
    return time.time() - t0


if __name__ == "__main__":
    for pages in [2, 5]:
        for delay in [0.5, 1.0, 2.0]:
            duree = benchmark(pages, delay)
            print(f"{pages} pages | delai {delay}s -> {duree:.1f}s")
