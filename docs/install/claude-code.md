# Install in Claude Code (command-line or desktop Code tab)

**Status:** see `ROUTES.md`. The headless command-line route was tested by us on a Mac on 2026-11-18 with the skill in a project-level skills folder; the steps below for a personal install are documented but untested.

## Steps

1. Unzip `share-project-v0.1.0.zip`. You get a folder named `share-project`.
2. Put that folder in your personal skills folder: `~/.claude/skills/share-project/` on a Mac (on Windows, the `.claude\skills` folder in your user folder). For one project only, put it in that project's `.claude/skills/` folder instead.
3. Start Claude Code in your project folder and ask: "share this project".

## What it does on your computer

As in `claude-desktop.md`: reads the folder in place, runs its standard-library Python helpers, writes the pack where you choose, and uses the network only for an update check you ask for.
