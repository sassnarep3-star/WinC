#!/usr/bin/env python3
"""Allocate register ids from the merged tree, and prove no reference dangles.

Why this exists (2026-11-20, session ab951e4c)
---------------------------------------------
Nine sessions worked this repository in parallel today. Every one of them had to choose an id for a
new row — `FLG-0nn`, `SG-nn`, `Q-nn`, `Snn`, `TP-nn` — by reading COORDINATION.md at the start of its
run and guessing what nobody else had taken yet. That guess went stale three times inside one day, so
rows were renumbered at merge time, and a renumbering is where a reference gets left behind
pointing at another session's row. See the flag titled "Third register-id collision inside one day".

Allocation is arithmetic, not judgement. So is reference checking. Both live here so the builder,
the gate and a human use the same numbers.

    python3 scripts/alloc_ids.py --next FLG            # the next free flag id
    python3 scripts/alloc_ids.py --next SG --count 3   # three free suggestion ids
    python3 scripts/alloc_ids.py --check               # dangling cross-register references
    python3 scripts/alloc_ids.py --rewrite FLG-026=FLG-041 --file data/flags.json
                                                    # rewrite ids in one file, id field included

`--check` is what `scripts/check_site.py` calls, so a stale citation fails the build instead of
waiting for a reader to notice that the flag it points at is about someone else's listing.
"""
import argparse, glob, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# register file -> (key holding the rows, id prefix, zero-padding)
REGISTERS = {
    "S":  ("data/sources.json",    "sources",    2),
    "FLG": ("data/flags.json",     "flags",      3),
    "SG": ("data/suggestions.json", "suggestions", 2),
    "Q":  ("data/questions.json",  "questions",  2),
    "TP": ("data/topics.json",     "topics",     2),
}
# A reference is a bare token: S07, FLG-012, SG-3, Q-15, TP-9. Bounded so a token inside a longer code never matches.
PATTERNS = {
    "S":   re.compile(r"(?<![A-Za-z0-9-])S(\d{2,3})(?![\d-])"),
    "FLG": re.compile(r"(?<![A-Za-z0-9-])FLG-(\d{3})(?![\d])"),
    "SG":  re.compile(r"(?<![A-Za-z0-9-])SG-(\d{2,3})(?![\d])"),
    "Q":   re.compile(r"(?<![A-Za-z0-9-])Q-(\d{2,3})(?![\d])"),
    "TP":  re.compile(r"(?<![A-Za-z0-9-])TP-(\d{2,3})(?![\d])"),
}


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def register_ids(kind):
    rel, key, width = REGISTERS[kind]
    doc = load(rel)
    out = set()
    for row in doc.get(key, []):
        rid = row.get("id") or row.get("slug") or ""
        m = re.fullmatch(rf"{re.escape(kind)}-?(\d+)", str(rid))
        if m:
            out.add(f"{kind}-{int(m.group(1)):0{width}d}" if kind != "S" else f"S{int(m.group(1)):0{width}d}")
    return out


def norm(kind, num):
    """Canonical id string for a kind + numeric part (S has no dash)."""
    width = REGISTERS[kind][2]
    if kind == "S":
        return f"S{int(num):0{width}d}"
    return f"{kind}-{int(num):0{width}d}"


def next_ids(kind, count=1):
    width = REGISTERS[kind][2]
    used = set()
    rel, key, _ = REGISTERS[kind]
    for row in load(rel).get(key, []):
        m = re.search(r"(\d+)$", str(row.get("id", "")))
        if m:
            used.add(int(m.group(1)))
    n = max(used) if used else 0
    out = []
    for _ in range(count):
        n += 1
        while norm(kind, n) in used:
            n += 1
        used.add(n)
        out.append(norm(kind, n))
    return out


def files_to_scan(html=True, data=True, docs=True, code=True):
    out = []
    if data:
        out += sorted(glob.glob(os.path.join(ROOT, "data", "**", "*.json"), recursive=True))
    if docs:
        # COORDINATION.md is deliberately NOT scanned: it is an append-only board, and each entry
        # quotes the ids as they read on the day it was written. Rewriting history to satisfy a
        # checker would destroy the thing that makes the board useful.
        out += [os.path.join(ROOT, n) for n in
                ("README.md", "EXECUTIVE-SUMMARY.md", "analytics/README.md")
                if os.path.exists(os.path.join(ROOT, n))]
    if code:
        out += sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))) + sorted(glob.glob(os.path.join(ROOT, "tools", "*.mjs")))
    if html:
        out += sorted(glob.glob(os.path.join(ROOT, "*.html"))) + sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
    seen, res = set(), []
    for f in out:
        r = os.path.relpath(f, ROOT)
        if r in seen or r.startswith("archive/") or "/archive/" in r or "node_modules" in r:
            continue
        seen.add(r)
        res.append(r)
    return res


