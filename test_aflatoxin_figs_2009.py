#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for aflatoxin_figs_2009.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import unittest

import aflatoxin_figs_2009 as af

# Header as in the CFIA file (15 columns).
HEAD = ["Sample No. – No. d’échantillon", "Region - Région", "Function", "Fonction", "Origin",
        "Origine", "Product", "Produit", "Date Sampled – Date d’échantillonage", "Type of test",
        "Type d’analyse", "Component", "Composant", "Result - Résultat", "Unit - Unité"]


def row(sample, origin, product, comp, value, unit="ppb"):
    cols = ["x"] * 15
    cols[0], cols[2], cols[4], cols[6], cols[8], cols[11], cols[13], cols[14] = (
        sample, "Import", origin, product, "02-Nov-09", comp, value, unit)
    return ",".join(cols)


def sample_rows(sample, origin, product, b1, b2, g1, g2, total):
    return [row(sample, origin, product, c, v)
            for c, v in zip(af.COMPONENTS, (b1, b2, g1, g2, total))]


MINI = "\n".join(
    [",".join(HEAD)]
    + sample_rows("S1", "TURKEY", "FIG", "10", "1.5", "2", "0", "13.5")
    + sample_rows("S2", "GREECE", "FIG", "0", "0", "0", "0", "0")
    + sample_rows("S3", "IRAN", "DATE", "0", "0", "0", "0", "0")
    + sample_rows("S4", "TURKEY", "FIG", "3", "0", "4", "0", "7")
) + "\n"


