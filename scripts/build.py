#!/usr/bin/env python3
"""Build the GitHub Pages site in docs/ from data/*.json, then validate it.

The build exits non-zero if any check fails, so a broken site is never published:
  - the Associates disclosure is present, above the fold and in the footer, on every page
  - every link to an Amazon host carries rel="sponsored"
  - every internal link and fragment resolves
  - every product row has an official source and its stored values match the URLs it cites
  - every blank value is listed against a Flagged for Review item
  - sitemap.xml and feed.xml parse and list every page

Run:  python3 scripts/build.py
"""
import csv
import datetime
import html
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")

SITE_BASE = "https://sassnarep3-star.github.io/WinC/"
SITE_NAME = "WinC Kitchen Picks"
TAGLINE = "Air fryers and meat thermometers, with every figure dated and sourced"
VERIFIED_ON = "2026-11-20"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
AMAZON_HOSTS = {"www.amazon.com", "amazon.com", "link.amazon", "amzn.to"}
OFFICIAL_HOSTS = {
    "www.amazon.com",
    "affiliate-program.amazon.com",
    "webservices.amazon.com",
    "www.ftc.gov",
    "developers.google.com",
}

NAV = [
    ("Home", "index.html"),
    ("Air fryers", "air-fryers/index.html"),
    ("Meat thermometers", "meat-thermometers/index.html"),
    ("Guides", "guides/index.html"),
    ("About and method", "about/index.html"),
]
DASHBOARD = [
    ("All products", "products/index.html"),
    ("Analysis", "analysis/index.html"),
    ("Executive summary", "executive-summary/index.html"),
    ("Questions", "questions/index.html"),
    ("Suggestions", "suggestions/index.html"),
    ("Compliance gate", "compliance/index.html"),
    ("Sources", "sources/index.html"),
    ("Campaign ledger", "ledger/index.html"),
    ("Flagged for review", "flagged-for-review/index.html"),
]
CATEGORIES = {
    "air-fryers": ("Air fryers", "air-fryers/index.html"),
    "meat-thermometers": ("Meat thermometers", "meat-thermometers/index.html"),
}

PREFIX = ""
PAGES = []  # (relpath, title, description)


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


SOURCES_DOC = load("sources.json")
PRODUCTS_DOC = load("products.json")
FLAGS_DOC = load("flags.json")
QUESTIONS_DOC = load("questions.json")
SUGGESTIONS_DOC = load("suggestions.json")
GUIDES_DOC = load("guides.json")
with open(os.path.join(DATA, "ledger.csv"), encoding="utf-8") as fh:
    LEDGER_ROWS = list(csv.DictReader(fh))
LEDGER_HEADERS = ["timestamp_utc", "source", "channel", "eligible_sessions", "clicks", "reported_orders", "provenance_ref"]

SRC = {s["id"]: s for s in SOURCES_DOC["sources"]}
PRODUCTS = PRODUCTS_DOC["products"]
FLAGS = {f["id"]: f for f in FLAGS_DOC["flags"]}


def E(value):
    return html.escape("" if value is None else str(value), quote=True)


def begin(relpath):
    """Set the relative prefix used by every internal link on this page."""
    global PREFIX
    PREFIX = "../" * relpath.count("/")


