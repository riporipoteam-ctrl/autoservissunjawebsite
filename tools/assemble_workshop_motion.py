"""One-off, pinned transformation of the Blue Service Desk page. Never serializes the whole document."""
from collections import Counter
from html import escape
from math import cos, radians, sin
from pathlib import Path
import re
from bs4 import BeautifulSoup

file = Path('index.html')
original = file.read_bytes().decode('utf-8')
STYLE_OLD = 'css/blue-service-desk.css?v=1.0'
STYLE_NEW = 'css/workshop-motion.css?v=2.0'
RUNTIME = '<script src="js/workshop-motion.js?v=2.0"></script>'
START = '<a href="#blueDesk" class="desk-jump">'
END = '    <!-- JavaScript Libraries -->'
assert original.count(START) == original.count(END) == original.count(STYLE_OLD) == 1
hero_old = BeautifulSoup(original[original.index(START):original.index(END)], 'html.parser')
get = lambda sel: hero_old.select_one(sel)
menus = [('pocetna', 'Početna'), ('usluge', 'Usluge'), ('galerija', 'Galerija'), ('o-nama', 'O nama'), ('lokacija', 'Lokacija'), ('kontakt', 'Kontakt')]
brand = get('.navbar-brand img')['src']
phone = get('#deskDock .call')['href']
assert phone == 'tel:+38761297847'
dir_url = escape(get('#deskDock .dir')['href'], quote=True)
dir_attrs = f'href="{dir_url}" rel="noopener" target="_blank"'
phone_icon = '<i class="fa fa-phone-alt" aria-hidden="true"></i>'
dir_icon = '<i class="fa fa-location-arrow" aria-hidden="true"></i>'

def chunks(s, a, b):
    start = s.index(a)
    end = s.index(b, start + len(a))
    return s[start:end]

def kicker(i, text):
    return f'<span class="wm-kicker"><b aria-hidden="true">{i:02}</b>{text}</span>'

def section(id_, title_id, extra=''):
    return f'<section id="{id_}" data-wm-chapter class="wm-section {extra}" aria-labelledby="{title_id}">'

def heading(n, tag, title_id, title, action=''):
    return f'<div class="wm-titleline" data-wm-reveal><div>{kicker(n, tag)}<h2 id="{title_id}">{title}</h2></div>{action}</div>'

nav_links = '\n'.join(f'        <a class="nav-link{" active" if i == 1 else ""}" href="#{slug}"{" aria-current=\"location\"" if i == 1 else ""}><span class="wm-nav-num" aria-hidden="true">{i:02}</span>{label}</a>'.replace('aria-current="location"','aria-current="location"') for i, (slug,label) in enumerate(menus,1))
header = f'''<a href="#workshopStory" class="wm-skip">Preskoči na sadržaj</a>
<header id="wmHeader">
  <nav class="navbar navbar-expand-lg nav-bar wm-nav" aria-label="Glavni meni">
    <div class="wm-wrap">
      <a href="#pocetna" class="navbar-brand"><img alt="Auto Servis Šunja" src="{brand}"></a>
      <div class="wm-header-tools">
        <button type="button" class="wm-motion-switch" data-wm-control aria-pressed="false" title="Pauziraj animacije stranice" hidden><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path class="wm-pause-icon" d="M9 5v14m6-14v14"/><path class="wm-play-icon" d="m9 5 10 7-10 7z"/></svg><span class="visually-hidden">Pauziraj animacije stranice</span></button>
        <button type="button" class="navbar-toggler collapsed" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false"><i class="fa fa-bars" aria-hidden="true"></i> Meni</button>
      </div>
      <div class="collapse navbar-collapse" id="navbarCollapse">
        <div class="navbar-nav" id="motionChapters">
{nav_links}
        </div>
        <a class="wm-button wm-nav-call" href="{phone}">{phone_icon} Pozovite</a>
      </div>
    </div>
  </nav>
</header>
<main id="workshopStory" tabindex="-1">'''

