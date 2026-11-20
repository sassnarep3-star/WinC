/* Kitchen Shortlist — privacy-preserving measurement
 *
 * Five defined events (FLG-009: taxonomy proposed here, pending owner approval):
 *   1. page_view             — a page was viewed
 *   2. outbound_product_click — reader clicked a sponsored product link
 *   3. guide_cta_click        — reader clicked a primary call-to-action button
 *   4. search_query           — reader ran the site search
 *   5. subscribe_click        — reader clicked an RSS / subscribe link
 *
 * Design:
 *   - No cookies. No third-party requests. No cross-site tracking.
 *   - Anonymous per-browser session id (random, stored locally, rotatable).
 *   - Events are always recorded locally (ring buffer) so the Measurement
 *     page can show them even before a server endpoint exists.
 *   - If window.SITE_ANALYTICS_ENDPOINT is configured, events are also
 *     POSTed (sendBeacon) to the self-hosted endpoint (see /analytics/).
 *   - Conversions/orders are deliberately NOT an on-site event: they arrive
 *     only from authorized Amazon Associates reports and are entered into
 *     the campaign ledger with a provenance link.
 */
(function () {
  "use strict";

  var ALLOWED = {
    page_view: 1,
    outbound_product_click: 1,
    guide_cta_click: 1,
    search_query: 1,
    subscribe_click: 1
  };
  var KEY = "ks_events_v1";
  var SKEY = "ks_session_v1";
  var MAX = 500;

  function session() {
    var s = null;
    try { s = localStorage.getItem(SKEY); } catch (e) {}
    if (!s) {
      s = "s-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
      try { localStorage.setItem(SKEY, s); } catch (e) {}
    }
    return s;
  }

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; }
  }

  function write(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list.slice(-MAX))); } catch (e) {}
  }

  function log(name, detail) {
    if (!ALLOWED[name]) return;
    var ev = {
      event: name,
      ts: new Date().toISOString(),
      session: session(),
      path: location.pathname,
      ref: document.referrer && document.referrer.indexOf(location.origin) !== 0 ? document.referrer.slice(0, 160) : "",
      detail: detail || {}
    };
    var list = read();
    list.push(ev);
    write(list);

    var endpoint = window.SITE_ANALYTICS_ENDPOINT;
    if (endpoint && navigator.sendBeacon) {
      try {
        navigator.sendBeacon(endpoint, JSON.stringify(ev));
      } catch (e) { /* offline / blocked: local copy remains */ }
    }
    document.dispatchEvent(new CustomEvent("ks:event", { detail: ev }));
    return ev;
  }

  window.KitLog = log;
  window.KitEvents = read;

  // page_view on load
  log("page_view", { title: document.title });

  // outbound product clicks
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a");
    if (!a) return;
    var href = a.href || "";
    if (a.classList.contains("js-outbound") || /amazon\.com\/dp\/|link\.amazon\//.test(href)) {
      log("outbound_product_click", {
        label: (a.textContent || "").trim().slice(0, 80),
        href: href.slice(0, 300)
      });
    } else if (a.classList.contains("js-cta")) {
      log("guide_cta_click", { label: (a.textContent || "").trim().slice(0, 80), href: href.slice(0, 200) });
    } else if (a.classList.contains("js-subscribe")) {
      log("subscribe_click", { href: href.slice(0, 200) });
    }
  }, true);
})();
