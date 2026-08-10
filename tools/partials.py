#!/usr/bin/env python3
"""
Eén bron van waarheid voor de blokken die op élke pagina staan: de header, de
footer, de GTM-snippet en het consent-blok. Die staan in tools/partials/ en dit
script zet ze in alle HTML-bestanden van de site.

Waarom zo en niet met JavaScript: de blokken blijven gewoon in de HTML staan,
dus een zoekmachine ziet de navigatie en de footer zonder JavaScript uit te
voeren. De prijs is dat je dit script moet draaien na een wijziging.

Draaien vanuit de repo-root:  python3 tools/partials.py .

De eerste keer herkent het script de blokken aan hun begin- en eindtag en zet
er markers omheen. Daarna werkt het op die markers. Idempotent: twee keer
draaien verandert niets extra.
"""
import os, re, sys, glob

WORTEL = sys.argv[1] if len(sys.argv) > 1 else '.'
PARTIALS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'partials')

# naam, beginpatroon, eindpatroon — in de volgorde waarin ze in de pagina staan
BLOKKEN = [
    ('consent',
     r'<!-- Google Consent Mode v2',
     r'<script src="/js/funpoints-consent\.js"></script>'),
    ('head-gtm',
     r'<!-- Google Tag Manager -->',
     r'<!-- End Google Tag Manager -->'),
    ('body-gtm',
     r'<!-- Google Tag Manager \(noscript\) -->',
     r'<!-- End Google Tag Manager \(noscript\) -->'),
    ('header', r'<header class="site-header">', r'</header>'),
    ('footer', r'<footer class="footer">', r'</footer>'),
]

BESTAND = {'consent': 'head-consent.html', 'head-gtm': 'head-gtm.html',
           'body-gtm': 'body-gtm.html', 'header': 'header.html',
           'footer': 'footer.html'}


def laad(naam):
    with open(os.path.join(PARTIALS, BESTAND[naam]), encoding='utf-8') as f:
        return f.read().rstrip('\n')


def vervang(tekst, naam, inhoud):
    """Zet het blok tussen markers. Werkt zowel op markers als op de ruwe tags."""
    start_marker = f'<!-- fp:{naam} -->'
    eind_marker = f'<!-- /fp:{naam} -->'
    nieuw = f'{start_marker}\n{inhoud}\n{eind_marker}'

    # Al voorzien van markers? Dan alleen de inhoud verversen.
    patroon = re.compile(re.escape(start_marker) + r'.*?' + re.escape(eind_marker), re.S)
    if patroon.search(tekst):
        return patroon.sub(lambda m: nieuw, tekst, count=1), True

    # Eerste keer: het blok opzoeken aan zijn begin- en eindtag.
    _, begin, eind = next(b for b in BLOKKEN if b[0] == naam)
    m = re.search(begin + r'.*?' + eind, tekst, re.S)
    if not m:
        return tekst, False
    return tekst[:m.start()] + nieuw + tekst[m.end():], True


def verwerk(pad, inhouden):
    s = open(pad, encoding='utf-8').read()
    origineel = s
    ontbreekt = []
    for naam, _, _ in BLOKKEN:
        s, ok = vervang(s, naam, inhouden[naam])
        if not ok:
            ontbreekt.append(naam)
    if s != origineel:
        open(pad, 'w', encoding='utf-8').write(s)
    return ('aangepast' if s != origineel else 'ongewijzigd'), ontbreekt


if __name__ == '__main__':
    inhouden = {naam: laad(naam) for naam, _, _ in BLOKKEN}
    bestanden = [p for p in glob.glob(os.path.join(WORTEL, '**/*.html'), recursive=True)
                 if not os.path.basename(os.path.dirname(p)).startswith('_')]
    telling = {}
    problemen = []
    for p in sorted(bestanden):
        r, ontbreekt = verwerk(p, inhouden)
        telling[r] = telling.get(r, 0) + 1
        if ontbreekt:
            problemen.append((os.path.relpath(p, WORTEL), ontbreekt))
    for k, v in sorted(telling.items()):
        print(f'{k}: {v}')
    if problemen:
        print('\nBlokken niet gevonden (nakijken):')
        for pad, blokken in problemen[:20]:
            print(f'  {pad}: {", ".join(blokken)}')
        print(f'  totaal: {len(problemen)}')
