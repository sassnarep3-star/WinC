# Counterform — the everyday kitchen edit

A static, publication-style Amazon Associates research and buying-guide site. The reader-facing experience leads with practical buyer questions; the research desk keeps product evidence, open decisions, measurement status and unresolved items visible.

## Local preview and checks

This is a dependency-free static site. Open `index.html` directly or serve the repository root with any static web server. Run the local integrity checks with:

```sh
python tests/check_site.py
python scripts/build_site.py
```

The build copies only the public site into the ignored `public_site/` directory. GitHub Actions validates the HTML links and disclosure placement, builds this clean artifact and deploys it to GitHub Pages from `main`.

## Pages

- `index.html` — publication landing page
- `pages/executive.html` — executive summary and recommended decision path
- `pages/field-notes.html` — question-shaped editorial hypotheses
- `pages/shortlist.html` — five submitted product references and separate intended/observed link records
- `pages/editorial.html` — sourcing, testing and human publication gates
- `pages/suggestions.html` — prioritized, reviewable recommendations
- `pages/questions.html` — knowns, unknowns and discovery steps
- `pages/measurement.html` — five-event proposal and empty campaign ledger
- `pages/disclosure.html` — disclosure language and official policy references
- `pages/flagged.html` — unresolved items, sources and next verification actions

## Evidence and operating limits

The supplied tracking ID is `shopnow047c-20`. The five `link.amazon` references are preserved as submitted inputs but their destinations and exact compliance status are unresolved. They are not labeled invalid. This site intentionally leaves product identities, intended ASINs, official listing URLs, prices, reviews, features, commission values and observed redirects blank until verified from authorized sources. A supplied short link is not treated as evidence of a product identity or tracking result.

No active analytics, conversion tracking, Amazon API/PA API integration, automated product discovery, or self-hosted endpoint is present. GitHub Pages is static hosting; the measurement page documents the missing architecture and proposed schema. No clicks, sales, revenue or traffic data are fabricated. Before enabling Special Links, product content or API-derived data, review current Amazon Associates terms and have an authorized operator test a Special Link and report in the enrolled workflow.

## Official references used

- Amazon Associates Program Operating Agreement: <https://affiliate-program.amazon.com/help/operating/agreement>
- Amazon Associates Program Policies: <https://affiliate-program.amazon.com/help/operating/policies>
- Amazon Associates Help (product links / ASIN): <https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC>
- FTC Endorsement Guides: What People Are Asking: <https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking>

These references establish policy context only; they do not independently verify the submitted product URLs, account, tracking ID or product claims. See `COORDINATION.md` for the task record and review gates.
