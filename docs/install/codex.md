# Install in Codex (command-line or app)

**Status:** see `ROUTES.md`. The command line on a Mac was tested by us on 2026-11-18/19, in headless runs with the skill in a project's `.agents/skills/` folder (both share actions, both sample projects). The personal install, interactive use and the Codex app are untested.

## Steps

1. Unzip `share-project-v0.1.0.zip`. You get a folder named `share-project`.
2. Put that folder in a skills folder Codex reads: your personal `~/.agents/skills/share-project/`, or a project's `.agents/skills/share-project/`.
3. Start Codex in your project folder and ask: "share this project".

## What it does on your computer

Reads the folder in place, runs its standard-library Python helpers, writes the pack where you choose, and uses the network only for an update check you ask for.
