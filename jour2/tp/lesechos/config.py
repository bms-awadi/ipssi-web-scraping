import re

URL = "https://www.lesechos.fr"
JSON_PATH = "lesechos.json"
SCREENSHOT_DIR = "screenshots"
HEURE_RE = re.compile(r"mis à jour|il y a \d+", re.IGNORECASE)

# Nombre de pages d'article visitees pour recuperer chapeau/heure_publi (voir details.py)
LIMITE_DETAILS = 15
