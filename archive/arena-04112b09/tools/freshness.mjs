// tools/freshness.mjs — the staleness queue described in SG-07 (option A).
// It reads OUR data and prints the rows a human has to re-check. It deliberately does not open a
// browser or poll a store: generating clicks or sessions programmatically is prohibited, and a
// repository job should not be scraping listings to find out whether a page moved.
import { loadAll, ROOT } from "./lib.mjs";

const D = loadAll();
const TODAY = new Date();
const WINDOW_DAYS = 30;
const rows = [];

for (const r of D.intent.records) {
  const reviewed = r.confirmed_on || null;
  const age = reviewed ? Math.floor((TODAY - new Date(reviewed + "T00:00:00Z")) / 86400000) : null;
  rows.push({
    id: r.id,
    state: r.intended_asin_confirmed ? (age > WINDOW_DAYS ? "stale" : "fresh") : "unresolved",
    age,
    action: !r.intended_asin_confirmed
      ? `confirm the listing, then set intended_asin/official_listing_url/confirmed_on (leave observed_redirect_target separate)`
      : age > WINDOW_DAYS
        ? `re-read the listing or remove the row — Program Content that is gone from Amazon must come off the site`
        : "none",
    flags: (r.related_flags || []).join(" ") || "—",
  });
}

const overdue = rows.filter((x) => x.state === "stale");
const unresolved = rows.filter((x) => x.state === "unresolved");
console.log(`\nfreshness — ${D.intent.records.length} register rows · ${unresolved.length} unresolved · ${overdue.length} past the ${WINDOW_DAYS}-day window\n`);
for (const x of rows) console.log(`  ${x.id.padEnd(6)} ${x.state.padEnd(11)} ${x.age === null ? "—" : String(x.age) + "d"}  ${x.action}  [${x.flags}]`);
console.log(`\nnext publish gate re-runs this as part of: npm run verify`);
console.log(`sources checked: ${D.sources.sources.length} registered, ${D.sources.sources.filter((s) => s.method === "fetched").length} fetched this session\n`);
if (overdue.length) { console.error(`${overdue.length} row(s) past window — fix before publishing`); process.exit(1); }
