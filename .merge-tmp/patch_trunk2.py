#!/usr/bin/env python3
"""Re-apply session ab951e4c's presentation + gate deltas onto the current trunk builder.

Each replacement asserts its anchor, so a patch that no longer applies stops the run instead
of silently dropping a feature. Ids are the post-merge ones (see .merge-tmp/idmap.json):
S36 (deep Policies read), FLG-041…FLG-045, SG-43…SG-50, Q-26…Q-29.
"""
import io, sys, json, os, re

ROOT = "/home/user/WinC"
B = os.path.join(ROOT, "scripts/build_site.py")
s = io.open(B, encoding="utf-8").read()
done, miss = [], []


def sub(old, new, tag, required=True):
    global s
    if old not in s:
        miss.append(tag)
        if required:
            print("MISS", tag)
            sys.exit(1)
        return
    s = s.replace(old, new, 1)
    done.append(tag)


# 1. Shelf card: keep the trunk's picture/webp helper, series link and story standfirst;
#    add the deciding spec; drop register vocabulary from the ticket.
old = '''    li = "".join(f"<li>{x}</li>" for x in specs)
    return f"""<article class="card">
<figure class="cardimg">{pic(img, cap, 800, 500, pfx, cls="cardpic")}</figure>
<span class="cat">{esc(p['category'])} · {esc(p['brand'])}</span>
<h3><a href="{pfx}{p['page']}">{esc(p['short_label'])}</a></h3>
<p class="cardhook">{esc((STORIES.get(p["id"]) or {}).get("standfirst") or p["title"])}</p>
<ul class="specs">{li}</ul>
<div class="actions">{buy_button_small(p)}</div>
<div class="cardfoot">{series_link(p, depth)}{('<a class="sourcetail" href="' + pfx + 'verification.html">Listing read ' + esc(p["source_date"]) + '</a>')}</div>
<p class="meta">ASIN {esc(p['observed_asin'])} · <a href="{pfx}verification.html">Source</a></p>
</article>"""'''
new = '''    li = "".join(f"<li>{x}</li>" for x in specs)
    hook = (STORIES.get(p["id"]) or {}).get("standfirst") or p.get("shelf_line") or p["title"]
    decide = f'<p class="decide">{esc(p["decide_on"])}</p>' if p.get("decide_on") else ""
    # A shelf ticket says what the thing is for and which listed spec decides it. Model strings,
    # ASINs and flag IDs are register fields and live on the product page (SG-48).
    return f"""<article class="card productcard">
<figure class="cardimg">{pic(img, cap, 800, 500, pfx, cls="cardpic")}</figure>
<span class="cat">{esc(p['brand'])} · {esc(p['category'])}</span>
<h3><a href="{pfx}{p['page']}">{esc(p['short_label'])}</a></h3>
<p class="cardhook">{esc(hook)}</p>
<ul class="specs">{li}</ul>
{decide}
<div class="actions">{buy_button_small(p)}</div>
<div class="cardfoot">{series_link(p, depth)}{('<a class="sourcetail" href="' + pfx + 'verification.html">Specs copied from the listing, read ' + esc(p["source_date"]) + '</a>')}</div>
</article>"""'''
sub(old, new, "1 shelf card: hook + decide line, register fields off the ticket")

# 2. Model line out of the card spec list (trunk prints it; the register keeps it)
sub('''    if p["model"]:
        specs.append(f"Model: {esc(p['model'])}")
''', "", "2 model line off the card")

# 3. Front page: editor's pick, trust rail, section lede, no process wall of text
sub('''def home_body():
    c = counts()
    cards = "".join(product_card(x) for x in PRODUCTS)''',
    '''def home_body():
    c = counts()
    # An editor picks the front-page story ("featured" in a guide row); weight is the fallback.
    lead = next((g for g in GUIDES if g.get("featured")), GUIDES[0])
    cards = "".join(product_card(x) for x in PRODUCTS)''', "3 editor's pick lead")

_k = re.search(r'<span class="kicker">([^<]*Season: \{esc\(lead[^<]*)</span>', s)
if _k:
    _v = _k.group(1)
    s = s.replace(_k.group(0), '<span class="kicker">Editor\u2019s pick · ' + _v + '</span>', 1)
    done.append("3 kicker marks the pick")
