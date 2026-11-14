"""Record a clean, genuine page scroll from the real live site for the film."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import time
OUT=Path("trailer_full_page");OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox","--disable-dev-shm-usage","--use-gl=swiftshader"])
    c=b.new_context(viewport={"width":1600,"height":900},device_scale_factor=1,
                    locale="bs-BA",timezone_id="Europe/Sarajevo",reduced_motion="no-preference")
    pg=c.new_page()
    pg.goto("https://autosunja.com/?skipIntro=1",wait_until="domcontentloaded",timeout=90000)
    pg.wait_for_timeout(2800)
    # Visiting sections triggers the site's lazy image loading and scroll reveals.
    height=pg.evaluate("document.documentElement.scrollHeight")
    print("REAL PAGE HEIGHT",height,flush=True)
    for y in range(0, min(height,16000), 450):
        pg.evaluate("(y) => window.scrollTo({top:y,behavior:'instant'})",y)
        pg.wait_for_timeout(95)
    pg.wait_for_timeout(1400)
    pg.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    pg.wait_for_timeout(350)
    # Capture exact page assets and layout, not an AI re-creation.
    pg.screenshot(path=str(OUT/"actual-site-full-page.png"),full_page=True,
                  animations="disabled",timeout=90000)
    print("FULL SCREENSHOT", (OUT/"actual-site-full-page.png").stat().st_size,flush=True)
    for name,sel in [("hero","#header-carousel"),("about","#o-nama"),("services","#usluge"),
                      ("gallery","#galerija"),("location","#lokacija"),("contact","#kontakt")]:
        loc=pg.locator(sel)
        if loc.count():
            loc.first.scroll_into_view_if_needed(timeout=12000)
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(OUT/f"{name}.png"),animations="disabled")
            print("SECTION",name,flush=True)
    c.close();b.close()
