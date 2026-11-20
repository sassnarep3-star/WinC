# Analytics endpoint (self-hosted)

The site (`docs/`) records five events **locally** by default. To aggregate
events across devices and browsers, deploy one of the endpoints here and set:

```html
<script>window.SITE_ANALYTICS_ENDPOINT = "https://your-endpoint/e";</script>
```

in the `<head>` of each page (replacing the `null` default).

## Why this exists

GitHub Pages is static — it cannot accept `POST`s. The measurement design
therefore ships as code + a one-line config switch, and stays in *local mode*
until a host is chosen (tracked as **FLG-006 / SG-12** on the site).

## The five events (FLG-009, pending owner approval)

| Event | Fired by |
|---|---|
| `page_view` | page load |
| `outbound_product_click` | click on a sponsored product link |
| `guide_cta_click` | click on a primary CTA |
| `search_query` | on-page search |
| `subscribe_click` | RSS / subscribe link |

Anything not in this allowlist is rejected by the endpoint (`422`).

## Variant A — Cloudflare Worker (recommended)

```bash
cd analytics
npx wrangler kv:namespace create EVENTS     # paste the id into wrangler.toml
npx wrangler deploy
```

- `POST /e` accepts an event JSON, increments day-scoped counters in KV.
- `GET /stats?day=YYYY-MM-DD` returns aggregate counts.
- No IPs, no cookies, no per-user rows are stored.

## Variant B — Python stdlib server

```bash
python3 server.py --port 8787 --root /var/lib/ks-analytics
```

- `POST /e` appends a minimal JSON line (event, path, anonymous session id,
  truncated detail — **no IP, no user agent, no raw referrer**).
- `GET /stats?day=YYYY-MM-DD` aggregates on read.
- Put it behind TLS (Caddy/nginx) and allow only the site origin.

## Privacy contract

1. No cookies; client session id is random and browser-local.
2. Endpoint never receives or stores raw IP addresses.
3. Only allowlisted event names are accepted.
4. CORS limited to the site origin.
5. The site's `privacy.html` must be updated **before** an endpoint goes live.

## Local mode (current)

Without an endpoint, events accumulate in `localStorage` (ring buffer, 500 max)
and render on `docs/measurement.html`. Nothing leaves the browser.
