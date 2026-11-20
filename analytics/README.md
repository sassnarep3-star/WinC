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

---

## `collect.py` — the one-command option (added 2026-11-20, session `arena-23d7ed19`)

`worker.js` is the edge deployment. If you would rather just run it somewhere you already have,
`analytics/collect.py` is the same contract with zero dependencies:

```bash
python3 analytics/collect.py --port 8080 --out /var/log/shopnow-events.jsonl \
        --origin https://sassnarep3-star.github.io
# then set CONFIG.endpoint in assets/app.js to https://HOST:8080/collect
```

Endpoints: `POST /collect` (only the five defined events), `GET /stats`, `GET /ledger`,
`GET /healthz`. Behaviour verified by test, not asserted: all five events → `202` and one JSON
line each; an out-of-set event (`purchase`) → `422`; malformed body → `400`; a `text/plain`
`sendBeacon` payload → accepted; `../` and CRLF in `page` → stored as `rejected`.
No IP logging (access log disabled), no cookies, no user-agent storage, no session stitching.

Honest limits: this counts **clicks and reads, not orders**. `/ledger` will never know a sale
happened. Order and revenue rows must be transcribed from Associates Central's own reports into
`data/campaign-ledger.json` with the export date, which is the only reason the ledger ships empty.
Run it behind TLS and keep the `--origin` pin on when it faces the public internet; this file is a
measurement tool, not a hardened service.

## How a measured number reaches the public site

The collector writes one JSON line per event to `events.jsonl` (gitignored, no IP, no cookie, no
user agent, five event names only). It never writes an order, because it cannot see one.

The only path from a figure to `data/campaign-ledger.json` — and therefore to `measurement.html` — is:

    python3 scripts/ledger_add.py --authorized \
        --timestamp 2026-12-05T00:00:00Z \
        --source "Associates Central > Reports > Earnings" \
        --channel "site:guides" --clicks 41 --orders 2 --sessions null \
        --provenance "earnings-2026-12-05.csv, exported by the owner on 2026-12-05"

It refuses rows without `--authorized`, rows whose fields are floats or derived values, rows whose
source or provenance contains an estimating word, and rows without a dated provenance string. The
`check_site.py` gate re-validates the file on every build. Until a first-party report exists the
ledger stays empty — that is the correct state, not an unfinished one.
