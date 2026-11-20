// tools/build.mjs — deterministic site generator.
// Data (data/*.json, content/guides/*.json) in, static HTML + sitemap + feed out.
// The published tree is the repo root because Pages is configured with source branch `main`, path `/`.
import { writeFileSync, readFileSync, mkdirSync, rmSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { loadAll, sourceMap, sourceLink, esc, inline, dateLong, ROOT, badge, STATE } from "./lib.mjs";

const D = loadAll();
const SRC = sourceMap(D.sources);
const CFG = D.config;
const BASE = CFG.site.base_url.replace(/\/$/, "");   // https://host/WinC
const TODAY = "2026-11-20";
const built = [];
const warnings = [];
const readText = (p) => readFileSync(p, "utf8");
const loadGuide = (f) => JSON.parse(readText(f));
const GUIDE_REL = "../../";
// intrinsic sizes so the browser can reserve the box (no layout shift on a slow phone)
const IMG_DIMS = { "hero.png": [1200, 654], "og.png": [1200, 633], "capacity.png": [1100, 600] };
// rich(): for HTML this file authored (tables that carry inline <code>/<a>). Data-file prose goes
// through inline(), which escapes; build-authored markup must survive.
const rich = (v) => String(v ?? "").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
const dims = (name) => { const d = IMG_DIMS[name] || [1200, 675]; return `width="${d[0]}" height="${d[1]}"`; };

// ---------- small view helpers ----------
const relrootOf = (dir) => (dir ? "../".repeat(dir.split("/").length) : "./");
const urlOf = (dir) => (dir ? `${BASE}/${dir}/` : `${BASE}/`);
const pill = (kind, extra = "") => badge(kind) + extra;

function row(cells, tag = "td") {
  return `<tr>${cells.map((c) => `<${tag}>${c}</${tag}>`).join("")}</tr>`;
}
function table(head, rows, opts = {}) {
  const cls = ["grid-table", opts.cls].filter(Boolean).join(" ");
  return `<div class="tablewrap"><table class="${cls}"><thead>${row(head, "th")}</thead><tbody>${rows.join("\n")}</tbody></table></div>`
    + (opts.caption ? `<p class="tcap">${inline(opts.caption)}</p>` : "");
}
function srcList(ids) {
  if (!ids || !ids.length) return "";
  const items = ids.map((id) => {
    const s = SRC.get(id);
    if (!s) { warnings.push(`unknown source id: ${id}`); return `<li class="src-missing">⚠ ${esc(id)} — not in register</li>`; }
    return `<li>${sourceLink(s)}</li>`;
  });
  return `<ul class="srcs">${items.join("")}</ul>`;
}
const blank = (reason) => `<span class="blank" title="${esc(reason || "")}">—<span class="blank-note"> not verified</span></span>`;

// ---------- page shell ----------
function shell(p) {
  const rel = p.relroot;
  const strip = `<div class="disclosure" role="note">
  <p class="disclosure-in"><span class="disc-required">${esc(CFG.monetization.earnings_statement)}</span>
  <span class="disc-plain">Every link to a store on this site is a paid link: if you buy after clicking it we may earn a commission, at no cost to you. We show no prices, ratings or review text, because we cannot verify a single product yet — <a href="${rel}disclosure/">what that means in practice</a>.</span>
  <a class="disc-more" href="${rel}disclosure/">Disclosure</a></p>
</div>`;

  const nav = D.editorial.nav.reader.map((n) => {
    const href = n.href.replace(/^\.\//, rel);
    const active = p.navKey && href.replace(/\/$/, "").endsWith(p.navKey);
    return `<a href="${href}"${active ? ' aria-current="page"' : ""}>${esc(n.label)}</a>`;
  }).join("");

  const groups = D.editorial.nav;
  const footWork = groups.single_group_for_dashboards.items.map((n) =>
    `<a href="${n.href.replace(/^\.\//, rel)}">${esc(n.label)}</a>`).join("");
  const footRead = groups.reader.map((n) =>
    `<a href="${n.href.replace(/^\.\//, rel)}">${esc(n.label)}</a>`).join("");

  const ld = p.ld ? `<script type="application/ld+json">${JSON.stringify(p.ld)}</script>` : "";

  return `<!doctype html>
<html lang="${CFG.site.default_locale}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(p.title)}</title>
<meta name="description" content="${esc(p.desc)}">
<link rel="canonical" href="${esc(p.canonical)}">
<meta name="theme-color" content="#f6f3ec">
<meta property="og:type" content="${p.ogType || "website"}">
<meta property="og:site_name" content="${esc(CFG.brand.name)}">
<meta property="og:title" content="${esc(p.title)}">
<meta property="og:description" content="${esc(p.desc)}">
<meta property="og:url" content="${esc(p.canonical)}">
<meta property="og:image" content="${BASE}/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="${esc(CFG.brand.name)} — new guides" href="${rel}feed.xml">
<link rel="stylesheet" href="${rel}assets/styles.css">
${ld}
</head>
<body class="pg-${p.cls}">
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <div class="mast-in">
    <a class="brand" href="${rel}">
      <span class="brand-mark" aria-hidden="true"></span>
      <span class="brand-txt"><span class="brand-name">${esc(CFG.brand.name)}</span><span class="brand-kicker">${esc(CFG.brand.kicker)}</span></span>
    </a>
    <p class="issue">Issue ${esc(String(CFG.issue.number).padStart(2, "0"))} · ${esc(dateLong(CFG.issue.date))} · ${esc(CFG.issue.season)}</p>
  </div>
  <nav class="nav" aria-label="Reader"><div class="nav-in">${nav}</div></nav>
</header>
${strip}
<main id="main">${p.body}</main>
<footer class="foot">
  <div class="foot-in">
    <div class="foot-brand">
      <p class="foot-name">${esc(CFG.brand.name)}</p>
      <p class="foot-tag">${esc(CFG.brand.tagline)}</p>
      <p class="foot-note">${esc(CFG.authorship.provenance)}</p>
    </div>
    <nav class="foot-col" aria-label="Read"><h2>${esc(groups.reader[0].label)} &amp; more</h2>${footRead}
      <a href="${rel}guides/">Guides index</a><a href="${rel}feed.xml">RSS feed</a><a href="${rel}sitemap.xml">Sitemap</a></nav>
    <nav class="foot-col" aria-label="${esc(groups.single_group_for_dashboards.label)}">
      <h2>${esc(groups.single_group_for_dashboards.label)}</h2>${footWork}</nav>
    <nav class="foot-col" aria-label="Policies"><h2>Policies &amp; contact</h2>
      <a href="${rel}disclosure/">Affiliate disclosure</a><a href="${rel}privacy/">Privacy &amp; measurement</a>
      <a href="${rel}about/">About, authorship &amp; corrections</a>
      <a href="${CFG.site.repo}" rel="noopener">Source repository</a></nav>
  </div>
  <div class="foot-bar"><div class="foot-bar-in">
    <p class="disc-required">${esc(CFG.monetization.earnings_statement)}</p>
    <p class="foot-fine">Registered tracking ID on outbound links: <code>${esc(CFG.monetization.tracking_id)}</code> · ${esc(CFG.monetization.tracking_id_status)}. Built from data in <code>data/</code>; every table cell that is not blank names its source. Site generated ${esc(TODAY)}.</p>
  </div></div>
</footer>
<script src="${rel}assets/js/app.js" defer></script>
<script src="${rel}assets/js/clicks.js" defer></script>
</body></html>`;
}

function emit(dir, p) {
  const relroot = relrootOf(dir);
  // Bodies are written root-relative ("./picks/"). Rewrite only the paths that really are site-root
  // paths, so a sibling link on /guides/ (./capacity-checklist/) is left alone while /about/'s
  // ./picks/ becomes ../picks/.
  const ROOT_PATHS = /^(picks|guides|sources|suggestions|questions|flagged|how-it-works|measurement|executive-summary|disclosure|privacy|about|data|assets|feed\.xml|sitemap\.xml|robots\.txt)/;
  const depthFix = (str) => str.replace(/(['"])\.\/([^'"]*)\1/g, (m, q, rest) =>
    (rest === "" || ROOT_PATHS.test(rest)) ? q + relroot + rest + q : m);
  // single-quoted attributes normalise to double quotes so the link gate can see every href
  const body = (relroot === "./" ? p.body : depthFix(p.body))
    .replace(/href='([^']*)'/g, (m, v) => `href="${v.replace(/"/g, "&quot;")}"`);
  const html = shell({ ...p, relroot, canonical: urlOf(dir), body });
  const file = join(ROOT, dir, "index.html");
  if (dir) mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, html);
  built.push({
    dir, relroot, file: dir ? `${dir}/index.html` : "index.html",
    canonical: urlOf(dir), title: p.title, desc: p.desc,
    type: p.type || "webpage", date: p.date || TODAY, modified: p.modified || p.date || TODAY,
    noindex: !!p.noindex,
  });
}

// ---------- guide block renderer ----------
function renderBlocks(blocks) {
  return blocks.map((b) => {
    switch (b.t) {
      case "lead": return `<p class="lede">${inline(b.x)}</p>`;
      case "h2": return `<h2 id="${slug(b.x)}">${inline(b.x)}</h2>`;
      case "h3": return `<h3>${inline(b.x)}</h3>`;
      case "p": return `<p>${inline(b.x)}</p>`;
      case "ul": return `<ul class="plain">${b.items.map((i) => `<li>${inline(i)}</li>`).join("")}</ul>`;
      case "check": return `<section class="checks"><h3>${inline(b.x || "Checklist")}</h3><ul>${b.items.map((i) => `<li>${inline(i)}</li>`).join("")}</ul></section>`;
      case "table": return table(b.head, b.rows.map((r) => row(r.map((c) => inline(c)))), { caption: b.caption });
      case "callout": return `<aside class="callout callout-${b.kind || "note"}"><p>${inline(b.x)}</p>${b.src ? `<p class="callout-src">Related: ${b.src.map((s) => `<a href="${GUIDE_REL}${/^SRC-/.test(s) ? "sources" : "flagged"}/#${s.toLowerCase()}">${s}</a>`).join(", ")}</p>` : ""}</aside>`;
      case "quote": return `<figure class="quote"><blockquote>${esc(b.x)}</blockquote><figcaption>${esc(b.cite)} ${b.src ? `<a href="${GUIDE_REL}sources/#${b.src.toLowerCase()}">${b.src}</a>` : ""}</figcaption></figure>`;
      case "figure": return `<figure class="fig"><img src="${GUIDE_REL}assets/img/${b.src}" alt="${esc(b.alt)}" loading="lazy" ${dims(b.src)}><figcaption>${inline(b.cap)} <span class="fig-tag">illustration, not product imagery</span></figcaption></figure>`;
      case "unverified": return `<section class="unver"><h3>Not answered by this page</h3><ul>${b.items.map((i) => `<li>${inline(i)}</li>`).join("")}</ul></section>`;
      default: warnings.push(`unknown block type ${b.t}`); return "";
    }
  }).join("\n");
}
// guide pages sit under /guides/<slug>/ so links to site pages need one extra level
// guide pages sit two levels below the site root

function slug(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);
}

// ---------- guides ----------
const guideDir = join(ROOT, "content", "guides");
const guides = readdirSync(guideDir).filter((f) => f.endsWith(".json")).map((f) => {
  const g = loadGuide(join(guideDir, f));
  const meta = D.editorial.guides.find((x) => x.slug === g.slug) || {};
  return { ...meta, ...g };
});


// ---------- HOME ----------
const counts = {
  sources: D.sources.sources.length,
  fetched: D.sources.sources.filter((s) => s.method === "fetched").length,
  rules: D.rules.rules.length,
  flags: D.flags.flags.filter((f) => f.status.startsWith("needs")).length,
  rows: D.intent.records.length,
  unresolved: D.intent.records.filter((r) => r.status === "unresolved").length,
  ideas: D.suggestions.suggestions.length,
  questions: D.questions.questions.length,
  guides: guides.length,
};

const heroGuides = guides.slice(0, 4);
const lead = heroGuides[0];
const rest = heroGuides.slice(1);

emit("", {
  cls: "home", navKey: "",
  title: `${CFG.brand.name} — ${CFG.brand.kicker}`,
  desc: `${CFG.brand.tagline} Question-shaped buyer guides for small kitchen appliances, with every claim tied to a source and no price or rating we cannot verify. Issue ${CFG.issue.number}, ${dateLong(CFG.issue.date)}.`,
  ogType: "website",
  date: CFG.issue.date,
  ld: {
    "@context": "https://schema.org", "@type": "WebSite",
    name: CFG.brand.name, alternateName: CFG.brand.short_name,
    description: CFG.brand.kicker, url: `${BASE}/`,
    publisher: { "@type": "Organization", name: CFG.brand.name },
  },
  body: `
<section class="hero">
  <div class="hero-main">
    <p class="kicker">Front page · ${esc(CFG.brand.promise)}</p>
    <h1>${esc(lead.title)}</h1>
    <p class="hero-dek">${inline(lead.dek)}</p>
    <p class="hero-meta">Published ${esc(dateLong(lead.published_on))} · ${esc(lead.author)} · ${lead.reading_time_min} min · <span class="tag-honest">no product named inside</span></p>
    <p class="hero-cta"><a class="btn btn-a" href="./guides/${lead.slug}/">Read the guide</a>
      <a class="btn btn-b" href="./picks/">See the desk &amp; what's blank</a></p>
  </div>
  <aside class="hero-side" aria-label="Desk status">
    <h2>Desk status</h2>
    <dl class="stats">
      <div><dt>Products supplied</dt><dd>${counts.rows}</dd></div>
      <div><dt>Confirmed enough to name</dt><dd class="alert">${counts.rows - counts.unresolved}</dd></div>
      <div><dt>Sources read from the publisher</dt><dd>${counts.fetched}<span class="of">/${counts.sources}</span></dd></div>
      <div><dt>Rules enforced at build time</dt><dd>${counts.rules}</dd></div>
      <div><dt>Items flagged for you</dt><dd>${counts.flags}</dd></div>
    </dl>
    <p class="hero-side-note">${esc(D.products.desk_statement)}</p>
  </aside>
</section>

<figure class="fig fig-lead">
  <img src="./assets/img/hero.png" alt="Illustration: a basket-style air fryer with its drawer pulled open, beside a cross-section diagram showing air circulating over a single layer of food, a folded towel and a tape measure on the counter." width="1200" ${dims("hero.png")}>
  <figcaption>The one comparison that matters is air reaching food. Our diagrams are drawn for this publication — <span class="fig-tag">illustration, not product imagery</span>, because reusing a store's photographs is a rights question we have not settled.</figcaption>
</figure>

<section class="band">
  <div class="band-head"><h2>On the desk now</h2><a class="more" href="./picks/">Full register →</a></div>
  <div class="verdict">
    <p class="verdict-line"><strong>${D.intent.records.length} links were supplied for marketing.</strong>
      All five are in the same state: the identifier measures ${D.intent.records[0].token_length} characters,
      no tracking tag is present in the address, and none of the four product fields
      (title, listing, price, rating) could be confirmed from an official source.</p>
    <ul class="chips">
      ${D.intent.records.map((r) => `<li><code>${esc(r.token_as_supplied)}</code><span>${r.token_length} chars · ${r.intended_asin_confirmed ? "confirmed" : "unresolved"}</span></li>`).join("")}
    </ul>
    <p class="verdict-foot">${counts.unresolved} of ${counts.rows} rows are blocked on three questions the account owner can answer in about fifteen minutes —
      <a href="./questions/#q-01">Q-01</a>, <a href="./questions/#q-02">Q-02</a>, <a href="./questions/#q-03">Q-03</a>.
      When they are answered, the titles below fill themselves and the guides gain a product link beside a “(paid link)” label.</p>
  </div>
</section>

<section class="band">
  <div class="band-head"><h2>Guides</h2><a class="more" href="./guides/">All ${counts.guides} →</a></div>
  <div class="cards">
    ${rest.concat(guides.slice(4)).map((g) => `
    <article class="card">
      <p class="card-kicker">${esc(g.cluster || "desk")} · ${esc(dateLong(g.published_on))}</p>
      <h3><a href="./guides/${g.slug}/">${esc(g.title)}</a></h3>
      <p>${esc(g.dek)}</p>
      <p class="card-foot"><span>${g.reading_time_min || 4} min</span><span class="dot">·</span><span>method, not measurement</span></p>
    </article>`).join("")}
  </div>
</section>

<section class="band two">
  <div>
    <div class="band-head"><h2>Before you decide anything</h2><a class="more" href="./questions/">${counts.questions} questions →</a></div>
    <ol class="qlist">
      ${D.questions.questions.filter((q) => q.severity === "blocking").map((q) => `
      <li><a href="./questions/#${q.id.toLowerCase()}"><strong>${esc(q.id)}</strong> ${esc(q.question)}</a>
        <span class="qwhy">${esc(q.what_we_lack)}</span></li>`).join("")}
    </ol>
  </div>
  <div>
    <div class="band-head"><h2>Ideas board</h2><a class="more" href="./suggestions/">${counts.ideas} suggestions →</a></div>
    <p class="lede-sm">Each idea lists its real options, a recommendation, and the instruction to hand a build session. Nothing is implemented until a row is accepted.</p>
    ${table(["Ref", "Suggestion", "Impact", "Decision"], D.suggestions.suggestions.slice(0, 5).map((s) =>
      row([`<code>${s.id}</code>`, `<a href="./suggestions/#${s.id.toLowerCase()}">${esc(s.title)}</a>`,
        `<span class="imp imp-${s.impact.split(" ")[0]}">${esc(s.impact)}</span>`, pill("pending")])))}
  </div>
</section>

<section class="band strip">
  <h2>What this site will not do</h2>
  <ul class="no">
    <li>Show a price, a star rating or a review quote. <span>Affiliate terms permit those only through an Amazon-served link or the approved API, and this desk has neither.</span></li>
    <li>Name a product we have not resolved. <span>A guide about an unconfirmed ASIN is a guide about a guess.</span></li>
    <li>Build a price-drop alert, a countdown, or a reward for clicking. <span>Each is expressly restricted by the program rules; each would also make the site worse to read.</span></li>
    <li>Score an appliance out of ten. <span>Nothing here has been cooked in.</span></li>
  </ul>
</section>
`,
});

// ---------- GUIDE pages ----------
for (const g of guides) {
  const rel = `../../`;
  emit(`guides/${g.slug}`, {
    cls: "guide", navKey: "guides",
    title: g.title,
    desc: g.dek,
    ogType: "article",
    date: g.published_on, modified: g.reviewed_on || g.published_on,
    ld: {
      "@context": "https://schema.org", "@type": "BlogPosting",
      headline: g.title, description: g.dek,
      image: `${BASE}/assets/img/hero.png`,
      datePublished: g.published_on, dateModified: g.reviewed_on || g.published_on,
      author: { "@type": "Organization", name: CFG.authorship.desk },
      publisher: { "@type": "Organization", name: CFG.brand.name },
      mainEntityOfPage: urlOf(`guides/${g.slug}`),
      inLanguage: CFG.site.default_locale,
    },
    body: `
<article class="article">
  <header class="art-head">
    <p class="kicker"><a href="${rel}guides/">Guides</a> · ${esc(g.cluster)}</p>
    <h1>${esc(g.title)}</h1>
    <p class="dek">${esc(g.dek)}</p>
    <p class="art-meta"><span>${esc(g.author)}</span><span class="dot">·</span><span>Published ${esc(dateLong(g.published_on))}</span>
      <span class="dot">·</span><span>Reviewed ${esc(dateLong(g.reviewed_on || g.published_on))}</span>
      <span class="dot">·</span><span>${g.reading_time_min} min</span></p>
    <p class="prov">${esc(g.provenance)}</p>
  </header>
  <div class="art-body">${renderBlocks(g.blocks)}</div>
  <footer class="art-foot">
    <p class="art-disc"><span class="disc-required">${esc(CFG.monetization.earnings_statement)}</span> — this page carries no store link, so there is nothing to label. When a product is confirmed, its link here will sit next to a <code>${esc(CFG.monetization.link_level_label)}</code> tag.</p>
    ${(g.related || []).length ? `<p class="related">Read next: ${(g.related || []).map((r) => `<a href="${rel}guides/${r}/">${esc((guides.find((x) => x.slug === r) || {}).title || r)}</a>`).join(" · ")}</p>` : ""}
    ${g.cta && g.cta.kind === "internal" ? `<p class="cta-inline"><a class="btn btn-b" href="${rel}${g.cta.href.replace(/^\.\//, "")}">${esc(g.cta.label)}</a></p>` : ""}
  </footer>
</article>`,
  });
}

// ---------- GUIDES index ----------
const byCluster = {};
for (const g of guides) (byCluster[g.cluster] ||= []).push(g);
emit("guides", {
  cls: "index", navKey: "guides",
  title: `Guides — ${CFG.brand.name}`,
  desc: "Buyer-method guides for small kitchen appliances: what to compare, what to measure, and which fields on a listing are verifiable. No product claims we cannot source.",
  body: `
<header class="page-head"><p class="kicker">${esc(CFG.brand.kicker)}</p>
<h1>Guides, by the question they answer</h1>
<p class="sub">Six clusters, ${guides.length} guides. Each is written to be useful without a single unverified product claim — which is why none of them names a model, and why the desk page has blanks in it.</p></header>
${D.editorial.clusters.map((c) => {
    const list = byCluster[c.slug] || [];
    return `<section class="cl">
  <h2>${esc(c.name)} <span class="cl-q">— ${esc(c.question)}</span></h2>
  <p class="cl-why">${esc(c.why)}</p>
  ${list.length ? `<ul>${list.map((g) => `<li><a href="./${g.slug}/">${esc(g.title)}</a><span>${esc(g.dek)}</span><span class="li-meta">${g.published_on}</span></li>`).join("")}</ul>`
      : `<p class="none">Nothing published in this cluster yet. It is queued, not forgotten: see the unranked list below.</p>`}
</section>`;
  }).join("")}
<section class="cl cl-queue"><h2>In the queue, unranked</h2>
<p class="cl-why">${esc(D.editorial.cadence.queue_policy)}</p>
${table(["Topic", "Cluster", "State"], D.editorial.upcoming_unranked.map((u) =>
    row([esc(u.topic), esc(u.cluster), `<span class="dim">${esc(u.state)}</span>`])))}
</section>`,
});

// ---------- PICKS (desk) ----------
const cols = D.products.columns;
emit("picks", {
  cls: "desk", navKey: "picks",
  title: `The Desk — five links, what we could confirm — ${CFG.brand.name}`,
  desc: "Product-intent register for the five supplied links: intended identifier, confirmation date and source, with observed redirect targets kept in a separate column and never merged.",
  body: `
<header class="page-head"><p class="kicker">Product desk · register</p>
<h1>Five links, zero confirmed products</h1>
<p class="sub">${esc(D.products.desk_statement)}</p>
<p class="policy"><strong>${esc(D.products.value_policy)}</strong></p></header>

<section class="band">
  <div class="band-head"><h2>Register</h2><p class="hint">Blank is a value. It means “no official confirmation reachable” — the reason is in the footer of the table.</p></div>
  ${table(cols.map((c) => esc(c.label)), D.intent.records.map((r) => {
    const cell = (c) => {
      const v = c.key === "token" ? r.token_as_supplied
        : c.key === "shape" ? `<span class="${r.token_length === 9 ? "fail" : "ok"}">${r.token_length} chars${r.token_length === 9 ? " · shape check failed" : ""}</span>`
        : c.key === "row" ? `<code>${r.id}</code>`
        : c.key === "supplied_link" ? `<code class="mono-xs">${esc(r.supplied_link.replace("https://", ""))}</code>`
        : c.key === "intended_asin_confirmed" ? (r.intended_asin_confirmed ? "yes" : `<span class="no">no</span>`)
        : r[c.key === "title" ? "product_title" : c.key];
      if (v === "" || v === null || v === undefined) return blank(c.blank_reason || "not confirmed by an official source");
      return typeof v === "string" && v.startsWith("<") ? v : esc(v);
    };
    return row(cols.map((c) => cell(c)));
  }))}
  <p class="blanks"><strong>About the address column.</strong> We print each supplied address instead of linking it: the destination is unconfirmed, the URL carries no tracking tag, and a reader should never be sent somewhere we cannot vouch for. Copy it to check it yourself, then confirm it with <a href="https://affiliate-program.amazon.com/help/operating/policies" rel="noopener">the linking requirements</a> open.</p>
  <p class="blanks"><strong>Why the empty columns are empty.</strong> Title, listing URL, price, rating and redirect target all require opening a listing. Egress from the build environment to the store is refused (see <a href="./flagged/#flg-003">FLG-003</a>), and price and rating fields are additionally restricted by the program rules (<a href="./flagged/#flg-005">FLG-005</a>). We did not fill any of them in.</p>
</section>

<section class="band two">
  <div>
    <div class="band-head"><h2>Per-row evidence</h2></div>
    ${D.intent.records.map((r) => `
    <article class="ev">
      <h3>${r.id} <span class="dim">${esc(r.token_as_supplied)}</span></h3>
      <dl class="kv">
        <dt>Intended identifier (as supplied)</dt><dd><code>${esc(r.intended_asin)}</code> ${r.intended_asin_confirmed ? "" : `<span class="no">· unconfirmed</span>`}</dd>
        <dt>Official listing URL</dt><dd>${r.official_listing_url ? esc(r.official_listing_url) : blank("no confirmed listing")}</dd>
        <dt>Confirmed on / by / source</dt><dd>${[r.confirmed_on, r.confirmed_by, r.confirmation_source].filter(Boolean).join(' · ') || blank('no confirmation event has taken place')}</dd>
        <dt>Observed redirect target <span class="sep">(kept separate, never merged with the two fields above)</span></dt><dd>${r.observed_redirect_target ? `<code>${esc(r.observed_redirect_target)}</code>` : `<span class="dim">${esc(r.observation_status)}</span>`}</dd>
        <dt>Observation detail</dt><dd class="small">${esc(r.observation_evidence)}</dd>
        <dt>Blocked by</dt><dd>${(r.blocks || []).map((b) => `<a href="./questions/#${b.toLowerCase()}">${b}</a>`).join(" ")}</dd>
        <dt>Flags</dt><dd>${(r.related_flags || []).map((b) => `<a href="./flagged/#${b.toLowerCase()}">${b}</a>`).join(" ")}</dd>
        <dt>Sources</dt><dd class="sr-inline">${srcList(r.src)}</dd>
      </dl>
    </article>`).join("")}
  </div>
  <div>
    <div class="band-head"><h2>What a row here is for</h2></div>
    <ul class="plain">${D.products.what_a_row_gives_the_reader.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
    <aside class="callout callout-note"><p>${esc(D.products.editorial_context.note)}</p>${srcList(D.products.editorial_context.src)}</aside>
    <h2 class="h-sm">The one test worth running this week</h2>
    <p>Per the project brief: one link per product, in the enrolled Associates flow, confirming the destination and that tracking reports it — before scaling to all five. Two constraints on that test are worth stating out loud: a test <em>purchase</em> through your own link is prohibited, and purchases by friends, relatives or employees are too, so confirmation must come from the click showing up in the account's own reports, not from a bought item. And the short links as supplied are not declared invalid here; that question stays open.</p>
    <p class="srcs-inline">${srcList(["SRC-02"])}${"" /* FLG-003 tracked separately */}</p>
  </div>
</section>`,
});

// ---------- SOURCES ----------
emit("sources", {
  cls: "sources", navKey: "sources",
  title: `Source register — ${CFG.brand.name}`,
  desc: "Every official page this site relied on, with the date it was read, how it was read, and the load-bearing sentence quoted so a reviewer can diff our claim against the source.",
  body: `
<header class="page-head"><p class="kicker">Verification</p>
<h1>Source register</h1>
<p class="sub">Read the quote, then the claim. <code>method</code> says exactly how we know: <em>fetched</em> means this session opened the page on the publisher's own domain; <em>referenced</em> means we could not open it and said so instead of assuming.</p></header>
${D.sources.sources.map((s) => `
<section class="srcrow" id="${s.id.toLowerCase()}">
  <h2><span class="src-id">${s.id}</span> ${esc(s.title)}</h2>
  <p class="src-pub">${esc(s.publisher)} · <span class="kind kind-${s.kind}">${esc(s.kind)}</span> · ${s.method === "fetched" ? `read ${esc(s.fetched_on)}` : s.method === "api" ? `observed ${esc(s.fetched_on)} via API` : s.method === "operator" ? "supplied in the brief" : s.method === "local" ? "measured in the build sandbox" : "not opened by us"}</p>
  ${s.page_states_updated ? `<p class="src-upd">Page states it was updated: ${esc(s.page_states_updated)}</p>` : ""}
  ${s.url ? `<p class="src-url"><a href="${esc(s.url)}" rel="noopener" target="_blank">${esc(s.url)}</a></p>` : `<p class="src-url dim">no URL — ${esc(s.kind)}</p>`}
  <p class="src-why">${esc(s.why_it_matters)}</p>
  ${(s.quotes || []).length ? `<div class="quotes">${s.quotes.map((q) => `<figure><blockquote>${esc(q.text)}</blockquote><figcaption>${esc(q.ref)}</figcaption></figure>`).join("")}</div>` : `<p class="dim small">No quotation stored — this row supports a negative finding (we could not confirm the thing), not a positive claim.</p>`}
</section>`).join("")}
<section class="band"><div class="band-head"><h2>How to audit this in ten minutes</h2></div>
<ol class="plain-ol">
  <li>Open the <a href="./flagged/">flagged list</a>. It names every claim this site declined to make.</li>
  <li>Pick one quote above and search for it on the source page. It should appear verbatim.</li>
  <li>Check a table cell on <a href="./picks/">the desk</a>. Every non-blank value should have a source id; every blank should have a reason.</li>
  <li>Run <code>npm run verify</code> in the repository. The same rules that bind the build are listed on <a href="./how-it-works/">Compliance &amp; the gate</a>.</li>
</ol></section>`,
});

// ---------- QUESTIONS ----------
emit("questions", {
  cls: "questions", navKey: "workroom",
  title: `Open questions — ${CFG.brand.name}`,
  desc: "What must be known before a reasonable decision can be made about this site: each question, the decision it unblocks, what we have, what we lack, and exactly where to find the answer.",
  body: `
<header class="page-head"><p class="kicker">Decision preconditions</p>
<h1>${D.questions.questions.length} questions that have to be answered first</h1>
<p class="sub">${esc(D.questions.how_to_read)}</p></header>
${table(["Ref", "Question", "Severity", "Answered by", "Status"], D.questions.questions.map((q) =>
    row([`<code>${q.id}</code>`, `<a href="#${q.id.toLowerCase()}">${esc(q.question)}</a>`,
      `<span class="sev sev-${q.severity.split(" ")[0]}">${esc(q.severity)}</span>`,
      esc(q.who_can_answer), q.answer ? '<span class="ok">answered</span>' : '<span class="no">open</span>'])),
  { caption: "Nothing on this list is rhetorical. Each one is the reason a column above it is blank." })}
${D.questions.questions.map((q) => `
<section class="q" id="${q.id.toLowerCase()}">
  <h2><span class="qid">${q.id}</span> ${esc(q.question)}</h2>
  <dl class="qdl">
    <dt>Decision it unblocks</dt><dd>${esc(q.decision_it_unblocks)}</dd>
    <dt>What we have</dt><dd>${esc(q.what_we_have)}</dd>
    <dt>What we lack</dt><dd class="lack">${esc(q.what_we_lack)}</dd>
    <dt>How to find out</dt><dd class="how">${esc(q.how_to_find_out || q.how_to_unblock)}</dd>
    <dt>Who can answer</dt><dd>${esc(q.who_can_answer)}</dd>
    <dt>Blocks</dt><dd>${(q.blocks || []).map((b) => `<code>${b}</code>`).join(" ") || "—"}</dd>
    <dt>If nobody answers</dt><dd class="dim">${esc(q.default_if_unanswered)}</dd>
    <dt>Answer</dt><dd class="answer">${q.answer ? esc(q.answer) : `<span class="no">empty on purpose</span> — this column is filled by a human or an account, never inferred`}</dd>
    <dt>Sources</dt><dd class="sr-inline">${srcList(q.src)}</dd>
  </dl>
</section>`).join("")}`,
});

// ---------- SUGGESTIONS ----------
emit("suggestions", {
  cls: "sugg", navKey: "suggestions",
  title: `Ideas board — ${CFG.brand.name}`,
  desc: "Every proposal for the site, with its real options, trade-offs, a recommendation and the exact instruction to hand a build session. Nothing is implemented until a row is accepted.",
  body: `
<header class="page-head"><p class="kicker">Review before you build</p>
<h1>${D.suggestions.suggestions.length} suggestions, each with the options spelled out</h1>
<p class="sub">Use the controls to accept, reject or defer a path. Choices are stored in this browser only and are never sent anywhere; the export button turns them into a block of markdown you can paste straight into a build session, which is how a decision here becomes a commit there.</p>
<p class="legend">${Object.entries(D.suggestions.state_legend).map(([k, v]) => `<span><strong>${esc(k)}</strong> — ${esc(v)}</span>`).join("")}</p>
<div class="decide-bar" id="decide-bar">
  <p><strong id="d-count">0</strong> of ${D.suggestions.suggestions.length} decided in this browser.
  <button type="button" class="btn btn-a" data-act="export">Export decisions as markdown</button>
  <button type="button" class="btn btn-c" data-act="clear">Clear my local choices</button></p>
  <pre class="export" id="export-out" hidden></pre>
</div>
${table(["Ref", "Suggestion", "Impact", "Effort", "Needs answered first", "Recommendation"], D.suggestions.suggestions.map((s) =>
    row([`<code>${s.id}</code>`, `<a href="#${s.id.toLowerCase()}">${esc(s.title)}</a>`,
      `<span class="imp imp-${s.impact.split(" ")[0]}">${esc(s.impact)}</span>`, `<code>${s.effort}</code>`,
      (s.depends_on || []).map((d) => `<a href="./questions/#${d.toLowerCase()}">${d}</a>`).join(" ") || "—",
      esc(s.recommendation.length > 110 ? s.recommendation.slice(0, 107) + "…" : s.recommendation)])))}
${D.suggestions.suggestions.map((s) => `
<section class="sg" id="${s.id.toLowerCase()}" data-sg="${s.id}">
  <h2><span class="sgid">${s.id}</span> ${esc(s.title)}</h2>
  <p class="sg-one">${esc(s.one_line)}</p>
  <p class="sg-why"><span class="lbl">Why</span>${esc(s.why)}</p>
  <div class="opts">
    ${s.options.map((o, i) => `<label class="opt"><input type="radio" name="d-${s.id}" value="${esc(o.label)}" data-sg="${s.id}">
      <span class="opt-body"><strong>${esc(o.label)}</strong><em>${esc(o.detail)}</em><span class="trade"><b>Trade-off:</b> ${esc(o.tradeoff)}</span></span></label>`).join("")}
  </div>
  <p class="sg-rec"><span class="lbl">Recommended</span>${esc(s.recommendation)}</p>
  <p class="sg-meta">Effort <code>${esc(s.effort)}</code> · Impact <code>${esc(s.impact)}</code> · Depends on ${(s.depends_on || []).map((d) => `<a href="./questions/#${d.toLowerCase()}">${d}</a>`).join(", ") || "nothing"}</p>
  <div class="prompt"><p class="lbl">Hand this to a build session</p>
    <pre><code>${esc(s.prompt_snippet)}</code></pre>
    <button type="button" class="btn btn-c" data-act="copy" data-for="${s.id}">Copy instruction</button></div>
  <p class="sg-state">Status: <span class="pill">${esc(s.decision)}</span> · chosen option: <span class="pill">${esc(s.accepted_option || "none")}</span></p>
</section>`).join("")}`,
});

// ---------- FLAGS ----------
emit("flagged", {
  cls: "flags", navKey: "workroom",
  title: `Flagged for review — ${CFG.brand.name}`,
  desc: "Everything this project could not verify, chose not to guess, or found inconsistent in its own instructions — with the source that shows it.",
  body: `
<header class="page-head"><p class="kicker">Needs review</p>
<h1>${D.flags.flags.length} things we are not pretending about</h1>
<p class="sub">None of these block the site. Each one blocks a specific claim, and the claim is simply not made. Where a flag says “unresolved”, it stays unresolved because the evidence to settle it is not reachable from this workspace — not because we decided it.</p></header>
${D.flags.flags.map((f) => `
<section class="fl" id="${f.id.toLowerCase()}">
  <h2><span class="flid">${f.id}</span> ${esc(f.title)} <span class="flsev">severity: ${esc(f.severity)}</span></h2>
  <dl class="fldl">
    <dt>Observed</dt><dd>${esc(f.observed)}</dd>
    <dt>Why it matters</dt><dd>${esc(f.why_it_matters)}</dd>
    <dt>What we did</dt><dd>${esc(f.we_did)}</dd>
    ${f.we_did_not ? `<dt>What we did not do</dt><dd>${esc(f.we_did_not)}</dd>` : ""}
    <dt>Resolution</dt><dd class="how">${esc(f.resolution)}</dd>
    <dt>Status</dt><dd>${esc(f.status)}</dd>
    <dt>Sources</dt><dd class="sr-inline">${srcList(f.src)}</dd>
  </dl>
</section>`).join("")}`,
});

// ---------- HOW IT WORKS ----------
emit("how-it-works", {
  cls: "rules", navKey: "workroom",
  title: `Compliance and the publishing gate — ${CFG.brand.name}`,
  desc: "The rules this site is built against, quoted from Amazon's own agreement and policies, with which of them a build can enforce automatically and which one a human has to look at.",
  body: `
<header class="page-head"><p class="kicker">Machinery</p>
<h1>What is automated, and what is gated</h1>
<p class="sub">Everything in the left column below runs on <code>npm run verify</code> and fails the build. Everything in the right column needs a person, because it depends on an account, a listing, or a judgement we refuse to fake.</p></header>
<section class="band">
  <div class="band-head"><h2>Pipeline</h2></div>
  ${(() => {
    const P = [
      ["Ingest supplied links", "auto", "t-auto", "Validated for shape (length, case, host) by the intent register; a token that fails the shape check can never become a published claim.", "SRC-12"],
      ["Confirm product identity", "human", "t-human", "Needs a real listing opened by the account owner. Recorded per row in <code>data/product-intent.json</code>, kept separate from any observed redirect.", "SRC-01 §1"],
      ["Build Special Links", "auto", "t-auto", "The generator emits the tagged format with <code>rel=&quot;sponsored nofollow&quot;</code> and the (paid link) label; the gate rejects a store link without a tag.", "SRC-01 §1 · SRC-02 §2(b) · SRC-16"],
      ["Write the guide", "drafted auto, owned by a person", "t-mixed", "Blocks come from <code>content/guides/*.json</code>; a named reviewer must set <code>reviewed_on</code> before a claim gets stronger than method.", "SRC-02 §1 · SRC-08"],
      ["Publish price or rating", "blocked, not declined", "t-blocked", "Not permitted from this position: only an Amazon-served link or the approved API may carry those values, and API access needs a sales threshold. The build forbids the pattern outright.", "SRC-02 §2(b), §6(t) · SRC-05"],
      ["Keep content fresh", "auto-flag, human-check", "t-mixed", "Rows older than 30 days fail the build, so the removal duty cannot be quietly skipped.", "SRC-02 §6(c)"],
      ["Sitemap, feed, canonical", "auto", "t-auto", "Regenerated from the guide registry on every build; the feed body carries no store link.", "SRC-07 · SRC-02 §4"],
      ["Measure clicks", "auto, local-only", "t-auto", "Counter in the visitor's browser; posting disabled until an endpoint exists. Never a per-visitor sub-tag.", "SRC-02 §2(b), §6(s)"],
      ["Optimise campaigns", "not built, on purpose", "t-none", "No campaign logic exists that could act on unverified data; the ledger starts empty by design.", "—"],
    ];
    return table(["Stage", "Automated?", "How it works here", "Rule"], P.map(([a, b, cls, c, d]) => row([
      `<strong>${esc(a)}</strong>`, `<span class="ptag ${cls}">${esc(b)}</span>`, rich(c), rich(d).replace(/ · /g, "<br>"),
    ])), { caption: "Read the middle column as the promise and the last column as the reason the promise is shaped that way." });
  })()}
</section>
<section class="band two">
  <div><div class="band-head"><h2>Why the AI pipeline is smaller than the brief implies</h2></div>
  <p>Two published constraints shape it, and they are worth stating before anyone builds an agent.</p>
  <ul class="plain">
    <li>Program Content and Special Links may not be used to develop machine-learning models or related technology without Amazon's prior written approval.</li>
    <li>Product data access runs through the Creators API, which requires an enrolled account and at least ten qualifying sales in the past thirty days; the older PA-API 5 endpoint returns 403 Forbidden.</li>
  </ul>
  <p>So the automatable part of “AI-powered” here is generation and hygiene: drafting structure, validating identifiers, keeping the sitemap and feed true, refusing a page that contains an unsourced claim, and queueing stale rows. The part that is not automatable from a repository is <em>acquiring the facts</em> — and pretending otherwise is how affiliate sites end up with invented prices.</p>
  <p class="rule-src">Sources: <a href="./sources/#src-02">SRC-02 §5, §6(s)</a>, <a href="./sources/#src-05">SRC-05</a>, <a href="./sources/#src-06">SRC-06</a>.</p></div>
  <div><div class="band-head"><h2>Build &amp; deploy</h2></div>
  <p>The site is generated, so the HTML you are reading is an artefact, not a hand-written file. Commands:</p>
  <ul class="code-list">
    <li><code>npm run build</code> — regenerate every page, the sitemap and the feed</li>
    <li><code>npm run check</code> — the gate: links, disclosure, sponsored rels, tag presence, price/rating patterns, sourced cells</li>
    <li><code>npm run verify</code> — build, then gate; this is what CI runs</li>
    <li><code>npm run serve</code> — preview at <code>http://localhost:8080/WinC/</code> with the same sub-path as Pages</li>
  </ul>
  <p>Deployment is GitHub Pages, publishing from branch <code>main</code> at <code>/</code> with a legacy build, which is why generated HTML sits at the repository root rather than in a <code>docs/</code> or <code>dist/</code> folder.</p>
  <p class="rule-src">Sources: <a href="./sources/#src-09">SRC-09</a>, <a href="./sources/#src-10">SRC-10</a>.</p></div>
</section>`,
});

// ---------- MEASUREMENT ----------
const ledger = readText(join(ROOT, "data/ledger.csv")).trim().split("\n");
emit("measurement", {
  cls: "meas", navKey: "workroom",
  title: `Measurement plan — ${CFG.brand.name}`,
  desc: "Five proposed events, an empty campaign ledger whose columns require an authorized first-party source, and the honest limits of what a static host can count.",
  body: `
<header class="page-head"><p class="kicker">Measure before optimising</p>
<h1>What gets counted, and what is deliberately missing</h1>
<p class="sub">${esc(D.events.provenance)}. The brief asked for “the five defined events” without enumerating them, so this is a proposal — and the proposal is recorded as a flag, not as a standard <a href="./flagged/#flg-009">(FLG-009)</a>.</p></header>
<section class="band">
  <div class="band-head"><h2>Events</h2><p class="hint">Storage: ${esc(D.events.storage.default)}</p></div>
  ${D.events.events.map((e) => `
  <article class="ev-def" id="ev-${e.name}">
    <h3><code>${esc(e.name)}</code> ${e.reportable_now ? '<span class="ok">collectible today</span>' : '<span class="no">needs a host</span>'}</h3>
    <p>${esc(e.why)}</p>
    <p class="ev-trig"><span class="lbl">Trigger</span>${esc(e.trigger)}</p>
    ${table(["Field", "Value"], e.fields.map((f) => row([`<code>${esc(f.k)}</code>`, esc(f.v)])))}
    <p class="ev-auth"><span class="lbl">Ledger may ingest</span>${esc(e.authorized_source_for_ledger)}</p>
  </article>`).join("")}
  <aside class="callout callout-warn"><p><strong>Hard rules baked into the collector.</strong> ${D.events.storage.compliance.map((c) => esc(c)).join(" ")}</p></aside>
</section>
<section class="band two">
  <div><div class="band-head"><h2>Campaign ledger</h2><p class="hint">Header defined, zero rows: no authorized report has been read into this repository.</p></div>
  <div class="csv"><table class="grid-table"><thead>${ledger[0].split(",").map((c) => `<th><code>${esc(c.trim())}</code></th>`).join("")}</thead>
  <tbody><tr><td class="empty-row" colspan="${ledger[0].split(",").length}">no rows — every column requires a first-party report before it may be filled</td></tr></tbody></table></div>
  <p class="dim small">Machine-readable version: <a href="./data/ledger.csv"><code>data/ledger.csv</code></a>. Written only by <code>npm run ledger:add</code>-style tooling with a source argument, never by hand-editing a number into a page.</p></div>
  <div><div class="band-head"><h2>Reporting rhythm</h2></div>
  <ul class="plain">
    <li><strong>Weekly</strong> — desk note: pages added, rows still unresolved, gate failures, ledger rows recorded <em>if</em> a report was read.</li>
    <li><strong>Monthly</strong> — cluster review: which question got impressions; the next topic is picked from that, not from preference.</li>
    <li><strong>On event</strong> — any stale product row (30 days) triggers a re-check or removal, because that is the rule, not a nicety.</li>
  </ul>
  <p>What we will not publish: a conversion rate, an estimated EPC, or a revenue forecast. Each needs inputs this desk is either not permitted to hold or has never seen, and a number that cannot be defended is worse than an empty cell.</p>
  <aside class="callout callout-note"><p>${esc(CFG.privacy.host_logs_ips)} That is why <a href="./privacy/">the privacy page</a> says “we send nothing” rather than “nothing is recorded”.</p></aside>
  </div>
</section>`,
});

// ---------- EXEC SUMMARY ----------
emit("executive-summary", {
  cls: "exec", navKey: "workroom",
  title: `Executive summary — ${CFG.brand.name}`,
  desc: "One page: what was asked for, what exists, what blocks it, and the order in which the rest can honestly be done.",
  body: `
<header class="page-head"><p class="kicker">Read this first</p>
<h1>Executive summary</h1>
<p class="sub">Written ${esc(dateLong(TODAY))} by session <code>arena-04112b09</code>, after a line-by-line pass over the brief, the repository, and six official pages.</p></header>
<section class="exec">
  <h2>1 · The situation in one paragraph</h2>
  <p>The brief asked for a compliant, traffic-worthy Amazon affiliate publication built around five products, plus the automation to research, publish and optimise it at scale. The repository was empty when this session started — one commit, a six-byte README — so there was no prior source register to polish. Of the five product identifiers supplied, none can currently be resolved to a listing, which means the only honest product page is a register of what is missing. Everything else the brief asked for — a shop-like front page, question-shaped guides, disclosure above the fold, sponsored links, sitemap and feed, a measurement plan, an empty-but-defined campaign ledger, and a gate that refuses unsourced claims — is built and live.</p>
  <h2>2 · What is live now</h2>
  ${table(["Surface", "State", "Where"], [
    ["Publication front page with disclosure strip, desk status and guide rail", "live", "./|front page"],
    [`${counts.guides} buyer-method guides, question-shaped, zero product claims`, "live", "./guides/|Guides"],
    ["Product-intent register: five rows, intended identifier, confirmation fields, separate redirect column", "live · all rows unresolved", "./picks/|The Desk"],
    [`Source register with quoted official text and read-dates`, `live · ${counts.fetched}/${counts.sources} fetched`, "./sources/|Source register"],
    [`${counts.rules}-rule publishing gate wired into the build`, "enforced", "./how-it-works/|Compliance & the gate"],
    ["Sitemap, RSS (no store links in item bodies), canonical, BlogPosting markup", "live", "./sitemap.xml|sitemap.xml"],
    ["Outbound click counter, local-only; collector shipped disabled", "live, in safe mode", "./measurement/|Measurement"],
    ["Campaign ledger: headers defined, zero rows", "ready, empty", "./data/ledger.csv|data/ledger.csv"],
    [`${counts.ideas}-row ideas board with options, recommendation and copy-paste build instructions`, "awaiting decisions", "./suggestions/|Ideas"],
    [`${counts.questions} open questions with discovery steps`, "three of them blocking", "./questions/|Open questions"],
    [`${D.flags.flags.length} flagged irregularities with sources`, "published", "./flagged/|Flagged for review"],
  ].map((r) => row([`<span>${esc(r[0])}</span>`, `<span class="ok">${esc(r[1])}</span>`, (() => { const [h, l] = r[2].split("|"); return `<a href="${h}">${esc(l)}</a>`; })()])))}
  <h2>3 · The three facts that changed the plan</h2>
  <ol class="plain-ol">
    <li><strong>Prices and ratings are not free data.</strong> They may be shown only where Amazon serves the link or from the approved API, and review/star display is tied to that same API. Result: no number in any currency appears anywhere on this site, and the build fails if one is added by hand.</li>
    <li><strong>The API that would power “automated research” is behind a sales gate.</strong> Creators API requires an enrolled account and at least ten qualifying sales in the last thirty days; PA-API 5 is deprecated and returns 403. Result: automation is sequenced <em>after</em> content earns, not before — and the ledger stays empty rather than predictive.</li>
    <li><strong>Some obvious affiliate tricks are explicitly forbidden.</strong> Price alerts, per-visitor sub-tagging, incentivised clicks, pop-ups, redirect intermediaries and search-engine placements on “amazon” keywords each have a clause. Result: they are absent by construction, and the gate asserts their absence.</li>
  </ol>
  <h2>4 · What is blocking the commercial half</h2>
  <p>Three blocking questions, all answerable by the account owner in under fifteen minutes: which product each link points at (<a href="./questions/#q-01">Q-01</a>), whether the identifier tokens are truncated (<a href="./questions/#q-02">Q-02</a>), and which marketplace the tracking ID is registered against (<a href="./questions/#q-03">Q-03</a>). Until those are answered, the site can publish method but not verdicts — which is exactly the distinction the guides are built on.</p>
  <h2>5 · Recommended path, in order</h2>
  ${table(["#", "Move", "Why this order", "Board ref"], [
    ["1", "Resolve the five identifiers by regenerating one tagged link per product from its listing", "Every other decision depends on knowing what the product is, and this motion satisfies the Special Link rule at the same time", "<a href='./suggestions/#sg-01'>SG-01</a>, <a href='./suggestions/#sg-02'>SG-02</a>"],
    ["2", "Fix the marketplace/locale (US vs NL/EU) before writing for it", "A wrong store link loses the sale and the reader at once; geo-redirects are prohibited so the choice has to be explicit", "<a href='./suggestions/#sg-03'>SG-03</a>"],
    ["3", "Publish one guide a week from the four briefed questions, then pick the fifth from Search Console queries", "Cadence with a measured selector is the only version of 'content strategy' this desk can defend", "<a href='./suggestions/#sg-08'>SG-08</a>, <a href='./suggestions/#sg-09'>SG-09</a>"],
    ["4", "Turn on measurement in the safe order: local counters + Search Console; collector only with a host and a legal basis", "Static hosting cannot receive events, and per-visitor tagging is barred; the honest floor is aggregate counting", "<a href='./suggestions/#sg-06'>SG-06</a>"],
    ["5", "Decide authorship (a named human) before any claim gets stronger than method", "The disclosure sentence is first-person; endorsements need an endorser", "<a href='./suggestions/#sg-12'>SG-12</a>"],
    ["6", "After ten qualifying sales in thirty days, unlock the API and only then build price-aware comparison tables and a staleness bot", "This is the sequence the rules force: content earns the data access, the data access earns the automation", "<a href='./suggestions/#sg-05'>SG-05</a>, <a href='./suggestions/#sg-07'>SG-07</a>"],
    ["7", "Keep the domain decision open until ten guides exist, then move with one commit", "Canonicals and the sitemap are generated; flip them once, deliberately", "<a href='./suggestions/#sg-10'>SG-10</a>"],
  ].map((r) => row(r.map((c, i) => i === 0 ? `<span class="stepno">${c}</span>` : rich(c)))))}
  <h2>6 · What this summary does not claim</h2>
  <ul class="plain">
    <li>It does not claim traffic, rankings, conversions or revenue. There is no measurement history in this repository, and the ledger is empty on purpose.</li>
    <li>It does not claim the five supplied links are invalid. Their compliance status is unresolved and stays flagged.</li>
    <li>It does not claim any product is good, bad, or suitable for you. No product has been confirmed, let alone tested.</li>
    <li>It does not present the ASIN length rule as verified from an official page; we reported a measurement, not a verdict from a source we could not open.</li>
  </ul>
  <p class="exec-close">Everything above is reproducible: the data files are published next to the HTML, the quotes are in the register, and <code>npm run verify</code> re-runs the whole argument.</p>
</section>`,
});

// ---------- DISCLOSURE / PRIVACY / ABOUT ----------
emit("disclosure", {
  cls: "policy", navKey: "",
  title: `Affiliate disclosure — ${CFG.brand.name}`,
  desc: "Exactly what our relationship with Amazon is, where the disclosures appear, and what this site refuses to publish.",
  body: `
<header class="page-head"><p class="kicker">Disclosure</p><h1>Who pays for what, here</h1></header>
<p class="lede"><strong>${esc(CFG.monetization.earnings_statement)}</strong> That sentence is the wording the Associates Program Operating Agreement requires, and we reproduce it without changing it. It appears at the top of every page, again in the footer of every page, and again at the end of every guide.</p>
${(() => {
  const LL = CFG.monetization.link_level_label, TID = CFG.monetization.tracking_id;
  const R = [
    ["The required sentence",
     "Strip under the masthead on every page; repeated in the footer; repeated on each guide",
     "The agreement requires it to be clearly and prominently stated on the site, and a reader should not have to scroll to find out who may be paid"],
    ["A link-level label",
     `Immediately beside each store link, reading “${LL}”`,
     "Amazon's own help separates the site-wide sentence from the label that sits next to a link"],
    ["The sponsored value",
     "In the markup of every store link: <code>rel=“sponsored nofollow”</code>",
     "Google documents <code>sponsored</code> as the value for paid placements; it costs us no traffic, because attribution is carried by the tag parameter, not by a search engine"],
    ["The tracking tag",
     `In the URL of every store link: <code>tag=${TID}</code>`,
     "The agreement permits only the tagged link formats Amazon provides, and an untagged link does not accrue"],
  ];
  return table(["What", "Where it appears", "Why"], R.map(([a, b, c]) =>
    row([`<strong>${esc(a)}</strong>`, rich(b), rich(c)])),
    { caption: "There are currently no store links to any product on this site, because no product is confirmed. The rules above are implemented in the generator and asserted by the gate, so the first real link is compliant on the day it appears." });
  })()}
<h2>What we will not do to earn a commission</h2>
<ul class="plain">
  <li>No prices, availability, star ratings or review text — only an Amazon-served link or the approved API may carry those, and we have neither.</li>
  <li>No price alerts, countdowns, “#1 best” badges, or invented test results.</li>
  <li>No redirect through an intermediate page: a link that sends a reader on without a click of their own disqualifies the purchase and hides the destination.</li>
  <li>No paid search on Amazon's own trademarks, and no Special Links inside an RSS item body or in unsolicited email.</li>
  <li>No reward, perk or donation incentive for clicking.</li>
</ul>
<p class="dim small">Full rule list with sources on <a href="./how-it-works/">Compliance &amp; the gate</a>. Corrections and contact route on <a href="./about/">About</a>.</p>`,
});

emit("privacy", {
  cls: "policy", navKey: "",
  title: `Privacy and measurement — ${CFG.brand.name}`,
  desc: "What this site records, what it sends, what the host logs, and what it will never do.",
  body: `
<header class="page-head"><p class="kicker">Privacy</p><h1>Nothing is sent off your device by us</h1></header>
<p class="lede">This is a static site. There is no analytics tag, no advertising pixel, no social widget and no third-party script: the two JavaScript files are ours, are same-origin, and load nothing else. Our own click counter keeps its totals in your browser's local storage and posts them nowhere — the collector ships switched off.</p>
${table(["Recorded", "Where", "Retention", "Sent to us?"], [
  ["Guide read progress, outbound link taps, decision-board choices", "your browser's <code>localStorage</code>", "until you clear it; a button on the ideas board clears it", "No. There is no endpoint configured."],
  ["Your IP address", "GitHub Pages, for security, per its own documentation", "as the host's policy states", "Not by us — by the host. We do not receive it."],
  ["Cookies", "— none set by this site", "—", "n/a"],
  ["Email address", "not collected; there is no signup form that transmits anything", "—", "n/a"],
].map((r) => row(r.map(rich))))}
<h2>If you turn the collector on</h2>
<p>The plan, in <a href="./suggestions/#sg-06">SG-06</a>, is an aggregate counter on infrastructure the operator runs, with a short retention window, no IP capture, and no per-visitor identifier. Two of those are not merely taste: the Associates terms bar associating a sub-tag or programme reporting with a specific end user, and they bar generating clicks or sessions artificially — so the collector is written to count events, never to invent them, and to refuse a visitor key outright.</p>
<p class="dim small">Readers in the EU: this site has no consent banner because it sets no cross-site trackers; the disclosure here is the notice. That position depends on the collector staying off, and it is <a href="./questions/#q-11">an open question (Q-11)</a> for the operator, not a legal conclusion.</p>`,
});

emit("about", {
  cls: "policy", navKey: "",
  title: `About, authorship and corrections — ${CFG.brand.name}`,
  desc: "Who writes here, how, with what limits, and how to correct us.",
  body: `
<header class="page-head"><p class="kicker">About</p><h1>${esc(CFG.brand.name)}</h1>
<p class="sub">${esc(CFG.brand.tagline)} ${esc(CFG.brand.promise)}</p></header>
<h2>Who made this</h2>
<p>Byline: <strong>${esc(CFG.authorship.desk)}</strong>. ${esc(CFG.authorship.provenance)}</p>
<p>There is no named human author yet, and we will not invent one. A fake reviewer would be a false identity in the masthead and a misleading endorsement in the copy at the same time, so every page here stops at <em>method</em> — what to check, which field to read, which claim is unverifiable — rather than asserting a personal test nobody performed. When the operator supplies a name, <code>authorship.person_byline</code> and <code>review_required</code> in <code>site.config.json</code> change, and each guide gains a <em>reviewed by</em> line.</p>
<h2>How we work</h2>
<ol class="plain-ol">
  <li>A claim enters a data file, not a page, with a source id attached.</li>
  <li>The generator writes the HTML; nobody hand-edits a published number.</li>
  <li>The gate refuses the build if a cell lacks a source, a disclosure is missing, a store link is untagged or unlabelled, or a price or rating pattern appears anywhere.</li>
  <li>Anything that cannot be confirmed stays visibly blank with a reason, and gets a row on the <a href="./flagged/">flagged</a> page.</li>
  <li>Product rows carry a re-check date; older than thirty days fails the build until someone re-reads or removes them.</li>
</ol>
<h2>Corrections</h2>
<p>Log: <a href="./data/corrections.json"><code>data/corrections.json</code></a> — schema published, no entries yet. A correction gets a row within one working day of confirmation, on the page it belongs to, with what was wrong and what is true.</p>
<h2>Contact</h2>
<p>The route that exists today is the repository: <a href="${esc(CFG.site.repo)}" rel="noopener"><code>${esc(CFG.site.repo.replace("https://", ""))}</code></a> — open an issue for a correction, an accepted decision from the ideas board, or the answers to the blocking questions. We deliberately do not print an email address we have not been given.</p>
<h2>Brand naming, in case it looks close to something</h2>
<p>The name contains no Amazon mark and does not imply sponsorship or endorsement by Amazon — which is both a requirement of the agreement and the reason the strip at the top of this page exists.</p>`,
});

// ---------- 404 (Pages serves /WinC/404.html; kept out of the sitemap) ----------
writeFileSync(join(ROOT, "404.html"), shell({
  relroot: "./", canonical: `${BASE}/404.html`, cls: "nf", navKey: "",
  title: `Page not found — ${CFG.brand.name}`,
  desc: "The URL you asked for is not part of this site.",
  body: `<section class="nf-body"><h1>Nothing at this address</h1>
<p>The site lives under <code>${esc(CFG.site.path_prefix)}</code> on GitHub Pages, so a hand-typed link is the usual reason for this.</p>
<p><a class="btn btn-a" href="./">Front page</a> <a class="btn btn-b" href="./guides/">Guides</a> <a class="btn btn-b" href="./picks/">The desk</a></p></section>`,
}));

// ---------- findability: sitemap, feed, robots ----------
const pub = built.filter((b) => !b.noindex);
writeFileSync(join(ROOT, "sitemap.xml"),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`
  + pub.map((b) => `  <url><loc>${esc(b.canonical)}</loc><lastmod>${b.modified}</lastmod></url>`).join("\n")
  + "\n</urlset>\n");

const feedItems = pub.filter((b) => b.type === "webpage" && b.dir.startsWith("guides/")).reverse();
writeFileSync(join(ROOT, "feed.xml"), `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${esc(CFG.brand.name)} — buyer guides</title>
  <link>${esc(BASE)}/</link>
  <description>${esc(CFG.brand.kicker)}. Headlines and dates only: this feed carries no store links, so the buying decision stays on a page where the disclosure is.</description>
  <language>${esc(CFG.site.default_locale)}</language>
  <lastBuildDate>${new Date(TODAY + "T07:00:00Z").toUTCString()}</lastBuildDate>
  <atom:link href="${esc(BASE)}/feed.xml" rel="self" type="application/rss+xml"/>
${feedItems.map((b) => `  <item>
    <title>${esc(b.title)}</title>
    <link>${esc(b.canonical)}</link>
    <guid isPermaLink="true">${esc(b.canonical)}</guid>
    <pubDate>${new Date(b.date + "T07:00:00Z").toUTCString()}</pubDate>
    <description>${esc(b.desc)}</description>
  </item>`).join("\n")}
</channel>
</rss>
`);

writeFileSync(join(ROOT, "robots.txt"), `# Generated. Static site on GitHub Pages under a sub-path.
User-agent: *
Allow: /
Sitemap: ${BASE}/sitemap.xml
`);

// ---------- generated client config (keeps JS state equal to site.config.json) ----------
mkdirSync(join(ROOT, "assets", "js"), { recursive: true });
writeFileSync(join(ROOT, "assets", "js", "config.js"),
`/* generated by tools/build.mjs — do not edit; edit site.config.json and rebuild */\nwindow.CRISP_MEASURE = ${JSON.stringify({
  endpoint: (CFG.measurement && CFG.measurement.endpoint) || null,
  events: D.events.events.map((e) => e.name),
  retention: D.events.storage.default,
  built_on: TODAY,
}, null, 2)};\n`);

// ---------- clean generated dirs that no longer map to data ----------
const genDir = join(ROOT, "guides");
for (const d of existsSync(genDir) ? readdirSync(genDir, { withFileTypes: true }) : []) {
  if (d.isDirectory() && !guides.some((g) => g.slug === d.name)) {
    warnings.push(`stale guide dir pruned: guides/${d.name}`);
    rmSync(join(genDir, d.name), { recursive: true, force: true });
  }
}

console.log(`built ${built.length} pages · ${pub.length} in sitemap · ${feedItems.length} feed items`);
console.log(`warnings: ${warnings.length}`);
for (const w of warnings) console.log("  ! " + w);
writeFileSync(join(ROOT, ".build-manifest.json"), JSON.stringify({ built_on: TODAY, pages: built, warnings }, null, 2));
