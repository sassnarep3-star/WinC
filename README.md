# WinC: Amazon affiliate picks (static site)

Live site: https://sassnarep3-star.github.io/WinC/ (GitHub Pages, serves the `docs/` folder of `main`)

A small, source-first buying guide for five Amazon listings (three air fryers, two meat thermometers). Every value is dated and cites an official source. A value that could not be confirmed is left blank and shown as **Unverified**, with a flag.

## Layout

| Path | What it is |
|---|---|
| `data/products.json` | Product records: submitted link, intended ASIN (blank until confirmed), official listing URL, observed ASIN, observed redirect target (kept separate), prices, ratings, sources. |
| `data/sources.json` | Source register with official links and verification status. |
| `data/flags.json` | Flagged for Review items, each with sources and an owner action. |
| `data/questions.json` | Questions and information gaps. |
| `data/suggestions.json` | Options to choose from. Nothing in it is implemented. |
| `data/guides.json` | Working-title guides. Not published. |
| `data/ledger.csv` | Campaign ledger. Header only, by design. |
| `scripts/build.py` | Generates every page in `docs/` from the data, then validates the result. |
| `docs/` | Generated site (GitHub Pages source). Do not edit by hand. |
| `COORDINATION.md` | Shared task board, claims, verification log, and PR/merge record. |

## Build and check

```bash
python3 scripts/build.py
```

The build exits non-zero if any check fails, so a broken site is not published. Checks include:

- the Associates disclosure is above the content and repeated in the footer on every page;
- every link to an Amazon host has `rel="sponsored"`;
- every internal link and `#anchor` resolves;
- each product has an official source, its URL-derived values match its stored values, and each blank value is listed against a flag;
- `sitemap.xml` and `feed.xml` parse and list every page.

## Editing

- Change values in `data/*.json`, then rebuild. Do not edit `docs/` directly.
- A blank value needs an entry in that product's `unverified_fields`, pointing to a flag in `data/flags.json`.
- Add a source to `data/sources.json` before citing it.

## Not in this repository (by design)

- No analytics or click counter: the site is static. See Flagged for Review F-08 and Suggestions S-02 and S-03.
- No Associates Special Link test: it requires a login to the owner's Associates account (F-09).
- No Amazon product images: pending the IP licence review (F-11).
