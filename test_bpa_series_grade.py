#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for bpa_series_grade.py (no network, no CFIA data). Made with AI agents working
in MV2's (Munim, Inc.) name."""
import datetime
import unittest

import bpa_series_grade as g

# Headers as the names-only census printed them (escapes for the accented letters).
H09 = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin",
       "Origine", "Product", "Produit", "Date Sampled – Date d’échantillonage",
       "Type of Test", "Type d’analyse", "Component", "Composant",
       "Result - Résultat", "Unit - Unité", "Plan Code - Code du régime"]
H16 = ["Sample No. – No. d’échantillon", "Region - Région", "Function",
       "Fonction", "Origin", "Origine", "Product", "Produit",
       "Date Sampled – Date d’échantillonage", "Type of Test",
       "Type d’analyse", "Component", "Composant", "Result - Résultat",
       "Report Unit - Unité de rapport", "Plan Code - Code du régime", "", ""]

# Product label counts from data/bpa-20NN_census.json (per sample).
CENSUS_PRODUCTS = {
    "bpa-2009": {"Infant Food": 100, "Infant Formula": 100},
    "bpa-2010": {"Apricot": 1, "Cereal - Other": 2, "Infant Formula - Dairy": 126,
                 "Infant Formula - Soy": 3, "Juice - Apple": 13, "Juice - Grape": 1,
                 "Meat & Vegetable": 1, "Mixed Fruit": 25, "Nectar - Pear": 1, "Peach": 25,
                 "Pear": 24, "Pineapple": 10, "Strawberry": 2},
    "bpa-2011": {"Asparagus": 1, "Bamboo Shoot": 1, "Banana": 2, "Bean": 1, "Bean - Black": 2,
                 "Bean - Fava": 1, "Bean - Green/Yellow": 12, "Bean - Kidney": 7,
                 "Bean - Other": 9, "Bean - wax": 2, "Beet": 1, "Beverage - Fruit": 2,
                 "Beverage - Other": 1, "Beverage - Tea": 1, "Carrot": 14, "Chickpea": 5,
                 "Corn": 20, "Juice - Apple": 13, "Juice - Tomato": 19,
                 "Juice/Nectar - Other": 1, "Kale": 1, "Longan": 1, "Lychee": 5, "Mango": 2,
                 "Mixed Fruit": 21, "Mixed Vegetables": 17, "Mushroom": 2, "Orange": 13,
                 "Papaya": 1, "Pasta - Canned": 96, "Pea": 23, "Pea - Organic": 2,
                 "Pea - Sugar": 1, "Peach": 25, "Pear": 18, "Pineapple": 10, "Plum": 1,
                 "Potato": 13, "Preserve - Apricot": 1, "Preserve - Blueberry": 1, "Soup": 5,
                 "Sweet Potato": 1, "Tomato": 13, "Tomato - Organic": 2,
                 "juice - pineapple": 13},
    "bpa-2012": {"Apricot": 3, "Artichoke Heart": 7, "Asparagus": 1, "Bamboo Shoot": 10,
                 "Bean": 3, "Bean - Organic": 6, "Beet": 1, "Beverage - Fruit": 36,
                 "Cabbage": 1, "Callaloo": 1, "Chickpea products": 1, "Coconut Milk": 46,
                 "Corn": 26, "Cucumber": 1, "Curry": 21, "Grapefruit": 2, "Heart of Palm": 5,
                 "JackFruit": 4, "Juice - Apple": 2, "Juice - Blend": 3, "Juice - Other": 3,
                 "Juice - Vegetable": 1, "Juice - other": 3, "Lentils products": 1,
                 "Longan": 1, "Lychee": 3, "Mango": 9, "Mixed Fruit": 26,
                 "Mixed Vegetables": 51, "Mushroom": 7, "Nectar - Mango": 2,
                 "Nectar - Other": 2, "Okra": 1, "Orange": 3, "Orange - Organic": 1,
                 "Papaya": 1, "Pasta - Canned": 119, "Pea": 2, "Pea - Organic": 1,
                 "Pea products": 1, "Peach": 4, "Pear": 4, "Pepper - Pickled Hot": 8,
                 "Pineapple": 10, "Pineapple - Organic": 1, "Salsa": 3, "Sauces": 1,
                 "Soup": 98, "Strawberry": 1, "Tomatillo": 2, "Tomato": 5, "Water Chestnut": 1,
                 "juice - pineapple": 20},
    "bpa-2013": {"Artichoke Heart": 1, "Asparagus": 1, "Bamboo Shoot": 3, "Bean Products": 1,
                 "Beverage - Fruit": 26, "Beverage - Other": 12, "Beverage - Sport": 3,
                 "Cherry": 1, "Chickpea Products": 1, "Coconut Milk": 13, "Corn": 43,
                 "Energy Drink": 24, "Gooseberry": 1, "Heart of Palm": 1,
                 "Infant Formula - Dairy": 46, "Infant Formula - Soy": 9, "JackFruit": 2,
                 "Juice - Apple": 5, "Juice - Blend": 2, "Juice - Mixed": 5, "Juice - Other": 4,
                 "Lychee": 3, "Mango": 4, "Mango - Organic": 1, "Misc Fruit": 4,
                 "Misc Vegetables": 6, "Mixed Fruit": 18, "Mixed Vegetables": 10,
                 "Mushroom": 3, "Orange": 1, "Papaya": 1, "Pasta - Canned": 45, "Peach": 1,
                 "Pie Filling - Blueberry": 6, "Pie Filling - Cherry": 5,
                 "Pie Filling - Other": 3, "Pie Filling - Pumpkin": 5, "Pie Filling - apple": 1,
                 "Pineapple": 1, "Sauces": 5, "Soft Drink": 15, "Soup": 48,
                 "juice - pineapple": 1},
    "bpa-2016": {"Apricot": 2, "Artichoke": 1, "Artichoke Heart": 1, "Asparagus": 6,
                 "Bamboo Shoot": 4, "Bean": 1, "Bean - Green/Yellow": 10, "Bean - wax": 2,
                 "Beet": 5, "Beverage - Fruit": 21, "Beverage - Other": 19,
                 "Beverage - Sport": 19, "Carrot": 4, "Coconut Milk": 14, "Corn": 7,
                 "Energy Drink": 21, "Grapefruit": 1, "Infant Formula - Dairy": 60,
                 "Infant Formula - Soy": 14, "JackFruit": 1, "Juice - Apple": 9,
                 "Juice - Blend": 3, "Juice - Orange": 1, "Juice - Other": 11,
                 "Juice - Tomato": 4, "Juice - Vegetable": 2, "Lychee": 1, "Mango": 1,
                 "Mixed Fruit": 25, "Mixed Vegetables": 9, "Mushroom": 7, "Nectar - Guava": 1,
                 "Nectar - Mango": 2, "Nectar - Other": 1, "Orange": 2, "Pasta - Canned": 49,
                 "Pea": 10, "Peach": 5, "Pear": 7, "Pie Filling - Blueberry": 5,
                 "Pie Filling - Cherry": 5, "Pie Filling - Other": 4, "Pie Filling - Pumpkin": 5,
                 "Pie Filling - apple": 1, "Pineapple": 4, "Pineapple - Organic": 1,
                 "Sauces": 14, "Soft Drink": 20, "Soup": 48, "Spinach": 4, "Tomato Sauce": 1,
                 "Yam": 1, "juice - pineapple": 15},
    "bpa-2017": {"Beef": 1, "Chicken": 5, "Crab": 1, "Fish": 4, "Fish/Seafood - Canned": 165,
                 "Ham": 5, "Herring": 1, "Mackerel": 2, "Meat - Canned": 219, "Mussel": 1,
                 "Oyster": 1, "Pork": 1, "Salmon": 12, "Shrimp": 1, "Tuna": 49},
}
TYPE_COUNTS = {
    "bpa-2009": {"food": 100, "formula": 100},
    "bpa-2010": {"formula": 129, "juice": 15, "fruit": 87, "other": 3},
    "bpa-2011": {"pasta": 96, "soup": 5, "fruit": 101, "juice": 50, "veg": 151},
    "bpa-2012": {"bev": 72, "coconut": 46, "fruit": 73, "curry": 21, "pasta": 119, "soup": 98,
                 "veg": 147},
    "bpa-2013": {"bev": 97, "coconut": 13, "fruit": 38, "formula": 55, "pasta": 45, "pie": 20,
                 "curry": 5, "soup": 48, "veg": 70},
    "bpa-2016": {"bev": 149, "coconut": 14, "fruit": 50, "formula": 74, "pasta": 49, "pie": 20,
                 "sauce": 15, "soup": 48, "veg": 72},
    "bpa-2017": {"meat": 231, "fish": 237},
}
ALT_NAME = {"badge": "Bisphenol A Diglycidyl Ether", "bpf": "Bisphenol F", "bps": "Bisphenol S"}


