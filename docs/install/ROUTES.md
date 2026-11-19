# Routes

Every route the skill is meant to work on, per capability, with one of three labels: **tested by us** (with the date), **reported working by a user** (through the feedback action), or **untested — try it and tell us**. ChatGPT-app and Codex results are kept apart. A route where private content is found in a pack is withdrawn until fixed.

| Route | Installs | Reads a local folder in place | Runs the helpers | Produces a zip | Notes |
|---|---|---|---|---|---|
| Claude desktop app, chat | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | A plain chat sees only uploaded files; the skill should stop at its first step. |
| Claude desktop app, Cowork | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | |
| Claude desktop app, Code tab | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | |
| Claude Code, command line (Mac) | tested by us, 2026-11-18/19 (project `.claude/skills` folder) | tested by us, 2026-11-18/19 | tested by us, 2026-11-18/19 | tested by us, 2026-11-18/19 | Headless runs, both actions, both samples (`pilot/RESULTS.md` "End to end"). Personal install (`~/.claude/skills`) and interactive use untested. |
| Claude account skill synced into Claude Code | untested — try it and tell us | — | — | — | Documentation disagrees on whether skills sync. |
| Codex, command line (Mac) | tested by us, 2026-11-18/19 (project `.agents/skills` folder) | tested by us, 2026-11-18/19 | tested by us, 2026-11-18/19 | tested by us, 2026-11-18/19 | Headless runs, both actions, both samples (`pilot/RESULTS.md` "End to end"). Personal install (`~/.agents/skills`) and interactive use untested. |
| Codex app | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | |
| ChatGPT app | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | Documented for Business, Enterprise, Healthcare and Edu workspaces only. |
| Any route on Windows | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | untested — try it and tell us | Helpers are written for both; not run on Windows. |
