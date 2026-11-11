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
        self.assertIn("css/style.css?v=18.4", INDEX)
        self.assertIn("js/main.js?v=18.4", INDEX)

    def test_core_sections_remain_present(self):
        for section_id in ("pocetna", "o-nama", "usluge", "galerija", "lokacija", "kontakt", "siteFooter"):
            self.assertIn(f'id="{section_id}"', INDEX)

    def test_social_photo_and_whole_image_system_remains(self):
        self.assertIn("photos.json", INDEX)
        self.assertIn("object-fit: contain !important", CSS)
        self.assertIn("--footer-photo", CSS)


if __name__ == "__main__":
    unittest.main()
