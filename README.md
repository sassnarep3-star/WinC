# WinC — ShopNow Kitchen

A polished Amazon affiliate publication: basket or oven-style? Compare before you buy.

**Live site:** https://sassnarep3-star.github.io/WinC/

## Working with it

```bash
python3 scripts/new_guide.py "A question a buyer actually asks" --category "Air Fryers"
python3 scripts/build_site.py   # rebuild the site from data/ (single source of truth)
python3 scripts/check_site.py   # compliance + integrity gate (exit 1 on violation)
python3 scripts/deploy_check.py # confirm Pages actually deployed, and that what is live is correct
# or: npm run build / npm run check / npm run verify / npm run new-guide
```

No third-party dependencies: Python standard library only.

## How this site is published

GitHub Pages serves this repository from the **branch** publishing source (`main`, path `/`).
That is deliberate and it is GitHub's own recommendation for a repository that commits its built
HTML and needs no build step at publish time
([GitHub Docs — configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)).

The repository previously carried **both** a branch publishing source and a custom GitHub Actions
publish workflow. GitHub's documentation describes those as two alternatives, and running both
made them contend for the `github-pages` environment: the legacy build record came back
`errored` with a duration of `0` seconds for two commits, because the build was aborted the
moment a concurrent Actions deployment held the environment. The competing workflow was removed
on 2026-11-20 so the branch build is the only publisher.

`.github/workflows/ci.yml` remains, and it is the thing that guards `main`: it rebuilds the site
from `data/`, runs the compliance gate, checks that the committed HTML is what the generator
produces, and runs an independent audit (`tools/audit.mjs`) written against the policy documents
rather than against this repo's own checker.

## The agent pipeline

`scripts/agent/` is the automation the brief asks for: research → draft → publish → optimise.

```bash
python3 scripts/agent/research.py   # one sourced brief per product
python3 scripts/agent/draft.py --all
python3 scripts/agent/publish.py     # build + gate; refuses to publish on a violation
python3 scripts/agent/optimize.py    # reads the campaign ledger
```

Every step carries the same rule as the gate: a value is either carried with the source it came
from, or it is left blank and flagged. `optimize.py` makes no recommendation while the campaign
ledger is empty, because there is nothing to recommend from yet. See `scripts/agent/README.md`.

## Layout

- `data/` — products, sources, flags, probes, suggestions, questions, categories (reader situations), topics (backlog), research briefs — single source of truth
- `data/guides/*.json` — one file per guide; publish by dropping a file
- `data/research/` — generated research briefs, one per product, every value with its source
- `scripts/build_site.py` — generates all HTML + sitemap + RSS + search index
- `scripts/check_site.py` — disclosure / sponsored / price / sitemap / link / imagery / claim-drift gate
- `scripts/deploy_check.py` — verifies the Pages build record and the live pages
- `scripts/new_guide.py` — scaffolds a guide so cadence needs no builder edits
- `scripts/agent/` — research → draft → publish → optimise pipeline
- `assets/` — stylesheet, measurement beacon, search index, `img/` (original illustrations)
- `analytics/` — self-hosted endpoint code (deploy separately; Pages is static)
- `tools/audit.mjs` — independent audit, written from the policy documents
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
