#!/usr/bin/env python3
"""Zet de SEO-paginaspec (markdown) om in kermissen.json — de bron voor de generator."""
import re, json, csv, unicodedata, sys
from collections import OrderedDict

SPEC = 'spec.md'
CSV_IN = 'kermissen.csv'
OUT = 'kermissen.json'

MAANDEN = ['januari','februari','maart','april','mei','juni','juli',
           'augustus','september','oktober','november','december']


def parse_nl_date(txt, jaar=2026):
    """'15 augustus' -> (2026, 8, 15)"""
    m = re.match(r'\s*(\d{1,2})\s+([a-z]+)', txt.strip(), re.I)
    if not m:
        return None
    d = int(m.group(1))
    maand = m.group(2).lower()
    if maand not in MAANDEN:
        return None
    return (jaar, MAANDEN.index(maand) + 1, d)


def main():
    spec = open(SPEC, encoding='utf-8').read()

    # --- CSV als feitelijke bron voor de datums -----------------------------
    csv_rows = {}
    with open(CSV_IN, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            csv_rows.setdefault((r['Gemeente'], r['Naam']), []).append(r)

    lines = spec.split('\n')
    provincie = None
    gemeente = None
    gemeente_slug = None
    postcode = None
    paginas = []
    huidig = None

    re_prov = re.compile(r'^### PROVINCIE (.+?) — (\d+) kermissen in (\d+) gemeenten')
    re_gem = re.compile(r'^#### (.+?) \((\d{4})\) — gemeentepagina `(/kermis/[^`]+)`')
    re_page = re.compile(r'^\*\*(.+?)\*\* · `(/kermis/[^`]+)`(.*)$')
    re_veld = re.compile(r'^- (Title|Description|H1|Antwoordzin|Keywords|Uniek \(uit data\)|Interne links)'
                         r'(?:\s*\(\d+\))?:\s*(.*)$')

    for ln in lines:
        m = re_prov.match(ln)
        if m:
            provincie = m.group(1).title().replace('Oost-Vlaanderen', 'Oost-Vlaanderen')
            continue
        m = re_gem.match(ln)
        if m:
            gemeente, postcode, gpad = m.group(1), m.group(2), m.group(3)
            gemeente_slug = gpad.rsplit('/', 1)[-1]
            continue
        m = re_page.match(ln)
        if m:
            naam, pad, staart = m.group(1), m.group(2), m.group(3)
            slug = pad.rsplit('/', 1)[-1]
            huidig = OrderedDict(
                naam=naam, pad=pad, slug=slug,
                gemeente=gemeente, gemeente_slug=gemeente_slug,
                postcode=postcode, provincie=provincie,
                noindex='noindex' in staart,
                uniek=[], links=[],
            )
            paginas.append(huidig)
            continue
        m = re_veld.match(ln)
        if m and huidig is not None:
            veld, waarde = m.group(1), m.group(2).strip()
            waarde = waarde.strip('`')
            if veld == 'Title':
                huidig['title'] = waarde
            elif veld == 'Description':
                huidig['description'] = waarde
            elif veld == 'H1':
                huidig['h1'] = waarde
            elif veld == 'Antwoordzin':
                huidig['antwoord'] = waarde.strip('"')
            elif veld == 'Keywords':
                huidig['keywords'] = [k.strip() for k in waarde.split('·') if k.strip()]
            elif veld.startswith('Uniek'):
                huidig['uniek'].append(waarde)
            elif veld == 'Interne links':
                for lm in re.finditer(r'\[([^\]]+)\]\((/kermis/[^)]+)\)', waarde):
                    label, href = lm.group(1), lm.group(2)
                    if label == 'gemeente':
                        continue
                    # Een link is 'zelfde gemeente' als het pad onder deze gemeente valt;
                    # de tekstmarkering "zelfde gemeente →" is daarvoor te onbetrouwbaar.
                    soort = ('zelfde-gemeente'
                             if href.startswith(f'/kermis/{gemeente_slug}/') else 'buurt')
                    huidig['links'].append({'label': label, 'href': href, 'soort': soort})

    # --- datums uit de H1 + CSV kruisen ------------------------------------
    zonder = 0
    for p in paginas:
        m = re.search(r'— (.+?) tot (.+)$', p['h1'])
        start = parse_nl_date(m.group(1)) if m else None
        eind = parse_nl_date(m.group(2)) if m else None
        # CSV is leidend waar beschikbaar
        rows = csv_rows.get((p['gemeente'], p['naam']), [])
        gekozen = None
        if len(rows) == 1:
            gekozen = rows[0]
        elif rows and start:
            iso = '%04d-%02d-%02d' % start
            for r in rows:
                if r['Startdatum'] == iso:
                    gekozen = r
                    break
        if gekozen:
            p['start'] = gekozen['Startdatum']
            p['eind'] = gekozen['Einddatum']
            p['postcode'] = gekozen['Postcode'] or p['postcode']
        elif start and eind:
            p['start'] = '%04d-%02d-%02d' % start
            p['eind'] = '%04d-%02d-%02d' % eind
        else:
            zonder += 1
            p['start'] = p['eind'] = None

    print(f'pagina\'s: {len(paginas)}  zonder datum: {zonder}  '
          f'noindex: {sum(1 for p in paginas if p["noindex"])}')

    # --- gemeenten en provincies afleiden ----------------------------------
    gemeenten = OrderedDict()
    for p in paginas:
        g = gemeenten.setdefault(p['gemeente_slug'], {
            'naam': p['gemeente'], 'slug': p['gemeente_slug'],
            'postcode': p['postcode'], 'provincie': p['provincie'], 'kermissen': []})
        g['kermissen'].append(p['slug'])

    provincies = OrderedDict()
    for p in paginas:
        pr = provincies.setdefault(p['provincie'], {
            'naam': p['provincie'], 'gemeenten': set(), 'aantal': 0})
        pr['gemeenten'].add(p['gemeente_slug'])
        pr['aantal'] += 1
    for pr in provincies.values():
        pr['gemeenten'] = sorted(pr['gemeenten'])

    json.dump({'paginas': paginas,
               'gemeenten': gemeenten,
               'provincies': provincies},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'gemeenten: {len(gemeenten)}  provincies: {len(provincies)}  → {OUT}')


if __name__ == '__main__':
    main()
