# TP - Veille technologique automatisée (Blog du Modérateur)

Scraper qui récupère jusqu'à 200 articles récents de blogdumoderateur.com,
les exporte en CSV et les stocke en SQLite.

## Comment le lancer

```bash
pip install requests beautifulsoup4 lxml
python scraper_bdm.py --max 200 --csv articles.csv --db articles.db
```

## Les 3 questions avant la première requête

**1. Ai-je le droit ?**
Oui, pour les pages utilisées ici. J'ai lu `https://www.blogdumoderateur.com/robots.txt` :
il interdit `/admin`, `/wp-admin`, `/feed/`, `/comments`, les pages de recherche
(`?s=`), ..., mais pas les pages de catégorie (`/web/`, `/tech/`...) utilisées
par ce script.

**2. Est-ce personnel ?**
Non. On récupère seulement titre, URL, date, catégorie et chapô : ce sont des
données éditoriales publiques, pas des données personnelles. Le RGPD ne
s'applique pas ici.

**3. Suis-je discret ?**
Oui. Le script s'identifie honnêtement avec `User-Agent: IPSSI-scraper
(+contact@ipssi.fr)` (pas un faux User-Agent de navigateur), et attend 1,5
seconde entre chaque page.

## robots.txt : le scraping de `/feed/` est-il autorisé ?

Non. Le fichier contient, pour tous les robots (`User-agent: *`) :

```
Disallow: /feed/
Disallow: /*/feed/
```

Ce script n'utilise jamais ces URLs.

## Sélecteurs CSS : ce que demandait le sujet vs ce qui marche vraiment

Le sujet du TP donne des sélecteurs qui ne correspondent plus au site actuel. 
Je l'ai vérifié en téléchargeant une vraie page avec `requests` et en
inspectant le HTML reçu avec BeautifulSoup, plutôt qu'en me fiant seulement à
l'inspecteur du navigateur (le navigateur peut afficher du HTML déjà modifié
par du JavaScript, alors que `requests` montre exactement ce que le script
reçoit réellement).

| Champ     | Sélecteur du sujet | Résultat              | Sélecteur utilisé dans le script |
|-----------|---------------------|------------------------|-----------------------------------|
| titre     | `h2.post-title a`   | 0 résultat             | `h3.entry-title`                  |
| url       | `h2.post-title a[href]` | 0 résultat         | `href` du `<a>` qui enveloppe soit le `<h3>`, soit tout l'`<article>` (2 carte coexistent sur une même page) |
| date      | `time[datetime]`    | Fonctionne, inchangé  | `time[datetime]`                  |
| catégorie | `.cat-links a`      | 0 résultat             | `.favtag`                         |
| chapô     | `.entry-summary`    | Jamais présent sur les pages de listing | reste vide `""` |

Le champ **chapô** est donc toujours vide dans les livrables : ce n'est pas un
bug, la page qui liste les articles n'affiche simplement plus de résumé
(seuls titre, date et catégorie apparaissent sur la carte).

Autre chose trouvée en testant le style proposé par le sujet pour
`parse_articles` (section 5.2, la version "refactorisée") : le repli utilisé
pour catégorie/chapô, `(c.select_one(".cat-links a") or {"_t":""}).get_text(strip=True)`,
plante avec `AttributeError: 'dict' object has no attribute 'get_text'` dès
que le sélecteur ne trouve rien — un dict Python n'a pas de méthode
`get_text()`. Testé directement dans l'interpréteur pour confirmer.
`parse_articles` suit finalement la forme "boucle + `.append()`" de la
section 2.2 du sujet, avec un `if/else` explicite par champ optionnel
plutôt que ce repli cassé. La list-comprehension demandée par la checklist
(section 5.2) est utilisée ailleurs dans le script, dans `scrape_all` :
`nouveaux = [a for a in candidats if a["url"] not in vus]`.

## Pagination : la page d'accueil ne fonctionne pas

Le sujet demande de vérifier que `/page/2/` a la même structure que `/page/1/`.
C'est vrai pour la structure HTML, mais pas pour le contenu des articles :
`/page/2/`, `/page/3/`, etc. renvoient exactement les **mêmes 41 articles**
que `/page/1/`. Vérifié en comparant les URLs extraites de 5 pages : 0
nouvel article après la page 1.

Point vérifié : ce n'est **pas** un cache qui renvoie la
page entière à l'identique. D'autres blocs de la page changent bien à
chaque requête (par exemple le bandeau d'inscription à la newsletter en bas
de page affiche un texte différent à chaque rafraîchissement : "le meilleur
de l'actualité digitale" sur la page 1, "gagner du temps" sur la page 2,
"70 000 pros" sur la page 3). Le serveur régénère donc bien chaque page,
mais la requête qui va chercher la liste des articles, elle, ignore le
numéro de page et renvoie toujours les mêmes 41 premiers articles.

Les archives de catégorie (`/web/page/2/`, `/tech/page/2/`...), paginent correctement : chaque
page apporte bien de nouveaux articles.

**Solution retenue** : `scrape_all` garde exactement le même schéma que celui
du sujet (une seule boucle `while`, mêmes noms de variables `tous`/`page`/
`nouveaux`, même condition d'arrêt) — seule `BASE_URL` change, pointant vers
l'archive de la catégorie `web` (`/web/page/{n}/`) plutôt que vers la page
d'accueil cassée. La catégorie `web` suffit à elle seule à atteindre 200
articles uniques en 13 pages, sans avoir besoin d'agréger plusieurs
catégories ni de dédoublonner manuellement.

## Résultat de l'exécution

```
python scraper_bdm.py --max 200
```

- 200 articles récupérés depuis l'archive de la catégorie `web`, qui a suffi
  à elle seule pour atteindre la cible en 13 pages
- `articles.csv` : 200 lignes de données + 1 ligne d'en-tête, encodage UTF-8
- `articles.db` : table `articles`, `SELECT COUNT(*)` renvoie 200
- Aucune erreur HTTP rencontrée pendant ce run (donc le mécanisme de retry
  n'a pas été déclenché, mais il est en place et testé séparément : un
  timeout ou un 5xx relance jusqu'à 3 fois avec un délai qui double à chaque
  tentative, et un 429 attend la durée indiquée par l'en-tête `Retry-After`)
- En relançant le script une seconde fois, la console affiche
  `SQLite : 0 nouvelles lignes inserees` : c'est normal, ce sont les mêmes
  200 articles qu'au run précédent, et `INSERT OR IGNORE` (avec `url UNIQUE`)
  les ignore silencieusement au lieu de créer des doublons.

### Auteur 
- Awadi BEDJA
