"""Offline checks of cfia_spice_auth 0.1.0 (no network).

The fixtures copy the column layout of CFIA's 2022-2023 Spices Authenticity CSV (nine
bilingual columns, cp1252-encoded accents) and an older one-language layout with a
title row. Every sample in them is made up, to exercise the parser and the
pre-registered grading rules. Apache-2.0. MV2 of Munim, Inc.
"""
import os
import unittest

import cfia_spice_auth as ca

HEADER = ('"Sample # - No d\'échantillon","Sampled From - Lieu d\'échantillonnage",'
          '"Declared Origin or Dealer Location","Origine ou principal lieu d\'affaires déclarés",'
          '"Product Name","Nom du produit","Sample Assessment - Évaluation de l\'échantillon",'
          '"Notes","Notes"')
ROWS = [
    "2022FCP-0001-4,ON,India,Inde,Turmeric,Curcuma,S,,",
    "2022FCP-0002-4,QC,India,Inde,Turmeric (Organic),Curcuma (biologique),U-I,"
    "Lead chromate detected,Chromate de plomb détecté",
    '2022FCP-0003-4,BC,Pakistan / India,Pakistan / Inde,Chili Powder,Piment en poudre,U-I,'
    'Sudan I detected,Soudan I détecté',
    '2022FCP-0004-4,ON,Egypt,Égypte,Cumin,Cumin,U-I,"Filler: wheat (gluten) detected",'
    '"Charge : blé (gluten) détecté"',
    "2022FCP-0005-4,AB,Egypt,Égypte,Coriander,Coriandre,INV,Investigative for colours,"
    "Enquête pour colorants",
    "2022FCP-0006-4,ON,China,Chine,Ginger,Gingembre,U-I,Peanut shell detected,"
    "Coque d'arachide détectée",
    "2022FCP-0007-4,PEI,Canada,Canada,Black Pepper,Poivre noir,S,,",
    ",,,,,,,,",
]
FIXTURE = ("\r\n".join([HEADER] + ROWS) + "\r\n").encode("cp1252")

OLD = ("Spices misrepresentation 2020-2021,,,,\r\n"
       "Sample Number,Product,Country of Origin,Assessment,Notes\r\n"
       "2020-001,Paprika,Spain,S,\r\n"
       "2020-002,Ground Ginger,India,U-I,Lead chromate\r\n"
       "2020-003,Oregano,Turkey,U-I,\r\n"
       "2020-004,Oregano,Turkey,U-I,\r\n").encode("utf-8")


class TestParse(unittest.TestCase):
    def setUp(self):
        self.rows, self.check = ca.parse_file(FIXTURE, "2022-2023")

    def test_encoding_and_header(self):
        self.assertEqual(self.check["encoding"], "cp1252")
        self.assertEqual(self.check["header_row"], 0)
        self.assertEqual(self.check["columns"]["origin"], "Declared Origin or Dealer Location")
        self.assertEqual(self.check["columns"]["product"], "Product Name")
        self.assertTrue(self.check["columns"]["assessment"].startswith("Sample Assessment"))
        self.assertTrue(self.check["columns"]["sample"].startswith("Sample #"))

    def test_rows(self):
        self.assertEqual(len(self.rows), 7)
        self.assertEqual([r["assessment"] for r in self.rows],
                         ["S", "U", "U", "U", "INV", "U", "S"])
        self.assertEqual(self.check["u_rows"], 4)
        self.assertEqual(self.check["u_rows_with_notes"], 4)
        self.assertEqual(self.check["assessment_codes"], {"S": 2, "U-I": 4, "INV": 1})

    def test_spice_and_origin(self):
        self.assertEqual(self.rows[1]["spice"], "turmeric")
        self.assertEqual(self.rows[2]["spice"], "chili")
        self.assertEqual(self.rows[6]["spice"], "black_pepper")
        self.assertEqual(self.rows[2]["origins"], ["PAKISTAN", "INDIA"])
        self.assertEqual(self.rows[0]["origins"], ["INDIA"])

    def test_classify(self):
        flags = [(r["lead"], r["dye"], r["filler"]) for r in self.rows]
        self.assertEqual(flags, [(False, False, False), (True, False, False),
                                 (False, True, False), (False, False, True),
                                 (False, True, False), (False, False, True),
                                 (False, False, False)])

    def test_regex_edges(self):
        self.assertFalse(ca.classify("Misleading label")["lead"])
        self.assertFalse(ca.classify("Leading brand")["lead"])
        self.assertTrue(ca.classify("Pb chromate positive")["lead"])
        self.assertFalse(ca.classify("Lead chromate (colour)")["dye"])
        self.assertTrue(ca.classify("Undeclared colour: tartrazine")["dye"])
        self.assertTrue(ca.classify("Foreign plant material")["filler"])
        self.assertFalse(ca.classify("Nutmeg")["filler"])
        self.assertEqual(ca.norm_assessment(" u-i "), "U")
        self.assertEqual(ca.norm_assessment("Insatisfaisant"), "U")
        self.assertEqual(ca.norm_assessment("INV"), "INV")
        self.assertEqual(ca.norm_assessment("Satisfactory"), "S")
        self.assertEqual(ca.norm_assessment("?"), "OTHER")
        self.assertEqual(ca.spice_of("Paprika, smoked"), "paprika")
        self.assertEqual(ca.spice_of("Sweet Basil"), "herbs")
        self.assertEqual(ca.spice_of("Anise"), "other")


