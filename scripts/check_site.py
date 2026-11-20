#!/usr/bin/env python3
"""Compliance + integrity gate for ShopNow Kitchen. Exit 1 on violation.
Run: python3 scripts/check_site.py
Checks: disclosure strip on every page, sponsored links, no prices, sitemap coverage,
internal links resolve, product data sanity (9-char tokens, 10-char ASINs, blank intended).
"""
import os, re, json, sys, html as _html, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sassnarep3-star.github.io/WinC/"
TAG = "shopnow047c-20"
errors = []

def fail(msg):
    errors.append(msg)

def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()

# --- data sanity ---
products = json.load(open(os.path.join(ROOT, "data/products.json"), encoding="utf-8"))["products"]
for p in products:
    if len(p["submitted_token"]) != 9:
        fail(f"{p['id']}: submitted token must be 9 chars, got {p['submitted_token']}")
    if len(p["observed_asin"]) != 10:
        fail(f"{p['id']}: observed ASIN must be 10 chars, got {p['observed_asin']}")
    if p["intended_asin"]:
        fail(f"{p['id']}: intended_asin must stay blank until confirmed (do not merge fields)")
    if p["price"]:
        fail(f"{p['id']}: price must stay blank (Program Policies)")
    if p["rating"]:
        fail(f"{p['id']}: rating must stay blank (unverified)")

# --- collect html pages ---
html_files = []
for dirpath, _, files in os.walk(ROOT):
    # skip .git, node_modules, analytics (code, not pages)
    rel = os.path.relpath(dirpath, ROOT)
    if rel.startswith(".git") or rel.startswith("analytics") or rel.startswith("scripts") or rel.startswith("data") or rel.startswith("archive"):
        continue
    for fn in files:
        if fn.endswith(".html"):
            html_files.append(os.path.relpath(os.path.join(dirpath, fn), ROOT))

if not html_files:
    fail("no html pages found — run scripts/build_site.py first")

PRICE_RE = re.compile(r"\$\s?\d|\bUSD\s?\d|€\s?\d|£\s?\d", re.I)

for hf in html_files:
    content = read(hf)
    # disclosure strip above the fold (must appear before </header> or early in body)
    if "As an Amazon Associate I earn from qualifying purchases." not in content:
        fail(f"{hf}: missing Associates disclosure statement")
    # disclosure strip div present
    if "disclosure-strip" not in content:
        fail(f"{hf}: missing disclosure strip")
    # Distinguish buy buttons (data-event=outbound_click) from evidence citations.
    # Buy buttons MUST be sponsored + tagged. Evidence links must NOT carry the tag
    # (they are citations, not paid placements) and must carry nofollow.
    for m in re.finditer(r'<a[^>]+href="(https://www\.amazon\.com/dp/[^"]+)"[^>]*>', content):
        tag = m.group(0)
        href = m.group(1)
        if 'data-event="outbound_click"' in tag:
            if 'rel="sponsored' not in tag:
                fail(f"{hf}: buy button missing rel=sponsored: {href[:80]}")
            if f"tag={TAG}" not in href:
                fail(f"{hf}: buy button missing tag {TAG}: {href[:80]}")
        else:
            # evidence citation link
            if f"tag={TAG}" in href:
                fail(f"{hf}: evidence link must not carry affiliate tag: {href[:80]}")
            if 'rel="nofollow' not in tag:
                fail(f"{hf}: evidence link missing rel=nofollow: {href[:80]}")
    # sponsored label near product links (at least one per page that has product links)
    if "amazon.com/dp/" in content and "Sponsored" not in content:
        fail(f"{hf}: has product links but no Sponsored label")
    # no prices rendered (allow $ in code samples? none expected)
    # strip script/style then check
    text = re.sub(r"<script.*?</script>", "", content, flags=re.S)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    if PRICE_RE.search(text):
        fail(f"{hf}: price-like text rendered (must stay blank per policy)")
    # no link.amazon reader buttons (short links only in verification provenance)
    for m in re.finditer(r'<a[^>]+href="https://link\.amazon/[^"]+"', content):
        fail(f"{hf}: link.amazon used as reader link (provenance only): {m.group(0)[:100]}")
    # internal links resolve (skip JS template fragments)
    for m in re.finditer(r'href="([^"]+)"', content):
        href = m.group(1)
        if href.startswith(("http", "mailto:", "#", "data:", "'", '"', "+", "{")):
            continue
        if "+" in href or "{" in href:
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        # resolve relative to page dir
        base = os.path.dirname(hf)
        resolved = os.path.normpath(os.path.join(base, target)) if base else target
        if not os.path.exists(os.path.join(ROOT, resolved)):
            fail(f"{hf}: broken internal link -> {href} (resolved {resolved})")

