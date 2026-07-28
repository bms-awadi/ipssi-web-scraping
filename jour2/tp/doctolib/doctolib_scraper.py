"""TP Jour 2 - TD 2.1 : Doctolib, fiches chirurgiens-dentistes a Nice.

Pipeline : requests (etape 1, montre que JS est necessaire) -> Selenium headless
(mesure de temps) -> Selenium normal (banniere cookies, scroll, extraction) -> export JSON.
Voir README.md pour le detail des choix techniques et la comparaison headless/normal.
"""

import json
import os
import time
from datetime import date, datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from browser import make_driver
from config import JSON_PATH, JSON_PATH_DISPO, SCREENSHOT_DIR, URL
from cookies import gerer_banniere_cookies
from dates import parser_date_creneau
from extraction import extraire_medecins
from requests_check import tester_requests
from scroll import scroll_to_bottom


def mesurer_headless() -> float | None:
    """Etape 2 : mode headless, chronometre pour comparaison avec le mode normal."""
    t0 = time.time()
    driver = make_driver(headless=True)
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        gerer_banniere_cookies(driver, wait)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-id='hcp-results']")))
        duree = time.time() - t0
        print(f"Mode headless reussi en {duree:.1f}s")
        return duree
    except Exception as e:
        print(f"Mode headless echoue ({type(e).__name__}) : {e}")
        return None
    finally:
        driver.quit()


def filtrer_semaine(medecins: list[dict]) -> list[dict]:
    """Ajoute la date du prochain RDV parsee et filtre ceux disponibles sous 7 jours."""
    aujourd_hui = date.today()
    limite_semaine = aujourd_hui + timedelta(days=7)

    for med in medecins:
        date_rdv = next(
            (d for d in (parser_date_creneau(c) for c in med["prochains_creneaux"]) if d),
            None,
        )
        med["prochain_rdv_date"] = date_rdv.isoformat() if date_rdv else None

    return [
        med for med in medecins
        if med["prochain_rdv_date"]
        and aujourd_hui <= date.fromisoformat(med["prochain_rdv_date"]) <= limite_semaine
    ]


def main():
    print("Scraper Doctolib - chirurgiens-dentistes a Nice")

    print("\nEtape 1 : test avec requests")
    tester_requests()

    print("\nEtape 2 : mode headless")
    t_headless = mesurer_headless()

    print("\nEtape 3 : mode normal (visible)")
    t0 = time.time()
    t_normal = 0
    driver = make_driver(headless=False)

    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        print("\nEtape 4 : gestion des cookies")
        gerer_banniere_cookies(driver, wait)

        print("\nEtape 5 : attente des resultats")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-id='hcp-results']")))
        print("Resultats charges")

        print("\nEtape 6 : scroll pour charger plus de resultats")
        scroll_to_bottom(driver, pauses=4)

        print("\nEtape 7 : extraction des chirurgiens-dentistes")
        medecins = extraire_medecins(driver, wait, limite=10)

        t_normal = time.time() - t0
        print(f"\nTemps d'execution mode normal : {t_normal:.1f}s")

        medecins_semaine = filtrer_semaine(medecins)

        print("\nEtape 8 : export des donnees")
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(medecins, f, indent=2, ensure_ascii=False)
        print(f"{len(medecins)} chirurgiens-dentistes exportes dans {JSON_PATH}")

        with open(JSON_PATH_DISPO, "w", encoding="utf-8") as f:
            json.dump(medecins_semaine, f, indent=2, ensure_ascii=False)
        print(f"{len(medecins_semaine)} avec RDV sous 7 jours exportes dans {JSON_PATH_DISPO}")

        print("\nResume des donnees extraites")
        for i, med in enumerate(medecins, 1):
            print(f"\n{i}. {med['nom_specialite']}")
            print(f"   Adresse : {med['adresse']}")
            print(f"   Consultation : {', '.join(med['type_consultation'])}")
            print(f"   Creneaux : {', '.join(med['prochains_creneaux'][:2])}")
            print(f"   URL : {med['url_fiche'][:60]}...")

        print(f"\n{len(medecins_semaine)} praticien(s) avec un RDV dans les 7 prochains jours")
        for med in medecins_semaine:
            print(f"  - {med['nom_specialite']} - {med['adresse']} - RDV le {med['prochain_rdv_date']}")

    except Exception as e:
        print(f"\nErreur lors de l'execution ({type(e).__name__}) : {e}")
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"doctolib_erreur_{timestamp}.png")
        if driver.save_screenshot(screenshot_path):
            print(f"Capture d'ecran sauvegardee dans {os.path.abspath(screenshot_path)}")
        else:
            print("La capture d'ecran a echoue (driver probablement dans un etat invalide)")

    finally:
        driver.quit()
        print("\nDriver ferme")

    print("\nComparaison des temps d'execution")
    print(f"Mode headless : {t_headless:.1f}s" if t_headless is not None else "Mode headless : echec")
    print(f"Mode normal   : {t_normal:.1f}s")


if __name__ == "__main__":
    main()
