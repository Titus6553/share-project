# B1 — baseline, Claude receiver, a real pack from the retired skill

- **Date:** 2026-11-18 · **Minutes:** 1 · **Completed:** yes (read only; no build asked)
- **Command:** `tools/pilot_session.sh claude <run> <prompt> 900 read-only` with `EXTRA_DIR=<the real pack>`: `claude -p --safe-mode --model opus --effort medium --no-session-persistence --permission-mode acceptEdits --permission-prompts none --tools Read,Glob,Grep --add-dir <pack>`, prompt on stdin. Model reported: Claude Opus 5.5.
- **Isolation:** new empty working folder; the pack was read in place (not copied) through `--add-dir`. `--safe-mode` turned off CLAUDE.md files, skills, hooks, plugins and MCP servers; read-only tools only. **Limits:** same Mac and same signed-in account; the Read tool is not confined to the added folder.
- **Input:** the real 11-file pack made by the retired skill on 2026-10-14 (a reconditioning tracker). Its contents are not reproduced here; it is real business material and stays in the brainstorm record.
- **Prompt:** "You have been given this folder: <path>. Read it and tell me what you would build, what you would need from me, and what is unclear. Do not build yet."

## What it did

Read all nine files and proposed a from-scratch rebuild of the same stack and layout the pack described ("laid out exactly as the architecture page describes").

## What it asked and assumed

- Asked where to build.
- Asked for sign-on provider details and which identity attribute holds the user's email.
- Missing behaviour: when an approval flag is set and who approves; roles versus the allow-list; when a car leaves the board; where repair-order lines come from; how vehicle fields are edited; whether the admin page is real.
- Rules not pinned down: what "elapsed days" means and the **colour thresholds** for card age; time zone for working days; whether a drag may skip stages.
- Contradictions between pages: two different language versions; a dependency said to be missing that is listed; a migration statement the chosen database does not support; a setting named in one page and not the other; two possible end points for a turnaround measure.
- No design assets, so the look would be written from scratch.

## Interventions

None.
