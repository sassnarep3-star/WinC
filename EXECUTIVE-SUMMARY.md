# Executive summary — ShopNow Kitchen (WinC)

**Site:** https://sassnarep3-star.github.io/WinC/ · **Tracking ID (as supplied):** shopnow047c-20 · **Date:** 2026-11-20

ShopNow Kitchen is a publication front page for five Amazon products (3 air fryers, 2 meat thermometers).
It leads with products, answers buyer questions, and keeps verification one click away — not in the way.

## What is live

- **Shop:** front page + 2 category pages + 5 product pages, all with Sponsored buy buttons (`rel="sponsored"`) and disclosure above the fold.
- **Guides:** 6 question-shaped guides (basket vs. oven-style, capacity checklist, cleanup/counter-space, multi-function questions, instant-read vs. leave-in, holiday crowd cook).
- **Trust:** verification register (intent vs. observed kept separate), 21-source register, 17 flagged items, redirect re-observation log, compliance gate (`scripts/check_site.py`).
- **Measurement:** 5-event beacon + Worker code; empty campaign ledger; sitemap + RSS + internal search.

## Key facts (all sourced)

| Fact | Value | Source |
|------|-------|--------|
| Submitted links | 5 link.amazon short links (9-char tokens) | Verification §1 |
| Observed ASINs | B0CDY277D3 · B09B7SB46R · B08DKYBTPH · B0DHZTCNR5 · B0DZFD6R9Z | Verification §1–2, §4 |
| Intended ASINs | Blank (9-char tokens are not ASINs) | S05 (ASIN = 10 chars) |
| Redirect targets, re-observed 2026-11-20 | 5/5 identical to 2026-11-17; every response carried `lv=shuf` + `plpRedirect=mhFallback` | S18, `data/probes.json` |
| Food-safety figures in the two new guides | Poultry 165°F; ground meats 160°F; steaks/chops/roasts 145°F + 3-min rest | S16, S17 (USDA FSIS) |
| Prices / ratings | Blank by policy + volatility | S02 (FLG-006) |
| Tracking ID | shopnow047c-20 (as supplied; unconfirmed — FLG-001) | Flagged for Review |
| Site URL | https://sassnarep3-star.github.io/WinC/ | S08 |

## What happens next (needs review)

1. Confirm tracking ID + run one-link Associates tests (FLG-001, FLG-002).
2. Re-observe redirects + resolve FLG-004/FLG-005 spec conflicts.
3. Deploy analytics endpoint; submit sitemap to Search Console.
4. Pick a path on the Direction page before the next build.

**No revenue forecast, no conversion score.** The ledger is empty until first-party reports arrive.

---

# Second-pass verification & publication polish — 2026-11-20 (session `arena-23d7ed19`)

This pass did not rebuild the site; it re-checked the merged one, fixed what was wrong, and added
the decision layer the brief asks for. Counts above were corrected to match the repo.

## What was verified

- **All five supplied links were re-resolved live, independently of the earlier sessions.** 5/5
  destinations matched the 2026-11-17 mapping (B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R,
  B00hJ57DV→B08DKYBTPH, B0c8moW59→B0DHZTCNR5, B0f3GKalj→B0DZFD6R9Z). This closes FLG-008.
- **The mechanism matters more than the match.** Every final URL carried `lv=shuf` and
  `plpRedirect=mhFallback` — Amazon's shuffle/listing-page fallback. The tokens are 9 characters
  with lowercase letters; Amazon ASINs are 10 characters. So the redirect is a reproducible record
  of *where a link goes*, and no evidence at all of *what was meant*. `intended_*` fields stay
  blank. Logged as FLG-009.
- **Two guides cited sources as bare text with no links** (capacity checklist, cleanup/counter
  space). Now linked, and the gate refuses an unlinked guide.
- **Login-gated Amazon pages are labelled as such.** The Operating Agreement and Program Policies
  text was taken from the indexed copy of the official page, not an authenticated read; sources.json
  now says so instead of implying a verified read.

## What changed on the site

- Meat Thermometers was advertised as a co-equal cluster with zero guides: **two new guides** added
  (instant-read vs. leave-in; holiday crowd cooking), grounded in USDA FSIS temperature guidance
  rather than adjectives.
- **Real imagery replaced the emoji glyphs** (four commissioned illustrations, every one captioned
  as an illustration; no Amazon product images, no logos), plus `og:image`/`twitter:card`, so a
  shared link is no longer a blank card.
- **Navigation labels now match destinations**: `guides/index.html` and `products/index.html` exist,
  and all nine dashboard surfaces sit in one "The Desk" group with a full footer repeat.
- Guides show **only their own cluster's products** (a meat-thermometer card used to close the
  air-fryer comparison).
- `About`/`Executive summary` counts are **computed from data**, read time is computed from word
  count (was a hardcoded "4 min read"), RSS dates are valid RFC-822 (they were not), and the
  capture block no longer promises a double opt-in flow that no code implements (FLG-013).
- `robots.txt` scopes `/scripts/`, `/data/`, `/analytics/`, `/archive/` out of the crawl set.

## Decision layer (the part meant to be reviewed, not read past)

- **`direction.html` — 14 suggestions**, each with problem, proposal, effort, cost, risk, *how we
  would know it worked*, evidence, and an instruction block for the next build prompt. Tick the
  ones you accept and the page assembles a copy-paste prompt carrying the standing rules
  (localStorage only; nothing is transmitted; nothing is auto-implemented).
- **`questions.html` — 16 open questions** (6 blocking) with what we have and can cite, what is
  missing, which decision the gap blocks, how to go find the answer, who can answer, and a blank
  answer cell. Includes a copy-ready pack for whoever owns the Associates account.

## Unchanged, on purpose

- No price, rating, review count, stock level, conversion score or revenue forecast anywhere.
- No testing, ranking or endorsement claim. No hands-on language: nobody has used these products.
- Short links are never called invalid; their status stays flagged (FLG-003) exactly as instructed.
- Reader buy buttons remain, but flagged as untested for destination and attribution (FLG-002).

## Remaining risk, stated plainly

Nothing in this repo can confirm the tracking ID is issued, that a hand-built `?tag=` link is an
approved link form for this account, or that these five listings are the five products that were
meant to be promoted (Q-01, Q-02, Q-16). Those need an enrolled Associates account. Until they are
answered, this is a well-sourced publication with a gated monetisation path — which is the correct
state to be in, not a half-finished one.


---

# Session `4ca9e665` — verification re-check, disclosure wording, close-out — 2026-11-20

- **Operating Agreement §5 re-fetched** from affiliate-program.amazon.com/help/operating/agreement: the required sentence "As an Amazon Associate I earn from qualifying purchases." matches the disclosure strip on every page.
- **FTC Endorsement Guides re-fetched.** ftc.gov is reachable now (the register said it was not). Its affiliate section says "a 'buy now' button would not be adequate" and that a "paid link" next to an affiliate link is adequate. The Amazon button tag said only "Sponsored", so it now reads "Sponsored · paid affiliate link" (FLG-017).
- **Pages:** build of `358dd0c` status `built`, no error. Gate: 26 pages, 25 sitemap URLs, no violations.
- **Not done, and still open:** tracking-ID confirmation, one-link Associates test, short-link status, FLG-004/005 spec conflicts, analytics deployment, Search Console. These need an enrolled Associates account or an owner decision.
