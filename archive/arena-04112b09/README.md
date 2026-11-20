# arena-04112b09 — alternate build, retired in favour of the published site

This is a complete second implementation of the same brief, kept as a **reference**, not as a live
surface. Its generated HTML is deliberately **not** in the tree: only the sources are.

## Why it is here instead of merged at the root

The session that produced it branched from `a6083c9c` (README only). While it worked, `main` advanced
through PRs #11, #16 and others into the published **ShopNow Kitchen** site, which owns the same paths:
root `index.html`, `feed.xml`, `sitemap.xml`, `robots.txt`, `404.html`, `data/products.json`,
`data/sources.json`, `data/flags.json`, `package.json`. A merge of the branch as it stood would have
**deleted 56 files of published work**.

So the merge resolution in `arena/04112b09-winc` keeps every published file and contributes only what
the live tree lacked: `tools/audit.mjs`, `tools/freshness.mjs`, `.github/workflows/ci.yml`, and this
archive. Nothing here is served as a page (the paths are not linked from the site), and `tools/audit.mjs`
skips `archive/` on purpose — an audit of the live site must not grade a retired draft.

## What the sources are

| Path | What it is |
|---|---|
| `tools/build.mjs`, `tools/lib.mjs` | whole-site generator: reads `site.config.json` + `data/*.json` + `content/guides/*.json`, writes one directory per page (`picks/index.html`, `guides/<slug>/index.html`, …), sitemap, headline-only RSS, `robots.txt`, JSON-LD, and `assets/js/config.js` so client state can never drift from the config |
| `tools/check.mjs` | 11-family compliance gate (G-01…G-15 + structure) that **refuses the build**; it is notable for one property: the required disclosure sentence is a literal inside the checker, not read from config, so editing the config cannot disable the check |
| `data/rules.json` | the 15 rules as data, each citing the clause it enforces |
| `data/product-intent.json` | the five supplied links with `intended_*` and `observed_redirect_target` in **separate** fields — the design the live register also uses |
| `data/events.json`, `data/editorial.json`, `data/ledger.csv` | five proposed analytics events (never-collected list included), the guide registry + cadence, and the empty campaign ledger with typed columns |
| `content/guides/*.json` | five block-structured buyer-method guides (`lead\|h2\|p\|ul\|check\|table\|callout\|quote\|unverified\|figure`), every block carrying its own provenance, no CTA |
| `site.config.json` | the brand "Crisp Report", issue number, disclosure strings, authorship gate, privacy defaults |
| `assets/` | the stylesheet, the two client scripts (table filter + local counters), and three illustrations |

## Where it was better, and where the published site is better

- **This build never linked an unconfirmed destination.** The five supplied `link.amazon/…` addresses are
  printed as copyable text, because at the time nothing behind them was observable. The published site
  resolved them to real listings (recorded in `../../data/probes.json`), so live buy buttons are correct
  *there* and were correct *here* only because less was known. Both designs are honest; the difference is
  evidence, not policy.
- **This build published no product facts at all** (no titles, no capacity, no dimensions) because none
  could be cited; the published site carries titles, brands, models, capacities and dimensions sourced to
  live listing re-reads. Its register is stronger.
- **The published site has search, a newsletter stub, six guides and per-product pages**; this build has
  none of those surfaces. On read-it-like-a-shop, the live site is further along.
- **The gate** here is broader (feed hygiene, verdict patterns, layout-shift, template leakage, secrets in
  published data, canonical↔sitemap agreement) and self-tested by injecting violations — which is why
  `tools/audit.mjs` now runs over the live tree as a second opinion rather than being discarded.

## Reproducing it (scratch, not into the site root)

```bash
mkdir -p /tmp/alt && cp -r archive/arena-04112b09/. /tmp/alt/ && cd /tmp/alt
node tools/build.mjs && node tools/check.mjs        # → "site is clean to publish."
```

It expects the layout it was written against (`data/`, `content/`, `site.config.json` as siblings), which
is why it lives in its own directory and not in the published tree.
