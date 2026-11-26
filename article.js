/* Laplace Research — Editorial article figure zoom lightbox. */
(function () {
  "use strict";

  var frames = document.querySelectorAll(".post-fig-frame[data-zoomable]");
  if (!frames.length) return;

  var box = document.createElement("div");
  box.className = "post-lightbox";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-label", "Enlarged figure");
  box.innerHTML =
    '<div class="post-lightbox-card">' +
    '<button type="button" class="post-lightbox-close" aria-label="Close enlarged figure">&times;</button>' +
    '<div class="post-lightbox-body"></div>' +
    '<p class="post-lightbox-cap"></p>' +
    "</div>";
  document.body.appendChild(box);

  var body = box.querySelector(".post-lightbox-body");
  var cap = box.querySelector(".post-lightbox-cap");
  var closeBtn = box.querySelector(".post-lightbox-close");
  var lastTrigger = null;

  function open(frame) {
    lastTrigger = frame;
    body.innerHTML = frame.innerHTML;
    var fig = frame.closest("figure");
    var fc = fig && fig.querySelector("figcaption");
    cap.textContent = fc ? fc.textContent : "";
    cap.style.display = cap.textContent ? "" : "none";
    box.classList.add("is-open");
    closeBtn.focus();
  }

  function close() {
    box.classList.remove("is-open");
    if (lastTrigger) lastTrigger.focus();
  }

  Array.prototype.forEach.call(frames, function (frame) {
    frame.addEventListener("click", function () { open(frame); });
    frame.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        open(frame);
      }
    });
  });

  closeBtn.addEventListener("click", close);
  box.addEventListener("click", function (e) {
    if (e.target === box) close();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && box.classList.contains("is-open")) close();
  });
})();