class TestOldLayout(unittest.TestCase):
    def test_title_row(self):
        rows, check = ca.parse_file(OLD, "2020-2021")
        self.assertEqual(check["encoding"], "utf-8-sig")
        self.assertEqual(check["header_row"], 1)
        self.assertEqual(check["columns"]["origin"], "Country of Origin")
        self.assertIsNone(check["columns"]["notes_fr"])
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[1]["spice"], "ginger")
        self.assertTrue(rows[1]["lead"])
        self.assertEqual(check["u_rows"], 3)
        self.assertEqual(check["u_rows_with_notes"], 1)

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            ca.parse_file(b"Sample Number,Assessment\r\n1,S\r\n", "x")
        with self.assertRaises(ValueError):
            ca.parse_file(b"a,b\r\n1,2\r\n", "x")


class TestGrade(unittest.TestCase):
    def test_fixture_grade(self):
        rows, _ = ca.parse_file(FIXTURE, "2022-2023")
        g = ca.grade(rows)
        p = g["predictions"]
        self.assertTrue(g["notes_gradable"])
        self.assertEqual(p["P1"]["value"], 1)
        self.assertEqual(p["P2"]["value"], "1 of 7")
        self.assertEqual(p["P3"]["value"], "filler 2 vs lead 1 of 4 U")
        self.assertEqual(p["P4"]["value"], "1 of 1")
        self.assertEqual(p["P5"]["value"], "1 of 1")
        self.assertEqual([p[k]["status"] for k in ("P1", "P2", "P3", "P4", "P5")],
                         ["met", "not met", "met", "met", "met"])
        self.assertEqual((g["met"], g["gradable"]), (4, 5))

    def test_notes_missing_not_gradable(self):
        rows, _ = ca.parse_file(OLD, "2020-2021")
        g = ca.grade(rows)
        self.assertFalse(g["notes_gradable"])
        self.assertEqual(g["gradable"], 0)

    def test_no_lead_rows(self):
        rows, _ = ca.parse_file(FIXTURE, "2022-2023")
        rows = [r for r in rows if not r["lead"]]
        p = ca.grade(rows)["predictions"]
        self.assertEqual(p["P1"]["status"], "not met")
        self.assertEqual(p["P2"]["status"], "met")
        self.assertEqual(p["P4"]["status"], "not gradable")
        self.assertEqual(p["P5"]["status"], "not gradable")

    def test_describe(self):
        rows, _ = ca.parse_file(FIXTURE, "2022-2023")
        d = ca.describe(rows)
        self.assertEqual(d["by_year"]["2022-2023"]["n"], 7)
        self.assertEqual(d["by_year"]["2022-2023"]["U"], 4)
        self.assertEqual(d["by_origin"]["(multiple)"]["n"], 1)
        self.assertEqual(d["by_origin"]["INDIA"]["lead"], 1)
        self.assertEqual(d["georgia_rows"], 0)
        self.assertEqual(len(d["lead_rows"]), 1)
        self.assertEqual(len(d["flagged_rows"]), 5)
        md = ca.summary_md({"grade": ca.grade(rows), "descriptive": d},
                           {"2022-2023": {"rows": 7, "encoding": "cp1252", "u_rows": 4,
                                          "u_rows_with_notes": 4, "sha256": "ab" * 32}})
        self.assertIn("| P1 |", md)
        self.assertIn("Lead chromate detected", md)


DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@unittest.skipUnless(os.path.exists(os.path.join(DATA, "cfia_spices_2022-2023.csv")),
                     "frozen CFIA files not committed yet")
class TestFrozenFiles(unittest.TestCase):
    def test_all_files_parse(self):
        for year, _ in ca.FILES:
            with open(os.path.join(DATA, "cfia_spices_%s.csv" % year), "rb") as f:
                rows, check = ca.parse_file(f.read(), year)
            self.assertGreater(len(rows), 50, year)


if __name__ == "__main__":
    unittest.main()
