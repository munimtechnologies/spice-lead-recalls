# SPDX-License-Identifier: Apache-2.0
# Offline tests for coumarin_cinnamon.py on small synthetic files in CFIA's open-data layout.
import csv
import io
import os
import tempfile
import unittest

import coumarin_cinnamon as cc

HEADER = ["Sample No. – No. d’échantillon", "Region - Région", "Function", "Fonction", "Origin", "Origine",
          "Product", "Produit", "Date Sampled", "Component", "Composant", "Result", "Unit - Unité"]


def _file(samples, unit="ppm", header=HEADER):
    """samples: [(id, origin, product, value[, component])] -> CSV bytes (utf-8 with BOM)."""
    out = io.StringIO()
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerow(header)
    for s in samples:
        sid, origin, product, value = s[:4]
        comp = s[4] if len(s) > 4 else "Coumarin"
        w.writerow([sid, "ONTARIO", "Import", "Importé", origin, origin, product, product, "2012-06-01",
                    comp, comp, value, unit])
    return ("﻿" + out.getvalue()).encode("utf-8")


def _many(n, prefix, origin, product, value):
    return [("%s%03d" % (prefix, i), origin, product, value) for i in range(n)]


def _rows(files):
    rows = []
    for label, raw in files:
        rows += cc.parse(raw, label)[0]
    return rows


def _all_met_files():
    return [("2011-12", _file(_many(10, "R", "China", "Ground cinnamon", "100"))),
            ("2012-13", _file(_many(40, "I", "Indonesia", "Ground cinnamon", "3000")
                              + [("T1", "China", "Ground cinnamon", "7621")]
                              + _many(2, "C", "Sri Lanka", "Ceylon cinnamon", "50")
                              + [("L1", "Sri Lanka", "Cinnamon sticks", "20")]
                              + _many(2, "S", "Vietnam", "Saigon cinnamon", "4000"))),
            ("2014-15", _file(_many(3, "M", "Mexico", "Pure vanilla extract", "2")
                              + [("N1", "Madagascar", "Pure vanilla extract", "1")]
                              + _many(5, "Z", "Madagascar", "Pure vanilla extract", "ND"))),
            ("2015-16", _file(_many(27, "G", "Unknown", "Ground cinnamon", "2500")
                              + [("H1", "Unknown", "Ground cinnamon", "5040")]))]


class Parse(unittest.TestCase):
    def test_counts_duplicates_and_components(self):
        rows, check = cc.parse(_file([("A1", "Sri Lanka", "Ceylon cinnamon sticks", "10"),
                                      ("A1D", "Sri Lanka", "Ceylon cinnamon sticks", "20"),
                                      ("A2", "Viet Nam", "Ground Saigon cinnamon", "5000"),
                                      ("A3", "Canada", "Pumpkin pie spice", "800"),
                                      ("A3", "Canada", "Pumpkin pie spice", "1", "Lead")]), "2012-13")
        self.assertEqual((check["data_rows"], check["samples"], check["other_component_rows"]), (5, 3, 1))
        self.assertEqual((check["cinnamon"], check["unit_override"]), (2, False))
        a1, a2, a3 = rows
        self.assertEqual((a1["ppm"], a1["results"], a1["form"], a1["claim"], a1["class"], a1["origin"]),
                         (15.0, 2, "stick", "ceylon", "verum-type", "SRI LANKA"))
        self.assertEqual((a2["origin"], a2["claim"], a2["form"], a2["class"]),
                         ("VIETNAM", "cassia", "ground", "cassia-type"))
        self.assertEqual((a3["cinnamon"], a3["class"], a3["ppm"]), (False, "", 800.0))

    def test_units(self):
        self.assertEqual(cc.number("0.5", "ppb"), (0.5, 1000.0, True))
        self.assertEqual(cc.number("<0.1", "ppm"), (0.0, 1.0, True))
        self.assertEqual(cc.number("ND", ""), (0.0, 1.0, True))
        self.assertEqual(cc.number("1,5", "mg/kg"), (1.5, 1.0, True))
        self.assertEqual(cc.number("2", ""), (2.0, 1.0, True))
        self.assertEqual(cc.number("x", "ppm"), (None, None, False))
        self.assertEqual(cc.number("3", "furlongs"), (None, None, False))

    def test_ppb_label_on_ppm_numbers_is_overridden(self):
        rows, check = cc.parse(_file([("B1", "Unknown", "Ground cinnamon", "5040"),
                                      ("B2", "Unknown", "Ceylon cinnamon", "6.8"),
                                      ("B3", "Mexico", "Pure vanilla extract", "2")], unit="ppb"), "2015-16")
        self.assertTrue(check["unit_override"])
        self.assertEqual([r["ppm"] for r in rows], [5040.0, 6.8, 2.0])
        self.assertTrue(rows[2]["vanilla"])

    def test_real_ppb_is_converted(self):
        rows, check = cc.parse(_file([("C1", "China", "Ground cinnamon", "3000000")], unit="ppb"), "x")
        self.assertFalse(check["unit_override"])
        self.assertEqual((rows[0]["ppm"], rows[0]["class"]), (3000.0, "cassia-type"))

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            cc.parse("Sample,Component\nX,Coumarin\n".encode("utf-8"))


