# SPDX-License-Identifier: Apache-2.0
# Offline tests for sudan_spices.py on a small synthetic file in CFIA's open-data layout.
import csv
import io
import unittest

import sudan_spices as ss

HEADER = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "Denrée", "Function",
          "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled – Date d’échantillonage", "Component", "Composant", "AMOUNT",
          "Report Unit - Unité de rapport"]
DYES = ("Sudan I", "Sudan II", "Sudan III", "Sudan IV")


def _file(samples):
    """samples: [(id, origin, product, {dye: amount})] -> CSV bytes (utf-8 with BOM)."""
    out = io.StringIO()
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerow(HEADER)
    for sid, origin, product, amounts in samples:
        for dye in DYES:
            w.writerow([sid, "ONTARIO", "IMFD", "DAIM", "Import", "importé", origin, origin,
                        product, product, "2019-10-01", dye, dye, amounts.get(dye, "0"), "ug/g"])
    return ("﻿" + out.getvalue()).encode("utf-8")


def _clean(n, origin="INDIA", product="Paprika", start=1):
    return [("C2019NPC%05d" % (start + i), origin, product, {}) for i in range(n)]


class Parse(unittest.TestCase):
    def test_counts_and_duplicates(self):
        rows, check = ss.parse(_file(_clean(3) + [("C2019NPC00002D", "INDIA", "Paprika", {})]))
        self.assertEqual(check["samples"], 3)              # the D duplicate merges into its base
        self.assertEqual(check["data_rows"], 16)
        self.assertEqual(set(check["components"]), {d.lower() for d in DYES})

    def test_positive_and_aliases(self):
        rows, _ = ss.parse(_file([("A1", "Côte d'Ivoire", "Chili powder", {"Sudan IV": "12.5"}),
                                  ("A2", "", "Sumac", {"Sudan I": "<0.1"})]))
        a1, a2 = rows
        self.assertEqual(a1["origin"], "IVORY COAST")
        self.assertTrue(a1["sudan_positive"])
        self.assertEqual(a1["positive"], ["sudan iv"])
        self.assertEqual(a2["origin"], ss.UNKNOWN)      # blank origin is unknown
        self.assertFalse(a2["sudan_positive"])          # "<LOD" reads as zero

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            ss.parse("Sample,Component\nX,Sudan I\n".encode("utf-8"))


class Grade(unittest.TestCase):
    def _grade(self, samples):
        rows, check = ss.parse(_file(samples))
        return ss.grade(rows, check)

    def test_all_met(self):
        samples = (_clean(30) + _clean(10, "TURKEY", "Sumac", 31) + _clean(20, "", "Cayenne", 41))
        g = self._grade(samples)
        self.assertTrue(g["gradable_parse"])
        self.assertEqual(g["met"], 6)
        self.assertEqual(g["gradable"], 6)

    def test_misses(self):
        samples = (_clean(10) + _clean(30, "SPAIN", "Paprika", 11) + _clean(10, "NIGERIA", "Chili", 41)
                   + _clean(5, "GEORGIA", "Chili", 51) + [("Z1", "SPAIN", "Paprika", {"Sudan III": "3"})])
        p = self._grade(samples)["predictions"]
        self.assertEqual(p["P2"]["status"], "not met")   # one Sudan positive
        self.assertEqual(p["P3"]["status"], "not met")   # Spain, not India, is top
        self.assertEqual(p["P3"]["value"], ["SPAIN"])
        self.assertEqual(p["P4"]["status"], "not met")   # 10 of 56 West African
        self.assertEqual(p["P5"]["status"], "not met")   # Georgia present
        self.assertEqual(p["P6"]["status"], "not met")   # every origin declared

    def test_too_small_is_not_gradable(self):
        g = self._grade(_clean(10))
        self.assertFalse(g["gradable_parse"])
        self.assertEqual(g["predictions"]["P1"]["status"], "not met")
        self.assertEqual(g["predictions"]["P3"]["status"], "not gradable")


if __name__ == "__main__":
    unittest.main()
