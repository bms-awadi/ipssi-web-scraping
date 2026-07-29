import sqlite3

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

DDL = """CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT NOT NULL,
    cours REAL,
    variation REAL,
    volume INTEGER,
    isin TEXT UNIQUE,
    url TEXT,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
)"""


class CleanPipeline:
    def process_item(self, item, spider):
        a = ItemAdapter(item)

        if a.get("libelle"):
            a["libelle"] = a["libelle"].strip()

        if a.get("cours"):
            a["cours"] = float(a["cours"].strip().replace(" ", "").replace(",", "."))

        if a.get("variation"):
            a["variation"] = float(
                a["variation"].strip().replace("%", "").replace(",", ".")
            )

        if a.get("volume"):
            a["volume"] = int(a["volume"].strip().replace(" ", "").replace("\xa0", ""))

        if not a.get("isin"):
            raise DropItem(f"ISIN manquant pour {a.get('libelle')!r}")

        return item


class SQLitePipeline:
    def open_spider(self, spider):
        self.cx = sqlite3.connect("bourse.db")
        self.cx.execute(DDL)
        self.cx.commit()

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        try:
            self.cx.execute(
                "INSERT OR IGNORE INTO actions (libelle,cours,variation,volume,isin,url) "
                "VALUES (:libelle,:cours,:variation,:volume,:isin,:url)",
                a.asdict(),
            )
            self.cx.commit()
        except sqlite3.Error as e:
            spider.logger.error(f"SQLite: {e}")
        return item

    def close_spider(self, spider):
        n = self.cx.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
        spider.logger.info(f"BDD : {n} actions en base")
        self.cx.close()