class Rules(unittest.TestCase):
    def test_is_cinnamon(self):
        for kind, product in (("", "Ground cinnamon"), ("", "Cassia bark"), ("", "Canela entera"),
                              ("Ground cinamon", "Brand X"), ("Spices", "Cinnamon sticks")):
            self.assertTrue(cc.is_cinnamon(kind, product), product)
        for kind, product in (("", "Cinnamon sugar"), ("", "Apple cinnamon tea"), ("", "Cinnamon raisin bagel"),
                              ("", "Ceylon tea with cinnamon"), ("", "Cinnamon oil"), ("", "Pumpkin pie spice"),
                              ("Cinnamon-containing foods", "Cinnamon")):
            self.assertFalse(cc.is_cinnamon(kind, product), product)

    def test_form_claim_class(self):
        self.assertEqual([cc.form_of(p) for p in ("Cinnamon sticks", "Cassia bark", "Ground cinnamon",
                                                  "Canela entera")], ["stick", "stick", "ground", "stick"])
        self.assertEqual([cc.claim_of(p) for p in ("Ceylon cinnamon", "True cinnamon, ground", "Saigon cinnamon",
                                                   "Korintje cinnamon", "Ground cinnamon",
                                                   "Ceylon cinnamon from China", "Cinnamon (Sri Lanka)")],
                         ["ceylon", "ceylon", "cassia", "cassia", "none", "both", "ceylon"])
        self.assertEqual([cc.klass(x) for x in (0.0, 299.9, 300.0, 999.0, 1000.0)],
                         ["verum-type", "verum-type", "intermediate", "intermediate", "cassia-type"])

    def test_is_vanilla(self):
        self.assertTrue(cc.is_vanilla("", "Pure vanilla extract"))
        self.assertTrue(cc.is_vanilla("", "Imitation vanilla flavour"))
        self.assertTrue(cc.is_vanilla("Oils and extracts", "Vanilla"))
        self.assertFalse(cc.is_vanilla("", "Vanilla chai tea"))
        self.assertFalse(cc.is_vanilla("", "Vanilla ice cream"))
        self.assertFalse(cc.is_vanilla("", "Cinnamon vanilla extract"))


