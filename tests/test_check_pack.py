# tests/test_check_pack.py
# Purpose: a clean pack passes; each required-file omission fails; links, nested archives, copied data, history and leftover secrets fail.
# Non-goals: message wording.
import os
import shutil
import unittest
import zipfile

from helpers import ROOT, make_pack
import check_pack


def put(path, text, mode="w"):
    with open(path, mode) as f:
        f.write(text)


def kinds(res):
    return {p["kind"] for p in res["problems"]}


class CheckPack(unittest.TestCase):
    def test_clean_packs_pass(self):
        for action in ("rebuild", "help"):
            res = check_pack.check(make_pack(self, action))
            self.assertEqual(res["problems"], [], action)

    def test_each_required_file_missing_fails(self):
        for action, names in (("rebuild", ["START-HERE.md", "COVERAGE.md", "DATA.md", "SETUP-LIST.md",
                                           "SAFETY-SUGGESTIONS.md", "REBUILD.md"]),
                              ("help", ["PROBLEM.md", "REPLY-FORMAT.md"])):
            for name in names:
                pack = make_pack(self, action)
                os.remove(os.path.join(pack, name))
                self.assertTrue(check_pack.check(pack)["problems"], f"{action} pack without {name} passed")

    def test_missing_heading_and_bad_outcome_fail(self):
        pack = make_pack(self)
        p = os.path.join(pack, "REBUILD.md")
        with open(p) as f:
            text = f.read().replace("## Checks that define done\n", "")
        with open(p, "w") as f:
            f.write(text)
        self.assertIn("missing heading", kinds(check_pack.check(pack)))
        pack = make_pack(self)
        p = os.path.join(pack, "START-HERE.md")
        with open(p) as f:
            text = f.read().replace("ready to rebuild against the stated checks", "totally safe")
        with open(p, "w") as f:
            f.write(text)
        self.assertIn("bad header value", kinds(check_pack.check(pack)))

    def test_link_nested_archive_copied_data_history_secret_fail(self):
        cases = {
            "link": lambda pack: os.symlink("/etc/hosts", os.path.join(pack, "project", "hosts")),
            "nested archive": lambda pack: zipfile.ZipFile(os.path.join(pack, "project", "old.zip"), "w").close(),
            "copied data file": lambda pack: shutil.copy(
                os.path.join(ROOT, "samples", "finance-dashboard", "data", "dealer_sales_2026.xlsx"),
                os.path.join(pack, "project", "data", "dealer_sales_2026.xlsx")),
            "changed stand-in": lambda pack: put(os.path.join(pack, "project", "data", "sales.csv"), "x,y,z,1\n", "a"),
            "history": lambda pack: os.makedirs(os.path.join(pack, "project", ".git")) or
                put(os.path.join(pack, "project", ".git", "config"), ""),
            "keys file": lambda pack: put(os.path.join(pack, "project", ".env"), "MAIL_KEY={{MAIL_KEY}}\n"),
            "key in code": lambda pack: put(os.path.join(pack, "project", "x.py"), 'k = "rsk_9Tg4Wq2Lp7Xz3Vn8Hb6D"\n'),
            "unlisted placeholder": lambda pack: put(os.path.join(pack, "project", "y.py"), 'k = "{{OTHER_KEY}}"\n'),
            "unfilled template": lambda pack: put(os.path.join(pack, "DATA.md"), "{{sheet or table name}}\n", "a"),
        }
        for name, spoil in cases.items():
            pack = make_pack(self)
            spoil(pack)
            self.assertTrue(check_pack.check(pack)["problems"], f"pack with {name} passed")


if __name__ == "__main__":
    unittest.main()
