import io, subprocess, re, os
ROOT="/home/user/WinC"
def git(rev, rel):
    return subprocess.run(["git","show",f"{rev}:{rel}"],cwd=ROOT,capture_output=True,text=True,check=True).stdout

# ---------------- COORDINATION.md: trunk verbatim + this session's sections
main = git("origin/main","COORDINATION.md").rstrip("\n")
mine = git("HEAD","COORDINATION.md")
i = mine.find("# Session ab951e4c —")
sec = mine[i:].rstrip("\n")
# this section was written before the second rebase: fix ids and add the second-round note
for old,new in [("S27 →","S36 →"),("as **S30**","as **S36**"),("SG-39 … SG-42","SG-43 … SG-50"),
                ("Q-24…Q-27","Q-26…Q-29"),("TP-15…TP-20","TP-19…TP-24")]:
    sec = sec.replace(old,new)
sec += """

## Second merge round (ab951e4c ← main `1d389bd`, PRs #40…#48)

The trunk moved again while this reconciliation was being written, and it had taken the very ids
the first renumbering had chosen. Round two, applied by `.merge-tmp` scripts and then re-checked:

| This pass's rows (after round one) | Final id | Why |
| --- | --- | --- |
| S30 deep read of Program Policies §2–§6 | **S36** | trunk filled S30…S35 with its own dated listing re-reads |
| FLG-026…029 (§6(d) endorsement, §6(c) removal, §5 ML, §4 email) | **FLG-041…FLG-044** | trunk's FLG-026…029 are different findings |
| FLG-030…040 | unchanged | free slots on trunk |
| SG-23…26, SG-39…42 | **SG-43…SG-50** | trunk filled both ranges with other suggestions |
| Q-24…Q-27 | **Q-26…Q-29** | trunk added Q-24 (site name) and Q-25 (illustration terms) |
| TP-15…TP-20 | **TP-19…TP-24** | trunk added TP-15…TP-18 |
| freshness question (was Q-24 in round one) | absorbed into trunk **Q-22** | same question, one row |

Trunk-wins files: `scripts/build_site.py`, `scripts/check_site.py`, `scripts/new_guide.py`,
`assets/style.css`, `tools/audit.mjs`, `package.json`, every generated page — each of this pass's
26 builder deltas re-applied on top with an assertion per patch (the one that no longer matched —
the front-page kicker, which the trunk had rewritten entirely — was skipped rather than forced).
`data/products.json`: the trunk's webp-backed illustration pipeline serves the shelf; this pass's
`shelf_line` / `decide_on` fields and `image_alt` artwork were added to it.

Structural response, because guessing ids three times in a day is the actual defect:
**`scripts/alloc_ids.py`** allocates the next free id from the merged tree and audits every
cross-register reference; **FLG-045** records the collision; **FLG-046** records a four-row gap in
the suggestions register that a live citation pointed into (found by the new checker on its first
run, and it predates this pass). The gate now runs the reference audit, so a half-renumbered row
cannot publish.

Verification on the merged tree: `npm run build` → *Built 41 pages, 40 sitemap URLs, 18 guides,
35 search rows*; `npm run check` → *no violations*; `node tools/audit.mjs --strict` → see the PR
record below; `npm test` → analytics contract tests OK.
"""
io.open(f"{ROOT}/COORDINATION.md","w",encoding="utf-8").write(main + "\n\n---\n\n" + sec + "\n")

# ---------------- README.md: trunk + this pass's machinery, into their own section
rd = git("origin/main","README.md").rstrip("\n")
add = """

## Machinery added on 2026-11-20 (session `ab951e4c`)

```bash
python3 scripts/freshness.py            # age of every recorded read; --as-of YYYY-MM-DD is deterministic
python3 scripts/alloc_ids.py --next FLG # next free id in a register, from the merged tree
python3 scripts/alloc_ids.py --check    # every S/FLG/SG/Q/TP reference must resolve
python3 scripts/ledger_add.py --help    # the only route a figure may take into the campaign ledger
# or: npm run fresh
```

- **Why a freshness clock exists.** Program Policies §6(c) requires an Associate to remove Program
  Content promptly once Amazon no longer displays it. Nothing in a repository can see Amazon's site,
  so the tool measures the one thing it does know: how old each recorded read is. Thresholds live in
  `data/freshness.json`, not in code. The removal decision stays human.
- **Why an id allocator exists.** Nine sessions worked in parallel today and each guessed which ids
  were free. Two rounds of renumbering later, `scripts/alloc_ids.py` is the authority on both
  allocation and reference integrity, and the gate runs its check on every build.
- **Why the ledger has a bouncer.** `scripts/ledger_add.py` refuses a row without `--authorized`,
  a non-integer or derived value, an estimating word, or an undated provenance string. The file
  stays empty until a first-party report exists — empty is the correct state, not a missing step.

Standing rules the gate enforces, added in the same pass: no flag ids, model strings or ASINs on a
shelf card; one optimized illustration per product (no shared or oversized asset); ledger rows carry
only the seven schema keys; the §6(d) non-endorsement statement must stay on the disclosure page;
recorded dates must be parseable and not in the future.
"""
io.open(f"{ROOT}/README.md","w",encoding="utf-8").write(rd + add + "\n")
print("README + COORDINATION resolved")
