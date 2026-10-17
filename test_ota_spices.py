# SPDX-License-Identifier: Apache-2.0
# Offline tests for ota_spices.py on small synthetic files in CFIA's open-data layout.
import csv
import io
import unittest

import ota_spices as ota

HEADER = ["Sample No. – No. d’échantillon", "Region - Région", "Product Type", "Type de produit",
          "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled – Date d’échantillonage", "Component", "Composant", "Result", "Unit - Unité"]


def _file(samples, header=HEADER):
    """samples: [(id, kind, origin, product, value[, component])] -> CSV bytes (utf-8 with BOM)."""
    out = io.StringIO()
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerow(header)
    for s in samples:
        sid, kind, origin, product, value = s[:5]
        comp = s[5] if len(s) > 5 else "Ochratoxin A"
        w.writerow([sid, "ONTARIO", kind, kind, "Import", "Importé", origin, origin, product, product,
                    "2014-06-01", comp, comp, value, "ppb"])
    return ("﻿" + out.getvalue()).encode("utf-8")


def _many(n, prefix, kind, origin, product, value):
    return [("%s%05d" % (prefix, i), kind, origin, product, value) for i in range(n)]


class Parse(unittest.TestCase):
    def test_counts_duplicates_and_components(self):
        rows, check = ota.parse(_file([("A1", "Spices", "India", "Paprika", "25"),
                                       ("A1D", "Spices", "India", "Paprika", "30"),
                                       ("A2", "Grain-based foods", "Canada", "Corn flakes", "<0.04"),
                                       ("A2", "Grain-based foods", "Canada", "Corn flakes", "2", "Aflatoxin B1")]))
        self.assertEqual(check["data_rows"], 4)
        self.assertEqual(check["samples"], 2)                # the D duplicate merges into its base
        self.assertEqual(check["other_component_rows"], 1)
        self.assertTrue(check["have_type_column"])
        a1, a2 = rows
        self.assertEqual((a1["ppb"], a1["results"], a1["spice_type"], a1["eu_limit"]), (30.0, 2, "paprika", 20.0))
        self.assertTrue(a1["over_eu"])
        self.assertEqual((a2["ppb"], a2["spice"], a2["origin"]), (0.0, False, "CANADA"))

    def test_units(self):
        self.assertEqual(ota.ppb("0.5", "mg/kg"), (500.0, True))
        self.assertEqual(ota.ppb("1,5", "µg/kg"), (1.5, True))
        self.assertEqual(ota.ppb("ND", "ppb"), (0.0, True))
        self.assertEqual(ota.ppb("2", ""), (2.0, True))
        self.assertEqual(ota.ppb("x", "ppb"), (None, False))
        self.assertEqual(ota.ppb("3", "furlongs"), (None, False))

    def test_no_type_column_uses_names(self):
        header = ["Sample No.", "Origin", "Product", "Component", "Result", "Unit"]
        raw = ("﻿" + "\n".join([",".join(header),
                                     "F1,India,Black peppercorns,Ochratoxin A,20,ppb",
                                     "F2,Canada,Ginger cookies,Ochratoxin A,5,ppb",
                                     "F3,USA,Sultanas,Ochratoxin A,11,ppb"]) + "\n").encode("utf-8")
        rows, check = ota.parse(raw)
        self.assertFalse(check["have_type_column"])
        f1, f2, f3 = rows
        self.assertEqual((f1["spice"], f1["spice_type"], f1["over_eu"]), (True, "pepper", True))
        self.assertFalse(f2["spice"])
        self.assertEqual((f3["vine_fruit"], f3["origin"]), (True, "UNITED STATES"))

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            ota.parse("Sample,Component\nX,OTA\n".encode("utf-8"))


class Rules(unittest.TestCase):
    def test_spice_type(self):
        self.assertEqual(ota.spice_type("Smoked Paprika"), ("paprika", 20.0))
        self.assertEqual(ota.spice_type("Chili powder"), ("chili", 20.0))
        self.assertEqual(ota.spice_type("Crushed red pepper flakes"), ("chili", 20.0))
        self.assertEqual(ota.spice_type("Ground nutmeg"), ("nutmeg", 15.0))
        self.assertEqual(ota.spice_type("Garam masala"), ("mixture", 15.0))
        self.assertEqual(ota.spice_type("Madras curry"), ("mixture", 15.0))
        self.assertEqual(ota.spice_type("Lemon pepper seasoning"), ("mixture", 15.0))
        self.assertEqual(ota.spice_type("Black pepper"), ("pepper", 15.0))
        self.assertEqual(ota.spice_type("Curry leaves"), ("other", None))
        self.assertEqual(ota.spice_type("Cinnamon"), ("other", None))

    def test_is_spice_and_vine_fruit(self):
        self.assertTrue(ota.is_spice("Spices", "Anything", True))
        self.assertFalse(ota.is_spice("Licorice", "Anise licorice", True))
        self.assertTrue(ota.is_spice("", "Black peppercorns", False))
        self.assertTrue(ota.is_spice("", "Vanilla beans", False))
        self.assertFalse(ota.is_spice("", "Chili beans", False))
        self.assertFalse(ota.is_spice("", "Ginger cookies", False))
        self.assertTrue(ota.is_vine_fruit("Dried fruits", "Sultana raisins", True))
        self.assertFalse(ota.is_vine_fruit("Grain-based foods", "Raisin bran", True))
        self.assertFalse(ota.is_vine_fruit("Dried fruits", "Dried figs", True))
        self.assertTrue(ota.is_vine_fruit("", "Thompson raisins", False))