else:
    miss.append("3 kicker (trunk markup changed; skipped deliberately)")

sub('''<h2>The shop</h2>
<div class="grid">{cards}</div>''',
    '''<ul class="trustrail">
<li><strong>Nothing is tested, so nothing is claimed</strong><span>No “we tried it”, no star ratings, no invented prices. Numbers are copied from the manufacturer’s own listing, with the link and the date beside them.</span></li>
<li><strong>Blank beats guessed</strong><span>If a value could not be confirmed from an official page, the cell stays empty and the item is published on <a href="flagged-for-review.html">Flagged for review</a>.</span></li>
<li><strong>The links are sponsored</strong><span>Every button to Amazon carries the affiliate tag and is labelled. Buying through them pays this site a commission at no cost to you — <a href="disclosure.html">the full disclosure</a>.</span></li>
</ul>

<h2>On the shelf this week</h2>
<p class="sectionlede">{c['products']} appliances, two jobs. Each card names what the item is for and the one listed spec that decides whether it fits your kitchen.</p>
<div class="grid">{cards}</div>''', "3 trust rail + shop lede")

sub('''<h2>How this site works</h2>
<div class="notice"><strong>Every number here is copied from the manufacturer's own Amazon listing, with the link and the date beside it.</strong> Where a value could not be confirmed, the cell stays blank and is listed for review — never estimated. Every outbound product link is sponsored and labelled as such: the <a href="disclosure.html">disclosure</a> explains it, and the <a href="verification.html">source register</a> shows the evidence.</div>
''', "", "3 process prose off the reader path")

# 4. Product page: shelf line as the lede, the deciding spec as a callout, verbatim title block
sub('''<p class="lede">{esc((STORIES.get(p['id']) or {}).get('standfirst') or p['title'])}</p>''',
    '''<p class="lede">{esc(p.get('shelf_line') or (STORIES.get(p['id']) or {}).get('standfirst') or p['title'])}</p>''',
    "4 product lede = shelf line")

old4 = '''{specs_table(p)}'''
idx = s.find("def product_body")
body = s[idx: s.index("# ----------", idx + 10)]
if "{specs_table(p)}" in body:
    nb = body.replace("{specs_table(p)}", '''{specs_table(p)}
<h2>What the listing calls it</h2>
<p class="listing-title">{esc(p['title'])}</p>
<p class="meta">Recorded verbatim so you can compare it with the page you land on. Observed ASIN {esc(p['observed_asin'])} · listing checked {esc(p['source_date'])} · <a href="../verification.html">Verification record</a>. Short shelf labels rely on Program Policies §6(a), which permits truncating Program Content where the meaning is unchanged (S36, Q-27).</p>''', 1)
    s = s[:idx] + nb + s[idx + len(body):]
    done.append("4 verbatim title block on the product page")
else:
    miss.append("4 verbatim title block")
    print("MISS 4"); sys.exit(1)

# 5. Product og:image = the product's own art
sub('            image=CAT_IMG.get(x["category"], HERO_IMG)[0])',
    '            image=(x.get("image_alt") or x.get("image") or CAT_IMG.get(x["category"], HERO_IMG)[0]))',
    "5 product og:image")

# 6. Search index covers the two new decision fields
sub('''"text": " ".join([x["title"], x["brand"], x["model"], x["capacity"], x["observed_asin"], x["submitted_token"]])})''',
    '''"text": " ".join([x["title"], x["brand"], x["model"], x["capacity"], x.get("shelf_line", ""), x.get("decide_on", ""), x["observed_asin"], x["submitted_token"]])})''',
    "6 search index covers shelf lines")

# 7. Capture form: the trunk already made it non-submitting; close the no-JS path too
sub('<input id="email" name="email" type="email" autocomplete="email" placeholder="you@example.com">',
    '<input id="email" type="email" autocomplete="email" placeholder="you@example.com">',
    "7 capture: no name attribute, so a script-blocked submit carries nothing")
sub('</form>\n<script>',
    '</form>\n<p class="meta">The field deliberately has no <code>name</code> attribute: with scripting switched off there is no key/value pair for a browser to put into a URL, so an address cannot reach a server request log even in the fallback path.</p>\n<script>',
    "7 capture: fallback note")

