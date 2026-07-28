import time


def scroll_to_bottom(driver, pauses: int = 3) -> None:
    """Defile progressivement jusqu'en bas de la page."""
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(pauses):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print(f"Scroll termine apres {i + 1} iteration(s)")
            break
        last_height = new_height
    else:
        print(f"Scroll effectue ({pauses} iterations)")
