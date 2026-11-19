#!/usr/bin/env python3
# share-project/scripts/build_zip.py
# Purpose: build the zip that is sent, only from a pack folder that passes check_pack.py, and verify the exact zip after writing.
# Non-goals: never adds anything the check did not see; never follows links; never runs project code.
"""Zip a checked pack.

Usage: python3 build_zip.py <pack-folder> <out.zip> [--message <message-file>]

Refuses (exit 1) unless check_pack.py passes, and unless the optional delivery message
screens clean. Writes regular files only, under one top folder named after the pack folder,
with relative paths, fresh timestamps, mode 644 and no archive comment. Then re-opens the zip
and confirms every entry is byte-identical to a checked file and nothing else is inside.
Exit 0 = zip written and verified; 1 = refused or verification failed; 2 = usage error."""

import hashlib
import os
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_pack import check  # noqa: E402
from screen import name_hits, screen_paths  # noqa: E402


def build(pack, out, message=None):
    pack = os.path.abspath(pack)
    out = os.path.abspath(out)
    if out.startswith(pack + os.sep):
        return ["the zip must be written outside the pack folder"]
    res = check(pack)
    if res["problems"]:
        return [f"check_pack: {p['kind']}: {p['where']}" for p in res["problems"]]
    if message:
        m = screen_paths([message])
        if m["findings"] or m["not_checked"]:
            return ["the delivery message has screening findings; rewrite it without keys or personal details"]
    top = os.path.basename(pack.rstrip(os.sep))
    # The pack folder's own name goes into every entry, and the zip's name travels with it:
    # neither may itself be a secret value or an id number.
    for label, name in (("pack folder", top), ("zip", os.path.basename(out))):
        if name_hits(name):
            return [f"the {label} name looks like a key or id number; rename it"]
    expected = {}
    for base, dirs, files in os.walk(pack, followlinks=False):
        dirs.sort()
        for n in sorted(files):
            full = os.path.join(base, n)
            if os.path.islink(full) or not os.path.isfile(full):
                return [f"not a regular file: {os.path.relpath(full, pack)}"]
            rel = os.path.relpath(full, pack).replace(os.sep, "/")
            with open(full, "rb") as f:
                expected[f"{top}/{rel}"] = f.read()
    now = time.localtime()[:6]
    tmp = out + ".partial"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in expected.items():
            info = zipfile.ZipInfo(name, now)
            info.external_attr = (0o100644 << 16)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    errors = []
    with zipfile.ZipFile(tmp) as z:
        if z.comment:
            errors.append("archive comment present")
        names = z.namelist()
        if sorted(names) != sorted(expected):
            errors.append("zip entries differ from the checked files")
        for info in z.infolist():
            n = info.filename
            if n.startswith("/") or ".." in n.split("/") or "\\" in n:
                errors.append(f"unsafe entry path: {n}")
            if name_hits(n):
                errors.append(f"entry name looks like a key or id number: {n}")
            if (info.external_attr >> 16) & 0o170000 != 0o100000:
                errors.append(f"not a regular file entry: {n}")
            if info.extra:
                errors.append(f"extra metadata on entry: {n}")
            if hashlib.sha256(z.read(info)).digest() != hashlib.sha256(expected.get(n, b"")).digest():
                errors.append(f"entry differs from the checked file: {n}")
    if errors:
        os.remove(tmp)
        return errors
    os.replace(tmp, out)
    return []


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    message = None
    args = list(argv)
    if "--message" in args:
        i = args.index("--message")
        if i + 1 >= len(args):
            print("build_zip: --message needs a file", file=sys.stderr)
            return 2
        message = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2 or not os.path.isdir(args[0]):
        print("build_zip: give a pack folder and the zip path", file=sys.stderr)
        return 2
    errors = build(args[0], args[1], message)
    if errors:
        for e in errors:
            print(f"REFUSED  {e}")
        return 1
    print(f"zip written and verified: {os.path.abspath(args[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
