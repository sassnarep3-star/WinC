#!/usr/bin/env python3
"""Freshness clock for externally-sourced claims (session ab951e4c, 2026-11-20).

Why this exists
---------------
Amazon Associates Program Policies §6(c) requires an Associate to *promptly* remove
Program Content that is no longer displayed on an Amazon Site. Everything on this
site that describes a product was copied from a listing on a recorded date
(`source_date`), and the food-safety and policy sentences were read from a
government or docs page on a recorded date. A date recorded once is not a
permanent fact: listings change, and nothing in a repository can see that.

What this does
--------------
It measures the *age of every recorded read* against the current date and reports
rows that have gone stale. It never invents a new value, never refreshes a date,
and never contacts a network. If a row is past the hard limit the script exits 1,
which is the signal that the row must be re-read from its official source — or
removed.

    python3 scripts/freshness.py                  # human report, exit 1 past hard limit
    python3 scripts/freshness.py --json           # machine-readable
    python3 scripts/freshness.py --as-of 2026-11-20   # deterministic (used by the gate)
    python3 scripts/freshness.py --soft 7 --hard 30   # custom thresholds

The numbers to change live in data/freshness.json, not in this file.
"""
import argparse, datetime, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, "data", "freshness.json")
DEFAULTS = {"soft_days": 14, "hard_days": 45,
            "note": "Thresholds for the age of a recorded read. Soft = worth re-checking; hard = do not publish without re-reading the source."}


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def parse(d):
    return datetime.date.fromisoformat(str(d).strip()[:10])


def rows(as_of):
    """(id, kind, field, date, age_days, source_url) for every externally-sourced value."""
    out = []

    def add(rid, kind, field, date_str, url):
        if not date_str:
            out.append({"id": rid, "kind": kind, "field": field, "date": None,
                        "age_days": None, "source": url or "", "state": "no date recorded"})
            return
        try:
            d = parse(date_str)
        except ValueError:
            out.append({"id": rid, "kind": kind, "field": field, "date": str(date_str),
                        "age_days": None, "source": url or "", "state": "unparseable date"})
            return
        out.append({"id": rid, "kind": kind, "field": field, "date": d.isoformat(),
                    "age_days": (as_of - d).days, "source": url or "", "state": ""})

    for p in load("data/products.json")["products"]:
        add(p["id"], "product", "source_date (listing read)", p.get("source_date"), p.get("source_url"))
        add(p["id"], "product", "observed_date (redirect observation)", p.get("observed_date"), p.get("observed_source"))
        for url in (p.get("live_read_fields") or {}).get("sources", []) if isinstance(p.get("live_read_fields"), dict) else []:
            add(p["id"], "product", "field-level source", p.get("source_date"), url)

    for g in sorted(glob.glob(os.path.join(ROOT, "data", "guides", "*.json"))):
        name = os.path.basename(g)
        if name.startswith("_"):
            continue
        with open(g, encoding="utf-8") as f:
            doc = json.load(f)
        add(doc.get("slug", name), "guide", "updated", doc.get("updated"), "")
        add(doc.get("slug", name), "guide", "published", doc.get("published"), "")

    for s in load("data/sources.json")["sources"]:
        add(s["id"], "source", "retrieval date", s.get("date"), s.get("url"))

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default="", help="ISO date to measure against (default: today)")
    ap.add_argument("--soft", type=int, default=0)
    ap.add_argument("--hard", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    cfg = DEFAULTS
    if os.path.exists(CFG_PATH):
        with open(CFG_PATH, encoding="utf-8") as f:
            cfg = {**DEFAULTS, **json.load(f)}
    soft = a.soft or cfg["soft_days"]
    hard = a.hard or cfg["hard_days"]
    as_of = parse(a.as_of) if a.as_of else datetime.date.today()

    rs = rows(as_of)
    for r in rs:
        if r["age_days"] is None:
            r["state"] = r["state"] or "no age"
        elif r["age_days"] > hard:
            r["state"] = "past hard limit — re-read the source or remove the claim"
        elif r["age_days"] > soft:
            r["state"] = "past soft limit — worth re-reading"
        elif r["age_days"] < 0:
            r["state"] = "date is in the future (clock or data error)"
        else:
            r["state"] = "fresh"

    bad = [r for r in rs if r["state"].startswith("past hard") or r["state"].startswith("unparseable")
           or r["state"].startswith("date is in the future")]
    warn = [r for r in rs if r["state"].startswith("past soft")]

    if a.json:
        print(json.dumps({"as_of": as_of.isoformat(), "soft_days": soft, "hard_days": hard,
                          "rows": rs, "counts": {"total": len(rs), "stale": len(bad), "aging": len(warn)}},
                         indent=2))
    else:
        print(f"freshness clock · as of {as_of.isoformat()} · soft {soft}d / hard {hard}d")
        widths = [max(len(str(r[k])) for r in rs) if rs else 0 for k in ("id", "kind", "field", "date")]
        for r in rs:
            age = "  n/a" if r["age_days"] is None else f"{r['age_days']:>4}d"
            mark = {"fresh": "  ok ", "past soft limit — worth re-reading": " warn ",
                    }.get(r["state"], "FAIL " if r["state"].startswith("past hard") else "  ·  ")
            print(f" [{mark}] {r['id']:<{widths[0]}} {r['kind']:<7} {r['field']:<{widths[2]}} "
                  f"{str(r['date']):<{widths[3]}} {age}  {r['state']}")
        print(f"\n{len(rs)} recorded reads: {len(bad)} past hard limit, {len(warn)} past soft limit.")
        if bad:
            print("Action: re-read each FAIL row against the official URL listed in data/sources.json, "
                  "update the date, and re-run npm run build && npm run check. Program Policies §6(c) "
                  "requires prompt removal of Program Content Amazon no longer displays (see FLG-027).")
        else:
            print("No row is past the hard limit. Run this again before publishing.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
