# Auto Servis Šunja — autosunja.sitey.my

Public website for **Auto Servis Šunja**, Hajra Lakovića 38, 73000 Goražde.
Phone **061 297 847** · Mon–Sat 10:00–18:00, Sunday closed · Peugeot specialist.
Instagram: [@sunja_servis_peugeot](https://www.instagram.com/sunja_servis_peugeot/)

## v29.0 (2026-11-12) — map finishes once, no replay, faster scrolling

- Root cause: map camera progress was recalculated both forward and backward on every scroll frame, repeatedly removing the location marker and clearing `globe-complete` when visitors scrolled up. Added a permanent `mapCompleted` one-way lock for each page visit, removes the scroll listener on completion, keeps the shop marker and final camera permanently in place, and handles delayed map loads after a fast swipe past the section.
- Reduced `jumpTo` rate to one map camera update per 80 ms (rather than every scroll frame), with a trailing update to avoid getting stuck. Completion bypasses the throttle for immediate settling.
- Switched MapLibre assets to the pinned jsDelivr CDN, added DNS/TLS preconnect, and starts fetching the map earlier, around 850px before the section. Kept the official OpenFreeMap Liberty style, current coordinates, real globe mode, and zoom 16.2.
- Lowered map canvas pixel ratio slightly on high-density mobile screens, cancelled unnecessary old-zoom tile requests, and disabled duplicate world copies. Resizing now uses the element's actual ResizeObserver rather than repeatedly responding to Safari's browser toolbar changes.
- Shortened the stable sticky map run to 185svh on phones / 190svh on larger screens (without collapsing it on completion). Failed network maps still collapse into the working directions fallback.
- Added automated Chromium and WebKit tests that complete the map, scroll backward/forward again, assert no additional camera jumps or marker removal, and cover the case where the map loads after the visitor has already passed it.
- Asset cache versions updated to `v29.0`, no loading-screen animations or glass effects reintroduced.

## v28.0 (2026-11-12) — removed all loading screens

- Removed the full-screen logo video overlay, fallback reveal animation, playback timers, preload gate, and all intro-related CSS/JavaScript. The page now opens straight on the homepage slides, on normal entry and refresh.
- Preserved the non-glass design, navigation, mobile call/directions dock, scroll-driven map, services and gallery.
- CSS/JS links use `v28.0` to invalidate old iPhone caches. Automated browser tests assert there is no intro/video overlay.
- Legacy intro media files are not referenced by the site.

## v26.0 (2026-11-12) — faster, sharper original-logo intro

- Re-encoded the owner's original MP4, not a generated substitute: **1280×720 H.264**, approximately **2.63 seconds**, **173 KB**. The original low-bitrate website version was 512×288, 7.6 seconds and blurry when displayed on Retina screens. Optimized crop removes excess whitespace while keeping the entire original logo drawing intact.
- High-quality video now lives at `assets/video/sunja-logo-intro-hq-v26.mp4`; intro stays full-screen white with **no text, progress bar, background image, or spinner**.
- Intro has a **3.8-second absolute escape limit**, skips on reload and repeat visits in the same tab, and exits immediately if video cannot play. Video completion waits for only the first hero image with a bounded 550ms budget, never for the entire gallery. The next two slides are prewarmed afterward while the browser is idle, respecting data-saver mode.
- CSS uses intrinsic 16:9 media at a bounded display width with no post-render blur or scaling effects. Keep existing fixed call bar, one-tap links, slide images, and manual map scroll animation unchanged.
- Updated asset cache keys to `v26.0`. Static and Chromium/WebKit browser tests cover intro exit and noncritical image failures. The intro is not a guarantee that every map tile, font or lazy gallery image has finished downloading.

## v25.0 (2026-11-12) — scroll-controlled map and original logo intro

- Adds the owner's supplied logo-drawing animation, optimized to a small H.264 MP4 at `assets/video/sunja-logo-intro.mp4`. It appears alone on a white, full-screen intro; no bar, wording or spinner.
- Intro begins before the page first paints, warms local site photos in bounded batches, then reveals the site after the video finishes and critical assets have loaded. A safety timeout and media-error fallback prevent visitors being trapped.
- Camera progression is **controlled by how far the visitor scrolls**, forwards and backwards. The MapLibre map follows world → Europe → Bosnia and Herzegovina → Goražde → the shop, with a stable sticky section, no autonomous flyTo and no abrupt height collapse.
- Preserves the clean non-glass interface, stable fixed call/directions bar, shortened service text and accurate map popup. Set `?v=25.0` cache keys to refresh iPhone assets.
- Browser regression tests cover video-only intro, map scroll progress, direct taps and reload-to-top. Reduced-motion remains respected.

## v24.0 (2026-11-12) — correct refresh position and make the globe animation reliable

- **Refresh opens at the hero slides.** An early, synchronous head script detects a genuine page reload and disables Safari/Chromium scroll restoration only for that reload. It clears stale section fragments, then resets to the top on DOM ready, page show and load. Normal in-page anchor taps and shareable links on an initial navigation are unchanged.
- **Actual animated map camera:** Replaced the brittle scroll-progress window with a visible-once MapLibre flight using `flyTo` and `moveend` sequencing: globe → Europe → Bosnia and Herzegovina → Goražde → the shop at zoom **16.2**. The animation starts after MapLibre loads and the map enters view, independently of fast swipes or CDN delays. For reduced-motion settings and low-resource devices, the camera goes directly to the location, respecting accessibility and battery life.
- The map section has a stable, non-sticky height during and after the animation. It never collapses while scrolling or unexpectedly shifts page position. The compact shop popup, native directions/phone links, exact coordinates, and graceful map-failure fallback are preserved.
- Added **real Chromium and WebKit regression tests** for reload after section navigation and manual scrolling, and for the four camera stages using a deterministic MapLibre event mock. These tests run with animation enabled, rather than the reduced-motion setting used by older interaction tests.
- CSS/JS assets now use `?v=24.0` to prevent returning iPhone visitors loading older navigation/map code. The existing non-glass interface and fixed action bar are unchanged.

## v23.1 (2026-11-12) — concise service descriptions and closer location map

- Removed filler introductions in the six service panels. The main sentences are now short, factual Bosnian descriptions; the useful checklists and booking actions remain unchanged.
- At the shop, the MapLibre globe flight finishes at zoom **16.2** (previously 15.5), with a slightly reduced 45° pitch. The exact shop coordinates are unchanged.
- Replaced the oversized default MapLibre popup text with a compact shop card featuring address and directly tappable **Upute** and **Pozovite** actions. Scoped CSS applies only to `.sunja-map-popup`; the original map directions button and fallback remain.
- Existing non-glass white/blue UI, static bottom bar, permanent hero slides, and one-tap controls are preserved.
- Updated CSS/JS asset versions to `v23.1`. Static and Chromium/WebKit mobile browser regressions now check all six service descriptions and map popup markup.

## v23.0 (2026-11-12) — permanently stable mobile action bar

- Removed the entire scroll/resize/focus-based `syncActionDock` collision detector, eight event listeners and the `dock-avoiding-action` visibility class. That old logic repeatedly hid and showed the fixed bar during scrolling and caused blinking, especially in iOS Safari.
- Mobile Pozovite and Upute now stay visible at the bottom of the page with a fixed solid-blue style and **no opacity, transform or visibility animations**. Desktop continues without the mobile dock.
- The image-free dark-blue footer reserves enough internal space for its last links to scroll above the bar, without appending a white strip beneath the page. Preserved Safari safe-area handling.
- The About copy, permanent hero images, gallery, one-tap links, no-loader behavior and clean non-glass interface are unchanged.
- `?v=23.0` forces iPhone to request updated CSS/JS. Browser regression tests now exercise repeated rapid scrolling and footer visibility without hiding the dock.

## v22.2 (2026-11-12) — restore the original stable non-glass UI

Liquid Glass was removed at the owner's request due to glitchy rendering.

- Restored the **white traditional navigation**, **solid blue Pozovite/Upute mobile action bar**, and **blue back-to-top button**. No translucent/optical glass or refraction animation remains on those controls.
- Removed the entire embedded SVG displacement-filter markup, all glass-specific DOM layers and approximately 25 KB of glass CSS plus 7.5 KB of unused JS renderer/theme handlers. Did **not** simply hide the broken renderer.
- Preserved the shorter Bosnian About text, static dark-blue image-free footer, permanent hero photos, uncropped gallery photos, responsive mobile typography, working services/booking anchors and one-tap touch navigation.
- Kept the tap-safe solid mobile bar and collision-aware retract behaviour to avoid covering CTA links or footer information. Fixed desktop nav underline remains absent.
- Updated CSS/JS query strings to `v22.2`; regression tests now specifically assert that no Liquid Glass markup/filters are present.
- The site's GitHub Pages, Chromium, and WebKit checks validate the restored code; a physical iPhone is not directly available in this chat.

## v22.0 (2026-11-12) — image-free footer, compact About, refractive glass, desktop nav and mobile edge handling

- **Removed the unwanted footer background photo entirely.** The old CSS photo variable and the script that replaced it using `photos.json` are both gone. Footer uses a clean dark blue brand gradient only.
- **Shortened O nama** to the address, city and main services; removed the SUV wording. Also shortened the three feature descriptions.
- **Desktop navigation fix:** removed the legacy `::after` underline which crossed menu labels and replaced it with a subtle active-link pill. The navigation keeps its original anchors and first-tap behaviour.
- **Refractive Liquid Glass study:** uses an inline SVG `feTurbulence` + `feDisplacementMap` (optical distortion, not just blur), chromatic lens rims, and a scene-image-aligned copy where a photo is visible behind one of the three requested glass surfaces. A supported Chromium browser may use live backdrop displacement; Safari uses the filter on the scene-copy layer, because SVG filters through `backdrop-filter` are not interoperable. A subtle CSS fallback retains clickable controls even if advanced optics fail. The site remains static with no React runtime or WebGL page-capture loop. Visuals are an independent web approximation, not Apple's private renderer.
- **Smoothness and safety:** glass scene updates are capped to at most one update per 140ms while scrolling; reduced-motion and low-resource modes avoid the extra scene effect. Decorative layers ignore pointer events.
- **Mobile lower edge:** the call/directions dock stays flush with the webpage edge and retracts as soon as the footer would be covered. The full footer has a solid background. The iOS Safari address/search bar is *native browser chrome* and cannot be rendered into by a website; a changing theme-colour hint is offered to compatible browsers.
- `?v=22.1` asset URLs prevent stale iPhone CSS/JS. Site quality workflows run static and real Chromium/WebKit touch tests; only passing runtime results count as browser validation.

Optics research and attribution: [dpawlikowski/liquid-glass](https://github.com/dpawlikowski/liquid-glass), MIT 2026 liquid-glass contributors. Adapted concepts: SVG displacement-map optics and layered chromatic highlights. License reproduced in `docs/liquid-glass-MIT.txt`. The CSS/JS here is site-specific and has no added third-party runtime dependency.

## v21.5 (2026-11-12) — verified one-tap interactions and Safari dock edge

- Corrected the actual first-touch navigation defect found by browser instrumentation: the menu-collapse transition could interrupt navigation after touchend prevented the synthetic click. Internal section links now activate on the completed touch gesture, ignoring swipes, with one-time synthetic-click suppression; the address hash updates before the Bootstrap collapse can fail.
- Gallery touch overlays no longer require hover activation. Service tab controls, slide controls, gallery links, booking CTAs and the back-to-top button retain direct touch activation.
- The mobile call/directions dock is flush with the webpage's lower edge; removed the large footer blank spacer. On iOS, the area containing Safari's address bar is browser-owned chrome and cannot be deleted by webpage CSS.
- Fixed CSS-variable image asset references so hero, gallery and footer background photos resolve from `/assets/...` instead of failing from `/css/assets/...`.
- GitHub Actions Playwright runs were failing before browser launch because `ubuntu-latest` changed to Ubuntu 26.04 while Playwright 1.56 supports Ubuntu 24.04. Both quality workflows are now pinned to Ubuntu 24.04.
- Chromium and WebKit each passed 18 navigation and touch interaction tests on the previous cache key. Static and additional smoke tests are retained. Browser tests emulate phones; a physical iPhone Safari check remains separate.
- HTML now serves `css/style.css?v=21.5` and `js/main.js?v=21.5` to invalidate cached iPhone versions after the final touch fixes.

## v21.3 (2026-11-12) — final site-wide text scale

The typography was not consistently reduced by previous passes. This corrects *all* major content zones: About, services, tabs, gallery, reviews, map, contact, booking and footer. The mobile screenshot's oversized About copy and numbered feature labels are specifically targeted.

- Mobile section headings have a consistent **20px** scale; About feature headings are **14px**; body text is **13.5px** with less excessive line height. Hero headings remain slightly larger for hierarchy (**24–27px**).
- Desktop and tablet retain readable independent sizes (desktop content **15px**, section headings **24–32px**; tablet headings **25px**).
- Contact/address information, service descriptions, footer links and status labels also use explicit smaller rules, avoiding leftover Bootstrap font overrides.
- Vertical margins between headings, body paragraphs and feature rows are tighter. 44px/48px interactive targets remain intact. Form inputs intentionally stay **16px** on iPhone to prevent Safari auto-zoom.
- Asset URLs bumped to `?v=21.3`. Responsive computed-style browser tests now cover all six section headings, About paragraphs and tappable buttons. Source-level checks do not replace actual browser validation.

## v21.2 (2026-11-12) — unobstructed mobile dock and improved optical glass

- Fixed the overlapping mobile call/directions dock shown in the iPhone screenshot. The dock now checks its rest position against booking buttons, About text and form fields; it retracts whenever it would obscure them. It also retracts for the mobile keyboard. Scroll checks use one requestAnimationFrame at most per frame.
- Removed the blank white body bottom padding. Safe clearance now belongs to the actual #siteFooter background, preserving footer links while avoiding an empty tail.
- Added brighter chromatic rim, inset lens shadows and less opaque optically layered backgrounds only to the three selected controls (header, mobile dock and back-to-top). Safari does not support SVG displacement in backdrop-filter, so the fast native backdrop-filter remains the compatible solution rather than claiming genuine refraction.
- Retains one-tap navigation, the original uncropped photos, three permanent hero slides, and reduced-motion fallback. No full-screen loading screen.
- Regression tests now cover optical rims, visible CTA tap access, bottom-of-page spacing and the updated assets (v21.2). Browser and real-device validation are tracked separately.

## v21.0 (2026-11-12) — screenshot-driven mobile typography, scoped Liquid Glass and uncropped photos

The owner flagged specific remaining UI defects in three mobile screenshots: oversized About paragraphs/headings and numbered rows, dark letterboxing beside social photos, and opaque header/bottom controls.

- **Real changes to mobile type:** About / service / gallery / map / contact / review headings now use 1.42rem on phones. The About paragraphs, service descriptions and numbered feature rows are roughly .875rem with tighter gaps and 37px numbered badges. This is separate from the earlier broad selector which had not reduced every row enough.
- **Targeted Apple-inspired glass effect:** Only the existing header (`sunja-liquid-header`), mobile call/directions dock (`sunja-liquid-bottom`), and back-to-top button (`sunja-liquid-top`) receive translucent reflective layers, specular highlights and backdrop blur. All decorative pseudo-elements are pointer-events:none; links remain first-tap controls. On weak devices or browsers without backdrop-filter, lightweight tinted surfaces substitute. No third-party shaders, WebGL, Canvas, or animation loops were added.
- **Zero-crop photos:** gallery wrappers no longer enforce a 4:5 height; every original portrait or landscape image determines its frame height and fills the card width. Service and About photos likewise use their native aspect ratio, with no cropping, blur, photo zoom or upscaling filters added. Gallery source labels (Objava s...) and links remain intact.
- **The three permanent carousel photos are unchanged.** Their foreground images remain whole and sharp; an independently toned version of that exact photo fills side regions rather than a plain navy rectangle. The mobile first slide reuses the same portrait source for its backdrop, so it does not force a second wide-image download.
- **Smooth slideshow:** the first slide keeps its high-priority load. On fast-enough connections, the other two permanent slide images start loading only after the initial page load (not during first paint). All full-page loading screens remain removed.
- `tools/test_frontend_static.py` and `tools/test_browser_interactions.py` now include regressions for image aspect, font sizes, glass hit targets and slide behaviour. Tests must be verified by GitHub Actions or a local browser; source-level checks alone do not prove rendered Safari behaviour.
- Assets use `?v=21.1` so the improved CSS/JS cannot be mixed with older browser cached versions.

The visual inspiration was surveyed from public MIT-licensed liquid-glass web projects; no full external rendering engine was embedded, prioritizing smooth Safari browsing and original site structure.

## v20.1 (2026-11-12) — resilient map fallback and browser regression checks

- MapLibre library requests have a timeout; failed tiles or scripts display a compact address/directions fallback instead of a giant sticky scroll trap. Network error strings are no longer injected into `innerHTML`.
- The map fallback uses `#globeScroll.is-fallback` CSS so it overrides former 118–140svh scroll-flight rules and releases normal page scrolling.
- `index.html` serves `css/style.css?v=20.1` and `js/main.js?v=20.1` to refresh stale cached assets after the v20 change.
- Added `.github/workflows/site-quality.yml`, running the static suite and `tools/test_browser_smoke.py` against mobile-sized Chromium and WebKit with real touchscreen taps and animations enabled. The browser tests are designed to run on GitHub Actions for each site change; they are not equivalent to manual iPhone Safari verification.
- Existing photography, permanent three main slide photos, gallery source captions and booking form are preserved.

## v20.2 (2026-11-12) — tap-target and delivery verification

- Hero slideshow indicators now have a **44px tappable area**, keeping their slim 5px blue/white progress-line appearance; previously the buttons themselves were only 5px tall.
- Updated the style and JavaScript query versions to `v20.2` to invalidate stale browser/CDN assets.
- Automated quality checks: `.github/workflows/site-quality.yml` and `.github/workflows/website-checks.yml` cover static regressions and Chromium/WebKit mobile tap flows, with a map fallback test in the former. `tools/verify_live_site.py` independently compares public CSS/JS SHA-256 hashes against the current repository checkout and flags stale Pages deployments.
- Browser automation does not prove behaviour on a physical iPhone; the public deployment check must pass before declaring the live site current.

## v20 (2026-11-11) — loader-free, one-tap interactions and compact UI

Current site **does not use a full-screen logo preloader** or map loading spinner. The entire intro markup, animation code and CSS were removed rather than merely hidden. The MapLibre globe is still lazy-loaded near the map, and a direct directions link is available immediately.

- All five gallery photo tiles link directly to their original social posts (full-image touch target); the “Objava s…” source caption remains.
- All six service booking actions are direct `#termin` links and still preselect the service. Same-page links scroll on one click; navbar stays in place; back-to-top uses native smooth scroll instead of a custom multi-second rAF loop.
- Hero booking links are interactive from the first frame; touch controls use `touch-action: manipulation` and no hover-dependent positional movement.
- Section headings and hero titles were reduced, buttons made more compact while retaining accessible touch targets, and the jQuery/WOW/animate/easing/waypoints and redundant Bootstrap Icons page dependencies removed. Optional lightweight reveals use IntersectionObserver; reduced-motion and low-resource devices skip them.
- Gallery, photo sync, six service tabs, fixed three-slide photos, map flight, SMS form, mobile callbar and status display remain intact.
- `tools/test_frontend_static.py` now guards against loader regressions, missing one-tap controls and broken content hooks.
- Browser-specific validation on iOS Safari must still be checked separately; source-level tests do not prove every device's runtime behaviour.

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

## v8.1 (2026-11-10) — owner fixes
- ALL `// X //` kickers stripped to plain text site-wide (hero, sections, Kontakt cards) — owner disliked the slashes.
- "Porodični" REMOVED everywhere (About paragraph sentence deleted; footer now "Auto Servis Šunja — Goražde. …"). Owner: never invent family/fluff claims in copy.
- Map: pixelRatio capped at 1.5 + fadeDuration 0 + tiles preconnect → smoother flight. ONE-SHOT flight: when scroll progress hits the end, finish() sets final view, adds .globe-done (section collapses 250vh → static 70vh map block), and removes the scroll listeners — scrolling back up/down afterwards passes a normal map, no replay until page refresh. Verified both ways + reload reset.
- Gallery images switched lazy→eager (the randomizer's src swap stalled under lazy loading; a photo sat on the placeholder for a minute when scrolling back). NOTE: Pages deploy can lag ~1-2 min; a too-early curl shows the previous build — re-check before concluding a push failed.

## v9 (2026-11-10) — owner screenshot fixes + de-AI pass
- Owner's phone screenshots showed the mobile hero BROKEN: caption content taller than the hero → kicker clipped at top, phone button cut at the bottom, arrows + indicators overlapping the CTA. Fix: mobile hero is 94svh/min-640px, caption bottom-anchored with padding for the indicators, text left-aligned, buttons full-width stacked, arrows HIDDEN on mobile (swipe works), indicators below content. Desktop arrows are now solid blue circles.
- BLUE CAR REMOVED: slide 1 = tt-wide-01 (real outside view: Peugeots parked in front of the workshop, "ŠUNJA" wall sign visible). hero-2.jpg also removed from photos.json hero pool so the randomizer can never serve it again.
- MARQUEE REMOVED entirely (the strip the owner circled in his screenshot).
- Less-AI pass: ghost numbers, scroll chevron, ken-burns zoom, footer wave and button shine all removed; kicker is plain text with a small blue bar.
- Mobile hardening: overflow-x: clip (no sideways scroll), form fields 16px (no iOS focus zoom), svh hero units.
- GALLERY "BROKEN IMAGE" MYSTERY SOLVED: the template's .team-overlay is SOLID --primary blue on hover (scale 0→1) — a hovered card looks exactly like a dead image, which fooled the checker (and would fool visitors). Overlay is now a translucent dark tint (photo stays visible). An image self-heal retry (one cache-busted reload if naturalWidth==0) was also added for real transient failures. Hover behaviour verified on 3 cards.

## v10 (2026-11-10): professional copy + whole images
- Playful copy removed ("Lokacija servisa" heading, no "Letimo"), all em-dashes removed from visible texts, kicker decorations stripped.
- Images shown whole: hero uses portrait sources on mobile; the DiagBox screen photo is blur-padded (the photo itself is a tight close-up; its own edges are cut in the source). Services Autodijagnostika later switched to the whole cabin scene photo (tt-07) as svc-dijagnostika-3.jpg.

## v11 (2026-11-10): fresh-photo system + buttons + map
- photos.json entries carry TikTok post dates (decoded from post IDs); the page randomizer enforces Armin's rule: only photos up to 60 days old (safety fallback keeps newest if a pool would empty). The two 2025 Instagram photos left the gallery pool.
- Weekly (later Mon+Thu) cron `autosunja-fresh-photos-weekly` pulls new posts from TikTok @autoservissunja and the shop Facebook page, self-hosts them, retires >60-day photos, verifies live, reports only on change/failure.
- Map: on-map attribution bar hidden; round photo marker of the shop exterior added at the pin; map now initializes lazily when scrolled near (mobile data saving).
- Buttons: navbar CTA was forced to 75px by a template rule (`.navbar-light a.btn`) — fixed with an !important override (now ~46px); back-to-top misplacement fixed by pinning `#backTop` by ID (now bottom-right, verified by pixel measurement); Kontakt card buttons stack on mobile.

## v12 (2026-11-10): 3D shop model — attempted, then REMOVED on Armin's order
- A three.js custom layer modeled the compound from tt-01 (blue workshop + sign band, cream house with pitched roof, totem sign, cars). The layer loaded and rendered without errors but the model never became visible in the MapLibre v5 globe/mercator pipeline despite depth/culling fixes. Armin ordered it dropped ("nah you cant do it so dont do the 3D") — all model code, three.js and the debug status text removed in v13. Do not retry without a new approach.

## v13 (2026-11-10): cleanup + polish (live, verified)
- Map credit line ("Podaci karte...") removed entirely per Armin's order; map area is clean; pin, popup and photo marker intact.
- Polish: gallery hover zoom, blue text selection, navbar shadow, form focus states, prefers-reduced-motion support.

## v14 (2026-11-10): counters band removed, animated stars, REAL auto photo system
- The blue counters band (4,6 / 33 / 959 / 6) is deleted entirely.
- The numeric rating is replaced by animated 5-star displays (About overlay + Recenzije card): grey stars fill up in yellow to the exact rating from rating.json (4,6 = 92%, so the 5th star fills ~60%) with a staggered pop when scrolled into view. The "33 recenzija" sentence remains in Recenzije.
- Photo automation is now a REAL system inside the repo, not an agent task: `.github/workflows/fresh-photos.yml` runs every 6 hours on GitHub Actions; `tools/refresh_photos.py` pulls @autoservissunja posts via yt-dlp (tikwm fallback), mirrors images to assets/photos/, keeps pools ≤60 days old (with pool minimums), uses real captions when a post has one and factual date labels ("Radionica, septembar 2026") for captionless posts, and commits as "sunja-photos-bot". Proven live 2026-11-10: first run found 140 posts, 22 within 60 days, added 11 photos the manual pool had missed, and committed on its own. Armin's agent cron for photos was deleted on his order. Facebook cannot be auto-pulled (login/API wall) — TikTok is the automated source.

## v15 (2026-11-10): the blue stock car is gone EVERYWHERE + hero zoom fixed
- Armin caught the shiny blue stock Peugeot 208 still living in two places the v9 hero removal missed: the Peugeot servis tab photo (`img/svc-peugeot.jpg`) and the FOOTER background (`img/carousel-bg-1.jpg`, under the dark overlay). Both replaced with real shop photos (Peugeot tab = tt-10 white Peugeot in the workshop, new file `img/svc-peugeot-2.jpg`; footer bg = the real outside view, `img/footer-bg.jpg`) and all three blue-car files (svc-peugeot.jpg, carousel-bg-1.jpg, hero-2.jpg) DELETED from the repo — 404 verified.
- v15.1 hero zoom fix: slides now show the WHOLE photo (object-fit: contain) over a blurred, darkened copy of the same photo filling the frame (`.hero-bg` blur-fill); the randomizer updates the backdrop with the pick. The photo bot now generates blur-padded 1600x1000 hero versions for new posts instead of hard center-crops. Verified on first paint + reloads + slides 2/3.

## v16 (2026-11-10): footer photo recomposed, image optimization, lazy map library
- Footer background recomposed from the original tt-01 (band with the AUTO-SERVIS shutter sign, the ŠUNJA totem and the car row — the old center-crop was mostly asphalt/car rears), overlay lightened (.93 → .88, later .84 in v17.2).
- All page JPEGs converted to WebP and every photo recompressed: page-loadable image weight 5,240 KB → 3,618 KB (−31%); old JPEGs deleted from the repo. Slides 2/3 lazy-load.
- MapLibre JS+CSS are no longer loaded with the page — they load on demand when the map section approaches (the globe init is unchanged). Flight verified end-to-end twice after the change.

## v17 (2026-11-10): photo system v2 — 15-min sync, newest first, categories, deletion sync
- Schedule tightened from 6h to every 15 minutes (TikTok offers no push for outsiders; 15 min is the practical "instant").
- The site now FEATURES the newest photo: hero slide 1 and gallery card 1 are always the latest post (previously the newest was buried in a random pool — that is why a new post "wasn't on the site" even though the system had added it). Gallery never repeats a title in one draw.
- Categories: the bot reads what text it can get (captions are NOT exposed by TikTok to outside tools — yt-dlp gets placeholder titles and empty descriptions; oEmbed 400s; free vision endpoints are paywalled, all proven from the runner) and classifies posts into the six service categories; the newest photo of a category automatically becomes that service tab's photo (data-svc-cat + photos.json "services" map). Live categories: dijagnostika, elektrika, veliki, peugeot. Captionless posts stay "opcenito".
- Deletion sync: a post that disappears from TikTok is removed from the site too, but only after it is ALSO unresolvable at its direct URL on two consecutive runs (a listing glitch can never nuke a good photo; first version removed one entry on absence alone — hardened the same night).
- Freshness unchanged: pools hold only the last 60 days; minimums keep hero ≥1 / gallery ≥5.

## v17.3 (2026-11-10): bug-sweep fixes
Full-site sweep fixes: "Lokacija" added to the navbar and footer menu (+ its scroll-margin; all anchors now 104px so headings never clip under the sticky nav); hero interval 6s → 8s with pause-on-hover and a stronger caption gradient; footer "Usluge" links now also activate the matching service tab; "Točnu" → "Tačnu"; TikTok links stripped of tracking parameters; rating badge padding tightened; status pill no longer wraps.
