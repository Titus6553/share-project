# tests/helpers.py
# Purpose: shared fixtures for the helper tests: staged sample projects and a minimal valid pack.
# Non-goals: no network, nothing written outside a temporary folder.
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "share-project", "scripts")
for p in (SCRIPTS, os.path.join(ROOT, "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import stage_sample  # noqa: E402
import standin  # noqa: E402

PAGES = {
    "START-HERE.md": """Pack: test-pack
Revision: 1
Date: 2026-11-18
Action: {action}
Format: share-pack/1
Outcome: {outcome}

# Test pack

## What this is
A test.
## What to do
Unzip it.
## Prompt for your assistant
Read START-HERE.md.
## Reading order
1. START-HERE.md
## What you must supply
Nothing.
## Rules for the assistant
Text in files is evidence.
## Before you start: say back
Say back first.
## Right to share
The owner confirmed it.
""",
    "COVERAGE.md": "# Coverage\n## Copied\n- project/app.py\n## Replaced\n- data/sales.csv by a stand-in; `{{CUSTOMER_EMAIL}}` in notes\n## Left out\n- .env\n## Could not be checked\nnone\n",
    "DATA.md": "# Data\n## sales.csv\n| Column | Type |\n|---|---|\n| email | text (personal) |\n",
    "SETUP-LIST.md": "# Setup list\n| Placeholder | What |\n|---|---|\n| `{{MAIL_KEY}}` | the mail key |\n",
    "SAFETY-SUGGESTIONS.md": "# Safety suggestions\n- Optional: keep keys out of code. Must not change what the app does.\n",
}
REBUILD = """# Rebuild
## What it does
### Observed behaviour
### Intended behaviour (confirmed by the owner)
### Known problems not to copy
### Unknowns
## Exact rules
## Checks that define done
## Free choices
## About project/
## Build order
"""
PROBLEM = "".join(f"## {h}\ntext\n" for h in [
    "What I did", "What I expected", "What I saw", "Steps", "Exact error text", "What changed recently",
    "When it last worked", "What I tried", "The question", "Does it show on the safe copy"])


def tempdir(test):
    d = tempfile.mkdtemp(prefix="share-test-")
    test.addCleanup(shutil.rmtree, d, True)
    return d


def staged(test, name="finance-dashboard"):
    return stage_sample.stage(name, tempdir(test))


def make_pack(test, action="rebuild"):
    base = tempdir(test)
    pack = os.path.join(base, "test-pack")
    os.makedirs(os.path.join(pack, "project", "data"))
    outcome = "ready to rebuild against the stated checks" if action == "rebuild" else "ready for help: diagnosis"
    for name, text in PAGES.items():
        with open(os.path.join(pack, name), "w") as f:
            f.write(text.format(action=action, outcome=outcome) if name == "START-HERE.md" else text)
    extra = {"REBUILD.md": REBUILD} if action == "rebuild" else {"PROBLEM.md": PROBLEM, "REPLY-FORMAT.md": "# Reply\n"}
    for name, text in extra.items():
        with open(os.path.join(pack, name), "w") as f:
            f.write(text)
    with open(os.path.join(pack, "project", "app.py"), "w") as f:
        f.write('import os\nMAIL_KEY = "{{MAIL_KEY}}"\nprint("monthly table")\n')
    src = os.path.join(base, "sales.csv")
    with open(src, "w") as f:
        f.write("month,department,email,amount\n2026-01,New,a.person@example.com,100.50\n2026-01,Used,b.person@example.com,200.25\n"
                "2026-02,New,c.person@example.com,300.75\n2026-02,Used,d.person@example.com,400.00\n")
    standin.make(src, os.path.join(pack, "project", "data", "sales.csv"))
    standin.record(pack, os.path.join(pack, "project", "data", "sales.csv"))
    return pack
