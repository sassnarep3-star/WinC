#!/usr/bin/env python3
"""Record observation #5 (session arena/6561e2ea-winc, 2026-11-20) in the redirect log.

The five supplied links were re-resolved live by this session through the same reader method
the earlier observations used. All five mappings reproduced again. This script appends the
per-row observation markers, updates the interpretation, and adds the provenance row.

It records only what was observed. The intended identifiers stay blank: a fifth reproduction
of a fallback route is still a fallback route, and nothing about it says what was meant.
"""
import json, collections, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBES = os.path.join(ROOT, "data", "probes.json")
SOURCES = os.path.join(ROOT, "data", "sources.json")
SESSION = "arena/6561e2ea-winc"
DATE = "2026-11-20"

# token -> what this session saw on the resolved listing
OBSERVED = {
    "B04G1MEwY": {
        "final_asin": "B0CDY277D3",
        "final_title": ("Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View "
                        "Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick "
                        "Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : "
                        "Home & Kitchen"),
        "breadcrumb_top": "Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers",
    },
    "B02NbDxp3": {
        "final_asin": "B09B7SB46R",
        "final_title": ("Amazon.com: Emeril Lagasse 26QT French Door Air Fryer, Convection Oven, "
                        "Toaster Oven, 26 Quart Stainless Steel, 24 Presets, 6 Cooking Accessories "
                        "Included, Dark Stainless Steel : Home & Kitchen"),
        "breadcrumb_top": "Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers",
    },
    "B00hJ57DV": {
        "final_asin": "B08DKYBTPH",
        "final_title": ("Amazon.com: CHEFMAN 8 Quart Large Air Fryer, 4-in-1 Air Fryer Oven, "
                        "TurboFry 4-in-1 with 450°F Hi-Fry, XL Nonstick Dishwasher-Safe Basket, "
                        "Digital Dual Air Fryer - Black : Home & Kitchen"),
        "breadcrumb_top": "Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers",
    },
    "B0c8moW59": {
        "final_asin": "B0DHZTCNR5",
        "final_title": ("Amazon.com: ThermoMaven 1 Second Instant Read Digital Meat Thermometer, "
                        "IP67 Waterproof Kitchen Food Thermometer for Cooking, Grilling, Smoker, "
                        "Camping : Kitchen & Dining"),
        "breadcrumb_top": "Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat",
    },
    "B0f3GKalj": {
        "final_asin": "B0DZFD6R9Z",
        "final_title": ("Amazon.com: CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin "
                        "Probes | WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | BBQ, Grill, "
                        "Oven, Smoker, Air Fryer | Gen3 : Home & Kitchen"),
        "breadcrumb_top": "Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat",
    },
}


def main():
    with io.open(PROBES, encoding="utf-8") as f:
        doc = json.load(f, object_pairs_hook=collections.OrderedDict)
    rows = doc["probes"]
    seen = 0
    tokens = set()
    for r in rows:
        tok = r.get("submitted_token")
        if tok not in OBSERVED:
            continue
        o = OBSERVED[tok]
        if r.get("final_asin") != o["final_asin"]:
            raise SystemExit("%s: observed ASIN changed to %s — this script only records "
                             "reproductions, not replacements" % (tok, o["final_asin"]))
        r["observation_5"] = collections.OrderedDict([
            ("session", SESSION),
            ("date", DATE),
            ("observation", 5),
            ("final_asin", o["final_asin"]),
            ("final_title", o["final_title"]),
            ("breadcrumb_top", o["breadcrumb_top"]),
            ("agrees_with_prior_observations", True),
            ("method", "Live HTTP resolution through the fetch_page reader, same method as observations #2, #3 and #4."),
        ])
        r["session"] = r.get("session") or SESSION
        r["date"] = r.get("date") or DATE
        seen += 1
        tokens.add(tok)
    if tokens != set(OBSERVED):
        raise SystemExit("expected the five tokens %s, got %s"
                         % (sorted(OBSERVED), sorted(tokens)))

    doc["probe_dates"].append("%s observation #5: %s" % (DATE, SESSION))
    doc["probe5_note"] = (
        "Fifth independent observation (session %s, %s), via live HTTP resolution through the "
        "fetch_page reader, same method as observations #2, #3 and #4. All five mappings "
        "reproduced 5/5 again — the fifth consecutive reproduction. Every resolved listing "
        "served its own product title and category breadcrumb, and every title matches the "
        "title stored in data/products.json, so the five products in the shop are still the five "
        "products the submitted tokens resolve to. The listing-internal conflicts observed by "
        "earlier sessions still stand on this capture: the Emeril <title> still says “Six "
        "Cooking Accessories Included” (FLG-010), the Chefman 8 Qt <title> still carries the "
        "450°F Hi-Fry wording against captured 200–400°F copy (FLG-005), and the ThermoMaven "
        "<title> wording rotated again (FLG-014). Nothing in this observation says anything the "
        "earlier ones did not: every final URL still carries lv=shuf and plpRedirect=mhFallback, "
        "so FLG-009’s fallback-route reading stands, and the intended_* fields remain blank. "
        "Provenance row: S31." % (SESSION, DATE))

    interp = doc["interpretation"]
    interp["reproduced"] = (
        "All five mappings have now been observed live on five separate occasions (2026-11-17 in "
        "the prior sessions, and four times on 2026-11-20 by sessions arena-23d7ed19, "
        "arena-82d39deb, arena-c2123b9c and %s). Every observation agrees, 5/5, so FLG-008 stays "
        "closed and the observed_* fields are reproducible rather than single-session noise."
        % SESSION)
    interp["what_reproduction_does_not_prove"] = (
        "Every final URL carries lv=shuf (shuffle) and plpRedirect=mhFallback (listing-page "
        "fallback). That is a fallback route, not a canonical resolution of the submitted token. "
        "The targets are stable per token across all five observations, so they are a usable "
        "observation — but they do not confirm that the person who supplied the links intended "
        "these five products. Five reproductions strengthen the observation and do not change "
        "what it is. Intended fields therefore stay blank.")

    with io.open(PROBES, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("observation #5 recorded on %d rows" % seen)

    # provenance row
    with io.open(SOURCES, encoding="utf-8") as f:
        sdoc = json.load(f, object_pairs_hook=collections.OrderedDict)
    if "S31" not in {s["id"] for s in sdoc["sources"]}:
        sdoc["sources"].append(collections.OrderedDict([
            ("id", "S31"),
            ("title", "Fifth redirect observation — data/probes.json, observation #5"),
            ("url", "https://www.amazon.com/dp/B0CDY277D3"),
            ("what", "All five supplied link.amazon tokens re-resolved live on 2026-11-20 by session arena/6561e2ea-winc through the fetch_page reader, the same method as observations #2-#4. 5/5 mappings reproduced for the fifth consecutive time: B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R, B00hJ57DV→B08DKYBTPH, B0c8moW59→B0DHZTCNR5, B0f3GKalj→B0DZFD6R9Z. Each resolved listing served its own title and breadcrumb, and each title matches data/products.json exactly. Every final URL still carries lv=shuf + plpRedirect=mhFallback, so the fallback-route reading (FLG-009) stands and the intended_* fields remain blank."),
            ("date", "2026-11-20"),
            ("access", "Fetched directly on 2026-11-20 by session arena/6561e2ea-winc. Per-row markers are in data/probes.json under observation_5."),
        ]))
        with io.open(SOURCES, "w", encoding="utf-8") as f:
            json.dump(sdoc, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("source S31 added")


if __name__ == "__main__":
    main()
