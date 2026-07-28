import requests

from config import URL


def tester_requests() -> None:
    try:
        resp = requests.get(
            URL,
            timeout=10,
            headers={"User-Agent": "IPSSI-scraper (+contact@ipssi.fr)"},
        )
        html = resp.text

        if "search-result-card" in html or "chirurgien-dentiste" in html.lower():
            print("Le contenu semble present dans le HTML brut")
        else:
            print("Le contenu est charge dynamiquement (JavaScript requis)")
            print("Selenium est necessaire pour ce scraping")

        print(f"Taille de la reponse : {len(html)} caracteres")

    except Exception as e:
        print(f"Erreur avec requests : {e}")
        print("Selenium est recommande")
