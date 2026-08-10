# funpoints-web

Website voor Funpoints — door Uki, Arne en Casper.

Statische site, geen build-stap voor de gewone pagina's: de HTML in de root en in
`/kennisbank/`, `/magazine/` en `/demo/` schrijf je met de hand.

## Wat waar staat

| Map | Wat |
|---|---|
| `*.html` (root) | Doelgroeppagina's, hoe-het-werkt, over-ons, privacy, 404 |
| `demo/` | De demo-landingspagina met het aanvraagformulier (Formspree) |
| `kennisbank/` | Artikels voor uitbaters en foorkramers |
| `magazine/` | Artikels voor bezoekers |
| `kermis/` | **Gegenereerd.** De kermiskalender: hub, provincies, gemeenten, kermissen |
| `tools/kermis/` | De data en de generator achter `/kermis/` |
| `styles.css` | Alle stijl van de site, één bestand |
| `tracking.js` | Interactietracking naar de dataLayer — zie `DATALAYER.md` |

## De kermiskalender

Alles onder `/kermis/` is gegenereerd uit `tools/kermis/kermissen.csv` en
`tools/kermis/paginaspec.md`. **Bewerk die pagina's niet met de hand** — bij de
volgende build is je wijziging weg. Hoe je hem opnieuw bouwt, staat in
`tools/kermis/README.md`.

## Meten

Google Tag Manager (`GTM-NKS4M9KK`). De site duwt gebeurtenissen in de
dataLayer; wat ermee gebeurt regel je in GTM, niet in de code. Alle namen staan
in `DATALAYER.md`.
