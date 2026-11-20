#!/usr/bin/env python3
"""Compliance + integrity gate for ShopNow Kitchen. Exit 1 on violation.
Run: python3 scripts/check_site.py
Checks: disclosure strip on every page, sponsored links, no prices, sitemap coverage,
internal links resolve, product data sanity (9-char tokens, 10-char ASINs, blank intended).
"""
import os, re, json, sys, xml.etree.ElementTree as ET

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

if errors:
    print(f"FAIL ({len(errors)} violations):")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: {len(html_files)} pages checked, {len(locs)} sitemap URLs, no violations.")
