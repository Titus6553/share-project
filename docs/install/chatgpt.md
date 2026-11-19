# Install in the ChatGPT app

**Status: untested — try it and tell us** (see `ROUTES.md`). A result in Codex is not a result for the ChatGPT app; they are listed separately.

## What we know from OpenAI's documentation (read 2026-11-18, not tested)

- Custom skills in the ChatGPT app are documented for Business, Enterprise, Healthcare and Edu workspaces. Personal plans are not named; that does not prove they cannot, or can, use skills.
- Uploaded skills are scanned and can be blocked.

## Steps to try

1. In a workspace that allows custom skills, open the skills settings and upload `share-project-v0.1.0.zip`.
2. The skill needs to read your project folder where it is and to run Python. If your ChatGPT session can only see files you upload, the skill stops and says so: it will not ask you to upload a project that holds keys or customer data.
3. If it installs and runs, ask: "share this project", and tell us what happened through the feedback action.
