/* Laplace Research — hover and focus tooltips for the HTML figures.
   Any element with data-tip-title shows a tooltip; data-tip adds a detail line.
   The same text lives in each mark's aria-label and in the table beside it. */
(function () {
  "use strict";

  var marks = document.querySelectorAll("[data-tip-title]");
  if (!marks.length) return;

  var tip = document.createElement("div");
  tip.className = "chart-tip";
  tip.setAttribute("aria-hidden", "true");
  document.body.appendChild(tip);

  function show(mark) {
    tip.textContent = "";
    var title = document.createElement("b");
    title.textContent = mark.getAttribute("data-tip-title");
    tip.appendChild(title);
    var detail = mark.getAttribute("data-tip");
    if (detail) {
      var line = document.createElement("span");
      line.textContent = detail;
      tip.appendChild(line);
    }

    var box = mark.getBoundingClientRect();
    tip.classList.add("is-visible");
    var w = tip.offsetWidth;
    var h = tip.offsetHeight;
    var x = box.left + box.width / 2 - w / 2;
    var y = box.top - h - 10;
    if (y < 8) y = box.bottom + 10;
    x = Math.max(8, Math.min(x, window.innerWidth - w - 8));
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }

  function hide() {
    tip.classList.remove("is-visible");
  }

  Array.prototype.forEach.call(marks, function (mark) {
    mark.addEventListener("mouseenter", function () { show(mark); });
    mark.addEventListener("mouseleave", hide);
    mark.addEventListener("focus", function () { show(mark); });
    mark.addEventListener("blur", hide);
  });

  window.addEventListener("scroll", hide, { passive: true });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") hide();
  });
})();
