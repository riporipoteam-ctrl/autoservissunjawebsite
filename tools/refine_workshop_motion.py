"""Apply the motion-system integration to the pinned draft, keeping map rules out of scope."""
from pathlib import Path

css = Path('css/workshop-motion.css')
source = css.read_text()
assert '#workshopStory .map-quick-link{color:#06398f;border-radius:99px}' in source
source = source.replace('#workshopStory .map-quick-link{color:#06398f;border-radius:99px}\n', '')
source = source.replace(':is(#workshopStory,#wmHeader,#wmDock,#siteFooter) :is(a,button,[tabindex]):focus-visible', ':is(#workshopStory,#wmHeader,#wmDock,#siteFooter) :is(a,button,[tabindex]):not(.map-quick-link):focus-visible')
source = source.replace('Mobile screens', 'Mobile screens').replace('padding-bottom:clamp(120px,24vh,240px)', 'padding-bottom:clamp(240px,51svh,575px)')
source = source.replace('calc(-48deg + var(--wm-hero,0)*133deg)', 'calc(-64deg + var(--wm-hero,0)*128deg)')
source = source.replace('translate3d(0,calc(var(--wm-hero,0)*-13px),0) scale(calc(1 + .11*var(--wm-hero,0)))', 'translate3d(0,calc(var(--wm-hero,0)*-27px*var(--wm-amplitude,1)),0) scale(calc(1 + .19*var(--wm-hero,0)*var(--wm-amplitude,1)))')
source = source.replace('calc(var(--wm-hero,0)*-37px)', 'calc(var(--wm-hero,0)*-44px)')
source = source.replace('calc(var(--wm-drift,0px)*.25)', 'calc(var(--wm-drift,0px)*var(--wm-frame-travel,.62))')
source = source.replace('calc(var(--wm-drift,0px)*-.42),0)', 'calc(var(--wm-drift,0px)*-.9),0) rotate(calc(var(--wm-sweep,0)*-8deg))')
css.write_text(source + '''
/* Scene rhythm and the hand-off from the opening dial to the service floor. */
#workshopStory .wm-section{padding:var(--wm-space) 0!important}
#workshopStory #usluge{background:var(--wm-blue)!important;border-top:0}
#workshopStory #galerija{background:var(--wm-dark)!important}
#workshopStory #o-nama{background:#e6f2fe!important}
#workshopStory #recenzije{padding:clamp(28px,4.6vw,60px) 0!important}
#workshopStory #lokacija{padding-bottom:24px!important}
#workshopStory #kontakt{background:#0a3b96!important}
#workshopStory h2{hyphens:auto}
#workshopStory>section[id]{scroll-margin-top:0}
#wmHeader .wm-header-tools{display:flex;align-items:center;gap:7px}
#wmHeader .wm-motion-switch{display:grid;place-items:center;width:45px;min-width:45px;height:45px;padding:0;background:#e8f3ff;color:#113e78;border-color:#94b6dd}
#wmHeader .wm-motion-switch:hover,#wmHeader .wm-motion-switch[aria-pressed=true]{background:#cfE5ff;color:#073a90}
.wm-motion-switch .wm-play-icon,.wm-motion-switch[aria-pressed=true] .wm-pause-icon{display:none}
.wm-motion-switch[aria-pressed=true] .wm-play-icon{display:inline}
#wmHeader .nav-link.active:not([aria-current=location]):not(:hover){background:none!important;color:var(--wm-ink)!important}
#pocetna .wm-pin{isolation:isolate}
.wm-hero-copy h1{width:fit-content}
.wm-gauge{width:118%;inset:-16% -2% auto auto;opacity:.86;transform:translate3d(0,calc(-23px*var(--wm-hero)*var(--wm-amplitude,1)),0)}
.wm-gauge .wm-needle{transform-box:view-box}
#workshopStory #header-carousel .carousel-inner{border:0!important}
#workshopStory #header-carousel .wm-film .hero-bg{width:100%!important;filter:none!important}
#workshopStory #header-carousel .wm-film{background:#173651}
#workshopStory #header-carousel .carousel-item picture img{border-radius:0!important}
.wm-odometer-track,.wm-coordinate i{position:relative;flex:1;min-width:2px;height:5px;border-block:1px solid #6f9cc7;background:repeating-linear-gradient(90deg,transparent 0 9px,#88add2 9px 10px);overflow:hidden}
.wm-odometer-track::after,.wm-coordinate i::after{content:'';position:absolute;inset:0;background:var(--wm-hi);transform-origin:left;transform:scaleX(var(--wm-hero,0))}
.wm-hero-handoff{display:none;pointer-events:none}
.wm-coordinate{display:flex;align-items:center;gap:10px;margin-top:18px;color:#1b4777;font:700 clamp(.65rem,1.3vw,.83rem)/1.2 system-ui,sans-serif;letter-spacing:.07em;font-variant-numeric:tabular-nums;white-space:nowrap}
.wm-coordinate i::after{transform:scaleX(var(--wm-entry,1))}
#workshopStory #usluge .tab-pane{animation:none!important;transform:none!important}
#workshopStory #usluge .wm-service-copy p{margin-bottom:0!important}
#workshopStory #usluge .wm-service-copy li{color:#355276!important}
#workshopStory #usluge .service-media-frame{position:relative;min-width:0;grid-template-rows:minmax(0,1fr);grid-template-columns:minmax(0,1fr);background:#d7e9fc}
#workshopStory #usluge .service-media-frame img{display:block;position:relative;inset:auto;min-width:0;max-height:100%!important;transform:translate3d(0,calc(var(--wm-drift,0px)*.33),0)}
#workshopStory #usluge .service-media-frame::after{display:block;content:'';inset:0 0 0 auto;position:absolute;background:linear-gradient(90deg,#d7e9fc00,#d7e9fc);width:12%;transform:scaleX(calc(1 - var(--wm-entry,1)));transform-origin:right;pointer-events:none}
#workshopStory #galerija .wm-frame{box-shadow:none!important;border-color:#5579a8!important;background:#143454!important}
.wm-frame-photo{position:relative;grid-template: minmax(0,1fr) / minmax(0,1fr);background:var(--gallery-bg),#123152;background-size:0}
#workshopStory #galerija .wm-frame img{position:absolute;inset:0;padding:0;object-position:center;background:none!important}
.wm-frame:nth-child(even){--wm-frame-travel:-.66}
.wm-frame:nth-child(3){--wm-frame-travel:1.04}
.wm-frame:nth-child(5){--wm-frame-travel:.86}
.wm-frame-foot .wm-icon{margin:0;flex:none;border-radius:50%}
#workshopStory #kontakt .wm-number{max-width:100%;overflow-wrap:normal;white-space:normal}
#workshopStory #kontakt .wm-contact-info p{color:#e2f0ff}
#workshopStory #kontakt::before{transform:translate3d(calc(var(--wm-drift,0px)*2.2),calc(var(--wm-drift,0px)*-.92),0) scale(calc(1 + var(--wm-sweep,0)*.20));inset:auto -12% -86% auto}
#siteFooter .hours-list p{border-radius:2px;border-bottom:1px dotted #516f94}
#siteFooter .hours-list p.today{background:#183c68}
#siteFooter .wm-footer-links a{min-height:32px;display:inline-flex;align-items:center;text-decoration:underline}
#siteFooter .wm-foot-end a{text-decoration:underline}
#backTop.wm-icon{border-radius:50%!important;box-shadow:none!important}
@media (min-width:1024px) and (min-height:690px){
 html[data-workshop-motion=full] #pocetna{background:linear-gradient(180deg,var(--wm-sky) 74%,var(--wm-blue) 98%)}
 html[data-workshop-motion=full] .wm-hero-handoff{display:block;position:absolute;inset:auto 0 0;height:clamp(25px,9vh,108px);background:var(--wm-blue);transform-origin:right bottom;transform:scale(calc(.055 + var(--wm-hero)*.945),calc(.055 + var(--wm-hero)*.31));clip-path:polygon(5% 0,100% 0,100% 100%,0 100%);z-index:-1}
 html[data-workshop-motion=full] .wm-hero-visual{transform:translate3d(0,calc(var(--wm-hero)*-22px),0)}
}
html[data-workshop-motion=light]{--wm-amplitude:.34}
@media (max-width:991.98px){
 #wmHeader #navbarCollapse{position:absolute;top:100%;left:0;right:0;width:auto;padding-inline:var(--wm-edge);background:var(--wm-paper);box-shadow:0 10px 24px #132f5140}
 #wmHeader #navbarCollapse.show{max-height:calc(100svh - var(--wm-nav) - 70px);overflow-y:auto}
 #wmHeader .wm-nav>.wm-wrap{flex-wrap:nowrap}
 #wmHeader .navbar-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}
 #wmDock{box-shadow:0 -4px 15px #08274c22!important;border:1px solid #6c8fb7!important}
 #wmDock a{padding:6px 3px!important;min-height:46px;font-size:.81rem!important;border-radius:8px!important}
 #siteFooter{padding-bottom:calc(70px + env(safe-area-inset-bottom,0px))!important}
}
@media (max-width:767.98px){
 .wm-gauge{width:70%;inset:-24% 0 auto auto}
}
html[data-workshop-motion=off]{scroll-behavior:auto!important}
html[data-workshop-motion=off] #workshopStory .stars.on :is(.stars-fg,.stars-fg i){animation:none!important;transition:none!important}
@media (prefers-reduced-motion:reduce){
 #pocetna .wm-hero-copy h1,#workshopStory .wm-arrived,#workshopStory #usluge .tab-pane.active .service-media-frame,#workshopStory .stars.on :is(.stars-fg,.stars-fg i){animation:none!important;transition:none!important}
}
''')

