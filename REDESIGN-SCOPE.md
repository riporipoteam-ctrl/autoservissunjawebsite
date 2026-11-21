# Auto Servis Šunja — UI Overhaul Scope

## Baseline

- **Mode:** Redesign · Overhaul, with protected identity and interaction contracts.
- **Public URL:** https://autosunja.com/
- **Repository:** `autoservissunjawebsite`, branch `main`, baseline `13f517f5e4599feaae5bfef3eb77ab1e0418a5f0`
- **Routes:** single-page site with anchors for `#pocetna`, `#o-nama`, `#usluge`, `#galerija`, `#recenzije`, `#lokacija`, and `#kontakt`.
- **Baseline checks:** 90 static frontend tests pass; live verifier passes; public HTML returns 200.
- **Baseline viewports inspected:** 375px mobile, 768px tablet, 1280px desktop, 1920px wide desktop.

## Preserve

- The owner's exact logo artwork, intro animation frames, animation order, and protected intro timing/behavior.
- Existing real workshop photos, service names, phone number, address, social links, map/directions links, review content, and legal/template credit.
- Existing anchor IDs, navigation labels, direct phone/directions/WhatsApp actions, service tabs, gallery links, map fallback, rating block, and mobile call bar.
- Existing reduced-motion behavior and no-horizontal-overflow guard.

## Improve

- Replace the current template-heavy visual rhythm with a more intentional workshop identity: stronger editorial hierarchy, clearer section transitions, fewer competing treatments, and better use of real photography.
- Normalize spacing, type scale, container widths, card geometry, controls, focus states, and touch targets across mobile/tablet/desktop.
- Recompose hero and service navigation so the primary path is obvious: call, directions, and service selection.
- Make gallery, reviews, location, and contact feel like a coherent conversion sequence instead of isolated template sections.
- Add adaptive client-side delivery: detect viewport, pointer/hover capability, reduced motion, Save-Data, device memory, CPU hints, and connection quality; expose only a non-identifying `data-sunja-device-profile` attribute and use it to tune image density, map initialization, animation intensity, and lazy loading.
- Keep all content usable while the intro is playing; preload only the true critical hero asset and schedule noncritical work after the intro closes.
- Reduce render-blocking third-party work and improve image loading with responsive sources, intrinsic dimensions, lazy decoding, and below-fold deferral.

## Remove or consolidate

- Unnecessary decorative repetition, oversized template spacing, generic pill/card treatments, and visual noise that does not support a customer action.
- Unnecessary above-the-fold third-party work and premature map/gallery initialization.
- The unused-preload warning caused by preloading the intro asset without matching its later Blob playback path.

## Protected intro contract

Do not change the `#sunjaIntro` markup, the owner-uploaded source asset, the generated exact-logo animation asset, the intro playback clock, the 25+ experience sequence, or the intro exit behavior except where needed to schedule unrelated page work behind it. The redesign begins after `sunja:intro-finished`.

## Design Read

```yaml
artifact: local-service automotive repair landing page
 audience: drivers in Goražde who need immediate trust, diagnosis, repair, or directions
visual-language: editorial workshop utility — precise blue, warm neutral surfaces, documentary photography, strong typographic signposting
mode: overhaul with protected brand and content contracts
visual-variance: 7/10
motion-intensity: 4/10
information-density: 6/10
asset-dependence: 8/10
brand-fidelity: 10/10
```

## Design decisions

- **Movement:** editorial information architecture with a restrained industrial/workshop character; not a generic SaaS dashboard and not a glossy automotive showroom.
- **Color philosophy:** keep Šunja blue as the recognizable action color; pair it with ink navy, warm off-white, graphite, and a small amber status accent. Color should clarify action and operating status, not decorate every card.
- **Typography:** retain the current brand-compatible Barlow/Ubuntu relationship where assets and CSS already depend on it, but use a more disciplined scale: compact utility text, assertive section titles, and readable 16–18px body copy with controlled line length.
- **Layout paradigm:** asymmetric editorial bands and anchored conversion panels instead of repeated centered Bootstrap rows. Use one strong content rail with occasional edge-to-edge image breaks.
- **Signature elements:** blue service index rail, photo-led workshop panels with technical captions, and a persistent but quiet action system for call/directions/WhatsApp.
- **Interaction philosophy:** every motion communicates state or hierarchy. Hover is additive, never required. Touch targets stay at least 44px. Reduced-motion and low-resource profiles get the same content with fewer effects.
- **Animation:** preserve the opening logo animation exactly. After it, use short compositor-friendly fades/slides (180–420ms), no parallax dependency, no scroll-jank, and no animation on low-resource or reduced-motion profiles.
- **Brand essence:** a trustworthy local workshop that makes the next step obvious. Personality: capable, direct, grounded.
- **Voice:** concise and practical. Example: “Recite šta auto radi. Mi ćemo pronaći zašto.” / “Pozovite prije dolaska.”

## Highest-risk change

Recomposing the hero and the service/contact sequence without losing the owner's real content or one-tap actions. Mitigation: preserve all IDs, links, labels, and data hooks; make the redesign CSS-first with small semantic markup changes only where necessary.

## Rollback / fallback

The baseline commit remains untouched. All redesign work will be committed as a separate commit, with existing test scripts run before push and browser acceptance rerun at the same four viewport classes before any publish action.
