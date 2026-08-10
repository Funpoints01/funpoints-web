#!/usr/bin/env python3
"""
Genereert de kermiskalender van funpoints.be uit kermissen.json.

Uitvoer (in de opgegeven doelmap, standaard de repo-root):
  /kermis/index.html                       nationale hub
  /kermis/provincie/<slug>/index.html      11 provinciepagina's
  /kermis/<gemeente>/index.html            574 gemeentepagina's
  /kermis/<gemeente>/<kermis>/index.html   633 kermispagina's
  /sitemap-kermis-<provincie>.xml          sitemap per provincie
  /sitemap-kermis.xml                      index van bovenstaande

Draaien:  python3 build_kermis.py [doelmap]
"""
import json, os, re, sys, html, unicodedata, datetime
from collections import defaultdict

# De gedeelde blokken staan één map hoger, in tools/partials/ — dezelfde bron
# als tools/partials.py gebruikt voor de handgeschreven pagina's.
PARTIALS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'partials'))


def partial(sleutel, naam):
    """De gedeelde blokken komen uit tools/partials/ — zelfde bron als de rest
    van de site, zodat header en footer nooit uit elkaar lopen. De markers
    eromheen laten tools/partials.py de blokken later terugvinden."""
    with open(os.path.join(PARTIALS, naam), encoding='utf-8') as f:
        return (f'<!-- fp:{sleutel} -->\n' + f.read().rstrip('\n')
                + f'\n<!-- /fp:{sleutel} -->')


CONSENT = partial('consent', 'head-consent.html')
GTM_HEAD = partial('head-gtm', 'head-gtm.html')
GTM_BODY = partial('body-gtm', 'body-gtm.html')
HEADER = partial('header', 'header.html')
FOOTER = partial('footer', 'footer.html')

BRON = 'kermissen.json'
DOEL = sys.argv[1] if len(sys.argv) > 1 else '.'
BASIS = 'https://funpoints.be'
JAAR = 2026
VANDAAG = datetime.date(2026, 8, 10)

MAANDEN = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
           'augustus', 'september', 'oktober', 'november', 'december']
DAGEN = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']

FEESTDAGEN = {
    '2026-01-01': 'Nieuwjaar', '2026-04-06': 'Paasmaandag',
    '2026-05-01': 'Dag van de Arbeid', '2026-05-14': 'O.-L.-H.-Hemelvaart',
    '2026-05-25': 'Pinkstermaandag', '2026-07-21': 'Nationale feestdag',
    '2026-08-15': 'O.-L.-V.-Hemelvaart', '2026-11-01': 'Allerheiligen',
    '2026-11-11': 'Wapenstilstand', '2026-12-25': 'Kerstmis',
}


# ----------------------------------------------------------------- hulpjes
def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def e(s):
    return html.escape(str(s), quote=True)


def datum(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d.day} {MAANDEN[d.month - 1]} {d.year}'


def datum_kort(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d.day} {MAANDEN[d.month - 1]}'


def dagnaam(iso):
    return DAGEN[datetime.date.fromisoformat(iso).weekday()]


def duur(start, eind):
    return (datetime.date.fromisoformat(eind) - datetime.date.fromisoformat(start)).days + 1


def status(start, eind, ref=VANDAAG):
    s = datetime.date.fromisoformat(start)
    t = datetime.date.fromisoformat(eind)
    if ref < s:
        return 'binnenkort'
    if ref > t:
        return 'voorbij'
    return 'open'


BADGE = {'binnenkort': '🗓️ Nog te komen', 'open': '🎡 Nu bezig', 'voorbij': '✔️ Voorbij'}


# ----------------------------------------------------------------- skelet
def kop(titel, beschrijving, canoniek, dl, extra_head='', jsonld=None, noindex=False):
    ld = ''
    if jsonld:
        ld = ('<script type="application/ld+json">'
              + json.dumps(jsonld, ensure_ascii=False, separators=(',', ':'))
              + '</script>\n')
    robots = '<meta name="robots" content="noindex,follow">\n' if noindex else ''
    dlj = json.dumps(dl, ensure_ascii=False, indent=2)
    consent, gtmhead, gtmbody, header = CONSENT, GTM_HEAD, GTM_BODY, HEADER
    bodyklasse = ''
    return f'''<!DOCTYPE html>
<html lang="nl-BE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{consent}
{gtmhead}
<title>{e(titel)}</title>
<meta name="description" content="{e(beschrijving)}">
{robots}<link rel="canonical" href="{canoniek}">
<link rel="alternate" hreflang="nl-BE" href="{canoniek}">
<link rel="alternate" hreflang="x-default" href="{canoniek}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canoniek}">
<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{e(beschrijving)}">
<meta property="og:locale" content="nl_BE">
<meta property="og:image" content="{BASIS}/img/funpoints-digitale-spaarkaart-kermis.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Funpoints — het digitale spaarkaartje van de kermis">
<meta property="og:site_name" content="Funpoints">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#10B981">
<link rel="icon" href="/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
{extra_head}{ld}</head>
<body{bodyklasse}>
{gtmbody}

<a class="skip-link" href="#main">Naar de inhoud</a>

{header}

<main id="main">
'''


def voet(sticky=''):
    return f'''</main>
{sticky}
{FOOTER}

<script src="/kermis/status.js" defer></script>
<script src="/tracking.js" defer></script>
</body>
</html>
'''


