/* Laplace Research — shared page behaviour: mobile menu and scroll reveal.
   Pages render fully without it; the "js" class only switches on extras. */
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");

  var rail = document.querySelector(".rail");
  var menu = rail && rail.querySelector(".menu");
  if (menu) {
    var close = function () {
      rail.classList.remove("open");
      menu.setAttribute("aria-expanded", "false");
    };
    menu.addEventListener("click", function () {
      var open = rail.classList.toggle("open");
      menu.setAttribute("aria-expanded", open ? "true" : "false");
    });
    // tapping a link closes the menu, including links to this same page
    rail.addEventListener("click", function (e) {
      if (e.target.closest("nav a, .cta")) close();
    });
    // a page restored from the back/forward cache comes back closed
    window.addEventListener("pageshow", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && rail.classList.contains("open")) {
        close();
        menu.focus();
      }
    });
  }

  var items = document.querySelectorAll(".reveal");
  if (!items.length) return;
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    items.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: "0px 0px -12% 0px", threshold: 0.05 });
  items.forEach(function (el) { io.observe(el); });
})();
