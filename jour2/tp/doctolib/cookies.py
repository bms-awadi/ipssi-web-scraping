"""Gestion de la banniere de consentement cookies (Didomi)."""

import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def gerer_banniere_cookies(driver, wait: WebDriverWait) -> bool:
    """Clique sur le bouton d'acceptation de la banniere cookies si elle est presente."""
    selecteurs = [
        (By.XPATH, '//button[contains(text(),"Accepter")]'),
        (By.XPATH, '//button[contains(text(),"Tout accepter")]'),
        (By.XPATH, '//button[contains(text(),"Accepter tous")]'),
        (By.CSS_SELECTOR, "[data-test='cookie-consent-accept']"),
        (By.ID, "didomi-notice-agree-button"),
        (By.CSS_SELECTOR, "[data-testid='cookie-consent-accept']"),
    ]

    for by, selector in selecteurs:
        try:
            btn = wait.until(EC.element_to_be_clickable((by, selector)))
            btn.click()
            time.sleep(1)
            print("Banniere cookies acceptee")
            return True
        except (TimeoutException, NoSuchElementException):
            continue

    print("Aucune banniere cookies detectee")
    return False
