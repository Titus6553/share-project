# Decisions

One line per builder choice the design left open. Newest at the bottom.

- 2026-11-18 · Skill name `share-project`; repository folder `share-project-skill`. The name holds no vendor name.
- 2026-11-18 · Licence MIT.
- 2026-11-18 · Helpers are Python 3 standard library only (3.9 or newer); no third-party package, no network except `update_fetch.py`. Where no Python runs, the skill reports each helper step as a check that could not run, and stops before delivery.
