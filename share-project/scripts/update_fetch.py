#!/usr/bin/env python3
# share-project/scripts/update_fetch.py
# Purpose: download a newer release of this skill into a staging folder outside any project and show what would change.
# Non-goals: installs nothing, replaces nothing, sends no project file; the publisher is NOT authenticated in this release.
"""Check for and stage an update of this skill. Nothing is installed.

Usage:
  python3 update_fetch.py --check                  print the newest published release number
  python3 update_fetch.py --fetch [--version X.Y.Z] [--staging <folder>]
  python3 update_fetch.py --from-file <zip> [--staging <folder>]   (a zip the owner already has)

The release comes from the fixed repository below (GitHub releases, asset
share-project-v<version>.zip). The zip is checked before anything is unpacked: one top
folder named share-project, relative paths only, no links, no nested archives, size limits.
It is unpacked into a new staging folder (default: a new folder in the system temporary
area), never into a project, and the exact zip is saved there as share-project-release.zip
for an app that installs skills from a zip. The output lists added, removed and changed files against the
installed copy, the release number inside the zip, and the zip's SHA-256.
Exit 0 = staged; 1 = refused (reason printed); 2 = usage or network error."""

import hashlib
import io
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile

REPOSITORY = "Titus6553/share-project"   # fixed at release; see references/update-and-feedback.md
SKILL = "share-project"
MAX_ZIP = 10 * 1024 * 1024
MAX_FILES = 200
MAX_UNPACKED = 20 * 1024 * 1024
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def installed_version():
    try:
        with open(os.path.join(HERE, "VERSION")) as f:
            return f.read().strip()
    except OSError:
        return "unknown"


def http_get(url, limit):
    req = urllib.request.Request(url, headers={"User-Agent": f"{SKILL}-update/{installed_version()}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read(limit + 1)
    if len(data) > limit:
        raise ValueError("download larger than allowed")
    return data


def latest():
    data = http_get(f"https://api.github.com/repos/{REPOSITORY}/releases/latest", 1024 * 1024)
    tag = json.loads(data).get("tag_name", "")
    if not re.match(r"^v?\d+\.\d+\.\d+$", tag):
        raise ValueError("the newest release has an unexpected name")
    return tag.lstrip("v")


def validate(data):
    """Return (zipfile, problems) for a candidate release zip held in memory."""
    problems = []
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return None, ["not a zip file"]
    infos = z.infolist()
    if len(infos) > MAX_FILES:
        problems.append("too many files")
    if sum(i.file_size for i in infos) > MAX_UNPACKED:
        problems.append("unpacks larger than allowed")
    for i in infos:
        n = i.filename
        parts = n.split("/")
        if n.startswith("/") or "\\" in n or ".." in parts or re.match(r"^[A-Za-z]:", n):
            problems.append(f"unsafe path: {n!r}")
        elif parts[0] != SKILL:
            problems.append(f"entry outside the {SKILL}/ folder: {n!r}")
        mode = (i.external_attr >> 16) & 0o170000
        if mode == 0o120000:
            problems.append(f"link inside the zip: {n!r}")
        if n.lower().endswith((".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".jar")):
            problems.append(f"nested archive: {n!r}")
    if f"{SKILL}/SKILL.md" not in z.namelist():
        problems.append("no SKILL.md in the release")
    return z, problems


def inside(path, folder):
    path, folder = os.path.realpath(path), os.path.realpath(folder)
    return path == folder or path.startswith(folder + os.sep)


def stage(data, staging):
    z, problems = validate(data)
    if problems:
        return None, problems
    if os.path.exists(staging) and os.listdir(staging):
        return None, ["the staging folder is not empty"]
    if inside(staging, os.getcwd()) or inside(staging, HERE):
        return None, ["the staging folder must be outside the current project and the installed skill"]
    os.makedirs(staging, exist_ok=True)
    for i in z.infolist():
        if i.filename.endswith("/"):
            continue
        out = os.path.join(staging, *i.filename.split("/"))
        if not inside(out, staging):
            return None, [f"unsafe path: {i.filename!r}"]
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(z.read(i))
    # Keep the exact checked bytes beside the unpacked folder: a desktop app installs from a zip.
    with open(os.path.join(staging, f"{SKILL}-release.zip"), "wb") as f:
        f.write(data)
    return os.path.join(staging, SKILL), []


def tree(root):
    out = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for n in files:
            full = os.path.join(base, n)
            with open(full, "rb") as f:
                out[os.path.relpath(full, root).replace(os.sep, "/")] = hashlib.sha256(f.read()).hexdigest()
    return out


def compare(new_root):
    old, new = tree(HERE), tree(new_root)
    return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new)),
            "changed": sorted(k for k in set(old) & set(new) if old[k] != new[k])}


def main(argv):
    if not argv or "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0

    def opt(name):
        if name in argv:
            i = argv.index(name)
            return argv[i + 1] if i + 1 < len(argv) else ""
        return None

    try:
        if "--check" in argv:
            print(f"installed: {installed_version()}  newest published: {latest()}")
            return 0
        staging = opt("--staging") or tempfile.mkdtemp(prefix="share-project-update-")
        if opt("--from-file"):
            with open(opt("--from-file"), "rb") as f:
                data = f.read(MAX_ZIP + 1)
            if len(data) > MAX_ZIP:
                print("REFUSED  the zip is larger than allowed")
                return 1
            source = os.path.abspath(opt("--from-file"))
        elif "--fetch" in argv:
            version = opt("--version") or latest()
            if not re.match(r"^\d+\.\d+\.\d+$", version):
                print("update: --version must look like 1.2.3", file=sys.stderr)
                return 2
            source = f"https://github.com/{REPOSITORY}/releases/download/v{version}/{SKILL}-v{version}.zip"
            data = http_get(source, MAX_ZIP)
        else:
            print("update: choose --check, --fetch or --from-file", file=sys.stderr)
            return 2
    except (urllib.error.URLError, ValueError, OSError) as e:
        print(f"update: could not get the release ({e.__class__.__name__}: {e})", file=sys.stderr)
        return 2
    new_root, problems = stage(data, staging)
    if problems:
        for p in problems:
            print(f"REFUSED  {p}")
        return 1
    try:
        with open(os.path.join(new_root, "VERSION")) as f:
            new_version = f.read().strip()
    except OSError:
        new_version = "unknown"
    diff = compare(new_root)
    print(f"Staged, not installed: {new_root}")
    print(f"Zip saved for an app's own install (same bytes as the fingerprint below): "
          f"{os.path.join(os.path.dirname(new_root), SKILL + '-release.zip')}")
    print(f"From: {source}")
    print(f"Release inside the zip: {new_version} (installed: {installed_version()})")
    print(f"SHA-256 of the downloaded zip: {hashlib.sha256(data).hexdigest()}")
    print("Publisher check: NOT DONE. This release of the skill cannot prove who published the zip;")
    print("a fingerprint from the same download does not prove it either.")
    for k in ("added", "removed", "changed"):
        print(f"{k}: {', '.join(diff[k]) if diff[k] else 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
