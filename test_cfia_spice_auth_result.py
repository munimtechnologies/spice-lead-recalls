"""Pins every headline figure in docs/cfia-spice-auth-0.1.0-result.md.

Self-contained: reads only the committed frozen per-sample table (the sealed
compute run's output) and recomputes the pre-registered grade from it. No repo
module import, stdlib only.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "cfia_spice_auth_rows.csv")

SOUTH_ASIA = {"INDIA", "PAKISTAN", "BANGLADESH", "SRI LANKA", "NEPAL"}


def rows():
    with open(CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class SpiceAuthResultTest(unittest.TestCase):
    def setUp(self):
        self.r = rows()

    def test_row_and_assessment_counts(self):
        self.assertEqual(len(self.r), 823)
        codes = {}
        for x in self.r:
            codes[x["assessment_raw"].strip()] = codes.get(x["assessment_raw"].strip(), 0) + 1
        self.assertEqual(codes["S"], 738)
        self.assertEqual(codes["U-I"], 57)
        self.assertEqual(codes["INV"], 28)

    def test_p1_p2_no_lead_chromate(self):
        self.assertEqual(sum(int(x["lead"]) for x in self.r), 0)

    def test_p3_fillers_beat_lead_among_failures(self):
        u = [x for x in self.r if x["assessment_raw"].strip() == "U-I"]
        self.assertEqual(len(u), 57)
        self.assertEqual(sum(int(x["filler"]) for x in u), 53)
        self.assertEqual(sum(int(x["lead"]) for x in u), 0)

    def test_filler_total(self):
        self.assertEqual(sum(int(x["filler"]) for x in self.r), 80)

    def test_dye_flags(self):
        dye = [x for x in self.r if int(x["dye"]) == 1]
        self.assertEqual(len(dye), 5)
        turmeric = [x for x in dye if x["spice"] == "turmeric"]
        cinnamon = [x for x in dye if x["spice"] == "cinnamon"]
        self.assertEqual(len(turmeric), 4)
        self.assertEqual(len(cinnamon), 1)
        # none of the dye-flagged turmerics is declared from South Asia
        for x in turmeric:
            self.assertNotIn(x["origin"].strip().upper(), SOUTH_ASIA)

    def test_no_georgia(self):
        georgia = [x for x in self.r if "GEORGIA" in x["origin"].strip().upper()]
        self.assertEqual(len(georgia), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
