/* Air & Ember — UI behaviour: nav, filters, local metrics panel */
document.addEventListener("DOMContentLoaded", function () {
  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // "Review desk" dropdown
  var group = document.querySelector(".nav-group");
  var groupBtn = document.querySelector(".nav-group-toggle");
  if (group && groupBtn) {
    groupBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = group.classList.toggle("open");
      groupBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function () {
      group.classList.remove("open");
      groupBtn.setAttribute("aria-expanded", "false");
    });
  }

  // Current-page highlighting (works from any flat path)
  var here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".site-nav a, .nav-group-panel a").forEach(function (a) {
    var target = (a.getAttribute("href") || "").split("/").pop();
    if (target === here) a.setAttribute("aria-current", "page");
  });

  // Client-side filters (products, guides, flags) — data-filter="search text"
  var input = document.querySelector("[data-filter-input]");
  if (input) {
    var items = Array.prototype.slice.call(document.querySelectorAll("[data-filter-item]"));
    var empty = document.querySelector("[data-filter-empty]");
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      items.forEach(function (el) {
        var hay = (el.getAttribute("data-filter-item") || el.textContent).toLowerCase();
        var ok = !q || hay.indexOf(q) !== -1;
        el.style.display = ok ? "" : "none";
        if (ok) shown++;
      });
      if (empty) empty.style.display = shown ? "none" : "block";
    });
  }

  // Local metrics panel (verification page) — this browser only
  var panel = document.getElementById("local-metrics");
  if (panel && window.aeEvents) {
    var render = function () {
      var list = window.aeEvents.list();
      var counts = {};
      list.forEach(function (ev) { counts[ev.e] = (counts[ev.e] || 0) + 1; });
      var rows = window.aeEvents.names.map(function (n) {
        return "<tr><td class='mono'>" + n + "</td><td>" + (counts[n] || 0) + "</td></tr>";
      }).join("");
      panel.innerHTML =
        "<table><thead><tr><th>Event</th><th>Count in this browser</th></tr></thead><tbody>" +
        rows + "</tbody></table>" +
        "<p style='font-size:.82rem;color:#55524a'>Stored only in this browser's localStorage — " +
        list.length + " record(s), no cookies, no third-party requests. " +
        "<button class='btn btn-ghost' style='padding:6px 12px;font-size:.82rem' id='clear-metrics'>Clear local records</button></p>";
      var btn = document.getElementById("clear-metrics");
      if (btn) btn.addEventListener("click", function () { window.aeEvents.clear(); render(); });
    };
    render();
  }
});
