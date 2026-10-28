#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for don_grains_2015.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import unittest

import don_grains_2015 as dg

# Headers as in the two CFIA files (DG 15 columns, MM 18).
DG_HEAD = ["﻿Sample No. – No. d’échantillon", "Region - Région", "Function", "Fonction",
           "Origin", "OriginE", "Product", "Produit", "Date Sampled – Date d’échantillonage",
           "Type of test", "Type d’analyse", "Component", "Composant", "Result - Résultat",
           "Unit - Unité"]
MM_HEAD = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "denrée",
           "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
           "Date Sampled – Date d’échantillonage", "Type of Test", "Type d’analyse",
           "Component", "Composant", "AMOUNT", "Report Unit - Unité de rapport", "Plan Code"]


def dg_row(sample, function, origin, product, value, comp=dg.DON, unit="ng/g"):
    cols = ["x"] * 15
    cols[0], cols[2], cols[4], cols[6], cols[11], cols[13], cols[14] = (
        sample, function, origin, product, comp, value, unit)
    return ",".join(cols)


def mm_row(sample, product, comp, value, unit="ng/g"):
    cols = ["x"] * 18
    cols[0], cols[4], cols[6], cols[8], cols[13], cols[15], cols[16] = (
        sample, "Import", "CANADA", product, comp, value, unit)
    return ",".join(cols)


MINI_DG = "\n".join([
    ",".join(DG_HEAD),
    dg_row("D1", "Domestic", "CANADA", "Grain - Barley", "1500"),
    dg_row("D2", "Import", "UNKNOWN", "Grain - Barley", "4.2"),
    dg_row("D3", "Import", "UNKNOWN", "Grain - Barley", "0"),
    dg_row("D4", "Unknown", "UNKNOWN", "Grain - Quinoa", "12"),
    dg_row("D5", "Unknown", "PERU", "Grain - Quinoa", "0"),
    dg_row("D6", "Import", "UNITED STATES", "Lentil", "3.1"),
    dg_row("D7", "Import", "UNITED STATES", "Lentil", "0"),
    dg_row("D8", "Domestic", "CANADA", "Millet", "450"),
]) + "\n"

MINI_MM = "\n".join([
    ",".join(MM_HEAD),
    mm_row("M1", "Grain - Barley", dg.DON, "40"),
    mm_row("M1", "Grain - Barley", "Ochratoxin A", "0.8"),
    mm_row("M2", "Grain - Barley", dg.DON, "0"),
    mm_row("M3", "Grain - Quinoa", dg.DON, "10"),
    mm_row("M4", "Corn Products", dg.DON, "200"),
]) + "\n"


