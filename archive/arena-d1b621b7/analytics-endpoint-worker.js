/**
 * Kitchen Shortlist — self-hosted analytics endpoint (Cloudflare Worker variant)
 *
 * Privacy design:
 *   - Accepts only the five allowlisted events (mirrors docs/assets/analytics.js).
 *   - Never stores raw IP addresses, user agents beyond a coarse browser hint,
 *     cookies, or referer URLs (path-only referrer is already client-truncated).
 *   - Aggregates counts per day/event/path in Workers KV; no per-event rows
 *     with identifiers are persisted.
 *   - CORS is restricted to the site origin.
 *
 * Deploy (see README.md in this folder):
 *   1. wrangler kv:namespace create EVENTS
 *   2. set the namespace id in wrangler.toml
 *   3. wrangler deploy
 *   4. set window.SITE_ANALYTICS_ENDPOINT = "https://<worker>/e" in the site
 */

const ALLOWED = new Set([
  "page_view",
  "outbound_product_click",
  "guide_cta_click",
  "search_query",
  "subscribe_click"
]);

const ORIGINS = new Set([
  "https://sassnarep3-star.github.io",
  "http://localhost:8000"
]);

const MAX_STR = 200;

function cors(request) {
  const origin = request.headers.get("Origin") || "";
  if (!ORIGINS.has(origin)) return null;
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin"
  };
}

function clamp(s, n = MAX_STR) {
  return typeof s === "string" ? s.slice(0, n) : "";
}

function dayKey(d = new Date()) {
  return d.toISOString().slice(0, 10); // YYYY-MM-DD (UTC)
}

export default {
  async fetch(request, env) {
    const headers = cors(request);
    if (!headers) return new Response("forbidden", { status: 403 });
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers });

    const url = new URL(request.url);

    if (request.method === "POST" && url.pathname === "/e") {
      let ev;
      try {
        ev = await request.json();
      } catch {
        return new Response("bad json", { status: 400, headers });
      }
      if (!ev || !ALLOWED.has(ev.event)) {
        return new Response("unknown event", { status: 422, headers });
      }

      const day = dayKey();
      const detail = ev.detail || {};
      // aggregate only — no identifiers persisted
      const ops = [
        count(env.EVENTS, `d:${day}:${ev.event}`),
        count(env.EVENTS, `d:${day}:path:${clamp(String(ev.path || ""), 120)}`)
      ];
      if (ev.event === "outbound_product_click" && detail.href) {
        ops.push(count(env.EVENTS, `d:${day}:out:${clamp(String(detail.href), 160)}`));
      }
      if (ev.event === "search_query" && detail.q) {
        ops.push(count(env.EVENTS, `d:${day}:q:${clamp(String(detail.q).toLowerCase(), 80)}`));
      }
      await Promise.all(ops);

      return new Response(JSON.stringify({ ok: true }), {
        status: 202,
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    if (request.method === "GET" && url.pathname === "/stats") {
      const day = url.searchParams.get("day") || dayKey();
      const prefix = `d:${day}:`;
      const out = {};
      let cursor;
      do {
        const page = await env.EVENTS.list({ prefix, cursor });
        for (const k of page.keys) {
          out[k.name] = Number((await env.EVENTS.get(k.name)) || 0);
        }
        cursor = page.list_complete ? undefined : page.cursor;
      } while (cursor);
      return new Response(JSON.stringify({ day, counts: out }), {
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    return new Response("ok", { headers });
  }
};

async function count(kv, key) {
  const cur = Number((await kv.get(key)) || 0);
  await kv.put(key, String(cur + 1));
}
