# SPDX-License-Identifier: Apache-2.0
# Offline tests for alternaria_eu.py on small synthetic files in CFIA's open-data layout.
import csv
import io
import os
import tempfile
import unittest

import alternaria_eu as ae

HEADER = ["Sample No. – No. d’échantillon", "Region - Région", "Function", "Fonction", "Origin", "Origine",
          "Product Type", "Product", "Produit", "Date Sampled", "Component", "Composant", "Result", "Unit - Unité"]


def _file(rows):
    """rows: [(id, origin, type, product, value, component)] -> CSV bytes (utf-8 with BOM)."""
    out = io.StringIO()
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerow(HEADER)
    for sid, origin, kind, product, value, comp in rows:
        w.writerow([sid, "ONTARIO", "Import", "Importé", origin, origin, kind, product, product, "2020-06-01",
                    comp, comp, value, "ppb"])
    return ("﻿" + out.getvalue()).encode("utf-8")


def _s(sid, origin, kind, product, aoh, ame):
    """One sample = an AOH row and an AME row."""
    return [(sid, origin, kind, product, aoh, "Alternariol"),
            (sid, origin, kind, product, ame, "Alternariol monomethyl ether")]


def _many(n, prefix, origin, kind, product, aoh, ame):
    out = []
    for i in range(n):
        out += _s("%s%04d" % (prefix, i), origin, kind, product, aoh, ame)
    return out


PFV, NUT, POM, INF = "Processed fruits and vegetables", "Nut/seed products", "Pomegranate products", "Infant foods"


def _all_met():
    return (_many(2400, "W", "Canada", "Grain-based foods", "Wheat flour", "1", "1")
            + _s("T1", "Italy", PFV, "Whole tomatoes", "800", "80")
            + _s("T2", "Italy", PFV, "Diced tomatoes", "300", "50")
            + _s("T3", "Spain", PFV, "Tomato sauce", "1", "6")
            + _many(20, "TW", "Canada", PFV, "Tomato sauce", "1", "1")
            + _many(10, "SE", "Turkey", NUT, "Sesame seeds", "2", "2")
            + _many(10, "SU", "Canada", NUT, "Sunflower seeds", "5", "5")
            + _many(2, "OA", "Ukraine", "Sunflower oil", "Sunflower oil", "12", "1")
            + _many(38, "OW", "Ukraine", "Sunflower oil", "Sunflower oil", "2", "2")
            + _many(3, "IA", "Canada", INF, "Infant rice cereal", "3", "0")
            + _many(7, "IW", "Canada", INF, "Infant rice cereal", "1", "1")
            + _many(5, "PT", "Turkey", POM, "Pomegranate juice", "150", "10")
            + _many(2, "PU", "USA", POM, "Pomegranate juice", "100", "5")
            + _many(5, "PC", "Canada", POM, "Pomegranate juice blend", "5", "1"))


def _misses():
    return (_many(2490, "W", "Canada", "Grain-based foods", "Wheat flour", "1", "1")
            + _s("T1", "Italy", PFV, "Whole tomatoes", "800", "70")
            + _many(9, "TW", "Canada", PFV, "Tomato sauce", "1", "1")
            + _s("SA", "Canada", NUT, "Sesame seeds", "31", "0")
            + _many(9, "SE", "Turkey", NUT, "Sesame seeds", "2", "2")
            + _many(10, "OW", "Ukraine", "Sunflower oil", "Sunflower oil", "2", "2")
            + _s("IA", "Canada", INF, "Infant rice cereal", "3", "0")
            + _many(9, "IW", "Canada", INF, "Infant rice cereal", "1", "1")
            + _many(5, "PC", "Canada", POM, "Pomegranate juice", "200", "0")
            + _many(5, "PU", "USA", POM, "Pomegranate juice", "50", "0"))


