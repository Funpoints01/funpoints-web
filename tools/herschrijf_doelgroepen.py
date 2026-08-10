#!/usr/bin/env python3
"""
Brengt de site terug naar twee doelgroepen: bezoekers en uitbaters.

Wat dit doet:
  - Vervangt 'foorkramer' in de doelgroep- en productpagina's. In publieksteksten
    wordt dat 'het kraam' of 'de uitbater', in zakelijke teksten 'medewerker'.
  - Laat het woord staan in de magazine- en kennisbankartikels: daar is het
    gewoon het juiste Nederlandse woord voor het beroep.
  - Verwijst /foorkramers.html door naar /uitbaters.html.

Draaien vanuit de repo-root:  python3 tools/herschrijf_doelgroepen.py .
"""
import os, re, sys

WORTEL = sys.argv[1] if len(sys.argv) > 1 else '.'

# Per bestand: (zoek, vervang). Bewust letterlijk en niet met een algemene
# regex — 'foorkramer' betekent niet overal hetzelfde.
VERVANGINGEN = {
    'index.html': [
        ("bezoekers sparen punten bij elk kraam, foorkramers scannen met hun telefoon — zonder kassa",
         "bezoekers sparen punten bij elk kraam, uitbaters scannen met hun telefoon — zonder kassa"),
        ("bezoekers sparen punten per kraam, foorkramers scannen met hun telefoon, uitbaters beheren acties en bereik",
         "bezoekers sparen punten per kraam en uitbaters beheren hun kramen, acties en bereik"),
        ("Simpel voor de bezoeker, slim voor de foorkramer.",
         "Simpel voor de bezoeker, slim voor de uitbater."),
        ("Toon je persoonlijke QR aan de foorkramer. Je punten worden meteen bijgeschreven.",
         "Toon je persoonlijke QR aan het kraam. Je punten worden meteen bijgeschreven."),
        ("Bezoekers sparen leuker, foorkramers werken sneller, en uitbaters bereiken hun klanten rechtstreeks.",
         "Bezoekers sparen leuker en uitbaters werken sneller én bereiken hun klanten rechtstreeks."),
    ],
    'bezoekers.html': [
        ("De foorkramer scant hem met zijn telefoon en je punten worden meteen bijgeschreven bij dat kraam.",
         "Ze scannen hem met een gewone telefoon en je punten worden meteen bijgeschreven bij dat kraam."),
        ("Toon 'm aan elk kraam — de foorkramer scant hem en je punten worden automatisch bij dàt kraam bijgeschreven",
         "Toon 'm aan elk kraam — ze scannen hem en je punten worden automatisch bij dàt kraam bijgeschreven"),
        ("Toon je persoonlijke QR aan de foorkramer bij elk kraam. Klaar.",
         "Toon je persoonlijke QR aan het kraam. Klaar."),
    ],
    'uitbaters.html': [
        ('Maak <a href="/foorkramers.html">foorkramer-logins</a> in enkele klikken',
         'Maak <a href="#aan-het-kraam">logins voor je medewerkers</a> in enkele klikken'),
        ("de foorkramer scant de QR-code van de klant met een gewone smartphone en de punten staan meteen geboekt",
         "je medewerker scant de QR-code van de klant met een gewone smartphone en de punten staan meteen geboekt"),
    ],
    'hoe-het-werkt.html': [
        ("De foorkramer scant de QR-code van de klant met een gewone smartphone of tablet",
         "Je medewerker scant de QR-code van de klant met een gewone smartphone of tablet"),
        ("De foorkramer scant en de punten staan meteen geboekt bij dat kraam.",
         "Aan het kraam scannen ze hem en de punten staan meteen geboekt bij dat kraam."),
        ("<!-- Schermafbeelding: scanscherm van de foorkramer.",
         "<!-- Schermafbeelding: het scanscherm aan het kraam."),
        ("een eigen login aan voor elke foorkramer",
         "een eigen login aan voor elke medewerker"),
    ],
    'demo/index.html': [
        ("Je foorkramer scant de QR-code van de klant met een gewone smartphone of tablet",
         "Je medewerker scant de QR-code van de klant met een gewone smartphone of tablet"),
        ("🎡 Voor uitbaters en foorkramers", "🎡 Voor kermisuitbaters"),
        ("🤝 Samen met foorkramers gebouwd", "🤝 Samen met de foor gebouwd"),
        ("de logins van je foorkramers samen op", "de logins van je medewerkers samen op"),
    ],
    'over-ons.html': [
        ("Funpoints wordt gebouwd door drie ondernemers, samen met foorkramers en getest aan echte kramen",
         "Funpoints wordt gebouwd door drie ondernemers, samen met de foor en getest aan echte kramen"),
        ("maar afgetoetst met foorkramers: hoe scan je met vettige handen",
         "maar afgetoetst aan het kraam: hoe scan je met vettige handen"),
        ("Ben je uitbater of foorkramer en wil je Funpoints aan jouw kraam zien werken?",
         "Baat je een kraam of attractie uit en wil je Funpoints aan het werk zien?"),
    ],
    'kennisbank/index.html': [
        ('"name": "Kennisbank voor foorkramers"', '"name": "Kennisbank voor kermisuitbaters"'),
        ('"description": "Praktische artikels voor foorkramers en kermisuitbaters."',
         '"description": "Praktische artikels voor kermisuitbaters en hun medewerkers."'),
        ("📚 Geschreven met foorkramers", "📚 Geschreven met de foor"),
        ("Kennisbank voor Foorkramers | Funpoints", "Kennisbank voor Kermisuitbaters | Funpoints"),
    ],
}

# Losse links die nog naar de oude doelgroeppagina wijzen.
LINKS = [
    ('<a href="/foorkramers.html">', '<a href="/uitbaters.html#aan-het-kraam">'),
]


def verwerk(pad, paren):
    s = open(pad, encoding='utf-8').read()
    origineel = s
    gemist = []
    for zoek, vervang in paren:
        if zoek not in s:
            if vervang not in s:          # al vervangen is geen probleem
                gemist.append(zoek[:60])
            continue
        s = s.replace(zoek, vervang)
    if s != origineel:
        open(pad, 'w', encoding='utf-8').write(s)
    return s != origineel, gemist


if __name__ == '__main__':
    import glob
    for naam, paren in VERVANGINGEN.items():
        pad = os.path.join(WORTEL, naam)
        if not os.path.exists(pad):
            print(f'ontbreekt: {naam}')
            continue
        gewijzigd, gemist = verwerk(pad, paren)
        print(f'{"aangepast" if gewijzigd else "ongewijzigd":12} {naam}')
        for g in gemist:
            print(f'   NIET GEVONDEN: {g}…')

    # Alle overige verwijzingen naar de oude doelgroeppagina.
    n = 0
    for pad in glob.glob(os.path.join(WORTEL, '**/*.html'), recursive=True):
        if pad.endswith('foorkramers.html'):
            continue
        s = open(pad, encoding='utf-8').read()
        o = s
        for zoek, vervang in LINKS:
            s = s.replace(zoek, vervang)
        if s != o:
            open(pad, 'w', encoding='utf-8').write(s)
            n += 1
    print(f'\nlinks bijgewerkt in {n} bestanden')
