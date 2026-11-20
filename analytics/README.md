# Self-hosted analytics endpoint (not run on GitHub Pages)

GitHub Pages serves static files only — it cannot run a server endpoint. This folder
ships the endpoint code so it can be deployed separately (e.g. Cloudflare Worker + KV).

## What it records (five defined events)

| # | Event | When it fires | Stored (aggregates only) |
|---|-------|---------------|--------------------------|
| 1 | `page_view` | Once per page load | day + page count |
| 2 | `outbound_click` | Click on a sponsored Amazon link | day + page + observed ASIN count |
| 3 | `guide_read` | Reader reaches 50%+ on a guide | day + page + depth bucket |
| 4 | `reader_capture_submit` | Newsletter form submitted | day + page count (no email stored) |
| 5 | `search_submit` | Internal search submitted | day + page count (query NOT stored) |

## Privacy rules

- No cookies, no fingerprinting, no IP / user-agent storage, no email storage.
- The Worker allow-lists fields and drops everything else.
- Client (`assets/app.js`) runs in local-only mode until `CONFIG.endpoint` is set.

## Deploy

1. Create a KV namespace and bind it as `COUNTS`.
2. Deploy `worker.js`.
3. Set `endpoint` in `assets/app.js` to the Worker `/collect` URL.
4. Record the deploy date on the Measurement page and in `COORDINATION.md`.

Status: **code shipped, not yet deployed** — see FLG-007 on the Flagged for Review page.
