# WinC — ShopNow Kitchen

A polished Amazon affiliate publication: basket or oven-style? Compare before you buy.

**Live site:** https://sassnarep3-star.github.io/WinC/

## Working with it

```bash
python3 scripts/new_guide.py "A question a buyer actually asks" --category "Air Fryers"
python3 scripts/build_site.py   # rebuild the site from data/ (single source of truth)
python3 scripts/check_site.py   # compliance + integrity gate (exit 1 on violation)
python3 scripts/freshness.py    # age of every recorded read; fails past data/freshness.json limits
python3 scripts/ledger_add.py --help   # the only way a row may enter the campaign ledger
# or: npm run build / npm run check / npm run verify / npm run new-guide / npm run fresh
```

No third-party dependencies: Python standard library only.

## Layout

- `data/` — products, sources, flags, probes, suggestions, questions, categories (reader situations),
  topics (backlog), freshness thresholds, campaign ledger — single source of truth
- `data/guides/*.json` — one file per guide; publish by dropping a file
- `scripts/build_site.py` — generates all HTML + sitemap + RSS + search index
- `scripts/check_site.py` — the gate: disclosure, sponsored qualification, no prices, sitemap
  coverage, link resolution, guide and register schema, imagery uniqueness, reader-path hygiene,
  ledger row schema, claim-drift and flag-reference integrity
- `scripts/freshness.py` — how old every externally-sourced claim is (Program Policies §6(c) duty
  to promptly remove Program Content Amazon no longer displays)
- `scripts/new_guide.py` — scaffolds a guide so cadence needs no builder edits
- `assets/` — stylesheet, measurement beacon, search index, `img/` (original editorial illustrations,
  optimized: 1.39 MB for the whole set)
- `analytics/` — self-hosted endpoint code (deploy separately; Pages is static)
- `*.html`, `guides/`, `products/` — generated site (committed for GitHub Pages)

## Rules that never bend

- Disclosure above the fold on every page + footer repeat.
- Every buy button is `rel="sponsored nofollow noopener"` + `Sponsored · paid affiliate link` + the tracking ID.
- No prices, ratings, or invented facts. Blank + flagged beats inferred.
- Every decision block names the one listed spec it rests on. No ranking, no preference.
- Intended vs. observed ASINs live in separate fields, never merged.
- Short links are never claimed invalid; their status is flagged (FLG-003).
- The site is not endorsed by, and does not endorse, any brand it names (Program Policies §6(d)).
- Nothing collected or displayed here trains a machine-learning model: Program Policies §5 bars
  using Program Content or Special Links for that without Amazon's express prior written approval.
- Reader imagery is original artwork, captioned as an illustration; no Amazon listing image is reused.
- A ledger row exists only if an authorized first-party report produced it, with a dated provenance
  string — `scripts/ledger_add.py` refuses anything else, and the file stays empty until then.

Pages a reader sees: front page, `products/index.html`, `guides/index.html`, `topics.html`,
<<<<<<< HEAD
two category pages, five product pages, nine guides. Pages an operator sees (one nav group, plus
=======
two category pages, five product pages, eleven guides (seasonal guides surface in a front-page band,
with season badges on every card). Pages an operator sees (one nav group, plus
>>>>>>> origin/main
the footer): `verification.html`, `flagged-for-review.html`, `questions.html`, `direction.html`,
`measurement.html`, `executive-summary.html`, `search.html`, `about.html`, `disclosure.html`.

See `COORDINATION.md` for the task board and session-by-session provenance, and
`EXECUTIVE-SUMMARY.md` for the full summary with sources.
