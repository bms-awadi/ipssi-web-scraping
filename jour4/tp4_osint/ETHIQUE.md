# Ethique - TP4 OSINT

Les 3 reponses (droit, personnel, discret) pour chaque TD sont
detaillees et argumentees dans `README.md`, directement sous la
section de chaque TD. Ce fichier en reprend la synthese, comme exige
par le sujet.

## TD 4.1 - Empreinte technique (Inria, Universite de Montpellier)

1. **Ai-je le droit ?** Oui. WHOIS et crt.sh sont des registres publics
   dont la consultation est le service prevu.
2. **Est-ce personnel ?** Non. Donnees techniques uniquement.
3. **Suis-je discret ?** Oui. User-Agent identifiable, `sleep(1)`
   entre chaque cible, robots.txt consulte.

## TD 4.2 - Cartographie (Amadeus, Capgemini, Mistral AI)

1. **Ai-je le droit ?** Oui, avec une correction : Google News RSS
   s'est revele interdit par son propre robots.txt, remplace par Bing
   News RSS, verifie autorise.
2. **Est-ce personnel ?** Essentiellement non : donnees d'entreprise
   (SIREN, adresse, code NAF), pas de collecte de donnees personnelles.
3. **Suis-je discret ?** Oui. User-Agent identifiable, `sleep(1)`
   entre chaque source.

## TD 4.3 - Veille Scrapy (Amadeus, Capgemini, Mistral AI)

1. **Ai-je le droit ?** Oui, meme correction qu'au TD 4.2 (Bing News
   a la place de Google News). `ROBOTSTXT_OBEY = True` actif.
2. **Est-ce personnel ?** Non. Titres, resumes et liens d'articles
   deja publics uniquement.
3. **Suis-je discret ?** Oui. `DOWNLOAD_DELAY = 1.0` +
   `RANDOMIZE_DOWNLOAD_DELAY`, User-Agent identifiable dediee.

## Defi 2 - domaine personnel (ecole-ipssi.com)

1. **Ai-je le droit ?** Oui, meme cadre que le TD 4.1 : registres
   publics uniquement, aucune authentification.
2. **Est-ce personnel ?** Non. En-tetes HTTP, WHOIS, sous-domaines -
   aucune donnee sur une personne physique.
3. **Suis-je discret ?** Oui. Meme script que le TD 4.1, memes
   garanties (User-Agent, delai).