def find_dangling(skip_html=True):
    """Every S/FLG/SG/Q/TP reference in the tree must exist in its register."""
    valid = {k: register_ids(k) for k in PATTERNS}
    dangling, counts = [], {k: 0 for k in PATTERNS}
    for rel in files_to_scan(html=not skip_html):
        text = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore").read()
        for kind, pat in PATTERNS.items():
            for m in pat.finditer(text):
                cid = norm(kind, m.group(1))
                counts[kind] += 1
                if cid not in valid[kind]:
                    line = text[:m.start()].count("\n") + 1
                    dangling.append(f"{rel}:{line}: cites {cid}, which is not in {REGISTERS[kind][0]}")
    return dangling, counts, valid


def rewrite(mapping, rel):
    """Renumber ids inside one file.

    The row's own `id` field is rewritten by the same rule as every prose citation, which is the
    step a human editing by hand gets wrong: the table of ids moves and the sentences do not.
    An id already claimed by another row is refused rather than silently duplicated.
    """
    path = os.path.join(ROOT, rel)
    text = io.open(path, encoding="utf-8").read()
    after = {}
    for src, dst in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        src, dst = src.strip(), dst.strip()
        n_from = len(re.findall(rf"(?<![A-Za-z0-9-]){re.escape(src)}(?![\d])", text))
        text = re.sub(rf"(?<![A-Za-z0-9-]){re.escape(src)}(?![\d])", dst, text)
        after[dst] = after.get(dst, 0) + n_from
    json.loads(text)  # refuse to write a file we just broke
    ids = re.findall(r'"id":\s*"([^"]+)"', text)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"REFUSED — rewriting {rel} would duplicate id(s): {', '.join(dupes)}. "
                         "Pick ids from --next, which only offers free ones.")
    io.open(path, "w", encoding="utf-8").write(text)
    return len(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", metavar="KIND", help="print the next free id for KIND (S, FLG, SG, Q, TP)")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--check", action="store_true", help="scan the tree for dangling cross-register references")
    ap.add_argument("--all-files", action="store_true", help="with --check, also scan generated HTML (slower)")
    ap.add_argument("--rewrite", action="append", default=[], metavar="OLD=NEW", help="renumber ids in --file")
    ap.add_argument("--file", help="file to rewrite (relative to the repository root)")
    a = ap.parse_args()

    if a.next:
        kind = a.next.upper().replace("FLG", "FLG")
        if kind not in REGISTERS:
            print(f"unknown register {kind!r}; choose from {', '.join(REGISTERS)}")
            return 2
        print(" ".join(next_ids(kind, a.count)))
        return 0

    if a.rewrite:
        if not a.file:
            print("--rewrite needs --file"); return 2
        mapping = {}
        for pair in a.rewrite:
            src, dst = pair.split("=", 1)
            mapping[src.strip()] = dst.strip()
        rewrite(mapping, a.file)
        print(f"rewrote {a.file}: {', '.join(f'{k}→{v}' for k, v in mapping.items())}")
        return 0

    if a.check:
        dangling, counts, valid = find_dangling(skip_html=not a.all_files)
        scope = "data, docs, scripts and tools" + (" + generated HTML" if a.all_files else "")
        print(f"reference check · {scope}")
        for k in sorted(counts):
            print(f"  {k:<4} {len(valid[k]):>3} registered · {counts[k]:>5} references scanned")
        if dangling:
            print(f"\nFAIL: {len(dangling)} dangling reference(s):")
            for d in dangling[:40]:
                print("  -", d)
            if len(dangling) > 40:
                print(f"  … {len(dangling) - 40} more")
            print("\nA renumbering must rewrite the references too. Either fix the citation, or")
            print("append the row the citation points at. Do not delete the sentence to pass the gate:")
            print("the reference is how a reader checks the claim.")
            return 1
        print("\nOK: every cross-register reference resolves.")
        return 0

    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
