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
    # The one-link Associates test record must be a complete record or an empty one.
    # A half-filled record is the dangerous case: it looks like a test happened.
    test = p.get("associates_link_test")
    if test is None:
        fail(f"{p['id']}: associates_link_test record is missing — add it, empty if untested")
    elif not isinstance(test, dict):
        fail(f"{p['id']}: associates_link_test must be an object")
    else:
        confirmed = (test.get("destination_confirmed") is True
                     and test.get("tracking_report_confirmed") is True)
        if confirmed:
            for field in ("special_link_url", "confirmation_date", "source", "report_reference"):
                if not test.get(field):
                    fail(f"{p['id']}: the one-link test is marked confirmed but '{field}' is empty")
            url = str(test.get("special_link_url"))
            if not url.startswith("https://"):
                fail(f"{p['id']}: the tested Special Link must be an https URL")
            if "amazon.com" not in url:
                fail(f"{p['id']}: the tested Special Link must point at an amazon.com page")
            if TAG not in url:
                fail(f"{p['id']}: the tested Special Link must carry the tracking ID {TAG}")
        else:
            # nothing may be claimed as confirmed while the record is empty
            for field in ("confirmation_date", "source", "report_reference"):
                if test.get(field):
                    fail(f"{p['id']}: the one-link test is not confirmed but '{field}' is filled in")

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
    # A buy button must declare its link state, and the declared state must match the
    # product's one-link test record. A button that calls itself verified without a
    # completed test is a claim the register cannot back.
    for m in re.finditer(r'<a\b[^>]*data-event="outbound_click"[^>]*>', content):
        tag = m.group(0)
        asin_m = re.search(r'data-asin="([^"]+)"', tag)
        state_m = re.search(r'data-link-state="([^"]+)"', tag)
        if not state_m:
            fail(f"{hf}: a buy button has no data-link-state — it must say whether the "
                 f"one-link Associates test has been completed")
            continue
        state = state_m.group(1)
        if state not in ("verified", "pending-verification"):
            fail(f"{hf}: data-link-state {state!r} is not a known state")
            continue
        if not asin_m:
            continue
        asin = asin_m.group(1)
        owner = next((p for p in products if p["observed_asin"] == asin), None)
        if owner is None:
            fail(f"{hf}: buy button points at ASIN {asin}, which is not in the register")
            continue
        expected = "verified" if (owner.get("associates_link_test") or {}).get("destination_confirmed") is True \
            and (owner.get("associates_link_test") or {}).get("tracking_report_confirmed") is True \
            else "pending-verification"
        if state != expected:
            fail(f"{hf}: buy button for {asin} declares data-link-state={state!r} but its "
                 f"one-link test record makes it {expected!r}")
        if state == "verified":
            url_m = re.search(r'href="([^"]+)"', tag)
            tested = (owner.get("associates_link_test") or {}).get("special_link_url")
            if url_m and tested and url_m.group(1) != tested:
                fail(f"{hf}: verified buy button for {asin} does not point at the tested Special Link")
    # no prices rendered (allow $ in code samples? none expected)
    # strip script/style then check
    text = re.sub(r"<script.*?</script>", "", content, flags=re.S)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    if PRICE_RE.search(text):
        fail(f"{hf}: price-like text rendered (must stay blank per policy)")
    # link.amazon short links are provenance, never reader links. A citation of the
    # submitted URL inside the source register is legitimate and carries rel="nofollow";
    # anything presented as a clickable destination is a violation.
    for m in re.finditer(r'<a[^>]+href="https://link\.amazon/[^"]+"[^>]*>', content):
        if 'rel="nofollow' not in m.group(0):
            fail(f"{hf}: link.amazon used as a reader link (provenance only): {m.group(0)[:100]}")
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
    # a <picture><source srcset> pointing at a missing file is a silent broken image
    for m in re.finditer(r'<source[^>]+srcset="([^"]+)"', content):
        src = m.group(1)
        if src.startswith(("http", "data:")):
            continue
        rel = os.path.normpath(os.path.join(base, src)) if base else src
        if not os.path.exists(os.path.join(ROOT, rel)):
            fail(f"{hf}: missing <source> image -> {src}")
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
ANSWER_STATES = {"answered", "partly", "open"}
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

