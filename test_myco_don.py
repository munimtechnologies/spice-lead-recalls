# SPDX-License-Identifier: Apache-2.0
"""Offline tests for myco_don 0.1.0 (no network, synthetic rows only)."""
import csv
import io
import os
import tempfile
import unittest
from unittest import mock

import myco_don as md

D = "–"
INFANT_HEADER = ["Sample No. %s No. d’échantillon" % D, "Function", "Fonction", "Origin", "Origine",
                 "Product", "Produit", "Date Sampled %s Date" % D, "Type of Test", "Type d’analyse",
                 "Component", "Composant", "Result %s Résultat" % D, "Unit %s Unité" % D,
                 "Plan Code %s Code du régime" % D]
OTADON_HEADER = ["Sample No. %s No. d’échantillon" % D, "Function", "Fonction", "Origin", "Origine",
                 "Product", "Produit", "Date Sampled %s Date" % D, "Type of Test", "Type d’analyse",
                 "Component", "Composant", "Amount", "Unit %s Unité" % D,
                 "Plan Code %s Code du régime" % D]


def make_text(header, rows):
    """rows = list of (sample, product, component, result)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    for sample, product, component, result in rows:
        w.writerow([sample, "Import", "Importé", "CANADA", "CANADA", product, "x", "2013-01-01",
                    "TEST", "TEST", component, "x", result, "ng/g", "2013_SB437"])
    return buf.getvalue()


INFANT_ROWS = [
    ("I1", "Infant Food - Cereal", md.DON, "0.6"),
    ("I2", "Infant Food - Cereal", md.DON, "22"),
    ("I3", "Infant Food - Cereal", md.DON, "250"),
    ("I4", "Infant Food - Cereal", md.DON, "0"),
    ("I5", "Infant Food - Cereal", md.DON, "0"),
]
# 2010-11: two rows per sample (OTA + DON).
OTADON_ROWS = [
    ("A", "Beer", md.DON, "1.0"), ("A", "Beer", md.OTA, "0.040"),
    ("B", "Flour - Wheat", md.DON, "2060"), ("B", "Flour - Wheat", md.OTA, "6.773"),
    ("C", "Wine", md.DON, "0"), ("C", "Wine", md.OTA, "0"),
    ("D", "Raisin", md.DON, "0"), ("D", "Raisin", md.OTA, "0"),
    ("E", "Infant Food - Cereal", md.DON, "1.1"), ("E", "Infant Food - Cereal", md.OTA, "0.6"),
]
DON2011_ROWS = [
    ("D1", "Beer", md.DON, "1.0"),
    ("D2", "Wheat Products", md.DON, "2460"),
    ("D3", "Beer", md.DON, "0"),
    ("D4", "Date", md.DON, "0"),
]


def parsed_synth():
    inf = md.parse_text(make_text(INFANT_HEADER, INFANT_ROWS))
    d10 = md.parse_text(make_text(OTADON_HEADER, OTADON_ROWS))
    d11 = md.parse_text(make_text(INFANT_HEADER, DON2011_ROWS))
    return {"infant": (inf[0], inf[1], True), "don2011": (d11[0], d11[1], True),
            "otadon2010": (d10[0], d10[1], True)}


class TestParse(unittest.TestCase):
    def test_non_detects(self):
        self.assertEqual(md.parse_result("0"), (0.0, False, "zero"))
        self.assertEqual(md.parse_result("0.000"), (0.0, False, "zero"))
        self.assertEqual(md.parse_result(""), (0.0, False, "blank"))
        self.assertEqual(md.parse_result("<20"), (0.0, False, "lt"))
        self.assertEqual(md.parse_result("ND"), (0.0, False, "nd_token"))

    def test_detects_and_bad(self):
        self.assertEqual(md.parse_result("0.040"), (0.04, True, "positive"))
        self.assertEqual(md.parse_result(" 2060 "), (2060.0, True, "positive"))
        self.assertEqual(md.parse_result("0,5"), (0.5, True, "positive_comma"))
        self.assertEqual(md.parse_result("abc"), (None, False, "bad"))
        self.assertEqual(md.parse_result("-1"), (None, False, "bad"))


class TestMatching(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(md.matches(250.0, "250"))
        self.assertTrue(md.matches(0.0404, "0.040"))
        self.assertFalse(md.matches(0.0406, "0.040"))
        self.assertTrue(md.matches(6.773, "6.773"))
        self.assertTrue(md.matches(1.08, "1.1"))
        self.assertFalse(md.matches(None, "1"))

    def test_within(self):
        self.assertTrue(md.within(100, (100, 135)))
        self.assertTrue(md.within(135, (100, 135)))
        self.assertFalse(md.within(99, (100, 135)))
        self.assertFalse(md.within(None, (0, 4)))


class TestColumns(unittest.TestCase):
    def test_result_or_amount(self):
        ci = md.find_columns(INFANT_HEADER)
        self.assertEqual(ci["result"], 12)
        self.assertEqual(ci["component"], 10)
        co = md.find_columns(OTADON_HEADER)
        self.assertEqual(co["result"], 12)  # "Amount"
        self.assertEqual(co["product"], 5)

    def test_bom_stripped(self):
        self.assertEqual(md.clean("﻿Sample No."), "Sample No.")


class TestFisher(unittest.TestCase):
    def test_symmetric_table(self):
        self.assertAlmostEqual(md.fisher_two_sided(5, 5, 5, 5), 1.0, places=9)

    def test_extreme_table(self):
        self.assertLess(md.fisher_two_sided(10, 0, 0, 10), 0.001)

    def test_cooccurrence(self):
        rows, _ = md.parse_text(make_text(OTADON_HEADER, [
            ("s1", "Beer", md.OTA, "1"), ("s1", "Beer", md.DON, "1"),
            ("s2", "Beer", md.OTA, "1"), ("s2", "Beer", md.DON, "0"),
            ("s3", "Beer", md.OTA, "0"), ("s3", "Beer", md.DON, "1"),
            ("s4", "Beer", md.OTA, "0"), ("s4", "Beer", md.DON, "0"),
        ]))
        co = md.cooccurrence(rows)
        self.assertEqual((co["both"], co["ota_only"], co["don_only"], co["neither"]), (1, 1, 1, 1))
        self.assertEqual(co["n_pairs"], 4)
        self.assertAlmostEqual(co["odds_ratio"], 1.0)


class TestGrade(unittest.TestCase):
    def setUp(self):
        self.parsed = parsed_synth()

    def test_parse_shapes(self):
        inf = self.parsed["infant"][1]
        self.assertEqual(inf["n_rows"], 5)
        self.assertEqual(inf["distinct_samples"], 5)
        self.assertEqual(inf["units"], {"ng/g": 5})
        d10 = self.parsed["otadon2010"][1]
        self.assertEqual(d10["n_rows"], 10)
        self.assertEqual(d10["distinct_samples"], 5)
        self.assertEqual(d10["rows_per_sample"], {"2": 5})
        self.assertEqual(d10["components"], {md.DON: 5, md.OTA: 5})

    def test_gate_fails_on_synthetic(self):
        preds, _ = md.grade(self.parsed)
        ids = [p["id"] for p in preds]
        self.assertEqual(ids, ["G"] + [f"P{i}" for i in range(1, 13)])
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["graded"] and not p["met"] for p in preds[1:]))

    def test_grades_when_gate_open(self):
        with mock.patch.object(md, "gate_file", return_value=(True, {"ok": True})):
            preds, co = md.grade(self.parsed)
        met = {p["id"]: p["met"] for p in preds}
        self.assertTrue(all(p["graded"] for p in preds))
        self.assertEqual(met, {"G": True, "P1": False, "P2": True, "P3": True, "P4": True,
                               "P5": False, "P6": True, "P7": True, "P8": False, "P9": False,
                               "P10": False, "P11": False, "P12": False})

    def test_outputs(self):
        with mock.patch.object(md, "gate_file", return_value=(True, {"ok": True})):
            preds, co = md.grade(self.parsed)
        desc = md.descriptive(self.parsed, co)
        with tempfile.TemporaryDirectory() as tmp:
            res = md.write_outputs(tmp, self.parsed, preds, co, desc, {"x": "y"})
            for name in ("myco_don_2010_samples.csv", "myco_don_cooccurrence.json",
                         "myco_don_summary.json", "myco_don_grades.json"):
                self.assertTrue(os.path.exists(os.path.join(tmp, name)), name)
            with open(os.path.join(tmp, "myco_don_2010_samples.csv"), encoding="utf-8") as fh:
                lines = list(csv.reader(fh))
            self.assertEqual(len(lines), 11)  # header + 10 rows
            self.assertEqual(lines[0], md.SAMPLE_FIELDS)


class TestConstants(unittest.TestCase):
    def test_sha_lengths(self):
        for key, spec in md.FILES.items():
            self.assertEqual(len(spec["sha256"]), 64, key)
            self.assertTrue(all(ch in "0123456789abcdef" for ch in spec["sha256"]), key)

    def test_dried_fruit_disjoint_products(self):
        self.assertNotIn(md.INFANT_CEREAL, md.DRIED_FRUIT_2010)
        self.assertNotIn("Wine", md.DRIED_FRUIT_2010)


if __name__ == "__main__":
    unittest.main()
