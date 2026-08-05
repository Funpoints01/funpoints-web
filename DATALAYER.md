# dataLayer — naslagwerk voor Google Tag Manager

Container: `GTM-NKS4M9KK`

Deze site duwt alle meetgegevens in de `dataLayer`. GTM beslist wat ermee
gebeurt — in de code staan geen GA4- of Ads-tags. Wil je iets anders meten,
dan pas je GTM aan en niet de website.

De code staat op twee plekken: de paginacontext in de `<head>` van elke pagina
(bewust vóór de GTM-snippet, zodat hij al klaarstaat bij de eerste tag), en de
interacties in `/tracking.js`, dat op elke pagina wordt ingeladen.

---

## 1. Paginacontext

Staat op élke pagina klaar voordat GTM laadt. Bruikbaar in tags die op
"Alle pagina's" vuren.

| Variabele | Betekenis | Mogelijke waarden |
|---|---|---|
| `page_type` | Soort pagina | `home`, `landingspagina`, `doelgroep`, `product`, `hub`, `artikel`, `info` |
| `page_category` | Onderdeel van de site | `product`, `conversie`, `kermis`, `kennisbank`, `magazine`, `bedrijf` |
| `page_audience` | Voor wie de pagina bedoeld is | `b2c`, `b2b`, `beide` |
| `page_name` | Leesbare naam van de pagina | vrije tekst |
| `page_language` | Taal | `nl-BE` |

Maak hiervan in GTM vijf variabelen van het type **Gegevenslaagvariabele**
met exact deze namen. Daarmee kan je bijvoorbeeld alle B2B-pagina's apart
rapporteren (`page_audience` is `b2b`), of alle artikelen (`page_type` is
`artikel`).

### Per pagina

| URL | page_type | page_category | page_audience |
|---|---|---|---|
| `/` | home | product | beide |
| `/demo/` | landingspagina | conversie | b2b |
| `/bezoekers.html` | doelgroep | product | b2c |
| `/foorkramers.html` | doelgroep | product | b2b |
| `/uitbaters.html` | doelgroep | product | b2b |
| `/hoe-het-werkt.html` | product | product | beide |
| `/kermis/` | hub | kermis | b2c |
| `/kennisbank/` | hub | kennisbank | b2b |
| `/kennisbank/*` (artikelen) | artikel | kennisbank | b2b |
| `/magazine/` | hub | magazine | b2c |
| `/magazine/*` (artikelen) | artikel | magazine | b2c |
| `/over-ons.html` | info | bedrijf | beide |

---

## 2. Gebeurtenissen

Maak in GTM per gebeurtenis een trigger van het type **Aangepaste
gebeurtenis** met exact de naam uit de eerste kolom.

### De conversie

| Gebeurtenis | Wanneer | Meegestuurd |
|---|---|---|
| `demo_aanvraag` | Demo-aanvraag geslaagd verstuurd | `formulier` |

**Dit is de enige echte conversie op de site.** Hang hier je Google
Ads-conversie en je GA4-conversie aan. Wil je GA4's ingebouwde
lead-rapportage gebruiken, noem de GA4-gebeurtenis in je tag dan
`generate_lead` — de naam in de dataLayer hoeft niet gelijk te zijn.

### De trechter ernaartoe

| Gebeurtenis | Wanneer | Meegestuurd |
|---|---|---|
| `formulier_gestart` | Eerste tik in een veld van het demoformulier | `formulier` |
| `formulier_verstuurpoging` | Klik op "Demo aanvragen", ook als validatie het tegenhoudt | `formulier` |
| `formulier_fout` | Een veld wordt afgekeurd | `formulier`, `fout_type`, `fout_veld`, `fout_melding` |

`fout_type` is `browservalidatie` (leeg of ongeldig veld) of `server`
(afgekeurd door Formspree). Zo zie je waar mensen vastlopen: veel
`formulier_gestart` met weinig `demo_aanvraag` betekent dat het formulier
zelf het probleem is, niet je advertenties.