def toy_csv(header, rows):
    out = [",".join('"%s"' % h for h in header)]
    for r in rows:
        out.append(",".join('"%s"' % x for x in r))
    return "\n".join(out) + "\n"


def row09(sid, product, value, date):
    return [sid, "Import", "Import", "United States", "United States", product, product, date,
            "BPA", "BPA", "Bisphenol A", "Bisphenol A", value, "ng/g", "2009_SB451"]


def row16(sid, product, comp, value, unit=g.UG):
    return [sid, "ONTARIO", "Import", "Import", "THAILAND", "THAILANDE", product, product,
            "2016-05-02", "BPA", "BPA", comp, comp, value, unit, "2016_SB451", "", ""]


def mk(name, sid, product, bpa=0.0, function="Import", date="", order=0, **alt):
    """A parsed sample (ppb values) for analysis tests."""
    comps = g.TARGETS[name]["components"]
    vals = {c: [0.0] for c in comps}
    vals["Bisphenol A"] = [bpa]
    for k, v in alt.items():
        vals[ALT_NAME[k]] = [v]
    s = {"sample": sid, "order": order, "product": product, "origin": "X",
         "function": function, "region": "", "date": date, "n_rows": len(comps),
         "values": vals, "bad": False}
    return g.finish(s, name)


