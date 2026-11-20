# Air & Ember edition (session arena-23428c9e) — archived

This folder preserves, verbatim, the standalone site built by session `arena-23428c9e`
(branch `arena/23428c9e-winc`) from the empty-repo state before it was integrated with the
multi-session **ShopNow Kitchen** site that had meanwhile become `main` (PRs #1–#16).

**Status: historical record only.** These pages are excluded from the live site's navigation,
sitemap and feed. The live site is main's architecture (`index.html`, `products/`, `guides/`,
`scripts/build_site.py` + `scripts/check_site.py` gate).

Why archived rather than shipped alongside:

1. Two parallel architectures would split the shared index/navigation, which only the
   integration step may change (COORDINATION.md rule).
2. This edition hardcodes dated price snapshots in HTML; main's Program-Policies
   price-display finding restricts prices to Amazon-served links / API, so main's
   blank-price policy is the canonical one.
3. Coverage already exists on main: register + intent record (`data/products.json`),
   flagged page, suggestions/direction, questions, verification, disclosure, measurement.

Contents: full page set (front page, products register with intent-vs-observed record,
5 guides, suggestions with decision cards S-01..S-10, questions Q-01..Q-16, flagged
FLG set, compliance, executive summary), design system (`css/`), privacy-preserving
5-event counter (`js/click-counter.js`), editorial imagery (`images/`), and the dated
product register snapshot (`data/products.register.json`, observed 2026-11-20).

Integration record: see the last section of `/COORDINATION.md`.
