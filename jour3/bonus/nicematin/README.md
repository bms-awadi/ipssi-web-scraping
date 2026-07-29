# Défi 1 - Spider sur un site régional (Nice-Matin)

**Cible :** `nicematin.com` (Alpes-Maritimes + Var), pages `/alpes-maritimes/`
et `/var/` le journal régional de référence pour la région où j'habite
(Nice).

## Vérifications avant écriture du spider

- `robots.txt` : `/alpes-maritimes/` et `/var/` ne sont pas dans les
  `Disallow`. En revanche le fichier impose un **`Crawl-delay: 10`**
  explicite la seule des cibles du Jour 3 à préciser un délai chiffré
  plutôt que de laisser la civilité technique à l'appréciation du scraper.
  `DOWNLOAD_DELAY` est donc réglé à `10.0` (vs `1.0` pour AlloCiné/Boursorama).
- Structure inspectée par téléchargement + lecture manuelle (pas de
  `scrapy shell` disponible dans cet environnement, mais même démarche :
  valider avant d'écrire le spider).

## Item (3 champs, comme demandé)

`titre`, `url`, `categorie` (commune + rubrique, sert de description la
page liste n'affiche aucune date).

## Pièges rencontrés

- La page recycle certaines cartes entre plusieurs blocs (un article "à la
  une" republié ailleurs) : sur `/alpes-maritimes/` seule, seulement **13
  articles uniques** sur 15 lignes brutes sous la barre des 20 exigés.
  Ajout de `/var/` (même journal, département voisin) + un `DedupPipeline`
  (rejette les doublons d'URL via `DropItem`) -> **26 articles uniques**.

## Différences avec AlloCiné (5 lignes)

1. **Structure imprévisible vs stable** : AlloCiné utilise des classes CSS
   stables et dédiées (`.meta-title-link`, `.stareval-note`) ; Nice-Matin
   utilise des classes utilitaires génériques (`fs-6 f-serif mb-0 lc-3
   fw-medium`, type Bootstrap) qui décrivent l'apparence, pas le rôle
   sémantique bien moins lisible et bien plus fragile à un futur
   redesign.
2. **Un seul niveau vs deux niveaux** : contrairement à AlloCiné/Boursorama
   (liste -> fiche détail), toutes les données utiles ici sont déjà sur la
   page liste spider à un seul niveau, plus simple.
3. **Pas de date exploitable** : AlloCiné a une date structurée
   (`.meta-body-info span.date`) ; ici aucune date n'apparaît sur la liste
   -> la catégorie/commune sert de substitut, comme permis par l'énoncé.
4. **Contenu dupliqué** : AlloCiné n'a jamais présenté le même film deux
   fois sur une page liste ; ici, la mise en page par blocs ("à la une",
   "populaire"...) répète parfois le même article -> nécessité d'un
   `DedupPipeline`, absent des deux autres projets.
5. **`Crawl-delay` explicite** : seul site du Jour 3 à préciser un délai
   chiffré dans `robots.txt`, plutôt que de laisser le choix du délai à
   l'appréciation du développeur.

## Lancer le crawl

```bash
cd nicematin
scrapy crawl articles -L INFO
```

Exporte `articles.csv` (26 lignes, 0 doublon).
