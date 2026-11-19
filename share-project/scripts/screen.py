#!/usr/bin/env python3
# share-project/scripts/screen.py
# Purpose: screen files (or a message) for keys, passwords and personal data, reporting file, line and kind, never the value.
# Non-goals: does not change any file and does not decide what is private by file type; names and headings are not screened as private.
"""Screen text for keys, passwords and personal details.

Usage:
  python3 screen.py <path> [<path> ...]      screen files and folders (folders are walked, links not followed)
  python3 screen.py --names <path> ...       also flag file and folder names that look like a secret value
  python3 screen.py --json ...               machine-readable result on stdout

Every regular file is screened whatever its extension. A file that is binary, larger than
1 MiB or unreadable is reported as NOT CHECKED, never as clean. Exit 0 = nothing found and
everything checked; 1 = findings or unchecked content; 2 = usage or environment error.
Matched values are never printed."""

import io
import json
import os
import re
import sqlite3
import sys
import zipfile

MAX_BYTES = 1024 * 1024
STANDIN_MARK = "standin-"

PLACEHOLDER = re.compile(r"^(\{\{[A-Z0-9_]+\}\}|\$\{?[A-Z0-9_]+\}?|<[A-Za-z0-9_ -]+>|os\.environ.*|process\.env.*|getenv.*|"
                         r"env\(.*|x+|\*+|changeme|your[_-].*|example.*|none|null|true|false|\"\"|'')$", re.I)

SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("cloud access key", re.compile(r"\b(AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("code-host token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20,})")),
    ("chat-service token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("payment-service key", re.compile(r"\b[rsp]k_(live|test)_[A-Za-z0-9]{10,}")),
    ("cloud API key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}")),
    ("AI-service key", re.compile(r"\bsk-(proj-|ant-)?[A-Za-z0-9_-]{20,}")),
    ("signed web token", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("password in an address", re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s/:@'\"]+:[^\s/@'\"]+@")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{16,}")),
    ("key-shaped value", re.compile(r"\b[A-Za-z]{2,8}_(?:[A-Za-z0-9]+_)*(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{12,}\b")),
]
ASSIGNMENT = re.compile(
    r"(?i)\b[\w.-]*(api[_-]?key|secret|token|passw(?:or)?d|pwd|passphrase|credential|private[_-]?key|access[_-]?key|"
    r"signing[_-]?key|auth[_-]?key|client[_-]?secret)[\w.-]*[\"']?\s*(?:[:=]|=>)\s*[\"']?([^\s\"',;#]{6,})")

PERSONAL_PATTERNS = [
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("phone number", re.compile(r"(?<![\w-])(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?![\w-])")),
    ("government id number", re.compile(r"(?<![\w-])\d{3}-\d{2}-\d{4}(?![\w-])")),
    ("vehicle id (VIN)", re.compile(r"\b(?=[A-HJ-NPR-Z0-9]*\d)(?=[A-HJ-NPR-Z0-9]*[A-HJ-NPR-Z])[A-HJ-NPR-Z0-9]{17}\b")),
]
CARD = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")


def luhn(digits):
    total, alt = 0, False
    for d in reversed(digits):
        n = int(d)
        if alt:
            n = n * 2 - 9 if n > 4 else n * 2
        total, alt = total + n, not alt
    return total % 10 == 0


def screen_text(text):
    """Return [(line, column, kind)] for one text. Values are not returned."""
    hits = []
    for ln, line in enumerate(text.splitlines(), start=1):
        if STANDIN_MARK in line and not any(p.search(line) for _, p in SECRET_PATTERNS):
            line = re.sub(r"\S*" + STANDIN_MARK + r"\S*", " ", line)
        for kind, pat in SECRET_PATTERNS:
            for m in pat.finditer(line):
                if not PLACEHOLDER.match(m.group(0)) and not ("{{" in m.group(0) and "}}" in m.group(0)):
                    hits.append((ln, m.start() + 1, kind))
        for m in ASSIGNMENT.finditer(line):
            value = m.group(2).strip("\"'")
            if not PLACEHOLDER.match(value) and not value.startswith("{{"):
                hits.append((ln, m.start(2) + 1, "password or key in an assignment"))
        for kind, pat in PERSONAL_PATTERNS:
            for m in pat.finditer(line):
                v = m.group(0)
                if v.lower().endswith(".invalid") or (kind == "phone number" and re.match(r"\(?000\b", v)):
                    continue  # stand-in shapes: reserved .invalid mail domain, area code 000 (never assigned)
                hits.append((ln, m.start() + 1, kind))
        for m in CARD.finditer(line):
            digits = re.sub(r"\D", "", m.group(0))
            if 13 <= len(digits) <= 19 and luhn(digits) and len(set(digits)) > 2:
                hits.append((ln, m.start() + 1, "payment card number"))
    seen, out = set(), []
    for h in hits:
        if (h[0], h[2]) not in seen:
            seen.add((h[0], h[2]))
            out.append(h)
    return out


