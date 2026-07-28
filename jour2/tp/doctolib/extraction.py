"""Extraction des fiches chirurgiens-dentistes depuis la page de resultats Doctolib.

Chaque fiche a un <a href=".../dentiste/nice/<slug>?...practice-...">, mais ce lien
n'enveloppe que le nom du praticien (pas l'adresse ni les disponibilites) : il faut donc
remonter jusqu'au conteneur de la carte via _racine_carte(). Les classes CSS internes
(nom, adresse, ...) sont des utilitaires Tailwind/design-system generiques qui changent
trop souvent pour etre fiables, donc on parse le texte visible de la carte plutot que
des selecteurs CSS.
"""

import os
import re
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import SCREENSHOT_DIR


def _racine_carte(lien):
    """Remonte du <a> jusqu'au conteneur complet de la fiche (nom, adresse, tarif,
    disponibilites). Tente d'abord la classe connue du design system Doctolib, puis
    remonte les parents jusqu'a obtenir un texte substantiel."""
    try:
        return lien.find_element(By.XPATH, "./ancestor::div[contains(@class,'dl-card')][1]")
    except NoSuchElementException:
        pass

    noeud = lien
    for _ in range(6):
        try:
            parent = noeud.find_element(By.XPATH, "..")
        except NoSuchElementException:
            break
        noeud = parent
        if len(noeud.text) > 80:
            break
    return noeud


def extraire_medecins(driver, wait: WebDriverWait, limite: int = 10) -> list[dict]:
    """Extrait les fiches chirurgiens-dentistes de la page de resultats Doctolib."""
    resultats = []

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-id='hcp-results']")))
    except TimeoutException:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"doctolib_erreur_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Erreur : resultats non charges - capture sauvegardee dans {screenshot_path}")
        return resultats

    liens = driver.find_elements(By.CSS_SELECTOR, "a[href*='practice-']")
    if not liens:
        liens = driver.find_elements(By.CSS_SELECTOR, "a[href*='/dentiste/nice/']")

    if not liens:
        print("Aucune carte trouvee")
        return resultats

    print(f"{len(liens)} cartes trouvees")

    for i, lien in enumerate(liens[:limite]):
        try:
            carte = _racine_carte(lien)
            lignes = [l.strip() for l in carte.text.split("\n") if l.strip()]

            nom = lignes[0] if lignes else "Non trouve"
            specialite = lignes[1] if len(lignes) > 1 else ""
            nom_specialite = f"{nom} - {specialite}" if specialite else nom

            # L'adresse commence a la 1ere ligne (apres nom/specialite) contenant un chiffre ;
            # si la ligne suivante est un code postal ("06200 Nice"), on la rattache.
            adresse = "Non trouvee"
            fin_adresse = 1
            for idx in range(2, len(lignes)):
                if any(c.isdigit() for c in lignes[idx]):
                    adresse = lignes[idx]
                    fin_adresse = idx
                    if idx + 1 < len(lignes) and re.match(r"^\d{5}\b", lignes[idx + 1]):
                        adresse += " " + lignes[idx + 1]
                        fin_adresse = idx + 1
                    break

            # Infos de disponibilite : on cible les lignes explicites ("Prochain RDV le ...",
            # "a partir du ..."), pas la grille de jours/tirets qui l'entoure.
            reste = lignes[fin_adresse + 1:]
            prochains_creneaux = [
                l for l in reste
                if "rdv" in l.lower() or "à partir du" in l.lower() or "disponib" in l.lower()
            ]
            if not prochains_creneaux:
                prochains_creneaux = ["Aucun creneau disponible"]

            url_fiche = lien.get_attribute("href") or "Non trouvee"

            texte_lower = carte.text.lower()
            type_consultation = ["Video"] if ("vidéo" in texte_lower or "téléconsult" in texte_lower) else ["Cabinet"]

            medecin = {
                "nom_specialite": nom_specialite,
                "adresse": adresse,
                "type_consultation": type_consultation,
                "prochains_creneaux": prochains_creneaux,
                "url_fiche": url_fiche,
            }
            resultats.append(medecin)
            print(f"  {i + 1}. {nom[:50]}")

        except Exception as e:
            print(f"  Erreur sur carte {i + 1} : {e}")
            continue

    return resultats
