#!/usr/bin/env python3
"""Append ONE measured row to the campaign ledger, with the gate in front of it.

The ledger (data/campaign-ledger.json) exists to hold figures obtained from
authorized first-party reports — an Amazon Associates Central report export, or
the owner's own analytics endpoint. It starts empty and the brief says so:
"add timestamp, source, channel, eligible sessions, clicks and reported orders
only when obtained from authorized first-party reports. Keep a dated provenance
trail. No conversion score or revenue forecast."

So this tool is deliberately obstructive:

  * it refuses any row whose source or provenance contains an estimating word
    (estimate, forecast, project, assume, backfill, model, infer, extrapolate, approximate);
  * it requires --authorized, a positive statement that the numbers were read
    out of a first-party report, not computed from a guess;
  * it requires a provenance string that names the artefact and carries a date
    (YYYY-MM-DD), because an undated figure cannot be re-checked;
  * it accepts only non-negative integers, or the literal word `null` for a
    field the report did not contain — an absent number stays absent;
  * it will not compute a rate. No column here is derived from another column.

    python3 scripts/ledger_add.py \\
        --timestamp 2026-12-05T00:00:00Z \\
        --source "Associates Central > Reports > Earnings" \\
        --channel "site:guides" \\
        --clicks 41 --orders 2 --sessions null \\
        --provenance "earnings-2026-12-05.csv, exported by the owner on 2026-12-05, kept in /records" \\
        --authorized --dry-run

Then re-run without --dry-run, and rebuild:
    python3 scripts/build_site.py && python3 scripts/check_site.py
"""
import argparse, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "data", "campaign-ledger.json")

# Words that mean "this number was not read out of a report".
BANNED = re.compile(r"\b(estimat\w*|forecast\w*|project(ing|ion|ed)?|assum\w*|backfill\w*|"
                    r"model(?:led|ing)?|infer\w*|extrapolat\w*|approximat\w*|guessed?|assumed)\b", re.I)
FIELDS = ("timestamp", "source", "channel", "eligible_sessions", "clicks", "reported_orders", "provenance")


def die(msg, code=2):
    print(f"REFUSED — {msg}")
    sys.exit(code)


def num_or_null(raw, field):
    if raw is None or raw.strip().lower() in ("", "null", "none", "—"):
        return None
    if not re.fullmatch(r"\d+", raw.strip()):
        die(f"{field} must be a non-negative integer or the literal word null; got {raw!r}. "
            "A number the report did not state stays blank — it is never derived from another field.")
    return int(raw.strip())


def check_timestamp(v):
    s = v.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            datetime.date.fromisoformat(s)
            return s
        iso = s[:-1] + "+00:00" if s.endswith("Z") else s
        datetime.datetime.fromisoformat(iso)
        return s
    except ValueError:
        die(f"timestamp {v!r} is not ISO-8601 (use 2026-12-05 or 2026-12-05T00:00:00Z).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timestamp", required=True, help="when the figure was observed or exported (ISO-8601)")
    ap.add_argument("--source", required=True, help="exact report or system name, e.g. 'Associates Central > Reports > Earnings'")
    ap.add_argument("--channel", required=True, help="e.g. 'site:guides', 'site:products', 'direct'")
    ap.add_argument("--sessions", default="null", help="eligible_sessions: integer or null")
    ap.add_argument("--clicks", default="null", help="clicks: integer or null")
    ap.add_argument("--orders", default="null", help="reported_orders: integer or null")
    ap.add_argument("--provenance", required=True, help="file name or URL of the export, plus the export date (YYYY-MM-DD)")
    ap.add_argument("--authorized", action="store_true", help="confirm the figures were read out of an authorized first-party report")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not a.authorized:
        die("no --authorized flag. The ledger accepts a row only when the numbers came from an "
            "authorized first-party report (Associates Central export, Creators API, or the site's own "
            "analytics endpoint). Nothing in this repo has access to those, so if you are reading this "
            "from a sandbox: stop, and leave the ledger empty.")

    row = {"timestamp": check_timestamp(a.timestamp), "source": a.source.strip(), "channel": a.channel.strip(),
           "eligible_sessions": num_or_null(a.sessions, "eligible_sessions"), "clicks": num_or_null(a.clicks, "clicks"),
           "reported_orders": num_or_null(a.orders, "reported_orders"), "provenance": a.provenance.strip()}

    if all(row[k] is None for k in ("eligible_sessions", "clicks", "reported_orders")):
        die("every measured field is null — that is a placeholder, not a row. At least one figure must "
            "come from the report (the others may stay null if the report did not state them).")

    for k in ("source", "channel", "provenance"):
        m = BANNED.search(row[k])
        if m:
            die(f"{k} contains {m.group(0)!r}, which is the vocabulary of an estimate. "
                "This ledger holds only figures that were read out of a report.")
    if not re.search(r"\d{4}-\d{2}-\d{2}", row["provenance"]):
        die("provenance must carry the export date as YYYY-MM-DD so the row can be re-checked later.")
    if len(row["provenance"]) < 20:
        die("provenance is too short to identify an artefact. Name the file or URL and the date it was taken.")

    with open(LEDGER, encoding="utf-8") as f:
        doc = json.load(f)
    rows = doc.get("rows", [])
    key = (row["timestamp"], row["source"], row["channel"])
    if any((r.get("timestamp"), r.get("source"), r.get("channel")) == key for r in rows):
        die("an identical row (same timestamp + source + channel) is already in the ledger — not duplicating it.")

    print("row the ledger would hold:")
    for k in FIELDS:
        print(f"  {k:<19} {row[k] if row[k] is not None else '— (not stated by the report)'}")

    if a.dry_run:
        print("\ndry run — nothing written. Re-run without --dry-run to append.")
        return

    rows.append(row)
    rows.sort(key=lambda r: str(r.get("timestamp", "")))
    doc["rows"] = rows
    trail = doc.setdefault("provenance_trail", [])
    trail.append({"date": datetime.date.today().isoformat(),
                  "action": f"Row appended by scripts/ledger_add.py (fields: {', '.join(k for k in FIELDS if k not in ('timestamp', 'provenance'))})",
                  "rows_added": 1,
                  "source": row["source"], "provenance": row["provenance"]})
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, LEDGER)
    print(f"\nappended. ledger now holds {len(rows)} row(s); rebuild with: python3 scripts/build_site.py")


if __name__ == "__main__":
    main()
