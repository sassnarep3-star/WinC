# COORDINATION.md — shared task board

Repository: `sassnarep3-star/WinC` · Site: https://sassnarep3-star.github.io/WinC/ (GitHub Pages, legacy build)

## Notes on this board (read first)

- The repository started as a single `README.md` with one commit (`a6083c9`). It contained **no** source register, **no** `COORDINATION.md`, **no** Operating Agreement copy, and **no** IDs such as `S01`–`S24`, `FLG-003`, `SG-27`–`SG-30`, `S02`. Those references in the request could not be checked against any file here. This board and the source register in `data/sources.json` were created new, with new IDs (`SRC-xx`, `F-xx`, `Q-xx`, `S-xx`). Nothing from the earlier references was reconstructed.
- Branch rule for this session: all work is on `arena/70d8ad52-winc`. The per-task `session-<id>/<task>` branch scheme in the request was **not** used, because the session rules fix the working branch. Tasks are separated by file scope below instead.
- Session ID for this board: `arena-70d8ad52` (single active session in this run).
- Status key: `unclaimed` · `in progress` · `done` · `needs review` (published on the Flagged for Review page; does not block) · `blocked` (needs an owner action that an agent cannot perform).

## Task board

| ID | Task | Status | Owner (session) | File scope | Notes |
|---|---|---|---|---|---|
| T-01 | Repo review + source register | done | arena-70d8ad52 | `data/sources.json`, `sources/` | 13 source rows, each with URL and verification status. See Sources page. |
| T-02 | Product-intent confirmation records (5 links) | done (partly) | arena-70d8ad52 | `data/products.json`, `products/` | Intended ASIN left blank (not confirmable). Observed redirect target stored in its own field. Price captured for 5, rating for 1. |
| T-03 | Compliance gate (disclosure, `rel="sponsored"`, link checks) | done | arena-70d8ad52 | `scripts/build.py`, `compliance/` | Build fails on missing disclosure, non-sponsored Amazon link, or broken internal link. |
| T-04 | Site build (landing, category pages, nav, footer, sitemap, RSS) | done | arena-70d8ad52 | `scripts/build.py`, `docs/`, `README.md` | Generated HTML in `docs/`. Pages source to be set to `main /docs` at integration. |
| T-05 | Analysis, executive summary, questions, suggestions | done | arena-70d8ad52 | `data/questions.json`, `data/suggestions.json`, `analysis/`, `executive-summary/`, `questions/`, `suggestions/` | Suggestions are proposals only. Nothing in them is implemented. |
| T-06 | Campaign ledger (empty, defined) | done | arena-70d8ad52 | `data/ledger.csv`, `ledger/` | Header only. No performance data was provided, so none is shown. |
| T-07 | Flagged for Review page | done | arena-70d8ad52 | `data/flags.json`, `flagged-for-review/` | 12 flags, each with source links and an owner action. Published as `needs review`. |
| T-08 | One Special Link test per product in the enrolled Associates workflow | blocked | — | none | Needs a login to the owner's Associates account. An agent cannot do this. Owner action listed in F-09. |
| T-09 | Privacy-preserving click counter + self-hosted analytics endpoint (5 events) | blocked | — | none | GitHub Pages is static, so there is no server-side endpoint. The five events are not defined anywhere in the repo. Options are on the Suggestions page (S-02, S-03). Nothing was installed. |
| T-10 | Integration: merge branch, re-verify combined data, build, PR to `main`, merge, confirm Pages | in progress | arena-70d8ad52 | all | See log below. |

## Verification log

| Date (UTC) | Task | What was verified | Sources | Irregularities raised |
|---|---|---|---|---|
| 2026-11-20 | T-01, T-02 | Five `link.amazon` links resolved with the fetch tool. Each landed on an `amazon.com/dp/` page. Titles, breadcrumbs, buy-box prices (and one rating) were read from those pages. | SRC-07…SRC-12 | F-01, F-02, F-03, F-04, F-06 |
| 2026-11-20 | T-03 | Operating Agreement §5 disclosure text read on the official page. Policy clauses §2(b), 2(v), 2(w) read from official search excerpts (full-page confirmation pending). FTC Disclosures 101 and Google `rel="sponsored"` read on official pages. | SRC-01, SRC-02, SRC-04, SRC-05 | F-03, F-07, F-10 |
| 2026-11-20 | T-02 | ASIN definition checked against PA-API 5.0 GetItems (official, search excerpt). Token lengths counted in code. | SRC-03 | F-01 |
| 2026-11-20 | T-04, T-06, T-07 | Build run from a fresh process: 14 pages written, validation passed. Negative tests confirmed the gate catches: a missing rel=sponsored, a missing disclosure, a broken internal link, a wrong tag flag, an unflagged blank, a row without an official source, and an ASIN that does not match its URL. | SRC-01 to SRC-13 | — |
| 2026-11-20 | T-10 | Pull request opened: https://github.com/sassnarep3-star/WinC/pull/5 (`arena/70d8ad52-winc` → `main`). Merge and Pages checks recorded below. | SRC-01 to SRC-13 | F-01 to F-12 (all carried into the PR body) |

## Integration record (T-10)

- PR: https://github.com/sassnarep3-star/WinC/pull/5
- Merge method: merge commit (`gh pr merge 5 --merge`), no approval gate, per the owner's instruction. Owner approval was not requested.
- Pages: source to be set to `main` / `/docs` after the merge, then the build status and the live URL are checked. Results are reported in the session summary.
- Unverified items and flags do not block the merge. They are published on the Flagged for Review page.

## Handoff / claim rules followed

- No other session held a claim when this board was created. No handoffs occurred.
- Claims were committed and pushed before the main work started (see git history of this file).
