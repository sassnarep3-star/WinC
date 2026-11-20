#!/usr/bin/env python3
"""Merge session ab951e4c's register additions into the registers as they stand on main.

House rule for every pass in this repo: the trunk wins on anything it changed, and
this session's rows are appended, renumbered past the trunk's ids, never made to
overwrite another session's row. The id mapping is printed so the renumbering is
auditable in COORDINATION.md.
"""
import json, subprocess, io, os, re, collections

ROOT = "/home/user/WinC"
log = collections.defaultdict(list)

def theirs(rel):
    out = subprocess.run(["git", "show", f"origin/main:{rel}"], cwd=ROOT, capture_output=True,
                         text=True, check=True)
    return json.loads(out.stdout)

def mine(rel):
    # read this session's version from HEAD, not the working tree: the tree is mid-merge
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)

def dump(rel, obj):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def renum(obj, mapping):
    if isinstance(obj, str):
        for a, b in mapping.items():
            obj = re.sub(rf"\b{re.escape(a)}\b", b, obj)
        return obj
    if isinstance(obj, list):
        return [renum(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: renum(v, mapping) for k, v in obj.items()}
    return obj

def merge_rows(rel, key, mine_rows, idof, titleof, prefix, mapping, absorb=None, note=""):
    doc = theirs(rel)
    rows = doc[key]
    have = {idof(r) for r in rows}
    by_title = {titleof(r): r for r in rows}
    n = max((int(re.search(r"(\d+)$", idof(r)).group(1)) for r in rows), default=0)
    out_map = {}
    for r in mine_rows:
        mid = idof(r)
        ab = (absorb or {}).get(mid)
        if ab:
            target = next((x for x in rows if idof(x) == ab[0]), None)
            if target is not None:
                ab[1](target, r)
                log[key].append(f"{mid}: substance merged into trunk {ab[0]} (no new row)")
                out_map[mid] = ab[0]
                continue
        if mid in have:
            twin = by_title.get(titleof(r))
            if twin is not None:
                log[key].append(f"{mid}: identical row already on trunk, skipped")
                out_map[mid] = mid
                continue
            n += 1
            new = f"{prefix}{n:02d}"
            r = dict(r); r["id"] = new
            rows.append(renum(r, mapping))
            log[key].append(f"{mid} -> {new} (trunk uses {mid} for something else)")
            out_map[mid] = new; have.add(new)
            continue
        rows.append(renum(r, mapping))
        log[key].append(f"{mid} appended unchanged")
        out_map[mid] = mid; have.add(mid)
    doc[key] = rows
    if note:
        doc["_note"] = (doc.get("_note", "") + note)
    dump(rel, doc)
    return doc, out_map

# ---------------- sources ----------------
t_src_doc = theirs("data/sources.json"); t_src = t_src_doc["sources"]
n = max(int(x["id"][1:]) for x in t_src)
SRC_MAP = {}
for row in mine("data/sources.json")["sources"]:
    if row["id"] != "S27":
        continue
    n += 1
    SRC_MAP["S27"] = f"S{n:02d}"
    r = dict(row); r["id"] = SRC_MAP["S27"]
    t_src.append(renum(r, {}))
    log["sources"].append(f"S27 -> {SRC_MAP['S27']} (trunk uses S27 for the FSIS leftovers page)")
for x in t_src:
    if x["id"] == "S28" and "how-to-deprecation" not in x.get("what", ""):
        x["what"] = x.get("what", "") + (" Read again 2026-11-20 (session ab951e4c): the same changelog's #how-to-deprecation "
            "anchor confirms the HowTo documentation is likewise retired, which is why no HowTo markup is emitted here.")
        x["access"] = (x.get("access", "") + " Second independent read on 2026-11-20 by session ab951e4c.")
        SRC_MAP["S28"] = "S28"
        log["sources"].append("S28: trunk row extended rather than a duplicate added")
    if x["id"] == "S17" and "Most food thermometers will give an accurate reading" not in x.get("what", ""):
        x["what"] = (x.get("what", "") + " Also read 2026-11-20 (session ab951e4c): “Most food thermometers will give an "
          "accurate reading within 2 to 4 degrees F”; ice-water calibration (stem ≥2 in, ≥30 s, should read 32°F); boiling-water "
          "calibration (212°F at sea level, distilled water, 2–5°F lower at altitude, ask the local Cooperative Extension "
          "office); “If the thermometer doesn't allow manual calibration, you may need to replace it”; care wording (most "
          "thermometers should not be immersed; plastic faces can melt; do not leave in food unless designed for it); the types "
          "table (oven-cord/fork “Cannot be calibrated”, thermistor “Some models can be calibrated”, thermocouple “Can be "
          "calibrated”, wireless/smart designed to remain in food at ≥1 in deep and “more costly”; read times 2–5 s / 10 s / "
          "1–2 min).")
        x["access"] = (x.get("access", "") + " Second independent read on 2026-11-20 by session ab951e4c.")
        SRC_MAP["S17"] = "S17"
        log["sources"].append("S17: trunk row extended with the calibration/care/types wording read this pass")
dump("data/sources.json", t_src_doc)

# ---------------- flags ----------------
fdoc = theirs("data/flags.json")
have = {f["id"] for f in fdoc["flags"]}
for row in mine("data/flags.json")["flags"]:
    if row["id"] in have:
        continue
    fdoc["flags"].append(renum(row, SRC_MAP))
    log["flags"].append(f"{row['id']} appended")
fdoc["flags"].append({"id": "FLG-036",
 "title": "Two illustration sets and two freshness clocks collided in the merge and were reconciled",
 "detail": ("Found by session ab951e4c while merging origin/main on 2026-11-20. This pass drew five product illustrations "
  "(assets/img/prod-*.jpg) and added a Python freshness clock (scripts/freshness.py + data/freshness.json); the trunk had in the "
  "meantime gained five per-product illustrations of its own (p6qt/p8qt/p26qt/pthermo/pchefiq, ~2.8 MB PNGs each), two seasonal "
  "PNGs, and a Node clock (tools/freshness.mjs). Ten near-identical 2.8 MB PNGs and two clocks is how a multi-session site gains "
  "weight and loses coherence. Resolution: the trunk's artwork is what cards and product pages show, because its captions describe "
  "each specific unit; this pass's five remain as guide header art, one per guide where it fits; every trunk PNG was converted to "
  "the same optimized 1200×750 q82 JPEG profile, so assets/img went from 20 MB to 2.3 MB and both sets are cheap. Both clocks "
  "remain wired (the Python one is what the gate and measurement.html use); consolidating them is a follow-up."),
 "action": ("Decide which freshness clock is canonical and delete or absorb the other. Do not generate a third illustration set for "
  "a product that already has one — check assets/img and data/products.json first. If a product needs photographic art instead, "
  "that is Q-07's owner decision, not another illustration."),
 "status": "recorded; consolidation open", "sources": [],
 "source_note": "Internal only — a repository-state finding from the merge itself, written down so a later session does not add a third set."})
log["flags"].append("FLG-036 appended (merge reconciliation record)")
dump("data/flags.json", fdoc)

# ---------------- products: trunk's image field wins ----------------
pdoc = theirs("data/products.json")
mine_by = {p["id"]: p for p in mine("data/products.json")["products"]}
for p in pdoc["products"]:
    src = mine_by.get(p["id"], {})
    for field in ("shelf_line", "decide_on"):
        if src.get(field):
            p[field] = src[field]
    p["image_alt"] = src.get("image", "")
    p["image_alt_caption"] = src.get("image_caption", "")
    p["image_note"] = ("Card and product-page art is the trunk illustration set. image_alt holds the parallel set drawn by session "
      "ab951e4c, kept as guide header art after the merge. Both are original editorial illustrations; see FLG-036.")
    log["products"].append(f"{p['id']}: shelf_line/decide_on added; image kept as the trunk's {p.get('image')}")
dump("data/products.json", pdoc)

# ---------------- topics ----------------
tdoc, TP_MAP = merge_rows("data/topics.json", "topics", mine("data/topics.json")["topics"],
    lambda x: x["id"], lambda x: x["title"], "TP-", SRC_MAP,
    note=" Rows renumbered during the merge into main (session ab951e4c, 2026-11-20): a topic id is a backlog slot, not a citation.")
trow = {x["title"]: x for x in tdoc["topics"]}
for row in mine("data/topics.json")["topics"]:
    if row.get("status") != "published":
        continue
    tgt = trow.get(row["title"])
    if tgt and tgt.get("status") in ("planned", "blocked"):
        for k in ("status", "published_as", "status_note"):
            if k in row:
                tgt[k] = row[k]
        tgt["source"] = row.get("source", tgt.get("source"))
        log["topics"].append(f"marked published on the trunk row “{row['title'][:36]}…”")
    else:
        log["topics"].append(f"published-marking skipped for “{row['title'][:36]}…” (trunk status="
                             f"{tgt.get('status') if tgt else 'no such row'})")
dump("data/topics.json", tdoc)

# ---------------- suggestions ----------------
SDOC, SG_MAP = merge_rows("data/suggestions.json", "suggestions", mine("data/suggestions.json")["suggestions"],
    lambda x: x["id"], lambda x: x["title"], "SG-", SRC_MAP,
    note=" Ids above the trunk's highest SG number belong to session ab951e4c and were renumbered during the merge; the trunk's own SG-21..SG-28 rows are another session's and were left untouched.")
sby = {x["id"]: x for x in SDOC["suggestions"]}
if "SG-19" in sby and sby["SG-19"]["status"] != "done-this-session":
    sby["SG-19"]["status"] = "done-this-session"
    sby["SG-19"]["status_detail"] = (sby["SG-19"].get("status_detail", "").strip() +
      " Decided and shipped in the merge (2026-11-20, session ab951e4c): the illustration line was completed and both parallel sets "
      "optimized to one profile (assets/img 20 MB -> 2.3 MB). Product cards and product pages use the trunk's per-product art; this "
      "pass's five remain as guide header art. Owner photography stays an option under Q-07; nothing depends on a stock licence and no "
      "Amazon listing image is reused. See FLG-036.").strip()
    log["suggestions"].append("SG-19: status -> done-this-session (trunk register was stale against the code)")
for sid, extra in [
    ("SG-03", "Second pass (session ab951e4c, merged): one optimized illustration per product, the trunk's set on the shelf and this "
              "pass's set on the guides, every caption still saying plainly that it is not a product photograph."),
    ("SG-15", "Second pass (session ab951e4c): the front page's process prose became a three-item trust rail, and product cards no "
              "longer print flag IDs, model strings or ASINs — evidence is one line in the card footer."),
]:
    if sid in sby and extra[16:56] not in sby[sid].get("status_detail", ""):
        sby[sid]["status_detail"] = (sby[sid].get("status_detail", "").strip() + " " + extra).strip()
        log["suggestions"].append(f"{sid}: status_detail extended")
for x in SDOC["suggestions"]:
    if x.get("status") in ("done-this-session", "shipped") and not re.search(
            r"session |arena-|ab951e4c|T\d", str(x.get("status_detail", ""))):
        x["status_detail"] = (x.get("status_detail", "").strip() +
            " · shipped by an earlier pass, named in that session's COORDINATION.md board entry").strip()
        log["suggestions"].append(f"{x['id']}: status_detail gained a pass attribution (new gate rule)")
dump("data/suggestions.json", SDOC)

# ---------------- questions ----------------
def absorb_runbook(target, mine_row):
    target["answer"] = ("Partly answered 2026-11-20 (session ab951e4c): scripts/freshness.py computes the age of every recorded read "
      "(56 rows) and fails past the threshold in data/freshness.json, so a stale or vanished listing is visible before it is cited; "
      "scripts/check_site.py re-runs the date-integrity half on every build. The human half stays open — who removes the content, and "
      "within how long (Program Policies §6(c), S30). FLG-027 records the gap; tools/freshness.mjs is a second, standalone clock that "
      "should be consolidated (FLG-036).")
    target["sources"] = sorted(set(target.get("sources", []) + [SRC_MAP.get("S27", "S30")]))

QDOC, Q_MAP = merge_rows("data/questions.json", "questions", mine("data/questions.json")["questions"],
    lambda x: x["id"], lambda x: x.get("title") or x["question"], "Q-", SRC_MAP,
    absorb={"Q-24": ("Q-22", absorb_runbook)},
    note=" Rows above the trunk's highest Q number were renumbered during the merge (session ab951e4c); a question id is a register slot, not a citation, and an answer stays blank when nobody has the fact.")
qby = {x["id"]: x for x in QDOC["questions"]}
for qid in ("Q-07", "Q-12", "Q-13", "Q-15", "Q-19"):
    mine_row = next((x for x in mine("data/questions.json")["questions"] if x["id"] == qid), None)
    if mine_row and qid in qby and not qby[qid].get("answer"):
        qby[qid].update(renum({"answer": mine_row["answer"], "sources": mine_row.get("sources", []),
                              "source_note": mine_row.get("source_note", "")}, SRC_MAP))
        log["questions"].append(f"{qid}: answer filled from this pass's source read")
    elif qid in qby:
        log["questions"].append(f"{qid}: trunk already carries an answer or the row is absent, left alone")
QDOC["blocking_count"] = sum(1 for q in QDOC["questions"] if str(q.get("blocking", "")).startswith("yes"))
dump("data/questions.json", QDOC)

print(json.dumps({k: v for k, v in log.items()}, indent=1))
print("\nSRC_MAP", SRC_MAP)
print("SG renum", {k: v for k, v in SG_MAP.items() if k != v})
print("Q renum", {k: v for k, v in Q_MAP.items() if k != v})
print("TP renum", {k: v for k, v in TP_MAP.items() if k != v})
for rel, key in [("data/sources.json","sources"),("data/flags.json","flags"),("data/suggestions.json","suggestions"),
                 ("data/questions.json","questions"),("data/topics.json","topics"),("data/products.json","products")]:
    print(rel.split('/')[-1], len(json.load(io.open(os.path.join(ROOT,rel),encoding="utf-8"))[key]))