class TestColumns(unittest.TestCase):
    def test_2009_header(self):
        self.assertEqual(g.find_columns(H09),
                         {"sample": 0, "component": 10, "value": 12, "unit": 13, "product": 5,
                          "origin": 3, "function": 1, "region": None, "date": 7, "plan": 14})

    def test_2016_header(self):
        self.assertEqual(g.find_columns(H16),
                         {"sample": 0, "component": 11, "value": 13, "unit": 14, "product": 6,
                          "origin": 4, "function": 2, "region": 1, "date": 8, "plan": 15})


class TestLabelMaps(unittest.TestCase):
    def test_maps_cover_census_labels_and_give_census_counts(self):
        for name in g.NAMES:
            products = CENSUS_PRODUCTS[name]
            self.assertEqual(set(products), set(g.TYPE_OF[name]), name)
            got = {}
            for label, n in products.items():
                t = g.TYPE_OF[name][label]
                got[t] = got.get(t, 0) + n
            self.assertEqual(got, TYPE_COUNTS[name], name)
            self.assertEqual(sum(got.values()), g.TARGETS[name]["samples"], name)

    def test_printed_n_said_in_advance(self):
        c13 = TYPE_COUNTS["bpa-2013"]
        self.assertEqual({t: r[0] for t, r in g.TABLE5_2013.items()}, c13)
        c16 = TYPE_COUNTS["bpa-2016"]
        for t in g.V6_GRADABLE:
            self.assertEqual(g.TABLE2_2016[t][0], c16[t], t)
        extra = sum(c16[t] - g.TABLE2_2016[t][0] for t in g.TABLE2_2016)
        self.assertEqual(extra, 27)                    # Table 1's other packaging
        c12 = TYPE_COUNTS["bpa-2012"]
        for t in ("bev", "coconut", "fruit", "soup"):
            self.assertEqual(g.TABLE5_2012[t][0], c12[t], t)
        for t in ("curry", "veg", "pasta"):
            self.assertNotEqual(g.TABLE5_2012[t][0], c12[t], t)
        salsa = CENSUS_PRODUCTS["bpa-2012"]["Salsa"]
        self.assertEqual(c12["curry"] + salsa, g.TABLE5_2012["curry"][0])
        self.assertEqual(c12["veg"] - salsa, g.TABLE5_2012["veg"][0])
        c17 = TYPE_COUNTS["bpa-2017"]
        self.assertEqual((g.TABLE2_2017["meat"][0], g.TABLE2_2017["fish"][0]),
                         (c17["meat"], c17["fish"]))