legacy=Path('js/main.js')
source=legacy.read_text()
old='''            if (document.hidden || document.documentElement.classList.contains("sunja-intro-active")) return;
            stop();'''
new='''            if (document.hidden || document.documentElement.classList.contains("sunja-intro-active")) return;
            stop();
            // Workshop in Motion owns its playback state, including the no-Bootstrap timer.
            if (document.documentElement.dataset.workshopMotion === "off" ||
                ((reduceMotion || perfLite) && !!document.getElementById("workshopStory"))) return;'''
# Initialise fallback button wiring before suppressing just its auto-play.
new=new.replace('''            if (document.documentElement.dataset.workshopMotion === "off" ||
                ((reduceMotion || perfLite) && !!document.getElementById("workshopStory"))) return;''','''            var shouldPlay = document.documentElement.dataset.workshopMotion !== "off" &&
                !((reduceMotion || perfLite) && document.getElementById("workshopStory") &&
                  !(document.documentElement.dataset.workshopMotion &&
                    document.documentElement.dataset.workshopMotion !== "off"));''')
assert source.count(old)==1
source=source.replace(old,new)
source=source.replace('                    instance.cycle();\n                    return;', '                    if (shouldPlay) instance.cycle();\n                    return;',1)
source=source.replace('            fallbackTimer = window.setInterval(function () { rotateBy(1); }, 6500);','            if (shouldPlay) fallbackTimer = window.setInterval(function () { rotateBy(1); }, 6500);',1)
source=source.replace('        window.addEventListener("sunja:intro-finished", startCycle);','        window.addEventListener("sunja:intro-finished", startCycle);\n        window.addEventListener("sunja:workshop-motion-change", startCycle);',1)
source=source.replace('(reduceMotion || fastTouchNavigation) ?','(reduceMotion || fastTouchNavigation || document.documentElement.dataset.workshopMotion === "off") ?')
legacy.write_text(source)

