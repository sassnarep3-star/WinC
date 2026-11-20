#!/usr/bin/env python3
"""Compliance + integrity gate for ShopNow Kitchen. Exit 1 on violation.
Run: python3 scripts/check_site.py
Checks: disclosure strip on every page, sponsored links, no prices, sitemap coverage,
internal links resolve, product data sanity (9-char tokens, 10-char ASINs, blank intended).
"""
import os, re, json, sys, html as _html, xml.etree.ElementTree as ET
from urllib.parse import urlparse

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
PROBES = json.load(open(os.path.join(ROOT, "data/probes.json"), encoding="utf-8"))
FLAGS = json.load(open(os.path.join(ROOT, "data/flags.json"), encoding="utf-8"))["flags"]
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
    intended_asin = p.get("intended_asin", "")
    intended_listing = urlparse(p.get("intended_listing_url", ""))
    intent_complete = (all(p.get(k) for k in (
        "intended_asin", "intended_listing_url", "confirmation_date", "intended_source"))
        and len(intended_asin) == 10
        and intended_asin == p.get("observed_asin")
        and intended_listing.scheme == "https"
        and intended_listing.hostname in ("amazon.com", "www.amazon.com")
        and f"/dp/{intended_asin}" in intended_listing.path)
    test = p.get("associates_link_test", {})
    if not isinstance(test, dict):
        fail(f"{p['id']}: associates_link_test must be a separate record")
        test = {}
    test_url = test.get("special_link_url", "")
    test_complete = (test.get("destination_confirmed") is True
                     and test.get("tracking_report_confirmed") is True
                     and all(test.get(k) for k in (
                         "confirmation_date", "source", "report_reference"))
                     and test_url.startswith("https://"))
    p["_purchase_link_ready"] = bool(intent_complete and test_complete)

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
outbound_seen = set()

# Anchor index: deep links into the flag and source tables are how a reader jumps to a row.
page_ids = {}
for hf in html_files:
    page_ids[hf] = set(re.findall(r'id=["\']([^"\']+)["\']', read(hf)))

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
    # Every live purchase link must match both the confirmed product intent and the exact
    # Special Link that was tested in Associates Central. An observed redirect alone never unlocks it.
    for m in re.finditer(r'<a\b[^>]*data-event="outbound_click"[^>]*>', content):
        tag = m.group(0)
        href_m = re.search(r'href="([^"]+)"', tag)
        asin_m = re.search(r'data-asin="([^"]+)"', tag)
        if 'rel="sponsored' not in tag:
            fail(f"{hf}: outbound purchase link missing rel=sponsored")
        if not href_m or not asin_m:
            fail(f"{hf}: outbound purchase link missing href or intended ASIN")
            continue
        href, asin = _html.unescape(href_m.group(1)), _html.unescape(asin_m.group(1))
        matches = [p for p in products if p.get("_purchase_link_ready")
                   and p.get("intended_asin") == asin
                   and p.get("associates_link_test", {}).get("special_link_url") == href]
        if not matches:
            fail(f"{hf}: outbound link is not backed by a completed intent + Associates test ({asin})")
        else:
            outbound_seen.add(asin)
    # A tagged Amazon URL that is not the tested buy button must not leak into reader copy.
    for m in re.finditer(r'<a\b[^>]*href="([^"]*tag=[^"]*)"[^>]*>', content):
        if 'data-event="outbound_click"' not in m.group(0):
            fail(f"{hf}: affiliate-tagged URL is not a marked outbound purchase link")
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
    # fragment anchors must resolve too (a dead #FLG-00x deep link is a broken reference)
    for m in re.finditer(r'href="([^"]*#[^"]+)"', content):
        href = _html.unescape(m.group(1))
        if href.startswith(("http", "mailto:", "data:")):
            continue
        tgt, _, frag = href.partition("#")
        if not frag:
            continue
        base = os.path.dirname(hf)
        target = os.path.normpath(os.path.join(base, tgt)) if tgt else hf
        if target not in page_ids:
            continue
        if frag not in page_ids[target]:
            fail(f"{hf}: broken in-page anchor -> {href}")

