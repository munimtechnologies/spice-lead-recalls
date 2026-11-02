#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for food_colours.py (food-colours 0.1.0 grader). No network, no real file.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import hashlib
import unittest

import food_colours as fc

C18_HEADER = ["Sample No. – No. d’échantillon", "Region - Région",
              "Commodity", "Denrée", "Function", "Fonction", "Origin", "Origine",
              "Product", "Produit", "Date Sampled – Date d’échantillonage",
              "Type of Test", "Type d’analyse", "Component", "Composant", "AMOUNT",
              "Report Unit - Unité de rapport", "Plan Code"]
C09_HEADER = ["﻿Sample No. – No. d’échantillon", "Region - Région",
              "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
              "Date Sampled – Date d’échantillonage", "Type of test",
              "Type d’analyse", "Component", "Composant", "Result - Résultat",
              "Unit - Unité"]
# Sample counts per product label from the published census (data/food_colours_c18_census.json).
C18_PRODUCTS = {"Baked Goods": 30, "Bakery Product - Cookie": 25, "Beet - Pickled": 9,
                "Candy - Hard": 30, "Candy - Soft": 30, "Cucumber - Pickled": 11,
                "Cucumber - Pickled Sweet": 2, "Essence/Flavour": 50, "Fruit Snacks": 25,
                "Gherkin - Pickled": 11, "Oil - Blend": 3, "Oil - Olive": 39, "Oil - Other": 3,
                "Oil - Palm": 23, "Oil - Soybean": 6, "Onion - Pickled": 2,
                "Pepper - Pickled": 1, "Pepper - Pickled Hot": 3,
                "Pickled Vegetable - Misc": 11, "Preserve - Jam/Jelly": 27,
                "Preserve - Raspberry": 1, "Preserve - Strawberry": 2, "Pudding": 30,
                "Salad Dressing": 25}


def rows_for(sid, product, colours, function="Import", date="1-Apr-18", origin="X",
             region="ONTARIO"):
    out = []
    for c, vals in colours.items():
        if not isinstance(vals, (list, tuple)):
            vals = [vals]
        for v in vals:
            out.append({"sample": sid, "product": product, "function": function,
                        "origin": origin, "region": region, "date": date, "test": "T",
                        "component": c, "value": v, "unit": fc.UNIT})
    return out


def toy_c18():
    rows = []
    rows += rows_for("A", "Candy - Hard", {"Allura Red": 539.0, "Tartrazine": 10.0,
                                           "Orange II": [0.0, 0.0]})
    rows += rows_for("B", "Oil - Palm", {"Sunset Yellow FCF": 5.0, "Tartrazine": 0.0})
    rows += rows_for("C", "Salad Dressing", {"Allura Red": 0.0}, function="Domestic")
    rows += rows_for("D", "Essence/Flavour", {"Orange II": [0.221, 0.0], "Allura Red": 0.0},
                     function="Unknown")
    rows += rows_for("E", "Pudding", {"Orange II": [0.02, 0.02], "Rhodamine B": [10.8, 0.0]})
    return rows, fc.samples_of(rows)


class TestReading(unittest.TestCase):
    def test_columns_c18(self):
        cols = fc.find_columns(C18_HEADER)
        self.assertEqual(cols, {"sample": 0, "region": 1, "function": 4, "origin": 6,
                                "product": 8, "date": 10, "test": 11, "component": 13,
                                "value": 15, "unit": 16})

    def test_columns_c09(self):
        cols = fc.find_columns(C09_HEADER)
        self.assertEqual(cols, {"sample": 0, "region": 1, "function": 2, "origin": 4,
                                "product": 6, "date": 8, "test": 9, "component": 11,
                                "value": 13, "unit": 14})

    def test_to_value(self):
        self.assertEqual(fc.to_value("0"), 0.0)
        self.assertEqual(fc.to_value(" 1.5 "), 1.5)
        for bad in ("<0.1", "-1", "", "nan", "ND"):
            self.assertIsNone(fc.to_value(bad), bad)

    def test_parse_c09_shape(self):
        lines = [",".join('"%s"' % h for h in C09_HEADER)]
        body = [("2009COL0001", "FOOD COLOURS (FAT)", "Fat-Soluble Dyes", "0", "µg/g"),
                ("2009COL0001", "FOOD COLOURS (WATER)", "Allura, red", "5.0", "µg/g"),
                ("2009COL0002", "FOOD COLOURS (FAT)", "Fat-Soluble Dyes", "0", "μg/g"),
                ("2009COL0002", "FOOD COLOURS (WATER)", "Amaranth", "x", "µg/g")]
        for sid, test, comp, val, unit in body:
            lines.append(",".join([sid, "QUEBEC", "Domestic", "Domestique", "CANADA", "CANADA",
                                   "Beverage", "Boisson", "9/21/2009", test, "t", '"%s"' % comp,
                                   "c", val, unit]))
        lines.append(",,,,,,,,,,,,,,")
        rows, problems = fc.parse("\n".join(lines) + "\n")
        self.assertEqual(len(rows), 4)
        self.assertEqual(problems, {"missing_roles": [], "bad_values": 1, "bad_units": 0,
                                    "short_rows": 0})
        samples = fc.samples_of(rows)
        self.assertEqual(sorted(samples), ["2009COL0001", "2009COL0002"])
        self.assertEqual(fc.detected(samples["2009COL0001"]), {"Allura, red": 5.0})
        self.assertEqual(fc.detected(samples["2009COL0002"]), {})
        self.assertEqual(samples["2009COL0001"]["product"], "Beverage")
        self.assertEqual(samples["2009COL0001"]["tests"],
                         {"FOOD COLOURS (FAT)": 1, "FOOD COLOURS (WATER)": 1})


