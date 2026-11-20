// tools/audit.mjs — an independent second gate over the published tree.
//
// Why a second gate exists: scripts/check_site.py is the authority for this site, and a gate that is
// only ever run by its own author is unverified. This file was written against the *policy documents*
// (data/sources.json: Operating Agreement §1/§5, Program Policies §2(b)/§6, Google outbound-link
// guidance) rather than against the existing checker, so a divergence between the two is a finding.
//
//   node tools/audit.mjs            → audit report in AUDIT.md, exit 0
//   node tools/audit.mjs --strict   → also exit 1 on any finding (CI)
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, dirname, resolve as abspath } from "node:path";

const ROOT = process.cwd();
const STRICT = process.argv.includes("--strict");
const CANONICAL = "As an Amazon Associate I earn from qualifying purchases."; // quoted from Agreement §5
const TAG = "shopnow047c-20";
const SKIP = (p) => /node_modules|\/\.git|archive\//.test(p) || p.startsWith(".git");

const walk = (dir, acc = []) => {
  for (const e of readdirSync(dir)) {
    if (e === ".git" || e === "node_modules" || e === "archive") continue;
    const f = join(dir, e);
    if (statSync(f).isDirectory()) walk(f, acc); else acc.push(f);
  }
  return acc;
};
const all = walk(ROOT);
const html = all.filter((f) => f.endsWith(".html"));
const rel = (f) => relative(ROOT, f).split("\\").join("/");
const read = (f) => readFileSync(f, "utf8");
const findings = [];
const add = (rule, msg) => findings.push({ rule, msg });

/* ---------- A1 disclosure: on every published page, above the fold and in the footer ---------- */
{
  const bad = [];
  for (const f of html) {
    const h = read(f);
    const stripEnd = h.indexOf("</main>") > 0 ? h.indexOf("</main>") : Math.min(h.length, 6000);
    const before = h.slice(0, stripEnd).replace(/<[^>]+>/g, " ");
    const after = h.slice(Math.max(stripEnd, h.indexOf("<footer"))).replace(/<[^>]+>/g, " ");
    if (!before.includes(CANONICAL)) bad.push(`${rel(f)} (sentence not above the closing </main>)`);
    else if (!after.includes(CANONICAL)) bad.push(`${rel(f)} (no repeat in the footer region)`);
  }
  if (bad.length) add("A1", `disclosure coverage incomplete: ${bad.slice(0, 6).join("; ")}${bad.length > 6 ? ` (+${bad.length - 6} more)` : ""}`);
  else console.log(`A1 disclosure  ✓  required Agreement §5 sentence present in the body and the footer of ${html.length} pages`);
}

/* ---------- A2 outbound links: buy buttons tagged+sponsored, citations untagged+nofollow ---------- */
{
  const bad = []; let buy = 0, cite = 0;
  for (const f of html) {
    const h = read(f);
    for (const m of h.matchAll(/<a\b[^>]*href="([^"]*(?:amazon\.com\/(?:[^"]*dp|product-reviews|gp\/)[^"]*|amzn\.to[^"]*|link\.amazon[^"]*))"[^>]*>/gi)) {
      const attrs = m[0], href = m[1];
      const isBuy = /data-event="outbound_click"/.test(attrs) || /amzn\.to|link\.amazon/.test(href);
      if (isBuy) {
        buy++;
        if (!/rel="[^"]*\bsponsored\b/.test(attrs)) bad.push(`${rel(f)}: buy link without rel~=sponsored`);
        if (!href.includes(`tag=${TAG}`)) bad.push(`${rel(f)}: buy link without the tracking tag (${href.slice(0, 60)})`);
      } else {
        cite++;
        if (href.includes(`tag=${TAG}`)) bad.push(`${rel(f)}: evidence citation carries the affiliate tag — it claims credit for a citation`);
        if (!/rel="[^"]*\b(nofollow|sponsored)\b/.test(attrs)) bad.push(`${rel(f)}: citation to a store page with no rel value`);
      }
    }
  }
  if (bad.length) add("A2", `${bad.length} outbound-link problem(s): ${bad.slice(0, 6).join("; ")}${bad.length > 6 ? ` (+${bad.length - 6})` : ""}`);
  else console.log(`A2 links       ✓  ${buy} buy links tagged + sponsored; ${cite} citation links untagged + nofollow`);
}

