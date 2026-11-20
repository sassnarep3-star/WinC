# Executive summary — ShopNow Kitchen (WinC)

**Site:** https://sassnarep3-star.github.io/WinC/ · **Tracking ID (as supplied):** shopnow047c-20 · **Date:** 2026-11-20

ShopNow Kitchen is a publication front page for five Amazon products (3 air fryers, 2 meat thermometers).
It leads with products, answers buyer questions, and keeps verification one click away — not in the way.

## What is live

- **Shop:** front page + 2 category pages + 5 product pages, all with Sponsored buy buttons (`rel="sponsored"`) and disclosure above the fold.
- **Guides:** 6 question-shaped guides (basket vs. oven-style, capacity checklist, cleanup/counter-space, multi-function questions, instant-read vs. leave-in, holiday crowd cook).
- **Trust:** verification register (intent vs. observed kept separate), 28-source register, 27 flagged items, redirect re-observation log (five observations), compliance gate (`scripts/check_site.py`).
- **Measurement:** 5-event beacon + Worker code; empty campaign ledger; sitemap + RSS + internal search.

## Key facts (all sourced)

| Fact | Value | Source |
|------|-------|--------|
| Submitted links | 5 link.amazon short links (9-char tokens) | Verification §1 |
| Observed ASINs | B0CDY277D3 · B09B7SB46R · B08DKYBTPH · B0DHZTCNR5 · B0DZFD6R9Z | Verification §1–2, §4 |
| Intended ASINs | Blank (9-char tokens are not ASINs) | S05 (ASIN = 10 chars) |
| Redirect targets, re-observed 2026-11-20 | First three observations 5/5 identical (2026-11-17, twice 2026-11-20); a fourth run matched 1/5 — four tokens landed on the Amazon homepage (FLG-026, cause unresolved, links not claimed invalid per FLG-003) | S18, S27, `data/probes.json` |
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
- **Amazon policy pages were read in full, not via an indexed copy.** The Operating Agreement (§5
  disclosure, §1 Special Links), the Program Policies (price/availability display rule, Special Link
  tag requirement), and the Associates help pages were all fetched directly and anonymously on
  2026-11-20; the FTC Endorsement Guides page is likewise reachable and was read directly.
  `data/sources.json` records the direct read for each. An earlier pass over-marked these as
  "login-gated / indexed copy" and ftc.gov as "unreachable"; that is corrected rather than left
  silently wrong.

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

# Third pass — verification, decision support, and a shop-shaped front page (2026-11-20, session `arena-82d39deb`)

The brief for this pass was: make it read like a shop, make suggestions reviewable before anyone
implements them, and verify every row against an official source. Those three things are what
changed. Nothing else moved.

## 1 · Verification — a third live observation, and one row that was wrong

- **All five supplied links were resolved live again**, by a session that had never seen them.
  5/5 destinations identical to the 2026-11-17 mapping and to the second 2026-11-20 observation.
  Every response again carried `lv=shuf` + `plpRedirect=mhFallback` — a fallback route, so the
  mapping is a reproducible record of *where the link goes* and still no evidence of *what was
  meant*. `intended_asin`, `intended_listing_url`, `confirmation_date` and `intended_source` stay
  blank for all five. (S22, `data/probes.json`)
- **Every listing's product-details table and bullet copy was re-read** to check the recorded spec
  rows line by line. That found **one wrong row**: the 8-quart Chefman was recorded at 1700 W /
  120 V, which is the wattage printed on the *6-quart* Chefman listing. The live bullet reads
  "1000 Watts/120 Volts – RJ38-SQSS-8T". Corrected, and the earlier capture is kept beside it
  (`power_prior_capture`) so the change is visible rather than silent. (FLG-022)
- **Four listing-internal contradictions were confirmed live**, and are now published on the
  product pages instead of being smoothed over: the 8-Qt temperature (title "450°F Hi-Fry" vs.
  bullets "200–400°F", FLG-005), the Emeril accessory count (title "Six" vs. bullets "7", FLG-010),
  the Emeril preset count (title 24 vs. bullets 25, FLG-020) and the 6-Qt capacity unit (details
  table "6 liters" vs. title "6 quart", FLG-018).
