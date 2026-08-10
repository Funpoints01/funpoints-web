# tools/ — de scripts achter de site

De site is statische HTML zonder framework. Deze map bevat de scripts die de
delen onderhouden die op véél pagina's tegelijk staan, zodat je ze op één plek
aanpast in plaats van in 1.243 bestanden.

Alles draait op kale Python 3, zonder packages.

## Het belangrijkste: partials

`partials/` bevat de blokken die op elke pagina staan:

| Bestand | Wat |
|---|---|
| `header.html` | De doelgroepbalk, het logo, de hoofdnavigatie en de demo-knop |
| `footer.html` | De vier footerkolommen en de onderbalk |
| `head-consent.html` | Google Consent Mode v2 en het laden van de cookiebanner |
| `head-gtm.html` | De GTM-snippet in de `<head>` |
| `body-gtm.html` | De GTM-noscript in de `<body>` |

In elke pagina staan die blokken tussen markers:

```html
<!-- fp:header -->
 …
<!-- /fp:header -->
```

Wijzig je iets aan de navigatie of de footer, dan pas je **alleen het bestand in
`partials/` aan** en draai je daarna vanuit de repo-root:

```
python3 tools/partials.py .
```

Dat zet het nieuwe blok in elke HTML-pagina, ook in de gegenereerde
kalenderpagina's. Twee keer draaien verandert niets extra.

Waarom niet met JavaScript de header inladen? Omdat de navigatie en de footer
dan uit de HTML verdwijnen. Nu staan ze er gewoon in — zoekmachines zien de
interne links zonder JavaScript uit te voeren. De prijs is dat je het script
moet draaien; die ruil is het waard.

## Volgorde bij een grote wijziging

```
python3 tools/kermis/parse_spec.py          # alleen als de kermisdata wijzigt
python3 tools/kermis/build_kermis.py ../..  # genereert /kermis/ opnieuw
python3 tools/partials.py .                 # zet header/footer/GTM overal gelijk
```

`build_kermis.py` leest zélf uit `partials/`, dus de kalender komt meteen goed
uit de generator. `partials.py` daarna draaien is alleen nodig voor de
handgeschreven pagina's — maar het kan altijd, het is idempotent.

## De overige scripts

| Script | Wat het doet | Wanneer draaien |
|---|---|---|
| `kermis/parse_spec.py` | Zet de paginaspec en de CSV om in `kermissen.json` | Bij nieuwe kermisdata |
| `kermis/build_kermis.py` | Genereert de 1.219 kalenderpagina's en de sitemaps | Na elke datawijziging of partial-wijziging |
| `auteurs.py` | Koppelt de 13 artikels aan één auteursentiteit `#redactie` | Bij een nieuw artikel |
| `schemas_inbouwen.py` | Zet de JSON-LD-graaf op `uitbaters.html` | Eenmalig gedraaid; hier als naslag |
| `consent_inbouwen.py` | Bouwde de cookiebanner in | Eenmalig gedraaid; `partials.py` doet dit nu |
| `herschrijf_doelgroepen.py` | Bracht de site terug naar twee doelgroepen | Eenmalig gedraaid; hier als naslag |

De laatste drie zijn migratiescripts. Ze staan hier zodat je kan nalezen wat er
precies gewijzigd is, niet omdat je ze opnieuw moet draaien.

## Wat je met de hand mag aanpassen

Alles buiten `/kermis/` en buiten de markers. De teksten op de doelgroeppagina's,
de artikels in `/kennisbank/` en `/magazine/`, de demopagina — die schrijf je
gewoon rechtstreeks.

**Niet** met de hand aanpassen: iets tussen `<!-- fp:… -->` en `<!-- /fp:… -->`,
en niets onder `/kermis/`. Bij de volgende build is dat weg.

## De kalender: wat er nu allemaal uitkomt

`tools/kermis/build_kermis.py` schrijft niet alleen pagina's. Één run levert:

| Uitvoer | Wat |
|---|---|
| `/kermis/**` | 1 hub, 11 provincie-, 574 gemeente- en 633 kermispagina's |
| `/kermis/status.js` | herrekent "nu bezig / nog te komen / voorbij" in de browser |
| `/kermis/zoek.js` | het zoekveld op de hub |
| `/kermis/filter.js` | het filterveld in de gemeentelijst van een provincie |
| `/kermis/gemeenten.json` | zoekindex, ± 20 kB, wordt pas opgehaald bij het eerste teken |
| `/data/activiteit.json` | voer voor de meldingen linksonder |
| `sitemap-kermis*.xml` | sitemaps per provincie plus de index |

Draai het script **vanuit `tools/kermis/`**, anders vindt het `../partials` niet:

```
cd tools/kermis && python3 build_kermis.py ../..
```

## De meldingen linksonder

`js/funpoints-social.js` toont om de zoveel seconden een melding linksonder.
De inhoud komt uit `/data/activiteit.json` en bestaat **uitsluitend uit
kermissen die volgens onze eigen kalender bezig zijn of eraan komen**.

Er staan geen verzonnen gebruikers, downloads of aantallen in, en dat is geen
kieskeurigheid: verzonnen gebruikersactiviteit tonen is een oneerlijke
handelspraktijk onder Boek VI van het Wetboek van Economisch Recht, en het is
precies het soort claim waar een concurrent of de Economische Inspectie op kan
aankloppen. Zodra er échte cijfers zijn (aanmeldingen, aangesloten kramen), kan
`activiteit.json` daarmee aangevuld worden — het script toont ze dan mee.

Het script staat op de bezoekerspagina's, het magazine, de kennisbank en alle
kalenderpagina's. Niet op `/demo/` (daar mag niets van het formulier afleiden)
en niet op `uitbaters.html`.

## blokken/

`tools/blokken/` bevat twee stukken HTML die klaarstaan maar bewust nog niet
online staan: `reviews.html` (quotes van uitbaters) en `cases.html` (gemeenten).
Ze wachten op echte inhoud — zie `tools/blokken/README.md` voor wat ik precies
nodig heb om ze te kunnen invullen.
