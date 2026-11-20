# Executive summary — ShopNow Kitchen (WinC)

**Site:** https://sassnarep3-star.github.io/WinC/ · **Tracking ID (as supplied):** shopnow047c-20 · **Date:** 2026-11-20

ShopNow Kitchen is a publication front page for five Amazon products (3 air fryers, 2 meat thermometers).
It leads with products, answers buyer questions, and keeps verification one click away — not in the way.

## What is live  *(counts recomputed from the repo on 2026-11-20 by session `ab951e4c`; they were stale in this block)*

<<<<<<< HEAD
- **Shop:** front page + 2 category pages + 5 product pages + a shop index, all with Sponsored buy buttons (`rel="sponsored nofollow noopener"`) and the Associates disclosure above the fold and again in the footer. Cards carry a shelf line, the deciding spec and one evidence link.
- **Guides:** 9 question-shaped guides — basket vs. oven-style, capacity checklist, cleanup/counter-space, multi-function questions, instant-read vs. leave-in, holiday crowd cook, the ice-cup accuracy check, whole-chicken fit against the 165°F rule, and how to read thermometer listing copy.
- **Trust:** verification register (intent vs. observed kept separate), **28 sources**, **34 flagged items**, redirect re-observation log (three dated observations), compliance gate (`scripts/check_site.py`, ~40 rule families) and a freshness clock (`scripts/freshness.py`).
- **Decisions:** **28 reviewed suggestions** and **26 open questions** (5 blocking) with answers recorded only where an official source supports them (5 answered).
- **Measurement:** 5-event beacon + Worker + stdlib collector (none deployed — Pages is static), a gated ledger ingest tool, an **empty** campaign ledger, sitemap + RSS + internal search.
- **Site:** 30 pages, 29 sitemap URLs, image set 1.39 MB (was 15 MB).
=======
- **Shop:** front page + 2 category pages + 5 product pages, all with Sponsored buy buttons (`rel="sponsored"`) and disclosure above the fold.
- **Guides:** 8 question-shaped guides (basket vs. oven-style, capacity checklist, cleanup/counter-space, multi-function questions, instant-read vs. leave-in, holiday crowd cook, leftovers food safety, listing literacy) + a seasonal band on the front page.
- **Trust:** verification register (intent vs. observed kept separate), 21-source register, 17 flagged items, redirect re-observation log, compliance gate (`scripts/check_site.py`).
- **Measurement:** 5-event beacon + Worker code; empty campaign ledger; sitemap + RSS + internal search.
>>>>>>> origin/main

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

- **`direction.html` — 28 suggestions**, each with problem, proposal, effort, cost, risk, *how we
  would know it worked*, evidence, and an instruction block for the next build prompt. Tick the
  ones you accept and the page assembles a copy-paste prompt carrying the standing rules
  (localStorage only; nothing is transmitted; nothing is auto-implemented).
- **`questions.html` — 22 open questions** (5 blocking) with what we have and can cite, what is
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

<<<<<<< HEAD
# Fourth pass — a shop that reads like a publication, and the policy details that were missing (2026-11-20, session `ab951e4c`)

Brief for this pass: make it look like a polished marketing affiliate site rather than AI output,
make the suggestions reviewable, list what has to be answered before a decision is reasonable, and
keep verifying line by line. Everything below is what changed; nothing was claimed that a source
does not support.

## 1 · Reader path: shop copy, not audit copy

