# Install in Codex (command-line or app)

**Status:** see `ROUTES.md`. The headless command-line route was tested by us on a Mac on 2026-11-18 with the skill in a project-level `.agents/skills` folder. The Codex app is untested.

## Steps

1. Unzip `share-project-v0.1.0.zip`. You get a folder named `share-project`.
2. Put that folder in a skills folder Codex reads: your personal `~/.agents/skills/share-project/`, or a project's `.agents/skills/share-project/`.
3. Start Codex in your project folder and ask: "share this project".

## What it does on your computer

Reads the folder in place, runs its standard-library Python helpers, writes the pack where you choose, and uses the network only for an update check you ask for.
