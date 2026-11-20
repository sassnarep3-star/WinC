# WinC — ShopNow Kitchen

A polished Amazon affiliate publication: basket or oven-style? Compare before you buy.

**Live site:** https://sassnarep3-star.github.io/WinC/

## Working with it

```bash
python3 scripts/build_site.py   # rebuild the site from data/ (single source of truth)
python3 scripts/check_site.py   # compliance + integrity gate (exit 1 on violation)
```

No third-party dependencies: Python standard library only.

## Layout

- `data/` — products, sources, flags (single source of truth)
- `scripts/build_site.py` — generates all HTML + sitemap + RSS + search index
- `scripts/check_site.py` — disclosure / sponsored / price / sitemap / link gate
- `assets/` — stylesheet, measurement beacon, search index
- `analytics/` — self-hosted endpoint code (deploy separately; Pages is static)
- `*.html`, `guides/`, `products/` — generated site (committed for GitHub Pages)

## Rules that never bend

- Disclosure above the fold on every page + footer repeat.
- Every buy button is `rel="sponsored"` + Sponsored label + tracking ID.
- No prices, ratings, or invented facts. Blank + flagged beats inferred.
- Intended vs. observed ASINs live in separate fields, never merged.
- Short links are never claimed invalid; their status is flagged (FLG-003).

See `COORDINATION.md` for the task board and `EXECUTIVE-SUMMARY.md` for the summary.
