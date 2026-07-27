"""Defi 1 (demo) - Adapter le scraper a un site different : Numerama.

Fichier autonome : n'importe rien de jour1/td/ ni de jour1/tp/, pour que
le dossier bonus/ reste independant et ne touche a rien d'autre. Reutilise
par diff_scrapes.py et benchmark_throttling.py (defis 2 et 3, meme site).

DEMO fournie par l'assistant a titre d'exemple. Le sujet precise que ce
defi doit etre refait par l'etudiant avec un site qui reflete son propre
interet : ce choix-la ne peut pas venir d'une IA.
"""

import csv
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.numerama.com/page/{n}/"
HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}
CHAMPS = ["titre", "url", "date", "categorie"]


def get_page(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    # r.content (octets bruts), pas r.text : numerama.com ne declare pas son
    # charset dans Content-Type, ce qui fait retomber requests sur
    # ISO-8859-1 par defaut et casse les accents. BeautifulSoup detecte le
    # bon encodage lui-meme a partir des octets.
    return BeautifulSoup(r.content, "lxml")


def parse_articles(soup: BeautifulSoup) -> list[dict]:
    articles = []
    for card in soup.select(".post-card"):
        lien = card.select_one(".post-card__title")
        date_tag = card.select_one(".post-card__date")
        if not lien or not lien.get("href", "").startswith("https://www.numerama.com/"):
            continue  # cartes sponsorisees / liens publicitaires externes

        # Pas de classe "categorie" visible sur les petites cartes : on la
        # deduit du premier segment de l'URL (ex: /vroom/..., /sciences/...).
        categorie = urlparse(lien["href"]).path.strip("/").split("/")[0]

        articles.append({
            "titre": lien.get_text(strip=True),
            "url": lien["href"],
            "date": date_tag.get_text(" ", strip=True) if date_tag else "",
            "categorie": categorie,
        })
    return articles


def scrape_all(max_articles: int = 20) -> list[dict]:
    tous = []
    vus = set()
    page = 1
    while len(tous) < max_articles:
        url = "https://www.numerama.com/" if page == 1 else BASE_URL.format(n=page)
        soup = get_page(url)
        candidats = parse_articles(soup)
        # vus est mis a jour au fil de la boucle (pas apres coup) : sinon un
        # meme article present deux fois sur une page (ex: en vedette et
        # dans le flux normal) passerait deux fois le filtre.
        nouveaux = []
        for a in candidats:
            if a["url"] not in vus:
                vus.add(a["url"])
                nouveaux.append(a)
        if not nouveaux:
            print(f"Plus d'articles a la page {page}, arret.")
            break
        tous.extend(nouveaux)
        print(f"Page {page} => {len(nouveaux)} articles | total={len(tous)}")
        page += 1
    return tous[:max_articles]


def sauver_csv(articles: list[dict], chemin: str = "articles_numerama.csv") -> None:
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS)
        w.writeheader()
        w.writerows(articles)
    print(f"CSV : {len(articles)} lignes -> {chemin}")


if __name__ == "__main__":
    arts = scrape_all(20)
    for a in arts[:3]:
        print(f"{a['date']} [{a['categorie']}] {a['titre'][:60]}")
    sauver_csv(arts)
