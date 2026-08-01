import json
import socket
import sys
import time

import requests
import whois

CIBLES_TD41 = [
    {"nom": "Inria", "domaine": "inria.fr"},
    {"nom": "Universite de Montpellier", "domaine": "umontpellier.fr"},
]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEADERS = {"User-Agent": "IPSSI-OSINT (+cours@ipssi.fr)"}


def analyse_whois(domaine: str) -> dict:
    try:
        w = whois.whois(domaine)
        return {
            "registrar": str(w.registrar or "n/a"),
            "creation_date": str(w.creation_date or "n/a")[:10],
            "expiration_date": str(w.expiration_date or "n/a")[:10],
            "name_servers": sorted(set(w.name_servers or [])),
            "country": str(w.country or "n/a"),
        }
    except Exception as e:
        return {"erreur": str(e)}


def analyse_headers(domaine: str) -> dict:
    try:
        r = requests.get(
            f"https://{domaine}", headers=HEADERS, timeout=10, allow_redirects=True
        )
        h = r.headers
        return {
            "status": r.status_code,
            "server": h.get("Server", "n/a"),
            "x_powered_by": h.get("X-Powered-By", "n/a"),
            "x_frame_options": h.get("X-Frame-Options", "n/a"),
            "csp_present": "Content-Security-Policy" in h,
            "hsts_present": "Strict-Transport-Security" in h,
        }
    except Exception as e:
        return {"erreur": str(e)}


def sous_domaines_crtsh(
    domaine: str, tentatives: int = 3, limite: int = 200
) -> list[str]:
    url = f"https://crt.sh/?q=%.{domaine}&output=json"
    derniere_erreur = None
    for tentative in range(tentatives):
        try:
            r = requests.get(url, headers=HEADERS, timeout=40)
            if r.status_code != 200:
                derniere_erreur = f"HTTP {r.status_code}"
                time.sleep(3 * (tentative + 1))
                continue
            data = r.json()
            subs = set()
            for entry in data:
                for nom in entry["name_value"].split("\n"):
                    nom = nom.strip()
                    if nom and "*" not in nom and nom.endswith(domaine):
                        subs.add(nom)
            return sorted(subs)[:limite]
        except Exception as e:
            derniere_erreur = str(e)
            time.sleep(3 * (tentative + 1))
    return [f"ERREUR apres {tentatives} tentatives: {derniere_erreur}"]


def analyse_robots(domaine: str) -> str:
    try:
        r = requests.get(f"https://{domaine}/robots.txt", headers=HEADERS, timeout=10)
        return r.text[:1000] if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as e:
        return str(e)


def analyser_domaine(domaine: str) -> dict:
    print(f"[*] Analyse de {domaine}...")
    rapport = {
        "domaine": domaine,
        "ip": socket.gethostbyname(domaine) if domaine else "n/a",
        "whois": analyse_whois(domaine),
        "headers_http": analyse_headers(domaine),
        "sous_domaines": sous_domaines_crtsh(domaine),
        "robots_txt": analyse_robots(domaine),
    }
    rapport["nb_sous_domaines"] = len(rapport["sous_domaines"])
    return rapport


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Usage Defi 2 : un seul domaine passe en argument.
        domaine = sys.argv[1]
        rapport = analyser_domaine(domaine)
        sortie = f"rapport_{domaine.split('.')[0]}.json"
        with open(sortie, "w", encoding="utf-8") as f:
            json.dump(rapport, f, indent=2, ensure_ascii=False)
        print(f"[+] Rapport sauvegarde : {sortie}")
    else:
        rapports = {}
        for cible in CIBLES_TD41:
            time.sleep(1)  # politesse
            rapports[cible["nom"]] = analyser_domaine(cible["domaine"])

        with open("rapport_domaines.json", "w", encoding="utf-8") as f:
            json.dump(rapports, f, indent=2, ensure_ascii=False)

        print("[+] Rapport sauvegarde : rapport_domaines.json")
        for nom, r in rapports.items():
            print(
                f"    {nom} : {r['nb_sous_domaines']} sous-domaines, "
                f"serveur {r['headers_http'].get('server', 'n/a')}, "
                f"CSP={r['headers_http'].get('csp_present')}, "
                f"HSTS={r['headers_http'].get('hsts_present')}"
            )
