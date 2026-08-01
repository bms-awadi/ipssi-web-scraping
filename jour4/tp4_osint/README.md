# TP4 - OSINT

## Choix des cibles
### TD 4.1 - Inria et Universite de Montpellier

Une these ne se "candidate" pas de la meme facon qu'un
poste salarie, mais le meme reflexe technique s'applique : avant de
viser un laboratoire, on peut evaluer sa maturite technique comme on
le ferait pour un employeur. D'ou le choix de deux structures de
recherche en informatique/IA plutot que deux entreprises :

- **Inria** (institut national de recherche en informatique et en
  automatique) : institut public specifiquement dedie a ce champ, la
  reference francaise pour une these en informatique/IA.
- **Universite de Montpellier** : ancrage regional (l'ecole elle-meme
  est a Montpellier), etablissement multidisciplinaire qui heberge des
  laboratoires de recherche en informatique (dont le LIRMM, rattache
  au CNRS et a l'universite).

Ensemble, ces deux structures donnent un contraste utile pour l'analyse
technique : institut national specialise contre universite regionale
generaliste, ce qui a produit deux profils de securite reellement
differents (voir resultats plus bas) plutot qu'une simple redite du
meme type d'infrastructure.

### TD 4.2 et TD 4.3 - Amadeus, Capgemini, Mistral AI

- **Amadeus** (amadeus.com) : grande entreprise tech de Sophia
  Antipolis (Cote d'Azur), gros recruteur dev/data dans la region.
- **Capgemini** (capgemini.com) : ESN nationale (CAC40), gros volume
  d'embauche junior/stagiaire, choix qui satisfait litteralement la
  consigne du TD 4.2 ("entreprise cotee au CAC40").
- **Mistral AI** (mistral.ai) : startup francaise d'IA generative,
  dans le champ direct du Mastere.

Le fil conducteur retenu pour ces deux TD : preparer une recherche
d'emploi/stage en enquetant sur plusieurs employeurs potentiels avant
de candidater ou de passer un entretien. TD 4.2 construit une fiche de
renseignement par entreprise, TD 4.3 fait une veille de presse continue
sur les memes noms.

---

## TD 4.1 - Empreinte technique (`td41_domaine.py`)

```bash
python td41_domaine.py
```

-> `rapport_domaines.json` (un rapport par cible : WHOIS, en-tetes
HTTP, sous-domaines crt.sh, robots.txt).

### Choix techniques

- **GET au lieu de HEAD** pour les en-tetes HTTP. Verifie : une
  requete HEAD ne renvoie ni Content-Security-Policy ni
  Strict-Transport-Security sur les domaines testes, meme quand le
  site les a reellement (verifie sur capgemini.com : GET renvoie les
  deux, HEAD aucun des deux). Utiliser HEAD ferait donc conclure a
  tort a l'absence de ces protections dans un rapport d'audit.
- **Retry avec backoff exponentiel** (3 tentatives, 3/6/9s, timeout
  40s) pour crt.sh, qui echoue de facon non deterministique : sur 3
  executions successives du meme script, ce ne sont jamais les memes
  cibles qui echouent (Capgemini+Mistral AI, puis Amadeus+Mistral AI,
  puis Mistral AI seul). Ce n'est pas un bug de notre cote, mais une
  limite reelle du service communautaire gratuit sous charge.
- **Split des `name_value` sur les retours a la ligne** avant
  dedoublonnage : un certificat multi-domaines (SAN) revient comme une
  seule entree crt.sh dont le champ contient plusieurs hostnames
  concatenes - sans ce split on obtient des "sous-domaines" absurdes
  de plusieurs lignes au lieu d'un hostname par entree.
- **Le script accepte un domaine en argument** en plus de la boucle
  par defaut sur Inria/Universite de Montpellier, pour servir aussi au
  Defi 2 sans dupliquer le code (`python td41_domaine.py un-domaine.fr`).

### Resultats reels obtenus

- **Inria** : registrar GIP RENATER (l'operateur du reseau francais de
  la recherche et de l'enseignement, coherent avec un institut public),
  200 sous-domaines trouves (dont des sous-domaines d'evenements
  passes comme `50ans.inria.fr`, des adresses par site comme
  `sophia.inria.fr`), HSTS present mais pas de CSP. Curiosite : le
  serveur renvoie deux fois le meme en-tete `X-Frame-Options`
  ("SAMEORIGIN, SAMEORIGIN"), une petite anomalie de configuration.
- **Universite de Montpellier** : registrar egalement GIP RENATER, CSP
  et HSTS tous les deux presents (meilleure posture que Inria sur ce
  point precis), 200 sous-domaines trouves dont plusieurs interessants
  d'un point de vue securite : `adminweb-prep.umontpellier.fr`
  (panneau d'administration visiblement de pre-production, expose
  publiquement) et deux instances Prometheus Alertmanager
  (`alertmanager.azimuth.crd.meso.umontpellier.fr`,
  `alertmanager.cloud.meso.umontpellier.fr`) - un outil de supervision
  interne qui ne devrait normalement pas etre visible depuis
  l'exterieur.

### Questions d'analyse

1. **Ai-je le droit ?** Oui. WHOIS et crt.sh sont des registres publics
   dont la consultation est le service prevu.
2. **Est-ce personnel ?** Non. Donnees techniques uniquement :
   registrar, serveurs de noms, sous-domaines, en-tetes HTTP.
3. **Suis-je discret ?** Oui. User-Agent identifiable
   (`IPSSI-OSINT (+cours@ipssi.fr)`), `time.sleep(1)` entre chaque
   cible, `robots.txt` consulte pour chaque domaine.

---

## TD 4.2 - Cartographie des entreprises (`td42_entite.py`)

```bash
python td42_entite.py
```

-> `fiche_entreprises.json` (une fiche par entreprise : SIREN,
Wikipedia, presse).

### Choix techniques

- **Remplacement de l'URL SIRENE du sujet** :
  `api.annuaire-entreprises.data.gouv.fr` ne resout plus (DNS
  inexistant, verifie). Remplacee par l'API officielle actuelle
  `recherche-entreprises.api.gouv.fr`.
- **Filtre anti-homonyme** : une recherche brute avec un seul resultat
  remonte parfois une entite sans rapport (chercher "Mistral" remonte
  des ascenseurs, une biscuiterie et des campings-car avant "MISTRAL
  AI"). On filtre donc sur les candidats dont le nom contient tous les
  mots de la recherche, puis on retient celui avec le plus grand
  nombre d'etablissements parmi ces candidats (proxy pour "entite
  operationnelle principale").
- **Resolution du titre Wikipedia via l'API de recherche** (avec le
  mot "entreprise" ajoute a la requete) plutot que deviner l'URL :
  `fr.wikipedia.org/wiki/Amadeus` tombe sur une page d'homonymie
  (Amadeus est aussi un film et le second prenom de Mozart).
- **Filtre anti-bandeau** sur l'extraction de l'intro Wikipedia : sans
  lui, un bandeau d'avertissement ("Cet article ne s'appuie pas assez
  sur des sources...") remonte a la place du vrai texte d'introduction
  sur certaines pages.
- **Bing News RSS a la place de Google News RSS**, avec un garde-fou
  `robots_autorise()` qui verifie explicitement robots.txt (via
  Protego, la meme bibliotheque que Scrapy) avant chaque appel a une
  source de presse tierce. Verifie : `news.google.com/robots.txt`
  interdit `/rss/` pour tout user-agent, ce que `feedparser` ignore
  silencieusement puisqu'il ne consulte jamais robots.txt.

### Resultats reels obtenus

| Entreprise | SIREN retenu | Articles presse |
|---|---|---|
| Amadeus | 344496252 (Biot, Sophia Antipolis) | 10 |
| Capgemini | 328781786 (Capgemini France) | 10 |
| Mistral AI | 952418325 (Mistral AI, Paris) | 10 |

### Questions d'analyse

1. **Ai-je le droit ?** Oui, avec une correction en cours de route :
   l'API SIRENE et Wikipedia (licence CC BY-SA) sont prevues pour cet
   usage. Pour la presse, Google News RSS s'est revele interdit par
   son propre robots.txt - remplace par Bing News RSS, verifie
   autorise et dont les conditions d'utilisation permettent un usage
   personnel non commercial.
2. **Est-ce personnel ?** Essentiellement non : SIREN, adresse du
   siege, code NAF sont des donnees d'entreprise. L'infobox Wikipedia
   peut citer des dirigeants nommes, mais ce sont des donnees
   professionnelles deja rendues publiques par l'entreprise elle-meme.
3. **Suis-je discret ?** Oui. User-Agent identifiable, `time.sleep(1)`
   entre chaque source et chaque entreprise, verification explicite de
   robots.txt avant toute requete vers une source de presse tierce.

---

## TD 4.3 - Veille Scrapy (`veille/`)

```bash
cd veille
scrapy crawl rss_spider -L INFO
```

-> `mentions.csv` + `veille.db` (table `mentions`, `UNIQUE(url)`,
colonne `entreprise`).

### Choix techniques

- **`async def start()` au lieu de `start_requests()`** : Scrapy 2.17
  n'appelle plus la methode classique automatiquement (verifie : un
  `start_requests` classique tournait sans generer une seule requete,
  "Crawled 0 pages"). Depuis Scrapy 2.13, le point d'entree est devenu
  `async def start()`.
- **Bing News par entreprise en source principale**, flux generalistes
  (Le Monde, Figaro, BFMTV, 01net) gardes en complement. Verifie : ces
  5 flux generalistes ont un taux de detection quasi nul pour une
  entreprise precise (0 mention un jour ou l'entreprise faisait
  pourtant la une de la presse economique via une source dediee).
- **`CONCURRENT_REQUESTS_PER_DOMAIN=1`** : suffisant car chaque flux
  interroge un domaine different (bing.com, lemonde.fr, lefigaro.fr...),
  Scrapy parallelise deja entre domaines sans avoir besoin de
  paralleliser sur un meme domaine.

### Resultat reel obtenu

31 mentions collectees (9 Amadeus, 11 Capgemini, 11 Mistral AI) apres
calibration du scoring (voir Defi 1 plus bas - avant calibration,
seulement 3 articles avaient un score non neutre).

### Questions d'analyse

1. **Ai-je le droit ?** Oui, meme correction qu'au TD 4.2 : Bing News
   RSS a la place de Google News RSS pour rester conforme a
   robots.txt. `ROBOTSTXT_OBEY = True` reste actif sur l'ensemble du
   spider.
2. **Est-ce personnel ?** Non. Seuls des titres, resumes et liens
   d'articles deja publics sont extraits.
3. **Suis-je discret ?** Oui. `DOWNLOAD_DELAY = 1.0` +
   `RANDOMIZE_DOWNLOAD_DELAY`, User-Agent identifiable dediee.

---

## Defis

### Defi 1 - Calibrer le scoring de sentiment

**Constat initial** : sur les 32 premiers articles reels collectes,
seulement 3 avaient un score non neutre (tous positifs), et les 3 ne
matchaient que par coincidence sur deux mots qui s'ecrivent pareil en
francais et en anglais ("acquisition", "expansion"). Aucun des 16
autres mots des listes `MOTS_NEGATIFS`/`MOTS_POSITIFS` (en francais)
n'a jamais matche quoi que ce soit. Cause : Amadeus, Capgemini et
Mistral AI sont couvertes presque exclusivement par la presse
anglophone via Bing News, pas francophone - un lexique uniquement
francais est donc structurellement mal adapte au contenu reellement
recupere.

**Lecture des articles reels et faux positifs notes** :
- "Amadeus picks up £1.2B loan to fund Idemia PS acquisition" (score
  2) : matche sur "acquisition", mais c'est une nouvelle plutot neutre
  (un emprunt pour financer un rachat n'est pas en soi une bonne
  nouvelle) - faux positif.
- "Amadeus beats profit forecasts, trims 2026 revenue outlook" (score
  2 apres calibration) : signal mixte (bat les previsions de profit,
  mais revoit les perspectives a la baisse) - matche sur "beats", a
  moitie vrai positif.
- "Amadeus IT Group: The Valuation Is Now Too Cheap To Ignore",
  "Amadeus profit jumps...", "Capgemini raises FY revenue target...",
  "Microsoft to fund Mistral's European AI expansion..." : vrais
  positifs clairs.
- "Capgemini to sell the biz that works for US government amid
  criticism of ICE contract" : article clairement a connotation
  negative (contrat controverse), passait en neutre avant calibration
  faute de mot-cle correspondant - repris au Defi 3 ci-dessous.

**Mots ajoutes** (voir `rss_spider.py`) :
- `MOTS_NEGATIFS` += "decline", "lowers", "criticism"
- `MOTS_POSITIFS` += "beats", "raises", "jumps"

**Mesure avant/apres** :

| | Avant calibration | Apres calibration |
|---|---|---|
| Articles score != 0 | 3 / 32 (9%) | 10 / 31 (32%) |
| Score = 2 (positif) | 3 | 7 |
| Score = 1 (negatif) | 0 | 3 |

**Precision estimee apres relecture manuelle** : sur les 7 articles
positifs, 5 a 6 sont de vrais positifs selon la lecture (1 cas mixte
discutable) ; sur les 3 articles negatifs, les 3 sont de vrais
negatifs. La precision s'ameliore nettement, mais reste un correctif
partiel : un lexique bilingue ou une detection de langue serait
necessaire pour une couverture reellement fiable sur ces 3 cibles,
puisque la quasi-totalite de leur couverture presse est anglophone.
Ajouter 3 mots par liste, comme demande, ne resout donc que
partiellement le probleme de fond.

### Defi 2 - OSINT sur un domaine personnel (ecole-ipssi.com)

```bash
python td41_domaine.py ecole-ipssi.com
```

Domaine reellement teste : `ecole-ipssi.com` (le vrai domaine de
l'ecole - `ipssi.fr` teste initialement par erreur s'est revele avoir
un probleme de certificat SSL et n'etre pas le bon domaine).

**Ce qui surprend dans le rapport** :
- Le serveur est identifie via l'en-tete HTTP : `o2switch-PowerBoost-v3`,
  qui revele l'hebergeur (o2switch, un hebergeur francais) et sa
  technologie de cache maison. Cette information est utile pour un
  attaquant : elle permet de cibler des vulnerabilites connues de cet
  hebergeur specifique plutot que de chercher a l'aveugle.
- Ni CSP ni HSTS ne sont presents (verifie via GET) - le site n'a
  aucune des deux protections de securite web de base.
- Un seul sous-domaine trouve via crt.sh (le domaine nu lui-meme,
  aucun `www.` ni sous-domaine additionnel avec certificat) - contraste
  net avec Inria et l'Universite de Montpellier (200 chacun), qui sont
  des infrastructures bien plus grandes.
- WHOIS confirme un hebergement chez IONOS, cree en 2014, en France.
- robots.txt revele un site WordPress avec le plugin de securite
  SecuPress installe (`/secupress-XXXXXXXX/`), et le bloc Yoast SEO
  standard.

**Paragraphe "Ce qu'un auditeur externe apprendrait en 5 minutes"** :
En 5 minutes d'OSINT passif sur `ecole-ipssi.com`, un auditeur externe
apprendrait que le site est un WordPress heberge chez o2switch (un
hebergeur mutualise francais grand public, pas une infrastructure
dediee), sans CSP ni HSTS actives, avec un seul sous-domaine visible
via Certificate Transparency - ce qui suggere une infrastructure
simple, sans environnement de pre-production ou de test expose
publiquement (contrairement a l'Universite de Montpellier, ou
plusieurs sous-domaines de ce type ont ete trouves). Le principal
risque identifiable n'est donc pas une fuite de perimetre technique,
mais l'absence des en-tetes de securite web de base, qui protegeraient
contre certaines attaques cote navigateur (injection de contenu,
detournement de clics).

### Defi 3 - Croiser veille et historique Wikipedia

**Article choisi** (score_alerte = 1) : "Capgemini to sell the biz
that works for US government amid criticism of ICE contract", publie
le 1er fevrier 2026 (verifie via `date_publi` dans `veille.db`).

**Historique Wikipedia verifie** (page francaise "Capgemini", via
l'API MediaWiki) : une modification a ete faite le jour meme de
l'article, le 1er fevrier 2026 a 09h42 par l'utilisateur Alexfouch,
avec le commentaire *"ajout d'une info suite a la vente filiale
concernee par ICE"*. Le diff montre l'ajout d'un paragraphe precisant
que Capgemini fournit des services informatiques a l'ICE
(*Immigration and Customs Enforcement*) americain depuis 2010, et
qu'un nouveau contrat signe en novembre 2025 fait l'objet de
controverses sur une clause financiere liee au nombre de personnes
localisees. D'autres modifications suivent les jours suivants (2 et 6
fevrier 2026) qui etoffent et corrigent ce meme paragraphe, dans une
sous-section intitulee "Collaboration avec l'ICE de l'administration
Trump".

**Conclusion - Wikipedia est-il fiable pour la veille temps reel ?**
Dans ce cas precis, oui dans une certaine mesure : la mise a jour de
la page francaise est intervenue le jour meme de la publication de
l'article source, ce qui est rapide. Mais Wikipedia reste une source
secondaire qui depend de contributeurs benevoles individuels
(l'historique montre des allers-retours, une reversion de
modification, et des corrections successives sur plusieurs jours) :
l'information y est utile pour confirmer qu'un evenement a eu un echo
et pour retracer sa reception publique, mais elle arrive apres coup et
reste soumise a la neutralite de point de vue exigee par Wikipedia -
elle ne remplace pas la source de presse primaire pour une veille en
temps reel.
