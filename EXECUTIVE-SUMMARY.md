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
| Guides | 15 question-shaped guides across both categories, plus two series pages that tie each cluster together |
| Topics | 18 in the published backlog — 4 marked published with links to the guide each became |
| Sources | 35 register rows, each with URL, what it confirms, and a retrieval date |
| Flags | 29 items, each with the action that would resolve it; all public on *Flagged for review* |
| Open questions | 25, of which 8 are blocking; four of those can only be answered inside an enrolled Associates account |
| Suggestions | 38, each with evidence, effort, cost, risk, how to measure it, and a copy-paste prompt block |
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

No prices. No ratings. No testing claims. Intended and observed ASINs in separate fields. Short links never called invalid. Every table row that makes a claim carries a source link or an explicit “internal only” note.

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

---

# Sixth observation and a shop-shaped front page (2026-11-20, session `f1fd0ff0`)

The brief for this pass had three parts: lead with the products, give the reader a decision to
make, and keep every number sourced. Three things changed on the site, and one row of data turned
out to be wrong in public.

## 1 · Verification, a sixth time — 5/5 titles verbatim, and two new findings

- **All five supplied links were re-resolved and all five listings re-read** on 2026-11-20. Two
  parallel sessions had already recorded observations #4 and #5 the same day; this is #6, and the
  register now holds six observations across two dates. 5/5 page `<title>` values match the stored product
  titles verbatim; the redirect responses still carry `lv=shuf` + `plpRedirect=mhFallback`. The
  Emeril page exposed its full details table, so dimensions (16.9" × 15.8" × 14.8"), capacity
  (24.6 litres), model `4-00675-02X-VN`, UPC `752356835682`, 1700 W and its own ASIN row were
  re-checked cell by cell against `data/products.json` — all match, and the same page repeats the
  six-versus-seven accessories contradiction (FLG-010) in `Configuration` vs `Item Highlight`.
- **FLG-026 (new):** two of five resolved URLs carried a variant parameter (`th=1`), and Amazon's
  own rails showed sibling listings for three products (Chefman 6 Qt dual basket `B0B7C327LK`,
  ThermoMaven Orange `B0GL7Z4KP4`, CHEF iQ Sense `B0DZFNQXGL`). A stable destination still does not
  pin the variant a reader is served, so no product page here claims a colour, size or bundle.
- **FLG-027 (new):** prices, star ratings and “Black Friday Deal” badges were visible during the
  reads and were not copied (Program Policies, S02). The consequence is stated as an open decision
  (SG-27 / Q-23), not left as a silent gap.
- **One reader-facing value was wrong in public:** the Chefman 8 Qt `temperature` and `model`
  fields carried “— see FLG-005” inside the *value*, so a shopper copying the number copied our
  bookkeeping with it. The fields are now clean (`200-400°F`, `RJ38-SQSS-8T`) and the disagreement
  lives where it belongs — the product page's “Where the listing disagrees with itself” block and
  the Flagged page. The gate now fails any spec value that carries a flag id.

## 2 · The shop, rebuilt so it reads like one

- Cards no longer print Amazon's keyword-stuffed title as body copy. Each carries a short editorial
  line written only from that product's own sourced fields, with the verbatim listing title moved
  to the product page under “What the listing itself says, verbatim”.
- One commissioned illustration per product, so no two cards share artwork, and product artwork doubles as each
  page's `og:image`. Every picture is captioned as a commissioned illustration that does not show the exact unit,
  and each file is served through the site's `<picture>` pipeline (a compressed PNG with a WebP twin) instead of the
  multi-megabyte originals the repo had started to accumulate.
- The front page leads with the products and a one-screen at-a-glance table (form, capacity,
  footprint, weight, what the listing sets it up for, source link per row), followed by the guides.
  Register counts no longer appear as a feature of the landing page; the dashboard pages are one
  navigation group plus the footer, as the brief asks.
- A dated seasonal strip points at the holiday guides, beside the season bands and the series rail the shop already runs. It states its year in its own text, because
  an undated seasonal promise is how a site ends up looking stale in public.

## 3 · Guides and backlog: four rows closed by this pass

`29` sources · `27` flags · `24` questions (5 blocking) ·
`30` suggestions (19 shipped, 10 open, 1 recommended now) · `13` topics (4 published).

Two guides were written this pass, each from sources already readable (a third, on turkey probe
placement, was drafted and then deleted because a parallel session published `guides/turkey-probe-placement.html` on the same question —
two near-identical articles is exactly the failure mode this site is trying to avoid):
**probe-accuracy-check** and **counter-fit-before-you-order** —
thermometer accuracy (USDA FSIS ice-water and boiling-water calibration methods, the 2–4°F
expectation, which types cannot be adjusted), probe placement for a holiday bird (three places in a
whole bird, 165°F, stuffing, the leave-in rule), and counter fit (the listed footprints and weights,
with ventilation clearance explicitly refused because no listing states one).

Build and gate at the close of this reconciliation are quoted in the final block of this section, after the three
merges with `main` — the site ends the day at 40 pages and 17 guides with the gate green.

## What still cannot be answered from this repo

Nothing changed about the four blockers: the tracking ID's issuance (FLG-001), the one-link
Associates test (FLG-002), the compliance status of the supplied short links (FLG-003), and the
specification conflicts inside two listings (FLG-004, FLG-005, FLG-010). All of them need an enrolled
Associates account or the owner's decision, and all of them are published on the Flagged page with
the action that settles each. No price, rating, ranking or revenue figure appears anywhere, and the
ledger stays empty until first-party reports arrive.

### Reconciliation with the parallel passes that landed mid-session

`main` absorbed two other sessions while this pass was in flight (PRs #38 and #41: their own fourth-pass verification, per-product artwork,
a computed season kicker, and the `turkey-probe-placement` + `black-friday-air-fryer-checklist` guides). Both merges were resolved by union,
main's rows keeping every colliding id, this session's rows renumbered (SG-39…SG-47, Q-24…Q-26, S30…S32, TP-15, FLG-026/027), this session's
re-read recorded as observation #6 rather than overwriting #4 or #5, and this session's duplicate holiday guide deleted. The five product
illustrations now resolve to this session's ~150 KB JPEGs and the 2.7–2.9 MB PNGs are gone. Full collision table in `COORDINATION.md`.

### Reconciliation with the parallel sessions that landed the same day

`main` absorbed three more passes while this one was being merged (PRs #17/#18 by their owners, then #37–#41 and #43–#45).
This session's contribution was merged into that tree by union, three times over, with these decisions:

- **Renderer:** `main`'s narrative/series/WebP builder was adopted; this session's front-page additions were grafted on
  top of it (an at-a-glance comparison table, a dated seasonal strip, an editorial card line that takes precedence over
  a scraped listing title) rather than replacing it. A shop gets one front page.
- **Duplicate guide deleted, not doubled:** this session drafted a turkey probe-placement guide, found
  `guides/turkey-probe-placement.html` already published by a parallel session, and removed its own. Two near-identical
  articles on one question is the slop behaviour the brief asks to avoid, so the backlog rows TP-06/TP-09 point at the page
  that exists.
- **Sixth observation:** `data/probes.json` now carries observations #1–#6 across 2026-11-17 and 2026-11-20 (four separate
  sessions). 5/5 tokens → 5/5 ASINs reproduced every time; observation #6 additionally compared each listing's `<title>`
  byte-for-byte with this register (5/5 verbatim) and re-checked the Emeril details table cell by cell. Nothing overwritten.
- **Id discipline:** where ids collided, `main`'s row kept the id and this session's rows were renumbered
  (S36–S38, FLG-030/031, SG-39…SG-47, Q-26…Q-28, TP-16), with cross-references fixed so no register row cites an id that
  now means something else. Four suggestion rows and one question row that a first-pass collision rule had silently dropped
  were restored, so the register matches the work actually done.
- **Imagery:** the PNG+WebP `<picture>` pair pipeline is kept; this session's JPEG conversions and their orphaned
  leftovers were deleted, and `data/products.json` carries one artwork reference per product instead of two competing sets.
- **Findings published rather than blocked:** FLG-030 (a `th=1` variant parameter on two of five resolved URLs, so a stable
  ASIN still does not pin the colour/size/bundle served) and FLG-031 (deal season arrives and the no-price stance is still
  an undecided editorial position, not a stated one), with SG-44/SG-45 and Q-26/Q-28 as the decisions the owner has to make.
- **Real defect found and fixed in public:** two Chefman 8 Qt spec values carried “— see FLG-005” inside the value a reader
  would copy. Values cleaned; the note lives on the product page and the Flagged page; the gate now fails that pattern, and
  also fails a seasonal strip with no year in it.

Standing rules for the next session, unchanged: prices, ratings, review counts and deal badges are never copied;
`intended_*` and `observed_*` stay separate; nothing is claimed about testing; the tracking ID (FLG-001), the one-link
Associates test (FLG-002) and the short-link status (FLG-003) still require the enrolled account, and the campaign ledger
stays empty until an authorized first-party report is filed with provenance.


---

### Fourth merge of `main` the same day (PR #48, session `arena-156c2ecf`) — id discipline a third time, and one source row deleted rather than duplicated

Their pass rewrote `data/sources.json`, `data/suggestions.json` and `data/topics.json` wholesale while this branch was being
reconciled. Resolution:

- **A duplicate source row was dropped, not merged.** This session had registered its own per-listing read rows; their S32/S33/S34
  are the same two listings read on the same date. Mine were deleted and every reference repointed at their rows, so the register
  carries one line per listing read. The only row this session added is S36, the sixth redirect observation, which their register
  did not have.
- **Suggestions renumbered again:** their SG-39…SG-42 keep the ids; this session's nine rows moved to SG-43…SG-51. Nine rows are
  real work records (card copy, artwork, glance table, bookkeeping out of reader copy, backlog closure, the price stance, the
  variant pin, the measurement-gated topics, print styles) — restoring them after an earlier collision rule silently dropped four
  of them, and re-dropping them now would lose the record again.
- **Topics:** their 18-row backlog was kept as the base; TP-06/TP-09 were flipped to their `turkey-probe-placement` page and
  TP-08 to the accuracy guide, and this session's counter-fit row was appended as **TP-19** (TP-15…TP-18 were already taken).
- **Their prose-count and dated-source-stamp rules (SG-39…SG-42) are honoured by this merge:** every source row this session
  touches carries its read date, and no count in the docs was typed — the reconciliation blocks below state the build numbers as
  the build printed them.
- Nothing else of mine survived as a duplicate: the stylesheet and the builder are main's, plus the two grafted blocks and the two
  grafted gate rules; my product JPEGs and my duplicate holiday guide stayed deleted.

`Built 40 pages, 39 sitemap URLs, 17 guides, 34 search rows.` → `OK: 40 pages checked, 39 sitemap URLs, no violations.` ·
`npm run verify` green (gate + `scripts/test_analytics.py` + `analytics/test_worker.mjs`).

### Fifth merge of `main` the same day (PR #49, session `arena/1c6908d1-winc`) — and a contradiction between observations, recorded rather than resolved

This pass merged with `-X theirs` (main wins every conflicting hunk), then re-registered this session's rows at free ids
rather than reusing taken ones. Outcome, in the order it matters:

- **What main's side kept:** its renderer, stylesheet, registers and its own new rows (S36, SG-43/SG-44, FLG-030, Q-26).
  This branch's topics flips (TP-06/TP-08/TP-09 → published pages), `sixth_observation` + `probe6_note`, the two new guides,
  `card_copy`, the glance table, the dated seasonal strip and the two gate rules all survived the merge — verified after it,
  not assumed.
- **What this session re-added at free ids:** sources S37 (the sixth observation) and the S17 calibration/care/types passages;
  flags FLG-031 (the undecided no-price stance), FLG-032 (the `th=1` variant parameter) and FLG-033 (below); questions
  Q-27/Q-28/Q-29; suggestions SG-45…SG-53 (nine records of the shop pass, with their cross-references repointed to the ids
  main actually uses, so no row cites an id that now means something else). SG-36/SG-37/SG-38/SG-43 are cross-referenced
  instead of duplicated, and the artwork row was rewritten to describe main's PNG+WebP pipeline rather than the JPEG set this
  session first drafted.
- **A real disagreement between observations, published:** FLG-030 records that `arena/1c6908d1`'s fetch path did *not*
  reproduce the five-token → five-ASIN mapping. Six observations by four sessions (2026-11-17 and five on 2026-11-20) map all
  five tokens to the same five ASINs every time, with the page titles matching verbatim. Neither side is overwritten: **FLG-033**
  states that the discrepancy is about the fetch path, not about the links, and sets the action that settles it — FLG-002's
  one-link test inside the enrolled Associates workflow, which is the only route that determines what a reader actually receives.
  The supplied short links are still not called invalid (FLG-003 unchanged).
- Duplication avoided rather than litigated: the two per-listing source rows this session had registered were dropped in favour
  of main's S32/S33/S34 (same listings, same date), and the duplicate holiday guide stayed deleted.

`Built 40 pages, 39 sitemap URLs, 17 guides, 34 search rows.` → `OK: 40 pages checked, 39 sitemap URLs, no violations.` ·
`npm run verify` green.

---

# Session `arena-156c2ecf` — line-by-line re-verification, decision-register completion — 2026-11-20

This pass re-verified the load-bearing claims against their official sources where the reader could
reach them, recorded the one fetch that failed instead of papering over it, added the seasonal
topic rows and the register rows this session owns, reconciled typed counts, and resolved two
rebases against the parallel PR rounds without dropping anyone's work.

## Re-verification this session (official sources, links for manual review)

| Ref | Source (manual review link) | Re-read result, 2026-11-20 |
|-----|------------------------------|-----------------------------|
| S01 | [Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | §5 disclosure sentence verbatim; §1 tagged Special Links; §6 §5-violation = material breach; stamp "Updated: October 15, 2025". **Confirmed live.** |
| S02 | [Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | Price/availability rule verbatim ((a) Amazon-served link or (b) Creators/PA API only); tag format "(appearing as XXXXX-##)"; stamp "Updated: April 14, 2026". **Confirmed live.** |
| S03 | [FTC Endorsement Guides FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) | "disclosed clearly and conspicuously"; affiliate section present. **Confirmed live.** |
| S05 | [What is an ASIN?](https://sell.amazon.com/blog/what-is-an-asin) | "unique 10-character alphanumeric code"; found after /dp/. **Confirmed live** — the 9-character submitted tokens cannot be ASINs, so `intended_asin` stays blank. |
| S09 | [Amazon listing B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) | `<title>` matched the stored product title verbatim; breadcrumb confirmed; `lv=shuf` + `plpRedirect=mhFallback` fallback observed again. **Identity confirmed live.** |
| S16/S17 | USDA FSIS pages | **Re-fetch FAILED in this session's reader (two attempts).** Not re-confirmed here; they stand on prior sessions' direct reads. Re-check before any new guide quotes them. |

## What changed

- **Suggestion register: SG-39..SG-42 added** (house-style/slop gate as a shipped standard, counts
  honesty, the dated re-read trail with recorded failures, and the next seasonal-publishing
  proposal). SG-27..SG-30 kept as the parallel pass wrote them — they are the rows the brief names.
- **Seasonal topic rows TP-16..TP-18** (Thanksgiving sizing, game-day timing, New Year counter
  space): catchy, question-shaped, each labelled "editorial hypothesis" in `chosen_from` — no
  popularity or search-volume claim, exactly as the topics page demands.
- **Typed counts reconciled** (SG-40): the state table above now matches the registers (15 guides,
  18 topics, 38 suggestions, 35 sources, 29 flags).
- **Rebase unions:** the PRs #37–#39 and #40–#45 rounds both conflicted with this branch; both
  sides kept every time (registers unioned, colliding IDs renumbered — T29–T32 became T39–T42,
  this session's topics moved to TP-16..TP-18 — HTML rebuilt from the merged data). Details in
  COORDINATION.md.

## Unchanged, on purpose

No price, rating, review count, revenue forecast or conversion score anywhere. Short links are
never called invalid (FLG-003). Intended vs observed identifiers stay in separate fields. The
campaign ledger stays empty until first-party reports exist.

---

# Audit-clean pass + verification #5 (2026-11-20, session `arena/1c6908d1-winc`)

This pass confirmed the independent-audit findings are cleared on `main`, re-ran the product
verification line by line, and added review-prompt suggestions distinct from the site's existing work.

## The independent audit is clean

`tools/audit.mjs` reports **0 findings** (all ten rules pass) on the merged tree. A6 (the `#src-*`
fragment links resolve — `main` fixed the source-row id quote style and rewrote the client-side search
with the DOM API) and A7 (the reader-capture form no longer puts the email in the URL — this session
upgraded it to `method="post"`, more robust than `get`+`novalidate` for a JavaScript-blocked browser)
are both addressed. `npm run verify` → **Built 38 pages, 37 sitemap URLs** / **OK: 38 pages checked,
37 sitemap URLs, no violations.**

## Verification pass #5, and one new irregularity

- **All five `amazon.com/dp/<ASIN>` listings re-read live on 2026-11-20.** Each `<title>` matched
  `data/products.json` verbatim; breadcrumb confirms category (3 air fryers, 2 meat thermometers). The
  `lv=shuf` + `plpRedirect=mhFallback` fallback route is present on all five (FLG-009/FLG-029). No spec
  value drifted; no correction needed.
- **New irregularity — FLG-030.** Re-fetching the five supplied `link.amazon` tokens directly did **not**
  reproduce the prior token→ASIN mapping via this fetch path: 4/5 resolved to the amazon.com homepage and
  `B0f3GKalj` returned HTTP 500 on two attempts. This does **not** establish the links are invalid
  (FLG-003 unchanged — never claimed invalid); it means the mapping's reproducibility across observation
  methods is in question. Recorded as source **S36**, flag **FLG-030**, and open question **Q-26**, with
  the resolution action (re-resolve in an enrolled Associates browser with cookies + region).

## New review-prompt suggestions (distinct from the site's existing suggestions)

- **SG-43 — editorial voice pass.** Make reader copy read like a publication, not generated text, without
  touching a single fact or source. Directly answers the brief's "should not read like AI slop."
- **SG-44 — accept/reject/defer review workflow.** Record the review decision in-repo per suggestion so
  the chosen path persists and gates the next build, rather than living only in the browser.

## Still open (owner-side)

Tracking-ID confirmation, the one-link Associates test, short-link compliance status, the
manufacturer-page spec conflicts, analytics-endpoint deployment and Search Console — all require an
enrolled Associates account or an owner decision this environment cannot reach. Nothing here is a
forecast; the campaign ledger stays empty until first-party reports arrive.

<<<<<<< HEAD

---

# Session b0920c92 — row-level sourcing site-wide, observation #6, decision desk, measurement proof (T43–T49)

Merged with `main` three times as parallel PRs landed (through #51); every register is the union of
all sessions' work.

## 1 · Every table row on every page carries its source
The gate's row-source rule now applies to every page: a row passes if it links an official source,
cites the source register, prints the source URL as text, or explicitly says its source is internal
or blank. The strict runs found 95 unsourced rows across the waves (61 + 22 + 12); all repaired with
per-row citations. Deep links (`#src-*`, `#flag-*`, `#q-*`, `#t-*`) are gate-checked to resolve.

## 2 · Observation #7 extends the short-link cross-path disagreement (FLG-034, S38)
Two independent sessions recorded the same divergence on 2026-11-20: four of the five `link.amazon`
short links land on the Amazon home page (FLG-030 by arena/1c6908d1; FLG-034 by this session, S38; cross-path disagreement recorded as FLG-033),
while all five direct `/dp/` listings still serve the recorded products. Recorded as observations,
not verdicts; FLG-003 stays open. The merged interpretation now separates the reproducible
observed-ASIN records from the unstable short-link behaviour.

## 3 · The measurement layer is proven against its hardened contract
`scripts/verify_measurement.py` runs the shipped collector as a real server, posts all five events
with the beacon's own payload, and asserts responses, aggregates, the hardened row schema, and that
no IP, user agent, cookie, email, search query, client timestamp or client site ID survives. It
caught a real defect in the pre-hardening collector (client-timestamp field mismatch) before the
hardened schema superseded that field entirely. `npm run verify` includes it.

## 4 · The decision desk names its deciders
Every suggestion row (40 across the union) carries its path (A–D), who decides it (SG-01, SG-07,
SG-08, SG-09, SG-10, SG-19, SG-20, SG-22, SG-29 and SG-30 need the account owner) and what would
have to be known to decide it. Question rows with no answer say "not yet answered".

## 5 · TP-06 published; register reconciled
**Where exactly do you put the probe in a chicken?** (TP-06) quotes the USDA FSIS *Food Thermometers*
factsheet (S17, fetched and read 2026-11-20) for the three-point whole-bird check and the 165 °F
minimum (S16). TP-01/TP-02 marked published crediting their sessions; this session's parallel TP-10
draft was dropped in favour of the merged one.
=======
### Integration outcome (this session)

PR #47 was merged into `main` as `0d257d5` after five rounds of reconciling with parallel sessions; GitHub Pages rebuilt
(`status: built`, no error) one second after the merge commit, and the new guide was re-fetched from the live URL to confirm the
deployed state. What landed: the sixth redirect observation, two sourced guides, the front-page glance table and dated seasonal
strip grafted onto main's renderer, `card_copy` on all five products, and four added gate rules. What was withdrawn on purpose:
this session's duplicate holiday guide, its two per-listing source rows, its JPEG artwork set, and its rewrite of the renderer
and stylesheet. Full reconciliation and handoff notes are in the `f1fd0ff0` section of `COORDINATION.md`.
>>>>>>> origin/main
