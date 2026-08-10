/* Filtert de gemeentelijst op een provinciepagina. Alles staat al in de
   HTML — dit verbergt enkel wat niet past, zodat de pagina zonder JavaScript
   volledig blijft werken en zoekmachines alle links zien. */
(function () {
  'use strict';
  var veld = document.getElementById('gem-filter');
  var lijst = document.getElementById('gemeentelijst');
  if (!veld || !lijst) return;
  var leeg = document.querySelector('.gem-leeg');
  var items = Array.prototype.slice.call(lijst.querySelectorAll('a'));
  var namen = items.map(function (a) {
    return a.textContent.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  });

  veld.addEventListener('input', function () {
    var q = veld.value.trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    var raak = 0;
    for (var i = 0; i < items.length; i++) {
      var toon = !q || namen[i].indexOf(q) !== -1;
      items[i].hidden = !toon;
      if (toon) raak++;
    }
    if (leeg) leeg.hidden = raak !== 0;
  });
})();