class TestPrintedArithmetic(unittest.TestCase):
    def test_2013_and_2012_rows(self):
        self.assertEqual(sum(r[0] for r in g.TABLE5_2013.values()), 391)
        self.assertEqual(sum(r[1] for r in g.TABLE5_2013.values()), g.V5["k"])
        self.assertEqual(sum(r[1] for r in g.TABLE5_2012.values()), 144)
        other = sum(g.TABLE5_2012[t][1] for t in g.V4_ROWS)
        self.assertEqual(g.V4["k"] - other, g.V4["pasta_soup_k"])

    def test_2016_averages(self):
        rows = g.TABLE2_2016.values()
        k = sum(r[1] for r in rows)
        w = sum(r[1] * float(r[4]) for r in rows) / k
        unw = sum(float(r[4]) for r in rows) / len(g.TABLE2_2016)
        self.assertEqual(k, 340)
        self.assertTrue(g.matches(w, "91.6"))
        self.assertTrue(g.matches(unw, "140"))
        self.assertFalse(g.matches(w, "140"))

    def test_2017_meat_average(self):
        fish_k, fish_avg = g.TABLE2_2017["fish"][1], float(g.TABLE2_2017["fish"][4])
        meat_k = g.TABLE2_2017["meat"][1]

        def total(meat_avg):
            return (meat_k * float(meat_avg) + fish_k * fish_avg) / (meat_k + fish_k)

        self.assertTrue(g.matches(total("35.6"), "44.8"))
        for alt in g.MEAT_AVG_ALTERNATIVES:
            self.assertFalse(g.matches(total(alt), "44.8"), alt)


