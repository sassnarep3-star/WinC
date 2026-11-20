#!/usr/bin/env python3
"""Merge two versions of the registers without dropping a row or duplicating an id.

Written on 2026-11-20 by session ab951e4c, after nine parallel sessions each guessed at free
ids in COORDINATION.md and the guesses went stale three times in one day. Renumbering by hand is
where references get left behind pointing at somebody else's row, so both halves are mechanical:

  • the trunk's rows win their content and their ids;
  • a branch's rows are appended at ids this repo's allocator says are free;
  • every S/FLG/SG/Q/TP reference inside an appended row is rewritten with the same map;
  • a row whose title already exists on the trunk is skipped instead of duplicated;
  • the result is validated (json parse, unique ids, and the reference audit) before it is written.

    python3 scripts/merge_registers.py --trunk origin/main          # dry run: prints the plan
    python3 scripts/merge_registers.py --trunk origin/main --write  # apply it

Run it *during* a conflicted merge, then rebuild and let `scripts/check_site.py` be the judge.
`--ours` defaults to HEAD. Rows the trunk does not know about but whose ids are free are kept as-is.
"""
import argparse, io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import alloc_ids as A  # noqa: E402  (the single source of truth for ids and references)

REGISTERS = [("data/sources.json", "sources", "S"), ("data/flags.json", "flags", "FLG"),
             ("data/suggestions.json", "suggestions", "SG"), ("data/questions.json", "questions", "Q"),
             ("data/topics.json", "topics", "TP")]


def show(rev, rel):
    out = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return json.loads(out.stdout)


def worktree(rel):
    return json.load(io.open(os.path.join(ROOT, rel), encoding="utf-8"))


def title_of(row):
    return (row.get("title") or row.get("question") or row.get("slug") or "").strip()


def plan_and_apply(trunk_rev, ours_rev, write):
    total_map, added_total = {}, 0
    for rel, key, kind in REGISTERS:
        base = show(trunk_rev, rel)
        if base is None:
            print(f"  {rel}: absent on {trunk_rev}, nothing to merge into")
            continue
        # Read BOTH sides from commits: during a conflicted merge the working tree holds conflict
        # markers, and parsing that is the classic way a merge script dies halfway through.
        ours = show(ours_rev, rel)
        cur = ours or worktree(rel)
        if ours is None:
            print(f"  {rel}: {ours_rev} has no such file, skipped"); continue
        # rows this branch carries that the trunk does not, judged by title
        trunk_titles = {title_of(r) for r in base.get(key, [])}
        trunk_ids = {r.get("id") for r in base.get(key, [])}
        ours_ids = {r.get("id") for r in (ours or {}).get(key, [])}
        rows = list(base.get(key, []))
        have = {r.get("id") for r in rows}
        mapping = {}
        added = []
        for r in cur.get(key, []):
            rid, ttl = r.get("id"), title_of(r)
            if ttl and ttl in trunk_titles:
                continue                      # trunk owns this row's content; it wins
            if rid in trunk_ids and rid not in ours_ids:
                continue                      # same id, different row, and it is not ours to move
            nid = rid
            if nid in have or (rid in ours_ids and rid not in trunk_ids and rid in {x.get("id") for x in rows}):
                nid = rid
            if nid in have:
                # Allocate locally from what this merge already holds. Asking the allocator each
                # time reads the file on disk, which does not know about the rows appended a moment
                # ago — that loop never terminates when the next free id is already taken.
                nums = [int(m.group(1)) for x in have if (m := re.search(r"(\d+)$", str(x)))]
                nxt = A.norm(kind, max(nums) + 1) if nums else rid
                while nxt in have:
                    nxt = A.norm(kind, int(re.search(r"(\d+)$", nxt).group(1)) + 1)
                mapping[rid] = nxt
                nid = nxt
            row = (A.renum(r, mapping) if mapping else r)
            row["id"] = nid
            rows.append(row)
            have.add(nid)
            added.append((rid, nid))
        if mapping:
            # references inside *every* row of the merged file must follow the map, but only for
            # rows that came from this branch — the trunk's own citations are its business.
            moved = {nid for _, nid in added}
            rows = [r if r.get("id") not in moved else A.renum(r, mapping) for r in rows]
        doc = dict(base)
        doc[key] = rows
        ids = [r.get("id") for r in rows]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise SystemExit(f"REFUSED {rel}: duplicate ids {dupes} — the allocator should not allow this")
        added_total += len(added)
        total_map.update(mapping)
        print(f"  {rel}: {len(base.get(key, []))} trunk rows -> {len(rows)} "
              f"(+{len(added)} from this branch{', renumbered ' + ', '.join(f'{a}→{b}' for a, b in added if a != b) if any(a != b for a, b in added) else ''})")
        if write:
            with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
                f.write("\n")
    return total_map, added_total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trunk", default="origin/main")
    ap.add_argument("--ours", default="HEAD")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    print(f"merging registers: base = {a.trunk}, additions from {a.ours}" + ("" if a.write else "  [dry run]"))
    mapping, added = plan_and_apply(a.trunk, a.ours, a.write)
    print(f"\n{added} row(s) carried over; id map: {json.dumps(mapping) if mapping else 'no renumbering needed'}")
    if not a.write:
        print("dry run — nothing written. Re-run with --write, then rebuild and run the gate.")
        return 0
    if os.path.exists(os.path.join(ROOT, "data/questions.json")):
        d = worktree("data/questions.json")
        d["blocking_count"] = sum(1 for q in d["questions"] if str(q.get("blocking", "")).startswith("yes"))
        with io.open(os.path.join(ROOT, "data/questions.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False); f.write("\n")
        print(f"questions.blocking_count recomputed: {d['blocking_count']}")
    dangling, _, _ = A.find_dangling(skip_html=True)
    if dangling:
        print(f"\nWARNING — {len(dangling)} dangling reference(s) remain (run scripts/alloc_ids.py --check):")
        for d in dangling[:10]:
            print("   -", d)
        return 1
    print("reference audit: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
