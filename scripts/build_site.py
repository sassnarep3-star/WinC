#!/usr/bin/env python3
"""Build the ShopNow Kitchen static site from data/ (single source of truth).
Run: python3 scripts/build_site.py
No third-party dependencies. Generated HTML is committed for GitHub Pages (legacy build).
"""
import json, html, os, datetime, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sassnarep3-star.github.io/WinC/"
TAG = "shopnow047c-20"
# Build-date knob: keep the shipped date by default so rebuilds are byte-stable;
# set WINC_BUILD_DATE=YYYY-MM-DD for a dated rebuild. (arena-c2123b9c, 2026-11-20)
TODAY = os.environ.get("WINC_BUILD_DATE", "2026-11-20")

def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)

PRODUCTS = load("data/products.json")["products"]
LEDGER = load("data/campaign-ledger.json")
SOURCES = load("data/sources.json")["sources"]
FLAGS = load("data/flags.json")["flags"]
SRC = {s["id"]: s for s in SOURCES}

def load_guides():
    """Guides live in data/guides/*.json so publishing = drop a file. Newest first."""
    out = []
    for fn in sorted(glob.glob(os.path.join(ROOT, "data", "guides", "*.json"))):
        if os.path.basename(fn).startswith("_"):
            continue
        with open(fn, encoding="utf-8") as f:
            g = json.load(f)
        g["_file"] = os.path.basename(fn)
        g.setdefault("category", g.get("cluster", ""))
        g.setdefault("image", "")
        g.setdefault("published", TODAY)
        g.setdefault("updated", TODAY)
        g.setdefault("season", "Everyday")
        out.append(g)
    out.sort(key=lambda g: (g.get("published", ""), int(g.get("weight", 0) or 0), g.get("slug", "")), reverse=True)
    return out

GUIDES = load_guides()
PROBES = load("data/probes.json")
_sug = load("data/suggestions.json")
SUGGESTIONS = _sug["suggestions"]
QUESTIONS = load("data/questions.json")["questions"]
QMETA = load("data/questions.json")
CATEGORY_DATA = load("data/categories.json")
CATEGORY_PROFILES = {c["category"]: c for c in CATEGORY_DATA["categories"]}
TOPIC_DATA = load("data/topics.json")
TOPICS = TOPIC_DATA["topics"]
STORY_DATA = load("data/stories.json")
STORIES = {s["product_id"]: s for s in STORY_DATA["stories"]}
SERIES = STORY_DATA.get("_series", {})
MAKERS = {m["name"]: m for m in load("data/makers.json")["makers"]}
MAKER_BY_ID = {m["id"]: m for m in load("data/makers.json")["makers"]}
# series metadata: slug, page path, illustration, caption, standfirst
SERIES_META = {
    "The Countertop Series": {
        "slug": "series/countertop.html",
        "kicker": "Series · air fryers",
        "title": "The Countertop Series: three air fryers, read closely",
        "desc": "Three air-fryer shapes compared on the specs their listings actually state — two drawers, one XL drawer, one French-door cavity — with the contradictions inside each listing named rather than smoothed over.",
        "image": "assets/img/series-countertop.webp",
        "caption": "Editorial illustration: a two-drawer fryer, a single-drawer fryer and a French-door oven on a counter. Not a product photograph.",
        "lede": "Every machine in this series was read from its own Amazon listing, line by line, and every figure on these pages comes from that read. Where a listing disagrees with itself, the disagreement is printed.",
    },
    "The Thermometer Files": {
        "slug": "series/thermometers.html",
        "kicker": "Series · thermometers",
        "title": "The Thermometer Files: two ways to answer one question",
        "desc": "A handheld instant-read and a three-probe wireless system, measured against USDA's published temperature targets — and against the failure modes each design invites.",
        "image": "assets/img/series-thermometer.webp",
        "caption": "Editorial illustration: an instant-read probe and a wireless hub with probes. Not a product photograph.",
        "lede": "The USDA's minimum temperatures are the same whichever thermometer you own. What differs is who holds the tool while the food cooks — and what happens when the tool, or the phone, or the network, stops answering.",
    },
}
SERIES_OF = {}
for sname, pids in SERIES.items():
    for pid in pids:
        SERIES_OF[pid] = sname

CATEGORIES = [("Air Fryers", "air-fryers.html"), ("Meat Thermometers", "thermometers.html")]
CAT_IMG = {
    "Air Fryers": ("assets/img/air-fryers.webp",
        "Editorial illustration: air fryer baskets open on a kitchen counter. Not a product photograph."),
    "Meat Thermometers": ("assets/img/thermometers.webp",
        "Editorial illustration: instant-read probe and wireless sensor on a countertop. Not a product photograph."),
}
HERO_IMG = ("assets/img/hero-counter.webp",
    "Editorial illustration: kitchen counter with an air fryer, a probe thermometer and a board of roasted potatoes. Not a product photograph.")

def prods(cat=None):
    return [x for x in PRODUCTS if cat is None or x["category"] == cat]
def guides_for(cat=None):
    return [g for g in GUIDES if cat is None or g.get("category") == cat]
