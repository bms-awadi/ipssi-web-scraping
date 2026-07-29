# TP Jour 3 - Scrapy : AlloCiné & Boursorama

### AlloCiné (`allocine/`, spider `films`)

| Champ | Sélecteur du sujet | Problème réel | Sélecteur corrigé |
|-------|---------------------|----------------|---------------------|
| Titre | `h1::text` | le vrai `<h1>` de la page est un lien de fil d'Ariane ("Cinéma"), pas le titre | `div.titlebar-title.titlebar-title-xl::text` |
| Réalisateur | `.meta-body-direction a::text` | le nom est dans un `<span>`, pas un `<a>` ; le bloc existe DEUX fois (réalisation "De" / scénario "Par") | XPath filtrant sur le label `"De"` |
| Note presse/spectateurs | `.stareval-note::text` / `:last-child` | les deux notes partagent la même classe CSS ; `:last-child` ne les distingue pas de façon fiable | XPath filtrant sur le libellé parent (`.rating-title` contenant "Presse"/"Spectateurs") |
| Année | `.meta-body-item strong::text` | pas de `<strong>` à cet endroit ; la date est dans `.meta-body-info span.date` | regex `\d{4}` sur le texte de date complet |

### Boursorama (`boursorama/`, spider `cac`)

| Champ | Sujet | Problème réel | Corrigé |
|-------|-------|----------------|---------|
| Lignes du tableau | `table.c-table tbody tr` | la page contient DEUX tableaux `.c-table` : un widget "Mes listes" générique (sans volume) + le vrai palmarès | `div.c-palmares table.c-table-top-flop tbody tr.c-table__row` |
| ISIN | extrait du slug d'URL (`href.split("/")[-2]`) | ce slug est un symbole interne Boursorama (ex. `1rPATE`), **pas** un code ISIN | crawl à deux niveaux : suivre le lien vers la fiche valeur, extraire `h2.c-faceplate__isin::text` |
| Cours/variation/volume | `cells[N].css("::text")` par position de colonne | fragile (dépend de l'ordre exact des colonnes) | classes CSS dédiées (`.c-instrument--last`, `.c-instrument--instant-variation`, `.c-instrument--totalvolume`) |

## Résultats

- `allocine/films.json` + `allocine/films.csv` : 50 films, 0 champ vide sur
  titre/année/réalisateur/url.
- `boursorama/bourse.db` (table `actions`) : 25 valeurs, 0 champ nul,
  `UNIQUE(isin)` vérifié fonctionnel (relance testée : aucun doublon inséré).
