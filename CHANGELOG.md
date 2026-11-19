# Changelog

## 0.1.2 — 2026-11-19

- `QUICK-GUIDE.pdf` replaced by a one-page plain version: a heading, a sentence and the exact line to type for setup, share, update, a received zip and feedback. Its source is now `docs/guide/quick-guide.html` (built with `weasyprint`).

## 0.1.1 — 2026-11-19

- The zip can be handed straight to an assistant. `INSTALL.md` tells the assistant what to do in each case: a first-time install into the personal skills folder (with the owner's yes), a copy already installed (same, older or newer), and a chat that cannot see the computer.
- `QUICK-GUIDE.pdf`, a two-page guide for the owner, travels in the zip. Its source was `docs/guide/quick-guide.md` (replaced in 0.1.2).

## 0.1.0 — 2026-11-19

- First version: two share actions (a rebuild pack and a help pack), an update action that downloads and shows a new release without installing it, and a feedback action that prepares an allowlisted report for the owner to approve.
- Helpers in Python 3 standard library only.
- Proven by a headless pilot on two invented sample projects, then end to end with the skill installed in Claude Code and Codex on the command line (see `pilot/RESULTS.md`). Desktop-app installs are untested (see `docs/install/ROUTES.md`).
