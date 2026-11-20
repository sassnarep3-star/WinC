# Coordination board

This repository was empty apart from `README.md` when this session began. No other task claims were present.

| Task | Status | Owner/session | File scope |
|---|---|---|---|
| Publication site, evidence register, editorial decision-support, and Pages deployment | in progress | `arena/f87d2975-winc` | `index.html`, `pages/`, `assets/`, `sitemap.xml`, `feed.xml`, `robots.txt`, `.github/workflows/pages.yml`, `scripts/`, `tests/`, `.gitignore`, `README.md`, `COORDINATION.md` |

## Verification and source notes

- Amazon Associates Operating Agreement: <https://affiliate-program.amazon.com/help/operating/agreement> — official Amazon Associates terms include use of tagged Special Links and the required Associate identification statement.
- Amazon Associates Program Policies: <https://affiliate-program.amazon.com/help/operating/policies> — official terms for product content, pricing/availability, and API usage.
- Amazon Associates Help, product links / ASIN: <https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC> — official Associates help material describes product link construction and ASINs.
- FTC endorsement disclosure guidance: <https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking> — official FTC guidance explains disclosure placement and affiliate relationships.
- Amazon Associates reporting help: <https://affiliate-program.amazon.com/help/node/topic/GMWAK55DQX8JEK7C> — official help on Associates report metrics and reports.
- Google Search Console Performance report: <https://support.google.com/webmasters/answer/7576553?hl=en> — official description of search queries, pages, clicks and impressions.

## Known irregularities / review gates

- The five submitted URLs use `link.amazon` and are retained exactly as submitted, but no target page, official listing URL, intended ASIN, redirect destination, product title, category, price, ratings, review claims, commission rate, or destination/tracking report was independently verified. They are not described as invalid. Do not publish them as purchase links until tested in the enrolled Associates workflow and destination/report confirmed.
- The provided strings are stored as submitted references only. Product-intent ASIN and official listing URL, confirmation date, source, and observed redirect target are separate fields and remain blank pending evidence.
- `shopnow047c-20` is user-provided as the selected tracking ID; enrollment, tag acceptance, and reporting status have not been verified.
- GitHub Pages is static hosting. No self-hosted analytics endpoint, conversion feed, click counter, event collection, or Amazon API integration is claimed as operating. No price/review/commission data is fabricated. The architecture and review checklist identify those as decisions/engineering gates.
- Product category is not independently confirmed from the supplied links. Air-fryer titles are labeled editorial hypotheses based on the user's brief, not popularity or product-fit findings.

## Completion log

- Implemented a responsive, publication-style static site with executive summary, question-led editorial briefs, evidence register, suggestion board, open-questions list, empty measurement ledger, disclosure page and flagged-review page. Every page has the Amazon disclosure strip under the masthead and a repeated footer disclosure; navigation and footer make research surfaces reachable.
- Preserved the five user-provided URLs as plain text (not active purchase buttons). Kept intended product identity and official listing fields separate from observed redirect target. Values are blank and explicitly unverified; link status remains unresolved, not declared invalid.
- Added sitemap, RSS 2.0 feed, robots.txt and a GitHub Actions Pages workflow. RSS currently has one truthful introductory publication item; proposed guide topics are not represented as already-published researched reviews.
- Added a proposed five-event analytics schema and empty campaign ledger. Analytics, endpoint, Search Console property, affiliate report import, API integration, reader capture and actual automation are explicitly not live.
- Checks run: `python tests/check_site.py` (10 HTML pages; local links and anchors, disclosures, sponsored attributes on any Amazon outbound link, and official links on every table data row); `python scripts/build_site.py`; `git diff --check`; XML parsing of sitemap and RSS feed. All passed locally.
- Deployment remains pending GitHub Pages Actions validation and successful publication from `main`. Product/account uncertainty and implementation gates are documented on the site's Flagged for review page.
