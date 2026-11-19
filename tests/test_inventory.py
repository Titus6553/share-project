# tests/test_inventory.py
# Purpose: the inventory sorts every planted file into the right kind and never prints a key value.
# Non-goals: exact reason wording.
import json
import os
import unittest

from helpers import staged
import inventory


class InventorySamples(unittest.TestCase):
    def setUp(self):
        self.project = staged(self)
        self.res = inventory.inventory(self.project)
        self.kind = {f["path"]: f["kind"] for f in self.res["files"]}

    def test_kinds(self):
        expect = {".env": "secret", "calc.py": "code", "requirements.lock": "code",
                  os.path.join("data", "dealer_sales_2026.xlsx"): "data", os.path.join("data", "old_exports.zip"): "left-out",
                  ".git/": "left-out", "shared-settings.txt": "left-out", os.path.join("static", "vendor.bundle.js"): "left-out",
                  os.path.join("assets", "logo.png"): "left-out", "backup-tok_7Rj2Kx9Wq4Lz8Pm3.json": "left-out"}
        for path, kind in expect.items():
            self.assertEqual(self.kind.get(path), kind, path)

    def test_json_with_records_is_data(self):
        # End review: a small exported JSON of rows at the project root was classed as code and copied.
        rows = os.path.join(self.project, "sales.json")
        with open(rows, "w") as f:
            json.dump({"rows": [{"customer": "Ada Moreno", "amount": 1}]}, f)  # follow-up: one record is enough
        self.assertEqual(inventory.classify("sales.json", rows)[0], "data")
        settings = os.path.join(self.project, "settings.json")
        with open(settings, "w") as f:
            json.dump({"stages": ["Inspection", "Body", "Detail"], "port": 8080}, f)
        self.assertEqual(inventory.classify("settings.json", settings)[0], "code")

    def test_key_names_only(self):
        self.assertEqual(self.res["key_names"][".env"], ["DEALER_FEED_API_KEY", "MAILER_TOKEN", "SMTP_PASSWORD", "REPORT_RECIPIENTS"])
        out = json.dumps(self.res)
        for value in ["fdk_live_4QmZ8vT2xR7nB1wK9cJ5", "Harbor-Lantern-6624!", "mlt_Zx81Qp55Rv20Lm73Hy6E"]:
            self.assertNotIn(value, out)

    def test_history_not_walked(self):
        self.assertFalse(any(p.startswith(".git" + os.sep) and p != ".git/" for p in self.kind))


if __name__ == "__main__":
    unittest.main()
