import time

from tqdm import tqdm

from fetch import new_session, get_page, CATEGORIES
from parse import parse_articles, extract_article
from storage import export_csv, store_sqlite

TARGET_COUNT = 200
DELAY_SECONDS = 1.5
MAX_PAGES_PER_CATEGORY = 20


def scrape(target_count=TARGET_COUNT):
    articles = []
    seen_urls = set()

    session = new_session()
    with tqdm(total=target_count, unit="article", desc="Scraping") as pbar:
        for category in CATEGORIES:
            if len(articles) >= target_count:
                break

            page = 1
            while len(articles) < target_count and page <= MAX_PAGES_PER_CATEGORY:
                html = get_page(session, category, page)
                if html is None:
                    break

                blocks = parse_articles(html)
                if not blocks:
                    tqdm.write(f"Plus d'articles pour {category}, categorie suivante.")
                    break

                new_articles = [
                    article
                    for block in blocks
                    if (article := extract_article(block)) is not None
                    and article["url"] not in seen_urls
                ]

                if not new_articles:
                    tqdm.write(
                        f"Pas de nouvel article pour {category} page {page}, categorie suivante."
                    )
                    break

                for article in new_articles:
                    seen_urls.add(article["url"])
                    articles.append(article)

                pbar.update(min(len(new_articles), target_count - pbar.n))

                page += 1
                time.sleep(DELAY_SECONDS)

    session.close()

    # Les categories sont scrapees l'une apres l'autre : on retrie par date
    # decroissante pour se rapprocher des "200 derniers articles" demandes.
    articles.sort(key=lambda a: a["date"] or "", reverse=True)
    return articles[:target_count]


def main():
    articles = scrape()
    export_csv(articles)
    store_sqlite(articles)


if __name__ == "__main__":
    main()
