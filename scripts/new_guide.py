#!/usr/bin/env python3
"""Publishing cadence tool: scaffold a guide as a JSON file, then build.

    python3 scripts/new_guide.py "Title here" --category "Air Fryers" \
        --cluster "Air fryers" --season "Everyday" [--slug override]

A new guide = one file in data/guides/ + `python3 scripts/build_site.py`.
Sitemap, RSS, the search index, the front-page rail, the guides index and the
About page's cluster counts all derive from that file, so nothing else needs
editing. The compliance gate (scripts/check_site.py) still has to pass.
"""
import argparse, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "data", "guides")
CATEGORIES = ("Air Fryers", "Meat Thermometers")

BODY = """<p>Open with the thing the reader is actually unsure about. Two to three sentences, no throat-clearing, no “in today’s fast-paced world”.</p>
<h2>Compare the parts that decide it</h2>
<div class="tablewrap"><table><thead><tr><th>Question</th><th>Option A</th><th>Option B</th></tr></thead><tbody>
<tr><td>What changes day to day</td><td>State only what a source states</td><td>State only what a source states</td></tr>
</tbody></table></div>
<p class="src">Sources: <a href="https://www.amazon.com/dp/OBSERVED_ASIN" rel="nofollow noopener" target="_blank">listing</a> · <a href="https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart" rel="noopener" target="_blank">official guidance</a> · checked YYYY-MM-DD.</p>
<div class="notice"><strong>What this page cannot tell you.</strong> No price, rating or review count appears on this site, and nobody here has used the products, so no testing claim is made. Every figure is linked to the page it was read from.</div>
<h2>Shop this comparison</h2>
<div class="grid">CARDS</div>
"""

FAQ = [
    ["Question a reader would type into a search box?", "Answer it in the first sentence, then add the nuance. Keep it factual and sourced."],
]

def slugify(t):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")[:60]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("title")
    ap.add_argument("--category", default=CATEGORIES[0], help="Cluster used for product matching: %s" % " / ".join(CATEGORIES))
    ap.add_argument("--cluster", default="", help="Display label, e.g. 'Capacity'")
    ap.add_argument("--season", default="Everyday")
    ap.add_argument("--slug", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if a.category not in CATEGORIES:
        sys.exit("category must be one of: %s (drives which products appear in CARDS)" % ", ".join(CATEGORIES))
    slug = a.slug or slugify(a.title)
    if not slug:
        sys.exit("could not derive a slug from that title; pass --slug")
    path = os.path.join(DIR, slug + ".json")
    if os.path.exists(path) and not a.force:
        sys.exit("data/guides/%s.json already exists (pass --force to overwrite)" % slug)

    today = datetime.date.today().isoformat()
    rel = "guides/%s.html" % slug
    doc = {
        "slug": slug,
        "path": rel,
        "title": a.title,
        "desc": "Finish this: one or two sentences, the promise of the page. Used as the meta description, the RSS summary and the card text — so it has to stand alone.",
        "cluster": a.cluster or a.category,
        "category": a.category,
        "published": today,
        "updated": today,
        "season": a.season,
        "image": "assets/img/hero-counter.jpg",
        "image_caption": "Editorial illustration. Not a product photograph.",
        "body": BODY,
        "faq": FAQ,
        "_provenance": "Scaffolded by scripts/new_guide.py on %s. Fill every 'Finish this'/'State only what a source states' cell or delete it before publishing." % today,
    }
    os.makedirs(DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    print("created data/guides/%s.json -> %s" % (slug, rel))
    print("next:  1) fill the file (title, desc, table rows with sources, faq)")
    print("       2) python3 scripts/build_site.py")
    print("       3) python3 scripts/check_site.py     # must pass before you commit")
    print("REMINDER: no prices, no ratings, no 'we tested it'. Any number you publish needs a source link.")

if __name__ == "__main__":
    main()
