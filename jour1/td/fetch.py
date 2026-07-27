import requests

BASE_URL = "https://www.blogdumoderateur.com"
TIMEOUT = 10

CATEGORIES = ["web", "tech", "marketing", "social", "ia"]

# User-Agent: pour éviter d'envoyer python-requests/x.x", que beaucoup de sites bloquent
# si on veut se faire accepter
# Accept-Language dit au serveur qu'on prefere du contenu en francais
# comme le ferait un navigateur configure en fr-FR.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}


def new_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def get_page(session, category, page_number):
    url = (
        f"{BASE_URL}/{category}/"
        if page_number == 1
        else f"{BASE_URL}/{category}/page/{page_number}/"
    )
    try:
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"Erreur HTTP {category} page {page_number} : {e}")
        return None
    except requests.Timeout:
        print(f"Timeout depasse {category} page {page_number}")
        return None
    return response.text
