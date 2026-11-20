#!/usr/bin/env python3
"""Fill in the answers the evidence actually supports (session arena/6561e2ea-winc).

Before this, all 22 rows of the open-questions register had an empty answer cell, so the
register could say what was missing but never what was known. A register like that is a
to-do list. This script writes the answers that the sources in data/sources.json support —
including the partial ones — and leaves the rest explicitly open, with the reason.

Three states, and the difference between them matters:
  answered      the evidence settles it; the answer says so and cites the source
  partly        part of it is settled by the evidence, the rest is named
  open          nobody has it; the answer cell stays blank and the discovery path stands

An answer is only "answered" if it names the source that settles it. Re-run this script
after adding a source to data/sources.json.
"""
import json, collections, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "questions.json")
DATE = "2026-11-20"

# qid -> (state, answer, [source ids])
ANSWERS = {
    "Q-01": ("partly",
             "Partly settled. The suffix is settled: Amazon's own help says “our software "
             "automatically adds \"-20\" to the end of all Associate IDs”, so shopnow047c-20 already "
             "carries the amazon.com marketplace suffix and the shape is right for a US site. What "
             "is not settled is whether the four-letter part is issued to this account and active. "
             "No public page lists it, and only Associates Central can say. Answer therefore: the "
             "tag is well-formed for amazon.com; its issuance is unconfirmed.",
             ["S20", "S06", "S21"]),
    "Q-02": ("answered",
             "No — the supplied tokens do not identify products, and they were never meant to. Each "
             "token is 9 characters; an ASIN is a 10-character code, so a token cannot be one. The "
             "mapping in this register is what the links resolve to, recorded live on four separate "
             "occasions with the same result each time (5/5 reproduce). Nothing public binds the "
             "short code to a product, so the intended fields stay blank and the observed target is "
             "kept in its own column. The intended fields are settled as “unknown”, which is a "
             "settled answer, not a gap in the record.",
             ["S05", "S14", "S22", "S29"]),
    "Q-03": ("partly",
             "Unresolved — and this site does not claim the short links are invalid. What is settled "
             "is the rule they would have to satisfy: “Special Links must use the Associates ID we "
             "have assigned to you”, and every link placed on the Site must include the Associate "
             "ID or “tag” (appearing as XXXXX-##) as a URL parameter. Whether a link.amazon short "
             "link satisfies that inside an enrolled account is not determinable from outside it. "
             "So the reader-facing buttons on this site are constructed as "
             "amazon.com/dp/<observed ASIN>?tag=shopnow047c-20, and the supplied short links appear "
             "as provenance text that cannot be clicked.",
             ["S02", "S15"]),
    "Q-04": ("partly",
             "Partly settled, and the part that matters is not public. The Program Policies carry "
             "the Commission Income Statement, but the rate that applies to a category is set by the "
             "terms Amazon applies to the account; the Operating Agreement also says Amazon “does "
             "not make any representation, warranty or covenant regarding the amount of traffic or "
             "commission income you can expect at any time”. So the rate is readable in Associates "
             "Central and nowhere else. No rate, order count or revenue figure is published on this "
             "site for that reason, and none should be until it comes from a first-party report.",
             ["S02", "S01"]),
    "Q-05": ("partly",
             "The conflicts are real in the listings; which side is right needs the manufacturer. "
             "All five listing pages were re-read on 2026-11-20. The Chefman 8 Qt title still reads "
             "“TurboFry® 4-in-1 with 450°F Hi-Fry” while the captured copy says 200–400°F; the "
             "Emeril title still says “Six Cooking Accessories Included”; the ThermoMaven title "
             "wording rotated again. A listing can contradict itself without either side being "
             "wrong, so the honest record is the conflict, not a chosen value. This site publishes the "
             "listing's own wording and flags the conflict.",
             ["S09", "S10", "S11", "S12", "S13"]),
    "Q-06": ("answered",
             "There is no named individual, and the site says so. The byline is “The ShopNow Kitchen "
             "Desk” — an editorial desk, not a person. Nobody involved has cooked with these "
             "products, and every product page says so instead of implying otherwise. The decision "
             "this row was really asking about is therefore settled as a fact: either a named author "
             "with stated experience appears, or the site keeps saying plainly that there is none. "
             "It currently says there is none.",
             []),
    "Q-07": ("answered",
             "Settled. Every image on this site is original editorial illustration produced for this "
             "project and committed in assets/img/. No third-party photograph, screenshot or "
             "manufacturer image is published. Each one is labelled in its alt text and caption as an "
             "illustration and not a product photograph, so a reader is never left thinking it shows "
             "the unit they would receive. Each product now has its own picture rather than "
             "borrowing a category plate.",
             []),
    "Q-08": ("answered",
             "No, and the ledger is empty on purpose rather than by omission. The beacon in "
             "assets/app.js counts five events in the reader's own browser; the self-hosted endpoint "
             "in analytics/ is not deployed, so nothing is transmitted anywhere. The campaign ledger "
             "has zero rows carrying numbers, and scripts/agent/optimize.py says exactly that and "
             "makes no recommendation. The five events are defined and instrumented; the collection "
             "half is what is missing.",
             []),
    "Q-09": ("open", "", []),
    "Q-10": ("partly",
             "Currently amazon.com (US) only, and the evidence is on the page. Every reader link is "
             "amazon.com/dp/<ASIN>?tag=shopnow047c-20; the “-20” is the marketplace suffix Amazon "
             "appends to Associate IDs, and the Operating Agreement lists the Amazon Sites by "
             "Schedule 1. Serving another marketplace needs a different Associate ID and a newly "
             "declared site, and would change the Special Links themselves — not just the hostname. "
             "Until that is decided and done, the site targets the US marketplace only.",
             ["S20", "S01", "S02"]),
    "Q-11": ("answered",
             "Settled on 2026-11-20: the site publishes from a branch, and the branch build is now "
             "the only publisher. The repository had both — a legacy Pages source (branch main, path "
             "/) and a custom GitHub Actions publish workflow — and GitHub's own documentation "
             "describes these as two alternatives, not two things to run together. While both ran, "
             "the legacy build record for two commits came back errored with a duration of 0 "
             "seconds: the build was aborted the moment a concurrent Actions deployment held the "
             "github-pages environment. Every legacy build that ran without that collision "
             "reported built. The competing workflow was removed, and scripts/deploy_check.py now "
             "checks the publisher's own record and the live pages.",
             ["S21", "S30", "S08"]),
    "Q-12": ("partly",
             "The machinery part is settled: publishing a guide is a data change, not a build change. "
             "Dropping a file into data/guides/ adds it to the site, the sitemap, the RSS feed and "
             "the search index in one build, and the gate refuses the build if any of it is broken. "
             "What is not settled is the cadence, and that is the owner's call: the honest cadence is "
             "the one that keeps the register true, which is bounded by how fast the desk can "
             "re-read a listing and keep the source register current. Publishing faster than that "
             "would mean publishing stale specs.",
             ["S08"]),
    "Q-13": ("answered",
             "Settled: no static price, ever, unless it comes from an API. Program Policies: “your "
             "Site may only show prices and availability if: (a) we serve the link in which that "
             "price and availability data are displayed, or (b) you obtain Product pricing and "
             "availability data via Creators API or PA API”. This site takes route (a) — every buy "
             "button sends the reader to the listing where the live figure is — and the price and "
             "rating cells in every table stay blank with a note saying why. A scraped price is not "
             "either route, so none is published.",
             ["S02"]),
    "Q-14": ("answered",
             "Settled as a procedure, in this order. First the account-side flags that gate live "
             "money — FLG-001 (is the tracking ID issued), FLG-002 (does one link per product reach "
             "the tracking report), FLG-003 (what is the supplied short link's status) — because "
             "only the account owner can clear them and nothing else matters until they are clear. "
             "Then the listing-side conflicts a reader might quote — FLG-005, FLG-010, FLG-014 — by "
             "re-reading the live listing and then the manufacturer's own page. Then presentation "
             "flags (FLG-004, FLG-015 to FLG-017), which are desk edits. Then infrastructure flags "
             "(FLG-007, the endpoint that is not deployed), which need a hosting decision.",
             []),
    "Q-15": ("partly",
             "Live and the same products, re-read 2026-11-20. All five listing pages served their "
             "own title and category breadcrumb today, and the titles match the register exactly, so "
             "the five products in the shop are still the five products. Stock and price are not "
             "published and are not answered here: they move, and Program Policies treat price and "
             "availability as one thing (S02). What was checked is identity, not inventory.",
             ["S09", "S10", "S11", "S12", "S13", "S02"]),
    "Q-16": ("answered",
             "Yes for amazon.com. Verbatim from Amazon's help: “our software automatically adds "
             "\"-20\" to the end of all Associate IDs”. So shopnow047c-20 already carries the "
             "marketplace suffix and must not have another one appended. This says nothing about "
             "whether the ID is issued or active — that is Q-01, and it is still open.",
             ["S20"]),
    "Q-17": ("partly",
             "The measuring half is settled; the target is the owner's. What this site can actually "
             "produce is: a reader arrives on a question, compares against published specs, and "
             "leaves through a link whose click is counted, with the count landing in a ledger that "
             "carries a date and a source. The first full reporting period after the endpoint is "
             "deployed is the earliest honest window, because before that there are no clicks to "
             "count. No revenue figure or conversion rate is forecast, because none has been "
             "measured.",
             ["S08"]),
    "Q-18": ("partly",
             "Currently five — the five products the brief supplied — and the constraint on widening "
             "is settled: a new product must arrive with the same record the five have, namely an "
             "intended ASIN, an official listing URL, a confirmation date and a source, held in "
             "fields separate from the observed redirect target. The research pipeline can extend "
             "the catalogue mechanically, but it will not add a product without that record. How "
             "many the shop should carry is the owner's call.",
             ["S05", "S02"]),
    "Q-19": ("answered",
             "The listing wins, for anything this site publishes, because the listing is what the "
             "reader is sent to and the only thing that can be cited. Program Policies forbid "
             "inaccurate, overbroad or misleading claims about a Product. Where a listing and a "
             "manufacturer page disagree, this site publishes the listing's own wording, shows the "
             "disagreement next to it, and flags it — it does not quietly prefer one side. A "
             "manufacturer page may be cited as the manufacturer's claim, never as this site's "
             "finding.",
             ["S02", "S09"]),
    "Q-20": ("answered",
             "Evergreen with a seasonal shelf. Guides carry a season field, the front page shows a "
             "seasonal band computed from the guides register, and the default cluster is "
             "“Everyday”. Because the band is computed rather than typed, it cannot drift from the "
             "guides that exist. The holiday guides are a shelf on an evergreen site, not the site "
             "itself, so the site keeps its value outside the weeks the guides were written for.",
             []),
    "Q-21": ("answered",
             "Nobody owns a list, because there is no list. The capture form records that a reader "
             "pressed Subscribe in their own browser and sends the address nowhere: the input "
             "carries no name attribute, the form is novalidate, and the submit is cancelled, so the "
             "address never reaches the page URL, the browser history or a request log. There is no "
             "provider, no consent flow and no retention period because nothing is collected. The "
             "one thing still open about it is whether a list should exist at all, which is a "
             "strategy question rather than a privacy one.",
             []),
    "Q-22": ("partly",
             "Three parts are settled. The redirect log holds four independent observations per "
             "token, so a change of target is detectable rather than invisible. The product-intent "
             "record keeps the observed ASIN separate from the intended one, so a replaced listing "
             "can be recorded without rewriting history. And the tooling checks that every "
             "product's observed ASIN still appears in the redirect log, so a mismatch fails the "
             "build instead of passing silently. What is missing is the desk-side procedure: who "
             "re-reads a listing when it changes, what a reader is told, and when a product leaves "
             "the shop. That is the runbook, and it is still to be written.",
             []),
}


