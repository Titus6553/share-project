# If someone handed you this skill

Read this when a person gave you `share-project` as a zip or a folder, instead of you finding it already installed. The person is probably not technical. Use plain words, ask one thing at a time, and never ask them to use a terminal. They decide; this page only tells you what usually helps.

`QUICK-GUIDE.pdf` in this folder is a two-page guide written for the person. Tell them it exists and offer to open it.

## 1. Work out which case you are in

| What you find | What to do |
|---|---|
| You can only see files the person uploaded to this chat. You cannot open folders on their computer or run Python 3. | Section 2. |
| You can open folders on their computer and run Python 3, and `share-project` is **not** in your skills. | First time. Section 3, then section 5. |
| `share-project` is already in your skills, and its `VERSION` is the same as this folder's. | Nothing to install. Say so and go to section 5. |
| It is already in your skills with a lower `VERSION` than this folder's. | Section 4, then section 5. |
| It is already in your skills with a higher `VERSION`. | Keep the installed one. Say the copy they handed you is older, and go to section 5. |

If the skill arrived as a zip, unzip it into a new, empty folder that is outside any project (for example a new folder in the person's Downloads or Documents). Never unzip it into a project folder.

## 2. A chat that cannot see the computer

Do not ask the person to upload their project so you can work on it here. This skill checks a project before anything leaves the computer, and an upload cannot be undone.

Tell them, in your own words, the two ways forward:

- **Use an assistant that works on a folder on this computer**: the Code tab or Cowork in the Claude desktop app, Claude Code, or Codex. Open the project folder there, hand over this same zip and ask again.
- **Add the skill through the app's settings**: in the Claude desktop app, Settings, then Capabilities (or Skills), then upload this zip, still zipped. In ChatGPT, the skills settings of a workspace that allows custom skills. They still need a session that can see the project folder to use it.

Then stop.

## 3. First time: keep it for next time

Ask once: "Do you want me to keep this skill so it is ready next time?"

- **Yes.** Copy the whole `share-project` folder into the personal skills folder of the assistant you are, creating the folder if it is missing:

  | You are | Copy it to (Mac or Linux) | On Windows |
  |---|---|---|
  | Claude Code, or the Code tab of the Claude desktop app | `~/.claude/skills/share-project/` | `.claude\skills\share-project\` in the user's home folder |
  | Codex | `~/.agents/skills/share-project/` | `.agents\skills\share-project\` in the user's home folder |
  | Cowork, ChatGPT or anything else | Use that app's own documented way to add a skill. If it only takes an upload through its settings, tell the person the settings steps in section 2 and use the skill from where it is for now. | |

  Never put it inside a project folder. After copying, check that `SKILL.md` and the `scripts` folder arrived, and tell the person the skill will be there in their next session (some apps need a restart).
- **No, or you cannot.** That is fine. Use it from where it is for this session, and tell them they will need to hand it over again next time.

## 4. An older copy is already installed

Tell the person which version is installed and which one they handed you. If they want the newer one, move the installed folder aside under a new name (for example `share-project-old`) outside the skills folder, copy the new folder in, and keep the old one until the new one has worked once. If anything fails, put the old folder back.

## 5. Use it

Read `SKILL.md` in this folder and follow it. Run the helpers by their full path from wherever this folder is now; they work the same installed or not.

If the person has not said what they want yet, tell them in two sentences what the skill does and ask which they want: to share a project so someone can rebuild it, or to share it so someone can help with a problem.

If a step fails, say what happened in plain words and offer the feedback action in `references/update-and-feedback.md`.
