#!/usr/bin/env python3
"""Build the ShopNow Kitchen static site from data/ (single source of truth).
Run: python3 scripts/build_site.py
No third-party dependencies. Generated HTML is committed for GitHub Pages (legacy build).
"""
import json, html, os, datetime

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
            f'<span class="sponsored-tag">Sponsored</span>')

def buy_button_small(p):
    return (f'<a class="btn" href="{esc(special_link(p))}" rel="sponsored nofollow noopener" '
            f'target="_blank" data-event="outbound_click" data-asin="{esc(p["observed_asin"])}">Check on Amazon</a> '
            f'<span class="sponsored-tag">Sponsored</span>')

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

NAV = [
    ("index.html", "Home"),
    ("air-fryers.html", "Air Fryers"),
    ("thermometers.html", "Thermometers"),
    ("guides/basket-or-oven-style-air-fryer.html", "Guides"),
    ("products/chefman-6qt-dual-basket-b0cdy277d3.html", "Products"),
    ("direction.html", "Direction"),
    ("verification.html", "Verification"),
    ("about.html", "About"),
]

def nav_html(current, depth):
    items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        h = ("../" * depth + href) if depth else href
        items.append(f'<a href="{h}"{cur}>{label}</a>')
    return '<nav class="mainnav" aria-label="Main"><div class="wrap">' + "".join(items) + "</div></nav>"

def footer_html(depth):
    p = "../" * depth
    return f"""<footer><div class="wrap">
<div class="footer-disclosure"><strong>As an Amazon Associate I earn from qualifying purchases.</strong>
This site contains sponsored product links (marked <span class="sponsored-tag">Sponsored</span>).
Prices and availability are shown on Amazon — check Amazon for current details.
<a href="{p}disclosure.html">Full disclosure</a></div>
<div class="cols">
<div><h4>Shop</h4><ul>
<li><a href="{p}air-fryers.html">Air Fryers</a></li>
<li><a href="{p}thermometers.html">Meat Thermometers</a></li>
<li><a href="{p}products/chefman-6qt-dual-basket-b0cdy277d3.html">All products</a></li>
</ul></div>
<div><h4>Guides</h4><ul>
<li><a href="{p}guides/basket-or-oven-style-air-fryer.html">Basket or oven-style?</a></li>
<li><a href="{p}guides/air-fryer-capacity-checklist.html">Capacity checklist</a></li>
<li><a href="{p}guides/cleanup-and-counter-space.html">Cleanup &amp; counter space</a></li>
<li><a href="{p}guides/multi-function-appliance-questions.html">Multi-function questions</a></li>
</ul></div>
<div><h4>Dashboard</h4><ul>
<li><a href="{p}verification.html">Verification &amp; sources</a></li>
<li><a href="{p}flagged-for-review.html">Flagged for Review</a></li>
<li><a href="{p}measurement.html">Measurement &amp; ledger</a></li>
<li><a href="{p}executive-summary.html">Executive summary</a></li>
<li><a href="{p}direction.html">Direction &amp; suggestions</a></li>
</ul></div>
<div><h4>Site</h4><ul>
<li><a href="{p}about.html">About &amp; authorship</a></li>
<li><a href="{p}search.html">Search</a></li>
<li><a href="{p}sitemap.xml">Sitemap</a></li>
<li><a href="{p}feed.xml">RSS feed</a></li>
<li><a href="{p}disclosure.html">Disclosure &amp; privacy</a></li>
</ul></div>
</div>
<p class="meta" style="color:#A8A29E">ShopNow Kitchen · {TODAY} · Tracking ID {TAG} (see Flagged for Review FLG-001). Product names and trademarks belong to their owners; this site is not endorsed by Amazon.</p>
</div></footer>"""

def head(title, desc, path, extra=""):
    canon = SITE + path
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<link rel="stylesheet" href="{'../' if '/' in path else ''}assets/style.css">
<link rel="alternate" type="application/rss+xml" title="ShopNow Kitchen" href="{'../' if '/' in path else ''}feed.xml">
{extra}
</head>"""

def page_html(path, title, desc, body, page_type="page", extra_head=""):
    depth = path.count("/")
    return (head(title, desc, path, extra_head) +
        f'<body data-page-type="{page_type}">'
        f'<header class="masthead"><div class="wrap"><a class="brand" href="{"../"*depth}index.html">ShopNow <span>Kitchen</span></a>'
        f'<p class="tagline">Basket or oven-style? Compare before you buy.</p>'
        f'<span class="dateline">{TODAY} · The Kitchen Desk</span></div></header>'
        + disclosure_strip_for(path) + nav_html(path, depth) +
        f'<main class="wrap">{body}</main>' + footer_html(depth) +
        f'<script src="{"../"*depth}assets/app.js" defer></script></body></html>')

def product_card(p, depth=0):
    pfx = "../" * depth
    icon = "🍟" if p["category"] == "Air Fryers" else "🌡️"
    specs = []
    if p["capacity"] and p["capacity"] != "—":
        specs.append(f"Capacity: {esc(p['capacity'])}")
    if p["dimensions"]:
        specs.append(f"Size: {esc(p['dimensions'])}")
    if p["model"]:
        specs.append(f"Model: {esc(p['model'])}")
    li = "".join(f"<li>{s}</li>" for s in specs)
    return f"""<article class="card">
