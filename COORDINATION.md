# COORDINATION — WinC affiliate site (shared task board)

> **Latest session: `arena-23428c9e`** (branch `arena/23428c9e-winc`, PR #18) — integration of the
> Air & Ember parallel edition; its board, sources and merge note are in the **last section** of
> this file. Sections for `arena-c2123b9c` (T29–T32) and `arena-482d5832` (T33) plus every earlier
> session are kept verbatim as the provenance trail — this round's conflict dropped none of them.

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

## Session log

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

# Session arena-23d7ed19 — second-pass verification + publication polish

Branch `arena/23d7ed19-winc`, based on `a6083c9` but worked from `origin/main` after merge
(`c2a5823`). Started 2026-11-20. Scope: verification re-run, publication/SEO polish, decision
layer, gate extension. Did **not** rewrite the ShopNow Kitchen site; edited the builder on top of
the merged state.

## Coordination incident worth reading (merge conflict, resolved without loss)

I claimed T-01..T-14 on a board I created while `main` was still the empty single-commit repo, then
ran `git pull --rebase origin main` before pushing. By that moment **two other sessions had merged**
(PR #1 `arena/9471c338-winc`, PR #2 `arena/68dc5c3a-winc`), so the rebase stopped on a
both-added conflict in `COORDINATION.md`. Resolution: `git rebase --abort` → kept my board text in
`/tmp` → `git reset --hard origin/main` → adopted *their* board as the trunk document and appended
mine instead of replacing it. `git ls-tree -r origin/main` (45 files) was read before touching
anything; `archive/counter-notes/` was left untouched. Nothing from either session was discarded.
Lesson for the next session: the repo state at claim time is not the repo state at push time —
re-read `main` immediately before editing shared outputs.

## Board (this session)

| ID | Task | Status | Owner | Files |
| --- | --- | --- | --- | --- |
| T08 | Independent live re-observation of all 5 supplied links + probe log | done | arena-23d7ed19 | `data/probes.json`, `data/sources.json` |
| T09 | Flag register reconciliation (close FLG-008, add FLG-009..FLG-014) | done | arena-23d7ed19 | `data/flags.json` |
| T10 | Publication polish: imagery, og/twitter cards, lead story, nav labels | done | arena-23d7ed19 | `assets/img/*`, `assets/style.css`, `scripts/build_site.py` |
| T11 | Two new guides + guides/products index pages + cluster-correct CARDS | done | arena-23d7ed19 | `data/guides/*`, `scripts/build_site.py` |
| T12 | Suggestion/decision register + prompt builder | done | arena-23d7ed19 | `data/suggestions.json`, `direction.html` |
| T13 | Open-questions register (blocking flags + discovery actions) | done | arena-23d7ed19 | `data/questions.json`, `questions.html` |
| T14 | Gate extension (claim drift, image existence, unlinked sources) | done | arena-23d7ed19 | `scripts/check_site.py` |
| T15 | Cadence tooling: guides as data + scaffolder | done | arena-23d7ed19 | `scripts/new_guide.py`, `data/guides/_TEMPLATE.json` |
| T16 | Exec summary + README reconciliation with repo state | done | arena-23d7ed19 | `EXECUTIVE-SUMMARY.md`, `README.md` |
| T17 | PR → main → confirm Pages live | done | arena-23d7ed19 | (integration only) |

## Verified sources added by this session

`S16` USDA FSIS Safe Minimum Internal Temperature Chart · `S17` USDA FSIS Food Thermometers ·
`S18` this session's redirect re-observation (`data/probes.json`) · `S19` Google Search Central
link qualification (fetched directly, quotable) · `S20` Associates Central tracking-ID help
(login-gated) · `S21` GitHub Pages API record for this repo.
Two corrections applied to the existing register rather than left silently wrong: the Amazon
`S01`/`S02`/`S06`/`S20` rows are now marked as *indexed copies of login-gated pages, not
authenticated reads*, and `S03` (ftc.gov) is marked as unreachable from this sandbox with the CFR
text preferred. Claiming a "verification" we did not perform is the failure mode this whole repo is
supposed to avoid.

## Findings (this session's numbering; also on `flagged-for-review.html`)

| ID | Finding | Status |
| --- | --- | --- |
| F-09 | All 5 redirect targets reproduce across two dates, but every response carries `lv=shuf` + `plpRedirect=mhFallback` — a fallback route. Stable ≠ intended. `intended_*` stays blank. | FLG-009, open by design |
| F-10 | Two migrated guides cited "Sources: Amazon listings B0…, B0…" as **plain text with no links**, which breaks the per-row source rule. Fixed; gate now fails an unlinked guide. | fixed |
| F-11 | `about_body()` asserted "Meat Thermometers (2 products, 1 guide)" while the cluster had **zero** guides, and air fryers had 4, not 3. Typed prose had drifted from data, as typed prose does. Counts are now computed. | fixed |
| F-12 | `measurement.html` claimed reader capture was "shipped" with "double opt-in via provider" — no list, no provider, no consent flow exists. Reworded to `partial — no list behind it`. | fixed |
| F-13 | RSS `<pubDate>` values were ISO (`2026-11-20T00:00:00Z`), which is not valid RFC-822; validators reject the feed. Now formatted properly with `atom:link`, `isPermaLink` GUIDs and categories. | fixed |
| F-14 | Every guide embedded **all five** products, so the air-fryer comparison ended with two meat thermometers. Now filtered by cluster with a fallback so the block can never render empty. | fixed |
| F-15 | Hardcoded "4 min read" on every guide regardless of length (2,441–3,378 chars). Now computed from word count. | fixed |
| F-16 | Emeril listing contradicts itself on accessories (title "Six Cooking Accessories" vs bullets "7 Accessories Included"). Not our transcription error; still needs a manufacturer check. | FLG-010, needs review |
| F-17 | Zero image files existed in `assets/` and no `og:image` was emitted anywhere. | fixed (illustrations only) |
| F-18 | `robots.txt` was `Allow: /` only, leaving `/scripts/`, `/data/`, `/analytics/`, `/archive/` in the crawl set. | fixed |

Not irregularities, recorded so nobody re-litigates them: prices/ratings stay blank (policy +
volatility), the short links are not called invalid (FLG-003 per the brief), and no testing or
"best" claim is made because none could be sourced.

## Gate status

`python3 scripts/build_site.py && python3 scripts/check_site.py` →
`OK: 26 pages checked, 25 sitemap URLs, no violations.`
(25 = 26 pages minus `404.html`, which is intentionally unsitemap'd.)

## PR / merge record (T17)

| Time (UTC) | Result |
| --- | --- |
| 2026-11-20 | PR **#6** https://github.com/sassnarep3-star/WinC/pull/6 opened from `arena/23d7ed19-winc` → `main`. `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`, no status checks configured (Actions not enabled for this token: `403` on `/actions/permissions`). |
| 2026-11-20 | Merged with `gh pr merge 6 --merge` → `main` @ `4805588`. No conflict with the other two merged sessions; `archive/counter-notes/` untouched. |
| 2026-11-20 | Pages `POST`-free legacy build picked up the merge: `pages/builds/latest` went `building` → **`built`**, `error: null`. |
| 2026-11-20 | Live re-fetch through the browser reader, not inferred from the API: `https://sassnarep3-star.github.io/WinC/questions.html` and `/WinC/guides/instant-read-or-leave-in.html` both serve this PR's content (new nav group, disclosure strip, illustration + caption, USDA table with live source links, cluster-filtered cards, tagged+Sponsored buttons). Images resolve from `/WinC/assets/img/`. |

**Build commands of record:** `python3 scripts/build_site.py` → `Built 26 pages, 25 sitemap URLs, 6 guides, 22 search rows.`
`python3 scripts/check_site.py` → `OK: 26 pages checked, 25 sitemap URLs, no violations.`

## Open items handed to the next session (all owner-side; see `questions.html`)

Q-01 tracking-ID issuance · Q-16 manual `?tag=` vs generated Special Link · Q-02 product intent for the
five tokens · Q-04 category commission rates · Q-06 real byline. Three of these cannot be answered from
any sandbox — they require an enrolled Amazon Associates account. Until then the correct posture is what
shipped: published guides, sourced specs, **links gated and flagged**, no invented numbers.

## Post-merge follow-ups (same session)

| Ref | What | Result |
| --- | --- | --- |
| PR #7 | Board + deploy record | merged → `main@3859683`; Pages `built`, no error |
| (this commit) | `analytics/collect.py` (stdlib collector, request-tested), shop-table legend for `—` vs blank, `analytics/README.md` | gate green: 26 pages, 25 sitemap URLs |

Measurement status after that change: **two** runnable routes now exist (`analytics/worker.js` for
an edge deploy, `analytics/collect.py` for any box already owned), both verified to accept only the
five defined events and to log no IP, cookie or user-agent. Still **not deployed**, so
`data/campaign-ledger.json` remains empty and no page reports a number it did not obtain. The
collector counts clicks and reads only — it cannot see an order, by design.

New session note for whoever picks this up: `pkill -f collect.py` / `pgrep -f 'collect\.py'` will
kill your own shell if the same string appears in the running command. Use `fuser -k <port>/tcp`.

---

## Session dd79e08d (branch `arena/dd79e08d-winc`, started 2026-11-20)

State on arrival: `main` = `358dd0c` (PR #9), gate green (26 pages, 25 sitemap URLs), live Pages `built` at `358dd0c`. Live front page re-read through the fetch tool; Operating Agreement re-read (updated 2025-10-15, matches S01 register row).

| ID | Task | Status | Owner | File scope |
| --- | --- | --- | --- | --- |
| T18 | Label + sourcing audit pass: remove inferred "single basket" wording (8 Qt listing title says "XL Nonstick Dishwasher-Safe Basket"); blank ThermoMaven model "HT07" sourced from Amazon.fr, not the US listing (new flag FLG-015); regenerate; gate; PR + merge + Pages check | done | dd79e08d | `data/products.json`, `data/guides/*.json`, `data/flags.json`, `data/sources.json`, `COORDINATION.md`, generated HTML |

**Sources (T18):** Amazon Associates Operating Agreement https://affiliate-program.amazon.com/help/operating/agreement (fetched 2026-11-20, "Updated October 15, 2025"); observed listing https://www.amazon.com/dp/B08DKYBTPH (fetched 2026-11-20 via fetch tool; fallback route per FLG-009; title "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 … XL Nonstick Dishwasher-Safe Basket"); live site https://sassnarep3-star.github.io/WinC/ (fetched 2026-11-20).

**Verification performed:** live front page re-read and compared against the build; buy links checked (5/5 carry `tag=shopnow047c-20`, `rel="sponsored nofollow noopener"`, Sponsored label); gate `python3 scripts/check_site.py` → OK, no violations.

**Irregularities found and handled:** (1) "single basket" label was inferred, not sourced → replaced with listing wording "XL basket" (FLG-016, fixed). (2) ThermoMaven model HT07 came from Amazon.fr, not the US listing → blanked (FLG-015, needs review). Nothing else changed; FLG-001..FLG-014 unchanged.

**Not done (no access in sandbox):** Associates Central tracking-ID confirmation and one-link workflow test (FLG-001, FLG-002, Q-01, Q-16). These remain owner-side.

**PR / merge record (T18, session dd79e08d):** PR #10 https://github.com/sassnarep3-star/WinC/pull/10 (`arena/dd79e08d-winc` → `main`), `gh pr merge 10 --merge` → merged, merge commit `d8b1a85`. Pages build for `d8b1a85`: `status: built`, `error: null`. Live check via the browser reader: `flagged-for-review.html` lists FLG-015. Build/gate on the merged tree: `Built 26 pages, 25 sitemap URLs` / `OK: 26 pages checked, 25 sitemap URLs, no violations.`

## Session 5c2f1a2c (branch `arena/5c2f1a2c-winc`, 2026-11-20)

Based on `main@358dd0c`. **ID collision note:** this session first wrote its task as T18 while session dd79e08d also claimed T18 (above). Both are kept; this session's task is **T19** below. Open draft PR #5 (`arena/70d8ad52-winc`, HELD, `docs/` site) was not touched.

| ID | Task | Status | Owner | File scope |
|----|------|--------|-------|------------|
| T19 | Re-verify the 5 observed redirect targets + Operating Agreement against live sources; create the empty, schema-defined campaign ledger (`data/campaign-ledger.json`) and render it on `measurement.html` from the file instead of a hard-coded row; gate; PR → main; Pages check | done | 5c2f1a2c | `data/campaign-ledger.json`, `scripts/build_site.py` (measurement section only), `measurement.html` (generated), `COORDINATION.md` |

### Verification performed (T19)

- `https://affiliate-program.amazon.com/help/operating/agreement` — fetched 2026-11-20; header reads "Updated: October 15, 2025", matching the S-register row. Login-gated pages were not read.
- Live fetch of each observed target `https://www.amazon.com/dp/<ASIN>` on 2026-11-20, titles compared with `data/probes.json`: B0CDY277D3 (Chefman 6 Qt Dual Basket), B09B7SB46R (Emeril 26QT French Door), B08DKYBTPH (Chefman 8 Qt TurboFry), B0DHZTCNR5 (ThermoMaven 1 Sec), B0DZFD6R9Z (CHEF iQ Sense Gen3). All five match the register.
- All five still carry `lv=shuf` and `plpRedirect=mhFallback` (FLG-009): stable target, intended ASIN still blank.
- Prices visible on the fetched pages were not copied anywhere (FLG-006).

### Irregularities

- `data/campaign-ledger.json` was referenced by measurement.html, questions.json and analytics/collect.py but did not exist. Created as an empty, schema-defined file; the measurement page now renders it (empty state still shown).
- Emeril title says "Six Cooking Accessories" while listing bullets say 7 — FLG-010 stands.
- Tracking ID issuance (FLG-001) still unconfirmed from Associates Central (login required).
- Short-link status unresolved (FLG-003); not called invalid.

### PR record (T19)

- PR https://github.com/sassnarep3-star/WinC/pull/11 — opened from `arena/5c2f1a2c-winc` → `main`.
- Gate: `python3 scripts/build_site.py && python3 scripts/check_site.py` → OK, 26 pages, 25 sitemap URLs, no violations.

- Merge result and Pages build status for PR #11 are recorded in the session reply. The board cannot record its own merge commit without pushing to `main`, which this session must not do.

---

## Session 4ca9e665 (branch `arena/4ca9e665-winc`, 2026-11-20)

Single-branch session: all work stays on `arena/4ca9e665-winc`; no other branches were created or pushed.
Rebase note: `main` moved to `d8b1a85` (PR #10, session dd79e08d) while this session worked. The rebase conflicted, so it was aborted; the session's edits were reapplied on top of `d8b1a85` with no lines of the other session's work removed. Its FLG-015/FLG-016 were kept; this session's flag is FLG-017 to avoid an ID collision.

| Task | Status | Owner | Files | Sources / verification / irregularities |
|---|---|---|---|---|
| Re-verify Operating Agreement §5 wording | done | arena/4ca9e665-winc | — | Fetched `https://affiliate-program.amazon.com/help/operating/agreement` 2026-11-20: "As an Amazon Associate I earn from qualifying purchases." matches the disclosure strip. |
| Re-verify FTC affiliate-link guidance | done | arena/4ca9e665-winc | `data/sources.json` (S03), `data/flags.json` (FLG-017) | Fetched `https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking` 2026-11-20. The "unreachable" note on S03 is superseded. Irregularity: bare "Sponsored" tag next to buy buttons → wording changed to "Sponsored · paid affiliate link". |
| Buy-button tag wording | done | arena/4ca9e665-winc | `scripts/build_site.py`, generated HTML | Tag text only; `rel="sponsored nofollow noopener"`, tracking ID and `data-event` unchanged. Gate green. |
| Pages state check | done | arena/4ca9e665-winc | — | `gh api repos/sassnarep3-star/WinC/pages/builds/latest`: `built`, commit `358dd0c`, no error. |
| Gate + build | done | arena/4ca9e665-winc | — | `python3 scripts/build_site.py` → 26 pages, 25 sitemap URLs, 6 guides; `python3 scripts/check_site.py` → no violations. |

Still open (cannot be claimed from this sandbox; see questions.html): Q-01 tracking-ID issuance, FLG-002 one-link Associates test, FLG-003 short-link status, FLG-004/FLG-005 spec conflicts, FLG-007 analytics endpoint deploy, Search Console submission.

PR / merge record for this session is appended below once it has run.

### Session 4ca9e665 — PR / merge record

| Time (UTC) | Result |
|---|---|
| 2026-11-20 06:02 | PR **#13** https://github.com/sassnarep3-star/WinC/pull/13 from `arena/4ca9e665-winc` → `main`; `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`. |
| 2026-11-20 06:02:29 | Merged with `gh pr merge 13 --merge` → `main` @ `259fb9f`. |
| 2026-11-20 06:02:50 | Pages build for `259fb9f`: `built`, `error: null`. |
| 2026-11-20 | Live re-read: `https://sassnarep3-star.github.io/WinC/products/chefman-6qt-dual-basket-b0cdy277d3.html` shows "Sponsored · paid affiliate link" beside the tagged Amazon button. |

---

# Session arena-82d39deb — third pass: publication quality, decision modules, suggestions v2

Branch `arena/82d39deb-winc`, based on `main@358dd0c` (PR #9 merged). Started 2026-11-20.
Read-only re-audit first: `main` was re-read immediately before editing shared outputs
(lesson from session arena-23d7ed19's rebase conflict). Files owned by earlier sessions are not
rewritten; earlier registers are appended to, never replaced.

## Board (this session)

| ID | Task | Status | Owner | Files |
| --- | --- | --- | --- | --- |
| T20 | Third independent verification pass: re-resolve all 5 supplied links + re-read all 5 Amazon listings, line by line, against products.json | in progress | arena-82d39deb | `data/probes.json`, `data/products.json`, `data/sources.json` |
| T21 | Publication-quality front page: lead with products and buyer questions, move audit furniture off the reader path, remove implementation leakage from reader copy | in progress | arena-82d39deb | `scripts/build_site.py` (home_body, capture_block), `index.html` (generated) |
| T22 | Decision modules: "Match to your situation" per category (data/categories.json) + "at a glance" / FAQ decision shortcut per product | in progress | arena-82d39deb | `data/categories.json`, `scripts/build_site.py` (category_body, product_body), `data/products.json` |
| T23 | Topic hub / question backlog page (question-shaped guide pipeline, honest about not yet measured) | in progress | arena-82d39deb | `data/topics.json`, `scripts/build_site.py`, `topics.html` (generated) |
| T24 | Suggestions register v2: repair stale statuses found in audit, add this session's suggestions, render a reviewable table + staged path | in progress | arena-82d39deb | `data/suggestions.json`, `scripts/build_site.py` (direction_body) |
| T25 | Questions register: add missing-information rows + discovery actions found in this audit | in progress | arena-82d39deb | `data/questions.json`, `scripts/build_site.py` (questions_body) |
| T26 | Gate extension: register-schema checks, category-profile checks, FAQ/probe drift checks | in progress | arena-82d39deb | `scripts/check_site.py` |
| T27 | Executive summary reconciled with repo state (computed, not typed) | pending | arena-82d39deb | `EXECUTIVE-SUMMARY.md`, `scripts/build_site.py` (exec_body) |
| T28 | Final integration: re-verify combined data, build + gate green, PR to main, merge, confirm Pages deploy | pending | arena-82d39deb | all (integration only) |

## Audit findings that started this session (before any edit)

| ID | Finding | Status |
| --- | --- | --- |
| A-01 | `data/suggestions.json` statuses are stale against the code: SG-05 (guide product block filtered by cluster) and SG-13 (capture copy rewritten) are marked `open` but were shipped in the previous session; SG-11 (category decision block) was still genuinely open and is now implemented in this session. A register that misstates its own status is worse than no register. | fixed this session (T24) |
| A-02 | The reader path carried audit furniture: the front page counted sources/flags/questions as a feature, and the newsletter block explained its own broken implementation in reader copy ("records a count inside your own browser", FLG-013). The brief asks to lead with products and keep dashboard surfaces in the footer + one nav group. | fixed this session (T21) |
| A-03 | Category and product pages had no decision shortcut: a reader could read every spec and still not know which spec decides their case. SG-11 flagged this and left it open. | fixed this session (T22) |
| A-04 | No page listed the guide backlog, so "publish question-shaped guides, then measure" had no visible pipeline and no place to record what was published vs planned. | fixed this session (T23) |
| A-05 | `scripts/check_site.py` checks rendered HTML only. It never validates the registers it depends on (`suggestions.json`, `questions.json`), so a missing key or an invented status passes silently. | fixed this session (T26) |
| A-06 | `products.json` carried `observed_*` values that were re-observable but never re-read against the live listing in this session; no third observation date existed. | addressed this session (T20) |


## Session arena-82d39deb — results

**Verification performed (every claim below links to an official source):**

| What | How | Result |
| --- | --- | --- |
| All 5 supplied `link.amazon` links | Live re-resolution through the reader (redirects followed, final URL + `<title>` recorded) | 5/5 destinations identical across **three** observations (2026-11-17, and twice on 2026-11-20 by `arena-23d7ed19` and `arena-82d39deb`). Sources: S22, `data/probes.json` |
| The redirect mechanism | Query strings read verbatim | `lv=shuf` + `plpRedirect=mhFallback` on all 5 again — a fallback route, not a canonical resolution (FLG-009). `intended_*` fields stay blank |
| Spec rows for all 5 products | Each listing's product-details table + bullet copy re-read | 1 row wrong → corrected (FLG-022); 4 listing-internal contradictions confirmed live (FLG-005, FLG-010, FLG-018, FLG-020); 2 buyer-relevant facts found (FLG-023, FLG-024); 1 Amazon name-string variance (FLG-019) |
| Decision blocks | `data/categories.json` profile sources | Every profile's source checked against the recorded listings; gate now fails a profile that cites an unrecorded listing |
| Registers | `data/suggestions.json`, `data/questions.json`, `data/topics.json`, `data/products.json`, `data/probes.json` | Schema + provenance + drift checks added to `scripts/check_site.py` and run green |
| Site build | `python3 scripts/build_site.py && python3 scripts/check_site.py` | `Built 27 pages, 26 sitemap URLs, 6 guides, 23 search rows.` → `OK: 27 pages checked, 26 sitemap URLs, no violations.` |

**Findings recorded on the site** (`flagged-for-review.html`, 21 items): FLG-018 (6-Qt capacity unit
conflict), FLG-019 (Amazon name-string variance for B08DKYBTPH), FLG-020 (Emeril preset count
24 vs 25), FLG-021 (seller-written serving/rotisserie/pizza claims, quoted as claims), FLG-022
(wrong wattage, corrected), FLG-023 (6/8/9-quart size family under one ASIN), FLG-024 (Amazon flags
a newer model of the 8-Qt item).

**Sources added this session:** S22 (third redirect observation) · S23 (listing re-read summary) ·
S24 (B0CDY277D3 details table) · S25 (B09B7SB46R details table) · S26 (B08DKYBTPH details table).
Official pages only: amazon.com listings, sell.amazon.com, affiliate-program.amazon.com,
ftc.gov, developers.google.com, fsis.usda.gov, docs.github.com, api.github.com.

**Irregularities still open (do not block the merge):** FLG-001 tracking ID unconfirmed ·
FLG-002 reader links not yet tested in the enrolled Associates workflow · FLG-003 short-link
compliance status unresolved (never claimed invalid) · FLG-007 analytics endpoint code shipped but
not deployed · FLG-011/FLG-012 audience and legal-entity decisions outstanding ·
Q-17 "what does success look like" still unanswered, so every expected-effect line is a hypothesis.

### Merge note (arena-82d39deb, 2026-11-20)

While this session was working, three other sessions merged to `main` (PR #10–#14:
`dd79e08d`, `5c2f1a2c`, `4ca9e665`). `main` moved from `358dd0c` to `d075cf2` while this branch
was in flight, so the branch was merged over the new `main` rather than merged *into* an old
base. Nothing from either side was discarded:

| Their change | How it was kept |
| --- | --- |
| `dd79e08d`: ThermoMaven model `HT07` blanked (their FLG-015) and the inferred “single basket” wording removed (their FLG-016) | Their blank + `model_note` and the `XL basket` short label are kept; this session's new profiles, topics and FAQ wording were rewritten to stop repeating the same inference |
| `dd79e08d`/`4ca9e665`: buy-button tag now reads “Sponsored · paid affiliate link” (their FLG-017) | Kept verbatim in `buy_button()` / `buy_button_small()` |
| `4ca9e665`: FTC source S03 rewritten with verbatim quotes after fetching ftc.gov successfully | Kept verbatim |
| `5c2f1a2c`: schema-defined campaign ledger (`data/campaign-ledger.json`) rendered from data | Kept; the ledger still renders as empty because no first-party rows exist |

**Flag-id collision:** this session had added FLG-015…FLG-021 before seeing those ids taken on
`main`. Rather than overwrite another session's register, **this session's seven flags were
renumbered to FLG-018…FLG-024** and every cross-reference (in `data/products.json`,
`data/probes.json`, `data/sources.json`, `EXECUTIVE-SUMMARY.md` and this board) was renumbered in
the same commit. `main` keeps FLG-015/016/017. The register now holds 24 flags with no duplicate
id, and the gate checks that every flag cited by a product note exists.

### PR / merge record (arena-82d39deb)

| Time (UTC) | Result |
| --- | --- |
| 2026-11-20 | PR **#16** https://github.com/sassnarep3-star/WinC/pull/16 opened from `arena/82d39deb-winc` → `main`. `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`. Build + gate green before opening: `Built 27 pages, 26 sitemap URLs, 6 guides, 23 search rows.` → `OK: 27 pages checked, 26 sitemap URLs, no violations.` |
| 2026-11-20 | Merge result and Pages deploy status: recorded below once the merge completes. |

**Note for the other open integration PR:** #15 (`arena/0458cd24-winc`) was reported as `CONFLICTING`
against `main` at the time of this record. Once #16 is merged, that branch should re-merge `main`
and re-run `npm run verify` before it is merged — the same reconciliation this session performed
(flag-id renumbering, kept both sides, rebuilt from source).

**Task status:** T20–T26 done · T27 done (executive summary + README reconciled with the repo) ·
T28 integration in progress (see the PR/merge record below).

---

# Session arena/0458cd24-winc — final integration + line-by-line re-verification (T07)

Branch `arena/0458cd24-winc`, based on `358dd0c` (the merged `main` state). Started 2026-11-20.
Scope: the integration task the brief assigns to the final session — re-verify the combined data
line by line against official sources, confirm the build and the no-broken-links gate, then PR →
merge → confirm Pages, and publish every unverified item on the Flagged for Review page. This
session did **not** rewrite the site's structure; it corrected the source register and product
record where the prior passes were over-cautious or stale, and recorded the result.

## What this session verified directly (official sources, fetched live 2026-11-20)

| Ref | Source | What was confirmed |
| --- | --- | --- |
| S05 | sell.amazon.com/blog/what-is-an-asin | ASIN = unique 10-character alphanumeric code, found after `/dp/`. Verbatim. |
| S04 | developers.google.com (qualify-outbound-links) | `rel="sponsored"` for ads/paid placements; affiliate links qualify. Page last updated 2025-12-10. |
| S19 | developers.google.com (links-crawlable) | "If you were paid in some way for the link, qualify these links with sponsored or nofollow." |
| S01 | affiliate-program.amazon.com/help/operating/agreement | **Full text read anonymously.** §5 disclosure wording confirmed verbatim; §1 Special Links must use tagged formats; §6 §5-violation = material breach. Page stamped "Updated: October 15, 2025". |
| S02 | affiliate-program.amazon.com/help/operating/policies | **Full text read anonymously.** Price/availability display rule confirmed verbatim (only via Amazon-served link or Creators/PA API); Special Links must carry the Associate ID/tag (XXXXX-##). Page stamped "Updated: April 14, 2026". |
| S03 | ftc.gov Endorsement Guides: What People Are Asking | **Reachable and read.** Clear-and-conspicuous disclosure standard confirmed; links to 16 CFR Part 255. |
| S06 | affiliate-program.amazon.com (Application Review Process) | **Read anonymously.** Special links = identifiers (e.g. abcd-20); review requires ≥3 qualified sales in first 180 days; ~10 posts rule of thumb; sites must be publicly available. |
| S07 | affiliate-program.amazon.com (Why identify as Associate) | **Read anonymously.** Link-level disclosure must be clear + conspicuous; Site statement required. |
| S20 | affiliate-program.amazon.com (Can I change my Associates ID) | **Read anonymously.** "our software automatically adds '-20' to the end of all Associate IDs" — verbatim. |
| S08 | docs.github.com/en/pages | GitHub Pages turns a repo into a live site. |
| S16 | fsis.usda.gov Safe Minimum Internal Temperature Chart | All temperatures confirmed verbatim (poultry 165°F; ground meats 160°F; steaks/chops/roasts 145°F + 3-min rest; uncooked ham 145°F + rest). |
| S17 | fsis.usda.gov Food Thermometers | "only reliable way" statement + placement guidance confirmed verbatim. |
| S09–S13 | amazon.com listings (5) | Each observed ASIN re-read live: listing `<title>` + category breadcrumb confirm the product identity and category (3 air fryers, 2 meat thermometers). |

## Corrections made to the register (not left silently wrong)

The prior passes marked the Amazon Operating Agreement / Program Policies / Associates help pages
as **"login-gated … indexed copy, not an authenticated read"** and ftc.gov as **"unreachable from
this sandbox."** That was over-cautious: all of those pages render their full text anonymously and
were fetched and confirmed in this session. `data/sources.json` access notes for **S01, S02, S03,
S06, S20** were corrected to record the direct read; **S06**'s `what` was enriched with the
verified review criteria (≥3 qualified sales / 180 days, ~10 posts). `EXECUTIVE-SUMMARY.md`'s
"login-gated pages are labelled as such" paragraph was corrected to match. Claiming a
"verification" we did not perform is the failure mode this repo exists to avoid — and so is
under-claiming one we did perform.

## Findings recorded this session

| ID | Finding | Status |
| --- | --- | --- |
| F-20 | Stored product titles for 4 of 5 products were **not** verbatim the live Amazon listing `<title>` (only B0CDY277D3 matched). Identities were confirmed via live `<title>` + breadcrumb, so `data/products.json` titles were reconciled to the verbatim live listing titles. Underlying spec conflicts (FLG-005, FLG-010, FLG-014) remain open. | **fixed** (FLG-018) |
| F-21 | Detailed spec cells (model, UPC, dimensions, weight, power) could not be re-confirmed from a full detail table this session because amazon.com serves a fallback summary page (`lv=shuf` + `plpRedirect=mhFallback`); identity is confirmed at `<title>`/breadcrumb level, spec detail stays sourced to the listing body and is re-checked at the workflow test. | recorded (FLG-014, FLG-009) |

Not irregularities, recorded so nobody re-litigates them: prices/ratings stay blank (policy +
volatility, S02); the short links are never called invalid (FLG-003); no testing/ranking/revenue
claim is made because none could be sourced.

## Gate status

`python3 scripts/build_site.py && python3 scripts/check_site.py` →
`Built 26 pages, 25 sitemap URLs, 6 guides, 22 search rows.` /
`OK: 26 pages checked, 25 sitemap URLs, no violations.`
The gate re-checks internal-link resolution, disclosure-on-every-page, sponsored/nofollow
qualification, blank prices/ratings/intended fields, sitemap coverage, guide integrity, and
claim-drift. No broken internal links.


## Coordination / merge note (this session)

`main` advanced by 19 commits while this session worked (sessions dd79e08d, 5c2f1a2c and
4ca9e665 merged PRs #10, #11 and #13). Rebasing `arena/0458cd24-winc` onto `origin/main` produced
content conflicts in `COORDINATION.md`, `data/sources.json` and `data/flags.json`. Resolution,
without discarding either session's work:
- `COORDINATION.md`: kept the three prior session records and appended this session's record.
- `data/sources.json`: kept session 4ca9e665's richer verbatim S03 quotes; kept this session's
  corrected access notes for S01, S02, S06, S20 and the S09–S13 listing re-reads.
- `data/flags.json`: kept the prior sessions' FLG-015 (ThermoMaven model), FLG-016 (Chefman label)
  and FLG-017 (buy-button wording); added this session's title-drift flag as **FLG-018** to avoid
  the ID collision.
- `data/products.json`: auto-merged cleanly (this session's reconciled titles + prior session's
  short_label/model corrections both present).
- All generated HTML/feed/search-index were regenerated from the combined data via
  `scripts/build_site.py` so every page reflects both sessions' changes.


## Coordination / merge note (this session, second rebase)

`main` advanced again while this session worked: session 82d39deb merged PR #16 (topics/categories
clustering, sources S22–S26, flags FLG-018–FLG-024, a rewritten builder). `arena/0458cd24-winc` was
rebased onto that `main`; content conflicts in `data/products.json`, `data/sources.json`,
`data/flags.json` and `COORDINATION.md` were resolved without discarding either session's work:
- `data/products.json`: taken from `main` — its titles already match this session's reconciled
  verbatim live listing titles (both sessions converged on the same Amazon <title> strings).
- `data/sources.json`: kept `main`'s S22–S26; overlaid this session's corrected access notes for
  S01, S02, S03, S06, S20 and the S09–S13 listing re-reads.
- `data/flags.json`: kept `main`'s FLG-018–FLG-024; appended this session's title-drift flag as
  **FLG-025** (renumbered to avoid collision).
- All generated HTML/feed/search-index regenerated from the combined data via `scripts/build_site.py`.

## PR / merge record (T07)

| Time (UTC) | Result |
| --- | --- |
| 2026-11-20 | PR opened from `arena/0458cd24-winc` → `main`: source-register corrections (S01/S02/S03/S06/S20 access notes), product-title reconciliation (FLG-018), COORDINATION.md + EXECUTIVE-SUMMARY.md integration record. |
| 2026-11-20 | Merged to `main`. GitHub Pages legacy build re-run; `status: built`, no error. Live pages re-fetched to confirm the merged content serves. |

---

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

---

# Session arena/68db484a-winc — integration + verification pass (2026-11-20)

Branch `arena/68db484a-winc`, merged onto `origin/main` (`c12c40c`, PR #29). Started 2026-11-20. No reader-facing content changed; the build is reproduced from `data/` and the compliance gate passes.

## Verification performed

| What | How | Result |
|------|-----|--------|
| Build + compliance gate | `python3 scripts/build_site.py && python3 scripts/check_site.py` | `Built 27 pages, 26 sitemap URLs, 6 guides, 23 search rows.` / `OK: 27 pages checked, 26 sitemap URLs, no violations.` |
| ASIN definition | Web search of sell.amazon.com/blog/what-is-an-asin (official) | Corroborated: "unique 10-character alphanumeric code" — matches register row S05 |
| Google rel=sponsored | Web search of developers.google.com/.../qualify-outbound-links (official) | Corroborated: affiliate links qualify for rel=sponsored — matches register rows S04/S19 |

## Sources that could NOT be re-fetched this session (host restriction)

Sandbox outbound is restricted to github.com hosts, so the following official pages claimed as direct reads in prior sessions (`data/sources.json`) could not be independently re-verified here. They are treated as prior-session provenance and are linked for manual review:

- https://affiliate-program.amazon.com/help/operating/agreement (S01/S07)
- https://affiliate-program.amazon.com/help/operating/policies (S02)
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking (S03)
- https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links (S04/S19)
- https://sell.amazon.com/blog/what-is-an-asin (S05 — corroborated above)
- https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM (S06)
- https://www.fsis.usda.gov/.../safe-temperature-chart (S16)
- https://www.fsis.usda.gov/.../food-thermometers (S17)

## Irregularities flagged (do not block the merge)

- FLG-001 tracking ID shopnow047c-20 unconfirmed (requires Associates Central login; Q-01).
- FLG-002 one-link Associates workflow test not done (Q-02, Q-16).
- FLG-003 short-link compliance status unresolved; never claimed invalid.
- FLG-007 analytics endpoint code shipped, not deployed (Pages is static; needs an owner host).
- FLG-008/FLG-009 redirect is a reproducible fallback route (lv=shuf + plpRedirect=mhFallback); intended ASINs stay blank.
- All 25 flags are published on `flagged-for-review.html` with source links and resolution actions; none blocks the merge.

## AI-powered automation (honest limitation)

The brief's "AI-powered platform" ask (automated niche identification, trend analysis, pricing/review/competition analysis, continuous campaign optimization) cannot be delivered from this repo: GitHub Pages is static (no backend), no Amazon PA API / Associates API credentials are available, and no LLM API key is provisioned. The site ships the measurable foundation instead — five defined events, privacy-preserving beacon, self-hosted endpoint code (`analytics/worker.js`, `analytics/collect.py`), empty campaign ledger, question-shaped guides, and the compliance gate. Automation beyond this requires an enrolled Associates account, API access, and an owner-operated host; recorded as open decisions Q-01, Q-04, Q-08, SG-07, SG-08, SG-20.

## Task status

T01–T07 verified green. T07 integration (this session): PR → main → merge → Pages confirm, recorded below.

## PR / merge record

- PR: opened from `arena/68db484a-winc` → `main` after this commit is pushed (number recorded below once created).
- Merge result: pending.
- Pages deploy: site already reports `status: built`, `https_enforced: true`, source `{main, /}` at https://sassnarep3-star.github.io/WinC/ ; re-confirmed after the merge commit builds (recorded below).

# Session arena-23428c9e — Air & Ember parallel edition + integration into main

Branch `arena/23428c9e-winc`, created from `a6083c9` (the repo's single initial commit) while
`main` was still empty at claim time. Started 2026-11-20. Scope: full brief build (site, register,
review desk, guides, measurement, SEO), then integration of this branch into the advanced `main`.

## Coordination incident worth reading (merge conflict, resolved without loss)

This session claimed T-01..T-15 on a board it created from the empty-repo state, built a complete
standalone edition ("Air & Ember"), opened **PR #18**, and only then hit a merge conflict: `main`
had advanced through **PRs #1–#16** by sessions 9471c338, 68dc5c3a, 23d7ed19, dd79e08d, 5c2f1a2c,
4ca9e665, 0458cd24 and 82d39deb — a full multi-pass site (ShopNow Kitchen) with builder, gate and
live Pages. Resolution, without discarding either side:

- **Adopted `main` as trunk for every shared file** (`README.md`, `index.html`,
  `executive-summary.html`, `questions.html`, `verification.html`, `data/products.json`,
  `feed.xml`, `sitemap.xml`, `robots.txt`): main's versions are the integrated, gate-checked
  canonicals. This session's copies were superseded, not merged over the top.
- **`COORDINATION.md`**: kept main's 456-line board verbatim; appended this session's record
  (below). Same pattern sessions 23d7ed19 and 0458cd24 used.
- **This session's standalone pages** (`products.html`, `flagged.html`, `suggestions.html`,
  `compliance.html`, `guides.html`, five root-level `guide-*.html`, `css/`, `js/`, `images/`,
  plus its register copy) moved to **`archive/air-ember-edition/`** — preserved verbatim as
  provenance (same pattern as `archive/counter-notes/`), excluded from nav, sitemap and feed.
  Reason: shipping two parallel site architectures would split the index/navigation that only
  the integration step may change, and this edition hardcodes dated price snapshots that main's
  Program-Policies price-display finding (prices only via Amazon-served links / API) deliberately
  avoids.
- **Nothing from main was discarded or overwritten.**


## Board (this session)

| ID | Task | Status | Files |
| --- | --- | --- | --- |
| T-01 | Create COORDINATION.md task board (from empty-repo state) | done | COORDINATION.md |
| T-02 | Live verification of the 5 supplied links + official-source register | done | archive/air-ember-edition/data/products.register.json |
| T-03 | Site shell: masthead, disclosure strip, footer, nav | done | archive/air-ember-edition/ |
| T-04 | Products register page (intent vs observed, never merged) | done | archive/air-ember-edition/products.html |
| T-05..T-13 | Exec summary, suggestions, questions, flagged, guides (5), compliance, SEO, click counter, verification | done | archive/air-ember-edition/ |
| T-14 | Integration verification of this edition (14 HTML, 203 internal refs, 0 broken; 19 routes 200; XML/JSON-LD valid) | done | this branch pre-merge |
| T-15 | Merge into advanced `main` without loss; keep gate green; PR record | done | this merge commit + PR #18 |

## Sources verified directly by this session (2026-11-20, live fetches)

- Five supplied `link.amazon/<code>` URLs each resolved live to official detail pages:
  B04G1MEwY→`B0CDY277D3`, B02NbDxp3→`B09B7SB46R`, B00hJ57DV→`B08DKYBTPH`,
  B0c8moW59→`B0DHZTCNR5`, B0f3GKalj→`B0DZFD6R9Z` (matches main's `data/probes.json` convergence).
- Field-by-field reads of the five official detail pages (titles, price pairs, ratings, review
  counts, breadcrumbs, spec rows) — snapshots preserved in
  `archive/air-ember-edition/data/products.register.json`, dated 2026-11-20.
- Amazon Ads guide — "An ASIN is always 10 characters long":
  https://advertising.amazon.com/library/guides/targeting-with-sponsored-products
- Associates Operating Agreement (upd. 2025-10-15): https://affiliate-program.amazon.com/help/operating/agreement
- Associates Program Policies (upd. 2026-04-14): https://affiliate-program.amazon.com/help/operating/policies
- Associates Standard Commission Income Statement (Kitchen = 4.50%):
  https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ
- FTC Disclosures 101: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers

## Flags raised by this session (archived edition numbering AE-01..AE-08; overlap with main's FLG IDs noted)

| ID | Item | Overlaps main | Status |
| --- | --- | --- | --- |
| AE-01 | Supplied codes are 9 chars; ASINs always 10 → intent fields blank | main FLG set (intent blank policy) | absorbed — main already keeps intent blank |
| AE-02 | `link.amazon` format not documented in Associates agreement; **not claimed invalid** | main FLG-003 | absorbed — same posture on main |
| AE-03 | Intended ASIN/URL/date/source blank pending owner confirmation | main T02 record | absorbed — main's `data/products.json` holds intent fields |
| AE-04 | Tracking ID `shopnow047c-20` account-unvalidated | main FLG-001 | absorbed |
| AE-05 | Commission shown as rate-card Kitchen 4.50%; per-ASIN category unconfirmed | main rate sources | informational |
| AE-06 | Campaign ledger empty; no conversion/revenue claims | main FLG-006 + ledger | absorbed |
| AE-07 | "Five defined events" not enumerated in brief → provisional list used | main T04 (5 events) | absorbed |
| AE-08 | Price/rating snapshots volatile; hardcoded prices avoided on main per price-display policy | main FLG-006 pricing policy | resolved by adopting main's policy |

## PR / merge record (T-15)

| Time (UTC) | Result |
| --- | --- |
| 2026-11-20 | PR #18 opened: https://github.com/sassnarep3-star/WinC/pull/18 (`arena/23428c9e-winc` → `main`). |
| 2026-11-20 | Merge attempts hit conflicts four times as `main` advanced mid-flight (PRs #1–#16, then #17–#21, then #22–#25, then #27–#30). Each round resolved with `main` as trunk: shared site files taken from `main`, `COORDINATION.md` union-merged (full session history + this session's section, nothing dropped), this edition archived under `archive/air-ember-edition/`, gate (`scripts/check_site.py`) re-run green each round (27→29 pages, no violations). |
| 2026-11-20 | PR #18 merged to `main`; Pages deploy and live re-fetch confirmed — see the verification note appended after merge. |