class Parse(unittest.TestCase):
    def test_components_duplicates_and_other_rows(self):
        rows, check = ae.parse(_file(_s("A1", "Italy", PFV, "Whole tomatoes", "8", "6")
                                     + _s("A1D", "Italy", PFV, "Whole tomatoes", "4", "2")
                                     + _s("A2", "Turkey", POM, "Pomegranate juice", "300", "20")
                                     + [("A3", "Canada", "Sunflower oil", "Sunflower oil", "5", "Tenuazonic acid")]
                                     + _s("A3", "Canada", "Sunflower oil", "Sunflower oil", "11", "<0.1")))
        self.assertEqual((check["data_rows"], check["samples"], check["other_component_rows"]), (9, 3, 1))
        self.assertEqual(check["with_components"], 3)
        a1, a2, a3 = rows
        self.assertEqual((a1["aoh"], a1["ame"], a1["total"], a1["category"], a1["state"], a1["origin"]),
                         (6.0, 4.0, 10.0, "processed tomato", "within", "ITALY"))
        self.assertEqual(a1["results"], 4)
        self.assertEqual((a2["category"], a2["pomegranate"], a2["total"], a2["state"]), ("", True, 320.0, ""))
        self.assertEqual((a3["aoh"], a3["ame"], a3["category"], a3["state"]), (11.0, 0.0, "sunflower oil", "above"))

    def test_totals_only_file(self):
        raw = ("Sample No.,Origin,Product,Result,Unit\n"
               "T1,Spain,Diced tomatoes,20,ppb\nT2,Domestic,Tomato sauce,4.9,ppb\nT3,USA,Crushed tomatoes,12,ppb\n"
               "T4,Canada,Sunflower oil,25,ppb\nT5,Canada,Sunflower oil,15,ppb\n").encode("utf-8")
        rows, check = ae.parse(raw)
        self.assertEqual(check["with_components"], 0)
        self.assertEqual([r["state"] for r in rows], ["above", "within", "undetermined", "above", "undetermined"])
        self.assertEqual([r["origin"] for r in rows], ["SPAIN", "CANADA", "UNITED STATES", "CANADA", "CANADA"])
        self.assertEqual(rows[0]["total"], 20.0)

    def test_units(self):
        self.assertEqual(ae.number("0.5", "ppb"), (0.5, True))
        self.assertEqual(ae.number("0.5", "ppm"), (500.0, True))
        self.assertEqual(ae.number("<0.05", "ppb"), (0.0, True))
        self.assertEqual(ae.number("ND", ""), (0.0, True))
        self.assertEqual(ae.number("1,5", "ug/kg"), (1.5, True))
        self.assertEqual(ae.number("2", ""), (2.0, True))
        self.assertEqual(ae.number("x", "ppb"), (None, False))
        self.assertEqual(ae.number("3", "furlongs"), (None, False))

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            ae.parse("Sample,Component\nX,Alternariol\n".encode("utf-8"))


class Rules(unittest.TestCase):
    def test_component_of(self):
        self.assertEqual([ae.component_of(c) for c in ("Alternariol", "Alternariol monomethyl ether", "AME",
                                                       "Total Alternaria toxins", "Tenuazonic acid",
                                                       "Alternariol monométhyl éther")],
                         ["AOH", "AME", "AME", "TOTAL", "", "AME"])

    def test_category(self):
        cases = ((INF, "Rice cereal for babies", "infant cereal"), (INF, "Pear puree", ""),
                 ("Grain-based foods", "Teething biscuits", "infant cereal"), (PFV, "Tomato paste", "processed tomato"),
                 ("", "Fresh tomatoes", ""), (NUT, "Sesame seeds", "sesame seeds"), ("", "Toasted sesame oil", ""),
                 (NUT, "Sunflower seeds, roasted", "sunflower seeds"), ("", "Sunflower seed butter", ""),
                 ("Sunflower oil", "Brand X", "sunflower oil"), ("Grain-based foods", "Barley flakes", ""))
        for kind, product, want in cases:
            self.assertEqual(ae.category(kind, product), want, product)
        self.assertTrue(ae.is_pomegranate(POM, "Juice blend"))
        self.assertFalse(ae.is_pomegranate("", "Grenadine syrup"))

    def test_bounded(self):
        def xs(above, und, within):
            return [{"state": "above"}] * above + [{"state": "undetermined"}] * und + [{"state": "within"}] * within
        self.assertEqual(ae.bounded(xs(1, 2, 3), lambda k, n: 2 <= k <= 4), ("not gradable", "1 above of 6 (2 undetermined)"))
        self.assertEqual(ae.bounded(xs(1, 2, 3), lambda k, n: k == 0)[0], "not met")
        self.assertEqual(ae.bounded(xs(2, 0, 3), lambda k, n: 2 <= k <= 4)[0], "met")