class TestParseAmount(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(dg.parse_amount(""), (0.0, False, "blank"))
        self.assertEqual(dg.parse_amount("ND"), (0.0, False, "text"))
        self.assertEqual(dg.parse_amount("<10"), (0.0, False, "text"))
        self.assertEqual(dg.parse_amount("0"), (0.0, False, "zero"))
        self.assertEqual(dg.parse_amount("0.0"), (0.0, False, "zero"))
        self.assertEqual(dg.parse_amount("-1"), (None, False, "bad"))
        self.assertEqual(dg.parse_amount("inf"), (None, False, "bad"))
        self.assertEqual(dg.parse_amount(" 4.2 "), (4.2, True, "pos"))


class TestLabels(unittest.TestCase):
    def test_groups_cover_census(self):
        self.assertEqual(len(dg.DG_PRODUCT_ROWS), 44)
        self.assertEqual(sum(dg.DG_PRODUCT_ROWS.values()), 997)
        sizes = {g: sum(v.values()) for g, v in dg.GROUPS.items()}
        self.assertEqual(sizes, {"SG": 353, "PS": 252, "OG": 197, "PU": 189, "MA": 6})
        self.assertEqual(sum(sizes[g] for g in dg.GRAIN_GROUPS), 802)
        labels = [lab for v in dg.GROUPS.values() for lab in v]
        self.assertEqual(len(labels), len(set(labels)))                # each label once

    def test_group_of(self):
        self.assertEqual(dg.group_of("Flour - rye"), "SG")
        self.assertEqual(dg.group_of("Arrowroot Products"), "PS")
        self.assertEqual(dg.group_of("Teff Products"), "OG")
        self.assertEqual(dg.group_of("Tofu"), "PU")
        self.assertEqual(dg.group_of("Meat Alternative"), "MA")
        self.assertEqual(dg.group_of("Corn Products"), "none")

    def test_shared_labels(self):
        self.assertEqual(len(dg.SHARED_LABELS), 18)
        self.assertEqual(dg.SHARED_LABELS, sorted(dg.SHARED_LABELS))
        self.assertTrue(set(dg.SHARED_LABELS) <= set(dg.DG_PRODUCT_ROWS))
        self.assertNotIn("Flour - rye", dg.SHARED_LABELS)
        self.assertNotIn("Flour - Other", dg.SHARED_LABELS)

    def test_columns(self):
        c = dg.find_columns(DG_HEAD)
        self.assertEqual((c["sample"], c["function"], c["origin"], c["product"],
                          c["component"], c["value"], c["unit"]), (0, 2, 4, 6, 11, 13, 14))
        c = dg.find_columns(MM_HEAD)
        self.assertEqual((c["value"], c["unit"], c["component"], c["function"]),
                         (15, 16, 13, 4))

    def test_percent_and_c1_band(self):
        self.assertEqual(dg.percent(454, 997), 46)
        self.assertEqual(dg.percent(453, 997), 45)
        self.assertEqual(dg.percent(463, 997), 46)
        self.assertEqual(dg.percent(464, 997), 47)
        self.assertEqual(dg.C1_POS, (454, 463))


class TestParse(unittest.TestCase):
    def test_dg(self):
        s, c = dg.parse_text(MINI_DG)
        self.assertEqual((c["n_rows"], c["distinct_samples"]), (8, 8))
        self.assertEqual(c["value_kinds"], {"pos": 5, "zero": 3})
        self.assertEqual(c["units"], {"ng/g": 8})
        self.assertEqual(c["functions"], {"Domestic": 2, "Import": 4, "Unknown": 2})
        self.assertEqual((s["D1"]["don"], s["D1"]["detected"], s["D1"]["group"]),
                         (1500.0, True, "SG"))
        self.assertEqual((s["D3"]["don"], s["D3"]["detected"]), (0.0, False))
        self.assertEqual(s["D6"]["group"], "PU")

    def test_mm_only_don(self):
        s, c = dg.parse_text(MINI_MM, only_component=dg.DON)
        self.assertEqual(c["n_rows"], 5)
        self.assertEqual(c["components"], {dg.DON: 4, "Ochratoxin A": 1})
        self.assertEqual(c["distinct_samples"], 4)
        self.assertEqual(c["value_kinds"], {"pos": 3, "zero": 1})
        self.assertEqual(s["M1"]["don"], 40.0)


class TestStats(unittest.TestCase):
    def setUp(self):
        self.dg = list(dg.parse_text(MINI_DG)[0].values())
        self.mm = list(dg.parse_text(MINI_MM, only_component=dg.DON)[0].values())

    def test_row_stats(self):
        st = dg.row_stats(dg.select(self.dg, ("Grain - Barley",)))
        self.assertEqual((st["n"], st["pos"], st["min"], st["max"], st["below_cut"],
                          st["ge_cut"], st["ge_400"], st["ge_750"]),
                         (3, 2, 4.2, 1500.0, 1, 1, 1, 1))
        self.assertAlmostEqual(st["avg"], 752.1, places=9)
        self.assertAlmostEqual(st["rate"], 2 / 3, places=12)
        empty = dg.row_stats([])
        self.assertEqual((empty["n"], empty["pos"], empty["rate"], empty["max"]),
                         (0, 0, None, None))

    def test_cross_tables(self):
        labs = ["Grain - Barley", "Grain - Quinoa"]
        cut = dg.cross_tables(self.dg, self.mm, labs)
        self.assertEqual(cut, {"Grain - Barley": (1, 2, 1, 1), "Grain - Quinoa": (1, 1, 1, 0)})
        own = dg.cross_tables(self.dg, self.mm, labs, at_cut=False)
        self.assertEqual(own["Grain - Barley"], (2, 1, 1, 1))

    def test_cmh(self):
        self.assertEqual(dg.cmh([(5, 5, 5, 5)]), (0.0, 1.0))
        chi2, p = dg.cmh([(20, 5, 2, 23)])
        self.assertAlmostEqual(chi2, 8.5 ** 2 / (25 * 25 * 22 * 28 / (2500 * 49)), places=9)
        self.assertLess(p, 0.001)
        self.assertEqual(dg.cmh([(0, 0, 0, 0)]), (0.0, 1.0))
        self.assertIsNone(dg.mh_or([(1, 0, 1, 0)]))
        self.assertAlmostEqual(dg.mh_or([(20, 5, 2, 23)]), 46.0, places=9)

    def test_grade_runs_and_gate_closes(self):
        _, c_dg = dg.parse_text(MINI_DG)
        _, c_mm = dg.parse_text(MINI_MM, only_component=dg.DON)
        gate = dg.gate_checks(c_dg, c_mm, self.dg, self.mm, True, True)
        self.assertTrue(gate["dg_sha256"])
        self.assertFalse(gate["dg_rows"])
        self.assertTrue(gate["dg_unit"])
        self.assertTrue(gate["dg_value_kinds"])
        self.assertTrue(gate["mm_don_min"])
        self.assertFalse(gate["mm_don_kinds"])          # 3 positives, not 306
        a = dg.analyse(self.dg, self.mm)
        preds = dg.grade(a, gate)
        self.assertEqual([p["id"] for p in preds],
                         ["G", "C1", "P1", "P2", "P3", "P4", "P5", "P6", "P7"])
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["met"] and not p["graded"] for p in preds[1:]))
        self.assertEqual(a["max_sample"]["sample"], "D1")
        self.assertEqual(a["max_sample"]["group"], "SG")
        self.assertEqual([x["sample"] for x in a["pulses_positive"]], ["D6"])
        self.assertEqual((a["grains"]["n"], a["grains"]["ge_400"], a["grains"]["ge_750"]),
                         (6, 2, 1))

    def test_value_kind_gate(self):
        bad = MINI_DG.replace(",4.2,", ",ND,")
        _, c_dg = dg.parse_text(bad)
        _, c_mm = dg.parse_text(MINI_MM, only_component=dg.DON)
        gate = dg.gate_checks(c_dg, c_mm, [], [], True, True)
        self.assertFalse(gate["dg_value_kinds"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
