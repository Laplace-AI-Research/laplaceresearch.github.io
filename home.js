/* Laplace Research — the homepage ridgeline.
   Rows of Laplace densities, f(x) = exp(-|x - mu| / b) / 2b, drawn back to
   front so nearer ridges hide farther ones. Each row's location and scale
   drift slowly, like beliefs being revised. One row is drawn in the accent:
   the sharpest, best-located estimate. Static under reduced motion. */
(function () {
  "use strict";

  var canvas = document.querySelector("[data-ridgeline]");
  if (!canvas || !canvas.getContext) return;

  var ctx = canvas.getContext("2d");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var dark = window.matchMedia("(prefers-color-scheme: dark)");

  /* deterministic so the picture is the same on every visit */
  var seed = 20261119;
  function rand() {
    seed = (seed * 16807) % 2147483647;
    return seed / 2147483647;
  }

  var ROWS = 30;
  var ACCENT_ROW = 21;
  var rows = [];
  for (var i = 0; i < ROWS; i++) {
    var depth = i / (ROWS - 1); // 0 = far, 1 = near
    rows.push({
      mu: 0.18 + rand() * 0.64,
      b: 0.035 + rand() * 0.075 + (1 - depth) * 0.03,
      amp: 0.55 + rand() * 0.55,
      mu2: rand(),
      w2: rand() < 0.55 ? 0.25 + rand() * 0.35 : 0,
      phase: rand() * Math.PI * 2,
      speed: 0.12 + rand() * 0.16,
    });
  }
  rows[ACCENT_ROW].mu = 0.64;
  rows[ACCENT_ROW].b = 0.03;
  rows[ACCENT_ROW].amp = 1.15;
  rows[ACCENT_ROW].w2 = 0;

  var W = 0;
  var H = 0;
  var colors = {};

  function readColors() {
    var cs = getComputedStyle(canvas);
    colors.bg = cs.getPropertyValue("--bg").trim() || "#fbfbf9";
    colors.ink = cs.getPropertyValue("--text").trim() || "#15171b";
    colors.accent = cs.getPropertyValue("--s1").trim() || "#2a78d6";
  }

  function resize() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function laplace(u, mu, b) {
    return Math.exp(-Math.abs(u - mu) / b);
  }

  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    var top = H * 0.16;
    var gap = (H - top) / (ROWS + 1);
    var step = W > 900 ? 3 : 2;

    for (var r = 0; r < ROWS; r++) {
      var row = rows[r];
      var base = top + gap * (r + 1);
      var height = gap * 6.5 * row.amp;
      var drift = Math.sin(t * row.speed + row.phase);
      var mu = row.mu + 0.05 * drift;
      var b = row.b * (1 + 0.28 * Math.sin(t * row.speed * 0.7 + row.phase * 1.3));
      var mu2 = row.mu2 + 0.04 * Math.cos(t * row.speed * 0.8 + row.phase);

      ctx.beginPath();
      ctx.moveTo(0, base);
      for (var x = 0; x <= W + step; x += step) {
        var u = x / W;
        var d = laplace(u, mu, b);
        if (row.w2) d = Math.max(d, row.w2 * laplace(u, mu2, b * 1.7));
        ctx.lineTo(x, base - height * d);
      }
      ctx.lineTo(W, H + 2);
      ctx.lineTo(0, H + 2);
      ctx.closePath();

      ctx.fillStyle = colors.bg;
      ctx.fill();

      var isAccent = r === ACCENT_ROW;
      var depth = r / (ROWS - 1);
      ctx.globalAlpha = isAccent ? 1 : 0.16 + depth * 0.42;
      ctx.strokeStyle = isAccent ? colors.accent : colors.ink;
      ctx.lineWidth = isAccent ? 1.75 : 1;
      ctx.lineJoin = "round";
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
  }

  var visible = true;
  var frame = null;
  var start = performance.now();

  var last = 0;

  function loop(now) {
    frame = null;
    /* the drift is slow, so 60fps is plenty even on high-refresh screens */
    if (now - last >= 15 || reduce.matches) {
      last = now;
      draw((now - start) / 1000);
    }
    if (visible && !reduce.matches && !document.hidden) {
      frame = requestAnimationFrame(loop);
    }
  }

  function kick() {
    if (frame === null) frame = requestAnimationFrame(loop);
  }

  function refresh() {
    readColors();
    resize();
    draw((performance.now() - start) / 1000);
    kick();
  }

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible) kick();
    }).observe(canvas);
  }

  document.addEventListener("visibilitychange", kick);
  window.addEventListener("resize", refresh);
  if (dark.addEventListener) {
    dark.addEventListener("change", refresh);
    reduce.addEventListener("change", refresh);
  }

  refresh();
})();
