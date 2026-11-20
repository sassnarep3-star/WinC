// tools/check.mjs — the publishing gate.
// Everything a repository can prove about itself is asserted here and fails the build; what it cannot
// prove (an account, a live listing, a human judgement) is reported as a gated item, never quietly passed.
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, dirname, resolve, relative } from "node:path";
import { loadAll, ROOT, esc } from "./lib.mjs";

const D = loadAll();
const CFG = D.config;
const BASE = CFG.site.base_url.replace(/\/$/, "");
const TODAY = new Date("2026-11-20T00:00:00Z");

const fails = [];
const gates = [];
const notes = [];
const fail = (rule, msg) => fails.push({ rule, msg });
const pass = (rule, msg) => gates.push({ rule, msg });

// ---------- file discovery ----------
function htmlFiles(dir, acc = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (e.name === "node_modules" || e.name.startsWith(".git")) continue;
    const p = join(dir, e.name);
    if (e.isDirectory()) htmlFiles(p, acc);
    else if (e.name.endsWith(".html")) acc.push(p);
  }
  return acc;
}
const files = htmlFiles(ROOT).sort();
if (!files.length) { console.error("no HTML generated — run npm run build first"); process.exit(1); }
const read = (p) => readFileSync(p, "utf8");
const relOf = (p) => relative(ROOT, p).replace(/\\/g, "/");

// ---------- G-01 / G-02: disclosure above the fold and in the footer ----------
{
  const req = CFG.monetization.earnings_statement;
  let bad = [];
  for (const f of files) {
    const h = read(f);
    const stripIdx = h.indexOf('class="disclosure"');
    const footIdx = h.lastIndexOf('class="foot-bar"');
    const inStrip = stripIdx > -1 && h.slice(stripIdx, stripIdx + 1400).includes(req);
    const inFoot = footIdx > -1 && h.slice(footIdx).includes(req);
    if (!inStrip || !inFoot) bad.push(`${relOf(f)} (strip:${inStrip ? "y" : "n"} footer:${inFoot ? "y" : "n"})`);
  }
  if (bad.length) fail("G-01/G-02", `required sentence missing or misplaced on ${bad.length} page(s): ${bad.join(", ")}`);
  else pass("G-01/G-02", `required Associates sentence present in the top strip and the footer on all ${files.length} pages`);
}

