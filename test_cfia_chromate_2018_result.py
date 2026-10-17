"""Pins every headline figure in docs/cfia-chromate-2018-0.1.0-result.md.

Self-contained: reads only the committed frozen per-sample table and recomputes
the pre-registered grade from it. No repo module import, stdlib only.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "cfia_chromate_2018_samples.csv")

# spice matrices that have their own published natural-chromium ceiling
CEILING_MATRICES = {"turmeric", "cinnamon", "chili/paprika", "cumin", "coriander"}


def rows():
    with open(CSV, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


class ChromateResultTest(unittest.TestCase):
    def setUp(self):
        self.r = rows()

    def test_sample_count(self):
        self.assertEqual(len(self.r), 131)

    def test_p1_over_ceiling(self):
        # samples of a spice with its own ceiling, and how many exceed it
        with_ceiling = [x for x in self.r if x["matrix"] in CEILING_MATRICES]
        self.assertEqual(len(with_ceiling), 81)
        over = [x for x in with_ceiling if x["over_ceiling"] == "1"]
        self.assertEqual(len(over), 1)
        self.assertEqual(over[0]["sample"], "C2018CLAS00046")
        self.assertEqual(over[0]["product"], "Cumin")
        self.assertEqual(over[0]["origin"], "INDIA")
        # genuinely high chromium and a positive spot test, but negligible lead
        self.assertAlmostEqual(float(over[0]["cr"]), 16.91)
        self.assertAlmostEqual(float(over[0]["pb"]), 0.52)
        self.assertEqual(over[0]["spot"], "Positive/Positif")

    def test_p2_cr_over_859(self):
        hi_cr = [x for x in self.r if float(x["cr"]) > 8.59]
        self.assertEqual(len(hi_cr), 1)

    def test_p3_band_without_floor(self):
        # molar Pb:Cr band alone (no lead floor) is not specific: 21 clean samples
        band = [x for x in self.r if x["band"] == "1"]
        self.assertEqual(len(band), 21)
        # every band sample has little lead and a negative spot test
        for x in band:
            self.assertLess(float(x["pb"]), 5.0)
            self.assertEqual(x["spot"], "Negative/Négatif")

    def test_p4_published_screen_flags_none(self):
        flagged = [x for x in self.r if float(x["pb"]) >= 18.0 and x["band"] == "1"]
        self.assertEqual(len(flagged), 0)
        self.assertLess(max(float(x["pb"]) for x in self.r), 18.0)

    def test_p5_lead_tail(self):
        hi_pb = [x for x in self.r if float(x["pb"]) >= 2.0]
        self.assertEqual(len(hi_pb), 6)
        self.assertLess(len(hi_pb) / len(self.r), 0.083)

    def test_spot_positive_count(self):
        pos = [x for x in self.r if x["spot"] == "Positive/Positif"]
        self.assertEqual(len(pos), 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
