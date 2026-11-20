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
| Guides | 10 question-shaped guides (one per category cluster plus seasonal and listing-literacy pieces) |
| Topics | 13 in the published backlog — 2 now marked published with links to the guide each became |
| Sources | 35 register rows, each with URL, what it confirms, and a retrieval date |
| Flags | 29 items, each with the action that would resolve it; all public on *Flagged for review* |
| Open questions | 25, of which 8 are blocking; 4 of those can only be answered inside an enrolled Associates account |
| Suggestions | 31, each with evidence, effort, cost, risk, how to measure it, and a copy-paste prompt block |
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
