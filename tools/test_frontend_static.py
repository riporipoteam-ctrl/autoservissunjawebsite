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
        self.assertIn("css/style.css?v=18.5", INDEX)
        self.assertIn("js/main.js?v=18.5", INDEX)

    def test_core_sections_remain_present(self):
        for section_id in ("pocetna", "o-nama", "usluge", "galerija", "lokacija", "kontakt", "siteFooter"):
            self.assertIn(f'id="{section_id}"', INDEX)

    def test_social_photo_and_whole_image_system_remains(self):
        self.assertIn("photos.json", INDEX)
        self.assertIn("object-fit: contain !important", CSS)
        self.assertIn("--footer-photo", CSS)


    def test_back_to_top_is_one_click_instant(self):
        self.assertIn("function jumpToTopInstantly()", JS)
        self.assertIn("window.scrollTo(0, 0)", JS)
        self.assertNotIn('animate({ scrollTop: 0 }', JS)

    def test_map_does_not_collapse_when_camera_arrives(self):
        self.assertNotIn("wrap.classList.add('globe-done')", INDEX)
        self.assertIn("var FLIGHT_END = 0.72;", INDEX)
        self.assertIn("wrap.classList.toggle('globe-arrived'", INDEX)

    def test_map_has_a_hold_zone_after_flight(self):
        self.assertIn("height: 300vh;", CSS)
        self.assertIn("#globeScroll.globe-arrived .globe-stage", CSS)


if __name__ == "__main__":
    unittest.main()
