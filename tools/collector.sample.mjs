// tools/collector.sample.mjs — NOT DEPLOYED. A reference collector for infrastructure the operator runs.
//
// Why it is not wired up: GitHub Pages serves files only, so there is nothing here to receive a POST
// (FLG-008), and an EU-facing site should not start collecting before the retention window and legal
// basis are decided (Q-11). The client counter therefore stays local until someone sets
// site.config.json → measurement.endpoint and rebuilds.
//
// Constraints this file is written against, from the Associates Program Policies:
//   · reporting may not be associated with a specific end user, and sub-tags may not be assigned per
//     visitor → no cookie, no fingerprint, no user id, no IP stored.
//   · clicks and impressions may not be generated artificially → this server only stores what a real
//     browser reports; it never replays, synthesises or re-fires an event, and it is not a crawler.
import { createServer } from "node:http";
import { appendFile } from "node:fs/promises";

const PORT = Number(process.env.PORT || 8090);
const FILE = process.env.EVENT_FILE || "./events.jsonl";
const ALLOW = new Set(["page_view", "guide_open", "outbound_click", "product_intent_check", "editorial_decision"]);
const MAX_BODY = 2048;

createServer(async (req, res) => {
  const cors = {
    "access-control-allow-origin": "*",           // set to your own site origin in production
    "access-control-allow-headers": "content-type",
    "access-control-allow-methods": "POST, OPTIONS",
  };
  if (req.method === "OPTIONS") { res.writeHead(204, cors); return res.end(); }
  if (req.method !== "POST") { res.writeHead(405, cors); return res.end("method not allowed"); }

  const chunks = []; let size = 0;
  for await (const c of req) { size += c.length; if (size > MAX_BODY) { res.writeHead(413, cors); return res.end("too large"); } chunks.push(c); }

  let ev;
  try { ev = JSON.parse(Buffer.concat(chunks).toString("utf8")); }
  catch { res.writeHead(400, cors); return res.end("bad json"); }

  if (!ALLOW.has(ev.e)) { res.writeHead(422, cors); return res.end("unknown event"); }
  // Refuse anything that smells like an identifier before it can be written to disk.
  const text = JSON.stringify(ev).toLowerCase();
  if (/cookie|clientid|user_?id|fingerprint|email|ip|token|subtag|sub_tag/.test(text)) {
    res.writeHead(451, cors); return res.end("payload rejected");
  }

  const line = JSON.stringify({ day: new Date().toISOString().slice(0, 10), ...ev }) + "\n";
  await appendFile(FILE, line, "utf8");

  // Deliberately absent: any access log. The host's own web-server log will still record IPs —
  // configure it not to, or accept that "we collect nothing" is then false.
  res.writeHead(204, { ...cors, "cache-control": "no-store" });
  res.end();
}).listen(PORT, "0.0.0.0", () => console.log(`collector listening on :${PORT} → ${FILE} (sample only; not referenced by the site)`));
