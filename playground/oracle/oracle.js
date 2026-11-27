/* Oracle and the Second Sensor: page controller. Renders the state model
   into prebuilt markup (nothing is rebuilt, so focus is never lost) and
   moves display B's wire. Fixture: oracle-data.js. Rules: oracle-model.js. */
(function () {
  "use strict";
  var O = window.LaplaceOracle;
  var root = document.querySelector(".or-main");
  if (!O || !O.fixture || !O.model || !root) return;
  var fx = O.fixture;
  var M = O.model;
  var pct = M.pct;

  var $ = function (sel) { return root.querySelector(sel); };
  var $$ = function (sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); };
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  var state = M.initial();
  var board = $(".or-board");
  var wireB = $("#or-wire-b");
  var jack = $("#or-jack");
  var status = $("#or-status");
  var input = $("#or-guess");
  var error = $("#or-guess-error");
  var more = $("#more");
  var steps = {};
  $$("[data-step]").forEach(function (el) { steps[el.getAttribute("data-step")] = el; });

  root.classList.add("or-live");

  function set(name, text) {
    $$('[data-bind="' + name + '"]').forEach(function (el) { el.textContent = text; });
  }

  /* ---------- family table (same-sensor fixture) ---------- */

  var body = $("#or-family");
  fx.family.forEach(function (m) {
    var tr = document.createElement("tr");
    if (m.id === "aquila") tr.className = "is-lead";
    var cells = [
      ["th", m.name],
      ["td", m.training],
      ["td", m.action === "buy" ? "Buy B" : "Stop"],
      ["td", M.pctMilli(m.afterA), "num"],
      ["td", M.pctMilli(m.afterAB), "num"]
    ];
    cells.forEach(function (c) {
      var cell = document.createElement(c[0]);
      if (c[0] === "th") cell.scope = "row";
      if (c[2]) cell.className = c[2];
      cell.textContent = c[1];
      tr.appendChild(cell);
    });
    body.appendChild(tr);
  });
  set("exactCopyA", pct(M.exact(fx.world, "copy", 1).p));
  set("exactCopyAB", pct(M.exact(fx.world, "copy", 2).p));

  /* ---------- the wire ---------- */

  var WIRE_Y = { copy: 31, independent: 75 };
  var wireY = WIRE_Y.copy;
  var anim = 0;
  function drawWire(y) {
    wireY = y;
    wireB.setAttribute("d", "M64 " + y + " C70 " + y + " 70 75 76 75");
    jack.style.top = y + "%";
  }
  function moveWire(to) {
    var target = WIRE_Y[to];
    cancelAnimationFrame(anim);
    if (reduced || target === wireY) { drawWire(target); return; }
    var from = wireY, t0 = 0, dur = 480;
    var tick = function (t) {
      if (!t0) t0 = t;
      var k = Math.min(1, (t - t0) / dur);
      var e = 1 - Math.pow(1 - k, 3);
      drawWire(from + (target - from) * e);
      if (k < 1) anim = requestAnimationFrame(tick);
    };
    anim = requestAnimationFrame(tick);
  }

  /* ---------- render ---------- */

  var READ = { unread: "Unread", positive: "Positive", supplied: "Positive" };

  function render() {
    var v = M.view(state, fx);
    var ph = v.phase;

    Object.keys(steps).forEach(function (k) { steps[k].hidden = true; });
    if (ph === "start") steps.start.hidden = false;
    if (ph === "decide") steps.decide.hidden = false;
    if (ph === "stopped" || ph === "forecast") steps.aquila.hidden = false;
    if (ph === "forecast") steps.forecast.hidden = false;
    if (ph === "revealed") steps.revealed.hidden = false;
    more.hidden = ph !== "revealed";

    // instrument and ledger
    set("credits", String(v.credits));
    $$(".or-pips i").forEach(function (pip, i) { pip.classList.toggle("on", i < v.credits); });
    ["A", "B"].forEach(function (d) {
      var s = v.displays[d];
      var node = $(".or-display-" + d.toLowerCase());
      node.setAttribute("data-state", s);
      set("display" + d, READ[s]);
      set("ledger" + d, s === "supplied" ? "Positive (supplied, free)" : READ[s]);
    });
    var copy = v.wiring === "copy";
    board.setAttribute("data-wiring", v.wiring);
    set("displayBSource", copy ? "copy of sensor A" : "from sensor B");
    set("wiringText", copy
      ? "Wiring: one physical sensor, sensor A, feeds both displays. Display B shows a copy of whatever sensor A reports."
      : "Wiring: sensor A feeds display A. A second sensor, sensor B, with the same 80% accuracy, feeds display B. Their errors are independent given the signal.");
    moveWire(v.wiring);

    // numbers
    set("exactAfterA", pct(v.exactAfterA));
    set("exactAfterAB", pct(v.exactAfterAB));
    set("aquilaEpisode", pct(v.aquilaEpisode));
    set("aquilaAfterA", pct(v.aquilaAfterA));
    set("aquilaAfterAB", pct(v.aquilaAfterAB));

    // Aquila's decision, after the visitor's
    var buy = v.route === "buy";
    set("aquilaTitle", buy ? "Display B reads Positive" : "You stopped with two credits");
    set("aquilaYou", buy ? "You spent all four credits." : v.displays.B === "supplied"
      ? "Display B is shown below as a supplied reading. You did not buy it, and you still have two credits."
      : "Display B is unread.");
    $$("[data-show]").forEach(function (el) {
      var show = el.getAttribute("data-show");
      el.hidden = show === "stopped" ? ph !== "stopped" : ph !== "forecast";
    });
    set("forcedText", buy
      ? "Aquila never saw display B in its own episode. The comparison uses a separate recorded test in which the evaluator gave Aquila both positive readings."
      : "This opens a separate recorded test in which the evaluator gave Aquila both positive readings.");

    // reveal
    set("revealTitle", copy ? "one piece of evidence" : "two pieces of evidence");
    if (v.skipped) {
      set("youValue", "\u2014");
      set("youNote", "Skipped");
    } else if (v.guess && v.guessOnThisWiring) {
      set("youValue", M.guessText(v.guess.value));
      set("youNote", "Same-sensor wiring");
    } else if (v.guess) {
      set("youValue", "\u2014");
      set("youNote", "Your " + M.guessText(v.guess.value) + " was for the same-sensor wiring");
    }
    set("why", copy
      ? "B reports whatever A reports, so seeing the same positive twice adds no evidence."
      : "Sensor B errs independently of sensor A, so its positive multiplies the odds by 4 again: 16 to 1.");
    var gap = Math.abs(v.gapPoints);
    set("gap", copy
      ? "Aquila\u2019s " + pct(v.aquilaAfterAB) + " is " + gap + " percentage points above the exact result."
      : "Aquila\u2019s recorded answer is " + pct(v.aquilaAfterAB) + " under both wirings, " + gap + " points below the exact result here.");
    set("trailYou", buy ? "Read A and B. " + v.credits + " credits left." : "Read A and stopped. " + v.credits + " credits left.");
    set("trailTest", copy
      ? "Aquila was given A and B, both positive, and told that B copies A."
      : "Aquila was given A and B, both positive, from independent sensors.");
    $$('input[name="wiring"]').forEach(function (r) { r.checked = r.value === v.wiring; });
    return v;
  }

  /* ---------- moves ---------- */

  function announce(text) {
    status.textContent = "";
    setTimeout(function () { status.textContent = text; }, 30);
  }

  function focusStep(name) {
    var h = steps[name] && steps[name].querySelector("h2");
    if (h) h.focus();
  }

  function dispatch(move, arg) {
    var next = M.step(state, move, arg);
    if (next === state) return;
    state = next;
    var v = render();
    var nums = "Exact calculation " + pct(v.exactAfterAB) + ". Oracle Aquila " + pct(v.aquilaAfterAB) + ".";
    switch (move) {
      case "readA":
        announce("Display A: Positive. " + v.credits + " credits left. Exact calculation " + pct(v.exactAfterA) + ". Oracle Aquila " + pct(v.aquilaEpisode) + ".");
        focusStep("decide");
        break;
      case "buyB":
        announce("Display B: Positive. " + v.credits + " credits left. Oracle Aquila stopped with two credits left.");
        focusStep("aquila");
        break;
      case "stop":
        announce("You stopped with " + v.credits + " credits. Oracle Aquila also stopped with two credits left.");
        focusStep("aquila");
        break;
      case "showCopy":
        announce("Separate recorded test: display B supplied as Positive. You still have " + v.credits + " credits.");
        focusStep("forecast");
        break;
      case "submit":
        announce("Your forecast " + M.guessText(arg) + ". " + nums);
        focusStep("revealed");
        break;
      case "skip":
        announce(nums);
        focusStep("revealed");
        break;
      case "rewire":
        announce((v.wiring === "copy" ? "Display B copies sensor A. " : "Display B reads an independent sensor B. ") + nums);
        break;
      case "reset":
        input.value = "";
        clearError();
        $$("details.or-details").forEach(function (d) { d.open = false; });
        announce("Reset. Prior 50%, " + v.credits + " credits, both displays unread.");
        focusStep("start");
        break;
    }
  }

  var MESSAGES = {
    empty: "Enter a probability from 0 to 100, or choose Just show me.",
    format: "Use a plain number, such as 82.5.",
    range: "Enter a value from 0 to 100."
  };
  function clearError() {
    error.hidden = true;
    error.textContent = "";
    input.removeAttribute("aria-invalid");
    input.setAttribute("aria-describedby", "or-guess-help");
  }

  root.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-move]");
    if (btn && root.contains(btn)) dispatch(btn.getAttribute("data-move"));
  });
  steps.forecast.addEventListener("submit", function (e) {
    e.preventDefault();
    var r = M.parseForecast(input.value);
    if (r.error) {
      error.textContent = MESSAGES[r.error];
      error.hidden = false;
      input.setAttribute("aria-invalid", "true");
      input.setAttribute("aria-describedby", "or-guess-help or-guess-error");
      input.focus();
      announce(MESSAGES[r.error]);
      return;
    }
    clearError();
    dispatch("submit", r.value);
  });
  input.addEventListener("input", function () { if (!error.hidden) clearError(); });
  $$('input[name="wiring"]').forEach(function (r) {
    r.addEventListener("change", function () { if (r.checked) dispatch("rewire", r.value); });
  });

  render();
})();
