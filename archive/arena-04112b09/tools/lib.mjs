// tools/lib.mjs — shared helpers for the generator and the gate.
// No dependencies: this has to run in CI and on a bare checkout without an install step.
import { readFileSync, existsSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export function dataPath(...p) { return join(ROOT, ...p); }
export function readJson(rel) {
  const abs = dataPath(rel);
  if (!existsSync(abs)) throw new Error(`missing data file: ${rel}`);
  try { return JSON.parse(readFileSync(abs, "utf8")); }
  catch (e) { throw new Error(`invalid JSON in ${rel}: ${e.message}`); }
}

export function loadAll() {
  return {
    config: readJson("site.config.json"),
    sources: readJson("data/sources.json"),
    intent: readJson("data/product-intent.json"),
    products: readJson("data/products.json"),
    rules: readJson("data/rules.json"),
    questions: readJson("data/questions.json"),
    suggestions: readJson("data/suggestions.json"),
    flags: readJson("data/flags.json"),
    events: readJson("data/events.json"),
    editorial: readJson("data/editorial.json"),
  };
}

// ---------- html ----------
export function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// Minimal inline formatter: **strong**, _em_, `code`, and bare URLs left as text.
export function inline(s) {
  let out = esc(s);
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/(^|[\s(])_([^_]+)_(?=[\s).,!?:;]|$)/g, "$1<em>$2</em>");
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  return out;
}

export function dateLong(iso) {
  if (!iso) return "";
  const [y, m, d] = String(iso).split("-").map(Number);
  const months = ["January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December"];
  return `${d} ${months[m - 1]} ${y}`;
}

// ---------- source register helpers ----------
export function sourceMap(sources) {
  const m = new Map();
  for (const s of sources.sources) m.set(s.id, s);
  return m;
}

export function sourceLink(s, { label } = {}) {
  if (!s) return "";
  const text = label || `${s.id} · ${s.title}`;
  if (!s.url) return `<span class="src src-internal" title="not a public URL: ${esc(s.kind)}">${esc(text)}</span>`;
  const flag = s.method === "referenced" ? " src-unfetched" : "";
  const title = `Method: ${s.method || "unknown"}${s.fetched_on ? ` · read ${s.fetched_on}` : " · not read by this session"}`;
  return `<a class="src${flag}" href="${esc(s.url)}" rel="noopener" target="_blank" title="${esc(title)}">${esc(text)}<span class="src-ext" aria-hidden="true">↗</span></a>`;
}

// ---------- link helpers ----------
export function isStoreUrl(href) {
  return /(^|\.)amazon\.[a-z.]{2,}$/i.test(new URL(href).hostname) || /(^|\.)amzn\.to$/i.test(new URL(href).hostname);
}

// ---------- state vocabulary (kept in one place so tables stay comparable) ----------
export const STATE = {
  unresolved: { label: "unresolved", cls: "s-unresolved", meaning: "we could not confirm this and will not guess" },
  verified: { label: "confirmed", cls: "s-verified", meaning: "checked against the cited official page on the recorded date" },
  blocked: { label: "blocked", cls: "s-blocked", meaning: "cannot proceed until an input exists" },
  pending: { label: "pending review", cls: "s-pending", meaning: "needs a human decision; nothing is built yet" },
  notPermitted: { label: "not shown — rule", cls: "s-blocked", meaning: "displaying it would breach the cited clause" },
};

export function badge(kind) {
  const s = STATE[kind] || STATE.unresolved;
  return `<span class="badge ${s.cls}">${s.label}</span>`;
}
