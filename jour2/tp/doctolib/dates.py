"""Parsing des dates de rendez-vous affichees en francais sur les fiches."""

import re
from datetime import date

from config import MOIS_FR


def parser_date_creneau(texte: str) -> date | None:
    """Extrait une date 'JJ mois AAAA' d'un texte du type 'Prochain RDV le 14 aout 2026'."""
    match = re.search(r"(\d{1,2})\s+([a-zéû]+)\s+(\d{4})", texte.lower())
    if not match:
        return None
    jour, mois_nom, annee = match.groups()
    mois = MOIS_FR.get(mois_nom)
    if not mois:
        return None
    try:
        return date(int(annee), mois, int(jour))
    except ValueError:
        return None
