# SPDX-License-Identifier: Apache-2.0
"""Tests for dried_tea_census 0.1.0 and the dried-tea-2009 0.1.1 addendum. Synthetic data only; no
CFIA file is read. Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name."""
import json
import os
import re
import unittest

import dried_tea_census as dc

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "docs", "dried-tea-2009-0.1.1-addendum.md")
STREET = re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(Road|Street|Avenue|Lane|Drive|Boulevard)\b")

LONG = "\n".join([
    "Sample Number / Numero,Product / Produit,Type of Test,Component,Result,Unit",
    "T1,Green,METALS,Mercury,0.01,ppm",
    "T1,Green,METALS,Lead,0.2,ppm",
    "T1A,Green,PESTICIDES-FPH053,Bifenthrin,0.05,ppm",
    "T2,Black,METALS,Mercury,<0.005,ppm",
    "T2,Black,METALS,Lead,0.3,ppm",
    "T2A,Black,PESTICIDES-LC,Imidacloprid,0.2,ppm",
    "T2A,Black,PESTICIDES-LC,Madeupcide,ND,ppm",
]) + "\n"

WIDE = "Sample Number,Tea Type,Mercury,Lead\nT1,Green,0.011,0.4\nT2,Black,0.012,<0.1\n"

PDF_TEXT = """•  PESTICIDES-FPH053 is a GC-MS-based multi-residue method with 4 analytes (listed below).
•  PESTICIDES-LC is an LC-MS-based multi-residue method with 2 analytes (listed below).

Test Type
PESTICIDES-FPH053
PESTICIDES-FPH053
PESTICIDES-FPH053

Test Name
 Pesticide Screen
 Pesticide Screen
 Pesticide Screen

Component
Naled
Naled
Aldrin

Page 1 of 2

Test Type
PESTICIDES-FPH053
PESTICIDES-LC
PESTICIDES-LC

Component
Mexacarbate
Mexacarbate
Carbaryl

Page 2 of 2
"""