VOET = voet()

ORG = {
    "@type": "Organization",
    "@id": f"{BASIS}/#organization",
    "name": "Funpoints",
    "url": f"{BASIS}/",
    "logo": {"@type": "ImageObject", "url": f"{BASIS}/favicon.png",
             "width": 256, "height": 256},
    "email": "info@funpoints.be",
    "description": "Funpoints is het digitale spaarsysteem voor de kermis.",
    "areaServed": "BE",
}


def kruimels(paren):
    return {"@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": BASIS + u}
                for i, (n, u) in enumerate(paren)]}


def faq_ld(paren):
    return {"@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": v,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for v, a in paren]}


def faq_html(paren):
    out = ['<div class="container faq">']
    for v, a in paren:
        out.append(f'''      <details class="faq-item">
        <summary>{e(v)}</summary>
        <div class="faq-answer">
          <p>{a}</p>
        </div>
      </details>''')
    out.append('    </div>')
    return '\n'.join(out)


# ----------------------------------------------------------------- laden
data = json.load(open(BRON, encoding='utf-8'))
paginas = data['paginas']
gemeenten = data['gemeenten']
provincies = data['provincies']

per_pad = {p['pad']: p for p in paginas}
per_gemeente = defaultdict(list)
for p in paginas:
    per_gemeente[p['gemeente_slug']].append(p)
for lijst in per_gemeente.values():
    lijst.sort(key=lambda p: p['start'])

prov_slug = {naam: slugify(naam) for naam in provincies}
prov_van_gemeente = {g: gemeenten[g]['provincie'] for g in gemeenten}
per_provincie = defaultdict(list)
for p in paginas:
    per_provincie[p['provincie']].append(p)
for lijst in per_provincie.values():
    lijst.sort(key=lambda p: (p['start'], p['gemeente']))

geschreven = []


def schrijf(pad_rel, inhoud):
    vol = os.path.join(DOEL, pad_rel.lstrip('/'))
    os.makedirs(os.path.dirname(vol), exist_ok=True)
    with open(vol, 'w', encoding='utf-8') as f:
        f.write(inhoud)
    geschreven.append(pad_rel)


