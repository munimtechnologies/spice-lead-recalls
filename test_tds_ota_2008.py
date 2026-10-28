#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for tds_ota_2008.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import io
import unittest

import tds_ota_2008 as t

# Header as in the English file (36 columns, from the names-only census).
HEAD = ["Food Name", "Sample Code", "Product Description", "Food Group",
        "Province/Territory of Origin", "Country of Origin", "Sample Type", "Sub Sample",
        "Sample Collection Date", "Reason Collected", "Human Illness Flag",
        "Sampling Location Type", "Sampling Location City Name", "Sampling Location Province",
        "Sampling Location Country", "Lab Name", "Analysis Completion Date", "Result Operator",
        "Result Value", "Units of measurement", "Analyte Name", "Analyte Group", "LOD", "LOQ",
        "MDL", "Basis for Result", "Quality Assurance", "Result Comments", "Test Method Name",
        "Test Method Code", "Instrumentation", "Method Comments", "Project Code", "Project Name",
        "Project Description", "Organization"]
RAISINS, FLOUR = "Fruits, Raisins, Semi-Moist", "Flour, white (wheat)"
ROWS = [  # sample, food, city, operator, value, unit, LOD, LOQ
    ("S1", RAISINS, "Quebec City", "=", "2.312", "ng/g", "0.004", "0.013"),
    ("S2", RAISINS, "Calgary", "=", "0.168", "ng/g", "0.004", "0.013"),
    ("S3", FLOUR, "Calgary", "=", "1.71", "ng/g", "0.004", "0.014"),
    ("S4", "Tea", "Quebec City", "<LOD/MDL", "0", "ng/ml", "0.002", "0.007"),
    ("S5", "Beans, String", "Calgary", "=", "0.004", "ng/g", "0.002", "0.006"),
    ("S6", "Dinners, Frozen Entrées", "Quebec City", "=", "0.071", "ng/g", "0.002", "0.006"),
]
FR_VALUES = {"S1": "2,312", "S2": "0,168", "S3": "1,71", "S4": "0", "S5": "0,004", "S6": "0,071"}


def line(cells):
    buf = io.StringIO()
    csv.writer(buf).writerow(cells)
    return buf.getvalue()


def cells(sample, food, city, op, value, unit, lod, loq):
    c = [""] * 36
    c[0], c[1], c[12], c[17], c[18], c[19], c[20], c[22], c[23] = (
        food, sample, city, op, value, unit, "Ochratoxin A", lod, loq)
    return c


def en_text(rows=ROWS):
    return line(HEAD) + "".join(line(cells(*r)) for r in rows) + line([""] * 36)


def fr_text(values=FR_VALUES, rows=ROWS):
    out = line([f"f{i}" for i in range(36)])
    for r in reversed(rows):
        if r[0] in values:
            out += line(cells(r[0], "x", "y", r[3], values[r[0]], r[5], r[6], r[7]))
    return out


class TestConstants(unittest.TestCase):
    def test_table3_and_map(self):
        self.assertEqual(len(t.TABLE3), 70)
        self.assertEqual(len(t.FILE_TO_CODE), 70)
        self.assertEqual(set(t.FILE_TO_CODE.values()), set(t.TABLE3))
        self.assertEqual(len(t.CODE_BY_KEY), 70)
        self.assertEqual(sum(1 for v in t.TABLE3.values() if v[5]), 12)
        self.assertEqual(len(t.CEREAL), 28)

    def test_table3_counts_against_text(self):
        nd = {y: sum(1 for c in t.TABLE3 if t.table3(c, y) == t.ND) for y in t.YEAR_INDEX}
        self.assertEqual(nd, {"2008": 21, "2009": 24})
        above = {y: sum(1 for c, v in t.TABLE3.items() if t.table3(c, y) != t.ND
                        and float(t.table3(c, y)) > v[4]) for y in t.YEAR_INDEX}
        self.assertEqual(above, t.C5_LOQ)

    def test_census_constants(self):
        self.assertEqual(len(t.EXPECTED_PAIRS), t.N_ROWS)
        self.assertEqual(sum(t.CITY_ROWS.values()), t.N_ROWS)
        self.assertEqual(sum(t.UNIT_ROWS.values()), t.N_ROWS)
        det = {y: sum(1 for c, yy in t.EXPECTED_PAIRS if yy == y and t.table3(c, y) != t.ND)
               for y in t.YEAR_INDEX}
        self.assertEqual(det, t.P1_DET)
        ml = [p for p in t.EXPECTED_PAIRS if t.TABLE3[p[0]][5] or p[0] in t.P2_EXTRA]
        self.assertEqual(len(ml), t.UNIT_ROWS["ng/ml"])

    def test_table3_top20(self):
        pairs = {}
        for c in t.TABLE3:
            if (c, "2008") in t.EXPECTED_PAIRS and (c, "2009") in t.EXPECTED_PAIRS:
                pairs[c] = tuple(0.0 if t.table3(c, y) == t.ND else float(t.table3(c, y))
                                 for y in ("2008", "2009"))
        self.assertEqual(len(pairs), 67)
        top = t.top20(pairs)
        self.assertEqual(top[0], "HH17")
        self.assertEqual(set(top), {"HH17", "FF20", "FF02", "FF12", "FF03", "FF01", "FF21",
                                    "NN05", "NN03", "FF11", "NN04", "FF08", "GG02", "FF10",
                                    "LL01", "JJ01", "NN01", "JJ11", "FF09", "FF16"})
        self.assertEqual(sum(1 for c in top if c in t.CEREAL), 16)


