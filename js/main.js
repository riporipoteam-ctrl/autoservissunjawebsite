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
        ".map-quick-link"
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
        if (typeof bootstrap !== "undefined" && bootstrap.Collapse) {
            bootstrap.Collapse.getOrCreateInstance(el, { toggle: false }).hide();
        } else {
            el.classList.remove("show");
            var toggle = document.querySelector(".navbar-toggler");
            if (toggle) toggle.setAttribute("aria-expanded", "false");
        }
    }

    // Same-page buttons need exactly one click, regardless of iOS hover
    // emulation. Native href fallback remains if this script is unavailable.
    document.addEventListener('click', function (event) {
        var element = event.target;
        var link = element && element.closest ? element.closest('a[href^="#"]') : null;
        if (!link || event.defaultPrevented || event.button > 0 ||
            event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

        var id = link.getAttribute("href").slice(1);
        if (!id) return;
        var target = document.getElementById(id);
        if (!target) return;

        event.preventDefault();
        if (link.closest("#navbarCollapse")) collapseMobileMenu();
        try { history.replaceState(null, '', '#' + encodeURIComponent(id)); } catch (e) {}
        target.scrollIntoView({
            behavior: (reduceMotion || fastTouchNavigation) ? "auto" : "smooth",
            block: "start"
        });
    }, true);

})();