class Grade(unittest.TestCase):
    def test_all_met(self):
        g = ae.grade(ae.parse(_file(_all_met()))[0])
        p = g["predictions"]
        self.assertEqual(g["samples"], 2505)
        self.assertEqual(p["P1"]["value"], "2505 samples")
        self.assertEqual(p["P2"]["value"], "880 ppb (Whole tomatoes; processed tomato)")
        self.assertEqual(p["P3"]["value"], "3 above of 23 (0 undetermined)")
        self.assertEqual(p["P4"]["value"], "0 above of 20 (0 undetermined)")
        self.assertEqual(p["P5"]["value"], "2 above of 40 (0 undetermined)")
        self.assertEqual(p["P6"]["value"], "3 above of 10 (0 undetermined)")
        self.assertEqual(p["P7"]["value"], {"TURKEY": 5, "UNITED STATES": 2})
        self.assertEqual(p["P8"]["value"], {"foreign_median": 160.0, "canada_median": 6.0, "n_foreign": 7,
                                            "n_canada": 5})
        self.assertEqual(p["P9"]["value"], "5 of 8")
        self.assertEqual((g["met"], g["gradable"]), (9, 9))

    def test_misses(self):
        g = ae.grade(ae.parse(_file(_misses()))[0])
        p = g["predictions"]
        self.assertEqual(g["samples"], 2540)
        self.assertEqual((p["P1"]["status"], p["P2"]["status"]), ("met", "met"))
        for k in ("P3", "P4", "P5", "P6", "P7", "P8", "P9"):
            self.assertEqual(p[k]["status"], "not met", k)
        self.assertEqual(p["P7"]["value"], {"CANADA": 5})
        self.assertEqual(p["P9"]["value"], "1 of 3")
        self.assertEqual((g["met"], g["gradable"]), (2, 9))

    def test_too_small_is_not_gradable(self):
        g = ae.grade(ae.parse(_file(_many(10, "T", "Italy", PFV, "Diced tomatoes", "20", "0")))[0])
        self.assertFalse(g["gradable_parse"])
        self.assertEqual(g["predictions"]["P1"]["status"], "not met")
        self.assertEqual(g["predictions"]["P3"]["status"], "not gradable")
        self.assertEqual((g["met"], g["gradable"]), (0, 1))


class Main(unittest.TestCase):
    def test_main_on_local_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, out = os.path.join(tmp, "data"), os.path.join(tmp, "out")
            os.makedirs(data)
            with open(os.path.join(data, "alternaria.csv"), "wb") as f:
                f.write(_file(_all_met()))
            self.assertEqual(ae.main(["--data-dir", data, "--out-dir", out]), 0)
            with open(os.path.join(out, "alternaria_samples.csv"), encoding="utf-8") as f:
                self.assertEqual(len(list(csv.reader(f))), 2506)            # header + 2505 samples
            with open(os.path.join(out, "summary.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("alternaria_eu", text)
            self.assertIn("| processed tomato | 10/5 | 23 | 3 | 20 | 0 |", text)


if __name__ == "__main__":
    unittest.main()
