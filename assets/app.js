/* ShopNow Kitchen — privacy-preserving measurement (no cookies, no fingerprinting, no PII).
   Five defined events: page_view, outbound_click, guide_read, reader_capture_submit, search_submit.
   Events are sent to a self-hosted endpoint IF configured; otherwise counted locally only.
   Endpoint code: analytics/worker.js (deploy separately — GitHub Pages is static). */
(function(){
  "use strict";
  var CONFIG = {
    // Set this to your deployed endpoint URL, e.g. "https://metrics.example.com/collect"
    // Leave empty to run in local-only mode (counts stored in localStorage, never transmitted).
    endpoint: "",
    siteId: "shopnow-kitchen"
  };
  var EVENTS = ["page_view","outbound_click","guide_read","reader_capture_submit","search_submit"];

  function now(){ return new Date().toISOString(); }
  function page(){ return location.pathname.replace(/^\/WinC\//,"").replace(/^\//,"") || "index.html"; }
  function bucketScroll(){
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    if (max <= 0) return "full";
    var pct = Math.round((h.scrollTop / max) * 100);
    if (pct >= 90) return "90+";
    if (pct >= 50) return "50-89";
    if (pct >= 25) return "25-49";
    return "0-24";
  }
  function localCount(event, props){
    try{
      var key = "sk_counts";
      var data = JSON.parse(localStorage.getItem(key) || "{}");
      data[event] = (data[event] || 0) + 1;
      data._last = { event: event, at: now(), page: page(), props: props || {} };
      localStorage.setItem(key, JSON.stringify(data));
    }catch(e){ /* storage unavailable — ignore */ }
  }
  function send(event, props){
    if (EVENTS.indexOf(event) === -1) return;
    var payload = { site: CONFIG.siteId, event: event, page: page(), at: now(), props: props || {} };
    localCount(event, payload.props);
    if (!CONFIG.endpoint) return; // local-only mode
    try{
      var body = JSON.stringify(payload);
      if (navigator.sendBeacon){
        var blob = new Blob([body], { type: "application/json" });
        navigator.sendBeacon(CONFIG.endpoint, blob);
      } else {
        fetch(CONFIG.endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: body, keepalive: true }).catch(function(){});
      }
    }catch(e){ /* never break the page for measurement */ }
  }

  // 1) page_view — once per page load
  send("page_view", { referrerCategory: document.referrer ? "external" : "direct" });

  // 2) outbound_click — every sponsored product link (data-asin carries observed ASIN)
  document.addEventListener("click", function(e){
    var a = e.target && e.target.closest ? e.target.closest('a[data-event="outbound_click"]') : null;
    if (a) send("outbound_click", { asin: a.getAttribute("data-asin") || "", target: "amazon" });
  }, true);

  // 3) guide_read — fired once when a reader reaches 50%+ on a guide page
  var guideFired = false;
  function onScroll(){
    if (guideFired) return;
    if (document.body && document.body.getAttribute("data-page-type") === "guide" && bucketScroll() === "50-89" || bucketScroll() === "90+" || bucketScroll() === "full"){
      // only on guides
      if (document.body.getAttribute("data-page-type") === "guide"){
        guideFired = true;
        send("guide_read", { depth: bucketScroll() });
      }
    }
  }
  document.addEventListener("scroll", onScroll, { passive: true });

  // 4) reader_capture_submit — newsletter form.
  //    The address must never reach the URL, the history or the host's request log. The form
  //    itself carries no `name` attribute and novalidate is set, so even a browser with this
  //    script blocked has nothing to submit; here we stop the navigation and keep the value
  //    in the page. No address is transmitted, and no pixel or double-opt-in provider exists
  //    yet (see the open questions on questions.html).
  var form = document.getElementById("reader-capture");
  if (form){
    form.addEventListener("submit", function(e){
      if (e && e.preventDefault) e.preventDefault();
      if (form.reportValidity && !form.reportValidity()) return;
      send("reader_capture_submit", { form: "newsletter" });
    });
  }

  // 5) search_submit — internal search. The query itself is NOT sent to the measurement
  //    endpoint; only the fact that a search happened. The term does stay in the page address,
  //    because the results page reads it from there — so it is in the URL the browser asks for.
  //    The disclosure page says so. The navigation is deliberately NOT cancelled: the results
  //    are rendered on the next load, and sendBeacon survives that navigation.
  var sform = document.getElementById("site-search");
  if (sform){
    sform.addEventListener("submit", function(){
      send("search_submit", { form: "internal" });
    });
  }

  // Expose for debugging (counts only, no PII)
  window.ShopNowMeasure = { send: send, events: EVENTS, config: CONFIG };
})();
