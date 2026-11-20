# WinC — Kitchen Shortlist

A publication-grade Amazon Associates affiliate site built from an empty
repository: question-shaped buyer guides, a transparent product shortlist, a
line-by-line source register, and a compliance gate that runs on every push.

**Live site:** https://sassnarep3-star.github.io/WinC/
**Tracking ID:** `shopnow047c-20` (status: unverified — see FLG-004 on the site)

## Repository layout

| Path | Purpose |
|---|---|
| `docs/` | The published site (GitHub Pages source, `/docs` on `main`) |
| `docs/data/` | Machine-readable records: product-intent record, source register, campaign ledger |
| `scripts/check_site.py` | Compliance & integrity gate (disclosure, sponsored links, row sources, sitemap/RSS/link integrity) |
| `.github/workflows/site-checks.yml` | Runs the gate on every push and PR |
| `analytics/` | Self-hosted analytics endpoint code (Worker + Python), privacy contract |
| `COORDINATION.md` | Shared task board for parallel sessions — read before starting work |

## Site map (reader-facing vs dashboard)

- **Reader:** Home · Guides · The Shortlist · Suggestions · Before You Decide · Executive Summary
- **Footer → Dashboard:** Source register · Flagged for review · Measurement · Campaign ledger · Compliance · About · Privacy · Sitemap · RSS

## Verification rules (enforced by CI)

1. Every table row carries a source link, or is an explicit empty state.
2. Values that cannot be confirmed from an official source stay **blank** and
   are labelled unverified — never inferred.
3. Intended product identifiers and observed redirect targets are stored in
   **separate fields** and never merged.
4. The exact Associates statement appears above the fold (strip under
   masthead) and in the footer of every page.
5. All `link.amazon` product links carry `rel="sponsored nofollow noopener"`.

Run locally:

```bash
python3 scripts/check_site.py
```

## Key official sources (checked 2026-11-20)

- Amazon Associates Operating Agreement — https://affiliate-program.amazon.com/help/operating/agreement
- Amazon Associates Program Policies — https://affiliate-program.amazon.com/help/operating/policies
- eCFR 16 CFR Part 255 (FTC Endorsement Guides) — https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255
- FTC Endorsement Guides FAQ — https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- Amazon Ads ASIN definition (10 characters) — https://advertising.amazon.com/library/guides/targeting-with-sponsored-products

Full register with per-claim links: `docs/source-register.html`.
Open irregularities: `docs/flagged.html` (FLG-001…FLG-012).
