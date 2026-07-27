# IPSSI - Web Scraping

Travaux du module Web Scraping (Mastère Dév, Data & IA), un dossier par jour.
Chaque jour contient deux parties :

- `td/` - pratique guidée en cours, non notée
- `tp/` - exercice noté, rendu sur ce repo

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
source .venv/bin/activate         # macOS / Linux
pip install -r requirements.txt
```

## Jour 1 - Requests & BeautifulSoup

Scraper de veille technologique sur le Blog du Modérateur (`requests` +
`BeautifulSoup4`, export CSV + SQLite).

- [`jour1/tp/`](jour1/tp/), le rendu : `scraper_bdm.py`, `articles.csv`, `articles.db`, et un `README.md` qui détaille le cadre légal et les écarts trouvés entre le sujet et le site réel.
- [`jour1/td/`](jour1/td/) - la version pratiquée en cours.
- [`jour1/bonus/`](jour1/bonus/) - défis autonomes du sujet.

## À venir

Jour 2 à 5 seront ajoutés au fur et à mesure de la semaine.


### Auteur
- Awadi BEDJA