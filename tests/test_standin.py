# tests/test_standin.py
# Purpose: stand-ins keep sheet, table and column names and types and contain no original value.
# Non-goals: how realistic the invented numbers look.
import os
import sqlite3
import unittest

from helpers import ROOT, tempdir
import find_canaries
import screen
import standin
from finance_reference import read_xlsx


class StandIns(unittest.TestCase):
    def setUp(self):
        self.out = tempdir(self)
        self.canaries = find_canaries.canaries()

    def no_original_values(self, path):
        hits = find_canaries.scan(path, self.canaries)
        self.assertEqual(hits, [], f"original values in {path}")
        res = screen.screen_paths([path])
        self.assertEqual((res["findings"], res["not_checked"]), ([], []))

    def test_workbook(self):
        src = os.path.join(ROOT, "samples", "finance-dashboard", "data", "dealer_sales_2026.xlsx")
        dst = os.path.join(self.out, "w.xlsx")
        res = standin.make(src, dst)
        before, after = read_xlsx(src), read_xlsx(dst)
        self.assertEqual(list(before), list(after))
        for sheet in before:
            self.assertEqual(before[sheet][0], after[sheet][0])
        idx = after["Deals"][0].index("sale_price")
        self.assertTrue(all(isinstance(float(r[idx]), float) for r in after["Deals"][1:]))
        self.assertIn("Deals.customer_email", res["personal_columns"])
        self.no_original_values(dst)

    def test_sqlite(self):
        src = os.path.join(ROOT, "samples", "recon-webapp", "data", "recon.db")
        dst = os.path.join(self.out, "r.db")
        standin.make(src, dst)
        def shape(p):
            con = sqlite3.connect(p)
            t = {n: [c[1:3] for c in con.execute(f'PRAGMA table_info("{n}")')] for (n,) in
                 con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            con.close()
            return t
        self.assertEqual(shape(src), shape(dst))
        self.no_original_values(dst)

    def test_date_cells_stay_date_cells(self):
        # Pilot R2: a rebuild tuned to a stand-in with text dates rejected real date-formatted cells.
        src, dst = os.path.join(self.out, "dates.xlsx"), os.path.join(self.out, "dates-out.xlsx")
        X = standin.XDate
        standin.write_xlsx(src, [("Deals", ["delivered_on", "amount"],
                                  [[X(46025), 10.5], [X(46056), 20.25], [X(46083), 7.0], [X(46090), 8.0]])])
        res = standin.make(src, dst)
        self.assertEqual(res["structure"]["sheets"][0]["columns"][0]["type"], "xdate")
        rows = standin.read_xlsx(dst)[0][1][1:]
        self.assertTrue(all(isinstance(r[0], X) for r in rows if r and r[0] not in (None, "")))

    def test_unsupported_is_left_out(self):
        src = os.path.join(ROOT, "samples", "finance-dashboard", "data", "old_exports.zip")
        with self.assertRaises(standin.LeftOut):
            standin.make(src, os.path.join(self.out, "x.zip"))
        self.assertFalse(os.path.exists(os.path.join(self.out, "x.zip")))


if __name__ == "__main__":
    unittest.main()
