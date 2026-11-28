/* Oracle and the Second Sensor: the recorded fixture.
   Source: Oracle fixed-history duplicate-reading diagnostics, November 2026.
   Aquila records: copy-11-1, copy-11-2, independent-11-1, independent-11-2.
   Probabilities are integer thousandths. These are single recorded responses
   from the named checkpoints, not averages; nothing here is calculated. */
(function (root) {
  "use strict";
  var fixture = {
    world: { prior: 500, credits: 4, cost: 2, hitIfOn: 800, hitIfOff: 200 },

    // Aquila's ordinary recorded episode: query A at 0.500, positive, stop at 0.800.
    episode: { model: "aquila", query: "A", before: 500, observation: "positive", action: "stop", after: 800 },

    // Fixed-history tests: the evaluator supplied A+ (step 1) and A+, B+ (step 2).
    // In the copy condition the model had been told that B copies A.
    records: {
      aquila: {
        copy: { afterA: { id: "copy-11-1", action: "stop", forecast: 800 }, afterAB: { id: "copy-11-2", action: "stop", forecast: 905 } },
        independent: { afterA: { id: "independent-11-1", action: "stop", forecast: 800 }, afterAB: { id: "independent-11-2", action: "stop", forecast: 905 } }
      }
    },

    // Same-sensor (copy) fixture for every checkpoint. The experiment archive also
    // holds independent-wiring records for these models; this demo includes only
    // Aquila's independent-wiring record.
    family: [
      { id: "base", name: "Inkling 2 Mini (base)", training: "Base control", action: "buy", afterA: 800, afterAB: 800 },
      { id: "lyra", name: "Oracle Lyra", training: "Supervised", action: "stop", afterA: 667, afterAB: 889 },
      { id: "vega", name: "Oracle Vega", training: "Reinforcement (from Lyra)", action: "stop", afterA: 714, afterAB: 889 },
      { id: "aquila", name: "Oracle Aquila", training: "Supervised", action: "stop", afterA: 800, afterAB: 905 },
      { id: "altair", name: "Oracle Altair", training: "Reinforcement (from Aquila)", action: "stop", afterA: 667, afterAB: 800 },
      { id: "cygnus", name: "Oracle Cygnus", training: "Supervised", action: "stop", afterA: 727, afterAB: 941 },
      { id: "deneb", name: "Oracle Deneb", training: "Reinforcement (from Cygnus)", action: "stop", afterA: 800, afterAB: 941 }
    ]
  };
  if (typeof module === "object" && module.exports) module.exports = fixture;
  else (root.LaplaceOracle = root.LaplaceOracle || {}).fixture = fixture;
})(this);
