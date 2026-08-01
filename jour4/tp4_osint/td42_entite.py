import json
import sys
import time

import feedparser
import requests
from bs4 import BeautifulSoup
from protego import Protego

from cibles import CIBLES

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEADERS = {"User-Agent": "IPSSI-OSINT (+cours@ipssi.fr)"}

SIRENE_URL = "https://recherche-entreprises.api.gouv.fr/search"

WIKIPEDIA_SEARCH_URL = "https://fr.wikipedia.org/w/api.php"
WIKIPEDIA_PAGE_URL = "https://fr.wikipedia.org/wiki/{titre}"

_ROBOTS_CACHE: dict[str, Protego] = {}


def robots_autorise(url: str) -> bool:
    domaine = url.split("/")[2]
    if domaine not in _ROBOTS_CACHE:
        try:
            r = requests.get(
                f"https://{domaine}/robots.txt", headers=HEADERS, timeout=10
            )
            _ROBOTS_CACHE[domaine] = Protego.parse(
                r.text if r.status_code == 200 else ""
            )
        except Exception:
            _ROBOTS_CACHE[domaine] = Protego.parse("")
    return _ROBOTS_CACHE[domaine].can_fetch(url, HEADERS["User-Agent"])


def chercher_sirene(nom: str) -> dict:
    try:
        r = requests.get(
            SIRENE_URL, params={"q": nom, "limite": 20}, headers=HEADERS, timeout=10
        )
        r.raise_for_status()
        data = r.json()
        resultats = data.get("results", [])
        if not resultats:
            return {"resultat": "Non trouve dans SIRENE"}

        mots = nom.lower().split()
        candidats = [
            e
            for e in resultats
            if all(m in (e.get("nom_complet") or "").lower() for m in mots)
        ]
        if not candidats:
            candidats = resultats  # repli si aucun match strict

        principal = max(candidats, key=lambda e: e.get("nombre_etablissements") or 0)
        siege = principal.get("siege", {})
        return {
            "siren": principal.get("siren"),
            "denomination": principal.get("nom_complet"),
            "adresse_siege": siege.get("adresse"),
            "code_naf": siege.get("activite_principale"),
            "date_creation": siege.get("date_creation"),
            "nombre_etablissements": principal.get("nombre_etablissements"),
        }
    except Exception as e:
        return {"erreur": str(e)}


def resoudre_page_wikipedia(nom: str) -> str | None:
    try:
        r = requests.get(
            WIKIPEDIA_SEARCH_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": f"{nom} entreprise",
                "format": "json",
                "srlimit": 1,
            },
            headers=HEADERS,
            timeout=10,
        )
        resultats = r.json().get("query", {}).get("search", [])
        return resultats[0]["title"] if resultats else None
    except Exception:
        return None


def scraper_wikipedia(nom: str) -> dict:
    titre = resoudre_page_wikipedia(nom)
    if not titre:
        return {"erreur": "Page Wikipedia non trouvee"}
    url = WIKIPEDIA_PAGE_URL.format(titre=titre.replace(" ", "_"))
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        infobox = {}
        table = soup.select_one("table.infobox, table.wikitable")
        if table:
            for tr in table.select("tr"):
                th = tr.select_one("th")
                td = tr.select_one("td")
                if th and td:
                    cle = th.get_text(strip=True)
                    val = td.get_text(" ", strip=True)[:200]
                    infobox[cle] = val
        intro = ""
        for p in soup.select("#mw-content-text p"):
            if p.find_parent(class_=lambda c: c and "bandeau" in c):
                continue
            txt = p.get_text(strip=True)
            if len(txt) > 80:
                intro = txt[:500]
                break
        return {"infobox": infobox, "intro": intro, "url": url}
    except Exception as e:
        return {"erreur": str(e)}


def veille_presse(nom: str, nb_max: int = 10) -> list[dict]:
    query = nom.replace(" ", "+")
    url = f"https://www.bing.com/news/search?q={query}&format=RSS"
    if not robots_autorise(url):
        return [{"erreur": f"robots.txt interdit {url}"}]
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        feed = feedparser.parse(r.content)
        return [
            {
                "titre": e.get("title", ""),
                "source": e.get("source", {}).get("title", ""),
                "date": e.get("published", ""),
                "lien": e.get("link", ""),
            }
            for e in feed.entries[:nb_max]
        ]
    except Exception as e:
        return [{"erreur": str(e)}]


def construire_fiche(nom: str) -> dict:
    print(f"[*] Construction de la fiche pour : {nom}")
    fiche = {"entite": nom}
    fiche["sirene"] = chercher_sirene(nom)
    time.sleep(1)
    fiche["wikipedia"] = scraper_wikipedia(nom)
    time.sleep(1)
    fiche["presse"] = veille_presse(nom)
    fiche["nb_articles"] = len(fiche["presse"])
    return fiche


if __name__ == "__main__":
    fiches = {cible["nom"]: construire_fiche(cible["nom"]) for cible in CIBLES}

    with open("fiche_entreprises.json", "w", encoding="utf-8") as f:
        json.dump(fiches, f, indent=2, ensure_ascii=False)

    print("[+] Fiches sauvegardees : fiche_entreprises.json")
    for nom, fiche in fiches.items():
        print(
            f"    {nom} : SIREN {fiche['sirene'].get('siren', 'n/a')}, "
            f"{fiche['nb_articles']} articles"
        )
