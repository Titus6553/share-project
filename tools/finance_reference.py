# tools/finance_reference.py
# Purpose: an independent calculation of the finance-dashboard sample's monthly figures, intended and as-built.
# Non-goals: not the sample's code and never imports it; reads a workbook with the standard library only.
"""Usage: python3 tools/finance_reference.py <workbook.xlsx> [--as-built]

Intended rules (the owner's): report month = delivered_on month, else contract_on month;
revenue = sum of sale_price; cost = sum of cost + sum of recon_cost (recon counted once);
gross = revenue - cost; money rounded half-up to whole dollars after summing; margin % =
gross / revenue * 100 rounded half-up to one decimal; status against the Targets sheet:
On track if rounded gross >= target, Watch if >= 90% of target, else Behind.
--as-built reproduces the planted defect: Used recon is subtracted twice."""

import json
import re
import sys
import zipfile
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def read_xlsx(path):
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        out = {}
        for sh in wb.find("m:sheets", NS):
            xml = ET.fromstring(z.read("xl/" + targets[sh.get(RNS)].lstrip("/").removeprefix("xl/")))
            rows = []
            for row in xml.iter(f"{{{NS['m']}}}row"):
                vals = {}
                for c in row.findall("m:c", NS):
                    col = re.match(r"[A-Z]+", c.get("r")).group(0)
                    t = c.get("t")
                    if t == "inlineStr":
                        v = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
                    elif t == "s":
                        v = shared[int(c.find("m:v", NS).text)]
                    else:
                        node = c.find("m:v", NS)
                        v = None if node is None else node.text
                    vals[col] = v
                width = max((_ci(k) for k in vals), default=-1) + 1
                rows.append([next((vals[k] for k in vals if _ci(k) == i), None) for i in range(width)])
            out[sh.get("name")] = rows
        return out


def _ci(col):
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n - 1


def money(d):
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def compute(path, as_built=False):
    sheets = read_xlsx(path)
    header, *deals = sheets["Deals"]
    idx = {h: i for i, h in enumerate(header)}
    acc = defaultdict(lambda: {"revenue": Decimal(0), "cost": Decimal(0)})
    for r in deals:
        month = (r[idx["delivered_on"]] or r[idx["contract_on"]])[:7]
        dept = r[idx["department"]]
        r = r + [None] * (len(header) - len(r))
        recon = Decimal(r[idx["recon_cost"]] or "0")
        cost = Decimal(r[idx["cost"]]) + recon + (recon if as_built and dept == "Used" else 0)
        acc[(month, dept)]["revenue"] += Decimal(r[idx["sale_price"]])
        acc[(month, dept)]["cost"] += cost
    t_header, *t_rows = sheets["Targets"]
    ti = {h: i for i, h in enumerate(t_header)}
    targets = {(r[ti["month"]], r[ti["department"]]): Decimal(r[ti["gross_target"]]) for r in t_rows}
    result = []
    for (month, dept), a in sorted(acc.items()):
        gross = a["revenue"] - a["cost"]
        g = money(gross)
        margin = (gross / a["revenue"] * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        target = targets.get((month, dept))
        status = None if target is None else ("On track" if g >= target else "Watch" if g >= target * Decimal("0.9") else "Behind")
        result.append({"month": month, "department": dept, "revenue": money(a["revenue"]),
                       "cost": money(a["cost"]), "gross": g, "margin_pct": str(margin), "status": status})
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(json.dumps(compute(sys.argv[1], "--as-built" in sys.argv), indent=1))
