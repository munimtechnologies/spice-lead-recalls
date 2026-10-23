#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for coumarin_eu_limits (no network, no CFIA download). Validates the
concentration parse (including the 0.1.1 unit fix), the EU-analogue classifier, the per-group
summary and the pre-registered grading on small hand-computed CSV fixtures."""
import csv
import io
import unittest

import coumarin_eu_limits as cel


class TestParsePpm(unittest.TestCase):
    def test_plain_mg_kg(self):
        self.assertAlmostEqual(cel.parse_ppm("5", "mg/kg"), 5.0)
        self.assertAlmostEqual(cel.parse_ppm("2510", "mg/kg"), 2510.0)
        self.assertAlmostEqual(cel.parse_ppm("12.3", "ppm"), 12.3)
        self.assertAlmostEqual(cel.parse_ppm("  7.0 ", "mg/kg"), 7.0)

    def test_decimal_comma(self):
        self.assertAlmostEqual(cel.parse_ppm("1,5", "mg/kg"), 1.5)

    def test_ppb_conversion(self):
        self.assertAlmostEqual(cel.parse_ppm("2000", "ppb"), 2.0)
        self.assertAlmostEqual(cel.parse_ppm("2000", "µg/kg"), 2.0)
        self.assertAlmostEqual(cel.parse_ppm("2000", "ug/kg"), 2.0)
        self.assertAlmostEqual(cel.parse_ppm("2000", "ng/g"), 2.0)

    def test_microgram_per_gram_is_mg_per_kg(self):
        # 0.1.1 fix: CFIA's 2013-14 file reports ug/g (= mg/kg); 0.1.0 divided it by 1000.
        self.assertAlmostEqual(cel.parse_ppm("2510", "µg/g"), 2510.0)
        self.assertAlmostEqual(cel.parse_ppm("12.2", "μg/g"), 12.2)
        self.assertAlmostEqual(cel.parse_ppm("5.6", "ug/g"), 5.6)
        self.assertAlmostEqual(cel.parse_ppm("5.6", "µg/g (ppm)"), 5.6)

    def test_larger_units(self):
        self.assertAlmostEqual(cel.parse_ppm("2.51", "mg/g"), 2510.0)
        self.assertAlmostEqual(cel.parse_ppm("2.51", "g/kg"), 2510.0)
        self.assertAlmostEqual(cel.parse_ppm("0.25", "%"), 2500.0)

    def test_unrecognised_unit_taken_as_mg_kg(self):
        self.assertIsNone(cel.unit_factor("furlongs"))
        self.assertAlmostEqual(cel.parse_ppm("7", "furlongs"), 7.0)

    def test_non_detect_is_zero(self):
        for tok in ("ND", "N.D.", "trace", "<0.1", "<LOD", "NQ"):
            self.assertEqual(cel.parse_ppm(tok, "mg/kg"), 0.0, tok)

    def test_blank_and_none(self):
        self.assertIsNone(cel.parse_ppm("", "mg/kg"))
        self.assertIsNone(cel.parse_ppm(None))


class TestClassify(unittest.TestCase):
    CASES = {
        "Baked Goods": ("baked-goods", "fine-bakery"),
        "Bakery Product - Cookie": ("cookie", "fine-bakery"),
        "Bakery Product - English Muffin": ("muffin", "fine-bakery"),
        "Bakery Product - Bagel": ("bread", "out-of-scope"),
        "Bakery Product - Bread": ("bread", "out-of-scope"),
        "Bakery Product - Bread - Other": ("bread", "out-of-scope"),
        "Baking Mixes": ("mix", "out-of-scope"),
        "Dried mixes": ("mix", "out-of-scope"),
        "Cereal - Adult": ("cereal", "breakfast-cereal"),
        "Cereal - Children": ("cereal", "breakfast-cereal"),
        "Infant Food - Cereal": ("infant", "out-of-scope"),
        "Oatmeal": ("oatmeal", "breakfast-cereal"),
        "Granola/Cereal Bar": ("bar", "out-of-scope"),
        "Spice - Mixed": ("spice", "out-of-scope"),
        "Tea - Herbal": ("tea", "out-of-scope"),
    }

    def test_classify_and_group(self):
        for product, (subcat, group) in self.CASES.items():
            self.assertEqual(cel.classify(product), subcat, product)
            self.assertEqual(cel.group_of(cel.classify(product)), group, product)


HEADER = ["Sample No.", "Region - Région", "Origin", "Product",
          "Result - Résultat", "Unit - Unité"]
FIXTURE = [
    ["1", "ATLANTIC", "CANADA", "Baked Goods", "5", "mg/kg"],
    ["2", "ATLANTIC", "CANADA", "Baked Goods", "10", "mg/kg"],
    ["3", "ONTARIO", "UNITED STATES", "Bakery Product - Cookie", "20", "mg/kg"],
    ["4", "ONTARIO", "CANADA", "Bakery Product - Bread", "1000", "mg/kg"],
    ["5", "WEST", "CANADA", "Cereal - Adult", "5", "mg/kg"],
    ["6", "WEST", "CANADA", "Cereal - Adult", "10", "mg/kg"],
    ["7", "WEST", "CANADA", "Cereal - Children", "15", "mg/kg"],
    ["8", "WEST", "UNITED STATES", "Cereal - Children", "25", "mg/kg"],
    ["9", "QUEBEC", "CANADA", "Oatmeal", "30", "mg/kg"],
    ["10", "QUEBEC", "UNITED KINGDOM", "Spice - Mixed", "2510", "mg/kg"],
    ["11", "ONTARIO", "UNITED STATES", "Tea - Herbal", "ND", "mg/kg"],
    ["12", "ONTARIO", "UNITED STATES", "Infant Food - Cereal", "<0.1", "mg/kg"],
    ["13", "ONTARIO", "CANADA", "Cereal - Adult", "8", "mg/kg"],
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
        self.s = cel.summarise(fixture_rows())

    def test_counts(self):
        self.assertEqual(self.s["n_rows"], 13)
        self.assertAlmostEqual(self.s["pooled_max_ppm"], 2510.0)

    def test_unit_census(self):
        self.assertEqual(self.s["units"], {"mg/kg": 13})
        self.assertEqual(self.s["n_unrecognised_unit"], 0)

    def test_fine_bakery(self):
        fb = self.s["fine_bakery"]
        self.assertEqual(fb["n"], 3)
        self.assertEqual(fb["n_over_limit"], 1)             # only 20 > 15
        self.assertAlmostEqual(fb["share_over_all"], 1 / 3)

    def test_cereal_core(self):
        cc = self.s["cereal_core"]
        self.assertEqual(cc["n"], 5)                        # excludes oatmeal + infant
        self.assertEqual(cc["n_over_limit"], 1)             # only 25 > 20
        self.assertAlmostEqual(cc["share_over_all"], 0.2)

    def test_oatmeal_and_combined(self):
        self.assertEqual(self.s["oatmeal"]["n"], 1)
        self.assertAlmostEqual(self.s["oatmeal"]["share_over_all"], 1.0)
        ca = self.s["cereal_all"]
        self.assertEqual(ca["n"], 6)
        self.assertEqual(ca["n_over_limit"], 2)             # 25 and 30


class TestCp1252MicroGramFile(unittest.TestCase):
    """Mirrors the real file: cp1252 bytes, French accents, unit written with the micro sign."""

    def setUp(self):
        text = ("Product,Origin,Region - Région,Result - Résultat,Unit - Unité\r\n"
                "Spice - Mixed,CANADA,ONTARIO,2260,µg/g\r\n"
                "Baked Goods,UNKNOWN,ATLANTIC,83.3,µg/g\r\n"
                "Baked Goods,UNKNOWN,WEST,14.6,µg/g\r\n"
                "Cereal - Adult,UNITED STATES,WEST,70.7,µg/g\r\n"
                "Cereal - Adult,UNITED STATES,WEST,19.8,µg/g\r\n")
        self.rows = cel.parse_rows(text.encode("cp1252"))
        self.s = cel.summarise(self.rows)

    def test_values_are_not_divided(self):
        self.assertAlmostEqual(self.s["pooled_max_ppm"], 2260.0)
        self.assertEqual([round(r["ppm"], 1) for r in self.rows], [2260.0, 83.3, 14.6, 70.7, 19.8])

    def test_over_limit_counts(self):
        self.assertEqual(self.s["fine_bakery"]["n_over_limit"], 1)   # 83.3 > 15; 14.6 is not
        self.assertEqual(self.s["cereal_core"]["n_over_limit"], 1)   # 70.7 > 20; 19.8 is not

    def test_unit_census(self):
        self.assertEqual(self.s["units"], {"ug/g": 5})
        self.assertEqual(self.s["n_unrecognised_unit"], 0)


class TestGrade(unittest.TestCase):
    def test_grade_on_fixture(self):
        preds = {p["id"]: p for p in cel.grade(cel.summarise(fixture_rows()))}
        self.assertFalse(preds["G0"]["met"])   # n=13 far below 740
        self.assertTrue(preds["P1"]["met"])    # fine share 0.333 in [0.20, 0.50]
        self.assertTrue(preds["P2"]["met"])    # cereal-core share 0.2 in [0.03, 0.22]
        self.assertTrue(preds["P3"]["met"])    # 0.333 > 0.2

    def test_grade_g0_passes_on_realistic_stats(self):
        stats = {
            "n_rows": 745, "pooled_max_ppm": 2510.0,
            "fine_bakery": {"share_over_all": 0.33, "n": 100, "n_over_limit": 33},
            "cereal_core": {"share_over_all": 0.09, "n": 136, "n_over_limit": 12},
        }
        preds = {p["id"]: p for p in cel.grade(stats)}
        self.assertTrue(preds["G0"]["met"])
        self.assertTrue(preds["P1"]["met"])
        self.assertTrue(preds["P2"]["met"])
        self.assertTrue(preds["P3"]["met"])

    def test_grade_g0_fails_out_of_range_max(self):
        stats = {
            "n_rows": 745, "pooled_max_ppm": 5000.0,
            "fine_bakery": {"share_over_all": 0.33, "n": 100, "n_over_limit": 33},
            "cereal_core": {"share_over_all": 0.09, "n": 136, "n_over_limit": 12},
        }
        preds = {p["id"]: p for p in cel.grade(stats)}
        self.assertFalse(preds["G0"]["met"])

    def test_grade_g0_fails_on_the_0_1_0_bug(self):
        # The 0.1.0 run: 749 rows, pooled max 2.51 (1000x too small) -> the gate must fail.
        stats = {
            "n_rows": 749, "pooled_max_ppm": 2.51,
            "fine_bakery": {"share_over_all": 0.0, "n": 100, "n_over_limit": 0},
            "cereal_core": {"share_over_all": 0.0, "n": 136, "n_over_limit": 0},
        }
        preds = {p["id"]: p for p in cel.grade(stats)}
        self.assertFalse(preds["G0"]["met"])


if __name__ == "__main__":
    unittest.main()
