#!/usr/bin/env python3
"""Step 1 — research. Build one brief per product from what this repository can actually prove.

Usage:
    python3 scripts/agent/research.py                # every product
    python3 scripts/agent/research.py --asin B0CDY277D3

Writes data/research/<asin>.json. A brief never contains a value that is not already in the
register, and never merges the intended and observed identifiers (that separation is the point
of the product-intent record — see FLG-002 and FLG-003).

PRICING IS GATED. Amazon's Program Policies allow price and availability to be shown only when
the link Amazon serves displays it, or when the data comes from the Creators API or the
Product Advertising API (https://affiliate-program.amazon.com/help/operating/policies).
Without PA API credentials this step records price_live = null and says why. It does not read
a price off a web page, because a scraped price is not a source Amazon permits us to publish.
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, SITE, load, save, today, fmt, blank_mark  # noqa: E402

SPEC_FIELDS = ["brand", "model", "category", "capacity", "dimensions", "weight",
               "temperature", "power", "upc"]
# Fields a listing may legitimately leave blank for a product type.
NOT_APPLICABLE = {"capacity": "Air Fryers", "power": "Meat Thermometers",
                  "temperature": "Air Fryers"}


def paapi_price(asin):
    """GATED: live price from the Product Advertising API, when credentials exist.

    Returns (price_or_None, note). Never scrapes and never guesses.
    """
    key = os.environ.get("PAAPI_ACCESS_KEY")
    secret = os.environ.get("PAAPI_SECRET_KEY")
    tag = os.environ.get("PAAPI_PARTNER_TAG")
    if not (key and secret and tag):
        return None, ("No Product Advertising API credentials in the environment, so no live price "
                      "was fetched. Program Policies allow a price to be displayed only when the "
                      "link Amazon serves shows it, or when it comes from the Creators/PA API "
                      "(S02). Until then the price stays blank and the reader is sent to Amazon.")
    # GATED: PA API requires a signed request per endpoint (ItemSearch / GetItems). The signing
    # code is deliberately not written blind: the API's auth and throttle rules change, and a
    # half-working signer that silently returns nothing is worse than no signer. Set the three
    # variables above, add the signed call here, and the brief will carry the API's own price.
    return None, ("PA API credentials were present but this build does not yet make a signed "
                  "ItemSearch call. The price stays blank rather than being guessed.")


def brief_for(p, flags, questions, probes):
    asin = p["observed_asin"]
    open_flags = [f for f in flags if asin in json.dumps(f)]
    blocking = [q for q in questions if asin in json.dumps(q)]
    specs = {}
    unknown = []
    for f in SPEC_FIELDS:
        v = fmt(p.get(f))
        if v:
            specs[f] = {"value": v, "source": p["source_url"], "source_date": p["source_date"]}
        else:
            specs[f] = {"value": "", "note": blank_mark()}
            if NOT_APPLICABLE.get(f) == p["category"]:
                specs[f]["note"] = "does not apply to this product type"
            else:
                unknown.append(f)

    price, price_note = paapi_price(asin)
    observed = next((pr for pr in probes if pr.get("final_asin") == asin), None)

    return {
        "generated": today(),
        "generated_by": "scripts/agent/research.py",
        "asin": asin,
        "product_id": p["id"],
        "title_as_listed": p["title"],
        "editorial": {k: p.get(k, "") for k in
                      ("dek", "best_for", "catch", "check_before_buying")},
        "identity": {
            "submitted_url": p["submitted_url"],
            "submitted_token": p["submitted_token"],
            "submitted_token_length": p.get("token_length"),
            "intended_asin": p.get("intended_asin", ""),
            "intended_listing_url": p.get("intended_listing_url", ""),
            "intended_confirmation_date": p.get("confirmation_date", ""),
            "intended_source": p.get("intended_source", ""),
            "observed_asin": asin,
            "observed_listing_url": p["observed_listing_url"],
            "observed_date": p.get("observed_date", ""),
            "observed_source": p.get("observed_source", ""),
            "note": ("The intended and observed identifiers are kept in separate fields on purpose. "
                     "Nothing public binds the submitted short token to a product, so the intended "
                     "field stays blank until the product-intent confirmation is done by hand "
                     "(FLG-002, FLG-003)."),
        },
        "specs": specs,
        "unknown_specs": unknown,
        "price_live": price,
        "price_live_note": price_note,
        "rating_live": None,
        "rating_live_note": ("Ratings are not published here. They move daily, and the Program "
                             "Policies price/availability rule (S02) is the reason a static copy of "
                             "one would be misleading."),
        "open_flags": [{"id": f["id"], "issue": f.get("issue", ""),
                        "action": f.get("action", "")} for f in open_flags],
        "blocking_questions": [{"id": q["id"], "question": q.get("question", ""),
                                "answer": q.get("answer", "")} for q in blocking],
        "redirect_observation": None if not observed else {
            "submitted_token": observed.get("submitted_token"),
            "final_asin": observed.get("final_asin"),
            "session": observed.get("session"),
            "date": observed.get("date"),
            "note": observed.get("note", ""),
        },
        "listing_conflicts": p.get("listing_notes", []),
        "faq": p.get("faq", []),
        "listing_url": p["source_url"],
        "site": SITE,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asin", help="one ASIN; default is every product in the register")
    args = ap.parse_args()

    products = load("data/products.json")["products"]
    flags = load("data/flags.json")["flags"]
    questions = load("data/questions.json")["questions"]
    probes = load("data/probes.json")["probes"]

    made = []
    for p in products:
        if args.asin and p["observed_asin"] != args.asin:
            continue
        b = brief_for(p, flags, questions, probes)
        rel = "data/research/%s.json" % p["observed_asin"]
        save(rel, b)
        made.append((rel, len(b["unknown_specs"])))
    if not made:
        print("no product matched --asin %s" % args.asin)
        return 1
    for rel, n in made:
        print("wrote %s (%d spec field(s) still unconfirmed)" % (rel, n))
    print("%d research brief(s) written. Every value carries its source; the rest stayed blank."
          % len(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
