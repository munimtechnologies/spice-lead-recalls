"""Unit tests for cfia_chromate_2018 on synthetic rows (no CFIA value is used).

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import unittest

import cfia_chromate_2018 as c

HEADER = ('﻿"Sample No. – No. d’échantillon","Region - Région","Commodity",'
          '"Denrée","Function","Fonction","Origin","Origine","Product","Produit",'
          '"Date Sampled – Date d’échantillonage","Component","Composant","AMOUNT",'
          '"Report Unit - Unité de rapport"')


def row(sid, product, comp, amount, function="Import/importé", origin="INDIA/INDE"):
    unit = "" if comp == "Chromates" else "ug/g"
    return ('"%s","ONTARIO","IMFD","DAIM","%s","%s","%s","%s","%s","%s","2018-06-01","%s","%s","%s","%s"'
            % (sid, function, function, origin, origin, product, product, comp, comp, amount, unit))


def sample(sid, product, pb, cr, spot="Negative/Négatif"):
    return [row(sid, product, "Lead/Plomb", pb), row(sid, product, "Chromium/Chrome", cr),
            row(sid, product, "Chromates", spot)]


def build(samples):
    lines = [HEADER]
    for s in samples:
        lines += sample(*s)
    return ("\n".join(lines) + "\n").encode("utf-8")


class TestHelpers(unittest.TestCase):
    def test_component(self):
        self.assertEqual(c.component_of("Lead/Plomb"), "pb")
        self.assertEqual(c.component_of("Chromium/Chrome"), "cr")
        self.assertEqual(c.component_of("Chromates"), "spot")
        self.assertIsNone(c.component_of("Cadmium"))

    def test_matrix(self):
        self.assertEqual(c.matrix_of("Turmeric"), "turmeric")
        self.assertEqual(c.matrix_of("Cayenne Pepper"), "chili/paprika")
        self.assertEqual(c.matrix_of("Chili Powder"), "chili/paprika")
        self.assertEqual(c.matrix_of("Paprika"), "chili/paprika")
        self.assertEqual(c.matrix_of("Coriander"), "coriander")
        self.assertEqual(c.matrix_of("Star Anise"), "generic")
        self.assertEqual(c.matrix_of("Spice Blend"), "generic")
        self.assertEqual(c.matrix_of("Thyme"), "generic")

    def test_ratio_and_verdict(self):
        # PbCrO4: 207.2 g lead per 51.996 g chromium -> molar ratio 1.
        self.assertAlmostEqual(c.molar_ratio(207.2, 51.996), 1.0)
        self.assertIsNone(c.molar_ratio(0.0, 1.0))
        self.assertIsNone(c.molar_ratio(1.0, 0.0))
        self.assertEqual(c.nyc_verdict(20.72, 5.1996), "chromate-like")
        self.assertEqual(c.nyc_verdict(10.0, 2.5), "too little lead to judge")
        self.assertEqual(c.nyc_verdict(30.0, 0.0), "no chromium detected")
        self.assertEqual(c.nyc_verdict(100.0, 1.0), "more lead than chromate")
        self.assertEqual(c.nyc_verdict(20.0, 50.0), "more chromium than lead")

    def test_english(self):
        self.assertEqual(c.english("Import/importé"), "Import")
        self.assertEqual(c.english("CANADA"), "CANADA")


class TestParseAndGrade(unittest.TestCase):
    def test_parse(self):
        rows, check = c.parse(build([("A1", "Turmeric/Curcuma", "0.12", "1.5"),
                                     ("A2", "Cumin/Cumin", "0", "9.0")]))
        self.assertEqual(check["data_rows"], 6)
        self.assertEqual(check["samples"], 2)
        self.assertEqual(check["pairs"], 2)
        self.assertEqual(check["pb_zero"], 1)
        self.assertEqual(check["bad_numbers"], 0)
        self.assertEqual(check["units"], {"ug/g": 4})
        a1, a2 = rows
        self.assertEqual((a1["product"], a1["matrix"], a1["pb"], a1["cr"]), ("Turmeric", "turmeric", 0.12, 1.5))
        self.assertEqual(a1["function"], "Import")
        self.assertEqual(a1["origin"], "INDIA")
        self.assertEqual(a1["spot"], "Negative/Négatif")
        self.assertFalse(a1["over_ceiling"])
        self.assertTrue(a2["over_ceiling"])  # cumin ceiling 8.59 < 9.0
        self.assertIsNone(a2["molar_ratio_pb_cr"])

    def test_grade_small_set_not_gradable(self):
        rows, check = c.parse(build([("A1", "Turmeric/Curcuma", "0.12", "1.5")]))
        g = c.grade(rows, check)
        self.assertEqual(g["gradable"], 0)

    def test_grade_full(self):
        samples = []
        # 120 clean turmerics: Pb 0.1, Cr 1.0 (ratio ~0.025, under the 2.88 ceiling)
        for i in range(120):
            samples.append(("T%d" % i, "Turmeric/Curcuma", "0.1", "1.0"))
        # 5 turmerics over the ceiling (3.0 > 2.88), one also over 8.59
        for i in range(4):
            samples.append(("H%d" % i, "Turmeric/Curcuma", "0.1", "3.0"))
        samples.append(("H9", "Turmeric/Curcuma", "0.1", "9.0"))
        # one blend in the band with lead >= 18 (ratio exactly 1)
        samples.append(("B1", "Spice Blend/Mélange d'épices", "20.72", "5.1996"))
        # one paprika in the band below the floor (Pb 4.144, Cr 1.04 -> ratio ~1.0)
        samples.append(("P1", "Paprika/Paprika", "4.144", "1.03992"))
        rows, check = c.parse(build(samples))
        self.assertEqual(check["pairs"], 127)
        g = c.grade(rows, check)
        p = g["predictions"]
        # own-ceiling samples: 120 + 5 turmeric + 1 paprika = 126; over: 5 turmeric
        self.assertEqual(p["P1"]["value"], "5 of 126")
        self.assertEqual(p["P1"]["status"], "met")  # 5 <= 6.3
        self.assertEqual(p["P2"]["value"], 1)
        self.assertEqual(p["P2"]["status"], "met")
        self.assertEqual(p["P3"]["value"], 2)
        self.assertEqual(p["P3"]["status"], "not met")
        self.assertEqual(p["P4"]["value"], 1)
        self.assertEqual(p["P4"]["status"], "not met")
        # Pb >= 2: blend 20.72 and paprika 4.144 -> 2 of 127 (1.6% < 8.3%)
        self.assertEqual(p["P5"]["value"], "2 of 127")
        self.assertEqual(p["P5"]["status"], "met")
        self.assertEqual(g["met"], 3)
        self.assertEqual(g["gradable"], 5)
        d = c.describe(rows)
        self.assertEqual(len(d["band_rows"]), 2)
        self.assertEqual(len(d["over_ceiling_rows"]), 5)
        self.assertEqual(d["by_matrix"]["turmeric"]["n"], 125)
        self.assertEqual(d["by_matrix"]["turmeric"]["over_ceiling"], 5)


if __name__ == "__main__":
    unittest.main()
