#!/usr/bin/env python3
# share-project/scripts/feedback.py
# Purpose: build the feedback report from fixed choices only, for the owner to read and approve before anything is sent.
# Non-goals: accepts no free text, sends nothing and opens nothing; it prints text and an address for the owner to use.
"""Prepare a feedback report.

Usage:
  python3 feedback.py --app <app> --mode <mode> --plan <plan> --os <os> --step <step> --outcome <outcome> [--category <category>]
  python3 feedback.py --choices          list every allowed value

Only the values listed by --choices are accepted; anything else is refused (exit 2), so no
project name, path, file name, error text, account or project content can enter the report.
Prints the report, then a pre-filled issue address for someone with a GitHub account and an
email form for everyone else. It never opens a link or sends anything: the owner reads the
report first and decides. Exit 0 = report printed; 2 = a value outside the allowed list."""

import os
import sys
from urllib.parse import quote

REPOSITORY = "Titus6553/share-project"   # fixed at release; see references/update-and-feedback.md
FEEDBACK_EMAIL = "the address Ben gave you with the skill"
CHOICES = {
    "app": ["claude-desktop-chat", "claude-desktop-cowork", "claude-desktop-code", "claude-code-terminal",
            "claude-web", "chatgpt-desktop", "chatgpt-web", "codex-app", "codex-terminal", "other"],
    "mode": ["chat", "agent", "project-folder", "unknown"],
    "plan": ["free", "pro", "max", "plus", "team", "business", "enterprise", "edu", "unknown"],
    "os": ["mac", "windows", "linux", "unknown"],
    "step": ["install", "capability-check", "intake", "inventory", "stand-ins", "screening", "preview",
             "final-check", "zip", "delivery", "receiving", "reply-note", "update", "feedback", "other"],
    "outcome": ["worked", "failed", "stopped-by-skill", "confusing", "slow"],
    "category": ["none", "could-not-read-folder", "could-not-run-helpers", "no-python", "zip-not-delivered",
                 "check-failed", "stand-in-failed", "unexpected-content-in-pack", "wording-unclear",
                 "install-refused", "update-failed", "other"],
}


def release():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(here, "VERSION")) as f:
            v = f.read().strip()
        return v if v.replace(".", "").isdigit() else "unknown"
    except OSError:
        return "unknown"


def parse(argv):
    values, i = {}, 0
    while i < len(argv):
        key = argv[i][2:] if argv[i].startswith("--") else None
        if key not in CHOICES or i + 1 >= len(argv):
            raise ValueError(f"unknown option {argv[i]!r}")
        if argv[i + 1] not in CHOICES[key]:
            raise ValueError(f"--{key} must be one of: {', '.join(CHOICES[key])}")
        values[key] = argv[i + 1]
        i += 2
    missing = [k for k in CHOICES if k != "category" and k not in values]
    if missing:
        raise ValueError("missing: " + ", ".join("--" + k for k in missing))
    values.setdefault("category", "none")
    return values


def report(values):
    lines = [f"share-project feedback (release {release()})"]
    lines += [f"{k}: {values[k]}" for k in CHOICES]
    return "\n".join(lines)


def main(argv):
    if not argv or "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    if argv == ["--choices"]:
        for k, v in CHOICES.items():
            print(f"--{k}: {', '.join(v)}")
        return 0
    try:
        values = parse(argv)
    except ValueError as e:
        print(f"feedback: {e}", file=sys.stderr)
        return 2
    text = report(values)
    title = f"Feedback: {values['outcome']} at {values['step']} ({values['app']})"
    print("REPORT (show this to the owner exactly as it is):\n")
    print(text)
    print("\nNothing has been sent. If the owner approves, one of:")
    print(f"- GitHub: https://github.com/{REPOSITORY}/issues/new?title={quote(title)}&body={quote(text)}")
    print(f"- Email: copy the report into an email to {FEEDBACK_EMAIL}.")
    print("Anything the owner adds by hand goes below a line reading 'Added by the owner:' so it is kept apart.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
