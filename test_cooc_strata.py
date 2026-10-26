#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for cooc_strata.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import math
import unittest

import cooc_strata as cs

RETAIL_HEAD = "sample,plan,function,origin,product,component,result_raw,ppb,detected\n"
FEED_HEAD = ("sid,year,province,region,species,feed_type,ingredient_type,ingredient_name,don_ppm,"
             "det_DON,det_OTA\n")


class TestParsing(unittest.TestCase):
    def test_retail_pairs_two_rows_per_sample(self):
        text = RETAIL_HEAD + (
            "S1,p,f,o,Wine,Deoxynivalenol,0,0.0,0\n"
            "S1,p,f,o,Wine,Ochratoxin A,0.5,0.5,1\n"
            "S2,p,f,o,Flour - Wheat,Deoxynivalenol,120,120.0,1\n"
            "S2,p,f,o,Flour - Wheat,Ochratoxin A,0.2,0.2,1\n"
            "S3,p,f,o,Raisin,Ochratoxin A,0,0.0,0\n")
        items, n_rows, n_samples = cs.retail_items(text)
        self.assertEqual((n_rows, n_samples), (5, 3))
        self.assertEqual(sorted(items), [("Flour - Wheat", True, True), ("Wine", True, False)])

    def test_feed_skips_untested_and_blank_names(self):
        text = FEED_HEAD + (
            "A,2000-2001,Quebec,East,M,S,Cereals,Corn,0.5,1,0\n"
            "B,2000-2001,Quebec,East,M,S,Cereals,,0.0,0,1\n"
            "C,2000-2001,Quebec,East,M,S,Cereals,\"Wheat, feed\",0.0,0,\n")
        items, n = cs.feed_items(text)
        self.assertEqual(n, 3)
        self.assertEqual(items, [("Corn", False, True), (cs.BLANK, True, False)])
        by_type, _ = cs.feed_items(text, key="ingredient_type")
        self.assertEqual([i[0] for i in by_type], ["Cereals", "Cereals"])

    def test_cells(self):
        items = [("x", True, True), ("x", True, False), ("y", False, True), ("y", False, False),
                 ("y", False, False)]
        self.assertEqual(cs.cells(items), (1, 1, 1, 2))
        self.assertEqual(cs.strata_tables(items), {"x": (1, 1, 0, 0), "y": (0, 0, 1, 2)})


class TestStatistics(unittest.TestCase):
    def test_mh_equals_common_or(self):
        mh, num, den = cs.mantel_haenszel([(10, 5, 5, 10), (10, 5, 5, 10)])
        self.assertAlmostEqual(mh, 4.0, places=12)
        self.assertAlmostEqual(num, 2 * 100 / 30, places=12)
        self.assertAlmostEqual(den, 2 * 25 / 30, places=12)

    def test_simpson_reversal(self):
        # Pooled association created purely by composition: each stratum has OR exactly 1.
        tabs = [(40, 10, 40, 10), (1, 9, 9, 81)]
        pooled = tuple(sum(x) for x in zip(*tabs))
        self.assertGreater(cs.odds_ratio(*pooled), 2.0)
        mh, _, _ = cs.mantel_haenszel(tabs)
        self.assertAlmostEqual(mh, 1.0, places=12)
        chi2, p = cs.cmh_test(tabs)
        self.assertEqual(chi2, 0.0)
        self.assertEqual(p, 1.0)

    def test_cmh_single_stratum(self):
        chi2, p = cs.cmh_test([(10, 5, 5, 10)])
        # Var = 15^4 / (30^2 * 29); X2 = (2.5 - 0.5)^2 / Var.
        self.assertAlmostEqual(chi2, 4 / (15 ** 4 / (900 * 29)), places=9)
        self.assertAlmostEqual(chi2, 2.062222, places=5)
        self.assertAlmostEqual(p, math.erfc(math.sqrt(chi2 / 2)), places=12)
        self.assertTrue(0.14 < p < 0.16)

    def test_cmh_ignores_degenerate_strata(self):
        base = cs.cmh_test([(10, 5, 5, 10)])
        more = cs.cmh_test([(10, 5, 5, 10), (0, 0, 3, 4), (1, 0, 0, 0)])
        self.assertAlmostEqual(base[0], more[0], places=12)
        self.assertEqual(cs.informative([(0, 0, 3, 4), (1, 0, 0, 0), (1, 1, 1, 1)]),
                         [(1, 1, 1, 1)])

    def test_mh_undefined(self):
        self.assertIsNone(cs.mantel_haenszel([(3, 0, 0, 4)])[0])

    def test_odds_ratio_haldane(self):
        self.assertAlmostEqual(cs.odds_ratio(2, 4, 3, 6), 1.0, places=12)
        self.assertAlmostEqual(cs.odds_ratio(0, 4, 3, 6), (0.5 * 6.5) / (4.5 * 3.5), places=12)


class TestGrading(unittest.TestCase):
    def fake(self, mh, p, pooled_or):
        return {"mh_or": mh, "cmh_p": p, "pooled_or": pooled_or}

    def test_all_met(self):
        gate = {"x": True}
        preds = cs.grade(self.fake(2.0, 0.001, 8.544642857142858),
                         self.fake(0.9, 0.4, 0.6970588235294117), None, gate)
        self.assertEqual([p["id"] for p in preds], ["G", "M1", "M2", "M3", "M4"])
        self.assertTrue(all(p["met"] for p in preds))

    def test_bounds(self):
        gate = {"x": True}
        preds = {p["id"]: p for p in cs.grade(self.fake(3.0, 0.2, 8.544642857142858),
                                              self.fake(0.6, 0.01, 0.6970588235294117),
                                              None, gate)}
        self.assertFalse(preds["M1"]["met"])   # 3.0 > sqrt(8.54) = 2.923
        self.assertFalse(preds["M2"]["met"])   # p 0.2
        self.assertFalse(preds["M3"]["met"])   # p 0.01 < 0.05
        self.assertFalse(preds["M4"]["met"])   # |ln 0.6| = 0.511 > |ln 0.697| = 0.361

    def test_gate_closed_grades_nothing(self):
        preds = cs.grade(self.fake(2.0, 0.001, 8.5), self.fake(0.9, 0.4, 0.7), None,
                         {"retail_pooled": False})
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["graded"] and not p["met"] for p in preds[1:]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
