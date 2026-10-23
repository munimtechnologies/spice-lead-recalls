#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for coumarin_infant (no network, no CFIA download). Validates the TDI
arithmetic, the infant-cereal and children's-cereal selection, the scenario counts and the
pre-registered grading on small hand-computed CSV fixtures."""
import csv
import io
import unittest

import coumarin_eu_limits as cel
import coumarin_infant as ci


class TestArithmetic(unittest.TestCase):
    def test_thresholds(self):
        # 0.1 mg/kg bw/day x 8 kg = 0.8 mg/day; 0.8 mg / 0.030 kg = 26.67 mg/kg.
        self.assertAlmostEqual(ci.threshold_ppm(8.0, 30.0), 26.6667, places=3)
        self.assertAlmostEqual(ci.threshold_ppm(8.0, 60.0), 13.3333, places=3)
        self.assertAlmostEqual(ci.threshold_ppm(8.0, 15.0), 53.3333, places=3)

    def test_pct_tdi(self):
        self.assertAlmostEqual(ci.pct_tdi(10.0, 8.0, 30.0), 37.5)
        self.assertAlmostEqual(ci.pct_tdi(ci.threshold_ppm(8.0, 30.0), 8.0, 30.0), 100.0)
        self.assertAlmostEqual(ci.pct_tdi(0.0, 8.0, 60.0), 0.0)

    def test_nearest_rank(self):
        self.assertEqual(ci.nearest_rank([1, 2, 3, 4, 5, 6], 0.9), 6)
        self.assertEqual(ci.nearest_rank(list(range(1, 11)), 0.9), 9)
        self.assertIsNone(ci.nearest_rank([], 0.9))

    def test_scenarios_are_the_preregistered_ones(self):
        self.assertEqual(ci.SCENARIOS, {"S1": (8.0, 30.0), "S2": (8.0, 60.0), "S3": (8.0, 15.0)})
        self.assertEqual(ci.TDI_MG_PER_KG_BW, 0.1)


HEADER = ["Sample No.", "Region - Région", "Origin", "Product",
          "Result - Résultat", "Unit - Unité"]
FIXTURE = [
    ["1", "ONTARIO", "CANADA", "Infant Food - Cereal", "ND", "mg/kg"],
    ["2", "ONTARIO", "CANADA", "Infant Food - Cereal", "0.5", "mg/kg"],
    ["3", "WEST", "UNITED STATES", "Infant Food - Cereal", "2.0", "mg/kg"],
    ["4", "WEST", "CANADA", "Infant Food - Cereal", "3.0", "mg/kg"],
    ["5", "QUEBEC", "CANADA", "Infant Food - Cereal", "14.0", "mg/kg"],
    ["6", "QUEBEC", "CANADA", "Infant Food - Cereal", "30.0", "mg/kg"],
    ["7", "ATLANTIC", "CANADA", "Infant Food - Cereal", "", "mg/kg"],
    ["8", "WEST", "CANADA", "Cereal - Children", "2.0", "mg/kg"],
    ["9", "WEST", "CANADA", "Cereal - Children", "4.0", "mg/kg"],
    ["10", "WEST", "CANADA", "Cereal - Children", "6.0", "mg/kg"],
    ["11", "QUEBEC", "UNITED KINGDOM", "Spice - Mixed", "2510", "mg/kg"],
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
        self.s = ci.summarise(fixture_rows())

    def test_counts(self):
        self.assertEqual(self.s["n_rows"], 10)               # the blank infant row is not measured
        self.assertAlmostEqual(self.s["pooled_max_ppm"], 2510.0)
        self.assertEqual(self.s["infant_rows"], 7)
        self.assertEqual(self.s["infant"]["n"], 6)
        self.assertEqual(self.s["infant_units"], {"mg/kg": 6})

    def test_infant_stats(self):
        inf = self.s["infant"]
        self.assertEqual(inf["n_detected"], 5)                # ND counts as 0, not detected
        self.assertAlmostEqual(inf["share_detected"], 5 / 6)
        self.assertAlmostEqual(inf["ppm_median"], 2.5)        # (2.0 + 3.0) / 2
        self.assertAlmostEqual(inf["ppm_p90"], 30.0)
        self.assertAlmostEqual(inf["ppm_max"], 30.0)
        self.assertEqual(inf["n_over_eu_cereal_20"], 1)

    def test_children_cereal_median(self):
        self.assertEqual(self.s["child_cereal"]["n"], 3)
        self.assertAlmostEqual(self.s["child_cereal"]["ppm_median"], 4.0)

    def test_scenarios(self):
        sc = self.s["scenarios"]
        self.assertEqual(sc["S1"]["n_over_tdi"], 1)           # 30 > 26.67; 14 is not
        self.assertEqual(sc["S2"]["n_over_tdi"], 2)           # 14 and 30 > 13.33
        self.assertEqual(sc["S3"]["n_over_tdi"], 0)           # nothing > 53.33
        self.assertAlmostEqual(sc["S1"]["share_over_tdi"], 1 / 6)
        self.assertAlmostEqual(sc["S1"]["max_pct_tdi"], 112.5)
        self.assertAlmostEqual(sc["S2"]["max_pct_tdi"], 225.0)
        self.assertAlmostEqual(sc["S3"]["max_pct_tdi"], 56.25)


class TestCp1252MicroGramFile(unittest.TestCase):
    """Mirrors the real file: cp1252 bytes, French accents, unit written with the micro sign."""

    def setUp(self):
        text = ("Product,Origin,Region - Région,Result - Résultat,Unit - Unité\r\n"
                "Infant Food - Cereal,CANADA,ONTARIO,27.0,µg/g\r\n"
                "Infant Food - Cereal,CANADA,WEST,26.6,µg/g\r\n"
                "Cereal - Children,CANADA,WEST,3.4,µg/g\r\n")
        self.s = ci.summarise(cel.parse_rows(text.encode("cp1252")))

    def test_values_are_not_divided(self):
        self.assertAlmostEqual(self.s["infant"]["ppm_max"], 27.0)
        self.assertEqual(self.s["infant_units"], {"ug/g": 2})

    def test_threshold_edge(self):
        self.assertEqual(self.s["scenarios"]["S1"]["n_over_tdi"], 1)   # 27.0 > 26.67 > 26.6


def stats(**over):
    s = {"n_rows": 749, "pooled_max_ppm": 2510.0, "infant_rows": 52,
         "infant": {"n": 52, "n_detected": 50, "share_detected": 50 / 52, "ppm_median": 2.0},
         "infant_units": {"ug/g": 52},
         "child_cereal": {"ppm_median": 3.4},
         "scenarios": {"S1": {"share_over_tdi": 1 / 52, "n_over_tdi": 1},
                       "S2": {"share_over_tdi": 5 / 52, "n_over_tdi": 5}}}
    s.update(over)
    return s


class TestGrade(unittest.TestCase):
    def test_grade_on_fixture(self):
        preds = {p["id"]: p for p in ci.grade(ci.summarise(fixture_rows()))}
        self.assertFalse(preds["G0"]["met"])   # 10 rows, far below 740
        self.assertFalse(preds["P1"]["met"])   # 1/6 = 0.167 > 0.10
        self.assertFalse(preds["P2"]["met"])   # 2/6 = 0.333 > 0.30
        self.assertTrue(preds["P3"]["met"])    # 2.5 < 4.0
        self.assertTrue(preds["P4"]["met"])    # 5/6 = 0.833 in [0.80, 1.0]

    def test_grade_all_met_on_realistic_stats(self):
        preds = {p["id"]: p for p in ci.grade(stats())}
        self.assertEqual([p for p in preds if not preds[p]["met"]], [])

    def test_zero_over_tdi_meets_p1_not_p2(self):
        sc = {"S1": {"share_over_tdi": 0.0, "n_over_tdi": 0},
              "S2": {"share_over_tdi": 0.0, "n_over_tdi": 0}}
        preds = {p["id"]: p for p in ci.grade(stats(scenarios=sc))}
        self.assertTrue(preds["P1"]["met"])
        self.assertFalse(preds["P2"]["met"])

    def test_g0_fails_on_wrong_infant_count(self):
        preds = {p["id"]: p for p in ci.grade(stats(infant_rows=51))}
        self.assertFalse(preds["G0"]["met"])

    def test_g0_fails_on_unit_mismatch(self):
        preds = {p["id"]: p for p in ci.grade(stats(infant_units={"ug/g": 50, "ug/kg": 2}))}
        self.assertFalse(preds["G0"]["met"])

    def test_g0_fails_on_the_0_1_0_unit_bug(self):
        preds = {p["id"]: p for p in ci.grade(stats(pooled_max_ppm=2.51))}
        self.assertFalse(preds["G0"]["met"])

    def test_p3_needs_strictly_lower_median(self):
        inf = {"n": 52, "n_detected": 50, "share_detected": 50 / 52, "ppm_median": 3.4}
        preds = {p["id"]: p for p in ci.grade(stats(infant=inf))}
        self.assertFalse(preds["P3"]["met"])


if __name__ == "__main__":
    unittest.main()
