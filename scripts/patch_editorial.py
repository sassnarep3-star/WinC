#!/usr/bin/env python3
"""One-shot: add editorial voice fields to data/products.json (session arena/6561e2ea-winc).

Every dek / best_for / catch / check_before_buying line below is a reading of data that is
already in this repository's own source register (the Amazon listing text captured in
data/products.json, or a flag the register already raises). Nothing here introduces a
price, a rating, a test result or a new spec. The listing title stays verbatim in
`title` and is no longer used as card body copy.
"""
import json, collections, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "products.json")

EDITORIAL = {
    "p1-chefman-6qt": {
        "dek": "Two 3-quart baskets that can finish at the same time, in the space one basket usually takes.",
        "best_for": "Cooking a main and a side together",
        "catch": "Each basket is 3 quarts, so one large item — a whole bird, a full sheet pan — will not fit in either one.",
        "check_before_buying": [
            "Measure your counter depth against the listed 13.38\" and leave room in front for the drawer to pull out.",
            "Decide whether you cook two things at once. If you usually cook one, a single 8-quart basket is the simpler buy.",
            "Check on the listing which parts are dishwasher-safe before you plan on hand-washing them.",
        ],
        "image": "assets/img/product-chefman-6qt.png",
        "image_caption": "Editorial illustration of a dual-basket air fryer with both baskets pulled open. Not a photograph of this product.",
    },
    "p2-emeril-26qt": {
        "dek": "A real countertop oven — French doors, wire racks, a cavity you can put a tray in — and the biggest one in the shop.",
        "best_for": "Baking, roasting, and cooking for more than four",
        "catch": "26.5 lb and 16.9 inches deep. It is the heaviest and the largest thing here, and it needs the most counter and the most cleaning.",
        "check_before_buying": [
            "Measure depth against the listed 16.9\" and check the cabinet clearance above it, not just the footprint.",
            "Count the presets you will actually use. Twenty-four options only help if they match your week.",
            "Budget for the racks, pan and accessories the listing says are included — more parts means more to wash.",
        ],
        "image": "assets/img/product-emeril-26qt.png",
        "image_caption": "Editorial illustration of a stainless French-door countertop oven. Not a photograph of this product.",
    },
    "p3-chefman-8qt": {
        "dek": "One large basket with a wide opening — the simplest footprint of the three fryers here.",
        "best_for": "One big batch of one thing",
        "catch": "The listing's own title and bullet copy disagree about the top temperature (FLG-005), and it does not mention viewing windows the way the 6-quart model does.",
        "check_before_buying": [
            "Re-read the temperature range on the live listing before you rely on it — the copy on that page conflicts (FLG-005).",
            "Check both the 12.75\" depth and the 13.5\" width; the drawer needs clearance in front as well as behind.",
            "If you plan to check the food without stopping the cook, confirm the listing mentions a window for this model.",
        ],
        "image": "assets/img/product-chefman-8qt.png",
        "image_caption": "Editorial illustration of a single-basket air fryer with the drawer partly open. Not a photograph of this product.",
    },
    "p4-thermomaven": {
        "dek": "A spot-check thermometer: pull it, press it, read it, put it back in the drawer.",
        "best_for": "Checking doneness without committing to a cook",
        "catch": "It tells you where the food is at the moment you ask. Nothing is watching it while you are doing something else.",
        "check_before_buying": [
            "Confirm the accuracy figure on the live listing before you build a plan around ±0.5°F.",
            "Note what the reading is measuring: a thermometer is only as good as the spot you put it in.",
            "If you are cooking for hours, compare it against a leave-in probe before you rely on a single spot check.",
        ],
        "image": "assets/img/product-thermomaven.png",
        "image_caption": "Editorial illustration of an instant-read probe thermometer beside a sliced steak. Not a photograph of this product.",
    },
    "p5-chefiq": {
        "dek": "Three probes, a wireless hub and alerts — the only product in the shop that keeps cooking while you walk away.",
        "best_for": "A whole bird plus sides, with a notification when it is done",
        "catch": "It is the only thing here that needs a hub, a network and a phone to tell you anything. Without those it is three expensive sticks.",
        "check_before_buying": [
            "Confirm the probe count and the hub contents on the live listing — this model family is listed several ways (FLG-014).",
            "Plan where the hub sits so the signal actually reaches it, and check the app works before the holiday.",
            "Check how the probes are cleaned, and whether you would rather hand-wash three of them after every cook.",
        ],
        "image": "assets/img/product-chefiq.png",
        "image_caption": "Editorial illustration of a wireless thermometer base with probes running into a pan. Not a photograph of this product.",
    },
}


def main():
    with io.open(PATH, encoding="utf-8") as f:
        doc = json.load(f, object_pairs_hook=collections.OrderedDict)
    seen = set()
    for p in doc["products"]:
        pid = p["id"]
        if pid not in EDITORIAL:
            raise SystemExit("no editorial block for product id %r" % pid)
        seen.add(pid)
        e = EDITORIAL[pid]
        for k in ("dek", "best_for", "catch", "check_before_buying", "image", "image_caption"):
            if not e.get(k):
                raise SystemExit("product %s: editorial field %s is empty" % (pid, k))
        if not isinstance(e["check_before_buying"], list) or len(e["check_before_buying"]) < 2:
            raise SystemExit("product %s: check_before_buying needs at least two items" % pid)
        if not os.path.exists(os.path.join(ROOT, e["image"])):
            raise SystemExit("product %s: image %s does not exist" % (pid, e["image"]))
        # editorial fields sit next to, never on top of, the sourced spec fields
        for k, v in e.items():
            p[k] = v
        # the editorial reading is grounded on the same listing the specs came from
        p["editorial_source"] = p["source_url"]
        p["editorial_source_date"] = p["source_date"]
        p["editorial_note"] = ("Written by the desk from this listing and the register. It adds no price, "
                               "no rating, no test result and no spec that is not already recorded above.")
    missing = set(EDITORIAL) - seen
    if missing:
        raise SystemExit("editorial blocks for unknown products: %s" % sorted(missing))
    with io.open(PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("patched %d products with editorial voice fields" % len(seen))


if __name__ == "__main__":
    main()
