# Auto Servis Šunja — autosunja.sitey.my

Public website for **Auto Servis Šunja** (Peugeot specialist), Hajra Lakovića 38, 73000 Goražde.
Served by GitHub Pages at [autosunja.sitey.my](https://autosunja.sitey.my).

## V4 design (Nov 2026)
- White, clean layout based on the free **CarServ** car-repair template structure (HTML Codex), in Šunja blue.
- Sections: topbar + sticky nav, hero with photo car and floating chips, blue facts counters strip, services, **interactive 3D viewer**, about, steps, Google review + Instagram, SMS booking form, contact + hours, FAQ, footer.
- Animations: GSAP + ScrollTrigger reveals and counters, Lenis smooth scrolling, hero car mouse-tilt.
- Logo: transparent versions generated from the original (`assets/sunja-logo-transparent.webp/.png`).

## 3D model
- `assets/peugeot-308.glb` — a real **Peugeot 308 CC** (model: Scopia/SweetHome3D library, converted from OBJ).
- Three.js is **self-hosted** under `assets/vendor/` (incl. the Draco decoder under `assets/vendor/draco/`), so the viewer has no CDN dependency.
- In the viewer the model gets position-welded smooth shading and a clearcoat "paint" material; visitors can rotate, zoom and change the body colour.

## Good to know
- The open/closed badge and the highlighted hours row compute the time in Europe/Sarajevo.
- The booking form composes an SMS to the shop number (061 297 847) — no backend needed.
