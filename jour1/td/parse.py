from bs4 import BeautifulSoup

FIELDNAMES = ["titre", "url", "date", "categorie", "chapeau"]


def parse_articles(html):
    """Construit l'arbre DOM et retourne les blocs <article> de la page."""
    soup = BeautifulSoup(html, "lxml")
    return soup.select("article.post")


def extract_article(block):
    """
    Demander : h2.post-title a / .cat-links a / .entry-summary comme
    Actuellement : soit tout l'<article> est enveloppe dans un <a> (cartes en
    tete de page), soit le <a> est imbrique a l'interieur, autour du seul
    <h3> (cartes de liste plus bas)..
    """
    title_tag = block.select_one("h3.entry-title")
    link_tag = (title_tag and title_tag.find_parent("a")) or block.find_parent("a")
    time_tag = block.select_one("time[datetime]")
    category_tag = block.select_one(".favtag")
    excerpt_tag = block.select_one(".entry-summary")

    if not link_tag or not title_tag:
        return None

    return {
        "titre": title_tag.text.strip(),
        "url": link_tag["href"],
        "date": time_tag["datetime"] if time_tag else None,
        "categorie": category_tag.text.strip() if category_tag else None,
        "chapeau": excerpt_tag.text.strip() if excerpt_tag else None,
    }