class Cells(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(dc.shape("0.5"), "number")
        self.assertEqual(dc.shape(" <0.1 "), "lt-number")
        self.assertEqual(dc.shape(""), "blank")
        self.assertEqual(dc.shape("ND"), "token")
        self.assertEqual(dc.shape("-1"), "negative-number")

    def test_metal_symbol(self):
        self.assertEqual(dc.metal_symbol("Mercury"), "Hg")
        self.assertEqual(dc.metal_symbol("Lead (Pb)"), "Pb")
        self.assertEqual(dc.metal_symbol("Pb"), "Pb")
        self.assertEqual(dc.metal_symbol("Beryllium"), "Be")
        self.assertEqual(dc.metal_symbol("Tin"), "Sn")
        self.assertIsNone(dc.metal_symbol("Abamectin B1"))
        self.assertIsNone(dc.metal_symbol("Spinosyn A"))
        self.assertIsNone(dc.metal_symbol("Chlorpyrifos"))
        self.assertIsNone(dc.metal_symbol(""))

    def test_base_id_and_names(self):
        self.assertEqual(dc.base_id("C123A"), "C123")
        self.assertEqual(dc.base_id("C123"), "C123")
        self.assertEqual(dc.base_id("A"), "A")
        self.assertEqual(dc.norm_name("  o,p’-DDT "), "o,p'-ddt")

    def test_find_columns(self):
        col = dc.find_columns(["Sample Number / Numero", "Product / Produit", "Type of Test",
                               "Component", "Result", "Unit"])
        self.assertEqual(col, {"sample": 0, "component": 3, "test": 2, "value": 4, "unit": 5})

    def test_gate(self):
        self.assertFalse(dc.gate(281600))
        self.assertTrue(dc.gate(281601))
        self.assertTrue(dc.gate(282624))
        self.assertFalse(dc.gate(282625))


class LongCensus(unittest.TestCase):
    def setUp(self):
        self.out = dc.census(LONG, {"bifenthrin", "imidacloprid"})

    def test_counts(self):
        o = self.out
        self.assertEqual(o["layout"], "long")
        self.assertEqual(o["rows"], 7)
        self.assertEqual(o["raw_sample_numbers"], 4)
        self.assertEqual(o["base_samples"], 2)
        self.assertEqual(o["base_samples_by_groups"], {"metal + pesticide": 2})
        self.assertEqual(o["sample_number_suffix"], {"metal": {"ends_A": 0, "no_A": 4},
                                                     "pesticide": {"ends_A": 3, "no_A": 0}})
        self.assertEqual(o["metal_count"], 2)
        self.assertTrue(o["mercury_named"])
        self.assertFalse(o["beryllium_named"])
        self.assertEqual(o["metal_rows"], 4)
        self.assertEqual(o["metal_rows_per_sample"], {"2": 2})
        self.assertEqual(o["pesticide_rows"], 3)
        self.assertEqual(o["pesticide_names"], 3)
        self.assertEqual(o["pesticide_tests"], {"PESTICIDES-FPH053": 1, "PESTICIDES-LC": 2})
        self.assertEqual(o["pesticide_rows_not_number_shape"], 1)
        self.assertEqual(o["pesticide_names_not_in_pdf"], ["Madeupcide"])
        self.assertEqual(o["tokens"], {"pesticide: ND": 1})
        self.assertEqual(o["label_columns"], ["Product / Produit"])
        self.assertEqual(o["labels_per_sample"], {"Green": 1, "Black": 1})
        self.assertEqual(o["mixed_label_sample_count"], 0)

    def test_value_column_is_shapes_only(self):
        prof = {p["index"]: p for p in self.out["profile"]}
        self.assertEqual(prof[4]["kind"], "values (shapes only)")
        self.assertEqual(prof[4]["shapes"], {"number": 5, "lt-number": 1, "token": 1})
        self.assertEqual(prof[1]["counts"], {"Green": 3, "Black": 4})
        self.assertNotIn("counts", prof[0])

    def test_no_value_is_printed(self):
        dump = json.dumps(self.out)
        for v in ("0.01", "0.3", "0.005", "0.05"):
            self.assertNotIn(v, dump, v)


class WideCensus(unittest.TestCase):
    def test_wide_is_reported_by_shape(self):
        out = dc.census(WIDE)
        self.assertEqual(out["layout"], "wide or unknown")
        self.assertIn("error", out)
        prof = {p["index"]: p for p in out["profile"]}
        self.assertEqual(prof[2]["shapes"], {"number": 2})
        self.assertEqual(prof[3]["shapes"], {"number": 1, "lt-number": 1})
        self.assertEqual(prof[1]["counts"], {"Green": 1, "Black": 1})
        dump = json.dumps(out)
        for v in ("0.011", "0.012", "0.4", "<0.1"):
            self.assertNotIn(v, dump, v)


class PdfTable(unittest.TestCase):
    def test_recount(self):
        r = dc.pdf_table(PDF_TEXT)
        self.assertEqual(r["stated"], {"PESTICIDES-FPH053": 4, "PESTICIDES-LC": 2})
        self.assertEqual(r["method_rows"], {"PESTICIDES-FPH053": 4, "PESTICIDES-LC": 2})
        self.assertEqual(r["component_rows"], 6)
        self.assertTrue(r["paired"])
        self.assertEqual(r["distinct"], {"PESTICIDES-FPH053": 3, "PESTICIDES-LC": 2})
        self.assertEqual(r["repeated"], {"PESTICIDES-FPH053": ["naled"], "PESTICIDES-LC": []})
        self.assertEqual(r["shared"], ["mexacarbate"])
        self.assertEqual(r["distinct_all"], 4)
        self.assertEqual(r["names"], ["aldrin", "carbaryl", "mexacarbate", "naled"])


class Addendum(unittest.TestCase):
    def setUp(self):
        with open(DOC, encoding="utf-8") as fh:
            self.doc = fh.read()

    def test_marker_disclosure_signature(self):
        self.assertIn("ADDENDUM-MARKER: dried-tea-2009-0.1.1-addendum", self.doc)
        self.assertIn("Made with AI agents working in MV2's (Munim, Inc.) name", self.doc)
        self.assertTrue(self.doc.rstrip().endswith("MV2, Munim, Inc., mv2@munimtech.com"))
        self.assertNotRegex(self.doc, r"\bMIT\b")
        self.assertIsNone(STREET.search(self.doc))

    def test_a1_arithmetic(self):
        for phrase in ("| 206 | 207 | 207 |", "| 160 | 157 | 157 |", "| 366 | 364 | 364 |",
                       "**202 distinct names**", "**353 distinct component names**"):
            self.assertIn(phrase, self.doc, phrase)
        repeats = {"Bendiocarb": 2, "Mexacarbate": 2, "Naled": 2, "Dicrotophos": 3}
        self.assertEqual(207 - sum(n - 1 for n in repeats.values()), 202)
        self.assertEqual(202 + 157 - 6, 353)
        self.assertEqual((206 + 160, 207 + 157), (366, 364))

    def test_items_present(self):
        self.assertIn("## A1.", self.doc)
        for item in ("A2.", "A3.", "A4.", "A5.", "A6.", "A7."):
            self.assertIn("- " + item, self.doc, item)


if __name__ == "__main__":
    unittest.main()
