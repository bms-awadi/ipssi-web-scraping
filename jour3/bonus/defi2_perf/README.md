# Défi 2 - Impact de CONCURRENT_REQUESTS sur la vitesse de crawl

Cible : spider `films` (projet `jour3/tp/allocine`), limité à 50 films
(la limite `MAX_FILMS` du spider lui-même, plus stricte que les "100" de
l'énoncé donc un plafond commun garanti sur les 3 runs).

## Run 1 - Réglages de production (`benchmark.py`)

Réglages de `settings.py` conservés (`AUTOTHROTTLE_ENABLED=True`,
`DOWNLOAD_DELAY=1.0`), seul `CONCURRENT_REQUESTS` varie :

| CONCURRENT_REQUESTS | temps (s) | items | items/s | ratio scraped/received |
|---|---|---|---|---|
| 1 | 66.8 | 50 | 0.75 | 0.89 |
| 4 | 68.7 | 50 | 0.73 | 0.89 |
| 8 | 69.9 | 50 | 0.72 | 0.89 |
| 16 | 70.1 | 50 | 0.71 | 0.89 |

**Constat surprenant : aucune différence mesurable.** Le temps ne bouge
quasiment pas entre 1 et 16 requêtes en parallèle.

### Pourquoi ? (1re explication)

`AUTOTHROTTLE_ENABLED=True` est actif, et `AUTOTHROTTLE_TARGET_CONCURRENCY`
n'a jamais été fixé dans `settings.py` -> il reste à sa valeur par défaut de
**1.0**. AutoThrottle ajuste dynamiquement le délai pour maintenir en
moyenne **une seule requête en vol** par domaine, *quelle que soit* la
valeur du plafond `CONCURRENT_REQUESTS`. Ce plafond ne fait qu'autoriser un
maximum AutoThrottle décide, lui, du nombre réellement utilisé. C'est
très exactement la réponse à *"pourquoi AUTOTHROTTLE peut-il battre une
valeur fixe élevée ?"* : une valeur fixe élevée sans throttle adaptatif
peut marteler un serveur lent et provoquer des 429/503 (donc des retries
qui *ralentissent* le crawl) ; AutoThrottle, lui, observe le temps de
réponse réel et n'accélère que si le serveur suit.

## Run 2 - AutoThrottle désactivé, délai fixe (`benchmark_no_throttle.py`)

`AUTOTHROTTLE_ENABLED=False`, `DOWNLOAD_DELAY=0.25` fixe,
`CONCURRENT_REQUESTS_PER_DOMAIN` aligné sur `CONCURRENT_REQUESTS` :

| CONCURRENT_REQUESTS | temps (s) | items/s |
|---|---|---|
| 1 | 19.6 | 2.55 |
| 4 | 18.8 | 2.65 |
| 8 | 19.0 | 2.63 |
| 16 | 19.1 | 2.62 |

**Toujours plat.** Cette fois la cause est différente : `DOWNLOAD_DELAY`
impose un délai minimum **entre deux requêtes envoyées vers le même
domaine**, quel que soit le nombre de requêtes déjà en vol en parallèle.
Avec un seul domaine crawlé (`allocine.fr`), ce délai à lui seul gate le
rythme d'émission des requêtes augmenter `CONCURRENT_REQUESTS` permet
d'avoir plus de requêtes *en attente de réponse* simultanément, mais pas
d'en *émettre* plus vite.

## Run 3 - Délai nul, pour isoler l'effet pur de la concurrence (`benchmark_delay0.py`)

`AUTOTHROTTLE_ENABLED=False`, `DOWNLOAD_DELAY=0` :

| CONCURRENT_REQUESTS | temps (s) | items/s |
|---|---|---|
| 1 | 6.1 | 8.23 |
| 4 | 3.7 | 13.66 |
| 8 | 4.0 | 12.62 |
| 16 | 3.8 | 13.18 |

**Ici, la concurrence compte enfin** : passer de 1 à 4 requêtes en
parallèle apporte un gain réel de **+66% de débit** (8.23 -> 13.66
items/s). Au-delà de 4, le gain devient négligeable (13.66 -> 12.62 -> 13.18,
un bruit de mesure plus qu'une tendance) : le facteur limitant n'est plus
la concurrence autorisée mais la latence réseau incompressible par requête
et le nombre de connexions que le serveur distant accepte réellement en
parallèle sur un seul domaine.

## Réponses aux questions posées

**"À partir de quelle valeur le gain devient-il négligeable ?"**
Sur cette cible (un seul domaine, 50 fiches), le gain plafonne dès
`CONCURRENT_REQUESTS` autour de 4 au-delà, ni le serveur ni le réseau ne permettent
d'aller plus vite. Ce seuil dépend du site cible (nombre de connexions
qu'il accepte) et n'est pas une constante universelle.

**"Pourquoi AUTOTHROTTLE peut-il battre une valeur fixe élevée ?"**
Parce qu'une valeur fixe élevée n'a aucun retour sur l'état réel du
serveur : si celui-ci ralentit ou renvoie des 429/503, une concurrence
fixe continue de cogner au même rythme, provoquant des retries qui
annulent le gain de vitesse. AutoThrottle observe la latence de chaque
réponse et adapte le délai en conséquence plus lent en façade, mais plus
robuste et souvent plus rapide *net* (moins d'échecs à rejouer) sur un
crawl long.

**"Que signifie un ratio `item_scraped_count / response_received_count`
< 0.5 sur AlloCiné ?"**
Ici le ratio observé est de 0.89 (50 items / 56 réponses) : sain les 6
réponses "sans item" correspondent exactement aux pages de liste/pagination
nécessaires pour atteindre 50 films (5 pages de listing, cf.
`request_depth_max: 5` dans les stats), pas à des échecs. Un ratio **< 0.5**
signifierait qu'**plus de la moitié des réponses ne produisent aucun
item** un signal d'alerte : soit un sélecteur cassé sur les fiches détail
(page téléchargée mais parsing vide), soit une pagination anormalement
profonde par rapport au nombre de films réellement extraits, soit un
`DropItem` déclenché en masse dans un pipeline. Sur un crawl à deux
niveaux comme celui-ci, ce ratio est une métrique de santé à surveiller en
prod.
