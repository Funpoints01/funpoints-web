# Klaarstaande blokken: reviews en cases

Twee dingen die je op de site wil — **wat uitbaters ervan vinden** en **welke
gemeenten meekijken** — kan ik niet zelf schrijven. Als er een quote van
"familie Baetens" op de site komt te staan die ik verzonnen heb, dan is dat een
misleidende handelspraktijk (Boek VI WER, art. VI.100). Voor een `Review` in
schema.org geldt hetzelfde: Google verwijdert rich results waarvan de
onderliggende review niet echt is, en dat kost je meer dan het opbrengt.

Daarom staan de blokken hier volledig uitgewerkt klaar. Zodra je de echte
teksten hebt, vul je ze in en plak je ze in de pagina. De opmaak, de responsive
CSS en de schema-koppeling zijn al gedaan.

## reviews.html

Voor `uitbaters.html`, tussen het prijzenblok en de FAQ.

Wat ik nodig heb per review:

| Veld | Voorbeeld | Verplicht |
|---|---|---|
| naam | Viskraam Baetens | ja |
| plaats of route | Oost-Vlaanderen | nee |
| quote | letterlijk, zoals gezegd | ja |
| sinds wanneer klant | mei 2026 | nee |
| foto van het kraam | jpg, minstens 800px breed | nee |
| akkoord om te publiceren | schriftelijk (mail volstaat) | **ja** |

Dat laatste is geen formaliteit: zonder toestemming mag je een bedrijfsnaam niet
in een aanbeveling zetten.

De `Review`-schema staat in het bestand mee, uitgecommentarieerd. Zet die pas
aan wanneer er minstens twee echte reviews staan — één review met een
`aggregateRating` van 5,0 leest als opgeklopt.

## cases.html

Voor `over-ons.html` of een nieuwe pagina `/gemeenten/`.

Er is een verschil dat je hier scherp moet houden:

- **"Gemeente X werkt met Funpoints"** — mag pas als het klopt en de gemeente
  akkoord is.
- **"Gemeente X heeft interesse getoond"** — mag je niet publiceren zonder hun
  toestemming, ook al is het waar. Een gesprek is nog geen goedkeuring, en een
  schepen die zijn gemeente onaangekondigd in een klantenlijst ziet staan, is
  meestal de laatste keer dat hij terugbelt.

Wat wél kan zonder iemands akkoord, en wat in `cases.html` als derde variant
klaarstaat: **het aanbod zelf** beschrijven — wat een gemeente of foorcommissie
aan Funpoints heeft (bezoekersaantallen zien, de kalender vullen, de kermis
zichtbaar maken) met een uitnodiging om contact op te nemen. Dat is de eerlijke
versie van "cases" zolang er nog geen cases zijn, en ze doet hetzelfde werk:
tonen dat je met gemeenten bezig bent.

## Invullen en plaatsen

1. Vervang alles tussen `{{ }}` door de echte tekst.
2. Verwijder de blokken die je niet gebruikt.
3. Plak het geheel op de aangegeven plek in de pagina.
4. Draai daarna `python3 tools/partials.py` om te controleren dat header en
   footer nog kloppen.
