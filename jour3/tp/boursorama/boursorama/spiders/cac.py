import re

import scrapy

from boursorama.items import ActionItem


class CacSpider(scrapy.Spider):
    name = "cac"
    allowed_domains = ["boursorama.com"]
    start_urls = ["https://www.boursorama.com/bourse/actions/palmares/france/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "RETRY_TIMES": 3,
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        lignes = response.css(
            "div.c-palmares table.c-table-top-flop tbody tr.c-table__row"
        )
        for ligne in lignes:
            lien = ligne.css("a.c-link::attr(href)").get()
            if not lien:
                continue
            data = {
                "libelle": ligne.css("a.c-link::text").get(),
                "cours": ligne.css(".c-instrument--last::text").get(),
                "variation": (
                    ligne.css(".c-instrument--instant-variation::text").get()
                    or ligne.css(".c-instrument--variation::text").get()
                ),
                "volume": ligne.css(".c-instrument--totalvolume::text").get(),
            }
            yield response.follow(lien, callback=self.parse_fiche, cb_kwargs=data)

    def parse_fiche(self, response, **data):
        isin_brut = response.css("h2.c-faceplate__isin::text").get()
        match = re.search(r"[A-Z]{2}[A-Z0-9]{9}\d", isin_brut) if isin_brut else None

        yield ActionItem(
            libelle=data["libelle"],
            cours=data["cours"],
            variation=data["variation"],
            volume=data["volume"],
            isin=match.group(0) if match else None,
            url=response.url,
        )
