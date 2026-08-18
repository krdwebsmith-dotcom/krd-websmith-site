/* KRD Websmith — site behaviour. No dependencies. Every hook is guarded. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ---- sticky header ---------------------------------------------------- */
  var header = document.getElementById("siteHeader");
  if (header) {
    var lastScrolled = null;
    var onScroll = function () {
      var next = window.scrollY > 24;
      if (next !== lastScrolled) {
        header.classList.toggle("scrolled", next);
        lastScrolled = next;
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---- mobile menu ------------------------------------------------------ */
  var toggle = document.getElementById("menuToggle");
  var menu = document.getElementById("mobileMenu");

  if (toggle && menu) {
    var setMenu = function (open) {
      menu.classList.toggle("open", open);
      toggle.classList.toggle("active", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      document.body.classList.toggle("menu-open", open);
    };

    toggle.addEventListener("click", function () {
      setMenu(!menu.classList.contains("open"));
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setMenu(false);
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && menu.classList.contains("open")) {
        setMenu(false);
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1000 && menu.classList.contains("open")) setMenu(false);
    });
  }

  /* ---- scroll reveals --------------------------------------------------- */
  var revealables = document.querySelectorAll(".reveal, .draw, .mask");

  if (!revealables.length) {
    /* nothing to do */
  } else if (reduced.matches || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) {
      el.classList.add("visible");
    });
  } else {
    var show = function (el) {
      el.classList.add("visible");
      observer.unobserve(el);
    };

    /* threshold 0 so elements taller than the viewport still qualify, and a
       top-side check so anything already scrolled past is shown rather than
       left at opacity 0 forever (anchor jumps, restored scroll, fast flicks). */
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting || entry.boundingClientRect.top < window.innerHeight) {
            show(entry.target);
          }
        });
      },
      { threshold: 0, rootMargin: "0px 0px -6% 0px" }
    );

    revealables.forEach(function (el) {
      observer.observe(el);
    });

    /* Safety net: reveal anything at or above the fold. Runs once on load and
       again when scrolling settles, so no element can stay hidden. */
    var sweep = function () {
      revealables.forEach(function (el) {
        if (el.classList.contains("visible")) return;
        if (el.getBoundingClientRect().top < window.innerHeight) show(el);
      });
    };
    var sweepTimer;
    var queueSweep = function () {
      clearTimeout(sweepTimer);
      sweepTimer = setTimeout(sweep, 120);
    };
    window.addEventListener("scroll", queueSweep, { passive: true });
    window.addEventListener("resize", queueSweep);
    window.addEventListener("load", sweep);
    sweep();
  }


  /* ---- footer year ----------------------------------------------------- */
  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
