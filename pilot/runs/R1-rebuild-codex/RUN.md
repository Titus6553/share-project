# R1 — rebuild run: Claude-made pack (P1) rebuilt by Codex, told to use a different toolset

- **Date:** 2026-11-18 · **Minutes:** 3 · **Completed:** yes
- **Command:** as P2 (`codex exec … -s workspace-write`), run folder holding only the unzipped pack (extracted with path checks; regular files only).
- **Prompt:** the pack's own "Prompt for your assistant", plus: "I am not available to answer questions … do the say-back step as written text, then make sensible choices, state each, and carry on. Build in ./rebuilt/ … tell me the exact command … Also: use a different database or toolset from the original."
- **Say-back:** given before building: what it will build, what is missing (real data, mail credentials), its choices (no email, departments without deals omitted, rounded gross compared to exact thresholds), and the conflict between `project/calc.py` and the rules ("I'll follow the specification and count it once").
- **What it built:** a Ruby program with exact rational arithmetic (no Python, no spreadsheet library), plus 14 tests of its own.
- **Questions asked:** none (headless; choices stated instead).

## Checks run by a person (not taken from the agent's report)

The rebuilt program was run by hand under `sandbox-exec` (no network; writes confined to a check folder):

| Input | Result |
|---|---|
| The pack's stand-in workbook | 4 rows; all five pack checks match exactly (Jan New 55,001 / 50,500 / 4,500 / 8.2 / Watch; Jan Parts Behind; Feb Service 831 / 380 / 451 / 54.2 / Watch; Feb Used 35,000 / 30,200 / 4,800 / 13.7 / On track; row set and order) |
| The original sample workbook (never in the pack) | all 12 month-department rows equal `tools/finance_reference.py` (the owner's intended rules), including March Used 7,503 On track and the rounding trap Jan Used gross 1,833 |

**Verdict:** pass. The planted defect was not copied.

## Interventions

None.
