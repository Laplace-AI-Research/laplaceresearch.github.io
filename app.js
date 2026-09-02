/* Laplace Research — panel choreography, headline reel, New York clock */
(function () {
  "use strict";

  var root = document.documentElement;
  var site = document.getElementById("site");
  var reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  /* --- headline: each letter spins like a lock dial, settling left to right --
     Widths are measured from the real glyphs and pinned before the first spin,
     so the line never shifts while the random characters cycle through. */

  var SPIN_TOTAL = 1180; // last letter lands here
  var SPIN_FIRST = 190; // first letter lands here
  var SPIN_TICK = 45; // ms between glyph swaps

  var UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  var LOWER = "abcdefghijklmnopqrstuvwxyz";
  var DIGITS = "0123456789";

  function poolFor(ch) {
    if (ch >= "A" && ch <= "Z") return UPPER;
    if (ch >= "a" && ch <= "z") return LOWER + DIGITS;
    return DIGITS;
  }

  function spinHeadline() {
    var headline = document.querySelector(".statement");
    if (!headline || reduceMotion || !("requestAnimationFrame" in window)) {
      return;
    }

    var cells = [];
    var source = Array.prototype.slice.call(headline.childNodes);
    headline.textContent = "";

    source.forEach(function (node) {
      if (node.nodeName === "BR") {
        headline.appendChild(document.createElement("br"));
        return;
      }
      // collapse the source indentation exactly as HTML would render it
      var text = (node.textContent || "").replace(/\s+/g, " ").trim();
      text.split("").forEach(function (ch) {
        if (ch === " ") {
          headline.appendChild(document.createTextNode(" "));
          return;
        }
        var cell = document.createElement("span");
        cell.className = "glyph is-spinning";
        cell.textContent = ch;
        headline.appendChild(cell);
        cells.push({ el: cell, ch: ch });
      });
    });

    if (!cells.length) return;

    // Measure every candidate glyph once, in the headline's own type, so each
    // slot can spin only through characters that actually fit it. Without this
    // a wide random letter overhangs its slot and collides with its neighbour.
    var gauge = document.createElement("span");
    gauge.setAttribute("aria-hidden", "true");
    gauge.style.cssText =
      "position:absolute;visibility:hidden;white-space:pre;pointer-events:none";
    headline.appendChild(gauge);

    var alphabet = UPPER + LOWER + DIGITS;
    var glyphWidth = {};
    alphabet.split("").forEach(function (ch) {
      var probe = document.createElement("span");
      probe.className = "glyph";
      probe.textContent = ch;
      gauge.appendChild(probe);
    });
    Array.prototype.forEach.call(gauge.children, function (probe, i) {
      glyphWidth[alphabet.charAt(i)] = probe.getBoundingClientRect().width;
    });

    // one read pass, then one write pass — avoids layout thrash
    cells.forEach(function (cell) {
      cell.width = cell.el.getBoundingClientRect().width;
    });
    headline.removeChild(gauge);

    cells.forEach(function (cell, i) {
      cell.el.style.width = cell.width.toFixed(2) + "px";
      cell.settleAt =
        SPIN_FIRST + (i / (cells.length - 1 || 1)) * (SPIN_TOTAL - SPIN_FIRST);

      var fits = poolFor(cell.ch)
        .split("")
        .filter(function (ch) {
          return glyphWidth[ch] <= cell.width + 0.5;
        });
      // very narrow slots (i, l) keep the three narrowest rather than none
      cell.pool = fits.length
        ? fits
        : poolFor(cell.ch)
            .split("")
            .sort(function (a, b) {
              return glyphWidth[a] - glyphWidth[b];
            })
            .slice(0, 3);
    });

    var start = performance.now();

    function step(now) {
      var elapsed = now - start;
      var spinning = false;

      for (var i = 0; i < cells.length; i++) {
        var cell = cells[i];
        if (cell.settled) continue;

        if (elapsed >= cell.settleAt) {
          cell.settled = true;
          cell.el.textContent = cell.ch;
          cell.el.className = "glyph is-set";
          continue;
        }

        spinning = true;
        if (!cell.nextSwap || now >= cell.nextSwap) {
          cell.el.textContent =
            cell.pool[Math.floor(Math.random() * cell.pool.length)];
          cell.nextSwap = now + SPIN_TICK;
        }
      }

      if (spinning) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }

  /* --- page-load reveal: wait on the background plate and the webfont --- */
  var revealed = false;

  function reveal() {
    if (revealed) return;
    revealed = true;
    root.classList.add("is-ready");
    spinHeadline();
  }

  var plate = new Image();
  var waits = [
    new Promise(function (done) {
      plate.onload = plate.onerror = done;
      plate.src = "assets/ridgeline.jpg";
    }),
  ];
  if (document.fonts && document.fonts.ready) waits.push(document.fonts.ready);

  Promise.all(waits).then(reveal);
  window.setTimeout(reveal, 2200); // never leave the page blank
  var triggers = Array.prototype.slice.call(
    document.querySelectorAll("[data-open]")
  );
  var panels = Array.prototype.slice.call(document.querySelectorAll(".panel"));
  var closers = Array.prototype.slice.call(
    document.querySelectorAll("[data-close]")
  );
  var current = null;

  function open(name) {
    if (current === name) return;
    current = name;
    site.classList.add("is-open");

    panels.forEach(function (panel) {
      var active = panel.dataset.panel === name;
      if (active) panel.hidden = false;
      // let the browser register `hidden = false` before transitioning
      requestAnimationFrame(function () {
        panel.classList.toggle("is-active", active);
      });
      if (!active) hideAfterFade(panel);
    });

    triggers.forEach(function (button) {
      button.setAttribute(
        "aria-expanded",
        String(button.dataset.open === name)
      );
    });
  }

  function close() {
    if (!current) return;
    current = null;
    site.classList.remove("is-open");
    panels.forEach(function (panel) {
      panel.classList.remove("is-active");
      hideAfterFade(panel);
    });
    triggers.forEach(function (button) {
      button.setAttribute("aria-expanded", "false");
    });
  }

  function hideAfterFade(panel) {
    window.setTimeout(function () {
      if (!panel.classList.contains("is-active")) {
        panel.hidden = true;
        panel.scrollTop = 0;
      }
    }, 520);
  }

  triggers.forEach(function (button) {
    button.addEventListener("click", function () {
      if (current === button.dataset.open) close();
      else open(button.dataset.open);
    });
  });

  closers.forEach(function (button) {
    button.addEventListener("click", close);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") close();
  });

  /* --- clock: New York, with the zone label following daylight saving --- */
  var clock = document.getElementById("clock");
  var zone = document.getElementById("zone");
  var ZONE = "America/New_York";

  var format = new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: ZONE,
  });

  var labelFormat = new Intl.DateTimeFormat("en-US", {
    timeZone: ZONE,
    timeZoneName: "short",
  });

  function label(date) {
    var part = labelFormat
      .formatToParts(date)
      .find(function (p) {
        return p.type === "timeZoneName";
      });
    return part ? part.value : "ET";
  }

  function tick() {
    var now = new Date();
    clock.textContent = format.format(now);
    zone.textContent = label(now);
  }

  tick();
  window.setInterval(tick, 1000);
})();