def words(html_str):
    return len(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", html_str)).split())
def read_min(g):
    return max(2, round(words(g["body"]) / 220))
def cluster_sentence():
    bits = []
    for name, _ in CATEGORIES:
        bits.append(f"{name} ({len(prods(name))} products, {len(guides_for(name))} guides)")
    return "; ".join(bits)
def counts():
    return {"products": len(PRODUCTS), "guides": len(GUIDES), "sources": len(SOURCES),
            "flags": len(FLAGS), "questions": len(QUESTIONS), "topics": len(TOPICS),
            "profiles": sum(len(v.get("profiles", [])) for v in CATEGORY_PROFILES.values()),
            "blocking": sum(1 for q in QUESTIONS if q.get("blocking","no").startswith("yes")),
            "open_sug": sum(1 for x in SUGGESTIONS if x["status"].startswith("open")),
            "done_sug": sum(1 for x in SUGGESTIONS if x["status"] == "done-this-session")}
BY_ASIN = {p["observed_asin"]: p for p in PRODUCTS}

def esc(s):
    return html.escape(str(s), quote=True)

def blank(v):
    v = (v or "").strip()
    return v if v else '<span class="blank">— blank (unverified)</span>'

def special_link(p):
    return f"https://www.amazon.com/dp/{p['observed_asin']}?tag={TAG}"

def buy_button(p, label=None):
    label = label or "Check price & details on Amazon"
    return (f'<a class="btn" href="{esc(special_link(p))}" rel="sponsored nofollow noopener" '
            f'target="_blank" data-event="outbound_click" data-asin="{esc(p["observed_asin"])}">{esc(label)}</a> '
            f'<span class="sponsored-tag">Sponsored · paid affiliate link</span>')

def buy_button_small(p):
    return (f'<a class="btn" href="{esc(special_link(p))}" rel="sponsored nofollow noopener" '
            f'target="_blank" data-event="outbound_click" data-asin="{esc(p["observed_asin"])}">Check on Amazon</a> '
            f'<span class="sponsored-tag">Sponsored · paid affiliate link</span>')

DISCLOSURE_STRIP = (
    '<div class="disclosure-strip" role="note"><div class="wrap">'
    '<strong>As an Amazon Associate I earn from qualifying purchases.</strong> '
    'This site contains sponsored product links. Prices and availability are shown on Amazon — '
    'check Amazon for current details. <a href="disclosure.html">Full disclosure</a>'
    '</div></div>'
)

def disclosure_strip_for(path):
    # fix relative link depth
    if "/" in path:
        link = "../disclosure.html"
    else:
        link = "disclosure.html"
    return (
        '<div class="disclosure-strip" role="note"><div class="wrap">'
        '<strong>As an Amazon Associate I earn from qualifying purchases.</strong> '
        'This site contains sponsored product links. Prices and availability are shown on Amazon — '
        f'check Amazon for current details. <a href="{link}">Full disclosure</a>'
        '</div></div>'
    )

NAV_READER = [
    ("index.html", "Home"),
    ("products/index.html", "The shop"),
    ("guides/index.html", "Guides"),
    ("air-fryers.html", "Air fryers"),
    ("thermometers.html", "Thermometers"),
    ("topics.html", "Topics"),
]
# Every dashboard surface lives in exactly one navigation group, and in the footer.
NAV_DESK = [
    ("verification.html", "Verification & sources"),
    ("flagged-for-review.html", "Flagged for review"),
    ("questions.html", "Open questions"),
    ("direction.html", "Suggestions & paths"),
    ("measurement.html", "Measurement & ledger"),
    ("executive-summary.html", "Executive summary"),
    ("search.html", "Search the site"),
    ("about.html", "About & method"),
    ("disclosure.html", "Disclosure"),
]

def nav_html(current, depth):
    pfx = "../" * depth
    def links(items):
        out = []
        for href, label in items:
            cur = ' aria-current="page"' if href == current else ""
            out.append(f'<a href="{pfx}{href}"{cur}>{label}</a>')
        return "".join(out)
    desk_cur = ' aria-current="page"' if any(href == current for href, _ in NAV_DESK) else ""
    return ('<nav class="mainnav" aria-label="Main content"><div class="wrap">'
            + links(NAV_READER)
            + f'<details class="desknav"{desk_cur}><summary>The Desk<span aria-hidden="true"> ⌄</span></summary>'
              f'<div class="deskgroup"><p class="desknote">Operations &amp; evidence — not part of the editorial flow.</p>'
            + links(NAV_DESK) + "</div></details></div></nav>")

def footer_html(depth):
    p = "../" * depth
    guide_links = "".join(
        f'<li><a href="{p}{g["path"]}">{esc(g["title"])}</a></li>' for g in GUIDES)
    cat_links = "".join(f'<li><a href="{p}{href}">{esc(n)}</a> ({len(prods(n))})</li>' for n, href in CATEGORIES)
    desk_links = "".join(f'<li><a href="{p}{href}">{label}</a></li>' for href, label in NAV_DESK)
    return f"""<footer><div class="wrap">
<div class="footer-disclosure"><strong>As an Amazon Associate I earn from qualifying purchases.</strong>
This site contains sponsored product links (marked <span class="sponsored-tag">Sponsored</span>).
Prices and availability are shown on Amazon — check Amazon for current details.
<a href="{p}disclosure.html">Full disclosure</a></div>
<div class="cols">
<div><h4>Shop</h4><ul>
<li><a href="{p}products/index.html">All {counts()['products']} products</a></li>
{cat_links}
</ul></div>
<div><h4>Guides</h4><ul>
<li><a href="{p}guides/index.html">All guides</a></li>
<li><a href="{p}topics.html">Topics: what is next</a></li>
{guide_links}
</ul></div>
<div><h4>The Desk</h4><ul>
{desk_links}
</ul></div>
<div><h4>Site</h4><ul>
<li><a href="{p}sitemap.xml">Sitemap</a></li>
<li><a href="{p}feed.xml">RSS feed</a></li>
<li><a href="{p}disclosure.html">Disclosure &amp; privacy</a></li>
<li><a href="{p}index.html">Front page</a></li>
</ul></div>
</div>
<p class="meta footnote">ShopNow Kitchen · {TODAY} · Tracking ID {TAG} (issuance unconfirmed — see FLG-001). Product names and trademarks belong to their owners; this site is not endorsed by or affiliated with Amazon beyond Associates participation. No testing, ranking or price claim is made without a stated source.</p>
</div></footer>"""


def head(title, desc, path, extra="", page_type="page", image=""):
    canon = SITE + path
    ogimg = f'\n<meta property="og:image" content="{SITE}{image}">' if image else ""
    tcard = ('\n<meta name="twitter:card" content="summary_large_image">' if image
             else '\n<meta name="twitter:card" content="summary">')
    ogtype = "article" if page_type == "guide" else "website"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{canon}">{ogimg}{tcard}
<link rel="stylesheet" href="{'../' if '/' in path else ''}assets/style.css">
<link rel="alternate" type="application/rss+xml" title="ShopNow Kitchen" href="{'../' if '/' in path else ''}feed.xml">
{extra}
</head>"""

def page_html(path, title, desc, body, page_type="page", extra_head="", image=""):
    depth = path.count("/")
    return (head(title, desc, path, extra_head, page_type, image) +
        f'<body data-page-type="{page_type}">'
        f'<header class="masthead"><div class="wrap"><a class="brand" href="{"../"*depth}index.html">ShopNow <span>Kitchen</span></a>'
        f'<p class="tagline">Basket or oven-style? Compare before you buy.</p>'
        f'<span class="dateline">{TODAY} · The Kitchen Desk</span></div></header>'
        + disclosure_strip_for(path) + nav_html(path, depth) +
        f'<main class="wrap">{body}</main>' + footer_html(depth) +
        f'<script src="{"../"*depth}assets/app.js" defer></script></body></html>')

def product_card(p, depth=0):
    pfx = "../" * depth
    img, cap = CAT_IMG.get(p["category"], HERO_IMG)
    specs = []
    if p["capacity"] and p["capacity"] != "—":
        specs.append(f"Capacity: {esc(p['capacity'])}")
    if p["dimensions"]:
        specs.append(f"Size: {esc(p['dimensions'])}")
    if p["weight"]:
        specs.append(f"Weight: {esc(p['weight'])}")
    if p["model"]:
        specs.append(f"Model: {esc(p['model'])}")
    # thermometers carry no capacity/model sometimes: fall back to the spec the listing does state
    if not specs:
        if p.get("temperature"):
            specs.append(f"Reading: {esc(p['temperature'])}")
        if p.get("power") and p["power"] != "—":
            specs.append(f"Power: {esc(p['power'])}")
    li = "".join(f"<li>{x}</li>" for x in specs)
    # The card carries one prose paragraph (the story standfirst), then the two decision
    # lines a shopper actually compares on: what it is best for, and what it costs you.
    # The longer dek belongs on the product page, where there is room for it.
    best = p.get("best_for")
    catch = p.get("catch")
    best_html = (f'<p class="bestfor"><strong>Best for</strong> {esc(best)}</p>'
                 if best else "")
    catch_html = (f'<p class="catchline"><strong>The catch:</strong> {esc(catch)}</p>'
                  if catch else "")
    return f"""<article class="card">
<figure class="cardimg">{pic(img, cap, 800, 500, pfx, cls="cardpic")}</figure>
<span class="cat">{esc(p['category'])} · {esc(p['brand'])}</span>
<h3><a href="{pfx}{p['page']}">{esc(p['short_label'])}</a></h3>
<p class="cardhook">{esc((STORIES.get(p["id"]) or {}).get("standfirst") or p["title"])}</p>
{best_html}
<ul class="specs">{li}</ul>
{catch_html}
<div class="actions">{buy_button_small(p)}</div>
<div class="cardfoot">{series_link(p, depth)}{('<a class="sourcetail" href="' + pfx + 'verification.html">Listing read ' + esc(p["source_date"]) + '</a>')}</div>
<p class="meta">ASIN {esc(p['observed_asin'])} · <a href="{pfx}verification.html">Source</a></p>
</article>"""

def pic(img, alt, w, h, pfx="", lazy=True, cls=None):
    """Serve WebP, keep the PNG as the fallback so no reference anywhere 404s.

    Returns a bare <img> when no WebP twin exists, so this helper can never point at a
    file the repository does not have.
    """
    webp = img[:-4] + ".webp" if img.lower().endswith(".png") else None
    load = ' loading="lazy"' if lazy else ""
    klass = f' class="{cls}"' if cls else ""
    if webp and os.path.exists(os.path.join(ROOT, webp)):
        return (f'<picture><source srcset="{pfx}{webp}" type="image/webp">'
                f'<img src="{pfx}{img}" alt="{esc(alt)}"{klass}{load} width="{w}" height="{h}"></picture>')
    return f'<img src="{pfx}{img}" alt="{esc(alt)}"{klass}{load} width="{w}" height="{h}">'

def guide_card(g, depth=0):
    pfx = "../" * depth
    img = g.get("image") or CAT_IMG.get(g.get("category", ""), HERO_IMG)[0]
    cap = g.get("image_caption", "Editorial illustration. Not a product photograph.")
    return f'''<article class="card guidecard">
<figure class="cardimg">{pic(img, "Editorial illustration for: " + g["title"], 800, 500, pfx, cls="cardpic")}</figure>
<span class="cat">Guide · {esc(g['cluster'])}</span>
<h3><a href="{pfx}{g['path']}">{esc(g['title'])}</a></h3>
<p>{esc(g['desc'])}</p>
<p class="meta">{esc(g['published'])} · {read_min(g)} min read · {esc(g.get('season', 'Everyday'))}</p>
</article>'''

def link_source_ids(text, prefix="", suffix=""):
    """Turn (S05)-style references into links to the source register anchor."""
    def repl(m):
        sid = m.group(1)
        if sid not in SRC:
            return m.group(0)
        return (f'<a href="{prefix}verification.html#src-{sid}">({sid})</a>')
    return re.sub(r"\((S\d{2})\)", repl, text)

def source_link(url, label):
    """Evidence citation. Deliberately NOT an affiliate link: no tag, nofollow."""
    return f'<a class="srclink" href="{esc(url)}" rel="nofollow noopener" target="_blank">{esc(label)}</a>'

def rich(text):
    """Escape, then let `backticked` spans become code. Register copy is prose, not HTML."""
    return re.sub(r"`([^`\n]{1,120})`", r"<code>\1</code>", esc(text))

def pill(text, kind="note"):
    return f'<span class="pill pill-{esc(kind)}">{esc(text)}</span>'

def specs_table(p):
    rows = [
        ("Brand", p["brand"]),
        ("Model", p["model"]),
        ("Category", p["category"]),
        ("Capacity", p["capacity"]),
        ("Dimensions", p["dimensions"]),
        ("Weight", p["weight"]),
        ("Temperature / accuracy", p["temperature"]),
        ("Power", p["power"]),
        ("UPC", p["upc"]),
        ("Price", p["price"]),
        ("Rating / reviews", p["rating"]),
    ]
    trs = []
    for k, v in rows:
        trs.append(f"<tr><th>{esc(k)}</th><td>{blank(v)}</td></tr>")
    return ('<div class="tablewrap"><table><thead><tr><th>Field</th><th>Value (as listed on Amazon)</th></tr></thead><tbody>'
            + "".join(trs) + "</tbody></table></div>"
            + f'<p class="src">Source: <a href="{esc(p["source_url"])}" rel="nofollow noopener" target="_blank">{esc(p["source_url"])}</a> · checked {esc(p["source_date"])}. Blank = not confirmed from an official source (see <a href="../flagged-for-review.html">Flagged for Review</a>).</p>')

def capture_block(depth=0):
    pfx = "../" * depth
    return f"""<section class="capture" aria-label="Reader updates">
<h3>Get the next comparison — checklist first, hype never.</h3>
<p>One email when a new guide publishes.</p>
<form id="reader-capture" action="" method="get" novalidate data-nosubmit="true">
<label for="email">Email address</label>
<input id="email" name="email" type="email" autocomplete="email" placeholder="you@example.com">
<button class="btn" type="submit">Subscribe</button>
</form>
<script>
// Nothing is transmitted and nothing is submitted — not even into this page's own URL.
// A browser with JavaScript disabled gets a disabled control and an honest sentence, not a silent GET.
document.getElementById('reader-capture').addEventListener('submit', function(e){{ e.preventDefault(); }});
</script>
<small>There is no newsletter running yet, so this control is switched off on purpose: it transmits nothing, stores your address nowhere, and cannot submit a form. A subscription flow needs a provider, a consent record and a retention period first — those are open questions on the <a href="{pfx}questions.html">questions page</a>, and the <a href="{pfx}disclosure.html">disclosure</a> states exactly what this site does and does not collect.</small>
</section>"""

# ---------- HOME ----------
def home_body():
    c = counts()
    cards = "".join(product_card(x) for x in PRODUCTS)
    rail = "".join(guide_card(g) for g in GUIDES[:4])
    img, cap = HERO_IMG
    lead = GUIDES[0]
    # series rail, built from the series register so it cannot drift
    series_cards = ""
    for sname, meta in SERIES_META.items():
        n = len(SERIES.get(sname, []))
        series_cards += (f'<a class="seriestile" href="{esc(meta["slug"])}">'
                         f'<img src="{esc(meta["image"])}" alt="{esc(meta["caption"])}" loading="lazy" width="1200" height="655">'
                         f'<span class="sname">{esc(sname)}</span>'
                         f'<span class="scount">{n} products · read closely</span></a>')
    tiles = ""
    for name, href in CATEGORIES:
        cimg, ccap = CAT_IMG[name]
        tiles += (f'<a class="cattile" href="{href}"><img src="{cimg}" alt="{esc(ccap)}" loading="lazy" width="800" height="500">'
                  f'<span class="catname">{esc(name)}</span><span class="catcount">{len(prods(name))} in the shop · {len(guides_for(name))} guides</span></a>')
    by_season = {}
    for g in GUIDES:
        s = (g.get("season") or "Everyday").strip()
        if s and s != "Everyday":
            by_season.setdefault(s, []).append(g)
    season_bands = ""
    for sname, gs in by_season.items():
        scards = "".join(guide_card(g) for g in gs)
        season_bands += f'<h2>In season · {esc(sname)}</h2>\n<div class="grid">{scards}</div>\n'
    return f"""
<section class="hero">
<span class="kicker">The Kitchen Desk · {len(GUIDES)} guides, {c['products']} products, every figure sourced</span>
<h1>Small appliances, decided on the specs that actually change your cooking</h1>
<p class="lede">Two drawers or one? Instant-read or leave-in? Each piece below turns one checkable listed spec into the question you are really asking — and prints where the listing disagrees with itself instead of smoothing it over.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · <a href="about.html">How we check</a> · <a href="verification.html">Source register</a></p>
<figure class="lede-figure">{pic(img, cap, 1200, 800, lazy=False)}<figcaption>{esc(cap)}</figcaption></figure>
<p class="cta-row"><a class="btn btn-ghost" href="products/index.html">Shop all {c['products']} products →</a> <a class="btn btn-quiet" href="{lead['path']}">Start with the newest guide</a></p>
</section>

<h2>The series</h2>
<p class="seclede">Each series reads one category's listings closely — the shape decision, the trades each design makes, and the numbers the listing contradicts.</p>
<div class="seriesgrid">{series_cards}</div>

{house_ad()}
<h2>The shop</h2>
<div class="grid">{cards}</div>
<p class="seclink"><a class="btn btn-quiet" href="products/index.html">Compare every spec in one table →</a></p>

<h2>Start with a question, not a brand</h2>
<div class="grid">{rail}</div>
<p class="seclink"><a class="btn btn-quiet" href="guides/index.html">All {c['guides']} guides →</a> <a class="btn btn-quiet" href="topics.html">What we are writing next →</a></p>

{season_bands}<h2>Or start with a category</h2>
<div class="catgrid">{tiles}</div>

<h2>How this site works</h2>
<div class="notice"><strong>Every number here is copied from the manufacturer's own Amazon listing, with the link and the date beside it.</strong> Where a value could not be confirmed, the cell stays blank and is listed for review — never estimated. Every outbound product link is sponsored and labelled as such: the <a href="disclosure.html">disclosure</a> explains it, and the <a href="verification.html">source register</a> shows the evidence.</div>
{capture_block()}
"""

# ---------- CATEGORY PAGES ----------
SPEC_LABELS = {
    "capacity": "listed capacity",
    "dimensions": "listed footprint",
    "weight": "listed weight",
    "temperature": "listed temperature range",
    "power": "listed power",
    "model": "listed model number",
    "title": "what the listing says the product is",
    "brand": "listed brand",
    "upc": "listed UPC",
    "listing_claims": "the listing's own claims",
    "observed_asin": "the ASIN the link resolves to",
}

def human_key(k):
    return k.replace("_", " ").capitalize()

def profile_block(cat):
    """Reader situations for a category. Every answer names the one listed spec it rests on."""
    profs = CATEGORY_PROFILES.get(cat, {}).get("profiles", [])
    if not profs:
        return '<p class="meta">No profiles recorded for this category yet.</p>'
    out = []
    for pr in profs:
        out.append(f"""<article class="profile">
<h3>{esc(pr['situation'])}</h3>
<p class="sugmeta">Deciding spec: <strong>{esc(SPEC_LABELS.get(pr['deciding_spec'], human_key(pr['deciding_spec'])))}</strong></p>
<p>{esc(pr['what_the_listings_say'])}</p>
<p><strong>What that means for you:</strong> {esc(pr['answer'])}</p>
<p class="src">Source: <a href="{esc(pr['source'])}" rel="nofollow noopener" target="_blank">{esc(pr['source'])}</a> · listings read {TODAY}.</p>
</article>""")
    return '<div class="profilelist">' + "".join(out) + "</div>"

def category_body(cat, title, intro, guide_links):
    ps = [p for p in PRODUCTS if p["category"] == cat]
    cards = "".join(product_card(p) for p in ps)
    cols = ["Field"] + [p["short_label"] for p in ps]
    fields = ["Brand", "Model", "Capacity", "Dimensions", "Weight", "Temperature / accuracy", "Power", "UPC", "Price"]
    keys = ["brand", "model", "capacity", "dimensions", "weight", "temperature", "power", "upc", "price"]
    head_row = "".join(f"<th>{esc(c)}</th>" for c in cols)
    rows = []
    for f, k in zip(fields, keys):
        cells = "".join(f"<td>{blank(p[k])}</td>" for p in ps)
        rows.append(f"<tr><th>{esc(f)}</th>{cells}</tr>")
    table = ('<div class="tablewrap"><table><thead><tr>' + head_row + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
             + '<p class="src">Sources: ' + " · ".join(f'<a href="{esc(p["source_url"])}" rel="nofollow noopener" target="_blank">{esc(p["observed_asin"])}</a>' for p in ps) + f' · checked {TODAY}. Blank = unverified.</p>')
    return f"""
<section class="hero"><span class="kicker">Category · {esc(cat)}</span>
<h1>{esc(title)}</h1><p class="lede">{esc(intro)}</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<h2>Match to your situation</h2>
<p>Each answer names the one listed spec that settles the case, and links the listing it came from. Nobody here has cooked with these units, so there is no “we tested it” line anywhere — you check the spec against your kitchen.</p>
{profile_block(cat)}
<div class="grid">{cards}</div>
<h2>Compare side by side</h2>
{table}
<h2>Guides for this category</h2>
<ul>{guide_links}</ul>
{capture_block()}
"""

def house_ad(depth=0):
    """A quiet in-shop promo. Not a pop-up, not a countdown: one line, one link, clearly ours."""
    lead = GUIDES[0] if GUIDES else None
    if not lead:
        return ""
    pfx = "../" * depth
    return f"""<aside class="housead" aria-label="From the Kitchen Desk">
<div><h3>Can one listed spec decide it for you?</h3>
<p>Start with “{esc(lead['title'])}” — {read_min(lead)} minutes, every figure linked, no price quoted anywhere.</p></div>
<a class="btn" href="{pfx}{esc(lead['path'])}">Read the guide →</a>
</aside>"""

# ---------- STORY LAYER: series + product narratives ----------
def series_link(p, depth=0):
    """Small series badge for a product card, or empty when the product is not in a series."""
    sname = SERIES_OF.get(p["id"])
    if not sname:
        return ""
    meta = SERIES_META[sname]
    return f'<a class="seriesbadge" href="{"../"*depth}{meta["slug"]}">{esc(sname)}</a>'

def story_paragraphs(st):
    return "".join(f"<p>{esc(par)}</p>" for par in st["paragraphs"])

def story_body(p):
    """The long narrative on a product page: a published piece, not a spec dump."""
    st = STORIES.get(p["id"])
    if not st:
        return ""
    mk = MAKER_BY_ID.get({"Chefman": "chefman", "Emeril": "emeril",
                          "ThermoMaven": "thermomaven", "CHEF iQ": "chefiq"}.get(p["brand"], ""), {})
    anchor_label = SPEC_LABELS.get(st.get("spec_anchor", ""), human_key(st.get("spec_anchor", "")))
    anchor_value = p.get(st.get("spec_anchor", "")) or "not confirmed from the listing"
    sname = SERIES_OF.get(p["id"])
    series_meta = SERIES_META.get(sname, {})
    # one series marker only: the badge itself links to the series page
    crumb = (f'<p class="seriesline"><a class="seriesmark" href="../{esc(series_meta.get("slug", ""))}">{esc(st["series"])}</a>'
             f' · <span class="meta">series</span></p>' if sname else "")
    maker = ""
    if mk:
        maker = (f'<div class="makerbox"><h3>About the maker: {esc(mk["name"])}</h3>'
                 f'<p>{esc(mk["story"])}</p>'
                 f'<ul class="makerclaims">'
                 + "".join(f'<li>{esc(c["claim"])} <span class="meta">— {esc(c["source_label"])}, '
                           f'<a href="../verification.html#src-{esc(c["source_id"])}">{esc(c["source_id"])}</a></span></li>'
                           for c in mk["checkable_claims"])
                 + "</ul>"
                 + (f'<p class="meta">Official brand site, listed for your own check and not quoted here: '
                    f'<a href="{esc(mk["official_site"])}" rel="nofollow noopener" target="_blank">{esc(mk["official_site"])}</a></p>'
                    if mk.get("official_site") else f'<p class="meta">{esc(mk.get("official_site_note", ""))}</p>')
                 + "</div>")
    flags = "".join(f'<a class="flagchip" href="../flagged-for-review.html">{esc(f)}</a>' for f in st.get("flags", []))
    flagrow = (f'<p class="meta">Listing contradictions this piece depends on: {flags}</p>' if flags else "")
    return f"""
<article class="story">
{crumb}
<h2>{(esc(st['headline']))}</h2>
<p class="standfirst">{esc(st['standfirst'])}</p>
<p class="anchorline"><strong>Deciding spec:</strong> {esc(anchor_label)} — <em>{esc(anchor_value)}</em>, as listed. <a href="{esc(p['source_url'])}" rel="nofollow noopener" target="_blank">Read it on Amazon</a></p>
{story_paragraphs(st)}
{flagrow}
{maker}
</article>"""

def series_body(sname):
    meta = SERIES_META[sname]
    pids = SERIES.get(sname, [])
    members = [p for p in PRODUCTS if p["id"] in pids]
    cards = "".join(product_card(p, depth=1) for p in members)
    pieces = ""
    for p in members:
        st = STORIES.get(p["id"])
        if not st:
            continue
        pieces += (f'<article class="seriespiece"><p class="meta">{esc(st["kicker"])} · {esc(p["short_label"])}</p>'
                   f'<h3>{esc(st["headline"])}</h3><p>{esc(st["standfirst"])}</p>'
                   f'<p><a class="btn btn-quiet" href="../{esc(p["page"])}">Read the full piece →</a></p></article>')
    guide_links = "".join(
        f'<li><a href="../{g["path"]}">{esc(g["title"])}</a> <span class="meta">({read_min(g)} min read)</span></li>'
        for g in GUIDES if g.get("category") in {q["category"] for q in members})
    return f"""
<section class="hero"><span class="kicker">{esc(meta['kicker'])}</span>
<h1>{esc(meta['title'])}</h1>
<p class="lede">{esc(meta['lede'])}</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · {len(members)} products · <a href="../about.html">How we check</a></p></section>
<figure class="lede-figure">{pic(meta["image"], meta["caption"], 1200, 655, "../", lazy=False)}<figcaption>{esc(meta["caption"])}</figcaption></figure>
<h2>In this series</h2>
<div class="grid">{cards}</div>
<h2>The pieces</h2>
<div class="serieslist">{pieces}</div>
<h2>Guides that go with it</h2>
<ul>{guide_links}</ul>
<div class="byline-box"><strong>How these pages are made.</strong> Each piece starts from one stored spec in <code>data/products.json</code> and argues only from that spec and from USDA's published figures where food safety is involved. No machine in this series has been tested or used by this desk, so no line here claims experience. Contradictions inside a listing are published on the product page and on <a href="../flagged-for-review.html">Flagged for review</a> rather than resolved by preference.</div>
{capture_block(depth=1)}
"""

# ---------- PRODUCT PAGES ----------
def product_body(p):
    related = [q for q in PRODUCTS if q["category"] == p["category"] and q["id"] != p["id"]]
    rel_cards = "".join(product_card(q, depth=1) for q in related)
    if p["category"] == "Air Fryers":
        guides = ('<li><a href="../guides/basket-or-oven-style-air-fryer.html">Basket or oven-style: what should you compare?</a></li>'
                  '<li><a href="../guides/air-fryer-capacity-checklist.html">Capacity checklist</a></li>'
                  '<li><a href="../guides/cleanup-and-counter-space.html">Cleanup &amp; counter-space trade-offs</a></li>')
    else:
        guides = ('<li><a href="../guides/instant-read-or-leave-in.html">Instant-read or leave-in probe</a></li>'
                  '<li><a href="../guides/multi-function-appliance-questions.html">Questions before buying a multi-function appliance</a></li>'
                  '<li><a href="../thermometers.html">Compare both thermometers</a></li>')
    notes = ""
    if p.get("listing_notes"):
        items = "".join(f'<li><strong>{esc(n["flag"])}:</strong> {esc(n["note"])}</li>' for n in p["listing_notes"])
        notes = (f'<h2>Where the listing disagrees with itself</h2><ul class="notes">{items}</ul>'
                 '<p class="meta">Every item above is published on the <a href="../flagged-for-review.html">Flagged for review</a> page with the action that would settle it. '
                 'None of them is resolved by guessing.</p>')
    claims = ""
    if p.get("listing_claims"):
        rows = "".join(f'<tr><th>{esc(human_key(k))}</th><td>{esc(v)}</td></tr>' for k, v in p["listing_claims"].items())
        claims = (f'<h2>What the listing claims, quoted as claims</h2><div class="tablewrap"><table><thead><tr><th>Claim</th>'
                  f'<th>What the listing says</th></tr></thead><tbody>{rows}</tbody></table></div>'
                  f'<p class="src">Source: <a href="{esc(p["source_url"])}" rel="nofollow noopener" target="_blank">{esc(p["source_url"])}</a> · read {esc(p["source_date"])}. '
                  "These are the statements the seller wrote on the listing — not measurements taken by this site.</p>")
    faq = p.get("faq") or []
    faq_html = ""
    if faq:
        rows = "".join(f'<details class="faqitem"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq)
        faq_html = f'<h2>Questions readers ask about this one</h2><div class="faqlist">{rows}</div>'
    # The desk's own read of the product: one line, what it is best for, and the catch.
    # Every one of these fields was checked against the register before it was written —
    # the specs table below is the evidence.
    dek = p.get("dek") or p["title"]
    best = p.get("best_for")
    catch = p.get("catch")
    desk = (f'<div class="deskline">'
            f'<p class="dekline">{esc(dek)}</p>'
            + (f'<p class="bestfor"><strong>Best for</strong> {esc(best)}</p>' if best else "")
            + (f'<p class="catchline"><strong>The catch:</strong> {esc(catch)}</p>' if catch else "")
            + "</div>")
    checks = p.get("check_before_buying") or []
    checks_html = ""
    if checks:
        items = "".join(f"<li>{esc(c)}</li>" for c in checks)
        checks_html = (f'<h2>Check these three things before you buy</h2><ul class="notes checks">{items}</ul>'
                       '<p class="meta">Each line is a check on the listing, not a verdict on the product. '
                       'Where the listing contradicts itself, the contradiction is named and flagged '
                       'rather than resolved here.</p>')
    return f"""
<section class="hero"><span class="kicker">{esc(p['category'])} · {esc(p['brand'])}</span>
<h1>{esc(p['short_label'])}</h1>
<p class="lede">{esc((STORIES.get(p['id']) or {}).get('standfirst') or p['title'])}</p>
{desk}
<p class="aslisted"><span class="aslabel">As listed on Amazon</span> {esc(p['title'])}</p>
<p class="meta">Observed ASIN {esc(p['observed_asin'])} · Listing checked {esc(p['source_date'])} · <a href="../verification.html">Verification record</a></p>
<div class="actions" style="margin:14px 0">{buy_button(p)}</div>
<p class="meta">You will go to Amazon. Price and availability are shown there. This button is a sponsored link.</p>
</section>
{story_body(p)}
{house_ad(depth=1)}
<h2>Specs (from Amazon’s listing)</h2>
{specs_table(p)}
{checks_html}
<h2>What to compare before you buy</h2>
<ul>
<li><strong>Capacity vs. your actual meals:</strong> {esc(p['capacity'] or 'see listing')} — measure the tray or bird you cook most often.</li>
<li><strong>Footprint:</strong> {esc(p['dimensions'] or 'not confirmed — measure the listing’s dimensions on Amazon')} — check counter depth and cabinet clearance.</li>
<li><strong>Cleanup:</strong> check whether baskets/parts are listed as dishwasher-safe on Amazon before you buy.</li>
<li><strong>Functions you will use weekly:</strong> presets only help if they match your routine (see the multi-function guide).</li>
</ul>
{notes}
{claims}
{faq_html}
<h2>Related guides</h2><ul>{guides}</ul>
<h2>More in {esc(p['category'])}</h2>
<div class="grid">{rel_cards}</div>
{capture_block(depth=1)}
"""

# ---------- GUIDES: loaded from data/guides/*.json (see load_guides) ----------

def guide_body(g):
    pool = prods(g.get("category")) or PRODUCTS
    cards = "".join(product_card(x, depth=1) for x in pool)
    body = g["body"].replace("CARDS", cards)
    cap = g.get("image_caption", "Editorial illustration. Not a product photograph.")
    fig = ""
    if g.get("image"):
        fig = (f'<figure class="lede-figure"><img src="../{esc(g["image"])}" alt="{esc(cap)}" width="1200" height="800">'
               f'<figcaption>{esc(cap)}</figcaption></figure>')
    cat_href = dict(CATEGORIES).get(g.get("category"), "guides/index.html")
    return f"""
<section class="hero"><span class="kicker">Guide · {esc(g['cluster'])} · Season: {esc(g.get('season','Everyday'))}</span>
<h1>{esc(g['title'])}</h1>
<p class="lede">{esc(g['desc'])}</p>
<p class="meta">By the ShopNow Kitchen Desk · Published {esc(g['published'])} · Updated {esc(g['updated'])} · {read_min(g)} min read · <a href="../{cat_href}">This category</a> · <a href="../verification.html">Sources</a></p>
</section>
{fig}
<div class="guide-hero">{body}</div>
<div class="byline-box"><strong>How this page was made.</strong> Written from published listings and official guidance, by an editorial desk — not from hands-on use, so no page here claims testing. Every table row links to its source; anything we could not confirm is left blank and listed on <a href="../flagged-for-review.html">Flagged for review</a>. Sponsored links are marked <span class="sponsored-tag">Sponsored</span>.</div>
{capture_block(depth=1)}
"""

def breadcrumb_jsonld(items):
    """items: list of (name, site-relative path)."""
    li = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
          for i, (n, u) in enumerate(items)]
    return ('<script type="application/ld+json">' +
            json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": li}) + "</script>")


def article_jsonld(g):
    return ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": g["title"], "description": g["desc"],
        "datePublished": g["published"], "dateModified": g.get("updated", g["published"]),
        "author": {"@type": "Organization", "name": "ShopNow Kitchen Desk"},
        "publisher": {"@type": "Organization", "name": "ShopNow Kitchen"},
        "image": SITE + (g.get("image") or HERO_IMG[0]),
        "mainEntityOfPage": SITE + g["path"],
        "isAccessibleForFree": True,
        "articleSection": g.get("cluster", ""),
    }) + "</script>")


def product_faq_jsonld(p):
    faq = p.get("faq") or []
    if not faq:
        return ""
    items = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]
    return ('<script type="application/ld+json">' +
            json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}) + "</script>")


def faq_jsonld(g):
    items = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]
    return ('<script type="application/ld+json">' +
            json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}) + "</script>")

# ---------- DIRECTION ----------
def status_pill_class(st):
    if st.startswith("done"): return "ok"
    if st.startswith("recommended"): return "act"
    if st.startswith("open-blocked"): return "blocked"
    if st.startswith("open"): return "wait"
    if st.startswith("fixed"): return "ok"
    return "note"

EFFORT = {"S": "small — hours", "M": "medium — a session", "L": "large — more than one session"}

def suggestion_table():
    rows = ""
    for x in SUGGESTIONS:
        cls = status_pill_class(x["status"])
        rows += (f'<tr><td><strong>{esc(x["id"])}</strong></td>'
                 f'<td><a href="#{esc(x["id"])}">{esc(x["title"])}</a></td>'
                 f'<td>{esc(x["area"])}</td><td>{esc(x["effort"])}</td><td>{esc(x["cost"])}</td>'
                 f'<td>{pill(x["status"], cls)}</td>'
                 f'<td>{esc(x["expected_effect"])}</td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th>ID</th><th>Suggestion</th><th>Area</th><th>Effort</th>'
            '<th>Cost</th><th>Status</th><th>How we would know it worked</th></tr></thead><tbody>'
            + rows + "</tbody></table></div>")


def suggestion_stages():
    now = [x for x in SUGGESTIONS if x["status"].startswith("recommended")]
    decide = [x for x in SUGGESTIONS if x["status"] == "open"]
    blocked = [x for x in SUGGESTIONS if x["status"].startswith("open-blocked")]
    shipped = [x for x in SUGGESTIONS if x["status"].startswith("shipped") or x["status"].startswith("done-this-session")]
    def block(title, items, note):
        if not items:
            return ""
        lis = "".join(f'<li><a href="#{esc(x["id"])}"><strong>{esc(x["id"])}</strong> — {esc(x["title"])}</a></li>' for x in items)
        return f'<h3>{esc(title)}</h3><ul class="stagelist">{lis}</ul><p class="meta">{esc(note)}</p>'
    return (block("Do now", now, "These gate everything else: until they are done, the site cannot earn or be measured.")
            + block("Decide next", decide, "Each one is a decision only the owner can take; the evidence is on the card below.")
            + block("Blocked", blocked, "Blocked items wait on a named question on the open-questions register.")
            + block("Already shipped", shipped, "Done in an earlier session or this one — kept so the reasoning is not lost."))


DECISION_PATHS = {
    "A": {
        "name": "Path A — Trust the money path first",
        "when": "Choose this if any commission at all depends on these links working.",
        "what": "Confirm the tracking ID, run the one-link Associates test per product, keep every link gated until it passes.",
        "steps": [
            "Q-01: confirm <code>shopnow047c-20</code> is issued and the Pages domain is on the site list (Associates Central → Tracking IDs).",
            "FLG-002: run one link through the enrolled workflow — click it, confirm the destination, then confirm the click appears in the report.",
            "Record the result in <code>data/products.json</code> → <code>intended_*</code> and <code>confirmation_date</code>; never merge it into <code>observed_*</code>.",
            "Re-run <code>npm run verify</code>; the gate refuses an intended ASIN that is not confirmed."],
        "cost": "No money. One owner session inside the Associates account.",
        "risk": "Temporarily suppresses the only monetisation path. That is the point: an untested tagged link is the classic reason accounts get closed.",
        "done_when": "Every buy button traces to a confirmed tracking ID and a recorded one-link test.",
    },
    "B": {
        "name": "Path B — Shop depth",
        "when": "Choose this if conversion matters more than reach right now.",
        "what": "Deepen the decision blocks, settle the imagery question, and add per-row source dates to every spec.",
        "steps": [
            "SG-10: resolve the two live listing conflicts (8-Qt temperature, Emeril accessory count) against the manufacturer page, not a sibling listing.",
            "SG-19 / Q-25: decide the imagery line — generated illustrations with a recorded licence, or licensed photography.",
            "SG-16: extend the reader-situation blocks so each one names its deciding spec and its source date.",
            "Re-read every spec row in a normal browser and correct any drift (FLG-029)."],
        "cost": "A photography budget if SG-19 goes that way; otherwise none.",
        "risk": "Depth on five products does not create reach. Pair it with Path D or the site stays a well-documented secret.",
        "done_when": "Every spec row has a dated read, and the imagery licence is on record.",
    },
    "C": {
        "name": "Path C — Content volume",
        "when": "Choose this if reach is the bottleneck and the links are known to work.",
        "what": "Two guides a week from the published topic backlog, one seasonal cluster at a time.",
        "steps": [
            "Pick topics from <code>data/topics.json</code> — the ones whose status is <code>planned</code>, not <code>blocked</code>.",
            "Scaffold each one with <code>python3 scripts/new_guide.py &quot;the question&quot;</code>; the index, sitemap, feed and search all follow from the file.",
            "Keep the rule: a row without an official source stays blank and gets a flag.",
            "Run the gate before every publish."],
        "cost": "Time only — roughly one session per two guides.",
        "risk": "Without measurement you are guessing which topic to write next, and the backlog's 'chosen from' column will stay honest but useless.",
        "done_when": "Four weeks of guides with the same gate discipline.",
    },
    "D": {
        "name": "Path D — Measure first",
        "when": "Choose this if you cannot say which page earns anything.",
        "what": "Deploy one analytics endpoint, verify the five events land, and add nothing until four weeks of real data exist.",
        "steps": [
            "FLG-007: deploy <code>analytics/worker.js</code> (or <code>analytics/collect.py</code>) and set <code>CONFIG.endpoint</code> in <code>assets/app.js</code>.",
            "SG-29: verify the Search Console property and submit <code>sitemap.xml</code>; record the date on the Measurement page.",
            "Watch <code>outbound_click</code> per ASIN, not page views. Clicks are the only number this site can currently see.",
            "Transcribe orders only from an authorised Associates report, into <code>data/campaign-ledger.json</code>, with the export date."],
        "cost": "One endpoint host; several free tiers exist, and <code>collect.py</code> needs only a box you already own.",
        "risk": "Four weeks of no new content. The compensation is that the fifth week's topic is chosen from queries instead of taste.",
        "done_when": "The ledger has its first first-party row with a provenance string.",
    },
}

def decision_desk(c):
    paths = ""
    for key, p in DECISION_PATHS.items():
        paths += (f'<div class="pickrow"><span class="n" style="display:inline-grid;place-items:center;width:26px;height:26px;'
                  f'border-radius:999px;background:#1C1917;color:#FBBF24;font-weight:800;font-size:13px">{key}</span>'
                  f'<div><strong>{esc(p["name"])}</strong><span class="meta">{esc(p["when"])}</span></div></div>')
    return f"""
<h2 id="decide">Choose a path — and see the consequences before you commit</h2>
<p>This is the section for deciding, not for browsing. Four paths, each with what it costs, what it risks and how you will know it worked. Nothing below changes the site by itself: a path is a decision, and the build applies it afterwards.</p>
<div class="desksteps">
<div class="deskstep"><span class="n">1</span><h4>Read the suggestions</h4><p>{c['open_sug']} open items, each with evidence, effort, risk and a way to measure it. <a href="#suggestions">Jump to the register</a></p></div>
<div class="deskstep"><span class="n">2</span><h4>Answer what blocks you</h4><p>{c['blocking']} blocking questions cannot be answered from this repo — they need the enrolled account. <a href="questions.html">Open the questions register</a></p></div>
<div class="deskstep"><span class="n">3</span><h4>Pick one path</h4><p>Paths are mutually exclusive for a single build. <a href="#paths">Compare the four</a></p></div>
<div class="deskstep"><span class="n">4</span><h4>Copy the prompt</h4><p>Tick the suggestions you accept and the page assembles the next build instruction. <a href="#prompt-builder">Build the prompt</a></p></div>
</div>
<h3 id="paths">The four paths</h3>
<div class="pickpath">{paths}</div>
<div class="tablewrap"><table><thead><tr><th>Path</th><th>What you spend</th><th>What can go wrong</th><th>Done when</th></tr></thead><tbody>
{''.join(f'<tr><td><strong>{esc(p["name"])}</strong><br><span class="meta">{esc(p["what"])}</span></td><td>{esc(p["cost"])}</td><td>{esc(p["risk"])}</td><td>{esc(p["done_when"])}</td></tr>' for p in DECISION_PATHS.values())}
</tbody></table></div>
<div class="notice warn"><strong>What no path can promise.</strong> Not one number on this site is a traffic, click, conversion or revenue forecast. The ledger is empty (FLG-028), no endpoint is deployed (FLG-007), and no Search Console property exists (SG-29) — so every “done when” above is a measurement you will take, not a result this page has seen.</div>
"""

def direction_body():
    c = counts()
    cards = ""
    for x in SUGGESTIONS:
        cls = status_pill_class(x["status"])
        detail = x.get("status_detail", "")
        detail_html = f'<p class="why"><span>Status detail</span>{rich(detail)}</p>' if detail else ""
        cards += f"""<article class="sug" id="{esc(x['id'])}">
<header><h3>{esc(x['title'])}</h3>{pill(x['status'], cls)}</header>
<p class="sugmeta">{esc(x['area'])} · {esc(x['id'])} · effort {esc(x['effort'])} ({EFFORT.get(x['effort'], x['effort'])}) · cost: {esc(x['cost'])}</p>
<p class="why"><span>Problem</span>{rich(x['problem'])}</p>
<p class="why"><span>Suggestion</span>{rich(x['proposal'])}</p>
<p class="why"><span>Risk</span>{rich(x['risk'])}</p>
<p class="why"><span>How we would know it worked</span>{rich(x['expected_effect'])}</p>
<p class="why"><span>Evidence</span>{rich(x['evidence'])}</p>
{detail_html}
<details class="promptbox"><summary>Instruction block for the next build prompt</summary>
<pre><code>{esc(x['feeds_prompt'])}</code></pre></details>
</article>"""
    return f"""
<section class="hero"><span class="kicker">Direction · {len(SUGGESTIONS)} suggestions, nothing implemented by surprise</span>
<h1>Read these, choose a path, and the next prompt writes itself</h1>
<p class="lede">Each suggestion states the evidence for it, what it changes, the risk, and how to tell whether it worked. Ticking boxes here changes nothing on the site — it stores your selection in this browser and assembles a copy-paste instruction block for whoever builds next. Implementation only starts after you choose.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · {c['open_sug']} still open, {c['done_sug']} shipped this session</p></section>

<h2 id="suggestions">The register at a glance</h2>
{suggestion_table()}
{decision_desk(c)}

<h2>Recommended sequence</h2>
<p>One build at a time. The order below is the order that keeps the site honest first and productive second.</p>
{suggestion_stages()}

<h2>Choose the next path</h2>
<div class="notice"><strong>How to choose:</strong> pick the path that matches what you want in the next month, not the one that sounds most ambitious. Paths are mutually exclusive for one build. Your choice is stored only in this browser (localStorage); no data leaves the device and nothing is sent anywhere.</div>
<form class="chooser" id="path-chooser">
<label><input type="radio" name="path" value="A"> <strong>Path A — Trust the money path first (recommended).</strong> Run the one-link Associates tests, confirm the tracking ID, keep links gated until they pass. Nothing grows until the click actually attributes.</label>
<label><input type="radio" name="path" value="B"> <strong>Path B — Shop depth.</strong> Extend the decision blocks with per-row source dates, then settle the imagery question (Q-07) and commission licensed photography. Best for conversion.</label>
<label><input type="radio" name="path" value="C"> <strong>Path C — Content volume.</strong> Two guides a week from the published topic backlog plus a seasonal cluster. Best for coverage; worst without measurement, because you will be guessing which topic to write next.</label>
<label><input type="radio" name="path" value="D"> <strong>Path D — Measure first.</strong> Deploy the endpoint and Search Console now, add nothing, and choose the next five topics from 4 weeks of real queries.</label>
<button class="btn" type="submit">Save my choice (this browser only)</button>
<span id="chooser-msg" class="meta"></span>
</form>
<script>
(function(){{var f=document.getElementById('path-chooser');if(!f)return;
function save(){{var v=document.querySelector('input[name=path]:checked');var m=document.getElementById('chooser-msg');
if(!v){{m.textContent='Pick a path first.';return;}}
try{{localStorage.setItem('sk_path',v.value);}}catch(e){{}}
m.textContent='Saved: Path '+v.value+' (this browser only, nothing transmitted).';}}
f.addEventListener('submit',function(e){{e.preventDefault();save();}});
try{{var s=localStorage.getItem('sk_path');if(s){{var r=document.querySelector('input[name=path][value="'+s+'"]');if(r)r.checked=true;}}}}catch(e){{}}}})();
</script>
<h2>The register, one card at a time</h2>
<p>Tick the ones you want, then copy the block at the bottom of the page. Anything marked <em>open-blocked</em> cannot start until the matching question on the <a href="questions.html">open-questions register</a> is answered.</p>
<div class="suglist">{cards}</div>
{prompt_builder()}
"""

def prompt_builder():
    ids = "".join(
        f'<label class="pick"><input type="checkbox" class="sg-pick" value="{esc(x["id"])}" data-title="{esc(x["title"])}" data-prompt="{esc(x["feeds_prompt"])}"> '
        f'<span>{pill(x["id"], status_pill_class(x["status"]))} {esc(x["title"])}</span></label>'
        for x in SUGGESTIONS)
    recommended = [x for x in SUGGESTIONS if x["status"].startswith("recommended") or x["status"].startswith("open") and not x["status"].startswith("open-blocked")]
    rec = "\n".join(f"- {x['feeds_prompt']}" for x in SUGGESTIONS
                    if x["status"].startswith("recommended") or x["id"] in ("SG-02", "SG-08", "SG-10", "SG-13", "SG-09"))
    return f"""<section class="builder" id="prompt-builder">
<h2>Build the next prompt</h2>
<p>Check the suggestions you accept. The list below updates in this browser and is never transmitted. Then paste it into the next build session — it already contains the standing rules (blank over guessed, intended vs observed kept separate, gate must pass before merge).</p>
<div class="picks">{ids}</div>
<label class="pick pick-path">Also apply path: <select id="path-select"><option value="">none</option><option>A</option><option>B</option><option>C</option><option>D</option></select></label>
<h3>Copy this</h3>
<textarea id="prompt-out" rows="14" readonly spellcheck="false">Check the boxes above to fill this in.</textarea>
<button class="btn" type="button" id="prompt-copy">Copy to clipboard</button>
<span id="copy-msg" class="meta"></span>
<h3>If you would rather not choose, this is the recommended set</h3>
<pre><code>{esc(rec)}</code></pre>
<script>
(function(){{
 var out=document.getElementById('prompt-out'), msg=document.getElementById('copy-msg');
 var HEAD="Implement on the ShopNow Kitchen site (repo sassnarep3-star/WinC). Standing rules: read COORDINATION.md and claim tasks before editing; never fill an unverified value \u2014 leave it blank and flag it; keep intended_* and observed_* fields separate; run npm run build && npm run check until green; open a PR to main, merge, and confirm Pages is live.\\n\\nACCEPTED SUGGESTIONS\\n";
 var TAIL="\\n\\nAlso: re-verify anything you touch against an official source and add it to data/sources.json with a retrieval date. Do not add prices, ratings, review counts, or hands-on-testing claims. Every outbound product link keeps rel=sponsored nofollow noopener and the affiliate tag.";
 function fmt(){{var on=[].slice.call(document.querySelectorAll('.sg-pick:checked'));
  var path=document.getElementById('path-select').value;
  if(!on.length&&!path){{out.value="Check the boxes above to fill this in.";return;}}
  var body=on.map(function(c){{return "- ["+c.value+"] "+c.dataset.title+"\\n  → "+c.dataset.prompt;}}).join("\\n");
  if(path){{body=(body?body+"\\n":"")+"- Path "+path+" from direction.html applies to this build.";}}
  out.value=HEAD+(body||"(none)")+TAIL;}}
 document.querySelectorAll('.sg-pick,#path-select').forEach(function(el){{el.addEventListener('change',fmt);}});
 document.getElementById('prompt-copy').addEventListener('click',function(){{
   if(!out.value||out.value.indexOf('Check the boxes')===0){{msg.textContent='Nothing selected yet.';return;}}
   out.select();
   try{{document.execCommand('copy');msg.textContent='Copied.';}}catch(e){{msg.textContent='Select the text and copy manually.';}}}});
 try{{var saved=JSON.parse(localStorage.getItem('sk_sugs')||'[]');
   document.querySelectorAll('.sg-pick').forEach(function(c){{if(saved.indexOf(c.value)>-1)c.checked=true;}});fmt();
   document.querySelectorAll('.sg-pick').forEach(function(c){{c.addEventListener('change',function(){{
     var sel=[].slice.call(document.querySelectorAll('.sg-pick:checked')).map(function(x){{return x.value;}});
     try{{localStorage.setItem('sk_sugs',JSON.stringify(sel));}}catch(e){{}}}});}});
 }}catch(e){{}}
}})();
</script>
</section>"""

# ---------- VERIFICATION ----------
def verification_body():
    # intent record
    intent_rows = []
    for p in PRODUCTS:
        intent_rows.append(
            f"<tr><td><code>{esc(p['submitted_url'])}</code><br><span class='meta'>token {esc(p['submitted_token'])} ({p['token_length']} chars, not linkable on purpose — FLG-003)</span></td>"
            f"<td>{blank(p['intended_asin'])}</td><td>{blank(p['intended_listing_url'])}</td>"
            f"<td>{blank(p['confirmation_date'])}</td><td>{blank(p['intended_source'])}</td>"
            f"<td><strong>{esc(p['observed_asin'])}</strong><br><a href='{esc(p['observed_listing_url'])}' rel='nofollow noopener' target='_blank'>{esc(p['observed_listing_url'])}</a><br><span class='meta'>{esc(p['observed_date'])}</span></td></tr>")
    intent_table = ('<div class="tablewrap"><table><thead><tr><th>Submitted link</th><th>Intended ASIN</th><th>Intended listing URL</th>'
                    '<th>Confirmation date</th><th>Intended source</th><th>Observed redirect target (separate field)</th></tr></thead><tbody>'
                    + "".join(intent_rows) + "</tbody></table></div>"
                    + '<div class="notice warn"><strong>Intent and observation are not the same fact.</strong> Intended fields are blank for all five: a 9-character token is not an ASIN (S05), and nothing public binds a short code to a product. Observed targets come from prior sessions’ live resolutions (S14) + Amazon listings (S09–S13). They are never merged.</div>')

    specs_rows = []
    for p in PRODUCTS:
        specs_rows.append(f"<tr><td>{esc(p['short_label'])}<br><span class='meta'>{esc(p['observed_asin'])}</span></td>"
                          f"<td>{esc(p['brand'])}</td><td>{esc(p['model'])}</td><td>{esc(p['capacity'])}</td>"
                          f"<td>{esc(p['dimensions'] or '— blank')}</td><td>{esc(p['weight'] or '— blank')}</td>"
                          f"<td>{esc(p['temperature'] or '— blank')}</td><td>{esc(p['power'] or '— blank')}</td><td>{esc(p['upc'] or '— blank')}</td>"
                          f"<td>{blank(p['price'])}</td>"
                          f"<td class='src'><a href='{esc(p['source_url'])}' rel='nofollow noopener' target='_blank'>Amazon listing</a><br>{esc(p['source_date'])}</td></tr>")
    specs_table_html = ('<div class="tablewrap"><table><thead><tr><th>Product</th><th>Brand</th><th>Model</th><th>Capacity</th><th>Dimensions</th><th>Weight</th><th>Temp/accuracy</th><th>Power</th><th>UPC</th><th>Price</th><th>Source</th></tr></thead><tbody>'
                        + "".join(specs_rows) + "</tbody></table></div>")

    src_rows = "".join(
        f'<tr id="src-{esc(s["id"])}"><td>{esc(s["id"])}</td><td>{esc(s["title"])}<br>' + (
            f'<code class="src">{esc(s["url"])}</code> <span class="meta">(recorded as text: a short-link redirect hop is not republished — FLG-003)</span>'
            if "link.amazon" in s["url"] else
            f'<a class="src" href="{esc(s["url"])}" rel="nofollow noopener" target="_blank">{esc(s["url"])}</a>')
        + f'</td><td>{esc(s["what"])}</td><td>{esc(s["date"])}</td></tr>'
        for s in SOURCES)
    src_table = ('<div class="tablewrap"><table><thead><tr><th>ID</th><th>Source</th><th>What was verified</th><th>Date</th></tr></thead><tbody>'
                 + src_table_rows(src_rows) + "</tbody></table></div>")

    trace_rows = [
        ("Read like a shop, not an audit", "Front page leads with 5 product cards; verification below the fold", "index.html"),
        ("Findable (one site to index)", "Sitemap, RSS, canonicals, JSON-LD, internal search", "sitemap.xml, feed.xml, search.html"),
        ("Disclosure above the fold, every page", "Strip under masthead + footer repeat + per-link Sponsored label", "all pages (gate-checked)"),
        ("Every outbound product link sponsored", "rel=sponsored nofollow + Sponsored tag + data-event", "all product links (gate-checked)"),
        ("Product-intent record (separate fields)", "Intended blank; observed populated; never merged", "this page"),
        ("Validated Special Links (one-link test)", "Constructed links pending Associates test (FLG-002); short links not claimed invalid (FLG-003)", "flagged-for-review.html"),
        ("Question-shaped guides + measure", f"{len(GUIDES)} guides published; {len(TOPICS)} topics queued; 5 events defined; ledger empty", "guides/, topics.html, measurement.html"),
        ("Click/conversion measurement first", "Beacon + Worker code; local-only until deployed (FLG-007)", "assets/app.js, analytics/"),
        ("Campaign ledger (evidence-based)", "Empty, well-defined; first-party reports only", "measurement.html"),
        ("Compliance gate in workflow", "scripts/check_site.py fails on disclosure/sponsored/price/sitemap violations", "scripts/check_site.py"),
        ("Publication polish (authorship, seasons, clusters)", "Kitchen Desk byline, season/cluster labels, RSS/Search Console/reader capture status", "about.html"),
        ("Suggestions + Q&A before decisions", f"Direction page with a reviewable table, a staged path and a prompt builder + {len(QUESTIONS)}-row Q&A table", "direction.html, questions.html"),
        ("Lead with the products, not the process", "Front page order: hero, shop, guides, categories, one method line; every dashboard surface in the footer and one nav group", "index.html"),
        ("Decision support, no ranking", f"{sum(len(v.get('profiles', [])) for v in CATEGORY_PROFILES.values())} reader situations, each naming the one listed spec it rests on", "air-fryers.html, thermometers.html, data/categories.json"),
        ("Topic pipeline visible", f"{len(TOPICS)} planned topics, each stating how it was chosen (hypothesis or measured query)", "topics.html"),
        ("Executive summary", "Summary + counts + next steps", "executive-summary.html"),
    ]
    trace = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class='src'>{esc(c)}</td></tr>" for a, b, c in trace_rows)
    trace_table = ('<div class="tablewrap"><table><thead><tr><th>Requirement</th><th>Where addressed</th><th>File</th></tr></thead><tbody>'
                   + trace + "</tbody></table></div>")

    return f"""
<section class="hero"><span class="kicker">Verification · Source register</span>
<h1>Verification: every row has a source, or it is blank</h1>
<p class="lede">Line-by-line checks against official sources. If a value cannot be confirmed from an official source, the cell is blank and flagged. Nothing is inferred.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>

<h2>1 · Product-intent confirmation record</h2>
<p>For each submitted link: intended ASIN, official listing URL, confirmation date, and source — kept in separate fields from the observed redirect target. <strong>Do not merge the two.</strong> Rationale: Amazon defines an ASIN as a 10-character code (S05); the submitted tokens are 9 characters, so they cannot be ASINs.</p>
{intent_table}

<h2>2 · Product specs (Amazon listings)</h2>
{specs_table_html}
<p class="src">Prices and ratings are blank per Program Policies (S02) and volatility (FLG-006). Dimensions/weight/temp/power/UPC are as listed on Amazon on {TODAY} — re-check on Amazon before buying.</p>

<h2>3 · Source register (official sources)</h2>
{src_table}

<h2>4 · Requirements trace</h2>
{trace_table}
{capture_block()}
"""

def src_table_rows(rows):
    return rows

# ---------- FLAGGED ----------
def flag_sources(f):
    """Official sources cited by a flag, linked into the source register."""
    ids = f.get("sources") or []
    if not ids:
        return '<span class="meta">' + esc(f.get("source_note") or "Internal only — no external source applies.") + "</span>"
    links = " ".join(
        f'<a href="verification.html#src-{sid}">{sid}</a>' for sid in ids if sid in SRC)
    extra = " ".join(f'<a href="{esc(u)}" rel="nofollow noopener" target="_blank">{esc(u)}</a>'
                     for u in f.get("source_urls") or [])
    return (links + " " + extra).strip()

def flagged_body():
    rows = "".join(
        f"<tr><td><strong>{esc(f['id'])}</strong></td><td>{esc(f['title'])}</td><td>{esc(f['detail'])}</td>"
        f"<td>{esc(f['action'])}</td><td>{flag_sources(f)}</td>"
        f"<td><span class='flagpill'>{esc(f['status'])}</span></td></tr>"
        for f in FLAGS)
    return f"""
<section class="hero"><span class="kicker">Flagged for Review · Needs review</span>
<h1>Flagged for Review: what we could not verify</h1>
<p class="lede">These items do not block the site. They are published here so you can review them after the site is live and request changes. Nothing flagged is presented as fact elsewhere.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<div class="tablewrap"><table><thead><tr><th>ID</th><th>Issue</th><th>Detail</th><th>Action to resolve</th><th>Official sources</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="notice"><strong>What “needs review” means:</strong> the site works without these answers, but the flagged facts stay blank or pending until the action is done. Request changes via the <a href="direction.html">Direction</a> page or a new issue.</div>
{capture_block()}
"""

# ---------- DISCLOSURE ----------
def disclosure_body():
    return f"""
<section class="hero"><span class="kicker">Disclosure &amp; privacy</span>
<h1>Disclosure: how this site earns money</h1>
<p class="lede">Plain language, above the fold, on every page — because you should not have to hunt for it.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<div class="notice"><strong>As an Amazon Associate I earn from qualifying purchases.</strong> When you click a link marked <span class="sponsored-tag">Sponsored</span> and buy on Amazon, this site may earn a commission at no extra cost to you. This statement appears under the masthead on every page and again in the footer (Operating Agreement §5, S01; link-level disclosure per S07; FTC clear-and-conspicuous standard, S03).</div>
<h2>What this means</h2>
<ul>
<li><strong>Sponsored links:</strong> every outbound product link carries <code>rel="sponsored nofollow"</code> (Google, S04) and a visible Sponsored label.</li>
<li><strong>Prices:</strong> this site does not display prices. Prices and availability are shown on Amazon (Program Policies, S02). “Check price on Amazon” is the only price action.</li>
<li><strong>No endorsement:</strong> an affiliate relationship does not mean Amazon endorses this site or its content.</li>
<li><strong>Original content:</strong> guides and comparisons are original. Amazon product descriptions are never copied.</li>
<li><strong>Privacy:</strong> no cookies, no fingerprinting, no email storage on this static site. Measurement counts aggregates only (see <a href="measurement.html">Measurement</a>). Reader-capture emails are handled by the email provider you choose.</li>
</ul>
<h2>Compliance gate</h2>
<p>Every build runs <code>scripts/check_site.py</code>, which fails if: any page lacks the disclosure strip, any product link lacks <code>rel="sponsored"</code> or the Sponsored label, any price is rendered, or the sitemap is incomplete. The gate is the publishing workflow — not a suggestion.</p>
<h2>Sources</h2>
<ul>
<li><a href="https://affiliate-program.amazon.com/help/operating/agreement" rel="nofollow noopener" target="_blank">Operating Agreement (S01)</a></li>
<li><a href="https://affiliate-program.amazon.com/help/operating/policies" rel="nofollow noopener" target="_blank">Program Policies (S02)</a></li>
<li><a href="https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking" rel="nofollow noopener" target="_blank">FTC Endorsement Guides (S03)</a></li>
<li><a href="https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links" rel="nofollow noopener" target="_blank">Google rel=sponsored (S04)</a></li>
</ul>
{capture_block()}
"""

# ---------- MEASUREMENT ----------
def ledger_rows_html():
    rows = LEDGER.get("rows", [])
    if not rows:
        return '<tr><td colspan="7"><span class="blank">— no rows yet (ledger is empty until first-party data arrives)</span></td></tr>'
    out = []
    for r in rows:
        cells = [r.get("timestamp"), r.get("source"), r.get("channel"), r.get("eligible_sessions"),
                 r.get("clicks"), r.get("reported_orders"), r.get("provenance")]
        tds = "".join("<td>%s</td>" % (esc(str(c)) if c not in (None, "") else '<span class="blank">—</span>') for c in cells)
        out.append("<tr>%s</tr>" % tds)
    return "\n".join(out)

def measurement_body():
    return f"""
<section class="hero"><span class="kicker">Measurement · Evidence-based iteration</span>
<h1>Measurement: clicks and conversions, counted honestly</h1>
<p class="lede">A privacy-preserving outbound-click counter and a self-hosted endpoint record five defined events. The campaign ledger starts empty — it fills only from authorized first-party reports. No conversion score. No revenue forecast.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>

<h2>The five defined events</h2>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Event</th><th>When it fires</th><th>What is stored</th><th>What is never stored</th></tr></thead><tbody>
<tr><td>1</td><td><code>page_view</code></td><td>Once per page load</td><td>Day + page (aggregate)</td><td>IP, user agent, cookies</td></tr>
<tr><td>2</td><td><code>outbound_click</code></td><td>Click on a Sponsored Amazon link</td><td>Day + page + observed ASIN</td><td>Identity, full URL, query</td></tr>
<tr><td>3</td><td><code>guide_read</code></td><td>Reader reaches 50%+ on a guide</td><td>Day + page + depth bucket</td><td>Reading content, identity</td></tr>
<tr><td>4</td><td><code>reader_capture_submit</code></td><td>Newsletter form submitted</td><td>Day + page count</td><td>Email address (provider handles it)</td></tr>
<tr><td>5</td><td><code>search_submit</code></td><td>Internal search submitted</td><td>Day + page count</td><td>Search query text</td></tr>
</tbody></table></div>
<p>Client: <code>assets/app.js</code> · Endpoint code: <code>analytics/worker.js</code> (deploy separately — GitHub Pages is static, FLG-007). Until <code>CONFIG.endpoint</code> is set, counts live only in the reader’s browser (localStorage).</p>

<h2>Campaign ledger (empty by design)</h2>
<p>Timestamp, source, channel, eligible sessions, clicks, and reported orders are recorded <strong>only</strong> when obtained from authorized first-party reports (Associates Reports). Keep a dated provenance trail. No conversion score or revenue forecast is presented here.</p>
<div class="tablewrap"><table><thead><tr><th>Timestamp</th><th>Source</th><th>Channel</th><th>Eligible sessions</th><th>Clicks</th><th>Reported orders</th><th>Provenance</th></tr></thead><tbody>
{ledger_rows_html()}
</tbody></table></div>
<p class="meta">Source file: <a href="https://github.com/sassnarep3-star/WinC/blob/main/data/campaign-ledger.json">data/campaign-ledger.json</a> · rows: {len(LEDGER.get("rows", []))} · provenance entries: {len(LEDGER.get("provenance_trail", []))}</p>

<h2>Findability status (SG-27..SG-30)</h2>
<div class="tablewrap"><table><thead><tr><th>Item</th><th>Status</th><th>Evidence</th></tr></thead><tbody>
<tr><td>Nav labels (SG-27)</td><td><span class="okpill">shipped</span></td><td>Single navigation group on every page</td></tr>
<tr><td>RSS feed (SG-28)</td><td><span class="okpill">shipped</span></td><td><a href="feed.xml">feed.xml</a> lists all guides + products</td></tr>
<tr><td>Search Console (SG-29)</td><td><span class="flagpill">pending</span></td><td>Sitemap ready at <a href="sitemap.xml">sitemap.xml</a>; submit in Search Console, then record date here</td></tr>
<tr><td>Reader capture (SG-30)</td><td><span class="warnpill">partial — no list behind it</span></td><td>Form renders on front page + guides; records a local count only. No list, no provider, no confirmed-opt-in flow yet — see FLG-013</td></tr>
<tr><td>Structured data</td><td><span class="okpill">shipped, with one honest caveat</span></td><td>Article, BreadcrumbList and ItemList JSON-LD are emitted and valid. FAQPage markup is still emitted for machine readability, but Google removed the FAQ rich-result feature in June 2026 (<a href="verification.html#src-S35">S35</a>) — this site does not count it as a rich-snippet win.</td></tr>
<tr><td>Internal search</td><td><span class="okpill">shipped</span></td><td><a href="search.html">search.html</a> (client-side, no server)</td></tr>
</tbody></table></div>
{capture_block()}
"""

# ---------- ABOUT ----------
def about_body():
    c = counts()
    return f"""
<section class="hero"><span class="kicker">About · Authorship &amp; method</span>
<h1>About ShopNow Kitchen: a publication, with its workings visible</h1>
<p class="lede">We compare countertop appliances on checkable specs and human buyer questions. Here is who writes, how we check, what “published” means here, and what we refuse to claim.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<h2>Authorship</h2>
<p>Every page is bylined <strong>the ShopNow Kitchen Desk</strong> — an editorial desk, not a person. We do not invent a name, credentials, a test kitchen, or hands-on experience. If we ever test something, the page will say what was tested, when, and what was observed. Until then we compare manufacturer and listing specs and say exactly that.</p>
<div class="notice"><strong>This is a decision, not a gap.</strong> A named expert byline would help readers and search engines judge us — but only if it is real. See <a href="questions.html">Q-06</a> and <a href="direction.html">SG-09</a>: supply one human name and bio and the site will use it; otherwise the desk byline stays and so does the “no testing claimed” rule.</div>
<h2>Methodology</h2>
<ol>
<li>Start from the submitted link; record intent and observation in <strong>separate fields, never merged</strong>.</li>
<li>Read the official source for every claim: the listing for a spec, the regulator for a safety figure, the programme agreement for a rule.</li>
<li>If a value cannot be confirmed, the cell stays blank and the item is flagged. Nothing is inferred, averaged or “best guessed”.</li>
<li>Every page passes a compliance gate before publish (<code>scripts/check_site.py</code>): disclosure present, paid links qualified, no static prices, no broken internal links, sitemap coverage complete.</li>
<li>Measure with the five defined events; fill the campaign ledger only from first-party reports, with a date attached.</li>
</ol>
<h2>Brand, seasons, and clusters</h2>
<ul>
<li><strong>Brand:</strong> ShopNow Kitchen — warm paper, ink text, terracotta and sage. Typography and whitespace, not badges and countdown timers.</li>
<li><strong>Imagery:</strong> commissioned editorial illustrations, always captioned as illustrations. No Amazon product images and no logos — the IP licence restricts them, and a scraped photo would promise a product we have not seen.</li>
<li><strong>Seasons:</strong> currently “Holiday cooking” alongside everyday cooking; grilling and holiday-baking angles run as guides, not as banners that expire on the server.</li>
<li><strong>Clusters (computed from data, so this cannot drift):</strong> {esc(cluster_sentence())}.</li>
</ul>
<h2>How a reader makes the decision</h2>
<p>Every category page opens with reader situations — “two of you, most weeknights” — and answers them by naming the one listed spec that settles the case, with the listing linked. No profile ranks a product best, and no profile reaches past a listed specification. Product pages add what the listing says, where the listing contradicts itself, and the questions readers actually ask, each with its source.</p>
<h2>Publishing cadence</h2>
<p>A new guide is one JSON file in <code>data/guides/</code>, then <code>npm run build</code>. Sitemap, RSS, the search index, this page’s cluster counts and every nav rail pick it up from the same source — no hand-edited lists. The next topic should come from measured queries rather than instinct, which is why <a href="measurement.html">measurement</a> is wired even while it records nothing yet. Every planned topic and how it was chosen is published on the <a href="topics.html">topics page</a>, so the editorial pipeline is visible rather than implied.</p>
<h2>Corrections</h2>
<p>If a row on this site is wrong, that is a defect, not a difference of opinion. Flagged items are published on <a href="flagged-for-review.html">Flagged for review</a> with the source link and the action that would settle them; we would rather show an open question than fill it with a guess.</p>
{capture_block()}
"""

# ---------- EXEC SUMMARY ----------
def exec_body():
    c = counts()
    total_pages = 4 + len(CATEGORIES) + len(PRODUCTS) + len(GUIDES) + len(NAV_DESK)
    return f"""
<section class="hero"><span class="kicker">Executive summary · for the owner, not for readers</span>
<h1>Executive summary: {c['products']} products, {c['guides']} guides, {c['flags']} flags, nothing invented</h1>
<p class="lede">ShopNow Kitchen is a publication front page over an evidence ledger. It leads with products and buyer questions; verification sits one click away instead of in the way. Every number below is computed from the repo, not typed by hand, so this page cannot go stale without the data going stale first.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · full text in <code>EXECUTIVE-SUMMARY.md</code></p></section>

<h2>What is live</h2>
<div class="tablewrap"><table><thead><tr><th>Layer</th><th>State</th><th>Where</th></tr></thead><tbody>
<tr><td>Shop</td><td>{c['products']} product pages, {len(CATEGORIES)} category pages, 1 shop index, each with a decision block or a decision shortcut</td><td><a href="products/index.html">The shop</a></td></tr>
<tr><td>Editorial</td><td>{c['guides']} question-shaped guides, {c['topics']} planned topics, {c['profiles']} reader situations that name their deciding spec</td><td><a href="guides/index.html">Guides</a> · <a href="topics.html">Topics</a></td></tr>
<tr><td>Trust</td><td>{c['sources']} sources, {c['flags']} flagged items, intended vs observed kept in separate fields</td><td><a href="verification.html">Verification</a> · <a href="flagged-for-review.html">Flagged</a></td></tr>
<tr><td>Decisions</td><td>{len(SUGGESTIONS)} suggestions ({c['open_sug']} open) + {c['questions']} questions, {c['blocking']} blocking</td><td><a href="direction.html">Suggestions</a> · <a href="questions.html">Open questions</a></td></tr>
<tr><td>Measurement</td><td>5 events defined, beacon shipped, endpoint <strong>not deployed</strong>, ledger empty by design</td><td><a href="measurement.html">Measurement</a></td></tr>
<tr><td>Findability</td><td>{total_pages} pages in the sitemap, RSS, canonicals, Article + FAQ + Breadcrumb schema, robots scoping internals out</td><td><code>sitemap.xml</code></td></tr>
</tbody></table></div>

<h2>The five links, in one table</h2>
<div class="tablewrap"><table><thead><tr><th>Supplied</th><th>Token length</th><th>Valid ASIN?</th><th>Observed destination</th><th>Intended ASIN</th></tr></thead><tbody>
{"".join(f"<tr><td><code>{esc(p['submitted_token'])}</code></td><td>{p['token_length']}</td><td>No — 10 characters required (S05)</td><td><strong>{esc(p['observed_asin'])}</strong></td><td>{blank(p['intended_asin'])}</td></tr>" for p in PRODUCTS)}
</tbody></table></div>
<p class="src">Observed live three times (2026-11-17, and twice on 2026-11-20 by sessions arena-23d7ed19 and arena-82d39deb): 5/5 destinations identical every time, and every final URL carried <code>lv=shuf</code> + <code>plpRedirect=mhFallback</code> — a fallback route, so “observed” is not “intended” (FLG-009). Log: <a href="verification.html#probes">Verification §4</a>.</p>

<h2>What the latest verification pass changed</h2>
<div class="tablewrap"><table><thead><tr><th>Finding</th><th>What changed</th><th>Where</th></tr></thead><tbody>
<tr><td>One spec row was wrong</td><td>The 8-quart Chefman was recorded at 1700 W / 120 V. Its live bullet reads “1000 Watts/120 Volts – RJ38-SQSS-8T” — 1700 W is the 6-quart model's number. Corrected, and the earlier capture kept beside it.</td><td>FLG-019, <a href="verification.html">Verification</a></td></tr>
<tr><td>Four listing-internal contradictions confirmed live</td><td>8-Qt temperature (title 450°F vs bullets 200–400°F) · Emeril accessory count (title 6 vs bullets 7) · Emeril preset count (title 24 vs bullets 25) · 6-Qt capacity unit (details “6 liters” vs title “6 quart”)</td><td>FLG-005, FLG-010, FLG-015, FLG-017</td></tr>
<tr><td>One Amazon product-name string differs from the earlier capture</td><td>B08DKYBTPH serves “TurboFry 4-in-1 … 450°F Hi-Fry” now and a different name string earlier. Both are stored; the live one is displayed.</td><td>FLG-016</td></tr>
<tr><td>Two buyer-relevant facts found in the live pages</td><td>The 8-Qt ASIN is a 6/8/9-quart size family, and Amazon's own page states there is a newer model of that item. Both are now on the product page.</td><td>FLG-020, FLG-021</td></tr>
</tbody></table></div>

<h2>What has to happen before any of this earns anything</h2>
<ol>
<li>Confirm the tracking ID and one test link per product in Associates Central (FLG-001, FLG-002, Q-01, Q-16).</li>
<li>Confirm intent for the five products with whoever supplied them (Q-02) — do not infer it from a redirect.</li>
<li>Deploy the metrics endpoint, then pick topics from Search Console queries rather than taste (SG-07, SG-08).</li>
<li>Settle the spec conflicts on the manufacturer page, not on Amazon marketing copy (FLG-005, FLG-010, Q-05, Q-19).</li>
<li>Decide the audience, the marketplace and what “working” means (Q-10, Q-17, SG-20) — before more content is written, not after.</li>
</ol>
<div class="notice"><strong>No revenue forecast, no conversion score, no traffic projection.</strong> There is no first-party data yet, so any number here would be fiction. The ledger stays empty until authorised reports arrive — that is the honest starting point, and it is also what makes the first real number meaningful.</div>
{capture_block()}
"""

# ---------- SEARCH ----------
def search_body():
    return f"""
<section class="hero"><span class="kicker">Search</span>
<h1>Search the shop</h1>
<p class="lede">Client-side search across products and guides. No server, no query tracking (only a <code>search_submit</code> count).</p></section>
<form class="searchbox" id="site-search" action="search.html" method="get">
<input type="search" name="q" id="q" placeholder="Try “dual basket”, “thermometer”, “capacity”…" aria-label="Search">
<button class="btn" type="submit">Search</button>
</form>
<div id="results"></div>
<script>
var INDEX=null;
fetch('assets/search-index.json').then(function(r){{return r.json();}}).then(function(d){{INDEX=d;run();}});
function run(){{
  var q=(new URLSearchParams(location.search).get('q')||'').toLowerCase().trim();
  var box=document.getElementById('results');
  if(!q){{box.innerHTML='<p class="meta">Type a query above.</p>';return;}}
  var hits=INDEX.filter(function(x){{return (x.title+' '+x.text).toLowerCase().indexOf(q)>-1;}});
  if(!hits.length){{box.innerHTML='<p>No matches for <strong>'+q+'</strong>. Try “air fryer” or “thermometer”.</p>';return;}}
  box.textContent='';
  var note=document.createElement('p'); note.className='meta';
  note.textContent=hits.length+' result(s) for “'+q+'”'; box.appendChild(note);
  var grid=document.createElement('div'); grid.className='grid';
  hits.forEach(function(h){{
    var art=document.createElement('article'); art.className='card';
    var cat=document.createElement('span'); cat.className='cat'; cat.textContent=h.kind;
    var h3=document.createElement('h3'); var a=document.createElement('a'); a.href=h.url; a.textContent=h.title; h3.appendChild(a);
    var p2=document.createElement('p'); p2.textContent=h.text.slice(0,180)+'…';
    art.appendChild(cat); art.appendChild(h3); art.appendChild(p2); grid.appendChild(art);
  }});
  box.appendChild(grid);
}}
</script>
"""

def notfound_body():
    return """
<section class="hero"><span class="kicker">Not found</span>
<h1>That page is not on the counter.</h1>
<p class="lede">Try the <a href="index.html">front page</a> or <a href="search.html">search</a>.</p></section>
"""

# ---------- INDEX & REGISTER PAGES ----------
def guides_index_body():
    pfx = "../"
    by_cat = {}
    for g in GUIDES:
        by_cat.setdefault(g.get("category", "Other"), []).append(g)
    secs = ""
    for cat, href in CATEGORIES:
        gs = by_cat.pop(cat, [])
        if not gs:
            continue
        secs += (f'<h2 id="{esc(cat.lower().replace(" ", "-"))}">{esc(cat)}</h2>'
                 f'<p class="seclink"><a href="{pfx}{href}">Browse all {esc(cat)} →</a></p>'
                 f'<div class="grid">' + "".join(guide_card(g, depth=1) for g in gs) + "</div>")
    for cat, gs in by_cat.items():
        secs += f'<h2>{esc(cat)}</h2><div class="grid">' + "".join(guide_card(g, depth=1) for g in gs) + "</div>"
    return f"""
<section class="hero"><span class="kicker">Guides · {counts()['guides']} published</span>
<h1>Guides: questions worth asking before you spend</h1>
<p class="lede">Every guide here is question-shaped on purpose. Nobody shops at 9pm for “brand X review”; they search the thing they are actually unsure about — does a dual basket beat one big one, how many quarts feed a family of four, whether a probe can live in the oven.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · <a href="{pfx}feed.xml">RSS</a> · <a href="{pfx}sitemap.xml">Sitemap</a></p></section>
<div class="notice"><strong>What these pages are not:</strong> not reviews, not “we tested it”, not rankings. They are structured comparisons of published specifications plus the food-safety figures regulators actually publish, with the source of every number one click away.</div>
{secs}
<h2>Cadence</h2>
<p>One JSON file in <code>data/guides/</code> plus <code>python3 scripts/new_guide.py &amp;&amp; python3 scripts/build_site.py</code> publishes a guide: this index, the front-page rail, the sitemap, the RSS feed, the search index and the About page’s cluster counts all read the same source — no hand-maintained list anywhere.</p>
<p class="seclink"><a class="btn btn-quiet" href="{pfx}direction.html">Suggest the next topic →</a> <a class="btn btn-quiet" href="{pfx}questions.html">Questions we still need answered →</a></p>
{capture_block(depth=1)}
"""

def products_index_body():
    pfx = "../"
    rows = ""
    for x in PRODUCTS:
        best_for = x.get("best_for") or ""
        best_cell = esc(best_for) if best_for else '<span class="blank">— blank (unverified)</span>'
        rows += (f'<tr><td><a href="{pfx}{esc(x["page"])}">{esc(x["short_label"])}</a><br><span class="meta">{esc(x["brand"])}</span></td>'
                 f'<td>{esc(x["category"])}</td>'
                 f'<td>{best_cell}</td>'
                 f'<td>{blank(x["capacity"] if x["capacity"] != "—" else "")}</td>'
                 f'<td>{blank(x["dimensions"])}</td><td>{blank(x["weight"])}</td><td>{blank(x["model"])}</td>'
                 f'<td>{blank(x["temperature"])}</td><td>{blank(x["power"])}</td>'
                 f'<td>{blank(x["price"])}</td><td>{blank(x["rating"])}</td>'
                 f'<td class="src">{source_link(x["source_url"], "Listing")} <span class="meta">{esc(x["source_date"])}</span></td></tr>')
    cards = "".join(product_card(x, depth=1) for x in PRODUCTS)
    return f"""
<section class="hero"><span class="kicker">The shop · {counts()['products']} products</span>
<h1>Everything in the shop, in one table</h1>
<p class="lede">Three air fryers, two thermometers. This is the honest version of a shop window: what the listing states, where we read it, and which cells we will not fill in for you.</p>
<p class="meta">By the ShopNow Kitchen Desk · Specs read {TODAY} · <a href="{pfx}verification.html">Verification</a></p></section>
{house_ad(depth=1)}
<div class="tablewrap"><table><thead><tr><th>Product</th><th>Category</th><th>Best for</th><th>Capacity</th><th>Footprint</th><th>Weight</th><th>Model</th><th>Temperature</th><th>Power</th><th>Price</th><th>Rating</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="legend"><strong>Reading the blanks:</strong> <code>—</code> means the field does not apply to that product type (a thermometer has no wattage). <span class="blank">— blank (unverified)</span> means we looked and could not confirm it, so we left it empty rather than estimate it. Both are answers; a guess would not be.</p>
<div class="notice"><strong>The price and rating columns are blank by policy, not by accident.</strong> Amazon’s Program Policies bar static price display, and ratings move daily — either number would be stale the moment it was written. The button on each card takes you to the listing, where the live figure is. See <a href="{pfx}flagged-for-review.html">FLG-006</a>.</div>
<h2>Cards</h2>
<div class="grid">{cards}</div>
<h2>How these five got here</h2>
<p>Each product entered the shop as a <code>link.amazon</code> short link rather than a listing URL. We recorded the token we were given, resolved it, and stored what came back in a separate field — because the response was a fallback route, not a canonical match. The raw redirects, the date, and what that does and does not prove are in <a href="{pfx}verification.html#probes">§4 of the verification register</a> and in <code>data/probes.json</code>.</p>
<p class="seclink"><a class="btn btn-quiet" href="{pfx}executive-summary.html">Read the executive summary →</a></p>
{capture_block(depth=1)}
"""

def question_sources(q):
    ids = q.get("sources") or []
    if not ids:
        return '<span class="meta">' + esc(q.get("source_note") or "Internal only — no external source applies.") + "</span>"
    return " ".join(f'<a href="verification.html#src-{sid}">{sid}</a>' for sid in ids if sid in SRC)

ANSWER_STATE = {
    "answered": ("answered", "ok"),
    "partly": ("partly answered", "act"),
    "open": ("still open", "wait"),
}

def answer_cell(q):
    """Render one answer cell: the state, the answer, and where the answer rests.

    An answer with no state is a claim nobody has sourced, so it stays blank. An answer
    that is not 'open' carries the date it was answered and either the source ids it
    rests on or a note saying it rests on this repository's own records — the gate in
    scripts/check_site.py refuses an answer that has neither.
    """
    state = q.get("answer_state")
    if not state:
        return blank(q.get("answer"))
    label, kind = ANSWER_STATE.get(state, (state, "note"))
    out = [pill(label, kind)]
    answer = (q.get("answer") or "").strip()
    if answer:
        out.append(f'<p class="answertxt">{esc(answer)}</p>')
    meta = []
    if q.get("answered_on"):
        meta.append(f'answered {esc(q["answered_on"])}')
    froms = q.get("answered_from") or []
    if froms:
        links = " ".join(
            f'<a href="verification.html#src-{esc(sid)}">{esc(sid)}</a>'
            for sid in froms if sid in SRC)
        if links:
            meta.append(f"rests on {links}")
    elif q.get("answered_from_note"):
        meta.append("rests on this repository’s own records")
    if meta:
        out.append(f'<p class="meta">{" · ".join(meta)}</p>')
    return "".join(out)

def answer_provenance(q):
    """The source column for a panel row: the source ids, or the internal-evidence note.

    A row that cannot name where its answer comes from would be a claim, so it says so
    in the row rather than in a footnote nobody reads.
    """
    froms = q.get("answered_from") or []
    if froms:
        links = " ".join(
            f'<a href="verification.html#src-{esc(sid)}">{esc(sid)}</a>'
            for sid in froms if sid in SRC)
        if links:
            return links
    if q.get("answered_from_note"):
        return '<span class="meta">Internal only — no external source applies.</span>'
    return '<span class="meta">Internal only — no external source applies.</span>'

def questions_body():
    c = counts()
    rows = ""
    for q in QUESTIONS:
        bl = q.get("blocking", "no")
        kind = "act" if bl.startswith("yes") else "note"
        rows += (f'<tr><td><strong>{esc(q["id"])}</strong><br>{pill("blocking" if bl.startswith("yes") else "non-blocking", kind)}</td>'
                 f'<td><strong>{esc(q["question"])}</strong><p class="meta">Gates: {esc(q["decision_it_gates"])}</p></td>'
                 f'<td>{link_source_ids(esc(q["have"]))}</td><td>{esc(q["missing"])}</td><td>{esc(q["discovery"])}</td>'
                 f'<td>{esc(q["owner"])}</td><td>{question_sources(q)}<br><span class="meta">Internal only — no external source applies.</span></td>'
                 f'<td class="answercell">{answer_cell(q)}</td></tr>')
    # The panel a reviewer reads first: what is settled enough to act on, and what is still
    # waiting on an account this environment cannot reach.
    settled = [q for q in QUESTIONS if q.get("answer_state") in ("answered", "partly")]
    still_open = [q for q in QUESTIONS if q.get("answer_state") == "open"]
    decidable = [q for q in settled if not q.get("blocking", "no").startswith("yes")]
    decide_rows = "".join(
        f'<tr><td><strong>{esc(q["id"])}</strong></td><td>{esc(q["question"])}</td>'
        f'<td>{esc(q.get("answer") or "")}</td>'
        f'<td>{answer_provenance(q)}</td></tr>' for q in decidable)
    open_rows = "".join(
        f'<tr><td><strong>{esc(q["id"])}</strong></td><td>{esc(q["question"])}</td>'
        f'<td>{esc(q.get("owner") or "")}</td><td>{esc(q.get("discovery") or "")}</td>'
        f'<td><span class="meta">Internal only — no external source applies.</span></td></tr>'
        for q in still_open)
    pack = "\n\n".join(f'{q["id"]}. {q["question"]}\nWhat we need: {q["missing"]}\nHow to get it: {q["discovery"]}'
                        for q in QUESTIONS if q.get("blocking", "no").startswith("yes"))
    return f"""
<section class="hero"><span class="kicker">Open questions · {c['questions']} rows, {c['blocking']} blocking</span>
<h1>What has to be answered before the next decision is reasonable</h1>
<p class="lede">Not a to-do list — a register. Each row states what we already know and can cite, what is genuinely missing, which decision that gap blocks, and the concrete action that produces the answer. Every row also carries an answer state: what is settled, what is only partly settled, and what is still open.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · evidence in <a href="verification.html">the source register</a>, consequences in <a href="flagged-for-review.html">Flagged for review</a></p></section>
<div class="notice"><strong>Read it this way:</strong> the {c['blocking']} blocking rows are worth more than any content decision. Four of them — Q-01, Q-02, Q-04 and Q-16 — can only be answered inside an enrolled Amazon Associates account, which this environment cannot reach. That is a fact about the tooling, not an excuse, and it is why the site ships with links gated rather than links guessed. When you have an answer, paste it into <code>answer</code> in <code>data/questions.json</code>: the table updates on the next build, and the matching flag closes.</div>
<h2>Decisions you can make now</h2>
<p>{len(decidable)} of the {c['questions']} rows are answered well enough to act on without waiting for the account owner. Each answer below is dated and names the source it rests on, so a reviewer can check it rather than take it on trust.</p>
<div class="tablewrap"><table><thead><tr><th>ID</th><th>Question</th><th>Answer</th><th>What it rests on</th></tr></thead><tbody>{decide_rows}</tbody></table></div>
<h2>Still open</h2>
<p>{len(still_open)} row(s) remain unanswered, and each says who can answer and how to find out. These are the gaps the register exists to expose — an open row is a real answer, not an omission.</p>
<div class="tablewrap"><table><thead><tr><th>ID</th><th>Question</th><th>Who can answer</th><th>How to discover it</th><th>Source</th></tr></thead><tbody>{open_rows}</tbody></table></div>
<div class="tablewrap"><table class="qtable"><thead><tr><th>ID</th><th>Question</th><th>What we have (and its source)</th><th>What we do not have</th><th>How to discover it</th><th>Who can answer</th><th>Official sources</th><th>Answer</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Before you publish anything else: the checklist</h2>
<p>Seven things a publisher usually settles before the eighth guide. Each row says why it matters here, what this repo already has, and where the answer has to come from. None of them is a technical task, which is exactly why they keep getting deferred behind the next article.</p>
<div class="tablewrap"><table><thead><tr><th>#</th><th>What to settle</th><th>Why it decides something</th><th>What the repo has today</th><th>Where the answer lives</th></tr></thead><tbody>
<tr><td>1</td><td>Tracking ID issued and active</td><td>Without it, no click can attribute to this site and every buy button is decoration</td><td>A well-formed string; nothing confirms issuance</td><td><a href="verification.html">Q-01</a> · <a href="https://affiliate-program.amazon.com/help/node/topic/GM6CHU93RDXZV7D8" rel="nofollow noopener" target="_blank">Associates ID help (S20)</a></td></tr>
<tr><td>2</td><td>One link tested through the enrolled workflow</td><td>A tagged link that was never tested can point somewhere unintended and still look correct</td><td>Observed destinations recorded for all five; none tested in the workflow</td><td><a href="verification.html">FLG-002</a> · <a href="https://affiliate-program.amazon.com/help/operating/policies" rel="nofollow noopener" target="_blank">Program Policies §2(b) (S02)</a></td></tr>
<tr><td>3</td><td>The disclosure sentence in place on every page</td><td>Operating Agreement §5 makes it a material term; FTC treats a buried disclosure as no disclosure</td><td>Shipped: strip under the masthead, repeat in the footer, per-link label</td><td><a href="https://affiliate-program.amazon.com/help/operating/agreement" rel="nofollow noopener" target="_blank">Agreement §5 (S01)</a> · <a href="https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking" rel="nofollow noopener" target="_blank">FTC guides (S03)</a></td></tr>
<tr><td>4</td><td>Which site tree is canonical</td><td>Two published trees means two sitemaps, split signals, and a crawler that has to guess</td><td>Repo root is published; three other trees sit in open PRs</td><td><a href="questions.html">Q-23</a> · <a href="direction.html#SG-35">SG-35</a><br><span class="meta">Internal only — no external source applies.</span></td></tr>
<tr><td>5</td><td>The name is free to use</td><td>A rename after indexing discards what the URL and the brand earned</td><td>No trademark or domain check is recorded</td><td><a href="questions.html">Q-24</a> · <a href="direction.html#SG-36">SG-36</a><br><span class="meta">Internal only — no external source applies.</span></td></tr>
<tr><td>6</td><td>Imagery licence on record</td><td>Publishing an asset you cannot show rights for is the same failure as an unsourced spec</td><td>Illustrations shipped and captioned; no licence row in the register</td><td><a href="questions.html">Q-25</a> · <a href="direction.html#SG-37">SG-37</a><br><span class="meta">Internal only — no external source applies.</span></td></tr>
<tr><td>7</td><td>One measurement deployed</td><td>Without a number, the next topic is chosen by taste and the ledger stays empty forever</td><td>Endpoint code shipped and tested; unlocked but not deployed</td><td><a href="measurement.html">FLG-007</a> · <a href="direction.html#SG-07">SG-07</a><br><span class="meta">Internal only — no external source applies.</span></td></tr>
</tbody></table></div>
<h2>Copy-ready question pack</h2>
<p>The blocking rows, as a message you can send to whoever owns the account.</p>
<pre><code>{esc(pack)}</code></pre>
<h2>Where a suggestion becomes a question</h2>
<ul>
<li><a href="direction.html">SG-01 / SG-08</a> depend on Q-01, Q-16 and the one-link test — money and measurement both wait on account access.</li>
<li><a href="direction.html">SG-09</a> is Q-06. Authorship is the only trust improvement nobody else can supply.</li>
<li><a href="direction.html">SG-03 / SG-10</a> depend on Q-05 and Q-07 — imagery and canonical specs.</li>
</ul>
{capture_block()}
"""

def probes_section():
    rows = ""
    for pr in PROBES["probes"]:
        agree = "matches 2026-11-17" if pr.get("agrees_with_prior_session") else "DIVERGES from 2026-11-17"
        flags = " ".join(f"<code>{esc(f)}</code>" for f in pr.get("observed_flags", []))
        note = f'<p class="meta">{esc(pr["note"])}</p>' if pr.get("note") else ""
        rows += (f'<tr><td><code>{esc(pr["submitted_token"])}</code><br><span class="meta">{pr["token_chars"]} chars · lowercase: {esc(pr["token_lowercase_letters"])}</span></td>'
                 f'<td>{esc(pr["http_result"])}</td><td><a href="{esc(pr["final_url"].split("?")[0])}" rel="nofollow noopener" target="_blank">{esc(pr["final_asin"])}</a></td>'
                 f'<td class="src">{flags}</td><td>{esc(agree)}</td><td>{esc(pr["breadcrumb_top"])}{note}</td></tr>')
    interp = PROBES["interpretation"]
    return f"""
<h2 id="probes">4 · Redirect re-observation log</h2>
<p>Independent re-check of all five supplied links, run by {esc(PROBES['probe_session'])} on {esc(PROBES['probe_date'])} — which closes FLG-008, the prior session’s note that nobody in this repo had observed the redirects directly. Method: {esc(PROBES['probe_method'])}</p>
<div class="tablewrap"><table><thead><tr><th>Supplied token</th><th>Result</th><th>Final listing</th><th>Query flags on the response</th><th>vs prior session</th><th>Browse path / note</th></tr></thead><tbody>{rows}</tbody></table></div>
<h3>What this proves</h3>
<p>{esc(interp['reproduced'])}</p>
<h3>What it does not prove</h3>
<p>{esc(interp['what_reproduction_does_not_prove'])}</p>
<div class="notice"><strong>Operational consequence.</strong> {esc(interp['operational_consequence'])}</div>
"""

# ---------- TOPICS (backlog) ----------
def topic_sources(t):
    urls = t.get("source") or []
    if not urls:
        return '<span class="meta">— none yet</span>'
    return " ".join(f'<a href="{esc(u)}" rel="nofollow noopener" target="_blank">{esc(u.split("/dp/")[-1] if "/dp/" in u else u)}</a>' for u in urls)

def published_link(t):
    """A published topic links to the guide it became; a planned one shows nothing."""
    pa = t.get("published_as")
    if not pa:
        return ""
    return '<br><a href="' + esc(pa) + '">Read it →</a>'

def topics_body():
    rows = ""
    for t in TOPICS:
        status = t.get("status", "planned")
        cls = "okpill" if status == "published" else ("flagpill" if status == "blocked" else "warnpill")
        rows += (f'<tr><td><strong>{esc(t["id"])}</strong></td>'
                 f'<td><strong>{esc(t["title"])}</strong><p class="meta">{esc(t["question"])}</p></td>'
                 f'<td>{esc(t["cluster"])}</td><td>{esc(t.get("season", "Everyday"))}</td>'
                 f'<td>{esc(t["why"])}</td><td>{esc(t["needs"])}</td>'
                 f'<td>{topic_sources(t)}</td>'
                 f'<td>{esc(t["chosen_from"])}</td>'
                 f'<td><span class="{cls}">{esc(status)}</span>{published_link(t)}</td></tr>')
    published = "".join(f'<li><a href="{g["path"]}">{esc(g["title"])}</a> <span class="meta">({esc(g.get("cluster",""))})</span></li>'
                        for g in GUIDES)
    return f"""
<section class="hero"><span class="kicker">Topics · {len(TOPICS)} in the backlog</span>
<h1>What we are writing next — and how each topic was chosen</h1>
<p class="lede">Every guide on this site starts as a question someone would actually type. This page shows the questions still to write, what each one would need, and — in plain words — whether the topic came from an editorial hunch or from a measured query.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<div class="notice"><strong>Read the “chosen from” column before treating a title as evidence of demand.</strong> No Search Console property exists for this site yet, so no topic on this list is chosen from measured queries. They are editorial hypotheses: plausible questions, not popularity claims. When the analytics endpoint and the Search Console property exist, this column is where a measured query replaces a hunch — and the gate fails if a topic ever claims measured demand without a recorded source.</div>
<div class="tablewrap"><table><thead><tr><th>ID</th><th>Topic (the question)</th><th>Cluster</th><th>Season</th><th>Why it earns a page</th><th>What it would need</th><th>Official sources</th><th>Chosen from</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Already published</h2>
<ul>{published}</ul>
<p class="seclink"><a class="btn btn-quiet" href="guides/index.html">Read the guides →</a> <a class="btn btn-quiet" href="direction.html">Suggest a different topic →</a></p>
<h2>How a topic gets written</h2>
<ol>
<li>A reader question that can be answered from listed specifications and published guidance — never from an opinion.</li>
<li>A row per claim, each with a source link, and anything unconfirmable left blank and flagged.</li>
<li>One JSON file in <code>data/guides/</code>, then <code>npm run build</code> — the index, sitemap, feed and search index all follow.</li>
<li>The gate runs before publish: disclosure present, sponsored links qualified, no static prices, no broken internal links.</li>
</ol>
{capture_block()}
"""

# ---------- BUILD ----------
def rfc822(d):
    return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")

def main():
    pages = {}
    P = page_html
    pages["index.html"] = P("index.html", "ShopNow Kitchen — Basket or oven-style? Compare before you buy.",
        "Five kitchen appliances compared on the specs you can check: capacity, footprint, cleanup, accuracy. Sources on every row, no invented prices.",
        home_body(), image=HERO_IMG[0])
    pages["products/index.html"] = P("products/index.html", "The shop — all five products, with sources | ShopNow Kitchen",
        "Every product in the shop in one table: capacity, footprint, weight, model, temperature, power, and the listing each value came from.",
        products_index_body(), image=HERO_IMG[0])
    pages["guides/index.html"] = P("guides/index.html", "Guides — question-shaped buying guides | ShopNow Kitchen",
        f"{counts()['guides']} buyer guides on air fryers and meat thermometers: capacity, cleanup, counter space, probes, and food-safety targets.",
        guides_index_body(), image=HERO_IMG[0])
    pages["topics.html"] = P("topics.html", "Topics — what we are writing next | ShopNow Kitchen",
        f"{len(TOPICS)} planned buyer questions, each with the sources it would need and how the topic was chosen. Editorial hypotheses until real query data exists.",
        topics_body(), image=HERO_IMG[0])
    pages["questions.html"] = P("questions.html", "Open questions — what must be answered before deciding | ShopNow Kitchen",
        f"{counts()['questions']} questions with what we have, what is missing, why it blocks a decision, and how to find the answer.",
        questions_body())
    guide_li = lambda cat: "".join(
        f'<li><a href="{g["path"]}">{esc(g["title"])}</a> <span class="meta">({read_min(g)} min read)</span></li>'
        for g in guides_for(cat)) or '<li>Guide incoming — see <a href="guides/index.html">all guides</a>.</li>'
    cat_copy = {
        "Air Fryers": ("Air Fryers — Compare basket vs. oven-style | ShopNow Kitchen",
            "Compare three air fryers on listed specs: Chefman 6 Qt dual basket, Chefman 8 Qt TurboFry, Emeril 26QT French Door. Capacity, footprint, cleanup, sources on every row.",
            "Air Fryers: basket or oven-style?",
            "Three air fryers, two shapes. Compare capacity, footprint and cleanup on the specs you can check — then read the guides written for exactly those questions."),
        "Meat Thermometers": ("Meat Thermometers — Instant-read vs. wireless | ShopNow Kitchen",
            "Compare ThermoMaven 1 Sec instant-read and CHEF iQ Sense Gen3 wireless on listed specs, plus the USDA temperature targets that decide which one you need.",
            "Meat thermometers: probe in your hand, or left in the food?",
            "One instant-read and one three-probe wireless system. The USDA food-safety targets are the same for both — what differs is who takes the reading, and when."),
    }
    for name, href in CATEGORIES:
        t, d, h1, lede = cat_copy[name]
        pages[href] = P(href, t, d,
            category_body(name, h1, lede, guide_li(name)),
            extra_head=breadcrumb_jsonld([("Home", "index.html"), (name, href)]),
            image=CAT_IMG[name][0])
    for x in PRODUCTS:
        cat_href_x = dict(CATEGORIES).get(x["category"], "products/index.html")
        pages[x["page"]] = P(x["page"], f"{x['short_label']} — specs & comparison | ShopNow Kitchen",
            f"{x['title']} Specs read from Amazon's listing, source linked. Price and rating intentionally not displayed.",
            product_body(x),
            extra_head=(product_faq_jsonld(x) + breadcrumb_jsonld(
                [("Home", "index.html"), ("The shop", "products/index.html"),
                 (x["category"], cat_href_x), (x["short_label"], x["page"])])),
            image=CAT_IMG.get(x["category"], HERO_IMG)[0])
    for g in GUIDES:
        g_cat = dict(CATEGORIES).get(g.get("category"), "guides/index.html")
        pages[g["path"]] = P(g["path"], g["title"] + " | ShopNow Kitchen", g["desc"], guide_body(g),
                             page_type="guide",
                             extra_head=(article_jsonld(g) + faq_jsonld(g) + breadcrumb_jsonld(
                                 [("Home", "index.html"), ("Guides", "guides/index.html"),
                                  (g.get("cluster", "Guides"), g_cat), (g["title"], g["path"])])),
                             image=g.get("image") or "")
    for sname, meta in SERIES_META.items():
        pages[meta["slug"]] = P(meta["slug"], meta["title"] + " | ShopNow Kitchen", meta["desc"],
            series_body(sname), image=meta["image"],
            extra_head=breadcrumb_jsonld([("Home", "index.html"), (sname, meta["slug"])]))
    pages["direction.html"] = P("direction.html", "Suggestions & paths — the decision board | ShopNow Kitchen",
        f"{len(SUGGESTIONS)} reviewed suggestions with evidence, effort, risk and how to measure each one; tick the ones you accept and copy the next build prompt.",
        direction_body())
    pages["verification.html"] = P("verification.html", "Verification — source register, intent record, redirect log | ShopNow Kitchen",
        "Line-by-line verification: product-intent record with intended and observed kept separate, spec sources, the source register, and the redirect re-observation log.",
        verification_body() + probes_section())
    pages["flagged-for-review.html"] = P("flagged-for-review.html", "Flagged for review — what we could not verify | ShopNow Kitchen",
        f"{counts()['flags']} flagged items with source links and the action that resolves each. Published, not hidden; none of it blocks the site.",
        flagged_body())
    pages["disclosure.html"] = P("disclosure.html", "Disclosure — how this site earns money | ShopNow Kitchen",
        "As an Amazon Associate I earn from qualifying purchases. Sponsored links, no displayed prices, and what we collect about you (locally only).",
        disclosure_body())
    pages["measurement.html"] = P("measurement.html", "Measurement — five events and an empty ledger | ShopNow Kitchen",
        "Privacy-preserving click counter, self-hosted endpoint code, five defined events, and a campaign ledger that stays empty until first-party reports arrive.",
        measurement_body())
    pages["about.html"] = P("about.html", "About — authorship, method, brand and cadence | ShopNow Kitchen",
        "Who writes ShopNow Kitchen (a desk, not a person), how every claim is sourced, what we refuse to claim, and how a new guide gets published.",
        about_body())
    pages["executive-summary.html"] = P("executive-summary.html", "Executive summary — five products, one shop, honest numbers | ShopNow Kitchen",
        "What is live, what the link investigation found, what must happen before this earns anything, and what is deliberately not claimed.",
        exec_body())
    pages["search.html"] = P("search.html", "Search — ShopNow Kitchen", "Client-side search across products, guides and registers. Nothing leaves your browser.",
        search_body())
    pages["404.html"] = P("404.html", "Not found | ShopNow Kitchen", "That page is not on the counter.", notfound_body())

    items = [{"@type": "ListItem", "position": n + 1, "url": SITE + x["page"], "name": x["short_label"]} for n, x in enumerate(PRODUCTS)]
    pages["index.html"] = pages["index.html"].replace("</head>", '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": items}) + "</script></head>")

    for path, content in pages.items():
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    # sitemap: lastmod from real per-page dates, not a build stamp
    dates = {g["path"]: g.get("updated", TODAY) for g in GUIDES}
    urls = []
    for path in sorted(pages.keys()):
        if path == "404.html":
            continue
        urls.append(f"  <url><loc>{SITE}{path}</loc><lastmod>{dates.get(path, TODAY)}</lastmod></url>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")

    # robots: content open, implementation internals kept out of the crawl set
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n"
                "Disallow: /scripts/\nDisallow: /data/\nDisallow: /analytics/\n"
                "Disallow: /archive/\nDisallow: /assets/search-index.json\n"
                f"Sitemap: {SITE}sitemap.xml\n")

    feed_items = []
    for g in GUIDES:
        feed_items.append(f"    <item><title>{esc(g['title'])}</title><link>{SITE}{g['path']}</link><guid isPermaLink=\"true\">{SITE}{g['path']}</guid>"
                          f"<category domain=\"{SITE}\">{esc(g.get('cluster', ''))}</category>"
                          f"<description>{esc(g['desc'])}</description><pubDate>{rfc822(g.get('published', TODAY))}</pubDate></item>")
    for x in PRODUCTS:
        feed_items.append(f"    <item><title>{esc(x['short_label'])}</title><link>{SITE}{x['page']}</link><guid isPermaLink=\"true\">{SITE}{x['page']}</guid>"
                          f"<description>{esc(x['title'])}</description><pubDate>{rfc822(TODAY)}</pubDate></item>")
    with open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>\n'
                f"  <title>ShopNow Kitchen</title><link>{SITE}</link><atom:link href=\"{SITE}feed.xml\" rel=\"self\" type=\"application/rss+xml\"/>"
                "<description>Basket or oven-style? Compare before you buy. Specs, sources and the questions that decide it — no hype.</description>\n"
                + "\n".join(feed_items) + "\n</channel></rss>\n")

    idx = []
    for x in PRODUCTS:
        idx.append({"title": x["short_label"], "url": x["page"], "kind": "Product · " + x["category"],
                    "text": " ".join([x["title"], x["brand"], x["model"], x["capacity"], x["observed_asin"], x["submitted_token"]])})
    for g in GUIDES:
        idx.append({"title": g["title"], "url": g["path"], "kind": "Guide · " + g["cluster"], "text": g["desc"] + " " + g.get("season", "")})
    for path, title, extra in [("air-fryers.html", "Air Fryers", "basket oven-style capacity cleanup"),
                               ("thermometers.html", "Meat Thermometers", "instant-read wireless probe USDA 165"),
                               ("products/index.html", "The shop", "all products table specs sources"),
                               ("guides/index.html", "All guides", "buyer questions checklists"),
                               ("topics.html", "Topics: what is next", "planned questions editorial backlog pipeline"),
                               ("direction.html", "Suggestions & paths", "decision board next prompt"),
                               ("questions.html", "Open questions", "missing information blocking"),
                               ("verification.html", "Verification", "sources intent observed redirect"),
                               ("flagged-for-review.html", "Flagged for review", "unverified items"),
                               ("measurement.html", "Measurement", "events ledger endpoint"),
                               ("executive-summary.html", "Executive summary", "what is live what happens next"),
                               ("about.html", "About", "authorship method brand cadence")]:
        idx.append({"title": title, "url": path, "kind": "Page", "text": title + " ShopNow Kitchen " + extra})
    with open(os.path.join(ROOT, "assets", "search-index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)

    print(f"Built {len(pages)} pages, {len(urls)} sitemap URLs, {len(GUIDES)} guides, {len(idx)} search rows.")

if __name__ == "__main__":
    main()
