/* Zoeken in de kermiskalender zonder server: de lijst van gemeenten staat
   in /kermis/gemeenten.json (± 20 kB) en wordt pas opgehaald zodra iemand het
   zoekveld gebruikt. Zo kost de zoekfunctie niets voor wie ze niet nodig heeft. */
(function () {
  'use strict';
  var veld = document.getElementById('kal-q');
  var bak = document.getElementById('kal-treffers');
  if (!veld || !bak) return;

  var lijst = null, bezig = false, wacht = null;

  function plat(t) {
    return t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function laden(daarna) {
    if (lijst) { daarna(); return; }
    if (bezig) return;
    bezig = true;
    fetch('/kermis/gemeenten.json')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        lijst = d.map(function (g) { return { n: g[0], s: g[1], p: g[2], a: g[3], z: plat(g[0]) }; });
        bezig = false;
        daarna();
      })
      .catch(function () { bezig = false; });
  }

  function toon() {
    var q = plat(veld.value.trim());
    if (q.length < 2) { sluit(); return; }
    laden(function () {
      if (!lijst) return;
      var begint = [], bevat = [];
      for (var i = 0; i < lijst.length && begint.length + bevat.length < 40; i++) {
        var g = lijst[i];
        if (g.z.indexOf(q) === 0) begint.push(g);
        else if (g.z.indexOf(q) > 0) bevat.push(g);
      }
      var res = begint.concat(bevat).slice(0, 8);
      if (!res.length) {
        bak.innerHTML = '<p class="leeg">Geen gemeente gevonden. Staat de jouwe er niet bij? Mail ' +
          '<a href="mailto:info@funpoints.be">info@funpoints.be</a>.</p>';
      } else {
        bak.innerHTML = res.map(function (g) {
          var woord = g.a === 1 ? 'kermis' : 'kermissen';
          return '<a role="option" href="/kermis/' + g.s + '/">' +
                 '<b>Kermis in ' + g.n + '</b>' +
                 '<span>' + g.a + ' ' + woord + ' \u00b7 ' + g.p + '</span></a>';
        }).join('');
      }
      bak.classList.add('open');
      veld.setAttribute('aria-expanded', 'true');
    });
  }

  function sluit() {
    bak.classList.remove('open');
    veld.setAttribute('aria-expanded', 'false');
  }

  veld.addEventListener('input', function () {
    clearTimeout(wacht);
    wacht = setTimeout(toon, 90);
  });
  veld.addEventListener('focus', function () { if (veld.value.trim().length > 1) toon(); });
  veld.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') { sluit(); return; }
    if (ev.key === 'ArrowDown') {
      var eerste = bak.querySelector('a');
      if (eerste) { ev.preventDefault(); eerste.focus(); }
    }
    if (ev.key === 'Enter') {
      var t = bak.querySelector('a');
      if (t) { ev.preventDefault(); window.location.href = t.getAttribute('href'); }
    }
  });
  bak.addEventListener('keydown', function (ev) {
    var items = Array.prototype.slice.call(bak.querySelectorAll('a'));
    var i = items.indexOf(document.activeElement);
    if (ev.key === 'ArrowDown' && i < items.length - 1) { ev.preventDefault(); items[i + 1].focus(); }
    if (ev.key === 'ArrowUp') { ev.preventDefault(); (i > 0 ? items[i - 1] : veld).focus(); }
    if (ev.key === 'Escape') { sluit(); veld.focus(); }
  });
  document.addEventListener('click', function (ev) {
    if (!bak.contains(ev.target) && ev.target !== veld) sluit();
  });
})();
