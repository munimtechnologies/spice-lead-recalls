#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for coumarin_tea (no network, no CFIA download). Validates the per-cup dose and
budget arithmetic, the tea-bucket selection, the scenario counts and the pre-registered grading on
small hand-computed CSV fixtures."""
import csv
import io
import unittest

import coumarin_eu_limits as cel
import coumarin_tea as ct


class TestArithmetic(unittest.TestCase):
    def test_budget(self):
        self.assertAlmostEqual(ct.budget_mg(60.0), 6.0)
        self.assertAlmostEqual(ct.budget_mg(15.0), 1.5)

    def test_dose(self):
        self.assertAlmostEqual(ct.dose_mg(2430.0, 2.0, 1.0), 4.86)
        self.assertAlmostEqual(ct.dose_mg(2430.0, 4.0, 1.0), 9.72)
        self.assertAlmostEqual(ct.dose_mg(0.0, 2.0, 1.0), 0.0)

    def test_thresholds(self):
        # one cup = whole day's budget: budget_mg / (dry_kg * transfer).
        self.assertAlmostEqual(ct.threshold_ppm(60.0, 2.0, 1.0), 3000.0)
        self.assertAlmostEqual(ct.threshold_ppm(60.0, 4.0, 1.0), 1500.0)
        self.assertAlmostEqual(ct.threshold_ppm(15.0, 2.0, 1.0), 750.0)
        self.assertAlmostEqual(ct.threshold_ppm(15.0, 4.0, 1.0), 375.0)

    def test_pct_budget(self):
        self.assertAlmostEqual(ct.pct_budget(2430.0, 60.0, 2.0, 1.0), 81.0)
        self.assertAlmostEqual(ct.pct_budget(2430.0, 15.0, 2.0, 1.0), 324.0)
        self.assertAlmostEqual(ct.pct_budget(2430.0, 15.0, 4.0, 1.0), 648.0)
        # at the threshold concentration, one cup is exactly 100% of the budget.
        self.assertAlmostEqual(ct.pct_budget(ct.threshold_ppm(15.0, 2.0), 15.0, 2.0), 100.0)

    def test_nearest_rank(self):
        self.assertEqual(ct.nearest_rank([1, 2, 3, 4, 5, 6], 0.9), 6)
        self.assertEqual(ct.nearest_rank(list(range(1, 11)), 0.9), 9)
        self.assertIsNone(ct.nearest_rank([], 0.9))

    def test_scenarios_are_the_preregistered_ones(self):
        self.assertEqual(ct.SCENARIOS, {"A1": (60.0, 2.0, 1.0), "A2": (60.0, 4.0, 1.0),
                                        "C1": (15.0, 2.0, 1.0), "C2": (15.0, 4.0, 1.0)})
        self.assertEqual(ct.TDI_MG_PER_KG_BW, 0.1)


HEADER = ["Sample No.", "Region - Région", "Origin", "Product",
          "Result - Résultat", "Unit - Unité"]
FIXTURE = [
    ["1", "ONTARIO", "CANADA", "Tea - Herbal", "ND", "mg/kg"],
    ["2", "ONTARIO", "SRI LANKA", "Tea - Herbal", "0.3", "mg/kg"],
    ["3", "WEST", "INDIA", "Tea - Black", "400", "mg/kg"],
    ["4", "QUEBEC", "CHINA", "Tea - Green", "800", "mg/kg"],
    ["5", "QUEBEC", "CANADA", "Tea - Herbal", "1600", "mg/kg"],
    ["6", "ATLANTIC", "INDIA", "Tea - Black", "2430", "mg/kg"],
    ["7", "WEST", "CANADA", "Tea - White", "", "mg/kg"],
    ["8", "QUEBEC", "UNITED KINGDOM", "Spice - Mixed", "2510", "mg/kg"],
    ["9", "ONTARIO", "CANADA", "Infant Food - Cereal", "5.0", "mg/kg"],
]


def fixture_rows():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for r in FIXTURE:
        w.writerow(r)
    return cel.parse_rows(buf.getvalue().encode("utf-8"))


class TestSummarise(unittest.TestCase):
    def setUp(self):
        self.s = ct.summarise(fixture_rows())

    def test_counts(self):
        self.assertEqual(self.s["n_rows"], 8)            # 6 tea + spice + infant measured; blank not
        self.assertAlmostEqual(self.s["pooled_max_ppm"], 2510.0)
        self.assertEqual(self.s["tea_rows"], 7)          # includes the blank tea row
        self.assertEqual(self.s["tea"]["n"], 6)
        self.assertEqual(self.s["tea_units"], {"mg/kg": 6})

    def test_tea_stats(self):
        t = self.s["tea"]
        self.assertEqual(t["n_detected"], 5)             # ND counts as 0, not detected
        self.assertAlmostEqual(t["share_detected"], 5 / 6)
        self.assertAlmostEqual(t["ppm_min"], 0.0)
        self.assertAlmostEqual(t["ppm_median"], 600.0)   # (400 + 800) / 2
        self.assertAlmostEqual(t["ppm_max"], 2430.0)
        self.assertAlmostEqual(t["ppm_p90"], 2430.0)

    def test_scenario_counts(self):
        sc = self.s["scenarios"]
        self.assertEqual(sc["A1"]["n_over_tdi"], 0)      # nothing > 3000
        self.assertEqual(sc["A2"]["n_over_tdi"], 2)      # 1600, 2430 > 1500
        self.assertEqual(sc["C1"]["n_over_tdi"], 3)      # 800, 1600, 2430 > 750
        self.assertEqual(sc["C2"]["n_over_tdi"], 4)      # 400, 800, 1600, 2430 > 375
        self.assertAlmostEqual(sc["C2"]["share_over_tdi"], 4 / 6)
        self.assertAlmostEqual(sc["A1"]["max_pct_budget"], 81.0)
        self.assertAlmostEqual(sc["C1"]["max_pct_budget"], 324.0)
        self.assertAlmostEqual(sc["C2"]["max_pct_budget"], 648.0)
        self.assertAlmostEqual(sc["A1"]["max_dose_mg"], 4.86)


class TestCp1252MicroGramFile(unittest.TestCase):
    """Mirrors the real file: cp1252 bytes, French accents, unit written with the micro sign."""

    def setUp(self):
        text = ("Product,Origin,Region - Région,Result - Résultat,Unit - Unité\r\n"
                "Tea - Herbal,INDIA,ONTARIO,2430.0,µg/g\r\n"
                "Tea - Black,CHINA,WEST,760.0,µg/g\r\n"
                "Tea - Green,SRI LANKA,QUEBEC,370.0,µg/g\r\n")
        self.s = ct.summarise(cel.parse_rows(text.encode("cp1252")))

    def test_values_are_not_divided(self):
        self.assertAlmostEqual(self.s["tea"]["ppm_max"], 2430.0)   # not 2.43
        self.assertEqual(self.s["tea_units"], {"ug/g": 3})

    def test_threshold_edges(self):
        sc = self.s["scenarios"]
        self.assertEqual(sc["A2"]["n_over_tdi"], 1)      # only 2430 > 1500
        self.assertEqual(sc["C1"]["n_over_tdi"], 2)      # 2430, 760 > 750
        self.assertEqual(sc["C2"]["n_over_tdi"], 2)      # 2430, 760 > 375; 370 is not


def stats(**over):
    s = {"n_rows": 745, "pooled_max_ppm": 2510.0, "tea_rows": 115,
         "tea": {"n": 115, "n_detected": 114, "ppm_max": 2430.0},
         "tea_units": {"ug/g": 115},
         "scenarios": {
             "A1": {"n_over_tdi": 0, "share_over_tdi": 0.0, "threshold_ppm": 3000.0},
             "A2": {"n_over_tdi": 5, "share_over_tdi": 0.04, "threshold_ppm": 1500.0},
             "C1": {"n_over_tdi": 25, "share_over_tdi": 0.22, "threshold_ppm": 750.0},
             "C2": {"n_over_tdi": 52, "share_over_tdi": 0.45, "threshold_ppm": 375.0}}}
    s.update(over)
    return s


class TestGrade(unittest.TestCase):
    def test_grade_on_fixture(self):
        preds = {p["id"]: p for p in ct.grade(ct.summarise(fixture_rows()))}
        self.assertFalse(preds["G0"]["met"])   # 8 rows, far below 740
        self.assertTrue(preds["P1"]["met"])    # 0 adult cups over at 2 g
        self.assertFalse(preds["P2"]["met"])   # 2/6 = 0.333 > 0.12
        self.assertFalse(preds["P3"]["met"])   # 3/6 = 0.50 > 0.40
        self.assertTrue(preds["P4"]["met"])    # 4/6 = 0.667 in [0.25, 0.70]

    def test_grade_all_met_on_realistic_stats(self):
        preds = {p["id"]: p for p in ct.grade(stats())}
        self.assertEqual([p for p in preds if not preds[p]["met"]], [])

    def test_p1_fails_when_any_adult_cup_over(self):
        sc = stats()["scenarios"]
        sc["A1"] = {"n_over_tdi": 1, "share_over_tdi": 1 / 115, "threshold_ppm": 3000.0}
        preds = {p["id"]: p for p in ct.grade(stats(scenarios=sc))}
        self.assertFalse(preds["P1"]["met"])

    def test_p1_needs_nonempty_tea(self):
        preds = {p["id"]: p for p in ct.grade(stats(tea={"n": 0, "n_detected": 0, "ppm_max": None}))}
        self.assertFalse(preds["P1"]["met"])

    def test_g0_fails_on_wrong_tea_count(self):
        preds = {p["id"]: p for p in ct.grade(stats(tea_rows=114))}
        self.assertFalse(preds["G0"]["met"])

    def test_g0_fails_on_unit_mismatch(self):
        preds = {p["id"]: p for p in ct.grade(stats(tea_units={"ug/g": 113, "ug/kg": 2}))}
        self.assertFalse(preds["G0"]["met"])

    def test_g0_fails_on_the_unit_bug(self):
        # the 0.1.0-style /1000 bug: pooled max 2.51, tea max 2.43 - both out of the gate bands.
        preds = {p["id"]: p for p in ct.grade(
            stats(pooled_max_ppm=2.51, tea={"n": 115, "n_detected": 114, "ppm_max": 2.43}))}
        self.assertFalse(preds["G0"]["met"])

    def test_g0_fails_on_low_detection(self):
        preds = {p["id"]: p for p in ct.grade(
            stats(tea={"n": 115, "n_detected": 100, "ppm_max": 2430.0}))}
        self.assertFalse(preds["G0"]["met"])


if __name__ == "__main__":
    unittest.main()
