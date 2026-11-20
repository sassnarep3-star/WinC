#!/usr/bin/env python3
"""Minimal self-hosted click/conversion collector for ShopNow Kitchen (stdlib only).

Why this exists: GitHub Pages is static, so the beacon in assets/app.js has nowhere to post.
`analytics/worker.js` is the edge deployment; this file is the "run it on a box you already
have" option, so that measuring is never blocked on choosing a hosting product.

    python3 analytics/collect.py --port 8080 --out /var/log/shopnow-events.jsonl
    # then in assets/app.js:  CONFIG.endpoint = "http://HOST:8080/collect"

Contract (matches assets/app.js):  POST /collect  {"site","event","page","props","ts"}
Only the five defined events are accepted. Event-specific allow-lists drop arbitrary client
properties, including email addresses and search queries. No cookies, no IP logging, no user-agent
storage, no cross-page session stitching. Each row carries only the server-generated day; client
timestamps and client-provided site IDs are discarded.

Read:  GET /stats -> aggregate counts (from the local file only)
       GET /ledger -> campaign-ledger rows aggregated by page+event

This records clicks, not orders. Orders and reported revenue must come from Amazon's own
first-party reports (Associates Central) and be appended to data/campaign-ledger.json by hand,
with the export date. Nothing here invents or estimates them.
"""
import argparse, json, os, re, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

EVENTS = ("page_view", "outbound_click", "guide_read", "reader_capture_submit", "search_submit")
MAX_BODY = 8 * 1024
ALLOWED_ORIGIN = None
PAGE_RE = re.compile(r"^[A-Za-z0-9._/-]{1,200}$")
ASIN_RE = re.compile(r"^[A-Za-z0-9]{10}$")
DEPTH_BUCKETS = {"full", "90+", "50-89", "25-49", "0-24"}


def normalize_event(payload):
    """Return only the fixed, non-PII event schema; reject malformed route/event data.

    Client properties are never copied wholesale: each event has an explicit allow-list.
    This boundary is important even though the bundled browser client currently sends only
    aggregate fields; a modified client must not be able to submit email addresses or queries.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    event = payload.get("event")
    if event not in EVENTS:
        raise ValueError("event not in the defined set")
    page = str(payload.get("page") or "")
    if len(page) > 200 or not PAGE_RE.fullmatch(page) or ".." in page:
        raise ValueError("invalid page")
    # One row per accepted event, dated by server day only (no time-of-day, no client identifiers).
    row = {"day": time.strftime("%Y-%m-%d", time.gmtime()),
           "event": event, "page": page, "props": {}}
    props = payload.get("props") if isinstance(payload.get("props"), dict) else {}
    if event == "outbound_click":
        asin = str(props.get("asin") or "")
        if ASIN_RE.fullmatch(asin):
            row["props"]["asin"] = asin.upper()
    elif event == "guide_read":
        depth = props.get("depth")
        if depth in DEPTH_BUCKETS:
            row["props"]["depth"] = depth
    return row


class Handler(BaseHTTPRequestHandler):
    out_path = None
    quiet = False

    def _send(self, code, payload, ctype="application/json"):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        # No tracking of any kind is set here; no Cookie, no ETag fingerprint.
        self.send_header("Cache-Control", "no-store")
        if ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/stats":
            self._send(200, self.aggregate())
        elif path == "/ledger":
            agg = {}
            for row in self.rows():
                key = (row.get("page", "?"), row.get("event", "?"))
                agg[key] = agg.get(key, 0) + 1
            rows = [{"page": p, "event": e, "count": n,
                     "obtained_from": "local event log (clicks/views only; not orders)"}
                    for (p, e), n in sorted(agg.items(), key=lambda kv: -kv[1])]
            self._send(200, {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                             "note": "Orders/revenue are NOT here. Append them from an authorised first-party export.",
                             "rows": rows})
        elif path == "/healthz":
            self._send(200, {"ok": True, "events": list(EVENTS)})
        else:
            self._send(404, {"error": "unknown path"})

    @staticmethod
    def rows():
        if not os.path.exists(Handler.out_path):
            return []
        with open(Handler.out_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except ValueError:
                        continue

    def aggregate(self):
        agg, pages = {}, {}
        n = 0
        for row in self.rows():
            n += 1
            agg[row.get("event", "?")] = agg.get(row.get("event", "?"), 0) + 1
            p = row.get("page", "?")
            pages[p] = pages.get(p, 0) + 1
        return {"events_total": n, "by_event": agg,
                "top_pages": sorted(pages.items(), key=lambda kv: -kv[1])[:20]}

    def do_POST(self):
        if urlparse(self.path).path != "/collect":
            return self._send(404, {"error": "unknown path"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            return self._send(413, {"error": "body too large or empty"})
        raw = self.rfile.read(length)
        if self.headers.get("Content-Type", "").startswith("text/plain"):
            # navigator.sendBeacon with a Blob may arrive as text/plain
            raw = raw.split(b"?", 1)[0]
        try:
            d = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self._send(400, {"error": "not json"})
        try:
            row = normalize_event(d)
        except ValueError as e:
            return self._send(422, {"error": str(e)})
        event, page = row["event"], row["page"]
        try:
            with open(Handler.out_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
                f.flush(); os.fsync(f.fileno())
        except OSError as e:
            return self._send(500, {"error": "write failed"})
        if not Handler.quiet:
            sys.stderr.write("%s %s %s\n" % (row["day"], event, page))
        self._send(202, {"ok": True})

    def log_message(self, *a):
        pass  # access logging would store IPs; deliberately off


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.jsonl"))
    ap.add_argument("--origin", default="", help="CORS origin to accept (e.g. https://<user>.github.io); empty = no origin restriction on reads")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    a.out_path = os.path.abspath(a.out)   # single source for the resolved path
    Handler.out_path = os.path.abspath(a.out)
    Handler.quiet = a.quiet
    global ALLOWED_ORIGIN
    ALLOWED_ORIGIN = a.origin or None
    d = os.path.dirname(Handler.out_path)
    if d:
        os.makedirs(d, exist_ok=True)
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print("collecting 5 events -> %s   (POST /collect, GET /stats, GET /ledger)" % a.out_path)
    print("no IP logging, no cookies, no user-agent capture. Ctrl-C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