# Tachometer: gauge ticks and arc centred on the needle pivot (400,310).
def point(r, degrees):
    a = radians(degrees)
    return 400 + r*cos(a), 310 + r*sin(a)

def ticks():
    for i in range(29):
        a = 198 + i*(144/28)
        x1,y1 = point(238 if i % 4 == 0 else 248, a)
        x2,y2 = point(263, a)
        yield f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke-width="{3 if i % 4 == 0 else 1}"/>'

gauge = f'''<svg class="wm-gauge" viewBox="0 0 800 346" aria-hidden="true" focusable="false">
  <g fill="none" stroke="#628dbb"><path d="M138 225 A275 275 0 0 1 662 225" opacity=".55"/>{''.join(ticks())}</g>
  <path class="wm-gauge-arc" d="M165 234 A247 247 0 0 1 635 234" pathLength="100" fill="none" stroke="#155ee4" stroke-width="6" stroke-linecap="round"/>
  <g class="wm-needle"><path d="M397 311 400 48 403 311z" fill="#084ac1"/><circle cx="400" cy="310" r="11" fill="#084ac1"/></g>
</svg>'''
# Read the original carousel fragment without rewriting local assets or controls.
carousel = chunks(original, '    <div id="header-carousel"', '    <dl class="desk-shop-facts">').strip()
for old, new in {'desk-shot':'wm-film', 'desk-shot-text':'wm-shot-bar', 'desk-shot-number':'wm-shot-index', 'desk-deck-controls':'wm-media-nav', 'desk-ico':'wm-icon'}.items():
    carousel = carousel.replace(f'{old}"',f'{new}"').replace(f'{old} ',f'{new} ')
carousel = carousel.replace('data-bs-ride="false"', 'aria-roledescription="karusel" data-bs-ride="false"')
status = str(get('#pocetna [data-status]'))
opening = f'''<section id="pocetna" data-wm-chapter aria-labelledby="wm-hero-title">
 <div class="wm-pin">
  <div class="wm-wrap">
   <div class="wm-hero-grid">
    <div class="wm-hero-copy">
      {kicker(1,'Radionica u Goraždu')}
      <h1 id="wm-hero-title"><span>Auto Servis</span> Šunja</h1>
      <p>{get('.desk-lead').get_text()}</p>
      <div class="wm-actions"><a class="wm-button" href="{phone}">{phone_icon} 061 297 847</a><a class="wm-button wm-button--paper" {dir_attrs}>{dir_icon} Upute</a></div>
    </div>
    <div class="wm-hero-visual">
      {gauge}
      <div class="wm-odometer"><span>Hajra Lakovića 38</span><span class="wm-odometer-track" aria-hidden="true"></span><span>73000 Goražde</span></div>
      {carousel}
    </div>
   </div>
   <div class="wm-workstrip"><span><strong>Radno vrijeme</strong> · Pon – Sub, 10:00 – 18:00</span>{status}<a class="wm-scroll-link" href="#usluge">Naše usluge <i class="fa fa-arrow-down" aria-hidden="true"></i></a></div>
  </div>
  <div class="wm-hero-handoff" aria-hidden="true"></div>
 </div>
</section>'''

tabs=[]
panels=[]
for i in range(1,7):
    tab = get(f'#desk-tab-{i}')
    panel = get(f'#tab-pane-{i}')
    text = tab.select_one('span').get_text()
    active = ' active' if i == 1 else ''
    tabs.append(f'<button id="wm-tab-{i}" type="button" class="nav-link wm-tab{active}" role="tab" data-bs-toggle="pill" data-bs-target="#tab-pane-{i}" aria-controls="tab-pane-{i}" aria-selected="{str(i==1).lower()}" tabindex="{0 if i==1 else -1}"><b aria-hidden="true">{i:02}</b><span>{escape(text)}</span></button>')
    pane_cls = ' show active' if i == 1 else ''
    photo = panel.select_one('.service-media-frame')
    panels.append(f'''<section class="tab-pane fade{pane_cls}" id="tab-pane-{i}" role="tabpanel" aria-labelledby="wm-tab-{i}" tabindex="0">
      <div class="wm-service-scene"><div class="wm-service-copy">{kicker(i,'Servisni program')}<h3>{panel.h3.get_text()}</h3>{panel.p}{panel.ul}<a class="wm-button" href="{phone}">{phone_icon} Pozovite</a></div>{photo}</div>
    </section>''')