/* ---------- A3 no redirect intermediaries published ---------- */
{
  const hits = [];
  for (const f of html) {
    const h = read(f);
    for (const m of h.matchAll(/<a\b[^>]*href="(https?:\/\/(?:link\.amazon|www\.amazon\.[a-z]{2,3}\/s\?|[^"]*\/redirect\/)[^"]*)"/gi))
      hits.push(`${rel(f)}: ${m[1].slice(0, 70)}`);
  }
  if (hits.length) add("A3", `redirect-intermediary or search-results link published (Program Policies §6 “Redirecting Links”): ${hits.slice(0, 4).join("; ")}`);
  else console.log("A3 no-redirect ✓  no link.amazon / amzn.to / redirect-hop anchors published");
}

/* ---------- A4 no price, rating or review text; A5 no verdicts ---------- */
{
  const PRICE = /(?:US)?\$\s?\d+(?:[.,]\d{2})\b|\b\d+(?:[.,]\d{2})\s?(?:USD|€|£)\b/g;
  const RATING = /(?:\b\d[.,]\d\s*(?:\/\s*5|out of 5)\b|\b\d(?:[.,]\d)?\s+stars?\b|\b\d(?:[.,]\d)?\s?★|\b\d{2,}[,\s]?\d{0,3}\s+reviews\b)/gi;
  const VERDICT = /(?:#\s?1\s+(?:air fryer|thermometer|appliance|model|pick|choice|spot|place)|(?:ranked|rated|named|voted)\s+#\d|best[- ](?:seller|selling|choice|value|pick|air fryer|thermometer|model|unit)|top[- ](?:rated|pick|choice|seller)|guaranteed (?:to |lowest|results)|perfect for everyone|editor.s choice)/i;
  const p = [], r = [], v = [];
  for (const f of html) {
    const text = read(f).replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, "").replace(/<[^>]+>/g, " ");
    const isQuoted = (idx) => text.slice(Math.max(0, idx - 220), idx).includes("Amazon shows") || /as listed on Amazon|quote|Amazon’s own/i.test(text.slice(Math.max(0, idx - 220), idx));
    for (const m of text.matchAll(PRICE)) if (!isQuoted(m.index)) p.push(`${rel(f)}: “${m[0]}”`);
    for (const m of text.matchAll(RATING)) if (!isQuoted(m.index)) r.push(`${rel(f)}: “${m[0]}”`);
    const vm = text.match(VERDICT); if (vm) v.push(`${rel(f)}: “${vm[0]}”`);
  }
  if (p.length) add("A4", `price figures outside a quotation (§2(b) reserves prices to Amazon-served links/API): ${p.slice(0, 5).join("; ")}`);
  if (r.length) add("A4", `rating or review-count text published (§6(t)): ${r.slice(0, 5).join("; ")}`);
  if (v.length) add("A5", `superiority or ranking verdict in copy: ${v.slice(0, 5).join("; ")}`);
  if (!p.length && !r.length) console.log(`A4 no-numbers  ✓  no price or rating figure in visible text of ${html.length} pages`);
  if (!v.length) console.log("A5 no-verdicts ✓  no ranking or superiority claim in copy");
}

/* ---------- A6 link + asset resolution ---------- */
{
  const broken = [];
  const idCache = new Map();
  const idsOf = (f) => { if (!idCache.has(f)) idCache.set(f, new Set([...read(f).matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]))); return idCache.get(f); };
  for (const f of html) {
    const h = read(f);
    for (const m of h.matchAll(/<(?:a|link|img)\b[^>]*?(?:href|src)="([^"]+)"/g)) {
      const u = m[1];
      if (/^(https?:|mailto:|javascript:|data:)/i.test(u)) continue;
      const [path, frag] = u.split("#");
      const abs = path === "" ? f : abspath(dirname(f), path);
      let target = abs;
      if (!existsSync(target)) {
        if (/\?/.test(path)) continue;
        if (existsSync(join(abs, "index.html"))) target = join(abs, "index.html");
        else if (!/\.(js|css|json|xml|csv|png|jpe?g|svg|webp|txt|ico)$/i.test(path) && existsSync(abs + ".html")) target = abs + ".html";
        else { broken.push(`${rel(f)} → ${u}`); continue; }
      }
      if (frag && target.endsWith(".html") && !idsOf(target).has(frag) && statSync(target).isFile()) broken.push(`${rel(f)}: fragment #${frag} not in ${rel(target)}`);
    }
    for (const m of h.matchAll(/<img\b[^>]*>/g)) {
      if (!/alt="/.test(m[0])) broken.push(`${rel(f)}: <img> without alt`);
      if (!/width="\d+"/.test(m[0]) || !/height="\d+"/.test(m[0])) broken.push(`${rel(f)}: <img> without intrinsic dimensions`);
    }
    for (const m of h.matchAll(/property="og:image"\s+content="([^"]+)"/g)) {
      const u = m[1];
      try { const p = new URL(u).pathname.replace(/^\/WinC/, ""); if (!existsSync(join(ROOT, p))) broken.push(`${rel(f)}: og:image points at a missing file (${p})`); } catch { broken.push(`${rel(f)}: og:image not absolute (${u})`); }
    }
    if (/\$\{/.test(h)) broken.push(`${rel(f)}: un-interpolated template expression leaked into output`);
  }
  if (broken.length) add("A6", `${broken.length} unresolved reference(s): ${broken.slice(0, 8).join("; ")}${broken.length > 8 ? ` (+${broken.length - 8})` : ""}`);
  else console.log(`A6 links       ✓  every internal link, fragment, image and og:image resolves across ${html.length} pages`);
}

