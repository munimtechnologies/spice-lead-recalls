#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for ota_grain_2018.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import unittest

import ota_grain_2018 as og

# Headers as in the two CFIA files (both 18 columns).
OG_HEAD = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "Commodity_F",
           "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
           "Date Sampled – Date d’échantillonage", "Type of test", "Type d’analyse",
           "Component", "Composant", "Result - Résultat", "ReportUnit", "PLAN_CODE"]
MM_HEAD = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "denrée",
           "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
           "Date Sampled – Date d’échantillonage", "Type of Test", "Type d’analyse",
           "Component", "Composant", "AMOUNT", "Report Unit - Unité de rapport", "Plan Code"]


def row(sample, origin, product, comp, value, unit="ppb"):
    cols = ["x"] * 18
    cols[0], cols[6], cols[8], cols[13], cols[15], cols[16], cols[17] = (
        sample, origin, product, comp, value, unit, "")
    return ",".join(cols)


O = og.OTA
MINI_OG = "\n".join([
    ",".join(OG_HEAD),
    row("G1", "CANADA", "Grain - Rice", O, "11"),
    row("G2", "UNKNOWN", "Grain - Rice", O, "ND"),
    row("G3", "ITALY", "Crackers", O, "0.9"),
    row("G4", "CANADA", "Crackers", O, "0.05"),
    row("G5", "UNKNOWN", "Buckwheat Products", O, "7.6"),
    row("G6", "UNKNOWN", "Flour - rye", O, "ND"),
    row("G7", "PERU", "Quinoa Products", O, "0.2"),
]) + "\n"

MINI_MM = "\n".join([
    ",".join(MM_HEAD),
    row("M1", "CANADA", "Crackers", O, "0", "ng/g"),
    row("M1", "CANADA", "Crackers", "Deoxynivalenol", "120", "ng/g"),
    row("M2", "CANADA", "Crackers", O, "1.2", "ng/g"),
    row("M3", "UNKNOWN", "Buckwheat Products", O, "0.8", "ng/g"),
    row("M4", "UNKNOWN", "Corn Products", O, "0", "ng/g"),
]) + "\n"


