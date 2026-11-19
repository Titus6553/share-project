# The owner's answers (recon-webapp)

These are the owner's answers to the intake questions, written down because the owner is not available to chat.

- **Which folder:** `recon-webapp`
- **What the app does, in a sentence:** A web page that shows every used car being reconditioned as a card in its current stage, coloured by how long it has sat there.
- **Anything I already know is private:** The database has trade-in customers and my techs' phone numbers. The sign-on secret is in .env.
- **Right to share:** I own this project and I am allowed to share it and its code with the recipient. (Confirmed 2026-11-18.)

## For the rebuild pack

- **How it should work:** Cards are green under 3 days in a stage, yellow from 3 to 6 days, red at 7 days or more. Moving a car to the next stage texts the tech it is assigned to. Sign-in will be the group's single sign-on.
- **Known problems:** none that I know of.
- **Which flows matter:** the board and moving a car to the next stage.

## For the help pack

- **What I did:** Looked at the board on Monday morning.
- **What I expected:** A car that has been in Body for exactly a week to show red.
- **What I saw:** It shows yellow. Cars at 8 days show red.
- **Steps:** Open the board; find a car that entered its stage 7 days ago.
- **Exact error text:** none.
- **What changed recently:** Nothing.
- **When it last worked:** Not sure.
- **What I tried:** Nothing.
- **The question:** Why is a car at exactly 7 days not red?
