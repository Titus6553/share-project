# R2 — rebuild run: Codex-made pack (P2) rebuilt by Claude

- **Date:** 2026-11-18 · **Minutes:** 4 (35 turns) · **Completed:** yes
- **Command:** as P1 (`claude -p --safe-mode … sandbox`), run folder holding only the unzipped pack.
- **Prompt:** the pack's own prompt plus the same headless note as R1 (no toolset change asked).
- **Say-back:** given; choices stated (Used recon once; non-Used recon ignored with a warning and an option to include it; rounded gross for status; blank margin at zero revenue; later duplicate target wins).
- **What it built:** Python standard library only (no spreadsheet library was installed), with its own workbook reader and 17 tests.
- **Questions asked:** none (headless).

## Checks run by a person

Run by hand under `sandbox-exec` with Python 3.14:

| Input | Result |
|---|---|
| The pack's stand-in workbook (check 5, and check 1's March Used rows) | 4 March rows; New 10,000 / 8,000 / 2,000 / 20.0 / On track; Parts, Service as stated; Used 32,000 / 26,500 / 5,500 / 17.2 / Watch — match |
| Check 2 (thresholds), check 3 (end-of-group rounding), check 4 (rounded gross vs target), each as a workbook built from the pack's stated inputs | 2000 On track, 1900 Watch, 1899 Behind; Parts 21 / 10 / 11 / 51.2; Service 2,000 / 1,000 / 1,000 / 50.0 On track — match |
| The original sample workbook (never in the pack) | all 12 rows equal the intended reference |

**Verdict:** pass. The planted defect was not copied.

## Problem seen

It rejects date cells formatted as dates: dates must be text, because the stand-in it was given stored dates as text. A real Excel export stores dates as date-formatted numbers, so a rebuild tuned to the stand-in could fail on the owner-side data. Stand-ins must keep the original's cell types.

## Interventions

None. The first run of the person-side check used the system's older Python (3.9) and failed on syntax; rerun with Python 3.14, as the rebuild's README states.
