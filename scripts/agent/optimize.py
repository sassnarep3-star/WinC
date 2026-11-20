#!/usr/bin/env python3
"""Step 4 — optimise. Read the campaign ledger and say what it actually supports.

Usage:
    python3 scripts/agent/optimize.py

Reads data/campaign-ledger.json and, when it exists, data/events.json (first-party click
events). Writes data/optimisation.json.

The rule: a recommendation must be traceable to a number this project obtained from an
authorised first-party report, with a date. While the ledger is empty there is no revenue
signal, no conversion score and no forecast — so this step prints the exact rows to collect
and refuses to rank products, pick a winner, or estimate what a change would earn. That is
not a missing feature; it is the difference between optimisation and guessing.

Every row added to the ledger must carry: timestamp, source, channel, eligible sessions,
clicks, and reported orders — with the orders figure taken from an authorised report (the
Associates Central order report), never from an estimate.
"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load, save, today  # noqa: E402

LEDGER_COLUMNS = [
    ("timestamp", "When the row was written (ISO date)"),
    ("source", "Where the number came from, e.g. 'Associates Central order report'"),
    ("channel", "Which surface: page, guide, product page, search, newsletter"),
    ("url", "The exact page the click was on"),
    ("eligible_sessions", "Sessions that were eligible under the reporting definition"),
    ("clicks", "Outbound clicks on a sponsored link"),
    ("reported_orders", "Orders reported by the authorised first-party report"),
    ("notes", "Anything a reader of the ledger needs to interpret the row"),
]


def main():
    led = load("data/campaign-ledger.json")
    rows = led.get("rows") or []
    events = None
    if os.path.exists(os.path.join(ROOT, "data", "events.json")):
        events = load("data/events.json")

    filled = [r for r in rows if any(r.get(c) not in (None, "") for c, _ in LEDGER_COLUMNS
                                      if c not in ("notes",))]

    out = {
        "generated": today(),
        "generated_by": "scripts/agent/optimize.py",
        "ledger_rows": len(rows),
        "ledger_rows_with_numbers": len(filled),
        "first_party_events_present": events is not None,
        "recommendations": [],
        "collection_plan": [],
        "policy": ("A recommendation needs a first-party number and a date. Until the ledger has "
                   "rows, this step reports what to collect and makes no claim about revenue, "
                   "conversion rate or which product performs best."),
    }

    if not filled:
        out["headline"] = ("No measured data yet. No recommendation can be made, and none is made.")
        out["collection_plan"] = [
            {"column": c, "meaning": m, "why": "Without this column a later row cannot be interpreted."}
            for c, m in LEDGER_COLUMNS
        ]
        out["next_step"] = (
            "Turn on the click counter (assets/app.js) and the self-hosted endpoint in analytics/, "
            "then fill one row per (date, channel, page) with numbers taken from the endpoint and "
            "the Associates Central order report. See measurement.html for the five recorded events "
            "and the open questions that gate the endpoint.")
    else:
        # With data, only make statements the rows support.
        by_channel = {}
        for r in filled:
            ch = r.get("channel") or "(not stated)"
            b = by_channel.setdefault(ch, {"clicks": 0, "reported_orders": 0, "sessions": 0, "rows": 0})
            for k, col in (("clicks", "clicks"), ("reported_orders", "reported_orders"),
                           ("eligible_sessions", "sessions")):
                try:
                    b[k] += int(r.get(col) or 0)
                except (TypeError, ValueError):
                    pass
            b["rows"] += 1
        out["by_channel"] = by_channel
        out["headline"] = ("%d ledger row(s) carry first-party numbers. Only channels with rows are "
                           "reported; nothing is extrapolated." % len(filled))
        out["next_step"] = ("Re-run this after each reporting period. A channel with clicks but no "
                            "reported orders is a question, not a failure — check the destination and "
                            "the tracking report (FLG-002) before drawing a conclusion.")

    save("data/optimisation.json", out)
    print(out["headline"])
    for r in out["recommendations"]:
        print(" - %s" % r)
    if not out["recommendations"]:
        print("No recommendation was made. That is the correct output for the current ledger state.")
    if out["collection_plan"]:
        print("\nTo make one possible, collect:")
        for c in out["collection_plan"]:
            print("  - %-20s %s" % (c["column"], c["meaning"]))
    print("\nWrote data/optimisation.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
