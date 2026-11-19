#!/usr/bin/env python3
# share-project/scripts/check_pack.py
# Purpose: the final inspection of a pack folder: required files and headings for its kind, then screening of every file.
# Non-goals: never fixes anything; never runs project code; a check that cannot run is a failure, not a pass.
"""Check a pack folder before it is zipped.

Usage: python3 check_pack.py <pack-folder> [--json]

Fails (exit 1) on: a missing required file or heading; an unfilled template marker; a
placeholder used in project/ but listed nowhere; any screening finding; any
file that could not be checked; a link, archive, version-history folder, keys file, image or
other file that cannot be checked; a data file that is not a recorded stand-in
(STANDINS.json, written by standin.py --pack). A placeholder used in project/ must be listed
in SETUP-LIST.md (something the receiver supplies) or COVERAGE.md (a replaced value).
Exit 0 = passes; 2 = usage error."""

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import classify  # noqa: E402
from screen import screen_paths  # noqa: E402

FORMAT = "share-pack/1"
HEADER_KEYS = ["Pack", "Revision", "Date", "Action", "Format", "Outcome"]
OUTCOME = re.compile(r"^(ready to rebuild against the stated checks|ready for help: .{3,}|incomplete: missing .{3,})$")
COMMON = {
    "START-HERE.md": ["What this is", "What to do", "Prompt for your assistant", "Reading order", "What you must supply",
                      "Rules for the assistant", "Before you start: say back", "Right to share"],
    "COVERAGE.md": ["Copied", "Replaced", "Left out", "Could not be checked"],
    "DATA.md": [],
    "SETUP-LIST.md": [],
    "SAFETY-SUGGESTIONS.md": [],
}
BY_ACTION = {
    "rebuild": {"REBUILD.md": ["What it does", "Observed behaviour", "Intended behaviour (confirmed by the owner)",
                               "Known problems not to copy", "Unknowns", "Exact rules", "Checks that define done",
                               "Free choices", "About project/", "Build order"]},
    "help": {"PROBLEM.md": ["What I did", "What I expected", "What I saw", "Steps", "Exact error text",
                            "What changed recently", "When it last worked", "What I tried", "The question",
                            "Does it show on the safe copy"],
             "REPLY-FORMAT.md": []},
}
TEMPLATE_MARK = re.compile(r"\{\{(?![A-Z0-9_]+\}\})[^}]*\}\}")
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
MAX_PACK_BYTES = 25 * 1024 * 1024
MAX_START_BYTES = 16 * 1024


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def headings(text):
    return {re.sub(r"\s+", " ", m.group(1)).strip().lower() for m in re.finditer(r"^#{1,4}\s+(.+?)\s*#*\s*$", text, re.M)}


def read_header(text):
    found = {}
    for line in text.splitlines()[:20]:
        m = re.match(r"^\s*(?:[-*]\s*)?\**([A-Za-z]+)\**:\s*(.+?)\s*$", line)
        if m and m.group(1) in HEADER_KEYS and m.group(1) not in found:
            found[m.group(1)] = m.group(2).strip("` ")
    return found


