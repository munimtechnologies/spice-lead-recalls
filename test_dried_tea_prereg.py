# SPDX-License-Identifier: Apache-2.0
"""Report-only arithmetic of docs/dried-tea-2009-0.1.0-prereg.md (CFIA 2009-10 pesticide
residues and metals in dried tea). Needs no file: every figure is copied from the printed pages.
Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name."""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "docs", "dried-tea-2009-0.1.0-prereg.md")
TYPES = {"black": 24, "green": 41, "herbal/blends": 12, "oolong": 13, "white": 10}
VIOLATIONS = {"black": 2, "green": 18, "herbal/blends": 7, "oolong": 12, "white": 2}
PRINTED_PCT = {"black": 8, "green": 44, "herbal/blends": 58, "oolong": 92, "white": 20}
STREET = re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(Road|Street|Avenue|Lane|Drive|Boulevard)\b")


def read_doc():
    with open(DOC, encoding="utf-8") as fh:
        return fh.read()


class ReportArithmetic(unittest.TestCase):
    def test_r1_types_add_to_100(self):
        self.assertEqual(sum(TYPES.values()), 100)

    def test_r2_violations_add_to_41_and_compliance_59(self):
        self.assertEqual(sum(VIOLATIONS.values()), 41)
        self.assertEqual(100 - sum(VIOLATIONS.values()), 59)

    def test_r3_type_shares_round(self):
        for t, n in TYPES.items():
            self.assertLessEqual(VIOLATIONS[t], n, t)
            self.assertEqual(round(100 * VIOLATIONS[t] / n), PRINTED_PCT[t], t)

    def test_r4_detected_but_compliant(self):
        self.assertEqual(69 - 41, 28)
        self.assertEqual(100 - 69, 31)

    def test_r6_size_rules_out_one_row_per_pesticide(self):
        band_hi = 276 * 1024
        self.assertEqual(band_hi, 282624)
        self.assertEqual(275 * 1024, 281600)
        per_row = band_hi / (340 * 100)
        self.assertLess(per_row, 8.4)
        self.assertGreater(per_row, 8.3)


class Note(unittest.TestCase):
    def setUp(self):
        self.doc = read_doc()

    def test_marker_and_disclosure(self):
        self.assertIn("PREREG-MARKER: dried-tea-2009-0.1.0-prereg", self.doc)
        self.assertIn("Made with AI agents working in MV2's (Munim, Inc.) name", self.doc)
        self.assertTrue(self.doc.rstrip().endswith("MV2, Munim, Inc., mv2@munimtech.com"))
        self.assertNotRegex(self.doc, r"\bMIT\b")
        self.assertIsNone(STREET.search(self.doc))
        self.assertIsNotNone(STREET.search(" ".join(["12", "Example", "Road"])))

    def test_note_states_the_printed_figures(self):
        for phrase in ("24 black, 41 green, 12\n  herbal/blends, 13 oolong and 10 white",
                       "oolong 92% (12 of 13)", "herbal/blends 58% (7 of 12)",
                       "green 44% (18 of 41)", "white 20% (2 of 10)", "black 8% (2 of 24)",
                       "f21f016693b4608ff7059d28be35bb26", "more than 281,600 and at most 282,624",
                       "87% of its dried tea samples"):
            self.assertIn(phrase, self.doc, phrase)

    def test_items_present(self):
        for item in ("R1.", "R2.", "R3.", "R4.", "R5.", "R6.", "C1.", "C2.", "C3.", "C4.",
                     "C5.", "V1.", "V2.", "V3.", "V4.", "V5.", "V6."):
            self.assertIn("- " + item, self.doc, item)


if __name__ == "__main__":
    unittest.main()