SRC_IDS = {x["id"] for x in json.load(open(os.path.join(ROOT, "data/sources.json"), encoding="utf-8"))["sources"]}
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
    # An answer must be traceable. Either it names the sources it rests on, or it says
    # explicitly that it rests on this repository's own records. An answer with neither is
    # a claim, and the whole point of the register is that it is not one.
    state = q.get("answer_state")
    if state not in ANSWER_STATES:
        fail(f"question {qid}: answer_state must be one of {sorted(ANSWER_STATES)}, got {state!r}")
    ans = str(q.get("answer") or "").strip()
    if state == "open" and ans:
        fail(f"question {qid}: answer_state 'open' must have an empty answer cell")
    if state and state != "open":
        if not ans:
            fail(f"question {qid}: answer_state {state!r} but the answer is empty")
        if not q.get("answered_on"):
            fail(f"question {qid}: an answered row needs the date it was answered")
        froms = q.get("answered_from")
        if not isinstance(froms, list):
            fail(f"question {qid}: answered_from must be a list (may be empty only with a note)")
        else:
            for sid in froms:
                if sid not in SRC_IDS:
                    fail(f"question {qid}: answered_from cites unknown source {sid!r}")
            if not froms and not q.get("answered_from_note"):
                fail(f"question {qid}: an answered row needs either a cited source or an "
                     f"answered_from_note saying it rests on this repository's own records")

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

# A redirect observation that disagrees with the recorded mapping must be recorded, not hidden.
# The observed_* fields in products.json rest on the observations that agreed; a later session
# that saw a different destination has to say so in probes.json, and the flag register has to
# carry it. A silent divergence would leave the register describing a link that no longer
# behaves the way the page says it does.
for pr in PROBES["probes"]:
    for obs_key, obs in pr.items():
        if not (obs_key.endswith("_observation") and isinstance(obs, dict)):
            continue
        if "matches_prior_observations" not in obs:
            continue
        if obs["matches_prior_observations"]:
            continue
        token = pr["submitted_token"]
        # a disagreement must be visible in the flag register, not only in the probe log
        flagged = any(token in json.dumps(f, ensure_ascii=False)
                      for f in FLAGS)
        if not flagged:
            fail(f"probes: {token} has a disagreeing {obs_key} but no flag mentions it — "
                 f"record the divergence on the Flagged for review page")

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


# --- every table row on every page must carry a source (the brief's hard rule) ---
# A row passes if it links to an official source (https), cites the source register
# (verification.html#src-), or explicitly says the source is internal and links the
# internal file it came from. A row that is blank must say so and point at the
# register where the gap is published. Nothing may simply have no source.
ROW_OK_LINK = ('href="https://', "href='https://")
ROW_OK_CITE = "verification.html#src-"
ROW_INTERNAL_MARKERS = ("Internal only", "Internal \u2014", "Internal -")
ROW_BLANK_MARKERS = ("blank (unverified)", "not confirmed", "not shown (policy)",
                     "no external source", "not applicable")