class TestHelpers(unittest.TestCase):
    def test_number_and_result(self):
        self.assertAlmostEqual(t.number("0,168"), 0.168)
        self.assertIsNone(t.number(""))
        self.assertIsNone(t.number("abc"))
        self.assertIsNone(t.number("nan"))
        self.assertEqual(t.parse_result("=", "0.04"), (0.04, "det"))
        self.assertEqual(t.parse_result("<LOD/MDL", "0"), (0.0, "below"))
        self.assertEqual(t.parse_result("ND", "0"), (0.0, "below"))
        self.assertEqual(t.parse_result("=", "0"), (None, "bad"))
        self.assertEqual(t.parse_result("<LOD/MDL", "0.01"), (None, "bad"))
        self.assertEqual(t.parse_result("", "0.5"), (None, "bad"))

    def test_matches_key_ranks(self):
        self.assertTrue(t.matches(0.168, "0.17"))
        self.assertFalse(t.matches(0.176, "0.17"))
        self.assertTrue(t.matches(1.04, "1.0"))
        self.assertFalse(t.matches(None, "1.0"))
        self.assertEqual(t.key("Dinners, Frozen Entrées"), "dinnersfrozenentrees")
        self.assertEqual(t.key("Dinners, Frozen Entrées"), "dinnersfrozenentrees")
        self.assertEqual(t.CODE_BY_KEY[t.key("Dinners, Frozen Entrées")], "MM02")
        self.assertEqual(t.ranks([0, 0, 1, 2]), [1.5, 1.5, 3.0, 4.0])
        self.assertAlmostEqual(t.spearman([0, 0, 1, 2], [0, 0, 2, 1]), 7 / 9)
        self.assertAlmostEqual(t.spearman([1, 2, 3], [3, 2, 1]), -1.0)
        self.assertIsNone(t.spearman([1, 2], [1, 2]))
        self.assertIsNone(t.spearman([1, 1, 1], [1, 2, 3]))

    def test_columns(self):
        c = t.find_columns(["﻿" + HEAD[0]] + HEAD[1:])
        self.assertEqual(c, {"food": 0, "sample": 1, "city": 12, "op": 17, "value": 18,
                             "unit": 19, "analyte": 20, "lod": 22, "loq": 23})
        with self.assertRaises(ValueError):
            t.find_columns(HEAD[:17])


