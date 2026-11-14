import hashlib
import json
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
JS = (ROOT / "js" / "main.js").read_text(encoding="utf-8")


class FrontendStaticTests(unittest.TestCase):
    def test_google_search_sitemap_has_only_the_real_canonical_page(self):
        sitemap = ROOT / "sitemap.xml"
        self.assertTrue(sitemap.is_file(), "A public sitemap.xml is required")
        root = ET.fromstring(sitemap.read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        self.assertEqual(root.tag, ns + "urlset")
        urls = root.findall(ns + "url")
        self.assertEqual(len(urls), 1, "Only the actual homepage is a distinct page")
        self.assertEqual(urls[0].findtext(ns + "loc"), "https://autosunja.com/")
        self.assertEqual(urls[0].findtext(ns + "lastmod"), "2026-11-14")
        self.assertNotIn("sitey.my", sitemap.read_text(encoding="utf-8"))

    def test_google_search_robots_allows_crawling_and_advertises_sitemap(self):
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn("Sitemap: https://autosunja.com/sitemap.xml", robots)
        self.assertNotIn("Disallow: /", robots)

    def test_google_search_has_grounded_local_autorepair_schema(self):
        matches = re.findall(
            r'<script type="application/ld\\+json">\\s*(.*?)\\s*</script>',
            INDEX, flags=re.S
        )
        self.assertEqual(len(matches), 1, "Use one canonical JSON-LD business record")
        data = json.loads(matches[0])
        self.assertEqual(data["@context"], "https://schema.org")
        self.assertEqual(data["@type"], "AutoRepair")
        self.assertEqual(data["name"], "Auto Servis Šunja")
        self.assertEqual(data["url"], "https://autosunja.com/")
        self.assertEqual(data["telephone"], "+38761297847")
        self.assertEqual(data["address"]["streetAddress"], "Hajra Lakovića 38")
        self.assertEqual(data["address"]["addressLocality"], "Goražde")
        self.assertEqual(data["address"]["postalCode"], "73000")
        self.assertEqual(data["address"]["addressCountry"], "BA")
        self.assertEqual(data["openingHoursSpecification"]["opens"], "10:00")
        self.assertEqual(data["openingHoursSpecification"]["closes"], "18:00")
        self.assertEqual(len(data["openingHoursSpecification"]["dayOfWeek"]), 6)
        self.assertIn("https://www.tiktok.com/@autoservissunja", data["sameAs"])
        self.assertNotIn("aggregateRating", data)
        self.assertNotIn("review", data)

    def test_google_search_meta_tags_are_searchable_and_consistent(self):
        self.assertIn("Auto Servis Šunja Goražde", INDEX)
        self.assertIn('rel="canonical" href="https://autosunja.com/"', INDEX)
        self.assertIn('property="og:locale" content="bs_BA"', INDEX)
        self.assertIn('name="robots" content="index, follow, max-image-preview:large"', INDEX)
        self.assertNotIn('content="noindex"', INDEX)
        self.assertNotIn("autosunja.sitey.my", INDEX)

    def test_custom_dot_com_domain_is_the_pages_domain(self):
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "autosunja.com")
        self.assertIn('rel="canonical" href="https://autosunja.com/"', INDEX)
        self.assertIn('content="https://autosunja.com/"', INDEX)
        self.assertIn('content="https://autosunja.com/assets/', INDEX)
        self.assertNotIn("autosunja.sitey.my", INDEX)

    def test_live_deployment_probe_targets_new_canonical_domain(self):
        probe = (ROOT / "tools" / "verify_live_site.py").read_text(encoding="utf-8")
        self.assertIn('BASE = "https://autosunja.com"', probe)
        self.assertNotIn('BASE = "https://autosunja.sitey.my"', probe)

    def test_v22_footer_photo_completely_removed(self):
        self.assertNotIn("--footer-photo", CSS + INDEX)
        self.assertNotIn("footerPhoto", INDEX)
        self.assertIn("/* v22.2: classic UI restored", CSS)
        self.assertIn("background-image:linear-gradient(", CSS)
        self.assertIn('id="siteFooter"', INDEX)

    def test_v22_about_short_address_first_without_suv(self):
        self.assertIn("Auto Servis Šunja se nalazi na adresi Hajra Lakovića 38", INDEX)
        self.assertIn("73000 Goražde", INDEX)
        self.assertNotIn("SUV-ova", INDEX)
        self.assertNotIn("od gradskih automobila", INDEX)

    def test_v22_desktop_nav_has_no_colliding_underline(self):
        self.assertIn(".navbar-light .navbar-nav .nav-link::after", CSS)
        self.assertIn("content:none !important", CSS)

    def test_v22_gradient_backdrops_can_be_refracted_without_screenshot_capture(self):
        self.assertNotIn("paintedBackground.indexOf", JS)
        self.assertNotIn("syncLensScene", JS)
        self.assertNotIn("html2canvas", JS + INDEX)

    def test_v22_real_svg_refractive_glass_and_accessible_overlays(self):
        self.assertNotIn("sunja-glass-distortion", INDEX + CSS + JS)
        self.assertNotIn("sunja-glass-refract", INDEX + CSS + JS)
        self.assertNotIn("sunja-liquid-header", INDEX + CSS + JS)
        self.assertNotIn("backdrop-filter: url(", CSS)
        self.assertIn("background:#fff !important", CSS)

    def test_v22_edge_safe_mobile_footer_and_theme(self):
        self.assertIn("viewport-fit=cover", INDEX)
        self.assertIn("theme-color", INDEX)
        self.assertNotIn("footer-theme-observer", JS)
        self.assertIn("background-color:#0b2154", CSS)
        self.assertIn("css/style.css?v=34.0", INDEX)
        self.assertIn("js/main.js?v=34.0", INDEX)

    def test_v34_intro_has_no_native_player_controls_or_interaction(self):
        self.assertIn('id="sunjaIntro"', INDEX)
        self.assertIn('id="sunjaIntroFrames"', INDEX)
        self.assertIn('src="assets/video/sunja-logo-uploaded-120percent-v34.webp"', INDEX)
        self.assertNotIn('<video id="sunjaIntroVideo"', INDEX)
        self.assertNotIn('<video', INDEX)
        self.assertNotIn('video.play()', INDEX)
        self.assertNotIn('showUploadedFramesFallback()', INDEX)
        self.assertIn('draggable="false"', INDEX)
        self.assertIn("pointer-events: none !important", CSS)
        self.assertIn("user-select: none !important", CSS)
        self.assertIn("window.__sunjaIntroForceFinish", INDEX)
        self.assertIn("introSafetyTimeout", INDEX)
        self.assertIn("function beginIntroAnimation()", INDEX)
        self.assertIn("function showIntroStill()", INDEX)
        self.assertNotIn('id="sunjaIntroProgress"', INDEX)
        self.assertNotIn('id="sunjaIntroLoading"', INDEX)
        self.assertNotIn("@keyframes sunjaLogoDraw", CSS)

    def test_v34_animation_is_original_frames_at_120_percent_speed_once(self):
        animation = ROOT / "assets/video/sunja-logo-uploaded-120percent-v34.webp"
        self.assertTrue(animation.is_file(), "Must publish a generated animated image")
        content = animation.read_bytes()
        self.assertEqual(content[:4], b"RIFF")
        self.assertEqual(content[8:12], b"WEBP")
        durations = []
        loop_count = None
        offset = 12
        while offset + 8 <= len(content):
            kind = content[offset:offset+4]
            length = int.from_bytes(content[offset+4:offset+8], "little")
            payload = content[offset+8:offset+8+length]
            if kind == b"ANIM":
                loop_count = int.from_bytes(payload[4:6], "little")
            if kind == b"ANMF":
                durations.append(int.from_bytes(payload[12:15], "little"))
            offset += 8 + length + (length % 2)
        self.assertGreaterEqual(len(durations), 60)
        self.assertEqual(loop_count, 1)
        self.assertGreater(sum(durations), 4700)
        self.assertLess(sum(durations), 5300)
        self.assertLess(animation.stat().st_size, 900_000)

    def test_v34_preserves_user_uploaded_source_mp4(self):
        source = ROOT / "assets/video/sunja-logo-intro-user-uploaded-v33.mp4"
        self.assertTrue(source.is_file())
        self.assertEqual(source.stat().st_size, 421504)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         "73e0c3297813c72d219d7770e65f0b3e05f2c1a7fa6dbe96d79378118ba4ac45")
        self.assertNotIn('src="assets/video/sunja-logo-intro-user-uploaded-v33.mp4"', INDEX)

    def test_v32_photo_replaces_full_footer_background_and_about_photo(self):
        photo = "assets/gallery/sunja-tiktok-7627945643490692373.webp"
        self.assertIn('data-about-photo src="' + photo + '"', INDEX)
        self.assertIn('url("../' + photo + '")', CSS)
        self.assertIn("#siteFooter.footer", CSS)
        self.assertNotIn('class="container footer-featured-photo"', INDEX)
        self.assertIn("https://vm.tiktok.com/ZN85hsoY9/", INDEX)

    def test_v32_mobile_chrome_and_safe_area_remain_blue(self):
        self.assertIn('meta name="theme-color" content="#0B5FA5"', INDEX)
        self.assertIn("/* v32: matching mobile-safe-area background", CSS)
        self.assertIn(".mobile-callbar::before", CSS)
        self.assertIn("env(safe-area-inset-bottom", CSS)

    def test_navbar_polish_is_actually_attached(self):
        self.assertIn('class="navbar navbar-expand-lg nav-bar ', INDEX)

    def test_v21_mobile_hero_uses_same_photo_for_backdrop_and_foreground(self):
        self.assertIn("--hero-photo-mobile:", INDEX)
        self.assertIn("var(--hero-photo-mobile)", CSS)
        self.assertIn('id="heroMainSrc"', INDEX)

    def test_v21_preloads_fixed_following_slides_after_first_load(self):
        self.assertIn('window.addEventListener("load", function ()', JS)
        self.assertIn('querySelectorAll(".carousel-item:not(.active) picture img")', JS)
        self.assertIn('slideImg.loading = "eager"', JS)
        self.assertIn('if (!saveData && !perfLite)', JS)

    def test_v21_glass_is_only_on_three_requested_controls(self):
        self.assertNotIn("sunja-liquid-", INDEX + CSS + JS)
        self.assertNotIn("sunja-glass-", INDEX + CSS + JS)
        self.assertIn('class="mobile-callbar"', INDEX)
        self.assertIn('class="navbar navbar-expand-lg nav-bar bg-white', INDEX)
        self.assertIn('back-to-top"', INDEX)
        self.assertIn("/* v22.2: classic UI restored", CSS)

    def test_v21_compact_typography_and_about_rows(self):
        self.assertIn("#o-nama > .container", CSS)
        self.assertIn("#o-nama h1", CSS)
        self.assertIn("#o-nama .ps-3 > span", CSS)
        self.assertIn("font-size: .875rem !important;", CSS)
        self.assertIn("width: 37px !important;", CSS)

    def test_v21_uncropped_media_and_curated_hero_backdrops(self):
        self.assertIn("aspect-ratio: auto !important;", CSS)
        self.assertIn(".team-item .position-relative", CSS)
        self.assertIn("height: auto !important;", CSS)
        self.assertIn("--hero-photo:", INDEX)
        self.assertIn("var(--hero-photo)", CSS)
        for source in ("radionica-dijagnostika.webp", "kljucevi-programiranje.webp"):
            self.assertIn(source, INDEX)
        self.assertNotIn("heroImg.src = pick", INDEX)

    def test_v21_anchors_remain_one_click_and_no_glass_overlay_blocks_taps(self):
        self.assertIn('href="tel:+38761297847"', INDEX)
        self.assertIn('id="backTop"', INDEX)
        self.assertIn('class="mobile-callbar"', INDEX)
        self.assertIn('class="navbar navbar-expand-lg nav-bar bg-white', INDEX)
        self.assertIn("activateSectionLink(link)", JS)

    def test_v214_dynamic_css_photo_vars_use_site_root(self):
        self.assertNotIn("footerPhoto", INDEX)
        self.assertIn("'url(\"/' + safeSrc + '\")'", INDEX)
        self.assertNotIn("'url(\"' + safeSrc + '\")'", INDEX)

    def test_v214_hero_backdrops_resolve_from_site_root(self):
        self.assertIn("--hero-photo:url('/assets/photos/", INDEX)
        self.assertIn("--hero-photo-mobile:url('/assets/photos/", INDEX)
        self.assertIn("--hero-photo:url('/assets/gallery/", INDEX)
        self.assertNotIn("--hero-photo:url('assets/", INDEX)

    def test_v214_section_links_activate_on_first_completed_touch(self):
        self.assertIn("document.addEventListener(\"touchstart\"", JS)
        self.assertIn("document.addEventListener(\"touchend\"", JS)
        self.assertIn("document.addEventListener(\"touchcancel\"", JS)
        self.assertIn("function activateSectionLink(link)", JS)
        self.assertIn("passive: false", JS)
        self.assertIn("Math.abs(touch.clientY", JS)
        self.assertIn("lastHandledTouch", JS)

    def test_v214_menu_closes_on_first_navigation_and_top_stays_visible(self):
        self.assertIn("function collapseMobileMenu()", JS)
        self.assertIn("collapseMobileMenu();", JS)
        self.assertIn("document.addEventListener('click', function (event)", JS)
        self.assertIn("#backTop", CSS)
        self.assertIn("scroll-behavior:auto !important", CSS)

    def test_v214_real_mobile_touch_targets_are_not_hover_gated(self):
        self.assertIn(".team-item .team-overlay.gallery-tile-link", CSS)
        self.assertIn("transform:none !important", CSS)
        self.assertIn("opacity:1 !important", CSS)
        self.assertIn("pointer-events:auto !important", CSS)
        self.assertIn("touch-action:manipulation", CSS)
        self.assertIn("@media (hover:none),(pointer:coarse)", CSS)

    def test_v214_flush_mobile_dock_has_no_empty_footer_spacer(self):
        self.assertIn(".mobile-callbar", CSS)
        self.assertIn("bottom:0 !important", CSS)
        self.assertIn("border-radius:14px 14px 0 0 !important", CSS)
        self.assertIn("#siteFooter", CSS)
        self.assertIn("padding-bottom:28px !important", CSS)
        self.assertIn("viewport-fit=cover", INDEX)

    def test_v214_browser_ci_has_known_supported_runner(self):
        for path in (".github/workflows/site-quality.yml",
                     ".github/workflows/website-checks.yml"):
            workflow = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("runs-on: ubuntu-24.04", workflow)
            self.assertNotIn("runs-on: ubuntu-latest", workflow)

    def test_v213_typography_is_site_wide_and_mobile_compact(self):
        self.assertIn("/* v21.3 — consistent site-wide typography */", CSS)
        self.assertIn("--sunja-mobile-copy: 13.5px;", CSS)
        self.assertIn("--sunja-mobile-title: 20px;", CSS)
        self.assertIn("--sunja-desktop-copy: 15px;", CSS)
        self.assertIn("#siteFooter", CSS)
        self.assertIn("#termin", CSS)
        self.assertIn(".service .nav .nav-link h4", CSS)
        self.assertIn("text-size-adjust: 100%", CSS)

    def test_v213_content_margins_and_tap_areas_preserved(self):
        self.assertIn("#o-nama p.mb-4", CSS)
        self.assertIn(".container-xxl.py-5", CSS)
        self.assertIn("min-height: 44px", CSS)
        self.assertIn("css/style.css?v=34.0", INDEX)
        self.assertIn("js/main.js?v=34.0", INDEX)

    def test_v212_glass_optical_rims_are_scoped(self):
        self.assertNotIn("sunja-liquid-", CSS + INDEX)
        self.assertNotIn("--glass-rim", CSS)
        self.assertIn("background:#0b5fa5 !important", CSS)
        self.assertIn("backdrop-filter:none !important", CSS)
        self.assertIn("/* v22.2: classic UI restored", CSS)

    def test_v212_no_blank_body_padding_and_safe_footer(self):
        self.assertIn("padding-bottom:0 !important", CSS)
        self.assertIn("#siteFooter", CSS)
        self.assertIn("safe-area-inset-bottom", CSS)
        self.assertNotIn("--dock-clearance", CSS)

    def test_v23_fixed_mobile_dock_has_no_scroll_toggle(self):
        self.assertNotIn("function syncActionDock()", JS)
        self.assertNotIn("scheduleActionDock", JS)
        self.assertNotIn("dock-avoiding-action", CSS + JS)
        self.assertNotIn("document.querySelector(\".mobile-callbar\")", JS)
        self.assertIn("/* v23: fixed no-flicker mobile dock */", CSS)
        self.assertIn("visibility: visible !important", CSS)
        self.assertIn("opacity: 1 !important", CSS)
        self.assertIn("transition: none !important", CSS)
        self.assertIn("min-height: calc(96px", CSS)

    def test_cache_versions_are_bumped(self):
        self.assertIn("css/style.css?v=34.0", INDEX)
        self.assertIn("js/main.js?v=34.0", INDEX)

    def test_v231_service_descriptions_are_short_without_filler(self):
        self.assertNotIn("Upalila se lampica na instrument tabli?", INDEX)
        self.assertNotIn("Redovno održavanje koje čuva motor", INDEX)
        self.assertNotIn("Izgubili ste ključ ili vam treba rezervni?", INDEX)
        self.assertIn("Dijagnostika i otkrivanje kvarova na vozilu.", INDEX)
        self.assertIn("Zamjena motornog ulja i filtera.", INDEX)
        self.assertIn("/* v23.1 compact service descriptions", CSS)

    def test_v231_map_close_zoom_and_compact_popup(self):
        self.assertIn("var SHOP_ZOOM = 16.2;", INDEX)
        self.assertIn("zoom: SHOP_ZOOM", INDEX)
        self.assertIn("zoom: SHOP_ZOOM", INDEX)
        self.assertIn("className: 'sunja-map-popup'", INDEX)
        self.assertIn("closeButton: false", INDEX)
        self.assertIn("focusAfterOpen: false", INDEX)
        self.assertIn("sunja-map-card__title", INDEX)
        self.assertIn("sunja-map-card__actions", INDEX)
        self.assertIn("sunja-map-card__address", INDEX)
        self.assertIn("/* v23.1 map popup: clean compact shop card */", CSS)
        self.assertIn(".sunja-map-popup .maplibregl-popup-content", CSS)

    def test_core_sections_remain_present(self):
        for section_id in ("pocetna", "o-nama", "usluge", "galerija", "lokacija", "kontakt", "siteFooter"):
            self.assertIn(f'id="{section_id}"', INDEX)

    def test_social_photo_and_whole_image_system_remains(self):
        self.assertIn("photos.json", INDEX)
        self.assertIn("object-fit: contain !important", CSS)
        self.assertNotIn("--footer-photo", CSS + INDEX)
        self.assertNotIn("footerPhoto", INDEX)


    def test_back_to_top_uses_one_native_scroll(self):
        self.assertIn('<button type="button" id="backTop"', INDEX)
        self.assertIn('window.scrollTo({ top: 0, behavior:', JS)
        self.assertNotIn('function step(now)', JS)
        self.assertNotIn('requestAnimationFrame(step)', JS)
        self.assertIn('touch-action: manipulation', CSS)

    def test_no_jquery_or_unused_icon_dependency(self):
        self.assertNotIn('jquery-3.4.1.min.js', INDEX)
        self.assertNotIn('bootstrap-icons@1.4.1', INDEX)
        self.assertNotIn('})(jQuery)', JS)
        self.assertIn('document.querySelector', JS)
        self.assertIn("addEventListener", JS)
        self.assertIn('fa fa-arrow-up', INDEX)

    def test_section_navigation_works_on_first_click(self):
        self.assertIn("document.addEventListener('click', function (event)", JS)
        self.assertIn("target.scrollIntoView(", JS)
        self.assertIn('history.replaceState(null, "",', JS)
        self.assertIn('top: 0 !important;', CSS)

    def test_book_service_is_a_direct_link(self):
        self.assertIn('href="#termin" data-service="Autodijagnostika"', INDEX)
        self.assertNotIn('<button class="btn btn-primary py-3 px-5 mt-3" data-service=', INDEX)

    def test_gallery_tile_is_entirely_clickable(self):
        self.assertIn('class="team-overlay position-absolute start-0 top-0 w-100 h-100 gallery-tile-link"', INDEX)
        self.assertIn('data-gallery-link', INDEX)
        self.assertIn('.gallery-tile-link', CSS)

    def test_type_and_buttons_are_compact(self):
        self.assertIn('/* v20.0: instant, compact and loader-free */', CSS)
        self.assertIn('#o-nama h1', CSS)
        self.assertIn('touch-action: manipulation', CSS)

    def test_v24_refresh_goes_back_to_hero_before_page_layout(self):
        self.assertIn("history.scrollRestoration = 'manual'", INDEX)
        self.assertIn("navigationType === 'reload'", INDEX)
        self.assertIn("location.pathname + location.search", INDEX)
        self.assertIn("window.scrollTo(0, 0)", INDEX)
        self.assertIn("pageshow", INDEX)

    def test_v30_map_settle_restores_normal_flow_and_smooths_camera(self):
        self.assertIn("function settleMapScroll()", INDEX)
        self.assertIn("window.scrollBy(0, shift)", INDEX)
        self.assertIn("contactSection.getBoundingClientRect().top", INDEX)
        self.assertIn("map.easeTo({", INDEX)
        self.assertIn("duration: 320", INDEX)
        self.assertIn("/* v30: settled map takes one screen, not a second swipe */", CSS)
        self.assertIn("#globeScroll.globe-complete {", CSS)
        self.assertIn("height: 100svh !important", CSS)

    def test_v29_map_locks_permanently_after_arrival(self):
        self.assertIn("var mapCompleted = false;", INDEX)
        self.assertIn("function finishMapOnce()", INDEX)
        self.assertIn("if (mapCompleted || fellBack || !loaded)", INDEX)
        self.assertIn("removeEventListener('scroll', queueMapProgress)", INDEX)
        self.assertIn("mapCompleted = true;", INDEX)
        self.assertIn("setShopMarker(true)", INDEX)
        self.assertIn("globe-complete", INDEX)

    def test_v29_map_avoids_scroll_frame_render_flood_and_starts_early(self):
        self.assertIn("var CAMERA_MIN_FRAME_MS = 140;", INDEX)
        self.assertIn("lastCameraAt", INDEX)
        self.assertIn("progress - lastMapProgress", INDEX)
        self.assertIn("rootMargin: '850px 0px'", INDEX)
        self.assertIn("cdn.jsdelivr.net/npm/maplibre-gl@5.6.0", INDEX)
        self.assertIn('href="https://cdn.jsdelivr.net"', INDEX)
        self.assertIn("pixelRatio: Math.min", INDEX)
        self.assertIn("cancelPendingTileRequestsWhileZooming: false", INDEX)
        self.assertIn("/* v29: stable finished map", CSS)

    def test_v24_map_plays_real_camera_flight_after_loading(self):
        self.assertIn("function updateMapOnScroll()", INDEX)
        self.assertIn("function queueMapProgress()", INDEX)
        self.assertIn("map.jumpTo({", INDEX)
        self.assertIn("mapFlightStops", INDEX)
        self.assertIn("window.addEventListener('scroll', queueMapProgress", INDEX)
        self.assertNotIn("map.flyTo({", INDEX)
        self.assertNotIn("function beginGlobeFlight()", INDEX)
        self.assertIn("/* v25: scrubbed globe scroll animation */", CSS)
        self.assertIn("position: sticky !important", CSS)
        self.assertIn("height: 220svh !important", CSS)

    def test_v31_map_preloads_before_scroll_and_limits_tile_flooding(self):
        self.assertIn("scheduleEarlyGlobeStart()", INDEX)
        self.assertIn("window.addEventListener('load', scheduleEarlyGlobeStart", INDEX)
        self.assertIn("cancelPendingTileRequestsWhileZooming: false", INDEX)
        self.assertIn("var CAMERA_MIN_FRAME_MS = 140;", INDEX)
        self.assertIn("duration: 320", INDEX)
        self.assertIn("rootMargin: '850px 0px'", INDEX)
        self.assertIn("setShopMarker(true)", INDEX)
        self.assertIn("function settleMapScroll()", INDEX)

    def test_v31_mobile_browser_chrome_matches_the_fixed_callbar(self):
        self.assertIn('name="theme-color" media="(max-width: 991.98px)" content="#0B5FA5"', INDEX)
        self.assertIn('name="theme-color" media="(min-width: 992px)"', INDEX)
        self.assertIn("/* v31: cross-browser fixed mobile action dock */", CSS)
        self.assertIn("env(safe-area-inset-bottom", CSS)
        self.assertIn(".mobile-callbar a.dir", CSS)
        self.assertIn("background:#0b5fa5", CSS)

    def test_v31_footer_uses_exact_supplied_tiktok_photo(self):
        self.assertIn('assets/gallery/sunja-tiktok-7627945643490692373.webp', INDEX)
        self.assertIn('https://vm.tiktok.com/ZN85hsoY9/', INDEX)
        self.assertNotIn('class="container footer-featured-photo"', INDEX)
        self.assertIn('class="container footer-photo-credit"', INDEX)
        self.assertIn("/* v31: featured real TikTok photo in footer */", CSS)

    def test_v24_map_keeps_fallback_and_directions(self):
        self.assertIn("wrap.classList.add('is-fallback')", INDEX)
        self.assertIn('class="map-quick-link"', INDEX)
        self.assertIn("map.resize()", INDEX)
        self.assertIn("setShopMarker(true)", INDEX)

    def test_rejected_outside_image_does_not_appear(self):
        self.assertNotIn("tt-20261108-59603d89", INDEX)
        self.assertNotIn("tt-20261110-5ab64c5a", INDEX)
        self.assertNotIn("tt-wide-01.webp", INDEX)
        self.assertNotIn("tt-01.webp", INDEX)
        self.assertIn("tt-20260919-d3b7439d.webp", INDEX)
        self.assertNotIn("aboutPhoto.src = aboutSrc", INDEX)

    def test_images_are_not_presented_with_blur_effects(self):
        self.assertIn("/*** v18.6: sharp media presentation ***/", CSS)
        self.assertIn("#header-carousel .hero-bg", CSS)
        self.assertIn("filter: none !important;", CSS)
        self.assertIn(".team-item .position-relative::before", CSS)
        self.assertIn("display: none !important;", CSS)

        self.assertIn("data-about-photo", INDEX)
        self.assertIn("css/style.css?v=34.0", INDEX)
        self.assertIn("js/main.js?v=34.0", INDEX)


    def test_three_slides_have_permanent_photos_and_no_auto_swap(self):
        self.assertIn("assets/photos/tt-wide-20260919-d3b7439d.webp", INDEX)
        self.assertIn("assets/gallery/radionica-dijagnostika.webp", INDEX)
        self.assertIn("assets/gallery/kljucevi-programiranje.webp", INDEX)
        self.assertNotIn("var heroPool =", INDEX)
        self.assertNotIn("heroImg.src = pick", INDEX)

    def test_map_failure_releases_sticky_scroll_and_keeps_directions(self):
        self.assertIn("wrap.classList.add('is-fallback')", INDEX)
        self.assertIn("#globeScroll.is-fallback", CSS)
        self.assertIn("#globeScroll.is-fallback .globe-sticky", CSS)
        self.assertIn("height: auto !important;", CSS)
        self.assertNotIn("wrap.style.height = '70vh'", INDEX)
        self.assertIn("Kartu nije moguće učitati", INDEX)
        self.assertIn('class="map-quick-link"', INDEX)

    def test_map_photo_overlay_removed_and_directions_available_immediately(self):
        self.assertNotIn("shop-photo-marker", INDEX)
        self.assertNotIn("photoMarker", INDEX)
        self.assertNotIn('id="globeLoading"', INDEX)
        self.assertIn('class="map-quick-link"', INDEX)
        self.assertIn("classList.add('is-loaded')", INDEX)
        self.assertIn("map.resize()", INDEX)

    def test_gallery_keeps_source_and_hides_photo_titles(self):
        self.assertNotIn('data-gallery-title', INDEX)
        self.assertIn('data-gallery-sub', INDEX)
        self.assertIn('Objava s TikToka', INDEX)

    def test_all_visible_hours_use_colon_style(self):
        self.assertNotIn("10.00", INDEX)
        self.assertNotIn("18.00", INDEX)
        self.assertIn("10:00", INDEX)
        self.assertIn("18:00", INDEX)

    def test_contact_card_status_wraps_on_mobile(self):
        self.assertIn('class="contact-spotlight', INDEX)
        self.assertIn("contact-actions", INDEX)
        self.assertIn(".contact-spotlight .status-pill", CSS)
        self.assertIn("overflow-wrap: anywhere", CSS)

    def test_permanent_slides_and_map_survive_cleanup(self):
        self.assertIn('id="header-carousel"', INDEX)
        self.assertIn('id="globeMap"', INDEX)
        self.assertIn("globe-complete", INDEX)
        self.assertNotIn("sunjaV19Scanner", CSS)


if __name__ == "__main__":
    unittest.main()
