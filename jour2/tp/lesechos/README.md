# TD 2.2 Les Echos : titres à la une

## Cadre légal

`https://www.lesechos.fr/robots.txt`, bloc `User-agent: *` :

```
Disallow: /internal
Disallow: /recherche
```

La page d'accueil (`/`) n'est **pas** interdite pour un robot générique
contrairement à la longue liste de bots nommément bloqués juste en dessous
(GPTBot, ClaudeBot, Amazonbot, CCBot, etc.), qui elle ne concerne que ces
robots précis. Scraping de la page d'accueil autorisé.

## Pourquoi Selenium et pas requests ?

1. **Contenu en JS** : `requests` seul (`requests_check.py`) reçoit un
   `403 Forbidden` avant même de savoir si le HTML contient les articles
   le WAF bloque la requête, pas seulement le rendu.
2. **Le WAF cible spécifiquement le mode headless** : Selenium headless
   obtient la même page *"Access Denied"* qu'un simple `requests`. Seul le
   mode normal (visible), sans flag d'évasion particulier, passe. C'est
   l'inverse du cas Doctolib (où headless fonctionne normalement) la
   comparaison headless/normal n'a donc pas le même sens sur les deux sites,
   voir ci-dessous.

## Structure

| Fichier | Rôle |
|---|---|
| `lesechos_scraper.py` | Point d'entrée : requests → headless → normal → extraction → export |
| `config.py` | Constantes (URL, chemin de sortie, regex de détection d'heure) |
| `browser.py` | Configuration du driver Chrome (normal / headless) |
| `requests_check.py` | Étape 1 : vérifie que `requests` seul ne suffit pas (403) |
| `extraction.py` | Repérage des cartes `<article>` sur la page d'accueil et extraction des 5 champs + `url_article` |
| `details.py` | Visite la page de chaque article pour compléter `chapeau` et `heure_publi` |

`config.SCREENSHOT_DIR` ("screenshots") reçoit une capture automatique si le
mode normal échoue (résultats non chargés, page d'erreur, etc.), même
mécanisme que côté Doctolib.

## Utilisation

```
python lesechos_scraper.py
```

- `requests` seul : `HTTP 403` (bloqué, confirmé) -> Headless : bloqué
(`TimeoutException`, Access Denied) → Normal : ~2 s (réussi) -> articles
extraits -> `lesechos.json`.

Comparaison headless vs normal : ici ce n'est pas un
gain de vitesse (le point habituel), c'est un **blocage total en headless**
- la vraie donnée intéressante de cette mesure sur ce site précis.

## Sélecteurs utilisés

Le site utilise des classes CSS générées automatiquement (style
`sc-19z4l96-2 jmiLnY`, propres à chaque déploiement) : inutilisables comme
sélecteurs stables. Extraction basée sur la structure et le texte à la
place :

- carte : `article`
- titre : attribut `title` du premier `a[href]` de la carte (plus fiable
  que le texte affiché, qui peut être tronqué visuellement)
- rubrique : dernière ligne de texte de la carte (hors `"PREMIUM"`)
- `heure_publi` : ligne contenant *"Mis à jour"* ou un motif *"il y a N"*
  absente sur la plupart des cartes (feature affichée seulement sur
  certains articles, pas un bug)
- `chapeau` : aucun résumé affiché sur les cartes de la page d'accueil de
  ce site (vérifié) → complété a posteriori depuis `meta[name="description"]`
  sur la page de l'article (voir `details.py`)
- `premium` : présence littérale du texte `"PREMIUM"` sur la carte (plus
  fiable que les icônes SVG, qui n'ont pas de classe distinctive)
- `url_article` : `href` du lien de la carte (déjà résolu en URL absolue par
  Selenium), permet de vérifier chaque entrée directement dans un navigateur

## Chapeau et heure de publication

Ces deux champs ne sont pas affichés sur les cartes de la page d'accueil.
`details.py` visite la page de chacun des `LIMITE_DETAILS` (15 par défaut,
`config.py`) premiers articles et lit :

- `chapeau` : balise `<meta name="description">`
- `heure_publi` : balise `<meta property="article:published_time">`, repli
  sur l'attribut `datetime` d'une balise `<time>`

Ces métadonnées sont choisies plutôt que le contenu visible de la page pour
deux raisons : elles sont présentes côté serveur même sur les articles
réservés aux abonnés (le corps du texte, lui, est tronqué par le paywall),
et elles ne dépendent pas des classes CSS générées par le bundler.

La limite à 15 est volontaire : chaque article visité est une requête de
plus sur un site protégé par un WAF (voir plus haut) mieux vaut rester
discret qu'exhaustif. Un court délai aléatoire (0,5 à 1,5 s) sépare chaque
visite. Les articles au-delà de la limite gardent `chapeau`/`heure_publi`
tels que trouvés sur la carte (souvent vides).
