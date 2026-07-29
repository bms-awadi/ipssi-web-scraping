# Jour 3 - Défis autonomes (bonus du TP)

Les 3 défis proposés en fin de TP, réalisés à la suite du TP principal
(AlloCiné + Boursorama).

## Défi 1 - Spider sur un site régional (voir [`nicematin/`](nicematin/))

Nice-Matin (`/alpes-maritimes/` + `/var/`), spider `articles` à un seul
niveau, Item à 3 champs (`titre`, `url`, `categorie`), `CleanPipeline` +
`DedupPipeline`, export `articles.csv`. 26 articles uniques.

## Défi 2 - Analyse de performance (voir [`defi2_perf/`](defi2_perf/))

Benchmark de `CONCURRENT_REQUESTS` (1/4/8/16) sur le spider `films`, en 3
temps : réglages de prod (plat, à cause d'AutoThrottle), délai fixe sans
throttle (toujours plat, à cause de `DOWNLOAD_DELAY`), délai nul (la
concurrence compte enfin, gain négligeable après 4).

## Défi 3 - SQL et interprétation financière (voir [`defi3_sql/`](defi3_sql/))

Requêtes SQL (top hausses/baisses, volume anormal) sur `bourse.db`, export
CSV, confrontation de 2 cas (ALTEN +19,3%, Sopra Steria +15,3%) avec de
vraies actualités financières trouvées sur le web, les deux confirmées à
moins de 1 point de variation par rapport à la presse.
