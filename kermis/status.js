/* Houdt de kermisstatus actueel zonder server: de pagina wordt statisch
   gebouwd, dit scriptje herberekent "nog te komen / nu bezig / voorbij"
   in de browser aan de hand van data-start en data-eind. */
(function () {
  'use strict';
  var vandaag = new Date();
  vandaag.setHours(0, 0, 0, 0);

  function label(start, eind) {
    var s = new Date(start + 'T00:00:00');
    var t = new Date(eind + 'T00:00:00');
    if (vandaag < s) {
      var dagen = Math.round((s - vandaag) / 86400000);
      if (dagen === 0) return '\uD83C\uDF61 Start vandaag';
      if (dagen === 1) return '\uD83D\uDDD3\uFE0F Start morgen';
      if (dagen <= 14) return '\uD83D\uDDD3\uFE0F Over ' + dagen + ' dagen';
      return '\uD83D\uDDD3\uFE0F Nog te komen';
    }
    if (vandaag > t) return '\u2714\uFE0F Voorbij';
    return '\uD83C\uDFA1 Nu bezig';
  }

  /* Losse badge bovenaan een kermispagina */
  Array.prototype.forEach.call(
    document.querySelectorAll('.kermis-status[data-start]'), function (el) {
      el.textContent = label(el.getAttribute('data-start'), el.getAttribute('data-eind'));
    });

  /* Statuskolom in een oudere kalendertabel */
  Array.prototype.forEach.call(
    document.querySelectorAll('.kermis-rij[data-start]'), function (rij) {
      var badge = rij.querySelector('.kermis-status');
      if (badge) badge.textContent = label(rij.getAttribute('data-start'),
                                           rij.getAttribute('data-eind'));
    });

  /* Kalenderregels: pil bijwerken en de regel dimmen als ze voorbij is */
  Array.prototype.forEach.call(
    document.querySelectorAll('.kal-item[data-start]'), function (rij) {
      var start = rij.getAttribute('data-start');
      var eind = rij.getAttribute('data-eind');
      var s = new Date(start + 'T00:00:00');
      var t = new Date(eind + 'T00:00:00');
      var pil = rij.querySelector('.kal-pil');
      rij.classList.remove('nu', 'voorbij');
      if (pil) pil.classList.remove('nu', 'komt');
      if (vandaag > t) {
        rij.classList.add('voorbij');
        if (pil) pil.textContent = 'Voorbij';
      } else if (vandaag < s) {
        var dagen = Math.round((s - vandaag) / 86400000);
        if (pil) {
          pil.classList.add('komt');
          pil.textContent = dagen === 0 ? 'Start vandaag'
            : dagen === 1 ? 'Morgen'
            : dagen <= 14 ? 'Over ' + dagen + ' dagen'
            : 'Nog te komen';
        }
      } else {
        rij.classList.add('nu');
        if (pil) { pil.classList.add('nu'); pil.textContent = 'Nu bezig'; }
      }
    });
})();
