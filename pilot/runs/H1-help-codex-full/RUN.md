# H1 — help run: Claude-made help pack (P1), full evidence, helped by Codex

- **Date:** 2026-11-18 · **Minutes:** 2 · **Completed:** yes — reply note written
- **Command:** as P2 (`codex exec … -s workspace-write`); run folder held only the unzipped pack.
- **Material:** P1's help pack with the packer's own diagnosis removed by hand (the "packer's observation" line, the hand-worked before/after figures, and "including its bug" in `COVERAGE.md`), so the helper had to find the cause. `project/calc.py` kept.
- **Prompt:** the pack's own prompt plus: "I am not available … do the say-back … write the reply note to ./REPLY.md … If the pack does not hold enough to answer, say exactly what is missing instead of guessing."

## Result

- Say-back first, as asked.
- **Diagnosis correct:** `deal_cost` adds recon twice for Used; one-line fix (`return cost`); before/after figures on the stand-in; checks; a reconciliation step on the owner's real workbook ("sum the three March Used recon charges").
- It ran the pack's `monthly_figures` on the stand-in values in its own sandbox: the helper side may run code; the sharing side never does.
- Flagged its own uncertainty: whether the DMS `cost` already includes recon.
- Reply note: canary search 0 hits; placeholders kept.

**Verdict:** pass.
