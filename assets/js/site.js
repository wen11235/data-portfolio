(function () {
  "use strict";

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- Scroll progress bar ----
  var bar = document.createElement("div");
  bar.className = "scroll-progress";
  document.body.prepend(bar);

  function updateProgress() {
    var scrollTop = window.scrollY;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = pct + "%";
  }
  window.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("resize", updateProgress);
  updateProgress();

  // ---- Theme toggle ----
  // The inline head script (see any page's <head>) already applied a saved
  // preference before first paint, to avoid a flash of the wrong theme. This
  // just builds the button and wires up the click behavior.
  var toggle = document.createElement("button");
  toggle.className = "theme-toggle";
  toggle.type = "button";
  toggle.setAttribute("aria-label", "Toggle light / dark theme");
  toggle.innerHTML =
    '<svg class="icon-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v3M12 18.5v3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M2.5 12h3M18.5 12h3M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/></svg>' +
    '<svg class="icon-moon" viewBox="0 0 24 24"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.8 6.8 0 0 0 10.5 10.5Z"/></svg>';
  document.body.prepend(toggle);

  toggle.addEventListener("click", function () {
    var current = document.documentElement.getAttribute("data-theme");
    var systemLight = window.matchMedia("(prefers-color-scheme: light)").matches;
    var currentlyLight = current ? current === "light" : systemLight;
    var next = currentlyLight ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
  });

  if (reducedMotion) return;

  // ---- Scroll reveal ----
  var targets = document.querySelectorAll(".card, .stat, .callout");
  targets.forEach(function (el, i) {
    el.classList.add("reveal");
    el.style.transitionDelay = Math.min(i % 6, 5) * 90 + "ms";
  });

  if (!("IntersectionObserver" in window)) {
    targets.forEach(function (el) { el.classList.add("is-visible"); });
    return;
  }

  // Double rAF: guarantees the browser has painted the hidden (opacity:0)
  // state at least one frame before observation starts, so anything already
  // in the initial viewport still visibly animates in instead of flashing.
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.15, rootMargin: "0px 0px -80px 0px" }
      );
      targets.forEach(function (el) { observer.observe(el); });
    });
  });
})();
