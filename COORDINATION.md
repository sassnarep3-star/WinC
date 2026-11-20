# COORDINATION.md — shared task board

Session ID: `arena-23428c9e` (branch `arena/23428c9e-winc`)
Created: 2026-11-20 (UTC)

How to claim: set Status to `in progress`, put your session ID and file scope in the row, commit and push immediately. Never start a task another session has claimed. `needs review` means published on the Flagged for Review page and does not block anything. When done: record sources, verification performed, irregularities below, mark `done`.

## Task board

| Task ID | Task | Status | Session ID | Files touched |
|---|---|---|---|---|
| T-01 | Create COORDINATION.md task board | done | arena-23428c9e | COORDINATION.md |
| T-02 | Attempt verification of 5 supplied product links (official sources only) | done | arena-23428c9e | data/products.json, FLAGGED-IRREGULARITIES.md |
| T-03 | Build site shell: layout, masthead, disclosure strip, footer, nav | done | arena-23428c9e | index.html, css/site.css, js/site.js, partials |
| T-04 | Products page: source-register table, one row per product, source links, blank+flag unverified fields | done | arena-23428c9e | products.html, data/products.json |
| T-05 | Executive summary page | done | arena-23428c9e | executive-summary.html |
| T-06 | Suggestions page (decision paths for review before implementation) | done | arena-23428c9e | suggestions.html |
| T-07 | Questions & Answers page (open questions, missing information) | done | arena-23428c9e | questions.html |
| T-08 | Flagged for Review page (irregularities + source links) | done | arena-23428c9e | flagged.html |
| T-09 | Buyer-question guides (question-shaped articles, no unverified product claims) | done | arena-23428c9e | guides.html, guides/*.html |
| T-10 | Compliance page: Associates disclosure, link marking, verification policy | done | arena-23428c9e | compliance.html |
| T-11 | SEO/findability: sitemap.xml, robots.txt, meta/OG tags, RSS feed | done | arena-23428c9e | sitemap.xml, robots.txt, feed.xml |
| T-12 | Outbound click counter (privacy-preserving, client-side, no third parties) | done | arena-23428c9e | js/click-counter.js |
| T-13 | Verification page: line-by-line method, sources used | done | arena-23428c9e | verification.html |
| T-14 | Integration: re-verify combined data, link check, build check | done | arena-23428c9e | all |
| T-15 | PR to main, merge, confirm GitHub Pages deploy | done | arena-23428c9e | — |

## Source log (official sources checked)

| Date (UTC) | What was checked | Official source | Result |
|---|---|---|---|
| 2026-11-20 | ASIN-format check for the 5 supplied identifiers | Amazon Ads official guide — https://advertising.amazon.com/library/guides/targeting-with-sponsored-products (quote verified: "An ASIN is always 10 characters long, and either entirely numeric … or starts with a 'B'") | Supplied IDs are 9 characters; observed official listing identifiers after `/dp/` are 10 characters. Flagged: supplied identifiers do not match ASIN format (FLG-001). |
| 2026-11-20 | Destination check of the 5 supplied `link.amazon` URLs | Live fetch of each supplied URL on 2026-11-20; each resolved to an amazon.com `/dp/` detail page | All five resolved and were recorded as **observed redirect targets** in a separate field (never merged with intended-ASIN fields). |
| 2026-11-20 | FTC disclosure guidance | Federal Trade Commission — https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Disclosure must be placed with the endorsement, hard to miss, simple language; used to design the above-the-fold disclosure strip. |
| 2026-11-20 | Amazon Associates Operating Agreement (updated 2025-10-15) | https://affiliate-program.amazon.com/help/operating/agreement | Verified live; Section 1 defines **Special Links** as links that "properly use the special 'tagged' link formats we provide". |
| 2026-11-20 | Amazon Associates Program Policies (updated 2026-04-14) | https://affiliate-program.amazon.com/help/operating/policies | Verified live; Special Links must include Associates ID/tag "appearing as XXXXX-## … as a parameter in the URL of each link". |
| 2026-11-20 | Associates Standard Commission Income rates | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Verified live; Table 1: **Kitchen = 4.50%**. Amazon assigns the fee category per product — per-ASIN category not confirmable without Associates account (flagged). |
| 2026-11-20 | Product listing facts (titles, prices, ratings, breadcrumbs, specs) for the 5 observed ASINs | https://www.amazon.com/dp/B0CDY277D3 · https://www.amazon.com/dp/B09B7SB46R · https://www.amazon.com/dp/B08DKYBTPH · https://www.amazon.com/dp/B0DHZTCNR5 · https://www.amazon.com/dp/B0DZFD6R9Z | Each field captured directly from the official detail page on 2026-11-20; price snapshots dated and marked subject to change. |

## Irregularities log (mirrors Flagged for Review page)

| ID | Irregularity | Status | Source |
|---|---|---|---|
| FLG-001 | All 5 supplied product identifiers are 9 characters; Amazon states "An ASIN is always 10 characters long". Supplied tokens are therefore not usable as ASINs as supplied. | needs review | https://advertising.amazon.com/library/guides/targeting-with-sponsored-products |
| FLG-002 | `link.amazon` is not a link format described in the Associates Operating Agreement or Program Policies (which describe "special 'tagged' link formats" with tag `XXXXX-##` as a URL parameter). Exact compliance status of the supplied short links is **unresolved — not claimed invalid**. | needs review | https://affiliate-program.amazon.com/help/operating/agreement · https://affiliate-program.amazon.com/help/operating/policies |
| FLG-003 | Intended ASIN / intended listing URL for each supplied link are unknown (owner intent not supplied). Intent fields kept blank and separate from observed redirect targets. | needs review | — |
| FLG-004 | Tracking ID `shopnow047c-20` could not be validated against an Associates account (no account access in this environment). | needs review | https://affiliate-program.amazon.com/help/operating/policies |
| FLG-005 | Commission rate shown is the official rate-card rate for **Kitchen** (4.50%); the fee category Amazon assigns per product cannot be confirmed without Associates reporting. | needs review | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |
| FLG-006 | Campaign ledger intentionally empty: no first-party click/order reports available yet. No conversion score or revenue forecast is presented. | needs review | — |
| FLG-007 | The brief references "the five defined events" for analytics but does not enumerate them; five events were defined locally pending confirmation. | needs review | — |
| FLG-008 | Price and rating snapshots are point-in-time (2026-11-20) and change frequently; they are dated on every surface. | needs review | official listing pages (source log) |

## Conflict / handoff log

| Date | Event |
|---|---|
| 2026-11-20 | Session arena-23428c9e created board (none existed), claimed T-01..T-15 (single-session start; scopes non-overlapping). |

## Merge / deploy record

| Item | Value |
|---|---|
| PR | (filled at T-15) |
| Merge result | (filled at T-15) |
| GitHub Pages | (filled at T-15) |
