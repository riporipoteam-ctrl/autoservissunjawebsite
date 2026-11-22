from html import escape
from pathlib import Path
import re
from bs4 import BeautifulSoup

path = Path('index.html')
source = path.read_bytes().decode('utf-8')
start = source.index('<!-- Topbar Start -->')
end = source.index('    <!-- JavaScript Libraries -->', start)
old_view = source[start:end]
soup = BeautifulSoup(old_view, 'html.parser')
prefix = source[:start]
scripts = source[end:]
assert prefix.count('css/overhaul-v49.css?v=53.0') == 1
new_prefix = prefix.replace('css/overhaul-v49.css?v=53.0', 'css/blue-service-desk.css?v=1.0', 1)
assert new_prefix[new_prefix.index('<body'):]==prefix[prefix.index('<body'):]


def need(node, selector):
    found = node.select_one(selector)
    assert found is not None, selector
    return found


def text(node):
    return escape(node.get_text(' ', strip=True))


def attr(node, name):
    return escape(str(node[name]), quote=True)


def icon(name):
    return f'<i class="fa fa-{name}" aria-hidden="true"></i>'


phone = attr(need(soup, '.mobile-callbar .call'), 'href')
assert phone == 'tel:+38761297847'
directions = attr(need(soup, '.mobile-callbar .dir'), 'href')
wa = attr(need(soup, '#kontakt a[href^="https://wa.me/"]'), 'href')
hero = need(soup, '#header-carousel')
slides = hero.select('.carousel-item')
assert len(slides)==3
phone_text = text(need(soup,'.mobile-callbar .call'))
address = text(need(soup,'#lokacija p'))
logo = str(need(soup,'.navbar-brand img'))
footer_logo = str(need(soup,'#siteFooter .footer-brand img')).replace(' class="mb-4"','')
status = str(need(soup,'.workshop-topbar [data-status]'))
status = re.sub(r' style="[^"]*"', '', status)
photo_location = 'Goražde, Hajra Lakovića 38'
nav_items = [('pocetna','Početna'),('usluge','Usluge'),('galerija','Galerija'),('o-nama','O nama'),('lokacija','Lokacija'),('kontakt','Kontakt')]
nav_links = ''.join(f'<a href="#{slug}" class="nav-link{" active" if i==0 else ""}">{label}</a>' for i,(slug,label) in enumerate(nav_items))
head = f'''<a href="#blueDesk" class="desk-jump">Preskoči na sadržaj</a>
<header id="deskHeader">
  <nav class="navbar navbar-expand-lg nav-bar desk-nav" aria-label="Glavni meni">
    <div class="desk-wrap">
      <a href="#pocetna" class="navbar-brand">{logo}</a>
      <button type="button" class="navbar-toggler collapsed" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Meni">{icon('bars')} Meni</button>
      <div class="collapse navbar-collapse" id="navbarCollapse">
        <div class="navbar-nav">{nav_links}</div>
        <a class="desk-button desk-nav-call" href="{phone}">{icon('phone-alt')} Pozovite</a>
      </div>
    </div>
  </nav>
</header>'''

photos = []
media_labels = ['Radionica', 'Dijagnostika', 'Ključevi']
for i, slide in enumerate(slides,1):
    title = 'Radionica Auto Servis Šunja' if i==1 else text(need(slide,'h1'))
    bg = need(slide,'.hero-bg')
    picture = need(slide,'picture')
    dest = '#galerija' if i==1 else '#usluge'
    link_label = 'Galerija' if i==1 else 'Sve usluge'
    data = ' data-svc-link="1"' if i==2 else ' data-svc-link="6"' if i==3 else ''
    photos.append(f'''<div class="carousel-item{' active' if i==1 else ''}">
      <div class="desk-shot">{bg}{picture}</div>
      <div class="desk-shot-text"><span class="desk-shot-number">0{i} / 03</span><strong>{title}</strong><a href="{dest}"{data}>{link_label} ↗</a></div>
    </div>''')
