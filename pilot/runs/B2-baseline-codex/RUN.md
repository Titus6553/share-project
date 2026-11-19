# B2 — baseline, Codex receiver, a real pack from the retired skill

- **Date:** 2026-11-18 · **Minutes:** about 2 · **Completed:** yes (read only; no build asked)
- **Command:** `tools/pilot_session.sh codex <run> <prompt> 900 read-only`: `codex exec --ignore-user-config --ignore-rules -m gpt-6-astra -c model_reasoning_effort="medium" -s read-only --skip-git-repo-check --ephemeral -C <empty run folder> -o <meta>/last.txt --json`.
- **Isolation:** new empty working folder; the pack was read in place by absolute path under the read-only sandbox. `--ignore-user-config` skipped the user's `config.toml` (MCP servers, model defaults). **Limits:** the user-level `AGENTS.md` (1.2 KB, about search boundaries) and the user's installed skills still load; same Mac and account; the read-only sandbox reads anywhere. The run's exit line was lost because the launcher script was edited while the run was in flight (fixed; not repeated).
- **Input:** the same real pack as B1, not reproduced here.
- **Prompt:** as B1.

## What it did

Read all nine files; called the pack "a rebuild specification with setup assets, not a runnable application"; proposed the same stack as the pack.

## What it asked and assumed

- Asked for the target location and whether the app is for one named dealership or reusable (it read the dealership's name out of the pack).
- Asked for screenshots or branding "if matching the original design matters".
- Production needs: hosting, domain, backups, sign-on metadata, user ids, who approves.
- Whether to start empty or import data; asked for "a representative sanitized sample".
- Unclear: completion semantics (two end stages), approval trigger and authority, permissions per role, where repair-order lines come from, time zone and whether delays pause the clock, stage skipping, duplicate VINs, deletion, renamed settings, admin scope.
- Same two page-to-page contradictions as B1.

## Interventions

None.