# ------------------------------------------------------- kermispagina
def bouw_kermis(p):
    g = gemeenten[p['gemeente_slug']]
    prov = p['provincie']
    ps = prov_slug[prov]
    url = BASIS + p['pad'] + '/'
    st = status(p['start'], p['eind'])
    n = duur(p['start'], p['eind'])
    feest = [naam for iso, naam in FEESTDAGEN.items()
             if p['start'] <= iso <= p['eind']]

    # ---- praktische tabel
    rijen = [
        ('Wanneer', f'{dagnaam(p["start"])} {datum(p["start"])} t.e.m. '
                    f'{dagnaam(p["eind"])} {datum(p["eind"])}'),
        ('Hoe lang', f'{n} {"dag" if n == 1 else "dagen"}'),
        ('Waar', f'{e(p["gemeente"])} ({e(p["postcode"])}), {e(prov)}'),
        ('Toegang', 'Gratis — je betaalt per attractie of per spel'),
        ('Openingsuren', 'Doordeweeks vanaf de namiddag, in het weekend vanaf de middag. '
                         'De exacte uren verschillen per kraam.'),
    ]
    if feest:
        rijen.insert(2, ('Feestdag', ' en '.join(feest) + ' valt in deze periode'))
    tabel = '\n'.join(
        f'          <tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rijen)

    # ---- lokale hoek
    uniek = '\n'.join(f'        <li>{e(u)}</li>' for u in p['uniek'])

    # ---- interne links
    zelfde = [l for l in p['links'] if l['soort'] == 'zelfde-gemeente']
    buurt = [l for l in p['links'] if l['soort'] == 'buurt']

    def kaartje(l, kicker):
        doel = per_pad.get(l['href'])
        omschrijving = ''
        if doel:
            omschrijving = (f'{datum_kort(doel["start"])} – {datum_kort(doel["eind"])} '
                            f'· {doel["gemeente"]}')
            titel = doel['naam']
        else:
            titel = l['label']
        return (f'        <a href="{l["href"]}/">\n'
                f'          <div class="k">{kicker}</div>\n'
                f'          <div class="t">{e(titel)}</div>\n'
                f'          <div class="d">{e(omschrijving)}</div>\n'
                f'        </a>')

    verder = []
    for l in zelfde:
        verder.append(kaartje(l, f'Ook in {e(p["gemeente"])}'))
    for l in buurt[:4]:
        verder.append(kaartje(l, 'In de buurt'))
    verder_html = ''
    if verder:
        verder_html = f'''
      <div class="related">
        <h2 id="in-de-buurt">Kermissen in de buurt</h2>
        <div class="related-grid">
{chr(10).join(verder)}
        </div>
      </div>'''

    # ---- FAQ
    vragen = [
        (f'Is de kermis in {p["gemeente"]} gratis?',
         'Ja. Het kermisterrein is vrij toegankelijk — je betaalt enkel per attractie, '
         'per spel of per portie. Met een <a href="/hoe-het-werkt.html">digitale spaarkaart</a> '
         'houd je bij elke beurt punten over.'),
        ('Gaat de kermis door bij regen?',
         'Meestal wel. De kramen blijven open bij regen; alleen bij storm of harde wind '
         'leggen foorkramers de hoge attracties tijdelijk stil. Bij twijfel volg je best '
         f'de kanalen van de gemeente {e(p["gemeente"])}.'),
    ]
    if n >= 8:
        vragen.append(
            (f'Hoe lang duurt {p["naam"]} in {p["gemeente"]}?',
             f'{n} dagen, van {datum(p["start"])} tot en met {datum(p["eind"])}. '
             'Dat zijn meerdere weekends — genoeg tijd om je punten te laten oplopen '
             'en ze bij een tweede bezoek in te ruilen.'))
    elif feest:
        vragen.append(
            (f'Valt {p["naam"]} samen met een feestdag?',
             f'Ja: {" en ".join(feest)} valt in deze periode. Op feestdagen openen '
             'de kramen doorgaans vroeger en is het merkbaar drukker dan op een gewone dag.'))
    else:
        vragen.append(
            (f'Wanneer is het volgend jaar kermis in {p["gemeente"]}?',
             'De data van de volgende editie zetten we op deze pagina zodra de gemeente '
             'ze vastlegt. Deze pagina blijft dezelfde — je hoeft dus niets nieuws te zoeken.'))
    vragen.append(
        (f'Kan ik punten sparen op de kermis in {p["gemeente"]}?',
         'Bij elk kraam dat met Funpoints werkt wel. Je toont je persoonlijke QR-code, de '
         'foorkramer scant hem, en je punten staan meteen geboekt. Staat er hier nog geen '
         'Funpoints-kraam? Laat het weten aan je vaste foorkramer — of '
         '<a href="/demo/">vraag een demo aan</a> als je er zelf een uitbaat.'))

    # ---- schema
    event = {
        "@type": "Event",
        "name": f'{p["naam"]} {p["gemeente"]}',
        "startDate": p['start'],
        "endDate": p['eind'],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "isAccessibleForFree": True,
        "url": url,
        "inLanguage": "nl-BE",
        "description": p['antwoord'],
        "location": {
            "@type": "Place",
            "name": f'{p["naam"]}, {p["gemeente"]}',
            "address": {
                "@type": "PostalAddress",
                "addressLocality": p['gemeente'],
                "postalCode": p['postcode'],
                "addressRegion": prov,
                "addressCountry": "BE",
            },
        },
        "image": [f"{BASIS}/img/funpoints-digitale-spaarkaart-kermis.png"],
    }
    ld = {"@context": "https://schema.org", "@graph": [
        event,
        kruimels([('Funpoints', '/'), ('Kermiskalender', '/kermis/'),
                  (prov, f'/kermis/provincie/{ps}/'),
                  (p['gemeente'], f'/kermis/{p["gemeente_slug"]}/'),
                  (p['naam'], p['pad'] + '/')]),
        faq_ld([(v, re.sub('<[^>]+>', '', a)) for v, a in vragen]),
        ORG]}

    dl = {"page_type": "kermis", "page_category": "kermis", "page_audience": "b2c",
          "page_name": f'{p["naam"]} {p["gemeente"]}', "page_language": "nl-BE",
          "kermis_gemeente": p['gemeente'], "kermis_provincie": prov,
          "kermis_status": st}

    body = f'''  <section class="page-hero article-head">
    <div class="container">
      <div class="article-head-inner">
      <p class="crumbs"><a href="/">Funpoints</a> › <a href="/kermis/">Kermiskalender</a> › <a href="/kermis/provincie/{ps}/">{e(prov)}</a> › <a href="/kermis/{p["gemeente_slug"]}/">{e(p["gemeente"])}</a> › {e(p["naam"])}</p>
      <span class="eyebrow kermis-status" data-start="{p['start']}" data-eind="{p['eind']}">{BADGE[st]}</span>
      <h1>{e(p["h1"])}</h1>
      </div>
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container article">
      <div class="answer">
        <p style="margin:0;">{e(p["antwoord"])}</p>
      </div>

      <h2 id="praktisch">Praktisch</h2>
      <div class="tabel-scroll">
        <table>
          <caption class="note">{e(p["naam"])} in {e(p["gemeente"])} — editie {JAAR}</caption>
          <tbody>
{tabel}
          </tbody>
        </table>
      </div>

      <h2 id="wat-staat-er">Wat staat er op het plein?</h2>
      <div class="cal-empty">
        <p><b>De attractielijst van deze kermis staat er nog niet.</b></p>
        <p>We zetten alleen kramen op deze pagina waarvan we de gegevens rechtstreeks van de
        uitbater krijgen — met foto's van dit plein in plaats van stockbeelden. Sta je hier met
        een kraam? <a href="/demo/">Laat het ons weten</a> en je attractie komt erbij te staan.</p>
      </div>

      <h2 id="lokale-hoek">Wat deze kermis eigen is</h2>
      <ul>
{uniek}
      </ul>

      <h2 id="spaaractie">Punten sparen op deze kermis</h2>
      <p>Funpoints vervangt het papieren spaarkaartje: je hebt één QR-code op je telefoon die
      elk deelnemend kraam scant. Je punten blijven bij het kraam waar je ze spaarde, en je
      neemt ze mee naar de volgende kermis op je route. <a href="/hoe-het-werkt.html">Zo werkt
      punten sparen</a>, van registreren tot je prijs uit de kast.</p>
      <p class="note">Deelnemende kramen verschijnen op deze pagina zodra ze aangesloten zijn.
      Nog geen Funpoints-kraam in {e(p["gemeente"])}? <a href="/uitbaters.html">Uitbaters lezen
      hier hoe ze aansluiten</a>.</p>

      <h2 id="veelgestelde-vragen">Veelgestelde vragen</h2>
    </div>
  </section>

  <section style="padding-top:0;">
{faq_html(vragen)}
  </section>

  <section style="padding-top:0;">
    <div class="container article">{verder_html}
    </div>
  </section>

  <section>
    <div class="container">
      <div class="cta">
        <h2>Spaar punten bij elke beurt</h2>
        <p>Eén QR-code voor alle deelnemende kramen, je punten reizen mee van kermis naar kermis.</p>
        <a class="btn btn-ghost btn-lg" href="/bezoekers.html">Zo werkt het voor bezoekers</a>
      </div>
    </div>
  </section>
'''
    schrijf(p['pad'] + '/index.html',
            kop(p['title'], p['description'], url, dl, jsonld=ld, noindex=p['noindex'])
            + body + VOET)


# ------------------------------------------------------ gemeentepagina
def bouw_gemeente(slug):
    g = gemeenten[slug]
    lijst = per_gemeente[slug]
    prov = g['provincie']
    ps = prov_slug[prov]
    url = f'{BASIS}/kermis/{slug}/'
    noindex = all(p['noindex'] for p in lijst)
    komend = [p for p in lijst if status(p['start'], p['eind']) != 'voorbij']
    eerst = komend[0] if komend else lijst[-1]
    aantal = len(lijst)

    title = f'Kermis in {g["naam"]} 2026 — data en spaaracties'
    if len(title) > 60:
        title = f'Kermis {g["naam"]} 2026 — data & spaaracties'[:60]
    woord = 'kermis' if aantal == 1 else 'kermissen'
    descr = (f'Wanneer is het kermis in {g["naam"]}? Alle {aantal} {woord} van 2026 '
             f'met data, uren en spaaracties. Registreer vooraf en spaar punten.')[:155]

    if komend:
        antwoord = (f'In {g["naam"]} ({g["postcode"]}) staan er {aantal} {woord} op de '
                    f'kalender van {JAAR}. De eerstvolgende is {eerst["naam"]}, '
                    f'van {datum(eerst["start"])} tot en met {datum(eerst["eind"])}. '
                    f'De toegang tot het kermisterrein is gratis.')
    else:
        antwoord = (f'In {g["naam"]} ({g["postcode"]}) stonden er {aantal} {woord} op de '
                    f'kalender van {JAAR}. De laatste was {eerst["naam"]}, '
                    f'van {datum(eerst["start"])} tot en met {datum(eerst["eind"])}. '
                    f'De data van de volgende editie komen op deze pagina zodra ze bekend zijn.')

    rijen = []
    for p in lijst:
        st = status(p['start'], p['eind'])
        rijen.append(
            f'          <tr class="kermis-rij" data-start="{p["start"]}" data-eind="{p["eind"]}">'
            f'<td><a href="{p["pad"]}/">{e(p["naam"])}</a></td>'
            f'<td>{datum_kort(p["start"])} – {datum_kort(p["eind"])}</td>'
            f'<td><span class="kermis-status">{BADGE[st]}</span></td></tr>')

    # buurgemeenten: uit de linkstructuur van de kermissen
    buurt, gezien = [], {slug}
    for p in lijst:
        for l in p['links']:
            if l['soort'] != 'buurt':
                continue
            doel = per_pad.get(l['href'])
            if doel and doel['gemeente_slug'] not in gezien:
                gezien.add(doel['gemeente_slug'])
                buurt.append(doel)
    buurt_html = ''
    if buurt:
        kaarten = '\n'.join(
            f'        <a href="/kermis/{b["gemeente_slug"]}/">\n'
            f'          <div class="k">{e(b["provincie"])}</div>\n'
            f'          <div class="t">Kermis in {e(b["gemeente"])}</div>\n'
            f'          <div class="d">{len(per_gemeente[b["gemeente_slug"]])} '
            f'{"kermis" if len(per_gemeente[b["gemeente_slug"]]) == 1 else "kermissen"} in {JAAR}</div>\n'
            f'        </a>' for b in buurt[:6])
        buurt_html = f'''
      <div class="related">
        <h2 id="in-de-buurt">Kermissen in de buurt van {e(g["naam"])}</h2>
        <div class="related-grid">
{kaarten}
        </div>
      </div>'''

    vragen = [
        (f'Wanneer is het kermis in {g["naam"]}?',
         f'{"De eerstvolgende" if komend else "De laatste"} kermis is {eerst["naam"]}, van '
         f'{datum(eerst["start"])} tot en met {datum(eerst["eind"])}. '
         f'In totaal staan er {aantal} {woord} op de kalender van {JAAR}.'),
        (f'Is de kermis in {g["naam"]} gratis?',
         'Ja, het terrein is vrij toegankelijk. Je betaalt per attractie, per spel of per portie.'),
        (f'Hoeveel kermissen telt {g["naam"]}?',
         f'{aantal} in {JAAR}. Dorps- en wijkkermissen wisselen elkaar af over het seizoen, '
         'dat in België loopt van het voorjaar tot half november.'),
    ]

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "url": url, "name": f'Kermissen in {g["naam"]}',
         "inLanguage": "nl-BE", "description": descr,
         "publisher": {"@id": f"{BASIS}/#organization"},
         "about": {"@type": "Place", "name": g['naam'],
                   "address": {"@type": "PostalAddress", "addressLocality": g['naam'],
                               "postalCode": g['postcode'], "addressRegion": prov,
                               "addressCountry": "BE"}}},
        {"@type": "ItemList", "name": f'Kermissen in {g["naam"]} {JAAR}',
         "numberOfItems": aantal,
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": p['naam'],
              "url": BASIS + p['pad'] + '/'} for i, p in enumerate(lijst)]},
        kruimels([('Funpoints', '/'), ('Kermiskalender', '/kermis/'),
                  (prov, f'/kermis/provincie/{ps}/'), (g['naam'], f'/kermis/{slug}/')]),
        faq_ld([(v, re.sub('<[^>]+>', '', a)) for v, a in vragen]),
        ORG]}

    dl = {"page_type": "gemeente", "page_category": "kermis", "page_audience": "b2c",
          "page_name": f'Kermis {g["naam"]}', "page_language": "nl-BE",
          "kermis_gemeente": g['naam'], "kermis_provincie": prov}

    body = f'''  <section class="page-hero article-head">
    <div class="container">
      <div class="article-head-inner">
      <p class="crumbs"><a href="/">Funpoints</a> › <a href="/kermis/">Kermiskalender</a> › <a href="/kermis/provincie/{ps}/">{e(prov)}</a> › {e(g["naam"])}</p>
      <span class="eyebrow">🗓️ {aantal} {woord} in {JAAR}</span>
      <h1>Kermis in {e(g["naam"])}</h1>
      </div>
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container article">
      <div class="answer">
        <p style="margin:0;">{e(antwoord)}</p>
      </div>

      <h2 id="kalender">De kermiskalender van {e(g["naam"])}</h2>
      <div class="tabel-scroll">
        <table>
          <thead><tr><th scope="col">Kermis</th><th scope="col">Wanneer</th><th scope="col">Status</th></tr></thead>
          <tbody>
{chr(10).join(rijen)}
          </tbody>
        </table>
      </div>
      <p class="note">Data zoals opgegeven door de gemeenten. Openingsuren en attracties
      verschijnen per kermis zodra de uitbater ze doorgeeft.</p>

      <h2 id="punten-sparen">Punten sparen in {e(g["naam"])}</h2>
      <p>Met Funpoints spaar je op elke deelnemende kermis punten met dezelfde QR-code op je
      telefoon. Je punten blijven staan tussen twee kermissen door, dus wat je in het voorjaar
      spaart, kan je in het najaar inruilen. <a href="/hoe-het-werkt.html">Zo werkt het</a>.</p>

      <h2 id="veelgestelde-vragen">Veelgestelde vragen</h2>
    </div>
  </section>

  <section style="padding-top:0;">
{faq_html(vragen)}
  </section>

  <section style="padding-top:0;">
    <div class="container article">{buurt_html}
    </div>
  </section>

  <section>
    <div class="container">
      <div class="cta">
        <h2>Sta jij met een kraam in {e(g["naam"])}?</h2>
        <p>Zet je kraam op deze pagina: je attractie, je openingsuren en je spaaractie,
        vindbaar voor iedereen die op "kermis {e(g["naam"])}" zoekt.</p>
        <a class="btn btn-ghost btn-lg" href="/demo/">Vraag een demo aan je kraam</a>
      </div>
    </div>
  </section>
'''
    schrijf(f'/kermis/{slug}/index.html',
            kop(title, descr, url, dl, jsonld=ld, noindex=noindex) + body + VOET)