# --- sitemap coverage ---
sm = read("sitemap.xml")
tree = ET.fromstring(sm)
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [e.text for e in tree.findall("s:url/s:loc", ns)]
for hf in html_files:
    if hf == "404.html":
        continue
    if SITE + hf not in locs:
        fail(f"sitemap.xml missing {hf}")
for loc in locs:
    if not loc.startswith(SITE):
        fail(f"sitemap loc outside site: {loc}")

# --- feed ---
feed = read("feed.xml")
if "<rss" not in feed:
    fail("feed.xml is not RSS")

# --- robots ---
robots = read("robots.txt")
if "Sitemap:" not in robots:
    fail("robots.txt missing Sitemap")

# --- extra gate (session arena-23d7ed19): drift that used to need a human reviewer ---
GUIDE_DIR = os.path.join(ROOT, "data", "guides")
guide_files = []
if os.path.isdir(GUIDE_DIR):
    guide_files = [fn for fn in sorted(os.listdir(GUIDE_DIR))
                   if fn.endswith(".json") and not fn.startswith("_")]
if not guide_files:
    fail("data/guides/ has no guide files (files starting with _ are templates)")

CATS = ("Air Fryers", "Meat Thermometers")
def _count_products(cat):
    return sum(1 for x in products if x["category"] == cat)
def _guide_docs():
    out = []
    for fn in guide_files:
        with open(os.path.join(GUIDE_DIR, fn), encoding="utf-8") as f:
            out.append(json.load(f))
    return out
guides = _guide_docs()
for g in guides:
    slug = os.path.splitext(g["_file"] if "_file" in g else fn)[0] if False else None
    name = g.get("slug") or (g.get("path", "").split("/")[-1].replace(".html", ""))
    gp = g.get("path", "")
    if not gp:
        fail(f"guide {name}: missing path"); continue
    if not os.path.exists(os.path.join(ROOT, gp)):
        fail(f"guide {name}: built page missing ({gp}) — run scripts/build_site.py")
    if SITE + gp not in locs:
        fail(f"guide {name}: {gp} not in sitemap.xml (cadence must not need hand-edits)")
    for field in ("title", "desc", "cluster", "category", "published", "body", "faq"):
        if not g.get(field):
            fail(f"guide {name}: field '{field}' is empty")
    body = g.get("body", "")
    if "CARDS" in body and "grid" not in body:
        fail(f"guide {name}: CARDS token used without a .grid wrapper")
    if not re.search(r'(amazon\.com|\.gov|associates|Operating Agreement)', body):
        fail(f"guide {name}: no source anchor in body — every published figure needs one")
    if g.get("category") not in CATS:
        fail(f"guide {name}: category '{g.get('category')}' is not a shop category, so CARDS falls back to all products")
    if g.get("image") and not os.path.exists(os.path.join(ROOT, g["image"])):
        fail(f"guide {name}: image {g['image']} does not exist")

# expected product counts per category: a category with zero guides is a dead end
for cat in CATS:
    if _count_products(cat) and not any(x.get("category") == cat for x in guides):
        fail(f"category {cat} has products but no guide — orphaned cluster")

