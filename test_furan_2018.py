#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for furan_2018.py (no network, no data). Made with AI agents working in MV2's
(Munim, Inc.) name. Code Apache-2.0."""
import csv
import io
import json
import os
import tempfile
import unittest

import furan_2018 as F

# The file's 18 columns, with the French accents left out (the parser reads the English parts).
HEADER = ["Sample No. - No. d'echantillon", "Region - Region", "Commodity", "denree", "Function",
          "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled - Date d'echantillonage", "Type of Test", "Type d'analyse", "Component",
          "Composant", "MaxOfAMOUNT", "Report Unit - Unite de rapport", "PLAN_CODE"]
COMPONENT = {"F": "Furan", "2MF": "2-Methylfuran", "3MF": "3-Methylfuran"}
# Label counts registered in P4 (they add to 250).
LABEL_COUNTS = (("Fish/Seafood - Canned", 50), ("Meat - Canned", 50), ("Sauce - Soy", 50),
                ("Evaporated Milk", 15), ("Milk Powder", 38), ("Dairy Alternative", 5),
                ("Beverage - Powdered Mixes - Hot", 34), ("Beverage - Powdered Mixes - Cold", 8))


def row(sample, product, analyte, value, unit="ng/g", plan="2018_TS023"):
    return [sample, "ATLANTIC", "IMFD", "DAIM", "Import", "importe", "THAILAND", "THAILANDE",
            product, "x", "2-Oct-18", "FURAN", "FURANE", COMPONENT[analyte], "x", value, unit,
            plan]


def as_csv(rows):
    buf = io.StringIO()
    csv.writer(buf).writerows([HEADER] + rows)
    return buf.getvalue()


def full_file(split_value="2.0"):
    """250 samples x 3 rows with the P4 label counts; all zero except the first Dairy
    Alternative's furan."""
    rows, i, first_split = [], 0, True
    for label, n in LABEL_COUNTS:
        for _ in range(n):
            i += 1
            sid = f"C2018FRAN{i:05d}"
            furan = "0"
            if label == "Dairy Alternative" and first_split:
                furan, first_split = split_value, False
            rows += [row(sid, label, "2MF", "0"), row(sid, label, "3MF", "0"),
                     row(sid, label, "F", furan)]
    return as_csv(rows)


