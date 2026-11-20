// ShopNow Kitchen — self-hosted analytics endpoint (Cloudflare Worker example).
// Privacy-preserving: stores ONLY aggregate counts per (day, event, page, asin).
// Never stores: IP address, user agent, cookies, fingerprints, email addresses, or search queries.
// Deploy: `npx wrangler deploy analytics/worker.js` (or paste into Cloudflare dashboard),
// then set CONFIG.endpoint in assets/app.js to the Worker URL.
// Requires a KV namespace bound as COUNTS. No third-party dependencies.

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({ ok: true, service: "shopnow-kitchen-metrics" });
    }
    if (request.method !== "POST" || url.pathname !== "/collect") {
      return new Response("not found", { status: 404 });
    }
    let body;
    try { body = await request.json(); } catch { return new Response("bad json", { status: 400 }); }

    const ALLOWED = ["page_view", "outbound_click", "guide_read", "reader_capture_submit", "search_submit"];
    if (!ALLOWED.includes(body.event)) return new Response("bad event", { status: 400 });

    // Allow-list fields only. Anything else in the payload is dropped.
    const day = (body.at || new Date().toISOString()).slice(0, 10);
    const page = String(body.page || "").slice(0, 120);
    const asin = String((body.props && body.props.asin) || "").slice(0, 20);
    const key = `${day}:${body.event}:${page}:${asin}`;

    const prev = parseInt((await env.COUNTS.get(key)) || "0", 10);
    await env.COUNTS.put(key, String(prev + 1));
    return new Response("ok", { status: 200 });
  }
};
