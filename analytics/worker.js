// ShopNow Kitchen — self-hosted analytics endpoint (Cloudflare Worker example).
// Privacy boundary: stores aggregate counts only; event properties have strict allow-lists.
// Never stores IP address, user agent, cookies, fingerprints, emails or search queries.
// Deploy with a KV namespace bound as COUNTS; set ALLOWED_ORIGIN to the publication origin.

const EVENTS = new Set([
  "page_view", "outbound_click", "guide_read", "reader_capture_submit", "search_submit"
]);
const PAGE_RE = /^[A-Za-z0-9._/-]{1,200}$/;
const ASIN_RE = /^[A-Za-z0-9]{10}$/;
const DEPTHS = new Set(["full", "90+", "50-89", "25-49", "0-24"]);

function corsHeaders(request, env) {
  const headers = { "Cache-Control": "no-store", "Vary": "Origin" };
  const origin = request.headers.get("Origin");
  if (origin && env.ALLOWED_ORIGIN && origin === env.ALLOWED_ORIGIN) {
    headers["Access-Control-Allow-Origin"] = env.ALLOWED_ORIGIN;
    headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS";
    headers["Access-Control-Allow-Headers"] = "Content-Type";
  }
  return headers;
}

function json(payload, status, headers) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json", ...headers }
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const headers = corsHeaders(request, env);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers });
    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "shopnow-kitchen-metrics" }, 200, headers);
    }
    if (request.method !== "POST" || url.pathname !== "/collect") {
      return new Response("not found", { status: 404, headers });
    }

    let body;
    try { body = await request.json(); } catch { return new Response("bad json", { status: 400, headers }); }
    if (!body || typeof body !== "object" || Array.isArray(body) || !EVENTS.has(body.event)) {
      return new Response("bad event", { status: 422, headers });
    }
    const page = typeof body.page === "string" ? body.page : "";
    if (!PAGE_RE.test(page) || page.includes("..")) {
      return new Response("bad page", { status: 422, headers });
    }

    // Construct a new object; never persist arbitrary client properties, ids, timestamps or email.
    const props = body.props && typeof body.props === "object" && !Array.isArray(body.props)
      ? body.props : {};
    const kept = {};
    if (body.event === "outbound_click" && typeof props.asin === "string" && ASIN_RE.test(props.asin)) {
      kept.asin = props.asin.toUpperCase();
    }
    if (body.event === "guide_read" && DEPTHS.has(props.depth)) kept.depth = props.depth;

    // Date is set by the server, not a client-provided field.
    const day = new Date().toISOString().slice(0, 10);
    const key = JSON.stringify([day, body.event, page, kept.asin || "", kept.depth || ""]);
    const previous = Number.parseInt((await env.COUNTS.get(key)) || "0", 10);
    await env.COUNTS.put(key, String(Number.isFinite(previous) ? previous + 1 : 1));
    return new Response("ok", { status: 202, headers });
  }
};
