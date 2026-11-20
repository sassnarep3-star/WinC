# WinC — ShopNow Kitchen

A polished Amazon affiliate publication: basket or oven-style? Compare before you buy.

**Live site:** https://sassnarep3-star.github.io/WinC/

## Working with it

```bash
python3 scripts/new_guide.py "A question a buyer actually asks" --category "Air Fryers"
python3 scripts/build_site.py   # rebuild the site from data/ (single source of truth)
python3 scripts/check_site.py   # compliance + integrity gate (exit 1 on violation)
# or: npm run build / npm run check / npm run verify / npm run new-guide
```

No third-party dependencies: Python standard library only.

## Layout

- `data/` — products, sources, flags, probes, suggestions, questions, categories (reader situations), topics (backlog) — single source of truth
- `data/guides/*.json` — one file per guide; publish by dropping a file
- `scripts/build_site.py` — generates all HTML + sitemap + RSS + search index
- `scripts/check_site.py` — disclosure / sponsored / price / sitemap / link / imagery / claim-drift gate
- `scripts/new_guide.py` — scaffolds a guide so cadence needs no builder edits
- `assets/` — stylesheet, measurement beacon, search index, `img/` (original illustrations)
- `analytics/` — self-hosted endpoint code (deploy separately; Pages is static)
- `*.html`, `guides/`, `products/` — generated site (committed for GitHub Pages)

## Rules that never bend

- Disclosure above the fold on every page + footer repeat.
- Every buy button is `rel="sponsored"` + Sponsored label + tracking ID.
- No prices, ratings, or invented facts. Blank + flagged beats inferred.
- Every decision block names the one listed spec it rests on. No ranking, no preference.
- Intended vs. observed ASINs live in separate fields, never merged.
- Short links are never claimed invalid; their status is flagged (FLG-003).

Pages a reader sees: front page, `products/index.html`, `guides/index.html`, `topics.html`,
two category pages, five product pages, eleven guides (seasonal guides surface in a front-page band,
with season badges on every card). Pages an operator sees (one nav group, plus
the footer): `verification.html`, `flagged-for-review.html`, `questions.html`, `direction.html`,
`measurement.html`, `executive-summary.html`, `search.html`, `about.html`, `disclosure.html`.

See `COORDINATION.md` for the task board and `EXECUTIVE-SUMMARY.md` for the summary.

## Content layer

- `data/makers.json` — one profile per maker: who they are, plus at least two checkable claims each tied to a source-register row. Never ranked, never inferred from the brand name.
- `data/stories.json` — the long-form narrative per product (headline, standfirst, deciding spec, paragraphs, flags it depends on) and the series membership. A story may only argue from a stored spec or from USDA's published figures.
- `assets/img/*.webp` — the illustration set, ~0.5 MB total. Captioned as illustrations; no Amazon product imagery or logos.

## Two gates, both must pass

`scripts/check_site.py` is the authority; `tools/audit.mjs` is the independent second opinion written from the policy documents rather than from the checker. The gate also parses every inline script with `node --check`, because a broken script is invisible to an HTML check.

```bash
npm run verify                      # build + check_site.py
node tools/audit.mjs --strict       # independent audit, exit 1 on any finding
```
