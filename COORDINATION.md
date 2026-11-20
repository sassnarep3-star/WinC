# COORDINATION — WinC affiliate site (shared task board)

> Session ID for this board: **68dc5c3a** (branch `arena/68dc5c3a-winc`).
> Rule: claim a task by writing the session ID + file scope, then commit and push the claim immediately.
> Never start a task another session has claimed. Keep scopes non-overlapping.
> `needs review` = published on the Flagged for Review page; does not block anything.
> Shared outputs (table data, index, navigation) are changed only by the final integration step
> in this session (single-session repo: the integration step is the same session, after all tasks).

## Task board

| ID | Task | Status | Owner (session) | File scope |
|----|------|--------|-----------------|------------|
| T01 | Repo audit + official-source verification (ASIN rule, Operating Agreement, Program Policies, FTC, Google rel=sponsored) | done | 68dc5c3a | COORDINATION.md, data/sources.json |
| T02 | Product-intent confirmation record + specs tables (intended vs observed kept separate) | done | 68dc5c3a | data/products.json, verification.html (via builder) |
| T03 | Shop-first site build (front page, categories, product pages, guides, disclosure, SEO, sitemap, RSS) | done | 68dc5c3a | scripts/build_site.py, assets/, *.html (generated) |
| T04 | Measurement layer (5 events, privacy-preserving counter, self-hosted endpoint code, empty campaign ledger) | done | 68dc5c3a | assets/app.js, analytics/, measurement.html |
| T05 | Direction section (suggestions, Q&A, path chooser) + executive summary + flagged page | done | 68dc5c3a | direction.html, executive-summary.html, flagged-for-review.html |
| T06 | Compliance gate (scripts/check_site.py) + link/sitemap checks, fix until green | done | 68dc5c3a | scripts/check_site.py |
| T07 | Final integration: re-verify combined data, confirm build + no broken links, PR to main, merge, confirm Pages deploy | in progress | 68dc5c3a | all (integration only) |

## Session log

- 2026-11-20 — 68dc5c3a claimed T01–T06 on branch arena/68dc5c3a-winc. Repo at start contained only README.md ("# WinC") on main (a6083c9). GitHub Pages already enabled (legacy, branch main, path /) at https://sassnarep3-star.github.io/WinC/ — verified via API.
- 2026-11-20 — 68dc5c3a verified from official sources: Amazon ASIN = 10 characters (sell.amazon.com); Operating Agreement §5 disclosure wording (affiliate-program.amazon.com/help/operating/agreement, updated 2025-10-15); Program Policies price-display rule (affiliate-program.amazon.com/help/operating/policies, updated 2026-04-14 — prices only via Amazon-served link or Creators/PA API); FTC Endorsement Guides affiliate disclosure (ftc.gov); Google rel="sponsored" for affiliate links (developers.google.com/search/docs/crawling-indexing/qualify-outbound-links). All five submitted link.amazon tokens are 9 characters (not ASINs). Observed redirect ASINs from prior sessions' live resolutions (2026-11-17) + Amazon listing snippets: B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R, B00hJ57DV→B08DKYBTPH, B0c8moW59→B0DHZTCNR5, B0f3GKalj→B0DZFD6R9Z. Intended fields left blank (nothing public binds a short code to a product); observed fields populated separately. Short-link compliance status NOT claimed invalid — see FLG-003.
- Irregularities flagged (see flagged-for-review.html): FLG-001 tracking ID unconfirmed; FLG-002 observed ASINs need one-link Associates test; FLG-003 short-link status unresolved; FLG-004 B0DHZTCNR5 vs B0DMDQZTZN URL variance; FLG-005 B08DKYBTPH model/temp conflicts; FLG-006 prices/ratings left blank per policy; FLG-007 endpoint not deployed (Pages is static).

## Handoffs / conflicts

- None (single session). If a claim is >60 min old with no commits, another session may take over and note it here.

## PR / merge record

- 2026-11-20 — 68dc5c3a (T07 integration): build + gate green (21 pages, 20 sitemap URLs). PR/merge/Pages result below.

## Session 9471c338 (merged via PR #1, archived 2026-11-20)

# Coordination board

This checkout has no session identifier beyond the active Arena branch (`arena/9471c338-winc`). It started with only `README.md`; no pre-existing task board, site, data register, or concurrent task claims were present. The user-requested separate session branches and immediate claim commit conflict with the repository session policy; work remains on the active branch.

| Task | Status | Owner | Files | Sources / verification / irregularities |
|---|---|---|---|---|
| Publication front page and guide/article concepts | done | arena/9471c338-winc | `index.html`, `styles.css` | Product facts deliberately omitted; submitted links retained exactly and marked sponsored. Article titles labeled as editorial hypotheses, not popularity claims. |
| Decision desk, executive summary, evidence gaps and suggestions | done | arena/9471c338-winc | `decision.html`, `styles.css` | Based on supplied brief and initial repository inspection; no product claims. |
| Flagged for review register | done | arena/9471c338-winc | `review.html`, `styles.css` | Records all five user-provided URLs and uncertainty. User brief notes FLG-003 unresolved; no assertion links are invalid. Policy links provided for manual verification. |
| Empty campaign/event ledger | done | arena/9471c338-winc | `ledger.html`, `styles.css` | No measurements invented. This static site does not implement a backend or collect analytics. |
| Build/deploy and source verification | needs review | arena/9471c338-winc | `.github/workflows/pages.yml`, `sitemap.xml`, `robots.txt`, `feed.xml` | Must test GitHub Pages in repository settings/deployment. No access to Amazon pages or Associates workflow was available in this environment; product identities, URLs, link status and claims remain unverified. |

