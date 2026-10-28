#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for patulin_2008.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import unittest

import patulin_2008 as pt

# Header as in the CFIA file (18 columns, from the names-only census).
HEAD = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "denrée", "Function",
        "Fonction", "Origin", "Origine", "Product", "Produit",
        "Date Sampled – Date d’échantillonage", "Type of Test", "Type d’analyse", "Component",
        "Composant", "AMOUNT", "Report Unit - Unité de rapport", "Plan Code"]


def row(sample, function, origin, product, amount, unit="ppb"):
    cols = ["x"] * 18
    (cols[0], cols[1], cols[4], cols[6], cols[8], cols[10], cols[13], cols[15], cols[16],
     cols[17]) = (sample, "BC", function, origin, product, "7-Nov-08", "Patulin", amount, unit,
                  "2008_FP8APL7")
    return ",".join(cols)


MINI = "\n".join([
    ",".join(HEAD),
    row("S1", "imported", "CHINA", pt.JUICE, "26.7"),
    row("S2", "imported", "CHINA", pt.CONC, "12"),
    row("S3", "imported", "CHILE", pt.CONC, "<10"),
    row("S4", "domestic", "CANADA", pt.JUICE, "ND"),
    row("S5", "imported", "UNITED STATES", pt.JUICE, "0"),
    row("S6", "imported", "CHINA", pt.CONC, "5.5"),
    ",,,,,,,,,,,,,,,,,",
]) + "\n"


