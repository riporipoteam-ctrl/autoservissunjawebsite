(function () {
    "use strict";

    var reduceMotion = false;
    try {
        reduceMotion = !!(window.matchMedia &&
            window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) {}

    var connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    var saveData = !!(connection && connection.saveData);
    var lowMemory = typeof navigator.deviceMemory === "number" && navigator.deviceMemory <= 2;
    var lowCpu = typeof navigator.hardwareConcurrency === "number" && navigator.hardwareConcurrency <= 2;
    var perfLite = saveData || lowMemory || lowCpu;

    if (perfLite) document.documentElement.classList.add("perf-lite");

    // Reveal only when useful. All content is visible and clickable before
    // this runs; nothing is blocked behind an animation or a loading screen.
    if (!reduceMotion && !perfLite && "IntersectionObserver" in window) {
        var revealObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-revealed");
                revealObserver.unobserve(entry.target);
            });
        }, { threshold: 0.08 });
        document.querySelectorAll(".wow").forEach(function (node) {
            revealObserver.observe(node);
        });
    }

    // The first hero photo retains fetchpriority=high. Once the page is loaded,
    // fetch the other two permanent slides on capable connections so Bootstrap
    // does not reveal an empty lazy image during the automatic transition.
    if (!saveData && !perfLite) {
        window.addEventListener("load", function () {
            var slides = document.querySelectorAll(".carousel-item:not(.active) picture img");
            slides.forEach(function (slideImg) {
                slideImg.decoding = "async";
                slideImg.loading = "eager";
            });
        }, { once: true });
    }

    var backTop = document.querySelector(".back-to-top");
    var chromeVisible = null;
    var scrollRaf = 0;

    function syncScrollChrome() {
        scrollRaf = 0;
        var show = (window.pageYOffset || document.documentElement.scrollTop || 0) > 300;
        if (show === chromeVisible) return;
        chromeVisible = show;
        document.documentElement.classList.toggle("is-scrolled", show);
        if (backTop) backTop.classList.toggle("is-visible", show);
    }

    function scheduleScrollChrome() {
        if (!scrollRaf) scrollRaf = window.requestAnimationFrame(syncScrollChrome);
    }

    window.addEventListener("scroll", scheduleScrollChrome, { passive: true });
    window.addEventListener("resize", scheduleScrollChrome, { passive: true });
    window.addEventListener("pageshow", scheduleScrollChrome);
    syncScrollChrome();

    // One tap initiates one native scroll. No custom 1.9s animation loop.
    function scrollToTopSmoothly() {
        window.scrollTo({ top: 0, behavior: (reduceMotion || fastTouchNavigation) ? "auto" : "smooth" });
    }
    if (backTop) {
        backTop.addEventListener("click", function (event) {
            event.preventDefault();
            scrollToTopSmoothly();
        });
    }

    // The floating mobile dock must never cover a booking action or form.
    // Compare against its REST position, not its animated rectangle, so hiding
    // it cannot cause a show/hide oscillation. One animation frame per scroll.
    var actionDock = document.querySelector(".mobile-callbar.sunja-liquid-bottom");
    var dockFrame = 0;
    var dockActions = document.querySelectorAll(
        "#o-nama .ps-3 > span, #o-nama a.btn, " +
        ".team-item a.gallery-tile-link, .social-tile, " +
        "#usluge .nav button, #usluge a.btn, #kontakt a.btn, " +
        "#recenzije a.btn, #galerija a.btn, " +
        "#termin input, #termin select, #termin textarea, " +
        "#termin button, #header-carousel .carousel-caption a.btn, " +
        ".map-quick-link, #siteFooter"
    );
    function syncActionDock() {
        dockFrame = 0;
        if (!actionDock || window.innerWidth >= 992) {
            document.documentElement.classList.remove("dock-avoiding-action");
            return;
        }
        var focus = document.activeElement;
        var isEditing = !!(focus && /^(INPUT|SELECT|TEXTAREA)$/.test(focus.tagName));
        var viewport = window.visualViewport;
        var keyboardOpen = !!(viewport &&
            viewport.height + viewport.offsetTop < window.innerHeight - 120);
        var dockStyle = window.getComputedStyle(actionDock);
        var bottomInset = parseFloat(dockStyle.bottom) || 0;
        var leftInset = parseFloat(dockStyle.left) || 0;
        var dockTop = window.innerHeight - bottomInset - actionDock.offsetHeight;
        var dockBottom = window.innerHeight - bottomInset;
        var dockRight = leftInset + actionDock.offsetWidth;
        var collides = false;
        if (!isEditing && !keyboardOpen) {
            for (var i = 0; i < dockActions.length; i++) {
                var rect = dockActions[i].getBoundingClientRect();
                if (rect.width < 2 || rect.height < 2) continue;
                if (rect.bottom > dockTop + 3 && rect.top < dockBottom - 3 &&
                    rect.right > leftInset && rect.left < dockRight) {
                    collides = true;
                    break;
                }
            }
        }
        document.documentElement.classList.toggle(
            "dock-avoiding-action", isEditing || keyboardOpen || collides
        );
    }
    function scheduleActionDock() {
        if (!dockFrame) dockFrame = requestAnimationFrame(syncActionDock);
    }
    if (actionDock) {
        window.addEventListener("scroll", scheduleActionDock, { passive: true });
        window.addEventListener("resize", scheduleActionDock, { passive: true });
        window.addEventListener("pageshow", scheduleActionDock);
        window.addEventListener("load", scheduleActionDock, { once: true });
        document.addEventListener("focusin", scheduleActionDock);
        document.addEventListener("focusout", scheduleActionDock);
        if (window.visualViewport) {
            window.visualViewport.addEventListener("resize", scheduleActionDock, { passive: true });
            window.visualViewport.addEventListener("scroll", scheduleActionDock, { passive: true });
        }
        requestAnimationFrame(syncActionDock);
    }

    // Mark the section the visitor is viewing without scroll-time DOM work.
    if ("IntersectionObserver" in window) {
        var links = Array.prototype.slice.call(
            document.querySelectorAll(".navbar-nav .nav-link[href^='#']")
        );
        var byId = {};
        links.forEach(function (link) {
            var id = link.getAttribute("href").slice(1);
            if (id) byId[id] = link;
        });

        var sections = Object.keys(byId).map(function (id) {
            return document.getElementById(id);
        }).filter(Boolean);

        if (sections.length) {
            var sectionObserver = new IntersectionObserver(function (entries) {
                var visible = entries.filter(function (entry) {
                    return entry.isIntersecting;
                }).sort(function (a, b) {
                    return b.intersectionRatio - a.intersectionRatio;
                })[0];

                if (!visible || !byId[visible.target.id]) return;
                links.forEach(function (link) { link.classList.remove("active"); });
                byId[visible.target.id].classList.add("active");
            }, {
                rootMargin: "-28% 0px -60% 0px",
                threshold: [0.02, 0.12, 0.3]
            });
            sections.forEach(function (section) {
                sectionObserver.observe(section);
            });
        }
    }

    // Touchscreen hash links should arrive immediately on the first tap.
    // Desktop users still get smooth scrolling; no secondary tap or delayed
    // timer is needed on touch/mobile screens.
    var fastTouchNavigation = !!(window.matchMedia &&
        window.matchMedia("(pointer: coarse)").matches);

    // Collapse the mobile menu synchronously on the same gesture, before
    // jumping to the target. A scroll before the collapse used to leave the
    // menu expanded and caused an apparent second-tap requirement.
    function collapseMobileMenu() {
        if (window.innerWidth >= 992) return;
        var el = document.getElementById("navbarCollapse");
        if (!el || !el.classList.contains("show")) return;
        try {
            if (typeof bootstrap !== "undefined" && bootstrap.Collapse) {
                bootstrap.Collapse.getOrCreateInstance(el, { toggle: false }).hide();
            }
        } catch (e) {
            // A failed Bootstrap transition must never cancel the tap.
        }
        if (el.classList.contains("show")) {
            el.classList.remove("show", "collapsing");
            el.classList.add("collapse");
            el.style.height = "";
        }
        var toggle = document.querySelector(".navbar-toggler");
        if (toggle) {
            toggle.setAttribute("aria-expanded", "false");
            toggle.classList.add("collapsed");
        }
    }

    // One tap activates internal links before iOS hover synthesis can swallow
    // the first click. Actual swipes are ignored. All non-hash links keep their
    // trusted browser behaviour (tel:, external posts, directions, WhatsApp).
    function activateSectionLink(link) {
        if (!link) return false;
        var id = (link.getAttribute("href") || "").slice(1);
        var target = id && document.getElementById(id);
        if (!target) return false;

        // The same gesture also preselects services, even if touchend has
        // suppressed the follow-up compatibility click event.
        var service = link.getAttribute("data-service");
        if (service && typeof window.pickServiceVal === "function") {
            window.pickServiceVal(service);
        }
        var serviceTab = link.getAttribute("data-svc-link");
        if (serviceTab) {
            var tab = document.querySelector(
                '[data-bs-target="#tab-pane-' + serviceTab + '"]'
            );
            if (tab) tab.click();
        }

        // Update the address first; a broken menu animation cannot swallow
        // the user's navigation. Scrolling is independent from Bootstrap.
        try {
            history.replaceState(null, "", "#" + encodeURIComponent(id));
        } catch (e) {
            window.location.hash = id;
        }
        if (link.closest("#navbarCollapse")) collapseMobileMenu();
        target.scrollIntoView({
            behavior: (reduceMotion || fastTouchNavigation) ? "auto" : "smooth",
            block: "start"
        });
        return true;
    }

    var startTouch = null;
    var lastHandledTouch = null;
    document.addEventListener("touchstart", function (event) {
        if (event.touches.length !== 1) { startTouch = null; return; }
        var origin = event.target;
        var link = origin && origin.closest ? origin.closest('a[href^="#"]') : null;
        if (!link) { startTouch = null; return; }
        var touch = event.touches[0];
        startTouch = {
            link: link, identifier: touch.identifier,
            x: touch.clientX, y: touch.clientY, at: Date.now()
        };
    }, { capture: true, passive: true });

    document.addEventListener("touchend", function (event) {
        var started = startTouch;
        startTouch = null;
        if (!started || event.changedTouches.length !== 1) return;
        var touch = event.changedTouches[0];
        if (touch.identifier !== started.identifier ||
            Math.abs(touch.clientY - started.y) > 12 ||
            Math.abs(touch.clientX - started.x) > 12 ||
            Date.now() - started.at > 900 || !started.link.isConnected) return;

        // Prevent the browser from emitting a second synthetic click, then
        // perform exactly one section activation from this trusted gesture.
        if (event.cancelable) event.preventDefault();
        lastHandledTouch = { link: started.link, at: Date.now() };
        activateSectionLink(started.link);
    }, { capture: true, passive: false });

    document.addEventListener("touchcancel", function () {
        startTouch = null;
    }, { capture: true, passive: true });

    // Desktop mouse, trackpad and keyboard continue through native click.
    document.addEventListener('click', function (event) {
        var origin = event.target;
        var link = origin && origin.closest ? origin.closest('a[href^="#"]') : null;
        if (!link || event.defaultPrevented || event.button > 0 ||
            event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        if (lastHandledTouch && lastHandledTouch.link === link &&
            Date.now() - lastHandledTouch.at < 900) {
            event.preventDefault();
            return;
        }
        if (!link.getAttribute("href").slice(1)) return;
        event.preventDefault();
        activateSectionLink(link);
    }, true);


    // footer-theme-observer: match browser-owned Safari chrome to the surface
    // behind the dock when the dark footer occupies the bottom of the viewport.
    // Browsers decide whether or how to honour dynamic theme-color changes.
    var themeColor = document.querySelector('meta[name="theme-color"]');
    var brandFooter = document.getElementById("siteFooter");
    var themeFrame = 0;
    function syncFooterTheme() {
        themeFrame = 0;
        if (!themeColor || !brandFooter) return;
        var rect = brandFooter.getBoundingClientRect();
        var inFooter = window.innerWidth < 992 &&
            rect.top <= window.innerHeight * 0.85 &&
            rect.bottom >= window.innerHeight * 0.35;
        var color = inFooter ? "#0b2154" : "#e8f4fc";
        if (themeColor.content !== color) themeColor.content = color;
        document.documentElement.classList.toggle("footer-at-bottom", inFooter);
    }
    function scheduleFooterTheme() {
        if (!themeFrame) themeFrame = requestAnimationFrame(syncFooterTheme);
    }
    if (brandFooter && themeColor) {
        window.addEventListener("scroll", scheduleFooterTheme, { passive: true });
        window.addEventListener("resize", scheduleFooterTheme, { passive: true });
        window.addEventListener("pageshow", scheduleFooterTheme);
        scheduleFooterTheme();
    }

    // Optical lens: SVG feDisplacementMap on an image-aligned copy of actual
    // visible media where available. Safari supports filter: url(#id) on
    // elements even though SVG-in-backdrop-filter is unavailable. Gradients
    // and non-image content retain the native backdrop/filter rim fallback.
    var lenses = Array.prototype.slice.call(
        document.querySelectorAll(".sunja-liquid-header, .sunja-liquid-bottom, #backTop")
    );
    var lensFrame = 0, lastLensTime = 0;
    var lensDisabled = perfLite || !!(window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    var isChromiumDesktop = /Chrom(e|ium)\//.test(navigator.userAgent) &&
        !/(Android|iPhone|iPad|iPod)/i.test(navigator.userAgent);
    if (isChromiumDesktop && !lensDisabled &&
        window.CSS && CSS.supports &&
        CSS.supports("backdrop-filter", "url(#sunja-glass-distortion)")) {
        document.documentElement.classList.add("sunja-optics-chromium");
    }
    function syncLensScene() {
        lensFrame = 0;
        if (lensDisabled || document.hidden || !document.elementsFromPoint) return;
        lastLensTime = performance.now();
        lenses.forEach(function (surface) {
            var layer = surface.querySelector(".sunja-glass-refract");
            if (!layer) return;
            if (getComputedStyle(surface).display === "none") return;
            var r = surface.getBoundingClientRect();
            if (r.bottom < 0 || r.top >= window.innerHeight) return;
            var x = Math.max(1, Math.min(window.innerWidth - 2, r.left + r.width / 2));
            var y = Math.max(1, Math.min(window.innerHeight - 2, r.top + r.height / 2));
            var found = null;
            var stack = document.elementsFromPoint(x, y);
            for (var k = 0; k < stack.length; k++) {
                var candidate = stack[k];
                if (surface === candidate || surface.contains(candidate)) continue;
                if (candidate.tagName === "IMG") {
                    var cr = candidate.getBoundingClientRect();
                    if (cr.width > 90 && cr.height > 75 &&
                        candidate.naturalWidth && candidate.naturalHeight) {
                        found = candidate;
                        break;
                    }
                }
            }
            if (!found) {
                layer.removeAttribute("data-glass-scene");
                return;
            }
            var src = found.currentSrc || found.src || "";
            if (src.indexOf(window.location.origin + "/assets/") !== 0) {
                layer.removeAttribute("data-glass-scene");
                return;
            }
            var ir = found.getBoundingClientRect();
            var style = getComputedStyle(found);
            var fittedW = ir.width, fittedH = ir.height;
            var rw = ir.width / found.naturalWidth;
            var rh = ir.height / found.naturalHeight;
            var fit = style.objectFit;
            if (fit === "cover" || fit === "contain") {
                var factor = fit === "cover" ? Math.max(rw, rh) : Math.min(rw, rh);
                fittedW = found.naturalWidth * factor;
                fittedH = found.naturalHeight * factor;
            }
            var lx = ir.left + (ir.width - fittedW) / 2 - r.left;
            var ly = ir.top + (ir.height - fittedH) / 2 - r.top;
            // All inputs originate from a same-origin HTMLImageElement.
            layer.style.setProperty("--sunja-scene-image",
                'url("' + src.replace(/["\\]/g, "") + '")');
            layer.style.setProperty("--sunja-scene-size",
                fittedW.toFixed(1) + "px " + fittedH.toFixed(1) + "px");
            layer.style.setProperty("--sunja-scene-position",
                lx.toFixed(1) + "px " + ly.toFixed(1) + "px");
            layer.setAttribute("data-glass-scene", "photo");
        });
    }
    function scheduleLensScene() {
        if (lensDisabled || lensFrame) return;
        if (performance.now() - lastLensTime < 140) return;
        lensFrame = requestAnimationFrame(syncLensScene);
    }
    if (lenses.length && !lensDisabled) {
        window.addEventListener("scroll", scheduleLensScene, { passive: true });
        window.addEventListener("resize", scheduleLensScene, { passive: true });
        window.addEventListener("load", scheduleLensScene, { once: true });
        window.addEventListener("pageshow", scheduleLensScene);
        scheduleLensScene();
    }

})();
