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

    // v40: keep the original slide appearance; only make its timing reliable.
    // Bootstrap performs the visual transition. This single timeout owns the
    // next-slide deadline so progress and automatic movement cannot drift.
    function setupHeroCarousel() {
        var hero = document.getElementById("header-carousel");
        if (!hero) return;

        var slides = Array.prototype.slice.call(hero.querySelectorAll(".carousel-item"));
        var indicators = Array.prototype.slice.call(hero.querySelectorAll(".hero-indicators button"));
        if (slides.length < 2) return;

        var interval = Number(hero.getAttribute("data-hero-interval")) || 6500;
        var instance = null;
        var cycleTimer = 0;
        var recoveryTimer = 0;
        var fallbackBound = false;
        var transitionPending = false;
        var eventsBound = false;

        function currentIndex() {
            return slides.findIndex(function (slide) {
                return slide.classList.contains("active");
            });
        }

        function canRotate() {
            return !document.hidden &&
                !document.documentElement.classList.contains("sunja-intro-active");
        }

        function clearCycle() {
            if (cycleTimer) window.clearTimeout(cycleTimer);
            cycleTimer = 0;
        }

        function setProgressDuration() {
            indicators.forEach(function (button) {
                var fill = button.querySelector("span");
                if (fill) fill.style.animationDuration = interval + "ms";
            });
        }

        function restartProgress() {
            indicators.forEach(function (button) {
                var fill = button.querySelector("span");
                if (!fill) return;
                fill.style.animation = "none";
                void fill.offsetWidth;
                // Set the exact duration inline. The legacy stylesheet has an
                // 8s animation; the actual slide interval is 6.5s.
                fill.style.animation = button.classList.contains("active")
                    ? "heroFill " + interval + "ms linear forwards"
                    : "none";
            });
        }

        function syncIndicators() {
            var active = currentIndex();
            indicators.forEach(function (button, index) {
                if (index === active) {
                    button.setAttribute("aria-current", "true");
                    button.classList.add("active");
                } else {
                    button.removeAttribute("aria-current");
                    button.classList.remove("active");
                }
            });
        }

        function scheduleNextSlide() {
            clearCycle();
            if (!canRotate()) return;
            cycleTimer = window.setTimeout(advanceNextSlide, interval);
        }

        function finishTransition() {
            transitionPending = false;
            if (recoveryTimer) window.clearTimeout(recoveryTimer);
            recoveryTimer = 0;
            syncIndicators();
            restartProgress();
            scheduleNextSlide();
        }

        function rotateTo(index) {
            var next = (index + slides.length) % slides.length;
            slides.forEach(function (slide, i) {
                slide.classList.toggle("active", i === next);
                slide.classList.remove("carousel-item-next", "carousel-item-prev",
                    "carousel-item-start", "carousel-item-end");
            });
            syncIndicators();
            finishTransition();
        }

        function rotateBy(delta) {
            var active = currentIndex();
            rotateTo((active < 0 ? 0 : active) + delta);
        }

        function handleSlideStart() {
            clearCycle();
            transitionPending = true;
            if (recoveryTimer) window.clearTimeout(recoveryTimer);
            // A normal Bootstrap transition completes in under a second. If its
            // "slid" event is lost, recover the scheduler without waiting forever.
            recoveryTimer = window.setTimeout(function () {
                if (transitionPending) finishTransition();
            }, 1400);
        }

        function handleSlideEnd() {
            finishTransition();
        }

        function bindBootstrapEvents() {
            if (eventsBound) return;
            eventsBound = true;
            hero.addEventListener("slide.bs.carousel", handleSlideStart);
            hero.addEventListener("slid.bs.carousel", handleSlideEnd);
        }

        function bindFallbackControls() {
            if (fallbackBound) return;
            fallbackBound = true;

            indicators.forEach(function (button, index) {
                button.addEventListener("click", function (event) {
                    event.preventDefault();
                    rotateTo(index);
                });
            });
            hero.querySelectorAll("[data-bs-slide]").forEach(function (button) {
                button.addEventListener("click", function (event) {
                    event.preventDefault();
                    rotateBy(button.getAttribute("data-bs-slide") === "prev" ? -1 : 1);
                });
            });

            var touchStart = null;
            hero.addEventListener("touchstart", function (event) {
                if (event.touches.length !== 1 ||
                    (event.target.closest && event.target.closest("a,button"))) {
                    touchStart = null;
                    return;
                }
                var point = event.touches[0];
                touchStart = { x: point.clientX, y: point.clientY };
            }, { passive: true });
            hero.addEventListener("touchend", function (event) {
                if (!touchStart || event.changedTouches.length !== 1) return;
                var point = event.changedTouches[0];
                var dx = point.clientX - touchStart.x;
                var dy = point.clientY - touchStart.y;
                touchStart = null;
                if (Math.abs(dx) < 44 || Math.abs(dy) > 60) return;
                rotateBy(dx < 0 ? 1 : -1);
            }, { passive: true });
        }

        function advanceNextSlide() {
            cycleTimer = 0;
            if (!canRotate()) return;

            var before = currentIndex();
            if (instance && typeof instance.next === "function") {
                try {
                    instance.next();
                    // Bootstrap silently ignores next() while an earlier slide
                    // is still marked as transitioning. If no event arrives,
                    // force one clean active-slide update and restart the clock.
                    window.setTimeout(function () {
                        if (!canRotate()) return;
                        if (currentIndex() === before && !transitionPending) {
                            rotateBy(1);
                        } else if (transitionPending) {
                            finishTransition();
                        } else if (!cycleTimer) {
                            scheduleNextSlide();
                        }
                    }, 1150);
                    return;
                } catch (error) {
                    instance = null;
                }
            }
            bindFallbackControls();
            rotateBy(1);
        }

        function startCycle() {
            if (!canRotate()) {
                clearCycle();
                if (recoveryTimer) window.clearTimeout(recoveryTimer);
                recoveryTimer = 0;
                return;
            }

            if (!instance && window.bootstrap && window.bootstrap.Carousel) {
                try {
                    bindBootstrapEvents();
                    var Carousel = window.bootstrap.Carousel;
                    // Bootstrap 5.0.0 exposes getInstance(), not the later
                    // getOrCreateInstance() helper. Support both safely.
                    instance = typeof Carousel.getInstance === "function"
                        ? Carousel.getInstance(hero)
                        : null;
                    if (!instance) {
                        instance = new Carousel(hero, {
                            interval: false,
                            ride: false,
                            pause: false,
                            wrap: true,
                            touch: true
                        });
                    }
                    if (typeof instance.pause === "function") instance.pause();
                } catch (error) {
                    instance = null;
                    bindFallbackControls();
                }
            } else if (!instance) {
                bindFallbackControls();
            }

            setProgressDuration();
            syncIndicators();
            restartProgress();
            scheduleNextSlide();
        }

        document.addEventListener("visibilitychange", function () {
            if (document.hidden) {
                clearCycle();
                if (recoveryTimer) window.clearTimeout(recoveryTimer);
                recoveryTimer = 0;
            } else {
                startCycle();
            }
        });
        window.addEventListener("pageshow", startCycle);
        window.addEventListener("sunja:intro-finished", startCycle);
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
        window.scrollTo({ top: 0, behavior: (reduceMotion || fastTouchNavigation) ? "auto" : "smooth" });
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



})();
