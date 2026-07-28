import random
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _meta(driver, css: str) -> str:
    try:
        return (
            driver.find_element(By.CSS_SELECTOR, css).get_attribute("content") or ""
        ).strip()
    except NoSuchElementException:
        return ""


def extraire_details(driver) -> tuple[str, str]:
    chapeau = _meta(driver, "meta[name='description']")

    heure_publi = _meta(driver, "meta[property='article:published_time']")
    if not heure_publi:
        try:
            el = driver.find_element(By.CSS_SELECTOR, "time")
            heure_publi = el.get_attribute("datetime") or el.text.strip()
        except NoSuchElementException:
            pass

    return chapeau, heure_publi


def enrichir_articles(driver, articles: list[dict], limite: int = 15) -> None:
    a_visiter = [a for a in articles[:limite] if a.get("url_article")]

    for i, art in enumerate(a_visiter):
        try:
            driver.get(art["url_article"])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            chapeau, heure = extraire_details(driver)
            if chapeau:
                art["chapeau"] = chapeau
            if heure:
                art["heure_publi"] = heure
            print(f"  {i + 1}/{len(a_visiter)} détaillé : {art['titre'][:50]}")
        except TimeoutException:
            print(f"  {i + 1}/{len(a_visiter)} ignoré (timeout) : {art['titre'][:50]}")
        except Exception as e:
            print(
                f"  {i + 1}/{len(a_visiter)} ignoré ({type(e).__name__}) : {art['titre'][:50]}"
            )

        time.sleep(random.uniform(0.5, 1.5))
