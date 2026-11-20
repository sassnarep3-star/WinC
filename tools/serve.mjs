// tools/serve.mjs — local preview that matches how Pages serves this repo:
// the whole site lives under a /WinC/ path prefix, and directory URLs need a trailing slash.
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { join, normalize, extname } from "node:path";
import { ROOT } from "./lib.mjs";

const PORT = Number(process.env.PORT || 8080);
const PREFIX = "/WinC";
const TYPES = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".xml": "application/xml; charset=utf-8", ".csv": "text/csv; charset=utf-8",
  ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".txt": "text/plain; charset=utf-8",
  ".ico": "image/x-icon", ".webp": "image/webp",
};

async function resolve(pathname) {
  let p = decodeURIComponent(pathname);
  if (p === "/" || p === "") p = PREFIX + "/";
  if (!p.startsWith(PREFIX + "/") && p !== PREFIX) return { redirect: PREFIX + "/" };
  let rel = "/" + p.slice(PREFIX.length).replace(/^\/+/, "");
  let abs = normalize(join(ROOT, rel));
  if (!abs.startsWith(ROOT)) return { status: 403, body: "outside root" };
  try {
    const st = await stat(abs);
    if (st.isDirectory()) {
      if (!p.endsWith("/")) return { redirect: p + "/" };
      abs = join(abs, "index.html");
    }
  } catch { /* fall through to 404 handling */ }
  return { abs };
}

createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  const r = await resolve(url.pathname);
  if (r.redirect) { res.writeHead(301, { location: r.redirect, "cache-control": "no-store" }); return res.end(); }
  if (r.status) { res.writeHead(r.status, { "cache-control": "no-store" }); return res.end(r.body); }
  try {
    const buf = await readFile(r.abs);
    res.writeHead(200, { "content-type": TYPES[extname(r.abs)] || "application/octet-stream", "cache-control": "no-store" });
    res.end(buf);
  } catch {
    let body = "not found";
    try { body = await readFile(join(ROOT, "404.html")); } catch { /* no 404 built yet */ }
    res.writeHead(404, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
    res.end(body);
  }
}).listen(PORT, "0.0.0.0", () => {
  console.log(`preview → http://0.0.0.0:${PORT}${PREFIX}/  (root redirects to ${PREFIX}/)`);
});
