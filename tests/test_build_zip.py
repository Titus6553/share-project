# tests/test_build_zip.py
# Purpose: the zip is built only from a passing pack, holds exactly the checked files, and refuses a message with personal data.
# Non-goals: compression details.
import os
import unittest
import zipfile

from helpers import make_pack, tempdir
import build_zip


class BuildZip(unittest.TestCase):
    def test_zip_matches_checked_files(self):
        pack = make_pack(self)
        out = os.path.join(tempdir(self), "pack.zip")
        self.assertEqual(build_zip.build(pack, out), [])
        with zipfile.ZipFile(out) as z:
            names = sorted(z.namelist())
            self.assertTrue(all(n.startswith("test-pack/") for n in names))
            self.assertEqual(z.comment, b"")
            for i in z.infolist():
                self.assertEqual((i.external_attr >> 16) & 0o777, 0o644)
        expected = sorted("test-pack/" + os.path.relpath(os.path.join(b, f), pack).replace(os.sep, "/")
                          for b, _, fs in os.walk(pack) for f in fs)
        self.assertEqual(names, expected)

    def test_refuses_failing_pack(self):
        pack = make_pack(self)
        os.remove(os.path.join(pack, "COVERAGE.md"))
        out = os.path.join(tempdir(self), "pack.zip")
        self.assertTrue(build_zip.build(pack, out))
        self.assertFalse(os.path.exists(out))

    def test_refuses_key_shaped_pack_folder_name(self):
        # End review: the folder name goes into every entry but was never screened.
        pack = make_pack(self)
        renamed = os.path.join(os.path.dirname(pack), "tok_7Rj2Kx9Wq4Lz8Pm3")
        os.rename(pack, renamed)
        out = os.path.join(tempdir(self), "pack.zip")
        self.assertTrue(build_zip.build(renamed, out))
        self.assertFalse(os.path.exists(out))

    def test_refuses_message_with_personal_data(self):
        pack = make_pack(self)
        msg = os.path.join(tempdir(self), "message.txt")
        with open(msg, "w") as f:
            f.write("Hi, here is the pack. Call Rosalind on 385-555-0177 if stuck.\n")
        out = os.path.join(tempdir(self), "pack.zip")
        self.assertTrue(build_zip.build(pack, out, msg))
        self.assertFalse(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
