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
