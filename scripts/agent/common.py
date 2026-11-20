#!/usr/bin/env python3
"""Shared helpers for the ShopNow Kitchen agent pipeline.

One rule, applied everywhere: a value is either carried with the source it came from, or it
is blank and flagged. Nothing here fills a gap with a plausible number.
"""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://sassnarep3-star.github.io/WinC/"

# Claims this repository may not make, wherever they appear. Same families the site gate
# blocks, kept here so a draft can never be written with them in the first place.
BANNED_CLAIMS = [
    r"\bwe tested\b", r"\bour\s+(test\s+)?lab\b", r"\bwe tried\b", r"\bbest overall\b",
    r"\beditor'?s choice\b", r"\bgame[- ]?changer\b", r"\bdelve\b", r"\belevate your\b",
    r"\bin today.s (fast|world)\b", r"\bin conclusion\b", r"\btrust us\b", r"\bonly \d+ left\b",
    r"\b(hottest|must-have|must have|blow[sd]? your mind)\b",
]
# A price, a rating or a review count, in any of the shapes they appear in.
NUMBER_CLAIMS = [
    re.compile(r"\$\s?\d"),
    re.compile(r"€\s?\d"),
    re.compile(r"£\s?\d"),
    re.compile(r"\b\d(?:\.\d+)?\s*(?:/|out of)\s*5\b"),
    re.compile(r"\b\d[\d,]*\s*(?:customer\s+)?reviews?\b", re.I),
    re.compile(r"\b\d[\d,]*\s*ratings?\b", re.I),
]


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def save(rel, obj):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def today():
    env = os.environ.get("WINC_BUILD_DATE")
    if env:
        return env
    return datetime.date.today().isoformat()


def claim_problems(text):
    """Return the claims in `text` that this repository may not publish."""
    out = []
    t = text or ""
    for pat in BANNED_CLAIMS:
        for m in re.finditer(pat, t, re.I):
            out.append("banned claim %r" % m.group(0))
    for rx in NUMBER_CLAIMS:
        for m in rx.finditer(t):
            out.append("unsourced number %r" % m.group(0))
    return out


def blank_mark():
    return "<blank: not confirmed from an official source>"


def fmt(v):
    """Render a register value. Blank stays blank and says so."""
    if v is None:
        return ""
    v = str(v).strip()
    return v if v else ""


def by_id(doc, key="id"):
    return {item[key]: item for item in doc}
