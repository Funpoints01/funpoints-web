#!/usr/bin/env python3
"""
Zet de JSON-LD-graaf en een zichtbaar FAQ-blok op /uitbaters.html en
/foorkramers.html. Idempotent: al aangepaste pagina's slaat hij over.

De FAQ-vragen staan bewust óók zichtbaar op de pagina — FAQPage-markup zonder
zichtbare vragen is in strijd met de richtlijnen van Google.

Draaien vanuit de repo-root:  python3 tools/schemas_inbouwen.py .
"""
import json, os, re, sys

WORTEL = sys.argv[1] if len(sys.argv) > 1 else '.'
BASIS = 'https://funpoints.be'
GEWIJZIGD = '2026-08-10'

ORG = {
    "@type": "Organization",
    "@id": f"{BASIS}/#organization",
    "name": "Funpoints",
    "url": f"{BASIS}/",
    "logo": {"@type": "ImageObject", "@id": f"{BASIS}/#logo",
             "url": f"{BASIS}/favicon.png", "width": 256, "height": 256,
             "caption": "Funpoints"},
    "image": {"@id": f"{BASIS}/#logo"},
    "email": "info@funpoints.be",
    "description": "Funpoints is het digitale spaarsysteem voor de kermis.",
    "areaServed": {"@type": "Country", "name": "België"},
}

SITE = {
    "@type": "WebSite",
    "@id": f"{BASIS}/#website",
    "url": f"{BASIS}/",
    "name": "Funpoints",
    "inLanguage": "nl-BE",
    "publisher": {"@id": f"{BASIS}/#organization"},
}


def webpage(url, naam, omschrijving, kruimel_id):
    return {
        "@type": "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": naam,
        "description": omschrijving,
        "inLanguage": "nl-BE",
        "isPartOf": {"@id": f"{BASIS}/#website"},
        "breadcrumb": {"@id": kruimel_id},
        "dateModified": GEWIJZIGD,
    }


def kruimels(id_, paren):
    return {"@type": "BreadcrumbList", "@id": id_,
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": BASIS + u}
                for i, (n, u) in enumerate(paren)]}


def faq_ld(url, paren):
    return {"@type": "FAQPage", "@id": url + "#faq",
            "mainEntity": [{"@type": "Question", "name": v,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for v, a in paren]}


def faq_html(kop, paren):
    items = '\n'.join(f'''      <details class="faq-item">
        <summary>{v}</summary>
        <div class="faq-answer">
          <p>{a}</p>
        </div>
      </details>''' for v, a in paren)
    return f'''
  <section style="padding-top:10px;">
    <div class="container section-head">
      <span class="kicker">Veelgestelde vragen</span>
      <h2>{kop}</h2>
    </div>
    <div class="container faq">
{items}
    </div>
  </section>
'''


# ------------------------------------------------------------- uitbaters
U_URL = f'{BASIS}/uitbaters.html'
U_FAQ = [
    ("Heb ik een kassasysteem nodig?",
     "Nee. Funpoints werkt los van je kassa. Je medewerker scant de QR-code van de klant "
     "met een gewone smartphone of tablet — meer heb je niet nodig om punten te boeken."),
    ("Kan ik meerdere kramen onder één account beheren?",
     "Ja. Je beheert al je kramen vanuit één dashboard, met statistieken en grafieken per "
     "kraam. Logins voor je medewerkers maak je zelf aan in enkele klikken."),
    ("Werkt het ook voor kramen zonder puntensysteem?",
     "Ja. Eetkramen en attracties die geen punten uitdelen, kunnen wel acties en vouchers "
     "opzetten — bijvoorbeeld een gratis ritje of een eenmalige voucher."),
    ("Hoe bereik ik bezoekers in de buurt?",
     "Je kiest een regio rond een postcode, ziet live hoeveel bezoekers je daarmee bereikt "
     "en stuurt een pushmelding over je actie. Je betaalt met credits, enkel voor wie je "
     "effectief bereikt. Minderjarigen worden automatisch afgeschermd."),
    ("Van wie zijn de klantgegevens?",
     "Van jou. De spaarders die je opbouwt zijn jouw klanten. Stop je ooit met Funpoints, "
     "dan neem je je gegevens mee."),
]

DASHBOARD = {
    "@type": "SoftwareApplication",
    "@id": f"{BASIS}/#dashboard",
    "name": "Funpoints-dashboard voor uitbaters",
    "url": "https://app.funpoints.be",
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web",
    "description": "Beheer je kramen, zet acties en vouchers op, bekijk statistieken per "
                   "kraam en bereik bezoekers in de buurt met gerichte meldingen.",
    "featureList": [
        "Statistieken en grafieken per kraam",
        "Meerdere kramen onder één account",
        "Logins aanmaken voor medewerkers",
        "Punten-bonus of eenmalige voucher als actie",
        "Pushmeldingen met targeting op regio",
    ],
    "publisher": {"@id": f"{BASIS}/#organization"},
    "inLanguage": "nl-BE",
}

SERVICE = {
    "@type": "Service",
    "@id": f"{BASIS}/#loyaliteitsdienst",
    "name": "Funpoints — loyaliteitssysteem voor de kermis",
    "serviceType": "Loyaliteitsprogramma voor kermisuitbatingen",
    "url": U_URL,
    "description": "Een digitaal spaar- en actiesysteem gebouwd voor kramen die van plein "
                   "naar plein reizen: punten per beurt, acties en vouchers, en bereik bij "
                   "bezoekers in de buurt — zonder kassa-koppeling.",
    "provider": {"@id": f"{BASIS}/#organization"},
    "areaServed": {"@type": "Country", "name": "België"},
    "audience": {"@type": "BusinessAudience",
                 "audienceType": "Kermisuitbaters, foorreizigers en lunaparkuitbaters"},
    "availableChannel": {
        "@type": "ServiceChannel",
        "serviceUrl": "https://app.funpoints.be",
        "name": "Funpoints-dashboard",
    },
    "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Wat Funpoints voor een uitbater doet",
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {
                "@type": "Service", "name": "Dashboard en statistieken",
                "description": "Alle kramen onder één account, met cijfers en grafieken "
                               "per kraam en logins voor je medewerkers."}},
            {"@type": "Offer", "itemOffered": {
                "@type": "Service", "name": "Acties en vouchers",
                "description": "Extra punten, een gratis ritje of een eenmalige voucher, "
                               "meteen zichtbaar bij de bezoekers in de app."}},
            {"@type": "Offer", "itemOffered": {
                "@type": "Service", "name": "Meldingen met bereik",
                "description": "Pushmeldingen naar bezoekers in een regio rond een "
                               "postcode, met een live teller van je bereik."}},
        ],
    },
}