<div class="icon" aria-hidden="true">{icon}</div>
<span class="cat">{esc(p['category'])} · {esc(p['brand'])}</span>
<h3><a href="{pfx}{p['page']}">{esc(p['short_label'])}</a></h3>
<p>{esc(p['title'])}</p>
<ul class="specs">{li}</ul>
<div class="actions">{buy_button_small(p)}</div>
<p class="meta">ASIN {esc(p['observed_asin'])} · <a href="{pfx}verification.html">Source</a></p>
</article>"""

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
    return f"""<section class="capture" aria-label="Reader capture">
<h3>Get the next comparison — no hype, just the checklist.</h3>
<p>One email when a new guide publishes. Double opt-in. No tracking pixel. Unsubscribe anytime.</p>
<form id="reader-capture" action="{pfx}measurement.html" method="get">
<label for="email">Email address</label>
<input id="email" name="email" type="email" required autocomplete="email" placeholder="you@example.com">
<button class="btn" type="submit">Subscribe</button>
</form>
<small>Submitting records a <code>reader_capture_submit</code> event (see <a href="{pfx}measurement.html">Measurement</a>). Your email is handled by the email provider you choose — this static site does not store it.</small>
</section>"""

# ---------- HOME ----------
def home_body():
    cards = "".join(product_card(p) for p in PRODUCTS)
    return f"""
<section class="hero">
<span class="kicker">Countertop cooking · Season: Everyday meals</span>
<h1>Basket or oven-style? Compare before you buy.</h1>
<p class="lede">Five kitchen appliances, compared on the specs you can check: capacity, size, cleanup, and what each one actually does. No “best” claims, no invented prices — just the numbers from Amazon’s own listings and the questions to ask before you spend.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · <a href="about.html">How we check</a> · <a href="verification.html">Sources</a></p>
</section>
<h2>Shop the five</h2>
<div class="grid">{cards}</div>
<div class="notice"><strong>How to read this page:</strong> every “Check on Amazon” button is a sponsored link (marked <span class="sponsored-tag">Sponsored</span>). Prices and availability live on Amazon. Specs below are copied from Amazon’s listings on {TODAY} — if a cell is blank, we could not confirm it and left it blank.</div>
<h2>Start with a question</h2>
<div class="grid">
<article class="card"><span class="cat">Guide · Air fryers</span><h3><a href="guides/basket-or-oven-style-air-fryer.html">Basket or oven-style air fryer: what should you compare?</a></h3><p>Two baskets that finish together vs. one big oven cavity — the trade-offs in capacity, footprint, and cleanup.</p></article>
<article class="card"><span class="cat">Guide · Capacity</span><h3><a href="guides/air-fryer-capacity-checklist.html">A no-hype checklist for comparing air fryer capacity</a></h3><p>Quarts mean different things. Measure the food, not the marketing.</p></article>
<article class="card"><span class="cat">Guide · Cleanup</span><h3><a href="guides/cleanup-and-counter-space.html">How to assess cleanup and counter-space trade-offs</a></h3><p>Dishwasher-safe parts, windows, and the inches your counter actually has.</p></article>
<article class="card"><span class="cat">Guide · Multi-function</span><h3><a href="guides/multi-function-appliance-questions.html">Questions to ask before buying a multi-function kitchen appliance</a></h3><p>24 functions sound great — until you ask which ones you will use weekly.</p></article>
</div>
<h2>Thermometers, too</h2>
<p>Two meat thermometers are in the shop: an instant-read probe and a wireless 3-probe system. <a href="thermometers.html">Compare them →</a></p>
{capture_block()}
<h2>What we do not do</h2>
<ul>
<li>No prices, ratings, or “bought in past week” numbers on this site (Program Policies + volatility — see <a href="flagged-for-review.html">FLG-006</a>).</li>
<li>No “best” rankings without a stated method. We compare specs; you decide.</li>
<li>No copied Amazon descriptions. Every word here is original.</li>
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

