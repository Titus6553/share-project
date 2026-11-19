# Update and feedback

Load this when the owner asks to update the skill, to send feedback, or when something fails and you offer feedback.

The skill's home is one fixed public repository, written into `scripts/update_fetch.py` and `scripts/feedback.py` as `REPOSITORY`. Until the publisher sets it, it reads `OWNER/share-project`, and the update and the GitHub route of feedback cannot work; say so plainly and offer the email route.

## Check for an update

1. Run `python3 scripts/update_fetch.py --check`. It prints the installed and the newest published release. This is the only network use besides the download below. No project file is ever sent.
2. If the owner wants the newer one, run `python3 scripts/update_fetch.py --fetch`. It downloads the release zip into a new folder outside the project, refuses unsafe zips (paths that climb out, links, nested archives, anything outside the skill folder), and lists what would be added, removed and changed, with the zip's fingerprint.
3. Show the owner that list. Say plainly: **this release cannot prove who published the zip**; the fingerprint comes from the same download, so it proves nothing about the publisher.
4. Nothing is installed by the helper. If the owner wants to install it, use the app's own way of adding a skill: in a desktop app, upload the staged zip again through its skills settings; in a command-line tool, the owner replaces the skill folder through that tool's documented skills location. Never write over the installed skill yourself, and keep the old version until the new one works.
5. If installing fails or the owner cancels, nothing changes: the current version stays installed and usable, and the staged folder can be deleted.

## Send feedback

1. Offer it when a step fails, or when the owner asks.
2. Pick values only from `python3 scripts/feedback.py --choices`: the app, the mode, the plan if known, the computer (mac, windows), the step and the outcome, and an error category. Never copy error text, logs, file or project names, paths, addresses, screenshots or account details: the helper refuses anything outside its list.
3. Run `python3 scripts/feedback.py --app … --mode … --plan … --os … --step … --outcome … --category …` and show the owner the whole report and both routes.
4. Only after the owner approves: for someone with a GitHub account, give them the printed issue address to open themselves; otherwise give them the report to paste into an email to Ben. Anything the owner adds by hand goes below "Added by the owner:" so it stays apart from the generated report.
5. A route that worked can be reported the same way (outcome `worked`); that is how untested routes become "reported working by a user".
