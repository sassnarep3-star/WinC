# Executive summary — ShopNow Kitchen (WinC)

**Site:** https://sassnarep3-star.github.io/WinC/ · **Tracking ID (as supplied):** shopnow047c-20 · **Date:** 2026-11-20
**Counts below are generated from the repo** (`python3 scripts/build_site.py && python3 scripts/check_site.py`), not typed. Source of the numbers: `data/*.json`.

---

## 1 · What this is

A five-product Amazon Associates publication in two categories — air fryers and meat thermometers — built so that **every published figure traces to an official page**, and anything that could not be confirmed is blank and flagged rather than guessed.

| Layer | State on this build |
|---|---|
| Products | 5 (3 air fryers, 2 meat thermometers), each with a long-form narrative, a spec table, an FAQ, and flagged listing contradictions |
| Series | 2 editorial series pages, generated from `data/stories.json` |
| Guides | 13 question-shaped guides across both categories, plus two series pages that tie each cluster together |
| Topics | 15 in the published backlog — 4 marked published with links to the guide each became |
| Sources | 35 register rows, each with URL, what it confirms, and a retrieval date |
| Flags | 29 items, each with the action that would resolve it; all public on *Flagged for review* |
| Open questions | 25, of which 8 are blocking; four of those can only be answered inside an enrolled Associates account |
| Suggestions | 33, each with evidence, effort, cost, risk, how to measure it, and a copy-paste prompt block |
| Measurement | 5 defined events; endpoint code (`analytics/worker.js`, `analytics/collect.py`) shipped and tested; **not deployed**; campaign ledger **empty** |
| Gates | `scripts/check_site.py` (authority) and `tools/audit.mjs` (independent, written from the policy documents) — **both pass with zero findings** |

## 2 · Key facts, each with its source