class TestValues(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(g.parse_value("0"), (0.0, "nd"))
        self.assertEqual(g.parse_value("0.0052"), (0.0052, "det"))
        self.assertEqual(g.parse_value("<0.001"), (0.0, "nd"))
        self.assertEqual(g.parse_value("ND"), (0.0, "nd"))
        self.assertEqual(g.parse_value("-1"), (None, "bad"))
        self.assertEqual(g.parse_value(""), (None, "bad"))
        self.assertEqual(g.parse_value("trace"), (None, "bad"))

    def test_units_and_matches(self):
        self.assertEqual(g.unit_label("μg/g"), g.UG)
        self.assertEqual(g.unit_label(" µg/g "), g.UG)
        self.assertTrue(g.matches(0.0052 * 1000, "5.2"))
        self.assertTrue(g.matches(1.204, "1.20"))
        self.assertFalse(g.matches(1.249, "1.20"))
        self.assertTrue(g.matches(138.5, "139") and g.matches(138.5, "138"))
        self.assertFalse(g.matches(None, "1.0"))

    def test_dates_and_ids(self):
        self.assertEqual(g.parse_date("10/1/2009"), datetime.date(2009, 10, 1))
        self.assertEqual(g.parse_date("1/1/2010 0:00"), datetime.date(2010, 1, 1))
        self.assertEqual(g.parse_date("2016-04-12"), datetime.date(2016, 4, 12))
        self.assertIsNone(g.parse_date("13/40/2009"))
        self.assertIsNone(g.parse_date("n/a"))
        self.assertEqual(g.id_number("2009BPA00065"), 65)
        self.assertEqual(g.id_number("C2013BHPA00319D"), 319)
        self.assertIsNone(g.id_number("x"))


class TestParse(unittest.TestCase):
    def rows09(self, third_date="10/3/2009"):
        return [row09("2009BPA0001", "Infant Food", "0", "10/1/2009"),
                row09("2009BPA0002", "Infant Formula", "2.5", "10/2/2009"),
                row09("2009BPA00065", "Infant Formula", "9.6", third_date)]

    def test_2009_file_ng_per_g(self):
        text = toy_csv(H09, self.rows09())
        samples, census = g.parse(text, "bpa-2009")
        self.assertEqual((census["rows"], census["samples"]), (3, 3))
        self.assertEqual(census["units"], {"ng/g": 3})
        self.assertEqual(census["kinds"], {"nd": 1, "det": 2})
        self.assertEqual(census["ids_bad"], [])
        self.assertEqual(census["rows_per_sample"], {"1": 3})
        by = {s["sample"]: s for s in samples}
        self.assertEqual(by["2009BPA0002"]["ppb"]["bpa"], 2.5)
        self.assertEqual(by["2009BPA0002"]["type"], "formula")
        self.assertEqual(by["2009BPA0001"]["type"], "food")
        self.assertEqual(by["2009BPA0001"]["ppb"]["badge"], 0.0)
        gate = g.gate_checks(census, len(text), "bpa-2009")
        for key in ("columns", "per_sample", "components", "units", "plan", "products",
                    "values"):
            self.assertTrue(gate[key], key)
        for key in ("size", "rows", "samples"):
            self.assertFalse(gate[key], key)

    def test_2009_dates(self):
        samples, _ = g.parse(toy_csv(H09, self.rows09()), "bpa-2009")
        t1 = g.date_order(samples)
        self.assertEqual((t1["parsed"], t1["distinct"], t1["span_days"]), (3, 3, 3))
        self.assertEqual((t1["first"], t1["last"]), ("2009-10-01", "2009-10-03"))
        self.assertTrue(t1["consecutive"])
        self.assertEqual(t1["rank_fits"], {"number": 3, "row": 3, "text": 3})
        self.assertEqual(t1["start_plus_number_fits"], 2)
        self.assertEqual(t1["long_ids"], [("2009BPA00065", "2009-10-03")])
        self.assertEqual(t1["weekdays"], {"Thu": 1, "Fri": 1, "Sat": 1})
        samples, _ = g.parse(toy_csv(H09, self.rows09("10/5/2009")), "bpa-2009")
        t1 = g.date_order(samples)
        self.assertFalse(t1["consecutive"])
        self.assertEqual(t1["span_days"], 5)
        self.assertEqual(t1["rank_fits"]["number"], 2)

    def test_2016_file_four_analytes_ug_per_g(self):
        rows = []
        for comp, v in zip(g.COMPONENTS, ("0.306", "0.0161", "0", "0")):
            rows.append(row16("C2016BPHA00001", "Coconut Milk", comp, v))
        for comp, v in zip(g.COMPONENTS, ("2.24", "0", "0", "0")):
            rows.append(row16("C2016BPHA00002", "Pie Filling - Pumpkin", comp, v, "μg/g"))
        samples, census = g.parse(toy_csv(H16, rows), "bpa-2016")
        self.assertEqual((census["rows"], census["samples"]), (8, 2))
        self.assertEqual(census["rows_per_sample"], {"4": 2})
        self.assertEqual(census["kinds"], {"det": 3, "nd": 5})
        self.assertEqual(census["units"], {g.UG: 8})
        by = {s["sample"]: s for s in samples}
        self.assertAlmostEqual(by["C2016BPHA00001"]["ppb"]["bpa"], 306.0)
        self.assertAlmostEqual(by["C2016BPHA00001"]["ppb"]["badge"], 16.1)
        self.assertAlmostEqual(by["C2016BPHA00002"]["ppb"]["bpa"], 2240.0)
        self.assertEqual(by["C2016BPHA00002"]["type"], "pie")
        gate = g.gate_checks(census, 0, "bpa-2016")
        for key in ("columns", "per_sample", "components", "units", "plan", "products",
                    "values"):
            self.assertTrue(gate[key], key)

    def test_bad_cell(self):
        text = toy_csv(H09, [row09("2009BPA0001", "Infant Food", "trace", "10/1/2009")])
        _, census = g.parse(text, "bpa-2009")
        self.assertEqual(census["kinds"], {"bad": 1})
        self.assertFalse(g.gate_checks(census, len(text), "bpa-2009")["values"])


class TestAnalysis(unittest.TestCase):
    def test_v3_on_toy_2011(self):
        n = "bpa-2011"
        samples = [mk(n, "2011BPA0001", "Pasta - Canned", 5.0),
                   mk(n, "2011BPA0002", "Carrot", 6.0), mk(n, "2011BPA0003", "Carrot", 7.0),
                   mk(n, "2011BPA0004", "Carrot", 8.0), mk(n, "2011BPA0005", "Pea - Sugar", 5.5),
                   mk(n, "2011BPA0006", "Corn", 9.0), mk(n, "2011BPA0007", "Peach"),
                   mk(n, "2011BPA0008", "Soup")]
        a = g.analyse_2011(samples)
        self.assertEqual(a["v3"], {"pasta": 1, "carrot": 3, "pea": 1, "corn": 1})
        self.assertEqual(a["bpa"]["all"]["k"], 6)
        self.assertEqual(a["bpa"]["veg"]["k"], 5)
        preds = {p["id"]: p for p in g.grade({n: a}, {n: {"size": True}})}
        self.assertEqual(list(preds), ["G09", "G10", "G11", "G12", "G13", "G16", "G17", "V1",
                                       "V2", "V3", "V4", "V5", "V6", "V7", "D1", "T1", "X6",
                                       "X7"])
        self.assertTrue(preds["G11"]["met"])
        self.assertFalse(preds["G09"]["met"])
        self.assertTrue(preds["V3"]["graded"])
        self.assertTrue(preds["V3"]["met"])
        self.assertFalse(preds["V1"]["graded"])
        self.assertEqual(preds["V1"]["observed"], {})
        self.assertFalse(preds["D1"]["graded"])
        self.assertIsNone(preds["T1"]["met"])

    def test_d1_shares(self):
        s12 = [mk("bpa-2012", "a", "Corn", 5.2), mk("bpa-2012", "b", "Corn"),
               mk("bpa-2012", "c", "Soup", 10.0), mk("bpa-2012", "d", "Curry")]
        s13 = [mk("bpa-2013", "e", "Corn", 1.0), mk("bpa-2013", "f", "Corn", 6.0),
               mk("bpa-2013", "g", "Energy Drink", 50.0), mk("bpa-2013", "h", "Soup", 5.3),
               mk("bpa-2013", "i", "Coconut Milk", 7.0)]
        d = g.d1_analysis(s12, s13)
        self.assertEqual(d["2012-13"]["groups"],
                         {"veg": [2, 1, 1], "pastasoup": [1, 1, 1], "curry": [1, 0, 0]})
        self.assertEqual(d["2013-14"]["groups"],
                         {"veg": [2, 2, 1], "pastasoup": [1, 1, 1], "coconut": [1, 1, 1]})
        self.assertAlmostEqual(d["2012-13"]["share"], 0.5)
        self.assertAlmostEqual(d["2013-14"]["share"], 0.75)
        self.assertAlmostEqual(d["ratio"], 1.5)

    def test_2016_tops_alt_and_twins(self):
        n = "bpa-2016"
        samples = [mk(n, "C1", "Pie Filling - Pumpkin", 2240.0),
                   mk(n, "C2", "Pie Filling - Cherry", 530.0),
                   mk(n, "C3", "Coconut Milk", 0.0, badge=224.0),
                   mk(n, "C4", "Bamboo Shoot", 10.0, bpf=3.8),
                   mk(n, "C5", "Bamboo Shoot", 10.0, bpf=3.8)]
        a = g.analyse_2016(samples)
        self.assertEqual(a["tops"]["pie"]["values"], [2240.0, 530.0])
        self.assertEqual(a["tops"]["pie"]["top"][0]["product"], "Pie Filling - Pumpkin")
        self.assertEqual(a["badge_top"]["sample"], "C3")
        self.assertEqual(a["twins"], [["C4", "C5"]])
        self.assertEqual(a["alt"]["bpf"]["veg"]["k"], 2)
        self.assertFalse(a["alt"]["bpf"]["veg"]["detected"])
        self.assertEqual(a["veg_avg"], {"139": False, "138": False})
        self.assertFalse(a["v6_rows"]["veg"]["avg"])
        self.assertEqual([s["sample"] for s in a["lowest"]], ["C4", "C5"])
        self.assertEqual(a["dates"]["parsed"], 0)

    def test_v7_on_toy_2017(self):
        n = "bpa-2017"
        samples = [mk(n, "C1", "Meat - Canned", 5.0, bps=1.79),
                   mk(n, "C2", "Tuna", 1480.0, badge=2.0),
                   mk(n, "C3", "Salmon", 567.0),
                   mk(n, "C4", "Chicken", 0.0, "Domestic", bpf=2.0)]
        a = g.analyse_2017(samples)
        self.assertEqual([s["sample"] for s in a["top_two"]], ["C2", "C3"])
        self.assertEqual(a["badge"]["k"], 1)
        self.assertEqual(a["badge"]["with_bpa"], 1)
        self.assertEqual(a["bpf"], {"k": 1, "with_bpa": 0})
        self.assertEqual(a["origins"]["meat"], [1, 1, 0, 2])
        preds = {p["id"]: p for p in g.grade({n: a}, {n: {"size": True}})}
        checks = preds["V7"]["observed"]["checks"]
        self.assertTrue(checks["top_1480_imported_fish_next_567"])
        self.assertTrue(checks["one_bps_meat_1.79"])
        self.assertFalse(checks["badge_72_of_which_69_with_bpa"])
        self.assertFalse(checks["bpf_68_all_with_bpa"])
        self.assertFalse(checks["meat_row"])
        self.assertFalse(preds["V7"]["met"])
        self.assertIsNone(preds["X7"]["met"])
        self.assertFalse(preds["X7"]["observed"]["badge_avg_10.1"])

    def test_grade_without_data_grades_nothing(self):
        preds = g.grade({}, {})
        for p in preds:
            if p["kind"] == "gate":
                self.assertFalse(p["met"])
            else:
                self.assertFalse(p["graded"])
                self.assertEqual(p["observed"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