class TestParseAmount(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(og.parse_amount(""), (0.0, False, "blank"))
        self.assertEqual(og.parse_amount("ND"), (0.0, False, "text"))
        self.assertEqual(og.parse_amount("<0.04"), (0.0, False, "text"))
        self.assertEqual(og.parse_amount("Not detected - Non détecté"), (0.0, False, "text"))
        self.assertEqual(og.parse_amount("0"), (0.0, False, "zero"))
        self.assertEqual(og.parse_amount("-1"), (None, False, "bad"))
        self.assertEqual(og.parse_amount("nan"), (None, False, "bad"))
        self.assertEqual(og.parse_amount(" 0.042 "), (0.042, True, "pos"))


class TestPrecision(unittest.TestCase):
    def test_tolerance(self):
        self.assertAlmostEqual(og.tolerance("0.050"), 0.0005, places=12)
        self.assertAlmostEqual(og.tolerance("0.077"), 0.0005, places=12)
        self.assertAlmostEqual(og.tolerance("1.1"), 0.05, places=12)
        self.assertAlmostEqual(og.tolerance("11"), 0.5, places=12)
        self.assertAlmostEqual(og.tolerance("30"), 0.5, places=12)

    def test_matches(self):
        self.assertTrue(og.matches(10.6, "11"))
        self.assertFalse(og.matches(11.6, "11"))
        self.assertTrue(og.matches(0.2449, "0.24"))
        self.assertFalse(og.matches(0.2451, "0.24"))
        self.assertFalse(og.matches(None, "1.1"))


class TestLabels(unittest.TestCase):
    def test_family(self):
        self.assertEqual(og.family("Grain - Rice"), "rice")
        self.assertEqual(og.family("Flour - rye"), "rye")
        self.assertEqual(og.family("Bran - Oat"), "oat")
        self.assertEqual(og.family("Grain - Kamut"), "kamut")
        self.assertEqual(og.family("Crackers"), "generic")
        self.assertEqual(sum(og.OG_PRODUCT_ROWS.values()), 496)
        fam = {}
        for lab, n in og.OG_PRODUCT_ROWS.items():
            fam[og.family(lab)] = fam.get(og.family(lab), 0) + n
        self.assertEqual(fam, {"rice": 99, "rye": 25, "oat": 97, "kamut": 25, "buckwheat": 23,
                               "quinoa": 24, "generic": 203})

    def test_columns(self):
        c = og.find_columns(OG_HEAD)
        self.assertEqual((c["value"], c["unit"], c["product"], c["sample"]), (15, 16, 8, 0))
        c = og.find_columns(MM_HEAD)
        self.assertEqual((c["value"], c["unit"], c["component"]), (15, 16, 13))

    def test_shared_labels_are_census_labels(self):
        self.assertTrue(set(og.SHARED_LABELS) <= set(og.OG_PRODUCT_ROWS))

    def test_report_rows_cover_census(self):
        sizes = {rid: sum(og.OG_PRODUCT_ROWS[lab] for lab in labels)
                 for rid, _t, labels, *_ in og.ROWS + og.PCT_ROWS}
        self.assertEqual(sizes, {"C1": 25, "C2": 28, "C3": 28, "C4": 28, "C6": 100, "C7": 97,
                                 "C8": 99, "C9": 29, "C10": 171})
        r22 = [lab for _rid, _t, labels, *_ in og.PCT_ROWS for lab in labels]
        self.assertEqual(sorted(r22), sorted(og.OG_PRODUCT_ROWS))      # each label once

    def test_percent(self):
        self.assertEqual(og.percent(52, 97), 54)
        self.assertEqual(og.percent(53, 97), 55)
        self.assertEqual(og.percent(14, 99), 14)
        self.assertEqual(og.percent(18, 29), 62)
        self.assertEqual(og.percent(92, 171), 54)
        self.assertEqual(og.percent(1, 2), 50)
        self.assertIsNone(og.percent(0, 0))
        st = {"n": 29, "pos": 18, "min": 0.061, "max": 1.52, "avg": 0.43}
        ok, detail = og.check_pct_row(st, 29, 62, "0.06", "1.5", "0.4")
        self.assertTrue(ok, detail)
        ok, _ = og.check_pct_row(dict(st, pos=17), 29, 62, "0.06", "1.5", "0.4")
        self.assertFalse(ok)


class TestParse(unittest.TestCase):
    def test_og(self):
        s, c = og.parse_text(MINI_OG)
        self.assertEqual((c["n_rows"], c["distinct_samples"]), (7, 7))
        self.assertEqual(c["value_kinds"], {"pos": 5, "text": 2})
        self.assertEqual(c["text_tokens"], {"ND": 2})
        self.assertEqual(c["units"], {"ppb": 7})
        self.assertEqual(c["rows_per_sample"], {"1": 7})
        self.assertEqual((s["G1"]["ota"], s["G1"]["detected"], s["G1"]["family"]),
                         (11.0, True, "rice"))
        self.assertEqual((s["G2"]["ota"], s["G2"]["detected"]), (0.0, False))

    def test_mm_only_ota(self):
        s, c = og.parse_text(MINI_MM, only_component=og.OTA)
        self.assertEqual(c["n_rows"], 5)
        self.assertEqual(c["components"], {og.OTA: 4, "Deoxynivalenol": 1})
        self.assertEqual(c["distinct_samples"], 4)
        self.assertEqual(c["value_kinds"], {"zero": 2, "pos": 2})
        self.assertFalse(s["M1"]["detected"])
        self.assertEqual(s["M2"]["ota"], 1.2)


class TestStats(unittest.TestCase):
    def setUp(self):
        self.og = list(og.parse_text(MINI_OG)[0].values())
        self.mm = list(og.parse_text(MINI_MM, only_component=og.OTA)[0].values())

    def test_row_stats(self):
        st = og.row_stats(og.select(self.og, ("Crackers",)))
        self.assertEqual((st["n"], st["pos"], st["min"], st["max"], st["ge_cut"]),
                         (2, 2, 0.05, 0.9, 1))
        self.assertAlmostEqual(st["avg"], 0.475, places=12)
        ok, detail = og.check_row(st, 2, 2, "0.050", "0.90", "0.48")
        self.assertTrue(ok, detail)
        ok, _ = og.check_row(st, 3, 2, "0.050", "0.90", "0.48")
        self.assertFalse(ok)

    def test_cross_tables(self):
        cut = og.cross_tables(self.og, self.mm, ["Crackers", "Buckwheat Products"])
        self.assertEqual(cut, {"Crackers": (1, 1, 1, 1), "Buckwheat Products": (1, 0, 1, 0)})
        own = og.cross_tables(self.og, self.mm, ["Crackers"], at_cut=False)
        self.assertEqual(own, {"Crackers": (2, 0, 1, 1)})

    def test_cmh(self):
        chi2, p = og.cmh([(5, 5, 5, 5)])
        self.assertEqual((chi2, p), (0.0, 1.0))
        chi2, p = og.cmh([(20, 5, 2, 23)])
        self.assertAlmostEqual(chi2, 8.5 ** 2 / (25 * 25 * 22 * 28 / (2500 * 49)), places=9)
        self.assertLess(p, 0.001)
        self.assertEqual(og.cmh([(0, 0, 0, 0)]), (0.0, 1.0))
        self.assertIsNone(og.mh_or([(1, 0, 1, 0)]))
        self.assertAlmostEqual(og.mh_or([(20, 5, 2, 23)]), 20 * 23 / (5 * 2), places=9)

    def test_grade_runs_and_gate_closes(self):
        _, c_og = og.parse_text(MINI_OG)
        _, c_mm = og.parse_text(MINI_MM, only_component=og.OTA)
        gate = og.gate_checks(c_og, c_mm, self.og, self.mm, True, True)
        self.assertTrue(gate["og_sha256"])
        self.assertFalse(gate["og_rows"])
        self.assertTrue(gate["og_unit"])
        self.assertTrue(gate["og_tokens"])
        self.assertTrue(gate["mm_ota_min"])
        a = og.analyse(self.og, self.mm)
        preds = og.grade(a, gate)
        ids = [p["id"] for p in preds]
        self.assertEqual(ids, ["G", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10",
                               "P1", "P2", "P3", "P4", "P5", "P6"])
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["met"] and not p["graded"] for p in preds[1:]))
        self.assertEqual([x["sample"] for x in a["over_3"]], ["G1", "G5"])
        self.assertEqual([x["sample"] for x in a["over_3_outside_no_limit"]], ["G1"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