class TestParse(unittest.TestCase):
    def setUp(self):
        self.recs, self.census, self.col = t.parse_text(en_text())

    def test_census(self):
        c = self.census
        self.assertEqual((c["n_rows"], c["distinct_samples"]), (6, 6))
        self.assertEqual(c["rows_per_sample"], {"1": 6})
        self.assertEqual(c["cities"], {"Quebec City": 3, "Calgary": 3})
        self.assertEqual(c["units"], {"ng/g": 5, "ng/ml": 1})
        self.assertEqual(c["operators"], {"=": 5, "<LOD/MDL": 1})
        self.assertEqual(c["kinds"], {"det": 5, "below": 1})
        self.assertEqual(c["unmapped_foods"], [])
        self.assertEqual(c["pairs"], [("FF12", "2009"), ("GG02", "2009"), ("HH17", "2008"),
                                      ("HH17", "2009"), ("KK06", "2008"), ("MM02", "2008")])

    def test_analyse(self):
        a = t.analyse(self.recs)
        self.assertEqual([m["sample"] for m in a["c1_mismatch"]], ["S5"])
        self.assertEqual(a["c2_checked"], 4)
        self.assertEqual([m["sample"] for m in a["c2_mismatch"]], ["S6"])
        self.assertEqual(a["detected"], {"2008": 2, "2009": 3})
        self.assertEqual(a["above_file_loq"], {"2008": 2, "2009": 2})
        self.assertEqual(a["above_paper_loq"], {"2008": 2, "2009": 2})
        self.assertEqual((a["maxima"]["2008"]["code"], a["maxima"]["2009"]["code"]),
                         ("HH17", "FF12"))
        self.assertEqual(a["ng_ml"], [("KK06", "2008")])
        self.assertEqual(a["expected_ng_ml"], [("KK06", "2008")])
        self.assertEqual((a["n_shared_foods"], a["top20_cereal"]), (1, 0))
        self.assertIsNone(a["spearman_2008_2009"])
        self.assertEqual(a["eu_reference_over"], [])
        self.assertEqual(a["lod_vs_paper_range"], {"in 0.001-0.008": 6})

    def test_gate_closed(self):
        gate = t.gate_checks(self.census, True)
        self.assertEqual(len(gate), 9)
        self.assertEqual({k for k, v in gate.items() if v}, {"sha256", "foods_mapped", "results"})
        preds = t.grade(t.analyse(self.recs), gate, {})
        self.assertEqual([p["id"] for p in preds],
                         ["G", "C1", "C2", "C3", "C4", "C5", "P1", "P2", "P3", "P4", "P5"])
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["met"] and not p["graded"] for p in preds[1:]))

    def test_open_gate_grades(self):
        gate = {k: True for k in t.gate_checks(self.census, True)}
        enfr = t.compare_fr(self.recs, fr_text(), self.col)
        preds = {p["id"]: p for p in t.grade(t.analyse(self.recs), gate, enfr)}
        self.assertTrue(all(p["graded"] for p in preds.values()))
        got = {k: p["met"] for k, p in preds.items()}
        self.assertEqual(got, {"G": True, "C1": False, "C2": False, "C3": True, "C4": False,
                               "C5": False, "P1": False, "P2": True, "P3": True, "P4": False,
                               "P5": False})

    def test_french_pairing(self):
        ok = t.compare_fr(self.recs, fr_text(), self.col)
        self.assertEqual((ok["paired"], ok["n_fr_rows"], ok["all_agree"]), (6, 6, True))
        off = t.compare_fr(self.recs, fr_text({**FR_VALUES, "S6": "0,07"}), self.col)
        self.assertEqual((off["value_disagree"], off["all_agree"]), (["S6"], False))
        short = dict(FR_VALUES)
        del short["S1"]
        miss = t.compare_fr(self.recs, fr_text(short), self.col)
        self.assertEqual((miss["paired"], miss["unpaired_en"], miss["all_agree"]),
                         (5, ["S1"], False))

    def test_bad_result_gate(self):
        rows = [r if r[0] != "S4" else ("S4", "Tea", "Quebec City", "=", "0", "ng/ml",
                                        "0.002", "0.007") for r in ROWS]
        recs, census, _ = t.parse_text(en_text(rows))
        self.assertEqual(census["kinds"].get("bad"), 1)
        self.assertFalse(t.gate_checks(census, True)["results"])

    def test_unmapped_food_gate(self):
        rows = [r if r[0] != "S4" else ("S4", "Kombucha", "Quebec City", "<LOD/MDL", "0",
                                        "ng/ml", "0.002", "0.007") for r in ROWS]
        _, census, _ = t.parse_text(en_text(rows))
        self.assertEqual(census["unmapped_foods"], ["Kombucha"])
        self.assertFalse(t.gate_checks(census, True)["foods_mapped"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
