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

## v6.1–v6.2 (2026-11-10) — exact-logo preloader, counters, map speed
- Owner REJECTED the hand-drawn SVG preloader in caps: never approximate his logo. Preloader now animates THE EXACT logo image (sunja-logo-transparent.webp) via a mask wipe ("drawing" reveal) + glowing pen line + progress bar; zero sketch elements in the HTML (verified by grep + frame-by-frame browser check). Verifier initially still saw the sketch = stale Pages/browser cache of the v6 HTML (max-age 600) — verify preloaders via a cache-busted URL.
- Counters band with REAL numbers only: Google 4,6 / 33 recenzije / TikTok 959 pratilaca / 6 usluga, count-up on scroll. Plus: footer wave divider, button shine sweep, bigger section titles/spacing, glassy navbar.
- Map speed: CARTO basemaps now require an API key (watermark error tiles) — reverted to tile.openstreetmap.org with keepBuffer 6, quantized scroll renders, 250vh scroll length, and JS tile PREFETCH for z17/z16/z12/z8 around the shop/Goražde/BiH so later zoom stages render instantly (verified: final stage fully tiled on arrival).

## v7 (2026-11-10) — traced EXACT logo preloader + real 3D globe map
- Preloader v7: the logo animation is now TRACED FROM THE OWNER'S ORIGINAL LOGO FILE (OpenCV contour trace of sunja-logo-transparent.png, blue + dark layers, eps 1.8): the logo's own outlines draw themselves -> fills fade in -> crossfade to the exact logo image -> lift. Verified frame-by-frame in a real browser: PASS. (v6's hand-drawn SVG and v6.1's mask wipe were both rejected by the owner in caps — never approximate his logo, and a wipe of the image wasn't "drawing" enough either.)
- Map v7: Leaflet/OSM replaced by MapLibre GL v5 + OpenFreeMap 'liberty' vector tiles (free, no key) with GLOBE projection: pinned scroll flies Svijet (3D sphere) -> Evropa -> BiH -> Gorazde -> street level (pitch 50, 3D buildings) ending in the marker + bubble. GOTCHA: the first build silently never ran — the guard called maplibregl.supported(), which threw in this build and killed the whole IIFE before even the fallback could run (blank pale-blue map, pill stuck on 'Svijet', no error anywhere). Fix pattern (v7.1): no supported() call, try/catch around everything, safety fallback timer registered BEFORE map creation, map 'error' -> fallback with the REASON written into the page text for diagnosis. Verified working end-to-end after the rewrite.
- OpenFreeMap TileJSON maxzoom is 14; final camera zoom 15.5 overzooms vector tiles (fine).

## v8 (2026-11-10) — hero slider redesign + extras
- Slider rebuilt (still Bootstrap carousel underneath): tall full-bleed slides (86vh) with left dark gradient, frosted-glass kicker pill, big 800-weight headlines, caption elements fade-up in stagger on slide activation (.h-anim under .carousel-item.active), giant outlined ghost numbers 01/02/03, progress-bar indicators bottom-left (active bar fills over the 6s interval), round glass prev/next buttons bottom-right (old full-height arrows gone), bouncing scroll chevron bottom-center. Mobile rules: 74vh, ghost/chevron hidden, indicators/arrows raised above the fixed call bar. Verified on desktop (fill animation, clicking, auto-advance, wrap); mobile width could not be rendered by the checker browser — owner checks on his phone.
- OG/Twitter share tags added (link previews now show title + workshop photo).
- Kontakt card: WhatsApp button (wa.me/38761297847) next to Upute za vožnju.
- Preloader is FAST on repeat visits within a session (sessionStorage flag: ~1s instead of ~2.5s).
- Marquee pauses on hover; html smooth scrolling.
- NOTE: the first v8 push attempt pushed CSS but the index.html edit script died on a meta-tag anchor mismatch (attribute order) — pushes reported OK for an UNCHANGED index. Always grep the live HTML for the new markers after pushing (done on the retry: all present).
