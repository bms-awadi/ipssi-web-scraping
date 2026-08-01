import scrapy

from veille.items import MentionItem

CIBLES_NOMS = ["Amadeus", "Capgemini", "Mistral AI"]

MOTS_NEGATIFS = [
    "fraude",
    "amende",
    "condamne",
    "scandale",
    "plainte",
    "liquidation",
    "faillite",
    "perquisition",
    "accuse",
    "decline",
    "lowers",
    "criticism",
]
MOTS_POSITIFS = [
    "croissance",
    "benefice",
    "record",
    "acquisition",
    "innovation",
    "nomination",
    "partenariat",
    "expansion",
    "investissement",
    "beats",
    "raises",
    "jumps",
]

FLUX_GENERALISTES = [
    "https://www.lemonde.fr/rss/une.xml",
    "https://www.lesechos.fr/rss/rss_une.xml",  # verifie : renvoie une erreur, ignore par Scrapy
    "https://www.lefigaro.fr/rss/figaro_actualites.xml",
    "https://www.bfmtv.com/rss/info/flux-rss/flux-toutes-les-actualites/",
    "https://www.01net.com/feed/",
]


class RssSpider(scrapy.Spider):
    name = "rss_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.0,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": "IPSSI-OSINT-veille (+cours@ipssi.fr)",
        "LOG_LEVEL": "INFO",
    }

    async def start(self):
        for nom in CIBLES_NOMS:
            query = nom.replace(" ", "+")
            url = f"https://www.bing.com/news/search?q={query}&format=RSS"
            yield scrapy.Request(
                url, callback=self.parse_bing_news, cb_kwargs={"entreprise": nom}
            )

        for url in FLUX_GENERALISTES:
            yield scrapy.Request(url, callback=self.parse_generaliste)

    def parse_bing_news(self, response, entreprise):
        for item in response.xpath("//item"):
            titre = item.xpath("title/text()").get("").strip()
            resume = item.xpath("description/text()").get("").strip()[:300]
            url = item.xpath("link/text()").get("").strip()
            date_pub = item.xpath("pubDate/text()").get("").strip()
            yield self._mention(titre, resume, url, date_pub, "Bing News", entreprise)

    def parse_generaliste(self, response):
        for item in response.xpath("//item | //entry"):
            titre = item.xpath("title/text()").get("").strip()
            resume = (
                item.xpath("description/text() | summary/text()").get("").strip()[:300]
            )
            texte = (titre + resume).lower()
            entreprise = next((n for n in CIBLES_NOMS if n.lower() in texte), None)
            if entreprise is None:
                continue
            url = item.xpath("link/text() | link/@href").get("").strip()
            date_pub = item.xpath("pubDate/text() | published/text()").get("").strip()
            source = response.url.split("/")[2]
            yield self._mention(titre, resume, url, date_pub, source, entreprise)

    @staticmethod
    def _mention(titre, resume, url, date_pub, source, entreprise):
        texte = (titre + " " + resume).lower()
        neg = sum(1 for m in MOTS_NEGATIFS if m in texte)
        pos = sum(1 for m in MOTS_POSITIFS if m in texte)
        score = 1 if neg > pos else (2 if pos > neg else 0)
        return MentionItem(
            titre=titre,
            url=url,
            source=source,
            date_publi=date_pub,
            resume=resume,
            score_alerte=score,
            entreprise=entreprise,
        )
