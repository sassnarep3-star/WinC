#!/usr/bin/env python3
"""
Kitchen Shortlist — self-hosted analytics endpoint (Python stdlib variant).

Privacy design (mirrors analytics/endpoint.js):
  - Accepts only the five allowlisted events.
  - Never writes IP addresses, cookies, or full referrers to disk.
  - Persists one JSON line per event WITHOUT identifiers beyond a rotating
    session id that the client already treats as anonymous; daily aggregate
    counters are derived from the log.
  - CORS restricted to the site origin.

Run (any host with Python 3.10+):
    python3 server.py --port 8787 --root /var/lib/ks-analytics

Then set on the site:
    window.SITE_ANALYTICS_ENDPOINT = "https://your-host/e"
"""
from __future__ import annotations

import argparse
import json
import threading
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ALLOWED = {
    "page_view",
    "outbound_product_click",
    "guide_cta_click",
    "search_query",
    "subscribe_click",
}
ORIGINS = {"https://sassnarep3-star.github.io", "http://localhost:8000"}
MAX_STR = 200
LOCK = threading.Lock()
ROOT = Path(".")


def clamp(value, n=MAX_STR) -> str:
    return value if isinstance(value, str) else ""


class Handler(BaseHTTPRequestHandler):
    server_version = "KitchenShortlist/1.0"

    def _cors(self) -> bool:
        origin = self.headers.get("Origin", "")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            return True
        return False

    def _code(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/e":
            self._code(404, {"error": "not found"})
            return
        length = min(int(self.headers.get("Content-Length") or 0), 8192)
        try:
            ev = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._code(400, {"error": "bad json"})
            return
        if not isinstance(ev, dict) or ev.get("event") not in ALLOWED:
            self._code(422, {"error": "unknown event"})
            return

        detail = ev.get("detail") or {}
        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": ev["event"],
            "path": clamp(str(ev.get("path", "")), 120),
            "session": clamp(str(ev.get("session", "")), 40),
            "detail": {
                k: clamp(str(v), 160)
                for k, v in list(detail.items())[:6]
            },
        }
        # NOTE: no IP, no user agent, no raw referrer written.
        with LOCK:
            with (ROOT / "events.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._code(202, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/stats":
            self._code(404, {"error": "not found"})
            return
        day = (parse_qs(parsed.query).get("day") or [None])[0]
        counts: Counter[str] = Counter()
        log = ROOT / "events.jsonl"
        if log.exists():
            with log.open(encoding="utf-8") as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if day and not rec["ts"].startswith(day):
                        continue
                    counts[rec["event"]] += 1
                    if rec["event"] == "outbound_product_click":
                        href = rec.get("detail", {}).get("href", "")
                        if href:
                            counts[f"out:{href}"] += 1
                    if rec["event"] == "search_query":
                        q = rec.get("detail", {}).get("q", "").lower()
                        if q:
                            counts[f"q:{q}"] += 1
        self._code(200, {"day": day or "all", "counts": dict(counts)})

    def log_message(self, fmt: str, *args) -> None:  # quiet default logging
        pass


def main() -> None:
    global ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--root", default=".", help="directory for events.jsonl")
    args = ap.parse_args()
    ROOT = Path(args.root)
    ROOT.mkdir(parents=True, exist_ok=True)
    print(f"Kitchen Shortlist analytics endpoint on {args.host}:{args.port} (root={ROOT})")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
