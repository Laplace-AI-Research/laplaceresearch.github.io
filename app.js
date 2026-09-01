/* Laplace Research — panel choreography + UTC clock */
(function () {
  "use strict";

  var root = document.documentElement;
  var site = document.getElementById("site");

  /* --- page-load reveal: wait on the background plate and the webfont --- */
  function reveal() {
    root.classList.add("is-ready");
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

  /* --- clock --- */
  var clock = document.getElementById("clock");
  var format = new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: "UTC",
  });

  function tick() {
    clock.textContent = format.format(new Date());
  }

  tick();
  window.setInterval(tick, 1000);
})();