pickers = ''.join(f'<button type="button" data-bs-target="#header-carousel" data-bs-slide-to="{i}"{" class=\"active\" aria-current=\"true\"" if i==0 else ""} aria-label="Slajd {i+1}: {name}">{name}</button>' for i,name in enumerate(media_labels))
hero_copy = text(need(slides[0],'.carousel-caption p'))
home = f'''<section id="pocetna" aria-labelledby="desk-hero-title">
 <div class="desk-wrap">
  <div class="desk-home-lead">
    <div><span class="desk-eyebrow">{photo_location}</span><h1 id="desk-hero-title">Auto Servis Šunja</h1><p class="desk-lead">{hero_copy}</p></div>
    <div class="desk-actions"><a class="desk-button desk-button--light" href="{phone}">{icon('phone-alt')} {phone_text}</a>
    <a class="desk-button desk-button--clear" href="{directions}" target="_blank" rel="noopener">{icon('location-arrow')} Upute</a></div>
  </div>
  <div class="desk-home-grid">
    <div id="header-carousel" class="carousel slide carousel-fade" data-bs-ride="false" data-bs-interval="6500" data-bs-pause="false" data-bs-touch="true" aria-label="Fotografije iz radionice">
      <div class="carousel-inner">{''.join(photos)}</div>
      <div class="desk-deck-controls">
        <div class="carousel-indicators hero-indicators">{pickers}</div>
        <button type="button" class="desk-ico hero-nav carousel-control-prev" data-bs-target="#header-carousel" data-bs-slide="prev" aria-label="Prethodno">{icon('chevron-left')}</button>
        <button type="button" class="desk-ico hero-nav carousel-control-next" data-bs-target="#header-carousel" data-bs-slide="next" aria-label="Sljedeće">{icon('chevron-right')}</button>
      </div>
    </div>
    <dl class="desk-shop-facts">
      <div><dt>Radno vrijeme</dt><dd>Pon – Sub · 10:00 – 18:00</dd></div>
      <div><dt>Adresa</dt><dd>Hajra Lakovića 38<br>73000 Goražde</dd></div>
      <div><dt>Danas</dt><dd>{status}</dd></div>
    </dl>
  </div>
 </div>
</section>'''

keys, details, footer_services = [], [], []
service_icons = ['laptop-code','car','oil-can','cog','bolt','key']
for i, glyph in enumerate(service_icons, 1):
    panel = need(soup,f'#tab-pane-{i}')
    title = text(need(panel,'h3'))
    image = str(need(panel,'img.service-image'))
    ps = panel.select('p')
    assert len(ps)>=4
    items = ''.join(f'<li>{text(p)}</li>' for p in ps[1:])
    flag = ' active' if i==1 else ''
    selection = 'true' if i==1 else 'false'
    details.append(f'''<section class="tab-pane fade{' show active' if i==1 else ''}" id="tab-pane-{i}" role="tabpanel" aria-labelledby="desk-tab-{i}">
      <div class="desk-service-panel"><div><h3>{title}</h3><p class="mb-4">{text(ps[0])}</p><ul>{items}</ul>
        <a class="desk-button" href="{phone}">{icon('phone-alt')} Pozovite</a></div><div class="service-media-frame">{image}</div></div></section>''')
    keys.append(f'''<button id="desk-tab-{i}" type="button" class="nav-link desk-service-key{flag}" role="tab" data-bs-toggle="pill" data-bs-target="#tab-pane-{i}" aria-controls="tab-pane-{i}" aria-selected="{selection}">{icon(glyph)}<span>{title}</span><span class="desk-service-no" aria-hidden="true">{i:02d}</span></button>''')
    footer_services.append(f'<a href="#usluge" data-svc-link="{i}">{title}</a>')
services = f'''<section id="usluge" class="desk-section" aria-labelledby="desk-services-title"><div class="desk-wrap">
  <div class="desk-section-head"><div><span class="desk-eyebrow">Naše usluge</span><h2 id="desk-services-title">Šta radimo</h2></div></div>
  <div class="nav nav-pills service-nav-grid" role="tablist" aria-label="Naše usluge">{''.join(keys)}</div>
  <div class="tab-content">{''.join(details)}</div>
</div></section>'''

gallery_cards = []
for img in soup.select('[data-gallery-img]'):
    card = img.find_parent(class_='team-item')
    link = need(card,'[data-gallery-link]')
    link['class'] = ['desk-ico','gallery-tile-link']
    sub = need(card,'[data-gallery-sub]')
    gallery_cards.append(f'<figure class="desk-frame team-item"><div class="desk-frame-media">{img}</div><figcaption class="desk-frame-foot">{sub}{link}</figcaption></figure>')
assert len(gallery_cards)==5
socials = []
for label, style in [('TikTok','tiktok'),('Facebook','facebook-f'),('Instagram','instagram')]:
    link = need(soup,f'#siteFooter a[aria-label="{label}"]')
    socials.append(f'<a href="{attr(link,"href")}" class="desk-ico" target="_blank" rel="noopener" aria-label="{label}"><i class="fab fa-{style}" aria-hidden="true"></i></a>')
tiktok = attr(need(soup,'#siteFooter a[aria-label="TikTok"]'),'href')
gallery = f'''<section id="galerija" class="desk-section" aria-labelledby="desk-gallery-title"><div class="desk-wrap">
  <div class="desk-section-head"><div><span class="desk-eyebrow">Galerija</span><h2 id="desk-gallery-title">Iz naše radionice</h2></div>
      <a class="desk-button desk-button--outline" href="{tiktok}" target="_blank" rel="noopener">@autoservissunja ↗</a></div>
  <div class="desk-reel" tabindex="0" role="region" aria-label="Galerija fotografija">{''.join(gallery_cards)}</div>
</div></section>'''