# ----------------------------------------------------- provinciepagina
def bouw_provincie(naam):
    ps = prov_slug[naam]
    lijst = per_provincie[naam]
    gems = sorted({p['gemeente_slug'] for p in lijst},
                  key=lambda s: gemeenten[s]['naam'])
    url = f'{BASIS}/kermis/provincie/{ps}/'
    noindex = all(p['noindex'] for p in lijst)
    komend = [p for p in lijst if status(p['start'], p['eind']) != 'voorbij']

    title = f'Kermissen in {naam} 2026 — volledige kalender'[:60]
    descr = (f'Alle {len(lijst)} kermissen in {naam} in 2026, per gemeente en op datum. '
             f'Data, uren en spaaracties op één kalender.')[:155]
    antwoord = (f'In {naam} staan er {len(lijst)} kermissen op de kalender van {JAAR}, '
                f'verspreid over {len(gems)} gemeenten. '
                + (f'De eerstvolgende is {komend[0]["naam"]} in {komend[0]["gemeente"]}, '
                   f'van {datum(komend[0]["start"])} tot en met {datum(komend[0]["eind"])}.'
                   if komend else 'Het seizoen is hier afgelopen; de data van volgend jaar '
                                  'komen op deze pagina zodra ze bekend zijn.'))

    volgende = komend[:12]
    rijen = '\n'.join(
        f'          <tr class="kermis-rij" data-start="{p["start"]}" data-eind="{p["eind"]}">'
        f'<td><a href="{p["pad"]}/">{e(p["naam"])}</a></td>'
        f'<td><a href="/kermis/{p["gemeente_slug"]}/">{e(p["gemeente"])}</a></td>'
        f'<td>{datum_kort(p["start"])} – {datum_kort(p["eind"])}</td></tr>'
        for p in volgende)

    kolommen = '\n'.join(
        f'        <a href="/kermis/{s}/">{e(gemeenten[s]["naam"])} '
        f'<span>({len(per_gemeente[s])})</span></a>' for s in gems)

    vragen = [
        (f'Hoeveel kermissen zijn er in {naam}?',
         f'{len(lijst)} in {JAAR}, verspreid over {len(gems)} gemeenten — van dorpskermissen '
         'van een weekend tot stadsforen die weken duren.'),
        (f'Wanneer loopt het kermisseizoen in {naam}?',
         f'De eerste kermis van {JAAR} start op {datum(min(p["start"] for p in lijst))}, '
         f'de laatste loopt tot {datum(max(p["eind"] for p in lijst))}.'),
    ]

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "url": url, "name": f'Kermissen in {naam}',
         "inLanguage": "nl-BE", "description": descr,
         "publisher": {"@id": f"{BASIS}/#organization"}},
        {"@type": "ItemList", "name": f'Kermissen in {naam} {JAAR}',
         "numberOfItems": len(lijst),
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1,
              "name": f'{p["naam"]} — {p["gemeente"]}',
              "url": BASIS + p['pad'] + '/'} for i, p in enumerate(lijst)]},
        kruimels([('Funpoints', '/'), ('Kermiskalender', '/kermis/'),
                  (naam, f'/kermis/provincie/{ps}/')]),
        faq_ld(vragen), ORG]}

    dl = {"page_type": "provincie", "page_category": "kermis", "page_audience": "b2c",
          "page_name": f'Kermissen {naam}', "page_language": "nl-BE",
          "kermis_provincie": naam}

    body = f'''  <section class="page-hero article-head">
    <div class="container">
      <div class="article-head-inner">
      <p class="crumbs"><a href="/">Funpoints</a> › <a href="/kermis/">Kermiskalender</a> › {e(naam)}</p>
      <span class="eyebrow">🗓️ {len(lijst)} kermissen · {len(gems)} gemeenten</span>
      <h1>Kermissen in {e(naam)}</h1>
      </div>
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container article">
      <div class="answer">
        <p style="margin:0;">{e(antwoord)}</p>
      </div>

      <h2 id="eerstvolgende">Eerstvolgende kermissen</h2>
      {'<div class="tabel-scroll"><table><thead><tr><th scope="col">Kermis</th><th scope="col">Gemeente</th><th scope="col">Wanneer</th></tr></thead><tbody>' + chr(10) + rijen + chr(10) + '</tbody></table></div>' if volgende else '<div class="cal-empty"><p><b>Het seizoen is hier afgelopen.</b></p><p>De data van volgend jaar komen op deze pagina zodra de gemeenten ze vastleggen.</p></div>'}

      <h2 id="gemeenten">Alle gemeenten in {e(naam)}</h2>
      <div class="gemeentelijst">
{kolommen}
      </div>

      <h2 id="veelgestelde-vragen">Veelgestelde vragen</h2>
    </div>
  </section>

  <section style="padding-top:0;">
{faq_html(vragen)}
  </section>

  <section>
    <div class="container">
      <div class="cta">
        <h2>Zet je kramen in {e(naam)} op de kalender</h2>
        <p>Elke stop van je route krijgt een eigen pagina met je attracties, je uren en je spaaractie.</p>
        <a class="btn btn-ghost btn-lg" href="/demo/">Vraag een demo aan je kraam</a>
      </div>
    </div>
  </section>
'''
    schrijf(f'/kermis/provincie/{ps}/index.html',
            kop(title, descr, url, dl, jsonld=ld, noindex=noindex) + body + VOET)


