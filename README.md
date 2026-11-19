# share-project

A skill for people who build small tools with an AI assistant (Claude, ChatGPT or Codex) and want to give a project to someone else safely.

It is written for dealership owners and managers who are not engineers. Their project folders hold customer data and keys; this skill makes a cleaned copy that can travel by email or a shared drive.

## What it does

Ask your assistant to **share this project**. It offers two ways:

- **Share so someone can rebuild it.** You get a zip another person's assistant can use to build its own working version of the main flows, with its own choice of database and tools. The zip carries the rules that must come out exactly right (formulas, thresholds, rounding, date grouping) and a few checks that say when the rebuild is done.
- **Share so someone can help.** You describe a problem; you get a zip someone else's assistant can read to find what is wrong and send back a reply note your own assistant can apply.

Both make the same cleaned copy:

- keys and passwords are left out and listed as things the receiver must supply;
- spreadsheets, CSV files and database files are never copied; each is replaced by a stand-in with the same sheet and column names and a few invented rows;
- version history, dependency folders and anything that cannot be checked are left out;
- the copy is screened for keys and personal data, you see what is in it before the zip is made, and the exact zip is checked again before you send it.

The skill says what it checked, what it could not check and what it left out. It never promises that a pack is completely safe.

Two more actions: **check for an update** (downloads and shows a newer version; installs nothing by itself) and **send feedback** (prepares a short report from a fixed list of choices for you to approve).

## Where to start

- Install: `docs/install/` has one page per app. Which apps have been tried, and how: `docs/install/ROUTES.md`.
- The skill itself: `share-project/SKILL.md`.
- What a pack contains: `share-project/references/pack-format.md`.
- How it was tested: `pilot/RESULTS.md`.

## For maintainers

- Tests: `python3 -m unittest discover -s tests -v`
- Release zip: `python3 tools/make_release.py` writes `dist/share-project-v<VERSION>.zip`; `--check` validates without writing.
- Builder choices are recorded in `DECISIONS.md`, one line each.
- Every value under `samples/` is invented. The planted test values are listed in `samples/CANARIES.md`.
