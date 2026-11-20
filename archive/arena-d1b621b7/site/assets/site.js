/* Kitchen Shortlist — site behavior (no dependencies) */
(function () {
  "use strict";

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Active nav link
  var here = location.pathname.replace(/index\.html$/, "");
  document.querySelectorAll(".nav a, .footer-nav a").forEach(function (a) {
    try {
      var target = new URL(a.href, location.origin).pathname.replace(/index\.html$/, "");
      if (target === here) a.setAttribute("aria-current", "page");
    } catch (e) { /* cross-origin: ignore */ }
  });

  // Year stamp
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  // Client-side search filter (guides / products / suggestions)
  var input = document.querySelector("[data-filter-input]");
  if (input) {
    var scope = document.querySelector(input.getAttribute("data-filter-input")) || document;
    var items = scope.querySelectorAll("[data-filter-item]");
    var count = document.querySelector("[data-filter-count]");
    var run = function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      items.forEach(function (el) {
        var hay = (el.getAttribute("data-filter-item") + " " + el.textContent).toLowerCase();
        var hit = !q || hay.indexOf(q) !== -1;
        el.hidden = !hit;
        if (hit) shown++;
      });
      if (count) {
        count.textContent = q
          ? shown + " of " + items.length + " match \u201c" + input.value.trim() + "\u201d"
          : items.length + " entries";
      }
      if (window.KitLog) window.KitLog("search_query", { q: q || "(cleared)", results: shown });
    };
    input.addEventListener("input", function () {
      clearTimeout(input._t);
      input._t = setTimeout(run, 220);
    });
  }

  // Suggestion status filter
  var toolbar = document.querySelector("[data-sg-toolbar]");
  if (toolbar) {
    toolbar.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-status]");
      if (!btn) return;
      toolbar.querySelectorAll("button").forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      var want = btn.getAttribute("data-status");
      document.querySelectorAll(".sg").forEach(function (card) {
        card.hidden = want !== "all" && card.getAttribute("data-status") !== want;
      });
    });
  }
})();
