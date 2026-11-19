# tools/make_samples.py
# Purpose: write the committed data files of both sample projects (workbook, nested archive, image, SQLite file).
# Non-goals: the extras that cannot live in git (history, an escaping link, an oversized file) are stage_sample.py's.
"""Usage: python3 tools/make_samples.py   (rewrites the files in place; deterministic)"""

import os
import sqlite3
import struct
import sys
import zipfile
import zlib

sys.path.insert(0, os.path.dirname(__file__))
from sample_data import FINANCE_TARGETS, finance_deals, recon_items, write_xlsx  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")
FIN = os.path.join(ROOT, "finance-dashboard")
REC = os.path.join(ROOT, "recon-webapp")


def png(path, w=8, h=8, rgb=(26, 127, 55)):
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


def finance():
    deals = finance_deals()
    header = list(deals[0])
    write_xlsx(os.path.join(FIN, "data", "dealer_sales_2026.xlsx"), [
        ("Deals", header, [[d[k] for k in header] for d in deals]),
        ("Targets", ["month", "department", "gross_target"], [[t["month"], t["department"], t["gross_target"]] for t in FINANCE_TARGETS]),
    ])
    nested = os.path.join(FIN, "data", "old_exports.zip")
    with zipfile.ZipFile(nested, "w", zipfile.ZIP_DEFLATED) as z:
        z.comment = b"exported for Thaddeus Okonkwo-Bell; archive ref arc_Vq3N8x6R2m"
        z.writestr(zipfile.ZipInfo("deals_2025_q4.csv", (2026, 1, 1, 0, 0, 0)),
                   "deal_id,customer_name,customer_phone,customer_email,sale_price\n"
                   "D-0907,Thaddeus Okonkwo-Bell,385-555-0193,thaddeus.okonkwobell@example.net,27314.55\n")
    png(os.path.join(FIN, "assets", "logo.png"))


def recon():
    items, staff = recon_items()
    path = os.path.join(REC, "data", "recon.db")
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE items (stock_no TEXT PRIMARY KEY, vin TEXT, year INTEGER, make TEXT, model TEXT, "
                "stage TEXT, entered_stage_on TEXT, assigned_to TEXT, trade_in_from TEXT, trade_in_phone TEXT)")
    con.execute("CREATE TABLE staff (email TEXT PRIMARY KEY, name TEXT, phone TEXT)")
    con.executemany("INSERT INTO items VALUES (:stock_no,:vin,:year,:make,:model,:stage,:entered_stage_on,"
                    ":assigned_to,:trade_in_from,:trade_in_phone)", items)
    con.executemany("INSERT INTO staff VALUES (:email,:name,:phone)", staff)
    con.commit()
    con.execute("VACUUM")
    con.close()
    png(os.path.join(REC, "static", "logo.png"), rgb=(9, 105, 218))


if __name__ == "__main__":
    finance()
    recon()
    print("samples written")
