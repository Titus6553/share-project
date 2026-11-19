#!/bin/bash
# tools/pilot_session.sh
# Purpose: run one headless pilot session (claude or codex) in a prepared run folder, with the isolation the pilot records.
# Non-goals: prepares nothing and inspects nothing; the run folder must already hold only the material under test.
# Usage: tools/pilot_session.sh <claude|codex> <run-dir> <prompt-file> <timeout-seconds> [read-only|write]
# SKILL_MODE=1 (claude only) swaps --safe-mode for --setting-sources project so a skill in <run>/.claude/skills loads.
# EXTRA_DIR=<path> lets a claude session read one more folder in place (codex read-only already reads in place).
# Writes <run-dir>-meta/{command.txt,transcript.*,last.txt,exit.txt}; the meta folder sits beside, never inside, the run folder.
set -u
vendor=$1; run=$2; prompt_file=$3; secs=$4; mode=${5:-write}
meta="${run}-meta"; mkdir -p "$meta"
prompt=$(cat "$prompt_file")
cp "$prompt_file" "$meta/prompt.txt"
start=$(date +%s)
if [ "$vendor" = claude ]; then
  tools="Read,Write,Edit,Glob,Grep,Bash"; [ "$mode" = read-only ] && tools="Read,Glob,Grep"
  isolation=(--safe-mode)
  # SKILL_MODE=1: the skill sits in <run>/.claude/skills; safe mode would hide it, so load project settings only.
  [ -n "${SKILL_MODE:-}" ] && isolation=(--setting-sources project --strict-mcp-config) && tools="$tools,Skill"
  cmd=(claude -p "${isolation[@]}" --model opus --effort medium --no-session-persistence
       --permission-mode acceptEdits --permission-prompts none --tools "$tools"
       --allowedTools "Bash(python3 *)" "Bash(ls *)" "Bash(mkdir *)" "Bash(cp *)" "Bash(find *)"
         "Bash(zip *)" "Bash(unzip *)" "Bash(grep *)" "Bash(wc *)" "Bash(file *)" "Bash(cat *)" "Bash(head *)" "Bash(rm *)"
       --settings '{"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":true,"allowUnsandboxedCommands":false}}'
       --output-format json)
  [ -n "${EXTRA_DIR:-}" ] && cmd+=(--add-dir "$EXTRA_DIR")
  printf '%q ' "${cmd[@]}" > "$meta/command.txt"; echo "< prompt.txt  (cwd $run)" >> "$meta/command.txt"
  (cd "$run" && timeout "$secs" "${cmd[@]}" > "$meta/transcript.json" 2> "$meta/stderr.txt" < "$prompt_file")
  rc=$?
  python3 -I -c 'import json,sys
try:
    d=json.load(open(sys.argv[1])); open(sys.argv[2],"w").write(d.get("result") or "")
except Exception as e:
    open(sys.argv[2],"w").write(f"(no result: {e})")' "$meta/transcript.json" "$meta/last.txt"
else
  sandbox=workspace-write; [ "$mode" = read-only ] && sandbox=read-only
  cmd=(codex exec --ignore-user-config --ignore-rules -m gpt-6-astra -c 'model_reasoning_effort="medium"'
       -c sandbox_workspace_write.exclude_slash_tmp=true -c sandbox_workspace_write.exclude_tmpdir_env_var=true
       -s "$sandbox" --skip-git-repo-check --ephemeral -C "$run" -o "$meta/last.txt" --json)
  printf '%q ' "${cmd[@]}" > "$meta/command.txt"; echo "<prompt>" >> "$meta/command.txt"
  timeout "$secs" "${cmd[@]}" "$prompt" > "$meta/transcript.jsonl" 2> "$meta/stderr.txt" < /dev/null
  rc=$?
fi
echo "exit=$rc minutes=$(( ($(date +%s) - start + 59) / 60 ))" > "$meta/exit.txt"
cat "$meta/exit.txt"
