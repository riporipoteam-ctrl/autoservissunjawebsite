"""Run the capture suite with a settled, pixel-measured real viewport control."""
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text()
prefix, marker, suffix = source.partition('results,failed = [],[]\n')
assert marker, 'Unexpected capture-suite version'
exec(compile(prefix, sys.argv[1], 'exec'))


def compare_view(p, frames, origin):
    seen = shot(p)
    # Keep the control applied across real frames. Passing style= to a one-off
    # capture can race composited layers on some Chromium phone configurations.
    style = p.add_style_tag(content=HIDE_IMAGES + f'{PHOTO}{{opacity:0!important;transition:none!important}}')
    try:
        raf(p, 9)
        clear = shot(p)
        return seen, clear, photos_painted(seen, clear, frames, origin)
    finally:
        style.evaluate('e=>e.remove()')
        raf(p, 9)


def observe_mobile(p, path, w, h, photos):
    saved, scores = 0, {}
    complete_test = 'e=>e.complete && e.naturalWidth>0'
    for top in sorted({r[1] for r in photos}):
        goal = round(top - (108 if not scores else min(165,h*.22)))
        approx_scroll(p, goal, w, h)
        p.mouse.move(3,round(h*.5))
        origin = round(p.evaluate('scrollY'))
        fresh = photo_boxes(p)
        idx = [i for i,(_,a,_,b) in enumerate(fresh) if a-origin>=68 and b-origin<=h-77 and i not in scores]
        if not idx:
            continue
        for i in idx:
            p.wait_for_function(complete_test,arg=p.locator(PHOTO).nth(i).element_handle())
        raf(p, 9)
        crops=[fresh[i] for i in idx]
        shown,clear,normal=compare_view(p,crops,origin)
        trace=TRACE/path.name
        if min(normal)<.08:
            shown.save(trace/f'view-{saved}-initial.png')
            clear.save(trace/f'view-{saved}-control.png')
            # Keep the normal lazy-loading policy. Check an untouched normal
            # viewport again before asking explicitly for image decoding.
            p.wait_for_timeout(1100)
            shown,clear,normal=compare_view(p,crops,origin)
            shown.save(trace/f'view-{saved}-settled.png')
            clear.save(trace/f'view-{saved}-settled-control.png')
            if min(normal)<.08:
                for i in idx:
                    p.locator(PHOTO).nth(i).evaluate('img=>img.decode()')
                raf(p, 10)
                decoded, decoded_clear, after_decode = compare_view(p,crops,origin)
                decoded.save(trace/f'view-{saved}-decoded.png')
                decoded_clear.save(trace/f'view-{saved}-decoded-control.png')
                print(f'{path.name} photos {[i+1 for i in idx]} before and after explicit decode: {normal} -> {after_decode}',flush=True)
                print(p.locator(PHOTO).evaluate_all('''a=>a.map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {src:e.currentSrc,ready:e.complete,natural:[e.naturalWidth,e.naturalHeight],rect:[r.x,r.y,r.width,r.height],scrollY,transform:s.transform,visibility:s.visibility,opacity:s.opacity}})'''),flush=True)
        scores.update(zip(idx,normal))
        shown.save(path/f'{15+saved:02}-gallery-in-viewport.png')
        saved+=1
        if len(scores)==5:
            break
    return [scores.get(i,0) for i in range(5)]


exec(compile(marker + suffix, sys.argv[1], 'exec'))
