#!/usr/bin/env python3
# share-project/scripts/inventory.py
# Purpose: list every file in a project folder and sort it into code-and-text, data file, secret or left out, with the reason.
# Non-goals: never prints file contents or key values; never follows links; never writes anywhere.
"""Inventory a project folder without reading secrets.

Usage: python3 inventory.py <project-folder> [--json]

Kinds:
  code      code and text: copied into the pack, then screened
  data      spreadsheets, CSV, local database files, exports: never copied; replaced by a stand-in
  secret    keys and credential files: never copied and never opened (variable names only)
  left-out  dependency folders, build output, version history, links, archives, binary or large files
Exit 0 on success, 2 on a usage error. Values in keys files are never printed."""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from screen import MAX_BYTES, name_hits  # noqa: E402

SKIP_DIRS = {
    ".git": "version history", ".hg": "version history", ".svn": "version history",
    "node_modules": "dependency folder", "venv": "dependency folder", ".venv": "dependency folder",
    "env": "dependency folder", "site-packages": "dependency folder", "vendor": "dependency folder",
    "bower_components": "dependency folder", ".bundle": "dependency folder",
    "__pycache__": "build output", "dist": "build output", "build": "build output", ".next": "build output",
    ".nuxt": "build output", "out": "build output", "target": "build output", ".parcel-cache": "build output",
    ".cache": "cache", ".pytest_cache": "cache", ".mypy_cache": "cache", ".ruff_cache": "cache",
    "coverage": "test output", ".idea": "editor settings", ".vscode": "editor settings",
    ".vercel": "hosting settings", ".netlify": "hosting settings", ".firebase": "hosting settings",
}
SKIP_FILES = {".DS_Store": "system file", "Thumbs.db": "system file", "desktop.ini": "system file"}

SECRET_NAMES = re.compile(
    r"(^\.env($|\.(?!example$|sample$|template$|dist$).+)|\.env$|^\.envrc$|\.(pem|key|p12|pfx|jks|keystore|kdbx|ppk|asc|gpg)$|"
    r"^id_(rsa|dsa|ecdsa|ed25519)|^\.netrc$|^\.npmrc$|^\.pypirc$|^\.pgpass$|^\.git-credentials$|"
    r"credentials?(\.[a-z]+)?$|service[-_]?account.*\.json$|^secrets?\.(json|ya?ml|toml|ini|txt)$|"
    r"^client_secret.*\.json$|token\.(json|pickle)$)", re.I)
DATA_EXT = {".csv", ".tsv", ".xlsx", ".xlsm", ".xls", ".xlsb", ".ods", ".numbers", ".db", ".sqlite",
            ".sqlite3", ".db3", ".mdb", ".accdb", ".parquet", ".feather", ".dbf", ".sav", ".dta",
            ".bak", ".dump", ".ndjson", ".jsonl"}
ARCHIVE_EXT = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar", ".jar", ".war", ".whl", ".egg"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".tif", ".tiff", ".heic", ".pdf",
             ".mp4", ".mov", ".mp3", ".wav", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".psd", ".ai"}
DATA_DIR_HINT = re.compile(r"(^|/)(data|exports?|backups?|dumps?|uploads|fixtures|seeds?)(/|$)", re.I)
ENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_.-]*)\s*[=:]")


def env_names(path):
    """Variable names in a keys file. Values are read only as far as the '=' and never kept."""
    names = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = ENV_LINE.match(line)
                if m and not line.lstrip().startswith("#"):
                    names.append(m.group(1))
    except OSError:
        return None
    return names


def classify(rel, full):
    name = os.path.basename(rel)
    ext = os.path.splitext(name)[1].lower()
    if name in SKIP_FILES:
        return "left-out", SKIP_FILES[name]
    if SECRET_NAMES.search(name):
        return "secret", "keys or credential file"
    hits = name_hits(name)
    if hits:
        return "left-out", f"the file name itself looks like a secret value ({hits[0]})"
    if ext in DATA_EXT or name.lower().endswith((".sql.gz", ".csv.gz")):
        return "data", "data file"
    if ext == ".sql":
        try:
            with open(full, "rb") as f:
                head = f.read(65536).upper()
            if b"INSERT INTO" in head or b"COPY " in head:
                return "data", "database export with rows"
        except OSError:
            return "left-out", "unreadable"
    if ext in ARCHIVE_EXT:
        return "left-out", "archive (cannot be checked inside)"
    if ext in MEDIA_EXT:
        return "left-out", "image, document or media file (cannot be checked for what it shows)"
    try:
        size = os.path.getsize(full)
    except OSError:
        return "left-out", "unreadable"
    if ext == ".json" and (DATA_DIR_HINT.search(rel) or size > 256 * 1024):
        return "data", "JSON data file"
    if size > MAX_BYTES:
        return "left-out", "larger than 1 MiB (too large to check)"
    try:
        with open(full, "rb") as f:
            if b"\x00" in f.read(8192):
                return "left-out", "binary file"
    except OSError:
        return "left-out", "unreadable"
    return "code", "code or text"


def inventory(project):
    project = os.path.abspath(project)
    files, keys = [], {}
    for base, dirs, names in os.walk(project, followlinks=False):
        dirs.sort()
        for d in list(dirs):
            full = os.path.join(base, d)
            rel = os.path.relpath(full, project)
            if os.path.islink(full):
                files.append({"path": rel, "kind": "left-out", "reason": "link (not followed)"})
                dirs.remove(d)
            elif d in SKIP_DIRS:
                files.append({"path": rel + "/", "kind": "left-out", "reason": SKIP_DIRS[d]})
                dirs.remove(d)
            elif name_hits(d):
                files.append({"path": rel + "/", "kind": "left-out", "reason": "the folder name itself looks like a secret value"})
                dirs.remove(d)
        for n in sorted(names):
            full = os.path.join(base, n)
            rel = os.path.relpath(full, project)
            if os.path.islink(full):
                files.append({"path": rel, "kind": "left-out", "reason": "link (not followed)"})
                continue
            if not os.path.isfile(full):
                files.append({"path": rel, "kind": "left-out", "reason": "special file"})
                continue
            kind, reason = classify(rel, full)
            entry = {"path": rel, "kind": kind, "reason": reason, "bytes": os.path.getsize(full)}
            files.append(entry)
            if kind == "secret":
                found = env_names(full) if not re.search(r"\.(pem|key|p12|pfx|jks|keystore|kdbx|ppk|gpg)$", n, re.I) else []
                keys[rel] = found if found is not None else []
    counts = {}
    for f in files:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    return {"project": project, "counts": counts, "files": files, "key_names": keys}


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("inventory: give one project folder", file=sys.stderr)
        return 2
    res = inventory(args[0])
    if "--json" in argv:
        print(json.dumps(res, indent=1))
        return 0
    for f in res["files"]:
        print(f"{f['kind']:<9} {f['path']}  ({f['reason']})")
    for path, names in res["key_names"].items():
        print(f"keys file {path}: {', '.join(names) if names else '(no variable names read)'}")
    print("counts: " + ", ".join(f"{k} {v}" for k, v in sorted(res["counts"].items())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