class TestMapsAndTables(unittest.TestCase):
    def test_product_map_gives_table1_sizes(self):
        self.assertEqual(set(fc.PRODUCT_TYPE), set(C18_PRODUCTS))
        per = {t: 0 for t in fc.TYPES}
        for label, n in C18_PRODUCTS.items():
            per[fc.PRODUCT_TYPE[label]] += n
        self.assertEqual(per, {"essence": 50, "oil": 99, "veg": 50, "sweets": 200})
        self.assertEqual({t: v[0] for t, v in fc.TABLE2.items()}, per)

    def test_printed_sums(self):
        self.assertEqual(sum(v[1] for v in fc.TABLE2.values()), 181)
        self.assertEqual(sum(v[2] for v in fc.TABLE2.values()), 336)
        self.assertEqual(sum(v[0] for v in fc.TABLE3.values()), 337)
        cols = [sum(v[i] for v in fc.TABLE1.values()) for i in range(3)]
        self.assertEqual(cols, [56, 184, 159])
        self.assertEqual(sum(cols), 399)

    def test_function_split(self):
        _, samples = toy_c18()
        self.assertEqual(fc.function_split(samples),
                         {"essence": [0, 0, 1], "oil": [1, 1, 0], "veg": [0, 0, 0],
                          "sweets": [0, 2, 0]})


class TestGrading2018(unittest.TestCase):
    def setUp(self):
        self.rows, self.samples = toy_c18()

    def test_by_type_and_v1(self):
        got, oil = fc.by_type(self.samples)
        self.assertEqual(got, {"essence": (1, 1, 1), "oil": (2, 1, 1), "veg": (0, 0, 0),
                               "sweets": (2, 2, 4)})
        self.assertEqual(oil, [1])
        v1 = fc.grade_v1(self.samples)
        self.assertFalse(v1["met"])
        self.assertEqual((v1["observed"]["with_colour_total"],
                          v1["observed"]["detections_total"]), (4, 6))

    def test_v2_orange_and_rhodamine_paths(self):
        v2 = fc.grade_v2(self.samples)
        self.assertFalse(v2["met"])
        col = v2["observed"]["colours"]
        orange = col["Orange II"]
        self.assertEqual((orange["n"], orange["n_ok"], orange["max_ok"], orange["avg_ok"]),
                         (2, True, True, True))
        self.assertAlmostEqual(orange["mean"], 0.1205, places=9)
        rb = col["Rhodamine B"]
        self.assertEqual((rb["n"], rb["n_ok"], rb["max_ok"], rb["avg_ok"]),
                         (1, True, True, True))
        allura = col["Allura Red"]
        self.assertEqual((allura["n"], allura["n_ok"], allura["max_ok"], allura["avg_ok"]),
                         (1, False, True, False))
        self.assertEqual(col["Indigo Carmine"]["n"], 0)
        self.assertEqual(v2["observed"]["other_colours_detected"], {})

    def test_v3_v4_v5(self):
        v3, v4, v5 = fc.grade_v3_v4_v5(self.samples)
        self.assertFalse(v3["met"])
        self.assertEqual(v3["observed"]["detections"], 6)
        self.assertEqual(v3["observed"]["orange_ii_levels"], [0.02, 0.221])
        self.assertEqual(v3["observed"]["orange_ii_low"], ["E"])
        self.assertEqual(v3["observed"]["orange_ii_low_types"], ["sweets"])
        self.assertEqual(v3["observed"]["type_cells_off"],
                         {"essence": -22, "oil": -12, "veg": -40, "sweets": -256})
        self.assertEqual((v4["met"], v4["observed"]["without_colour"]), (False, 1))
        self.assertEqual(v5["observed"]["colours_per_positive"], {"1": 2, "2": 2})
        self.assertEqual((v5["observed"]["one_to_four"], v5["observed"]["five_or_more"]), (4, 0))
        self.assertFalse(v5["met"])

    def test_v6_v7(self):
        v6, v7 = fc.grade_v6_v7(self.samples)
        self.assertTrue(v6["met"])
        top = v6["observed"]["top"]
        self.assertEqual(len(top), 5)
        self.assertEqual((top[0]["sample"], top[0]["colour"], top[0]["product"]),
                         ("A", "Allura Red", "Candy - Hard"))
        self.assertEqual((top[1]["colour"], top[1]["ppm"]), ("Rhodamine B", 10.8))
        self.assertTrue(v7["met"])
        self.assertEqual([x["sample"] for x in v7["observed"]["rhodamine_b"]], ["E"])

    def test_double_rows_and_coding(self):
        d = fc.double_rows(self.samples)
        self.assertEqual(d["Orange II"], {"both_rows": 1, "one_row": 1})
        self.assertEqual(d["Rhodamine B"], {"both_rows": 0, "one_row": 1})
        self.assertEqual(d["Chrysoidine G"], {"both_rows": 0, "one_row": 0})
        c = fc.coding(self.rows)
        self.assertEqual((c["rows_zero"], c["rows_above_zero"]), (7, 7))
        self.assertEqual(c["smallest_above_zero"]["Orange II"], 0.02)