class Grade(unittest.TestCase):
    def test_all_met_and_replication_excluded(self):
        g = cc.grade(_rows(_all_met_files()))
        p = g["predictions"]
        self.assertTrue(g["gradable_parse"])
        self.assertEqual(g["primary_cinnamon"], 74)
        self.assertEqual(p["P1"]["value"], "74 primary, 28 in 2015-16")
        self.assertTrue(p["P3"]["value"].startswith("71 of 74 ("))
        self.assertEqual(p["P6"]["value"], {"cassia-type": 2})
        self.assertEqual(p["P7"]["value"], {"cassia-type": 43})          # 2011-12's China rows stay out
        self.assertEqual(p["P8"]["value"], {"verum-type": 3})
        self.assertEqual(p["P9"]["value"], {"MEXICO": 3, "MADAGASCAR": 1})
        self.assertEqual((g["met"], g["gradable"]), (9, 9))

    def test_misses(self):
        files = [("2012-13", _file(_many(30, "I", "Indonesia", "Ground cinnamon", "500")
                                   + [("T1", "China", "Ground cinnamon", "7621"),
                                      ("C1", "Sri Lanka", "Ceylon cinnamon", "3000"),
                                      ("C2", "Canada", "Ceylon cinnamon", "40"),
                                      ("K1", "Canada", "Cassia cinnamon", "200"),
                                      ("S1", "Vietnam", "Saigon cinnamon", "4000"),
                                      ("L1", "Sri Lanka", "Cinnamon sticks", "2000"),
                                      ("L2", "Sri Lanka", "Ground cinnamon", "800"),
                                      ("H1", "China", "Cinnamon sticks", "100")])),
                 ("2014-15", _file([("M1", "Mexico", "Pure vanilla extract", "3"),
                                    ("M2", "Mexico", "Pure vanilla extract", "3"),
                                    ("V1", "Madagascar", "Pure vanilla extract", "2"),
                                    ("V2", "Madagascar", "Pure vanilla extract", "2")])),
                 ("2015-16", _all_met_files()[3][1])]
        g = cc.grade(_rows(files))
        p = g["predictions"]
        self.assertEqual(g["primary_cinnamon"], 66)
        self.assertEqual((p["P1"]["status"], p["P2"]["status"]), ("met", "met"))
        for k in ("P3", "P4", "P5", "P6", "P7", "P8", "P9"):
            self.assertEqual(p[k]["status"], "not met", k)
        self.assertTrue(p["P3"]["value"].startswith("32 of 66 ("))
        self.assertTrue(p["P4"]["value"].startswith("31 of 66 ("))
        self.assertEqual([x["ppm"] for x in p["P5"]["value"]], [3000.0, 40.0])
        self.assertEqual(p["P6"]["value"], {"cassia-type": 1, "verum-type": 1})
        self.assertEqual(p["P7"]["value"], {"intermediate": 30, "cassia-type": 2, "verum-type": 1})
        self.assertEqual(p["P8"]["value"], {"cassia-type": 2, "intermediate": 1})
        self.assertEqual(p["P9"]["value"], {"MADAGASCAR": 2, "MEXICO": 2})       # a tie is not met
        self.assertEqual((g["met"], g["gradable"]), (2, 9))

    def test_too_small_is_not_gradable(self):
        g = cc.grade(_rows([("2015-16", _file(_many(10, "G", "Unknown", "Ground cinnamon", "2500")))]))
        self.assertFalse(g["gradable_parse"])
        self.assertEqual(g["predictions"]["P1"]["status"], "not met")
        self.assertEqual(g["predictions"]["P2"]["status"], "not gradable")
        self.assertEqual((g["met"], g["gradable"]), (0, 1))


class Describe(unittest.TestCase):
    def test_tables_and_summary(self):
        r1, c1 = cc.parse(_file([("A", "Sri Lanka", "Ceylon cinnamon", "40"),
                                 ("B", "China", "Ground cinnamon", "3000"),
                                 ("V", "Mexico", "Pure vanilla extract", "2")]), "2012-13")
        rows = r1 + cc.parse(_file([("R", "China", "Cinnamon sticks", "500")]), "2011-12")[0]
        d = cc.describe(rows)
        self.assertEqual(d["primary"]["n"], 2)
        self.assertEqual(d["primary"]["by_origin"]["SRI LANKA"],
                         {"n": 1, "verum-type": 1, "intermediate": 0, "cassia-type": 0, "max_ppm": 40.0})
        self.assertEqual([x["product"] for x in d["primary"]["claimed_or_sri_lanka"]], ["Ceylon cinnamon"])
        self.assertEqual(d["replication_2011_12"]["intermediate"][0]["sample"], "R")
        self.assertEqual(d["vanilla"]["detected"][0]["origin"], "MEXICO")
        self.assertIn("coumarin_cinnamon", cc.summary_md({"grade": cc.grade(rows), "descriptive": d,
                                                          "checks": [c1]}))


class Main(unittest.TestCase):
    def test_main_on_local_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, out = os.path.join(tmp, "data"), os.path.join(tmp, "out")
            os.makedirs(data)
            for label, raw in _all_met_files():
                with open(os.path.join(data, "%s.csv" % label), "wb") as f:
                    f.write(raw)
            self.assertEqual(cc.main(["--data-dir", data, "--out-dir", out]), 0)
            with open(os.path.join(out, "coumarin_samples.csv"), encoding="utf-8") as f:
                self.assertEqual(len(list(csv.reader(f))), 94)            # header + 84 cinnamon + 9 vanilla
            for name in ("grades.json", "summary.md"):
                self.assertTrue(os.path.exists(os.path.join(out, name)), name)


if __name__ == "__main__":
    unittest.main()
