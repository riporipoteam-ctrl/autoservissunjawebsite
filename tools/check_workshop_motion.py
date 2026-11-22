"""Exercise the exact draft in Chromium or WebKit, then record review evidence."""
import json
import os
import re
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from PIL import Image, ImageDraw, ImageOps
from playwright.sync_api import sync_playwright, expect

SIZES = [(1920,1080),(1366,768),(1024,768),(820,1180),(768,1024),(390,844),(360,800)]
SECTIONS = [('#pocetna .wm-pin','opening'),('#usluge','services'),('#galerija','gallery'),('#o-nama','workshop'),('#recenzije','reviews'),('#lokacija','location'),('#globeScroll','map-fallback'),('#kontakt','contact'),('#siteFooter','footer')]
ENGINE = os.environ['BROWSER_ENGINE']
OUT = Path(os.environ.get('CAPTURE_DIR', 'captures')).resolve()
OUT.mkdir(parents=True,exist_ok=True)
TEL = 'tel:+38761297847'
MAPS = re.compile(r'^https://www\.google\.com/maps/dir/\?api=1&destination=Auto\+Servis')
BROWSER_ERRORS = []

class Site(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

http = ThreadingHTTPServer(('127.0.0.1', 0), Site)
Thread(target=http.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{http.server_port}'

def check_images(page, loc):
    for img in loc.all():
        img.evaluate('e => e.loading = "eager"')
        page.wait_for_function('e => e.complete && e.naturalWidth > 0',arg=img.element_handle())

def new_context(browser, w, h, reduce='no-preference', expect_lite=False, script=True, record=False):
    context = browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,has_touch=w<=820,is_mobile=w<=390,reduced_motion=reduce,java_script_enabled=script, **({'record_video_dir':str(OUT/'recording'),'record_video_size':{'width':1024,'height':576}} if record else {}))
    # Use known capability values for layout emulation rather than runner CPU counts.
    context.add_init_script(f"Object.defineProperty(Navigator.prototype,'hardwareConcurrency',{{get:()=>{2 if expect_lite else 8}}});")
    # Capture the site's existing fallback deterministically; the remote tile service
    # is intentionally not validated in this layout suite.
    context.route('**/maplibre-gl@5.6.0/dist/maplibre-gl.js', lambda r: r.abort())
    return context

def start(context, intro=False):
    p = context.new_page()
    p.set_default_timeout(6200)
    p.on('pageerror', lambda error: BROWSER_ERRORS.append(str(error)))
    p.goto(base + ('/' if intro else '/?skipIntro=1'),wait_until='domcontentloaded',timeout=20000)
    return p

def at(p, sel, pad=75):
    p.locator(sel).evaluate('(el,pad) => window.scrollTo({top:Math.max(0,el.getBoundingClientRect().top + scrollY - pad),behavior:"instant"})',pad)
    frames(p)

def jump(p, y):
    p.evaluate('y => window.scrollTo({top:y,behavior:"instant"})',y)
    frames(p)

def frames(p):
    p.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(() => requestAnimationFrame(resolve))))')

def sample(p):
    return p.evaluate('''() => {
      let root=document.documentElement, hero=document.querySelector('#pocetna'), pin=hero.querySelector('.wm-pin');
      return {y:scrollY, pin:pin.getBoundingClientRect().top, position:getComputedStyle(pin).position,
       runway:hero.offsetHeight-pin.offsetHeight, progress:+root.style.getPropertyValue('--wm-progress'),
       dial:+hero.style.getPropertyValue('--wm-hero'), transform:getComputedStyle(hero.querySelector('.wm-needle')).transform,
       photo:getComputedStyle(hero.querySelector('.carousel-item.active img')).transform,
       current:document.querySelector('#motionChapters [aria-current=location]')?.hash || '',
       width:root.clientWidth, document:root.scrollWidth};
    }''')

def fits(p, selector):
    info=p.locator(selector).evaluate('''el => {let r=el.getBoundingClientRect();return [r.left,r.right,document.documentElement.clientWidth,el.clientWidth,el.scrollWidth]}''')
    assert info[0] >= -1 and info[1] <= info[2]+1 and info[4] <= info[3]+2, (selector,info)

