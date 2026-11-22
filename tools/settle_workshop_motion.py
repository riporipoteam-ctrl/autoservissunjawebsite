"""Give the opening a real sticky runway; verify pause with a physical pointer."""
from pathlib import Path
import sys


def replace(s, a, b):
    if s.count(a) != 1:
        raise ValueError(f'Expected exactly one occurrence of {a[:144]!r}')
    return s.replace(a,b,1)


def site():
    p=Path('css/workshop-motion.css')
    s=p.read_text()
    s=replace(s,'#workshopStory{min-width:0}', '''#workshopStory{min-width:0}
/* Section targets own their offsets. Native focus on the sticky toolbar must not scroll the page. */
html[data-wm-ready='1']{scroll-padding-top:0}''')
    s=replace(s,' html[data-workshop-motion=full] #workshopStory #pocetna{padding-bottom:clamp(240px,51svh,575px)}', ''' /* A sticky child travels inside the section's content box, not its padding. */
 html[data-workshop-motion=full] #workshopStory #pocetna::after{content:'';display:block;height:clamp(240px,51svh,575px)}''')
    p.write_text(s)
    p=Path('js/workshop-motion.js')
    s=p.read_text()
    s=replace(s, '''    const anchor = hero.getBoundingClientRect().bottom <= window.innerHeight * .28 ? story.querySelector('#usluge') : null;
    const anchorTop = anchor?.getBoundingClientRect().top;
    paused = !paused;
    readMode();
    if (anchor) {
      const shift = anchor.getBoundingClientRect().top - anchorTop;
      if (Math.abs(shift) > 1) window.scrollBy({top:shift,behavior:'instant'});
    }''', '''    const y = window.scrollY;
    const navHeight = document.getElementById('wmHeader')?.offsetHeight || 0;
    const heroRect = hero.getBoundingClientRect();
    const anchor = heroRect.bottom <= window.innerHeight * .55 ? story.querySelector('#usluge') : null;
    const anchorTop = anchor?.getBoundingClientRect().top;
    const wasFull = mode === 'full';
    const previousAnchor = root.style.overflowAnchor;
    root.style.overflowAnchor = 'none';
    paused = !paused;
    readMode();
    const below = anchor ? anchor.getBoundingClientRect().top + window.scrollY - anchorTop : y;
    const inOpening = wasFull && paused && !anchor && y > 0 && y <= hero.offsetHeight + heroRect.top - navHeight + y;
    const destination = Math.max(0, inOpening ? heroRect.top + y - navHeight : below);
    if (Math.abs(window.scrollY - destination) > 1) window.scrollTo({top:destination,behavior:'instant'});
    requestAnimationFrame(() => { root.style.overflowAnchor = previousAnchor; });''')
    # The opening check uses its original viewport bounds, before the shorter paused layout.
    s=replace(s,"wasFull && paused && !anchor && y > 0 && y <= hero.offsetHeight + heroRect.top - navHeight + y", "wasFull && paused && !anchor && y > 0 && heroRect.bottom > navHeight")
    p.write_text(s)
    p=Path('index.html')
    s=p.read_text()
    s=replace(s,'css/workshop-motion.css?v=2.2','css/workshop-motion.css?v=2.3')
    s=replace(s,'js/workshop-motion.js?v=2.1','js/workshop-motion.js?v=2.2')
    p.write_text(s)


def test(filename):
    p=Path(filename)
    s=p.read_text()
    s=replace(s,"        gallery_photo.scroll_into_view_if_needed()\n        assert", "        frames(p)\n        assert")
    s=replace(s,"        old_top=p.locator('#galerija').evaluate('e => e.getBoundingClientRect().top')\n        toggle=p.locator('[data-wm-control]')\n        toggle.click()", '''        toggle=p.locator('[data-wm-control]')
        def press_motion():
            b=toggle.bounding_box()
            x,y=b['x']+b['width']/2,b['y']+b['height']/2
            assert toggle.evaluate('(e,xy)=>e.contains(document.elementFromPoint(...xy))',[x,y]), b
            if w<=820:
                p.touchscreen.tap(x,y)
            else:
                p.mouse.click(x,y)
        frames(p)
        old_top=p.locator('#galerija').evaluate('e => e.getBoundingClientRect().top')
        press_motion()''')
    s=replace(s,"        toggle.click()\n        expect(root).to_have_attribute('data-workshop-motion',mode)", "        press_motion()\n        expect(root).to_have_attribute('data-workshop-motion',mode)")
    s=replace(s,"    p.wait_for_function('''() => {let top=document.querySelector('#usluge').getBoundingClientRect().top;return top >= 61 && top <= 95;}''')", "    p.wait_for_function('''() => {let top=document.querySelector('#usluge').getBoundingClientRect().top;return top >= 61 && top <= 95;}''')\n    frames(p)")
    s=replace(s,"            p.wait_for_timeout(800)", "            p.wait_for_timeout(1150)")
    s=replace(s,"    print('Protected intro played in order:", "    print('Protected intro played in order:")
    s=replace(s,"if failures or BROWSER_ERRORS:\n    raise SystemExit('\\n'.join(failures+BROWSER_ERRORS))\nif ENGINE=='chromium':\n    make_review()", '''if ENGINE=='chromium':
    try:
        make_review()
    except FileNotFoundError as e:
        if not failures:
            raise
        print(f'Review overview incomplete: {e}',flush=True)
if failures or BROWSER_ERRORS:
    raise SystemExit('\\n'.join(failures+BROWSER_ERRORS))''')
    p.write_text(s)


if sys.argv[1]=='site':
    site()
else:
    test(sys.argv[2])
