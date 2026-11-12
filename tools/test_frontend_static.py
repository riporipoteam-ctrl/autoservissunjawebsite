import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
JS = (ROOT / "js" / "main.js").read_text(encoding="utf-8")


class FrontendStaticTests(unittest.TestCase):
    def test_v22_footer_photo_completely_removed(self):
        self.assertNotIn("--footer-photo", CSS + INDEX)
        self.assertNotIn("footerPhoto", INDEX)
        self.assertIn("/* v22: footer, optical glass, compact about, nav, and safe edges */", CSS)
        self.assertIn("background-image: linear-gradient(", CSS)
        self.assertIn("id=\"siteFooter\"", INDEX)

    def test_v22_about_short_address_first_without_suv(self):
        self.assertIn("Auto Servis Šunja se nalazi na adresi Hajra Lakovića 38", INDEX)
        self.assertIn("73000 Goražde", INDEX)
        self.assertNotIn("SUV-ova", INDEX)
        self.assertNotIn("od gradskih automobila", INDEX)

    def test_v22_desktop_nav_has_no_colliding_underline(self):
        self.assertIn("/* v22: navbar link active pill replaces overlapping underline */", CSS)
        self.assertIn(".navbar-light .navbar-nav .nav-link::after", CSS)
        self.assertIn("content: none !important;", CSS)

    def test_v22_real_svg_refractive_glass_and_accessible_overlays(self):
        self.assertIn('id="sunja-glass-distortion"', INDEX)
        self.assertIn("<feDisplacementMap", INDEX)
        self.assertIn("<feTurbulence", INDEX)
        self.assertIn('class="sunja-glass-refract"', INDEX)
        self.assertIn("filter: url(#sunja-glass-distortion)", CSS)
        self.assertIn("pointer-events: none !important;", CSS)
        self.assertIn("prefers-reduced-motion: reduce", CSS)

    def test_v22_edge_safe_mobile_footer_and_theme(self):
        self.assertIn("viewport-fit=cover", INDEX)
        self.assertIn("theme-color", INDEX)
        self.assertIn("footer-theme-observer", JS)
        self.assertIn("background-color: #0b2154", CSS.lower())
        self.assertIn("css/style.css?v=22.0", INDEX)
        self.assertIn("js/main.js?v=22.0", INDEX)

    def test_fullscreen_loaders_are_removed(self):
        self.assertNotIn('id="preloader"', INDEX)
        self.assertNotIn('plTrace', INDEX)
        self.assertNotIn('pl-ignition', INDEX + JS + CSS)
        self.assertNotIn('#preloader', CSS)
        self.assertNotIn('#spinner', CSS)
        self.assertNotIn('Ignition-style signature intro', INDEX)
        self.assertNotIn('globe-loading-spinner', INDEX + CSS)
        self.assertNotIn('lib/wow/wow.min.js', INDEX)
        self.assertNotIn('lib/animate/animate.min.css', INDEX)

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
        self.assertIn("sunja-liquid-header", INDEX)
        self.assertIn("sunja-liquid-bottom", INDEX)
        self.assertIn("sunja-liquid-top", INDEX)
        self.assertIn("/* v21.0 — responsive optics, original-ratio media, and compact type */", CSS)
        self.assertIn("-webkit-backdrop-filter:", CSS)
        self.assertIn("pointer-events: none;", CSS)
        self.assertNotIn("id=\"preloader\"", INDEX)

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
        self.assertIn("href=\"tel:+38761297847\"", INDEX)
        self.assertIn('id="backTop"', INDEX)
        self.assertIn('class="mobile-callbar sunja-liquid-bottom"', INDEX)
        self.assertIn('class="navbar navbar-expand-lg nav-bar sunja-liquid-header', INDEX)
        self.assertIn('id="backTop" class="btn btn-lg btn-primary btn-lg-square back-to-top sunja-liquid-top', INDEX)

    def test_v214_dynamic_css_photo_vars_use_site_root(self):
        self.assertIn("'url(\"/' + footerPhoto + '\")'", INDEX)
        self.assertIn("'url(\"/' + safeSrc + '\")'", INDEX)
        self.assertNotIn("'url(\"' + footerPhoto + '\")'", INDEX)
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
        self.assertIn("#backTop.sunja-liquid-top.is-visible", CSS)
        self.assertIn("html { scroll-behavior: auto !important; }", CSS)

    def test_v214_real_mobile_touch_targets_are_not_hover_gated(self):
        self.assertIn("/* v21.4: stable first-touch surfaces and dock flush */", CSS)
        self.assertIn(".team-item .team-overlay.gallery-tile-link", CSS)
        self.assertIn("transform: none !important;", CSS)
        self.assertIn("opacity: 1 !important;", CSS)
        self.assertIn("pointer-events: auto !important;", CSS)
        self.assertIn("touch-action: manipulation;", CSS)
        self.assertIn("@media (hover: none), (pointer: coarse)", CSS)

    def test_v214_flush_mobile_dock_has_no_empty_footer_spacer(self):
        self.assertIn(".mobile-callbar.sunja-liquid-bottom", CSS)
        self.assertIn("bottom: 0 !important;", CSS)
        self.assertIn("border-radius: 23px 23px 0 0 !important;", CSS)
        self.assertIn("#siteFooter", CSS)
        self.assertIn("padding-bottom: 28px !important;", CSS)
        self.assertIn("viewport-fit=cover", INDEX)
        self.assertIn('name="theme-color" content="#e8f4fc"', INDEX)

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
        self.assertIn("css/style.css?v=22.0", INDEX)
        self.assertIn("js/main.js?v=22.0", INDEX)

    def test_v212_glass_optical_rims_are_scoped(self):
        self.assertIn("/* v21.2: optical glass and obstruction-free mobile actions */", CSS)
        self.assertIn(".sunja-liquid-header::after", CSS)
        self.assertIn(".sunja-liquid-bottom::after", CSS)
        self.assertIn("#backTop.sunja-liquid-top::after", CSS)
        self.assertIn("-webkit-mask-composite: xor", CSS)
        self.assertIn("mask-composite: exclude", CSS)
        self.assertIn("pointer-events: none", CSS)

    def test_v212_no_blank_body_padding_and_safe_footer(self):
        self.assertIn("body { padding-bottom: 0 !important; }", CSS)
        self.assertIn("#siteFooter", CSS)
        self.assertIn("--dock-clearance", CSS)
        self.assertIn("safe-area-inset-bottom", CSS)

    def test_v212_dock_does_not_cover_page_actions(self):
        self.assertIn("function syncActionDock()", JS)
        self.assertIn("dock-avoiding-action", JS)
        self.assertIn("getBoundingClientRect()", JS)
        self.assertIn("document.activeElement", JS)
        self.assertIn("pointer-events: none !important;", CSS)
        self.assertIn("requestAnimationFrame(syncActionDock)", JS)

    def test_cache_versions_are_bumped(self):
        self.assertIn("css/style.css?v=22.0", INDEX)
        self.assertIn("js/main.js?v=22.0", INDEX)

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

    def test_map_does_not_collapse_or_replay_after_arrival(self):
        self.assertNotIn("wrap.classList.add('globe-done')", INDEX)
        self.assertIn("var FLIGHT_END = 0.90;", INDEX)
        self.assertIn("var flightLocked = false;", INDEX)
        self.assertIn("if (!flightLocked && p >= FLIGHT_END", INDEX)
        self.assertIn("var flightP = flightLocked ? FLIGHT_END", INDEX)
        self.assertIn("var lockedViewApplied = false;", INDEX)
        self.assertIn("if (flightLocked) {", INDEX)
        self.assertIn("setShopMarker(true);", INDEX)
        self.assertIn("wrap.classList.toggle('globe-arrived'", INDEX)

        self.assertIn("var mapReleased = false;", INDEX)
        self.assertIn("rect.bottom <= 0", INDEX)
        self.assertIn("globe-complete", INDEX)

    def test_map_exits_quickly_after_flight(self):
        self.assertIn("height: 170svh;", CSS)
        self.assertIn("height: 145svh;", CSS)
        self.assertIn("height: 118svh !important;", CSS)
        self.assertIn("height: 82svh !important;", CSS)
        self.assertNotIn("height: 300vh;", CSS)
        self.assertNotIn("height: 280vh;", CSS)
        self.assertIn("#globeScroll.globe-arrived .globe-stage", CSS)
        self.assertIn("stickyEl.offsetHeight", INDEX)


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
        self.assertIn("css/style.css?v=22.0", INDEX)
        self.assertIn("js/main.js?v=22.0", INDEX)


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
