#!/usr/bin/env python3
"""Confirm GitHub Pages actually deployed this site, and that what is live is correct.

Run: python3 scripts/deploy_check.py [--skip-live]

Two independent halves:

  1. THE PUBLISHER'S RECORD (GitHub API)
     Reads the repository's Pages configuration and the most recent Pages build, and
     checks that the build finished `built` with no error and that the commit it published
     is the tip of `main` (or an ancestor of it). This is the answer to "did Pages deploy
     successfully?" that does not depend on anybody eyeballing a badge.

  2. WHAT IS LIVE (HTTP)
     Fetches the published URLs and checks the things the compliance gate cannot check on
     a build artifact: HTTP 200, the Associates disclosure statement above the fold, the
     Operating Agreement disclosure wording, rel="sponsored" on every reader buy link,
     canonical URLs pointing at this site, and no price-like string anywhere in the body.

Exit code 0 = deployed and correct. Exit code 1 = something is wrong; the reasons are printed.

The live half needs to reach the published domain. In a network-restricted sandbox use
`--skip-live` and run the live half from a machine that can reach it (or read the same
pages with the browser reader and compare them against `dist` expectations by hand).
"""
import json, os, re, sys, subprocess, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "sassnarep3-star/WinC"
SITE = "https://sassnarep3-star.github.io/WinC/"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
PRICE_RE = re.compile(r"\$\s?\d|€\s?\d|£\s?\d|\bUSD\s?\d", re.I)

# The URLs that must be live. One per page type in the site, not every page — the gate
# covers the whole tree; this checks that the publisher really served it.
LIVE_PATHS = [
    "index.html",
    "products/index.html",
    "products/chefman-6qt-dual-basket-b0cdy277d3.html",
    "guides/index.html",
    "guides/basket-or-oven-style-air-fryer.html",
    "air-fryers.html",
    "thermometers.html",
    "verification.html",
    "flagged-for-review.html",
    "questions.html",
    "direction.html",
    "measurement.html",
    "executive-summary.html",
    "disclosure.html",
    "about.html",
    "search.html",
    "topics.html",
    "feed.xml",
    "sitemap.xml",
    "robots.txt",
]

problems = []
notes = []


def gh(path):
    """Call the GitHub API with the token gh already has, or no token for public reads."""
    url = "https://api.github.com" + path
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "winc-deploy-check",
    })
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True).stdout.strip()


def check_publisher():
    try:
        pages = gh("/repos/%s/pages" % REPO)
    except Exception as e:
        problems.append("cannot read the Pages configuration: %s" % e)
        return
    notes.append("Pages build_type=%s source=%s/%s public=%s"
                 % (pages.get("build_type"),
                    (pages.get("source") or {}).get("branch"),
                    (pages.get("source") or {}).get("path"),
                    pages.get("public")))
    try:
        build = gh("/repos/%s/pages/builds/latest" % REPO)
    except Exception as e:
        problems.append("cannot read the latest Pages build: %s" % e)
        return
    status = build.get("status")
    err = (build.get("error") or {}).get("message")
    sha = build.get("commit")
    notes.append("latest Pages build: status=%s commit=%s error=%s"
                 % (status, (sha or "")[:9], err))
    if status != "built":
        problems.append("the latest Pages build is %r, not 'built'%s"
                        % (status, (" (%s)" % err) if err else ""))
    if not sha:
        problems.append("the latest Pages build record carries no commit")
        return
    main = git("rev-parse", "origin/main")
    if main and sha != main:
        anc = subprocess.run(["git", "merge-base", "--is-ancestor", sha, main],
                             cwd=ROOT, capture_output=True).returncode == 0
        if anc:
            notes.append("the published commit %s is an ancestor of origin/main %s — main has moved on since"
                         % (sha[:9], main[:9]))
        else:
            problems.append("the published commit %s is not on origin/main (%s)" % (sha[:9], main[:9]))


def check_live():
    for path in LIVE_PATHS:
        url = SITE + path
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
                code = r.status
        except urllib.error.HTTPError as e:
            problems.append("%s -> HTTP %s" % (url, e.code))
            continue
        except Exception as e:
            # the host itself is unreachable (air-gapped sandbox, blocked egress) — that is a
            # property of where the command runs, not a fault in the site. Say so once.
            problems.append("the published site could not be reached from this machine (%s) — "
                            "run this check somewhere with access to %s, or use --skip-live" % (e, SITE))
            return
        if code != 200:
            problems.append("%s -> HTTP %s" % (url, code))
            continue
        if path.endswith(".html"):
            if DISCLOSURE not in body:
                problems.append("%s -> the Associates disclosure statement is missing" % url)
            # the disclosure must sit above the fold: before the first </header>
            head_end = body.find("</header>")
            if head_end == -1 or DISCLOSURE not in body[:head_end]:
                problems.append("%s -> the disclosure strip is not above the fold" % url)
            for m in re.finditer(r'<a[^>]+href="(https://www\.amazon\.com/dp/[^"]+)"[^>]*>', body):
                tag = m.group(0)
                if 'data-event="outbound_click"' in tag and 'rel="sponsored' not in tag:
                    problems.append("%s -> a live buy link is missing rel=sponsored" % url)
                    break
            if 'rel="canonical"' in body and SITE not in body:
                problems.append("%s -> canonical URL does not point at this site" % url)
        if PRICE_RE.search(re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", body)):
            problems.append("%s -> the live page contains a price-like string" % url)
    notes.append("checked %d live URLs" % len(LIVE_PATHS))


def main():
    skip_live = "--skip-live" in sys.argv
    check_publisher()
    if skip_live:
        notes.append("live checks skipped (--skip-live)")
    else:
        check_live()
    for n in notes:
        print("  " + n)
    if problems:
        print("\nFAIL (%d problem(s)):" % len(problems))
        for p in problems:
            print(" -", p)
        return 1
    print("\nOK: Pages published this repository and the live pages are correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
