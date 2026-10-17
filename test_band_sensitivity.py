"""Offline tests for cr_band_sensitivity.py (standard library only).

Recomputes the band-edge and rounding sensitivity table from the committed
data/cr_baseline.csv and data/nyc_spice_pb_cr_pairs.csv, checks it against the
committed data/cr_band_sensitivity.csv, and pins every count quoted in
docs/cr-band-sensitivity-0.1.0.md."""
import csv
import math
import os
import tempfile
import unittest

import cr_band_sensitivity as bs

HERE = os.path.dirname(os.path.abspath(__file__))
COMMITTED = os.path.join(HERE, "data", "cr_band_sensitivity.csv")

ALGERIAN_TURMERIC = "2968"
RAZ_EL_HANOUT = "3034"
CORIANDERS = {"3282", "2290"}


class BandSensitivityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = bs.load_rows(bs.BASELINE)
        cls.pairs = bs.load_rows(bs.PAIRS)
        cls.res = bs.analyse(cls.baseline, cls.pairs)
        cls.by_id = {d["lead_row_id"]: d for d in cls.res["rows"]}
        with open(COMMITTED, encoding="utf-8") as fh:
            cls.committed = list(csv.DictReader(fh))

    def test_committed_csv_matches_recomputation(self):
        self.assertEqual(len(self.committed), len(self.res["rows"]))
        for got, row in zip(self.res["rows"], self.committed):
            for key in ("lead_row_id", "chromium_row_id", "product_name", "purchase_country",
                        "matrix", "verdict_r1_5", "verdict_r2", "verdict_r3",
                        "verdict_r2_worst_rounding"):
                self.assertEqual(row[key], str(got[key]), (row["lead_row_id"], key))
            for key in ("lead_ppm", "chromium_ppm", "highest_ceiling_ppm"):
                self.assertEqual(float(row[key]), got[key])
            self.assertTrue(math.isclose(float(row["molar_ratio_pb_cr"]),
                                         got["molar_ratio_pb_cr"], abs_tol=1e-9))
            for key in ("edge_r1_5", "edge_r2", "edge_r3", "edge_r2_worst_rounding"):
                self.assertTrue(math.isclose(float(row[key]), got[key], abs_tol=0.006),
                                (row["lead_row_id"], key, row[key], got[key]))
            if got["r_crit"] == "":
                self.assertEqual(row["r_crit"], "")
            else:
                self.assertTrue(math.isclose(float(row["r_crit"]), got["r_crit"], abs_tol=2e-4),
                                (row["lead_row_id"], row["r_crit"], got["r_crit"]))

    def test_operating_edge_reproduces_cr_baseline(self):
        for b in self.baseline:
            d = self.by_id[b["lead_row_id"]]
            self.assertTrue(math.isclose(d["edge_r2"], float(b["edge_ppm"]), abs_tol=0.006))
            self.assertEqual(d["verdict_r2"], b["baseline_verdict"])
            self.assertTrue(math.isclose(d["molar_ratio_pb_cr"], float(b["molar_ratio_pb_cr"]),
                                         abs_tol=1e-9))

    def test_counts_by_band_edge(self):
        self.assertEqual(self.res["counts"][1.5],
                         {"robust": 30, "unresolved": 3, "outside-band": 1})
        self.assertEqual(self.res["counts"][2.0], {"robust": 32, "unresolved": 2})
        self.assertEqual(self.res["counts"][3.0], {"robust": 32, "unresolved": 2})

    def test_tight_edge_moves_exactly_two_pairs(self):
        unresolved = {d["lead_row_id"] for d in self.res["rows"] if d["verdict_r1_5"] == "unresolved"}
        self.assertEqual(unresolved, CORIANDERS | {ALGERIAN_TURMERIC})
        outside = {d["lead_row_id"] for d in self.res["rows"] if d["verdict_r1_5"] == "outside-band"}
        self.assertEqual(outside, {RAZ_EL_HANOUT})

    def test_wide_edge_admits_no_new_pair(self):
        for r in bs.EDGES:
            self.assertEqual(self.res["entrants"][r], [])
        self.assertLess(abs(self.res["nearest_above_band_ratio"] - 3.207), 0.002)

    def test_r_crit(self):
        robust = [d for d in self.res["rows"] if d["verdict_r2"] == "robust"]
        tightest = max(robust, key=lambda d: d["r_crit"])
        self.assertEqual(tightest["lead_row_id"], RAZ_EL_HANOUT)
        self.assertLess(abs(tightest["r_crit"] - 1.8317), 2e-4)
        self.assertLess(abs(self.by_id[ALGERIAN_TURMERIC]["r_crit"] - 1.5587), 2e-4)
        self.assertEqual(sum(1 for d in robust if d["r_crit"] < 1.5), 30)
        for rid in CORIANDERS:
            self.assertEqual(self.by_id[rid]["r_crit"], "")

    def test_robust_ratios_sit_in_the_pigment_range(self):
        ratios = sorted(d["molar_ratio_pb_cr"] for d in self.res["rows"] if d["verdict_r2"] == "robust")
        self.assertEqual(len(ratios), 32)
        self.assertEqual(sum(1 for x in ratios if 1.0 <= x <= 1.4), 27)
        self.assertLess(abs((ratios[15] + ratios[16]) / 2 - 1.161), 1e-3)

    def test_r_crit_is_the_flip_point(self):
        b = next(r for r in self.baseline if r["lead_row_id"] == ALGERIAN_TURMERIC)
        pb, cr = float(b["lead_ppm"]), float(b["chromium_ppm"])
        hi, lo = float(b["highest_ceiling_ppm"]), float(b["lowest_ceiling_ppm"])
        rc = bs.r_crit(pb, cr, hi)
        self.assertEqual(bs.verdict(pb, cr, rc + 1e-6, hi, lo), "robust")
        self.assertEqual(bs.verdict(pb, cr, rc - 1e-3, hi, lo), "unresolved")

    def test_worst_case_rounding(self):
        self.assertEqual(self.res["worst_rounding_counts"], {"robust": 32, "unresolved": 2})
        d = self.by_id[ALGERIAN_TURMERIC]
        self.assertLess(abs(d["edge_r2_worst_rounding"] / d["highest_ceiling_ppm"] - 1.2076), 2e-3)

    def test_half_unit(self):
        self.assertEqual(bs.half_unit(20.0), 0.5)
        self.assertTrue(math.isclose(bs.half_unit(6.1), 0.05))
        self.assertEqual(bs.half_unit(2200.0), 50.0)
        self.assertEqual(bs.half_unit(78000.0), 500.0)
        self.assertTrue(math.isclose(bs.half_unit(0.52), 0.005))
        self.assertEqual(bs.half_unit(0.0), 0.0)

    def test_write_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.csv")
            bs.write_csv(self.res, p)
            with open(p, encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
        self.assertEqual([r["lead_row_id"] for r in rows],
                         [r["lead_row_id"] for r in self.committed])


if __name__ == "__main__":
    unittest.main()