about = text(need(soup,'#o-nama p.mb-4'))
about_img = need(soup,'img[data-about-photo]')
about_img['class'] = ['desk-profile-image','svc-photo']
review = need(soup,'#recenzije')
review_link = need(review,'a[href]')
review_copy = need(review,'p')
review_copy.attrs.pop('class',None)
profile = f'''<div class="desk-profile-band desk-section"><div class="desk-wrap desk-profile-grid">
  <section id="o-nama" class="desk-profile" aria-labelledby="desk-about-title">
    <span class="desk-eyebrow">O nama</span><h2 id="desk-about-title">Auto Servis Šunja u Goraždu</h2>
    <div class="desk-profile-body">{about_img}<div><p>{about}</p><div class="desk-experience"><strong>25+</strong> godina iskustva</div></div></div>
  </section>
  <section id="recenzije" class="desk-review" aria-labelledby="desk-reviews-title">
    <span class="desk-eyebrow">Recenzije</span><h2 id="desk-reviews-title">Ocjena na Google kartama</h2>
    {need(review,'[data-stars]')}{review_copy}
    <a class="desk-button desk-button--outline" href="{attr(review_link,'href')}" target="_blank" rel="noopener">Pogledajte na Google kartama ↗</a>
  </section>
</div></div>'''
map_start = source.index('<div class="globe-scroll" id="globeScroll">',start)
map_end = source.index('    <!-- Globe Map End -->',map_start)
map_markup = source[map_start:map_end]
location = f'''<section id="lokacija" class="desk-loc" aria-labelledby="desk-location-title"><div class="desk-wrap">
  <div class="desk-section-head"><div><span class="desk-eyebrow">Lokacija</span><h2 id="desk-location-title">Lokacija servisa</h2><p>{address}</p></div>
      <a class="desk-button" href="{directions}" target="_blank" rel="noopener">{icon('location-arrow')} Upute za vožnju</a></div>
</div></section>
{map_markup}'''
contact = f'''<section id="kontakt" class="desk-section" aria-labelledby="desk-contact-title"><div class="desk-wrap">
  <span class="desk-eyebrow">Kontakt</span><h2 id="desk-contact-title">Kontaktirajte Auto Servis Šunja</h2>
  <div class="desk-contact"><div class="desk-contact-call"><span class="desk-eyebrow">Telefon</span><a class="desk-number" href="{phone}">{phone_text}</a>
    <div class="desk-actions"><a class="desk-button desk-button--light" href="{phone}">{icon('phone-alt')} Pozovite</a><a class="desk-button desk-button--clear" href="{wa}" target="_blank" rel="noopener">WhatsApp ↗</a></div>
  </div><div class="desk-contact-info"><p><strong>Adresa</strong>{address}</p><p><strong>Radno vrijeme</strong>Pon – Sub: 10:00 – 18:00 · Nedjelja: zatvoreno</p></div></div>
</div></section>'''
original_footer = need(soup,'#siteFooter')
credit = need(original_footer,'.footer-photo-credit a')
author = need(original_footer,'.copyright a[href*="facebook.com"]')
footer = f'''<footer id="siteFooter"><div class="desk-wrap">
  <div class="desk-footer-grid">
    <div class="desk-foot-brand">{footer_logo}<p>Auto Servis Šunja · Goražde</p><div class="desk-socials">{''.join(socials)}</div></div>
    <div><h2>Radno vrijeme</h2>{need(original_footer,'.hours-list')}</div>
    <div><h2>Usluge</h2><div class="desk-footer-links">{''.join(footer_services)}</div></div>
  </div>
  <div class="desk-foot-credit">© Auto Servis Šunja, sva prava zadržana. · Designed by <a href="{attr(author,'href')}" target="_blank" rel="noopener">{text(author)}</a> · <a href="{attr(credit,'href')}" target="_blank" rel="noopener">Fotografija naše radionice</a></div>
</div></footer>
<div id="deskDock" class="mobile-callbar" aria-label="Brzi kontakt"><a class="call" href="{phone}">{icon('phone-alt')} {phone_text}</a>
 <a class="dir" href="{directions}" target="_blank" rel="noopener">{icon('location-arrow')} Upute</a></div>
<button type="button" id="backTop" class="desk-ico back-to-top" aria-label="Nazad na vrh" title="Nazad na vrh">{icon('arrow-up')}</button>'''

out = f'{new_prefix}{head}\n<main id="blueDesk" tabindex="-1">\n{home}\n{services}\n{gallery}\n{profile}\n{location}\n{contact}\n</main>\n{footer}\n{scripts}'
assert out.endswith(scripts) and map_markup in out
result = BeautifulSoup(out,'html.parser')
ids = [node['id'] for node in result.select('[id]')]
assert len(ids)==len(set(ids)), [key for key in ids if ids.count(key)>1]
assert len(result.select('#header-carousel picture img'))==3
assert len(result.select('#usluge .tab-pane img.service-image'))==6
assert len(result.select('[data-gallery-img]'))==5
for image in soup.select('img'):
    assert result.find('img', src=image.get('src')) is not None, image.get('src')
assert not result.select('form')
for link in result.select('a[href^="#"]'):
    assert link['href'][1:] in ids, link['href']
path.write_bytes(out.encode('utf-8'))
