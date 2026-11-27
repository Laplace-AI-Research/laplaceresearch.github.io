/* Safety & Responsibility: highlight the current section in the contents list,
   and fold the list away on narrow screens. The page works without it. */
(function () {
  "use strict";
  var toc = document.querySelector(".sf-toc");
  if (!toc) return;
  var links = Array.prototype.slice.call(toc.querySelectorAll("a[href^='#']"));

  var narrow = matchMedia("(max-width: 1180px)");
  var fold = function () { toc.open = !narrow.matches; };
  fold();
  if (narrow.addEventListener) narrow.addEventListener("change", fold);
  toc.addEventListener("click", function (e) {
    if (narrow.matches && e.target.closest("a")) toc.open = false;
  });

  if (!("IntersectionObserver" in window)) return;
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
  var visible = {};
  var mark = function () {
    var current = null;
    links.some(function (a) {
      var id = a.getAttribute("href").slice(1);
      if (visible[id]) { current = a; return true; }
      return false;
    });
    if (!current) return;
    links.forEach(function (a) {
      if (a === current) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  };
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) { visible[entry.target.id] = entry.isIntersecting; });
    mark();
  }, { rootMargin: "-10% 0px -60% 0px" });
  Object.keys(byId).forEach(function (id) {
    var el = document.getElementById(id);
    if (el) io.observe(el);
  });
})();
