#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests of fumonisin_grade.py on synthetic data (no CFIA file, no network).
    python -m unittest -v test_fumonisin_grade
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import io
import unittest

import fumonisin_grade as fg

HEADER = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin", "Origine", "Product",
          "Produit", "Date Sampled – Date d’échantillonage", "Type of Test", "Type d’analyse",
          "Component", "Composant", "Result - Résultat", "Unit - Unité",
          "Plan Code - Code du régime"]


def row(sid, product, date, comp, value, unit="ng/g"):
    return [sid, "Domestic", "Domestique", "CANADA", "CANADA", product, product, date,
            "FUMONISINS", "FUMONISINES", comp, comp, value, unit, "2010_TS002"]


def text_of(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    w.writerows(rows)
    return buf.getvalue()


def s(sid, product, total, group, year="2012-13"):
    return {"id": sid, "product": product, "total": total, "group": group, "year": year,
            "values": {"B1": total, "B2": 0.0}}


class Parsing(unittest.TestCase):
    def test_parse_totals_groups_and_years(self):
        text = text_of([
            row("2010FMN0001", "Cornmeal", "2010-11-02", "Fumonisin B1", "10.5"),
            row("2010FMN0001", "Cornmeal", "2010-11-02", "Fumonisin B2", "9.6"),
            row("2010FMN0002", "Chips - Corn", "2010-12-01", "Fumonisin B1", "0"),
            row("2010FMN0002", "Chips - Corn", "2010-12-01", "Fumonisin B2", "0"),
            row("2010FMN0003", "Cereal - Corn", "2011-01-05", "Fumonisin B1", "1,234"),
            row("2010FMN0003", "Cereal - Corn", "2011-01-05", "Fumonisin B2", "0,5"),
        ])
        samples, problems = fg.parse(text, "fum10")
        self.assertFalse(any(problems.values()), problems)
        by = {x["id"]: x for x in samples}
        self.assertEqual(len(by), 3)
        self.assertAlmostEqual(by["2010FMN0001"]["total"], 20.1, places=6)
        self.assertEqual(by["2010FMN0002"]["total"], 0)
        self.assertAlmostEqual(by["2010FMN0003"]["total"], 1234.5, places=6)
        self.assertEqual([by[k]["group"] for k in sorted(by)], ["cornmeal_grits", "block", "cereal"])
        self.assertEqual({x["year"] for x in samples}, {"2010-11"})

    def test_parse_problems(self):
        text = text_of([
            row("A1", "Popcorn", "2010-11-02", "Fumonisin B1", "5", unit="ug/g"),
            row("A1", "Popcorn", "2010-11-02", "Fumonisin B3", "1"),
            row("A2", "Teacake", "2010-11-02", "Fumonisin B1", "x"),
        ])
        samples, problems = fg.parse(text, "fum10")
        self.assertEqual(problems["bad_unit"], ["A1: B1"])
        self.assertEqual(problems["unknown_component"], ["A1: Fumonisin B3"])
        self.assertEqual(problems["non_numeric"], ["A2: B1"])
        self.assertEqual(sorted(problems["missing_component"]), ["A1: B2", "A2: B1", "A2: B2"])
        self.assertEqual(problems["unmapped_product"], ["A2: Teacake"])

    def test_number_and_bands(self):
        self.assertEqual(fg.number("2,608"), 2608.0)
        self.assertEqual(fg.number("0,54"), 0.54)
        self.assertEqual(fg.number("12.5"), 12.5)
        with self.assertRaises(ValueError):
            fg.number("abc")
        self.assertTrue(fg.within(20.75, 20.75, 20.85))
        self.assertFalse(fg.within(20.85, 20.75, 20.85))
        self.assertTrue(fg.matches(249.2, 249, 0))
        self.assertTrue(fg.matches(28.84, 28.8, 1))
        self.assertFalse(fg.matches(28.86, 28.8, 1))
        self.assertEqual(fg.kib_band_up(86), (87040, 88064))


class Maps(unittest.TestCase):
    def test_b_group(self):
        self.assertEqual([fg.b_group(p) for p in ("Tea - Black", "Beverage - Tea", "Tofu",
                                                   "Meat Alternative", "Cornmeal",
                                                   "Infant Food - Cereal")],
                         ["tea", "tea", "soy", "soy", "grain", "grain"])

    def test_label_grain(self):
        want = {"Popcorn": "corn", "TACO": "corn", "Flour - rye": "rye", "BRAN - OAT": "oat",
                "Oatmeal": "oat", "Grain - Other": None, "Cereal - Children": None,
                "Teff Products": "teff", "Bakery Product - Tortilla/Wrap/Pita": None,
                "Grain - Buckwheat": "buckwheat", "Flour - Rice": "rice",
                "Crispbread/Crouton": None, "Corn Starch": "corn"}
        for label, grain in want.items():
            self.assertEqual(fg.label_grain(label), grain, label)

    def test_f11_group(self):
        self.assertEqual([fg.f11_group(p) for p in ("Corn - Sweet - Organic", "Misc - Soy",
                                                     "Cereal - Other", "Tofu")],
                         ["corn", "soy", "other", "unmapped"])


class Grades(unittest.TestCase):
    def test_f10(self):
        rows = [s("c1", "Cereal - Corn", 900, "cereal"), s("c2", "Cereal - Corn", 1000, "cereal"),
                s("c3", "Cereal - Corn", 1100, "cereal"), s("c4", "Cereal - Corn", 1200, "cereal"),
                s("m1", "Cornmeal", 6650.2, "cornmeal_grits"),
                s("m2", "Cornmeal", 850, "cornmeal_grits"),
                s("m3", "Cornmeal", 820, "cornmeal_grits"),
                s("m4", "Cornmeal", 19.6, "cornmeal_grits"),
                s("b1", "Corn Products", 801, "block"), s("b2", "Chips - Corn", 20.2, "block"),
                s("p1", "Popcorn", 0, "popcorn")]
        g = fg.grade_f10(rows)
        self.assertEqual(g["V1"]["stats"]["positives"], 10)
        self.assertFalse(g["V1"]["held"])
        self.assertTrue(g["V2"]["held"], g["V2"]["checks"])
        self.assertTrue(g["V2"]["chips_label_at_min"])
        self.assertTrue(g["V3"]["held"], g["V3"]["checks"])
        self.assertTrue(g["V4"]["held"], g["V4"]["checks"])
        self.assertEqual(g["V4"]["by_group"], {"cereal": 4, "cornmeal_grits": 3, "block": 1})
        self.assertFalse(g["2010-V5"]["held"])

    def test_f11(self):
        rows = [s("a", "Corn Products", 20.8, "corn"), s("b", "Cornmeal", 4442.5, "corn"),
                s("c", "Flour - Soy", 22.4, "soy"), s("d", "Bean - Soy", 0, "soy"),
                s("e", "Cereal - Other", 50, "other")]
        g = fg.grade_f11(rows)
        c = g["A-V1"]["checks"]
        self.assertEqual((c["positives_162"], c["one_soy"], c["soy_is_flour"],
                          c["soy_rounds_to_22_4"], c["corn_or_other_161"]),
                         (False, True, True, True, False))
        self.assertTrue(g["A-V2"]["held"])
        self.assertTrue(g["A-V3"]["held"])
        self.assertAlmostEqual(g["A-V4"]["corn"]["mean"], 2231.65, places=6)
        self.assertFalse(g["A-V4"]["held"])

    def test_b(self):
        rows = [s("g1", "Cornmeal", 7790.0, "grain", "2012-13"),
                s("g2", "Chips - Corn", 20.0, "grain", "2017-18"),
                s("s1", "Tofu", 27.0, "soy", "2012-13"),
                s("s2", "Flour - Soy", 45.0, "soy", "2013-14"),
                s("s3", "Bean - Soy", 0, "soy", "2013-14"),
                s("t1", "Tea - Black", 43.0, "tea", "2016-17"),
                s("t2", "Tea - Green", 0, "tea", "2016-17")]
        g = fg.grade_b(rows)
        c = g["B-V1"]["checks"]
        self.assertEqual((c["positives_1076"], c["grain_1073"], c["soy_2"], c["tea_1"]),
                         (False, False, True, True))
        self.assertTrue(g["B-V2"]["held"], g["B-V2"]["checks"])
        self.assertTrue(g["B-V3"]["held"], g["B-V3"]["checks"])
        self.assertTrue(g["B-V4"]["held"], g["B-V4"]["checks"])
        c = g["B-V11"]["checks"]
        self.assertEqual((c["grain_365"], c["soy_36"], c["total_364"]), (False, True, False))
        self.assertEqual(g["B-V11"]["means"]["total"], 1585.0)
        self.assertIsNone(g["B-V6"]["held"])
        self.assertFalse(g["B-V7"]["held"])

    def test_dup_suffix_and_lookups(self):
        rows = [s("C2013FUMN00303", "Cornmeal", 10, "grain"),
                s("C2013FUMN00303D", "Cornmeal", 12, "grain"),
                s("C2014FUMN00001D", "Tofu", 0, "soy"),
                s("C2014FUMN00002", "Grain - Rice", 249.2, "grain", "2014-15")]
        d = fg.dup_suffix(rows)
        self.assertEqual([(x["id"], x["stem_in_file"]) for x in d],
                         [("C2013FUMN00303D", True), ("C2014FUMN00001D", False)])
        self.assertEqual(d[0]["stem_total"], 10)
        hits = fg.lookups(rows, {"rice 249": (249, 0)})
        self.assertEqual([h["id"] for h in hits["rice 249"]], ["C2014FUMN00002"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
