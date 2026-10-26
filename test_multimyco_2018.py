#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for multimyco_2018.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import math
import unittest

import multimyco_2018 as mm

# A realistic 18-column header (English + French columns, as in the CFIA file).
HEAD = ("Sample No.,Region,Commodity,denree,Function,Fonction,Origin,Origine,Product,Produit,"
        "Date Sampled,Type of Test,Type analyse,Component,Composant,AMOUNT,"
        "Report Unit - Unite,Plan Code")


def row(sample, func, origin, product, comp, amount):
    cols = ["x"] * 18
    cols[0] = sample
    cols[4] = func
    cols[6] = origin
    cols[8] = product
    cols[13] = comp
    cols[15] = amount
    cols[16] = "ppb"
    cols[17] = "2018_SB427"
    return ",".join(cols)


MINI = "\n".join([
    HEAD,
    row("S1", "Domestic", "CANADA", "Flour - Corn", "Deoxynivalenol", "100"),
    row("S1", "Domestic", "CANADA", "Flour - Corn", "Ochratoxin A", "<0.5"),
    row("S1", "Domestic", "CANADA", "Flour - Corn", "Fumonisin B1", "200"),
    row("S2", "Unknown", "UNKNOWN", "Crackers", "Deoxynivalenol", "0"),
    row("S2", "Unknown", "UNKNOWN", "Crackers", "Ochratoxin A", "5"),
    row("S2", "Unknown", "UNKNOWN", "Crackers", "Fumonisin B1", ""),
]) + "\n"


