import re

import scrapy

from allocine.items import FilmItem


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/meilleurs/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "ROBOTSTXT_OBEY": True,
    }

    MAX_FILMS = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduled = 0

    def parse(self, response):
        # 1) Suivre chaque lien vers fiche détail
        liens = response.css("h2.meta-title a.meta-title-link::attr(href)").getall()
        for lien in liens:
            if self.scheduled >= self.MAX_FILMS:
                return
            self.scheduled += 1
            yield response.follow(lien, callback=self.parse_film)

        # 2) Pagination - motif d'URL ?page=N (le bouton "Suivante" du site
        # est un <span> sans href exploitable, obfusqué côté JS)
        if self.scheduled < self.MAX_FILMS:
            match = re.search(r"page=(\d+)", response.url)
            page_actuelle = int(match.group(1)) if match else 1
            page_suivante = (
                f"https://www.allocine.fr/film/meilleurs/?page={page_actuelle + 1}"
            )
            yield response.follow(page_suivante, callback=self.parse)

    def parse_film(self, response):
        titre = response.css("div.titlebar-title.titlebar-title-xl::text").get()

        date_sortie = response.css(".meta-body-info span.date::text").get()
        annee = None
        if date_sortie:
            m = re.search(r"\d{4}", date_sortie)
            annee = m.group(0) if m else None

        realisateur = ", ".join(
            response.xpath(
                "//div[contains(@class,'meta-body-direction')]"
                "[.//span[@class='light'][normalize-space(text())='De']]"
                "//span[contains(@class,'dark-grey-link')]/text()"
            ).getall()
        ).strip()

        yield FilmItem(
            titre=titre,
            annee=annee,
            realisateur=realisateur or None,
            note_presse=self._note(response, "Presse"),
            note_spectateurs=self._note(response, "Spectateurs"),
            url=response.url,
        )

    @staticmethod
    def _note(response, label):
        return response.xpath(
            f"//div[@class='rating-item']"
            f"[.//span[contains(@class,'rating-title')][contains(text(),'{label}')]]"
            f"//span[contains(@class,'stareval-note')]/text()"
        ).get()
