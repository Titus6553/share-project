# tools/stage_sample.py
# Purpose: copy a sample project to a working folder and add the canaries git cannot hold
#          (a version history with a removed secret, a link pointing outside the project, an oversized code file).
# Non-goals: never touches the committed samples; never runs sample code.
"""Usage: python3 tools/stage_sample.py <sample-name> <dest-dir>

Writes <dest-dir>/<sample-name>/ (the project) and <dest-dir>/OUTSIDE-SECRET-<sample>.txt
(the target of the escaping link). Refuses an existing project folder."""

import os
import shutil
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")

EXTRAS = {
    "finance-dashboard": {
        "history_file": "settings_old.py",
        "history_text": 'OLD_FEED_KEY = "fdk_live_9Yb3Mr6Ue2Wf5Ka7Hq"\n',
        "outside_text": "outside_secret_Lm5Q8r2Z7x4P9k1Wfd\n",
        "big_file": "static/vendor.bundle.js",
        "big_tail": 'window.__cfg={apiKey:"bnd_K4p9X2m7Q1z8R5v3W6fd"};\n',
    },
    "recon-webapp": {
        "history_file": "old_secrets.json",
        "history_text": '{"sso_client_secret": "sso_old_Tc4Vn7Kp2Zm9Lq5Xrw"}\n',
        "outside_text": "outside_secret_Rp3W8n6Q2v9Z4k7Hrw\n",
        "big_file": "static/vendor.bundle.js",
        "big_tail": 'window.__cfg={apiKey:"bnd_Z8q2V6m4R1x9K3p7Nrw"};\n',
    },
}


def git(cwd, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_NOSYSTEM": "1", "HOME": cwd,
           "GIT_AUTHOR_NAME": "Owner", "GIT_AUTHOR_EMAIL": "owner@example.org",
           "GIT_COMMITTER_NAME": "Owner", "GIT_COMMITTER_EMAIL": "owner@example.org",
           "GIT_AUTHOR_DATE": "2026-01-05T09:00:00", "GIT_COMMITTER_DATE": "2026-01-05T09:00:00"}
    subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True)


def stage(name, dest):
    if name not in EXTRAS:
        sys.exit(f"unknown sample {name!r}; choose one of {sorted(EXTRAS)}")
    x = EXTRAS[name]
    project = os.path.join(dest, name)
    if os.path.exists(project):
        sys.exit(f"refusing: {project} already exists")
    os.makedirs(dest, exist_ok=True)
    shutil.copytree(os.path.join(ROOT, name), project, symlinks=True)
    git(project, "init", "-q", "-b", "main")
    with open(os.path.join(project, x["history_file"]), "w") as f:
        f.write(x["history_text"])
    git(project, "add", x["history_file"])
    git(project, "commit", "-q", "-m", "first version")
    os.remove(os.path.join(project, x["history_file"]))
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "move keys out of code")
    outside = os.path.join(dest, f"OUTSIDE-SECRET-{name}.txt")
    with open(outside, "w") as f:
        f.write(x["outside_text"])
    os.symlink(os.path.join("..", os.path.basename(outside)), os.path.join(project, "shared-settings.txt"))
    big = os.path.join(project, x["big_file"])
    os.makedirs(os.path.dirname(big), exist_ok=True)
    with open(big, "w") as f:
        line = "/* chart library build */ function c(a,b){return a+b}\n"
        f.write(line * (1_200_000 // len(line) + 1))
        f.write(x["big_tail"])
    return project


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(stage(sys.argv[1], os.path.abspath(sys.argv[2])))
