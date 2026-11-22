"""Correct the motion draft's Bootstrap 5.0 integration and strengthen its click targets."""
from pathlib import Path

p=Path('js/main.js')
s=p.read_text()
a='''                    instance = window.bootstrap.Carousel.getOrCreateInstance(hero, {
                        interval: 6500, ride: false, pause: false, wrap: true, touch: true
                    });'''
b='''                    var Carousel = window.bootstrap.Carousel;
                    instance = Carousel.getInstance(hero) || new Carousel(hero, {
                        interval: 6500, ride: false, pause: false, wrap: true, touch: true
                    });'''
assert s.count(a)==1
s=s.replace(a,b)
s=s.replace('bootstrap.Collapse.getOrCreateInstance(el, { toggle: false }).hide();', '(bootstrap.Collapse.getInstance(el) || new bootstrap.Collapse(el, { toggle: false })).hide();')
p.write_text(s)

p=Path('js/workshop-motion.js')
s=p.read_text()
a="  carousel.addEventListener('slid.bs.carousel', imageDeck);"
assert s.count(a)==1
s=s.replace(a,a+"\n  // Bootstrap 5.0 restarts automatic playback when the selected indicator is clicked.\n  carousel.addEventListener('click', () => { if (mode === 'off') setTimeout(syncCarousel, 0); });")
s=s.replace('window.bootstrap?.Carousel.getInstance(carousel)', 'window.bootstrap?.Carousel?.getInstance(carousel)')
p.write_text(s)

p=Path('index.html')
s=p.read_text()
a='#wmHeader #navbarCollapse{display:block!important}#wmHeader .navbar-nav{display:flex;flex-flow:row wrap}'
b='#wmHeader .wm-nav>.wm-wrap{flex-wrap:wrap}#wmHeader #navbarCollapse{display:block!important;position:static;width:100%;padding:0;box-shadow:none}#wmHeader .navbar-nav{display:flex;flex-flow:row wrap}'
assert s.count(a)==1
s=s.replace(a,b).replace('css/workshop-motion.css?v=2.0','css/workshop-motion.css?v=2.1').replace('js/workshop-motion.js?v=2.0','js/workshop-motion.js?v=2.1').replace('js/main.js?v=40.1','js/main.js?v=40.2')
p.write_text(s)

p=Path('css/workshop-motion.css')
s=p.read_text()
s+='''
/* Clicking a photograph still opens its original gallery post. */
#workshopStory #galerija .wm-frame .gallery-tile-link{position:static}
#workshopStory #galerija .wm-frame .gallery-tile-link::after{content:'';position:absolute;inset:0;z-index:1}
#workshopStory #galerija .wm-frame:focus-within{outline:2px solid #ffdc94;outline-offset:3px}
#workshopStory #galerija .wm-frame:hover .wm-frame-foot{background:#1b4777}
#wmHeader .wm-motion-switch:hover,#wmHeader .wm-motion-switch[aria-pressed=true]{background:#cfe5ff}
'''
p.write_text(s)
