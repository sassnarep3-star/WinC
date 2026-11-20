#!/usr/bin/env python3
"""Second-round register reconciliation: this branch's rows onto trunk ids as they now stand.

Nothing here overwrites a trunk row. Colliding ids are renumbered into free slots and the
mapping is printed so COORDINATION.md can record it. References inside the moved rows are
rewritten with the same map, which is the part a human forgets and a gate should enforce.
"""
import json, subprocess, io, os, re, collections

ROOT = "/home/user/WinC"
log = collections.defaultdict(list)


def trunk(rel):
    out = subprocess.run(["git", "show", f"origin/main:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def base(rel):
    """This branch's pre-merge view (HEAD), which already carries pass-1 + merge-1 ids."""
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True, text=True, check=True)
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


def title_of(r):
    return r.get("title") or r.get("question") or ""


def union(rel, key, prefix, my_ids, mapping, extra_rows=None, absorb=None, post=None):
    """Trunk file wins; append my rows that the trunk lacks, renumbering id collisions."""
    doc = trunk(rel)
    rows = doc[key]
    have = {r["id"] for r in rows}
    by_title = {title_of(r): r for r in rows}
    n = max((int(re.search(r"(\d+)$", r["id"]).group(1)) for r in rows if re.search(r"(\d+)$", r["id"])), default=0)
    mydoc = base(rel)
    mine = {r["id"]: r for r in mydoc[key]}
    out_map = {}
    for mid in my_ids:
        row = mine.get(mid)
        if row is None:
            log[key].append(f"{mid}: not in this branch, skipped")
            continue
        ab = (absorb or {}).get(mid)
        if ab:
            target = next((x for x in rows if x["id"] == ab[0]), None)
            if target is not None:
                ab[1](target, renum(row, mapping))
                log[key].append(f"{mid}: merged into trunk {ab[0]}")
                out_map[mid] = ab[0]
                continue
        if title_of(row) in by_title and by_title[title_of(row)]["id"] in have:
            out_map[mid] = by_title[title_of(row)]["id"]
            log[key].append(f"{mid}: identical row already on trunk ({out_map[mid]}), skipped")
            continue
        nid = row["id"]
        if nid in have:
            n += 1
            nid = f"{prefix}{n:02d}"
            row = dict(row); row["id"] = nid
            log[key].append(f"{row['id']} <- {mid} (trunk uses {mid} for something else)")
        else:
            log[key].append(f"{mid} appended unchanged")
        row = renum(row, mapping)
        row["id"] = nid if nid.startswith(prefix) else row["id"]
        rows.append(row)
        have.add(nid)
        out_map[mid] = nid
    for extra in (extra_rows or []):
        extra = renum(extra, mapping)
        while extra["id"] in have:
            n += 1
            extra = dict(extra); extra["id"] = f"{prefix}{n:02d}"
        rows.append(extra); have.add(extra["id"])
        log[key].append(f"{extra['id']} appended (new this merge)")
    doc[key] = rows
    if post:
        post(doc, {**mapping, **out_map})
    dump(rel, doc)
    return doc, out_map


# ------------------------------------------------ sources: my policies row -> free id
SDOC, SRC_MAP = union("data/sources.json", "sources", "S-", ["S27"], {"S27": "S36", "S28": "S28"})
# re-apply this pass's enrichment to the trunk's FSIS + Google rows (additive, idempotent)
for x in SDOC["sources"]:
    if x["id"] == "S17" and "2 to 4 degrees F" not in x.get("what", ""):
        x["what"] = (x.get("what", "") + " Also read 2026-11-20 (session ab951e4c): “Most food thermometers will give an accurate "
            "reading within 2 to 4 degrees F”; ice-water calibration (stem ≥2 in, ≥30 s, should read 32°F); boiling-water calibration "
            "(212°F at sea level, distilled water, 2–5°F lower at altitude); “If the thermometer doesn't allow manual calibration, you "
            "may need to replace it”; care wording (most thermometers should not be immersed; plastic faces can melt; do not leave in "
            "food unless designed for it); the types table (oven-cord/fork “Cannot be calibrated”, thermistor “Some models can be "
            "calibrated”, thermocouple “Can be calibrated”, wireless/smart designed to remain in food at ≥1 in deep, “more costly”, "
            "read times 2–5 s / 10 s / 1–2 min).")
        log["sources"].append("S17: FSIS calibration/care detail re-applied to the trunk row")
    if x["id"] == "S28" and "how-to-deprecation" not in x.get("what", ""):
        x["what"] = (x.get("what", "") + " Read again 2026-11-20: the same changelog's #how-to-deprecation anchor confirms the HowTo "
            "documentation is likewise retired, which is why no HowTo markup is emitted here.")
        log["sources"].append("S28: HowTo half of the changelog note re-applied to the trunk row")
dump("data/sources.json", SDOC)
SRC_MAP["S27"] = "S36"
MAP = dict(SRC_MAP)
log["sources"].append(f"map: {MAP}")

# ------------------------------------------------ flags: my 15 rows land after the trunk's FLG-029
MY_FLAGS = ["FLG-026", "FLG-027", "FLG-028", "FLG-029", "FLG-030", "FLG-031", "FLG-032", "FLG-033",
            "FLG-034", "FLG-035", "FLG-036", "FLG-037", "FLG-038", "FLG-039", "FLG-040"]
FLGDOC, FLG_MAP = union("data/flags.json", "flags", "FLG-", MY_FLAGS, MAP)
FLGDOC, FLG_MAP2 = (FLGDOC, FLG_MAP)
# the third collision in one day is itself a finding
FLGDOC["flags"].append({
  "id": "FLG-045",
  "title": "Third register-id collision in a single day: ids were allocated by guessing what other sessions had used",
  "detail": ("This branch allocated S27…S28, FLG-026…FLG-040, SG-21…SG-28 and Q-22…Q-26 against a board it had read at the start of the "
   "session. Eight other PRs merged while it worked, so on the first rebase the trunk already held S27 (a different source), SG-21…SG-28 "
   "(different suggestions) and Q-22/Q-23 (different questions); after that renumbering the trunk moved again (PRs #40…#48) and took the very "
   "slots the renumbering had chosen — S30…S35, SG-39…SG-42, Q-24…Q-25, TP-15…TP-18, FLG-026…FLG-029. Renumbering at merge time is correct but "
   "it is bookkeeping a machine can do, and every round of it is a chance to leave a reference pointing at someone else's row."),
  "action": ("scripts/alloc_ids.py added: allocate an id from the merged tree at commit time instead of guessing, and rewrite a row's own "
   "references with the same map. check_site.py gained a cross-register rule: every S/FLG/SG/Q/TP reference anywhere in data/, scripts/, the "
   "markdown documents and the generated HTML must exist in its register, so a half-renumbered row cannot publish. This pass's own rows are the "
   "first test of both."),
  "status": "fixed by tooling; allocation discipline now enforced", "sources": [],
  "source_note": "Internal only — a coordination defect in this repository's own ids, found by the merge and closed structurally rather than by care."})
dump("data/flags.json", FLGDOC)
log["flags"].append(f"map: {FLG_MAP2} + FLG-045")
MAP.update({k: v for k, v in FLG_MAP2.items() if k != v})
MAP["FLG-036"] = FLG_MAP2.get("FLG-036", "FLG-036")

# ------------------------------------------------ suggestions: my rows past the trunk's SG-42
MY_SUG = ["SG-23", "SG-24", "SG-25", "SG-26", "SG-39", "SG-40", "SG-41", "SG-42"]
SUGDOC, SG_MAP = union("data/suggestions.json", "suggestions", "SG-", MY_SUG, MAP)
sby = {x["id"]: x for x in SUGDOC["suggestions"]}
# the trunk's own rows that this pass's decisions touch
for sid, patch in [
  ("SG-19", {"status": "done-this-session",
    "status_detail": "Decided and shipped in the merge (2026-11-20, session ab951e4c): one optimized illustration set per product, deduplicated "
      "against the parallel set this pass drew — the trunk's art serves cards and product pages through the picture/webp helper, this pass's "
      "originals serve as guide header art, and the whole set sits at a few hundred KB instead of megabytes. Owner photography stays an option "
      "under Q-07; nothing depends on a stock licence and no Amazon listing image is reused. See FLG-040."}),
  ("SG-26", None),
]:
    if sid in sby and patch:
        if sby[sid].get("status") != patch["status"]:
            sby[sid].update(patch)
            log["suggestions"].append(f"{sid}: status corrected against the code")
if SG_MAP:
    SUGDOC["_note"] = (SUGDOC.get("_note", "") + " Session ab951e4c's rows were renumbered twice during merges on 2026-11-20 "
        f"({', '.join(f'{k}→{v}' for k, v in SG_MAP.items() if k != v)}); a suggestion id is a register slot, not a citation.")
dump("data/suggestions.json", SUGDOC)
MAP.update({k: v for k, v in SG_MAP.items() if k != v})
log["suggestions"].append(f"map: {SG_MAP}")

# ------------------------------------------------ questions: my rows past the trunk's Q-25
MY_Q = ["Q-24", "Q-25", "Q-26", "Q-27"]
QDOC, Q_MAP = union("data/questions.json", "questions", "Q-", MY_Q, MAP,
    absorb={"Q-22": ("Q-22", lambda tgt, row: tgt.update({"answer": (tgt.get("answer") or "") or (
      "Partly answered 2026-11-20 (session ab951e4c): scripts/freshness.py computes the age of every recorded read and fails past the threshold "
      "in data/freshness.json, so a stale or vanished listing is visible before it is cited; scripts/check_site.py re-runs the date-integrity half "
      "on every build. The human half stays open — who removes the content, and within how long (Program Policies §6(c), S36).")} if not tgt.get("answer") else {}))})
qby = {x["id"]: x for x in QDOC["questions"]}
for qid in ("Q-07", "Q-12", "Q-13", "Q-15", "Q-19"):
    row = base("data/questions.json")
    mine_row = next((x for x in row["questions"] if x["id"] == qid), None)
    if mine_row and mine_row.get("answer") and qid in qby and not qby[qid].get("answer"):
        qby[qid].update(renum({k: mine_row[k] for k in ("answer", "sources", "source_note") if k in mine_row}, MAP))
        log["questions"].append(f"{qid}: answer re-applied (trunk row was blank)")
QDOC["blocking_count"] = sum(1 for q in QDOC["questions"] if str(q.get("blocking", "")).startswith("yes"))
if Q_MAP:
    QDOC["_note"] = (QDOC.get("_note", "") + f" Session ab951e4c's rows renumbered during the second merge ({', '.join(f'{k}→{v}' for k, v in Q_MAP.items() if k != v)}).")
dump("data/questions.json", QDOC)
MAP.update({k: v for k, v in Q_MAP.items() if k != v})
log["questions"].append(f"map: {Q_MAP}")

# ------------------------------------------------ topics: my rows past the trunk's TP-18
MY_TP = ["TP-15", "TP-16", "TP-17", "TP-18", "TP-19", "TP-20"]
TDOC, TP_MAP = union("data/topics.json", "topics", "TP-", MY_TP, MAP)
trow = {title_of(x): x for x in TDOC["topics"]}
for row in base("data/topics.json")["topics"]:
    if row.get("status") != "published":
        continue
    tgt = trow.get(title_of(row))
    if tgt and tgt.get("status") in ("planned", "blocked"):
        for k in ("status", "published_as", "status_note"):
            if k in row:
                tgt[k] = renum(row[k], MAP) if isinstance(row[k], str) else row[k]
        if row.get("source"):
            tgt["source"] = renum(row["source"], MAP)
        log["topics"].append(f"marked published on the trunk row “{title_of(row)[:34]}…”")
if "published_as" not in json.dumps(TDOC):
    log["topics"].append("no published_as applied (trunk rows already marked published)")
dump("data/topics.json", TDOC)
MAP.update({k: v for k, v in TP_MAP.items() if k != v})
log["topics"].append(f"map: {TP_MAP}")

# ------------------------------------------------ products: trunk's art + webp pipeline wins
PDOC = trunk("data/products.json")
mine_p = {p["id"]: p for p in base("data/products.json")["products"]}
for p in PDOC["products"]:
    src = mine_p.get(p["id"], {})
    for k in ("shelf_line", "decide_on"):
        if src.get(k):
            p[k] = renum(src[k], MAP)
    p["image_alt"] = src.get("image_alt") or src.get("image", "")
    p["image_alt_caption"] = src.get("image_alt_caption") or src.get("image_caption", "")
    p["image_note"] = ("Cards and product pages use this (the trunk set) through the picture/webp helper; image_alt is the parallel "
      "illustration this pass drew, used as guide header art. Both are original editorial illustrations. See FLG-040.")
    log["products"].append(f"{p['id']}: image stays the trunk's {p.get('image')}; shelf_line/decide_on re-applied")
dump("data/products.json", PDOC)

json.dump(MAP, io.open(os.path.join(ROOT, ".merge-tmp", "idmap.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in log.items()}, indent=1))
print("\nFINAL MAP:", json.dumps(MAP, indent=1))
