#!/usr/bin/env python3
"""Add the decision-making suggestions (session arena/6561e2ea-winc).

The brief asks for a section a person can review, so they can choose a path before anything
is implemented. The register already listed 34 suggestions, but they were mostly about the
*site*. These six are about the *decision* — what can be decided today, what each suggestion
unblocks, which question it waits on, and how the next topic gets chosen from measured
evidence rather than instinct.

Every row keeps the register's shape, and every row names the evidence it rests on.
"""
import json, collections, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "suggestions.json")
DATE = "2026-11-20"
SESSION = "arena/6561e2ea-winc"

NEW = [
    collections.OrderedDict([
        ("id", "SG-41"),
        ("title", "Answer the questions, and show the reader which ones are answered"),
        ("status", "done-this-session"),
        ("area", "Decision"),
        ("problem", "Every one of the 22 rows in the open-questions register had an empty answer cell. The register could say what was missing but never what was known, which made it a to-do list rather than a decision surface — and made it impossible to tell which questions were actually blocking a decision."),
        ("proposal", "Give every question an answer_state of answered / partly / open, write the answer the sources support (including the partial ones), cite the source in each answer, and put a 'decisions you can make now' panel at the top of the questions page so a reviewer sees the settled questions before the table."),
        ("effort", "M"),
        ("cost", "none"),
        ("risk", "An answer that is not sourced becomes a claim. The gate now rejects an answered row with no answer date or no source list, so this cannot rot silently."),
        ("expected_effect", "A reviewer can separate 'we know this' from 'we are waiting on someone' in one screen. Measure: rows carrying a non-empty answer; the count is printed in the page header."),
        ("evidence", "data/questions.json now records 11 answered, 10 partly answered and 1 open row; every non-open answer names the source ids it rests on."),
        ("feeds_prompt", "Keep every question row carrying an answer_state, an answer date and a source list. When a new source lands in data/sources.json, re-run scripts/patch_answers.py and re-check the counts."),
        ("status_detail", "Shipped by %s on %s. The questions page now opens with the answered / partly / still open split." % (SESSION, DATE)),
    ]),
    collections.OrderedDict([
        ("id", "SG-42"),
        ("title", "Make every suggestion carry the decision it unblocks and the question it waits on"),
        ("status", "recommended-now"),
        ("area", "Decision"),
        ("problem", "A suggestion register that only says 'what would change' cannot be triaged. The reviewer has to hold the whole map in their head to work out which suggestions are blocked by which question, and which ones are free to start today."),
        ("proposal", "Add two fields to every suggestion row: unblocks (the decision it makes possible) and waits_on (the question id it depends on, or none). Then the direction page can sort and filter: 'free to start', 'waiting on Q-01', 'waiting on the account owner'."),
        ("effort", "S"),
        ("cost", "none"),
        ("risk", "Low. It is two fields and a table column; the existing rows can be filled in one pass and the gate can require them."),
        ("expected_effect", "A reviewer picks a path by reading two columns instead of reconstructing the dependencies. Measure: the number of suggestions whose waits_on is filled; the direction page shows the split."),
        ("evidence", "Today the register has 34 rows and no dependency column, while the questions register already identifies five blocking rows."),
        ("feeds_prompt", "Add unblocks and waits_on to every suggestion in data/suggestions.json, require both in scripts/check_site.py, and show the split on direction.html as three counts: free to start, waiting on a question, waiting on the account owner."),
    ]),
    collections.OrderedDict([
        ("id", "SG-43"),
        ("title", "Let the pipeline propose the next topic from the register, not from instinct"),
        ("status", "open"),
        ("area", "Machinery"),
        ("problem", "The topic backlog records how each topic was chosen, and every entry says 'editorial hypothesis'. That is honest, but it means the next topic is a guess — and a guess is exactly the thing that ages badly while the question register and the search index both sit there unused."),
        ("proposal", "Extend scripts/agent/research.py with a 'propose' mode that ranks candidate topics by (a) questions in the register whose answer is now 'answered' and whose decision is still open, and (b) pages that exist but have no guide above them. It should propose, with its evidence, and publish nothing: the desk still chooses."),
        ("effort", "M"),
        ("cost", "none"),
        ("risk", "A proposal engine that looks authoritative can launder a guess into a plan. Mitigation: every proposal must print the question ids and the pages it reasoned from, and must be labelled a proposal."),
        ("expected_effect", "The next topic is chosen from the register's own gaps. Measure: proposed topics whose chosen_from names a question id rather than a hypothesis."),
        ("evidence", "data/topics.json requires every topic to state its provenance and every entry currently says hypothesis; scripts/agent/research.py already reads the questions register."),
        ("feeds_prompt", "Add a propose mode to scripts/agent/research.py that reads data/questions.json and data/topics.json, ranks candidate topics by unanswered-but-now-settled questions and uncovered clusters, prints the evidence for each proposal, and writes nothing."),
    ]),
    collections.OrderedDict([
        ("id", "SG-44"),
        ("title", "Record which decision a click was meant to inform, not just which page it left"),
        ("status", "open"),
        ("area", "Measurement"),
        ("problem", "The outbound_click event records the page and the ASIN. It does not record the question the reader was on, so a ledger can say 'the capacity guide sent 40 clicks' but never 'the capacity guide answered the question 40 people actually had'. The brief asks for evidence-based iteration, and evidence needs the question attached."),
        ("proposal", "Add the guide's cluster and the question the page answers to the outbound_click payload, so a ledger row can be read as 'readers asking X left via this product'. The data-event attribute on each buy link already knows the ASIN; the page context is one more field."),
        ("effort", "S"),
        ("cost", "none"),
        ("risk", "Adding fields to an event that is not yet deployed is free now and awkward later, which argues for doing it before the endpoint goes live rather than after."),
        ("expected_effect", "The first reporting period can answer 'which question sends buyers', not only 'which page sends clicks'. Measure: ledger rows carrying a question id."),
        ("evidence", "assets/app.js sends {asin, target} on outbound_click; the pages carry a cluster on every guide."),
        ("feeds_prompt", "Extend the outbound_click payload with the page cluster and the question the page answers, add the matching columns to data/campaign-ledger.json, and keep the rule that no row is written without a first-party number."),
    ]),
    collections.OrderedDict([
        ("id", "SG-45"),
        ("title", "Check the disclosure wording per link type, not once for the whole site"),
        ("status", "open"),
        ("area", "Compliance"),
        ("problem", "The site uses one marker on every reader link. The FTC Endorsement Guides are specific that a disclosure must be clear and conspicuous and close to the link, and Amazon's own help says the link-level disclosure must be clear and conspicuous. One marker for a product card and one for a link buried in a comparison table are not the same placement, and the review so far has treated them as one thing."),
        ("proposal", "Write a short matrix — link type (card button, in-text product link, guide comparison link, footer link) against marker, placement and wording — and check each row against the Operating Agreement §5 and the FTC Endorsement Guides. Publish the matrix on the disclosure page so the placement is reviewable rather than assumed."),
        ("effort", "S"),
        ("cost", "none"),
        ("risk", "None to the site; the risk is in the paperwork, where an unreviewed placement is a compliance gap nobody can see."),
        ("expected_effect", "Every reader link's disclosure can be checked against a written rule instead of a general one. Measure: rows in the matrix with a named source and a date."),
        ("evidence", "S01 §5, S03 (affiliate disclosure section), S07 (clear and conspicuous, near the link) are all in the register; the current implementation is a single badge on every link."),
        ("feeds_prompt", "Add a disclosure matrix to the disclosure page — one row per link type, with the marker, the placement, the exact wording and the source id — and make the gate check each row's wording appears on the page."),
    ]),
    collections.OrderedDict([
        ("id", "SG-46"),
        ("title", "Add the honest counterfactual: what would make someone buy the other one"),
        ("status", "open"),
        ("area", "Editorial"),
        ("problem", "Each product page now says what it is best for and what its catch is. It does not say what would send a reader to the other product in the shop. A comparison that never mentions the alternative reads as a sales page, which is the register's own line: no ranking, no preference, no verdict."),
        ("proposal", "Add one line per product — 'choose this instead if …' — pointing at the sibling product and the one spec that would push a reader that way. It is a cross-link with a reason, and it can be written entirely from the specs already in the register."),
        ("effort", "M"),
        ("cost", "none"),
        ("risk", "An alternative line that reads as a verdict ('the other one is worse') would break the no-ranking rule the gate enforces. The wording must name a situation, not a winner."),
        ("expected_effect", "The shop reads as a shop that will lose a sale, which is the strongest trust signal available without testing anything. Measure: cross-links between product pages, and the outbound clicks that follow them."),
        ("evidence", "Each product already carries a dek, a best_for line and a catch in data/products.json, all grounded in the listing; the sibling products and their deciding specs are already in data/categories.json."),
        ("feeds_prompt", "Add a 'choose this instead if' line per product in data/products.json, pointing at the sibling product and the one spec that decides it, and render it on the product page as a cross-link. Keep it a situation, never a winner."),
    ]),
]


def main():
    with io.open(PATH, encoding="utf-8") as f:
        doc = json.load(f, object_pairs_hook=collections.OrderedDict)
    existing = {s["id"] for s in doc["suggestions"]}
    for s in NEW:
        if s["id"] in existing:
            print("skip (already present): %s" % s["id"])
            continue
        for field in ("id", "title", "status", "area", "problem", "proposal", "risk",
                      "expected_effect", "evidence", "feeds_prompt", "effort", "cost"):
            if not s.get(field):
                raise SystemExit("%s: field %s is empty" % (s["id"], field))
        doc["suggestions"].append(s)
        print("added %s — %s" % (s["id"], s["title"]))
    doc["updated"] = DATE
    doc["reviewed_by_session"] = (doc.get("reviewed_by_session", "") +
                                  "; SG-41..SG-46 added by %s (%s)" % (SESSION, DATE)).strip("; ")
    with io.open(PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("suggestions now: %d" % len(doc["suggestions"]))


if __name__ == "__main__":
    main()