# A completed test should produce a live button; incomplete tests must never do so.
for p in products:
    if p.get("_purchase_link_ready") and p["intended_asin"] not in outbound_seen:
        fail(f"{p['id']}: link record is marked complete but no matching sponsored button was rendered")

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


# --- register schema (session arena-82d39deb) -------------------------------
# The registers the pages are built from are checked as data, not only as HTML.
# A missing key or an invented status used to pass silently.
SUG_STATUSES = {"recommended-now", "open", "open-blocked", "shipped", "done-this-session"}
sug_doc = json.load(open(os.path.join(ROOT, "data/suggestions.json"), encoding="utf-8"))
suggestions = sug_doc["suggestions"]
seen = set()
for s in suggestions:
    sid = s.get("id", "<no id>")
    if sid in seen:
        fail(f"suggestions.json: duplicate id {sid}")
    seen.add(sid)
    for field in ("id", "title", "status", "area", "problem", "proposal", "risk",
                  "expected_effect", "evidence", "feeds_prompt", "effort", "cost"):
        if not s.get(field):
            fail(f"suggestion {sid}: field '{field}' is empty")
    if s.get("status") not in SUG_STATUSES:
        fail(f"suggestion {sid}: status {s.get('status')!r} is not one of {sorted(SUG_STATUSES)}")
    if s.get("effort") not in ("S", "M", "L"):
        fail(f"suggestion {sid}: effort {s.get('effort')!r} must be S, M or L")

q_doc = json.load(open(os.path.join(ROOT, "data/questions.json"), encoding="utf-8"))
seen_q = set()
for q in q_doc["questions"]:
    qid = q.get("id", "<no id>")
    if qid in seen_q:
        fail(f"questions.json: duplicate id {qid}")
    seen_q.add(qid)
    for field in ("id", "question", "decision_it_gates", "have", "missing", "discovery", "owner"):
        if not q.get(field):
            fail(f"question {qid}: field '{field}' is empty")
    if "answer" not in q:
        fail(f"question {qid}: 'answer' key missing (use an empty string, never omit it)")
    if not str(q.get("blocking", "")).startswith(("yes", "no")):
        fail(f"question {qid}: blocking must start with 'yes' or 'no'")

FLAG_IDS = {f["id"] for f in FLAGS}
for p in products:
    for note in p.get("listing_notes", []) or []:
        if note.get("flag") not in FLAG_IDS:
            fail(f"{p['id']}: listing_note cites unknown flag {note.get('flag')!r}")
        if not note.get("note"):
            fail(f"{p['id']}: listing_note without text")
    faq = p.get("faq") or []
    if len(faq) < 2:
        fail(f"{p['id']}: needs at least 2 FAQ pairs (a product page with no reader questions is not a decision shortcut)")
    for qa in faq:
        if not isinstance(qa, list) or len(qa) != 2 or not qa[0] or not qa[1]:
            fail(f"{p['id']}: malformed FAQ pair {qa!r}")

cat_doc = json.load(open(os.path.join(ROOT, "data/categories.json"), encoding="utf-8"))
PRODUCT_FIELDS = {"capacity", "dimensions", "weight", "temperature", "power", "model",
                   "title", "brand", "upc", "listing_claims", "observed_asin"}
LISTING_URLS = {p["source_url"] for p in products}
for c in cat_doc["categories"]:
    if c["category"] not in CATS:
        fail(f"categories.json: {c['category']!r} is not a shop category")
    profs = c.get("profiles") or []
    if len(profs) < 2:
        fail(f"categories.json: category {c['category']} has {len(profs)} profiles (need at least 2)")
    for pr in profs:
        for field in ("situation", "deciding_spec", "what_the_listings_say", "answer", "source"):
            if not pr.get(field):
                fail(f"categories.json: {c['category']} profile {pr.get('situation')!r}: '{field}' is empty")
        if pr.get("deciding_spec") not in PRODUCT_FIELDS:
            fail(f"categories.json: {c['category']} profile {pr.get('situation')!r} names deciding spec "
                 f"{pr.get('deciding_spec')!r}, which is not a field in data/products.json")
        if not str(pr.get("source", "")).startswith("https://"):
            fail(f"categories.json: {c['category']} profile {pr.get('situation')!r} has no https source link")
        if not any(p["observed_asin"] in pr.get("source", "") for p in products):
            fail(f"categories.json: {c['category']} profile {pr.get('situation')!r} cites a source that is not one of "
                 f"the recorded listings: {pr.get('source')}")