class TestRules(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(F.parse_value("0"), (0.0, "nd"))
        self.assertEqual(F.parse_value("51.62"), (51.62, "det"))
        self.assertEqual(F.parse_value("3"), (3.0, "det"))
        self.assertEqual(F.parse_value("<1")[1], "nd")
        self.assertEqual(F.parse_value("ND")[1], "nd")
        for bad in ("", "-1", "NA", "trace"):
            self.assertEqual(F.parse_value(bad)[1], "bad", bad)

    def test_analyte(self):
        self.assertEqual(F.analyte("Furan"), "F")
        self.assertEqual(F.analyte(" 2-Methylfuran "), "2MF")
        self.assertEqual(F.analyte("3-METHYLFURAN"), "3MF")
        self.assertEqual(F.analyte("furan/furane"), "F")
        self.assertIsNone(F.analyte("Furans"))
        self.assertIsNone(F.analyte(""))

    def test_matches(self):
        self.assertTrue(F.matches(5.05, "5.1"))
        self.assertTrue(F.matches(63.99, "64"))
        self.assertTrue(F.matches(145.51, "146"))
        self.assertFalse(F.matches(10.345, "9.7"))
        self.assertFalse(F.matches(None, "1.2"))
        self.assertTrue(F.matches(0.0, "0"))

    def test_columns(self):
        c = F.find_columns(HEADER)
        self.assertEqual((c["sample"], c["component"], c["value"], c["unit"], c["product"],
                          c["origin"], c["function"], c["plan"], c["date"]),
                         (0, 13, 15, 16, 8, 6, 4, 17, 10))

    def test_category(self):
        self.assertEqual(F.category("Dairy Alternative", 2.0), "canned-milk")
        self.assertEqual(F.category("Dairy Alternative", 0.0), "dried-dairy")
        self.assertEqual(F.category("Beverage - Powdered Mixes - Cold", 0.0), "dried-beverage")
        self.assertEqual(F.category("Something else", 1.0), "unmapped")
        self.assertEqual(F.clean(" Meat –  Canned "), "Meat - Canned")

    def test_match_figure(self):
        m = F.match_figure([1.0, 2.04, 38.3, 38.17], ["38", "38.17", "2.0"])
        self.assertEqual(m["matched"], 3)
        self.assertEqual(m["unmatched"], [])
        self.assertEqual(m["extras"], [1.0])
        m = F.match_figure([5.0], ["5.5", "5"])
        self.assertEqual(m["matched"], 1)
        self.assertEqual(m["unmatched"], ["5.5"])
        self.assertEqual(m["extras"], [])


class TestPrintedFigures(unittest.TestCase):
    def test_figure_lengths(self):
        self.assertEqual({c: len(v) for c, v in F.FIGURE.items()},
                         {"canned-fish": 50, "canned-meat": 50, "canned-milk": 10,
                          "dried-beverage": 15, "soy-sauce": 50})
        for c, v in F.FIGURE.items():
            self.assertEqual(len(v), F.TABLE2[c][1], c)

    def test_printed_internal(self):
        p = F.printed_internal()
        self.assertEqual(p["table2_detected_sum"], 175)
        self.assertEqual(p["table2_samples_sum"], 250)
        self.assertEqual(p["figure_n"], 175)
        ok = {c: r["mean_matches_table2"] for c, r in p["figure"].items()}
        self.assertEqual(ok, {"canned-fish": True, "canned-meat": True, "canned-milk": True,
                              "dried-beverage": False, "soy-sauce": True})
        self.assertAlmostEqual(p["figure"]["dried-beverage"]["mean"], 10.345, places=3)
        self.assertTrue(F.matches(p["beverage_sum_over_16"], "9.7"))
        self.assertGreater(p["figure_mean_all"], 45.2)
        self.assertLess(p["figure_mean_all"], 45.4)
        self.assertFalse(F.matches(p["figure_mean_all"], "45.5"))

    def test_registered_constants(self):
        self.assertEqual(sum(r[0] for r in F.TABLE2.values()), F.N_SAMPLES)
        self.assertEqual(sum(n for _, n in LABEL_COUNTS), F.N_SAMPLES)
        self.assertEqual(F.N_ROWS, 3 * F.N_SAMPLES)
        self.assertEqual(set(F.LABELS), {label for label, _ in LABEL_COUNTS})


class TestParse(unittest.TestCase):
    def test_small_file(self):
        text = as_csv([
            row("C2018FRAN00001", "Fish/Seafood - Canned", "2MF", "51.62"),
            row("C2018FRAN00001", "Fish/Seafood - Canned", "3MF", "0"),
            row("C2018FRAN00001", "Fish/Seafood - Canned", "F", "10.51"),
            row("C2018FRAN00002", "Dairy Alternative", "2MF", "0"),
            row("C2018FRAN00002", "Dairy Alternative", "3MF", "0"),
            row("C2018FRAN00002", "Dairy Alternative", "F", "0"),
            row("C2018FRAN00003", "Dairy Alternative", "3MF", "0"),
            row("C2018FRAN00003", "Dairy Alternative", "3MF", "1.5"),
            row("C2018FRAN00003", "Dairy Alternative", "F", "0"),
            [""] * 18,
        ])
        samples, census = F.parse(text)
        by = {s["sample"]: s for s in samples}
        a = by["C2018FRAN00001"]
        self.assertAlmostEqual(a["sum"], 62.13, places=9)
        self.assertEqual((a["n_detected"], a["category"], a["kind"]), (2, "canned-fish", "det"))
        b = by["C2018FRAN00002"]
        self.assertEqual((b["sum"], b["category"], b["kind"]), (0.0, "dried-dairy", "nd"))
        c = by["C2018FRAN00003"]
        self.assertEqual((c["sum"], c["category"], c["missing"], c["repeated"]),
                         (1.5, "canned-milk", ["2MF"], ["3MF"]))
        self.assertIsNone(c["2MF"])
        self.assertEqual(census["rows"], 9)
        self.assertEqual(census["kinds"], {"det": 3, "nd": 6})
        self.assertEqual(census["units"], {"ng/g": 9})
        self.assertEqual(census["plans"], {"2018_TS023": 9})
        self.assertEqual(census["rows_per_sample"], {"3": 3})
        self.assertEqual(census["missing_analyte"], {"C2018FRAN00003": ["2MF"]})
        self.assertEqual(census["repeated_analyte"], {"C2018FRAN00003": ["3MF"]})
        self.assertEqual(census["unknown_components"], 0)
        g = F.gate_checks(census, F.SIZE)
        self.assertEqual(g, {"size": True, "columns": True, "rows": False, "samples": False,
                             "components": True, "units": False, "plan": False,
                             "products": True, "values": True})

    def test_bad_cells_fail_gate(self):
        text = as_csv([row("C2018FRAN00001", "Meat - Canned", "F", "n/a"),
                       row("C2018FRAN00001", "Meat - Canned", "2MF", "0", unit="ug/kg")])
        _, census = F.parse(text)
        self.assertEqual(census["bad_shapes"], ["n/a"])
        g = F.gate_checks(census, 1)
        self.assertFalse(g["values"])
        self.assertFalse(g["size"])
        self.assertFalse(g["units"])


class TestFullRun(unittest.TestCase):
    def test_gate_grade_and_outputs(self):
        samples, census = F.parse(full_file())
        gate = F.gate_checks(census, F.SIZE)
        self.assertTrue(all(gate.values()), gate)
        a = F.analyse(samples)
        self.assertEqual(a["cats"]["canned-milk"]["n"], 16)
        self.assertEqual(a["cats"]["dried-dairy"]["n"], 42)
        self.assertEqual(a["cats"]["dried-beverage"]["n"], 42)
        self.assertEqual(a["grand"]["k"], 1)
        preds = F.grade(a, gate)
        self.assertEqual([p["id"] for p in preds],
                         ["G", "C2", "C3", "CF", "CT", "P1", "P2", "P3", "P4"])
        met = {p["id"]: p["met"] for p in preds}
        self.assertTrue(met["G"])
        self.assertTrue(met["P4"])
        for pid in ("C2", "CF", "CT", "P1", "P2", "P3"):
            self.assertFalse(met[pid], pid)
        with tempfile.TemporaryDirectory() as d:
            result = F.write_outputs(d, samples, census, a, preds, {"source": "test"})
            self.assertEqual(result["n_graded"], 9)
            with open(os.path.join(d, "furan_2018_summary.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["study"], "furan-2018")
            with open(os.path.join(d, "furan_2018_samples.csv"), encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.reader(fh))), 251)

    def test_failed_gate_grades_nothing(self):
        gate = F.gate_checks(F.empty_census(), -1)
        preds = F.grade({"printed_internal": F.printed_internal()}, gate)
        self.assertEqual(sum(1 for p in preds if p["graded"]), 1)
        self.assertFalse(any(p["met"] for p in preds))


if __name__ == "__main__":
    unittest.main()