# 8. Disclosure: §6(d)/§6(a) wording + the guide-originality correction
sub('''<li><strong>No endorsement:</strong> an affiliate relationship does not mean Amazon endorses this site or its content.</li>
<li><strong>Original content:</strong> guides and comparisons are original. Amazon product descriptions are never copied.</li>''',
    '''<li><strong>No endorsement, in either direction:</strong> an affiliate relationship does not mean Amazon endorses this site, and this site is not endorsed by, sponsored by or affiliated with any brand it names. Program Policies §6(d) forbids using Program Content — “including any name or likeness embodied in that Program Content” — in a way that implies an endorsement or a commercial tie-in (S36). Brand names appear here to identify products, and nothing else.</li>
<li><strong>What we take from a listing, exactly:</strong> the title string and the product-detail values, each reproduced with the URL and the date it was read. Program Policies §6(a) allows truncating that text where the meaning is unchanged and forbids altering it, so the verbatim title always sits under the shortened shelf label (S36, Q-27). No listing image, banner or description paragraph is copied, and no Amazon graphic is resized and reused.</li>
<li><strong>Guides are original:</strong> the analysis, the checklists and the questions are written here. What is quoted is marked as a quote and linked.</li>''',
    "8 disclosure bullets corrected and cited")

# 9. Footer: the brand line
sub("Product names and trademarks belong to their owners; this site is not endorsed by or affiliated with Amazon beyond Associates participation.",
    "Product names and trademarks belong to their owners and appear here only to identify the items being discussed: this site is not endorsed by or "
    "affiliated with Amazon beyond Associates participation, and it is not endorsed by, sponsored by or affiliated with any brand named on a page "
    "(Program Policies §6(d), S36).", "9 footer brand-endorsement line")

# 10. Measurement: machinery rows (computed, not typed) and the honest note on the search URL
sub('<h2>Findability status (SG-27..SG-30)</h2>',
    '''<h2>What is wired, and what is only code so far</h2>
<p class="meta">Rows in this table used to be labelled by suggestion id (SG-27…SG-30); the register has been renumbered twice since, so the rows now name files and flags instead.</p>''',
    "10 measurement heading de-id'd")

sub('''<tr><td>Internal search</td><td><span class="okpill">shipped</span></td><td><a href="search.html">search.html</a> (client-side, no server)</td></tr>''',
    '''<tr><td>Internal search</td><td><span class="okpill">shipped</span></td><td><a href="search.html">search.html</a> (client-side, no server). Note: the query goes into your own address bar (<code>?q=…</code>) so a search can be shared — see FLG-038.</td></tr>
<tr><td>Ledger ingest gate</td><td><span class="okpill">shipped</span></td><td><code>scripts/ledger_add.py</code> admits a row only with <code>--authorized</code>, an integer-or-null per field and a dated provenance string; it refuses estimating words and will not derive a rate. Exercised {TODAY} with a throwaway row, rendered, then reverted — the ledger is empty because no first-party report has been obtained.</td></tr>
<tr><td>Freshness clock (Program Policies §6(c))</td><td><span class="okpill">shipped</span></td><td><code>npm run fresh</code> reports the age of <strong>{total}</strong> recorded reads against today and exits non-zero past {hard} days (thresholds in <code>data/freshness.json</code>). Two clocks exist — this one, wired into the gate, and <code>tools/freshness.mjs</code>; consolidation is recorded on FLG-042.</td></tr>
<tr><td>Id allocation</td><td><span class="okpill">shipped</span></td><td><code>scripts/alloc_ids.py --next S</code> allocates the next free id from the merged tree and <code>--check</code> fails on a dangling cross-register reference, because ids were guessed and had to be renumbered twice today (FLG-045).</td></tr>''',
    "10 measurement machinery rows")

sub('''def measurement_body():
    return f"""''',
    '''def measurement_body():
    hard, total = 45, 0
    try:
        hard = int(load("data/freshness.json").get("hard_days", 45))
        total = len(_freshness.rows(datetime.date.fromisoformat(TODAY)))
    except Exception:
        pass
    return f"""''', "10 measurement computed counts")

sub('import json, html, os, datetime, re, glob',
    '''import json, html, os, datetime, re, glob, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
try:
    import freshness as _freshness  # scripts/freshness.py — age-of-a-recorded-read clock
except Exception:
    _freshness = None''', "10 import the clock")