| Fact | Value | Source |
|---|---|---|
| Submitted links | 5 × `link.amazon` short links, 9-character tokens | Verification §1 |
| ASIN format | 10 alphanumeric characters | [sell.amazon.com — What is an ASIN](https://sell.amazon.com/blog/what-is-an-asin) (S05) |
| Observed destinations | B0CDY277D3 · B09B7SB46R · B08DKYBTPH · B0DHZTCNR5 · B0DZFD6R9Z — identical across four observations | `data/probes.json`, Verification §4 |
| Intended ASINs | **Blank for all five.** Nothing public binds a 9-char short code to a product; the redirect is a fallback route (`lv=shuf`, `plpRedirect=mhFallback`) | S05, FLG-003, FLG-009, FLG-029 |
| Listing titles | All five re-read live on 2026-11-20 and confirmed **verbatim** against the stored titles | S30–S34 |
| Disclosure sentence | “As an Amazon Associate I earn from qualifying purchases.” — §5, verbatim | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) (S01) |
| Price/availability display | Only via an Amazon-served link or Creators/PA API — so this site shows **no prices** | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) (S02) |
| Outbound link marking | `rel="sponsored"` + visible *Sponsored · paid affiliate link* label on every buy button | [Google: qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) (S04, S19) |
| Food-safety figures in the thermometer cluster | Poultry 165°F · ground meats 160°F · steaks/chops/roasts 145°F + 3-min rest · fish 145°F · leftovers 165°F | [USDA FSIS temperature chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) (S16), re-read verbatim 2026-11-20 |
| FAQ rich results | Google **removed** the FAQ rich-result feature in June 2026; FAQPage markup is kept for machine readability only | [Google Search Central changelog](https://developers.google.com/search/updates#removing-faq-rich-result) (S35) |
| Tracking ID | `shopnow047c-20` — well-formed, **issuance unconfirmed** | FLG-001, Q-01 |

## 3 · What changed in this session (arena-038c0b80)

1. **It reads like a shop now.** The front page leads with a publication headline, two series tiles, five product cards carrying a one-line hook and a source tail, then guides, then seasons, then categories. Every product page opens with an editorial narrative — headline, standfirst, deciding spec — before the spec table. A quiet house ad points at the newest guide on the front page, the shop index and every category page.
2. **Everything has a maker and a story.** New `data/makers.json` (4 makers, each with ≥2 checkable claims tied to a register source) and `data/stories.json` (5 product narratives + 2 cluster notes). Each narrative names the *one* stored spec it rests on, states the trade-off the spec creates, and prints the listing's own contradictions.
3. **Three new guides**, one of which is the missing shape-decision piece: *Two baskets or one?* (air fryers), *One second or all night* (thermometers, with the USDA table), and the cluster note that ties each series together. Two backlog topics are now marked published with links to what they became.
4. **A decision section exists.** `direction.html` now opens with a four-step decision desk: read the suggestions → answer what blocks you → pick one of four paths → copy the prompt. The four paths each carry cost, risk, and a “done when” that is a measurement, not a promise. `questions.html` gained a seven-row *before you publish anything else* checklist that a non-technical owner can work through.
5. **Three new suggestions and three new questions** from this session's own audit: duplicate site trees (SG-35/Q-23), name clearance (SG-36/Q-24), imagery licence (SG-37/Q-25) — plus TP-13, a topic chosen from a verification finding rather than a hunch.
6. **The imagery is 30× smaller.** Five 3.5–4 MB PNGs became six WebP files totalling ~0.5 MB; every reference (HTML, builder, guide data, templates) was updated and the gate verifies every asset resolves. Intrinsic `width`/`height` are set on every image so nothing shifts while loading.
7. **Two audit findings fixed at the source** (they had been open since before this session): the source-register anchors used single quotes so the independent audit could not resolve 60 cross-references (A6), and the reader-capture form would submit an address into a GET URL in a browser with JavaScript disabled while the page claimed otherwise (A7). The form is now `novalidate`, `action=""`, guarded, and the copy says the control is switched off on purpose.
8. **The gate got stricter.** `scripts/check_site.py` now fails on: an `SG-`/`Q-`/`FLG-` id cited anywhere in the HTML that does not exist in its register; a story with fewer than three paragraphs, an unknown flag, or a `spec_anchor` that is not a stored product field; a maker claim citing an unknown source; and a capture form without the transport guard.

## 4 · What is deliberately not claimed

- **No prices, ratings or review counts** anywhere. Both are barred by Program Policies and volatile by nature.
- **No testing.** Nothing in this shop has been cooked with, measured or opened by anyone writing about it. Every page says so.
- **No revenue, conversion, traffic or ranking forecast.** The ledger is empty because no first-party report exists (FLG-028).
- **No claim that the supplied short links are invalid.** Their compliance status is unresolved (FLG-003); they are simply not republished as link hops.
- **No claim that a section of the site "ranks".** Search Console is not set up and no analytics endpoint is deployed, so findability work is described as work done, never as results achieved.

## 5 · What has to happen before this earns anything

1. **Q-01 / FLG-002 — the money path.** Confirm the tracking ID and run one link through the enrolled Associates workflow per product. Everything else is decoration until a click can attribute.
2. **Q-23 / SG-35 — one site.** Three open pull requests each ship a different full website into this repo. Pick one tree, archive the rest.
3. **Q-24 / SG-36 — the name.** A trademark and domain search before more is invested in the current name.
4. **Q-25 / SG-37 — the imagery licence.** A dated record of commercial-use terms for the generated illustrations.
5. **FLG-007 / SG-07 — one measurement.** Deploy an endpoint, then choose the next topic from measured `outbound_click` and query data instead of instinct.
6. **FLG-029 — re-read every listing in a normal browser.** The sandbox only sees Amazon's fallback summary route; detail-table rows should be confirmed once by a human against the real page.

## 6 · Where to look

- Reader path: [front page](https://sassnarep3-star.github.io/WinC/) · [the shop](https://sassnarep3-star.github.io/WinC/products/index.html) · [guides](https://sassnarep3-star.github.io/WinC/guides/index.html) · [series](https://sassnarep3-star.github.io/WinC/series/countertop.html)
- Decision path: [suggestions + paths](https://sassnarep3-star.github.io/WinC/direction.html) · [open questions](https://sassnarep3-star.github.io/WinC/questions.html) · [topics](https://sassnarep3-star.github.io/WinC/topics.html)
- Evidence path: [verification](https://sassnarep3-star.github.io/WinC/verification.html) · [flagged for review](https://sassnarep3-star.github.io/WinC/flagged-for-review.html) · [measurement](https://sassnarep3-star.github.io/WinC/measurement.html) · [executive summary](https://sassnarep3-star.github.io/WinC/executive-summary.html)

---

## Appendix — earlier sessions (kept verbatim as provenance)

The records below are the repo's own history, kept so nobody re-litigates a settled point. Later sessions corrected earlier ones where the record was wrong; the corrections are noted inline where they occur.

### First pass (session 68dc5c3a / arena/a42979d2-winc)

Five supplied links recorded as 9-character tokens, resolved live, ASIN format checked against sell.amazon.com, Operating Agreement and Program Policies read, and a shop-first site built.

### Second pass (arena-23d7ed19)

Independent re-observation of all five links; closed FLG-008; added imagery, `og:` cards, cluster-filtered product blocks, RSS dates as RFC-822, computed read-times, robots scoping. Corrected two guides that cited sources as unlinked plain text, and the About page's typed cluster counts.

### Third pass (arena-82d39deb)

Added reader-situation profiles per category, per-product FAQs, the topic backlog page, suggestions v2, and a register-schema gate. Renumbered its own flags to FLG-018..024 when ids collided with a parallel session. Documented that every redirect still carried `lv=shuf` + `plpRedirect=mhFallback` (FLG-009).

### Integration passes (arena/0458cd24-winc, arena/c2123b9c-winc)

Corrected the register where earlier sessions had over-claimed (Amazon policy pages marked “login-gated, indexed copy” when they are publicly readable) and under-claimed (ftc.gov marked unreachable when it is reachable). Added `tools/audit.mjs` + `.github/workflows/ci.yml` and the seasonal band. Their audit found the A6 and A7 defects this session fixed.

### What every pass has held constant

<<<<<<< HEAD
No prices. No ratings. No testing claims. Intended and observed ASINs in separate fields. Short links never called invalid. Every table row that makes a claim carries a source link or an explicit “internal only” note.
=======
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
furniture (a regression guard for the rebuild). `npm run verify` → **OK: 29 pages checked, 28
sitemap URLs, no violations.** (8 guides, 24 search rows)

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


---

# Session `arena-c2123b9c` — observation #4, seasonal editorial, register back-fill — 2026-11-20

Merged on top of the third pass (`main@715b923`) after resolving a both-sides-edited rebase without
discarding either lineage. Tasks renumbered T29–T32 after an ID collision with arena-82d39deb's
T20–T28 claims (this session first claimed T22–T25, then T18–T21 on the previous rebase — both
renumbered; no other session's claim or work was touched).

- **Observation #4 (T29):** all five supplied links re-resolved live a fourth time; **5/5 mappings
  reproduce** again (S29, `data/probes.json`). New per-listing notes recorded verbatim: the Emeril
  title still says "Six Cooking Accessories" (FLG-010 stands on a third capture); the Chefman 8 Qt
  title still shows 450°F Hi-Fry against captured 200–400°F copy (FLG-005 stands); the ThermoMaven
  title wording rotated again (consistent with FLG-014); channel IDs varied (704/500). Every response
  still carries `lv=shuf` + `plpRedirect=mhFallback` — FLG-009 stands. Intended fields stay blank.
- **Dangling references found and fixed (T31):** the findability table on `measurement.html` rendered
  SG-27..SG-30 that were never registered in `data/suggestions.json`. Back-filled SG-27..SG-30 to
  match the rendered statuses exactly, then added SG-31..SG-34 — with SG-31 marked `shipped` because
  arena-82d39deb's comparison table already implements it, and SG-33 split into its shipped half
  (Article + BreadcrumbList by arena-82d39deb) and its open half (validator pass + copy audit after
  Google removed the FAQ rich result documentation in June 2026, S28). Q-22 (dead-listing runbook)
  added; my seasonal-windows question was dropped as a duplicate of Q-20, and reader-list questions
  point at Q-21. A reference audit now reports zero dangling S/FLG/SG/Q ids repo-wide.
- **New guides (T30):** "Reheating holiday leftovers in an air fryer" (USDA FSIS-sourced, S27,
  verbatim quotes: 2-hour rule, 3–4 days, 165°F reheat target, 40–140°F danger zone, rolling boil
  for liquids) and "How to read an air fryer listing" (listing literacy; blanks and the live listing
  conflicts used as teaching material). Front page gains a seasonal band computed from the guides
  register; `TODAY` in the builder is now overridable via `WINC_BUILD_DATE` (default unchanged).
- **New source evidence:** S27 (USDA FSIS Leftovers, fetched), S28 (Google updates — FAQ rich result
  docs removed, June 2026), S29 (observation #4 provenance).
- **Gate on the merged tree:** `OK: 29 pages checked, 28 sitemap URLs, no violations.` (8 guides,
  25 search rows). The stricter register-schema gate from the third pass passes unchanged.

---

# Session `arena/a81c0f0e-winc` — publication polish, catchy guides, final integration (2026-11-20)

This pass answers the user's explicit ask that the site read like a **polished marketing affiliate
publication** (not "AI slop"), carry **catchy trendy articles**, and keep a **reviewable suggestion
and question layer**. It re-verified everything from official sources first, then added publication
polish and published more question-shaped guides from the already-verified backlog. Nothing was
invented and no compliance rule was relaxed. It was rebased onto the advanced `main` (which already
carries a seasonal band from arena-c2123b9c), so this session's edits are additive on top: it did not
rewrite `home_body` — it added season badges on guide cards, a season lead on category pages, and an
explicit design directive to the build-prompt builder.

## Re-verified from official sources, live on 2026-11-20

- **Compliance backbone:** Amazon Associates Operating Agreement ("Updated: October 15, 2025"; §1
  Special Links "tagged" format; §5 disclosure), Program Policies ("Updated: April 14, 2026";
  price/availability display rule + Special Link tag requirement), FTC Endorsement Guides
  ("disclosed clearly and conspicuously"; links to 16 CFR Part 255), Google's `rel="sponsored"`
  guidance ("Last updated 2025-12-10"; "Mark links that are advertisements or paid placements … with
  the `sponsored` value"), and the ASIN definition (sell.amazon.com: "unique 10-character alphanumeric
  code", "appears after '/dp/'").
- **USDA FSIS:** Safe Minimum Internal Temperature Chart (poultry 165°F; ground meats 160°F;
  steaks/chops/roasts 145°F + 3-min rest) and Food Thermometers ("the only reliable way").
- **All five product listings** re-read live: every stored `<title>` and breadcrumb matched
  verbatim, confirming the three air fryers and two meat thermometers. The fallback summary page
  (`lv=shuf` + `plpRedirect=mhFallback`) matches the prior note. The ThermoMaven page showed a
  price in the live read; the site still leaves prices blank per Program Policies S02 — a deliberate
  compliance choice, unchanged.

## What this session added (additive on `main`)

- **Three new catchy, question-shaped guides** published from the verified topic backlog: *Your
  first air fryer: the six checks before you buy*, *Air fryer vs. convection oven: what actually
  changes?*, and *How much food actually fits in 6 quarts?*. Every numeric cell is a value read
  from the listed Amazon product; no price, rating, ranking or hands-on-test claim is made. These
  surface automatically on the front page and in the seasonal band because guides are loaded from
  `data/guides/*.json`.
- **Publication polish (additive):** a `season_pill` badge on every guide card, a guide count and
  season-framed lead on each category page, and an explicit **design directive** in the
  build-prompt builder so the suggestions feed a polished-marketing-publication build directly. The
  front-page seasonal band from the earlier pass is kept as-is.
- **Decision layer:** a new suggestion **SG-35** records the publication-polish pass.

## What still has to happen before this earns anything

1. Confirm the tracking ID and run one-link Associates tests (FLG-001, FLG-002, Q-01, Q-16).
2. Confirm intent for the five products with whoever supplied them (Q-02).
3. Deploy the metrics endpoint and submit the sitemap to Search Console, then choose topics from
   measured queries (SG-07, SG-08) — until then every topic is an editorial hypothesis, not a claim.
4. Settle the spec conflicts on the manufacturer page, not on Amazon marketing copy (FLG-005,
   FLG-010, Q-05, Q-19).
5. Decide the audience, the marketplace and what "working" means (Q-10, Q-17, SG-20).

**No revenue forecast, no conversion score, no traffic projection.** The ledger stays empty until
authorised first-party reports arrive.
>>>>>>> origin/main
