"""Browser smoke checks for first-tap interactions and map failure on desktop/mobile.

Runs from GitHub Actions with Playwright. No credentials and no live-site writes.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import re
import unittest

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class BrowserSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            partial(QuietHandler, directory=str(ROOT)),
        )
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = "http://127.0.0.1:%d/" % cls.server.server_address[1]
        cls.playwright = sync_playwright().start()
        cls.browsers = {
            "Chromium": cls.playwright.chromium.launch(headless=True),
            "WebKit": cls.playwright.webkit.launch(headless=True),
        }

    @classmethod
    def tearDownClass(cls):
        for browser in cls.browsers.values():
            browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def exercise_browsers(self, test_body):
        for name, browser in self.browsers.items():
            with self.subTest(browser=name):
                context = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    is_mobile=True,
                    has_touch=True,
                    device_scale_factor=2,
                    reduced_motion="reduce",
                )
                context.set_default_timeout(12000)
                page = context.new_page()
                try:
                    test_body(page)
                finally:
                    context.close()

    def test_no_preloader_and_compact_typography(self):
        def check(page):
            page.goto(self.origin, wait_until="domcontentloaded")
            self.assertEqual(page.locator("#preloader").count(), 0)
            self.assertEqual(page.locator("#spinner").count(), 0)
            size = page.locator("#o-nama h1").evaluate(
                "(el) => parseFloat(getComputedStyle(el).fontSize)"
            )
            self.assertLessEqual(size, 40)
            self.assertEqual(page.locator(".gallery-tile-link").count(), 5)

        self.exercise_browsers(check)

    def test_mobile_menu_navigates_in_one_tap(self):
        def check(page):
            page.goto(self.origin, wait_until="domcontentloaded")
            page.locator(".navbar-toggler").tap()
            expect(page.locator("#navbarCollapse")).to_have_class(re.compile(r"\bshow\b"))
            page.locator('.navbar-nav a[href="#o-nama"]').tap()
            self.assertEqual(page.evaluate("location.hash"), "#o-nama")
            expect(page.locator("#navbarCollapse")).not_to_have_class(re.compile(r"\bshow\b"))

        self.exercise_browsers(check)

    def test_service_selection_books_on_first_tap(self):
        def check(page):
            page.goto(self.origin, wait_until="domcontentloaded")
            page.locator('button[data-bs-target="#tab-pane-6"]').tap()
            expect(page.locator("#tab-pane-6")).to_have_class(re.compile(r"\bactive\b"))
            page.locator('a[data-service="Ključevi i daljinski"]').tap()
            self.assertEqual(page.evaluate("location.hash"), "#termin")
            self.assertEqual(page.locator("#fService").input_value(), "Ključevi i daljinski")

        self.exercise_browsers(check)

    def test_gallery_tile_opens_on_first_tap(self):
        def check(page):
            page.goto(self.origin, wait_until="domcontentloaded")
            tile = page.locator("a.gallery-tile-link").first
            self.assertTrue((tile.get_attribute("href") or "").startswith("https://"))
            with page.expect_popup(timeout=12000):
                tile.tap()

        self.exercise_browsers(check)

    def test_failed_map_releases_scroll_trap(self):
        def check(page):
            page.route(
                re.compile(r".*/maplibre-gl@5\.6\.0/dist/maplibre-gl\.js.*"),
                lambda route: route.abort(),
            )
            page.goto(self.origin, wait_until="domcontentloaded")
            page.locator("#globeScroll").scroll_into_view_if_needed()
            expect(page.locator("#globeScroll")).to_have_class(re.compile("is-fallback"), timeout=12000)
            height = page.locator("#globeScroll").evaluate(
                "(el) => el.getBoundingClientRect().height"
            )
            self.assertLess(height, 800)
            self.assertIn("google.com/maps/dir", page.locator(".map-quick-link").get_attribute("href"))

        self.exercise_browsers(check)


if __name__ == "__main__":
    unittest.main()
