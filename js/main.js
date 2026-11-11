(function ($) {
    "use strict";

    var reduceMotion = false;
    try {
        reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) {}

    var saveData = !!(navigator.connection && navigator.connection.saveData);
    var lowMemory = typeof navigator.deviceMemory === "number" && navigator.deviceMemory <= 2;
    var lowCpu = typeof navigator.hardwareConcurrency === "number" && navigator.hardwareConcurrency <= 2;
    var perfLite = saveData || lowMemory || lowCpu;

    if (perfLite) {
        document.documentElement.classList.add("perf-lite");
    }

    // Template spinner is separate from the branded exact-logo preloader.
    setTimeout(function () {
        if ($("#spinner").length) {
            $("#spinner").removeClass("show");
        }
    }, 1);

    // Scroll reveal animations are kept on capable devices and disabled for
    // users/devices that explicitly benefit from less motion/work.
    if (!reduceMotion && typeof WOW !== "undefined") {
        new WOW({ mobile: !perfLite }).init();
    }

    var $win = $(window);
    var $sticky = $(".sticky-top");
    var $backTop = $(".back-to-top");
    var chromeVisible = null;
    var scrollRaf = 0;

    function syncScrollChrome() {
        scrollRaf = 0;
        var show = $win.scrollTop() > 300;
        if (show === chromeVisible) return;
        chromeVisible = show;

        $sticky.css("top", show ? "0px" : "-100px");
        $backTop.toggleClass("is-visible", show);
    }

    // One passive scroll listener + rAF replaces two independent handlers.
    window.addEventListener("scroll", function () {
        if (!scrollRaf) {
            scrollRaf = requestAnimationFrame(syncScrollChrome);
        }
    }, { passive: true });
    syncScrollChrome();

    // Desktop dropdown hover. Namespace + clear old handlers so resize does
    // not stack duplicate listeners.
    var $dropdown = $(".dropdown");
    var $dropdownToggle = $(".dropdown-toggle");
    var $dropdownMenu = $(".dropdown-menu");
    var showClass = "show";

    function bindDropdownHover() {
        $dropdown.off(".sunjaHover");

        if (window.matchMedia && window.matchMedia("(min-width: 992px)").matches) {
            $dropdown
                .on("mouseenter.sunjaHover", function () {
                    var $this = $(this);
                    $this.addClass(showClass);
                    $this.find($dropdownToggle).attr("aria-expanded", "true");
                    $this.find($dropdownMenu).addClass(showClass);
                })
                .on("mouseleave.sunjaHover", function () {
                    var $this = $(this);
                    $this.removeClass(showClass);
                    $this.find($dropdownToggle).attr("aria-expanded", "false");
                    $this.find($dropdownMenu).removeClass(showClass);
                });
        }
    }

    var resizeRaf = 0;
    window.addEventListener("resize", function () {
        if (resizeRaf) cancelAnimationFrame(resizeRaf);
        resizeRaf = requestAnimationFrame(function () {
            resizeRaf = 0;
            bindDropdownHover();
            syncScrollChrome();
        });
    }, { passive: true });
    bindDropdownHover();

    var topScrollFrame = 0;

    function scrollToTopSmoothly() {
        if (topScrollFrame) {
            cancelAnimationFrame(topScrollFrame);
            topScrollFrame = 0;
        }

        var scroller = document.scrollingElement || document.documentElement;
        var startY = Math.max(
            window.pageYOffset || 0,
            scroller.scrollTop || 0,
            document.body.scrollTop || 0
        );

        if (startY <= 1) {
            window.scrollTo(0, 0);
            return;
        }

        // One tap = one controlled trip. Longer pages get a little more time
        // instead of trying to cover thousands of pixels in a few frames.
        var duration = Math.min(1800, Math.max(700, startY / 5));
        var startedAt = performance.now();

        function step(now) {
            var progress = Math.min(1, (now - startedAt) / duration);
            var eased = 1 - Math.pow(1 - progress, 4);
            var y = Math.round(startY * (1 - eased));

            window.scrollTo(0, y);

            if (progress < 1) {
                topScrollFrame = requestAnimationFrame(step);
            } else {
                topScrollFrame = 0;
                window.scrollTo(0, 0);
                scroller.scrollTop = 0;
                document.body.scrollTop = 0;
                syncScrollChrome();
            }
        }

        topScrollFrame = requestAnimationFrame(step);
    }

    $backTop.on("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        scrollToTopSmoothly();
    });

    // Keep the navbar state synced with the section the visitor is viewing.
    // This is observer-based, so it costs essentially nothing while idle.
    (function setupScrollSpy() {
        if (!("IntersectionObserver" in window)) return;

        var links = Array.prototype.slice.call(document.querySelectorAll(".navbar-nav .nav-link[href^='#']"));
        var byId = {};
        links.forEach(function (link) {
            var id = link.getAttribute("href").slice(1);
            if (id) byId[id] = link;
        });

        var sections = Object.keys(byId).map(function (id) {
            return document.getElementById(id);
        }).filter(Boolean);

        if (!sections.length) return;

        var observer = new IntersectionObserver(function (entries) {
            var visible = entries
                .filter(function (entry) { return entry.isIntersecting; })
                .sort(function (a, b) { return b.intersectionRatio - a.intersectionRatio; })[0];

            if (!visible || !byId[visible.target.id]) return;
            links.forEach(function (link) { link.classList.remove("active"); });
            byId[visible.target.id].classList.add("active");
        }, {
            rootMargin: "-28% 0px -60% 0px",
            threshold: [0.02, 0.12, 0.3]
        });

        sections.forEach(function (section) { observer.observe(section); });
    })();

    // On phones/tablets, collapse the menu after choosing a section.
    document.querySelectorAll("#navbarCollapse .nav-link").forEach(function (link) {
        link.addEventListener("click", function () {
            var collapseEl = document.getElementById("navbarCollapse");
            if (!collapseEl || !collapseEl.classList.contains("show") || typeof bootstrap === "undefined") return;
            bootstrap.Collapse.getOrCreateInstance(collapseEl, { toggle: false }).hide();
        });
    });

})(jQuery);
