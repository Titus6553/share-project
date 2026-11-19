# The owner's answers (finance-dashboard)

These are the owner's answers to the intake questions, written down because the owner is not available to chat.

- **Which folder:** `finance-dashboard`
- **What the app does, in a sentence:** Every month it reads my DMS export workbook and shows revenue, cost, gross profit, margin and a status against target for each department (New, Used, Service, Parts).
- **Anything I already know is private:** The workbook has customer names, phone numbers and emails. The mail key and passwords are in the .env file.
- **Right to share:** I own this project and I am allowed to share it and its code with the recipient. (Confirmed 2026-11-18.)

## For the rebuild pack

- **How it should work:** A deal counts in the month it was delivered, or in its contract month if it has not been delivered yet. Gross profit is the sale price minus the cost; for Used cars the reconditioning cost is part of the cost. Money is shown in whole dollars. Status is On track at or above the month's target on the Targets sheet, Watch at or above 90% of it, otherwise Behind.
- **Known problems:** none that I know of.
- **Which flows matter:** the monthly table. The email is nice to have.

## For the help pack

- **What I did:** Ran `python app.py` after dropping the March export into the workbook.
- **What I expected:** Used gross profit for March around $7,500, which is what my DMS statement says.
- **What I saw:** The dashboard shows $4,061 for March Used gross, and Used shows "Behind". New, Service and Parts match the DMS.
- **Steps:** Put the export in `data/dealer_sales_2026.xlsx`, run `python app.py`, open `report.html`.
- **Exact error text:** No error for this. Separately, in April it crashed once; the error is in `logs/run.log` and went away after I fixed an "N/A" in the spreadsheet.
- **What changed recently:** Nothing that I know of.
- **When it last worked:** I am not sure it was ever right for Used; January and February look low too.
- **What I tried:** Re-ran it, re-exported from the DMS.
- **The question:** Why is Used gross profit too low?
