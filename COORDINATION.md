# COORDINATION — WinC affiliate site (shared task board)

> **Current session: `arena-82d39deb`** (branch `arena/82d39deb-winc`, based on `main@358dd0c`).
> That session's board, sources and findings are in the **last section of this file**. Earlier
> sections are kept verbatim as the provenance trail. Rule: claim a task by writing the session ID
> + file scope, then commit and push the claim immediately. Never start a task another session has
> claimed. Keep scopes non-overlapping.

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
| Spec rows for all 5 products | Each listing's product-details table + bullet copy re-read | 1 row wrong → corrected (FLG-019); 4 listing-internal contradictions confirmed live (FLG-005, FLG-010, FLG-015, FLG-017); 2 buyer-relevant facts found (FLG-020, FLG-021); 1 Amazon name-string variance (FLG-016) |
| Decision blocks | `data/categories.json` profile sources | Every profile's source checked against the recorded listings; gate now fails a profile that cites an unrecorded listing |
| Registers | `data/suggestions.json`, `data/questions.json`, `data/topics.json`, `data/products.json`, `data/probes.json` | Schema + provenance + drift checks added to `scripts/check_site.py` and run green |
| Site build | `python3 scripts/build_site.py && python3 scripts/check_site.py` | `Built 27 pages, 26 sitemap URLs, 6 guides, 23 search rows.` → `OK: 27 pages checked, 26 sitemap URLs, no violations.` |

**Findings recorded on the site** (`flagged-for-review.html`, 21 items): FLG-015 (6-Qt capacity unit
conflict), FLG-016 (Amazon name-string variance for B08DKYBTPH), FLG-017 (Emeril preset count
24 vs 25), FLG-018 (seller-written serving/rotisserie/pizza claims, quoted as claims), FLG-019
(wrong wattage, corrected), FLG-020 (6/8/9-quart size family under one ASIN), FLG-021 (Amazon flags
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

**Task status:** T20–T26 done · T27 done (executive summary + README reconciled with the repo) ·
T28 integration in progress (see the PR/merge record below).
