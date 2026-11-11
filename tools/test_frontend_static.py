import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
JS = (ROOT / "js" / "main.js").read_text(encoding="utf-8")


class FrontendStaticTests(unittest.TestCase):
    def test_exact_logo_loader_uses_real_asset(self):
        self.assertIn('class="pl-final" src="assets/sunja-logo-transparent.webp', INDEX)
        self.assertIn('id="plTrace"', INDEX)

    def test_v184_loader_has_visible_ink_sweep(self):
        self.assertIn('class="pl-ink"', INDEX)
        self.assertIn('pl-draw-finished', JS + INDEX)
        self.assertIn("/*** v18.4: controlled visual polish ***/", CSS)

    def test_navbar_polish_is_actually_attached(self):
        self.assertIn('class="navbar navbar-expand-lg nav-bar ', INDEX)

    def test_cache_versions_are_bumped(self):
        self.assertIn("css/style.css?v=18.7", INDEX)
        self.assertIn("js/main.js?v=18.7", INDEX)

    def test_core_sections_remain_present(self):
        for section_id in ("pocetna", "o-nama", "usluge", "galerija", "lokacija", "kontakt", "siteFooter"):
            self.assertIn(f'id="{section_id}"', INDEX)

    def test_social_photo_and_whole_image_system_remains(self):
        self.assertIn("photos.json", INDEX)
        self.assertIn("object-fit: contain !important", CSS)
        self.assertIn("--footer-photo", CSS)


    def test_back_to_top_is_one_click_controlled_scroll(self):
        self.assertIn('<button type="button" id="backTop"', INDEX)
        self.assertIn("function scrollToTopSmoothly()", JS)
        self.assertIn('root.style.scrollBehavior = "auto"', JS)
        self.assertIn("requestAnimationFrame(step)", JS)
        self.assertNotIn('href="#" id="backTop"', INDEX)
        self.assertNotIn('animate({ scrollTop: 0 }', JS)

    def test_map_does_not_collapse_or_replay_after_arrival(self):
        self.assertNotIn("wrap.classList.add('globe-done')", INDEX)
        self.assertIn("var FLIGHT_END = 0.72;", INDEX)
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

    def test_map_has_a_hold_zone_after_flight(self):
        self.assertIn("height: 300vh;", CSS)
        self.assertIn("#globeScroll.globe-arrived .globe-stage", CSS)


    def test_images_are_not_presented_with_blur_effects(self):
        self.assertIn("/*** v18.6: sharp media presentation ***/", CSS)
        self.assertIn("#header-carousel .hero-bg", CSS)
        self.assertIn("filter: none !important;", CSS)
        self.assertIn(".team-item .position-relative::before", CSS)
        self.assertIn("display: none !important;", CSS)

        self.assertIn("data-about-photo", INDEX)
        self.assertIn("css/style.css?v=18.7", INDEX)
        self.assertIn("js/main.js?v=18.7", INDEX)


if __name__ == "__main__":
    unittest.main()