topic_doc = json.load(open(os.path.join(ROOT, "data/topics.json"), encoding="utf-8"))
seen_t = set()
for t in topic_doc["topics"]:
    tid = t.get("id", "<no id>")
    if tid in seen_t:
        fail(f"topics.json: duplicate id {tid}")
    seen_t.add(tid)
    for field in ("id", "title", "cluster", "question", "why", "needs", "status", "chosen_from"):
        if not t.get(field):
            fail(f"topic {tid}: field '{field}' is empty")
    if t.get("status") not in ("planned", "blocked", "published"):
        fail(f"topic {tid}: status {t.get('status')!r} must be planned, blocked or published")
    allowed_clusters = set(CATS) | {g.get("cluster", "") for g in guides} | {"Cross-cluster"}
    if t.get("cluster") not in allowed_clusters:
        fail(f"topic {tid}: cluster {t.get('cluster')!r} is not a shop category, a published cluster, or 'Cross-cluster'")
    # a topic may only claim measured demand if it says where the measurement came from
    cf = str(t.get("chosen_from", "")).lower()
    if not any(m in cf for m in ("hypothesis", "measured quer", "verification", "search console")):
        fail(f"topic {tid}: 'chosen_from' must state its provenance (an editorial hypothesis, a measured query, "
             f"or a verification finding) — got {t.get('chosen_from')!r}")

# probes and products must not drift apart
probe_tokens = {pr["submitted_token"] for pr in PROBES["probes"]}
probe_asins = {pr["final_asin"] for pr in PROBES["probes"]}
for p in products:
    if p["submitted_token"] not in probe_tokens:
        fail(f"{p['id']}: submitted token {p['submitted_token']} has no redirect observation in data/probes.json")
    if p["observed_asin"] not in probe_asins:
        fail(f"{p['id']}: observed_asin {p['observed_asin']} does not appear in the redirect log")
for pr in PROBES["probes"]:
    if pr["final_asin"] not in {p["observed_asin"] for p in products}:
        fail(f"probes: {pr['submitted_token']} resolves to {pr['final_asin']}, which is not a recorded product")

# guides: FAQ depth and a source anchor per published page
for g in guides:
    if len(g.get("faq") or []) < 3:
        fail(f"guide {g.get('slug')}: fewer than 3 FAQ entries")

# reader-path regression guard: the front page must stay a shop, not a status report
idx_text = scan_text("index.html") if os.path.exists(os.path.join(ROOT, "index.html")) else ""
for phrase in ("why the numbers here are boring", "records a count inside your own browser",
               "items we could not confirm, published on"):
    if phrase in idx_text.lower():
        fail(f"index.html: front page carries process furniture ({phrase!r}) — the reader path must lead with products")
if "the shop" not in idx_text.lower():
    fail("index.html: front page no longer shows the shop")


# --- every register row must carry an official source link (or say why not) ---
REGISTER_PAGES = ["questions.html", "topics.html", "flagged-for-review.html", "products/index.html"]
for hf in REGISTER_PAGES:
    if not os.path.exists(os.path.join(ROOT, hf)):
        fail(f"{hf}: register page missing")
        continue
    content = read(hf)
    for m in re.finditer(r"(?s)<tr[^>]*>(.*?)</tr>", content):
        row = m.group(1)
        if "<td" not in row:
            continue  # header row
        has_source = ('href="https://' in row) or ('href="verification.html#src-' in row)
        if not has_source and "Internal only" not in row:
            fail(f"{hf}: a table row carries no official source link and no 'internal only' note")
    # and the page must point at the source register
    if 'href="https://' not in content and 'href="verification.html#src-' not in content:
        fail(f"{hf}: register page links to no source at all")


if errors:
    print(f"FAIL ({len(errors)} violations):")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: {len(html_files)} pages checked, {len(locs)} sitemap URLs, no violations.")
