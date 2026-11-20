/* Crisp Report — reader-side interactions.
   Same-origin, no third-party requests, no cookies. Everything stored here stays in this browser. */
(function () {
  "use strict";
  var KEY = "crisp.desk.v1";

  function store(read, patch) {
    var cur = {};
    try { cur = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { cur = {}; }
    if (read && !patch) return cur;
    try {
      var next = Object.assign({}, cur, patch || {});
      if (patch && patch.__wipe) { localStorage.removeItem(KEY); return {}; }
      localStorage.setItem(KEY, JSON.stringify(next));
      return next;
    } catch (e) { return cur; }
  }

  /* ---------- ideas board: decision capture ---------- */
  function initDecisions() {
    var bar = document.getElementById("decide-bar");
    if (!bar) return;
    var saved = store(true);
    var count = 0;

    Array.prototype.forEach.call(document.querySelectorAll(".opt input[type=radio]"), function (inp) {
      var sg = inp.getAttribute("data-sg");
      if (saved[sg] && saved[sg].option === inp.value) inp.checked = true;
      inp.addEventListener("change", function () {
        var patch = {};
        patch[sg] = { option: inp.value, at: new Date().toISOString() };
        store(false, patch);
        refresh();
      });
    });

    function refresh() {
      var s = store(true);
      count = Object.keys(s).filter(function (k) { return s[k] && s[k].option; }).length;
      var el = document.getElementById("d-count");
      if (el) el.textContent = String(count);
    }
    refresh();

    var out = document.getElementById("export-out");
    bar.addEventListener("click", function (ev) {
      var b = ev.target.closest ? ev.target.closest("[data-act]") : null;
      if (!b) return;
      var act = b.getAttribute("data-act");
      if (act === "clear") {
        store(false, { __wipe: true });
        Array.prototype.forEach.call(document.querySelectorAll(".opt input"), function (i) { i.checked = false; });
        refresh();
        if (out) { out.hidden = false; out.textContent = "Local choices cleared. Nothing was sent anywhere — there is no endpoint."; }
        return;
      }
      if (act === "export") {
        var md = buildMarkdown();
        if (out) { out.hidden = false; out.textContent = md; }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(md).then(function () {
            b.textContent = "Copied — paste it into a build session";
            setTimeout(function () { b.textContent = "Export decisions as markdown"; }, 2600);
          }, function () { /* clipboard blocked; the text is on screen */ });
        }
      }
    });

    function buildMarkdown() {
      var s = store(true);
      var lines = ["# Decision sheet — Crisp Report ideas board", "",
        "Exported " + new Date().toISOString(), "",
        "Apply these, in this order, and leave every other row untouched.", ""];
      var ids = Object.keys(s).filter(function (k) { return s[k] && s[k].option; });
      if (!ids.length) {
        lines.push("_No options chosen yet. Pick one per card, then export again._");
        return lines.join("\n");
      }
      ids.sort().forEach(function (id) {
        var card = document.getElementById(id.toLowerCase());
        var title = card ? (card.querySelector("h2") || {}).textContent : id;
        lines.push("## " + id + " — " + (title || "").trim());
        lines.push("- Chosen option: " + s[id].option);
        lines.push("- Decision at: " + s[id].at);
        if (card) {
          var pre = card.querySelector(".prompt pre code");
          if (pre) lines.push("- Instruction: " + pre.textContent.trim());
        }
        lines.push("- Also required: set `decision` and `accepted_option` for this row in `data/suggestions.json`, then run `npm run verify` and commit both the data file and the regenerated HTML.", "");
      });
      lines.push("Note for the implementer: any product claim implied by these choices still needs a source id in `data/sources.json`. Do not fill a blank to make a table look finished.");
      return lines.join("\n");
    }
  }

  /* ---------- copy a build instruction ---------- */
  function initCopy() {
    document.addEventListener("click", function (ev) {
      var b = ev.target.closest ? ev.target.closest('[data-act="copy"]') : null;
      if (!b) return;
      var id = b.getAttribute("data-for");
      var card = document.getElementById(id.toLowerCase());
      var code = card && card.querySelector(".prompt pre code");
      if (!code) return;
      var txt = code.textContent.trim();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(txt).then(function () {
          b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy instruction"; }, 2000);
        }, function () { b.textContent = "Select and copy manually"; });
      } else { b.textContent = "Copy manually from the box above"; }
    });
  }

  /* ---------- table filter (the "simple dashboard" affordance) ---------- */
  function initFilters() {
    Array.prototype.forEach.call(document.querySelectorAll(".tablewrap"), function (wrap, idx) {
      var table = wrap.querySelector("table.grid-table");
      if (!table) return;
      var rows = table.querySelectorAll("tbody tr");
      if (rows.length < 4) return;
      var box = document.createElement("p");
      box.className = "filter";
      box.innerHTML = '<label for="f' + idx + '">Filter ' + rows.length + ' rows</label> <input id="f' + idx +
        '" type="search" placeholder="text, an id like SG-03, or a status" autocomplete="off">';
      wrap.parentNode.insertBefore(box, wrap);
      var input = box.querySelector("input");
      var msg = document.createElement("p");
      msg.className = "filter-msg"; msg.hidden = true; msg.textContent = "No rows match.";
      wrap.parentNode.insertBefore(msg, wrap.nextSibling);
      input.addEventListener("input", function () {
        var q = input.value.toLowerCase().trim();
        var shown = 0;
        Array.prototype.forEach.call(rows, function (tr) {
          var hit = !q || tr.textContent.toLowerCase().indexOf(q) > -1;
          tr.hidden = !hit;
          if (hit) shown++;
        });
        msg.hidden = shown !== 0;
      });
    });
  }

  /* ---------- keyboard: jump to first matching row on register pages ---------- */
  function initSlashFocus() {
    document.addEventListener("keydown", function (e) {
      if (e.key !== "/" || (e.target && /input|textarea/i.test(e.target.tagName))) return;
      var f = document.querySelector(".filter input");
      if (f) { e.preventDefault(); f.focus(); }
    });
  }

  function boot() { initDecisions(); initFilters(); initCopy(); initSlashFocus(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
