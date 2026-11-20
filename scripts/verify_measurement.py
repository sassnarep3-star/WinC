#!/usr/bin/env python3
"""End-to-end proof that the measurement layer actually works.

Runs analytics/collect.py as a real HTTP server, posts the five defined events with
exactly the payload shape assets/app.js sends, and checks what comes back:

  1. every one of the five events is accepted (HTTP 202)
  2. an event outside the defined set is rejected (HTTP 422), as is a malformed page
  3. /stats and /ledger report the counts that were posted
  4. the stored rows use the hardened privacy schema: server day + event + page +
     allow-listed props only (client timestamps and site IDs are discarded by design)
  5. nothing identity-bearing is stored: no IP, no user agent, no cookie, no email,
     no search query, no client timestamp

Run: python3 scripts/verify_measurement.py
Exit 1 on failure. No third-party dependencies.
"""
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECT = os.path.join(ROOT, "analytics", "collect.py")
EVENTS = ("page_view", "outbound_click", "guide_read", "reader_capture_submit", "search_submit")
failures = []


def check(cond, msg):
    if cond:
        print(f"  ok   {msg}")
    else:
        failures.append(msg)
        print(f"  FAIL {msg}")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def post(url, payload, ctype="application/json"):
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    tmpdir = tempfile.mkdtemp(prefix="shopnow-measure-")
    outfile = os.path.join(tmpdir, "events.jsonl")

    proc = subprocess.Popen(
        [sys.executable, COLLECT, "--port", str(port), "--host", "127.0.0.1",
         "--out", outfile, "--quiet"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # wait for the port to answer
        deadline = time.time() + 15
        up = False
        while time.time() < deadline:
            try:
                get(base + "/healthz")
                up = True
                break
            except Exception:
                time.sleep(0.15)
        check(up, "collector starts and answers /healthz")
        if not up:
            return

        # --- the five events, exactly as assets/app.js sends them -------------------
        samples = [
            ("page_view", {"referrerCategory": "direct"}, "index.html", {}),
            ("outbound_click", {"asin": "B0CDY277D3", "target": "amazon"},
             "products/chefman-6qt-dual-basket-b0cdy277d3.html", {"asin": "B0CDY277D3"}),
            ("guide_read", {"depth": "50-89", "injected": "x"},
             "guides/basket-or-oven-style-air-fryer.html", {"depth": "50-89"}),
            ("reader_capture_submit", {"form": "newsletter", "email": "evil@example.com"},
             "index.html", {}),
            ("search_submit", {"form": "internal", "query": "cheapest air fryer"},
             "search.html", {}),
        ]
        for name, props, page, expect_props in samples:
            payload = {"site": "shopnow-kitchen", "event": name, "page": page,
                       "at": "2026-11-20T00:00:00.000Z", "props": props}
            code, body = post(base + "/collect", payload)
            check(code == 202, f"{name}: accepted with HTTP 202 (got {code}) {body[:60]}")

        # --- anything outside the contract must be refused --------------------------
        code, _ = post(base + "/collect", {"site": "shopnow-kitchen", "event": "secret_event",
                                           "page": "index.html", "at": "x"})
        check(code == 422, f"undefined event rejected with HTTP 422 (got {code})")
        code, _ = post(base + "/collect", {"site": "s", "event": "page_view",
                                           "page": "../etc/passwd", "at": "x"})
        check(code == 422, f"path traversal in page rejected with HTTP 422 (got {code})")

        # --- what the endpoint reports --------------------------------------------
        stats = get(base + "/stats")
        check(stats.get("events_total") == 5,
              f"/stats counts all 5 posted events (got {stats.get('events_total')})")
        by = stats.get("by_event", {})
        check(set(by) == set(EVENTS), f"/stats reports exactly the five defined events ({sorted(by)})")

        ledger = get(base + "/ledger")
        check(len(ledger.get("rows", [])) == 5,
              f"/ledger returns one aggregate row per page+event ({len(ledger.get('rows', []))})")
        note = ledger.get("note", "").lower()
        check("not here" in note and "first-party" in note,
              "/ledger states that orders are not in it and must come from a first-party export")

        # --- what is actually on disk ------------------------------------------------
        rows = []
        with open(outfile, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        check(len(rows) == 5, f"exactly 5 rows written to the event log (got {len(rows)})")
        check(all(r.get("day") and re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["day"]) for r in rows),
              "every stored row is dated by server day only (no time-of-day)")
        check(all(set(r) == {"day", "event", "page", "props"} for r in rows),
              "each row has exactly the four agreed fields (day, event, page, props)")

        # per-event allow-lists: the injected junk must be gone
        by_event = {r["event"]: r for r in rows}
        check(by_event["outbound_click"]["props"].get("asin") == "B0CDY277D3",
              "outbound_click keeps the allow-listed observed ASIN")
        check(by_event["outbound_click"]["props"].get("target") is None,
              "outbound_click drops non-allow-listed props")
        check(by_event["guide_read"]["props"].get("depth") == "50-89"
              and by_event["guide_read"]["props"].get("injected") is None,
              "guide_read keeps the depth bucket and drops everything else")
        check(by_event["reader_capture_submit"]["props"] == {},
              "reader_capture_submit stores no props — the submitted email never lands")
        check(by_event["search_submit"]["props"] == {},
              "search_submit stores no props — the query text never lands")
        check(by_event["page_view"]["props"] == {},
              "page_view stores no props — the referrer category never lands")

        blob = json.dumps(rows)
        check("127.0.0.1" not in blob, "no client IP address is stored")
        check("urllib" not in blob.lower() and "user-agent" not in blob.lower(),
              "no user agent is stored")
        check(not re.search(r"cookie", blob, re.I), "no cookie is stored")
        check("@" not in blob, "no email address is stored")
        check("cheapest" not in blob and "query" not in blob.lower(), "no search query text is stored")
        check("2026-11-20T00:00:00" not in blob and "shopnow-kitchen" not in blob,
              "no client timestamp and no client site ID are stored")
        check("amazon.com" not in blob, "outbound_click does not store the full URL")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    print()
    if failures:
        print(f"FAIL ({len(failures)} problems):")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("OK: measurement layer verified end to end — 5 events accepted, 2 payloads rejected, "
          "nothing identity-bearing stored.")


if __name__ == "__main__":
    main()