# ---------- GUIDES ----------
GUIDES = [
    {
        "path": "guides/basket-or-oven-style-air-fryer.html",
        "title": "Basket or oven-style air fryer: what should you compare?",
        "desc": "Two baskets that finish together vs. one big oven cavity. Compare capacity, footprint, and cleanup across the three air fryers in the shop.",
        "cluster": "Air Fryers",
        "body": """
<p>Three air fryers are in the shop, and they split into two shapes. Two are <strong>basket-style</strong> (one or two removable baskets you slide in and out). One is <strong>oven-style</strong> (a countertop oven cavity with French doors and racks). The shape changes everything about capacity, cleanup, and counter space — so compare the shape first, then the specs.</p>
<h2>The two shapes, in plain terms</h2>
<div class="tablewrap"><table><thead><tr><th>Question</th><th>Basket-style (Chefman 6 Qt dual, Chefman 8 Qt)</th><th>Oven-style (Emeril 26QT French Door)</th></tr></thead><tbody>
<tr><td>How food goes in</td><td>Pull-out baskets; two small baskets (6 Qt model) or one large basket (8 Qt model)</td><td>French doors open to a rack cavity; fits a whole chicken or 12-inch pizza per listing</td></tr>
<tr><td>Capacity shape</td><td>6 Qt split as two 3-Qt baskets, or 8 Qt in a single basket</td><td>26QT (24.6 L) single cavity</td></tr>
<tr><td>Footprint (listing)</td><td>6 Qt: 13.38×11.81×10.63 in · 8 Qt: 12.75×13.5×10 in</td><td>16.9×15.8×14.8 in — the largest of the three</td></tr>
<tr><td>Weight (listing)</td><td>13.3 lb (6 Qt) · 12.8 lb (8 Qt)</td><td>26.5 lb — about double; plan where it lives</td></tr>
<tr><td>Cleanup</td><td>Nonstick, dishwasher-safe baskets (per listings)</td><td>Racks, pan, drip tray, crisper basket — more parts to wash</td></tr>
</tbody></table></div>
<p class="src">Sources: <a href="https://www.amazon.com/dp/B0CDY277D3" rel="nofollow noopener" target="_blank">B0CDY277D3</a> · <a href="https://www.amazon.com/dp/B08DKYBTPH" rel="nofollow noopener" target="_blank">B08DKYBTPH</a> · <a href="https://www.amazon.com/dp/B09B7SB46R" rel="nofollow noopener" target="_blank">B09B7SB46R</a> · checked 2026-11-20.</p>
<h2>Which shape fits your kitchen?</h2>
<ul>
<li><strong>Choose basket-style if</strong> you cook two foods at once (main + side), want the smallest footprint, and prefer fewer parts to wash.</li>
<li><strong>Choose oven-style if</strong> you need rack space for baking, rotisserie, or a full tray — and you have the counter depth for a 16.9-inch-deep unit.</li>
<li><strong>Either way,</strong> measure your counter and the cabinet above it before you order. Depth is where oven-style units surprise people.</li>
</ul>
<h2>Shop the comparison</h2>
<div class="grid">CARDS</div>
<h2>Frequently asked questions</h2>
<div class="faq">
<details><summary>Is a 6-quart dual basket the same as a 6-quart single basket?</summary><p>No. The Chefman 6 Qt splits capacity into two 3-Qt baskets with a Sync Finish option, so two foods can finish together. A single 6-Qt basket gives one larger space. Compare how you actually cook: two small batches, or one big one?</p></details>
<details><summary>Why is the oven-style model so much heavier?</summary><p>Per its listing it weighs 26.5 pounds, roughly double the basket models, because it is a full countertop oven with racks and accessories (7 included per listing). Weight matters for where it lives and how you clean around it.</p></details>
<details><summary>Do I need windows to see the food?</summary><p>The Chefman 6 Qt has easy-view windows on each basket; the Chefman 8 Qt listing does not mention windows. Windows help you check doneness without pulling the basket — a small thing that matters if you cook often.</p></details>
</div>
""",
        "faq": [
            ("Is a 6-quart dual basket the same as a 6-quart single basket?", "No. The Chefman 6 Qt splits capacity into two 3-Qt baskets with a Sync Finish option, so two foods can finish together. A single 6-Qt basket gives one larger space. Compare how you actually cook: two small batches, or one big one?"),
            ("Why is the oven-style model so much heavier?", "Per its listing it weighs 26.5 pounds, roughly double the basket models, because it is a full countertop oven with racks and accessories (7 included per listing). Weight matters for where it lives and how you clean around it."),
            ("Do I need windows to see the food?", "The Chefman 6 Qt has easy-view windows on each basket; the Chefman 8 Qt listing does not mention windows. Windows help you check doneness without pulling the basket — a small thing that matters if you cook often."),
        ],
    },
    {
        "path": "guides/air-fryer-capacity-checklist.html",
        "title": "A no-hype checklist for comparing air fryer capacity",
        "desc": "Quarts mean different things. Measure the food, not the marketing — a practical capacity checklist for the three air fryers in the shop.",
        "cluster": "Air Fryers",
        "body": """
<p>“6 quart,” “8 quart,” and “26 quart” sound like a simple ladder. They are not. A dual-basket 6 Qt is two 3-Qt spaces. An 8 Qt is one space. A 26QT oven is a rack cavity measured differently again. Use this checklist to compare capacity by the food you cook, not by the biggest number.</p>
<h2>The checklist</h2>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Check</th><th>How to do it</th></tr></thead><tbody>
<tr><td>1</td><td>Measure your most-cooked food</td><td>Put your usual tray, bird, or batch of fries on a ruler. Write down length × width × height.</td></tr>
<tr><td>2</td><td>Compare usable space, not quarts</td><td>Two 3-Qt baskets ≠ one 6-Qt basket. A 26QT oven fits a 12-inch pizza per listing — does that match your pans?</td></tr>
<tr><td>3</td><td>Check basket count</td><td>Dual basket (Chefman 6 Qt) = cook main + side together. Single basket (Chefman 8 Qt) = one larger batch.</td></tr>
<tr><td>4</td><td>Check depth, not just width</td><td>Emeril 26QT is 16.9 in deep. Measure counter depth + cabinet clearance before you buy.</td></tr>
<tr><td>5</td><td>Check weight &amp; storage</td><td>Emeril 26.5 lb vs. Chefman ~13 lb. Heavier ovens tend to stay in one spot — is that your plan?</td></tr>
<tr><td>6</td><td>Ignore “bought in past week”</td><td>Popularity badges change daily and are not on this site. Capacity is a measurement, not a vote.</td></tr>
</tbody></table></div>
<h2>Worked example (from the shop)</h2>
<div class="tablewrap"><table><thead><tr><th>Model</th><th>Capacity (listing)</th><th>What it means for dinner</th></tr></thead><tbody>
<tr><td>Chefman 6 Qt Dual (B0CDY277D3)</td><td>6 Qt as two 3-Qt baskets</td><td>Chicken in one basket, fries in the other; Sync Finish ends them together.</td></tr>
<tr><td>Chefman 8 Qt (B08DKYBTPH)</td><td>8 Qt single basket</td><td>One bigger batch — better for a single large item or a full basket of fries.</td></tr>
<tr><td>Emeril 26QT (B09B7SB46R)</td><td>26QT oven cavity</td><td>Rack cooking: whole chicken, 12-inch pizza, or a full tray of cookies per listing.</td></tr>
</tbody></table></div>
<p class="src">Sources: Amazon listings B0CDY277D3, B08DKYBTPH, B09B7SB46R · checked 2026-11-20.</p>
<h2>Shop by capacity</h2>
<div class="grid">CARDS</div>
<h2>Frequently asked questions</h2>
<div class="faq">
<details><summary>Is 8 quarts always bigger than 6 quarts?</summary><p>For usable single-batch space, yes — the 8 Qt is one basket. But the 6 Qt dual gives you two independent spaces, which can be more useful for a main + side meal. “Bigger” depends on the meal.</p></details>
<details><summary>How do I know if a 12-inch pizza fits?</summary><p>The Emeril listing says it fits a 12-inch pizza. Measure your actual pan (including handles) and compare it to the cavity dimensions on Amazon before you buy.</p></details>
</div>
""",
        "faq": [
            ("Is 8 quarts always bigger than 6 quarts?", "For usable single-batch space, yes — the 8 Qt is one basket. But the 6 Qt dual gives you two independent spaces, which can be more useful for a main + side meal. “Bigger” depends on the meal."),
            ("How do I know if a 12-inch pizza fits?", "The Emeril listing says it fits a 12-inch pizza. Measure your actual pan (including handles) and compare it to the cavity dimensions on Amazon before you buy."),
        ],
    },
    {
        "path": "guides/cleanup-and-counter-space.html",
        "title": "How to assess cleanup and counter-space trade-offs",
        "desc": "Dishwasher-safe parts, windows, and the inches your counter actually has. A practical cleanup and footprint guide for basket vs. oven-style fryers.",
        "cluster": "Air Fryers",
        "body": """
<p>Air fryers promise less oil. They do not promise less washing. Cleanup and counter space are where “great on paper” appliances end up in a closet. Compare these two things before you buy.</p>
<h2>Cleanup: count the parts</h2>
<div class="tablewrap"><table><thead><tr><th>Model</th><th>Parts to wash (per listing)</th><th>What to verify on Amazon</th></tr></thead><tbody>
<tr><td>Chefman 6 Qt Dual</td><td>Two nonstick baskets; dishwasher-safe per listing</td><td>“Dishwasher safe” wording + window seals (hand-wash vs. dishwasher)</td></tr>
<tr><td>Chefman 8 Qt</td><td>One nonstick basket; dishwasher-safe parts per listing</td><td>Same — confirm which parts are dishwasher-safe</td></tr>
<tr><td>Emeril 26QT</td><td>Rack, bake pan, drip tray, crisper basket, rotisserie spit, fetch tool (7 accessories)</td><td>Which accessories are dishwasher-safe; crumb-tray access</td></tr>
</tbody></table></div>
<p class="src">Sources: Amazon listings B0CDY277D3, B08DKYBTPH, B09B7SB46R · checked 2026-11-20.</p>
<h2>Counter space: measure depth first</h2>
<ul>
<li><strong>Chefman 6 Qt:</strong> 13.38 in deep × 11.81 in wide × 10.63 in tall.</li>
<li><strong>Chefman 8 Qt:</strong> 12.75 in deep × 13.5 in wide × 10 in tall.</li>
<li><strong>Emeril 26QT:</strong> 16.9 in deep × 15.8 in wide × 14.8 in tall — measure counter depth and the cabinet above it.</li>
</ul>
<p>Tip: tape the footprint on your counter with painter’s tape. Leave it for a day. If you keep moving it, it is too big for that spot.</p>
<h2>Windows and shake reminders: small features, daily use</h2>
<p>The Chefman 6 Qt has easy-view windows and a shake reminder; the 8 Qt has an LED shake reminder. These do not change capacity — they change how often you open the basket to check. If you cook daily, they matter. If you cook weekly, they do not.</p>
<h2>Shop with cleanup in mind</h2>
<div class="grid">CARDS</div>
<h2>Frequently asked questions</h2>
<div class="faq">
<details><summary>Are all parts dishwasher-safe?</summary><p>Listings say baskets/parts are dishwasher-safe, but always confirm which parts on Amazon — windows, seals, and accessories are often hand-wash only.</p></details>
<details><summary>How much counter depth do I need?</summary><p>At least the unit’s depth plus a few inches to pull baskets or open doors. The Emeril needs ~17 inches of depth; many counters are 24–25 inches deep, but cabinets above can be the real limit.</p></details>
</div>
""",
        "faq": [
            ("Are all parts dishwasher-safe?", "Listings say baskets/parts are dishwasher-safe, but always confirm which parts on Amazon — windows, seals, and accessories are often hand-wash only."),
            ("How much counter depth do I need?", "At least the unit’s depth plus a few inches to pull baskets or open doors. The Emeril needs ~17 inches of depth; many counters are 24–25 inches deep, but cabinets above can be the real limit."),
        ],
    },
    {
        "path": "guides/multi-function-appliance-questions.html",
        "title": "Questions to ask before buying a multi-function kitchen appliance",
        "desc": "24 functions sound great — until you ask which ones you will use weekly. Questions for oven-style fryers and wireless thermometers.",
        "cluster": "Multi-function",
        "body": """
<p>“24 cooking functions” and “5 sensors” are real specs — and easy to overvalue. Before you buy a multi-function appliance, ask which functions you will use every week, and what the extra complexity costs you in cleanup, counter space, and learning curve.</p>
<h2>Ask these seven questions</h2>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Question</th><th>Why it matters</th></tr></thead><tbody>
<tr><td>1</td><td>Which 3 functions will I use weekly?</td><td>Emeril lists 24 presets (air fry, bake, broil, dehydrate, roast, slow cook…). Name your three before you buy.</td></tr>
<tr><td>2</td><td>What do the accessories cost me?</td><td>7 accessories = 7 things to wash and store. Count them.</td></tr>
<tr><td>3</td><td>Does it replace something I own?</td><td>An oven-style fryer can replace a toaster oven — but only if it fits your counter (16.9 in deep).</td></tr>
<tr><td>4</td><td>For thermometers: probe or wireless?</td><td>ThermoMaven is a single instant-read probe (±0.5°F). CHEF iQ Sense is 3 wireless probes + hub with WiFi and app alerts.</td></tr>
<tr><td>5</td><td>What does “wireless” require?</td><td>CHEF iQ needs WiFi + app + hub charging. ThermoMaven needs a battery and works anywhere. Match to your cooking (grill vs. oven).</td></tr>
<tr><td>6</td><td>What is the heat limit?</td><td>CHEF iQ lists 1000°F heat-safe. Confirm the limit for your grill/smoker on Amazon.</td></tr>
<tr><td>7</td><td>What will I check on Amazon?</td><td>Price, availability, and “dishwasher-safe” wording live on Amazon. This site does not show prices (policy).</td></tr>
</tbody></table></div>
<p class="src">Sources: <a href="https://www.amazon.com/dp/B09B7SB46R" rel="nofollow noopener" target="_blank">B09B7SB46R</a> · <a href="https://www.amazon.com/dp/B0DHZTCNR5" rel="nofollow noopener" target="_blank">B0DHZTCNR5</a> · <a href="https://www.amazon.com/dp/B0DZFD6R9Z" rel="nofollow noopener" target="_blank">B0DZFD6R9Z</a> · checked 2026-11-20.</p>
<h2>Probe vs. wireless: the real choice</h2>
<div class="tablewrap"><table><thead><tr><th></th><th>ThermoMaven 1 Sec (instant-read)</th><th>CHEF iQ Sense Gen3 (wireless)</th></tr></thead><tbody>
<tr><td>How it works</td><td>Fold-out probe, 1-second reading, auto-rotate LED</td><td>3 ultra-thin probes in food + hub; WiFi to app; flip/rest reminders</td></tr>
<tr><td>Best for</td><td>Quick checks: steak, chicken, candy, everyday cooking</td><td>Long cooks: brisket, turkey, smoker — monitor from another room</td></tr>
<tr><td>Needs</td><td>Battery; no app</td><td>WiFi, app, hub charging; up to 70 hours per charge (listing)</td></tr>
<tr><td>Accuracy (listing)</td><td>±0.5°F, NIST &amp; NSF certified</td><td>4 internal sensors + ambient sensor; 5 sensors total</td></tr>
</tbody></table></div>
<h2>Shop the multi-function picks</h2>
<div class="grid">CARDS</div>
<h2>Frequently asked questions</h2>
<div class="faq">
<details><summary>Do I need 24 functions?</summary><p>Only if you will use them. Most households use 3–5 weekly. If your three are air fry, bake, and roast, a simpler basket model may serve you better than a 24-function oven.</p></details>
<details><summary>Is wireless always better than instant-read?</summary><p>No. Wireless wins for long, unattended cooks. Instant-read wins for quick, portable checks and needs no app or WiFi. They solve different problems.</p></details>
</div>
""",
        "faq": [
            ("Do I need 24 functions?", "Only if you will use them. Most households use 3–5 weekly. If your three are air fry, bake, and roast, a simpler basket model may serve you better than a 24-function oven."),
            ("Is wireless always better than instant-read?", "No. Wireless wins for long, unattended cooks. Instant-read wins for quick, portable checks and needs no app or WiFi. They solve different problems."),
        ],
    },
]