- **Shelf cards rewritten.** Each product now leads with a shelf line (what it is for, in the
  listing's own terms) and a *decide on* line naming the one spec that settles the case, plus one
  evidence link. The old card printed a keyword-stuffed listing title, a model number, `see
  FLG-005` and a bare ASIN — register vocabulary that no shop prints on a shelf ticket.
- **Every product got its own artwork.** Five new original illustrations (dual basket, oven-style
  with a bird, XL basket, folding instant-read, leave-in probes to a hub), each captioned *not a
  product photograph*. Before this pass the three air fryers shared one image and both thermometers
  shared another — the single most obvious generated-site tell on the page.
- **Asset weight: 15 MB → 1.39 MB.** The four 3.7 MB PNGs became nine optimized 1200×750 JPEGs,
  every reference updated in data, and the gate now refuses a PNG asset or one image shared by two
  products (SG-21).
- **Process prose off the reader path.** The front page's wall of method text is now a three-item
  trust rail ("nothing is tested, so nothing is claimed" / "blank beats guessed" / "the links are
  sponsored"), each pointing at the register that proves it.
- Two gate rules were verified by *breaking* them first (shared image, stale flag reference), so
  they are known to fail rather than assumed to pass.

## 2 · Editorial: three guides, and the backlog kept truthful

Published from sources that can be re-read, not from adjectives:

| Guide | The claim it rests on |
|---|---|
| [Thermometer accuracy / ice-cup check](guides/thermometer-accuracy-ice-cup-check.html) | USDA FSIS: *"Most food thermometers will give an accurate reading within 2 to 4 degrees F"*; its documented ice-water (32°F) and boiling-water (212°F at sea level, −2°F to −5°F at altitude) procedures; its calibration-per-type table (*oven-cord and fork: "Cannot be calibrated"*). |
| [Whole-chicken fit](guides/whole-chicken-air-fryer-fit.html) | The three listings' own capacity/footprint/weight strings, the observation that **no listing publishes an interior cavity dimension**, plus FSIS's 165°F and three-place bird check. |
| [Reading thermometer listing copy](guides/listing-wording-thermometer-claims.html) | FSIS's care rule (*"Most thermometers should not be immersed in water"*, *"do not leave … unless the manufacturer's instructions specifically say it can withstand heat"*) read against the listing's IP67 and 1000°F wording. |

No testing claim, no price, no rating, no "best". Each closes a backlog row: TP-03, TP-06, TP-08
and TP-09 are marked published **with a pointer to the guide that answers them**, and six new rows
were added from gaps found while writing (dishwasher-safe part lists, clearance, Sync Finish,
read-time vs the FSIS table, alarm behaviour, preset names). Each new row states how it was chosen:
editorial hypothesis, because no Search Console property exists.

## 3 · Compliance: five clauses that had never been read into this register

The Program Policies page renders anonymously, so §2(b), §4, §5, §6(a), §6(c) and §6(d) were read
verbatim on 2026-11-20 and recorded as **S27** with the quotes. Consequences, all now on the site:

- **§6(d) — no implied endorsement.** Brand and celebrity names sit beside buy buttons on every
  product surface. The disclosure, the About page and the site-wide footer now state that the site
  is not endorsed by or affiliated with any brand named on a page, and the gate fails if that
  sentence disappears (FLG-026).
- **§6(c) — prompt removal of Program Content Amazon no longer displays.** No process existed.
  `scripts/freshness.py` measures the age of all 56 recorded reads against today, warns past 14
  days and fails past 45 (thresholds in `data/freshness.json`, not in code); the removal decision
  itself stays human and is recorded as open (FLG-027, Q-24).
- **§6(a) — Program Content may be truncated where meaning is unchanged, not altered.** The site's
  short shelf labels rely on exactly that permission, so the verbatim listing title is published on
  every product page under the label, and the comparison is flagged for a human rather than asserted
  as compliant (FLG-031, Q-23).
- **§5 — Program Content may not be used to develop machine-learning models without Amazon's
  express prior written approval.** This is the boundary on the "AI-powered platform" ambition: this
  repo automates rendering, gating and record-keeping and contains no crawler or corpus export. The
  ban is written into the standing rules so a future pass cannot drift past it (FLG-028, Q-25).
- **§4 — Special Links in email are permitted only where the recipient solicited the message.** The
  capture form records nothing today, so no rule is broken — and no list can be built from it.
  Recorded as the gate in front of any future newsletter (FLG-029, Q-21, SG-27).
- **Disclosure over-claim corrected (FLG-032).** The page asserted *"Amazon product descriptions are
  never copied"* while every product page publishes the listing's verbatim title and its detail
  values — which is the whole verification method. Replaced with what is actually taken, what is
  never taken, and the clause that permits it.
- **Expectation repair from Google (S28, FLG-030).** Google's changelog carries *"Removing
  documentation for the FAQ rich result feature"* (June 2026) and both the FAQPage and HowTo
  documentation URLs now redirect to it. The site keeps emitting FAQ markup for parsing and claims
  no SERP feature from it; no HowTo markup is added.

## 4 · Decision layer, made checkable

- **`direction.html`** — 28 suggestion rows. SG-19 (imagery line) was decided and shipped here;
  SG-21…SG-28 added. Each of the four paths now lists **the register rows it comprises** and
  **the questions it waits on**, so a choice can be audited before it is made instead of after.
- **`questions.html`** — 26 rows, 5 blocking. Five rows gained answers this pass (Q-07, Q-12,
  Q-13, Q-15, Q-19), each answer citing the source that supports it; Q-22…Q-26 were opened by the
  policy read above. A blank answer still means *nobody has it*, never *skipped*.
- **Register honesty enforced, not hoped for.** A `done-this-session` row must now name the pass
  that shipped it — three rows said "this session", which means nothing once four sessions have said
  it (the `_note` was corrected to stop readers reading `reviewed_by_session` as authorship). The
  gate also checks the ledger schema, the freshness data, card hygiene and imagery uniqueness.
- **Findings drift found and fixed (FLG-034).** The executive summary page's "what changed" table
  cited flag IDs that had drifted to the wrong findings after a renumbering; all five references were
  corrected, a structural rule now fails any page citing a flag that does not exist, and SG-28
  proposes moving pass-level findings into a data file so the semantic half cannot rot either.

## 5 · Numbers, computed

| Register | Now | Before this pass |
|---|---|---|
| Pages / sitemap URLs | 30 / 29 | 27 / 26 |
| Guides | 9 | 6 |
| Sources | 28 | 26 |
| Flagged items | 34 | 25 |
| Open questions (blocking / answered) | 26 (5 / 5) | 21 (5 / 0) |
| Suggestions (open / blocked) | 28 (9 / 2) | 20 (5 / 0) |
| Topic backlog rows (published) | 18 (4) | 12 (0) |
| Image payload | 1.39 MB | 15 MB |
| Recorded reads on the freshness clock | 56 | — (no clock existed) |

`npm run build` → *Built 30 pages, 29 sitemap URLs, 9 guides, 26 search rows.*
`npm run check` → *OK: 30 pages checked, 29 sitemap URLs, no violations.*

## 6 · What this pass deliberately did not do

No prices, ratings, review counts, stock levels, conversion scores, revenue forecasts or traffic
projections. No ranking and no "best". No claim that the supplied short links are invalid (FLG-003
stays unresolved). No `intended_*` field filled from a redirect. No analytics deployed (Pages is
static; FLG-007), and no ledger row: `scripts/ledger_add.py` was exercised with a throwaway row,
rendered, and reverted, because no authorized first-party report exists to record.
=======
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