- **Two buyer-relevant facts were found in the live pages**: the 8-Qt ASIN is a 6/8/9-quart size
  family (so the same link can land on a different size, FLG-023), and Amazon's own page states
  there is a newer model of that item (FLG-024).
- **Amazon's name strings vary for the same ASIN.** The live title for B08DKYBTPH reads
  "TurboFry® 4-in-1 with 450°F Hi-Fry"; the earlier capture read "TurboFry Touch …". Both are
  stored; the live one is displayed. (FLG-019)

Source register grew from 21 to 26 rows; flagged items from 14 to 21.

## 2 · Decision support — the reader now gets an answer, not just a table

- **`data/categories.json` → "Match to your situation"** on both category pages: 11 reader
  situations ("Two of you, most weeknights", "You cook in the air fryer specifically"). Each one
  names the **single listed spec that settles the case**, states what the listings say about it,
  and links the listing it came from. No profile ranks a product best, and the gate fails the
  build if a profile names a field that does not exist in `data/products.json`.
- **Product pages** gained three things: what to compare before you buy (already there, now above
  the specs), *where the listing disagrees with itself* (each contradiction with its flag id), and
  *what the listing claims, quoted as claims* (serving size, rotisserie and pizza limits stay the
  seller's words, FLG-021) — plus a three-question reader FAQ with FAQ schema.
- **Guides** gained a third FAQ each where they had two, so every guide answers at least three
  questions on the page itself.

## 3 · Reviewable suggestions and a visible topic pipeline

- **`direction.html`** now opens with a review table (ID · suggestion · area · effort · cost ·
  status · how we would know it worked) and a **recommended sequence**: *Do now* → *Decide next* →
  *Blocked* → *Already shipped*. Two statuses in the register were stale — SG-05 and SG-13 were
  marked `open` after the previous session had already shipped them — and are corrected, with the
  shipping session named. Six new suggestions were added (SG-15 … SG-20), including the one this
  pass exists to answer: **SG-16, "every category needs a decision shortcut that names its
  deciding spec"**.
- **`topics.html`** publishes the 12 queued topics with, for each one, the reader question, why it
  earns a page, what it would need, and **how the topic was chosen**. Every one of them says
  "editorial hypothesis" or names the verification finding that raised it. None claims popularity,
  search volume or demand, because no Search Console property exists yet. The gate refuses a topic
  that claims measured demand without naming the measurement source.
- **Questions register** grew from 16 to 21 rows: what success would even look like (Q-17),
  whether the catalogue stays at five products (Q-18), which source wins when a listing and a
  manufacturer page disagree (Q-19), seasonal or evergreen (Q-20), and who owns the reader list
  and its consent flow (Q-21).

## 4 · The machinery

The compliance gate now also checks the **registers as data**, not only the rendered HTML: every
suggestion needs its seven fields and a status from a known vocabulary; every question needs its
fields and an explicit (possibly empty) `answer` key; every category needs at least two profiles
whose deciding spec exists in the product data and whose source is a recorded listing; every topic
needs a stated provenance; products' listing notes must cite a flag that exists; the redirect log
and the product records must not drift apart; and the front page must not reintroduce process
furniture (a regression guard for the rebuild). `npm run verify` → **OK: 27 pages checked, 26
sitemap URLs, no violations.**

## What has to happen before any of this earns anything

1. Confirm the tracking ID and run one-link Associates tests (FLG-001, FLG-002, Q-01, Q-16).
2. Confirm intent for the five products with whoever supplied them (Q-02) — a redirect is not intent.
3. Deploy the metrics endpoint, then choose topics from measured queries (SG-07, SG-08).
4. Settle the spec conflicts on the manufacturer page, not on Amazon marketing copy (FLG-005,
   FLG-010, Q-05, Q-19).
5. Decide the audience, the marketplace and what "working" means (Q-10, Q-17, SG-20) — before more
   content is written, not after.

**No revenue forecast, no conversion score, no traffic projection.** The ledger stays empty until
authorised first-party reports arrive.

# Fourth verification pass & integration — 2026-11-20 (session `arena-9a3bb152`)

## What was re-read line by line (official sources, fetched live 2026-11-20)

| Ref | Source | Result |
|-----|--------|--------|
| S01 | Associates Operating Agreement | §5 sentence ("As an Amazon Associate I earn from qualifying purchases.") and §6 material-breach clause confirmed verbatim; stamped "Updated: October 15, 2025". |
| S02 | Associates Program Policies | Price/availability rule and the XXXXX-## tag rule confirmed verbatim; stamped "Updated: April 14, 2026". |
| S03 | FTC Endorsement Guides FAQ | All four quoted affiliate sentences confirmed verbatim ("clearly and conspicuously", "The closer the disclosure is to your recommendation, the better.", "buy now" inadequate, "Paid link" adequate). |
| S04 | Google — qualify outbound links | `rel="sponsored"` guidance confirmed; stamped "Last updated 2025-12-10 UTC". |
| S05 | Sell on Amazon — what is an ASIN | "unique 10-character alphanumeric code" and the `/dp/` URL rule confirmed verbatim. |
| S16/S17 | USDA FSIS | Temperature chart values confirmed verbatim (poultry 165°F; ground meats 160°F; steaks/chops/roasts 145°F + 3-min rest; uncooked ham 145°F + rest). |
| S09–S13 | The five observed listings | 5/5 stored titles equal the live listing `<title>` (minus Amazon's prefix/suffix); category breadcrumbs confirm 3 air fryers + 2 meat thermometers. |

## What was observed (fourth probe run)

All five supplied `link.amazon` tokens were re-resolved through the same reader. **1 of 5 matched
the recorded mapping** (B0f3GKalj → B0DZFD6R9Z, same `lv=shuf` + `plpRedirect=mhFallback` flags);
the other four (B04G1MEwY, B02NbDxp3, B00hJ57DV, B0c8moW59) landed on the Amazon homepage.
Cause unresolved — reader-side degradation and short-link behavior change cannot be separated
from this environment. Published as **FLG-026** with the action (browser re-check + enrolled
Associates one-link test, FLG-002). No link is claimed invalid (FLG-003); `observed_*` fields
still rest on the three earlier 5/5-matching observations (S14, S18, S22); `intended_*` stays blank.

## Register defects found and repaired (not left silently wrong)

1. **FLG-025 carried a duplicate of FLG-015** after an earlier conflict resolution, instead of the
   title-drift flag `COORDINATION.md` documents. Restored to the title-drift record (status
   `resolved 2026-11-20`, sources S09–S13); the duplicate content is dropped.
2. **Executive-summary table cited the wrong flag ids** after the earlier renumbering
   (wattage cited FLG-019 → actually FLG-022; contradictions cited FLG-015/FLG-017 → actually
   FLG-020/FLG-018; name-string cited FLG-016 → actually FLG-019; buyer facts cited
   FLG-020/FLG-021 → actually FLG-023/FLG-024). All references corrected in
   `scripts/build_site.py` and rebuilt pages.
3. **Stale "5/5 identical every time" claim** across the front-of-book copy: rewritten to state
   three matching observations plus the divergent fourth (FLG-026).

## Reader-path tone audit

Front page, both category pages, five product pages and six guides read as a shop/publication:
lead story, product cards with Sponsored labels, decision blocks, FAQ, seasonal framing. Audit
surfaces (verification, flags, questions, suggestions, measurement, executive summary) sit in one
nav group ("The Desk") and the footer, off the reader path. No ranking, price, or testing claim
appears anywhere on the reader path.

## Gate status

`python3 scripts/build_site.py && python3 scripts/check_site.py` → green after these edits
(`Built 27 pages, 26 sitemap URLs, 6 guides, 23 search rows.` / `OK: 27 pages checked, 26 sitemap URLs, no violations.`). Re-verified again after the integration merge.
