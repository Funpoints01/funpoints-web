/* Funpoints — interactietracking voor Google Tag Manager.
   Duwt gebeurtenissen in de dataLayer; GTM beslist wat ermee gebeurt.
   Alle namen staan gedocumenteerd in DATALAYER.md. */
(function () {
  'use strict';

  var dataLayer = (window.dataLayer = window.dataLayer || []);
  function push(obj) { dataLayer.push(obj); }

  /* Kaartlinks bevatten titel + omschrijving; neem dan alleen de titel. */
  function tekstVan(el) {
    var titel = el.querySelector ? el.querySelector('.t, b') : null;
    return ((titel || el).textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80);
  }

  /* Waar op de pagina is geklikt? Bepaalt de waarde van klik_positie. */
  function positieVan(el) {
    if (el.closest('.app-knop'))   return 'app-knop';
    if (el.closest('.btn-store'))   return 'downloadblok';
    if (el.closest('.sticky-cta'))  return 'mobiele-balk';
    if (el.closest('.subnav'))      return 'subnavigatie';
    if (el.closest('header'))       return 'hoofdnavigatie';
    if (el.closest('footer'))       return 'footer';
    if (el.closest('.cta'))         return 'cta-blok';
    if (el.closest('.formcard'))    return 'formulier';
    if (el.closest('.toc'))         return 'inhoudsopgave';
    if (el.closest('.related'))     return 'verder-lezen';
    if (el.closest('.jump'))        return 'doorsteek';
    if (el.closest('.lp-hero') || el.closest('.hero') || el.closest('.page-hero')) return 'hero';
    if (el.closest('.usp'))         return 'usp-kaart';
    if (el.closest('.card'))        return 'kaart';
    if (el.closest('.article'))     return 'artikeltekst';
    return 'overig';
  }

  /* app.funpoints.be telt als extern: andere hostnaam. */
  function isExtern(href) {
    try { return new URL(href, location.href).hostname !== location.hostname; }
    catch (e) { return false; }
  }

  /* ---------------------------------------------------------- klikken */
  document.addEventListener('click', function (e) {
    var link = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!link) return;

    var href = link.getAttribute('href') || '';
    var tekst = tekstVan(link);
    var positie = positieVan(link);

    if (href.indexOf('mailto:') === 0) {
      push({ event: 'mail_klik', klik_tekst: tekst, klik_positie: positie, mail_adres: href.slice(7) });
      return;
    }
    if (href.indexOf('tel:') === 0) {
      push({ event: 'telefoon_klik', klik_tekst: tekst, klik_positie: positie });
      return;
    }
    if (positie === 'subnavigatie') {
      push({ event: 'doelgroep_gekozen', doelgroep: tekst, klik_bestemming: href });
      return;
    }
    if (isExtern(href)) {
      push({ event: 'uitgaande_klik', klik_tekst: tekst, klik_positie: positie, klik_bestemming: href });
      return;
    }
    if (positie === 'inhoudsopgave') {
      push({ event: 'inhoudsopgave_klik', klik_tekst: tekst });
      return;
    }

    var isCta = link.classList.contains('btn') || link.classList.contains('more') ||
                positie === 'doorsteek' || positie === 'verder-lezen' ||
                positie === 'cta-blok' || positie === 'mobiele-balk';
    if (isCta) {
      push({ event: 'cta_klik', cta_tekst: tekst, cta_positie: positie, cta_bestemming: href });
    }
  }, true);

  /* ------------------------------------------------------ mobiel menu */
  var menuknop = document.getElementById('navtoggle');
  if (menuknop) {
    menuknop.addEventListener('change', function () {
      if (menuknop.checked) push({ event: 'menu_geopend' });
    });
  }

  /* --------------------------------------------------- demoformulier */
  var formulier = document.getElementById('demo-form');
  if (!formulier) return;
  var naam = 'demo-landingspagina';

  /* Eerste tik in een veld = start van de aanvraag (funnelstap 1). */
  var gestart = false;
  ['input', 'change'].forEach(function (type) {
    formulier.addEventListener(type, function () {
      if (gestart) return;
      gestart = true;
      push({ event: 'formulier_gestart', formulier: naam });
    }, true);
  });

  /* Poging tot versturen (funnelstap 2). Bewust op de knop en niet op het
     submit-event: als de browservalidatie het tegenhoudt, komt er nooit een
     submit — en juist die pogingen wil je kunnen tellen. */
  var verstuurknop = formulier.querySelector('[data-fs-submit-btn]');
  if (verstuurknop) {
    verstuurknop.addEventListener('click', function () {
      push({ event: 'formulier_verstuurpoging', formulier: naam });
    });
  }

  /* Blokkerende browservalidatie: welk veld hield het tegen? */
  formulier.addEventListener('invalid', function (e) {
    push({
      event: 'formulier_fout', formulier: naam,
      fout_type: 'browservalidatie',
      fout_veld: (e.target && (e.target.name || e.target.id)) || 'onbekend'
    });
  }, true);

  /* Foutmelding die door Formspree wordt teruggestuurd. */
  if (window.MutationObserver) {
    formulier.querySelectorAll('[data-fs-error]').forEach(function (vak) {
      new MutationObserver(function () {
        var melding = vak.textContent.trim();
        if (!melding) return;
        push({
          event: 'formulier_fout', formulier: naam,
          fout_type: 'server',
          fout_veld: vak.getAttribute('data-fs-error') || 'formulier',
          fout_melding: melding.slice(0, 120)
        });
      }).observe(vak, { childList: true, subtree: true, characterData: true });
    });
  }
})();
