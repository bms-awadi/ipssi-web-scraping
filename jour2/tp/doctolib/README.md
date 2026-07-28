# TD 2.1  Doctolib : chirurgiens-dentistes à Nice

## Remarque

Le `robots.txt` de doctolib.fr interdit `/search`, `*/doctors/*` et
`*/availabilities*` et la page
`/dentiste/nice` route en réalité côté client vers `/search?keyword=dentiste&location=nice`
(confirmé via `document.baseURI` en DevTools). Ce dossier contient malgré tout
un scraper fonctionnel exécuté sur les données réelles du site, à usage
strictement pédagogique et local (pas de republication, pas de volume).

## Structure

| Fichier | Rôle |
|---|---|
| `doctolib_scraper.py` | Point d'entrée : orchestre les étapes 1 à 8 du sujet |
| `config.py` | Constantes (URL, chemins de sortie, mois français) |
| `browser.py` | Configuration du driver Chrome (normal / headless) |
| `cookies.py` | Gestion de la bannière de consentement (Didomi) |
| `scroll.py` | Défilement pour charger le contenu paresseux |
| `extraction.py` | Repérage des fiches et extraction des 5 champs |
| `dates.py` | Parsing des dates françaises ("14 août 2026") |
| `requests_check.py` | Étape 1 : vérifie que `requests` seul ne suffit pas |

Chaque fiche est en réalité un `<a href=".../dentiste/nice/<slug>?...practice-...">`
qui n'enveloppe que le nom du praticien, pas le reste de la carte (adresse,
tarif, disponibilités). `extraction._racine_carte()` remonte jusqu'au
conteneur complet avant de lire le texte visible ligne par ligne les
classes CSS internes (utilitaires Tailwind/design system) changent trop
souvent pour servir de sélecteurs stables.

## Utilisation

```
python doctolib_scraper.py
```

Produit :
- `doctolib.json` les fiches extraites (5 champs du sujet + `prochain_rdv_date`)
- `doctolib_disponibles_semaine.json` sous-ensemble filtré : uniquement les
  praticiens dont le prochain RDV tombe dans les 7 jours suivant l'exécution
- `screenshots/doctolib_erreur_<horodatage>.png` capture automatique si
  l'attente des résultats échoue

## Comparaison headless / normal

Dernière exécution mesurée :

| Mode | Temps | Portée mesurée |
|---|---|---|
| Headless | ~65 s | navigation + bannière cookies + attente du conteneur de résultats uniquement |
| Normal | ~125 s | navigation + cookies + attente + **scroll (4 pauses de 1,5 s) + extraction de 10 fiches** |

Les deux chiffres ne sont pas directement comparables : le mode headless
s'arrête dès que le conteneur de résultats apparaît, alors que le mode
normal inclut en plus le scroll et l'extraction complète. Sur ce site, le
gain du headless n'est donc pas mesuré sur le même périmètre pour une
comparaison à périmètre égal il faudrait chronométrer l'extraction complète
dans les deux modes.

## Choix techniques

- **URL** : `/chirurgien-dentiste/nice` (slug du sujet) redirige silencieusement
  vers l'accueil le bon slug actuel est `/dentiste/nice` (confirmé par
  fetch direct : titre de page correct côté serveur).
- **Anti-détection minimal** : `--disable-blink-features=AutomationControlled`
  et `excludeSwitches: ["enable-automation"]`, plus un user-agent explicite
  suffisant ici, pas de contournement supplémentaire.
- **Sélecteurs de carte** : `a[href*='practice-']` (repli sur
  `a[href*='/dentiste/nice/']`) plutôt que les anciens `data-test-id`/classes
  devinés, qui ne correspondaient plus au markup actuel.
- **Extraction par texte plutôt que par classe CSS** : les classes internes
  (nom, adresse, prix) sont des utilitaires Tailwind générés, instables d'un
  déploiement à l'autre. Le texte visible de la carte, lui, garde un ordre
  stable (nom / spécialité / adresse / disponibilités).
- **Filtre "7 prochains jours"** : seules les fiches affichant explicitement
  un "Prochain RDV le …" sont datées ; les fiches montrant une grille de
  jours sans ce badge ressortent avec `prochain_rdv_date: null` (créneau
  potentiellement disponible dans la semaine affichée, mais non confirmé par
  le texte scrapé).
