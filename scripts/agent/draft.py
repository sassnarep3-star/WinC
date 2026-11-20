#!/usr/bin/env python3
"""Step 2 — draft. Turn a research brief into a structured guide draft a person can edit.

Usage:
    python3 scripts/agent/draft.py --all
    python3 scripts/agent/draft.py --asin B0CDY277D3
    python3 scripts/agent/draft.py --title "Basket or oven-style? what should you compare?" \
        --category "Air Fryers" --question "Basket or oven-style air fryer: what should I compare?"

Writes data/drafts/<slug>.json. A draft is a STAGING AREA: it is not part of the published
site until a person moves it into data/guides/ and the build is re-run. This step will not
write a price, a rating, a review count, or a sentence claiming that anyone tested anything —
if a draft needs one of those, the gap is recorded in the draft instead.
"""
import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load, save, today, claim_problems, blank_mark  # noqa: E402

SPEC_ROWS = [("brand", "Brand"), ("model", "Model"), ("capacity", "Capacity"),
             ("dimensions", "Footprint"), ("weight", "Weight"),
             ("temperature", "Temperature / accuracy"), ("power", "Power"), ("upc", "UPC")]


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:70] or "draft"


def spec_table(brief):
    rows = []
    for key, label in SPEC_ROWS:
        s = brief["specs"].get(key, {})
        v = s.get("value") or ""
        note = s.get("note", "")
        if v:
            cell = v
        elif note == "does not apply to this product type":
            cell = "—"
        else:
            cell = '<span class="blank">— blank (unverified)</span>'
        rows.append("<tr><th>%s</th><td>%s</td></tr>" % (label, cell))
    return ('<div class="tablewrap"><table><thead><tr><th>Field</th>'
            '<th>Value (as listed on Amazon)</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>"
            + '<p class="src">Source: <a href="%s" rel="nofollow noopener" target="_blank">%s</a>'
              ' · read %s. Blank = not confirmed from an official source.</p>'
              % (brief["listing_url"], brief["listing_url"], brief["specs"].get("brand", {}).get("source_date", "")))


def build_body(brief, question):
    ed = brief["editorial"]
    asin = brief["asin"]
    src = ('<p class="src">Sources: <a href="%s" rel="nofollow noopener" target="_blank">%s</a>'
           ' · checked %s.</p>' % (brief["listing_url"], asin, brief.get("generated", "")))
    parts = []
    parts.append("<p>%s</p>" % (ed.get("dek") or brief["title_as_listed"]))
    if ed.get("best_for"):
        parts.append("<p><strong>Best for:</strong> %s</p>" % ed["best_for"])
    parts.append("<h2>What the listing says</h2>")
    parts.append(spec_table(brief))
    if ed.get("catch"):
        parts.append("<h2>The catch</h2><p>%s</p>" % ed["catch"])
    checks = ed.get("check_before_buying") or []
    if checks:
        parts.append("<h2>Before you buy, check these three things</h2><ul class=\"checklist\">")
        for c in checks:
            parts.append("<li>%s</li>" % c)
        parts.append("</ul>")
    if brief.get("open_flags"):
        parts.append("<h2>What the listing gets wrong, or leaves out</h2><ul class=\"notes\">")
        for f in brief["open_flags"]:
            parts.append("<li><strong>%s:</strong> %s</li>" % (f["id"], f.get("issue", "")))
        parts.append("</ul>")
    if brief.get("faq"):
        parts.append("<h2>Frequently asked questions</h2><div class=\"faq\">")
        for qa in brief["faq"]:
            parts.append("<details><summary>%s</summary><p>%s</p></details>" % (qa[0], qa[1]))
        parts.append("</div>")
    parts.append(src)
    return "\n".join(parts)


def build_draft(brief, title, category, question):
    body = build_body(brief, question)
    problems = claim_problems(body + " " + title + " " + (question or ""))
    if problems:
        # A draft that would trip the site gate is a defect, not a draft. Refuse and say why.
        return None, problems
    slug = slugify(title)
    return {
        "slug": slug,
        "path": "guides/%s.html" % slug,
        "title": title,
        "desc": (brief["editorial"].get("dek") or brief["title_as_listed"])[:180],
        "cluster": category,
        "category": category,
        "published": today(),
        "updated": today(),
        "season": "Everyday",
        "image": "",
        "image_caption": "",
        "body": body,
        "faq": brief.get("faq", []),
        "_status": "draft — needs a desk edit before it can be published",
        "_generated_by": "scripts/agent/draft.py",
        "_source_asin": brief["asin"],
        "_sourced_from": brief["listing_url"],
        "_question": question or "",
        "_gaps": {
            "price": brief.get("price_live_note", ""),
            "rating": brief.get("rating_live_note", ""),
            "unconfirmed_specs": brief.get("unknown_specs", []),
            "blocking_questions": [q["id"] for q in brief.get("blocking_questions", [])],
        },
        "_move_to": "data/guides/%s.json" % slug,
    }, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--asin")
    ap.add_argument("--title")
    ap.add_argument("--category", default="Air Fryers")
    ap.add_argument("--question")
    args = ap.parse_args()

    briefs = []
    rdir = os.path.join(ROOT, "data", "research")
    if not os.path.isdir(rdir):
        print("no research briefs found — run scripts/agent/research.py first")
        return 1
    for fn in sorted(os.listdir(rdir)):
        if fn.endswith(".json"):
            briefs.append(load("data/research/" + fn))
    if args.asin:
        briefs = [b for b in briefs if b["asin"] == args.asin]
    if not briefs:
        print("no brief matched")
        return 1

    written = 0
    for b in briefs:
        title = args.title or ("%s: what the listing actually says" % b["editorial"].get("dek", b["asin"])[:60])
        question = args.question or ("What should I compare about %s?" % b["editorial"].get("dek", b["asin"])[:60])
        draft, problems = build_draft(b, title, args.category, question)
        if draft is None:
            print("REFUSED to draft %s — %s" % (b["asin"], "; ".join(sorted(set(problems)))))
            continue
        rel = "data/drafts/%s.json" % draft["slug"]
        save(rel, draft)
        written += 1
        print("wrote %s (from %s)" % (rel, b["asin"]))
    print("%d draft(s) written to data/drafts/. A draft is not published until a person moves it "
          "into data/guides/ and the build is re-run." % written)
    return 0


if __name__ == "__main__":
    sys.exit(main())