def carousel(p):
    p.evaluate("bootstrap.Carousel.getInstance(document.querySelector('#header-carousel')).pause()")
    for n in range(3):
        indicator=p.locator(f'#header-carousel [data-bs-slide-to="{n}"]')
        indicator.click()
        expect(indicator).to_have_attribute('aria-current','true')
        check_images(p,p.locator('#header-carousel .carousel-item.active img'))
    p.locator('#header-carousel .carousel-control-next').click()
    expect(p.locator('#header-carousel [data-bs-slide-to="0"]')).to_have_attribute('aria-current','true')
    p.locator('#header-carousel .carousel-control-prev').click()
    expect(p.locator('#header-carousel [data-bs-slide-to="2"]')).to_have_attribute('aria-current','true')
    p.locator('#header-carousel [data-bs-slide-to="0"]').click()
    expect(p.locator('#header-carousel .carousel-item').first).to_have_class(re.compile(r'\bactive\b'))

def verify_services(p, w):
    at(p,'#usluge')
    for n in range(1,7):
        tab = p.locator(f'#wm-tab-{n}')
        tab.tap() if w <= 390 else tab.click()
        expect(tab).to_have_attribute('aria-selected','true')
        pane = p.locator(f'#tab-pane-{n}')
        expect(pane).to_be_visible()
        expect(pane.locator(f'a[href="{TEL}"]')).to_be_visible()
        check_images(p,pane.locator('img'))
        fits(p,f'#tab-pane-{n} h3')
    p.locator('#wm-tab-6').focus()
    p.keyboard.press('ArrowRight')
    expect(p.locator('#wm-tab-1')).to_have_attribute('aria-selected','true')


def input_nav(p, w):
    at(p,'#pocetna',80)
    if w < 992:
        menu=p.locator('#wmHeader .navbar-toggler')
        menu.tap()
        expect(p.locator('#navbarCollapse')).to_be_visible()
        p.locator('#motionChapters a[href="#usluge"]').tap()
        expect(p.locator('#navbarCollapse')).to_be_hidden()
        expect(menu).to_have_attribute('aria-expanded','false')
        for selector, attr in [('#wmDock .call',TEL),('#wmDock .dir',MAPS)]:
            el=p.locator(selector)
            expect(el).to_have_attribute('href',attr)
            assert el.evaluate('''e => {const r=e.getBoundingClientRect();return r.height>=44 && e.contains(document.elementFromPoint((r.left+r.right)/2,(r.top+r.bottom)/2));}'''), selector
    else:
        p.locator('#motionChapters a[href="#usluge"]').click()
    expect(p).to_have_url(re.compile('#usluge$'))
    p.wait_for_function('''() => {let top=document.querySelector('#usluge').getBoundingClientRect().top;return top >= 61 && top <= 95;}''')
    expect(p.locator('#motionChapters a[href="#usluge"]')).to_have_attribute('aria-current','location')