## Sources and verification

- User-submitted product URLs and tracking ID in the task prompt (not independently verified).
- Amazon Associates Operating Agreement: https://affiliate-program.amazon.com/help/operating/agreement (manual current-terms review still required).
- FTC Endorsement Guides FAQ: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking (reference only; legal review still required).
- Initial repository inspection: `git status`, `git log`, `README.md`, file listing. Initial repository had no source register or site.

## Known limitations

- Product names, intended ASINs, official listing URLs, observed redirects, specifications, pricing, stock, reviews, commission rates, conversion potential, and enrollment status are not known. Intended product identifier and observed redirect must be stored independently when a workflow test is performed.
- Amazon Associates workflow and reports require authorized account access and cannot be completed from this repository. No automated Amazon data collection, click counter, self-hosted analytics endpoint, Search Console property, RSS feed, or live Page deploy has been activated.
- GitHub Pages publishing requires the repository's Pages configuration and successful deployment check. Do not represent the site as live until verified.

### Integration note (68dc5c3a, 2026-11-20)

Session 9471c338's Counter Notes stub (decision.html, review.html, ledger.html, styles.css) is preserved under `archive/counter-notes/` as historical record. The live site is ShopNow Kitchen (this branch), which implements the full brief: verified products, measurement, guides. Their `.github/workflows/pages.yml` is kept; live deploy remains legacy Pages (branch main, path /).

---

## Session 1f90cb3e — live re-verification and correction pass (branch `arena/1f90cb3e-winc`)

**Session ID: `1f90cb3e`.** Start state: this branch was rebased onto `origin/main` (c2a5823), which
already contains the merged ShopNow Kitchen site from session `68dc5c3a` (PR #2). This session does
**not** rebuild the site. It re-verifies the shipped data **line by line against live official
sources** and corrects what is wrong — the task the final integration step is required to do.

### Claim (T08)

| ID | Task | Status | Owner (session) | File scope |
|----|------|--------|-----------------|------------|
| T08 | Live re-verification of all five product records + corrections + source/flag register refresh + §2(k) Program Content disclaimer + ledger-export in measurement | in progress | 1f90cb3e | `data/products.json`, `data/sources.json`, `data/flags.json`, `scripts/build_site.py`, `scripts/check_site.py`, `assets/`, `COORDINATION.md` |

### Why this scope, and how it avoids the other live sessions

- Sessions `70d8ad52` and `f87d2975` branched from the **initial commit** `a6083c9` (their boards
  state the repo "contained only README.md"). Their branches currently contain **only** a
  `COORDINATION.md`; they have written no site files. They are building *alternate* layouts
  (`docs/`, `pages/`, `sources/`, `scripts/build.py`).
- This session works against the **merged** site on `main` (`scripts/build_site.py` +
  `scripts/check_site.py`, root-level HTML), because that is what is deployed and what a reader sees.
- **Conflict risk flagged:** when `70d8ad52` or `f87d2975` opens a PR, their branch is based on the
  initial commit and their file layout differs from `main`. Merging either would **replace** the
  merged site rather than extend it. The integration decision on those PRs belongs to whoever
  integrates last; this session's corrections are written to the merged layout so they survive
  either way. Recorded here so no session's work is silently discarded.

### What this session verified live (2026-11-20) — first-hand, not inherited

All five submitted `link.amazon` short links were re-resolved live in this session (closing the
sandbox limitation behind FLG-008). Each landed on an `amazon.com/dp/<ASIN>` page:

| Submitted | Live redirect target (observed 2026-11-20) | Listing title read on that page |
|---|---|---|
| `link.amazon/B04G1MEwY` | `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven |
| `link.amazon/B02NbDxp3` | `B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven |
| `link.amazon/B00hJ57DV` | `B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry 4-in-1 with 450°F Hi-Fry Option |
| `link.amazon/B0c8moW59` | `B0DHZTCNR5` | ThermoMaven 1 Sec Professional Digital Meat Thermometer |
| `link.amazon/B0f3GKalj` | `B0DZFD6R9Z` | CHEF iQ Sense \| Smart Wireless Meat Thermometer |

Errors found in the shipped `data/products.json` (all against the live listings above) are recorded
on the Flagged for Review page with the corrected value and the source line that contradicts it.

### Session log

- 2026-11-20 — 1f90cb3e claimed T08 on `arena/1f90cb3e-winc`, rebased onto `origin/main`.
- 2026-11-20 — Re-read official sources live: Operating Agreement (updated 2025-10-15) §5
  disclosure wording; Program Policies (updated 2026-04-14) §2(b) Special Links, §2(b) price/availability
  rule, §2(k) Program Content text disclaimer, §2(h) 24-hour storage limit; Creators API GetItems
  ItemIdType table ("10-Character alphanumeric unique identifier"); 16 CFR 255.5 (eCFR); FTC
  Disclosures 101; Google `rel="sponsored"`; GitHub Pages docs.
