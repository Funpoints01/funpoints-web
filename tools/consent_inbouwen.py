#!/usr/bin/env python3
"""
Bouwt het Consent Mode v2-blok, het bannerscript en de footerlink in de
handgeschreven pagina's in. Idempotent: al aangepaste pagina's slaat hij over.

Draaien vanuit de repo-root:  python3 tools/consent_inbouwen.py .
"""
import re, sys, glob, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else '.'

VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'

CONSENT = '''
<!-- Google Consent Mode v2 — standaard alles geweigerd, zoals de EER vereist.
     Dit blok moet vóór het bannerscript en vóór GTM staan. -->
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent', 'default', {
  ad_storage: 'denied',
  ad_user_data: 'denied',
  ad_personalization: 'denied',
  analytics_storage: 'denied',
  personalization_storage: 'denied',
  functionality_storage: 'granted',
  security_storage: 'granted',
  wait_for_update: 500
});
gtag('set', 'ads_data_redaction', true);
gtag('set', 'url_passthrough', true);
</script>
<!-- Cookiebanner. Bewust synchroon: een opgeslagen keuze moet doorgegeven zijn
     vóór GTM zijn eerste tag afvuurt. Geen async, geen defer. -->
<script src="/js/funpoints-consent.js"></script>'''

PRIVACY = '      <a href="/privacy.html">Privacybeleid</a>'
COOKIELINK = '      <a href="#cookievoorkeuren" data-fpc-open>Cookievoorkeuren</a>'


def verwerk(pad):
    s = open(pad, encoding='utf-8').read()
    origineel = s

    if 'funpoints-consent.js' not in s:
        if VIEWPORT not in s:
            return 'geen viewport-tag'
        s = s.replace(VIEWPORT, VIEWPORT + CONSENT, 1)

    if 'data-fpc-open' not in s and PRIVACY in s:
        s = s.replace(PRIVACY, PRIVACY + '\n' + COOKIELINK, 1)

    if s == origineel:
        return 'ongewijzigd'
    open(pad, 'w', encoding='utf-8').write(s)
    return 'aangepast'


if __name__ == '__main__':
    bestanden = [p for p in glob.glob(os.path.join(WORTEL, '**/*.html'), recursive=True)
                 if os.sep + 'kermis' + os.sep not in p]
    telling = {}
    for p in sorted(bestanden):
        r = verwerk(p)
        telling[r] = telling.get(r, 0) + 1
        print(f'{r:12} {os.path.relpath(p, WORTEL)}')
    print()
    for k, v in telling.items():
        print(f'{k}: {v}')