def guide_body(g):
    cards = "".join(product_card(p, depth=1) for p in PRODUCTS)
    body = g["body"].replace("CARDS", cards)
    return f"""
<section class="hero"><span class="kicker">Guide · {esc(g['cluster'])} · Question-shaped</span>
<h1>{esc(g['title'])}</h1>
<p class="lede">{esc(g['desc'])}</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY} · 4 min read · <a href="../verification.html">Sources</a></p>
</section>
<div class="guide-hero">{body}</div>
{capture_block(depth=1)}
"""

def faq_jsonld(g):
    items = []
    for q, a in g["faq"]:
        items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    return ('<script type="application/ld+json">' +
            json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}) + "</script>")

# ---------- DIRECTION ----------
def direction_body():
    return f"""
<section class="hero"><span class="kicker">Direction · Suggestions for review</span>
<h1>Direction: suggestions, open questions, and the path chooser</h1>
<p class="lede">Nothing here is implemented yet. Review the suggestions, answer the questions, and pick a path. Implementation starts only after you choose.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>

<h2>Suggestions (choose one path)</h2>
<div class="notice"><strong>How to choose:</strong> pick the path that matches your goal. Paths are mutually exclusive for the next build. Your choice is stored only in this browser (localStorage) — no data leaves the device.</div>
<form class="chooser" id="path-chooser">
<label><input type="radio" name="path" value="A"> <strong>Path A — Shop depth (recommended).</strong> Add one comparison page per category, real product photography (licensed), and a weekly guide cadence. Best for organic traffic from buyer questions.</label>
<label><input type="radio" name="path" value="B"> <strong>Path B — Content volume.</strong> Publish 2 guides/week from the question backlog, add seasonal clusters (grilling, holiday baking). Best for search coverage; slower per-page quality.</label>
<label><input type="radio" name="path" value="C"> <strong>Path C — Measurement first.</strong> Deploy the analytics endpoint, run the one-link Associates tests, and wait for first-party data before adding content. Best for data-driven decisions; slowest to grow.</label>
<button class="btn" type="submit">Save my choice (this browser only)</button>
<span id="chooser-msg" class="meta"></span>
</form>
<script>
document.getElementById('path-chooser').addEventListener('submit',function(e){{
  e.preventDefault();
  var v=document.querySelector('input[name=path]:checked');
  if(!v){{document.getElementById('chooser-msg').textContent='Pick a path first.';return;}}
  try{{localStorage.setItem('sk_path',v.value);}}catch(err){{}}
  document.getElementById('chooser-msg').textContent='Saved: Path '+v.value+' (stored in this browser only).';
}});
try{{var s=localStorage.getItem('sk_path');if(s){{var r=document.querySelector('input[name=path][value="'+s+'"]');if(r)r.checked=true;}}}}catch(err){{}}
</script>

<h2>Questions, information, and answers</h2>
<p>What we know, what we do not, and how to discover the missing pieces. Blank means unverified — never inferred.</p>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Question</th><th>What we know (with source)</th><th>What we do not know</th><th>How to discover it</th></tr></thead><tbody>
<tr><td>Q1</td><td>Is tracking ID {TAG} issued and active?</td><td>Shape matches abcd-20 pattern (S06).</td><td>Issued/active status — no public page confirms it (FLG-001).</td><td>Check Associates Central; record confirmation date.</td></tr>
<tr><td>Q2</td><td>Do the five short links resolve to the observed ASINs?</td><td>Prior sessions resolved them live 2026-11-17 (S14); listings confirm the ASINs exist (S09–S13).</td><td>Re-observation in this session (sandbox blocked — FLG-008).</td><td>Re-observe from unrestricted network; update observed_date.</td></tr>
<tr><td>Q3</td><td>Are link.amazon short links permitted Special Links?</td><td>Unresolved (FLG-003). Not claimed invalid.</td><td>Exact compliance status.</td><td>Confirm in Associates Central; keep short links out of reader buttons until confirmed.</td></tr>
<tr><td>Q4</td><td>What are the current prices?</td><td>Policy: do not display static prices (S02).</td><td>Current prices (intentionally blank — FLG-006).</td><td>Read on Amazon; or Creators/PA API with timestamp.</td></tr>
<tr><td>Q5</td><td>Which products convert?</td><td>Nothing — ledger is empty by design.</td><td>Clicks, orders, sessions (no first-party data yet).</td><td>Deploy endpoint + Associates Reports; fill ledger only from authorized reports.</td></tr>
<tr><td>Q6</td><td>Which guides get searched?</td><td>Four question-shaped guides published; RSS + sitemap live.</td><td>Search queries, traffic (no Search Console data yet).</td><td>Submit sitemap in Search Console; read queries monthly.</td></tr>
<tr><td>Q7</td><td>Which specs are wrong?</td><td>FLG-004 (ThermoMaven variant) + FLG-005 (Chefman model/temp) flagged.</td><td>Canonical model/temp for B08DKYBTPH; canonical ASIN for ThermoMaven.</td><td>Confirm on live listings + manufacturer pages.</td></tr>
<tr><td>Q8</td><td>What imagery can we use?</td><td>No Amazon images used (IP License, S02).</td><td>Licensed photography.</td><td>Commission/license photos; never scrape Amazon images.</td></tr>
</tbody></table></div>
<p class="src">Sources: S01–S15 on the <a href="verification.html">Verification</a> page. Flags: <a href="flagged-for-review.html">Flagged for Review</a>.</p>

<h2>Design-direction pack (for the next build prompt)</h2>
<ul>
<li><strong>Look:</strong> warm paper background, ink text, terracotta + green accents; product cards first, verification below the fold. No dark-mode dashboard, no chart-junk.</li>
<li><strong>Voice:</strong> human buyer questions as headlines; short answers; checklists over adjectives. No “AI-powered” hype on reader pages.</li>
<li><strong>Imagery:</strong> licensed lifestyle photos (counter, food, hands) + simple SVG icons. No Amazon product images, no logos.</li>
<li><strong>Seasons &amp; clusters:</strong> “Countertop Cooking” season; clusters “Air Fryers” and “Meat Thermometers”; seasonal angles (grilling, holiday baking) as guides, not banners.</li>
<li><strong>Findability:</strong> one sitemap, one RSS feed, question-shaped titles, FAQ schema, internal links from every guide to its category.</li>
</ul>
{capture_block()}
"""

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
<tr><td>Reader capture (SG-30)</td><td><span class="okpill">shipped (form)</span></td><td>Newsletter form on front page + guides; double opt-in via provider</td></tr>
<tr><td>Internal search</td><td><span class="okpill">shipped</span></td><td><a href="search.html">search.html</a> (client-side, no server)</td></tr>
</tbody></table></div>
{capture_block()}
"""

# ---------- ABOUT ----------
def about_body():
    return f"""
