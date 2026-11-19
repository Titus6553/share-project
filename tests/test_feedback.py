# tests/test_feedback.py
# Purpose: the feedback report holds only allowlisted values; any free text is refused.
# Non-goals: the layout of the printed report.
import unittest

import feedback

GOOD = ["--app", "codex-terminal", "--mode", "agent", "--plan", "unknown", "--os", "mac",
        "--step", "zip", "--outcome", "failed", "--category", "check-failed"]


class Feedback(unittest.TestCase):
    def test_allowlisted_report(self):
        text = feedback.report(feedback.parse(GOOD))
        for line in text.splitlines()[1:]:
            key, value = line.split(": ")
            self.assertIn(value, feedback.CHOICES[key])

    def test_free_text_refused(self):
        for bad in (GOOD[:-1] + ["ValueError at /Users/someone/project/calc.py"],
                    GOOD + ["--note", "anything"],
                    ["--app", "my-dealer-dashboard"] + GOOD[2:]):
            with self.assertRaises(ValueError):
                feedback.parse(bad)


if __name__ == "__main__":
    unittest.main()