class TestGrading2009(unittest.TestCase):
    def build(self, fat_positive=False):
        rows = []
        for i in range(1, 101):
            sid = "2009COL%04d" % i
            fat = 1.0 if (fat_positive and i == 100) else 0.0
            rows += rows_for(sid, "Beverage", {fc.C09_FAT: fat})
            if i <= 38:
                rows += rows_for(sid, "Beverage", {"Allura, red": 1.0})
            elif i == 39:
                rows += rows_for(sid, "Beverage", {"Amaranth": 1.0, "Erythrosine": 1.0})
            elif i == 40:
                rows += rows_for(sid, "Beverage", {"Brilliant blue": 1.0, "Indigotine": 1.0})
            elif i == 41:
                rows += rows_for(sid, "Beverage", {"Erythrosine": 2.0})
        return fc.samples_of(rows)

    def test_v8_met(self):
        v8 = fc.grade_v8(self.build())
        obs = v8["observed"]
        self.assertEqual((obs["with_colour"], obs["results"], obs["five_colours"]), (41, 43, 40))
        self.assertAlmostEqual(obs["five_share"], 40 / 43, places=12)
        self.assertTrue(v8["met"])

    def test_v8_fat_positive_fails(self):
        v8 = fc.grade_v8(self.build(fat_positive=True))
        self.assertFalse(v8["met"])
        self.assertEqual(v8["observed"]["fat_soluble_above_zero"], ["2009COL0100"])
        self.assertFalse(v8["observed"]["checks"]["forty_one_with_colour"])

    def test_v9_ungraded(self):
        v9 = fc.grade_v9()
        self.assertEqual((v9["graded"], v9["met"]), (False, None))


class TestDescriptive(unittest.TestCase):
    def test_twins_mixed_ids_dates(self):
        rows = []
        rows += rows_for("C2018FCOL00001", "Candy - Soft", {"Allura Red": 3.0, "Tartrazine": 1.0},
                         date="1-Apr-18")
        rows += rows_for("C2018FCOL00003", "Candy - Soft", {"Allura Red": 3.0, "Tartrazine": 1.0},
                         date="2-Apr-18")
        rows += rows_for("C2018FCOL00004D", "Pudding", {"Allura Red": 0.0}, date="5-Apr-18")
        rows += rows_for("C2018FCOL00004D", "Pudding", {"Tartrazine": 0.0}, date="6-Apr-18")
        samples = fc.samples_of(rows)
        self.assertEqual(fc.twins(samples), [["C2018FCOL00001", "C2018FCOL00003"]])
        self.assertEqual(fc.mixed(samples),
                         [{"sample": "C2018FCOL00004D", "fields": ["date"],
                           "values": {"date": ["5-Apr-18", "6-Apr-18"]}}])
        ids = fc.ids_and_dates(samples)
        self.assertEqual((ids["id_range"], ids["gaps"], ids["bad_ids"]), ([1, 4], [2], []))
        self.assertEqual(ids["suffixed"], [{"sample": "C2018FCOL00004D",
                                            "base": "C2018FCOL00004", "base_present": False}])
        self.assertEqual((ids["first"], ids["last"], ids["distinct"]),
                         ("2018-04-01", "2018-04-05", 3))
        self.assertEqual(ids["text_rank_fits"], 2)
        self.assertEqual(fc.parse_date("9/21/2009").isoformat(), "2009-09-21")

    def test_gate(self):
        raw = b"abc"
        target = {"size": 3, "md5": hashlib.md5(raw).hexdigest()}
        rows, samples = toy_c18()
        problems = {"missing_roles": [], "bad_values": 0, "bad_units": 0, "short_rows": 0}
        checks, facts = fc.gate(raw, target, rows, problems, samples, 5)
        self.assertTrue(all(checks.values()), checks)
        self.assertEqual((facts["rows"], facts["samples"]), (14, 5))
        checks, _ = fc.gate(raw, target, rows, problems, samples, 5, want_rows_per_sample=46)
        self.assertFalse(checks["rows_per_sample"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
