#!/usr/bin/env python3
"""Step 3 — publish. Build the site, run the compliance gate, and only then say it is published.

Usage:
    python3 scripts/agent/publish.py

This step never edits content. It calls the same two commands a person would run by hand:

    python3 scripts/build_site.py
    python3 scripts/check_site.py

and refuses to report success if the gate reports a violation. It also reports whether the
committed output matches what the generator produced — if it does not, the site that is live
and the site the data describes are different files, and that must be fixed before publishing.

Exit code 0 = built, gate green, committed output matches. Exit code 1 = something is wrong and
the reason is printed.
"""
import os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT  # noqa: E402


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    rc, out = run([sys.executable, "scripts/build_site.py"])
    print(out.strip())
    if rc != 0:
        print("\nFAIL: the build did not complete.")
        return 1

    rc, out = run([sys.executable, "scripts/check_site.py"])
    print(out.strip())
    if rc != 0:
        print("\nFAIL: the compliance gate reported a violation. Nothing was published.")
        return 1

    # The committed tree must equal the generator's output, or the live site and the
    # registers describe different pages.
    rc, out = run(["git", "diff", "--stat", "--", "*.html", "*.xml", "assets/search-index.json"])
    if out.strip():
        print("\nFAIL: the committed site differs from what the generator produced. "
              "Run `python3 scripts/build_site.py` and commit the result before publishing.")
        print(out.strip())
        return 1

    print("\nOK: built, gate green, and the committed site matches the registers.")
    print("Next: commit the output, merge to main, and confirm the deploy with "
          "`python3 scripts/deploy_check.py`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