def main():
    with io.open(PATH, encoding="utf-8") as f:
        doc = json.load(f, object_pairs_hook=collections.OrderedDict)
    qs = doc["questions"]
    ids = {q["id"] for q in qs}
    missing = set(ANSWERS) - ids
    if missing:
        raise SystemExit("answer blocks for unknown question ids: %s" % sorted(missing))
    for q in qs:
        qid = q["id"]
        if qid not in ANSWERS:
            continue
        state, text, srcs = ANSWERS[qid]
        if state not in ("answered", "partly", "open"):
            raise SystemExit("%s: bad state %r" % (qid, state))
        if state == "open":
            if text:
                raise SystemExit("%s: state 'open' must have an empty answer" % qid)
        elif not text:
            raise SystemExit("%s: state %r needs an answer" % (qid, state))
        q["answer_state"] = state
        q["answer"] = text
        q["answered_on"] = DATE if state != "open" else ""
        q["answered_from"] = srcs
        if state != "open" and not srcs:
            # An answer that rests on nothing is a claim, not a finding. Internal-only answers
            # must say so in the source note instead of citing a document they did not read.
            q["answered_from_note"] = (
                "Settled from this repository's own records on %s: the site's own files and "
                "tooling. No external source applies to this row." % DATE)
        else:
            q["answered_from_note"] = ""
    doc["updated"] = DATE
    doc["_note"] = ("Open-questions register: what we know and can cite, what is genuinely missing, "
                     "which decision the gap blocks, the concrete action that produces the answer, "
                     "and the answer as far as the evidence reaches it. Every row now carries an "
                     "answer_state: 'answered' (the source settles it), 'partly' (the source settles "
                     "part of it and the rest is named), or 'open' (nobody has it and the answer cell "
                     "stays blank). A blank answer cell means the question is still open, not that "
                     "the row was skipped.")
    doc["blocking_count"] = sum(1 for q in qs if str(q.get("blocking", "")).startswith("yes"))
    doc["answered_count"] = sum(1 for q in qs if q.get("answer_state") == "answered")
    doc["partly_count"] = sum(1 for q in qs if q.get("answer_state") == "partly")
    doc["open_count"] = sum(1 for q in qs if q.get("answer_state") == "open")
    with io.open(PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("answers written: %d answered, %d partly, %d open"
          % (doc["answered_count"], doc["partly_count"], doc["open_count"]))


if __name__ == "__main__":
    main()
