/* Air & Ember — privacy-preserving click & event counter.
   Five events (FLG-007: canonical list pending owner confirmation):
     1. page_view            — fires once per page load
     2. outbound_product_click — fires on any sponsored product CTA
     3. guide_read           — fires after 10s or 50% scroll on guide pages
     4. disclosure_click     — fires when the disclosure link is followed
     5. suggestion_click     — fires when a suggestion decision link is used
   Privacy: no cookies, no identifiers, no third-party requests. Events are kept
   in this browser's localStorage only (capped). A same-origin endpoint can be
   enabled later (see Suggestions S-04) — it is OFF by default because static
   hosting has no backend. */
(function () {
  var KEY = "ae_events_v1";
  var CAP = 500;
  var ENDPOINT_OFF = true; // set false only when a same-origin /api/event exists

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY) || "[]"); }
    catch (e) { return []; }
  }
  function write(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list.slice(-CAP))); } catch (e) {}
  }
  function record(name, detail) {
    var list = read();
    list.push({
      e: name,
      t: new Date().toISOString(),
      p: location.pathname.replace(/^.*\/WinC/, "") || "/",
      d: detail || ""
    });
    write(list);
    if (!ENDPOINT_OFF && navigator.sendBeacon) {
      try { navigator.sendBeacon("/api/event", JSON.stringify(list[list.length - 1])); } catch (e) {}
    }
  }

  window.aeEvents = {
    record: record,
    list: read,
    clear: function () { try { localStorage.removeItem(KEY); } catch (e) {} },
    names: ["page_view", "outbound_product_click", "guide_read", "disclosure_click", "suggestion_click"]
  };

  document.addEventListener("DOMContentLoaded", function () {
    record("page_view");

    document.addEventListener("click", function (ev) {
      var el = ev.target.closest("[data-event]");
      if (!el) return;
      var kind = el.getAttribute("data-event");
      if (kind === "outbound_product_click") {
        record("outbound_product_click", el.getAttribute("data-product") || "");
      } else if (kind === "disclosure_click") {
        record("disclosure_click", el.getAttribute("href") || "");
      } else if (kind === "suggestion_click") {
        record("suggestion_click", el.getAttribute("data-suggestion") || "");
      }
    });

    // guide_read: 10 seconds on page or halfway down the article
    if (document.body.classList.contains("is-guide")) {
      var fired = false;
      var fire = function () {
        if (fired) return;
        fired = true;
        record("guide_read", document.title);
      };
      setTimeout(fire, 10000);
      window.addEventListener("scroll", function () {
        var h = document.documentElement;
        var pct = (h.scrollTop + h.clientHeight) / h.scrollHeight;
        if (pct >= 0.5) fire();
      }, { passive: true });
    }
  });
})();
