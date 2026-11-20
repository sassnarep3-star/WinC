#!/usr/bin/env python3
"""Contract tests for the self-hosted collector's privacy boundary."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("shopnow_collect", ROOT / "analytics" / "collect.py")
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)


class EventContractTests(unittest.TestCase):
    def test_only_five_named_events_are_accepted(self):
        for event in collect.EVENTS:
            with self.subTest(event=event):
                row = collect.normalize_event({"event": event, "page": "guides/example.html"})
                self.assertEqual(row["event"], event)
        with self.assertRaises(ValueError):
            collect.normalize_event({"event": "purchase", "page": "index.html"})

    def test_only_outbound_asin_and_guide_depth_survive(self):
        click = collect.normalize_event({
            "event": "outbound_click", "page": "products/item.html",
            "props": {"asin": "b0cdY277d3", "email": "reader@example.test", "query": "secret"},
            "site": "attacker", "ts": "1999-01-01T00:00:00Z"
        })
        self.assertEqual(click["props"], {"asin": "B0CDY277D3"})
        self.assertNotIn("site", click)  # site identity is not stored per row
        self.assertNotIn("ts_client", click)
        self.assertNotIn("ts_server", click)
        self.assertRegex(click["day"], r"^\d{4}-\d{2}-\d{2}$")

        read = collect.normalize_event({
            "event": "guide_read", "page": "guides/example.html",
            "props": {"depth": "50-89", "email": "reader@example.test", "query": "secret"}
        })
        self.assertEqual(read["props"], {"depth": "50-89"})

    def test_unapproved_or_malformed_properties_are_dropped(self):
        for event in ("page_view", "reader_capture_submit", "search_submit"):
            row = collect.normalize_event({
                "event": event, "page": "index.html",
                "props": {"email": "reader@example.test", "query": "private", "asin": "B0CDY277D3"}
            })
            self.assertEqual(row["props"], {})
        row = collect.normalize_event({
            "event": "outbound_click", "page": "index.html", "props": {"asin": "not-an-asin"}
        })
        self.assertEqual(row["props"], {})

    def test_bad_pages_are_rejected_not_logged(self):
        for page in ("", "../private", "index.html?email=x", "x" * 201, "bad\\nroute"):
            with self.subTest(page=page), self.assertRaises(ValueError):
                collect.normalize_event({"event": "page_view", "page": page})
        with self.assertRaises(ValueError):
            collect.normalize_event(["not", "an", "object"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