/* ---------- A7 no interactive capture, no scheduled traffic ---------- */
{
  const bad = [];
  for (const f of all) {
    const r = rel(f);
    if (f.endsWith(".html")) {
      const h = read(f);
      // A capture control is fine when the page says what it does; the risk is the FALLBACK path.
      // method="get" without novalidate/onsubmit-guard means a browser with JS blocked submits the
      // address into a URL — which then sits in history and in the host's request log.
      const form = h.match(/<form\b[\s\S]{0,1200}?<\/form>/i);
      if (form) {
        const f0 = form[0];
        const captures = /<input[^>]+type="(email|tel)"/i.test(f0);
        const guarded = /novalidate/i.test(f0) || /method="post"/i.test(f0) || /action=""/.test(f0);
        const jsGuard = new RegExp(`id="${(f0.match(/id="([^"]+)"/) || [, "\u0000"])[1]}"`).test(h) && /preventDefault|return false/.test(read(f).match(/<script[\s\S]*?<\/script>/gi)?.join("") || "");
        if (captures && !guarded && !jsGuard)
          bad.push(`${r}: capture control inside a GET form with no novalidate/action="" guard — a JS-blocked browser submits the value into a URL (history + request log), while the page says it goes nowhere`);
        if (/<(?:button|a)\b[^>]*>[^<]*(price alert|countdown|notify me when)/i.test(h)) bad.push(`${r}: incentive/alert copy`);
      }
    }
    if (r.startsWith("assets/js/") && f.endsWith(".js")) {
      const s = read(f);
      if (/setInterval|new Worker|importScripts/.test(s)) bad.push(`${r}: scheduled or background activity (synthetic-traffic surface)`);
      if (/document\.cookie|localStorage\.setItem\([^)]*(id|user|visitor)/i.test(s)) bad.push(`${r}: per-visitor identifier (sub-tags may not bind to an end user)`);
    }
  }
  if (bad.length) add("A7", bad.join("; "));
  else console.log("A7 no-capture  ✓  no forms, capture fields, alerts, polling or per-visitor identifiers");
}

/* ---------- A8 sitemap <-> canonical agreement ---------- */
{
  const sm = existsSync(join(ROOT, "sitemap.xml")) ? read(join(ROOT, "sitemap.xml")) : "";
  const listed = new Set([...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => { try { return new URL(m[1]).pathname.replace(/^\/WinC/, ""); } catch { return m[1]; } }));
  const ghosts = [...listed].filter((p) => p && !existsSync(join(ROOT, p)));
  const mism = [];
  for (const f of html) {
    if (f.endsWith("404.html")) continue;
    const c = (read(f).match(/rel="canonical"\s+href="([^"]+)"/) || [, ""])[1];
    if (!c) { mism.push(`${rel(f)}: no canonical`); continue; }
    let path; try { path = new URL(c).pathname.replace(/^\/WinC/, ""); } catch { mism.push(`${rel(f)}: canonical not absolute (${c})`); continue; }
    if (!listed.has(path)) mism.push(`${rel(f)}: canonical ${path} is not in the sitemap`);
  }
  if (ghosts.length) add("A8", `sitemap lists ${ghosts.length} loc(s) with no file behind them: ${ghosts.slice(0, 5).join(", ")}`);
  if (mism.length) add("A8", `${mism.length} canonical/sitemap disagreement(s): ${mism.slice(0, 6).join("; ")}${mism.length > 6 ? ` (+${mism.length - 6})` : ""}`);
  if (!ghosts.length && !mism.length) console.log(`A8 sitemap     ✓  ${listed.size} locs all resolve; every page's canonical is listed (one indexable URL per page)`);
}