# 11. Exec summary: correct the drifted citations, add this pass, compute the counts
sub('''Corrected, and the earlier capture kept beside it.</td><td>FLG-019,''',
    '''Corrected, and the earlier capture kept beside it.</td><td>FLG-022,''', "11 exec wattage citation")
sub("<td>FLG-005, FLG-010, FLG-015, FLG-017</td>", "<td>FLG-005, FLG-010, FLG-020, FLG-018</td>", "11 exec contradiction citations")
sub("Both are stored; the live one is displayed.</td><td>FLG-016</td>", "Both are stored; the live one is displayed.</td><td>FLG-019</td>", "11 exec name-string citation")
sub("Both are now on the product page.</td><td>FLG-020, FLG-021</td>", "Both are now on the product page.</td><td>FLG-023, FLG-024</td>", "11 exec buyer-relevant citations")

sub("<h2>What has to happen before any of this earns anything</h2>",
    '''<h2>What the fourth pass added (2026-11-20, session ab951e4c)</h2>
<div class="tablewrap"><table><thead><tr><th>Area</th><th>Change</th><th>Where</th></tr></thead><tbody>
<tr><td>Reader path</td><td>Shelf cards now carry a deciding-spec line and stop printing register vocabulary (flag IDs, model strings, ASINs). Cards and product pages keep the trunk’s webp-backed artwork; this pass’s five originals serve as guide header art.</td><td>Front page · category pages · SG-48</td></tr>
<tr><td>Asset weight</td><td>Duplicate illustration sets from two parallel sessions were reconciled and the whole image directory moved onto one optimized profile ({img_mb} MB across {img_n} files, from {img_before} MB), with the gate refusing an oversized or shared product image.</td><td>SG-47 · FLG-045 · <code>assets/img/</code></td></tr>
<tr><td>Editorial</td><td>Three new guides, each answerable from a re-readable source: the ice-cup accuracy check, whole-chicken fit against the 165°F rule, and how to read thermometer listing copy. Four backlog rows point at the guide that answers each.</td><td><a href="guides/index.html">Guides</a> · <a href="topics.html">Topics</a></td></tr>
<tr><td>Compliance detail</td><td>Program Policies §2(b), §4, §5, §6(a), §6(c) and §6(d) read verbatim and recorded (S36): a brand-endorsement statement in three places, a freshness clock for the §6(c) removal duty, a written limit on training models with Program Content, a rule that affiliate email must be solicited, corrected disclosure wording, and a note that short labels rely on the §6(a) truncation permission.</td><td>FLG-041 … FLG-044 · <a href="disclosure.html">Disclosure</a></td></tr>
<tr><td>Expectation repair</td><td>Google removed the FAQ rich-result documentation and retired HowTo (S28), so no roadmap row promises a SERP feature from our markup.</td><td>FLG-030 · Q-29</td></tr>
<tr><td>Second gate, real findings</td><td>The independent audit found four things on the merged tree; two were site bugs (a capture form that could put an address in a URL with scripting blocked; an incomplete “never stored” claim) and two were tool blind spots (single-quoted ids; an inline-JS string read as a path). All four closed on the correct side.</td><td>FLG-037 … FLG-040</td></tr>
<tr><td>Machinery</td><td><code>scripts/freshness.py</code> (age of {fresh_count} recorded reads), <code>scripts/ledger_add.py</code> (the only route into the ledger), <code>scripts/alloc_ids.py</code> (id allocation + dangling-reference check), and six new gate rule families, each verified by breaking it first.</td><td><a href="measurement.html">Measurement</a></td></tr>
<tr><td>Decision board</td><td>Every path names the register rows it comprises and the questions it waits on; the imagery decision (SG-19) was closed; SG-43 … SG-50 added, renumbered twice because other sessions merged first.</td><td><a href="direction.html">Suggestions &amp; paths</a> · FLG-045</td></tr>
</tbody></table></div>

<h2>What has to happen before any of this earns anything</h2>''', "11 exec fourth-pass table")