def viewport(browser,w,h):
    label=f'{w}x{h}'
    path=OUT/label
    path.mkdir(exist_ok=True)
    context=new_context(browser,w,h)
    try:
        p=start(context)
        root=p.locator('html')
        mode='full' if w>=1024 else 'light'
        expect(root).to_have_attribute('data-workshop-motion',mode)
        expect(p.locator('#wm-hero-title')).to_have_text('Auto Servis Šunja')
        expect(p.locator(f'#pocetna a[href="{TEL}"]')).to_be_visible()
        expect(p.locator('#pocetna a.wm-button--paper')).to_have_attribute('href',MAPS)
        expect(p.locator('#globeScroll .map-quick-link')).to_have_attribute('href',MAPS)
        expect(p.locator('#globeScroll')).to_have_class(re.compile(r'\bis-fallback\b'))
        p.evaluate('() => document.fonts.ready')
        p.evaluate("bootstrap.Carousel.getInstance(document.querySelector('#header-carousel')).pause()")
        check_images(p,p.locator('#header-carousel .active picture img'))
        fits(p,'#wm-hero-title')
        for selector in ('#wmHeader .wm-wrap','.wm-hero-copy','.wm-hero-visual','#usluge .service-nav-grid','#galerija .wm-film-grid','#kontakt .wm-number','#siteFooter .wm-footer-grid'):
            fits(p,selector)
        p.screenshot(path=path/'01-first-screen.png')
        before=sample(p)
        if w>=1024:
            assert before['position']=='sticky' and before['runway']>=230, before
            p.mouse.move(w*.6,h*.5)
            p.mouse.wheel(0,int(before['runway']*.51))
            p.wait_for_function("parseFloat(document.querySelector('#pocetna').style.getPropertyValue('--wm-hero')) > .39")
            mid=sample(p)
            assert abs(mid['pin']-before['pin'])<=2 and mid['y']-before['y']>=90,(before,mid)
            assert mid['dial'] > before['dial'] and mid['progress'] > before['progress'] and mid['transform'] != before['transform'] and mid['photo'] != before['photo'], (before,mid)
            p.screenshot(path=path/'02-dial-mid-scroll.png')
            jump(p,before['runway']+100)
            end=sample(p)
            assert end['pin'] < mid['pin']-70 and end['dial']>=.96,(mid,end)
            p.screenshot(path=path/'03-handoff.png')
        else:
            assert before['position']!='sticky' and before['runway']<=1,before
            jump(p,120)
            mid=sample(p)
            assert before['pin']-mid['pin']>=115 and mid['dial']>before['dial'] and mid['progress']>before['progress'],(before,mid)
            end=mid
            p.screenshot(path=path/'02-light-scroll.png')
        assert before['document']<=before['width']+1 and mid['document']<=mid['width']+1,(before,mid)
        input_nav(p,w)
        verify_services(p,w)
        p.locator('#siteFooter [data-svc-link="5"]').click()
        expect(p.locator('#wm-tab-5')).to_have_attribute('aria-selected','true')
        p.locator('#wm-tab-1').click()
        jump(p,0)
        carousel(p)
        at(p,'#galerija')
        start_gallery=p.locator('#galerija').evaluate('e=>[e.style.getPropertyValue("--wm-drift"),getComputedStyle(e.querySelector("img")).transform]')
        jump(p,p.evaluate('scrollY')+min(170,h*.3))
        after_gallery=p.locator('#galerija').evaluate('e=>[e.style.getPropertyValue("--wm-drift"),getComputedStyle(e.querySelector("img")).transform]')
        assert start_gallery != after_gallery, (start_gallery,after_gallery)
        check_images(p,p.locator('#galerija img'))
        expect(p.locator('#galerija [data-gallery-link]')).to_have_count(5)
        # Controls remain available and the page holds place when paused.
        old_top=p.locator('#galerija').evaluate('e => e.getBoundingClientRect().top')
        toggle=p.locator('[data-wm-control]')
        toggle.click()
        expect(root).to_have_attribute('data-workshop-motion','off')
        expect(toggle).to_have_attribute('aria-pressed','true')
        frames(p)
        assert abs(old_top - p.locator('#galerija').evaluate('e => e.getBoundingClientRect().top'))<=5, (old_top,sample(p))
        assert p.locator('#pocetna').evaluate("el=>!el.style.getPropertyValue('--wm-hero')")
        assert p.locator('#galerija').evaluate("el=>!el.style.getPropertyValue('--wm-drift')")
        verify_services(p,w)
        toggle.click()
        expect(root).to_have_attribute('data-workshop-motion',mode)
        expect(toggle).to_have_attribute('aria-pressed','false')
        assert p.locator('#kontakt .wm-number').get_attribute('href')==TEL
        fits(p,'#kontakt .wm-number')
        p.evaluate("bootstrap.Carousel.getInstance(document.querySelector('#header-carousel')).pause()")
        for i,(selector,title) in enumerate(SECTIONS,4):
            at(p,selector)
            el=p.locator(selector)
            if title in ('gallery','workshop'):
                check_images(p,el.locator('img'))
            el.screenshot(path=path/f'{i:02}-{title}.png',timeout=10000)
        jump(p,0)
        p.screenshot(path=path/'14-full-page.png',full_page=True,timeout=14000)
        assert sample(p)['document']<=sample(p)['width']+1
        print(label, mode, f'pin {before["pin"]:.0f}->{mid["pin"]:.0f}', f'dial {before["dial"]:.3f}->{mid["dial"]:.3f}', f'CSS width {before["width"]}/{mid["document"]}',flush=True)
        return {'size':label,'mode':mode,'before':before,'mid':mid,'after':end,'gallery':[start_gallery,after_gallery]}
    finally:
        context.close()