<section class="hero"><span class="kicker">About · Authorship &amp; method</span>
<h1>About ShopNow Kitchen: a publication, not a dashboard</h1>
<p class="lede">We compare countertop appliances on checkable specs and human buyer questions. Here is who writes, how we check, and what “published” means here.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<h2>Authorship</h2>
<p>Every page is bylined <strong>the ShopNow Kitchen Desk</strong> (editorial team). We do not invent personal credentials, test kitchens, or hands-on reviews. If we ever test a product, the page will say what was tested, when, and what was observed — with photos. Until then, we compare manufacturer/Amazon-listed specs and say so.</p>
<h2>Methodology</h2>
<ol>
<li>Start from the submitted link; record intent and observation in separate fields (never merged).</li>
<li>Confirm specs on Amazon’s own listing pages; link every table row to its source.</li>
<li>Leave unverified cells blank and flag them (see <a href="flagged-for-review.html">Flagged for Review</a>).</li>
<li>Run the compliance gate (<code>scripts/check_site.py</code>) before publishing.</li>
<li>Measure with the five defined events; fill the ledger only from first-party reports.</li>
</ol>
<h2>Brand, seasons, and clusters</h2>
<ul>
<li><strong>Brand:</strong> ShopNow Kitchen — warm paper, ink text, terracotta + green. No Amazon logos or product images.</li>
<li><strong>Season:</strong> “Countertop Cooking” (everyday meals). Seasonal angles (grilling, holiday baking) appear as guides, not banners.</li>
<li><strong>Clusters:</strong> <em>Air Fryers</em> (3 products, 3 guides) and <em>Meat Thermometers</em> (2 products, 1 guide). Every guide links to its category.</li>
</ul>
<h2>Publishing cadence</h2>
<p>New guides are added to the existing sitemap and RSS feed in the same build. The next topic is chosen from measured Search Console queries — not instinct — once Search Console data exists (see <a href="measurement.html">Measurement</a>).</p>
{capture_block()}
"""

# ---------- EXEC SUMMARY ----------
def exec_body():
    return f"""
