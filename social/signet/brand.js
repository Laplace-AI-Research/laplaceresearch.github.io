/* Signet brand primitives (Laplace Lattice system, research/brand/laplace-lattice.html in conviction-research).
   Every plate is a square lattice pressed by seals with the Laplace-kernel profile; one wax mark per image.
   Pure canvas so plates render at exact pixel sizes and can be saved as PNG. */
(function () {
  const TAU = Math.PI * 2;
  const P = {
    paper: "#EEF0EC", plate: "#E5E8E3", ink: "#16181D", graphite: "#59606A", rule: "#C4C9C2",
    wax: "#8E1E19", prussian: "#1E3D66",
  };
  const PD = {
    paper: "#101216", plate: "#171A1F", ink: "#E6E8E3", graphite: "#969CA5", rule: "#2C3037",
    wax: "#D65B4F", prussian: "#86A8DA",
  };
  const F = {
    display: '"Bodoni Moda", "Bodoni 72", Didot, Georgia, serif',
    body: '"Instrument Sans", "Helvetica Neue", Arial, sans-serif',
    mono: '"JetBrains Mono", ui-monospace, Menlo, monospace',
  };

  function rgb(hex) {
    const n = parseInt(hex.replace("#", ""), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  // Laplace pinch: r' = r (1 - k e^{-r/R}); monotone for k < 1, so lines never cross.
  function pinch(x, y, S) {
    let px = x, py = y;
    for (const s of S) {
      const dx = px - s.x, dy = py - s.y, r = Math.hypot(dx, dy);
      const f = 1 - s.k * Math.exp(-r / s.R);
      px = s.x + dx * f; py = s.y + dy * f;
    }
    return [px, py];
  }
  function lattice(ctx, x0, y0, w, h, o) {
    const { gap, seals = [], color, lw = 0.75, alpha = 1, lines = true, dots = 0, dotAlpha = 1 } = o;
    const ox = x0 + (w % gap) / 2, oy = y0 + (h % gap) / 2;
    ctx.save();
    ctx.beginPath(); ctx.rect(x0, y0, w, h); ctx.clip();
    ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = lw;
    if (lines) {
      ctx.globalAlpha = alpha; ctx.beginPath();
      for (let y = oy; y <= y0 + h + 0.1; y += gap) {
        let first = true;
        for (let x = x0 - gap; x <= x0 + w + gap; x += 3) { const p = pinch(x, y, seals); first ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]); first = false; }
      }
      for (let x = ox; x <= x0 + w + 0.1; x += gap) {
        let first = true;
        for (let y = y0 - gap; y <= y0 + h + gap; y += 3) { const p = pinch(x, y, seals); first ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]); first = false; }
      }
      ctx.stroke();
    }
    if (dots) {
      ctx.globalAlpha = dotAlpha;
      for (let y = oy; y <= y0 + h + 0.1; y += gap) for (let x = ox; x <= x0 + w + 0.1; x += gap) {
        const p = pinch(x, y, seals); ctx.beginPath(); ctx.arc(p[0], p[1], dots, 0, TAU); ctx.fill();
      }
    }
    ctx.restore();
  }
  function ringRadii(N, Rmax, rin) {
    const L = Math.log(1 / (N + 1)), out = [];
    for (let k = 1; k <= N; k++) out.push(rin + (Rmax - rin) * Math.log(k / (N + 1)) / L);
    return out;
  }
  function rings(ctx, s, o) {
    const { N, Rmax, rin, color, lw, wax } = o;
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw;
    for (const r of ringRadii(N, Rmax, rin)) { ctx.beginPath(); ctx.arc(s.x, s.y, Math.max(0.5, r), 0, TAU); ctx.stroke(); }
    if (wax) { ctx.fillStyle = wax; ctx.beginPath(); ctx.arc(s.x, s.y, Math.max(2, rin * 0.6), 0, TAU); ctx.fill(); }
    ctx.restore();
  }
  // Banded contours of psi = sum a e^{-|x-c|/b} (impression / two-colour renderings).
  function bands(w, h, srcs, color, thr, step) {
    const off = document.createElement("canvas"); off.width = w; off.height = h;
    const o = off.getContext("2d"), img = o.createImageData(w, h), D = img.data;
    const [r, g, b] = rgb(color);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      let v = 0;
      for (const s of srcs) v += (s.a || 1) * Math.exp(-Math.hypot(i - s.x, j - s.y) / s.b);
      if (v > thr && Math.floor((v - thr) / step) % 2 === 0) {
        const k = (j * w + i) * 4; D[k] = r; D[k + 1] = g; D[k + 2] = b; D[k + 3] = 255;
      }
    }
    o.putImageData(img, 0, 0);
    return off;
  }
  // A pressed seal: lattice pinch + contour rings, one per billion parameters.
  function pressed(ctx, box, seals, pal, o = {}) {
    const S = seals.map(s => ({ x: s.x, y: s.y, R: s.R, k: s.k ?? 0.72 }));
    lattice(ctx, box.x, box.y, box.w, box.h, {
      gap: o.gap ?? 40, seals: S, color: pal.ink, lw: o.lw ?? 0.9, alpha: o.alpha ?? 0.22, dots: o.dots ?? 1.6, dotAlpha: 0.85,
    });
    seals.forEach((s, i) => rings(ctx, s, {
      N: s.N, Rmax: s.Rmax, rin: Math.max(5, s.Rmax * 0.1), color: pal.ink,
      lw: s.lw ?? (s.N > 6 ? 1.3 : 1.6), wax: (o.waxIndex ?? seals.length - 1) === i ? pal.wax : null,
    }));
  }
  function sealSVG(N, { solid = false, px = 0, pal = P } = {}) {
    const R = 44, rin = 7, lw = N > 6 ? 1.6 : (px && px <= 32 ? 3.6 : 2.6);
    let out = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="Signet mark, ${N} rings"${px ? ` width="${px}" height="${px}"` : ""}>`;
    if (solid) out += `<circle cx="50" cy="50" r="49" fill="${pal.ink}"/>`;
    ringRadii(N, R, rin).forEach(r => {
      out += `<circle cx="50" cy="50" r="${r.toFixed(2)}" fill="none" stroke="${solid ? pal.paper : pal.ink}" stroke-width="${lw}"/>`;
    });
    out += `<circle cx="50" cy="50" r="${px && px <= 24 ? 7 : 4.2}" fill="${pal.wax}"/></svg>`;
    return out;
  }

  /* ---------- type helpers ---------- */
  function font(ctx, fam, size, weight = 400, style = "") { ctx.font = `${style} ${weight} ${size}px ${F[fam]}`.trim(); }
  function text(ctx, s, x, y, o = {}) {
    ctx.save();
    font(ctx, o.fam || "body", o.size || 24, o.weight || 400, o.style || "");
    ctx.fillStyle = o.color || "#000"; ctx.textAlign = o.align || "left"; ctx.textBaseline = o.base || "alphabetic";
    if (o.track) ctx.letterSpacing = o.track + "px";
    const m = ctx.measureText(s), w = m.width;
    if (o.knock) { // flat paper knockout so type never sits on lattice lines
      const pad = o.pad ?? 6, x0 = o.align === "right" ? x - w : (o.align === "center" ? x - w / 2 : x);
      const fill = ctx.fillStyle; ctx.fillStyle = o.knock;
      ctx.fillRect(x0 - pad, y - m.actualBoundingBoxAscent - pad, w + 2 * pad, m.actualBoundingBoxAscent + m.actualBoundingBoxDescent + 2 * pad);
      ctx.fillStyle = fill;
    }
    ctx.fillText(s, x, y);
    ctx.restore();
    return w;
  }
  function wrap(ctx, s, x, y, maxW, lh, o = {}) {
    ctx.save(); font(ctx, o.fam || "body", o.size || 24, o.weight || 400, o.style || "");
    if (o.track) ctx.letterSpacing = o.track + "px";
    const words = s.split(" "); let line = "", lines = [];
    for (const wd of words) { const t = line ? line + " " + wd : wd; if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = wd; } else line = t; }
    if (line) lines.push(line);
    ctx.fillStyle = o.color || "#000"; ctx.textAlign = o.align || "left";
    lines.forEach((l, i) => ctx.fillText(l, x, y + i * lh));
    ctx.restore();
    return lines.length;
  }
  let markImg = null;
  function loadMark(src) {
    return new Promise(res => { const im = new Image(); im.onload = () => { markImg = im; res(); }; im.onerror = () => res(); im.src = src; });
  }
  function mark(ctx, x, y, size, color) { // Laplace lab asterisk, tinted to one colour
    if (!markImg) return;
    const off = document.createElement("canvas"); off.width = off.height = size * 2;
    const o = off.getContext("2d"); o.drawImage(markImg, 0, 0, size * 2, size * 2);
    o.globalCompositeOperation = "source-in"; o.fillStyle = color; o.fillRect(0, 0, size * 2, size * 2);
    ctx.drawImage(off, x, y, size, size);
  }

  window.SignetBrand = { P, PD, F, TAU, pinch, lattice, ringRadii, rings, bands, pressed, sealSVG, font, text, wrap, loadMark, mark };
})();