def check(pack):
    pack = os.path.abspath(pack)
    problems = []

    def bad(kind, where, detail=""):
        problems.append({"kind": kind, "where": where, "detail": detail})

    start = os.path.join(pack, "START-HERE.md")
    if not os.path.isfile(start):
        bad("missing file", "START-HERE.md")
        return {"pack": pack, "action": None, "problems": problems}
    with open(start, encoding="utf-8", errors="replace") as f:
        start_text = f.read()
    hdr = read_header(start_text)
    for k in HEADER_KEYS:
        if k not in hdr:
            bad("missing header line", "START-HERE.md", f"{k}:")
    action = hdr.get("Action", "").lower()
    if action not in BY_ACTION:
        bad("bad header value", "START-HERE.md", "Action: must be rebuild or help")
    if hdr.get("Format") and hdr["Format"] != FORMAT:
        bad("bad header value", "START-HERE.md", f"Format: must be {FORMAT}")
    if hdr.get("Outcome") and not OUTCOME.match(hdr["Outcome"]):
        bad("bad header value", "START-HERE.md", "Outcome: must be one of the three outcomes")
    if hdr.get("Date") and not re.match(r"^\d{4}-\d{2}-\d{2}$", hdr["Date"]):
        bad("bad header value", "START-HERE.md", "Date: must be YYYY-MM-DD")
    if hdr.get("Revision") and not hdr["Revision"].isdigit():
        bad("bad header value", "START-HERE.md", "Revision: must be a whole number")
    if os.path.getsize(start) > MAX_START_BYTES:
        bad("too long", "START-HERE.md", f"over {MAX_START_BYTES // 1024} KiB; the first page must stay short")

    required = dict(COMMON)
    required.update(BY_ACTION.get(action, {}))
    for name, heads in required.items():
        path = os.path.join(pack, name)
        if not os.path.isfile(path):
            bad("missing file", name)
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        have = headings(text)
        for h in heads:
            if h.lower() not in have:
                bad("missing heading", name, h)
        if TEMPLATE_MARK.search(text):
            bad("template text not filled in", name)
    if not os.path.isdir(os.path.join(pack, "project")):
        bad("missing folder", "project/")

    standins = {}
    rec = os.path.join(pack, "STANDINS.json")
    if os.path.isfile(rec):
        try:
            with open(rec) as f:
                standins = {e["path"]: e["sha256"] for e in json.load(f)["standins"]}
        except (ValueError, KeyError, TypeError):
            bad("unreadable record", "STANDINS.json")

    total, used = 0, set()
    for base, dirs, files in os.walk(pack, followlinks=False):
        for d in list(dirs):
            rel = os.path.relpath(os.path.join(base, d), pack)
            if os.path.islink(os.path.join(base, d)):
                bad("link", rel)
                dirs.remove(d)
            elif d in (".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv"):
                bad("left-out folder present", rel)
                dirs.remove(d)
        for n in files:
            full = os.path.join(base, n)
            rel = os.path.relpath(full, pack)
            if os.path.islink(full) or not os.path.isfile(full):
                bad("link or special file", rel)
                continue
            total += os.path.getsize(full)
            kind, reason = classify(rel, full)
            if rel == "STANDINS.json":
                continue
            if kind == "data":
                inner = os.path.relpath(full, os.path.join(pack, "project"))
                if standins.get(inner) != sha256(full):
                    bad("data file that is not a recorded stand-in", rel)
            elif kind != "code":
                bad(f"{kind} file present", rel, reason)
            if rel.startswith("project" + os.sep) and kind == "code":
                with open(full, encoding="utf-8", errors="replace") as f:
                    used.update(PLACEHOLDER.findall(f.read()))
    if total > MAX_PACK_BYTES:
        bad("too large", "pack", f"over {MAX_PACK_BYTES // (1024 * 1024)} MiB")

    listed = set()
    for page in ("SETUP-LIST.md", "COVERAGE.md"):
        path = os.path.join(pack, page)
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                listed |= set(PLACEHOLDER.findall(f.read()))
    for name in sorted(used - listed):
        bad("placeholder in project/ not listed in SETUP-LIST.md (keys, accounts) or COVERAGE.md (replaced values)", name)

    screened = screen_paths([pack], names=True)
    for f in screened["findings"]:
        bad("screening finding", f"{f['file']}:{f['line']}" if f["line"] else f["file"], f["kind"])
    for n in screened["not_checked"]:
        bad("could not be checked", n["file"], n["reason"])
    return {"pack": pack, "action": action or None, "files_checked": screened["files_checked"], "problems": problems}


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("check_pack: give one pack folder", file=sys.stderr)
        return 2
    res = check(args[0])
    if "--json" in argv:
        print(json.dumps(res, indent=1))
    else:
        for p in res["problems"]:
            print(f"PROBLEM  {p['kind']}: {p['where']}" + (f" ({p['detail']})" if p["detail"] else ""))
        print(f"{'PASS' if not res['problems'] else 'FAIL'}: {len(res['problems'])} problem(s), "
              f"{res.get('files_checked', 0)} file(s) screened")
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
