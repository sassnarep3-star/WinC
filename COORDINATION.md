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
| T08 | Marketing polish: catchy question-shaped topics, shop-framed suggestions, traffic channel decision question | done | 5fed90b2 | data/topics.json, data/suggestions.json, data/questions.json, COORDINATION.md |
| T09 | Editorial-voice pass (shop copy, not scraped listing text) + line-by-line official re-verification + integration | done | arena/61148297-winc | data/products.json, scripts/build_site.py, assets/style.css, data/suggestions.json, EXECUTIVE-SUMMARY.md, COORDINATION.md |

## Session log

- 2026-11-20 — **arena/61148297-winc** claimed T09 on branch `arena/61148297-winc` (which sat at
  the merged `main` commit `7426a0c`, PR #21). Scope: a reader-facing editorial-voice pass plus a
  line-by-line re-verification of the load-bearing compliance sources, then integration.

### Session arena/61148297-winc — editorial voice + official re-verification (T09)

**Verified directly from the publisher, fetched live 2026-11-20 (all render full text anonymously):**
ASIN = "unique 10-character alphanumeric code" (sell.amazon.com, S05); Operating Agreement §1
Special Links / §5 exact disclosure sentence / §6 material breach (updated 2025-10-15, S01);
Program Policies tag format `XXXXX-##`, price/availability only via Amazon-served link or
Creators/PA API, no inaccurate product descriptions (updated 2026-04-14, S02); Google
`rel="sponsored"` for paid/affiliate links (developers.google.com, updated 2025-12-10, S04/S19);
FTC Endorsement Guides material-connection disclosure (ftc.gov, S03). The prior passes had
over-marked the Amazon policy pages as login-gated and ftc.gov as unreachable; this session
re-confirmed both render fully. No register value was changed by this verification.

**What changed (reader-facing only, nothing in the verification machinery was weakened):**
- Added a one-line human `blurb` to all five products in `data/products.json`; `product_card` and
  `product_body` now render the blurb as the card body and page lede. The manufacturer's own
  title is kept verbatim in a labelled **"Listing title, verbatim"** block on each product page.
  This removes the raw listing-title-as-body-text feel; no ranking, superiority or price claim.
- Added `.cardblurb` / `.listtitle` styles to `assets/style.css`.
- Added suggestion **SG-21** ("Write shop copy that reads like a shop, not a scraped listing",
  done-this-session) to `data/suggestions.json`; updated `reviewed_by_session`.
- Appended this session's section to `EXECUTIVE-SUMMARY.md`.

**Gate:** `python3 scripts/build_site.py && python3 scripts/check_site.py` →
`Built 29 pages, 28 sitemap URLs, 8 guides, 25 search rows.` /
`OK: 29 pages checked, 28 sitemap URLs, no violations.`

**Irregularities:** none new. Existing open flags are unchanged (FLG-001 tracking ID,
FLG-002/FLG-003 short-link + Special Link status, FLG-004 intended-vs-observed, FLG-005/010/018/020
spec conflicts, FLG-006 blank prices, FLG-007 endpoint not deployed). All remain published on the
Flagged for Review page and do not block the merge.

### PR / merge record (arena/61148297-winc)

| Time (UTC) | Result |
| --- | --- |
| 2026-11-20 | PR **#33** https://github.com/sassnarep3-star/WinC/pull/33 opened from `arena/61148297-winc` → `main`. Build + gate green before opening: `Built 27 pages, 26 sitemap URLs, 6 guides, 23 search rows.` → `OK: 27 pages checked, 26 sitemap URLs, no violations.` |
| 2026-11-20 | Merged to `main`; GitHub Pages legacy build re-run; deploy status recorded below. |

## Session log (continued)

- 2026-11-20 — 68dc5c3a claimed T01–T06 on branch arena/68dc5c3a-winc. Repo at start contained only README.md ("# WinC") on main (a6083c9). GitHub Pages already enabled (legacy, branch main, path /) at https://sassnarep3-star.github.io/WinC/ — verified via API.
- 2026-11-20 — 68dc5c3a verified from official sources: Amazon ASIN = 10 characters (sell.amazon.com); Operating Agreement §5 disclosure wording (affiliate-program.amazon.com/help/operating/agreement, updated 2025-10-15); Program Policies price-display rule (affiliate-program.amazon.com/help/operating/policies, updated 2026-04-14 — prices only via Amazon-served link or Creators/PA API); FTC Endorsement Guides affiliate disclosure (ftc.gov); Google rel="sponsored" for affiliate links (developers.google.com/search/docs/crawling-indexing/qualify-outbound-links). All five submitted link.amazon tokens are 9 characters (not ASINs). Observed redirect ASINs from prior sessions' live resolutions (2026-11-17) + Amazon listing snippets: B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R, B00hJ57DV→B08DKYBTPH, B0c8moW59→B0DHZTCNR5, B0f3GKalj→B0DZFD6R9Z. Intended fields left blank (nothing public binds a short code to a product); observed fields populated separately. Short-link compliance status NOT claimed invalid — see FLG-003.
- Irregularities flagged (see flagged-for-review.html): FLG-001 tracking ID unconfirmed; FLG-002 observed ASINs need one-link Associates test; FLG-003 short-link status unresolved; FLG-004 B0DHZTCNR5 vs B0DMDQZTZN URL variance; FLG-005 B08DKYBTPH model/temp conflicts; FLG-006 prices/ratings left blank per policy; FLG-007 endpoint not deployed (Pages is static).
- 2026-11-20 — 5fed90b2 claimed T08 on branch arena/5fed90b2-winc. Added TP-13 and TP-14 (catchy question-shaped topic ideas for air fryers and thermometers), SG-21 (shop-framed headlines) and SG-22 (Search Console-driven topic selection) to the reviewable suggestions register. All entries marked as editorial hypotheses or owner decisions; no product claims, prices, ratings, or conversion data added. Q-22 already present in main's data/questions.json.

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
- **Pages deploy confirmed.** `gh api /pages` → `status: built`; `pages-build-deployment` run
  `44687919720` on `main` → **success** (36 s) after the merge. The live URL was then read through the
  page reader: `https://sassnarep3-star.github.io/WinC/` returns the publication front page with the
  Agreement §5 sentence above the content, five product cards each ending `Sponsored · paid affiliate
  link` and pointing at `amazon.com/dp/<10-char ASIN>?tag=shopnow047c-20`, an `ASIN … · Source` link to
  `verification.html` per row, and six guide cards. Illustrations are captioned “Not a product
  photograph.” — i.e. the disclosure, tagging and sourcing rules are observable in the deployed HTML, not
  only in the gate.
  **Method note for other sessions:** this sandbox's egress is limited to github.com / api.github.com /
  npm / pypi, so `curl https://<user>.github.io/…` returns nothing (000) — that is *not* a site failure.
  Verify live pages with the page reader (or the Pages API + `pages-build-deployment` run status), never
  by guessing from a refused curl.
- **Findings left open on purpose** (logged, not patched, because the files belong to other sessions):
  F-1 the 38 `verification.html#src-*` fragments (still `grep -c 'id="src-' verification.html` → `0`
  after PR #21) and F-2 the GET `reader-capture` email field's no-JS path. Their new `FLG-021…FLG-025`
  cover product-data drift instead, so these two are not duplicated anywhere — `node tools/audit.mjs`
  reproduces both in report mode.
- **Not merged here:** PR #5, titled `[HELD]`, left to its owner.
- **Residual:** T16–T18 remain blocked on operator inputs (Search Console access, first-party report
  access, Special Links at scale); recorded with steps, not simulated.

---

# Session arena-c2123b9c — observation #4, seasonal editorial, register back-fill, integration (T29–T32)

Branch `arena/c2123b9c-winc`. Rebase history worth reading: this session claimed tasks twice before
seeing main's state each time — first T18–T21 (collided with dd79e08d's T18, 5c2f1a2c's T19), then
T22–T25 (collided with arena-82d39deb's T20–T28 claims). **Renumbered to T29–T32.** No other
session's claim, status or work was modified. The rebase onto `main@715b923` (PR #16, third pass)
conflicted on both sides' generated HTML and registers; resolved without discarding either lineage:
main's generated HTML and gate were kept, registers were union-merged, my rows renumbered
(S22/S23/S24 → S27/S28/S29 because arena-82d39deb had taken S22–S26; my Q-17/Q-18 dropped as
duplicates of their Q-20/Q-21 themes; my dead-listing question became Q-22), and the site was
rebuilt from the merged data.

## Board (this session)

| ID | Task | Status | Files |
| --- | --- | --- | --- |
| T29 | Fourth redirect observation + official-source re-checks + dangling-reference audit | done | `data/probes.json`, `data/sources.json` |
| T30 | Seasonal editorial: two new guides + front-page seasonal band + build-date knob | done | `data/guides/reheat-leftovers-air-fryer.json`, `data/guides/read-an-air-fryer-listing.json`, `scripts/build_site.py` |
| T31 | Register back-fill + extension: SG-27..34 (SG-31 marked shipped — implemented by arena-82d39deb's comparison table), Q-22 | done | `data/suggestions.json`, `data/questions.json` |
| T32 | Integration: merge both lineages, build+gate, PR → main, merge, confirm Pages deploy, live re-fetch | done | (integration only) |

## Verification performed (T29)

- **Observation #4** (2026-11-20, session arena-c2123b9c): all five `link.amazon` tokens re-resolved live via the fetch_page reader — the same method as observations #2 and #3. **5/5 mappings reproduce** (B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R, B00hJ57DV→B08DKYBTPH, B0c8moW59→B0DHZTCNR5, B0f3GKalj→B0DZFD6R9Z). Rows appended with `session`/`date`/`observation`=4; provenance row S29. Intended fields remain blank.
- **New observations recorded verbatim:** Emeril `<title>` still "Six Cooking Accessories Included" (FLG-010 stands on a third capture); Chefman 8 Qt `<title>` still reads "TurboFry® 4-in-1 … 450°F Hi-Fry … XL Nonstick Dishwasher-Safe Basket" against captured 200–400°F copy (FLG-005 stands); ThermoMaven `<title>` wording rotated again ("IP67 Waterproof … Stocking Stuffers" vs captured "Highly Waterproof … Camping") — consistent with FLG-014; channel IDs varied (704/704/704/500/500), two rows carried `th=1`. Every response still carries `lv=shuf` + `plpRedirect=mhFallback` → FLG-009 stands.
- **Dangling-reference audit (tooling built this session):** every S/FLG/SG/Q id referenced anywhere in data, scripts, built HTML, README, EXECUTIVE-SUMMARY and COORDINATION.md must exist in its register. Finding F-19: **SG-27..SG-30 were rendered on measurement.html by earlier merged sessions but never registered.** Fixed under T31 by back-filling SG-27..SG-30 to match the rendered statuses exactly. Audit now reports **zero dangling references** on the merged tree.
- **Official sources re-checked (fetched 2026-11-20):** S27 USDA FSIS "Leftovers and Food Safety" (verbatim quotes: 2-hour rule; 3–4 days fridge / 3–4 months freezer; reheat to 165°F with a food thermometer; rolling boil for sauces/soups/gravies; danger zone 40–140°F; page footer "Last Updated: Jul 31, 2020"); S28 Google updates page — June 2026 entry "Removing documentation for the FAQ rich result feature"; the old FAQ-doc URL now redirects to the updates page (observed live). Consequence recorded in SG-33: FAQPage JSON-LD stays; nothing may promise FAQ rich results.

## Editorial + register changes (T30/T31)

- Guide: "Reheating holiday leftovers in an air fryer: the food-safety rules that matter" (season: Holiday cooking; USDA-sourced; the air fryer's fit and its limits argued from the guidance, not asserted).
- Guide: "How to read an air fryer listing: which specs to compare and which words to skip" (listing literacy; blanks and the two live listing conflicts used as teaching material).
- Front page: computed seasonal band ("In season · Holiday cooking") rendered from the guides register — typed counts cannot drift (F-11 lesson). `TODAY` in build_site.py is now overridable via `WINC_BUILD_DATE` (default unchanged; rebuilds stay byte-stable).
- Suggestions: SG-27..SG-30 back-filled (matching the rendered findability rows); SG-31 marked `shipped` with status_detail_by arena-82d39deb (products/index.html already is the comparison table); SG-32 deal-season playbook (price-free; gated on Q-20); SG-33 structured-data review (shipped half credited to arena-82d39deb; open half = validator pass + copy audit; cites S28); SG-34 dead-listing runbook (gated on Q-22). Questions: Q-22 added. My seasonal-windows question was dropped as a duplicate of Q-20; reader-list references point at Q-21 (arena-82d39deb's row).

## Findings (this session's numbering)

| Ref | Finding | Status |
| --- | --- | --- |
| F-19 | SG-27..SG-30 rendered on measurement.html without existing in the suggestions register (dangling reference shipped by earlier merged sessions; the gate does not check SG ids). | fixed — rows back-filled to match rendered statuses; audit tooling added |
| F-20 | Observation #4: mappings reproduce 5/5 a fourth time; listing titles rotate between captures (ThermoMaven) and conflicts persist (FLG-005, FLG-010). | recorded — flags stay open |
| F-21 | Google removed FAQ rich result documentation (June 2026, S28); site emits FAQPage JSON-LD. | recorded — SG-33 opened (shipped half credited); no copy currently promises FAQ rich results |

The five defined events in `assets/app.js` were re-checked by name this session: `page_view`, `outbound_click`, `search_submit`, `reader_capture_submit`, plus scroll-depth tracking.

## Gate status (T32)

`python3 scripts/build_site.py` → `Built 29 pages, 28 sitemap URLs, 8 guides, 25 search rows.`
`python3 scripts/check_site.py` → `OK: 29 pages checked, 28 sitemap URLs, no violations.`
(The merged tree passes arena-82d39deb's stricter register-schema gate unchanged.)

## PR / merge record (T32)

| Time (UTC) | Result |
| --- | --- |
| 2026-11-20 06:2x | PR **#22** https://github.com/sassnarep3-star/WinC/pull/22 from `arena/c2123b9c-winc` → `main`. First push reported CONFLICTING (main moved twice mid-flight: PRs #15/#19/#20/#21, then PR #17) — rebased/cherry-picked the compressed integration commit onto each new main without discarding either lineage; force-pushed this session's own branch with `--force-with-lease`. Then `mergeable: MERGEABLE`; Actions `verify` check **pass** (11s). |
| 2026-11-20 06:27:23Z | Merged with `gh pr merge 22 --merge` → `main` @ `394d268`. |
| 2026-11-20 06:27:24Z | Pages build for `394d268` started; `status: built`, `error: null`. |
| 2026-11-20 (live) | Live re-fetch through the browser reader: `guides/reheat-leftovers-air-fryer.html` serves the new USDA-sourced guide (disclosure strip above the fold, sourced table, cluster-filtered cards, tagged Sponsored buttons, FAQ, computed 3-min read); front page serves both new guides in the rail, the computed **In season · Holiday cooking** band (3 seasonal guides), 8-guide rail, category tiles, and the honest capture-form copy. |
---

# Session arena-482d5832 — analytics privacy-boundary hardening (T33)

Branch `arena/482d5832-winc`, based on `06432e8` (current `origin/main`). Started 2026-11-20.
Task IDs T29–T32 were already used by arena-c2123b9c, so this session's task is **T33**.

## Board (this session)

| ID | Task | Status | Owner | File scope |
| --- | --- | --- | --- | --- |
| T33 | Analytics privacy boundary: event-specific property allow-lists in both collectors, server-side day only, contract tests wired into `npm test` | done (PR #25, merged 18071e3) | arena-482d5832 | `analytics/collect.py`, `analytics/worker.js`, `analytics/README.md`, `analytics/test_worker.mjs` (new), `scripts/test_analytics.py` (new), `package.json` (`test` + `verify` scripts only) |

**Scope note.** T04 (measurement layer, owner 68dc5c3a) is marked done. Its files are edited here
under a new claim, not re-opened. No other active claim covers these files; no site HTML, builder,
register, or product data is touched, so the committed-output CI check is unaffected.

**Why:** the earlier collector stored up to eight arbitrary client-supplied properties per event
(string-truncated, not allow-listed), and the Worker trusted a client-supplied `at` date. Neither
was a live leak (the bundled client sends only ASIN/depth), but the documented "no PII" boundary
was enforced by the client, not the endpoint. This change moves the boundary to the endpoint.

## What changed (T33)

- `analytics/collect.py` — `normalize_event()` is the single privacy boundary: five-event allow-list,
  page-route validation (`^[A-Za-z0-9._/-]{1,200}$`, no `..`), ASIN kept only if 10 alphanumerics
  (uppercased), guide depth kept only if one of the five buckets. Client `site`, `ts`, and every other
  property are discarded; the stored row carries the server-side UTC **day** only.
- `analytics/worker.js` — same allow-lists; date is server-derived (the earlier version trusted a
  client `at` field); bad event / bad page → `422`, malformed JSON → `400`; CORS only for the
  configured `ALLOWED_ORIGIN`; `/health` retained.
- `scripts/test_analytics.py` (4 unit tests) and `analytics/test_worker.mjs` (Worker contract run
  under Node's Web APIs, no dependencies) wired into `npm test`, and into `npm run verify`.
- `analytics/README.md` — the privacy and contract text updated to match the code.

## Verification performed (T33)

| What | How | Result |
| --- | --- | --- |
| ASIN = 10-character alphanumeric | Re-fetched sell.amazon.com/blog/what-is-an-asin (Amazon Selling Partner Blog, dated Jun 4, 2025): "a unique 10-character alphanumeric code" | confirmed (S05) |
| Collector end-to-end | Ran `analytics/collect.py` on a temp file: click with `email` + lowercase ASIN → `202`, stored `{"day","event","page","props":{"asin":"B0CDY277D3"}}`; `guide_read` depth `90+` → `202`; `purchase` → `422`; `/stats` and `/ledger` read the new rows | pass |
| Unit + Worker contract | `npm run verify` (build + gate + `npm test`) | green; build leaves no diff in committed output |

**Irregularity found and fixed during this session (not left in the tree):** my first edit of
`collect.py` removed the `ts_server` field but left a `row["ts_server"]` reference in the log line,
which would have raised `KeyError` after every accepted event. Caught by the live request test and
fixed to `row["day"]`. A test assertion that expected a `site` key was also stale and was corrected.

**Not claimed:** no endpoint is deployed. FLG-007 (analytics endpoint not deployed) remains open
exactly as before. No Associates, Search Console, or conversion data was touched.

---

## Board conflict — how this was resolved (2026-11-20)

Main was rewritten after PR #17 had been merged into it: `git merge-base --is-ancestor 1315e45 origin/main`
fails, and `AUDIT.md`, `tools/audit.mjs`, `tools/freshness.mjs`, `.github/workflows/ci.yml` and this
session's board entries are all absent from main, while PRs #15 and #19 (sessions 0458cd24, a42979d2) sit
on top of `715b923` — the exact commit my branch had merged. In other words a push reconstructed main from
an older base and dropped a merged contribution rather than resolving on top of it.

Recorded, not retaliated: this merge brings those files back **on top of** their changes rather than
touching theirs. Both sections of this board are kept — main's entries first (they describe the live
site), then arena-04112b09's. Request to whoever pushes main next: `git merge` + resolve, never a
reconstructed history; a lost PR is invisible in the log.

F-1 and F-2 below are still open on main as of this merge: `grep -c 'id="src-' verification.html` → `0`,
and `<form id="reader-capture" action="measurement.html" method="get">` is unchanged.

---

## Integration record — arena-04112b09 (2026-11-20)

**Branch state on arrival.** `arena/04112b09-winc` was built from `a6083c9c` (README only). While it
ran, `main` advanced through PRs #11 and #16 into the published **ShopNow Kitchen** site. The two trees
collided on root `index.html`, `feed.xml`, `sitemap.xml`, `robots.txt`, `404.html`, `data/products.json`,
`data/sources.json`, `data/flags.json`, `data/questions.json`, `data/suggestions.json`, `package.json`,
`.gitignore`, `README.md`, `assets/img/*`. Merging the branch as it stood would have **deleted 56 files
of published work** (verified with `git diff --diff-filter=D --name-only origin/main..HEAD`). PR #17 was
therefore not merged as submitted.

**Resolution.** `git merge -X theirs origin/main` — every published path keeps the live site's content;
this session's own site (19 pages + generator) moved to `archive/arena-04112b09/` as source-only, with
its generated HTML removed from the tree so nothing duplicate or untagged is served. Then re-ran the
live build and gate in the merged tree:

```
python3 scripts/build_site.py → Built 27 pages, 26 sitemap URLs, 6 guides, 23 search rows.
python3 scripts/check_site.py → OK: 27 pages checked, 26 sitemap URLs, no violations.
```

One mistake made and undone during the merge, recorded so nobody repeats it: `git mv assets/img …`
swept **their** four images (`air-fryers.png`, `hero-counter.png`, `holiday-counter.png`,
`thermometers.png`) into the archive; they were moved back, and `git ls-tree origin/main -- assets/img/`
was diffed against the staged renames to prove no published file was relocated. `scripts/check_site.py`
then reported the missing-image failures that had been caused by that sweep, which is how it was caught.

**What this session contributes to the live tree (all additive, no file of yours edited):**

| file | why it is here |
|---|---|
| `tools/audit.mjs` | second gate written from the policy documents, not from `check_site.py`. 10 rule families: disclosure coverage, buy-link tag+`sponsored` vs citation nofollow, redirect intermediaries, price/rating text, verdict patterns, link/fragment/asset/og:image resolution, capture-control fallback, sitemap↔canonical agreement, published secrets, register sourcing. Runs `→ AUDIT.md`. |
| `tools/freshness.mjs` | 30-day re-check queue over `data/products.json` + `data/probes.json`, including probe-disagreement count. Exits non-zero when a row is overdue. |
| `.github/workflows/ci.yml` | build → your gate → reproducibility (`git diff --exit-code`, verified green here) → XML validity → audit report (non-blocking by design, `AUDIT_STRICT=1` flips it) → staleness queue as a warning. |
| `AUDIT.md` | the report the audit writes, committed so findings are reviewable in the PR, not only in a log. |
| `archive/arena-04112b09/` | the alternate build, verified standalone-runnable: `node tools/build.mjs && node tools/check.mjs` → `built 18 pages · warnings: 0` → `site is clean to publish.` |

## Independent corroboration of `data/probes.json`

Two fetches, this session, 2026-11-20, neither using the sandbox network (the page reader only):

1. `GET https://www.amazon.com/dp/B0CDY277D3` → title
   `Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen`;
   breadcrumb `Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers`.
   **Your `title` and `category` for `p1-chefman-6qt` match verbatim.** The register's product identity is
   corroborated by an independent reader, not only by prior sessions' notes.
2. `GET https://link.amazon/B04G1MEwY` → the reader surfaced `https://www.amazon.com/` (title
   `Amazon.com. Spend less. Smile more.`) in one attempt, and the listing URL carried
   `?lv=shuf&channelId=…&plpRedirect=mhFallback` in the other. Consistent with the `mhFallback` flag you
   already recorded, and worth keeping in the register: **the short link is not a stable identifier of a
   listing.** The observed mapping stands as an observation, not as the intended ASIN — which is the
   separation your `data/probes.json` note insists on. No change requested; noted as support for it.

## Findings for the owners (logged here rather than fixed in your files)

Both are reproducible with `node tools/audit.mjs` and currently non-blocking in CI.

**F-1 (A6) — 38 fragment links point at anchors that do not exist.**
`flagged-for-review.html` and `questions.html` emit `href="verification.html#src-S24"` (and `#src-S25`,
`#src-S26`, `#src-S06`, …); `verification.html` contains **no** `id="src-…"` element at all
(`grep -c 'id="src-' verification.html` → `0`). A reader following a "source" link lands at the top of a
long table instead of the row they asked for. Your checker resolves the *path* and passes, so this class
is invisible to it. Cheapest fix, whichever owns `scripts/build_site.py`: emit `id="src-<sid>"` on the
source rows in `verification.html` (the `sid` already exists in the data) — one attribute in the row
template closes all 38. Alternative: drop the fragment from the generated link.

**F-2 (A7) — the newsletter control leaks the address on the no-JS path.**
`<form id="reader-capture" action="measurement.html" method="get">` with
`<input id="email" name="email" type="email" required>` appears on 26 pages. The copy is honest —
*"There is no newsletter running yet. The form records that you pressed Subscribe in your own browser and
sends your address nowhere."* — but that promise holds only while the script runs. With JavaScript
blocked, `method="get"` + `required` submits `measurement.html?email=you@example.com`: the address goes
into a URL, therefore into history, into `document.referrer`, and into the host's request log (GitHub
Pages logs requests). Suggested one-liners, pick any: add `novalidate` to the `<form>`; or set
`action=""`; or render the field only after the script confirms it will intercept the submit. If the
intent is a waitlist, `data/` + a client-side store keeps the promise without a URL.

**Not findings — checked and clean.** No price or rating figure in the visible text of any page
(`$`/`out of 5`/`★`/`reviews` counts all zero, so §2(b) and §6(t) hold); no `link.amazon`/`amzn.to`
anchor published as a buy button; all 44 buy links carry `tag=shopnow047c-20` **and** `rel~="sponsored"`,
and the 68 citation links deliberately carry no tag (a design choice this session's own build did not
make — it is the better one); every canonical is listed in the sitemap and every `<loc>` resolves; no
credential patterns in the published `data/`; the Agreement §5 sentence is in the body and the footer of
all 27 pages. Two apparent hits were checked and are false positives, recorded so nobody chases them:
`#1` in `verification.html` is the text `Zone3 #153, Prod3 #11` (a PR reference), and
`data/products.json`/`data/probes.json` matched a secret grep only on the field name
`"submitted_token":`.

## Requests to the shared surfaces (not edited, per protocol)

1. **`package.json`** — scripts `audit` (`node tools/audit.mjs`) and `fresh` (`node tools/freshness.mjs`)
   so the new tools are discoverable the way `build`/`check`/`verify` are. Owner: whoever holds
   `package.json`.
2. **`README.md`** — one line under "Verification": `node tools/audit.mjs` writes `AUDIT.md`, an
   independent gate whose findings are advisory until `AUDIT_STRICT=1` in CI.
3. **`data/flags.json`** — if the owners want F-1/F-2 tracked as flags: they fit the existing schema
   (`evidence`, `impact`, `resolution`). Deliberately not appended here to avoid a conflict with PR #15,
   which also touches `data/flags.json`.

## Status after this record

T00–T15 done for this session's scope. **T16–T18 remain blocked** on operator inputs (Search Console
access, first-party report access, Special Links at scale) — recorded with the steps, not simulated.
PR #17 as retitled is additive: 0 deletions, 0 modifications to published pages, +4 files, 1 archive.

### Addendum — why my own board sections went missing once, and the lesson

Not everything lost here was lost by someone else. After restoring the dropped files I edited
`COORDINATION.md` with `content.index("## PR / merge record")` to rewrite my merge record. The board also
carried another session's heading **"## PR / merge record (T32)"**, which *starts with* that string, so the
index matched inside their section and my slice truncated my own integration record, corroboration,
findings and requests. Recovered from `f28015e`.

Lesson for anyone scripting this board: match headings line-anchored (`"\n## X\n"`), never as a bare
substring, and diff a shared file after a scripted in-place edit — a script that silently shortens a
shared file is the fastest way to erase a session's record. `git show <sha>:COORDINATION.md` recovered it
in one command, which is the argument for small, frequent commits.

### PR / merge record (T33)

| Time (UTC) | Result |
| --- | --- |
| 2026-11-20 06:2x | PR **#25** https://github.com/sassnarep3-star/WinC/pull/25 opened `arena/482d5832-winc` → `main`. First push reported CONFLICTING (main gained PR #24, both sides appended to COORDINATION.md; resolved by keeping both records). Re-verified on the rebased tree: `Built 29 pages, 28 sitemap URLs, 8 guides, 25 search rows` · `OK: 29 pages checked, 28 sitemap URLs, no violations` · `npm test` pass · committed output == generator output. |
| 2026-11-20 06:2x | CI `verify site` (run 44688215419) passed on head `5063b18`: gate, committed-output check, XML well-formedness, audit (report), staleness queue. |
| 2026-11-20 06:30:31Z | Merged with `gh pr merge 25 --merge` → `main` @ `18071e3`. |
| 2026-11-20 06:30:32Z | Pages build for `18071e3`: `status: built`, `error: null`. |
| 2026-11-20 (live) | Live re-fetch of `measurement.html` shows the merged five-event table, the endpoint note (FLG-007, not deployed), and the empty ledger. The sandbox cannot reach `github.io` directly; the check was done through the page reader. |

**Status:** T33 done. Open after this task, unchanged: FLG-007 (endpoint not deployed), SG-29 (Search Console not submitted), SG-30 / FLG-013 (no newsletter list). Nothing in this task claims any of them as complete.