### Navigatie en interesse

| Gebeurtenis | Wanneer | Meegestuurd |
|---|---|---|
| `cta_klik` | Klik op een knop, kaartlink of "verder lezen" | `cta_tekst`, `cta_positie`, `cta_bestemming` |
| `doelgroep_gekozen` | Klik in de doelgroepbalk bovenaan | `doelgroep`, `klik_bestemming` |
| `uitgaande_klik` | Klik naar een ander domein, o.a. `app.funpoints.be` | `klik_tekst`, `klik_positie`, `klik_bestemming` |
| `mail_klik` | Klik op een e-mailadres | `klik_tekst`, `klik_positie`, `mail_adres` |
| `telefoon_klik` | Klik op een telefoonnummer | `klik_tekst`, `klik_positie` |
| `inhoudsopgave_klik` | Klik in de inhoudsopgave van een artikel | `klik_tekst` |
| `menu_geopend` | Het mobiele menu wordt opengeklapt | — |

`cta_positie` en `klik_positie` vertellen wáár op de pagina geklikt is:
`hero`, `cta-blok`, `mobiele-balk`, `doorsteek`, `verder-lezen`,
`inhoudsopgave`, `usp-kaart`, `kaart`, `artikeltekst`, `hoofdnavigatie`,
`subnavigatie`, `footer`, `formulier`, `overig`.

Daarmee kan je zien welke knop de aanvragen oplevert. Staat bijvoorbeeld
`cta_positie` = `mobiele-balk` bovenaan, dan weet je dat de vaste knop
onderaan het scherm zijn werk doet.

---

## 3. Wat je niet in de code hoeft te zetten

GTM heeft hier ingebouwde triggers voor — gebruik die in plaats van extra code:

- **Scrolldiepte** — trigger *Scroll-diepte*, bijvoorbeeld op 25/50/75/90%.
  Interessant op de artikelen (`page_type` is `artikel`).
- **Tijd op pagina** — trigger *Timer*.
- **Zichtbaarheid van een element** — trigger *Elementzichtbaarheid*,
  bijvoorbeeld op `#demo-form` om te meten hoeveel mensen het formulier
  überhaupt in beeld krijgen.

---

## 4. Nog te regelen: toestemming

Er staat **geen cookiebanner** op de site en Google Consent Mode is niet
ingesteld. Voor een Belgische site met Google Analytics of Google Ads is dat
een openstaand punt: zonder toestemming mag je in principe geen
analytische of advertentiecookies plaatsen.

Twee wegen:

1. Een cookiebanner koppelen (Cookiebot, Iubenda, Axeptio, CookieYes) en die
   in GTM aansluiten op Consent Mode v2. De meeste hebben een kant-en-klare
   GTM-sjabloon.
2. Een analysepakket zonder cookies gebruiken (Plausible, Fathom, Simple
   Analytics), waarvoor in veel gevallen geen banner nodig is.

Ik heb Consent Mode bewust niet vast ingesteld: zonder banner die
toestemming kán geven, zou alles op "geweigerd" blijven staan en meet je
niets meer. Dit is een keuze die jullie eerst moeten maken.

Ook `/privacy.html` bestaat nog niet, terwijl er in de footer en onder het
demoformulier naar verwezen wordt. Dat is nodig zodra je persoonsgegevens
verzamelt via het formulier.

---

## 5. Snel testen

1. Open GTM → **Voorbeeld** (Preview) en vul `https://funpoints.be` in.
2. Klik op een pagina rond: in het paneel links zie je de gebeurtenissen
   binnenkomen.
3. Klik op een gebeurtenis en open het tabblad **Data Layer** om de
   meegestuurde waarden te controleren.
4. Vul het demoformulier in met een testaanvraag en kijk of
   `formulier_gestart`, `formulier_verstuurpoging` en `demo_aanvraag`
   na elkaar verschijnen.
