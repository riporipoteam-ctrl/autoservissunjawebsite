"""Apply narrowly scoped motion draft fixes and prepare its review tests."""
from pathlib import Path
import sys


def require_replace(s, a, b):
    if s.count(a) != 1:
        raise ValueError(f'Expected exactly one occurrence of {a[:144]!r}')
    return s.replace(a,b,1)


def site():
    p=Path('js/main.js')
    s=p.read_text()
    s=require_replace(s, '''        var el = document.getElementById("navbarCollapse");
        if (!el || !el.classList.contains("show")) return;
        try {''', '''        var el = document.getElementById("navbarCollapse");
        if (!el) return;
        var toggle = document.querySelector(".navbar-toggler");
        // Bootstrap ignores hide() while an opening transition is in progress.
        // Complete that transition now so this same tap can close the menu.
        if (el.classList.contains("collapsing") && toggle && toggle.getAttribute("aria-expanded") === "true") {
            el.dispatchEvent(new Event("transitionend"));
        }
        if (!el.classList.contains("show")) return;
        try {''')
    s=require_replace(s, '''        var toggle = document.querySelector(".navbar-toggler");
        if (toggle) {''', '''        if (toggle) {''')
    p.write_text(s)
    p=Path('css/workshop-motion.css')
    s=p.read_text()
    s=require_replace(s, '.wm-gauge{width:118%;inset:-16% -2% auto auto;', '.wm-gauge{width:118%;inset:-16% 0 auto auto;')
    p.write_text(s)
    p=Path('index.html')
    s=p.read_text()
    s=require_replace(s,'css/workshop-motion.css?v=2.1','css/workshop-motion.css?v=2.2')
    s=require_replace(s,'js/main.js?v=40.2','js/main.js?v=40.3')
    p.write_text(s)


def reviewer(filename):
    p=Path(filename)
    s=p.read_text()
    s=require_replace(s,'from playwright.sync_api import sync_playwright, expect','from playwright.sync_api import sync_playwright, expect\nimport imageio_ffmpeg\nimport traceback')
    s=require_replace(s,"        check_images(p,p.locator('#header-carousel .carousel-item.active img'))", "        expect(p.locator('#header-carousel .carousel-item').nth(n)).to_have_class(re.compile(r'\\bactive\\b'))\n        check_images(p,p.locator('#header-carousel .carousel-item.active img'))")
    s=require_replace(s,"    p.locator('#header-carousel .carousel-control-prev').click()", "    expect(p.locator('#header-carousel .carousel-item').first).to_have_class(re.compile(r'\\bactive\\b'))\n    p.locator('#header-carousel .carousel-control-prev').click()")
    s=require_replace(s,"    p.locator('#header-carousel [data-bs-slide-to=\"0\"]').click()", "    expect(p.locator('#header-carousel .carousel-item').nth(2)).to_have_class(re.compile(r'\\bactive\\b'))\n    p.locator('#header-carousel [data-bs-slide-to=\"0\"]').click()")
    s=require_replace(s,"        expect(p.locator('#galerija [data-gallery-link]')).to_have_count(5)", '''        expect(p.locator('#galerija [data-gallery-link]')).to_have_count(5)
        gallery_photo = p.locator('#galerija .wm-frame-photo').first
        gallery_photo.scroll_into_view_if_needed()
        assert gallery_photo.evaluate("""el => {
          const r=el.getBoundingClientRect();
          const x=r.left+r.width/2, y=Math.min(r.bottom-5, Math.max(r.top+5, (65+innerHeight-65)/2));
          return document.elementFromPoint(x,y)?.closest('[data-gallery-link]') === el.parentElement.querySelector('[data-gallery-link]');
        }"""), 'Gallery photo center does not open its post' ''')
    s=require_replace(s,"            expect(img).to_have_attribute('data-fallback-applied','1')", "            if 'galerija' in s:\n                at(p,'#galerija')\n            img.evaluate('e => e.loading = \"eager\"')\n            expect(img).to_have_attribute('data-fallback-applied','1')")
    s=require_replace(s,"['ffmpeg','-hide_banner'", "[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner'")
    s=require_replace(s,"'-b:v','365k','-maxrate','435k','-bufsize','630k'", "'-crf','20','-maxrate','1750k','-bufsize','2500k'")
    s=require_replace(s,"        for i,(selector,title) in enumerate(SECTIONS,4):", "        for i,(selector,title) in enumerate(SECTIONS,4):")
    s=s.replace('            print(failures[-1],flush=True)', '            print(failures[-1],flush=True)\n            traceback.print_exc()')
    p.write_text(s)


if sys.argv[1]=='site':
    site()
else:
    reviewer(sys.argv[2])
