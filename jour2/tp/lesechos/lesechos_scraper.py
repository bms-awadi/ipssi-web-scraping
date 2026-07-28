import json
import os
import time
from datetime import datetime

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from browser import make_driver
from config import JSON_PATH, LIMITE_DETAILS, SCREENSHOT_DIR, URL
from details import enrichir_articles
from extraction import extraire_articles
from requests_check import tester_requests


def main():
    tester_requests()

    # Headless : documente le blocage WAF plutot que de le contourner.
    t0 = time.time()
    d1 = make_driver(headless=True)
    try:
        d1.get(URL)
        WebDriverWait(d1, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )
        t_headless = time.time() - t0
        print(f"Headless : {t_headless:.1f}s (reussi)")
    except (TimeoutException, WebDriverException) as e:
        print(f"Headless : bloque ({e.__class__.__name__}) - voir README")
    finally:
        d1.quit()

    # Normal (visible) : celui qui fonctionne reellement sur ce site.
    t0 = time.time()
    driver = make_driver(headless=False)
    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )
        t_normal = time.time() - t0
        print(f"Normal   : {t_normal:.1f}s")

        articles = extraire_articles(driver)
        print(f"{len(articles)} articles extraits")

        print(
            f"Détail de {min(LIMITE_DETAILS, len(articles))} article(s) (chapeau, heure_publi)"
        )
        enrichir_articles(driver, articles, limite=LIMITE_DETAILS)

        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"Exporte -> {JSON_PATH}")
    except Exception as e:
        print(f"Erreur en mode normal ({type(e).__name__}) : {e}")
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(
            SCREENSHOT_DIR, f"lesechos_erreur_{timestamp}.png"
        )
        if driver.save_screenshot(screenshot_path):
            print(
                f"Capture d'ecran sauvegardee dans {os.path.abspath(screenshot_path)}"
            )
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
