import argparse
import csv
import sqlite3
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.blogdumoderateur.com/web/page/{n}/"
MAX = 200

HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

CHAMPS = ["titre", "url", "date", "categorie", "chapeau"]

DDL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    categorie TEXT,
    chapeau TEXT,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


def get_page(url: str, tries: int = 3) -> BeautifulSoup:
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"429 - attente {wait}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml")
        except requests.Timeout:
            print(f"Timeout tentative {attempt + 1}/{tries}")
            time.sleep(2**attempt)
        except requests.HTTPError as e:
            if e.response.status_code < 500:
                raise  # 4xx definitif, inutile de reessayer
            time.sleep(2**attempt)
    raise RuntimeError(f"Echec apres {tries} tentatives : {url}")


def parse_articles(soup: BeautifulSoup) -> list[dict]:
    articles = []
    for card in soup.select("article.post"):
        titre_tag = card.select_one("h3.entry-title")
        if not titre_tag:
            continue  # carte sans titre exploitable, on l'ignore

        lien_tag = titre_tag.find_parent("a") or card.find_parent("a")
        date_tag = card.select_one("time[datetime]")
        categorie_tag = card.select_one(".favtag")
        chapeau_tag = card.select_one(".entry-summary")

        titre = titre_tag.get_text(strip=True)
        url = lien_tag["href"]
        date = date_tag["datetime"][:10] if date_tag else ""
        categorie = categorie_tag.get_text(strip=True) if categorie_tag else ""
        chapeau = chapeau_tag.get_text(strip=True)[:300] if chapeau_tag else ""

        articles.append(
            {
                "titre": titre,
                "url": url,
                "date": date,
                "categorie": categorie,
                "chapeau": chapeau,
            }
        )
    return articles


def scrape_all(max_articles: int = MAX) -> list[dict]:
    tous = []
    page = 1
    while len(tous) < max_articles:
        url = (
            "https://www.blogdumoderateur.com/web/"
            if page == 1
            else BASE_URL.format(n=page)
        )
        soup = get_page(url)
        nouveaux = parse_articles(soup)
        if not nouveaux:
            print(f"Plus d'articles a la page {page}, arret.")
            break
        tous.extend(nouveaux)
        print(f"Page {page} => {len(nouveaux)} articles | total={len(tous)}")
        page += 1
        time.sleep(1.5)  # throttling : au moins 1s entre requetes (civilite)
    return tous[:max_articles]


def sauver_csv(articles: list[dict], chemin: str = "articles.csv") -> None:
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS, extrasaction="ignore")
        w.writeheader()
        w.writerows(articles)
    print(f"CSV : {len(articles)} lignes -> {chemin}")


def sauver_sqlite(articles: list[dict], chemin: str = "articles.db") -> None:
    with sqlite3.connect(chemin) as cx:
        cx.execute(DDL)
        inserted = 0
        for a in articles:
            try:
                cx.execute(
                    "INSERT OR IGNORE INTO articles (titre,url,date,categorie,chapeau) "
                    "VALUES (:titre,:url,:date,:categorie,:chapeau)",
                    a,
                )
                inserted += cx.execute("SELECT changes()").fetchone()[0]
            except sqlite3.Error as e:
                print(f"Erreur SQLite : {e}")
        cx.commit()
    print(f"SQLite : {inserted} nouvelles lignes inserees dans {chemin}")


def main():
    p = argparse.ArgumentParser(description="Scraper Blog du Moderateur")
    p.add_argument("--max", type=int, default=200, help="Nb max d'articles")
    p.add_argument("--csv", default="articles.csv")
    p.add_argument("--db", default="articles.db")
    args = p.parse_args()

    print(f"Demarrage - cible : {args.max} articles")
    articles = scrape_all(args.max)
    sauver_csv(articles, args.csv)
    sauver_sqlite(articles, args.db)
    print(f"Termine : {len(articles)} articles")


if __name__ == "__main__":
    main()