class TestParseAmount(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(mm.parse_amount(""), (0.0, False, "blank"))
        self.assertEqual(mm.parse_amount("  "), (0.0, False, "blank"))
        self.assertEqual(mm.parse_amount("<0.5"), (0.0, False, "lt"))
        self.assertEqual(mm.parse_amount("ND"), (0.0, False, "nd"))
        self.assertEqual(mm.parse_amount("0"), (0.0, False, "zero"))
        self.assertEqual(mm.parse_amount("0.0"), (0.0, False, "zero"))
        self.assertEqual(mm.parse_amount("2,570"), (None, False, "comma"))
        self.assertEqual(mm.parse_amount("abc"), (None, False, "bad"))
        self.assertEqual(mm.parse_amount("-3"), (None, False, "bad"))
        ppb, det, kind = mm.parse_amount("12.5")
        self.assertEqual((ppb, det, kind), (12.5, True, "pos"))

    def test_matches(self):
        self.assertTrue(mm.matches(2570.0, "2570"))
        self.assertTrue(mm.matches(2570.4, "2570"))
        self.assertFalse(mm.matches(2571.2, "2570"))
        self.assertTrue(mm.matches(4.2, "4.2"))
        self.assertFalse(mm.matches(4.3, "4.2"))
        self.assertFalse(mm.matches(None, "4.2"))


class TestParsing(unittest.TestCase):
    def test_census_and_detection(self):
        rows, census = mm.parse_text(MINI)
        self.assertEqual(census["n_rows"], 6)
        self.assertEqual(census["distinct_samples"], 2)
        self.assertEqual(census["components"],
                         {"Deoxynivalenol": 2, "Ochratoxin A": 2, "Fumonisin B1": 2})
        self.assertEqual(census["products"], {"Flour - Corn": 1, "Crackers": 1})
        self.assertEqual(census["origins"], {"CANADA": 1, "UNKNOWN": 1})
        self.assertEqual(census["amount_kinds"], {"pos": 3, "lt": 1, "zero": 1, "blank": 1})
        self.assertEqual(census["amount_distinct"], 6)
        self.assertEqual(census["rows_per_sample"], {"3": 2})

        dets = mm.sample_detections(rows)
        self.assertEqual(dets["S1"], {"Deoxynivalenol", "Fumonisin B1"})
        self.assertEqual(dets["S2"], {"Ochratoxin A"})
        self.assertEqual(mm.any_detected_count(dets), 2)
        self.assertEqual(mm.group_count(dets, ("Deoxynivalenol",)), 1)
        self.assertEqual(mm.group_count(dets, ("Ochratoxin A",)), 1)
        self.assertEqual(mm.detected_labels(dets),
                         {"Deoxynivalenol", "Fumonisin B1", "Ochratoxin A"})

    def test_analyte_values(self):
        rows, _ = mm.parse_text(MINI)
        self.assertEqual(mm.analyte_detected_values(rows, "Deoxynivalenol"), [100.0])
        self.assertEqual(mm.analyte_detected_values(rows, "Ochratoxin A"), [5.0])
        # The 0 cell counts toward "all values" (as 0.0) but is not a detection.
        self.assertEqual(sorted(mm.analyte_all_values(rows, "Deoxynivalenol")), [0.0, 100.0])

    def test_analyse_small(self):
        rows, _ = mm.parse_text(MINI)
        a = mm.analyse(rows)
        self.assertEqual(a["any_detected"], 2)
        self.assertEqual(a["groups"]["DON"], 1)
        self.assertEqual(a["groups"]["Fumonisins"], 1)
        self.assertEqual(a["groups"]["OTA"], 1)
        self.assertEqual(a["n_detected_analytes"], 3)
        self.assertEqual(a["crackers_n"], 1)
        self.assertEqual(a["crackers_ota_n"], 1)
        self.assertEqual(a["max_groups"], 2)           # S1 has DON + fumonisins
        self.assertEqual(a["max_groups_products"], ["Flour - Corn"])


class TestStatistics(unittest.TestCase):
    def test_mh_common_or(self):
        mh, num, den = mm.mantel_haenszel([(10, 5, 5, 10), (10, 5, 5, 10)])
        self.assertAlmostEqual(mh, 4.0, places=12)
        self.assertAlmostEqual(num, 2 * 100 / 30, places=12)
        self.assertAlmostEqual(den, 2 * 25 / 30, places=12)

    def test_cmh_single(self):
        chi2, p = mm.cmh_test([(10, 5, 5, 10)])
        self.assertAlmostEqual(chi2, 4 / (15 ** 4 / (900 * 29)), places=9)
        self.assertAlmostEqual(chi2, 2.062222, places=5)
        self.assertAlmostEqual(p, math.erfc(math.sqrt(chi2 / 2)), places=12)

    def test_odds_ratio(self):
        self.assertAlmostEqual(mm.odds_ratio(2, 4, 3, 6), 1.0, places=12)
        self.assertAlmostEqual(mm.odds_ratio(0, 4, 3, 6), (0.5 * 6.5) / (4.5 * 3.5), places=12)

    def test_simpson_reversal(self):
        tabs = [(40, 10, 40, 10), (1, 9, 9, 81)]
        pooled = tuple(sum(x) for x in zip(*tabs))
        self.assertGreater(mm.odds_ratio(*pooled), 2.0)
        mh, _, _ = mm.mantel_haenszel(tabs)
        self.assertAlmostEqual(mh, 1.0, places=12)
        chi2, p = mm.cmh_test(tabs)
        self.assertEqual((chi2, p), (0.0, 1.0))


FAKE = {
    "any_detected": 386,
    "groups": {"DON": 306, "Fumonisins": 105, "Ergot": 46, "Zearalenone": 34, "OTA": 20,
               "CPA": 18, "STE": 12, "Aflatoxins": 11, "HT2T2": 8, "NIV": 7},
    "n_detected_analytes": 17,
    "never_detected": sorted(mm.NEVER_DETECTED),
    "analytes": {
        "DON": {"max": 2570.0, "avg_pos": 282.0, "avg_all": 1.0, "n_detected": 306},
        "OTA": {"max": 34.0, "avg_pos": 4.2, "avg_all": 0.1, "n_detected": 20},
        "CPA": {"max": 47.0, "avg_pos": 11.0, "avg_all": 0.3, "n_detected": 18},
        "STE": {"max": 12.0, "avg_pos": 2.7, "avg_all": 0.1, "n_detected": 12},
        "NIV": {"max": 86.0, "avg_pos": 22.0, "avg_all": 0.2, "n_detected": 7},
    },
    "crackers_n": 101, "crackers_ota_n": 5, "crackers_ota_rate": 5 / 101,
    "ota_over_3": 7,
    "max_groups": 9, "max_groups_products": ["Flour - Corn"],
    "don_fumonisin": {"pooled": [80, 20, 20, 630], "pooled_or": 8.0, "mh_or": 2.0,
                      "cmh_p": 0.01, "n_strata": 5},
}

OPEN_GATE = {k: True for k in (
    "sha256", "rows", "samples", "rows_per_sample", "components", "products", "one_plan",
    "one_unit", "origin_canada", "origin_unknown", "origin_foreign", "origin_distinct",
    "amount_format")}


class TestGrading(unittest.TestCase):
    def test_all_met(self):
        preds = mm.grade(FAKE, OPEN_GATE)
        self.assertEqual([p["id"] for p in preds],
                         ["G", "P1", "P2", "P3", "P4", "C1", "P5", "P6", "P7", "P8"])
        self.assertTrue(all(p["met"] for p in preds), [p["id"] for p in preds if not p["met"]])

    def test_misses(self):
        a = dict(FAKE)
        a["any_detected"] = 388          # text value, not Table 2's 386
        a["groups"] = dict(FAKE["groups"], Fumonisins=104)
        a["ota_over_3"] = 6
        a["don_fumonisin"] = dict(FAKE["don_fumonisin"], mh_or=9.0)  # not attenuated
        preds = {p["id"]: p for p in mm.grade(a, OPEN_GATE)}
        self.assertFalse(preds["P1"]["met"])
        self.assertFalse(preds["P4"]["met"])
        self.assertFalse(preds["P5"]["met"])
        self.assertFalse(preds["P7"]["met"])  # |ln 9| > |ln 8|
        self.assertTrue(preds["P2"]["met"])
        self.assertTrue(preds["P3"]["met"])

    def test_gate_closed_grades_nothing(self):
        closed = dict(OPEN_GATE, amount_format=False)
        preds = mm.grade(FAKE, closed)
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["graded"] and not p["met"] for p in preds[1:]))


