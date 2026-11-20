
---

# Fourth pass — shop-first reader path, policy detail read to the clause, and id discipline (2026-11-20, session `ab951e4c`)

Brief for this pass: make it read like a polished affiliate shop rather than AI output or an audit;
make the suggestions reviewable before implementation; list what has to be answered before a
decision is reasonable; keep verifying line by line against official sources. Counts below are read
from the registers at write time, and every page that states a count computes it from the same data.

## 1 · Reader path: shelf copy, not register copy

- **Cards now answer the buying question first.** Each product leads with a shelf line (what the
  listing says the thing is for) and a *decide on* line naming the one listed spec the decision rests
  on, followed by the button and a single evidence link. What left the card: the keyword-stuffed
  listing title, the model number, `see FLG-0nn`, and the bare ASIN. Those are register fields and
  they are still published — on the product page and in the verification table.
- **One image per product, on one optimized profile.** This pass drew five original illustrations; the
  trunk had meanwhile drawn its own five. Rather than shipping ten near-identical multi-megabyte
  files, the merge put the trunk's webp-backed set on cards and product pages and kept this pass's
  art as guide header art. `assets/img` is 10.2 MB across 40 files, and the gate refuses a
  shared or oversized product asset. Recorded as a merge decision, not hidden (FLG-045).
- **The front page's method essay became three lines.** "Nothing is tested, so nothing is claimed ·
  Blank beats guessed · The links are sponsored", each linking the register that proves it. The
  verbatim listing title now sits under the short shelf label on every product page, which is what
  makes the label's truncation defensible under §6(a).

## 2 · Editorial: three guides, and a backlog that says what it closed

| Guide | What it rests on |
|---|---|
| Thermometer accuracy / the ice-cup check | USDA FSIS: “most food thermometers will give an accurate reading within 2 to 4 degrees F”, its ice-water and boiling-water procedures, its calibration-per-type table, and “if the thermometer doesn't allow manual calibration, you may need to replace it” |
| Can it fit a whole chicken? | The three listings' own capacity, footprint and weight strings — including that none of them publishes an interior cavity dimension — plus the FSIS 165°F minimum and the three-place bird check |
| Reading thermometer listing copy | FSIS care and placement rules (“most thermometers should not be immersed in water”; do not leave one in the food unless the maker designed it to) read against the listing's IP67, 1000°F and “unlimited range” wording |

No test claim, no price, no rating, no “best”. The topic backlog went to 24 rows with 8 marked
published **pointing at the guide that answers each**, and the rest stating in their own words that
they are editorial hypotheses because no Search Console property exists. Cadence: this pass shipped
three guides in one build, which is what the machinery supports per focused pass (SG-43).

## 3 · Compliance: read the clauses, then change what the site says

The Program Policies page renders anonymously, so §2(b), §4, §5, §6(a), §6(c) and §6(d) were read
verbatim on 2026-11-20 and recorded as **S36**, and the consequences are on the site rather than in a
to-do list:

- **§6(d) — no implied endorsement.** Brand and celebrity names sit beside buy buttons, so the
  disclosure, the About page and the site-wide footer now state plainly that no named brand endorses
  or sponsors this site. The gate fails if that sentence goes missing (FLG-041).
- **§6(c) — remove Program Content promptly.** `scripts/freshness.py` measures the age of
  82 recorded reads and exits non-zero past the limit in `data/freshness.json` (14 / 45 days). The
  removal decision stays human and is recorded as open (FLG-042, Q-22).
