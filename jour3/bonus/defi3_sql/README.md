# Défi 3 - SQL et interprétation financière

## Découverte préalable : `bourse.db` ne contient QUE des hausses

En tentant d'enrichir `bourse.db` avec le filtre "Baisses" du site
(`?france_filter[variation]=50002`, visible dans le formulaire HTML de la
page palmarès), le crawl échoue **volontairement** :

```
2026-07-29 16:24:09 [scrapy.downloadermiddlewares.robotstxt] DEBUG: Forbidden by robots.txt:
<GET https://www.boursorama.com/bourse/actions/palmares/france/?france_filter%5Bvariation%5D=50002>
```

`robots.txt` de Boursorama contient explicitement :
```
Disallow: /*filter[variation]=*
Disallow: /*filter%5Bvariation%5D=*
```

Avec `ROBOTSTXT_OBEY = True` (imposé par la checklist du TP), Scrapy bloque
cette requête tout seul - **on ne contourne pas cette règle**. Le spider
`cac` reste donc sur la page par défaut, qui ne montre que les hausses.
Conséquence directe sur l'analyse SQL ci-dessous : la requête "5 plus
grandes baisses" renvoie en réalité **les 5 plus faibles hausses**, pas de
vraies baisses (toutes les variations en base sont positives). C'est
documenté ici plutôt que masqué.

## Requêtes exécutées (voir [`queries.sql`](queries.sql))

**Top 5 "hausses"** (les vraies, en tête du palmarès) :

| libellé | variation (%) | cours |
|---|---|---|
| ALTEN | 19.31 | 79.70 |
| SOPRA STERIA | 15.27 | 198.50 |
| KERING | 13.81 | 285.10 |
| BUREAU VERITAS | 8.09 | 29.53 |
| ATOS GROUP | 6.45 | 33.98 |

**5 plus faibles hausses** (pas des baisses, cf. limitation ci-dessus) :

| libellé | variation (%) | cours |
|---|---|---|
| DBV TECHNOLOGIES | 1.85 | 2.416 |
| VIVENDI | 2.07 | 2.026 |
| EMEIS | 2.28 | 13.91 |
| IPSOS | 2.29 | 42.86 |
| EDENRED | 2.31 | 28.83 |

**Volume anormalement élevé (> 2x la moyenne du jour)** :

| libellé | volume | cours |
|---|---|---|
| STELLANTIS | 4 344 752 | 5.304 |
| TOTALENERGIES | 1 606 328 | 75.81 |
| BUREAU VERITAS | 1 386 867 | 29.53 |

Export complet : [`analyse_bourse.csv`](analyse_bourse.csv).

## Confrontation avec l'actualité réelle (2 cas documentés)

### Cas 1 - ALTEN (+19,3% scrapé)

Recherche web : *"Alten grimpe en Bourse, porté par une croissance
supérieure aux attentes et des notes d'analystes"* (ABC Bourse) - l'action
a bondi d'environ **20%** le 29 juillet 2026, la plus forte hausse du SBF
120, après un relèvement des objectifs annuels porté par une croissance
organique meilleure qu'attendu (aéronautique, défense, ferroviaire). Les
résultats semestriels complets doivent être publiés le 25 septembre - ce
mouvement anticipe donc la publication officielle sur la base d'un
pré-communiqué/note d'analystes.

**Écart scrapé (19,31%) vs presse (~20%) : cohérent**, l'écart de 0,7 pt
s'explique par l'heure exacte du scrape (cours qui bouge en continu) vs
l'heure de l'article.

Source : [Alten grimpe en Bourse, porté par une croissance supérieure aux attentes et des notes d'analystes](https://www.abcbourse.com/marches/alten-grimpe-en-bourse-porte-par-une-croissance-superieure-aux-attentes-et-des_700564)

### Cas 2 - SOPRA STERIA (+15,3% scrapé)

Recherche web : *"Sopra Steria bondit en Bourse après avoir relevé sa
prévision de croissance pour 2026"* (ABC Bourse / Zonebourse) - l'action a
grimpé de **14,9%** vers 10h40, après un relèvement de la prévision de
croissance organique 2026 (de 1-2% à 2-2,5%), porté par un CA S1 2026 de
2,96 Md€ (+4,1% en publié, +3% organique) et une accélération au T2
(+5,3% organique vs +4,4% au T1). Le contexte sectoriel joue aussi : le
secteur IT avait été récemment fragilisé par des avertissements
d'entreprises américaines, ce qui accentue le soulagement des
investisseurs sur cette publication.

**Écart scrapé (15,27%) vs presse (14,9%) : cohérent**, même explication
(cours en mouvement continu entre l'article et le scrape).

Source : [Sopra Steria bondit en Bourse après avoir relevé sa prévision de croissance pour 2026](https://www.abcbourse.com/marches/sopra-steria-bondit-en-bourse-apres-avoir-releve-sa-prevision-de-croissance-pour_700560)

## Conclusion

Les deux plus fortes hausses du palmarès scrapé correspondent chacune à une
annonce de résultats/prévisions **publiée le jour même**, avec des
pourcentages de variation cohérents à 1 point près entre la donnée scrapée
et la presse financière - bon signal de fiabilité pour `bourse.db`. Le vrai
angle mort de cette base n'est pas la qualité de l'extraction, mais son
**périmètre** : sans les vraies baisses (bloquées par `robots.txt`), toute
analyse "gagnants vs perdants" serait biaisée si on ne documentait pas
cette limite.
