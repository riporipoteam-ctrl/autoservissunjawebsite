"""Capture actual, unmodified autosunja.com visuals for an off-site launch trailer.

Produces desktop/mobile scroll recordings and screenshots. Does not deploy
anything to the website, and doesn't synthesize fake interface screens.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path("trailer_capture")
OUT.mkdir(exist_ok=True)
URL = "https://autosunja.com/?skipIntro=1"

async def capture_one(browser, name, width, height, duration_ms, dpr=1):
    context = await browser.new_context(
        viewport={"width":width,"height":height},
        device_scale_factor=dpr,
        locale="bs-BA", timezone_id="Europe/Sarajevo",
        record_video_dir=str(OUT),
        record_video_size={"width":width,"height":height},
        reduced_motion="no-preference"
    )
    page = await context.new_page()
    errors=[]
    page.on("pageerror",lambda exc: errors.append(str(exc)[:200]))
    await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2800)
    await page.evaluate("document.documentElement.style.scrollBehavior='auto'")
    await page.screenshot(path=str(OUT/f"{name}-hero.png"),animations="disabled")
    scroll_height=await page.evaluate("Math.max(document.body.scrollHeight,document.documentElement.scrollHeight)")
    print(name,"height",scroll_height,"page_errors",errors,flush=True)
    # True, continuous browser recording rather than fake still image pan.
    await page.evaluate("""async duration => {
      await new Promise(resolve => {
        const maxScroll = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight) - innerHeight;
        const start = performance.now();
        function tick(now) {
          const fraction = Math.min(1, (now-start)/duration);
          // Linear page velocity with gentle start and end.
          const ease = fraction < .08 ? fraction*fraction/(.08) : fraction > .92 ? 1-(1-fraction)*(1-fraction)/.08 : fraction;
          window.scrollTo(0, Math.round(maxScroll*ease));
          if (fraction < 1) requestAnimationFrame(tick);
          else resolve();
        }
        requestAnimationFrame(tick);
      });
    }""", duration_ms)
    await page.wait_for_timeout(800)
    await page.screenshot(path=str(OUT/f"{name}-end.png"),animations="disabled")
    for section,selector in (
        ("about","#o-nama"),("services","#usluge"),("gallery","#galerija"),
        ("location","#lokacija"),("contact","#kontakt")):
        loc=page.locator(selector)
        if await loc.count():
            try:
                await loc.first.scroll_into_view_if_needed(timeout=3000)
                await page.wait_for_timeout(250)
                await page.screenshot(path=str(OUT/f"{name}-{section}.png"),animations="disabled")
            except Exception as exc:
                print("section_skip",section,str(exc)[:120],flush=True)
    await page.close()
    video=page.video
    if video is not None:
        await video.save_as(str(OUT/f"{name}-scroll.webm"))
    await context.close()
    print("CAPTURED",name,"video", (OUT/f"{name}-scroll.webm").stat().st_size,flush=True)

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(args=[
            "--disable-dev-shm-usage","--no-sandbox",
            "--use-gl=swiftshader","--enable-webgl"
        ])
        await capture_one(browser,"desktop",1600,900,14000)
        await capture_one(browser,"mobile",430,932,8500)
        await browser.close()

if __name__=="__main__":
    asyncio.run(main())