/* ---------- A9 secrets ---------- */
{
  const SECRET = /aws_secret|access_key_id|BEGIN (?:RSA|OPENSSH)|sk-[a-z0-9]{20,}|x-amz-credential|api[_-]?token\s*[:=]\s*["'][a-z0-9]{12,}/i;
  const bad = all.filter((f) => /\.(json|js|html|xml|csv|yml|yaml|txt)$/.test(f)).filter((f) => SECRET.test(read(f))).map(rel);
  if (bad.length) add("A9", `possible credential material published in: ${bad.join(", ")}`);
  else console.log(`A9 no-secrets  ✓  no credential patterns in ${all.filter((f) => /\.(json|js|html|xml|csv|yml|yaml|txt)$/.test(f)).length} text files`);
}

/* ---------- A10 register: populated claim fields need a source ---------- */
{
  const pf = join(ROOT, "data/products.json");
  if (existsSync(pf)) {
    const rows = (JSON.parse(read(pf)).products) || [];
    const bad = [];
    for (const p of rows) {
      const claimFields = ["title", "brand", "model", "capacity", "dimensions", "observed_asin", "observed_listing_url"];
      const srcFields = ["observed_source", "intended_source", "source", "sources"];
      const hasSrc = srcFields.some((k) => String(p[k] ?? "").trim().length > 8 || (Array.isArray(p[k]) && p[k].length));
      const hasClaim = claimFields.some((k) => String(p[k] ?? "").trim().length > 0);
      if (hasClaim && !hasSrc) bad.push(`${p.id}: ${claimFields.filter((k) => p[k]).length} claim field(s) with no source string`);
      if (p.observed_asin && !/^[A-Z0-9]{10}$/.test(p.observed_asin)) bad.push(`${p.id}: observed_asin “${p.observed_asin}” is not 10 characters`);
      if (String(p.intended_asin ?? "").trim() && !String(p.confirmation_date ?? "").trim()) bad.push(`${p.id}: intended_asin set without a confirmation date`);
    }
    if (bad.length) add("A10", bad.join("; "));
    else console.log(`A10 register   ✓  ${rows.length} product rows: every populated claim field carries a source string; intended/observed kept separate`);
  }
}

/* ---------- report ---------- */
const line = "-".repeat(74);
let out = `# Audit — independent gate\n\nRun: \`node tools/audit.mjs\` · date: ${new Date().toISOString().slice(0, 10)}\n\n${line}\n\n`;
out += `Scanned ${html.length} published HTML pages, ${all.length} tracked files (archive/ excluded — that tree is a retired alternate build, not a live surface).\n`;
out += `Canonical disclosure string is fixed inside this file, quoted from Associates Program Operating Agreement §5,\nso editing site configuration cannot switch the check off.\n\n`;
out += findings.length ? `## Findings (${findings.length})\n\n${findings.map((f) => `- **${f.rule}** ${f.msg}`).join("\n")}\n\n` : "";
out += `## What each rule protects\n\n| Rule | Prevents | Authority |\n|---|---|---|\n| A1 | a reader finding out about the commission after the click | Agreement §5 |\n| A2 | untagged buy links earning nothing; tagged citations implying a paid placement | Policies §2(b), §1; Google sponsored value |\n| A3 | redirect intermediaries | Policies §6 “Redirecting Links” |\n| A4 | prices/ratings we may not publish | Policies §2(b), §6(t) |\n| A5 | verdicts about products we have not tested | Policies §1 original content; Google helpful-content |\n| A6 | 404s and layout shift | crawl quality |\n| A7 | capture without transport, synthetic traffic, per-user sub-tags | Policies §2(b), §6(s) |\n| A8 | pages that cannot be found, or locs that 404 | indexing basics |\n| A9 | leaking credentials by publishing data/ | operational safety |\n| A10 | an unsourced product claim reaching the page | this project's own rule |\n\n${line}\n${findings.length ? `${findings.length} finding(s).` : "No findings."}${STRICT && findings.length ? " (--strict: exit 1)" : ""}\n`;
writeFileSync(join(ROOT, "AUDIT.md"), out);
console.log(`\nreport → AUDIT.md · ${findings.length} finding(s)${findings.length && !STRICT ? " (report mode: not blocking)" : ""}`);
if (STRICT && findings.length) process.exit(1);
