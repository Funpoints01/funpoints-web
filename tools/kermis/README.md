# Kermiskalender — hoe je hem opnieuw genereert

De hele kalender onder `/kermis/` is gegenereerd. Pas **nooit** een gegenereerde
HTML-pagina met de hand aan: bij de volgende build is die wijziging weg. Pas de
bron aan en draai de build opnieuw.

## De bestanden

| Bestand | Wat het is |
|---|---|
| `kermissen.csv` | De ruwe data: 633 kermissen met gemeente, postcode, start- en einddatum. |
| `paginaspec.md` | De SEO-paginaspec: per kermis de title, description, H1, antwoordzin, keywords, lokale hoek en interne links. |
| `parse_spec.py` | Leest `paginaspec.md` + `kermissen.csv` en schrijft `kermissen.json`. |
| `kermissen.json` | Het datamodel waar de generator mee werkt. Gegenereerd — niet met de hand bewerken. |
| `build_kermis.py` | Schrijft alle HTML-pagina's en sitemaps. |

## Opnieuw bouwen

Vanuit deze map, met de repo-root als doel:

```
python3 parse_spec.py            # paginaspec.md → kermissen.json
python3 build_kermis.py ../..    # kermissen.json → HTML + sitemaps
```

Dat schrijft:

- `/kermis/index.html` — de nationale hub
- `/kermis/provincie/<provincie>/index.html` — 11 provinciepagina's
- `/kermis/<gemeente>/index.html` — 574 gemeentepagina's
- `/kermis/<gemeente>/<kermis>/index.html` — 633 kermispagina's
- `/sitemap.xml`, `/sitemap-kermis.xml` en zes `/sitemap-kermis-<provincie>.xml`

Alleen Python 3 nodig, geen packages.

## Een jaar verder

1. Zet de nieuwe data in `kermissen.csv` (zelfde kolommen).
2. Laat een nieuwe `paginaspec.md` genereren, of pas de bestaande aan.
3. Draai de twee commando's hierboven.

De URL's blijven dezelfde: `/kermis/aalter/septemberkermis/` is de pagina van
díe kermis, elk jaar opnieuw. Het jaartal staat in de title en de H1, niet in het
pad — zo houdt de pagina de autoriteit die ze opbouwt.

## Twee dingen om te weten

**Datums staan hard in de HTML, de status niet.** De pagina's zijn statisch, dus
"nog te komen / nu bezig / voorbij" wordt bij het bouwen berekend én daarna in de
browser opnieuw bepaald door `/kermis/status.js`. Zonder JavaScript ziet een
bezoeker de status van de bouwdatum; de datums zelf kloppen altijd.

**Franstalige pagina's staan op `noindex`.** 43 kermissen liggen in Wallonië en
hebben een Nederlandstalig sjabloon. Die staan bewust niet in de sitemaps en
dragen `<meta name="robots" content="noindex,follow">`. Haal dat pas weg als er
een Franse vertaling staat: `build_kermis.py` volgt de `noindex`-vlag uit
`kermissen.json`, die uit de paginaspec komt.

## Waar de provinciepagina's staan

De paginaspec zette de provinciepagina op `/kermis/<provincie>`, maar dat botst
met twee gemeentepagina's: Antwerpen en Brussel zijn allebei ook een gemeente in
de data. Daarom staan de provincies op `/kermis/provincie/<provincie>/`. De
gemeentepagina's houden het korte pad, want dat is de URL waar lokaal op gezocht
wordt.
