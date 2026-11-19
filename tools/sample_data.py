# tools/sample_data.py
# Purpose: the invented rows behind both sample projects, and a tiny standard-library .xlsx writer.
# Non-goals: no real person, dealer or key; nothing here is read by the skill itself.
"""Every value here is invented. Phones use the 555-01xx fictional range; emails use reserved
example domains. They are still personal-data canaries: the screening must flag them."""

import random
import zipfile
from xml.sax.saxutils import escape

FIRST = ["Marisol", "Delphine", "Ignatius", "Rosalind", "Thaddeus", "Ottoline", "Cassius", "Wilhelmina",
         "Barnaby", "Esperanza", "Leopold", "Henrietta", "Ambrose", "Philippa", "Lazarus", "Clementine",
         "Peregrine", "Seraphina", "Octavius", "Marigold", "Fitzgerald", "Evangeline", "Cornelius", "Josephine"]
LAST = ["Quintanilla", "Arkwright", "Wollstonecraft", "Featherstone", "Okonkwo", "Vanterpool", "Merriweather",
        "Delacroix-Hale", "Pemberton", "Ashgrove", "Thistlewood", "Bramhall", "Kettleborough", "Larkspur",
        "Moorcroft", "Nightingale", "Oakenshaw", "Penhaligon", "Quillfeather", "Ravensworth", "Saltonstall",
        "Tregarthen", "Underhill", "Wetherby"]
VIN_CHARS = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"


def _people(rng, n, domain, area="801", shift=0):
    out = []
    for i in range(n):
        first = FIRST[(i * 5 + 3) % len(FIRST)] if shift else FIRST[i]
        last = LAST[(i * 7 + shift) % len(LAST)]
        out.append({
            "name": f"{first} {last}",
            "phone": f"{area}-555-01{10 + i:02d}",
            "email": f"{first.lower()}.{last.lower().replace('-', '')}@{domain}",
            "vin": "JF2" + "".join(rng.choice(VIN_CHARS) for _ in range(14)),
        })
    return out


def finance_deals():
    """24 deals, Jan-Mar 2026, four departments. Prices carry cents so rounding matters."""
    rng = random.Random(20261118)
    people = _people(rng, 24, "example.net")
    depts = ["New", "Used", "Service", "Parts"]
    rows = []
    for i, p in enumerate(people):
        dept = depts[i % 4]
        month = 1 + (i // 8)
        contract_day = 3 + (i * 5) % 25
        # Three Used and New deals contract in one month and deliver in the next (date-grouping rule).
        delivered = "" if i in (5, 14) else (
            f"2026-{month + 1:02d}-02" if i in (1, 9, 17) and month < 3 else f"2026-{month:02d}-{contract_day + 1:02d}")
        base = {"New": 38000, "Used": 21000, "Service": 640, "Parts": 310}[dept]
        price = round(base + rng.randint(0, 9000 if dept in ("New", "Used") else 400) + rng.randint(0, 99) / 100, 2)
        margin = {"New": 0.06, "Used": 0.14, "Service": 0.55, "Parts": 0.36}[dept] + rng.randint(-4, 4) / 100
        cost = round(price * (1 - margin) + rng.randint(0, 99) / 100, 2)
        recon = round(600 + rng.randint(0, 1400) + rng.randint(0, 99) / 100, 2) if dept == "Used" else 0.0
        rows.append({
            "deal_id": f"D-{1001 + i}", "department": dept, "customer_name": p["name"],
            "customer_phone": p["phone"], "customer_email": p["email"],
            "vin": p["vin"] if dept in ("New", "Used") else "",
            "contract_on": f"2026-{month:02d}-{contract_day:02d}", "delivered_on": delivered,
            "sale_price": price, "cost": cost, "recon_cost": recon,
            "salesperson": ["Avery Lindqvist", "Jordan Pellegrino", "Morgan Haverford"][i % 3],
        })
    return rows


FINANCE_TARGETS = [
    {"month": f"2026-{m:02d}", "department": d, "gross_target": t}
    for m in (1, 2, 3) for d, t in (("New", 9000), ("Used", 6500), ("Service", 900), ("Parts", 300))
]


def recon_items():
    rng = random.Random(1118)
    people = _people(rng, 10, "example.org", area="208", shift=3)
    stages = ["Inspection", "Mechanical", "Body", "Detail", "Photos", "Frontline"]
    staff = [{"email": f"tech{n}@example.org", "name": nm, "phone": f"435-555-01{50 + n:02d}"}
             for n, nm in enumerate(["Quincy Abernathy-Stone", "Rhiannon Vasquez-Lowell", "Silas Wintermere"])]
    items = []
    for i, p in enumerate(people):
        items.append({
            "stock_no": f"U{4410 + i}", "vin": p["vin"], "year": 2019 + i % 5,
            "make": "Subaru", "model": ["Outback", "Forester", "Crosstrek", "Ascent", "Impreza"][i % 5],
            "stage": stages[i % 6], "entered_stage_on": f"2026-03-{1 + (i * 3) % 27:02d}",
            "assigned_to": staff[i % 3]["email"], "trade_in_from": p["name"], "trade_in_phone": p["phone"],
        })
    return items, staff


# ---- minimal .xlsx writer (inline strings and numbers only) ----

def _col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _sheet_xml(header, rows):
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for r, values in enumerate([header] + rows, start=1):
        cells = []
        for c, v in enumerate(values, start=1):
            ref = f"{_col(c)}{r}"
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                cells.append(f'<c r="{ref}"><v>{v}</v></c>')
            else:
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>')
        out.append(f'<row r="{r}">{"".join(cells)}</row>')
    out.append("</sheetData></worksheet>")
    return "".join(out)


def write_xlsx(path, sheets):
    """sheets: list of (name, header, rows-as-lists)."""
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>']
    wb_sheets, wb_rels = [], []
    for i, (name, _, _) in enumerate(sheets, start=1):
        ct.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        wb_sheets.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
        wb_rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
    ct.append("</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + "".join(wb_sheets) + "</sheets></workbook>")
    wbr = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
           + "".join(wb_rels) + "</Relationships>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in (("[Content_Types].xml", "".join(ct)), ("_rels/.rels", rels),
                           ("xl/workbook.xml", wb), ("xl/_rels/workbook.xml.rels", wbr)):
            z.writestr(zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0)), data)
        for i, (_, header, rows) in enumerate(sheets, start=1):
            z.writestr(zipfile.ZipInfo(f"xl/worksheets/sheet{i}.xml", (2026, 1, 1, 0, 0, 0)), _sheet_xml(header, rows))