motion = Path('js/workshop-motion.js')
source=motion.read_text()
source=source.replace('  if (!hero) return;','  if (!hero) return;').replace("  const toggle = document.querySelector('[data-wm-control]');", "  if (!pin || !carousel || !nav) return;\n  const toggle = document.querySelector('[data-wm-control]');")
source=source.replace("    const next = paused || reduce.matches || root.classList.contains('perf-lite') ? 'off' : wide.matches ? 'full' : 'light';\n    if (mode !== next) {", "    const next = paused || reduce.matches || root.classList.contains('perf-lite') ? 'off' : wide.matches ? 'full' : 'light';\n    if (root.classList.contains('sunja-intro-active')) return;\n    if (mode !== next) {")
source=source.replace("          scene.style.removeProperty('--wm-drift');", "          scene.style.removeProperty('--wm-drift');\n          scene.style.removeProperty('--wm-entry');\n          scene.style.removeProperty('--wm-sweep');")
source=source.replace("    }\n    if (toggle && toggleText)","      window.dispatchEvent(new Event('sunja:workshop-motion-change'));\n    }\n    if (toggle && toggleText)",1)
source=source.replace("      toggleText.textContent = paused ? 'Pokreni animacije' : 'Pauziraj animacije';", "      toggleText.textContent = 'Smanjeno kretanje';\n      toggle.title = paused ? 'Pokreni animacije stranice' : 'Pauziraj animacije stranice';")
source=source.replace('    heroSpan = Math.max(view * .46, hero.offsetHeight - pin.offsetHeight);', "    heroSpan = mode === 'full' ? Math.max(1, hero.offsetHeight - pin.offsetHeight) : Math.max(view * .53, hero.offsetHeight * .74);")
source=source.replace("    hero.style.setProperty('--wm-hero', clamp((y - (bounds[0]?.top || 0)) / heroSpan).toFixed(4));", "    const top = Math.max(0, (bounds[0]?.top || 0) - (document.getElementById('wmHeader')?.offsetHeight || 0));\n    hero.style.setProperty('--wm-hero', clamp((y - top) / heroSpan).toFixed(4));")
source=source.replace("      const phase = clamp((sample - scene.top + view * .34) / (scene.height + view * .64));", "      const phase = clamp((y + view * .90 - scene.top) / (Math.min(scene.height, view) + view * .42));")
source=source.replace("      scene.el.style.setProperty('--wm-phase', stamp);", "      scene.el.style.setProperty('--wm-phase', stamp);\n      scene.el.style.setProperty('--wm-entry', clamp(phase * 2.3).toFixed(3));\n      scene.el.style.setProperty('--wm-sweep', (phase - .5).toFixed(3));")
source=source.replace("(mode === 'full' ? 60 : 16)","(mode === 'full' ? 89 : 18)")
old="""    paused = !paused;
    readMode();
    if (!paused && mode !== 'off' && !document.hidden) window.bootstrap?.Carousel.getInstance(carousel)?.cycle();"""
new="""    // Preserve the reader's place when changing the opening scene's height.
    const anchor = hero.getBoundingClientRect().bottom <= window.innerHeight * .28 ? story.querySelector('#usluge') : null;
    const anchorTop = anchor?.getBoundingClientRect().top;
    paused = !paused;
    readMode();
    if (anchor) {
      const shift = anchor.getBoundingClientRect().top - anchorTop;
      if (Math.abs(shift) > 1) window.scrollBy({top:shift,behavior:'instant'});
    }"""
assert source.count(old)==1
source=source.replace(old,new)
source=source.replace("  document.addEventListener('shown.bs.tab'", "  document.querySelector('.wm-skip')?.addEventListener('click', () => story.focus({preventScroll:true}));\n  document.addEventListener('shown.bs.tab'")
motion.write_text(source)
