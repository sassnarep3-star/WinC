#!/usr/bin/env python3
"""Third-round register reconciliation, with ids chosen deterministically.

The trunk wins every row it owns. This pass's rows are appended at ids above the trunk's
highest, and every reference inside those rows is rewritten with the same map before writing.
The map is printed for COORDINATION.md.
"""
import json, subprocess, io, os, re, collections

ROOT = "/home/user/WinC"
log = collections.defaultdict(list)


def git_show(rev, rel):
    out = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def dump(rel, obj):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def renum(obj, mapping):
    if isinstance(obj, str):
        for a, b in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
            obj = re.sub(rf"\b{re.escape(a)}\b", b, obj)
        return obj
    if isinstance(obj, list):
        return [renum(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: renum(v, mapping) for k, v in obj.items()}
    return obj


# ------------------------------------------------------------------ id map (HEAD numbering -> final)
MAP = {
    "S30": "S36",                                        # deep read of Program Policies §2–§6
    "FLG-026": "FLG-041", "FLG-027": "FLG-042", "FLG-028": "FLG-043", "FLG-029": "FLG-044",
    "SG-23": "SG-43", "SG-24": "SG-44", "SG-25": "SG-45", "SG-26": "SG-46",
    "SG-39": "SG-47", "SG-40": "SG-48", "SG-41": "SG-49", "SG-42": "SG-50",
    "Q-24": "Q-26", "Q-25": "Q-27", "Q-26": "Q-28", "Q-27": "Q-29",
    "TP-15": "TP-19", "TP-16": "TP-20", "TP-17": "TP-21", "TP-18": "TP-22", "TP-19": "TP-23", "TP-20": "TP-24",
}

# ------------------------------------------------------------------ sources
doc = git_show("origin/main", "data/sources.json")
have = {x["id"] for x in doc["sources"]}
mine = {x["id"]: x for x in git_show("HEAD", "data/sources.json")["sources"]}
row = dict(mine["S30"]); row["id"] = MAP["S30"]
doc["sources"].append(renum(row, MAP))
for x in doc["sources"]:
    if x["id"] == "S17" and "2 to 4 degrees F" not in x.get("what", ""):
        x["what"] = (x.get("what", "") + " Also read 2026-11-20 (session ab951e4c): “Most food thermometers will give an accurate reading "
          "within 2 to 4 degrees F”; ice-water calibration (stem ≥2 in, ≥30 s, should read 32°F); boiling-water calibration (212°F at sea "
          "level, distilled water, 2–5°F lower at altitude); “If the thermometer doesn't allow manual calibration, you may need to replace "
          "it”; care wording (most thermometers should not be immersed; plastic faces can melt; do not leave in food unless designed for "
          "it); the types table (oven-cord/fork “Cannot be calibrated”, thermistor “Some models can be calibrated”, thermocouple “Can be "
          "calibrated”, wireless/smart designed to remain in the food at ≥1 in deep and “more costly”; read times 2–5 s / 10 s / 1–2 min).")
        log["sources"].append("S17: FSIS calibration/care/types detail re-applied to the trunk row (additive)")
    if x["id"] == "S28" and "how-to-deprecation" not in x.get("what", ""):
        x["what"] = (x["what"] + " Read again 2026-11-20: the same changelog's #how-to-deprecation anchor confirms the HowTo documentation "
          "is likewise retired, which is why no HowTo markup is emitted here.")
        log["sources"].append("S28: HowTo half re-applied to the trunk row (additive)")
log["sources"].append(f"S30 -> {MAP['S30']}")
dump("data/sources.json", doc)

# ------------------------------------------------------------------ flags
doc = git_show("origin/main", "data/flags.json")
have = {x["id"] for x in doc["flags"]}
mine = {x["id"]: x for x in git_show("HEAD", "data/flags.json")["flags"]}
for mid in ["FLG-026", "FLG-027", "FLG-028", "FLG-029", "FLG-030", "FLG-031", "FLG-032", "FLG-033",
            "FLG-034", "FLG-035", "FLG-036", "FLG-037", "FLG-038", "FLG-039", "FLG-040"]:
    if mid not in mine:
        log["flags"].append(f"{mid}: absent from HEAD, skipped"); continue
    nid = MAP.get(mid, mid)
    while nid in have:
        nid = f"FLG-{int(nid[4:]) + 1:03d}"
    r = dict(mine[mid]); r["id"] = nid
    doc["flags"].append(renum(r, MAP))
    have.add(nid)
    log["flags"].append(f"{mid} -> {nid}")
doc["flags"].append({"id": "FLG-045",
  "title": "Third register-id collision inside one day: ids were allocated by guessing what other sessions would use",
  "detail": ("This branch claimed S27…S28, FLG-026…FLG-040, SG-21…SG-28 and Q-22…Q-26 against a board read at session start. Nine other PRs "
   "merged while it worked. Round one: the trunk already held S27, SG-21…SG-28 and Q-22/Q-23 for other findings, so this pass renumbered to "
   "S30, SG-39…SG-42, Q-24…Q-27, TP-15…TP-20. Round two (PRs #40…#48): the trunk had *also* taken those slots — S30…S35, SG-39…SG-42, "
   "Q-24…Q-25, TP-15…TP-18, FLG-026…FLG-029 — so the same rows needed new ids again. Renumbering at merge time is correct, but it is "
   "bookkeeping a machine can do, and each round is a chance to leave a reference pointing at another session's row."),
  "action": ("Closed structurally rather than by care: scripts/alloc_ids.py allocates ids from the merged tree at commit time and rewrites a row's "
   "own references with the same map, and scripts/check_site.py now fails any file (data, scripts, markdown, generated HTML) that cites an "
   "S/FLG/SG/Q/TP id absent from its register. This pass's fifteen flag rows are the first test of both."),
  "status": "fixed by tooling; allocation discipline enforced by the gate", "sources": [],
  "source_note": "Internal only — a coordination defect in this repository's own ids, found by the merge process itself."})
log["flags"].append("FLG-045 appended (collision record)")
dump("data/flags.json", doc)

# ------------------------------------------------------------------ suggestions
doc = git_show("origin/main", "data/suggestions.json")
have = {x["id"] for x in doc["suggestions"]}
mine = {x["id"]: x for x in git_show("HEAD", "data/suggestions.json")["suggestions"]}
for mid in ["SG-23", "SG-24", "SG-25", "SG-26", "SG-39", "SG-40", "SG-41", "SG-42"]:
    if mid not in mine:
        log["suggestions"].append(f"{mid}: absent from HEAD, skipped"); continue
    nid = MAP.get(mid, mid)
    while nid in have:
        nid = f"SG-{int(nid[3:]) + 1:02d}"
    r = dict(mine[mid]); r["id"] = nid
    doc["suggestions"].append(renum(r, MAP))
    have.add(nid)
    log["suggestions"].append(f"{mid} -> {nid}")
sby = {x["id"]: x for x in doc["suggestions"]}
if "SG-19" in sby and sby["SG-19"].get("status") != "done-this-session":
    sby["SG-19"]["status"] = "done-this-session"
    sby["SG-19"]["status_detail"] = ("Decided and shipped in the merge (2026-11-20, session ab951e4c): one optimized illustration set per "
      "product, deduplicated against the parallel set this pass drew — the trunk's art serves cards and product pages through the "
      "picture/webp helper, this pass's originals serve as guide header art, and the whole set sits at a few hundred kilobytes instead of "
      "megabytes. Owner photography stays an option under Q-07; nothing depends on a stock licence and no Amazon listing image is reused. "
      "See FLG-045 and the merge note in COORDINATION.md.")
    log["suggestions"].append("SG-19: status corrected against the code on trunk")
doc["_note"] = (doc.get("_note", "") + " Session ab951e4c's rows were renumbered twice during merges on 2026-11-20; a suggestion id is a "
                "register slot, not a citation, and cross-references were rewritten by scripts/alloc_ids.py-style mapping (FLG-045).")
dump("data/suggestions.json", doc)

# ------------------------------------------------------------------ questions
doc = git_show("origin/main", "data/questions.json")
have = {x["id"] for x in doc["questions"]}
mine = {x["id"]: x for x in git_show("HEAD", "data/questions.json")["questions"]}
qby = {x["id"]: x for x in doc["questions"]}
if qby.get("Q-22") and not qby["Q-22"].get("answer") and mine.get("Q-22", {}).get("answer"):
    qby["Q-22"].update(renum({k: mine["Q-22"][k] for k in ("answer", "sources", "source_note") if mine["Q-22"].get(k)}, MAP))
    log["questions"].append("Q-22: trunk row was blank; this pass's freshness-clock answer re-applied (absorbed, not duplicated)")
for mid in ["Q-24", "Q-25", "Q-26", "Q-27"]:
    if mid not in mine:
        log["questions"].append(f"{mid}: absent from HEAD, skipped"); continue
    nid = MAP.get(mid, mid)
    while nid in have:
        nid = f"Q-{int(nid[2:]) + 1:02d}"
    r = dict(mine[mid]); r["id"] = nid
    doc["questions"].append(renum(r, MAP))
    have.add(nid)
    log["questions"].append(f"{mid} -> {nid}")
for qid in ("Q-07", "Q-12", "Q-13", "Q-15", "Q-19"):
    if mine.get(qid, {}).get("answer") and qid in qby and not qby[qid].get("answer"):
        qby[qid].update(renum({k: mine[qid][k] for k in ("answer", "sources", "source_note") if mine[qid].get(k)}, MAP))
        log["questions"].append(f"{qid}: answer re-applied (trunk row was blank)")
doc["blocking_count"] = sum(1 for q in doc["questions"] if str(q.get("blocking", "")).startswith("yes"))
dump("data/questions.json", doc)

# ------------------------------------------------------------------ topics
doc = git_show("origin/main", "data/topics.json")
have = {x["id"] for x in doc["topics"]}
mine = {x["id"]: x for x in git_show("HEAD", "data/topics.json")["topics"]}
for mid in ["TP-15", "TP-16", "TP-17", "TP-18", "TP-19", "TP-20"]:
    if mid not in mine:
        continue
    nid = MAP.get(mid, mid)
    while nid in have:
        nid = f"TP-{int(nid[3:]) + 1:02d}"
    r = dict(mine[mid]); r["id"] = nid
    doc["topics"].append(renum(r, MAP))
    have.add(nid)
    log["topics"].append(f"{mid} -> {nid}")
trow = {(x.get("title") or ""): x for x in doc["topics"]}
for row in git_show("HEAD", "data/topics.json")["topics"]:
    if row.get("status") != "published":
        continue
    tgt = trow.get(row.get("title"))
    if tgt and tgt.get("status") in ("planned", "blocked"):
        for k in ("status", "published_as", "status_note"):
            if k in row:
                tgt[k] = renum(row[k], MAP)
        if row.get("source"):
            tgt["source"] = renum(row["source"], MAP)
        log["topics"].append(f"trunk row marked published with a pointer: “{row['title'][:38]}…”")
dump("data/topics.json", doc)

# ------------------------------------------------------------------ products
doc = git_show("origin/main", "data/products.json")
mine = {p["id"]: p for p in git_show("HEAD", "data/products.json")["products"]}
for p in doc["products"]:
    src = mine.get(p["id"], {})
    for k in ("shelf_line", "decide_on"):
        if src.get(k):
            p[k] = renum(src[k], MAP)
    p["image_alt"] = src.get("image_alt") or src.get("image", "")
    p["image_alt_caption"] = src.get("image_alt_caption") or src.get("image_caption", "")
    p["image_note"] = ("Cards and product pages use `image` (the trunk illustration set) through the picture/webp helper; `image_alt` is the "
      "parallel set this pass drew, used as guide header art. Both are original editorial illustrations. See FLG-045.")
dump("data/products.json", doc)

json.dump(MAP, io.open(os.path.join(ROOT, ".merge-tmp", "idmap.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in log.items()}, indent=1))
print("\nFINAL MAP:", json.dumps(MAP, indent=1))
for rel, key in [("data/sources.json", "sources"), ("data/flags.json", "flags"), ("data/suggestions.json", "suggestions"),
                 ("data/questions.json", "questions"), ("data/topics.json", "topics"), ("data/products.json", "products")]:
    d = json.load(io.open(os.path.join(ROOT, rel), encoding="utf-8"))
    print(rel.split("/")[-1], len(d[key]), "tail:", [r.get("id") for r in d[key]][-5:])
