# Audit — independent gate

Run: `node tools/audit.mjs` · date: 2026-11-20

--------------------------------------------------------------------------

Scanned 38 published HTML pages, 117 tracked files (archive/ excluded — that tree is a retired alternate build, not a live surface).
Canonical disclosure string is fixed inside this file, quoted from Associates Program Operating Agreement §5,
so editing site configuration cannot switch the check off.

## What each rule protects

| Rule | Prevents | Authority |
|---|---|---|
| A1 | a reader finding out about the commission after the click | Agreement §5 |
| A2 | untagged buy links earning nothing; tagged citations implying a paid placement | Policies §2(b), §1; Google sponsored value |
| A3 | redirect intermediaries | Policies §6 “Redirecting Links” |
| A4 | prices/ratings we may not publish | Policies §2(b), §6(t) |
| A5 | verdicts about products we have not tested | Policies §1 original content; Google helpful-content |
| A6 | 404s and layout shift | crawl quality |
| A7 | capture without transport, synthetic traffic, per-user sub-tags | Policies §2(b), §6(s) |
| A8 | pages that cannot be found, or locs that 404 | indexing basics |
| A9 | leaking credentials by publishing data/ | operational safety |
| A10 | an unsourced product claim reaching the page | this project's own rule |

--------------------------------------------------------------------------
No findings.