# every referenced local asset must exist
for hf in html_files:
    content = read(hf)
    base = os.path.dirname(hf)
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', content):
        src = m.group(1)
        if src.startswith(("http", "data:", "mailto:")):
            continue
        rel = os.path.normpath(os.path.join(base, src)) if base else src
        if not os.path.exists(os.path.join(ROOT, rel)):
            fail(f"{hf}: missing image -> {src}")
    for m in re.finditer(r'<meta property="og:image" content="([^"]+)"', content):
        u = m.group(1)
        if not u.startswith(SITE):
            fail(f"{hf}: og:image not on this site: {u}")
        elif not os.path.exists(os.path.join(ROOT, u[len(SITE):])):
            fail(f"{hf}: og:image file missing: {u}")

# claims the repo has no evidence for. Affirmative-claim patterns only:
# negations ("no hands-on testing was performed") are the correct copy and stay allowed.
BANNED = [
    (r"\bwe tested\b", "claims testing that has not happened"),
    (r"\bour\s+(test\s+)?lab\b", "claims a test facility"),
    (r"\bwe tried\b", "claims personal use"),
    (r"\bbest overall\b", "ranking without a stated method"),
    (r"\beditor'?s choice\b", "award language without a process"),
    (r"\bdouble opt-in\b", "promises a consent flow no code implements"),
    (r"\bgame[- ]?changer\b", "AI-slop register"),
    (r"\bdelve\b", "AI-slop register"),
    (r"\belevate your\b", "AI-slop register"),
    (r"\bin today.s (fast|world)\b", "AI-slop register"),
    (r"\bin conclusion\b", "essay filler"),
    (r"\btrust us\b", "asks for trust instead of showing sources"),
    (r"\bonly \d+ left\b", "false scarcity"),
    (r"\b(hottest|must-have|must have|blow[sd]? your mind)\b", "hype without a source"),
]
NEGATORS = ("no ", "not ", "never ", "without ", "avoid ", "refuse", "cannot", "can't",
            "don't", "do not ", "won't", "zero ", "neither", "claims nothing", "only")
def scan_text(hf):
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", read(hf))
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = _html.unescape(t)
    # drop quoted mentions: this site quotes bad copy in order to say it does not use it
    q = "".join(chr(c) for c in (0x201C, 0x201D, 0x2018, 0x2019, 34, 39, 96))
    t = re.sub("[" + q + "][^" + q + "]{1,90}[" + q + "]", " ", t)
    return t
for hf in html_files:
    text = scan_text(hf)
    for pat, why in BANNED:
        for m in re.finditer(pat, text, re.I):
            pre = text[max(0, m.start() - 60):m.start()].lower()
            pre = pre[pre.rfind(".") + 1:]
            if any(n in pre for n in NEGATORS):
                continue  # negated mention, e.g. "no hands-on testing"
            fail(f"{hf}: banned phrase {m.group(0)!r} — {why}")

# typed counts drift; computed counts do not. About page must match the data.
parts = "; ".join(f"{c} ({_count_products(c)} products, {sum(1 for x in guides if x.get('category')==c)} guides)" for c in CATS)
about = read("about.html")
if parts not in about:
    fail(f"about.html cluster counts do not match data (expected substring: {parts!r}) — compute them in build_site.py, do not type them")

# nav labels must resolve to index pages, not to a single leaf
idx = read("index.html")
for label, target in (("Guides", "guides/index.html"), ("The shop", "products/index.html")):
    if f'href="{target}"' not in idx:
        fail(f"navigation: '{label}' does not point at {target}")
    if not os.path.exists(os.path.join(ROOT, target)):
        fail(f"navigation target missing: {target}")

# process file the brief requires
if not os.path.exists(os.path.join(ROOT, "COORDINATION.md")):
    fail("COORDINATION.md missing — shared task board is required by the working agreement")


if errors:
    print(f"FAIL ({len(errors)} violations):")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: {len(html_files)} pages checked, {len(locs)} sitemap URLs, no violations.")