# ------------------------------------------------------------ hub
def bouw_hub():
    url = f'{BASIS}/kermis/'
    komend = sorted([p for p in paginas
                     if status(p['start'], p['eind']) != 'voorbij' and not p['noindex']],
                    key=lambda p: p['start'])
    bezig = [p for p in paginas if status(p['start'], p['eind']) == 'open']
    title = 'Kermiskalender België 2026 — Alle Kermissen | Funpoints'[:60]
    descr = (f'Alle {len(paginas)} kermissen van 2026 in België: data, openingsuren en '
             'spaaracties per gemeente. Zoek de kermis in jouw buurt.')[:155]
    antwoord = (f'Op deze kalender staan {len(paginas)} kermissen in {len(gemeenten)} Belgische '
                f'gemeenten voor {JAAR}. Per kermis vind je de exacte data, wat je er mag '
                'verwachten en welke spaaractie er loopt. De toegang tot een kermisterrein is '
                'in België altijd gratis — je betaalt per attractie.')

    rijen = '\n'.join(
        f'          <tr class="kermis-rij" data-start="{p["start"]}" data-eind="{p["eind"]}">'
        f'<td><a href="{p["pad"]}/">{e(p["naam"])}</a></td>'
        f'<td><a href="/kermis/{p["gemeente_slug"]}/">{e(p["gemeente"])}</a></td>'
        f'<td>{datum_kort(p["start"])} – {datum_kort(p["eind"])}</td></tr>'
        for p in komend[:20])

    provkaarten = '\n'.join(
        f'''      <a href="/kermis/provincie/{prov_slug[n]}/">
        <b>{e(n)}</b>
        <span>{provincies[n]["aantal"]} kermissen in {len(provincies[n]["gemeenten"])} gemeenten</span>
      </a>''' for n in sorted(provincies, key=lambda n: -provincies[n]['aantal']))

    vragen = [
        ('Hoeveel kermissen zijn er in België?',
         f'Op deze kalender staan er {len(paginas)} voor {JAAR}, in {len(gemeenten)} gemeenten. '
         'Het werkelijke aantal ligt hoger: veel kleine wijkkermissen worden nergens centraal '
         'bijgehouden.'),
        ('Wanneer loopt het kermisseizoen in België?',
         'Het klassieke seizoen loopt van het vroege voorjaar tot half november, met '
         'Wapenstilstand (11 november) als traditionele afsluiter. Rond carnaval en de '
         'kerstperiode komen daar winterkermissen bij.'),
        ('Is de kermis gratis?',
         'Het terrein wel. Je betaalt per attractie, per spel of per portie. Hoeveel dat kost '
         'lees je in <a href="/magazine/wat-kost-een-dagje-kermis/">wat kost een dagje kermis</a>.'),
        ('Staat mijn gemeente op de kalender?',
         f'We dekken {len(gemeenten)} gemeenten. Kies je provincie hierboven en zoek je gemeente '
         'in de lijst. Ontbreekt ze? Dan hebben we er nog geen data voor — laat het weten via '
         '<a href="mailto:info@funpoints.be">info@funpoints.be</a>.'),
    ]

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "url": url, "name": f'Kermiskalender België {JAAR}',
         "inLanguage": "nl-BE", "description": descr,
         "publisher": {"@id": f"{BASIS}/#organization"},
         "image": {"@type": "ImageObject",
                   "url": f"{BASIS}/img/funpoints-digitale-spaarkaart-kermis.png",
                   "width": 1200, "height": 630,
                   "caption": "Funpoints — het digitale spaarkaartje van de kermis"}},
        {"@type": "ItemList", "name": f'Kermissen in België per provincie',
         "numberOfItems": len(provincies),
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": n,
              "url": f'{BASIS}/kermis/provincie/{prov_slug[n]}/'}
             for i, n in enumerate(sorted(provincies))]},
        kruimels([('Funpoints', '/'), ('Kermiskalender', '/kermis/')]),
        faq_ld([(v, re.sub('<[^>]+>', '', a)) for v, a in vragen]), ORG]}

    dl = {"page_type": "hub", "page_category": "kermis", "page_audience": "b2c",
          "page_name": "Kermiskalender", "page_language": "nl-BE"}

    body = f'''  <section class="page-hero">
    <div class="container">
      <span class="eyebrow">🗓️ {len(paginas)} kermissen · {len(gemeenten)} gemeenten</span>
      <h1>Kermiskalender België</h1>
      <p>Wanneer staat de kermis in jouw gemeente? Data, uren en de spaaractie per kermis —
      van dorpskermis tot stadsfoor.</p>
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container article">
      <div class="answer">
        <p style="margin:0;">{e(antwoord)}</p>
      </div>
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container section-head">
      <span class="kicker">Kies je provincie</span>
      <h2>Kermissen per provincie</h2>
    </div>
    <div class="container jump">
{provkaarten}
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container section-head">
      <span class="kicker">Eerstvolgende</span>
      <h2>Kermissen die eraan komen</h2>
      <p>{len(bezig)} kermissen zijn nu bezig, {len(komend)} staan er nog op de kalender van {JAAR}.</p>
    </div>
    <div class="container article">
      <div class="tabel-scroll">
        <table>
          <thead><tr><th scope="col">Kermis</th><th scope="col">Gemeente</th><th scope="col">Wanneer</th></tr></thead>
          <tbody>
{rijen}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container section-head">
      <span class="kicker">Zoek je gemeente</span>
      <h2>Jouw kermis op deze kalender?</h2>
      <p>Elke kermis krijgt een eigen pagina. Staat er een Funpoints-uitbater, dan komen daar
      de attracties, de openingsuren en de spaaractie bij te staan.</p>
    </div>
    <div class="container grid-3">
      <div class="card">
        <div class="ic tint-green">📅</div>
        <h3>Data &amp; duur</h3>
        <p>Start- en einddatum per kermis, met de feestdagen die erin vallen — want dan is het druk.</p>
      </div>
      <div class="card">
        <div class="ic tint-coral">🎡</div>
        <h3>Wat er staat</h3>
        <p>De attracties en kramen van dit jaar, rechtstreeks van de uitbater die er staat.</p>
      </div>
      <div class="card linked">
        <div class="ic tint-violet">🎁</div>
        <h3>De spaaractie</h3>
        <p>Welke prijzen je kan sparen en hoe je vooraf registreert.</p>
        <a class="more" href="/bezoekers.html">Zo spaar je punten →</a>
      </div>
    </div>
  </section>

  <section style="padding-top:10px;">
    <div class="container article">
      <h2 id="veelgestelde-vragen">Veelgestelde vragen</h2>
    </div>
{faq_html(vragen)}
  </section>

  <section style="padding-top:10px;">
    <div class="container jump">
      <a href="/magazine/wat-kost-een-dagje-kermis/">
        <b>💶 Wat kost een dagje kermis?</b>
        <span>Richtprijzen per attractie en per spel, plus een rekenvoorbeeld voor een gezin.</span>
      </a>
      <a href="/magazine/grootste-kermissen-van-belgie/">
        <b>🏆 De grootste kermissen van België</b>
        <span>Luik, de Zuidfoor en de Sinksenfoor — met bezoekerscijfers en bronnen.</span>
      </a>
    </div>
  </section>

  <section>
    <div class="container">
      <div class="cta">
        <h2>Uitbater? Zo kom je op deze kalender</h2>
        <p>Zet je stops op Funpoints en elke kermis van jouw route krijgt hier een eigen pagina —
        vindbaar voor iedereen die op jouw gemeente zoekt.</p>
        <a class="btn btn-ghost btn-lg" href="/demo/">Vraag een demo aan je kraam</a>
      </div>
    </div>
  </section>
'''
    schrijf('/kermis/index.html',
            kop(title, descr, url, dl, jsonld=ld) + body + VOET)


