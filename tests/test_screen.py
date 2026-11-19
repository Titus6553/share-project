# tests/test_screen.py
# Purpose: every canary kind in the samples is either found or reported as not checked, never silently cleared.
# Non-goals: wording of messages.
import os
import unittest

from helpers import staged
import screen


class ScreenSamples(unittest.TestCase):
    def test_finance_canaries_found_or_unchecked(self):
        project = staged(self)
        res = screen.screen_paths([project], names=True)
        found = {(f["file"], f["kind"]) for f in res["findings"]}
        files = {f for f, _ in found}
        for must in ["config.py", "calc.py", "notes.md", os.path.join("logs", "run.log"), "requirements.lock",
                     ".env", "backup-tok_7Rj2Kx9Wq4Lz8Pm3.json"]:
            self.assertIn(must, files, f"no finding in {must}")
        unchecked = {n["file"] for n in res["not_checked"]}
        for must in ["shared-settings.txt", os.path.join("static", "vendor.bundle.js"),
                     os.path.join("data", "old_exports.zip"), os.path.join("assets", "logo.png")]:
            self.assertIn(must, unchecked, f"{must} was neither found nor reported unchecked")

    def test_values_are_never_printed(self):
        project = staged(self)
        res = screen.screen_paths([project], names=True)
        text = repr(res)
        for value in ["rsk_9Tg4Wq2Lp7Xz3Vn8Hb6D", "delphine.arkwright@example.net", "385-555-0177", "pxt_Fq72Lw19Zr44Mn08aKd3"]:
            self.assertNotIn(value, text)

    def test_placeholders_and_standin_shapes_are_clean(self):
        text = ('API_KEY = "{{API_KEY}}"\ntoken = os.environ["TOKEN"]\nurl = "https://{{USER}}:{{PASS}}@host/x"\n'
                "standin-3@example.invalid, 000-555-0112\n")
        self.assertEqual(screen.screen_text(text), [])
        # End review: the exemption once blanked a whole token, hiding a real value next to a stand-in.
        self.assertTrue(screen.screen_text("standin-1,alice.moreno@dealer.example.net"))
        self.assertTrue(screen.screen_text("password=standin-hunter2xyz"))

    def test_card_numbers_need_the_checksum(self):
        self.assertTrue(screen.screen_text("card 5425 2334 3010 9903"))
        self.assertFalse(screen.screen_text("order 5425 2334 3010 9904"))


if __name__ == "__main__":
    unittest.main()
