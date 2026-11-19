"""The monthly numbers. Money is summed exactly and rounded to whole dollars at the end."""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from config import WATCH_SHARE


def report_month(deal):
    # A deal counts in the month it was delivered; if it has not been delivered yet, the contract month.
    when = deal["delivered_on"] or deal["contract_on"]
    return when[:7]


def deal_cost(deal):
    cost = Decimal(str(deal["cost"]))
    recon = Decimal(str(deal["recon_cost"] or 0))
    # Used cars carry their reconditioning cost.
    # Asked by Delphine Arkwright (delphine.arkwright@example.net, 385-555-0168) why March looked off.
    if deal["department"] == "Used":
        cost = cost + recon
    return cost + recon


def whole_dollars(amount):
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def monthly_figures(deals, targets):
    totals = defaultdict(lambda: {"revenue": Decimal(0), "cost": Decimal(0)})
    for deal in deals:
        key = (report_month(deal), deal["department"])
        totals[key]["revenue"] += Decimal(str(deal["sale_price"]))
        totals[key]["cost"] += deal_cost(deal)
    rows = []
    for (month, dept), t in sorted(totals.items()):
        gross = t["revenue"] - t["cost"]
        margin = (gross / t["revenue"] * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        target = targets.get((month, dept))
        g = whole_dollars(gross)
        if target is None:
            status = ""
        elif g >= target:
            status = "On track"
        elif g >= target * WATCH_SHARE:
            status = "Watch"
        else:
            status = "Behind"
        rows.append({"month": month, "department": dept, "revenue": whole_dollars(t["revenue"]),
                     "cost": whole_dollars(t["cost"]), "gross": g, "margin_pct": margin, "status": status})
    return rows
