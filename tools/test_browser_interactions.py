"""Browser smoke checks for one-tap navigation on the actual static site.

Run: python -m unittest tools.test_browser_interactions
Requires: pip install playwright; python -m playwright install chromium
"""
import functools
import os
import http.server
import re
import threading
import unittest
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class SiteInteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler, directory=str(ROOT)
        )
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.server_thread = threading.Thread(
            target=cls.server.serve_forever, daemon=True
        )
        cls.server_thread.start()
        cls.url = "http://127.0.0.1:" + str(cls.server.server_port) + "/"
        cls.playwright = sync_playwright().start()
        engine = os.environ.get("BROWSER_ENGINE", "chromium")
        if engine not in ("chromium", "webkit"):
            raise ValueError("Expected chromium or webkit BROWSER_ENGINE")
        cls.browser = getattr(cls.playwright, engine).launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join(timeout=4)

    def setUp(self):
        mobile_device = dict(self.playwright.devices["iPhone 13"])
        mobile_device.pop("default_browser_type", None)
        self.context = self.browser.new_context(
            **mobile_device,
            reduced_motion="reduce",
        )
        self.page = self.context.new_page()
        self.page.goto(self.url, wait_until="load", timeout=45000)

    def tearDown(self):
        self.context.close()

    def test_initial_page_has_no_blocking_loader(self):
        self.assertEqual(self.page.locator("#preloader").count(), 0)
        self.assertEqual(self.page.locator("#spinner").count(), 0)
        expect(self.page.locator(".navbar-toggler")).to_be_visible()
        expect(self.page.locator("#header-carousel")).to_be_visible()

    def test_mobile_menu_section_link_works_on_one_tap(self):
        self.page.locator(".navbar-toggler").tap()
        expect(self.page.locator("#navbarCollapse")).to_have_class(
            re.compile(r"\bshow\b")
        )
        self.page.locator("#navbarCollapse a[href='#o-nama']").tap()
        expect(self.page).to_have_url(re.compile(r"#o-nama$"))
        expect(self.page.locator("#navbarCollapse")).not_to_have_class(
            re.compile(r"\bshow\b")
        )

    def test_hero_booking_link_works_on_first_tap(self):
        self.page.locator(
            "#header-carousel .carousel-item.active a[href='#termin']"
        ).first.tap()
        expect(self.page).to_have_url(re.compile(r"#termin$"))
        expect(self.page.locator("#smsForm")).to_be_attached()

    def test_service_booking_works_in_one_tap_and_preselects(self):
        self.page.locator(
            ".service .nav [data-bs-target='#tab-pane-6']"
        ).tap()
        self.page.locator(
            "#tab-pane-6 a[data-service='Ključevi i daljinski']"
        ).tap()
        expect(self.page).to_have_url(re.compile(r"#termin$"))
        expect(self.page.locator("#fService")).to_have_value(
            "Ključevi i daljinski"
        )

    def test_gallery_photo_opens_with_first_tap(self):
        # Capture the activation without contacting external social websites.
        self.page.evaluate("""() => {
            const tile = document.querySelector('[data-gallery-link]');
            window.__galleryTapCount = 0;
            tile.addEventListener('click', event => {
                event.preventDefault();
                window.__galleryTapCount += 1;
            });
        }""")
        self.page.locator("[data-gallery-link]").first.tap()
        self.assertEqual(self.page.evaluate("window.__galleryTapCount"), 1)

    def test_back_to_top_works_on_one_tap(self):
        self.page.evaluate("window.scrollTo(0, 1400)")
        expect(self.page.locator("#backTop")).to_have_class(
            re.compile(r"\bis-visible\b")
        )
        self.page.locator("#backTop").tap()
        self.page.wait_for_function("window.scrollY <= 4", timeout=5000)

    def test_desktop_nav_link_works_on_first_click(self):
        desktop = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            reduced_motion="reduce",
        )
        try:
            page = desktop.new_page()
            page.goto(self.url, wait_until="load", timeout=45000)
            page.locator(".navbar-nav a[href='#usluge']").click()
            expect(page).to_have_url(re.compile(r"#usluge$"))
        finally:
            desktop.close()


if __name__ == "__main__":
    unittest.main()
