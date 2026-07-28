from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from config import HEURE_RE


def extraire_articles(driver) -> list[dict]:
    resultats = []
    cartes = driver.find_elements(By.CSS_SELECTOR, "article")
    for art in cartes:
        try:
            lien = art.find_element(By.CSS_SELECTOR, "a[href]")
        except NoSuchElementException:
            continue

        titre = (lien.get_attribute("title") or lien.text).strip()
        if not titre:
            continue
        url_article = lien.get_attribute("href") or ""

        lignes = [l.strip() for l in art.text.split("\n") if l.strip()]
        premium = "PREMIUM" in lignes
        lignes_utiles = [l for l in lignes if l != "PREMIUM"]
        rubrique = lignes_utiles[-1] if lignes_utiles else ""
        heure_publi = next((l for l in lignes_utiles if HEURE_RE.search(l)), "")
        # Pas de resume/chapo affiche sur les cartes de la page d'accueil de ce
        # site (verifie : seuls kicker/titre/rubrique/heure y figurent) -> "".
        # Recupere via meta[name=description] sur la page de l'article, voir details.py
        chapeau = ""

        resultats.append(
            {
                "titre": titre,
                "rubrique": rubrique,
                "chapeau": chapeau,
                "heure_publi": heure_publi,
                "premium": premium,
                "url_article": url_article,
            }
        )
    return resultats
