# COORDINATION.md — shared task board

Repo: `sassnarep3-star/WinC` · Board started: 2026-11-20 (UTC) · This file is the only cross-session
coordination surface. Read it **before** claiming work; write to it **before** editing files.

## Session IDs

| session | branch prefix | role | first active |
|---|---|---|---|
| `arena-04112b09` | `arena/04112b09-winc` | build + final integration (this session) | 2026-11-20 |

## Protocol (all sessions)

1. Read this file. Claim a task by setting **Status: in progress**, **Owner**, **Scope** (file globs), then
   `git commit` + `git push` the claim immediately. Never start a task another session holds.
2. Work only inside your claimed scope, on your own branch. If you need a file outside it, log a
   `REQUEST` below instead of editing.
3. `git pull --rebase` before every push. Small, frequent commits.
4. On conflict: stop, resolve without discarding the other session's work, record it in `## Conflict log`.
5. A claim older than 60 minutes with no commits may be taken over; note the handoff in `## Log`.
6. Shared outputs (`data/products.json`, `data/sources.json`, `index.html`, nav/footer, `sitemap.xml`,
   `feed.xml`) are changed **only by the final integration session**, after all other tasks are done.
7. Nothing is marked `done` until its sources, verification and irregularities are recorded here.
8. Never mark a field verified unless it was checked against an official source and that source is linked
   in `data/sources.json`. Unconfirmed values stay **blank** and get a `FLG-` entry.

## Statuses

`unclaimed` → `in progress` → `needs review` (published on Flagged for Review; does not block) → `done`.
`blocked` = cannot proceed until an input exists (see `data/questions.json`).

## Task board

| id | task | status | owner | scope |
|---|---|---|---|---|
| T00 | Repo review; inventory what the brief references vs what exists | **done** | arena-04112b09 | read-only |
| T01 | Coordination board + claim protocol | **done** | arena-04112b09 | `COORDINATION.md` |
| T02 | Source register (fetched official policy pages, quoted findings) | **done** | arena-04112b09 | `data/sources.json` |
| T03 | Product-intent confirmation register for the 5 supplied links | **done** | arena-04112b09 | `data/products.json`, `data/product-intent.json` |
| T04 | Compliance rules table + publishing gate (`check.mjs`) | **done** | arena-04112b09 | `data/rules.json`, `tools/check.mjs` |
| T05 | Data-driven site generator + Pages layout | **done** | arena-04112b09 | `tools/build.mjs`, `tools/lib.mjs`, `*.html` |
| T06 | Buyer guides (5–6 question-shaped, no product claims) | **done** | arena-04112b09 | `content/guides/*.json` |
| T07 | Suggestions board (options + recommendation + decision capture) | **done** | arena-04112b09 | `data/suggestions.json`, `suggestions/**` |
| T08 | Open questions / missing-information register + discovery steps | **done** | arena-04112b09 | `data/questions.json`, `questions/**` |
| T09 | Flagged-for-review page from `data/flags.json` | **done** | arena-04112b09 | `flagged/**` |
| T10 | Measurement: 5 events, campaign ledger (empty), click counter, privacy | **done** | arena-04112b09 | `data/events.json`, `data/ledger.csv`, `assets/js/clicks.js` |
| T11 | Findability: sitemap, RSS, robots, canonical, JSON-LD | **done** | arena-04112b09 | `sitemap.xml`, `feed.xml`, `robots.txt` |
| T12 | Editorial cadence, clusters, authorship, brand, imagery | **done** | arena-04112b09 | `data/editorial.json`, `assets/img/*` |
| T13 | Executive summary (page + README) | **done** | arena-04112b09 | `executive-summary/**`, `README.md` |
| T14 | CI gate workflow (build + verify on PR/push) | **done** | arena-04112b09 | `.github/workflows/ci.yml` |
| T15 | PR → merge → confirm Pages deploy → record result | **done** | arena-04112b09 | repo-wide (integration) |
| T16 | Product resolution (needs real ASINs / Associates account) | **blocked** | — | `data/products.json` |
| T17 | Price/commission automation (needs Creators API; 10 sales/30 days) | **blocked** | — | none yet |
| T18 | Hosted analytics collector (needs a server; Pages is static only) | **blocked** | — | `tools/collector.sample.mjs` |

## Claims

**arena-04112b09** — T00–T15 complete. T16–T18 remain **blocked** on operator inputs (see the log); they touch no files and block nothing. Scope: `data/**`, `content/**`, `tools/**`, `assets/**`,
`*.html`, `*.xml`, `robots.txt`, `README.md`, `package.json`, `site.config.json`, `_config.yml`,
`.github/workflows/ci.yml`, `COORDINATION.md`. Rationale: the repository was empty at start (see T00), so
there is no in-flight work to collide with. T16–T18 are left deliberately blocked and touch no files.

## Log

- 2026-11-20 05:31 · arena-04112b09 · `git log` at start = 1 commit (`a6083c9 Initial commit`); tree
  contained only `README.md` (6 bytes, `# WinC`). **No prior data files, no COORDINATION.md, no site, no
  Pages source files existed.** Recorded because the operator brief refers to artifacts that are not in
  this repo (see FLG-002).
