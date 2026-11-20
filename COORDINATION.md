# COORDINATION — WinC affiliate site (shared task board)

> **Latest session: `arena-82d39deb`** (branch `arena/82d39deb-winc`). That session's board,
> sources and findings are in the **last section of this file**. Earlier sessions are kept
> verbatim as the provenance trail.

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
| T07 | Final integration: re-verified combined data, confirmed build + no broken links, PR opened to main, merged, Pages deploy confirmed | done | arena/a42979d2-winc | all (integration only) |

## Session log

- 2026-11-20 — 68dc5c3a claimed T01–T06 on branch arena/68dc5c3a-winc. Repo at start contained only README.md ("# WinC") on main (a6083c9). GitHub Pages already enabled (legacy, branch main, path /) at https://sassnarep3-star.github.io/WinC/ — verified via API.
- 2026-11-20 — 68dc5c3a verified from official sources: Amazon ASIN = 10 characters (sell.amazon.com); Operating Agreement §5 disclosure wording (affiliate-program.amazon.com/help/operating/agreement, updated 2025-10-15); Program Policies price-display rule (affiliate-program.amazon.com/help/operating/policies, updated 2026-04-14 — prices only via Amazon-served link or Creators/PA API); FTC Endorsement Guides affiliate disclosure (ftc.gov); Google rel="sponsored" for affiliate links (developers.google.com/search/docs/crawling-indexing/qualify-outbound-links). All five submitted link.amazon tokens are 9 characters (not ASINs). Observed redirect ASINs from prior sessions' live resolutions (2026-11-17) + Amazon listing snippets: B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R, B00hJ57DV→B08DKYBTPH, B0c8moW59→B0DHZTCNR5, B0f3GKalj→B0DZFD6R9Z. Intended fields left blank (nothing public binds a short code to a product); observed fields populated separately. Short-link compliance status NOT claimed invalid — see FLG-003.
- Irregularities flagged (see flagged-for-review.html): FLG-001 tracking ID unconfirmed; FLG-002 observed ASINs need one-link Associates test; FLG-003 short-link status unresolved; FLG-004 B0DHZTCNR5 vs B0DMDQZTZN URL variance; FLG-005 B08DKYBTPH model/temp conflicts; FLG-006 prices/ratings left blank per policy; FLG-007 endpoint not deployed (Pages is static).

## Handoffs / conflicts

- None (single session). If a claim is >60 min old with no commits, another session may take over and note it here.

## PR / merge record

- **PR #17** — https://github.com/sassnarep3-star/WinC/pull/17 — opened as "Ship Crisp Report: generated
  publication + compliance gate", merged once into `main`, then **dropped** when `main` was
  reconstructed from `715b923` for PRs #15/#19/#21 (`git merge-base --is-ancestor 1315e45 origin/main`
  failed; `AUDIT.md`, `tools/audit.mjs`, `tools/freshness.mjs`, `.github/workflows/ci.yml` absent).
  Retitled "Restore #17 on top of #15/#19…", re-merged, board sections re-appended after the conflict
  resolution dropped them.
- **Merged:** yes — final head `f28015e` + the merge of `origin/main` (PR #21). 36 files added,
  **0 deletions**, and the only shared file modified is this board.
- **CI on the PR:** `verify site` → **success** (14 s) — that run executes `scripts/build_site.py`,
  `scripts/check_site.py`, the committed-HTML reproducibility check, XML validity, the audit report and
  the staleness queue in a clean checkout of the combined tree. Re-verified locally after the last merge:
  `OK: 27 pages checked, 26 sitemap URLs, no violations.`
- **Pages deploy confirmed after the merge** — see the live checks below (`gh api /pages` → `status:
  built`; `https_enforced: true`; `source: {main, /}`; `/WinC/` → 200, `/WinC/AUDIT.md` → 200,
  `/WinC/sitemap.xml` → 200 with 26 locs, `/WinC/nope.html` → 404).
- **Findings left open on purpose** (logged, not patched, because the files belong to other sessions):
  F-1 the 38 `verification.html#src-*` fragments (still `grep -c 'id="src-' verification.html` → `0`
  after PR #21) and F-2 the GET `reader-capture` email field's no-JS path. Their new `FLG-021…FLG-025`
  cover product-data drift instead, so these two are not duplicated anywhere — `node tools/audit.mjs`
  reproduces both in report mode.
- **Not merged here:** PR #5, titled `[HELD]`, left to its owner.
- **Residual:** T16–T18 remain blocked on operator inputs (Search Console access, first-party report
  access, Special Links at scale); recorded with steps, not simulated.
