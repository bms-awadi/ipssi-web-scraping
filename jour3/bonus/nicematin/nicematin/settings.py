BOT_NAME = "nicematin"

SPIDER_MODULES = ["nicematin.spiders"]
NEWSPIDER_MODULE = "nicematin.spiders"

ADDONS = {}


USER_AGENT = "IPSSI-scraper (+contact@ipssi.fr)"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 10

ITEM_PIPELINES = {
    "nicematin.pipelines.CleanPipeline": 100,
    "nicematin.pipelines.DedupPipeline": 200,
}

FEEDS = {
    "articles.csv": {"format": "csv", "encoding": "utf-8", "overwrite": True},
}

FEED_EXPORT_ENCODING = "utf-8"
