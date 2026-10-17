"""Offline tests for cr_ceiling_stress.py (standard library only).

Recomputes the ceiling-inflation stress test from the committed
data/cr_baseline.csv, checks it against the committed data/cr_ceiling_stress.csv,
and pins the graded result of the pre-registered predictions H1-H4 in
docs/cr-ceiling-stress-0.1.0-prereg.md (H1-H3 met, H4 failed)."""
import csv
import math
import os
import tempfile
import unittest

import cr_ceiling_stress as cs

HERE = os.path.dirname(os.path.abspath(__file__))
COMMITTED = os.path.join(HERE, "data", "cr_ceiling_stress.csv")


class StressTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = cs.load_rows(cs.LOCAL)
        cls.res = cs.analyse(cls.rows)
        with open(COMMITTED, encoding="utf-8") as f:
            cls.committed = list(csv.DictReader(f))

    def test_committed_csv_matches_recomputation(self):
        robust = self.res["robust"]
        self.assertEqual(len(self.committed), len(robust))
        for got, row in zip(robust, self.committed):
            self.assertEqual(row["lead_row_id"], got["lead_row_id"])
            self.assertEqual(row["chromium_row_id"], got["chromium_row_id"])
            self.assertEqual(row["product_name"], got["product_name"])
            self.assertTrue(math.isclose(float(row["edge_ppm"]), got["edge_ppm"], abs_tol=1e-9))
            self.assertTrue(math.isclose(float(row["highest_ceiling_ppm"]),
                                         got["highest_ceiling_ppm"], abs_tol=1e-9))
            self.assertTrue(math.isclose(float(row["k"]), got["k"], abs_tol=1e-4),
                            (row["product_name"], row["k"], got["k"]))
            self.assertEqual(row["survives_2x"], str(got["survives_2x"]))
            self.assertEqual(row["survives_5x"], str(got["survives_5x"]))

    def test_h1_sanity(self):
        self.assertEqual(self.res["n_total"], 34)
        self.assertEqual(self.res["n_robust"], 32)
        self.assertTrue(all(d["k"] > 1.0 for d in self.res["robust"]))
        self.assertNotIn("coriander", {d["matrix"] for d in self.res["robust"]})

    def test_h2_most_fragile_is_algerian_turmeric(self):
        mf = self.res["most_fragile"]
        self.assertEqual((mf["product_name"], mf["purchase_country"]), ("Turmeric", "ALGERIA"))
        self.assertLessEqual(abs(mf["k"] - 1.247), 0.003)

    def test_h3_doubling_leaves_at_least_24(self):
        self.assertGreaterEqual(self.res["survival"][2.0], 24)
        self.assertEqual(self.res["survival"][2.0], 30)

    def test_h4_monotone_but_tenfold_bound_fails(self):
        counts = [self.res["survival"][s] for s in cs.SCALES]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertEqual(counts, [31, 31, 30, 30, 29, 24])
        # Pre-registered "at most 8 at 10x" is NOT met: 24 survive.
        self.assertGreater(self.res["survival"][10.0], 8)

    def test_write_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.csv")
            cs.write_csv(self.res, p)
            with open(p, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        self.assertEqual([r["lead_row_id"] for r in rows],
                         [r["lead_row_id"] for r in self.committed])


if __name__ == "__main__":
    unittest.main()
