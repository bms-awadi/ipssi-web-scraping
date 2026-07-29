import scrapy

from nicematin.items import ArticleItem


class ArticlesSpider(scrapy.Spider):
    name = "articles"
    allowed_domains = ["nicematin.com"]
    start_urls = [
        "https://www.nicematin.com/alpes-maritimes/",
        "https://www.nicematin.com/var/",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 10.0,
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        cartes = response.css("div.col.d-flex.flex-column.align-items-stretch.gap-1")
        for carte in cartes:
            titre = " ".join(
                t.strip()
                for t in carte.css(
                    "div.fs-6.f-serif.mb-0.lc-3.fw-medium::text"
                ).getall()
                if t.strip()
            )
            url = carte.css("a.d-flex.flex-column.gap-05::attr(href)").get()
            categorie = " - ".join(
                c.strip()
                for c in carte.css("div.d-inline-block.small span::text").getall()
                if c.strip()
            )
            if not titre or not url:
                continue
            yield ArticleItem(titre=titre, url=url, categorie=categorie or None)
