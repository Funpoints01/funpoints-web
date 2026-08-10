/*! Funpoints — cookiebanner + Google Consent Mode v2
 *  Plaats dit bestand op /js/funpoints-consent.js
 *  Laden: SYNCHROON in <head>, ná het consent-default-blok en VÓÓR de GTM-snippet.
 *  Geen externe afhankelijkheden, geen cookies vóór toestemming.
 */
(function () {
  "use strict";

  var COOKIE = "fp_consent";
  var VERSIE = 1;                 // verhoog dit als je de categorieën wijzigt → banner komt opnieuw
  var BEWAARTERMIJN = 180;        // dagen (max. 6 maanden, conform GBA-richtlijn)

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  /* ── opslag ─────────────────────────────────────────── */
  function lees() {
    var m = document.cookie.match(new RegExp("(?:^|; )" + COOKIE + "=([^;]*)"));
    if (!m) return null;
    try {
      var o = JSON.parse(decodeURIComponent(m[1]));
      return o && o.v === VERSIE ? o : null;
    } catch (e) { return null; }
  }
  function schrijf(o) {
    o.v = VERSIE;
    o.ts = new Date().toISOString();
    document.cookie = COOKIE + "=" + encodeURIComponent(JSON.stringify(o)) +
      ";path=/;max-age=" + (BEWAARTERMIJN * 86400) + ";SameSite=Lax" +
      (location.protocol === "https:" ? ";Secure" : "");
  }

  /* ── consent doorgeven aan Google + GTM ─────────────── */
  function toepassen(keuze, bron) {
    var stat = keuze.statistieken ? "granted" : "denied";
    var mark = keuze.marketing ? "granted" : "denied";
    gtag("consent", "update", {
      analytics_storage: stat,
      ad_storage: mark,
      ad_user_data: mark,
      ad_personalization: mark,
      personalization_storage: mark,
      functionality_storage: "granted",
      security_storage: "granted"
    });
    window.dataLayer.push({
      event: "fp_consent_update",
      consent_statistieken: keuze.statistieken ? "granted" : "denied",
      consent_marketing: keuze.marketing ? "granted" : "denied",
      consent_bron: bron || "banner"
    });
  }

  /* ── eerdere keuze meteen herstellen (vóór GTM vuurt) ── */
  var opgeslagen = lees();
  if (opgeslagen) toepassen(opgeslagen, "opgeslagen");

  /* ── stijl ──────────────────────────────────────────── */
  var CSS =
  '.fpc-overlay{position:fixed;inset:0;background:rgba(36,27,58,.45);z-index:9998;display:none}' +
  '.fpc-overlay.open{display:block}' +
  '.fpc{position:fixed;z-index:9999;left:16px;right:16px;bottom:16px;margin:0 auto;max-width:640px;' +
  'background:#FFF8F0;color:#241B3A;border:1px solid rgba(36,27,58,.12);border-radius:20px;' +
  'box-shadow:0 20px 50px rgba(36,27,58,.28);padding:24px;font-family:Poppins,system-ui,-apple-system,sans-serif;' +
  'font-size:15px;line-height:1.6;display:none}' +
  '.fpc.open{display:block}' +
  '.fpc h2{font-size:20px;font-weight:800;margin:0 0 8px;letter-spacing:-.01em}' +
  '.fpc p{margin:0 0 14px;color:#4A4258}' +
  '.fpc a{color:#E11D63;font-weight:700}' +
  '.fpc-knoppen{display:flex;gap:10px;flex-wrap:wrap}' +
  '.fpc-btn{flex:1 1 auto;min-width:150px;border:0;cursor:pointer;border-radius:999px;padding:13px 20px;' +
  'font:inherit;font-weight:800;font-size:15px}' +
  '.fpc-btn-ja{background:#10B981;color:#fff}' +
  '.fpc-btn-nee{background:#fff;color:#241B3A;border:2px solid rgba(36,27,58,.16)}' +
  '.fpc-btn-kies{background:none;color:#6f6885;text-decoration:underline;flex:0 0 auto;min-width:0;padding:13px 4px;font-weight:600}' +
  '.fpc-keuzes{display:none;margin:4px 0 16px;border-top:1px solid rgba(36,27,58,.1);padding-top:14px}' +
  '.fpc-keuzes.open{display:block}' +
  '.fpc-rij{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px solid rgba(36,27,58,.07)}' +
  '.fpc-rij:last-child{border-bottom:0}' +
  '.fpc-rij input{margin-top:4px;width:18px;height:18px;accent-color:#10B981;flex:0 0 auto}' +
  '.fpc-rij b{display:block;font-size:14.5px}' +
  '.fpc-rij span{font-size:13px;color:#6f6885}' +
  '.fpc-vast{font-size:12px;color:#6f6885;font-weight:700;white-space:nowrap;margin-top:3px}' +
  '.fpc :focus-visible{outline:3px solid #8B5CF6;outline-offset:2px}' +
  '@media(max-width:520px){.fpc{padding:20px 18px}.fpc-btn{flex:1 1 100%}}' +
  '@media(prefers-reduced-motion:no-preference){.fpc.open{animation:fpc-in .22s ease-out}' +
  '@keyframes fpc-in{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}}';

  /* ── markup ─────────────────────────────────────────── */
  var HTML =
  '<h2 id="fpc-titel">Cookies op Funpoints</h2>' +
  '<p id="fpc-tekst">We gebruiken cookies om de site te laten werken. Met jouw toestemming meten we ook hoe de site gebruikt wordt en tonen we relevante advertenties. Je keuze geldt zes maanden en je past ze altijd aan onderaan de pagina. Meer in ons <a href="/privacy.html">privacybeleid</a>.</p>' +
  '<div class="fpc-keuzes" id="fpc-keuzes">' +
    '<div class="fpc-rij"><span class="fpc-vast">Altijd aan</span><span><b>Noodzakelijk</b><span>Nodig om de site te tonen en je keuze te onthouden. Deze kan je niet uitzetten.</span></span></div>' +
    '<div class="fpc-rij"><input type="checkbox" id="fpc-stat"><label for="fpc-stat"><b>Statistieken</b><span>Meet anoniem welke pagina\'s bezocht worden, zodat we de site kunnen verbeteren.</span></label></div>' +
    '<div class="fpc-rij"><input type="checkbox" id="fpc-mark"><label for="fpc-mark"><b>Marketing</b><span>Meet of onze advertenties werken en toont je relevantere advertenties.</span></label></div>' +
  '</div>' +
  '<div class="fpc-knoppen">' +
    '<button type="button" class="fpc-btn fpc-btn-ja" id="fpc-ja">Alles aanvaarden</button>' +
    '<button type="button" class="fpc-btn fpc-btn-nee" id="fpc-nee">Alles weigeren</button>' +
    '<button type="button" class="fpc-btn fpc-btn-kies" id="fpc-kies" aria-expanded="false" aria-controls="fpc-keuzes">Zelf kiezen</button>' +
  '</div>';

  var banner, overlay, laatsteFocus;

  function bouw() {
    var st = document.createElement("style"); st.textContent = CSS;
    document.head.appendChild(st);

    overlay = document.createElement("div");
    overlay.className = "fpc-overlay";

    banner = document.createElement("div");
    banner.className = "fpc";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-modal", "true");
    banner.setAttribute("aria-labelledby", "fpc-titel");
    banner.setAttribute("aria-describedby", "fpc-tekst");
    banner.innerHTML = HTML;

    document.body.appendChild(overlay);
    document.body.appendChild(banner);

    document.getElementById("fpc-ja").addEventListener("click", function () {
      bewaarEnSluit({ statistieken: true, marketing: true });
    });
    document.getElementById("fpc-nee").addEventListener("click", function () {
      bewaarEnSluit({ statistieken: false, marketing: false });
    });
    document.getElementById("fpc-kies").addEventListener("click", function () {
      var vak = document.getElementById("fpc-keuzes");
      var open = vak.classList.toggle("open");
      this.setAttribute("aria-expanded", open ? "true" : "false");
      this.textContent = open ? "Mijn keuze bewaren" : "Zelf kiezen";
      if (!open) {
        bewaarEnSluit({
          statistieken: document.getElementById("fpc-stat").checked,
          marketing: document.getElementById("fpc-mark").checked
        });
      }
    });

    // Tab blijft binnen het venster zolang er geen keuze is.
    banner.addEventListener("keydown", function (e) {
      if (e.key !== "Tab") return;
      var f = banner.querySelectorAll("button, input, a[href]");
      if (!f.length) return;
      var eerste = f[0], laatste = f[f.length - 1];
      if (e.shiftKey && document.activeElement === eerste) { e.preventDefault(); laatste.focus(); }
      else if (!e.shiftKey && document.activeElement === laatste) { e.preventDefault(); eerste.focus(); }
    });
    // Bewust géén sluiten met Escape of klik naast het venster:
    // wegklikken mag niet als toestemming gelden.
  }

  function toon(bestaand) {
    if (!banner) bouw();
    document.getElementById("fpc-stat").checked = !!(bestaand && bestaand.statistieken);
    document.getElementById("fpc-mark").checked = !!(bestaand && bestaand.marketing);
    // Bij heropenen begint het keuzevak weer dicht, anders staat de knop nog
    // op "Mijn keuze bewaren" van de vorige keer.
    var vak = document.getElementById("fpc-keuzes");
    var kies = document.getElementById("fpc-kies");
    vak.classList.remove("open");
    kies.setAttribute("aria-expanded", "false");
    kies.textContent = "Zelf kiezen";
    laatsteFocus = document.activeElement;
    overlay.classList.add("open");
    banner.classList.add("open");
    document.getElementById("fpc-ja").focus();
  }

  function bewaarEnSluit(keuze) {
    schrijf(keuze);
    toepassen(keuze, "banner");
    overlay.classList.remove("open");
    banner.classList.remove("open");
    if (laatsteFocus && laatsteFocus.focus) laatsteFocus.focus();
  }

  /* ── publieke API: link "Cookievoorkeuren" in de footer ── */
  window.funpointsCookies = {
    open: function () { toon(lees()); },
    huidige: function () { return lees(); }
  };

  function start() {
    // Elk element met data-fpc-open of href="#cookievoorkeuren" heropent de banner.
    Array.prototype.forEach.call(
      document.querySelectorAll('[data-fpc-open], a[href="#cookievoorkeuren"]'),
      function (el) {
        el.addEventListener("click", function (e) { e.preventDefault(); toon(lees()); });
      });
    if (!lees()) toon(null);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