def row_is_sourced(row):
    # A row also passes when it prints the source URL as text (not a link) - the
    # verification register deliberately records short-link redirect hops as
    # non-clickable text (FLG-029), and the URL is still the manual-review source.
    if re.search(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+", re.sub(r"<[^>]+>", " ", row)):
        return True
    if any(k in row for k in ROW_OK_LINK):
        return True
    if ROW_OK_CITE in row:
        return True
    if "Internal only" in row:
        return True
    has_link = 'href="' in row or "href='" in row
    if has_link and any(m in row for m in ROW_INTERNAL_MARKERS):
        return True
    if has_link and any(m in row for m in ROW_BLANK_MARKERS):
        return True
    return False

for hf in html_files:
    content = read(hf)
    for m in re.finditer(r"(?s)<tr[^>]*>(.*?)</tr>", content):
        row = m.group(1)
        if "<td" not in row:
            continue  # header row
        if not row_is_sourced(row):
            fail(f"{hf}: a table row carries no official source link, no source-register "
                 f"citation and no explicit internal/blank note: {re.sub(r'<[^>]+>', ' ', row)[:90]!r}")

# --- deep links into the source register and the flagged register must resolve ---
ANCHOR_PAGES = {}
for hf in html_files:
    ANCHOR_PAGES[hf] = set(re.findall(r'id="([^"]+)"', read(hf)))

for hf in html_files:
    content = read(hf)
    for m in re.finditer(r'href="([^"]*?)#(src-[A-Za-z0-9]+|flag-FLG-[0-9]+|q-Q-[0-9]+|t-T-[0-9]+)"', content):
        target, anchor = m.group(1), m.group(2)
        target = target.replace("../", "").replace("./", "")
        if target and not target.endswith(".html"):
            continue
        if not target:
            target = hf
        if target not in ANCHOR_PAGES:
            fail(f"{hf}: deep link target page missing -> {target}#{anchor}")
        elif anchor not in ANCHOR_PAGES[target]:
            fail(f"{hf}: deep link anchor does not exist -> {target}#{anchor}")


# --- narrative + register integrity (session arena-038c0b80) -----------------
# Every cross-reference the site publishes must resolve, and every story must rest on
# a stored spec. Silent drift here is how a register starts lying about itself.
story_doc = json.load(open(os.path.join(ROOT, "data/stories.json"), encoding="utf-8"))
FLAG_IDS_ALL = {f["id"] for f in FLAGS}
PRODUCT_KEYS = {p["id"] for p in products}
for st in story_doc["stories"]:
    sid = st.get("product_id", "<no id>")
    for field in ("product_id", "series", "kicker", "headline", "standfirst", "paragraphs", "spec_anchor"):
        if not st.get(field):
            fail(f"stories.json: {sid}: field '{field}' is empty")
    if not isinstance(st.get("paragraphs"), list) or len(st["paragraphs"]) < 3:
        fail(f"stories.json: {sid}: needs at least 3 paragraphs to be a piece rather than a blurb")
    for f in st.get("flags", []) or []:
        if f not in FLAG_IDS_ALL:
            fail(f"stories.json: {sid}: cites unknown flag {f}")
    if st["spec_anchor"] not in PRODUCT_FIELDS:
        fail(f"stories.json: {sid}: spec_anchor '{st['spec_anchor']}' is not a stored product field")
for sname, pids in story_doc.get("_series", {}).items():
    for pid in pids:
        if pid not in PRODUCT_KEYS:
            fail(f"stories.json: series '{sname}' lists unknown product {pid}")

maker_doc = json.load(open(os.path.join(ROOT, "data/makers.json"), encoding="utf-8"))
for mk in maker_doc["makers"]:
    for field in ("id", "name", "who", "story", "checkable_claims"):
        if not mk.get(field):
            fail(f"makers.json: {mk.get('id')}: field '{field}' is empty")
    if len(mk["checkable_claims"]) < 2:
        fail(f"makers.json: {mk['id']}: fewer than 2 checkable claims")
    for c in mk["checkable_claims"]:
        if c.get("source_id") not in SRC_IDS:
            fail(f"makers.json: {mk['id']}: claim cites unknown source {c.get('source_id')!r}")
        if not c.get("claim") or not c.get("source_label"):
            fail(f"makers.json: {mk['id']}: claim without text or source label")

# every SG-/Q-/FLG- id cited in reader-facing HTML must exist in its register
for hf in html_files:
    if hf.startswith("archive"):
        continue
    body = read(hf)
    for sg in set(re.findall(r"\bSG-\d{2}\b", body)):
        if sg not in seen:
            fail(f"{hf}: cites {sg}, which is not in data/suggestions.json")
    for qq in set(re.findall(r"\bQ-\d{2}\b", body)):
        if qq not in seen_q:
            fail(f"{hf}: cites {qq}, which is not in data/questions.json")
    for ff in set(re.findall(r"\bFLG-\d{3}\b", body)):
        if ff not in FLAG_IDS_ALL:
            fail(f"{hf}: cites {ff}, which is not in data/flags.json")

# the capture control must stay switched off and un-submittable
# a page that merely MENTIONS the form (e.g. a suggestion card) is not a page that renders it
cap_pages = [hf for hf in html_files if 'id="reader-capture"' in read(hf)]
for hf in cap_pages:
    body = read(hf)
    if 'novalidate' not in body or 'data-nosubmit="true"' not in body:
        fail(f"{hf}: capture form lacks the novalidate/data-nosubmit guard (a JS-blocked browser would GET the address into a URL)")
    if 'method="get"' in body and 'action=""' not in body:
        fail(f"{hf}: capture form has a method with no empty action guard")

# --- inline JavaScript must parse (session arena-038c0b80) -------------------
# A broken inline script is invisible to every HTML check and to a reader until
# they click something. `node --check` is cheap and catches it.
import subprocess, tempfile
if html_files:
    for hf in html_files:
        body = read(hf)
        for k, m in enumerate(re.finditer(r"(?s)<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", body)):
            js = m.group(1).strip()
            if not js or js.startswith("{"):
                continue  # empty or JSON-LD
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
                tf.write(js)
                tmp = tf.name
            try:
                r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
                if r.returncode != 0:
                    first = [ln for ln in r.stderr.splitlines() if "Error" in ln][:1]
                    fail(f"{hf}: inline script #{k} does not parse as JavaScript ({first[0] if first else 'syntax error'})")
            except FileNotFoundError:
                pass  # node not installed: skip rather than fail the gate for a missing tool
            finally:
                os.unlink(tmp)

# --- register language kept out of reader values, and dated seasonal copy (f1fd0ff0) ---
for p2 in products:
    for fld in ("capacity", "dimensions", "weight", "temperature", "power", "model", "upc", "brand"):
        val = p2.get(fld) or ""
        if "FLG-" in val or re.search(r"\bS\d\d\b", val):
            fail(f"{p2['id']}: '{fld}' carries register language ({val[:60]!r}) — a reader copies this value into a "
                 f"shopping list; the note belongs in listing_notes and on Flagged for Review")
    cc = p2.get("card_copy")
    if cc:
        if "FLG-" in cc or PRICE_RE.search(cc):
            fail(f"{p2['id']}: card_copy carries a flag id or a price")
        if len(cc) > 400:
            fail(f"{p2['id']}: card_copy is {len(cc)} chars — a card line, not an article")

# a published topic must point at a guide file that actually exists
for t3 in topic_doc["topics"]:
    if t3.get("status") == "published":
        pa = t3.get("published_as") or ""
        if not pa:
            fail(f"topic {t3.get('id')}: marked published with no published_as path")
            continue
        if not os.path.exists(os.path.join(ROOT, pa)):
            fail(f"topic {t3.get('id')}: published_as {pa} is not built")
        src = "data/guides/" + os.path.basename(pa) + "src" if False else "data/guides/" + os.path.basename(pa).replace(".html", ".json")
        if not os.path.exists(os.path.join(ROOT, src)):
            fail(f"topic {t3.get('id')}: {pa} has no source file {src} (publish = drop a file in data/guides/)")

# an undated seasonal promise is how a site looks stale in public
idx_html2 = read("index.html") if os.path.exists(os.path.join(ROOT, "index.html")) else ""
m_sea = re.search(r'(?s)<section class="seasonal".*?</section>', idx_html2)
if m_sea and not re.search(r"20\d\d", m_sea.group(0)):
    fail("index.html: the seasonal strip carries no year — date it or drop it")
if m_sea and "amazon.com/dp/" in m_sea.group(0):
    fail("index.html: the seasonal strip links a product listing; keep it editorial and let the shop do that")


if errors:
    print(f"FAIL ({len(errors)} violations):")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: {len(html_files)} pages checked, {len(locs)} sitemap URLs, no violations.")