# ------------------------------------------------------------ sitemaps
def bouw_sitemaps():
    vandaag = VANDAAG.isoformat()
    indexen = []
    hub_urls = [(f'{BASIS}/kermis/', vandaag)]
    for naam in sorted(provincies):
        lijst = [p for p in per_provincie[naam] if not p['noindex']]
        if not lijst:
            continue
        ps = prov_slug[naam]
        hub_urls.append((f'{BASIS}/kermis/provincie/{ps}/', vandaag))
        urls = []
        for s in sorted({p['gemeente_slug'] for p in lijst}):
            urls.append((f'{BASIS}/kermis/{s}/', vandaag))
        for p in lijst:
            urls.append((BASIS + p['pad'] + '/', p['start']))
        blok = '\n'.join(
            f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{m}</lastmod>\n  </url>'
            for u, m in urls)
        schrijf(f'/sitemap-kermis-{ps}.xml',
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + blok + '\n</urlset>\n')
        indexen.append(f'/sitemap-kermis-{ps}.xml')

    # De hub en de provinciepagina's samen in sitemap-kermis.xml. Bewust géén
    # geneste sitemapindex: het sitemapprotocol staat maar één niveau toe.
    blok = '\n'.join(
        f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{m}</lastmod>\n  </url>'
        for u, m in hub_urls)
    schrijf('/sitemap-kermis.xml',
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + blok + '\n</urlset>\n')

    # Hoofdindex: alle sitemaps van de site op één niveau.
    alles = (['/sitemap-core.xml', '/sitemap-kermis.xml'] + indexen
             + ['/sitemap-kennisbank.xml', '/sitemap-magazine.xml'])
    blok = '\n'.join(
        f'  <sitemap>\n    <loc>{BASIS}{i}</loc>\n    <lastmod>{vandaag}</lastmod>\n  </sitemap>'
        for i in alles)
    schrijf('/sitemap.xml',
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + blok + '\n</sitemapindex>\n')
    return indexen


