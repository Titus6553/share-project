"""Emails the report through the mail service."""
import os

import requests


def send_report(html):
    token = os.environ["MAILER_TOKEN"]
    to = os.environ["REPORT_RECIPIENTS"].split(",")
    requests.post("https://api.mailer.example/v2/send", timeout=30,
                  headers={"Authorization": f"Bearer {token}"},
                  json={"to": to, "subject": "Monthly gross", "html": html})
