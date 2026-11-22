/* Workshop in Motion: native scrolling, one frame per paint, no external library. */
(() => {
  'use strict';
  const root = document.documentElement;
  const story = document.getElementById('workshopStory');
  const hero = story?.querySelector('#pocetna');
  if (!hero) return;
  const pin = hero.querySelector('.wm-pin');
  const carousel = hero.querySelector('#header-carousel');
  const nav = document.getElementById('motionChapters');
  const toggle = document.querySelector('[data-wm-control]');
  const toggleText = toggle?.querySelector('span');
  const chapters = [...story.querySelectorAll('[data-wm-chapter]')];
  const linkById = new Map([...nav.querySelectorAll('a[href^="#"]')].map(a => [a.hash.slice(1), a]));
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const wide = window.matchMedia('(min-width: 1024px) and (min-height: 690px)');
  const clamp = x => Math.min(1, Math.max(0, x));
  let paused = false, raf = 0, pendingMeasure = true, activeId = '', mode = '', bounds = [], heroSpan = 0, view = 1, total = 1;

  function syncCarousel() {
    const instance = window.bootstrap?.Carousel.getInstance(carousel);
    if (!instance) return;
    if (mode === 'off' || document.hidden || root.classList.contains('sunja-intro-active')) instance.pause();
  }

  function readMode() {
    const next = paused || reduce.matches || root.classList.contains('perf-lite') ? 'off' : wide.matches ? 'full' : 'light';
    if (mode !== next) {
      mode = next;
      root.dataset.workshopMotion = mode;
      pendingMeasure = true;
      if (mode === 'off') {
        hero.style.removeProperty('--wm-hero');
        chapters.forEach(scene => {
          scene.style.removeProperty('--wm-phase');
          scene.style.removeProperty('--wm-drift');
        });
      }
    }
    if (toggle && toggleText) {
      toggle.hidden = reduce.matches || root.classList.contains('perf-lite');
      toggle.setAttribute('aria-pressed', String(paused));
      toggleText.textContent = paused ? 'Pokreni animacije' : 'Pauziraj animacije';
    }
    syncCarousel();
    schedule(true);
  }

  function measure(y) {
    view = Math.max(1, window.innerHeight);
    total = Math.max(1, root.scrollHeight - view);
    bounds = chapters.map(el => {
      const rect = el.getBoundingClientRect();
      return {el, top: rect.top + y, height: rect.height, last: ''};
    });
    heroSpan = Math.max(view * .46, hero.offsetHeight - pin.offsetHeight);
    pendingMeasure = false;
  }

  function frame() {
    raf = 0;
    const y = window.scrollY || 0;
    if (pendingMeasure) measure(y);
    const sample = y + view * .38;
    let next = chapters[0]?.id;
    for (const scene of bounds) if (scene.top <= sample) next = scene.el.id;
    if (next && activeId !== next) {
      linkById.get(activeId)?.removeAttribute('aria-current');
      linkById.get(next)?.setAttribute('aria-current','location');
      activeId = next;
    }
    if (mode === 'off' || document.hidden || root.classList.contains('sunja-intro-active')) return;
    root.style.setProperty('--wm-progress', clamp(y / total).toFixed(4));
    hero.style.setProperty('--wm-hero', clamp((y - (bounds[0]?.top || 0)) / heroSpan).toFixed(4));
    for (const scene of bounds) {
      if (scene.top > y + view * 1.25 || scene.top + scene.height < y - view * .25) continue;
      const phase = clamp((sample - scene.top + view * .34) / (scene.height + view * .64));
      const stamp = phase.toFixed(3);
      if (stamp === scene.last) continue;
      scene.last = stamp;
      scene.el.style.setProperty('--wm-phase', stamp);
      scene.el.style.setProperty('--wm-drift', `${Math.round((phase - .5) * (mode === 'full' ? 60 : 16))}px`);
    }
  }

  function schedule(invalidate = false) {
    if (invalidate) pendingMeasure = true;
    if (!raf) raf = requestAnimationFrame(frame);
  }

  function afterIntro() {
    if (root.classList.contains('sunja-intro-active')) return;
    root.dataset.wmReady = '1';
    readMode();
  }

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        entry.target.classList.add('wm-arrived');
        observer.unobserve(entry.target);
      }
    }, {rootMargin:'0px 0px -9% 0px',threshold:.15});
    story.querySelectorAll('[data-wm-reveal]').forEach(node => observer.observe(node));
  }
  if ('ResizeObserver' in window) {
    const resize = new ResizeObserver(() => schedule(true));
    resize.observe(story);
    chapters.forEach(el => resize.observe(el));
  }
  toggle?.addEventListener('click', () => {
    paused = !paused;
    readMode();
    if (!paused && mode !== 'off' && !document.hidden) window.bootstrap?.Carousel.getInstance(carousel)?.cycle();
  });
  const imageDeck = (event) => {
    if (!carousel.contains(event.target)) return;
    if (mode === 'off') syncCarousel();
  };
  carousel.addEventListener('slid.bs.carousel', imageDeck);
  document.addEventListener('shown.bs.tab', () => schedule(true));
  window.addEventListener('scroll', () => schedule(), {passive:true});
  window.addEventListener('resize', readMode, {passive:true});
  window.addEventListener('load', afterIntro, {once:true});
  window.addEventListener('pageshow', afterIntro);
  window.addEventListener('sunja:intro-finished', afterIntro);
  document.addEventListener('visibilitychange', afterIntro);
  for (const mq of [reduce, wide]) {
    if (mq.addEventListener) mq.addEventListener('change', readMode);
    else mq.addListener(readMode);
  }
  afterIntro();
})();