# ------------------------------------------------------------ status.js
STATUS_JS = '''/* Houdt de kermisstatus actueel zonder server: de pagina wordt statisch
   gebouwd, dit scriptje herberekent "nog te komen / nu bezig / voorbij"
   in de browser aan de hand van data-start en data-eind. */
(function () {
  'use strict';
  var vandaag = new Date();
  vandaag.setHours(0, 0, 0, 0);

  function label(start, eind) {
    var s = new Date(start + 'T00:00:00');
    var t = new Date(eind + 'T00:00:00');
    if (vandaag < s) {
      var dagen = Math.round((s - vandaag) / 86400000);
      if (dagen === 0) return '\\uD83C\\uDF61 Start vandaag';
      if (dagen === 1) return '\\uD83D\\uDDD3\\uFE0F Start morgen';
      if (dagen <= 14) return '\\uD83D\\uDDD3\\uFE0F Over ' + dagen + ' dagen';
      return '\\uD83D\\uDDD3\\uFE0F Nog te komen';
    }
    if (vandaag > t) return '\\u2714\\uFE0F Voorbij';
    return '\\uD83C\\uDFA1 Nu bezig';
  }

  /* Losse badge bovenaan een kermispagina */
  Array.prototype.forEach.call(
    document.querySelectorAll('.kermis-status[data-start]'), function (el) {
      el.textContent = label(el.getAttribute('data-start'), el.getAttribute('data-eind'));
    });

  /* Statuskolom in een kalendertabel */
  Array.prototype.forEach.call(
    document.querySelectorAll('.kermis-rij[data-start]'), function (rij) {
      var badge = rij.querySelector('.kermis-status');
      if (badge) badge.textContent = label(rij.getAttribute('data-start'),
                                           rij.getAttribute('data-eind'));
    });
})();
'''


# ------------------------------------------------------------ uitvoeren
if __name__ == '__main__':
    for p in paginas:
        bouw_kermis(p)
    for s in gemeenten:
        bouw_gemeente(s)
    for n in provincies:
        bouw_provincie(n)
    bouw_hub()
    schrijf('/kermis/status.js', STATUS_JS)
    idx = bouw_sitemaps()

    print(f'{len(geschreven)} bestanden geschreven in {DOEL}')
    print(f'  kermispagina\'s : {len(paginas)}')
    print(f'  gemeentepagina\'s: {len(gemeenten)}')
    print(f'  provinciepagina\'s: {len(provincies)}')
    print(f'  sitemaps        : {len(idx) + 1}')
