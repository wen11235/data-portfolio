(function () {
  "use strict";

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canHover = window.matchMedia("(hover: hover)").matches;

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

  // ---- Image lightbox (report screenshots) ----
  // Functional, not decorative — runs regardless of reduced-motion.
  var reportImgs = document.querySelectorAll(".report figure img");
  if (reportImgs.length) {
    var overlay = document.createElement("div");
    overlay.className = "lightbox-overlay";
    var overlayImg = document.createElement("img");
    overlay.appendChild(overlayImg);
    document.body.appendChild(overlay);

    function closeLightbox() {
      overlay.classList.remove("is-open");
    }
    reportImgs.forEach(function (img) {
      img.addEventListener("click", function () {
        overlayImg.src = img.currentSrc || img.src;
        overlayImg.alt = img.alt || "";
        overlay.classList.add("is-open");
      });
    });
    overlay.addEventListener("click", closeLightbox);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeLightbox();
    });
  }

  // ---- Copy-code buttons ----
  document.querySelectorAll("pre").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "Copy";
    btn.addEventListener("click", function () {
      var code = pre.querySelector("code");
      var text = code ? code.textContent : pre.textContent;
      navigator.clipboard.writeText(text).then(
        function () {
          btn.textContent = "Copied!";
          btn.classList.add("copied");
          setTimeout(function () {
            btn.textContent = "Copy";
            btn.classList.remove("copied");
          }, 1500);
        },
        function () {}
      );
    });
    pre.appendChild(btn);
  });

  // ---- Card 3D tilt (hover-capable pointers only) ----
  if (canHover && !reducedMotion) {
    document.querySelectorAll(".card").forEach(function (card) {
      var rect = null;
      card.addEventListener("mouseenter", function () {
        rect = card.getBoundingClientRect();
      });
      card.addEventListener("mousemove", function (e) {
        if (!rect) rect = card.getBoundingClientRect();
        var relX = (e.clientX - rect.left) / rect.width;
        var relY = (e.clientY - rect.top) / rect.height;
        var rotateY = (relX - 0.5) * 9;
        var rotateX = (0.5 - relY) * 9;
        card.style.transform =
          "perspective(900px) rotateX(" + rotateX.toFixed(2) + "deg) rotateY(" + rotateY.toFixed(2) + "deg) translateY(-5px)";
      });
      card.addEventListener("mouseleave", function () {
        card.style.transform = "";
        rect = null;
      });
    });
  }

  if (reducedMotion) return;

  // ---- Animated stat counters ----
  // Parses a leading numeric token out of arbitrary stat text (handles
  // commas, decimals, a currency/percent/unit prefix or suffix, and either
  // hyphen or a Unicode minus sign) and counts it up from 0. Anything that
  // doesn't start with a recognizable number (e.g. "10¹–10⁶") is left as-is.
  function animateStatValue(el) {
    var raw = el.textContent.trim();
    var match = raw.match(/^([£$]?)([-−]?)([\d,]+(?:\.\d+)?)(.*)$/);
    if (!match) return;
    var prefix = match[1];
    var sign = match[2] ? "-" : "";
    var numStr = match[3];
    var suffix = match[4];
    var target = parseFloat(numStr.replace(/,/g, ""));
    if (isNaN(target)) return;
    var decimals = numStr.indexOf(".") > -1 ? numStr.split(".")[1].length : 0;
    var hasCommas = numStr.indexOf(",") > -1;
    var duration = 1100;
    var start = null;

    function format(n) {
      var s = n.toFixed(decimals);
      if (hasCommas) {
        var parts = s.split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        s = parts.join(".");
      }
      return s;
    }

    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = prefix + sign + format(target * eased) + suffix;
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = raw;
      }
    }
    requestAnimationFrame(step);
  }

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
              if (entry.target.classList.contains("stat")) {
                var valueEl = entry.target.querySelector(".value");
                if (valueEl) animateStatValue(valueEl);
              }
            }
          });
        },
        { threshold: 0.15, rootMargin: "0px 0px -80px 0px" }
      );
      targets.forEach(function (el) { observer.observe(el); });
    });
  });
})();
