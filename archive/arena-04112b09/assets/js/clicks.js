/* Crisp Report — event layer.
   Five events, defined in data/events.json and mirrored by the generated assets/js/config.js.
   Default behaviour: count in this browser, send nothing. A POST happens only if the operator
   puts a URL in site.config.json -> measurement.endpoint and rebuilds.
   Deliberate absences: no preventDefault (an interstitial or redirect would disqualify the sale),
   no visitor id, no per-visitor sub-tag (barred by the program rules), no synthetic events. */
(function () {
  "use strict";
  var CFG = window.CRISP_MEASURE || { endpoint: null, events: [] };
  var KEY = "crisp.events.v1";
  var SESSION = "crisp.session.v1";

  function read(k, fb) { try { return JSON.parse(sessionStorage.getItem(k) || "null") || fb; } catch (e) { return fb; } }
  function write(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "null") || blank(); } catch (e) { return blank(); } }
  function save(s) { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} }
  function blank() {
    var t = {};
    (CFG.events.length ? CFG.events : ["page_view", "guide_open", "outbound_click", "product_intent_check", "editorial_decision"])
      .forEach(function (n) { t[n] = 0; });
    return { started: null, totals: t, targets: {}, pages: {}, bands: {} };
  }

  function send(payload) {
    if (!CFG.endpoint) return;                 // off by default: nothing leaves the device
    try {
      var body = JSON.stringify(payload);
      if (navigator.sendBeacon) { navigator.sendBeacon(CFG.endpoint, new Blob([body], { type: "application/json" })); return; }
      fetch(CFG.endpoint, { method: "POST", body: body, headers: { "content-type": "application/json" }, keepalive: true, mode: "no-cors", credentials: "omit" });
    } catch (e) { /* measurement must never break a reader's navigation */ }
  }

  function record(name, dims) {
    var s = load();
    if (!s.started) s.started = Date.now();
    s.totals[name] = (s.totals[name] || 0) + 1;
    var ev = { e: name, t: Math.floor(Date.now() / 1000), p: path() };
    for (var k in (dims || {})) if (dims[k] !== null && dims[k] !== undefined) ev[k] = dims[k];
    if (dims && dims.target) { s.targets[dims.target] = (s.targets[dims.target] || 0) + 1; }
    save(s);
    send(ev);
    paint();
    return ev;
  }

  function path() {
    var p = location.pathname;
    var i = p.indexOf("/WinC/");
    return i > -1 ? "." + p.slice(i + 6) : p;
  }
  var STORE = /(^|\.)amazon\.[a-z.]{2,}$|(^|\.)amzn\.to$/i;

  /* ---------- 1. page_view ---------- */
  var seen = read(SESSION, { views: 0 });
  seen.views += 1; write(SESSION, seen);
  record("page_view", { target: path() });
  var s0 = load(); s0.pages[path()] = (s0.pages[path()] || 0) + 1; save(s0);

  /* ---------- 2. guide_open ---------- */
  var body = document.querySelector(".art-body");
  var opened = false;
  function markOpen() {
    if (opened) return; opened = true;
    var entry = document.referrer && document.referrer.indexOf(location.host) > -1 ? "internal"
      : (document.referrer ? "search" : "direct");
    if (/\/feed\.xml|rss/i.test(location.search)) entry = "feed";
    record("guide_open", { target: path(), entry: entry });
  }
  if (body) {
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (en) { if (en.intersectionRatio >= 0.4) { markOpen(); io.disconnect(); } });
      }, { threshold: [0.4] });
      io.observe(body);
    }
    var bands = [25, 50, 75, 100], queued = false;
    var measure = function () {
      queued = false;
      var h = document.documentElement;
      var doc = h.scrollHeight - h.clientHeight;
      if (doc <= 0) return;
      var pct = Math.min(100, Math.round((h.scrollTop || document.body.scrollTop) / doc * 100));
      var top = bands.filter(function (b) { return pct >= b - 6; }).pop() || 0;
      var st = load();
      if (!st.bands[path()] || top > st.bands[path()]) { st.bands[path()] = top; save(st); }
      if (top >= 25) markOpen();
    };
    addEventListener("scroll", function () { if (!queued) { queued = true; requestAnimationFrame(measure); } }, { passive: true });
    measure();
  }

  /* ---------- 3. outbound_click ---------- */
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest ? ev.target.closest("a[href]") : null;
    if (!a) return;
    var host = "";
    try { host = new URL(a.href, location.href).hostname; } catch (e) { return; }
    if (!STORE.test(host)) return;
    if (!/^[a-z]+:$/.test(new URL(a.href, location.href).protocol)) return;
    var rel = (a.getAttribute("rel") || "").toLowerCase();
    var dims = {
      target: host,
      tag_present: /[?&]tag=/.test(a.href),
      rel_ok: /sponsored/.test(rel),
      row: a.getAttribute("data-product") || "none"
    };
    // Recorded, then the browser navigates. We never delay or reroute the reader.
    record("outbound_click", dims);
  }, true);

  /* ---------- 4. product_intent_check ---------- */
  if (/\/picks\/?$/.test(path())) {
    var unresolved = document.querySelectorAll(".s-unresolved").length;
    var shapeFails = document.querySelectorAll(".grid-table .fail").length;
    record("product_intent_check", { rows_unresolved: unresolved, shape_failures: shapeFails });
  }

  /* ---------- 5. editorial_decision ---------- */
  document.addEventListener("change", function (ev) {
    var r = ev.target;
    if (!r || r.type !== "radio" || !/^d-SG-/.test(r.name || "")) return;
    record("editorial_decision", { suggestion: r.getAttribute("data-sg"), choice: r.value });
  });

  /* ---------- local panel: only on the measurement page ---------- */
  function paint() {
    if (!/\/measurement\/?$/.test(path())) return;
    var mount = document.getElementById("local-counts");
    if (!mount) return;
    var s = load();
    var rows = Object.keys(s.totals).map(function (k) {
      return "<tr><td><code>" + k + "</code></td><td>" + s.totals[k] + "</td></tr>";
    }).join("");
    var tg = Object.keys(s.targets).filter(function (k) { return s.targets[k] > 0; }).slice(0, 8)
      .map(function (k) { return "<li><code>" + k.replace(/[</>]/g, "") + "</code> — " + s.targets[k] + "</li>"; }).join("");
    mount.innerHTML =
      '<h2>What this browser has recorded</h2>' +
      '<p class="dim small">Read from <code>localStorage</code> on this device. Nothing here has been transmitted' +
      (CFG.endpoint ? " — an endpoint is configured, so events were posted." : ", because no endpoint is configured.") +
      ' <button type="button" class="btn btn-c" id="clr">Clear them</button></p>' +
      '<table class="grid-table"><thead><tr><th>Event</th><th>Count on this device</th></tr></thead><tbody>' + rows + "</tbody></table>" +
      (tg ? '<p class="dim small">Targets this device tapped:</p><ul class="plain small">' + tg + "</ul>" : "");
    var b = document.getElementById("clr");
    if (b) b.addEventListener("click", function () { try { localStorage.removeItem(KEY); sessionStorage.removeItem(SESSION); } catch (e) {} location.reload(); });
  }
  function ensureMount() {
    if (!/\/measurement\/?$/.test(path())) return;
    var m = document.querySelector("main");
    if (!m || document.getElementById("local-counts")) return;
    var sec = document.createElement("section");
    sec.className = "band"; sec.id = "local-counts";
    m.appendChild(sec);
    paint();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ensureMount);
  else ensureMount();
})();
