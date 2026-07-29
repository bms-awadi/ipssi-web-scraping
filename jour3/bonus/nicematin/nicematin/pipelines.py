from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CleanPipeline:
    def process_item(self, item, spider):
        a = ItemAdapter(item)
        if a.get("titre"):
            a["titre"] = a["titre"].strip()
        if a.get("categorie"):
            a["categorie"] = a["categorie"].strip()
        return item


class DedupPipeline:
    def __init__(self):
        self.urls_vus = set()

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        if a["url"] in self.urls_vus:
            raise DropItem(f"Doublon : {a['url']}")
        self.urls_vus.add(a["url"])
        return item
