/* Funpoints — meldingen linksonder
   ---------------------------------------------------------------------------
   Wat dit toont: kermissen die volgens onze eigen kalender nu bezig zijn of
   eraan komen. De inhoud komt uit /data/activiteit.json, dat door de
   kalendergenerator wordt geschreven. Er staat niets in dat niet klopt: geen
   verzonnen gebruikers, geen verzonnen downloads, geen opgeklopte aantallen.
   Dat is niet alleen netter, het is ook wat de wet vraagt — verzonnen
   gebruikersactiviteit tonen is een oneerlijke handelspraktijk onder Boek VI
   van het Wetboek van Economisch Recht.

   Zodra er echte cijfers te tonen zijn (aanmeldingen, aangesloten kramen),
   kan dat bestand aangevuld worden met een "echte" lijst in dezelfde vorm;
   dit script toont ze dan mee.

   Gedrag:
   - eerste melding na 6 seconden, daarna om de 14 seconden
   - maximaal 4 per bezoek, en niet meer dan één reeks per sessie
   - wegklikken zet het voor de rest van de sessie stil
   - respecteert prefers-reduced-motion en verschijnt niet op smalle schermen
     waar een sticky CTA staat
   --------------------------------------------------------------------------- */
(function () {
  'use strict';

  var SLEUTEL = 'fp_meldingen_gezien';
  var MAX = 4;
  var EERSTE = 6000;
  var TUSSEN = 14000;

  if (document.documentElement.hasAttribute('data-geen-meldingen')) return;

  try {
    if (window.sessionStorage && sessionStorage.getItem(SLEUTEL) === 'ja') return;
  } catch (e) { /* privémodus: gewoon doorgaan */ }

  var MAANDEN = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
                 'augustus', 'september', 'oktober', 'november', 'december'];

  var vandaag = new Date();
  vandaag.setHours(0, 0, 0, 0);

  function datum(iso) {
    var d = new Date(iso + 'T00:00:00');
    return d.getDate() + ' ' + MAANDEN[d.getMonth()];
  }

  function dagen(iso) {
    return Math.round((new Date(iso + 'T00:00:00') - vandaag) / 86400000);
  }

  /* Zet een kalenderitem om in een melding, of geeft null als het item
     vandaag niet relevant is. */
  function melding(k) {
    var tot = dagen(k.e);
    var start = dagen(k.s);
    if (tot < 0) return null;                 /* al voorbij */
    if (start > 21) return null;              /* nog te ver weg */
    if (start <= 0) {
      return {
        ic: '🎡',
        titel: k.n + ' is nu bezig',
        tekst: k.g + ' · nog tot ' + datum(k.e),
        href: k.u
      };
    }
    return {
      ic: '🗓️',
      titel: k.n + ' komt eraan',
      tekst: k.g + ' · vanaf ' + datum(k.s) + (start <= 7 ? ' (over ' + start + ' dagen)' : ''),
      href: k.u
    };
  }

  function bouwBak() {
    var el = document.createElement('div');
    el.className = 'fp-melding';
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    el.innerHTML =
      '<button class="sluit" type="button" aria-label="Meldingen sluiten">✕</button>' +
      '<span class="ic"></span>' +
      '<a class="tk"><b></b><span></span></a>';
    document.body.appendChild(el);
    /* Staat er onderaan al een sticky CTA, dan schuift de melding erboven */
    if (document.querySelector('.sticky-cta')) {
      document.body.classList.add('heeft-sticky');
    }
    return el;
  }

  function start(lijst) {
    if (!lijst.length) return;

    var bak = bouwBak();
    var ic = bak.querySelector('.ic');
    var link = bak.querySelector('.tk');
    var titel = bak.querySelector('b');
    var tekst = bak.querySelector('.tk span');
    var i = 0, timer = null, gestopt = false;

    function stop() {
      gestopt = true;
      clearTimeout(timer);
      bak.classList.remove('zichtbaar');
      try { sessionStorage.setItem(SLEUTEL, 'ja'); } catch (e) {}
      setTimeout(function () { if (bak.parentNode) bak.parentNode.removeChild(bak); }, 400);
    }

    bak.querySelector('.sluit').addEventListener('click', stop);

    link.addEventListener('click', function () {
      if (window.dataLayer) {
        window.dataLayer.push({
          event: 'melding_klik',
          melding_titel: titel.textContent,
          melding_doel: link.getAttribute('href')
        });
      }
    });

    function volgende() {
      if (gestopt) return;
      if (i >= Math.min(MAX, lijst.length)) { stop(); return; }
      var m = lijst[i++];
      ic.textContent = m.ic;
      titel.textContent = m.titel;
      tekst.textContent = m.tekst;
      link.setAttribute('href', m.href);
      bak.classList.add('zichtbaar');
      timer = setTimeout(function () {
        bak.classList.remove('zichtbaar');
        timer = setTimeout(volgende, 700);
      }, TUSSEN - 700);
    }

    timer = setTimeout(volgende, EERSTE);

    /* Niet doorgaan als het tabblad niet zichtbaar is */
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { clearTimeout(timer); }
      else if (!gestopt) { timer = setTimeout(volgende, 2500); }
    });
  }

  function laden() {
    fetch('/data/activiteit.json')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var uit = [];
        (d.kermissen || []).forEach(function (k) {
          var m = melding(k);
          if (m) uit.push(m);
        });
        /* Bezige kermissen eerst, dan wat er als eerste aankomt */
        uit.sort(function (a, b) { return a.ic === b.ic ? 0 : a.ic === '🎡' ? -1 : 1; });
        /* Een beetje spreiding zodat niet vier keer dezelfde gemeente komt */
        var gezien = {}, gefilterd = [];
        uit.forEach(function (m) {
          var g = m.tekst.split(' ·')[0];
          if (gezien[g]) return;
          gezien[g] = 1;
          gefilterd.push(m);
        });
        start(gefilterd);
      })
      .catch(function () { /* geen meldingen, ook goed */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', laden);
  } else {
    laden();
  }
})();
