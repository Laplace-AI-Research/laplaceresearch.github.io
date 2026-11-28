// Unit tests for the Oracle and the Second Sensor state model.
// Run from the repo root: node --test tools/playground/
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const M = require("../../playground/oracle/oracle-model.js");
const fx = require("../../playground/oracle/oracle-data.js");

const play = (...moves) => moves.reduce((s, m) => (Array.isArray(m) ? M.step(s, m[0], m[1]) : M.step(s, m)), M.initial());

test("initial state", () => {
  const v = M.view(M.initial(), fx);
  assert.equal(v.phase, "start");
  assert.equal(v.credits, 4);
  assert.equal(M.pct(v.prior), "50%");
  assert.deepEqual(v.displays, { A: "unread", B: "unread" });
  assert.equal(v.guess, null);
  assert.equal(v.wiring, "copy");
});

test("read A then stop keeps two credits, also after the forced copy", () => {
  let s = play("readA");
  assert.equal(M.credits(s, fx.world), 2);
  assert.equal(M.pct(M.view(s, fx).exactAfterA), "80%");
  assert.equal(M.pct(M.view(s, fx).aquilaEpisode), "80%");
  s = M.step(s, "stop");
  assert.equal(M.phase(s), "stopped");
  assert.equal(M.credits(s, fx.world), 2);
  assert.deepEqual(M.displays(s), { A: "positive", B: "unread" });
  s = M.step(s, "showCopy");
  assert.equal(M.phase(s), "forecast");
  assert.equal(M.credits(s, fx.world), 2);
  assert.deepEqual(M.displays(s), { A: "positive", B: "supplied" });
  assert.equal(M.step(s, "buyB"), s, "cannot buy after stopping");
});

test("read A then buy B: 4 -> 2 -> 0 and repeats are no-ops", () => {
  let s = M.initial();
  const seen = [M.credits(s, fx.world)];
  s = M.step(s, "readA"); seen.push(M.credits(s, fx.world));
  assert.equal(M.step(s, "readA"), s);
  s = M.step(s, "buyB"); seen.push(M.credits(s, fx.world));
  assert.deepEqual(seen, [4, 2, 0]);
  for (const m of ["readA", "buyB", "stop", "showCopy"]) assert.equal(M.step(s, m), s);
  assert.equal(M.route(s), "buy");
  assert.deepEqual(M.displays(s), { A: "positive", B: "positive" });
});

test("forecast parsing", () => {
  assert.deepEqual(M.parseForecast(""), { error: "empty" });
  assert.deepEqual(M.parseForecast("   "), { error: "empty" });
  assert.deepEqual(M.parseForecast("-1"), { error: "format" });
  assert.deepEqual(M.parseForecast("abc"), { error: "format" });
  assert.deepEqual(M.parseForecast("100.01"), { error: "range" });
  assert.deepEqual(M.parseForecast("101"), { error: "range" });
  assert.deepEqual(M.parseForecast("0"), { value: 0 });
  assert.deepEqual(M.parseForecast("100"), { value: 100 });
  assert.deepEqual(M.parseForecast("82.5"), { value: 82.5 });
  assert.deepEqual(M.parseForecast("82.5%"), { value: 82.5 });
  assert.deepEqual(M.parseForecast(".5"), { value: 0.5 });
});

test("submit only accepts a valid number in the forecast phase", () => {
  const s = play("readA", "buyB");
  assert.equal(M.step(s, "submit", undefined), s);
  assert.equal(M.step(s, "submit", NaN), s);
  assert.equal(M.step(s, "submit", 101), s);
  for (const v of [0, 100, 82.5]) {
    const r = M.step(s, "submit", v);
    assert.equal(M.phase(r), "revealed");
    assert.deepEqual(r.guess, { value: v, wiring: "copy" });
    assert.equal(M.guessText(v), String(v) + "%");
  }
  assert.equal(M.step(play("readA"), "submit", 50).revealed, false);
});

test("copy reveal and rewiring", () => {
  let s = play("readA", "stop", "showCopy", ["submit", 82.5]);
  let v = M.view(s, fx);
  assert.equal(M.pct(v.exactAfterAB), "80%");
  assert.equal(M.pct(v.aquilaAfterAB), "90.5%");
  assert.equal(v.gapPoints, 10.5);
  assert.equal(v.guessOnThisWiring, true);
  s = M.step(s, "rewire", "independent");
  v = M.view(s, fx);
  assert.equal(M.pct(v.exactAfterAB), "94.1%");
  assert.ok(Math.abs(v.exactAfterAB - 16 / 17) < 1e-15);
  assert.equal(M.pct(v.aquilaAfterAB), "90.5%");
  assert.equal(M.pct(v.aquilaAfterA), "80%");
  assert.equal(v.guessOnThisWiring, false);
  assert.equal(v.guess.wiring, "copy");
  assert.equal(v.credits, 2);
  assert.deepEqual(v.displays, { A: "positive", B: "supplied" });
  s = M.step(s, "rewire", "copy");
  v = M.view(s, fx);
  assert.equal(M.pct(v.exactAfterAB), "80%");
  assert.equal(M.pct(v.aquilaAfterAB), "90.5%");
  assert.equal(v.guessOnThisWiring, true);
  assert.equal(M.step(s, "rewire", "bogus"), s);
  assert.equal(M.step(play("readA", "buyB"), "rewire", "independent").wiring, "copy", "no rewiring before reveal");
});

test("skip reveals without a visitor number", () => {
  const s = play("readA", "buyB", "skip");
  assert.equal(M.phase(s), "revealed");
  assert.equal(s.guess, null);
  assert.equal(s.skipped, true);
});

test("reset clears everything", () => {
  const s = M.step(play("readA", "buyB", ["submit", 70], ["rewire", "independent"]), "reset");
  assert.deepEqual(s, M.initial());
});

test("display rounding never turns 90.5 into 91", () => {
  assert.equal(M.pctMilli(905), "90.5%");
  assert.equal(M.pctMilli(800), "80%");
  assert.equal(M.pctMilli(667), "66.7%");
  assert.equal(M.pct(16 / 17), "94.1%");
});

test("fixture matches the brief", () => {
  const rows = fx.family.map((m) => [m.name, m.action, m.afterA, m.afterAB]);
  assert.deepEqual(rows, [
    ["Inkling 2 Mini (base)", "buy", 800, 800],
    ["Oracle Lyra", "stop", 667, 889],
    ["Oracle Vega", "stop", 714, 889],
    ["Oracle Aquila", "stop", 800, 905],
    ["Oracle Altair", "stop", 667, 800],
    ["Oracle Cygnus", "stop", 727, 941],
    ["Oracle Deneb", "stop", 800, 941]
  ]);
  const a = fx.records.aquila;
  assert.deepEqual([a.copy.afterA, a.copy.afterAB, a.independent.afterA, a.independent.afterAB].map((r) => [r.id, r.action, r.forecast]), [
    ["copy-11-1", "stop", 800], ["copy-11-2", "stop", 905], ["independent-11-1", "stop", 800], ["independent-11-2", "stop", 905]
  ]);
  assert.deepEqual(fx.episode, { model: "aquila", query: "A", before: 500, observation: "positive", action: "stop", after: 800 });
});
