# Auto Servis Šunja — autosunja.sitey.my

Public website for **Auto Servis Šunja**, Hajra Lakovića 38, 73000 Goražde.
Phone **061 297 847** · Mon–Sat 10:00–18:00, Sunday closed · Peugeot specialist.
Instagram: [@sunja_servis_peugeot](https://www.instagram.com/sunja_servis_peugeot/)

## v5 (2026-11-09) — built on the real CarServ template

The site is built directly on the free **CarServ** car-repair template by
[HTML Codex](https://htmlcodex.com/car-repair-html-template) (Bootstrap 5),
downloaded and adapted — not a hand-made imitation:

- Template palette recolored to Šunja blue (`--primary: #0B5FA5`), white + clean
- Real template parts: topbar, sticky navbar, hero carousel, about, tabbed
  services, contact with Google Map, dark footer
- Custom additions: live open/closed status pill (Europe/Sarajevo), today
  highlight in the hours list, gallery with the shop's OWN Instagram photos,
  Google review block, SMS booking form (composes an `sms:` message to the
  shop number — no backend), mobile Pozovi/Upute call bar
- All photos are the shop's own (Peugeot photo + official Instagram photos);
  the template's stock/demo images were replaced everywhere
- License: CarServ is CC BY 4.0 — the "Designed By HTML Codex" credit in the
  footer must stay (see the template's LICENSE terms)

Structure: `index.html`, `css/`, `js/`, `lib/` (template),
`img/` (crops of the shop's photos), `assets/` (logos + gallery originals).

## Earlier versions
- v4 (2026-11-08): hand-coded page *following* CarServ's structure — rejected
  by the owner as not professional enough, superseded by v5.
- v3 dark/3D and v2 plain light: rejected, removed.

## v6 (2026-11-10) — animations, globe map, TikTok photos + randomizer
- Loading screen: the Šunja logo DRAWS ITSELF (SVG stroke animation of the swoosh, engine square, gear, arrow, wordmark), then the real logo fades in and the screen lifts (~2.5s).
- Ken-burns zoom on hero slides + a blue scrolling services marquee under the hero.
- Photos: 12 real workshop photos pulled from the shop's TikTok @autoservissunja (assets/photos/tt-*.webp + wide crops). Service images now match their service (DiagBox screen = dijagnostika, ECU board = autoelektrika, valve train = veliki servis, engine bay = mali servis).
- Randomizer: photos.json pools — hero slide 1 picks 1 of 5 photos per visit; the gallery shows 5 random of 14 photos per visit (each links to its TikTok/Instagram post). NOTE: the first verifier "hero doesn't randomize" report was a measurement artifact (it read the static ALT text); src-level checks confirm all 5 hero images rotate.
- Custom map: Leaflet/OpenStreetMap scroll experience (replaces the Google iframe) — a 320vh pinned section zooms Svijet → Evropa → Bosna i Hercegovina → Goražde → the shop (exact pin 43.6651456, 18.982064 from Google Maps) ending with a marker + bubble (address, directions link, phone). Kontakt now has a navy info card with an "Upute za vožnju" button.
- Gallery's bottom card is now a black TikTok follow card (Instagram demoted per owner's order).
