/* Funpoints — de schermopname in de hero
   ---------------------------------------------------------------------------
   Waarom dit scriptje bestaat: de video staat bovenaan de pagina, en daar
   telt elke kilobyte. Zou de <video> gewoon een src hebben, dan begint de
   browser hem meteen te downloaden en concurreert hij met het lettertype, de
   stylesheet en de afbeelding waar Google de laadtijd op meet.

   Daarom: in de HTML staat alleen een poster (35 kB webp). Pas nadat de
   pagina volledig geladen is, en pas als de browser toch niets te doen heeft,
   hangen we de bron eronder en starten we het afspelen. De bezoeker ziet
   meteen een stilstaand beeld en een seconde later begint het te bewegen.

   Verder:
   - staat de video niet in beeld, dan pauzeert hij (scheelt batterij)
   - wie in zijn systeem "minder beweging" heeft staan, krijgt enkel de poster
   - op een trage of gelimiteerde verbinding laden we hem niet
   --------------------------------------------------------------------------- */
(function () {
  'use strict';

  var videos = document.querySelectorAll('video[data-src]');
  if (!videos.length) return;

  /* Respecteer de systeeminstelling voor minder beweging */
  var rustig = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (rustig) return;

  /* Databesparing of een trage verbinding? Dan blijft het bij de poster. */
  var net = navigator.connection;
  if (net && (net.saveData === true || /^([23]g|slow-2g)$/.test(net.effectiveType || ''))) return;

  function laad(video) {
    if (video.dataset.geladen) return;
    video.dataset.geladen = '1';
    /* mp4 eerst: dat bestand is het kleinst en werkt op iOS, Safari, Chrome en
       Edge. De webm staat erachter voor browsers zonder H.264 (sommige Linux-
       builds van Chromium en Firefox). De browser haalt er maar één op. */
    [['data-src', 'video/mp4'], ['data-src-webm', 'video/webm']].forEach(function (paar) {
      var url = video.getAttribute(paar[0]);
      if (!url) return;
      var bron = document.createElement('source');
      bron.src = url;
      bron.type = paar[1];
      video.appendChild(bron);
    });
    video.load();
    var poging = video.play();
    if (poging && poging.catch) { poging.catch(function () { /* browser wil niet: poster blijft */ }); }
  }

  /* Pauzeren zodra hij uit beeld scrolt, weer starten als hij terugkomt. */
  function volg(video) {
    if (!('IntersectionObserver' in window)) return;
    new IntersectionObserver(function (rijen) {
      rijen.forEach(function (r) {
        if (r.isIntersecting) {
          if (video.dataset.geladen) { var p = video.play(); if (p && p.catch) p.catch(function () {}); }
        } else if (!video.paused) {
          video.pause();
        }
      });
    }, { threshold: 0.15 }).observe(video);
  }

  function start() {
    var doen = function () {
      Array.prototype.forEach.call(videos, function (v) { laad(v); volg(v); });
    };
    if ('requestIdleCallback' in window) {
      requestIdleCallback(doen, { timeout: 2500 });
    } else {
      setTimeout(doen, 900);
    }
  }

  if (document.readyState === 'complete') start();
  else window.addEventListener('load', start);
})();