class TestParseAmount(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(pt.parse_amount(""), (None, "blank"))
        self.assertEqual(pt.parse_amount("ND"), (0.0, "nd"))
        self.assertEqual(pt.parse_amount("n.d."), (0.0, "nd"))
        self.assertEqual(pt.parse_amount("Not detected"), (0.0, "nd"))
        self.assertEqual(pt.parse_amount("<10"), (0.0, "lt"))
        self.assertEqual(pt.parse_amount("< 10"), (0.0, "lt"))
        self.assertEqual(pt.parse_amount("<LOQ"), (0.0, "nd"))
        self.assertEqual(pt.parse_amount("<abc"), (None, "text"))
        self.assertEqual(pt.parse_amount("0"), (0.0, "zero"))
        self.assertEqual(pt.parse_amount("0.0"), (0.0, "zero"))
        self.assertEqual(pt.parse_amount("-1"), (None, "bad"))
        self.assertEqual(pt.parse_amount("nan"), (None, "bad"))
        self.assertEqual(pt.parse_amount(" 26.7 "), (26.7, "num"))
        self.assertEqual(pt.parse_amount("trace"), (None, "text"))


class TestColumnsAndConstants(unittest.TestCase):
    def test_columns(self):
        c = pt.find_columns(["﻿" + HEAD[0]] + HEAD[1:])
        self.assertEqual((c["sample"], c["region"], c["function"], c["origin"], c["product"],
                          c["date"], c["component"], c["value"], c["unit"], c["plan"]),
                         (0, 1, 4, 6, 8, 10, 13, 15, 16, 17))

    def test_census_constants(self):
        self.assertEqual(sum(pt.PRODUCT_ROWS.values()), 104)
        self.assertEqual(sum(pt.FUNCTION_ROWS.values()), 104)
        self.assertEqual(sum(pt.ORIGIN_ROWS.values()), 104)
        self.assertEqual(len(pt.ORIGIN_ROWS), 9)
        self.assertEqual(pt.FUNCTION_ROWS["domestic"], pt.ORIGIN_ROWS["CANADA"])
        self.assertEqual(round(100 * (37 + 55) / 104, 1), 88.5)
        self.assertEqual((44 - 37, 60 - 55), (pt.C1_JUICE, pt.C1_CONC))

    def test_helpers(self):
        self.assertTrue(pt.matches(24.0, "24.0"))
        self.assertTrue(pt.matches(26.66, "26.7"))
        self.assertFalse(pt.matches(24.06, "24.0"))
        self.assertFalse(pt.matches(None, "24.0"))
        self.assertEqual(pt.half_unit("24.0"), 0.05)
        self.assertEqual(pt.parse_date("7-Nov-08"), "2008-11-07")
        self.assertEqual(pt.parse_date("10-Mar-09"), "2009-03-10")
        self.assertIsNone(pt.parse_date("bad"))
        self.assertAlmostEqual(pt.fisher_two_sided(2, 1, 0, 3), 0.4, places=12)
        self.assertAlmostEqual(pt.fisher_two_sided(2, 3, 0, 1), 1.0, places=12)
        self.assertEqual(pt.fisher_two_sided(0, 0, 0, 0), 1.0)


class TestParse(unittest.TestCase):
    def setUp(self):
        self.samples, self.census = pt.parse_text(MINI)
        self.recs = list(self.samples.values())

    def test_census(self):
        c = self.census
        self.assertEqual((c["n_rows"], c["distinct_samples"]), (6, 6))
        self.assertEqual(c["rows_per_sample"], {"1": 6})
        self.assertEqual(c["value_kinds"], {"num": 3, "lt": 1, "nd": 1, "zero": 1})
        self.assertEqual(c["units"], {"ppb": 6})
        self.assertEqual(c["products"], {pt.JUICE: 3, pt.CONC: 3})
        self.assertEqual(c["functions"], {"imported": 5, "domestic": 1})
        self.assertEqual(c["components"], {"Patulin": 6})

    def test_analyse(self):
        a = pt.analyse(self.recs)
        self.assertEqual([q["sample"] for q in a["quantified"]], ["S1", "S2"])
        self.assertEqual((a["juice_ge"], a["conc_ge"], a["n_ge_rl"]), (1, 1, 2))
        self.assertEqual((a["juice_max"], a["conc_max"]), (26.7, 12.0))
        self.assertEqual((a["n_ge_ml"], a["n_over_eu_infant"]), (0, 2))
        self.assertEqual((a["n_between"], a["between"]), (1, [5.5]))
        self.assertEqual((a["domestic_origins"], a["imported_canada"]), (["CANADA"], 0))
        self.assertEqual((a["below_15"], a["domestic_ge"], a["china_ge"]), (1, 0, 2))
        self.assertEqual(a["china_table"], [2, 1, 0, 3])
        self.assertEqual(a["function_table"], [2, 3, 0, 1])
        self.assertAlmostEqual(a["china_p"], 0.4, places=12)
        self.assertEqual(a["below_rl_entries"], {"<10": 1, "ND": 1, "0": 1})
        self.assertEqual((a["date_min"], a["date_max"], a["dates_parsed"]),
                         ("2008-11-07", "2008-11-07", 6))
        self.assertEqual(a["by_origin"]["CHINA"], {"n": 3, "ge_rl": 2})

    def test_gate_closes_and_grade_shape(self):
        gate = pt.gate_checks(self.census, True)
        self.assertEqual(len(gate), 10)
        self.assertTrue(gate["sha256"])
        self.assertFalse(gate["rows"])
        self.assertFalse(gate["component"])
        self.assertTrue(gate["unit"])
        self.assertTrue(gate["value_kinds"])
        preds = pt.grade(pt.analyse(self.recs), gate)
        self.assertEqual([p["id"] for p in preds],
                         ["G", "C1", "C2", "C3", "C4", "P1", "P2", "P3", "P4", "P5"])
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["met"] and not p["graded"] for p in preds[1:]))

    def test_open_gate_grades(self):
        gate = {k: True for k in pt.gate_checks(self.census, True)}
        preds = {p["id"]: p for p in pt.grade(pt.analyse(self.recs), gate)}
        self.assertTrue(all(p["graded"] for p in preds.values()))
        got = {k: p["met"] for k, p in preds.items()}
        self.assertEqual(got, {"G": True, "C1": False, "C2": False, "C3": True, "C4": True,
                               "P1": False, "P2": True, "P3": False, "P4": True, "P5": False})

    def test_value_kind_gate(self):
        bad = MINI.replace(",ND,", ",n/a,")
        _, census = pt.parse_text(bad)
        self.assertEqual(census["value_kinds"].get("text"), 1)
        self.assertFalse(pt.gate_checks(census, True)["value_kinds"])

    def test_unknown_unit_gate(self):
        bad = MINI.replace(",26.7,ppb,", ",26.7,furlongs,")
        _, census = pt.parse_text(bad)
        self.assertFalse(pt.gate_checks(census, True)["unit"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
