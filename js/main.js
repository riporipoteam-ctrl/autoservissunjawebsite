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

    $backTop.on("click", function (event) {
        event.preventDefault();
        if (reduceMotion) {
            window.scrollTo(0, 0);
        } else {
            $("html, body").stop(true).animate({ scrollTop: 0 }, 700, "easeInOutExpo");
        }
    });

})(jQuery);
