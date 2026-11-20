# Executive summary — ShopNow Kitchen (WinC)

**Site:** https://sassnarep3-star.github.io/WinC/ · **Tracking ID (as supplied):** shopnow047c-20 · **Date:** 2026-11-20

ShopNow Kitchen is a publication front page for five Amazon products (3 air fryers, 2 meat thermometers).
It leads with products, answers buyer questions, and keeps verification one click away — not in the way.

## What is live

- **Shop:** front page + 2 category pages + 5 product pages, all with Sponsored buy buttons (`rel="sponsored"`) and disclosure above the fold.
- **Guides:** 4 question-shaped guides (basket vs. oven-style, capacity checklist, cleanup/counter-space, multi-function questions).
- **Trust:** verification register (intent vs. observed kept separate), 15-source register, 8 flagged items, compliance gate (`scripts/check_site.py`).
- **Measurement:** 5-event beacon + Worker code; empty campaign ledger; sitemap + RSS + internal search.

## Key facts (all sourced)

| Fact | Value | Source |
|------|-------|--------|
| Submitted links | 5 link.amazon short links (9-char tokens) | Verification §1 |
| Observed ASINs | B0CDY277D3 · B09B7SB46R · B08DKYBTPH · B0DHZTCNR5 · B0DZFD6R9Z | Verification §1–2 |
| Intended ASINs | Blank (9-char tokens are not ASINs) | S05 (ASIN = 10 chars) |
| Prices / ratings | Blank by policy + volatility | S02 (FLG-006) |
| Tracking ID | shopnow047c-20 (as supplied; unconfirmed — FLG-001) | Flagged for Review |
| Site URL | https://sassnarep3-star.github.io/WinC/ | S08 |

## What happens next (needs review)

1. Confirm tracking ID + run one-link Associates tests (FLG-001, FLG-002).
2. Re-observe redirects + resolve FLG-004/FLG-005 spec conflicts.
3. Deploy analytics endpoint; submit sitemap to Search Console.
4. Pick a path on the Direction page before the next build.

**No revenue forecast, no conversion score.** The ledger is empty until first-party reports arrive.
