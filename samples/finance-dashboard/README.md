# Monthly gross dashboard

Built with my AI assistant in January 2026. Every month I drop the DMS export into `data/dealer_sales_2026.xlsx` and run `python app.py`. It writes `report.html` and, if I say so, emails it to the managers.

- Departments: New, Used, Service, Parts
- Targets live on the "Targets" sheet of the same workbook
- Email goes through the mail service; the key is in `.env`
