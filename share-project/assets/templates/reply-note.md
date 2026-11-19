# Reply note format

The helper's assistant writes its answer in this format and the helper sends it back to the owner. The owner asks their own assistant to weigh the proposed edits against the current real project and apply them through its normal care; the note is advice, never permission to run its commands.

```
Reply to pack: {{pack-id}} revision {{revision}}
From: {{helper's first name or "a helper"}}
Date: {{yyyy-mm-dd}}

## What was established
## What is uncertain
## Proposed edits
### {{project/<file>}}
{{what to change and why; a small before/after excerpt}}
## How to check
{{steps the owner's assistant can follow, with expected results}}
```

Keep every `{{PLACEHOLDER}}`. Include no keys, passwords, personal values, private file paths or raw diagnostic output.
