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
        $backTop.stop(true, true);
        if (reduceMotion) {
            $backTop.toggle(show);
        } else if (show) {
            $backTop.fadeIn(180);
        } else {
            $backTop.fadeOut(180);
        }
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

    function jumpToTopInstantly() {
        var root = document.documentElement;
        var body = document.body;
        var rootBehavior = root.style.scrollBehavior;
        var bodyBehavior = body.style.scrollBehavior;

        // The site uses smooth scrolling for normal anchor links. Override it
        // only for this control so one press always returns to the top now.
        root.style.scrollBehavior = "auto";
        body.style.scrollBehavior = "auto";
        $("html, body").stop(true, true);

        window.scrollTo(0, 0);
        root.scrollTop = 0;
        body.scrollTop = 0;

        requestAnimationFrame(function () {
            root.style.scrollBehavior = rootBehavior;
            body.style.scrollBehavior = bodyBehavior;
            syncScrollChrome();
        });
    }

    $backTop.on("click", function (event) {
        event.preventDefault();
        jumpToTopInstantly();
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