- 2026-11-20 05:33 · arena-04112b09 · Pages already enabled by operator: `build_type=legacy`,
  `source={branch:main,path:/}`, `html_url=https://sassnarep3-star.github.io/WinC/`, `https_enforced=true`
  (GET `/repos/sassnarep3-star/WinC/pages`). Consequence: static HTML must sit at the repo root on `main`,
  and every internal link must be relative because the site is served from a sub-path.
- 2026-11-20 05:40 · arena-04112b09 · Machine-checkable finding: all five supplied identifier tokens are
  **9 characters** (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`, `B0c8moW59`, `B0f3GKalj`) and are mixed-case.
  Logged as FLG-001. Not repaired or guessed — no invented ASINs.
- 2026-11-20 05:42 · arena-04112b09 · Sandbox egress is restricted to github.com/api.github.com/
  codeload/npmjs/pypi. `curl` to `link.amazon:443` and `www.amazon.com:443` failed with
  `SSL_ERROR_SYSCALL` (curl exit 35). Recorded as **environment block, not evidence** about those hosts;
  link resolution is therefore marked inconclusive rather than invalid (FLG-003 stays unresolved, as the
  brief instructs).
- 2026-11-20 05:44 · arena-04112b09 · Policy research done from Amazon's own domains; 6 primary pages
  fetched and quoted into `data/sources.json`. Two load-bearing facts found that change the plan:
  (a) price/rating display is only permitted via links Amazon serves or via Creators/PA API
  (Participation Requirements §2(b)); (b) Creators API requires **≥10 qualifying sales in the past 30
  days**, so "automated optimization" cannot be step one — it is gated behind traffic and sales.
- 2026-11-20 05:46 · arena-04112b09 · Wrote claims; starting file generation.

## Requests (cross-scope)

- none. If a session needs a shared file changed, add a row:
  `| requested by | file | change wanted | reason | status |`

## Conflict log

- none yet.

## Verification record

Method: every published value carries a `src` key into `data/sources.json`. Sources were fetched from the
publisher's own domain on 2026-11-20 and the load-bearing sentence was stored as a quote, so a reviewer can
diff our claim against their text. `tools/check.mjs` re-enforces this at build time (rule G-04) and fails the
build if a table cell holds a value with no source, if the disclosure sentence is missing from any page, or
if an outbound link lacks `rel="sponsored nofollow"` or a `tag=` parameter.

| row group | checked against | result |
|---|---|---|
| Disclosure sentence & placement | SRC-01 §5 (affiliate-program.amazon.com) | matches required wording exactly |
| Link-level "(paid link)" wording | SRC-03 (official Associates FAQ) | adopted verbatim examples |
| 24 h session / 89 d cart / 180 d ship deadline | SRC-02, Commission Income Statement §1 | recorded, quoted |
| Disqualified: redirecting links, search-engine links, paid "amazon" keywords | SRC-02 §2(c)(d)(e) | encoded as gate checks G-06/G-07 |
| No price data except API/Amazon-served | SRC-02 Participation Requirements §2(b) | no price published anywhere; fields blank |
| No Amazon reviews/star ratings | SRC-02 Participation Requirements §6(t) as fetched | review fields blank + FLG-005 |
| No price-alerting feature on site | SRC-02 §6(y) | deliberately not built; noted in suggestions SG-11 |
| No per-user sub-tagging of clicks | SRC-02 §2(b) sub-tag paragraph | collector is aggregate-only |
| No ML training on Program Content | SRC-02 §5 | flagged FLG-007 (gates "AI pipeline") |
| PA-API 5 deprecated → Creators API | SRC-06 (official notice) | recorded; blocks T17 |
| Creators API prerequisites incl. 10 sales/30 d | SRC-05 | recorded; drives sequencing |
| GitHub Pages project-site sub-path & IP logging | SRC-09 (docs.github.com) | relative links + privacy note |
| Article/BlogPosting schema fields | SRC-07 | emitted by generator |
| people-first content guidance | SRC-08 | titles written to it, no hype |
| ASIN = 10 characters | Seller Central help, **not reachable** from here | UNVERIFIED by us — see FLG-001 note |
| Tracking ID `shopnow047c-20` validity | needs Associates account | UNVERIFIED → FLG-004 |
| The 5 supplied links → products | needs resolvable link/account | UNVERIFIED → FLG-003 |

## Irregularities flagged for the operator

FLG-001 (identifier length), FLG-002 (brief cites artifacts absent from repo), FLG-003 (short-link
compliance, left unresolved on instruction), FLG-004 (tracking ID unverifiable), FLG-005 (no price/rating
data permitted pre-API), FLG-006 (empty repo/no prior register), FLG-007 (AI-training + automation limits),
FLG-008 (static host cannot host a collector), FLG-009 (brief mixes "audit register" and "shop" goals;
resolved by splitting surfaces). Full text and sources: `data/flags.json` and the live **Flagged for Review**
page. None block the merge.

## PR / merge record
## Completion record — arena-04112b09 (T02–T15)

Delivered in commit `652e058` + `2425729`. Site: 19 generated pages under the Pages root, plus
`sitemap.xml`, `feed.xml`, `robots.txt`, `404.html`. Data-first: `data/*.json` + `content/guides/*.json`
are the only editable surface; editing HTML by hand fails the CI reproducibility step.

| artefact | what it holds | verification performed |
|---|---|---|
| `data/sources.json` | 16 sources; 10 fetched from the publisher's own domain today, 2 API/local measurements, 1 operator brief, **3 recorded as `referenced` because we could not open them** | each row stores the load-bearing sentence verbatim + the read date, so a reviewer can diff claim against source |
| `data/product-intent.json` | 5 rows: intended identifier, confirmation date/by/source, **observed redirect in a separate field** (never merged); price/rating/review/availability left blank | blanks asserted by gate G-04; shape check asserts no product value may attach to an unresolved identifier |
| `data/rules.json` + `tools/check.mjs` | 15 rule families, each mapped to the clause it enforces | `npm run check` passes clean; **the tester was tested** — see below |
| `data/questions.json` | 15 decision preconditions, 3 blocking, each with where to look and what happens if nobody answers | every row cites a source id or is marked unknown |
| `data/suggestions.json` | 15 ideas with options, trade-offs, a recommendation and a copy-paste build instruction; published as an interactive board with local decision capture + markdown export | decision capture stores nothing off-device; gate G-10 asserts that |
| `data/flags.json` | 12 irregularities with evidence and resolution paths, published as Flagged for review | nothing here blocks the merge; FLG-001/003/005/006 gate specific claims |
| `data/ledger.csv` | campaign ledger, headers only, zero rows | G-04 refuses a row without an authorized first-party source |
| guides ×5 | question-shaped buyer-method pages, no product named | G-06 (no price/rating), G-07 (no verdict), G-15 (links) all green |

### Gate self-test (why the machinery is trustworthy rather than decorative)

Injected three violations, then restored:
1. broken internal href authored by the generator → caught by G-15;
2. an invented `$149.99` in guide prose → caught by G-06;
3. the disclosure sentence paraphrased **in `site.config.json`** → initially **not** caught, because
   G-01 read its expected value from the file it policed. Fixed: the canonical sentence is now a literal
   inside `tools/check.mjs` (quoted from SRC-01 §5) and config drift is itself a failure. Re-tested: caught.
Also found and fixed while testing: the link gate only read double-quoted `href`/`src`, so single-quoted
attributes were invisible to it; and `inline()` was escaping HTML the generator authored (fixed with a
separate `rich()` for build-owned strings, `inline()` still escapes data-file prose).

### Corrections made during the build (so nobody re-introduces them)

- Front page briefly linked `link.amazon/...` as an anchor. Removed: an unconfirmed, untagged store URL
  must never be a live link. The address is printed as copyable text on the register page instead.
- Front page repeated one identical 200-character sentence across five rows. Replaced with a single
  verdict plus identifier chips; per-row repetition stays only on the register, where a complete
  register is the point.
- Illustrations shipped at ~1.6 MB each; quantised to a palette and resized to 1200px (116–222 KB).
- Pseudo-precision removed from guide copy (invented cm/° figures replaced with "the figure the manual
  states"), because an unsourced number in a measurement guide is the exact failure mode we are avoiding.

### Sources consulted (all read 2026-11-20, from the publisher's domain)

- https://affiliate-program.amazon.com/help/operating/agreement — §1 Special Links, §5 disclosure, §6 termination
- https://affiliate-program.amazon.com/help/operating/policies — Commission Income Statement §1–§2,
  Participation Requirements §1–§6, Products Statement (prices §2(b), reviews §6(t), self-purchase §6(u),
  no price alerts §6(y), no per-user sub-tags §2(b), no ML training without approval §5)
- https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 — link-level "(paid link)" wording
- https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction — 10 qualifying sales / 30 days
- https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation — PA-API 5 → 403
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- https://developers.google.com/search/docs/appearance/structured-data/article · /fundamentals/creating-helpful-content · /crawling-indexing/qualify-outbound-links
- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- API: `GET /repos/sassnarep3-star/WinC/pages` → `build_type=legacy`, `source={main,/}`,
  `html_url=https://sassnarep3-star.github.io/WinC/`

**Not verified, and left unverified on purpose:** the 10-character ASIN rule (Seller Central help was not
reachable here → SRC-13 `referenced`), whether `link.amazon` links are valid Special Links (FLG-003,
unresolved per instruction), and whether `shopnow047c-20` is registered to this site (FLG-004).

### Handoff notes for other sessions

- Do not hand-edit `*.html`, `sitemap.xml`, `feed.xml`, `assets/js/config.js`: regenerate.
- `data/` is intentionally published (FLG-010). Keep secrets out of it.
- To add a guide: create `content/guides/<slug>.json`, register it in `data/editorial.json`, run
  `npm run verify`. Sitemap, feed and nav update themselves.
- To close FLG-001/003: fill `data/product-intent.json` rows (intent fields only; redirect observations go
  in `observed_redirect_target`), then rebuild. The desk, front page and freshness queue follow automatically.

## PR / merge record

