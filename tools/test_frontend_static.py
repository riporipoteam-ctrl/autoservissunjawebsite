import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
JS = (ROOT / "js" / "main.js").read_text(encoding="utf-8")


class FrontendStaticTests(unittest.TestCase):
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

    def test_cache_versions_are_bumped(self):
        self.assertIn("css/style.css?v=21.1", INDEX)
        self.assertIn("js/main.js?v=21.1", INDEX)

    def test_core_sections_remain_present(self):
        for section_id in ("pocetna", "o-nama", "usluge", "galerija", "lokacija", "kontakt", "siteFooter"):
            self.assertIn(f'id="{section_id}"', INDEX)

    def test_social_photo_and_whole_image_system_remains(self):
        self.assertIn("photos.json", INDEX)
        self.assertIn("object-fit: contain !important", CSS)
        self.assertIn("--footer-photo", CSS)


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
        self.assertIn("history.replaceState(null, '',", JS)
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
        self.assertIn("css/style.css?v=21.1", INDEX)
        self.assertIn("js/main.js?v=21.1", INDEX)


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