# ----------------------------------------------------------- foorkramers
F_URL = f'{BASIS}/foorkramers.html'
F_FAQ = [
    ("Moet ik een app installeren?",
     "Nee. Funpoints werkt gewoon in de browser van je telefoon. Je opent de pagina, logt "
     "in en kan scannen — er is niets zwaars te installeren."),
    ("Hoeveel tijd kost het per klant?",
     "Een paar seconden. Scannen en boeken is één handeling. Een nieuwe klant registreren "
     "duurt ongeveer een halve minuut en gebeurt aan de balie, terwijl jij verder werkt."),
    ("Hoe zie ik of een voucher nog geldig is?",
     "Aan de kleur. Je scant de voucher en het scherm wordt groen als hij geldig is, en "
     "rood als hij al gebruikt werd. Dubbel inwisselen kan dus niet."),
    ("Hoe krijg ik een login?",
     "Van je uitbater. Die maakt jouw login aan vanuit zijn dashboard. Baat je zelf een "
     "kraam uit? Dan komen we langs op je standplaats en zetten we het samen op."),
]

SCANNER = {
    "@type": "SoftwareApplication",
    "@id": f"{BASIS}/#scanner",
    "name": "Funpoints-scanner voor aan het kraam",
    "url": "https://app.funpoints.be",
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web",
    "description": "Scan de QR-code van de klant met je eigen telefoon, boek of trek punten "
                   "af en wissel vouchers in. Werkt in de browser, zonder installatie.",
    "featureList": [
        "QR-code van de klant scannen met een gewone telefoon",
        "Punten boeken en aftrekken",
        "Vouchers inwisselen met groen-of-rood controle",
        "Puntensaldo van de klant meteen zichtbaar",
    ],
    "publisher": {"@id": f"{BASIS}/#organization"},
    "isRelatedTo": {"@id": f"{BASIS}/#dashboard"},
    "inLanguage": "nl-BE",
}


PAGINAS = {
    'uitbaters.html': {
        'graaf': [
            ORG, SITE,
            webpage(U_URL, "Loyaliteitssysteem voor kermis en lunapark",
                    "Het spaarsysteem gebouwd voor de kermis: beheer je kramen, zet acties "
                    "en vouchers op en bereik bezoekers in de buurt.",
                    U_URL + "#kruimels"),
            kruimels(U_URL + "#kruimels",
                     [("Funpoints", "/"), ("Voor uitbaters", "/uitbaters.html")]),
            SERVICE, DASHBOARD,
            faq_ld(U_URL, U_FAQ),
        ],
        'faq_kop': 'Wat uitbaters ons vragen',
        'faq': U_FAQ,
    },
    'foorkramers.html': {
        'graaf': [
            ORG, SITE,
            webpage(F_URL, "Punten scannen en boeken met je telefoon",
                    "Scan de QR van de klant, boek punten en wissel vouchers in — snel, "
                    "zonder papierwerk.",
                    F_URL + "#kruimels"),
            kruimels(F_URL + "#kruimels",
                     [("Funpoints", "/"), ("Voor uitbaters", "/uitbaters.html"),
                      ("Aan het kraam", "/foorkramers.html")]),
            SCANNER,
            faq_ld(F_URL, F_FAQ),
        ],
        'faq_kop': 'Wat we het vaakst horen aan het kraam',
        'faq': F_FAQ,
    },
}


def verwerk(pad, spec):
    s = open(pad, encoding='utf-8').read()
    if 'application/ld+json' in s:
        return 'had al schema'

    ld = ('<script type="application/ld+json">\n'
          + json.dumps({"@context": "https://schema.org", "@graph": spec['graaf']},
                       ensure_ascii=False, indent=2)
          + '\n</script>\n')
    s = s.replace('</head>', ld + '</head>', 1)

    # Het FAQ-blok komt vóór het afsluitende CTA-blok te staan.
    merk = '  <section>\n    <div class="container">\n      <div class="cta">'
    if merk not in s:
        return 'geen CTA-blok gevonden'
    s = s.replace(merk, faq_html(spec['faq_kop'], spec['faq']).lstrip('\n') + '\n' + merk, 1)

    open(pad, 'w', encoding='utf-8').write(s)
    return 'aangepast'


if __name__ == '__main__':
    for naam, spec in PAGINAS.items():
        pad = os.path.join(WORTEL, naam)
        print(f'{verwerk(pad, spec):20} {naam}')