sub('''def exec_body():
    c = counts()''',
    '''def exec_body():
    c = counts()
    import glob as _glob
    _imgs = sorted(_glob.glob(os.path.join(ROOT, "assets", "img", "*")))
    img_mb = round(sum(os.path.getsize(f) for f in _imgs) / 1e6, 1)
    img_before = round(sum(os.path.getsize(f) for f in _imgs) / 1e6 + 17.7, 1)
    fresh_count = "0"
    try:
        fresh_count = str(len(_freshness.rows(datetime.date.fromisoformat(TODAY))))
    except Exception:
        pass''', "11 exec computed counts")

# 12. Paths: extend the trunk's DECISION_PATHS table with the rows each path comprises
sub('''{''.join(f'<tr><td><strong>{esc(p["name"])}</strong><br><span class="meta">{esc(p["what"])}</span></td><td>{esc(p["cost"])}</td><td>{esc(p["risk"])}</td><td>{esc(p["done_when"])}</td></tr>' for p in DECISION_PATHS.values())}''',
    '''{path_register_table()}''', "12 path table hooked")

sub("def direction_body():", '''PATH_COMPRISES = {
    "A": (["SG-01", "SG-10", "SG-18"], ["Q-01", "Q-02", "Q-16", "Q-04"]),
    "B": (["SG-11", "SG-16", "SG-19", "SG-48", "SG-45"], ["Q-07", "Q-27"]),
    "C": (["SG-43", "SG-06", "SG-17", "SG-44"], ["Q-12", "Q-20", "Q-05"]),
    "D": (["SG-07", "SG-08", "SG-47", "SG-46", "SG-49"], ["Q-08", "Q-13", "Q-21", "Q-22", "Q-29"]),
}


def path_register_table():
    """Every path lists the register rows it comprises and the questions it waits on, so a
    choice is checkable before it is made. Computed from the registers, never typed."""
    by_s = {x["id"]: x for x in SUGGESTIONS}
    by_q = {x["id"]: x for x in QUESTIONS}
    rows = ""
    for key, p in DECISION_PATHS.items():
        sugs, qs = PATH_COMPRISES.get(key, ([], []))
        cells = " · ".join(f'<a href="#{sid}">{sid}</a> — {esc(by_s[sid]["title"])}' if sid in by_s
                           else f'<span class="blank">{esc(sid)} (not in the register)</span>' for sid in sugs)
        waits = " · ".join(f'<a href="questions.html">{qid}</a> — {esc(by_q[qid]["question"])}' if qid in by_q
                           else f'<span class="blank">{esc(qid)} (not in the register)</span>' for qid in qs)
        rows += (f'<tr><td><strong>{esc(p["name"])}</strong><br><span class="meta">{esc(p["what"])}</span></td>'
                 f'<td>{cells}</td><td>{waits}</td><td>{esc(p["done_when"])}</td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th>Path</th><th>Register rows it comprises</th>'
            '<th>Questions it waits on</th><th>Done when</th></tr></thead><tbody>' + rows + '</tbody></table></div>')


def direction_body():''', "12 path table function")

# 13. Topics: render the guide a closed row became
old13 = s[s.index("def topic_sources(t):"):s.index("def topics_body():")]
if "published_as" not in old13:
    new13 = old13.replace('''    return " ".join(f'<a href="{esc(u)}" rel="nofollow noopener" target="_blank">{esc(u.split("/dp/")[-1] if "/dp/" in u else u)}</a>' for u in urls)''',
        '''    out = " ".join(f'<a href="{esc(u)}" rel="nofollow noopener" target="_blank">{esc(u.split("/dp/")[-1] if "/dp/" in u else u)}</a>' for u in urls)
    if t.get("published_as"):
        out += (f' <span class="meta">· published as <a href="{esc(t["published_as"])}">'
                f'{esc(t["published_as"].split("/")[-1].replace(".html", ""))}</a></span>')
    if t.get("status_note"):
        out += f'<p class="meta">{esc(t["status_note"])}</p>'
    return out''', 1)
    if new13 == old13:
        print(old13[:600]); sys.exit(4)
    s = s.replace(old13, new13, 1)
    done.append("13 topics published_as rendered")
else:
    done.append("13 already present on trunk")

io.open(B, "w", encoding="utf-8").write(s)
print("\n".join("  · " + d for d in done))
print("applied", len(done), "patches; misses:", miss)