class TestGateChecks(unittest.TestCase):
    def _census(self):
        foreign = {f"F{i}": 1 for i in range(27)}
        foreign["F27"] = 277
        origins = {"CANADA": 155, "UNKNOWN": 291}
        origins.update(foreign)
        return {
            "n_rows": 18750, "distinct_samples": 750,
            "components": dict(mm.COMPONENT_COUNTS), "products": dict(mm.PRODUCT_SAMPLES),
            "origins": origins, "functions": {}, "plans": {"2018_SB427": 18750},
            "units": {"ppb": 18750}, "amount_kinds": {"pos": 900, "zero": 17850},
            "amount_distinct": 207, "rows_per_sample": {"25": 750},
        }

    def test_open(self):
        checks = mm.gate_checks(self._census(), True)
        self.assertTrue(all(checks.values()), [k for k, v in checks.items() if not v])

    def test_comma_fails(self):
        c = self._census()
        c["amount_kinds"] = {"pos": 900, "zero": 17849, "comma": 1}
        self.assertFalse(mm.gate_checks(c, True)["amount_format"])

    def test_bad_sha_fails(self):
        self.assertFalse(mm.gate_checks(self._census(), False)["sha256"])

    def test_origin_counts(self):
        c = self._census()
        c["origins"]["CANADA"] = 154
        self.assertFalse(mm.gate_checks(c, True)["origin_canada"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
