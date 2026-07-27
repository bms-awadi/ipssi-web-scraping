import csv
import sqlite3
from contextlib import closing
from pathlib import Path

from parse import FIELDNAMES

CSV_PATH = Path("articles.csv")
DB_PATH = Path("scraper.db")

DDL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    categorie TEXT,
    chapeau TEXT,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def export_csv(articles, path=CSV_PATH):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(articles)
    print(f"{len(articles)} articles exportes vers {path}")


def store_sqlite(articles, path=DB_PATH):
    with closing(sqlite3.connect(path)) as cx:
        cx.executescript(DDL)
        cx.executemany(
            """
            INSERT OR IGNORE INTO articles (titre, url, date, categorie, chapeau)
            VALUES (:titre, :url, :date, :categorie, :chapeau)
            """,
            articles,
        )
        cx.commit()
    print(f"Articles inseres dans {path}")
