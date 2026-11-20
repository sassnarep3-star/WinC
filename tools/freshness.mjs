// tools/freshness.mjs — the staleness queue over the live registers.
// Reads data/products.json (+ data/probes.json) and prints what a human must re-check.
// It never opens the store: generating sessions or clicks programmatically is prohibited, and a
// repository job should not be scraping listings to learn whether a page moved.
//   node tools/freshness.mjs [--days N] [--quiet]
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
const DAYS = Number(process.argv[++process.argv.indexOf("--days")] || 30);
const QUIET = process.argv.includes("--quiet");
const read = (p) => (existsSync(join(ROOT, p)) ? JSON.parse(readFileSync(join(ROOT, p), "utf8")) : null);
const products = read("data/products.json")?.products || [];
const probes = read("data/probes.json")?.probes || [];
const TODAY = new Date();

// dates in these registers are human notes ("2026-11-17 + snippet 2026-11-20"), so take the latest
// ISO date inside the string rather than assuming a parseable field
const lastDate = (s) => (String(s || "").match(/\d{4}-\d{2}-\d{2}/g) || []).sort().pop() || null;
const ageOf = (d) => (d ? Math.floor((TODAY - new Date(d + "T00:00:00Z")) / 864e5) : null);
const probeFor = (p) => probes.find((x) => x.submitted_token === p.submitted_token || x.final_asin === p.observed_asin) || null;

const rows = products.map((p) => {
  const observed = ageOf(lastDate(p.observed_date));
  const confirmed = lastDate(p.confirmation_date);
  const pr = probeFor(p);
  const state = !confirmed
    ? observed === null ? "no observation" : observed > DAYS ? "stale observation" : "observed, intent unconfirmed"
    : ageOf(confirmed) > DAYS ? "stale confirmation" : "fresh";
  return {
    id: p.id, title: p.title ? `${String(p.title).slice(0, 34)}…` : "—",
    observed, state, agrees: pr ? (pr.agrees_with_prior_session ? "yes" : "no") : "n/a",
    action: !confirmed
      ? "confirm the intended listing with the account owner, then fill intended_asin + confirmation_date (leave observed_* separate)"
      : observed !== null && observed > DAYS
        ? "re-read the listing or remove the row — content that is gone from Amazon must come off the site"
        : "none",
  };
});
const overdue = rows.filter((r) => r.state.startsWith("stale"));
if (!QUIET) {
  console.log(`\nfreshness — ${rows.length} product rows · window ${DAYS}d · ${overdue.length} overdue · ${rows.filter((r) => r.agrees === "no").length} probe disagreement(s)\n`);
  for (const r of rows)
    console.log(`  ${r.id.padEnd(34)} ${String(r.observed === null ? "—" : r.observed + "d").padStart(6)}  ${r.state.padEnd(26)} agree:${r.agrees.padEnd(4)} ${r.action}`);
  console.log(`\n  published rows: every store page in the register is re-read on this cadence; the site's own gate`);
  console.log(`  (scripts/check_site.py) remains the blocker — this queue only tells you who has to act.\n`);
}
process.exit(overdue.length ? 1 : 0);
