# Auto Servis Šunja — Approved UI Overhaul Plan

## Product and implementation

This is a single-page static workshop website. The redesign will keep the existing anchor-based information architecture and real business content while replacing the template-heavy visual rhythm with a workshop-editorial system. The implementation will stay within the current HTML/CSS/vanilla-JS stack so the GitHub Pages deployment remains simple and the opening logo intro remains an isolated protected contract.

The primary work is a tokenized CSS layer for the header, hero, action controls, service navigation, gallery, reviews, map, contact, and footer. Existing selectors and IDs remain available to preserve deep links, tests, and direct actions. Small HTML additions are limited to semantics, responsive image metadata, and device-profile hooks.

The adaptive layer will be a lightweight client-side capability profile. It uses viewport class, coarse pointer/hover support, reduced-motion preference, Save-Data, device-memory/CPU hints, and connection quality where available. It writes only a non-identifying `data-sunja-device-profile` value to the document and uses that value to control image density, motion, map startup, and noncritical work. It will not fingerprint users or send telemetry.

The intro listener will continue to warm only the critical hero asset while the protected logo sequence plays. Noncritical map, gallery enhancement, and reveal work will start after `sunja:intro-finished`, with a fallback for `skipIntro` and browsers without the event.

## Design system

The approved system is editorial workshop utility: Šunja blue for action and brand recognition; ink navy and graphite for structure; warm off-white for calm reading surfaces; and a restrained amber status accent. Typography keeps the existing Barlow/Ubuntu relationship but tightens scale, line length, and weight contrast. Layout uses asymmetrical editorial bands, a strong content rail, photo-led panels, and a persistent but quiet action system. Post-intro motion is short, compositor-friendly, and disabled or reduced for low-resource and reduced-motion profiles.

## Project structure

- `index.html`: single-page structure, metadata, anchor routes, content blocks, and protected intro markup.
- `css/style.css`: existing tokens and component rules, followed by the approved overhaul layer.
- `js/main.js`: existing interactions plus adaptive profile and deferred noncritical initialization hooks.
- `assets/`, `img/`: real workshop imagery and owner-supplied brand assets.
- `tools/`: static checks, browser smoke checks, and live verifier.

## Protected contracts

Do not change the exact logo assets, intro timing/sequence/exit behavior, anchor IDs, navigation labels, phone/directions/WhatsApp links, service-tab data hooks, map fallback, review data, gallery source links, legal/template credit, or reduced-motion content availability.

## Validation and delivery

Run static checks, browser acceptance at 375×812, 768×1024, 1280×720, and 1920×1080, console and overflow checks, and the live verifier. Review changed files, commit to `main`, push to the connected GitHub repository, and only publish after the tested push is confirmed. The public URL will be rechecked after deployment.
