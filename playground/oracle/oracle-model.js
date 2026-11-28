/* Oracle and the Second Sensor: deterministic state model.
   No DOM. Every transition returns a new state, or the same state when the
   move is not allowed, so repeated clicks or key presses cannot charge twice. */
(function (root) {
  "use strict";

  var WIRINGS = ["copy", "independent"];

  function initial() {
    return { purchases: [], stopped: false, supplied: false, guess: null, skipped: false, revealed: false, wiring: "copy" };
  }

  function with_(state, patch) {
    var next = {};
    Object.keys(state).forEach(function (k) { next[k] = state[k]; });
    Object.keys(patch).forEach(function (k) { next[k] = patch[k]; });
    return next;
  }

  function credits(state, world) {
    return world.credits - world.cost * state.purchases.length;
  }

  function route(state) {
    if (state.purchases.length === 2) return "buy";
    if (state.stopped) return "stop";
    return null;
  }

  function phase(state) {
    if (state.revealed) return "revealed";
    if (state.purchases.length === 0) return "start";
    if (state.purchases.length === 2 || state.supplied) return "forecast";
    if (state.stopped) return "stopped";
    return "decide";
  }

  // "unread" | "positive" (bought by the visitor) | "supplied" (diagnostic, free)
  function displays(state) {
    return {
      A: state.purchases.indexOf("A") >= 0 ? "positive" : "unread",
      B: state.purchases.indexOf("B") >= 0 ? "positive" : state.supplied ? "supplied" : "unread"
    };
  }

  var moves = {
    readA: function (s) {
      return phase(s) === "start" ? with_(s, { purchases: ["A"] }) : s;
    },
    buyB: function (s) {
      return phase(s) === "decide" ? with_(s, { purchases: ["A", "B"] }) : s;
    },
    stop: function (s) {
      return phase(s) === "decide" ? with_(s, { stopped: true }) : s;
    },
    showCopy: function (s) {
      return phase(s) === "stopped" ? with_(s, { supplied: true }) : s;
    },
    submit: function (s, value) {
      if (phase(s) !== "forecast" || typeof value !== "number" || !(value >= 0 && value <= 100)) return s;
      return with_(s, { guess: { value: value, wiring: s.wiring }, skipped: false, revealed: true });
    },
    skip: function (s) {
      return phase(s) === "forecast" ? with_(s, { guess: null, skipped: true, revealed: true }) : s;
    },
    rewire: function (s, wiring) {
      return phase(s) === "revealed" && WIRINGS.indexOf(wiring) >= 0 ? with_(s, { wiring: wiring }) : s;
    },
    reset: function () {
      return initial();
    }
  };

  function step(state, move, arg) {
    var fn = moves[move];
    if (!fn) throw new Error("Unknown move: " + move);
    return fn(state, arg);
  }

  // Visitor input: a plain percentage, 0 to 100 inclusive, decimals allowed.
  function parseForecast(text) {
    var t = String(text == null ? "" : text).trim().replace(/\s*%$/, "");
    if (t === "") return { error: "empty" };
    if (!/^(\d+(\.\d*)?|\.\d+)$/.test(t)) return { error: "format" };
    var v = Number(t);
    if (!(v >= 0 && v <= 100)) return { error: "range" };
    return { value: v };
  }

  // Exact posterior for two positive readings, in full precision.
  function exact(world, wiring, readings) {
    var odds = world.prior / (1000 - world.prior);
    var lr = world.hitIfOn / world.hitIfOff;
    if (readings >= 1) odds *= lr;
    if (readings >= 2) odds *= wiring === "copy" ? 1 : lr;
    return { odds: odds, p: odds / (1 + odds) };
  }

  // One decimal place, trailing ".0" dropped: 80%, 90.5%, 94.1%.
  function pct(p) {
    var tenths = Math.round(p * 1000 + 1e-9);
    var s = (tenths / 10).toFixed(1);
    return s.replace(/\.0$/, "") + "%";
  }
  function pctMilli(m) { return pct(m / 1000); }
  function guessText(v) { return String(v) + "%"; }

  // All numbers the page shows for a given state come from here.
  function view(state, fx) {
    var w = state.wiring;
    var rec = fx.records.aquila[w];
    var exA = exact(fx.world, w, 1);
    var exAB = exact(fx.world, w, 2);
    return {
      phase: phase(state),
      route: route(state),
      credits: credits(state, fx.world),
      displays: displays(state),
      wiring: w,
      prior: fx.world.prior / 1000,
      exactAfterA: exA.p,
      exactAfterAB: exAB.p,
      aquilaEpisode: fx.episode.after / 1000,
      aquilaAfterA: rec.afterA.forecast / 1000,
      aquilaAfterAB: rec.afterAB.forecast / 1000,
      gapPoints: Math.round(rec.afterAB.forecast - exAB.p * 1000) / 10,
      guess: state.guess,
      guessOnThisWiring: !!state.guess && state.guess.wiring === w,
      skipped: state.skipped
    };
  }

  var api = { initial: initial, step: step, phase: phase, credits: credits, displays: displays, route: route, parseForecast: parseForecast, exact: exact, pct: pct, pctMilli: pctMilli, guessText: guessText, view: view };
  if (typeof module === "object" && module.exports) module.exports = api;
  else (root.LaplaceOracle = root.LaplaceOracle || {}).model = api;
})(this);
