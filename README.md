# Crisp Report — an affiliate publication that refuses to guess

**Live site:** <https://sassnarep3-star.github.io/WinC/> · **Tracking ID in use:** `shopnow047c-20` (operator-supplied, not verified against an account — see FLG-004)

This repository is a working Amazon affiliate site **and** the register behind it. Reader-facing pages
carry the buy-this, not-the-audit tone the brief asked for; the audit surface is one click away in the
footer, where the source register, the open questions, the ideas board and the flagged items live.

```
npm run build     # regenerate every page, the sitemap and the feed from data/ + content/
npm run check     # the gate: 11 rule families, fails the build on an unsourced cell
npm run verify    # build + gate (this is what CI runs)
npm run fresh     # staleness queue for confirmed product rows
npm run serve     # preview at http://localhost:8080/WinC/ exactly as Pages serves it
```

No dependencies. `tools/*.mjs` is plain Node ≥18, and the site is static HTML + CSS + two scripts, so
GitHub Pages (legacy build, branch `main`, path `/`) serves it without a pipeline.

## Executive summary

**The ask.** Collect, organise and analyse a full requirements list; turn a careful source register into
a page a buyer can act on; make it findable; automate what can be automated and gate what cannot; lead
with products rather than verification; measure before optimising; keep disclosure above the fold and
every product link marked sponsored; replace ambiguous outbound links with validated Special Links; and
market five supplied products.

**What was here when this session started.** One commit, a 6-byte `README.md`. No site, no data, no
coordination board — while the brief referred to an existing register, rows `SG-27…SG-30`, `FLG-003` and
sources `S01 · S07 · S24`. Numbering therefore restarts here, and the discrepancy is logged as
[FLG-002](data/flags.json) rather than back-filled with invented history.

**What is live now.** A 19-page generated site: front page, five buyer-method guides, the product desk,
the source register, an ideas board with per-option trade-offs and decision export, a questions register,
the compliance gate, the measurement plan, disclosure/privacy/about pages, plus `sitemap.xml`,
`feed.xml`, `robots.txt`, canonicals and `BlogPosting` markup.

**The finding that reorders the plan.** Product *facts* are not free. Amazon's Participation Requirements
allow prices and availability only inside an Amazon-served link or from the Creators/PA API, tie reviews
and star ratings to that same API, and the Creators API requires an enrolled account with **at least ten
qualifying sales in the past thirty days** (PA-API 5 now returns `403 AccessDeniedException`). So
"automate product research, then publish" cannot be the order of work: publishing compliant, useful
content is what earns the data access that makes automation possible. Everything else follows from that —
the ledger ships empty, no price appears anywhere, and the gate fails a build that tries to add one.

**The blocker on the commercial half.** All five supplied identifiers are **9 characters**
(`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`, `B0c8moW59`, `B0f3GKalj`), and egress from this workspace to the
store is refused, so nothing behind them could be confirmed. Rather than guess, the desk publishes the
exact strings, the measurement, and blank product columns with reasons. Three blocking questions
([Q-01…Q-03](data/questions.json)) are answerable by the account owner in about fifteen minutes and would
fill the register automatically.

## How the honesty is enforced, not promised

| Rule | Enforcement |
|---|---|
| Required sentence `As an Amazon Associate I earn from qualifying purchases.` | G-01/G-02 — present in the strip above the content **and** the footer of all 19 pages, else build fails |
| Every populated table cell cites a source id in the register | G-04 — blank needs a reason; a value needs a `src`; intent and observed-redirect columns must stay separate |
| Store links tagged, `rel="sponsored nofollow"`, labelled `(paid link)`, never redirected | G-03/G-05 — plus a forward rule: a *confirmed* row with no compliant link also fails |
| No price, rating or review text | G-06 — currency/rating patterns outside a quoted official source fail the build |
| No unsupported verdicts | G-07 — superiority or ranking claims in guide prose and headings are rejected |
| No price alerts, incentives, countdowns, pop-ups, capture forms | G-08/G-14 — and the disclosure page is required to *state* the refusal |
| Measurement stays aggregate; scripts never rewrite a link | G-10 — no `href` mutation, no cookie, no `setInterval` polling, endpoint off by default |
| Confirmed rows expire | G-12 — 30-day window; `npm run fresh` prints the queue |
| Feed carries no store links; sitemap points at real pages | G-13 |
| No broken links, fragments, assets or `og:image` | G-15 — crawl of every generated page |
| Identifier shape | structure — an unresolved token may never acquire a product value |

`data/sources.json` holds the quoted sentence next to each claim, with the date it was read and *how* it
was read (`fetched`, `api`, `operator`, `local`, or `referenced` for the things we could not open — which
are published as such instead of being quietly dropped).

## Layout

```
index.html                     publication front page
guides/<slug>/index.html       five question-shaped buyer guides (generated from content/guides/*.json)
picks/                         the desk: product-intent register, blank cells with reasons
sources/                       source register, with the official wording quoted
questions/                     15 decision preconditions + where to find each answer
suggestions/                   15 ideas: options, trade-offs, recommendation, decision export
flagged/                       12 irregularities, each with its evidence
how-it-works/                  pipeline (automated vs gated) and the rule table
measurement/                   five events, empty ledger, reporting rhythm
executive-summary/             this summary, on the site
disclosure/ privacy/ about/    the three policy pages
data/ content/ site.config.json  the source of truth for all of the above
tools/                        build, gate, freshness, preview, sample collector
.github/workflows/ci.yml      runs verify on every push and PR
COORDINATION.md                shared task board for parallel sessions
```

Generated HTML is committed because Pages builds from this branch — the CI job `verify` checks the
committed output matches what the generator produces, so the data files stay the only place to edit.

## Read first, if you are reviewing

1. [`COORDINATION.md`](COORDINATION.md) — what was claimed, verified, and where the conflicts are.
2. `data/flags.json` → published as **Flagged for review** — everything not pretended.
3. `data/questions.json` → published as **Open questions** — what to answer to unlock the product half.
4. `data/suggestions.json` → published as the **Ideas board** — pick an option per card, export the
   decision sheet, hand it to a session.
