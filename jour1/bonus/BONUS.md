# Défis bonus

Les 3 défis utilisent le même site : **Numerama**.

## Défi 1 — Adapter le scraper à un site différent

Site différent du Blog du Modérateur par le sujet (tech grand public plutôt
que marketing/web) et par la structure HTML (thème différent).

Script : [`scraper_numerama.py`](scraper_numerama.py), autonome (sa propre
fonction `get_page()`/`scrape_all()`/`sauver_csv()`, sans dépendre de
`jour1/tp/`). Réutilisé tel quel par les défis 2 et 3 ci-dessous.

**Sélecteurs identifiés :**

| Champ     | Sélecteur                                    |
|-----------|-------------------------------------------------|
| carte     | `.post-card`                                     |
| titre     | `.post-card__title` (texte)                      |
| url       | `.post-card__title` (attribut `href`)            |
| date      | `.post-card__date` (texte, format `JJ.MM.AAAA HH:MM`) |
| catégorie | pas de classe dédiée sur les petites cartes : déduite du premier segment de l'URL (`/vroom/...`, `/sciences/...`, `/pop-culture/...`) |

**Problèmes rencontrés et corrigés :**

1. Numerama ne déclare pas son encodage dans l'en-tête HTTP
   `Content-Type`, donc `requests` retombait par défaut sur `ISO-8859-1` et
   cassait les accents (`l'Ã©pisode` au lieu de `l'épisode`). Corrigé en
   donnant à BeautifulSoup les octets bruts (`r.content`) plutôt que le
   texte déjà mal décodé par `requests` (`r.text`).
2. Certaines cartes de la page d'accueil sont des liens publicitaires
   natifs (`native.humanoid.fr/...`) plutôt que de vrais articles —
   filtrées en ne gardant que les liens dont l'URL commence par
   `https://www.numerama.com/`.
3. Un même article peut apparaître deux fois sur une seule page (en
   vedette + dans le flux normal). Le premier `scrape_all()` mettait à jour
   la liste des URLs déjà vues seulement après avoir traité toute la page,
   donc les deux occurrences passaient le filtre (page 1 : 50 cartes mais
   seulement 45 URLs uniques). Corrigé en vérifiant et mettant à jour cette
   liste article par article, au fil de la boucle.

Ce qui est plus simple qu'avec le Blog du Modérateur : un seul gabarit de
carte (`.post-card`) au lieu de deux, donc pas besoin de gérer plusieurs cas
pour retrouver le lien. Ce qui est plus difficile : l'absence de charset
dans les en-têtes HTTP, l'absence de sélecteur de catégorie explicite (il
faut la déduire de l'URL), et les doublons intra-page. Le sélecteur du
titre est du même type que sur le Blog du Modérateur (un texte de balise de
titre dans un lien), seul le nom de classe change.

## Défi 2 — Détecter les nouveautés entre deux crawls

Script : [`diff_scrapes.py`](diff_scrapes.py), code repris tel quel du sujet.

Démo avec un vrai écart temporel (pas simulé) : deux exports de
`scraper_numerama.py`, `snapshot_1.csv` et `snapshot_2.csv`.

```
python diff_scrapes.py snapshot_1.csv snapshot_2.csv
Nouveaux : 0
Disparus : 0
Stables : 20
```

**Résultat et limite** : l'écart réel entre ces deux crawls n'est
que d'environ 1 minute 30 (17:33:03 puis 17:34:37), pas les 2h/24h demandés
par le vrai défi, donc 0 nouveauté n'a rien de surprenant car l'intervalle est bien trop court pour répondre à la vraie question du défi.



## Défi 3 — Benchmark honnête du throttling

Script : [`benchmark_throttling.py`](benchmark_throttling.py), sur
`numerama.com/page/{n}/`. Pour rester civil envers le site pendant cette
démo, seules les lignes 2 et 5 pages ont été mesurées réellement (21
requêtes au total), pas la grille complète 2/5/10 × 0,5/1/2s.

| Pages | 0.5 s | 1.0 s | 2.0 s |
|-------|-------|-------|-------|
| 2     | 2.4s  | 2.7s  | 4.7s  |
| 5     | 5.0s  | 6.7s  | 11.7s |
| 10    | (non mesuré, voir extrapolation) | | |

