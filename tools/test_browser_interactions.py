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
        self.page.goto(self.url + "?skipIntro=1", wait_until="load", timeout=45000)

    def tearDown(self):
        self.context.close()

    def test_v24_reload_resets_anchor_and_scroll_to_hero(self):
        self.page.locator(".navbar-toggler").tap()
        self.page.locator("#navbarCollapse a[href='#usluge']").tap()
        expect(self.page).to_have_url(re.compile(r"#usluge$"))
        self.assertGreater(self.page.evaluate("window.scrollY"), 200)
        self.page.reload(wait_until="load", timeout=45000)
        self.page.wait_for_function(
            "() => location.hash === '' && scrollY < 6", timeout=7000
        )
        self.assertEqual(self.page.evaluate("location.hash"), "")
        self.assertEqual(
            self.page.locator("#header-carousel .carousel-item.active").count(), 1
        )
        self.page.evaluate("window.scrollTo(0, 1700)")
        self.assertGreater(self.page.evaluate("window.scrollY"), 200)
        self.page.reload(wait_until="load", timeout=45000)
        self.page.wait_for_function(
            "() => location.hash === '' && scrollY < 6", timeout=7000
        )

    def test_v24_map_runs_staged_fly_to_on_first_visible_load(self):
        context = self.browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True, has_touch=True, reduced_motion="no-preference",
        )
        context.add_init_script("""
            window.__mapJumps = [];
            class FakeMap {
                constructor(opts) { this.options = opts; this.callbacks = {}; }
                on(name, cb) {
                    this.callbacks[name] = cb;
                    if (name === 'load') setTimeout(cb, 25);
                    return this;
                }
                resize() {}
                setProjection() {}
                jumpTo(opts) { window.__mapJumps.push(opts); return this; }
            }
            class FakePopup { constructor(){} setHTML(){ return this; } }
            class FakeMarker {
                constructor(){}
                setLngLat(){ return this; }
                setPopup(){ return this; }
                addTo(){ return this; }
                togglePopup(){ return this; }
                remove(){}
            }
            window.maplibregl = {Map: FakeMap, Popup: FakePopup, Marker: FakeMarker};
        """)
        try:
            pg = context.new_page()
            pg.goto(self.url, wait_until="domcontentloaded", timeout=45000)
            pg.evaluate("""() => {
                const w = document.querySelector("#globeScroll");
                window.scrollTo({top: w.offsetTop + 10, behavior: 'instant'});
            }""")
            pg.wait_for_function("window.__mapJumps.length > 0", timeout=12000)
            low = pg.evaluate("window.__mapJumps.at(-1).zoom")
            pg.evaluate("""() => {
                const w = document.querySelector("#globeScroll");
                window.scrollTo({top: w.offsetTop + (w.offsetHeight - innerHeight) * .7, behavior: 'instant'});
            }""")
            pg.wait_for_function("(low) => window.__mapJumps.at(-1).zoom > low + 2", arg=low, timeout=8000)
            high = pg.evaluate("window.__mapJumps.at(-1).zoom")
            self.assertGreater(high, low)
            pg.evaluate("""() => {
                const w = document.querySelector("#globeScroll");
                window.scrollTo({top: w.offsetTop + 10, behavior:'instant'});
            }""")
            pg.wait_for_function("(high) => window.__mapJumps.at(-1).zoom < high - 2", arg=high, timeout=8000)
        finally:
            context.close()

    def test_v29_completed_globe_never_rewinds_or_rerenders_on_scroll_up(self):
        context = self.browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True, has_touch=True, reduced_motion="no-preference",
        )
        context.add_init_script("""
            window.__mapJumps = [];
            window.__markerRemoves = 0;
            class FakeMap {
                constructor(opts) { this.options = opts; this.callbacks = {}; }
                on(name, cb) {
                    this.callbacks[name] = cb;
                    if (name === 'load') setTimeout(cb, 20);
                    return this;
                }
                resize() {}
                setProjection() {}
                jumpTo(opts) { window.__mapJumps.push(opts); return this; }
            }
            class FakePopup { constructor(){} setHTML(){ return this; } }
            class FakeMarker {
                constructor(){}
                setLngLat(){ return this; }
                setPopup(){ return this; }
                addTo(){ return this; }
                togglePopup(){ return this; }
                remove(){ window.__markerRemoves++; }
            }
            window.maplibregl = {Map: FakeMap, Popup: FakePopup, Marker: FakeMarker};
        """)
        try:
            page = context.new_page()
            page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
            page.evaluate("""() => {
                const w = document.getElementById("globeScroll");
                window.scrollTo(0, w.offsetTop + w.offsetHeight - innerHeight + 8);
            }""")
            page.wait_for_function(
                "() => document.querySelector('#globeScroll').classList.contains('globe-complete')",
                timeout=8000,
            )
            initial_count = page.evaluate("window.__mapJumps.length")
            self.assertGreaterEqual(initial_count, 1)
            final = page.evaluate("window.__mapJumps.at(-1)")
            self.assertAlmostEqual(final["zoom"], 16.2, delta=.1)
            page.evaluate("""() => {
                const w = document.getElementById("globeScroll");
                window.scrollTo(0, w.offsetTop + 5);
            }""")
            page.wait_for_timeout(240)
            self.assertEqual(page.evaluate("window.__mapJumps.length"), initial_count)
            self.assertEqual(page.evaluate("window.__markerRemoves"), 0)
            self.assertTrue(page.locator("#globeScroll").evaluate(
                "(w) => w.classList.contains('globe-complete')"
            ))
            page.evaluate("""() => {
                const w = document.getElementById("globeScroll");
                window.scrollTo(0, w.offsetTop + w.offsetHeight - innerHeight + 8);
                window.dispatchEvent(new Event("resize"));
                window.scrollTo(0, 0);
            }""")
            page.wait_for_timeout(220)
            self.assertEqual(page.evaluate("window.__mapJumps.length"), initial_count)
        finally:
            context.close()


    def test_v30_finished_map_releases_upward_scroll_without_page_jump(self):
        context = self.browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True, has_touch=True, reduced_motion="no-preference",
        )
        context.add_init_script("""
            window.__mapJumps = [];
            class FakeMap {
                on(name, cb) {
                    if (name === 'load') setTimeout(cb, 25);
                    return this;
                }
                resize() {}
                setProjection() {}
                jumpTo(camera) { window.__mapJumps.push(camera); return this; }
                easeTo(camera) { window.__mapJumps.push(camera); return this; }
                stop() {}
            }
            class FakePopup { setHTML(){ return this; } }
            class FakeMarker {
                setLngLat(){return this;} setPopup(){return this;}
                addTo(){return this;} togglePopup(){return this;}
            }
            window.maplibregl = {Map:FakeMap, Popup:FakePopup, Marker:FakeMarker};
        """)
        try:
            page = context.new_page()
            page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
            page.evaluate("""() => {
                const map = document.querySelector('#globeScroll');
                const target = map.offsetTop + (map.offsetHeight - innerHeight) * .99;
                window.scrollTo(0, target);
                window.__contactBeforeFinish =
                    document.querySelector('#kontakt').getBoundingClientRect().top;
            }""")
            page.wait_for_function(
                "() => document.querySelector('#globeScroll').classList.contains('globe-complete')",
                timeout=10000,
            )
            state = page.evaluate("""() => {
                const w = document.querySelector('#globeScroll');
                return {
                    height: w.getBoundingClientRect().height,
                    viewport: innerHeight,
                    stickyPosition: getComputedStyle(w.querySelector('.globe-sticky')).position,
                    contactShift: document.querySelector('#kontakt').getBoundingClientRect().top -
                        window.__contactBeforeFinish,
                    jumps: window.__mapJumps.length,
                };
            }""")
            self.assertLessEqual(state["height"], state["viewport"] + 2)
            self.assertEqual(state["stickyPosition"], "relative")
            self.assertLessEqual(abs(state["contactShift"]), 6)
            # Mobile WebKit does not implement Playwright's synthetic wheel;
            # use an actual wheel on Chromium and a native page scroll there.
            if os.environ.get("BROWSER_ENGINE", "chromium") == "webkit":
                page.evaluate("window.scrollBy(0, -260)")
            else:
                page.mouse.wheel(0, -260)
            page.wait_for_function(
                "() => scrollY < document.querySelector('#globeScroll').offsetTop - 100",
                timeout=5000,
            )
            self.assertEqual(page.evaluate("window.__mapJumps.length"), state["jumps"])
        finally:
            context.close()

    def test_v29_scrolling_past_map_before_load_finishes_once(self):
        context = self.browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True, has_touch=True, reduced_motion="no-preference",
        )
        context.add_init_script("""
            window.__mapJumps = [];
            class FakeMap {
                constructor(o) { this.options=o; this.callbacks={}; window.__mapStarted=true; }
                on(name, cb) {
                    this.callbacks[name]=cb;
                    if (name === 'load') setTimeout(cb, 750);
                    return this;
                }
                resize() {}
                setProjection() {}
                jumpTo(o) { window.__mapJumps.push(o); return this; }
            }
            class FakePopup { constructor(){} setHTML(){return this;} }
            class FakeMarker {
                setLngLat(){return this;} setPopup(){return this;}
                addTo(){return this;} togglePopup(){return this;}
                remove(){}
            }
            window.maplibregl={Map:FakeMap,Popup:FakePopup,Marker:FakeMarker};
        """)
        try:
            pg=context.new_page()
            pg.goto(self.url, wait_until="domcontentloaded")
            pg.evaluate("""() => {
                const w=document.getElementById("globeScroll");
                window.scrollTo(0, w.offsetTop + 20);
            }""")
            pg.wait_for_function("window.__mapStarted === true", timeout=5000)
            pg.evaluate("""() => {
                const w=document.getElementById("globeScroll");
                window.scrollTo(0, w.offsetTop + w.offsetHeight + 250);
            }""")
            pg.wait_for_function(
                "document.getElementById('globeScroll').classList.contains('globe-complete')",
                timeout=8000,
            )
            self.assertAlmostEqual(
                pg.evaluate("window.__mapJumps.at(-1).zoom"), 16.2, delta=.1
            )
            before=pg.evaluate("window.__mapJumps.length")
            pg.evaluate("window.scrollTo(0, 0)")
            pg.wait_for_timeout(200)
            self.assertEqual(pg.evaluate("window.__mapJumps.length"), before)
        finally:
            context.close()

    def test_v31_intro_plays_original_logo_only_and_releases_page(self):
        context = self.browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True, has_touch=True, reduced_motion="no-preference",
        )
        try:
            page = context.new_page()
            page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
            expect(page.locator("#sunjaIntroVideo")).to_have_count(1)
            expect(page.locator("#sunjaIntro")).to_be_visible()
            self.assertEqual(page.locator("#sunjaIntroProgress, #sunjaIntroLoading").count(), 0)
            page.locator("#sunjaIntroVideo").evaluate(
                "(v) => v.dispatchEvent(new Event('ended'))"
            )
            page.wait_for_function(
                "() => !document.documentElement.classList.contains('sunja-intro-active')",
                timeout=7000,
            )
            expect(page.locator("#header-carousel")).to_be_visible()
            page.reload(wait_until="domcontentloaded", timeout=45000)
            expect(page.locator("#sunjaIntroVideo")).to_have_count(1)
        finally:
            context.close()

    def test_v31_android_and_ios_mobile_callbar_colors(self):
        page = self.page
        theme = page.locator('meta[name="theme-color"][media="(max-width: 991.98px)"]')
        self.assertEqual(theme.get_attribute("content").lower(), "#0b5fa5")
        bar = page.locator(".mobile-callbar")
        expect(bar).to_be_visible()
        self.assertEqual(
            bar.evaluate("(x) => getComputedStyle(x).position"), "fixed"
        )
        self.assertEqual(
            page.locator(".mobile-callbar a.call").evaluate(
                "(x) => getComputedStyle(x).backgroundColor"
            ), "rgb(11, 95, 165)"
        )
        self.assertEqual(
            page.locator(".mobile-callbar a.dir").evaluate(
                "(x) => getComputedStyle(x).backgroundColor"
            ), "rgb(11, 33, 84)"
        )

    def test_mobile_menu_section_link_works_on_one_tap(self):
        self.page.locator(".navbar-toggler").tap()
        expect(self.page.locator("#navbarCollapse")).to_have_class(
            re.compile(r"\bshow\b")
        )
        self.page.evaluate("""() => {
            window.__navTouchDebug = [];
            for (const type of ["pointerdown","touchstart","touchend","pointerup","click"]) {
                document.addEventListener(type, (e) => {
                    const link = e.target && e.target.closest && e.target.closest("a");
                    window.__navTouchDebug.push({
                        type, tag: e.target && e.target.tagName,
                        href: link && link.getAttribute("href"),
                        prevented: e.defaultPrevented,
                        hash: location.hash,
                        expanded: document.querySelector("#navbarCollapse").className
                    });
                }, true);
            }
        }""")
        self.page.locator("#navbarCollapse a[href='#o-nama']").tap()
        self.assertEqual(
            self.page.evaluate("location.hash"), "#o-nama",
            str(self.page.evaluate("window.__navTouchDebug"))
        )
        expect(self.page.locator("#navbarCollapse")).not_to_have_class(
            re.compile(r"\bshow\b")
        )
        # Closing via a section link must not break the next menu opening.
        self.page.locator(".navbar-toggler").tap()
        expect(self.page.locator("#navbarCollapse")).to_have_class(
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

    def test_hero_indicators_have_usable_touch_targets(self):
        dots = self.page.locator(".hero-indicators button")
        self.assertEqual(dots.count(), 3)
        for i in range(3):
            height = dots.nth(i).evaluate(
                "(el) => el.getBoundingClientRect().height"
            )
            self.assertGreaterEqual(height, 40)
        dots.nth(1).tap()
        expect(
            self.page.locator("#header-carousel .carousel-item").nth(1)
        ).to_have_class(re.compile(r"\bactive\b"))

    def test_v22_dock_retracts_over_footer_links(self):
        dock = self.page.locator(".mobile-callbar")
        self.page.evaluate(
            "window.scrollTo(0, document.documentElement.scrollHeight)"
        )
        self.page.wait_for_timeout(180)
        self.assertFalse(self.page.evaluate(
            "document.documentElement.classList.contains('dock-avoiding-action')"
        ))
        self.assertEqual(
            dock.evaluate("(el) => getComputedStyle(el).visibility"), "visible"
        )
        self.assertEqual(
            dock.evaluate("(el) => getComputedStyle(el).opacity"), "1"
        )
        self.assertEqual(
            dock.evaluate("(el) => getComputedStyle(el).pointerEvents"), "auto"
        )
        footer = self.page.locator("#siteFooter")
        clearance = footer.evaluate(
            "(el) => parseFloat(getComputedStyle(el).paddingBottom)"
        )
        self.assertGreaterEqual(clearance, dock.evaluate(
            "(el) => el.getBoundingClientRect().height"
        ))

    def test_v22_footer_is_plain_dark_without_a_photo(self):
        footer = self.page.locator("#siteFooter")
        bg = footer.evaluate("(el) => getComputedStyle(el).backgroundImage")
        self.assertNotIn("url(", bg)
        self.assertIn("gradient", bg)

    def test_v22_about_is_short_and_has_address(self):
        text = self.page.locator("#o-nama p.mb-4").first.inner_text()
        self.assertIn("Hajra Lakovića 38", text)
        self.assertIn("Goražde", text)
        self.assertNotIn("SUV", text)
        self.assertLess(len(text), 280)

    def test_v22_optical_lenses_are_real_svg_and_do_not_block_taps(self):
        self.assertEqual(self.page.locator(".sunja-glass-refract").count(), 0)
        self.assertEqual(self.page.locator("#sunja-glass-distortion").count(), 0)
        header = self.page.locator(".navbar.nav-bar")
        self.assertEqual(header.evaluate(
            "(el) => getComputedStyle(el).backdropFilter"), "none")
        self.assertEqual(header.evaluate(
            "(el) => getComputedStyle(el).backgroundColor"), "rgb(255, 255, 255)")

    def test_v22_desktop_nav_has_no_overlap_underline(self):
        desktop = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            reduced_motion="reduce",
        )
        try:
            pg = desktop.new_page()
            pg.goto(self.url, wait_until="load")
            node = pg.locator(".navbar-nav a[href='#galerija']")
            after = node.evaluate(
                "(el) => getComputedStyle(el, '::after').content"
            )
            self.assertEqual(after, "none")
            node.click()
            expect(pg).to_have_url(re.compile(r"#galerija$"))
        finally:
            desktop.close()

    def test_v213_typography_across_narrow_phone_tablet_desktop(self):
        sizes = (
            (320, 700, 20.5, 13.6),
            (820, 900, 25.5, 15.1),
            (1280, 800, 32.5, 15.1),
        )
        for width, height, heading_limit, copy_limit in sizes:
            with self.subTest(width=width):
                context = self.browser.new_context(
                    viewport={"width": width, "height": height},
                    is_mobile=width <= 767,
                    has_touch=width <= 991,
                    reduced_motion="reduce",
                )
                try:
                    page = context.new_page()
                    page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
                    heading = page.locator("#o-nama h1").evaluate(
                        "(node) => parseFloat(getComputedStyle(node).fontSize)"
                    )
                    copy = page.locator("#o-nama p.mb-4").first.evaluate(
                        "(node) => parseFloat(getComputedStyle(node).fontSize)"
                    )
                    self.assertLessEqual(heading, heading_limit)
                    self.assertLessEqual(copy, copy_limit)
                    self.assertGreaterEqual(copy, 13)
                finally:
                    context.close()

    def test_v214_mobile_dock_is_flush_to_page_edge(self):
        dock = self.page.locator(".mobile-callbar")
        bottom = dock.evaluate("(el) => parseFloat(getComputedStyle(el).bottom)")
        self.assertAlmostEqual(bottom, 0, delta=1)
        footer_pad = self.page.locator("#siteFooter").evaluate(
            "(el) => parseFloat(getComputedStyle(el).paddingBottom)"
        )
        self.assertGreaterEqual(
            footer_pad, dock.evaluate(
                "(el) => el.getBoundingClientRect().height"
            )
        )

    def test_v214_first_tap_on_service_tab_and_gallery_link(self):
        tab = self.page.locator('button[data-bs-target="#tab-pane-2"]')
        tab.tap()
        expect(self.page.locator("#tab-pane-2")).to_have_class(
            re.compile(r"\bactive\b")
        )
        tile = self.page.locator("a.gallery-tile-link").first
        tile.scroll_into_view_if_needed()
        self.assertEqual(
            tile.evaluate("(el) => getComputedStyle(el).transform"), "none"
        )
        self.assertGreaterEqual(float(tile.evaluate(
            "(el) => getComputedStyle(el).opacity"
        )), 0.99)
        self.page.evaluate("""() => {
            const tile = document.querySelector('a.gallery-tile-link');
            window.__oneTapHits = 0;
            tile.addEventListener('click', e => {
                e.preventDefault();
                window.__oneTapHits++;
            });
        }""")
        tile.tap()
        self.assertEqual(self.page.evaluate("window.__oneTapHits"), 1)

    def test_v213_all_mobile_sections_have_compact_typography(self):
        for section in ("o-nama", "usluge", "galerija", "recenzije",
                        "lokacija", "kontakt"):
            title = self.page.locator("#" + section + " h1").first
            size = title.evaluate("(el) => parseFloat(getComputedStyle(el).fontSize)")
            self.assertLessEqual(size, 21, section)

        about_copy = self.page.locator("#o-nama p.mb-4").first
        size = about_copy.evaluate(
            "(el) => parseFloat(getComputedStyle(el).fontSize)"
        )
        self.assertLessEqual(size, 13.6)
        feature_copy = self.page.locator("#o-nama .ps-3 > span").first
        feature_size = feature_copy.evaluate(
            "(el) => parseFloat(getComputedStyle(el).fontSize)"
        )
        self.assertLessEqual(feature_size, 13.6)

    def test_v213_text_keeps_booking_and_dock_tap_areas(self):
        for selector in ("#o-nama a[href='#termin']",
                         ".mobile-callbar .call",
                         ".mobile-callbar .dir"):
            el = self.page.locator(selector).first
            height = el.evaluate("(node) => node.getBoundingClientRect().height")
            self.assertGreaterEqual(height, 44, selector)

    def test_v231_all_service_descriptions_are_compact(self):
        expected = {
            "tab-pane-1": "Dijagnostika i otkrivanje kvarova na vozilu.",
            "tab-pane-2": "Održavanje i popravke Peugeot vozila.",
            "tab-pane-3": "Zamjena motornog ulja i filtera.",
            "tab-pane-4": "Zamjena zupčastog remena",
            "tab-pane-5": "Dijagnostika i popravka električnih sistema",
            "tab-pane-6": "Izrada i programiranje auto ključeva",
        }
        for tab_id, text in expected.items():
            with self.subTest(tab=tab_id):
                para = self.page.locator("#" + tab_id + " p.mb-4").first
                description = para.inner_text()
                self.assertIn(text, description)
                self.assertLess(len(description), 105)

    def test_v21_mobile_type_is_genuinely_smaller(self):
        title = self.page.locator("#o-nama h1")
        para = self.page.locator("#o-nama > .container p").first
        title_size = title.evaluate("(node) => parseFloat(getComputedStyle(node).fontSize)")
        para_size = para.evaluate("(node) => parseFloat(getComputedStyle(node).fontSize)")
        self.assertLessEqual(title_size, 26)
        self.assertLessEqual(para_size, 15)

    def test_v21_gallery_photo_fills_natural_width_without_crop(self):
        img = self.page.locator("[data-gallery-img]").first
        img.scroll_into_view_if_needed()
        img.evaluate("(node) => node.decode()")
        rect = img.evaluate("""(node) => {
            const p = node.parentElement.getBoundingClientRect();
            const b = node.getBoundingClientRect();
            return {
                imageWidth: b.width, parentWidth: p.width,
                imageRatio: b.width / b.height,
                naturalRatio: node.naturalWidth / node.naturalHeight,
                fit: getComputedStyle(node).objectFit
            };
        }""")
        self.assertGreater(rect["imageWidth"] / rect["parentWidth"], 0.98)
        self.assertAlmostEqual(rect["imageRatio"], rect["naturalRatio"], delta=0.05)
        self.assertEqual(rect["fit"], "contain")

    def test_v212_dock_hides_when_booking_button_would_be_covered(self):
        dock = self.page.locator(".mobile-callbar")
        positions = [
            0, 550, 1000, 1550, 2100, 2800,
            600, 2400, 100, 3200, 0
        ]
        for pos in positions:
            self.page.evaluate("(y) => window.scrollTo(0, y)", pos)
            self.page.wait_for_timeout(55)
            visible = dock.evaluate("""(el) => {
                const style = getComputedStyle(el);
                const box = el.getBoundingClientRect();
                return {
                    visibility: style.visibility,
                    opacity: style.opacity,
                    display: style.display,
                    bottomOffset: innerHeight - box.bottom,
                    pointer: style.pointerEvents
                };
            }""")
            self.assertEqual(visible["visibility"], "visible", pos)
            self.assertEqual(visible["opacity"], "1", pos)
            self.assertEqual(visible["display"], "flex", pos)
            self.assertEqual(visible["pointer"], "auto", pos)
            self.assertLessEqual(abs(visible["bottomOffset"]), 2, pos)
        self.page.locator("#o-nama a[href='#termin']").tap()
        expect(self.page).to_have_url(re.compile(r"#termin$"))

    def test_v212_footer_has_no_unstyled_body_tail(self):
        self.assertEqual(
            self.page.locator("body").evaluate(
                "(el) => getComputedStyle(el).paddingBottom"
            ), "0px"
        )
        self.assertGreaterEqual(
            self.page.locator("#siteFooter").evaluate(
                "(el) => parseFloat(getComputedStyle(el).paddingBottom)"
            ), self.page.locator(".mobile-callbar").evaluate(
                "(el) => el.getBoundingClientRect().height"
            )
        )

    def test_v21_three_glass_surfaces_stay_accessible(self):
        self.assertEqual(self.page.locator(".sunja-liquid-header").count(), 0)
        self.assertEqual(self.page.locator(".sunja-liquid-bottom").count(), 0)
        self.assertEqual(self.page.locator("#backTop.sunja-liquid-top").count(), 0)
        self.assertEqual(self.page.locator(".mobile-callbar a").count(), 2)
        self.page.locator(".navbar-toggler").tap()
        expect(self.page.locator("#navbarCollapse")).to_have_class(
            re.compile(r"\bshow\b")
        )
        self.page.locator("#navbarCollapse a[href='#o-nama']").tap()
        expect(self.page).to_have_url(re.compile(r"#o-nama$"))

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