def name_hits(rel_path):
    """A file or folder name that is itself a secret value (or id number) is flagged."""
    hits = []
    for part in rel_path.replace("\\", "/").split("/"):
        for kind, pat in SECRET_PATTERNS + PERSONAL_PATTERNS[2:]:
            if pat.search(part):
                hits.append(kind)
    return hits


def _workbook_text(data):
    """The XML parts of a spreadsheet, read in memory. Anything else inside makes it unchecked."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        parts = []
        for info in z.infolist():
            if not info.filename.endswith((".xml", ".rels")) or info.file_size > 4 * MAX_BYTES:
                return None, f"spreadsheet holds a part that cannot be checked ({info.filename})"
            parts.append(z.read(info).decode("utf-8", "replace"))
        text = re.sub(r"<[^>]+>", "\n", "\n".join(parts))
        return text, None
    except (zipfile.BadZipFile, OSError, RuntimeError):
        return None, "spreadsheet could not be read"


def _sqlite_text(path):
    """Every table's schema and values, read without changing the file."""
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
        lines = []
        for name, sql in con.execute("SELECT name, sql FROM sqlite_master WHERE sql IS NOT NULL"):
            lines.append(sql)
            if sql.upper().startswith("CREATE TABLE"):
                for row in con.execute(f'SELECT * FROM "{name}" LIMIT 100000'):
                    lines.append(" | ".join("" if v is None else str(v) for v in row))
        con.close()
        return "\n".join(lines), None
    except sqlite3.DatabaseError:
        return None, "database file could not be read"


def read_text(path):
    """Return (text, None) or (None, reason-not-checked)."""
    try:
        size = os.path.getsize(path)
        if size > MAX_BYTES:
            return None, f"larger than {MAX_BYTES // 1024} KiB"
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        return None, f"unreadable ({e.__class__.__name__})"
    if path.lower().endswith((".xlsx", ".xlsm")) and data[:4] == b"PK\x03\x04":
        return _workbook_text(data)
    if data[:16] == b"SQLite format 3\x00":
        return _sqlite_text(path)
    if b"\x00" in data[:8192]:
        return None, "binary"
    try:
        return data.decode("utf-8"), None
    except UnicodeDecodeError:
        try:
            return data.decode("cp1252"), None
        except UnicodeDecodeError:
            return None, "not readable as text"


def screen_paths(paths, names=False):
    result = {"findings": [], "not_checked": [], "files_checked": 0}
    for top in paths:
        top = os.path.abspath(top)
        if os.path.islink(top):
            result["not_checked"].append({"file": top, "reason": "link (not followed)"})
            continue
        if os.path.isfile(top):
            walk = [(os.path.dirname(top), [], [os.path.basename(top)])]
            base_for_rel = os.path.dirname(top)
        else:
            walk = os.walk(top, followlinks=False)
            base_for_rel = top
        for base, dirs, files in walk:
            dirs.sort()
            for d in list(dirs):
                full = os.path.join(base, d)
                rel = os.path.relpath(full, base_for_rel)
                if os.path.islink(full):
                    result["not_checked"].append({"file": rel, "reason": "link (not followed)"})
                    dirs.remove(d)
                elif names:
                    for kind in name_hits(d):
                        result["findings"].append({"file": rel, "line": 0, "column": 0, "kind": f"{kind} in a folder name"})
            for name in sorted(files):
                full = os.path.join(base, name)
                rel = os.path.relpath(full, base_for_rel)
                if names:
                    for kind in name_hits(name):
                        result["findings"].append({"file": rel, "line": 0, "column": 0, "kind": f"{kind} in a file name"})
                if os.path.islink(full) or not os.path.isfile(full):
                    result["not_checked"].append({"file": rel, "reason": "link or special file (not followed)"})
                    continue
                text, why = read_text(full)
                if text is None:
                    result["not_checked"].append({"file": rel, "reason": why})
                    continue
                result["files_checked"] += 1
                for ln, col, kind in screen_text(text):
                    result["findings"].append({"file": rel, "line": ln, "column": col, "kind": kind})
    return result


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args or "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0 if args or "--help" in argv else 2
    missing = [a for a in args if not os.path.lexists(a)]
    if missing:
        print(f"screen: cannot find {', '.join(missing)}", file=sys.stderr)
        return 2
    res = screen_paths(args, names="--names" in argv)
    if "--json" in argv:
        print(json.dumps(res, indent=1))
    else:
        for f in res["findings"]:
            where = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"FOUND       {where}  {f['kind']}")
        for n in res["not_checked"]:
            print(f"NOT CHECKED {n['file']}  {n['reason']}")
        print(f"{res['files_checked']} file(s) checked, {len(res['findings'])} finding(s), {len(res['not_checked'])} not checked")
    return 1 if res["findings"] or res["not_checked"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
