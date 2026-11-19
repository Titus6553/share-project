# tests/test_update_fetch.py
# Purpose: the update helper rejects unsafe release zips and stages a good one outside any project without installing it.
# Non-goals: network access (every case uses a local zip).
import io
import os
import unittest
import zipfile

from helpers import tempdir
import update_fetch


def zip_bytes(entries, link=None):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in entries.items():
            z.writestr(name, data)
        if link:
            info = zipfile.ZipInfo(link)
            info.external_attr = 0o120777 << 16
            z.writestr(info, "/etc/passwd")
    return buf.getvalue()


GOOD = {"share-project/SKILL.md": "---\nname: share-project\n---\n", "share-project/VERSION": "9.9.9\n"}


class UpdateFetch(unittest.TestCase):
    def test_unsafe_archives_refused(self):
        for entries, link in (({**GOOD, "share-project/../../escape.txt": "x"}, None),
                              ({**GOOD, "/abs.txt": "x"}, None),
                              ({**GOOD, "other/file.txt": "x"}, None),
                              ({**GOOD, "share-project/inner.zip": "x"}, None),
                              (GOOD, "share-project/link"),
                              ({"share-project/README.md": "x"}, None)):
            staging = os.path.join(tempdir(self), "stage")
            root, problems = update_fetch.stage(zip_bytes(entries, link), staging)
            self.assertIsNone(root)
            self.assertTrue(problems)
            self.assertFalse(os.path.exists(os.path.join(os.path.dirname(staging), "escape.txt")))

    def test_good_release_staged_not_installed(self):
        staging = os.path.join(tempdir(self), "stage")
        before = update_fetch.tree(update_fetch.HERE)
        root, problems = update_fetch.stage(zip_bytes(GOOD), staging)
        self.assertEqual(problems, [])
        self.assertTrue(os.path.isfile(os.path.join(root, "SKILL.md")))
        # End review: the checked zip was not kept, so a desktop app had nothing to install from.
        with open(os.path.join(staging, "share-project-release.zip"), "rb") as f:
            self.assertEqual(f.read(), zip_bytes(GOOD))
        self.assertEqual(update_fetch.tree(update_fetch.HERE), before)


if __name__ == "__main__":
    unittest.main()
