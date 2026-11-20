#!/usr/bin/env python3
"""Build the ShopNow Kitchen static site from data/ (single source of truth).
Run: python3 scripts/build_site.py
No third-party dependencies. Generated HTML is committed for GitHub Pages (legacy build).
"""
import json, html, os, datetime, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sassnarep3-star.github.io/WinC/"
TAG = "shopnow047c-20"
TODAY = "2026-11-20"

def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)

PRODUCTS = load("data/products.json")["products"]
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

CATEGORIES = [("Air Fryers", "air-fryers.html"), ("Meat Thermometers", "thermometers.html")]
CAT_IMG = {
    "Air Fryers": ("assets/img/air-fryers.png",
        "Editorial illustration: air fryer baskets open on a kitchen counter. Not a product photograph."),
    "Meat Thermometers": ("assets/img/thermometers.png",
        "Editorial illustration: instant-read probe and wireless sensor on a countertop. Not a product photograph."),
}
HERO_IMG = ("assets/img/hero-counter.png",
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
            "flags": len(FLAGS), "questions": len(QUESTIONS),
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
    li = "".join(f"<li>{x}</li>" for x in specs)
    return f"""<article class="card">
<figure class="cardimg"><img src="{pfx}{img}" alt="{esc(cap)}" loading="lazy" width="800" height="500"></figure>
<span class="cat">{esc(p['category'])} · {esc(p['brand'])}</span>
<h3><a href="{pfx}{p['page']}">{esc(p['short_label'])}</a></h3>
<p>{esc(p['title'])}</p>
<ul class="specs">{li}</ul>
<div class="actions">{buy_button_small(p)}</div>
<p class="meta">ASIN {esc(p['observed_asin'])} · <a href="{pfx}verification.html">Source</a></p>
</article>"""

def guide_card(g, depth=0):
    pfx = "../" * depth
    img = g.get("image") or CAT_IMG.get(g.get("category", ""), HERO_IMG)[0]
    cap = g.get("image_caption", "Editorial illustration. Not a product photograph.")
    return f'''<article class="card guidecard">
<figure class="cardimg"><img src="{pfx}{esc(img)}" alt="Editorial illustration for: {esc(g['title'])}" loading="lazy" width="800" height="500"></figure>
<span class="cat">Guide · {esc(g['cluster'])}</span>
<h3><a href="{pfx}{g['path']}">{esc(g['title'])}</a></h3>
<p>{esc(g['desc'])}</p>
<p class="meta">{esc(g['published'])} · {read_min(g)} min read · {esc(g.get('season', 'Everyday'))}</p>
</article>'''

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
<form id="reader-capture" action="{pfx}measurement.html" method="get">
<label for="email">Email address</label>
<input id="email" name="email" type="email" required autocomplete="email" placeholder="you@example.com">
<button class="btn" type="submit">Subscribe</button>
</form>
<small>The honest version: this is a static site, so submitting only records a <code>reader_capture_submit</code> count inside your own browser and takes you to the <a href="{pfx}measurement.html">measurement page</a>. No list exists and nothing reaches a server until the owner wires up an email provider — see <a href="{pfx}flagged-for-review.html">FLG-013</a>.</small>
</section>"""

# ---------- HOME ----------
def home_body():
    c = counts()
    cards = "".join(product_card(x) for x in PRODUCTS)
    rail = "".join(guide_card(g) for g in GUIDES)
    img, cap = HERO_IMG
    lead = GUIDES[0]
    tiles = ""
    for name, href in CATEGORIES:
        cimg, ccap = CAT_IMG[name]
        tiles += (f'<a class="cattile" href="{href}"><img src="{cimg}" alt="{esc(ccap)}" loading="lazy" width="800" height="500">'
                  f'<span class="catname">{esc(name)}</span><span class="catcount">{len(prods(name))} in the shop · {len(guides_for(name))} guides</span></a>')
    return f"""
<section class="hero">
<span class="kicker">Countertop cooking · Season: {esc(lead.get('season', 'Everyday'))}</span>
<h1>{esc(lead['title'])}</h1>
<p class="lede">{esc(lead['desc'])}</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · {read_min(lead)} min read · <a href="about.html">How we check</a> · <a href="verification.html">Sources</a></p>
<figure class="lede-figure"><img src="{img}" alt="{esc(cap)}" width="1200" height="750"><figcaption>{esc(cap)}</figcaption></figure>
<p class="cta-row"><a class="btn btn-ghost" href="{lead['path']}">Read the guide →</a> <a class="btn btn-quiet" href="products/index.html">See all {c['products']} products</a></p>
</section>

<h2>The shop</h2>
<div class="grid">{cards}</div>
<div class="notice"><strong>How to read this page:</strong> every “Check on Amazon” button is a sponsored link, marked <span class="sponsored-tag">Sponsored</span>. Prices and availability live on Amazon, not here. The specs are copied from Amazon’s own listings on {TODAY}; where a cell is blank it is because we could not confirm the value, and we would rather show you a gap than a guess.</div>

<h2>Start with a question, not a product</h2>
<div class="grid">{rail}</div>
<p><a class="btn btn-quiet" href="guides/index.html">All {c['guides']} guides →</a></p>

<h2>Browse by category</h2>
<div class="catgrid">{tiles}</div>

<h2>Why the numbers here are boring in a good way</h2>
<ul>
<li>{c['sources']} sources on the <a href="verification.html">verification register</a>. Every product row links to the listing it came from, with the date it was read.</li>
<li>{c['flags']} items we could not confirm, published on <a href="flagged-for-review.html">Flagged for review</a> with the action that would settle each one.</li>
<li>Intended product and observed redirect are stored as separate fields, on purpose: a link that redirects somewhere is not proof of what someone meant.</li>
<li>{c['questions']} open questions ({c['blocking']} of them blocking) are on one page: <a href="questions.html">Open questions</a>.</li>
</ul>
{capture_block()}
<h2>What we do not do</h2>
<ul>
<li>No “best” rankings without a stated method. We compare listed specs; you decide.</li>
<li>No invented hands-on testing. Nobody on this desk has cooked with these five units, so no page claims it.</li>
<li>No copied Amazon descriptions, no scraped Amazon images, no countdown timers, no “only 3 left in stock”.</li>
</ul>
"""

# ---------- CATEGORY PAGES ----------
def category_body(cat, title, intro, guide_links):
    ps = [p for p in PRODUCTS if p["category"] == cat]
    cards = "".join(product_card(p) for p in ps)
    # comparison table
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
<div class="grid">{cards}</div>
<h2>Compare side by side</h2>
{table}
<h2>Guides for this category</h2>
<ul>{guide_links}</ul>
{capture_block()}
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
        guides = ('<li><a href="../guides/multi-function-appliance-questions.html">Questions before buying a multi-function appliance</a></li>'
                  '<li><a href="../thermometers.html">Compare both thermometers</a></li>')
    return f"""
<section class="hero"><span class="kicker">{esc(p['category'])} · {esc(p['brand'])}</span>
<h1>{esc(p['short_label'])}</h1>
<p class="lede">{esc(p['title'])}</p>
<p class="meta">Observed ASIN {esc(p['observed_asin'])} · Listing checked {esc(p['source_date'])} · <a href="../verification.html">Verification record</a></p>
<div class="actions" style="margin:14px 0">{buy_button(p)}</div>
<p class="meta">You will go to Amazon. Price and availability are shown there. This button is a sponsored link.</p>
</section>
<h2>Specs (from Amazon’s listing)</h2>
{specs_table(p)}
<h2>What to compare before you buy</h2>
<ul>
<li><strong>Capacity vs. your actual meals:</strong> {esc(p['capacity'] or 'see listing')} — measure the tray or bird you cook most often.</li>
<li><strong>Footprint:</strong> {esc(p['dimensions'] or 'not confirmed — measure the listing’s dimensions on Amazon')} — check counter depth and cabinet clearance.</li>
<li><strong>Cleanup:</strong> check whether baskets/parts are listed as dishwasher-safe on Amazon before you buy.</li>
<li><strong>Functions you will use weekly:</strong> presets only help if they match your routine (see the multi-function guide).</li>
</ul>
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
        fig = (f'<figure class="lede-figure"><img src="../{esc(g["image"])}" alt="{esc(cap)}" width="1200" height="750">'
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

def direction_body():
    c = counts()
    cards = ""
    for x in SUGGESTIONS:
        cls = status_pill_class(x["status"])
        opts = ""
        cards += f"""<article class="sug" id="{esc(x['id'])}">
<header><h3>{esc(x['title'])}</h3>{pill(x['status'], cls)}</header>
<p class="sugmeta">{esc(x['area'])} · {esc(x['id'])} · effort {esc(x['effort'])} ({EFFORT.get(x['effort'], x['effort'])}) · cost: {esc(x['cost'])}</p>
<p class="why"><span>Problem</span>{rich(x['problem'])}</p>
<p class="why"><span>Suggestion</span>{rich(x['proposal'])}</p>
<p class="why"><span>Risk</span>{rich(x['risk'])}</p>
<p class="why"><span>How we would know it worked</span>{rich(x['expected_effect'])}</p>
<p class="why"><span>Evidence</span>{rich(x['evidence'])}</p>
<details class="promptbox"><summary>Instruction block for the next build prompt</summary>
<pre><code>{esc(x['feeds_prompt'])}</code></pre></details>
</article>"""
    return f"""
<section class="hero"><span class="kicker">Direction · {len(SUGGESTIONS)} suggestions, nothing implemented by surprise</span>
<h1>Read these, choose a path, and the next prompt writes itself</h1>
<p class="lede">Each suggestion states the evidence for it, what it changes, the risk, and how to tell whether it worked. Ticking boxes here changes nothing on the site — it stores your selection in this browser and assembles a copy-paste instruction block for whoever builds next. Implementation only starts after you choose.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · {c['open_sug']} still open, {c['done_sug']} already shipped this session</p></section>

<h2>Choose the next path</h2>
<div class="notice"><strong>How to choose:</strong> pick the path that matches what you want in the next month, not the one that sounds most ambitious. Paths are mutually exclusive for one build. Your choice is stored only in this browser (localStorage); no data leaves the device and nothing is sent anywhere.</div>
<form class="chooser" id="path-chooser">
<label><input type="radio" name="path" value="A"> <strong>Path A — Trust the money path first (recommended).</strong> Run the one-link Associates tests, confirm the tracking ID, keep links gated until they pass. Nothing grows until the click actually attributes.</label>
<label><input type="radio" name="path" value="B"> <strong>Path B — Shop depth.</strong> Add a “match to your situation” block to both categories and per-row source dates on every spec, then licensed photography. Best for conversion; needs the imagery decision (Q-07).</label>
<label><input type="radio" name="path" value="C"> <strong>Path C — Content volume.</strong> Two guides a week from the question backlog plus a seasonal cluster. Best for coverage; worst without measurement, because you will be guessing which topic to write next.</label>
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
<h2>The register</h2>
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
 var HEAD="Implement on the ShopNow Kitchen site (repo sassnarep3-star/WinC). Standing rules: read COORDINATION.md and claim tasks before editing; never fill an unverified value — leave it blank and flag it; keep intended_* and observed_* fields separate; run `npm run build && npm run check` until green; open a PR to main, merge, and confirm Pages is live.\n\nACCEPTED SUGGESTIONS\n";
 var TAIL="\n\nAlso: re-verify anything you touch against an official source and add it to data/sources.json with a retrieval date. Do not add prices, ratings, review counts, or hands-on-testing claims. Every outbound product link keeps rel=\"sponsored nofollow noopener\" and the affiliate tag.";
 function fmt(){{
  var on=[].slice.call(document.querySelectorAll('.sg-pick:checked'));
  var path=document.getElementById('path-select').value;
  if(!on.length&&!path){{out.value="Check the boxes above to fill this in.";return;}}
  var body=on.map(function(c){{return "- ["+c.value+"] "+c.dataset.title+"\n  → "+c.dataset.prompt;}}).join("\n");
  if(path){{body=(body?body+"\n":"")+"- Path "+path+" from direction.html applies to this build.";}}
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
            f"<tr><td>{esc(p['submitted_url'])}<br><span class='meta'>token {esc(p['submitted_token'])} ({p['token_length']} chars)</span></td>"
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
        f"<tr><td>{esc(s['id'])}</td><td>{esc(s['title'])}<br><a class='src' href='{esc(s['url'])}' rel='nofollow noopener' target='_blank'>{esc(s['url'])}</a></td><td>{esc(s['what'])}</td><td>{esc(s['date'])}</td></tr>"
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
        ("Question-shaped guides + measure", "4 guides published; 5 events defined; ledger empty", "guides/, measurement.html"),
        ("Click/conversion measurement first", "Beacon + Worker code; local-only until deployed (FLG-007)", "assets/app.js, analytics/"),
        ("Campaign ledger (evidence-based)", "Empty, well-defined; first-party reports only", "measurement.html"),
        ("Compliance gate in workflow", "scripts/check_site.py fails on disclosure/sponsored/price/sitemap violations", "scripts/check_site.py"),
        ("Publication polish (authorship, seasons, clusters)", "Kitchen Desk byline, season/cluster labels, RSS/Search Console/reader capture status", "about.html"),
        ("Suggestions + Q&A before decisions", "Direction page with path chooser + Q&A table", "direction.html"),
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
def flagged_body():
    rows = "".join(
        f"<tr><td><strong>{esc(f['id'])}</strong></td><td>{esc(f['title'])}</td><td>{esc(f['detail'])}</td><td>{esc(f['action'])}</td><td><span class='flagpill'>{esc(f['status'])}</span></td></tr>"
        for f in FLAGS)
    return f"""
<section class="hero"><span class="kicker">Flagged for Review · Needs review</span>
<h1>Flagged for Review: what we could not verify</h1>
<p class="lede">These items do not block the site. They are published here so you can review them after the site is live and request changes. Nothing flagged is presented as fact elsewhere.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<div class="tablewrap"><table><thead><tr><th>ID</th><th>Issue</th><th>Detail</th><th>Action to resolve</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
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
<tr><td colspan="7"><span class="blank">— no rows yet (ledger is empty until first-party data arrives)</span></td></tr>
</tbody></table></div>

<h2>Findability status (SG-27..SG-30)</h2>
<div class="tablewrap"><table><thead><tr><th>Item</th><th>Status</th><th>Evidence</th></tr></thead><tbody>
<tr><td>Nav labels (SG-27)</td><td><span class="okpill">shipped</span></td><td>Single navigation group on every page</td></tr>
<tr><td>RSS feed (SG-28)</td><td><span class="okpill">shipped</span></td><td><a href="feed.xml">feed.xml</a> lists all guides + products</td></tr>
<tr><td>Search Console (SG-29)</td><td><span class="flagpill">pending</span></td><td>Sitemap ready at <a href="sitemap.xml">sitemap.xml</a>; submit in Search Console, then record date here</td></tr>
<tr><td>Reader capture (SG-30)</td><td><span class="warnpill">partial — no list behind it</span></td><td>Form renders on front page + guides; records a local count only. No list, no provider, no confirmed-opt-in flow yet — see FLG-013</td></tr>
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
<h2>Publishing cadence</h2>
<p>A new guide is one JSON file in <code>data/guides/</code>, then <code>npm run build</code>. Sitemap, RSS, the search index, this page’s cluster counts and every nav rail pick it up from the same source — no hand-edited lists. The next topic should come from measured queries rather than instinct, which is why <a href="measurement.html">measurement</a> is wired even while it records nothing yet.</p>
<h2>Corrections</h2>
<p>If a row on this site is wrong, that is a defect, not a difference of opinion. Flagged items are published on <a href="flagged-for-review.html">Flagged for review</a> with the source link and the action that would settle them; we would rather show an open question than fill it with a guess.</p>
{capture_block()}
"""

# ---------- EXEC SUMMARY ----------
def exec_body():
    c = counts()
    return f"""
<section class="hero"><span class="kicker">Executive summary · for the owner, not for readers</span>
<h1>Executive summary: {c['products']} products, {c['guides']} guides, nothing invented</h1>
<p class="lede">ShopNow Kitchen is a publication front page over an evidence ledger. It leads with products and buyer questions; verification sits one click away instead of in the way. Every number below is computed from the repo, not typed by hand, so this page cannot go stale without the data going stale first.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · full text in <code>EXECUTIVE-SUMMARY.md</code></p></section>

<h2>What is live</h2>
<div class="tablewrap"><table><thead><tr><th>Layer</th><th>State</th><th>Where</th></tr></thead><tbody>
<tr><td>Shop</td><td>{c['products']} product pages, 2 category pages, 1 shop index, all with sponsored buttons and disclosure above the fold</td><td><a href="products/index.html">The shop</a></td></tr>
<tr><td>Editorial</td><td>{c['guides']} question-shaped guides, newest first, each filtered to its own cluster</td><td><a href="guides/index.html">Guides index</a></td></tr>
<tr><td>Trust</td><td>{c['sources']} sources, {c['flags']} flagged items, intended vs observed kept in separate fields</td><td><a href="verification.html">Verification</a></td></tr>
<tr><td>Decisions</td><td>{len(SUGGESTIONS)} suggestions ({c['open_sug']} open, {c['done_sug']} done this session) + {c['questions']} questions, {c['blocking']} blocking</td><td><a href="direction.html">Suggestions</a> · <a href="questions.html">Open questions</a></td></tr>
<tr><td>Measurement</td><td>5 events defined, beacon shipped, endpoint <strong>not deployed</strong>, ledger empty by design</td><td><a href="measurement.html">Measurement</a></td></tr>
<tr><td>Findability</td><td>1 sitemap ({c['guides'] + c['products'] + 12} URLs), RSS, canonicals, FAQ + Article schema, robots scoping internals out</td><td><code>sitemap.xml</code></td></tr>
</tbody></table></div>

<h2>The five links, in one table</h2>
<div class="tablewrap"><table><thead><tr><th>Supplied</th><th>Token length</th><th>Valid ASIN?</th><th>Observed destination</th><th>Intended ASIN</th></tr></thead><tbody>
{"".join(f"<tr><td><code>{esc(p['submitted_token'])}</code></td><td>{p['token_length']}</td><td>No — 10 characters required (S05)</td><td><strong>{esc(p['observed_asin'])}</strong></td><td>{blank(p['intended_asin'])}</td></tr>" for p in PRODUCTS)}
</tbody></table></div>
<p class="src">Re-observed independently on {PROBES['probe_date']} by {esc(PROBES['probe_session'])}: 5/5 destinations matched the earlier observation, and every final URL carried <code>lv=shuf</code> + <code>plpRedirect=mhFallback</code> — a fallback route, so “observed” is not “intended” (FLG-009). Log: <a href="verification.html">Verification §4</a>.</p>

<h2>What has to happen before any of this earns anything</h2>
<ol>
<li>Confirm the tracking ID and one test link per product in Associates Central (FLG-001, FLG-002, Q-01, Q-16).</li>
<li>Confirm intent for the five products with whoever supplied them (Q-02) — do not infer it from a redirect.</li>
<li>Deploy the metrics endpoint, then pick topics from Search Console queries rather than taste (SG-07, SG-08).</li>
<li>Settle the spec conflicts on the manufacturer page, not on Amazon marketing copy (FLG-005, FLG-010, Q-05).</li>
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
  box.innerHTML='<p class="meta">'+hits.length+' result(s) for <strong>'+q+'</strong></p><div class="grid">'+
    hits.map(function(h){{return '<article class="card"><span class="cat">'+h.kind+'</span><h3><a href="'+h.url+'">'+h.title+'</a></h3><p>'+h.text.slice(0,180)+'…</p></article>';}}).join('')+'</div>';
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
        rows += (f'<tr><td><a href="{pfx}{esc(x["page"])}">{esc(x["short_label"])}</a><br><span class="meta">{esc(x["brand"])}</span></td>'
                 f'<td>{esc(x["category"])}</td><td>{blank(x["capacity"] if x["capacity"] != "—" else "")}</td>'
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
<div class="tablewrap"><table><thead><tr><th>Product</th><th>Category</th><th>Capacity</th><th>Footprint</th><th>Weight</th><th>Model</th><th>Temperature</th><th>Power</th><th>Price</th><th>Rating</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="legend"><strong>Reading the blanks:</strong> <code>—</code> means the field does not apply to that product type (a thermometer has no wattage). <span class="blank">— blank (unverified)</span> means we looked and could not confirm it, so we left it empty rather than estimate it. Both are answers; a guess would not be.</p>
<div class="notice"><strong>The price and rating columns are blank by policy, not by accident.</strong> Amazon’s Program Policies bar static price display, and ratings move daily — either number would be stale the moment it was written. The button on each card takes you to the listing, where the live figure is. See <a href="{pfx}flagged-for-review.html">FLG-006</a>.</div>
<h2>Cards</h2>
<div class="grid">{cards}</div>
<h2>How these five got here</h2>
<p>Each product entered the shop as a <code>link.amazon</code> short link rather than a listing URL. We recorded the token we were given, resolved it, and stored what came back in a separate field — because the response was a fallback route, not a canonical match. The raw redirects, the date, and what that does and does not prove are in <a href="{pfx}verification.html#probes">§4 of the verification register</a> and in <code>data/probes.json</code>.</p>
<p class="seclink"><a class="btn btn-quiet" href="{pfx}executive-summary.html">Read the executive summary →</a></p>
{capture_block(depth=1)}
"""

def questions_body():
    c = counts()
    rows = ""
    for q in QUESTIONS:
        bl = q.get("blocking", "no")
        kind = "act" if bl.startswith("yes") else "note"
        rows += (f'<tr><td><strong>{esc(q["id"])}</strong><br>{pill("blocking" if bl.startswith("yes") else "non-blocking", kind)}</td>'
                 f'<td><strong>{esc(q["question"])}</strong><p class="meta">Gates: {esc(q["decision_it_gates"])}</p></td>'
                 f'<td>{esc(q["have"])}</td><td>{esc(q["missing"])}</td><td>{esc(q["discovery"])}</td>'
                 f'<td>{esc(q["owner"])}</td><td class="answercell">{blank(q["answer"])}</td></tr>')
    pack = "\n\n".join(f'{q["id"]}. {q["question"]}\nWhat we need: {q["missing"]}\nHow to get it: {q["discovery"]}'
                        for q in QUESTIONS if q.get("blocking", "no").startswith("yes"))
    return f"""
<section class="hero"><span class="kicker">Open questions · {c['questions']} rows, {c['blocking']} blocking</span>
<h1>What has to be answered before the next decision is reasonable</h1>
<p class="lede">Not a to-do list — a register. Each row states what we already know and can cite, what is genuinely missing, which decision that gap blocks, and the concrete action that produces the answer. A blank answer cell means nobody has it yet, not that we skipped it.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · evidence in <a href="verification.html">the source register</a>, consequences in <a href="flagged-for-review.html">Flagged for review</a></p></section>
<div class="notice"><strong>Read it this way:</strong> the {c['blocking']} blocking rows are worth more than any content decision. Four of them — Q-01, Q-02, Q-04 and Q-16 — can only be answered inside an enrolled Amazon Associates account, which this environment cannot reach. That is a fact about the tooling, not an excuse, and it is why the site ships with links gated rather than links guessed. When you have an answer, paste it into <code>answer</code> in <code>data/questions.json</code>: the table updates on the next build, and the matching flag closes.</div>
<div class="tablewrap"><table class="qtable"><thead><tr><th>ID</th><th>Question</th><th>What we have (and its source)</th><th>What we do not have</th><th>How to discover it</th><th>Who can answer</th><th>Answer</th></tr></thead><tbody>{rows}</tbody></table></div>
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
            image=CAT_IMG[name][0])
    for x in PRODUCTS:
        pages[x["page"]] = P(x["page"], f"{x['short_label']} — specs & comparison | ShopNow Kitchen",
            f"{x['title']} Specs read from Amazon's listing, source linked. Price and rating intentionally not displayed.",
            product_body(x), image=CAT_IMG.get(x["category"], HERO_IMG)[0])
    for g in GUIDES:
        pages[g["path"]] = P(g["path"], g["title"] + " | ShopNow Kitchen", g["desc"], guide_body(g),
                             page_type="guide", extra_head=faq_jsonld(g), image=g.get("image") or "")
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