def other_states(browser):
    for reduce,lite in [('reduce',False),('no-preference',True)]:
        c=new_context(browser,1366,768,reduce,expect_lite=lite)
        try:
            p=start(c)
            expect(p.locator('html')).to_have_attribute('data-workshop-motion','off')
            expect(p.locator('[data-wm-control]')).to_be_hidden()
            before=sample(p)
            jump(p,160)
            after=sample(p)
            assert before['pin']-after['pin']>=156 and not after['dial'] and before['transform']==after['transform'],(before,after)
            assert p.evaluate("bootstrap.Carousel.getInstance(document.querySelector('#header-carousel'))._interval === null")
            jump(p,0)
            carousel(p)
            verify_services(p,1366)
            p.screenshot(path=OUT/('reduced-motion.png' if not lite else 'light-device.png'), full_page=False)
        finally:
            c.close()
    c=new_context(browser,390,844,script=False)
    try:
        p=start(c)
        expect(p.locator('#pocetna h1')).to_be_visible()
        expect(p.locator('#motionChapters a[href="#usluge"]')).to_be_visible()
        for n in range(1,7):
            expect(p.locator(f'#tab-pane-{n}')).to_be_visible()
        expect(p.locator('#wmDock .call')).to_have_attribute('href',TEL)
    finally:
        c.close()
    # Golden image URLs are kept unchanged. Force a missing primary to exercise each recovery path.
    c=new_context(browser,390,844)
    try:
        c.route('**/assets/gallery/sunja-tiktok-7627945643490692373.webp', lambda r: r.fulfill(status=404,body=''))
        c.route('**/assets/services/autodijagnostika.webp', lambda r: r.fulfill(status=404,body=''))
        c.route('**/assets/photos/qa-missing.webp', lambda r: r.fulfill(status=404,body=''))
        c.route('**/photos.json', lambda r: r.fulfill(json={'gallery':[{'source':'tiktok','src':'assets/photos/qa-missing.webp','href':'https://www.tiktok.com/@autoservissunja','title':'QA','quality_v':2}]}))
        p=start(c)
        for s in ('#heroMainImg','#tab-pane-1 img','#galerija [data-gallery-img]'):
            img=p.locator(s).first
            expect(img).to_have_attribute('data-fallback-applied','1')
            check_images(p,img)
            src=img.get_attribute('data-fallback-src')
            assert img.evaluate('img=>img.currentSrc').endswith(src),src
    finally:
        c.close()
    print('Reduced motion, performance mode, no-script content and photo recovery passed',flush=True)


def intro(browser,record=False):
    c=new_context(browser,1366,768,record=record)
    c.add_init_script('''window.introOrder=[];
        window.addEventListener('sunja:intro-experience-start',()=>window.introOrder.push('experience'));
        window.addEventListener('sunja:intro-finished',()=>window.introOrder.push('site'));''')
    video_path=None
    try:
        p=start(c,True)
        el=p.locator('#sunjaIntro')
        expect(el).to_be_visible()
        expect(el).to_have_class(re.compile(r'\bsunja-intro-playing\b'),timeout=7500)
        expect(p.locator('#sunjaIntroFrames')).to_have_attribute('src',re.compile(r'^blob:'))
        assert p.evaluate('window.introOrder')==[]
        p.screenshot(path=OUT/'intro-01-logo.png')
        expect(el).to_have_class(re.compile(r'\bsunja-intro-show-experience\b'),timeout=7500)
        assert p.evaluate('window.introOrder')==['experience']
        assert p.evaluate('!document.documentElement.dataset.workshopMotion')
        p.wait_for_timeout(1060)
        p.screenshot(path=OUT/'intro-02-experience.png')
        expect(el).to_be_hidden(timeout=5500)
        expect(p.locator('html')).to_have_attribute('data-workshop-motion','full')
        assert p.evaluate('window.introOrder')==['experience','site']
        p.screenshot(path=OUT/'intro-03-site.png')
        if record:
            p.evaluate("bootstrap.Carousel.getInstance(document.querySelector('#header-carousel')).pause()")
            p.wait_for_timeout(400)
            p.mouse.move(1100,570)
            # Native wheel during the pinned chapter, then work through the actual page.
            for i in range(13):
                p.mouse.wheel(0,44)
                p.wait_for_timeout(92)
            for selector in ('#usluge','#galerija','#o-nama','#recenzije','#lokacija','#kontakt','#siteFooter'):
                p.locator(selector).evaluate('''el=>window.scrollTo({top:el.getBoundingClientRect().top + scrollY-76,behavior:'smooth'})''')
                p.wait_for_timeout(800)
                if selector=='#usluge':
                    p.locator('#wm-tab-2').click()
                    check_images(p,p.locator('#tab-pane-2 img'))
                    p.wait_for_timeout(340)
            video=p.video
    finally:
        c.close()
    if record:
        video_path=video.path()
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',video_path,'-an','-c:v','libx264','-preset','fast','-pix_fmt','yuv420p','-b:v','365k','-maxrate','435k','-bufsize','630k','-movflags','+faststart',str(OUT/'workshop-scroll.mp4')],check=True)
        Path(video_path).unlink()
    print('Protected intro played in order: original logo → 25+ experience reveal → redesigned site',flush=True)


