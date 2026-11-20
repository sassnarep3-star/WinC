# WinC — Air & Ember

Live site: **https://sassnarep3-star.github.io/WinC/** (GitHub Pages, branch `main`)

A source-linked Amazon Associates publication built around five supplied product links — three air fryers and two meat thermometers — with a public review desk (verification log, flagged items, suggestions with decision paths, question list, compliance policy).

## Structure

| Path | What it is |
|---|---|
| `index.html` | Publication front page — picks first, guides second |
| `products.html` | Source register: every row links its official listing; intent vs observed fields never merged |
| `guides.html`, `guide-*.html` | Five question-shaped buying guides (each ends with sources) |
| `suggestions.html` | Decision cards (S-01…S-10): options, effort, impact, decision question |
| `questions.html` | Q-01…Q-16: answered (with sources) vs open (with how-to-close) |
| `verification.html` | Line-by-line method + source register + local metrics panel |
| `flagged.html` | FLG-001…008: unverified items & irregularities with evidence |
| `compliance.html` | Disclosure, link marking, Special Links decision, publishing gate |
| `executive-summary.html` | One-page status for stakeholders |
| `data/products.json` | Machine-readable register |
| `sitemap.xml`, `robots.txt`, `feed.xml` | SEO / findability |
| `js/click-counter.js` | Privacy-preserving 5-event counter (localStorage only) |
| `COORDINATION.md` | Shared task board: claims, sources, irregularities, merge record |

## Verification rule

Every table row carries a source link to an official site. Values that can't be confirmed from an official source are left **blank** and flagged — never inferred. Prices/ratings are dated snapshots (observed 2026-11-20) with live links for re-checking.

## Disclosure

As an Amazon Associate we earn from qualifying purchases. All product links are marked `rel="sponsored"` and visibly tagged. See `compliance.html`.
