# The rebuild pack

Load this when the owner chose "so someone can rebuild it". The promise to the owner is **a working equivalent of the main flows**, not an identical copy.

## REBUILD.md

Use `assets/templates/rebuild-brief.md`. Headings: `What it does` (with `Observed behaviour`, `Intended behaviour (confirmed by the owner)`, `Known problems not to copy`, `Unknowns`), `Exact rules`, `Checks that define done`, `Free choices`, `About project/`, `Build order`.

**Exact rules.** For each main flow the owner named, write down every formula, threshold, default, unit, rounding rule and date or grouping rule a rebuild must get exactly right, whether it lives in code, configuration or the input workbook. Give the file in `project/` each comes from. Mark each one "read from code", "confirmed by owner" or "inferred". Boundaries matter: say whether a threshold is "at or above" or "above". If a rule cannot be carried safely or explained, mark that flow incomplete and set the outcome to `incomplete: missing <what>`.

**Checks that define done.** Three to six checks the owner agrees to, each with exact invented inputs, the exact expected output and how the expected value was worked out.
- Work the finance rules out yourself from the owner's stated rules. Do not take the original code's output as proof of itself.
- Prefer checks whose inputs are rows of the stand-in data file, so one run of the rebuild against the stand-in shows every check. Write those invented rows into the stand-in after `scripts/standin.py` makes it, then run `python3 scripts/standin.py <stand-in> --record-only --pack <pack>` so its record matches (running `standin.py` again without `--record-only` would regenerate the file and lose the rows). Or describe the rows exactly in the check.
- Cover each boundary of each threshold (just below, exactly at, just above), each rounding rule with a value that rounds differently if summed in another order, and each date rule with a row that falls on the other side of it.
- Where the original's result differs from the intended one because of a known problem, give both and say the rebuild must match the intended one.
- Every check the sender did not run is marked `not run`. The share actions never run the project, so that is normally all of them.

**Known problems.** If reading the code shows a defect, write it under "Known problems not to copy" and tell the owner in plain words. The owner decides whether it is a defect; until then mark it "found while reading; not confirmed by the owner".

**Free choices.** Say the receiver may choose any database, language and tools; list what is required (the behaviour and the exact rules) apart from what is free (storage, framework, layout details, hosting).

**About project/.** "How the original did it; use it for exact formulas and layout; you do not have to copy it."

**Build order.** Short steps, each with a check.

## What the pilot showed

A Claude-made pack was rebuilt by Codex in Ruby, and a Codex-made pack by Claude in Python with no spreadsheet library. Both rebuilds passed every check when a person ran them, and both reproduced the owner's intended figures on a workbook they never saw. The checks with exact inputs and boundary cases were what made that possible (`pilot/RESULTS.md` in the skill's repository).