<section class="hero"><span class="kicker">Executive summary</span>
<h1>Executive summary: five products, one shop, honest numbers</h1>
<p class="lede">ShopNow Kitchen is a publication front page for five Amazon products (3 air fryers, 2 meat thermometers) with tracking ID {TAG}. It leads with products, answers buyer questions, and keeps verification one click away — not in the way.</p>
<p class="meta">By the ShopNow Kitchen Desk · Updated {TODAY}</p></section>
<h2>What is live</h2>
<ul>
<li><strong>Shop:</strong> front page + 2 category pages + 5 product pages, all with Sponsored buy buttons (rel=sponsored) and disclosure above the fold.</li>
<li><strong>Guides:</strong> 4 question-shaped guides (basket vs. oven-style, capacity checklist, cleanup/counter-space, multi-function questions).</li>
<li><strong>Trust:</strong> verification register (intent vs. observed kept separate), 15-source register, 8 flagged items, compliance gate.</li>
<li><strong>Measurement:</strong> 5-event beacon + Worker code; empty campaign ledger; sitemap + RSS + internal search.</li>
</ul>
<h2>Key facts (all sourced)</h2>
<div class="tablewrap"><table><thead><tr><th>Fact</th><th>Value</th><th>Source</th></tr></thead><tbody>
<tr><td>Submitted links</td><td>5 link.amazon short links (9-char tokens)</td><td class="src"><a href="verification.html">Verification §1</a></td></tr>
<tr><td>Observed ASINs</td><td>B0CDY277D3 · B09B7SB46R · B08DKYBTPH · B0DHZTCNR5 · B0DZFD6R9Z</td><td class="src"><a href="verification.html">Verification §1–2</a></td></tr>
<tr><td>Intended ASINs</td><td>Blank (9-char tokens are not ASINs; nothing public binds them)</td><td class="src">S05 (ASIN = 10 chars)</td></tr>
<tr><td>Prices / ratings</td><td>Blank by policy + volatility</td><td class="src">S02 (FLG-006)</td></tr>
<tr><td>Tracking ID</td><td>{TAG} (as supplied; unconfirmed — FLG-001)</td><td class="src"><a href="flagged-for-review.html">FLG-001</a></td></tr>
<tr><td>Site URL</td><td>{SITE}</td><td class="src">S08</td></tr>
</tbody></table></div>
<h2>What happens next (needs your review)</h2>
<ol>
<li>Confirm tracking ID + run one-link Associates tests (FLG-001, FLG-002).</li>
<li>Re-observe redirects + resolve FLG-004/FLG-005 spec conflicts.</li>
<li>Deploy analytics endpoint; submit sitemap to Search Console.</li>
<li>Pick a path on the <a href="direction.html">Direction</a> page before the next build.</li>
</ol>
<div class="notice"><strong>No revenue forecast, no conversion score.</strong> The ledger is empty until first-party reports arrive. That is the honest starting point.</div>
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

