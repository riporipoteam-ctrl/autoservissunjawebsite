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
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    }
    if (backTop) {
        backTop.addEventListener("click", function (event) {
            event.preventDefault();
            scrollToTopSmoothly();
        });
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
        try { history.replaceState(null, '', '#' + encodeURIComponent(id)); } catch (e) {}
        target.scrollIntoView({
            behavior: reduceMotion ? "auto" : "smooth",
            block: "start"
        });
    });

    // Collapse mobile navigation on its first selection.
    document.querySelectorAll("#navbarCollapse .nav-link").forEach(function (link) {
        link.addEventListener("click", function () {
            var el = document.getElementById("navbarCollapse");
            if (!el || !el.classList.contains("show") || typeof bootstrap === "undefined") return;
            bootstrap.Collapse.getOrCreateInstance(el, { toggle: false }).hide();
        });
    });
})();
