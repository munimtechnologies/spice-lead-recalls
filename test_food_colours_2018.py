# SPDX-License-Identifier: Apache-2.0
# Offline tests for food_colours_2018.py on small synthetic files in CFIA's open-data layout.
import csv
import io
import unittest

import food_colours_2018 as fc

HEADER = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "Denrée",
          "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled – Date d’échantillonage", "Component", "Composant", "AMOUNT",
          "Report Unit - Unité de rapport"]
COMPS = ("Allura Red", "Tartrazine", "Rhodamine B", "Orange II", "Sudan IV")


def _file(samples):
    """samples: [(id, origin, commodity, product, {colour: amount})] -> CSV bytes (utf-8 with BOM)."""
    out = io.StringIO()
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerow(HEADER)
    for sid, origin, commodity, product, amounts in samples:
        for comp in COMPS:
            w.writerow([sid, "ONTARIO", commodity, commodity, "Import", "importé", origin, origin,
                        product, product, "2018-10-01", comp, comp, amounts.get(comp, "0"), "ppm"])
    return ("﻿" + out.getvalue()).encode("utf-8")


def _clean(n, origin="INDIA", commodity="Sweets", product="Hard candy", start=1):
    return [("C2018FC%05d" % (start + i), origin, commodity, product, {}) for i in range(n)]


class Parse(unittest.TestCase):
    def test_counts_and_duplicates(self):
        rows, check = fc.parse(_file(_clean(3) + [("C2018FC00002D", "INDIA", "Sweets", "Hard candy", {})]))
        self.assertEqual(check["samples"], 3)              # the D duplicate merges into its base
        self.assertEqual(check["data_rows"], 20)
        self.assertEqual(set(check["components"]), {c.lower() for c in COMPS})

    def test_positive_permitted_and_aliases(self):
        rows, _ = fc.parse(_file([("A1", "Unspecified", "Sweets", "Gummy candy",
                                   {"Allura Red": "539", "Rhodamine B": "10.8"}),
                                  ("A2", "", "Oils", "Chili oil", {"Sudan IV": "<0.1"})]))
        a1, a2 = rows
        self.assertEqual(a1["origin"], fc.UNKNOWN)
        self.assertEqual(a1["positive"], ["allura red", "rhodamine b"])
        self.assertEqual(a1["non_permitted"], ["rhodamine b"])
        self.assertEqual(a1["max_permitted_ppm"], 539.0)
        self.assertEqual(a2["origin"], fc.UNKNOWN)
        self.assertEqual(a2["positive"], [])              # "<LOD" reads as zero
        self.assertEqual(a2["category"], "oils")

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            fc.parse("Sample,Component\nX,Rhodamine B\n".encode("utf-8"))


class Rules(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(fc.classify("Sweets", ""), "sweets")
        self.assertEqual(fc.classify("Processed vegetables", ""), "processed vegetables")
        self.assertEqual(fc.classify("Essences/Flavourings", ""), "essences/flavourings")
        self.assertEqual(fc.classify("", "Olive oil"), "oils")
        self.assertEqual(fc.classify("", "Chili oil"), "oils")
        self.assertEqual(fc.classify("", "Pickled sweet peppers"), "processed vegetables")
        self.assertEqual(fc.classify("", "Ginger candy"), "sweets")
        self.assertEqual(fc.classify("", "Vanilla essence"), "essences/flavourings")
        self.assertEqual(fc.classify("", "Widget"), fc.UNCLASSIFIED)

    def test_is_permitted(self):
        self.assertTrue(fc.is_permitted("Allura Red"))
        self.assertTrue(fc.is_permitted("Ponceau SX"))
        self.assertTrue(fc.is_permitted("Erythrosin B"))
        self.assertFalse(fc.is_permitted("Erythrosin Yellowish"))
        self.assertFalse(fc.is_permitted("Ponceau 4R"))
        self.assertFalse(fc.is_permitted("Rhodamine B"))
        self.assertFalse(fc.is_permitted("Orange II"))


class Grade(unittest.TestCase):
    def _grade(self, samples):
        rows, check = fc.parse(_file(samples))
        return fc.grade(rows, check)

    def test_all_met(self):
        samples = (_clean(298) + _clean(60, "ITALY", "Oils", "Olive oil", 299)
                   + _clean(40, "CANADA", "Processed vegetables", "Pickles", 359)
                   + [("R1", "INDIA", "Sweets", "Hard candy", {"Rhodamine B": "10.8"}),
                      ("O1", "MEXICO", "Sweets", "Lollipop", {"Orange II": "0.2"})])
        g = self._grade(samples)
        self.assertTrue(g["gradable_parse"])
        self.assertEqual(g["samples"], 400)
        self.assertEqual(g["met"], 6)
        self.assertEqual(g["gradable"], 6)
        self.assertEqual(g["predictions"]["P6"]["value"], "0 of 60")

    def test_misses(self):
        samples = (_clean(200, "CANADA", "Sweets", "Candy") + _clean(100, "NIGERIA", "Oils", "Palm oil", 201)
                   + _clean(88, "INDIA", "Processed vegetables", "Pickles", 301)
                   + [("R1", "CANADA", "Processed vegetables", "Pickled peppers", {"Rhodamine B": "5"}),
                      ("O1", "INDIA", "Processed vegetables", "Chutney", {"Orange II": "0.1"})])
        p = self._grade(samples)["predictions"]
        self.assertEqual(p["P2"]["status"], "met")       # exactly one Rhodamine B sample
        self.assertEqual(p["P3"]["status"], "not met")   # it is a processed vegetable
        self.assertEqual(p["P3"]["value"], "processed vegetables")
        self.assertEqual(p["P4"]["status"], "not met")   # Canada is not Asia
        self.assertEqual(p["P5"]["status"], "not met")   # Orange II in a chutney
        self.assertEqual(p["P6"]["status"], "not met")   # 100 of 100 oils Nigerian

    def test_two_rhodamine_samples(self):
        samples = _clean(385) + [("R1", "INDIA", "Sweets", "Candy", {"Rhodamine B": "1"}),
                                 ("R2", "CHINA", "Sweets", "Candy", {"Rhodamine B": "2"})]
        g = self._grade(samples)
        self.assertEqual(g["predictions"]["P2"]["status"], "not met")
        self.assertEqual(g["predictions"]["P3"]["status"], "not gradable")
        self.assertEqual(g["predictions"]["P4"]["status"], "not gradable")
        self.assertEqual(g["predictions"]["P5"]["status"], "not gradable")   # no Orange II
        self.assertEqual(g["predictions"]["P6"]["status"], "not gradable")   # no oils
        self.assertEqual(g["gradable"], 2)

    def test_unclassified_rhodamine_is_not_gradable(self):
        samples = _clean(385) + [("R1", "INDIA", "", "Widget", {"Rhodamine B": "1"})]
        p = self._grade(samples)["predictions"]
        self.assertEqual(p["P3"]["status"], "not gradable")
        self.assertEqual(p["P4"]["status"], "met")

    def test_too_small_is_not_gradable(self):
        g = self._grade(_clean(10))
        self.assertFalse(g["gradable_parse"])
        self.assertEqual(g["predictions"]["P1"]["status"], "not met")
        self.assertEqual(g["predictions"]["P3"]["status"], "not gradable")


if __name__ == "__main__":
    unittest.main()