class TestParseAmount(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(af.parse_amount(""), (0.0, False, "blank"))
        self.assertEqual(af.parse_amount("ND"), (0.0, False, "text"))
        self.assertEqual(af.parse_amount("<0.2"), (0.0, False, "text"))
        self.assertEqual(af.parse_amount("0"), (0.0, False, "zero"))
        self.assertEqual(af.parse_amount("-1"), (None, False, "bad"))
        self.assertEqual(af.parse_amount("nan"), (None, False, "bad"))
        self.assertEqual(af.parse_amount(" 7.5 "), (7.5, True, "pos"))


class TestColumnsAndConstants(unittest.TestCase):
    def test_columns(self):
        c = af.find_columns(["﻿" + HEAD[0]] + HEAD[1:])
        self.assertEqual((c["sample"], c["region"], c["function"], c["origin"], c["product"],
                          c["date"], c["component"], c["value"], c["unit"]),
                         (0, 1, 2, 4, 6, 8, 11, 13, 14))

    def test_census_constants(self):
        self.assertEqual(sum(af.PRODUCT_ROWS.values()), 500)
        self.assertEqual(sum(af.ORIGIN_ROWS.values()), 500)
        self.assertEqual(len(af.ORIGIN_ROWS), 11)
        self.assertTrue(all(n % 5 == 0 for n in af.ORIGIN_ROWS.values()))
        self.assertEqual(len(af.COMPONENTS), 5)
        self.assertEqual(af.TOTAL, "Total Aflatoxins")

    def test_matches(self):
        self.assertTrue(af.matches(7.46, "7.5"))
        self.assertTrue(af.matches(78.7, "78.7"))
        self.assertFalse(af.matches(7.44, "7.5"))
        self.assertFalse(af.matches(None, "7.5"))
        self.assertEqual(af.half_unit("78.7"), 0.05)


class TestParse(unittest.TestCase):
    def setUp(self):
        self.samples, self.census = af.parse_text(MINI)
        self.recs = list(self.samples.values())

    def test_census(self):
        c = self.census
        self.assertEqual((c["n_rows"], c["distinct_samples"]), (20, 4))
        self.assertEqual(c["rows_per_sample"], {"5": 4})
        self.assertEqual(c["value_kinds"], {"pos": 7, "zero": 13})
        self.assertEqual(c["nonzero_cells"], 7)
        self.assertEqual(c["units"], {"ppb": 20})
        self.assertEqual(c["products"], {"FIG": 15, "DATE": 5})
        self.assertEqual(c["components"], {comp: 4 for comp in af.COMPONENTS})

    def test_records(self):
        s1 = self.samples["S1"]
        self.assertEqual((s1["product"], s1["origin"], s1["date"]), ("FIG", "TURKEY", "02-Nov-09"))
        self.assertEqual(s1["values"][af.TOTAL], 13.5)
        self.assertAlmostEqual(af.form_sum(s1), 13.5, places=12)
        self.assertEqual(af.largest_form(s1), af.B1)
        self.assertEqual(af.largest_form(self.samples["S4"]), af.G1)
        self.assertEqual(af.largest_form(self.samples["S2"]), af.B1)   # ties go to B1
        self.assertTrue(af.is_positive(s1))
        self.assertFalse(af.is_positive(self.samples["S3"]))
        self.assertEqual(af.eu_flags(s1), {"over_b1": True, "over_sum": True})
        self.assertEqual(af.eu_flags(self.samples["S4"]), {"over_b1": False, "over_sum": False})

    def test_analyse(self):
        a = af.analyse(self.recs)
        self.assertEqual([p["sample"] for p in a["positives"]], ["S1", "S4"])
        self.assertEqual((a["fig_pos"], a["date_pos"], a["n_positive"]), (2, 0, 2))
        self.assertEqual((a["total_min"], a["total_max"]), (7.0, 13.5))
        self.assertAlmostEqual(a["max_sum_gap"], 0.0, places=12)
        self.assertTrue(a["b1_in_all"])
        self.assertEqual((a["b1_largest"], a["origin_hits"], a["eu_any"], a["g1_pos"]),
                         (1, 2, 1, 2))
        self.assertEqual(a["by_product"], {"DATE": {"n": 1, "pos": 0}, "FIG": {"n": 3, "pos": 2}})
        self.assertEqual(a["product_origin"], {"FIG|TURKEY": 2, "FIG|GREECE": 1, "DATE|IRAN": 1})

    def test_sum_gap(self):
        bad = MINI.replace(",13.5,", ",14,")
        a = af.analyse(list(af.parse_text(bad)[0].values()))
        self.assertAlmostEqual(a["max_sum_gap"], 0.5, places=12)

    def test_gate_closes_and_grade_shape(self):
        gate = af.gate_checks(self.census, self.recs, True)
        self.assertTrue(gate["sha256"])
        self.assertFalse(gate["rows"])
        self.assertTrue(gate["one_row_per_component"])
        self.assertTrue(gate["labels_per_sample"])
        self.assertTrue(gate["unit"])
        self.assertTrue(gate["value_kinds"])
        self.assertFalse(gate["nonzero_cells"])
        preds = af.grade(af.analyse(self.recs), gate)
        self.assertEqual([p["id"] for p in preds],
                         ["G", "C1", "C2", "P1", "P2", "P3", "P4", "P5", "P6"])
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["met"] and not p["graded"] for p in preds[1:]))

    def test_open_gate_grades(self):
        gate = {k: True for k in af.gate_checks(self.census, self.recs, True)}
        preds = {p["id"]: p for p in af.grade(af.analyse(self.recs), gate)}
        self.assertTrue(all(p["graded"] for p in preds.values()))
        self.assertFalse(preds["C1"]["met"])             # 2 figs, not 4
        self.assertFalse(preds["C2"]["met"])             # 7.0 is not 7.5
        self.assertTrue(preds["P1"]["met"])
        self.assertTrue(preds["P2"]["met"])
        self.assertFalse(preds["P3"]["met"])             # 1 < 3
        self.assertTrue(preds["P4"]["met"])
        self.assertFalse(preds["P5"]["met"])             # 1 < 3
        self.assertTrue(preds["P6"]["met"])

    def test_value_kind_gate(self):
        bad = MINI.replace(",13.5,", ",ND,")
        samples, census = af.parse_text(bad)
        gate = af.gate_checks(census, list(samples.values()), True)
        self.assertFalse(gate["value_kinds"])

    def test_mixed_labels(self):
        bad = MINI.replace("S4,x,Import,x,TURKEY,x,FIG,x,02-Nov-09,x,x,Aflatoxin G2",
                           "S4,x,Import,x,GREECE,x,FIG,x,02-Nov-09,x,x,Aflatoxin G2")
        samples, census = af.parse_text(bad)
        self.assertTrue(samples["S4"]["mixed_labels"])
        gate = af.gate_checks(census, list(samples.values()), True)
        self.assertFalse(gate["labels_per_sample"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
