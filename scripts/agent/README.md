# ShopNow Kitchen — agent pipeline

Four commands, one gate. Each step is deterministic, reads only what is already in this
repository, and **refuses to write a value it cannot point at a source for**. Nothing in this
directory scrapes Amazon, guesses a price, or writes a sentence that claims testing.

```
  research.py  →  draft.py  →  publish.py  →  optimize.py
   (what do we  (turn the     (build, gate,   (read the ledger
    actually    register into  publish)        and say what to
    know?)      a draft)                       do next)
```

| Step | Command | Reads | Writes | Refuses to |
|---|---|---|---|---|
| Research | `python3 scripts/agent/research.py` | `data/products.json`, `data/sources.json`, `data/flags.json`, `data/probes.json` | `data/research/<asin>.json` | record any spec that is not already in the register |
| Draft | `python3 scripts/agent/draft.py --asin B0CDY277D3` | `data/research/*.json`, `data/guides/*.json` | `data/drafts/<slug>.json` | emit a price, a rating, a review count, or a "we tested" claim |
| Publish | `python3 scripts/agent/publish.py` | everything | the site | publish if `scripts/check_site.py` reports a violation |
| Optimise | `python3 scripts/agent/optimize.py` | `data/campaign-ledger.json`, `data/events.json` (if present) | `data/optimisation.json` | recommend an action it cannot justify from a first-party number |

Run all four in order:

```bash
python3 scripts/agent/research.py && \
python3 scripts/agent/draft.py --all && \
python3 scripts/agent/publish.py && \
python3 scripts/agent/optimize.py
```

## The rule that makes this honest

Every one of these steps takes the same rule as its gate:

> If a value cannot be confirmed from an official source, it is left blank and flagged.
> Never infer, never estimate, never fill in a plausible number.

`research.py` therefore produces *blanks* wherever the register has blanks, and
`draft.py` refuses to write a sentence containing a price, a rating, a review count or a
testing claim. Both are checkable: run them and read the output. `publish.py` refuses to
publish if `check_site.py` fails, so a bad draft can never reach the live site.

## Where the authorised data plugs in

Two steps are ready to be fed by an authorised first-party source and are *deliberately
inert* until one exists. They are marked in the code with `# GATED:`.

1. **Amazon Product Advertising / Creators API pricing.** Amazon's Program Policies allow
   price and availability to be displayed only when the link Amazon serves displays it, or
   when the data comes from the Creators API or PA API
   (<https://affiliate-program.amazon.com/help/operating/policies>). Set `PAAPI_ACCESS_KEY`,
   `PAAPI_SECRET_KEY` and `PAAPI_PARTNER_TAG` in the environment and `research.py` will
   attach a `price_live` block **taken from the API response**, never typed in. Without
   those variables it records `price_live: null` and explains why.

2. **First-party click and order reports.** Orders and commissions can only come from an
   authorised report — the Associates Central order report, or the self-hosted analytics
   endpoint in `analytics/`. `optimize.py` reads `data/campaign-ledger.json`, which is
   filled by hand from those reports with a dated provenance trail. While that ledger is
   empty, `optimize.py` prints exactly which rows to collect and makes no recommendation.

Until both are switched on, this pipeline **publishes verifiable prose and no numbers it
cannot prove**. That is the intended behaviour, not a missing feature.

## What "AI" means here

The pipeline is the part that can be automated, done properly: the mechanical, repeatable
work that a human should not have to redo — re-reading the register, building a research
brief, turning a brief into a structured draft, running the gate, and reporting what the
ledger does and does not yet support. The editorial judgement — which question a guide
answers, what a product's honest drawback is, whether a comparison is fair — stays with
the desk and is recorded in `data/products.json` and `data/guides/*.json`, where a reviewer
can see who wrote it and what it rests on.

`data/drafts/*.json` is a staging area. A draft is **not** published until a person moves
it into `data/guides/` and the build is re-run; `publish.py` will refuse to publish a
draft that has not been through that step.