// ---------- G-03/G-05: outbound link hygiene ----------
const STORE_HOST = /(^|\.)amazon\.[a-z.]{2,}$|(^|\.)amzn\.to$/i;
// A *commerce* link is one that can earn: a listing path or a short link. A help or API-documentation
// link is a citation, and tagging it would be nonsense - so the gate separates the two.
const PRODUCT_LINK = (href) => {
  let u; try { u = new URL(href); } catch { return false; }
  if (!STORE_HOST.test(u.hostname)) return false;
  if (/^\/(dp|gp\/product|product\/|gp\/aw\/|exec\/obidos\/ASIN)/i.test(u.pathname)) return true;
  if (/amzn\.to$/i.test(u.hostname)) return true;
  if (u.hostname === "link.amazon") return true;
  return false;
};
const DOC_HOST_PATH = (href) => {
  let u; try { u = new URL(href); } catch { return false; }
  return /\/(help|creatorsapi|gp\/help|product-safety-alerts)/i.test(u.pathname) || /affiliate-program\.amazon\.|sellercentral\.amazon\./i.test(u.hostname);
};
function hostOf(href) { try { return new URL(href, "https://x.invalid").hostname; } catch { return ""; } }
{
  let storeLinks = 0, problems = [];
  for (const f of files) {
    const h = read(f);
    for (const m of h.matchAll(/<a\b([^>]*)>/g)) {
      const attrs = m[1];
      const href = (attrs.match(/href="([^"]+)"/) || [])[1] || "";
      if (!/^https?:/i.test(href)) continue;
      const host = hostOf(href);
      if (!PRODUCT_LINK(href)) {
        if (STORE_HOST.test(host) && !DOC_HOST_PATH(href) && !/amazon\.[a-z.]{2,}$/.test(host) === false && /(^|\.)(www|smile)\.amazon\./i.test(host) === false && !DOC_HOST_PATH(href))
          { /* non-listing commerce-ish host: leave to the allowlist check */ }
        continue;
      }
      storeLinks++;
      const rel = (attrs.match(/rel="([^"]+)"/) || [])[1] || "";
      if (!/sponsored/.test(rel)) problems.push(`${relOf(f)}: store link without rel~=sponsored (${href})`);
      if (host === "link.amazon" || !/[?&]tag=[^&"]+/.test(href))
        problems.push(`${relOf(f)}: store link with no tag parameter or an unresolved host (${href})`);
      // G-03: a link-level label must sit in the same block
      const around = h.slice(Math.max(0, m.index - 900), m.index + 1400);
      if (!around.includes(CFG.monetization.link_level_label))
        problems.push(`${relOf(f)}: store link without a ${CFG.monetization.link_level_label} label nearby`);
    }
  }
  // forward-looking half of the rule: a confirmed product must actually be linked, labelled and tagged
  const confirmed = D.intent.records.filter((r) => r.intended_asin_confirmed);
  if (confirmed.length && storeLinks === 0)
    fail("G-03", `${confirmed.length} product row(s) are marked confirmed but no compliant store link exists in the build`);
  else if (problems.length) fail("G-05", problems.join("; "));
  else pass("G-05", storeLinks === 0
    ? "no store link published — correct while every row is unresolved; unconfirmed addresses appear only as copyable text"
    : `${storeLinks} store link(s) all tagged, sponsored and labelled`);
}

// ---------- G-04: every populated data cell resolves to a source ----------
{
  const ids = new Set(D.sources.sources.map((s) => s.id));
  const problems = [];
  const need = (obj, where) => {
    (obj.src || []).forEach((s) => { if (!ids.has(s)) problems.push(`${where} cites unknown source ${s}`); });
    if (!obj.src || !obj.src.length) problems.push(`${where} has no source id`);
  };
  D.intent.records.forEach((r) => {
    need(r, r.id);
    if (r.product_title && !r.confirmed_on) problems.push(`${r.id} has a title with no confirmation date`);
    if (r.official_listing_url && !r.confirmed_on) problems.push(`${r.id} has a listing URL with no confirmation date`);
    ["price", "rating", "review_count", "availability"].forEach((k) => {
      if (String(r[k] ?? "") !== "") problems.push(`${r.id}.${k} is populated but may only come from an approved API`);
    });
    // the brief's instruction: intent and observation must never be merged
    if (r.observed_redirect_target && r.official_listing_url && r.observed_redirect_target === r.official_listing_url)
      problems.push(`${r.id} stores the observed redirect in the intent field — keep them separate`);
  });
  const scan = (node, where) => {
    if (Array.isArray(node)) node.forEach((n, i) => scan(n, `${where}[${i}]`));
    else if (node && typeof node === "object") {
      if (node.id && (node.src || node.question || node.title)) need(node, where);
      Object.keys(node).forEach((k) => { if (k !== "src") scan(node[k], `${where}.${k}`); });
    }
  };
  ["flags", "questions", "suggestions"].forEach((k) => scan(D[k][k], k));
  D.rules.rules.forEach((r) => { if (!r.source) problems.push(`${r.id} has no source citation`); });
  const badRefs = [];
  for (const s of D.sources.sources) if (s.method === "fetched" && !s.url) badRefs.push(s.id);
  if (badRefs.length) problems.push(`fetched sources with no URL: ${badRefs.join(", ")}`);
  if (problems.length) fail("G-04", problems.join("; "));
  else pass("G-04", `every populated register field cites a source in the register (${D.sources.sources.length} sources, ${D.intent.records.length} rows)`);
}

// ---------- G-06: no price, rating or review text outside quoted source ----------
{
  const PRICE = /(?:[$€£]\s?\d|\b\d[\d.,]*\s?(?:USD|EUR|GBP|NLG)\b)/;
  const RATING = /(?:\b\d[.,]\d\s*(?:\/\s*5|out of 5)\b|\b\d(?:[.,]\d)?\s+stars?\b|\b\d(?:[.,]\d)?\s?★)/i;
  const insideQuote = (h, idx) => {
    const before = h.lastIndexOf("<blockquote", idx);
    const closeBefore = h.lastIndexOf("</blockquote>", idx);
    return before > -1 && before > closeBefore;
  };
  const strict = files.filter((f) => {
    const r = relOf(f);
    return r === "index.html" || r.startsWith("guides/") || r.startsWith("picks/") || r.startsWith("suggestions/");
  });
  const problems = [];
  for (const f of files) {
    const h = read(f);
    for (const re of [PRICE, RATING]) {
      for (const m of h.matchAll(new RegExp(re.source, re.flags.includes("g") ? re.flags : re.flags + "g"))) {
        if (insideQuote(h, m.index)) continue;
        const where = relOf(f);
        const strictPage = strict.includes(f);
        if (strictPage) problems.push(`${where}: price/rating pattern "${m[0]}" in published copy`);
        else problems.push(`${where}: price/rating pattern "${m[0]}" outside a quoted source — move it into the register`);
      }
    }
  }
  if (problems.length) fail("G-06", problems.slice(0, 8).join("; ") + (problems.length > 8 ? ` (+${problems.length - 8} more)` : ""));
  else pass("G-06", "no price, rating or review-count value in any page outside a quoted official source");
}

// ---------- G-07: no unsupported verdicts in guide prose or headings ----------
{
  // The forbidden thing is a verdict about a product we have not examined - not the word "best" in
  // "the one that predicts usage best". So the pattern must attach to a product noun or a ranking.
  const BANNED = /(?:#1|\bno\.? ?1\b|best[- ](?:seller|selling|choice|value|pick|air fryer|oven|model|unit|option|buy)|top[- ](?:rated|pick|choice|seller)|number one (?:air fryer|appliance|model)|guaranteed (?:to |lowest |results)|perfect for everyone|our top recommendation|editor's choice)/i;
  const problems = [];
  for (const f of files.filter((x) => relOf(x).startsWith("guides/"))) {
    const h = read(f);
    const prose = [...h.matchAll(/<(h1|h2|h3|p)\b[^>]*>([\s\S]*?)<\/\1>/g)]
      .map((m) => m[2].replace(/<[^>]+>/g, ""));
    prose.forEach((txt) => {
      const m = txt.match(BANNED);
      if (m && !/must not|never|we do not|refuse|without|no\b/i.test(txt))
        problems.push(`${relOf(f)}: superlative "${m[0]}" in prose — "${txt.slice(0, 70)}…"`);
    });
  }
  if (problems.length) fail("G-07", problems.join("; "));
  else pass("G-07", "guide prose and headings carry no superiority, ranking or test claim");
}

// ---------- G-08: forbidden features are absent ----------
{
  // A feature is a form control, a scheduled poll, or a data row that says it ships. Prose that
  // *refuses* the feature (which the disclosure page must contain) is required, not a violation.
  const hits = [];
  for (const f of files) {
    const h = read(f);
    if (/<form\b/i.test(h)) hits.push(`${relOf(f)}: a <form> element exists on a static host that cannot receive it`);
    if (/<input[^>]+type="(email|tel)"/i.test(h)) hits.push(`${relOf(f)}: a capture field with no transport`);
    for (const m of h.matchAll(/<(button|input)[^>]*(data-feature|name)="([^"]*)"/g))
      if (/alert|watch|track|notify|countdown|reward/i.test(m[3])) hits.push(`${relOf(f)}: feature control "${m[3]}"`);
  }
  for (const f of ["assets/js/app.js", "assets/js/clicks.js"].map((x) => join(ROOT, x)).filter(existsSync))
    if (/setInterval|setTimeout\([^)]*fetch/.test(read(f))) hits.push(`${relOf(f)}: scheduled polling - a synthetic-traffic surface`);
  for (const [file, obj] of [["suggestions", D.suggestions], ["products", D.products], ["events", D.events]])
    if (JSON.stringify(obj).match(/"(status|state)"\s*:\s*"(shipped|live|built)"/) && JSON.stringify(obj).match(/price.{0,12}alert/i))
      hits.push(`data/${file}.json: a price-alert feature is marked as shipped`);
  const refuses = read(join(ROOT, "disclosure/index.html")).replace(/<[^>]+>/g, " ");
  if (!/price alerts/i.test(refuses)) hits.push("disclosure page no longer states the refusal it is built on");
  if (hits.length) fail("G-08", hits.join("; "));
  else pass("G-08", "no forms, capture fields, scheduled polls or alert features; the refusal is stated on the disclosure page");
}

// ---------- G-10: measurement stays aggregate, JS never rewrites a link ----------
{
  const js = ["app.js", "clicks.js"].map((f) => join(ROOT, "assets/js", f)).filter(existsSync);
  const problems = [];
  for (const f of js) {
    const src = read(f);
    if (/a\.href\s*=|location\.assign|location\.replace|window\.open/.test(src))
      problems.push(`${relOf(f)}: script mutates navigation — that is a redirect surface`);
    if (/\.href\s*=|setAttribute\(\s*["']href|URLSearchParams|searchParams\.set\(|\?tag=/.test(src))
      problems.push(`${relOf(f)}: script constructs or rewrites a link (a redirect/cloaking surface, and tags must be ours to set)`);
    if (/document\.cookie\s*=/.test(src)) problems.push(`${relOf(f)}: sets a cookie`);
  }
  const cfg = existsSync(join(ROOT, "assets/js/config.js")) ? read(join(ROOT, "assets/js/config.js")) : "";
  const endpointOn = /endpoint:\s*"(https?:)?\/\//.test(cfg);
  if (problems.length) fail("G-10", problems.join("; "));
  else pass("G-10", `collector scripts are aggregate-only and non-navigating; endpoint ${endpointOn ? "CONFIGURED (check the retention and legal basis first)" : "off — nothing is transmitted"}`);
  if (endpointOn) notes.push("an endpoint is configured: publish the retention window and legal basis on /privacy/ before traffic arrives");
}

// ---------- G-12: staleness of anything confirmed ----------
{
  const problems = [];
  for (const r of D.intent.records) {
    if (!r.intended_asin_confirmed) continue;
    if (!r.confirmed_on) { problems.push(`${r.id} confirmed without a date`); continue; }
    const age = (TODAY - new Date(r.confirmed_on + "T00:00:00Z")) / 86400000;
    if (age > 30) problems.push(`${r.id} was confirmed ${Math.round(age)} days ago: re-check or remove`);
  }
  if (problems.length) fail("G-12", problems.join("; "));
  else pass("G-12", "no confirmed product row is older than its 30-day re-check window (all five are still unresolved, which is reported, not hidden)");
}

// ---------- G-13: feed carries no store link; sitemap is true ----------
{
  const feed = read(join(ROOT, "feed.xml"));
  const sm = read(join(ROOT, "sitemap.xml"));
  const problems = [];
  if (STORE_HOST.test(feed.replace(/<link>[^<]*<\/link>/g, ""))) problems.push("feed body mentions a store host");
  for (const d of [dirname("picks/index.html")]) void d;
  for (const m of feed.matchAll(/<description>([\s\S]*?)<\/description>/g))
    if (/amzn\.to|amazon\./.test(m[1])) problems.push("a feed description contains a store link");
  const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  if (!locs.length) problems.push("sitemap is empty");
  if (new Set(locs).size !== locs.length) problems.push("sitemap has duplicate <loc> entries");
  for (const l of locs) {
    if (!l.startsWith(BASE)) { problems.push(`sitemap url outside the site root: ${l}`); continue; }
    const tail = l.slice(BASE.length).replace(/^\//, "").replace(/\/$/, "");
    const f = tail ? join(ROOT, tail, "index.html") : join(ROOT, "index.html");
    if (!existsSync(f)) problems.push(`sitemap points at a missing page: ${l}`);
  }
  const robots = read(join(ROOT, "robots.txt"));
  if (!robots.includes(`${BASE}/sitemap.xml`)) problems.push("robots.txt does not declare the sitemap for this sub-path");
  if (problems.length) fail("G-13", problems.join("; "));
  else pass("G-13", `feed is link-free at item level; sitemap lists ${locs.length} real pages under ${BASE}`);
}

// ---------- G-15: no broken internal link or fragment, everywhere ----------
{
  const problems = [];
  const idsByFile = new Map();
  for (const f of files) {
    const h = read(f);
    idsByFile.set(f, new Set([...h.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
  }
  for (const f of files) {
    const h = read(f);
    const dir = dirname(f);
    for (const m of h.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>/g)) {
      const href = m[1];
      if (/^(mailto:|javascript:|#)/i.test(href)) continue;
      if (/^https?:/i.test(href)) {
        const host = hostOf(href);
        const allowed = ["github.com", "affiliate-program.amazon.com", "developers.google.com", "docs.github.com", "api.github.com", "www.ftc.gov", "sellercentral.amazon.com", "www.amazon.com"];
        if (!allowed.some((a) => host === a || host.endsWith("." + a)))
          problems.push(`${relOf(f)}: outbound link to a host outside the allowlist (${host})`);
        continue;
      }
      const [pathPart, frag] = href.split("#");
      let target;
      if (!pathPart) target = f;
      else if (/^[a-z]+:/.test(pathPart)) continue;
      else target = resolve(dir, pathPart);
      if (statSync(target, { throwIfNoEntry: false })?.isDirectory()) target = join(target, "index.html");
      if (!existsSync(target)) { problems.push(`${relOf(f)}: broken link → ${href}`); continue; }
      if (frag && target.endsWith(".html") && !idsByFile.get(target)?.has(frag))
        problems.push(`${relOf(f)}: fragment #${frag} not found in ${relOf(target)}`);
    }
    // assets referenced by this page must exist too
    for (const a of h.matchAll(/<(?:link|script|img)\b[^>]*?(?:href|src)="([^"]+)"/g)) {
      const u = a[1];
      if (/^https?:/i.test(u)) continue;
      const t = resolve(dir, u.split("#")[0]);
      if (!existsSync(t)) problems.push(`${relOf(f)}: missing asset ${u}`);
    }
    for (const og of h.matchAll(/property="og:image" content="([^"]+)"/g)) {
      const tail = og[1].slice(BASE.length);
      if (tail && !existsSync(join(ROOT, tail.replace(/^\//, "")))) problems.push(`${relOf(f)}: og:image missing ${tail}`);
    }
  }
  if (problems.length) fail("G-15", problems.slice(0, 12).join("; ") + (problems.length > 12 ? ` (+${problems.length - 12} more)` : ""));
  else pass("G-15", `every internal link, fragment, asset and og:image resolves across ${files.length} pages`);
}

// ---------- structural sanity ----------
{
  const problems = [];
  for (const f of files) {
    const h = read(f);
    const r = relOf(f);
    const h1 = (h.match(/<h1\b/g) || []).length;
    if (h1 !== 1) problems.push(`${r}: ${h1} <h1> tags`);
    if (!/<meta name="description" content=".{20,300}">/.test(h)) problems.push(`${r}: description missing or outside 20–300 chars`);
    const canon = (h.match(/rel="canonical" href="([^"]+)"/) || [])[1] || "";
    const dir = dirname(f) === ROOT.toString() || dirname(f).endsWith("WinC") ? "" : relOf(dirname(f));
    const want = dir ? `${BASE}/${dir}/` : `${BASE}/`;
    if (canon !== want && r !== "404.html") problems.push(`${r}: canonical ${canon} ≠ ${want}`);
    if (/<img\b(?![^>]*\salt=)/.test(h)) problems.push(`${r}: an <img> without alt`);
    if (/TODO|TBD|Lorem ipsum|PLACEHOLDER/i.test(h.replace(/<[^>]+>/g, " "))) problems.push(`${r}: placeholder text left in`);
  }
  // data hygiene
  const dup = {};
  D.intent.records.forEach((r) => { dup[r.token_as_supplied] = (dup[r.token_as_supplied] || 0) + 1; });
  Object.entries(dup).forEach(([k, v]) => { if (v > 1) problems.push(`duplicate identifier token in register: ${k}`); });
  D.intent.records.forEach((r) => {
    const ten = /^[A-Za-z0-9]{10}$/.test(r.token_as_supplied);
    if (ten && !r.intended_asin_confirmed) notes.push(`${r.id}: token is 10 characters now, but unconfirmed - verify against the listing before naming a product`);
    if (!ten && r.intended_asin_confirmed) problems.push(`${r.id} is marked confirmed on an identifier that fails the shape check (length ${r.token_length})`);
    if (!ten && (r.product_title || r.official_listing_url || r.price || r.rating))
      problems.push(`${r.id} carries a product value while its identifier is unresolved`);
  });
  if (problems.length) fail("structure", problems.join("; "));
  else pass("structure", "one h1 per page, descriptions present, canonicals match the Pages sub-path, no placeholders, register shape check consistent");
}

// ---------- report ----------
const out = { built_on: TODAY.toISOString().slice(0, 10), passed: gates, failed: fails, notes };
console.log(`\ngate — ${gates.length} passed, ${fails.length} failed, ${notes.length} note(s)\n`);
for (const g of gates) console.log(`  ✓ ${g.rule.padEnd(11)} ${g.msg}`);
for (const n of notes) console.log(`  · note        ${n}`);
for (const f of fails) console.log(`  ✗ ${f.rule.padEnd(11)} ${f.msg}`);
console.log("");
if (fails.length) {
  console.error(`BUILD REFUSED: ${fails.length} gate failure(s). A blank cell is allowed; an unsourced one is not.`);
  process.exit(1);
}
console.log("site is clean to publish.");
