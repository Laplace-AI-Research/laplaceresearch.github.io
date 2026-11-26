(function () {
  "use strict";

  // 1. One-click copy for Hugging Face repo IDs
  document.querySelectorAll(".mc-repo[data-repo]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var repo = btn.getAttribute("data-repo");
      var act = btn.querySelector(".mc-repo-act");
      if (!repo) return;
      var done = function () {
        btn.classList.add("copied");
        if (act) act.textContent = "Copied";
        window.setTimeout(function () {
          btn.classList.remove("copied");
          if (act) act.textContent = "Copy";
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(repo).then(done).catch(done);
      } else {
        done();
      }
    });
  });

  // 2. Family filter pills
  var pills = Array.from(document.querySelectorAll(".fpill[data-filter]"));
  var blocks = Array.from(document.querySelectorAll(".fam-block[data-family]"));
  var rows = Array.from(document.querySelectorAll(".mmatrix tbody tr[data-family]"));

  function applyFilter(fam) {
    pills.forEach(function (p) {
      p.setAttribute("aria-pressed", String(p.getAttribute("data-filter") === fam));
    });
    blocks.forEach(function (b) {
      b.hidden = fam !== "all" && b.getAttribute("data-family") !== fam;
    });
    rows.forEach(function (r) {
      r.hidden = fam !== "all" && r.getAttribute("data-family") !== fam;
    });
  }

  pills.forEach(function (p) {
    p.addEventListener("click", function () {
      applyFilter(p.getAttribute("data-filter") || "all");
    });
  });

  // 3. Cards vs. Compare table view switch
  var vbtns = Array.from(document.querySelectorAll(".vbtn[data-view]"));
  var cardsWrap = document.getElementById("models-cards");
  var matrixWrap = document.getElementById("models-matrix");

  function applyView(view) {
    vbtns.forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-view") === view));
    });
    if (cardsWrap && matrixWrap) {
      cardsWrap.hidden = view === "table";
      matrixWrap.hidden = view !== "table";
    }
  }

  vbtns.forEach(function (b) {
    b.addEventListener("click", function () {
      applyView(b.getAttribute("data-view") || "cards");
    });
  });
})();