class Grade(unittest.TestCase):
    def _grade(self, samples):
        rows, check = ota.parse(_file(samples))
        return ota.grade(rows, check)

    def _all_met(self, top_product="Paprika"):
        return ([("S0", "Spices", "Spain", top_product, "1770")]
                + _many(7200, "G", "Grain-based foods", "Canada", "Wheat flour", "0.5")
                + _many(80, "I", "Spices", "India", "Chili powder", "25")
                + _many(5, "N", "Spices", "Indonesia", "Nutmeg", "40")
                + _many(20, "C", "Spices", "Canada", "Black pepper", "1")
                + _many(694, "V", "Spices", "Vietnam", "Cinnamon", "0")
                + _many(6, "R", "Dried fruits", "Turkey", "Raisins", "20"))

    def test_all_met(self):
        g = self._grade(self._all_met())
        self.assertTrue(g["gradable_parse"])
        self.assertEqual((g["samples"], g["spices"]), (8006, 800))
        self.assertTrue(g["predictions"]["P3"]["value"].startswith("86 of 800 ("))
        self.assertEqual(g["predictions"]["P6"]["value"], "Canada 0/20, foreign 86/780")
        self.assertEqual((g["met"], g["gradable"]), (8, 8))

    def test_misses(self):
        samples = ([("S0", "Spices", "Unknown", "Paprika", "1770")]
                   + _many(7300, "G", "Grain-based foods", "Canada", "Wheat flour", "0.5")
                   + _many(10, "C", "Spices", "Canada", "Chili powder", "25")
                   + _many(5, "I", "Spices", "India", "Turmeric", "16")
                   + _many(3, "N", "Spices", "India", "Nutmeg", "20")
                   + _many(3, "M", "Spices", "Indonesia", "Nutmeg", "20")
                   + _many(700, "X", "Spices", "China", "Garlic powder", "0")
                   + [("R1", "Dried fruits", "USA", "Raisins", "12"),
                      ("R2", "Dried fruits", "Iran", "Sultanas", "50")])
        g = self._grade(samples)
        p = g["predictions"]
        self.assertEqual((g["samples"], g["spices"]), (8024, 722))
        self.assertEqual(p["P2"]["status"], "met")
        for k in ("P3", "P4", "P5", "P6", "P7", "P8"):
            self.assertEqual(p[k]["status"], "not met", k)
        self.assertTrue(p["P3"]["value"].startswith("22 of 722 ("))           # 3.0%, under 5%
        self.assertEqual(p["P4"]["value"], ota.UNKNOWN)
        self.assertEqual(p["P5"]["value"], {"CANADA": 10, "INDIA": 8, "INDONESIA": 3})
        self.assertEqual(p["P6"]["value"], "Canada 10/10, foreign 11/711")
        self.assertEqual(p["P8"]["value"], {"INDIA": 3, "INDONESIA": 3})        # a tie is not met
        self.assertEqual((g["met"], g["gradable"]), (2, 8))

    def test_max_not_paprika_is_inconsistent(self):
        p = self._grade(self._all_met("Cayenne"))["predictions"]
        self.assertEqual(p["P2"]["status"], "not met")
        self.assertEqual(p["P4"]["status"], "not gradable")

    def test_too_small_is_not_gradable(self):
        g = self._grade(_many(10, "G", "Grain-based foods", "Canada", "Wheat flour", "0.5"))
        self.assertFalse(g["gradable_parse"])
        self.assertEqual(g["predictions"]["P1"]["status"], "not met")
        self.assertEqual(g["predictions"]["P2"]["status"], "not gradable")
        self.assertEqual((g["met"], g["gradable"]), (0, 1))

    def test_spice_count_out_of_range(self):
        g = self._grade(_many(8000, "G", "Grain-based foods", "Canada", "Wheat flour", "0")
                        + _many(100, "S", "Spices", "India", "Paprika", "1"))
        self.assertFalse(g["gradable_parse"])


class Describe(unittest.TestCase):
    def test_tables(self):
        rows, _ = ota.parse(_file([("S1", "Spices", "Spain", "Paprika", "30"),
                                   ("S2", "Spices", "Spain", "Cumin", "2"),
                                   ("R1", "Dried fruits", "Iran", "Raisins", "11")]))
        d = ota.describe(rows)
        self.assertEqual(d["spices_by_type"]["paprika"]["over_eu"], 1)
        self.assertEqual(d["spices_by_origin"]["SPAIN"], {"n": 2, "with_eu_limit": 1, "over_eu": 1, "max_ppb": 30.0})
        self.assertEqual(d["top_25_spices"][0]["product"], "Paprika")
        self.assertEqual(d["vine_fruit_over_10_ppb"][0]["origin"], "IRAN")
        self.assertIn("ota_spices", ota.summary_md({"grade": ota.grade(rows, {}), "descriptive": d,
                                                    "check": {"data_rows": 3, "samples": 3, "bad_numbers": 0,
                                                              "other_component_rows": 0,
                                                              "have_type_column": True, "header": [],
                                                              "units": {}, "types": {}}}))


if __name__ == "__main__":
    unittest.main()