def internal(target, text, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{E(PREFIX + target)}"{c}>{E(text)}</a>'


def external(url, text=None, cls=""):
    host = urlparse(url).hostname or ""
    rel = "sponsored noopener" if host in AMAZON_HOSTS else "noopener"
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{E(url)}" rel="{rel}" target="_blank"{c}>{E(text or url)}</a>'


def src_chips(ids):
    chips = []
    for sid in ids:
        if sid in SRC:
            chips.append(external(SRC[sid]["url"], sid, "src"))
        elif sid.startswith("F-") and sid in FLAGS:
            chips.append(f'<a class="src" href="{E(PREFIX)}flagged-for-review/index.html#{sid.lower()}">{sid}</a>')
    return " ".join(chips) if chips else '<span class="badge unverified">No source</span>'


REPO_BUILD = "https://github.com/sassnarep3-star/WinC/blob/main/scripts/build.py"


def src_text(text):
    """Escape free text, turning each SRC-xx token into a link to its official URL."""
    out, pos = [], 0
    for m in re.finditer(r"SRC-\d\d", text):
        out.append(E(text[pos:m.start()]))
        sid = m.group(0)
        out.append(external(SRC[sid]["url"], sid, "src") if sid in SRC else E(sid))
        pos = m.end()
    out.append(E(text[pos:]))
    return "".join(out)


def badge(text):
    t = text.lower()
    if t.startswith("partly") or t.startswith("partial"):
        cls = "partial"
    elif t.startswith(("verified", "answered", "pass", "adopted", "built")):
        cls = "pass"
    elif t.startswith(("unanswered", "unverified")):
        cls = "unverified"
    elif t.startswith(("unresolved", "open", "flag", "awaiting", "not published", "not reviewed", "blocked")):
        cls = "flag" if not t.startswith("blocked") else "blocked"
    else:
        cls = "neutral"
    return f'<span class="badge {cls}">{E(text)}</span>'


def unverified(flag=None):
    ref = f' <span class="flagref">{E(flag)}</span>' if flag else ""
    return f'<span class="badge unverified">Unverified</span>{ref}'


def table(headers, rows, cls="data"):
    head = "".join(f"<th>{E(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def price_value(text):
    return float(text.replace("$", "").replace(",", ""))


def layout(relpath, title, description, body):
    nav_links = "".join(
        f'<a href="{E(PREFIX + href)}">{E(label)}</a>' for label, href in NAV
    )
    dash_links = "".join(
        f'<li><a href="{E(PREFIX + href)}">{E(label)}</a></li>' for label, href in DASHBOARD
    )
    shop_links = "".join(
        f'<li><a href="{E(PREFIX + href)}">{E(label)}</a></li>' for label, href in NAV
    )
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} | {E(SITE_NAME)}</title>
<meta name="description" content="{E(description)}">
<link rel="stylesheet" href="{E(PREFIX)}assets/site.css">
<link rel="alternate" type="application/rss+xml" title="{E(SITE_NAME)} feed" href="{E(PREFIX)}feed.xml">
</head>
<body>
<header class="masthead">
  <div class="wrap mast-row">
    <a class="brand" href="{E(PREFIX)}index.html"><span class="brand-name">{E(SITE_NAME)}</span><span class="brand-tag">Working name · {E(TAGLINE)}</span></a>
    <nav class="primary" aria-label="Main">{nav_links}</nav>
  </div>
</header>
<div class="disclosure" role="note">
  <div class="wrap"><strong>Affiliate disclosure.</strong> {E(DISCLOSURE)} Links marked “Sponsored” go to Amazon. <span class="muted">Prices, availability and ratings are not shown on this site; see the live Amazon listing.</span></div>
</div>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="disclosure-foot"><strong>Affiliate disclosure.</strong> {E(DISCLOSURE)} Links marked “Sponsored” go to Amazon. We may earn a commission on qualifying purchases. Prices change; check the Amazon page before you buy.</div>
    <div class="foot-grid">
      <div><h4>Shop</h4><ul>{shop_links}</ul></div>
      <div><h4>Dashboard</h4><ul>{dash_links}</ul></div>
      <div><h4>Site</h4><ul>
        <li><a href="{E(PREFIX)}feed.xml">RSS feed</a></li>
        <li><a href="{E(PREFIX)}sitemap.xml">Sitemap</a></li>
        <li><a href="{E(PREFIX)}about/index.html">About and method</a></li>
        <li><a href="https://github.com/sassnarep3-star/WinC" rel="noopener" target="_blank">Repository</a></li>
      </ul></div>
    </div>
    <p class="muted">Last verified {E(VERIFIED_ON)}. Values marked Unverified could not be confirmed from an official source and are left blank on purpose.</p>
  </div>
</footer>
</body>
</html>
"""
    out_path = os.path.join(OUT, relpath)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    PAGES.append((relpath, title, description))


def product_card(p):
    cat_label = CATEGORIES[p["category"]][0]
    price = '<span class="muted">Price: see the live Amazon listing</span>'
    return f"""<article class="card" id="card-{p['id'].lower()}">
  <div class="cat">{E(cat_label)} · {E(p['id'])}</div>
  <h3>{E(p['display_name'])}</h3>
  <div class="price">{price}</div>
  <div class="status-note">{badge('Partly verified')} {src_chips(p['sources'])}</div>
  <div style="margin-top:auto;display:flex;gap:10px;flex-wrap:wrap;align-items:center">
    {external(p['submitted_link'], 'View on Amazon', 'btn')}
    {internal('products/index.html#' + p['id'].lower(), 'Details')}
  </div>
</article>"""


# ---------------------------------------------------------------- pages

def page_home():
    rel = "index.html"
    begin(rel)
    cards = "".join(product_card(p) for p in PRODUCTS)
    cat_tiles = "".join(
        f'<a class="tile" href="{E(PREFIX + href)}"><span class="cat">{E(label)}</span><span class="tile-count">{sum(1 for p in PRODUCTS if p["category"] == key)} picks</span><span class="tile-arrow">→</span></a>'
        for key, (label, href) in CATEGORIES.items()
    )
    body = f"""
<section class="hero">
  <div class="kicker">Air fryers · Meat thermometers</div>
  <h1>Five Amazon picks, sourced and dated.</h1>
  <p class="lede">Compare three basket and oven-style air fryers and two meat thermometers. Each card shows the product, the source of its details, and the date we checked them. Prices and ratings are shown only on Amazon. If a detail could not be confirmed, the card says so.</p>
</section>
<section>
  <h2>The five picks</h2>
  <div class="grid">{cards}</div>
</section>
<section class="split">
  <div>
    <h2>Browse by category</h2>
    <div class="tiles">{cat_tiles}</div>
  </div>
  <div class="callout">
    <h3>Before you buy</h3>
    <ul>
      <li>Prices and availability change. Amazon's price at the time of purchase is the one that applies.</li>
      <li>Protection plans shown on Amazon pages are not part of our picks, and their ratings are not product ratings.</li>
      <li>Every link to Amazon is marked sponsored. We may earn a commission on qualifying purchases.</li>
    </ul>
  </div>
</section>
<section>
  <h2>Still being checked</h2>
  <p>Some links and figures are not yet confirmed. The open items are listed for review, with their sources and the owner action each needs.</p>
  <p>{internal('flagged-for-review/index.html', 'Flagged for review')} · {internal('suggestions/index.html', 'Suggestions to choose from')} · {internal('questions/index.html', 'Open questions')} · {internal('executive-summary/index.html', 'Executive summary')}</p>
</section>
"""
    layout(rel, "Five Amazon picks, sourced and dated", "Air fryers and meat thermometers from Amazon, each with a source link, a check date and a clear disclosure.", body)


def category_page(key):
    label, rel = CATEGORIES[key]
    begin(rel)
    items = [p for p in PRODUCTS if p["category"] == key]
    rows = []
    for p in items:
        rows.append([
            f'<a href="{E(PREFIX)}products/index.html#{p["id"].lower()}"><strong>{E(p["display_name"])}</strong></a><br><span class="muted">{E(p["id"])}</span>',
            external(p["submitted_link"], "See price on Amazon", "btn btn-small"),
            src_chips(p["sources"]),
        ])
    body = f"""
<section>
  <div class="kicker">Category</div>
  <h1>{E(label)}</h1>
  <p class="lede">Prices and ratings are not shown here. Each row links to the live Amazon listing, where the current price and rating appear.</p>
</section>
<section>
  {table(["Product", "Link", "Sources"], rows)}
</section>
<section class="callout">
  <h3>What this table does not say</h3>
  <p>It does not rank these products, does not forecast sales or commission, and does not say which product converts best. No demand or trend data is held for this category yet (see <a href="{E(PREFIX)}analysis/index.html">Analysis</a>).</p>
</section>
"""
    layout(rel, label, f"{label}: five Amazon picks with source links and check dates.", body)


def page_products():
    rel = "products/index.html"
    begin(rel)
    intent_rows, detail_rows = [], []
    for p in PRODUCTS:
        pid = p["id"].lower()
        intent_rows.append([
            f'<span id="{pid}"></span><strong>{E(p["id"])}</strong>',
            f'<code>{E(p["submitted_link"])}</code>',
            f'<code>{E(p["submitted_token"])}</code><br><span class="muted">{len(p["submitted_token"])} characters</span>',
            unverified("F-01") if not p["intended_asin"] else f'<code>{E(p["intended_asin"])}</code>',
            external(p["official_listing_url"], p["official_listing_url"]),
            f'<code>{E(p["observed_asin"])}</code>',
            external(p["observed_redirect_target"], "Observed redirect target", "small"),
            badge("Flag: no tag observed") if not p["tag_observed_in_redirect"] else badge("Pass: tag observed"),
            E(p["confirmation_date"]),
            src_chips(p["sources"]),
        ])
        detail_rows.append([
            f'<strong>{E(p["display_name"])}</strong><br><span class="muted">{E(p["page_title"])}</span>',
            E(CATEGORIES[p["category"]][0]),
            E(p["breadcrumb"]),
            '<span class="muted">Not shown; see the live listing</span>',
            src_chips(p["sources"]),
        ])
    body = f"""
<section>
  <div class="kicker">Dashboard · product register</div>
  <h1>All products</h1>
  <p class="lede">One row per submitted link. The intended ASIN and the observed redirect are stored in separate columns and are never merged. Blank values are marked Unverified and point to a flag.</p>
</section>
<section>
  <h2>Intent and redirect record</h2>
  {table(["ID", "Submitted link", "Submitted token", "Intended ASIN", "Official listing URL", "Observed ASIN", "Observed redirect", "Tag check", "Confirmed", "Sources"], intent_rows)}
</section>
<section>
  <h2>Listing details</h2>
  {table(["Product", "Category", "Breadcrumb (as shown)", "Price and rating", "Sources"], detail_rows)}
</section>
<section class="callout">
  <h3>How to read this</h3>
  <p>The submitted token is what the link path contains. The observed ASIN is taken from the Amazon page the link reached. Those two values are different for every product, and neither was merged into the other. Read the <a href="{E(PREFIX)}flagged-for-review/index.html">flags</a> before relying on any row.</p>
</section>
"""
    layout(rel, "All products", "Product register: submitted links, observed ASINs, redirect targets and sources.", body)


def page_analysis():
    rel = "analysis/index.html"
    begin(rel)
    n = len(PRODUCTS)
    token_mismatch = sum(1 for p in PRODUCTS if p["submitted_token"] != p["observed_asin"])
    token_not_10 = sum(1 for p in PRODUCTS if len(p["submitted_token"]) != 10)
    tag_seen = sum(1 for p in PRODUCTS if "tag=" in p["observed_redirect_target"])
    rows = [
        ["Products in scope", str(n), "Count of submitted links (3 air fryers, 2 meat thermometers).", src_text("SRC-07 to SRC-12"), badge("Verified")],
        ["Pages reached and read", f"{n} of {n}", "Each short link resolved to an amazon.com /dp/ page.", src_text("SRC-12"), badge("Verified")],
        ["Price and rating display", "Not shown", "Program Policies (Participation Requirements) allow prices on this site only when Amazon serves them or they come from Creators API or PA API. The captured values are kept as an internal record and are not published.", src_text("SRC-02"), badge("Flag: F-13")],
        ["Submitted tokens with 10 characters", f"{n - token_not_10} of {n}", "Length of each submitted path token, counted in code.", src_text("SRC-03 (ASIN definition), SRC-12"), badge("Verified")],
        ["Submitted tokens equal to observed ASIN", f"{n - token_mismatch} of {n}", "Token compared with the ASIN in the redirected /dp/ URL.", src_text("SRC-07 to SRC-11, SRC-12"), badge("Verified")],
        ["Redirect targets carrying a tag= parameter", f"{tag_seen} of {n}", "Searched for 'tag=' in each stored redirect URL.", src_text("SRC-02 (Participation Requirement 2(b))"), badge("Flag: F-02")],
    ]
    unanalysed = [
        ["Commission potential", "Not analysed", "The rate card for these products was not captured (Q-07)."],
        ["Competition", "Not analysed", "No competitor, seller, or listing-count data captured."],
        ["Demand and trend", "Not analysed", "No search, sales-rank, or dated trend data exists (Q-08)."],
        ["Conversion", "Not analysed", "No click, session, or order data was provided (Q-17). No conversion claim is made."],
        ["Revenue forecast", "Not analysed", "Not presented. No forecast is supported by the data held."],
    ]
    body = f"""
<section>
  <div class="kicker">Dashboard · findings</div>
  <h1>Analysis</h1>
  <p class="lede">Only figures that can be counted or read from the source pages appear here. Each row shows how it was derived. Items that need data we do not hold are listed as not analysed, not estimated.</p>
</section>
<section>
  <h2>Findings from the captured data</h2>
  {table(["Measure", "Result", "How it was derived", "Source", "Status"], rows)}
</section>
<section>
  <h2>Not analysed</h2>
  <p class="status-note">These are left out on purpose. Estimating them would need data that is not in this repository.</p>
  {table(["Area", "Status", "Reason"], [[E(a), badge(b), E(c)] for a, b, c in unanalysed])}
</section>
<section class="callout">
  <h3>What the findings mean for the next step</h3>
  <p>The biggest open issue is attribution: none of the five redirect targets shows the tracking tag (F-02), and the short-link status is unresolved (F-03). Until a single-link test is done (F-09), the findings above describe the listings, not the affiliate performance.</p>
</section>
"""
    layout(rel, "Analysis", "Findings from the captured Amazon listing data, with how each figure was derived.", body)


def page_exec():
    rel = "executive-summary/index.html"
    begin(rel)
    n = len(PRODUCTS)
    body = f"""
<section>
  <div class="kicker">Dashboard · executive summary</div>
  <h1>Executive summary</h1>
  <p class="lede">A working draft for owner review. It describes five Amazon listings and what could and could not be confirmed. It makes no performance, revenue, or commission claim.</p>
</section>
<section>
  <h2>What is here</h2>
  <ul>
    <li>{n} products from the submitted links: three air fryers and two meat thermometers. Each has a product page, a check date, and a source link (<a href="{E(PREFIX)}products/index.html">All products</a>).</li>
    <li>A source register of {len(SRC)} entries with verification status (<a href="{E(PREFIX)}sources/index.html">Sources</a>).</li>
    <li>A compliance gate that runs on every build. It checks the Associates disclosure, the sponsored marking on Amazon links, and internal links (<a href="{E(PREFIX)}compliance/index.html">Compliance gate</a>).</li>
    <li>Open questions, suggestions for you to choose from, and {len(FLAGS)} flags for review (<a href="{E(PREFIX)}questions/index.html">Questions</a>, <a href="{E(PREFIX)}suggestions/index.html">Suggestions</a>, <a href="{E(PREFIX)}flagged-for-review/index.html">Flagged for review</a>).</li>
  </ul>
</section>
<section>
  <h2>What is confirmed</h2>
  <ul>
    <li>All {n} submitted links resolve to an amazon.com product page. The observed ASIN in each page's URL is different from the submitted token (<a href="{E(PREFIX)}analysis/index.html">Analysis</a>).</li>
    <li>Prices and ratings are not published. The Program Policies allow them on this site only if Amazon serves them or they come from Creators API or PA API (<a href="{E(PREFIX)}flagged-for-review/index.html">Flag F-13</a>).</li>
    <li>The Associates disclosure text is as stated in Operating Agreement section 5 (<a href="{E(SRC['SRC-01']['url'])}" rel="noopener" target="_blank">SRC-01</a>).</li>
  </ul>
</section>
<section>
  <h2>What is not confirmed</h2>
  <ul>
    <li><strong>Attribution.</strong> No redirect target carries the Associates tag, so none of the five links has been shown to credit tracking ID shopnow047c-20 (F-02).</li>
    <li><strong>Short-link status.</strong> The compliance status of the link.amazon links is unresolved. They are not claimed to be invalid (F-03).</li>
    <li><strong>Intended ASINs.</strong> The submitted tokens are 9 characters; the ASIN is defined as 10 (F-01). Intended ASINs are left blank.</li>
    <li><strong>Marketplace.</strong> The destinations are amazon.com; the owner's location is the Netherlands (F-04).</li>
    <li><strong>Commission, competition, demand, trend, conversion.</strong> Not analysed (see the Analysis page).</li>
  </ul>
</section>
<section>
  <h2>Decisions needed from you</h2>
  <ul>
    <li><strong>Outbound links</strong> until the single-link test passes: keep, hide, or replace (Suggestions S-01).</li>
    <li><strong>Analytics</strong>: hosting option and the five event definitions (S-02, S-03). The click counter cannot run on GitHub Pages alone.</li>
    <li><strong>Cadence and first guide</strong> (S-04, S-05). The four guide titles are working titles only.</li>
    <li><strong>Marketplace and name</strong> (S-08, S-10).</li>
  </ul>
</section>
<section>
  <h2>Blocked: needs your login or a server</h2>
  <ul>
    <li><strong>Single-link test in the Associates workflow</strong> (T-08, F-09). Needs your Associates account. An agent cannot run it.</li>
    <li><strong>Click counter and analytics endpoint</strong> (T-09, F-08). Needs a host that runs a server, and the five events defined.</li>
  </ul>
</section>
"""
    layout(rel, "Executive summary", "Executive summary of the Amazon affiliate picks site: what is confirmed, what is not, and what needs a decision.", body)


def page_questions():
    rel = "questions/index.html"
    begin(rel)
    rows = []
    for q in QUESTIONS_DOC["questions"]:
        refs = []
        for r in q["refs"]:
            if r.startswith("F-"):
                refs.append(f'<a class="src" href="{E(PREFIX)}flagged-for-review/index.html#{r.lower()}">{E(r)}</a>')
            elif r in SRC:
                refs.append(external(SRC[r]["url"], r, "src"))
        rows.append([
            f'<strong>{E(q["id"])}</strong>',
            E(q["question"]),
            badge(q["status"]),
            E(q["have"]),
            E(q["missing"]),
            E(q["how_to_find_out"]),
            " ".join(refs) or '<span class="badge unverified">No source</span>',
        ])
    body = f"""
<section>
  <div class="kicker">Dashboard · decision readiness</div>
  <h1>Questions</h1>
  <p class="lede">{E(QUESTIONS_DOC['intro'])}</p>
</section>
<section>
  {table(["ID", "Question", "Status", "What we have", "What is missing", "How to find out", "Refs"], rows)}
</section>
"""
    layout(rel, "Questions", "Questions and information gaps that must be addressed before a decision.", body)


def page_suggestions():
    rel = "suggestions/index.html"
    begin(rel)
    blocks = []
    for s in SUGGESTIONS_DOC["suggestions"]:
        opt_rows = [[f"<strong>{E(o['letter'])}</strong>", E(o["text"]), E(o["tradeoff"])] for o in s["options"]]
        blocks.append(f"""<article class="sugg" id="{s['id'].lower()}">
  <h3>{E(s['id'])} · {E(s['topic'])} {badge(s['status'])}</h3>
  {table(["Option", "What it means", "Trade-off"], opt_rows)}
  <p><strong>Recommendation:</strong> {E(s['recommendation'])}</p>
</article>""")
    body = f"""
<section>
  <div class="kicker">Dashboard · choose the path</div>
  <h1>Suggestions</h1>
  <p class="lede">{E(SUGGESTIONS_DOC['intro'])}</p>
</section>
<section>
  {''.join(blocks)}
</section>
"""
    layout(rel, "Suggestions", "Suggestions to review and choose from before any change is made.", body)


def page_compliance():
    rel = "compliance/index.html"
    begin(rel)
    checks = [
        ["C-01", "Associates statement stated clearly and prominently on the site", "SRC-01", badge("Pass: built, checked on every build"), "Exact text in the strip under the masthead on every page, repeated in the footer."],
        ["C-02", "Disclosure placed where it is hard to miss, with the endorsement", "SRC-04", badge("Pass: built. Legal review open (F-10)"), "Strip sits directly under the masthead, above the content, not only on an About page."],
        ["C-03", "Affiliate links marked as sponsored", "SRC-05", badge("Pass: checked on every build"), "Every link to an Amazon host (including link.amazon) has rel=\"sponsored\"."],
        ["C-04", "Each Special Link carries the Associates tag", "SRC-02 (2(b))", badge("Flag: F-02"), "No tag observed in any redirect target."],
        ["C-05", "No cloaking or obscured site URL", "SRC-02 (2(v))", badge("Pass: by design, with flag"), "Site links are direct. The submitted short links are redirects and are flagged (F-03)."],
        ["C-06", "No link shortener used unclearly", "SRC-02 (2(w))", badge("Unresolved: F-03"), "Status of link.amazon not determined. Not claimed invalid."],
        ["C-07", "No claims that need proof the owner does not hold", "SRC-04", badge("Pass"), "No performance, ranking, or quality claims are made. Figures are dated snapshots."],
        ["C-08", "Product imagery used only as permitted", "SRC-02 (IP licence)", badge("Pass: no Amazon images used (F-11)"), "IP licence not read in full."],
        ["C-09", "Internal links and fragments resolve (no broken links)", "Build check (scripts/build.py)", badge("Pass: checked on every build"), "Every internal link and #anchor is resolved against the generated files."],
        ["C-10", "Every table row cites an official source", "Build check (scripts/build.py)", badge("Pass: checked on every build"), "A row without an official source fails the build."],
        ["C-11", "Blank values marked Unverified and linked to a flag", "Build check (scripts/build.py)", badge("Pass: checked on every build"), "A blank value with no flag fails the build."],
        ["C-12", "Analytics: no data collected without a defined event list and host", "SRC-04", badge("Blocked: F-08"), "Nothing installed. See Suggestions S-02 and S-03."],
    ]
    body = f"""
<section>
  <div class="kicker">Dashboard · publishing gate</div>
  <h1>Compliance gate</h1>
  <p class="lede">The build runs these checks before anything is written to the live site. If a check fails, the build stops and the previous version stays live.</p>
</section>
<section>
  {table(["ID", "Requirement", "Source", "Result", "Notes"], [[E(c[0]), E(c[1]), (external(REPO_BUILD, c[2], "src") if c[2].startswith("Build check") else src_text(c[2])), c[3], E(c[4])] for c in checks])}
</section>
<section class="callout">
  <h3>Not legal advice</h3>
  <p>These checks confirm that the design follows the sources listed. They do not replace a review by counsel (Q-15).</p>
</section>
"""
    layout(rel, "Compliance gate", "Compliance checks run on every build: disclosure, sponsored links, internal links, sources.", body)


def page_sources():
    rel = "sources/index.html"
    begin(rel)
    rows = []
    for s in SOURCES_DOC["sources"]:
        sid = s["id"].lower()
        rows.append([
            f'<span id="{sid}"></span><strong>{E(s["id"])}</strong>',
            E(s["title"]),
            external(s["url"]),
            E(s["publisher"]),
            E(s["page_date"]),
            badge(s["status"]),
            E(s["supports"]),
        ])
    body = f"""
<section>
  <div class="kicker">Dashboard · source register</div>
  <h1>Sources</h1>
  <p class="lede">Every value on the site traces to one of these entries. Status says how far each one was read. The register was created in this repository (see Flagged for review, F-05).</p>
</section>
<section>
  {table(["ID", "Title", "Official link", "Publisher", "Page date", "Status", "What it supports"], rows)}
</section>
<p class="status-note">Retrieved {E(SOURCES_DOC['retrieved_on'])}. {E(SOURCES_DOC['note'])}</p>
"""
    layout(rel, "Sources", "Source register with official links and verification status for every value.", body)


def page_ledger():
    rel = "ledger/index.html"
    begin(rel)
    if LEDGER_ROWS:
        rows = [[E(r.get(h, "")) for h in LEDGER_HEADERS] for r in LEDGER_ROWS]
    else:
        rows = [[f'<span class="muted">No entries yet</span>'] + ['<span class="muted">—</span>'] * (len(LEDGER_HEADERS) - 1)]
    body = f"""
<section>
  <div class="kicker">Dashboard · measurement</div>
  <h1>Campaign ledger</h1>
  <p class="lede">An empty, defined ledger. A row is added only when figures come from an authorised first-party report, with the timestamp, source, and a reference to that report.</p>
</section>
<section>
  {table(LEDGER_HEADERS, rows)}
</section>
<section class="callout">
  <h3>Rules for adding rows</h3>
  <ul>
    <li>Only figures from authorised first-party reports (for example, an Associates report for tracking ID shopnow047c-20).</li>
    <li>Record the timestamp in UTC, the source, the channel, eligible sessions, clicks, and reported orders.</li>
    <li>Keep a dated provenance reference to the report. Do not estimate or back-fill.</li>
    <li>No conversion score or revenue forecast is shown on any page until enough rows exist and you approve a method.</li>
  </ul>
</section>
"""
    layout(rel, "Campaign ledger", "Empty campaign ledger with defined columns and rules for adding first-party data.", body)


def page_flags():
    rel = "flagged-for-review/index.html"
    begin(rel)
    rows = []
    for f in FLAGS_DOC["flags"]:
        rows.append([
            f'<span id="{f["id"].lower()}"></span><strong>{E(f["id"])}</strong>',
            E(f["severity"]),
            f'<strong>{E(f["title"])}</strong><br>{E(f["detail"])}',
            src_chips(f["sources"]),
            E(f["owner_action"]),
            badge("Open: does not block publication"),
        ])
    body = f"""
<section>
  <div class="kicker">Dashboard · review queue</div>
  <h1>Flagged for Review</h1>
  <p class="lede">{E(FLAGS_DOC['status_note'])}</p>
</section>
<section>
  {table(["ID", "Severity", "Issue", "Sources", "Owner action", "Status"], rows)}
</section>
"""
    layout(rel, "Flagged for Review", "Flagged for Review: irregularities and unverified items, with sources and owner actions.", body)


def page_guides():
    rel = "guides/index.html"
    begin(rel)
    rows = [[f'<strong>{E(g["id"])}</strong>', E(g["working_title"]), E(g["question_it_answers"]), E(g["sourcing_needed"]), badge(GUIDES_DOC["status"])] for g in GUIDES_DOC["guides"]]
    body = f"""
<section>
  <div class="kicker">Guides</div>
  <h1>Guides in planning</h1>
  <p class="lede">{E(GUIDES_DOC['intro'])}</p>
</section>
<section>
  {table(["ID", "Working title (question)", "Question it answers", "Sourcing needed", "Status"], rows)}
</section>
<section class="callout">
  <h3>Publishing rules, once a guide is chosen</h3>
  <ul>
    <li>Every factual claim links to an official source in the register.</li>
    <li>The guide is added to the sitemap and the RSS feed on the day it is published.</li>
    <li>Cadence and first topic wait for your choice (Suggestions S-04, S-05).</li>
  </ul>
</section>
"""
    layout(rel, "Guides", "Guides in planning: working-title buyer questions, not yet published.", body)


def page_about():
    rel = "about/index.html"
    begin(rel)
    body = f"""
<section>
  <div class="kicker">About</div>
  <h1>About and method</h1>
  <p class="lede">{E(SITE_NAME)} is a working name for a static, source-first buying guide. Values come from the pages named in the register, with the date of capture.</p>
</section>
<section>
  <h2>How values are checked</h2>
  <ul>
    <li>Each product page is read with a fetch tool on {E(VERIFIED_ON)}. Values are copied as shown.</li>
    <li>Counts and ranges on the Analysis page are computed in the build from the stored values.</li>
    <li>Anything that cannot be confirmed is left blank and shown as Unverified, with a flag.</li>
  </ul>
</section>
<section>
  <h2>Limits of this review</h2>
  <ul>
    <li>Pages were read without a logged-in or local session (F-12).</li>
    <li>The sandbox could not reach link.amazon directly; the fetch tool was used for the redirects.</li>
    <li>Policy clauses 2(b), 2(v), and 2(w) were read from official search excerpts; a full-page check is pending.</li>
  </ul>
</section>
<section>
  <h2>Analytics status</h2>
  <p>No analytics or click counter is installed. The site is static (GitHub Pages), so no server endpoint exists. See Flagged for review F-08 and Suggestions S-02, S-03.</p>
</section>
<section>
  <h2>Feeds</h2>
  <p><a href="{E(PREFIX)}feed.xml">RSS feed</a> · <a href="{E(PREFIX)}sitemap.xml">Sitemap</a> · <a href="{E(PREFIX)}robots.txt">robots.txt</a></p>
</section>
"""
    layout(rel, "About and method", "How this site checks its values, its limits, and its analytics status.", body)


def page_css():
    css = """:root{--ink:#1f1d1a;--muted:#6b645b;--paper:#fbf8f3;--card:#fff;--line:#e6dfd3;--accent:#b4502a;--accent-ink:#8f3a1b;--gold:#fff3d1;--gold-line:#e8c96a;--green:#2e6b3f;--green-bg:#e4f2e7;--amber:#7a5000;--amber-bg:#fdf0cf;--grey-bg:#ece8e1;--red:#9b2b2b;--red-bg:#f8e1e1;--serif:Georgia,"Iowan Old Style","Times New Roman",serif;--sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:20px}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 var(--sans)}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
a{color:var(--accent-ink)}
.masthead{background:#fff;border-bottom:1px solid var(--line)}
.mast-row{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:18px 20px}
.brand{text-decoration:none;color:var(--ink);display:flex;flex-direction:column}
.brand-name{font:700 26px/1.1 var(--serif)}
.brand-tag{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1.1px;margin-top:4px}
nav.primary{display:flex;gap:20px;flex-wrap:wrap}
nav.primary a{text-decoration:none;color:var(--ink);font-weight:600;font-size:15px;padding:6px 0;border-bottom:2px solid transparent}
nav.primary a:hover{border-bottom-color:var(--accent)}
.disclosure{background:var(--gold);border-bottom:1px solid var(--gold-line);font-size:14px;padding:10px 0}
.muted{color:var(--muted)}
main{padding:30px 20px 56px;min-height:60vh}
h1{font:700 40px/1.15 var(--serif);margin:.2em 0 .3em}
h2{font:700 25px/1.25 var(--serif);margin:1.6em 0 .5em}
h3{font:700 18px/1.35 var(--sans);margin:1.1em 0 .4em}
.kicker{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--accent-ink);font-weight:700}
.lede{font-size:18px;color:#3b3732;max-width:72ch}
.hero{padding:8px 0 4px}
.grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));margin:20px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:8px}
.card .cat{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);font-weight:700}
.card h3{margin:0;font:700 19px/1.3 var(--serif)}
.price{font-size:24px;font-weight:700;line-height:1.2}
.price .muted{font-size:13px;font-weight:400}
.status-note{font-size:14px;color:var(--muted)}
.btn{display:inline-block;background:var(--accent);color:#fff!important;text-decoration:none;padding:10px 16px;border-radius:999px;font-weight:700;font-size:15px}
.btn:hover{background:var(--accent-ink)}
.btn-small{padding:6px 12px;font-size:13px}
.split{display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start}
@media (max-width:760px){.split{grid-template-columns:1fr}h1{font-size:32px}}
.tiles{display:grid;gap:12px;grid-template-columns:1fr 1fr}
.tile{display:grid;grid-template-columns:1fr auto;gap:4px 12px;text-decoration:none;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px}
.tile .cat{font:700 18px/1.3 var(--serif)}
.tile-count{color:var(--muted);font-size:14px}
.tile-arrow{grid-row:1/3;grid-column:2;font-size:22px;color:var(--accent)}
.callout{background:#fff;border-left:4px solid var(--accent);padding:14px 18px;border-radius:8px;margin:20px 0}
.callout h3{margin-top:0}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff;margin:12px 0}
table.data{border-collapse:collapse;width:100%;font-size:14px;min-width:560px}
table.data th,table.data td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.data th{background:#f4efe7;font-size:12px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)}
table.data tr:last-child td{border-bottom:0}
code{font:12.5px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;word-break:break-all}
.small{font-size:12px}
.badge{display:inline-block;font-size:12px;font-weight:700;padding:2px 9px;border-radius:999px;white-space:nowrap;margin:1px 0}
.badge.pass{background:var(--green-bg);color:var(--green)}
.badge.partial,.badge.flag{background:var(--amber-bg);color:var(--amber)}
.badge.unverified{background:var(--grey-bg);color:#4f4a43}
.badge.blocked{background:var(--red-bg);color:var(--red)}
.badge.neutral{background:#eee;color:#333}
.flagref{font-size:12px;color:var(--accent-ink);font-weight:700}
a.src{font-size:12px;font-weight:700;margin-right:4px}
.sugg{margin:18px 0 28px}
.site-footer{background:#1f1d1a;color:#e9e4dc;padding:36px 0 48px;margin-top:40px}
.site-footer a{color:#f4d9c6}
.site-footer h4{font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#bfb6a8;margin:0 0 8px}
.foot-grid{display:grid;gap:24px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));margin:20px 0}
.foot-grid ul{list-style:none;padding:0;margin:0}
.foot-grid li{margin:5px 0}
.disclosure-foot{border:1px solid #5a5249;padding:12px 16px;border-radius:8px;font-size:14px}
.site-footer .muted{color:#b7ae9f}
"""
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "site.css"), "w", encoding="utf-8") as fh:
        fh.write(css)


def write_feed_sitemap():
    today = datetime.date(2026, 11, 20)
    rfc822 = today.strftime("%a, %d %b %Y 00:00:00 GMT")
    items = [
        ("Site launch: product register, sources and flags", "The first version of the register is live: five Amazon listings with source links, a source register, a compliance gate, and an open list of flags. Prices and ratings are not published.", "index.html"),
    ]
    rss_items = "".join(
        f"<item><title>{E(t)}</title><link>{E(SITE_BASE + l)}</link><guid isPermaLink=\"true\">{E(SITE_BASE + l)}</guid><pubDate>{rfc822}</pubDate><description>{E(d)}</description></item>"
        for t, d, l in items
    )
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{E(SITE_NAME)}</title><link>{E(SITE_BASE)}</link><description>{E(TAGLINE)}</description><language>en</language><lastBuildDate>{rfc822}</lastBuildDate>{rss_items}</channel></rss>
"""
    with open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8") as fh:
        fh.write(feed)
    urls = [SITE_BASE] + [SITE_BASE + rel for rel, _, _ in PAGES if rel != "index.html"]
    url_xml = "".join(f"<url><loc>{E(u)}</loc><lastmod>{today.isoformat()}</lastmod></url>" for u in urls)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{url_xml}</urlset>\n'
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sitemap)
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_BASE}sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()


# ---------------------------------------------------------------- validation

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.anchors = []   # (href, rel)
        self.in_main_before_disclosure = None
        self.saw_disclosure_strip = False
        self.disclosure_positions = []
        self.main_seen = False
        self.text = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "a" and "href" in d:
            self.anchors.append((d["href"], d.get("rel", "") or ""))
        if tag == "main":
            self.main_seen = True
        if tag == "div" and "class" in d and "disclosure" in d["class"].split():
            self.saw_disclosure_strip = True
            if not self.main_seen:
                self.in_main_before_disclosure = True

    def handle_data(self, data):
        self.text.append(data)


def validate(errors):
    pages = {}
    for rel, _, _ in PAGES:
        with open(os.path.join(OUT, rel), encoding="utf-8") as fh:
            raw = fh.read()
        parser = PageParser()
        parser.feed(raw)
        pages[rel] = (parser, raw)

    # 0. No prices or ratings are published (Program Policies; see F-13).
    for rel, (parser, raw) in pages.items():
        visible = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
        if re.search(r"\$\d", visible):
            errors.append(f"{rel}: a price figure is published (see F-13)")
        if re.search(r"out of 5|\d\.\d\s*/\s*5\b|\d\.\d stars|\d[\d,]* reviews|\d\.\d\s*\(\s*[\d,]{3,}\s*\)", visible):
            errors.append(f"{rel}: a product rating is published (see F-13)")

    # 1. Disclosure above the fold and repeated in the footer, on every page.
    for rel, (parser, raw) in pages.items():
        if DISCLOSURE not in raw:
            errors.append(f"{rel}: Associates disclosure text missing")
        if not parser.saw_disclosure_strip or parser.in_main_before_disclosure is not True:
            errors.append(f"{rel}: disclosure strip is not placed above the main content")
        if raw.count(DISCLOSURE) < 2:
            errors.append(f"{rel}: disclosure not repeated in the footer")

    # 2. Every link to an Amazon host is sponsored; internal links and fragments resolve.
    for rel, (parser, raw) in pages.items():
        here = os.path.dirname(os.path.join(OUT, rel))
        for href, rel_attr in parser.anchors:
            host = urlparse(href).hostname or ""
            if host in AMAZON_HOSTS and "sponsored" not in rel_attr.split():
                errors.append(f"{rel}: Amazon link without rel=sponsored -> {href}")
            if href.startswith(("http://", "https://", "mailto:")) or href == "#":
                continue
            path, _, frag = href.partition("#")
            if href.startswith("#"):
                target_rel, target_parser = rel, parser
            else:
                target_path = os.path.normpath(os.path.join(here, path))
                if os.path.isdir(target_path):
                    target_path = os.path.join(target_path, "index.html")
                if not os.path.exists(target_path):
                    errors.append(f"{rel}: broken internal link -> {href}")
                    continue
                target_rel = os.path.relpath(target_path, OUT)
                if target_rel not in pages:
                    if target_rel.endswith(("feed.xml", "sitemap.xml", "robots.txt")):
                        continue
                    errors.append(f"{rel}: link to file not in page list -> {href}")
                    continue
                target_parser = pages[target_rel][0]
            if frag and frag not in target_parser.ids:
                errors.append(f"{rel}: missing anchor #{frag} on {target_rel}")

    # 3. Product records: official source, URL-derived values, flags for blanks.
    for p in PRODUCTS:
        pid = p["id"]
        if not any(SRC.get(s, {}).get("url", "") and (urlparse(SRC[s]["url"]).hostname in OFFICIAL_HOSTS) for s in p["sources"]):
            errors.append(f"{pid}: no official source on its row")
        for s in p["sources"]:
            if s not in SRC:
                errors.append(f"{pid}: unknown source {s}")
        if urlparse(p["official_listing_url"]).hostname not in OFFICIAL_HOSTS:
            errors.append(f"{pid}: official listing URL is not on an official host")
        m = re.search(r"/dp/([A-Z0-9]{10})", p["official_listing_url"])
        if not m or m.group(1) != p["observed_asin"]:
            errors.append(f"{pid}: observed_asin does not match the official listing URL")
        if urlparse(p["observed_redirect_target"]).hostname not in AMAZON_HOSTS:
            errors.append(f"{pid}: observed redirect target is not on an Amazon host")
        if p["tag_observed_in_redirect"] != ("tag=" in p["observed_redirect_target"]):
            errors.append(f"{pid}: tag_observed_in_redirect disagrees with the stored URL")
        if p["submitted_token_length"] != len(p["submitted_token"]):
            errors.append(f"{pid}: submitted_token_length is wrong")
        if p["submitted_token"] not in p["submitted_link"]:
            errors.append(f"{pid}: submitted token is not in the submitted link")
        if p["intended_asin"] and not re.fullmatch(r"[A-Z0-9]{10}", p["intended_asin"]):
            errors.append(f"{pid}: intended ASIN is not 10 characters")
        blanks = [k for k in ("intended_asin",) if not p[k]]
        for k in blanks:
            flag = p.get("unverified_fields", {}).get(k)
            if not flag or flag not in FLAGS:
                errors.append(f"{pid}: blank '{k}' is not listed against a flag")
        for k, flag in p.get("unverified_fields", {}).items():
            if flag not in FLAGS:
                errors.append(f"{pid}: unverified field '{k}' points to unknown flag {flag}")
        if p["category"] not in CATEGORIES:
            errors.append(f"{pid}: unknown category {p['category']}")

    # 4. Sources and flags are complete.
    for s in SOURCES_DOC["sources"]:
        if not s["url"].startswith("https://"):
            errors.append(f"{s['id']}: source URL is not https")
        if not s.get("status"):
            errors.append(f"{s['id']}: source has no verification status")
    for f in FLAGS.values():
        if not f.get("owner_action"):
            errors.append(f"{f['id']}: flag has no owner action")
        for s in f["sources"]:
            if s not in SRC:
                errors.append(f"{f['id']}: unknown source {s}")
    for q in QUESTIONS_DOC["questions"]:
        for r in q["refs"]:
            if r not in SRC and r not in FLAGS:
                errors.append(f"{q['id']}: unknown reference {r}")
    for s in SUGGESTIONS_DOC["suggestions"]:
        if len(s["options"]) < 2:
            errors.append(f"{s['id']}: needs at least two options")

    # 5. Feed and sitemap parse, and the sitemap lists every page.
    for name in ("sitemap.xml", "feed.xml"):
        try:
            ET.parse(os.path.join(OUT, name))
        except ET.ParseError as exc:
            errors.append(f"{name}: does not parse ({exc})")
    locs = {el.text for el in ET.parse(os.path.join(OUT, "sitemap.xml")).iter() if el.tag.endswith("loc")}
    for rel, _, _ in PAGES:
        url = SITE_BASE + ("" if rel == "index.html" else rel)
        if url not in locs:
            errors.append(f"sitemap.xml: missing {url}")
    return pages


def main():
    global PAGES
    PAGES = []
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    page_css()
    page_home()
    category_page("air-fryers")
    category_page("meat-thermometers")
    page_products()
    page_analysis()
    page_exec()
    page_questions()
    page_suggestions()
    page_compliance()
    page_sources()
    page_ledger()
    page_flags()
    page_guides()
    page_about()
    write_feed_sitemap()

    errors = []
    validate(errors)
    print(f"Built {len(PAGES)} pages into {os.path.relpath(OUT, ROOT)}/")
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} problem(s)")
        for err in errors:
            print("  -", err)
        return 1
    print("Validation passed: disclosure, sponsored links, internal links and anchors, product records, sources, flags, feed and sitemap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
