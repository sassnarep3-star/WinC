#!/usr/bin/env python3
"""
Site checker — compliance & integrity gate for Kitchen Shortlist.

Runs on every push/PR (.github/workflows/site-checks.yml). Fails (exit 1) when:

  1.  A page is missing the exact Associates statement, the disclosure strip
      above <main>, or the footer disclosure repeat.
  2.  A page is missing canonical / lang / title / meta description.
  3.  An outbound link to link.amazon lacks rel="sponsored", or any other
      amazon.com link lacks rel="nofollow" or rel="sponsored".
  4.  A data-table row shows content without a source link (empty-state and
      data-nosrc rows are exempt by design).
  5.  A price pattern ($X.XX) appears in any data-table cell (V-06/V-07 gate).
  6.  An internal link (page or #fragment) does not resolve.
  7.  sitemap.xml / rss.xml drift from the actual files.
  8.  JSON data records are malformed or merge intended/observed fields.
  9.  Referenced assets (css/js/img) are missing.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BASE = "https://sassnarep3-star.github.io/WinC/"

STATEMENT = "As an Amazon Associate I earn from qualifying purchases."
ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------- helpers
def collect_ids(text: str) -> set[str]:
    return set(re.findall(r'id="([^"]+)"', text))


def local_targets(href: str, page: Path) -> tuple[Path | None, str | None]:
    """Resolve an internal href to (file, fragment) or (None, None) if external."""
    href, frag = urldefrag(href)
    if href.startswith(("http://", "https://", "mailto:", "tel:")):
        if href.startswith(BASE):
            rel = href[len(BASE):] or "index.html"
            return DOCS / rel, frag or None
        return None, None
    if href.startswith("#"):
        return page, frag or None
    if href.startswith("/"):
        # absolute site path e.g. /WinC/assets/...
        parts = href.lstrip("/").split("/", 1)
        if len(parts) == 2 and parts[0] == "WinC":
            return DOCS / parts[1], frag or None
        return DOCS / href.lstrip("/"), frag or None
    # relative to the page
    target = (page.parent / href.split("#")[0]).resolve()
    return target, frag or None


# ---------------------------------------------------------------- checks
def check_pages() -> list[Path]:
    pages = sorted(p for p in DOCS.rglob("*.html") if p.is_file())
    if not pages:
        err("no HTML pages found under docs/")
        return pages

    for page in pages:
        text = read(page)
        rel = page.relative_to(DOCS)
        is_404 = page.name == "404.html"

        # 1. disclosure
        if text.count(STATEMENT) < 2:
            err(f"{rel}: Associates statement must appear twice (strip + footer); found {text.count(STATEMENT)}")
        if 'class="disclosure"' not in text:
            err(f"{rel}: missing disclosure strip")
        else:
            if text.find('class="disclosure"') > text.find("<main"):
                err(f"{rel}: disclosure strip is not above <main>")
        if "footer-disclosure" not in text:
            err(f"{rel}: missing footer disclosure")

        # 2. head hygiene
        if 'rel="canonical"' not in text:
            err(f"{rel}: missing canonical link")
        if '<html lang="en"' not in text:
            err(f"{rel}: missing <html lang=\"en\">")
        if "<title>" not in text:
            err(f"{rel}: missing <title>")
        if not is_404 and 'name="description"' not in text:
            err(f"{rel}: missing meta description")
        if not is_404 and '<nav class="nav"' not in text:
            err(f"{rel}: missing main navigation")

        # 3. outbound link marking
        for m in re.finditer(r"<a\s[^>]*?>", text, re.S):
            tag = m.group(0)
            hm = re.search(r'href="([^"]+)"', tag)
            if not hm:
                continue
            href = hm.group(1)
            if "link.amazon" in href:
                if "sponsored" not in tag:
                    err(f"{rel}: link.amazon href without rel=sponsored -> {href[:80]}")
            elif re.search(r"amazon\.com/(?:dp/|gp/product/)", href):
                if "nofollow" not in tag and "sponsored" not in tag:
                    err(f"{rel}: amazon product href without rel nofollow/sponsored -> {href[:80]}")

        # 4/5. data tables: every row needs a source link; no price patterns
        for tbl in re.findall(r'<table class="data[^"]*"[^>]*>.*?</table>', text, re.S):
            for attrs, row in re.findall(r"<tr([^>]*)>(.*?)</tr>", tbl, re.S | re.I):
                if re.search(r"<th[\s>]", row, re.I):
                    continue
                if 'data-nosrc="true"' in attrs:
                    continue
                cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)
                if not cells:
                    continue
                if "empty-state" in row and any("colspan" in c for c in re.findall(r"<td([^>]*)>", row, re.I)):
                    continue  # placeholder / empty-state rows
                if not re.search(r'<a\s[^>]*href="', row):
                    snippet = re.sub(r"\s+", " ", row)[:90]
                    err(f"{rel}: table row without source link -> {snippet}")
                for cell in cells:
                    if re.search(r"\$\s?\d", cell):
                        snippet = re.sub(r"\s+", " ", cell)[:60]
                        err(f"{rel}: price pattern in data cell (V-06 gate) -> {snippet}")

        # 9. referenced local assets exist
        for attr in ("href", "src"):
            for val in re.findall(rf'{attr}="([^"]+)"', text):
                if val.startswith(("http", "mailto", "#", "//")):
                    continue
                if any(val.endswith(ext) for ext in (".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".xml", ".json", ".rss")):
                    target, _ = local_targets(val, page)
                    if target is not None and not target.exists():
                        err(f"{rel}: missing asset {val}")

    return pages


def check_internal_links(pages: list[Path]) -> None:
    id_cache: dict[Path, set[str]] = {}
    for page in pages:
        text = read(page)
        rel = page.relative_to(DOCS)
        for m in re.finditer(r'href="([^"]+)"', text):
            href = m.group(1)
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            target, frag = local_targets(href, page)
            if target is None:
                continue
            if not target.exists():
                err(f"{rel}: broken internal link {href}")
                continue
            if frag and target.suffix == ".html":
                if target not in id_cache:
                    id_cache[target] = collect_ids(read(target))
                if frag not in id_cache[target]:
                    err(f"{rel}: fragment #{frag} not found in {target.relative_to(DOCS)}")


def check_sitemap(pages: list[Path]) -> None:
    sm = DOCS / "sitemap.xml"
    if not sm.exists():
        err("sitemap.xml missing")
        return
    try:
        tree = ET.parse(sm)
    except ET.ParseError as e:
        err(f"sitemap.xml parse error: {e}")
        return
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [el.text.strip() for el in tree.findall(".//sm:loc", ns) if el.text]
    if not locs:
        locs = [el.text.strip() for el in tree.iter() if el.tag.endswith("loc") and el.text]

    fileset = {p for p in pages}
    mapped: set[Path] = set()
    for loc in locs:
        if not loc.startswith(BASE):
            err(f"sitemap: loc not under canonical base: {loc}")
            continue
        rel = loc[len(BASE):] or "index.html"
        f = DOCS / rel
        if not f.exists():
            err(f"sitemap: loc points to missing file {loc}")
        else:
            mapped.add(f)

    for p in fileset:
        if p.name == "404.html":
            continue
        if p not in mapped:
            err(f"sitemap: page not listed -> {p.relative_to(DOCS)}")


def check_rss(pages: list[Path]) -> None:
    rss = DOCS / "rss.xml"
    if not rss.exists():
        err("rss.xml missing")
        return
    try:
        tree = ET.parse(rss)
    except ET.ParseError as e:
        err(f"rss.xml parse error: {e}")
        return
    items = [el for el in tree.iter() if el.tag.endswith("item")]
    if not items:
        err("rss.xml has no items")
        return
    item_links = set()
    for it in items:
        link = next((c.text.strip() for c in it if c.tag.endswith("link") and c.text), None)
        if not link:
            err("rss.xml: item without link")
            continue
        if not link.startswith(BASE):
            err(f"rss.xml: item link outside base: {link}")
            continue
        f = DOCS / link[len(BASE):]
        if not f.exists():
            err(f"rss.xml: item link missing file {link}")
        else:
            item_links.add(f)

    for p in pages:
        if p.parent.name == "guides" and p.name != "index.html" and p not in item_links:
            err(f"rss.xml: guide missing from feed -> {p.relative_to(DOCS)}")


def check_robots() -> None:
    rb = DOCS / "robots.txt"
    if not rb.exists():
        err("robots.txt missing")
        return
    text = read(rb)
    if f"Sitemap: {BASE}sitemap.xml" not in text:
        err("robots.txt: missing sitemap pointer")


def check_json_records() -> None:
    # products.json — schema + field separation
    try:
        data = json.loads(read(DOCS / "data" / "products.json"))
    except Exception as e:  # noqa: BLE001
        err(f"products.json: {e}")
        return
    prods = data.get("products", [])
    if len(prods) != 5:
        err(f"products.json: expected 5 products, found {len(prods)}")
    for i, p in enumerate(prods, 1):
        for block in ("intended", "observed"):
            if block not in p:
                err(f"products.json P-0{i}: missing '{block}' block (separation rule)")
        it, ob = p.get("intended", {}), p.get("observed", {})
        for k in ("code", "official_listing_url", "confirmation_date", "source"):
            if not it.get(k):
                err(f"products.json P-0{i}: intended.{k} missing/empty")
        for k in ("checked_date", "redirect_target", "listing_title"):
            if not ob.get(k):
                err(f"products.json P-0{i}: observed.{k} missing/empty")
        for k in ("price", "rating", "commission_rate"):
            if ob.get(k) is not None:
                err(f"products.json P-0{i}: observed.{k} must stay null until policy-compliant source (V-06/V-07/V-09)")

    # sources.json
    try:
        src = json.loads(read(DOCS / "data" / "sources.json"))
    except Exception as e:  # noqa: BLE001
        err(f"sources.json: {e}")
        return
    if len(src.get("verified_claims", [])) < 14:
        err("sources.json: expected >= 14 verified claims")
    for row in src.get("verified_claims", []):
        if not row.get("source", "").startswith("http"):
            err(f"sources.json {row.get('id')}: claim without http source")
    for row in src.get("observations", []):
        if not row.get("source", "").startswith("http"):
            err(f"sources.json {row.get('id')}: observation without http source")

    # campaign ledger — must be empty of data rows
    try:
        led = json.loads(read(DOCS / "data" / "campaign-ledger.json"))
    except Exception as e:  # noqa: BLE001
        err(f"campaign-ledger.json: {e}")
        return
    if led.get("rows") != []:
        err("campaign-ledger.json: rows must be [] until authorized reports exist")
    if len(led.get("columns", [])) < 8:
        err("campaign-ledger.json: column schema incomplete")


def check_no_jekyll() -> None:
    if not (DOCS / ".nojekyll").exists():
        err("docs/.nojekyll missing (GitHub Pages would run Jekyll needlessly)")


def main() -> int:
    if not DOCS.is_dir():
        print("docs/ directory not found", file=sys.stderr)
        return 1
    pages = check_pages()
    check_internal_links(pages)
    check_sitemap(pages)
    check_rss(pages)
    check_robots()
    check_json_records()
    check_no_jekyll()

    for w in WARNINGS:
        print(f"WARN  {w}")
    if ERRORS:
        for e in ERRORS:
            print(f"FAIL  {e}")
        print(f"\n{len(ERRORS)} check(s) failed.")
        return 1
    print(f"OK    all checks passed ({len(pages)} pages).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