- **§6(a) — truncate where the meaning is unchanged, never alter.** The short labels rely on that
  permission, so the full title is published under each one and the comparison is flagged for a human
  rather than declared compliant (FLG-044's sibling finding, Q-27).
- **§5 — no Program Content in model training** without Amazon's express prior written approval. This
  is the boundary on the "AI-powered product research" ambition, and it is written into the standing
  rules so a later pass cannot drift past it: this repository renders, checks and records; it has no
  crawler and no corpus export (FLG-043, Q-28).
- **§4 — affiliate links in email only where the recipient solicited the message.** The capture form
  collects nothing today, so no rule is broken and no list can be started from it (FLG-044, Q-21).
- **Disclosure accuracy.** The page used to claim “Amazon product descriptions are never copied” while
  every product page reproduces the listing's verbatim title — the practice is the method, so the
  sentence was fixed to say what is taken, what is never taken, and the clause that permits it (FLG-032).
- **Google's own changelog** confirms the FAQ rich-result documentation was removed and HowTo retired
  (**S28**): the site keeps FAQ markup for parsing and promises no SERP feature (FLG-030, Q-29).

## 4 · The independent second gate found four things, and two were this site's fault

`tools/audit.mjs` (another session's checker, run against the merged tree) disagreed with the primary
gate four times. Each disagreement was chased to the correct side:

| Finding | Who was wrong | Outcome |
|---|---|---|
| 52 “unresolved fragment” reports against the source register | the audit read only double-quoted `id=` | both sides fixed: register anchors are double-quoted, the audit accepts either style (FLG-039) |
| an “unresolved reference” to a JavaScript concatenation | the audit treated inline JS as markup | fixed in the audit, with the reason at the change site (FLG-040) |
| the capture form could submit an address into a URL when scripting was blocked | **the site** | the trunk made it non-submitting; this pass removed the field's `name` attribute so a script-blocked submit has no key/value pair to carry, and the page says why (FLG-037) |
| “never stored: search query text” while search puts `?q=` in the address bar | **the claim was incomplete** | disclosed rather than removed, because the URL is the mechanism that makes server-less search shareable (FLG-038) |

## 5 · Machinery, and the register's own hygiene

- `scripts/ledger_add.py` is the only way a row enters the campaign ledger: `--authorized`,
  integer-or-null measured fields, a dated provenance string, no estimating words, and no derived
  rates. It was exercised end-to-end — a throwaway row rendered into `measurement.html`, then the
  ledger was reverted to empty, because no authorized first-party report exists to record.
- `scripts/alloc_ids.py` allocates ids from the merged tree and audits every cross-register
  reference. It exists because nine parallel sessions guessed at free ids and the guesses went stale
  twice inside a day (FLG-045). On its first run it found a pre-existing defect: the suggestions
  register had a four-row hole that a live citation pointed into; the citation was corrected to name
  the duty instead of inventing rows to fill the gap (FLG-046).
- The gate gained rule families for card hygiene, imagery uniqueness and size, ledger row schema, the
  §6(d) statement, recorded-date sanity and reference integrity. Each was verified by breaking it
  first — including three negative tests run against the merged tree before being reverted.
- `data/suggestions.json` is 46 rows (24 shipped, 20 open) and every shipped row names the pass
  that shipped it; 8 rows said “this session”, which stops meaning anything after nine sessions.
  `data/questions.json` is 29 rows, 8 blocking, 6 answered from a source.

## 6 · Counts, read from the registers

| Register | Now |
|---|---|
| Guides | 18 |
| Sources | 36 |
| Flagged items | 46 |
| Suggestions | 46 |
| Open questions | 29 (8 blocking, 6 answered) |
| Topic backlog | 24 (8 published) |
| Recorded reads on the freshness clock | 82 |
| `assets/img` | 40 files, 10.2 MB |

`npm run verify` on the merged tree: build → gate → analytics tests; `node tools/audit.mjs --strict`
reports no findings.

## 7 · Deliberately absent

No prices, ratings, review counts, stock levels, conversion scores, revenue forecasts or traffic
projections. No testing, ranking or endorsement claim. The supplied short links are still not called
invalid (FLG-003 unresolved) and `intended_*` fields stay blank. The analytics endpoint is still not
deployed (Pages is static, FLG-007). The ledger is still empty.
