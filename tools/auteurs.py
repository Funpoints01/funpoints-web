#!/usr/bin/env python3
"""
Koppelt de auteur van de artikels aan één entiteit.

De artikels hadden wel een `author`, maar als los Organization-object dat op elke
pagina opnieuw beschreven werd en nergens naar verwees. Daardoor zag een
zoekmachine dertien losse auteurs in plaats van één redactie. Dit script maakt
er één entiteit van — `#redactie`, "Het Funpoints-team", met /over-ons.html als
adres — precies wat er ook zichtbaar onder elk artikel staat.

Draaien vanuit de repo-root:  python3 tools/auteurs.py .
"""
import glob, json, os, re, sys

WORTEL = sys.argv[1] if len(sys.argv) > 1 else '.'
BASIS = 'https://funpoints.be'

REDACTIE = {
    "@type": "Organization",
    "@id": f"{BASIS}/#redactie",
    "name": "Het Funpoints-team",
    "url": f"{BASIS}/over-ons.html",
    "description": "De redactie van Funpoints: drie ondernemers die samen met de "
                   "foor schrijven over de kermis en over digitaal sparen.",
    "parentOrganization": {"@id": f"{BASIS}/#organization"},
}


def verwerk(pad):
    s = open(pad, encoding='utf-8').read()
    m = re.search(r'<script type="application/ld\+json">\n?(.*?)\n?</script>', s, re.S)
    if not m:
        return 'geen JSON-LD'
    d = json.loads(m.group(1))
    graaf = d.get('@graph')
    if not graaf:
        return 'geen @graph'

    artikels = [x for x in graaf if x.get('@type') == 'Article']
    if not artikels:
        return 'geen Article'

    for a in artikels:
        a['author'] = {"@id": f"{BASIS}/#redactie"}
        a.setdefault('publisher', {"@id": f"{BASIS}/#organization"})

    if not any(x.get('@id') == f'{BASIS}/#redactie' for x in graaf):
        # net na het artikel, zodat de graaf leesbaar blijft
        graaf.insert(graaf.index(artikels[-1]) + 1, REDACTIE)

    nieuw = ('<script type="application/ld+json">\n'
             + json.dumps({"@context": "https://schema.org", "@graph": graaf},
                          ensure_ascii=False, indent=2) + '\n</script>')
    s = s[:m.start()] + nieuw + s[m.end():]
    open(pad, 'w', encoding='utf-8').write(s)
    return 'aangepast'


if __name__ == '__main__':
    paden = sorted(glob.glob(os.path.join(WORTEL, 'kennisbank/*/index.html'))
                   + glob.glob(os.path.join(WORTEL, 'magazine/*/index.html')))
    for p in paden:
        print(f'{verwerk(p):12} {os.path.relpath(p, WORTEL)}')
