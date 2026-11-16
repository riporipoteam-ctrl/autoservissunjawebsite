(function () {
    'use strict';
    var body = document.body;
    var car = document.querySelector('.testing-car-art');
    var hero = document.getElementById('header-carousel');
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Scroll-triggered reveals: content remains visible if IntersectionObserver is unavailable.
    var revealTargets = document.querySelectorAll(
        '.carousel-caption h6, .carousel-caption h1, .carousel-caption p, .carousel-caption .status-pill, ' +
        '#o-nama .row, #usluge .text-center, #usluge .service-nav-grid, #usluge .tab-pane, ' +
        '#galerija .container, #recenzije .bg-white, #lokacija .text-center, #kontakt .text-center, #kontakt .contact-spotlight, .social-tile'
    );
    if (!reduceMotion && 'IntersectionObserver' in window) {
        var revealObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('is-testing-visible');
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
        revealTargets.forEach(function (el, index) {
            el.setAttribute('data-testing-reveal', '');
            el.style.transitionDelay = (Math.min(index % 4, 3) * 70) + 'ms';
            revealObserver.observe(el);
        });
    }

    // The real Peugeot image floats in a perspective stage; its pose scrubs with scroll.
    if (car && hero && !reduceMotion) {
        var mouseX = 0, mouseY = 0, scrollProgress = 0, frame = 0;
        function renderCar() {
            frame = 0;
            var rect = hero.getBoundingClientRect();
            var runway = Math.max(1, hero.offsetHeight * 0.9);
            scrollProgress = Math.max(0, Math.min(1, -rect.top / runway));
            var shiftX = mouseX * 18 + scrollProgress * 40;
            var shiftY = mouseY * -13 + scrollProgress * 75;
            var rotX = mouseY * -3.5;
            var rotY = 7 + mouseX * 8 - scrollProgress * 5;
            var rotZ = -3 + scrollProgress * 3;
            var scale = 1 - scrollProgress * .13;
            car.style.transform = 'translate3d(' + shiftX.toFixed(1) + 'px,' + shiftY.toFixed(1) + 'px,0) rotateX(' + rotX.toFixed(2) + 'deg) rotateY(' + rotY.toFixed(2) + 'deg) rotateZ(' + rotZ.toFixed(2) + 'deg) scale(' + scale.toFixed(3) + ')';
        }
        function queueCar() { if (!frame) frame = window.requestAnimationFrame(renderCar); }
        window.addEventListener('scroll', queueCar, { passive: true });
        window.addEventListener('resize', queueCar, { passive: true });
        window.addEventListener('pointermove', function (event) {
            if (event.pointerType === 'touch') return;
            mouseX = (event.clientX / Math.max(1, window.innerWidth) - .5) * 2;
            mouseY = (event.clientY / Math.max(1, window.innerHeight) - .5) * 2;
            queueCar();
        }, { passive: true });
        queueCar();
    }

    // Small tactile 3D response on cards, disabled on touch devices.
    var tiltCards = document.querySelectorAll('.social-tile, .service-nav-grid .nav-link, #recenzije .bg-white');
    if (!reduceMotion && window.matchMedia && window.matchMedia('(pointer: fine)').matches) {
        tiltCards.forEach(function (el) {
            el.setAttribute('data-testing-tilt', '');
            el.addEventListener('pointermove', function (event) {
                var r = el.getBoundingClientRect();
                var x = (event.clientX - r.left) / Math.max(1, r.width) - .5;
                var y = (event.clientY - r.top) / Math.max(1, r.height) - .5;
                el.style.transform = 'perspective(800px) rotateX(' + (-y * 3).toFixed(2) + 'deg) rotateY(' + (x * 4).toFixed(2) + 'deg) translateY(-2px)';
            });
            el.addEventListener('pointerleave', function () { el.style.transform = ''; });
        });
    }

    // Make page theme explicit for browser automation and avoid touching root-page behavior.
    body.dataset.design = 'testing';
})();
