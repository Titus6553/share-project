"""Settings for the monthly gross dashboard."""

WORKBOOK = "data/dealer_sales_2026.xlsx"
DEALS_SHEET = "Deals"
TARGETS_SHEET = "Targets"
DEPARTMENTS = ["New", "Used", "Service", "Parts"]

# Status against target: On track at or above target, Watch at or above 90% of target, else Behind.
WATCH_SHARE = 0.90

# The report service key. TODO move to .env like the others.
REPORT_SERVICE_KEY = "rsk_9Tg4Wq2Lp7Xz3Vn8Hb6D"
REPORT_SERVICE_URL = "https://reports.dealer-group.example/v1/upload"
