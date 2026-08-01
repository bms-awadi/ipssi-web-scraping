BOT_NAME = "veille"

SPIDER_MODULES = ["veille.spiders"]
NEWSPIDER_MODULE = "veille.spiders"

ADDONS = {}


USER_AGENT = "IPSSI-OSINT-veille (+cours@ipssi.fr)"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

ITEM_PIPELINES = {
    "veille.pipelines.CleanPipeline": 100,
    "veille.pipelines.SQLitePipeline": 200,
}

FEEDS = {
    "mentions.csv": {"format": "csv", "encoding": "utf-8", "overwrite": True},
}

FEED_EXPORT_ENCODING = "utf-8"
