"""Verify workshop photos by the pixels actually painted in browser screenshots."""
import io
import json
import math
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from PIL import Image, ImageChops, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

SIZES = [(1920,1080),(1366,768),(1024,768),(820,1180),(768,1024),(390,844),(360,800)]
CHAPTERS = [('04-opening','#pocetna .wm-pin'),('05-services','#usluge'),('06-gallery','#galerija'),('07-workshop','#o-nama'),('08-reviews','#recenzije'),('09-location','#lokacija'),('10-map-fallback','#globeScroll'),('11-contact','#kontakt'),('12-footer','#siteFooter')]
PHOTO = '#galerija .wm-frame-photo img'
FRAME = '#galerija .wm-frame-photo'
HIDE_IMAGES = f'{PHOTO}{{visibility:hidden!important}}'
CLEAN = '#wmDock,#backTop{visibility:hidden!important}'
NO_CHROME = CLEAN + '#wmHeader{visibility:hidden!important}'
ENGINE = os.environ['BROWSER_ENGINE']
OUT = Path(os.environ.get('CAPTURE_DIR', 'captures')).resolve()
TRACE = OUT.parent / 'capture-diagnostics'

class Site(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

http = ThreadingHTTPServer(('127.0.0.1', 0), partial(Site, directory=Path.cwd()))
Thread(target=http.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{http.server_port}'


def raf(p, n=4):
    p.evaluate('n => new Promise(resolve => {const tick=()=>n-- > 0 ? requestAnimationFrame(tick) : resolve(); tick();})', n)


def jump(p, y):
    p.evaluate('(y) => scrollTo({top:y,behavior:"instant"})', max(0,y))
    raf(p)


def doc_box(p, sel):
    return p.locator(sel).evaluate('''el=>{const r=el.getBoundingClientRect();return [Math.floor(r.left+scrollX),Math.floor(r.top+scrollY),Math.ceil(r.right+scrollX),Math.ceil(r.bottom+scrollY)]}''')


def photo_boxes(p):
    return p.locator(FRAME).evaluate_all('''a=>a.map(el=>{const r=el.getBoundingClientRect();return [Math.round(r.left+scrollX),Math.round(r.top+scrollY),Math.round(r.right+scrollX),Math.round(r.bottom+scrollY)]})''')


def shot(p, **opts):
    return Image.open(io.BytesIO(p.screenshot(timeout=22000, **opts))).convert('RGB')


def images_ready(p, sel):
    for loc in p.locator(sel).all():
        loc.evaluate('e=>{e.loading="eager"}')
        p.wait_for_function('e=>e.complete && e.naturalWidth>0', arg=loc.element_handle())
        loc.evaluate('e=>e.decode()', timeout=9000)
    raf(p, 6)


def photos_painted(a, b, rects, origin=0):
    assert a.size == b.size, (a.size,b.size)
    rates = []
    for x1,y1,x2,y2 in rects:
        dx,dy=math.ceil((x2-x1)*.14),math.ceil((y2-y1)*.14)
        box=(x1+dx, y1+dy-origin, x2-dx, y2-dy-origin)
        assert 0<=box[0]<box[2]<=a.width and 0<=box[1]<box[3]<=a.height, (box, a.size)
        bands=ImageChops.difference(a.crop(box),b.crop(box)).split()
        hist=ImageChops.lighter(ImageChops.lighter(bands[0],bands[1]),bands[2]).histogram()
        rates.append(round(sum(hist[14:])/sum(hist),3))
    return rates


def approx_scroll(p, goal, w, h):
    p.mouse.move(round(w*.70),round(h*.58))
    for _ in range(24):
        y = round(p.evaluate('scrollY'))
        d = goal-y
        if abs(d)<=3:
            break
        try:
            p.mouse.wheel(0,max(-320,min(320,d)))
        except Exception as exc:
            if 'wheel' not in str(exc).lower():
                raise
            break
        raf(p, 6)
        if abs(p.evaluate('scrollY')-y)<1:
            break
    if abs(p.evaluate('scrollY')-goal)>=5:
        p.evaluate('y=>scrollTo({top:y,behavior:"smooth"})',goal)
        p.wait_for_function('y=>Math.abs(scrollY-y)<5',arg=goal)
    # Let the site's normal transforms settle before taking the before/after pair.
    p.wait_for_timeout(620)


def observe_mobile(p, path, w, h, photos):
    done = {}
    scores = {}
    for top in sorted({r[1] for r in photos}):
        goal = round(top - (108 if not done else min(165,h*.22)))
        approx_scroll(p, goal, w, h)
        origin = round(p.evaluate('scrollY'))
        idx = [i for i,(_,a,_,b) in enumerate(photos) if a-origin>=68 and b-origin<=h-77]
        idx = [i for i in idx if i not in done or scores[i]<.08]
        if not idx:
            continue
        for i in idx:
            p.wait_for_function('e=>e.complete && e.naturalWidth>0',arg=p.locator(PHOTO).nth(i).element_handle())
        raf(p, 6)
        a = shot(p)
        b = shot(p, style=HIDE_IMAGES)
        scores.update(zip(idx,photos_painted(a,b,[photos[i] for i in idx],origin)))
        name = f'{15+len(set(done.values())):02}-gallery-in-viewport.png'
        a.save(path/name)
        done.update((i,name) for i in idx)
        if len(done)==5 and min(scores.values())>=.08:
            break
    return [scores.get(i,0) for i in range(5)]


def stitch_gallery(p, box):
    x1,top,x2,bottom = box
    output = Image.new('RGB',(x2-x1,bottom-top))
    hidden = output.copy()
    h = p.viewport_size['height']
    rows = photo_boxes(p)
    # Cut between rows, never through an image. Hide only fixed review overlays.
    cuts = [top]
    while bottom-cuts[-1]>h-2:
        start = cuts[-1]
        safe = [y for y in range(start+1,start+h-1) if not any(t-1<y<b+1 for _,t,_,b in rows)]
        cuts.append(max(safe))
    cuts.append(bottom)
    for start,end in zip(cuts,cuts[1:]):
        jump(p, start)
        p.wait_for_timeout(570)
        origin = round(p.evaluate('scrollY'))
        band = (x1,start-origin,x2,end-origin)
        assert 0<=band[1]<band[3]<=h, band
        output.paste(shot(p, style=NO_CHROME).crop(band),(0,start-top))
        hidden.paste(shot(p, style=NO_CHROME+HIDE_IMAGES).crop(band),(0,start-top))
    return output, hidden


def verify_size(browser, w, h):
    path = OUT/f'{w}x{h}'
    path.mkdir(parents=True,exist_ok=True)
    traced = TRACE/path.name
    traced.mkdir(parents=True,exist_ok=True)
    ctx = browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,has_touch=w<=820,is_mobile=w<=390)
    ctx.add_init_script("Object.defineProperty(Navigator.prototype,'hardwareConcurrency',{get:()=>8});")
    ctx.route('**/maplibre-gl@5.6.0/dist/maplibre-gl.js',lambda route:route.abort())
    p = ctx.new_page()
    p.set_default_timeout(10000)
    observed_errors = []
    p.on('pageerror',lambda e:observed_errors.append(str(e)))
    try:
        p.goto(base+'/?skipIntro=1',wait_until='domcontentloaded',timeout=25000)
        mode = 'full' if w>=1024 else 'light'
        p.wait_for_function('m=>document.documentElement.dataset.workshopMotion===m',arg=mode)
        p.wait_for_function("document.querySelector('#globeScroll').classList.contains('is-fallback')")
        p.evaluate('() => document.fonts.ready')
        p.evaluate("bootstrap.Carousel.getInstance(document.querySelector('#header-carousel')).pause()")
        images_ready(p,'#header-carousel .active picture img')
        shot(p).save(path/'01-first-screen.png')
        runway = p.locator('#pocetna').evaluate('e=>e.offsetHeight-e.querySelector(".wm-pin").offsetHeight')
        jump(p, round(runway*.51) if mode=='full' else 120)
        p.wait_for_timeout(360)
        shot(p).save(path/('02-dial-mid-scroll.png' if mode=='full' else '02-light-scroll.png'))
        if mode=='full':
            jump(p, runway+100)
            p.wait_for_timeout(330)
            shot(p).save(path/'03-handoff.png')
        # The pinned revision has more than five local originals. Wait for the
        # page to select its five real photos; don't replace its randomizer.
        p.wait_for_function('''()=>{const a=[...document.querySelectorAll('#galerija [data-gallery-img]')];return a.length===5&&a.every(i=>i.getAttribute('src').startsWith('assets/photos/'))&&new Set(a.map(i=>i.src)).size===5}''')
        photos = photo_boxes(p)
        normal = observe_mobile(p,path,w,h,photos) if w<=390 else None
        if normal is not None:
            print(path.name,'normal painted:',normal,flush=True)
        # Stills are a separate pass: await the decoding of the final selected
        # photos and web fonts, not the default fallbacks present at startup.
        images_ready(p,'#usluge .tab-pane.active img, #galerija img, #o-nama img')
        for name,sel in CHAPTERS:
            if name=='06-gallery':
                continue
            jump(p, (0 if name=='04-opening' else doc_box(p,sel)[1]-74))
            p.wait_for_timeout(560)
            p.locator(sel).screenshot(path=path/f'{name}.png',style=NO_CHROME,timeout=16000)
        box = doc_box(p,'#galerija')
        jump(p,box[1]-75)
        p.wait_for_timeout(620)
        el = p.locator('#galerija')
        native = Image.open(io.BytesIO(el.screenshot(style=NO_CHROME,timeout=16000))).convert('RGB')
        native_hidden = Image.open(io.BytesIO(el.screenshot(style=NO_CHROME+HIDE_IMAGES,timeout=16000))).convert('RGB')
        rates = photos_painted(native,native_hidden,photos,box[1])
        rendered, method = native, 'native section'
        if min(rates)<.08 or native.size!=(box[2]-box[0],box[3]-box[1]):
            native.save(traced/'native-section.png')
            rendered, hidden = stitch_gallery(p,box)
            final_rates = photos_painted(rendered,hidden,photos,box[1])
            method = 'stitched from real viewport captures'
        else:
            final_rates = rates
        rendered.save(path/'06-gallery.png')
        jump(p,0)
        p.wait_for_timeout(620)
        full = shot(p,full_page=True,style=CLEAN)
        noimg = shot(p,full_page=True,style=CLEAN+HIDE_IMAGES)
        full_rates = photos_painted(full,noimg,photos)
        full_method = 'native full-page'
        final_full_rates = full_rates
        if min(full_rates)<.08:
            full.crop(box).save(traced/'native-full-page-gallery.png')
            if method == 'native section':
                hidden = native_hidden
            assert rendered.size==(box[2]-box[0], box[3]-box[1]), (rendered.size,box)
            full.paste(rendered,(box[0],box[1]))
            noimg.paste(hidden,(box[0],box[1]))
            final_full_rates = photos_painted(full,noimg,photos)
            full_method = f'full-page still with verified {method} for gallery region'
        full.save(path/'14-full-page.png')
        assert full.width==w and full.height>h, full.size
        assert all((path/f'{n}.png').stat().st_size>500 for n,_ in CHAPTERS)
        assert p.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth+1')
        record = {'size':path.name,'engine':ENGINE,'normal':normal,'nativeSection':rates,'finalSection':final_rates,'sectionMethod':method,'nativeFull':full_rates,'finalFull':final_full_rates,'fullMethod':full_method,'photos':p.locator(PHOTO).evaluate_all('a=>a.map(e=>e.getAttribute("src"))'),'errors':observed_errors}
        print(json.dumps(record,ensure_ascii=False),flush=True)
        return record
    finally:
        ctx.close()


def phone_sheet():
    path=OUT/'390x844'
    slides=[('01-first-screen','01  Početna'),('05-services','02  Usluge'),('06-gallery','03  Galerija'),('07-workshop','04  Radionica'),('09-location','05  Lokacija'),('11-contact','06  Kontakt')]
    canvas=Image.new('RGB',(1260,1580),'#101f37')
    draw=ImageDraw.Draw(canvas)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    draw.text((22,20),'AUTO SERVIS ŠUNJA  /  MOBILNI PREGLED  /  390 × 844',fill='#dbedff',font=ImageFont.truetype(font,23))
    for i,(name,label) in enumerate(slides):
        x=22+414*(i%3); y=65+748*(i//3)
        draw.text((x,y),label,fill='#dbedff',font=ImageFont.truetype(font,18))
        image=Image.open(path/f'{name}.png').convert('RGB')
        image.thumbnail((390,704),Image.Resampling.LANCZOS)
        canvas.paste(image,(x,y+28))
    canvas.save(OUT/'phone-review.jpg',quality=91,optimize=True,subsampling=0)


results,failed = [],[]
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
    browser=getattr(pw,ENGINE).launch()
    for w,h in SIZES:
        try:
            row=verify_size(browser,w,h)
            results.append(row)
            if min(row['finalSection']+row['finalFull']+(row['normal'] or []))<.08 or row['errors']:
                failed.append(f'{w}x{h}: gallery pixels or browser errors')
        except Exception as exc:
            import traceback
            traceback.print_exc()
            failed.append(f'{w}x{h}: {exc}')
    browser.close()
http.shutdown()
(OUT/'photo-paint-report.json').write_text(json.dumps({'draft':os.environ.get('DRAFT_SHA',''),'engine':ENGINE,'photosCheckedAtEachSize':5,'minimumPaintedFraction':.08,'results':results,'failures':failed},indent=2))
if failed:
    raise SystemExit('\n'.join(failed))
if ENGINE=='chromium':
    phone_sheet()