# ---------- BUILD ----------
def main():
    pages = {}  # path -> html
    pages["index.html"] = page_html("index.html", "ShopNow Kitchen — Basket or oven-style? Compare before you buy.", "Five kitchen appliances compared on checkable specs: capacity, size, cleanup. No hype, no invented prices.", home_body())
    pages["air-fryers.html"] = page_html("air-fryers.html", "Air Fryers — Compare basket vs. oven-style", "Compare three air fryers: Chefman 6 Qt dual basket, Chefman 8 Qt, Emeril 26QT French Door. Capacity, size, cleanup.", category_body("Air Fryers", "Air Fryers: basket or oven-style?", "Three air fryers, two shapes. Compare capacity, footprint, and cleanup on the specs you can check.", '<li><a href="guides/basket-or-oven-style-air-fryer.html">Basket or oven-style: what should you compare?</a></li><li><a href="guides/air-fryer-capacity-checklist.html">Capacity checklist</a></li><li><a href="guides/cleanup-and-counter-space.html">Cleanup &amp; counter-space trade-offs</a></li>'))
    pages["thermometers.html"] = page_html("thermometers.html", "Meat Thermometers — Instant-read vs. wireless", "Compare ThermoMaven 1 Sec instant-read and CHEF iQ Sense Gen3 wireless (3 probes, WiFi). Accuracy, range, needs.", category_body("Meat Thermometers", "Meat Thermometers: probe or wireless?", "One instant-read probe and one 3-probe wireless system. Compare accuracy, range, and what each needs to work.", '<li><a href="guides/multi-function-appliance-questions.html">Questions before buying a multi-function appliance</a></li>'))
    for p in PRODUCTS:
        pages[p["page"]] = page_html(p["page"], f"{p['short_label']} — specs & comparison | ShopNow Kitchen", f"{p['title']}. Specs from Amazon's listing, sources linked. Sponsored link to Amazon.", product_body(p))
    for g in GUIDES:
        pages[g["path"]] = page_html(g["path"], g["title"] + " | ShopNow Kitchen", g["desc"], guide_body(g), page_type="guide", extra_head=faq_jsonld(g))
    pages["direction.html"] = page_html("direction.html", "Direction — Suggestions, questions, and the path chooser", "Review suggestions, open questions, and pick the next build path. Nothing is implemented until you choose.", direction_body())
    pages["verification.html"] = page_html("verification.html", "Verification — Sources, intent record, and specs", "Every table row has a source link or is blank and flagged. Product-intent record with intended vs. observed kept separate.", verification_body())
    pages["flagged-for-review.html"] = page_html("flagged-for-review.html", "Flagged for Review — What we could not verify", "Eight flagged items that do not block the site. Review them after the site is live and request changes.", flagged_body())
    pages["disclosure.html"] = page_html("disclosure.html", "Disclosure — How this site earns money", "As an Amazon Associate I earn from qualifying purchases. Sponsored links, no displayed prices, privacy.", disclosure_body())
    pages["measurement.html"] = page_html("measurement.html", "Measurement — Five events and an empty ledger", "Privacy-preserving click counter, self-hosted endpoint, five defined events, empty campaign ledger.", measurement_body())
    pages["about.html"] = page_html("about.html", "About — Authorship, method, seasons and clusters", "Who writes ShopNow Kitchen, how we check, and what published means here.", about_body())
    pages["executive-summary.html"] = page_html("executive-summary.html", "Executive summary — Five products, one shop", "What is live, key sourced facts, and what happens next.", exec_body())
    pages["search.html"] = page_html("search.html", "Search — ShopNow Kitchen", "Client-side search across products and guides.", search_body())
    pages["404.html"] = page_html("404.html", "Not found | ShopNow Kitchen", "That page is not on the counter.", notfound_body())

    # ItemList JSON-LD for home
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + p["page"], "name": p["short_label"]} for i, p in enumerate(PRODUCTS)]
    pages["index.html"] = pages["index.html"].replace("</head>", '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": items}) + "</script></head>")

    for path, content in pages.items():
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    # sitemap.xml
    urls = []
    for path in sorted(pages.keys()):
        if path == "404.html":
            continue
        urls.append(f"  <url><loc>{SITE}{path}</loc><lastmod>{TODAY}</lastmod></url>")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    # robots.txt
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")

    # feed.xml (RSS 2.0)
    feed_items = []
    for g in GUIDES:
        feed_items.append(f"    <item><title>{esc(g['title'])}</title><link>{SITE}{g['path']}</link><guid>{SITE}{g['path']}</guid><description>{esc(g['desc'])}</description><pubDate>{TODAY}T00:00:00Z</pubDate></item>")
    for p in PRODUCTS:
        feed_items.append(f"    <item><title>{esc(p['short_label'])}</title><link>{SITE}{p['page']}</link><guid>{SITE}{p['page']}</guid><description>{esc(p['title'])}</description><pubDate>{TODAY}T00:00:00Z</pubDate></item>")
    feed = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
            f"  <title>ShopNow Kitchen</title><link>{SITE}</link><description>Basket or oven-style? Compare before you buy. Capacity, size, cleanup — no hype.</description>\n"
            + "\n".join(feed_items) + "\n</channel></rss>\n")
    with open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(feed)

    # search index
    idx = []
    for p in PRODUCTS:
        idx.append({"title": p["short_label"], "url": p["page"], "kind": "Product · " + p["category"], "text": p["title"] + " " + p["brand"] + " " + p["model"] + " " + p["capacity"] + " " + p["observed_asin"]})
    for g in GUIDES:
        idx.append({"title": g["title"], "url": g["path"], "kind": "Guide · " + g["cluster"], "text": g["desc"]})
    for path, title in [("air-fryers.html", "Air Fryers"), ("thermometers.html", "Meat Thermometers"), ("direction.html", "Direction"), ("verification.html", "Verification"), ("measurement.html", "Measurement"), ("about.html", "About"), ("executive-summary.html", "Executive summary")]:
        idx.append({"title": title, "url": path, "kind": "Page", "text": title + " ShopNow Kitchen"})
    with open(os.path.join(ROOT, "assets", "search-index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2)

    print(f"Built {len(pages)} pages + sitemap + feed + search index.")

if __name__ == "__main__":
    main()
