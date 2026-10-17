"""Self-contained check of docs/speciation-candidates-0.1.0.md (no network, stdlib only).

Recomputes the Cr(VI) speciation candidate list straight from the committed
data/cr_ceiling_stress.csv and data/cr_baseline.csv, and pins the three pairs and their
numbers that the sheet names. The selection rule is fixed: the robust pairs with
k = edge_ppm / highest_ceiling_ppm < 5. Apache-2.0. MV2 of Munim, Inc.
"""
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
STRESS = os.path.join(HERE, "data", "cr_ceiling_stress.csv")
BASELINE = os.path.join(HERE, "data", "cr_baseline.csv")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@unittest.skipUnless(os.path.exists(STRESS), "cr_ceiling_stress.csv not present")
class TestCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load(STRESS)
        for r in cls.rows:
            r["k_calc"] = float(r["edge_ppm"]) / float(r["highest_ceiling_ppm"])
        # candidates = robust pairs with k < 5, in ascending k
        cls.cands = sorted((r for r in cls.rows if r["k_calc"] < 5.0),
                           key=lambda r: r["k_calc"])

    def test_thirty_two_robust_pairs(self):
        self.assertEqual(len(self.rows), 32)

    def test_k_matches_reported(self):
        for r in self.rows:
            self.assertAlmostEqual(r["k_calc"], float(r["k"]), places=3)

    def test_exactly_three_candidates(self):
        self.assertEqual(len(self.cands), 3)

    def test_candidates_are_the_named_three(self):
        got = [(r["product_name"], r["purchase_country"]) for r in self.cands]
        self.assertEqual(got, [
            ("Turmeric", "ALGERIA"),
            ("Spice Mix", "BANGLADESH"),
            ("Raz El Hanout", "ALGERIA"),
        ])

    def test_candidate_k_values(self):
        ks = [round(r["k_calc"], 4) for r in self.cands]
        self.assertEqual(ks, [1.2465, 1.9406, 3.9534])

    def test_k_below_5_matches_survives_5x_false(self):
        for r in self.rows:
            below5 = r["k_calc"] < 5.0
            self.assertEqual(below5, r["survives_5x"] == "False")

    def test_first_two_fail_a_2x_inflation(self):
        self.assertEqual([r["survives_2x"] for r in self.cands[:2]], ["False", "False"])
        self.assertEqual(self.cands[2]["survives_2x"], "True")  # Raz El Hanout

    def test_median_k_far_above_candidates(self):
        ks = sorted(r["k_calc"] for r in self.rows)
        median = (ks[15] + ks[16]) / 2
        self.assertGreater(median, 50.0)


@unittest.skipUnless(os.path.exists(BASELINE), "cr_baseline.csv not present")
class TestBaselineValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_id = {r["lead_row_id"]: r for r in load(BASELINE)}

    def test_lab_values_in_sheet(self):
        # (lead_row_id, Pb ppm, Cr ppm) as printed in the candidate table
        for rid, pb, cr in (("2968", 20.0, 6.1), ("2156", 170.0, 38.0), ("3034", 2200.0, 310.0)):
            row = self.by_id[rid]
            self.assertEqual(row["baseline_verdict"], "robust")
            self.assertAlmostEqual(float(row["lead_ppm"]), pb, places=2)
            self.assertAlmostEqual(float(row["chromium_ppm"]), cr, places=2)


if __name__ == "__main__":
    unittest.main()
