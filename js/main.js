(function () {
    "use strict";

    var reduceMotion = false;
    try {
        reduceMotion = !!(window.matchMedia &&
            window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) {}

    var connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    var saveData = !!(connection && connection.saveData);
    var effectiveType = connection && typeof connection.effectiveType === "string"
        ? connection.effectiveType.toLowerCase() : "";
    var slowConnection = /^(slow-2g|2g|3g)$/.test(effectiveType);
    var deviceMemory = typeof navigator.deviceMemory === "number"
        ? navigator.deviceMemory : null;
    var hardwareConcurrency = typeof navigator.hardwareConcurrency === "number"
        ? navigator.hardwareConcurrency : null;
    var lowMemory = deviceMemory !== null && deviceMemory <= 2;
    var lowCpu = hardwareConcurrency !== null && hardwareConcurrency <= 2;
    var perfLite = saveData || lowMemory || lowCpu;
    // Device age/model is not reliably exposed (and guessing it is brittle).
    // Upgrade motion only when both reported capability hints are strong.
    var motionRich = !reduceMotion && !perfLite && deviceMemory !== null &&
        hardwareConcurrency !== null && deviceMemory >= 8 && hardwareConcurrency >= 6;
    var root = document.documentElement;
    var pointerCoarse = !!(window.matchMedia && window.matchMedia("(pointer: coarse)").matches);
    var hoverCapable = !!(window.matchMedia && window.matchMedia("(hover: hover)").matches);
    var width = window.innerWidth || document.documentElement.clientWidth || 0;
    var viewport = width < 480 ? "compact" : width < 768 ? "mobile" : width < 1200 ? "tablet" : "desktop";
    var connectionClass = slowConnection ? "slow" : (effectiveType || "unknown");
    root.dataset.sunjaDeviceProfile = [viewport, pointerCoarse ? "touch" : "pointer",
        hoverCapable ? "hover" : "no-hover", perfLite ? "lite" : "full",
        reduceMotion ? "reduced" : "motion", connectionClass].join("-");
    root.classList.toggle("perf-lite", perfLite);
    root.classList.toggle("motion-rich", motionRich);
    root.classList.toggle("motion-standard", !motionRich && !perfLite && !reduceMotion);
    root.classList.toggle("motion-reduced", reduceMotion);

    // Stable media loading: every important image has a committed local
    // fallback. Hidden Bootstrap service tabs are made eager immediately
    // before activation so Safari does not keep a lazy image blank in a
    // previously display:none panel.
    function wireReliableImage(img) {
        if (!img || img.dataset.reliableImageWired === "1") return;
        img.dataset.reliableImageWired = "1";
        var frame = img.closest(".service-media-frame");
        function markReady() {
            img.classList.add("image-ready");
            img.classList.remove("image-failed");
            if (frame) {
                frame.classList.add("image-ready");
                frame.classList.remove("image-failed");
            }
        }
        function recoverImage() {
            var fallback = img.getAttribute("data-fallback-src");
            // The inline handler in <head> may already have switched src
            // before this bundle attached its own error listener.
            if (img.dataset.fallbackApplied === "1" && fallback === img.getAttribute("src")) {
                window.setTimeout(function () {
                    if (img.complete && img.naturalWidth === 0) {
                        img.classList.add("image-failed");
                        if (frame) frame.classList.add("image-failed");
                    }
                }, 0);
                return;
            }
            if (fallback && img.dataset.fallbackApplied !== "1" &&
                fallback !== img.getAttribute("src")) {
                img.dataset.fallbackApplied = "1";
                img.loading = "eager";
                var picture = img.closest("picture");
                var source = picture && picture.querySelector("source");
                if (source) source.srcset = fallback;
                var slide = img.closest(".carousel-item");
                var backdrop = slide && slide.querySelector(".hero-bg");
                if (backdrop) {
                    var localUrl = "url('/" + fallback + "')";
                    backdrop.style.setProperty("--hero-photo", localUrl);
                    backdrop.style.setProperty("--hero-photo-mobile", localUrl);
                }
                img.src = fallback;
                return;
            }
            img.classList.add("image-failed");
            if (frame) frame.classList.add("image-failed");
        }
        img.addEventListener("load", markReady);
        img.addEventListener("error", recoverImage);
        // The first hero image may finish (or fail) before this script runs.
        if (img.complete) {
            if (img.naturalWidth > 0) markReady();
            else recoverImage();
        }
    }

    var stableImages = Array.prototype.slice.call(document.querySelectorAll(
        "#header-carousel picture img[data-fallback-src], #usluge img.service-image"
    ));
    stableImages.forEach(wireReliableImage);

    var heroPrimary = document.getElementById("heroMainImg");
    if (heroPrimary) {
        heroPrimary.loading = "eager";
        heroPrimary.fetchPriority = "high";
    }
    // Prepare only the selected service. The remaining five stay lazy to
    // avoid downloading every large portrait image on older/limited devices.
    function prepareServiceImage(button) {
        var selector = button && button.getAttribute("data-bs-target");
        var panel = selector && document.querySelector(selector);
        var image = panel && panel.querySelector("img.service-image");
        if (!image) return;
        wireReliableImage(image);
        image.loading = "eager";
        image.fetchPriority = "high";
        if (image.complete && image.naturalWidth > 0) {
            if (typeof image.decode === "function") image.decode().catch(function () {});
            image.classList.add("image-ready");
        }
    }
    var serviceButtons = document.querySelectorAll(
        "#usluge .service-nav-grid [data-bs-toggle='pill']"
    );
    serviceButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            prepareServiceImage(button);
        }, true);
    });
    var activeServiceButton = document.querySelector(
        "#usluge .service-nav-grid .nav-link.active"
    );
    if (activeServiceButton) prepareServiceImage(activeServiceButton);

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
    if (!saveData && !slowConnection && !perfLite) {
        window.addEventListener("load", function () {
            var slides = document.querySelectorAll(".carousel-item:not(.active) picture img");
            slides.forEach(function (slideImg) {
                slideImg.decoding = "async";
                slideImg.loading = "eager";
            });
        }, { once: true });
    }

    // v37: deterministic hero auto-rotation. Bootstrap may fail to arrive
    // on restrictive mobile networks; keep a tiny no-dependency fallback.
    // Do not spend carousel cycles underneath the full-screen brand intro.
    function setupHeroCarousel() {
        var hero = document.getElementById("header-carousel");
        if (!hero) return;
        var slides = Array.prototype.slice.call(hero.querySelectorAll(".carousel-item"));
        var indicators = Array.prototype.slice.call(hero.querySelectorAll(".hero-indicators button"));
        if (slides.length < 2) return;
        var instance = null, fallbackTimer = 0, wiredFallback = false;

        function rotateBy(delta) {
            var active = slides.findIndex(function (slide) { return slide.classList.contains("active"); });
            var next = (active + delta + slides.length) % slides.length;
            slides.forEach(function (slide, i) {
                slide.classList.toggle("active", i === next);
            });
            indicators.forEach(function (button, i) {
                button.classList.toggle("active", i === next);
                if (i === next) button.setAttribute("aria-current", "true");
                else button.removeAttribute("aria-current");
            });
        }
        function stop() {
            if (fallbackTimer) window.clearInterval(fallbackTimer);
            fallbackTimer = 0;
            if (instance && typeof instance.pause === "function") instance.pause();
        }
        function startCycle() {
            if (document.hidden || document.documentElement.classList.contains("sunja-intro-active")) return;
            stop();
            // Workshop in Motion owns its playback state, including the no-Bootstrap timer.
            var currentMode = root.dataset.workshopMotion;
            var shouldPlay = currentMode ? currentMode !== "off" :
                !document.getElementById("workshopStory") || !(reduceMotion || perfLite);
            if (window.bootstrap && window.bootstrap.Carousel) {
                try {
                    var Carousel = window.bootstrap.Carousel;
                    instance = Carousel.getInstance(hero) || new Carousel(hero, {
                        interval: 6500, ride: false, pause: false, wrap: true, touch: true
                    });
                    if (shouldPlay) instance.cycle();
                    return;
                } catch (error) {
                    instance = null;
                }
            }
            if (!wiredFallback) {
                wiredFallback = true;
                indicators.forEach(function (button, i) {
                    button.addEventListener("click", function () {
                        var current = slides.findIndex(function (slide) { return slide.classList.contains("active"); });
                        rotateBy(i - current);
                        startCycle();
                    });
                });
                hero.querySelectorAll("[data-bs-slide]").forEach(function (button) {
                    button.addEventListener("click", function () {
                        rotateBy(button.getAttribute("data-bs-slide") === "prev" ? -1 : 1);
                        startCycle();
                    });
                });
            }
            if (shouldPlay) fallbackTimer = window.setInterval(function () { rotateBy(1); }, 6500);
        }
        document.addEventListener("visibilitychange", function () {
            if (document.hidden) stop();
            else startCycle();
        });
        window.addEventListener("pageshow", startCycle);
        window.addEventListener("sunja:intro-finished", startCycle);
        window.addEventListener("sunja:workshop-motion-change", startCycle);
        startCycle();
    }
    setupHeroCarousel();

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
        window.scrollTo({ top: 0, behavior: (reduceMotion || fastTouchNavigation || document.documentElement.dataset.workshopMotion === "off") ? "auto" : "smooth" });
    }
    if (backTop) {
        backTop.addEventListener("click", function (event) {
            event.preventDefault();
            scrollToTopSmoothly();
        });
    }

    // Mobile Pozovite/Upute bar is CSS-fixed. Never toggle visibility on scroll:
    // the former geometry collision detector caused Safari flicker.

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
        if (!el) return;
        var toggle = document.querySelector(".navbar-toggler");
        // Bootstrap ignores hide() while an opening transition is in progress.
        // Complete that transition now so this same tap can close the menu.
        if (el.classList.contains("collapsing") && toggle && toggle.getAttribute("aria-expanded") === "true") {
            el.dispatchEvent(new Event("transitionend"));
        }
        if (!el.classList.contains("show")) return;
        try {
            if (typeof bootstrap !== "undefined" && bootstrap.Collapse) {
                (bootstrap.Collapse.getInstance(el) || new bootstrap.Collapse(el, { toggle: false })).hide();
            }
        } catch (e) {
            // A failed Bootstrap transition must never cancel the tap.
        }
        if (el.classList.contains("show")) {
            el.classList.remove("show", "collapsing");
            el.classList.add("collapse");
            el.style.height = "";
        }
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
        // target.scrollIntoView( is intentionally avoided in embedded previews;
        // calculate the sticky-header offset and use window.scrollTo instead.
        var header = document.querySelector(".nav-bar");
        var offset = header ? header.getBoundingClientRect().height : 0;
        var destination = Math.max(0, target.getBoundingClientRect().top + window.pageYOffset - offset - 10);
        window.scrollTo({
            top: destination,
            behavior: (reduceMotion || fastTouchNavigation || document.documentElement.dataset.workshopMotion === "off") ? "auto" : "smooth"
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



})();
