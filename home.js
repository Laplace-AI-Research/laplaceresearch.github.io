/* Laplace Research — homepage results card and writing carousel.
   Results are held-out point estimates from the conviction repository
   (results/{E0_base,E2_sft,E3b_grpo_base,V2}/metrics.json, test_structural). */
(function () {
  "use strict";

  var data = {
    acc: {
      note: "Higher is better.",
      rows: [
        ["Conviction Vector", "GRPO", 0.644, "var(--s2)"],
        ["Conviction Anchor", "SFT", 0.58, "var(--s1)"],
        ["Conviction Meridian", "SFT → GRPO", 0.56, "var(--s3)"],
        ["Qwen3-1.7B base", "", 0.424, "var(--quiet)", true],
      ],
    },
    res: {
      note: "Higher is better: the share of forged records the model refused to adopt.",
      rows: [
        ["Conviction Meridian", "SFT → GRPO", 0.578, "var(--s3)"],
        ["Conviction Anchor", "SFT", 0.531, "var(--s1)"],
        ["Qwen3-1.7B base", "", 0.34, "var(--quiet)", true],
        ["Conviction Vector", "GRPO", 0.315, "var(--s2)"],
      ],
    },
    flip: {
      note: "Lower is better: how often social pressure alone flipped a correct answer.",
      rows: [
        ["Conviction Vector", "GRPO", 0.348, "var(--s2)"],
        ["Conviction Meridian", "SFT → GRPO", 0.375, "var(--s3)"],
        ["Conviction Anchor", "SFT", 0.389, "var(--s1)"],
        ["Qwen3-1.7B base", "", 0.536, "var(--quiet)", true],
      ],
    },
  };

  var list = document.getElementById("rows");
  var foot = document.getElementById("card-foot");
  var tabs = document.querySelectorAll(".tabs [data-metric]");
  var base = "Point estimates on the scripted structural split. Greedy decoding, thinking disabled. ";

  function render(key) {
    var d = data[key];
    list.textContent = "";
    d.rows.forEach(function (r, i) {
      var li = document.createElement("li");
      if (r[4]) li.className = "ref";
      li.style.setProperty("--c", r[3]);
      li.innerHTML =
        '<span class="rk">' + (i + 1) + '</span><span class="sw"></span>' +
        '<span class="nm"></span><span class="tr"><i></i></span>' +
        '<span class="vl">' + r[2].toFixed(3) + "</span>";
      var name = li.querySelector(".nm");
      name.textContent = r[0];
      if (r[1]) {
        var small = document.createElement("small");
        small.textContent = r[1];
        name.appendChild(small);
      }
      li.querySelector("i").style.setProperty("--v", 0);
      list.appendChild(li);
    });
    requestAnimationFrame(function () {
      list.querySelectorAll("i").forEach(function (bar, i) {
        bar.style.setProperty("--v", d.rows[i][2]);
      });
    });
    foot.textContent = base + d.note;
  }

  if (list && foot) {
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (t) {
          t.setAttribute("aria-selected", String(t === tab));
        });
        render(tab.dataset.metric);
      });
    });
    render("acc");
  }

  var carousel = document.getElementById("carousel");
  document.querySelectorAll(".arrows [data-dir]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (!carousel) return;
      var card = carousel.querySelector(".post");
      var step = card ? card.getBoundingClientRect().width + 12 : 312;
      carousel.scrollBy({ left: Number(button.dataset.dir) * step, behavior: "smooth" });
    });
  });
})();
