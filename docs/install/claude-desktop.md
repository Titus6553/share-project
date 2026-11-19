# Install in the Claude desktop app

**Status: untested — try it and tell us** (see `ROUTES.md`). Screenshots will be added once a person has been through these steps.

## What you need

- The Claude desktop app on a Mac or Windows computer, signed in.
- A plan that allows custom skills, with code execution turned on (Settings → Capabilities). Claude's help pages differ on which plans allow uploading a skill; if the upload option is missing, your plan may not have it.
- The file `share-project-v0.1.0.zip`, saved somewhere you can find it. Do not unzip it.

## Steps

1. Open Settings → Capabilities (or Skills) and choose to upload a skill.
2. Pick `share-project-v0.1.0.zip`.
3. Turn the skill on if it is not on already.
4. Open a session that can see your project folder on this computer (for example Cowork or the Code tab, pointed at the folder). The skill does not work in a plain chat where you would have to upload your project: it stops and tells you so.
5. Ask: "share this project".

## What the skill does on your computer

- Reads your project folder where it is. It never changes it.
- Runs its own small Python helpers, which use only Python's built-in parts: they list your files, make stand-in copies of data files with invented rows, look for keys and personal details, check the pack and build the zip. They never start your project's code.
- Writes the pack and the zip to the place you choose (the Desktop is suggested).
- Uses the network only if you ask it to check for an update (it then contacts GitHub). Feedback is never sent by the skill; you send it yourself if you choose to.
