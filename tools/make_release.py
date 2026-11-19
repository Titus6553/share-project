#!/usr/bin/env python3
# tools/make_release.py
# Purpose: build dist/share-project-v<VERSION>.zip with the skill folder as its only root entry, or (--check) validate without writing.
# Non-goals: publishes nothing; never includes caches, tests, samples or anything outside share-project/.
"""Usage: python3 tools/make_release.py [--check]

--check validates: frontmatter has only name and description, name equals the folder name and
holds no vendor name, description is at most 200 characters; VERSION files agree; every file
the skill text names exists; the zip layout (one root folder, regular files, modes 644/755).
Without --check it also writes dist/share-project-v<VERSION>.zip. Exit 0 = ok, 1 = problems."""

import io
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = "share-project"
SKILL_DIR = os.path.join(ROOT, SKILL)
SKIP = {"__pycache__", ".DS_Store"}
STAMP = (2026, 1, 1, 0, 0, 0)


def files():
    out = []
    for base, dirs, names in os.walk(SKILL_DIR, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for n in sorted(names):
            if n in SKIP or n.endswith(".pyc"):
                continue
            full = os.path.join(base, n)
            out.append((full, os.path.relpath(full, ROOT).replace(os.sep, "/")))
    return out


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        fields[k.strip()] = v.strip().strip('"')
    return fields


def check():
    problems = []
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    if not os.path.isfile(skill_md):
        return ["share-project/SKILL.md is missing"]
    with open(skill_md) as f:
        text = f.read()
    fm = frontmatter(text)
    if fm is None:
        problems.append("SKILL.md has no frontmatter")
    else:
        if set(fm) != {"name", "description"}:
            problems.append(f"frontmatter must hold only name and description (has {sorted(fm)})")
        if fm.get("name") != SKILL:
            problems.append("frontmatter name must equal the folder name")
        if re.search(r"claude|anthropic", fm.get("name", ""), re.I):
            problems.append("the name may not contain a vendor name")
        if not 0 < len(fm.get("description", "")) <= 200:
            problems.append(f"description must be 1-200 characters (is {len(fm.get('description', ''))})")
    if len(text.splitlines()) >= 500:
        problems.append("SKILL.md must stay under 500 lines")
    with open(os.path.join(ROOT, "VERSION")) as f:
        version = f.read().strip()
    try:
        with open(os.path.join(SKILL_DIR, "VERSION")) as f:
            if f.read().strip() != version:
                problems.append("share-project/VERSION differs from VERSION")
    except OSError:
        problems.append("share-project/VERSION is missing")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        problems.append("VERSION must look like 1.2.3")
    named = set()
    for full, _ in files():
        if full.endswith(".md"):
            with open(full) as f:
                named |= set(re.findall(r"`((?:references|scripts|assets)/[A-Za-z0-9_./-]+)`", f.read()))
    for rel in sorted(named):
        if not os.path.exists(os.path.join(SKILL_DIR, rel)):
            problems.append(f"the skill text names {rel}, which does not exist")
    for full, rel in files():
        if os.path.islink(full):
            problems.append(f"link in the skill folder: {rel}")
    return problems, version


def build_zip(version):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        dirs = set()
        for full, rel in files():
            parts = rel.split("/")
            for i in range(1, len(parts)):
                d = "/".join(parts[:i]) + "/"
                if d not in dirs:
                    dirs.add(d)
                    info = zipfile.ZipInfo(d, STAMP)
                    info.external_attr = (0o040755 << 16) | 0x10
                    z.writestr(info, b"")
            info = zipfile.ZipInfo(rel, STAMP)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(full, "rb") as f:
                z.writestr(info, f.read())
    return buf.getvalue()


def check_layout(data):
    problems = []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for i in z.infolist():
            if i.filename.split("/")[0] != SKILL:
                problems.append(f"zip entry outside {SKILL}/: {i.filename}")
            mode = (i.external_attr >> 16) & 0o7777
            want = 0o755 if i.filename.endswith("/") else 0o644
            if mode != want:
                problems.append(f"zip entry mode {oct(mode)} for {i.filename}")
    return problems


def main(argv):
    result = check()
    if isinstance(result, list):
        problems, version = result, None
    else:
        problems, version = result
    data = build_zip(version) if version else b""
    if data:
        problems += check_layout(data)
    for p in problems:
        print(f"PROBLEM  {p}")
    if problems:
        return 1
    if "--check" in argv:
        print(f"release check passed for {SKILL} {version} ({len(files())} files)")
        return 0
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    out = os.path.join(ROOT, "dist", f"{SKILL}-v{version}.zip")
    with open(out, "wb") as f:
        f.write(data)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