services = f'''{section('usluge','wm-services-title')}<div class="wm-wrap">
  {heading(2,'Naše usluge','wm-services-title','Šta radimo')}
  <div class="nav nav-pills service-nav-grid" role="tablist" aria-label="Naše usluge">{chr(10).join(tabs)}</div>
  <div class="tab-content">{chr(10).join(panels)}</div>
</div></section>'''

frames=[]
for i, frame in enumerate(hero_old.select('#galerija .team-item'),1):
    img, link, sub = frame.img, frame.select_one('[data-gallery-link]'), frame.select_one('[data-gallery-sub]')
    link['class'] = ['wm-icon', 'gallery-tile-link']
    link.i['aria-hidden'] = 'true'
    frames.append(f'''<figure class="wm-frame team-item"><div class="wm-frame-photo">{img}</div><figcaption class="wm-frame-foot"><b aria-hidden="true">{i:02}/05</b>{sub}{link}</figcaption></figure>''')
profile_link = get('#galerija .desk-button')
profile_link['class'] = ['wm-button', 'wm-button--glass']
gallery = f'''{section('galerija','wm-gallery-title')}<div class="wm-wrap">
  {heading(3,'Galerija','wm-gallery-title','Iz naše radionice',str(profile_link))}
  <div class="wm-film-grid">{chr(10).join(frames)}</div>
</div></section>'''

about = f'''{section('o-nama','wm-about-title')}<div class="wm-wrap wm-workshop-grid">
  <figure class="wm-workshop-visual">{get('[data-about-photo]')}<figcaption class="wm-stamp"><strong>25+</strong> godina iskustva</figcaption></figure>
  <div class="wm-workshop-copy" data-wm-reveal>{kicker(4,'O nama')}<h2 id="wm-about-title">Auto Servis Šunja u Goraždu</h2>{get('#o-nama p')}
  <div class="wm-actions"><a class="wm-button wm-button--paper" href="#recenzije">Recenzije <i class="fa fa-arrow-down" aria-hidden="true"></i></a></div></div>
</div></section>'''
review_link = get('#recenzije a')
review_link['class'] = ['wm-button','wm-button--paper']
stars = get('[data-stars]')
stars['aria-hidden'] = 'true'
review = f'''<section id="recenzije" class="wm-section" aria-labelledby="wm-reviews-title"><div class="wm-wrap wm-review-row" data-wm-reveal>
  <div><span class="wm-kicker">Recenzije</span><h2 id="wm-reviews-title">Ocjena na Google kartama</h2></div>
  <div class="wm-review-note">{stars}{get('#recenzije p')}{review_link}</div>
</div></section>'''
loc = f'''{section('lokacija','wm-location-title')}<div class="wm-wrap">
 <div class="wm-titleline" data-wm-reveal><div>{kicker(5,'Lokacija')}<h2 id="wm-location-title">Lokacija servisa</h2>{get('#lokacija p')}</div><a class="wm-button" {dir_attrs}>{dir_icon} Upute za vožnju</a></div>
 <div class="wm-coordinate" aria-hidden="true"><span>43.6651456° N</span><i></i><span>18.982064° E</span></div>
</div></section>'''
map_markup = chunks(original,'<div class="globe-scroll"','<section id="kontakt"')
contact = f'''{section('kontakt','wm-contact-title')}<div class="wm-wrap">
  {kicker(6,'Kontakt')}
  <div class="wm-contact-row" data-wm-reveal><div><h2 id="wm-contact-title">Kontaktirajte Auto Servis Šunja</h2>
    <a class="wm-number" href="{phone}">061 297 847</a>
    <div class="wm-actions"><a class="wm-button wm-button--paper" href="{phone}">{phone_icon} Pozovite</a><a class="wm-button wm-button--glass" {dir_attrs}>{dir_icon} Upute</a><a class="wm-button wm-button--glass" href="https://wa.me/38761297847" target="_blank" rel="noopener">WhatsApp ↗</a></div>
  </div><div class="wm-contact-info">{''.join(str(p) for p in hero_old.select('.desk-contact-info p'))}</div></div>
</div></section>'''
footer = chunks(original,'<footer id="siteFooter">','<div id="deskDock"')
for old,new in {'desk-wrap':'wm-wrap','desk-footer-grid':'wm-footer-grid','desk-foot-brand':'wm-foot-brand','desk-socials':'wm-actions','desk-ico':'wm-icon','desk-footer-links':'wm-footer-links','desk-foot-credit':'wm-foot-end','Designed by':'Dizajn:'}.items():
    footer = footer.replace(old,new)
