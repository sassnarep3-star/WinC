#!/usr/bin/env python3
"""Assign one editorial illustration per guide (session arena/6561e2ea-winc).

Every guide gets its own picture instead of borrowing the category plate, because a front-page
rail where six cards share one image reads as generated. A guide is only assigned an image that
actually exists on disk; anything else is left alone so the builder keeps its category fallback.
Re-run this after new artwork lands.
"""
import json, glob, os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE_DIR = os.path.join(ROOT, "data", "guides")

# slug -> (image path, caption)
ASSIGN = {
    "basket-or-oven-style-air-fryer": (
        "assets/img/guide-basket-or-oven.png",
        "Editorial illustration of two air fryer baskets beside a countertop oven. Not a product photograph."),
    "instant-read-or-leave-in": (
        "assets/img/guide-thermometer-types.png",
        "Editorial illustration of an instant-read thermometer and a leave-in probe. Not a product photograph."),
    "air-fryer-capacity-checklist": (
        "assets/img/guide-capacity.png",
        "Editorial illustration of three air fryer baskets with a measuring tape. Not a product photograph."),
    "holiday-crowd-thermometer-questions": (
        "assets/img/guide-holiday.png",
        "Editorial illustration of a roast bird in an oven with a probe in it. Not a product photograph."),
    "cleanup-and-counter-space": (
        "assets/img/guide-cleanup.png",
        "Editorial illustration of air fryer parts on a counter with a measuring tape. Not a product photograph."),
    "multi-function-appliance-questions": (
        "assets/img/guide-multifunction.png",
        "Editorial illustration of a countertop oven with racks and accessories laid out. Not a product photograph."),
    "reheat-leftovers-air-fryer": (
        "assets/img/guide-reheat.png",
        "Editorial illustration of reheated leftovers beside an air fryer basket. Not a product photograph."),
    "read-an-air-fryer-listing": (
        "assets/img/guide-listing.png",
        "Editorial illustration of a laptop next to an air fryer and a notepad. Not a product photograph."),
}


def main():
    changed = []
    for fn in sorted(glob.glob(os.path.join(GUIDE_DIR, "*.json"))):
        if os.path.basename(fn).startswith("_"):
            continue
        with io.open(fn, encoding="utf-8") as f:
            g = json.load(f)
        slug = g.get("slug") or os.path.splitext(os.path.basename(fn))[0]
        if slug not in ASSIGN:
            continue
        img, cap = ASSIGN[slug]
        if not os.path.exists(os.path.join(ROOT, img)):
            print("skip (artwork not on disk yet): %s -> %s" % (slug, img))
            continue
        if g.get("image") == img and g.get("image_caption") == cap:
            continue
        g["image"] = img
        g["image_caption"] = cap
        with io.open(fn, "w", encoding="utf-8") as f:
            json.dump(g, f, indent=2, ensure_ascii=False)
            f.write("\n")
        changed.append(slug)
    print("guide artwork assigned: %s" % (", ".join(changed) if changed else "(no change)"))


if __name__ == "__main__":
    main()