def make_review():
    slides=[OUT/'1366x768/01-first-screen.png',OUT/'1366x768/02-dial-mid-scroll.png',OUT/'1366x768/04-opening.png',OUT/'1366x768/05-services.png',OUT/'1366x768/06-gallery.png',OUT/'1366x768/07-workshop.png',OUT/'1366x768/09-location.png',OUT/'1366x768/11-contact.png']
    cv=Image.new('RGB',(1260,1520),'#101f37')
    dr=ImageDraw.Draw(cv)
    dr.text((18,17),'AUTO SERVIS SUNJA  /  WORKSHOP IN MOTION  /  DESKTOP',fill='#dbedff',font=ImageFontDefault(20))
    labels=['01  Opening','01  Dial mid-scroll','01  Opening scene','02  Services','03  Gallery','04  Workshop','05  Location','06  Contact']
    for i,(f,label) in enumerate(zip(slides,labels)):
        x=18+626*(i%2); y=58+365*(i//2)
        img=Image.open(f).convert('RGB')
        dr.text((x,y),label,fill='#dbedff', font=ImageFontDefault(17))
        img.thumbnail((598,321),Image.Resampling.LANCZOS)
        cv.paste(img,(x,y+26))
    cv.save(OUT/'desktop-review.jpg',quality=86,optimize=True)
    cv=Image.new('RGB',(1260,1550),'#101f37')
    dr=ImageDraw.Draw(cv)
    dr.text((18,17),'AUTO SERVIS SUNJA  /  PHONE LAYOUT  /  390 x 844',fill='#dbedff',font=ImageFontDefault(20))
    pngs=['01-first-screen','05-services','06-gallery','07-workshop','09-location','11-contact']
    labels=['01  Opening','02  Services','03  Gallery','04  Workshop','05  Location','06  Contact']
    for i,(name,label) in enumerate(zip(pngs,labels)):
        x=18+414*(i%3); y=58+744*(i//3)
        dr.text((x,y),label,fill='#dbedff', font=ImageFontDefault(17))
        img=Image.open(OUT/f'390x844/{name}.png').convert('RGB')
        img.thumbnail((392,695),Image.Resampling.LANCZOS)
        cv.paste(img,(x,y+26))
    cv.save(OUT/'phone-review.jpg',quality=86,optimize=True)


def ImageFontDefault(size):
    from PIL import ImageFont
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)


with sync_playwright() as pw:
    browser=getattr(pw,ENGINE).launch()
    failures=[]
    results=[]
    for w,h in SIZES:
        try:
            results.append(viewport(browser,w,h))
        except Exception as exc:
            failures.append(f'{w}x{h}: {exc}')
            print(failures[-1],flush=True)
    for fn in (other_states,lambda b:intro(b,ENGINE=='chromium')):
        try:
            fn(browser)
        except Exception as exc:
            failures.append(f'{getattr(fn,"__name__","extra")}: {exc}')
            print(failures[-1],flush=True)
    browser.close()
http.shutdown()
(OUT/'observations.json').write_text(json.dumps({'engine':ENGINE,'build':os.environ.get('DRAFT_SHA',''),'viewports':results,'failures':failures,'pageErrors':BROWSER_ERRORS,'map':'Image captures deliberately render the existing fallback, not remote tiles.'},ensure_ascii=False,indent=2))
if failures or BROWSER_ERRORS:
    raise SystemExit('\n'.join(failures+BROWSER_ERRORS))
if ENGINE=='chromium':
    make_review()