footer = footer.replace('<div class="wm-foot-end">','<div class="wm-foot-end"><span>').replace('Fotografija naše radionice</a></div>', 'Fotografija naše radionice</a></span><a href="#pocetna">Na vrh ↑</a></div>')
dock = chunks(original,'<div id="deskDock"',END).replace('deskDock','wmDock').replace('desk-ico','wm-icon')
# Native anchors and all service information remain usable without scripting.
noscript = '''<noscript><style>
#wmHeader{position:relative}#wmHeader .navbar-toggler,#workshopStory .service-nav-grid,#header-carousel .wm-media-nav{display:none!important}
#wmHeader #navbarCollapse{display:block!important}#wmHeader .navbar-nav{display:flex;flex-flow:row wrap}
#workshopStory #usluge .tab-pane{display:block!important;opacity:1!important;transform:none!important;animation:none!important;margin-bottom:12px}
</style></noscript>'''

before, after = original.split(START,1)[0], original[original.index(END):]
start_updated = before.replace(STYLE_OLD, STYLE_NEW)
assert after.endswith('</body>\n\n</html>\n') or '</body>' in after
result = start_updated + '\n'.join([header, opening, services, gallery, about, review, loc, map_markup, contact, '</main>', footer, dock, noscript, '']) + after.replace('</body>', f'    {RUNTIME}\n</body>', 1)
assert result.split('<a href="#workshopStory"',1)[0].replace(STYLE_NEW, STYLE_OLD) == before
assert result[result.index(END):].replace(f'    {RUNTIME}\n','',1) == after
assert chunks(result,'<div class="globe-scroll"','<section id="kontakt"') == map_markup + '\n'
new = BeautifulSoup(result, 'html.parser')
old = BeautifulSoup(original, 'html.parser')
ids = Counter(n['id'] for n in new.select('[id]'))
assert max(ids.values()) == 1, [k for k,v in ids.items() if v>1]
assert not re.search(r'blueDesk|desk-|blue-service-desk', result)
for n in new.select('a[href^="#"], [data-bs-target^="#"]'):
    ref = n.get('data-bs-target') or n['href']
    assert ref[1:] in ids, ref
for n in new.select('[aria-labelledby], [aria-controls]'):
    for attr in ('aria-labelledby', 'aria-controls'):
        for id_ in n.get(attr,'').split():
            assert id_ in ids, (attr,id_)
for selector,count in [('#header-carousel img',3),('#usluge img.service-image',6),('#galerija [data-gallery-img]',5)]:
    old_assets=old.select(selector)
    new_assets=new.select(selector)
    assert len(old_assets)==len(new_assets)==count
    for a,b in zip(old_assets,new_assets):
        assert all(a.get(key)==b.get(key) for key in ('src','alt','data-fallback-src','data-fallback-alt','onerror')), (a,b)
assert set(n['src'] for n in old.select('img')) == set(n['src'] for n in new.select('img'))
assert [n['href'] for n in new.select('[rel*=icon]')] == [n['href'] for n in old.select('[rel*=icon]')]
assert 'var SHOP = [18.982064, 43.6651456];' in result
assert result.count(RUNTIME)==1
file.write_bytes(result.encode('utf-8'))
