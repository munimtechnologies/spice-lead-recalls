# SPDX-License-Identifier: Apache-2.0
"""Offline tests for perchlorate_series.py (perchlorate-series 0.1.0 grader). Label counts are
copied from the published census records (data/perchlorate_p1x_census.json); every value is
synthetic. No network and no CFIA file. Made with AI agents working in MV2's (Munim, Inc.) name."""
import csv
import hashlib
import io
import unittest

import perchlorate_series as ps

P10_COUNTS = {
    "Arugula": 6, "Bean - Green/Yellow": 23, "Broccoli": 23, "Broccoli - Organic": 1,
    "Cabbage": 25, "Cabbage - Chinese": 2, "Carrot": 39, "Carrot - Organic": 1, "Celery": 22,
    "Celery - Organic": 2, "Chard": 6, "Chard - Organic": 2, "Cheese": 23, "Cucumber": 22,
    "Grape": 26, "Grape - Organic": 3, "Infant Formula - Dairy": 74, "Infant Formula - Soy": 15,
    "Kale": 3, "Kale - Organic": 1, "Lettuce": 12, "Lettuce - Leaf": 24, "Lettuce - head": 1,
    "Melon - Cantaloupe": 16, "Milk": 42, "Misc Vegetables": 11, "Orange": 22,
    "Orange - Organic": 1, "Radicchio": 1, "Spinach": 40, "Strawberry": 19, "Tomato": 54,
    "Tomato (GH)": 1, "Watermelon": 24, "Yogurt": 24}
P11_COUNTS = {
    "Arugula": 1, "Blueberry": 16, "Blueberry - Organic": 6, "Chard": 35, "Chard - Organic": 13,
    "Cheese": 1, "Cider - Apple": 6, "Cream": 15, "Cucumber": 90, "Cucumber - Organic": 5,
    "Dessert - Frozen": 28, "Dessert - Frozen (Dairy)": 3, "Desserts": 7, "Dressing": 28,
    "Endive - Broadleaf": 1, "Grapefruit": 19, "Grapefruit - Organic": 6,
    "Infant Formula - Dairy": 67, "Infant Formula - Dairy - Organic": 1,
    "Infant Formula - Soy": 19, "Juice - Apple": 20, "Juice - Apple - Organic": 2,
    "Juice - Blend": 5, "Juice - Blueberry": 3, "Juice - Carrot": 12, "Juice - Cranberry": 3,
    "Juice - Grape": 27, "Juice - Grape - Organic": 1, "Juice - Grapefruit": 5,
    "Juice - Mixed": 10, "Juice - Orange": 29, "Juice - Orange - Organic": 3,
    "Juice - Other": 42, "Juice - Pomegranate": 5, "Juice - Tomato": 16, "Juice - Vegetable": 28,
    "Juice - Vegetable - ORGANIC": 2, "Kale - Organic": 1, "Lemon": 20, "Lemon - Organic": 5,
    "Lettuce": 116, "Lettuce - Boston": 2, "Lettuce - Leaf": 101, "Lettuce - Leaf - Organic": 3,
    "Lettuce - Organic": 18, "Lettuce - head": 6, "Lettuce - head - Organic": 1,
    "Melon - Cantaloupe": 19, "Melon - Cantaloupe - Organic": 3, "Misc": 2, "Misc - Dairy": 85,
    "Misc - Dairy - Organic": 2, "Nectar - Other": 4, "Nectar - Prune": 2, "Orange": 83,
    "Orange - Organic": 9, "Pudding": 25, "Sauces": 37, "Spinach": 42, "Spinach - Organic": 2,
    "Strawberry": 78, "Strawberry - Organic": 8, "Tomato": 80, "Tomato - Organic": 8,
    "Watermelon": 79, "Watermelon - Organic": 5}
P13_COUNTS = {
    "Arugula": 9, "Basil": 6, "Bay Leaves": 1, "Beverage - Fruit": 1, "Beverage - Other": 3,
    "Beverage - Yogurt": 10, "Camembert": 3, "Cheddar": 1, "Cheese": 13, "Chive": 3,
    "Cilantro": 2, "Couscous": 10, "Cranberry - dried": 5, "Dandelion": 1, "Date": 5,
    "Dessert - Frozen (Dairy)": 9, "Dessert - Frozen (Non-Dairy)": 1, "Dill": 3,
    "Dried Fruit": 20, "Dried Vegetables": 17, "Endive": 2, "Endive - Broadleaf": 2, "Feta": 2,
    "Fig": 5, "Fingerling Potatoes": 4, "Flour - Rice": 9, "Flour - Wheat": 15, "Gouda": 1,
    "Grain - Rice": 14, "Grain - Wheat": 1, "Herb - Bay Leaves - Fresh": 2,
    "Herb - Chive - Fresh": 2, "Herb - Cilantro - Fresh": 1, "Herb - Dill - Fresh": 1,
    "Herb - Oregano - Fresh": 4, "Herb - Parsley - Fresh": 1, "Herb - Rosemary - Fresh": 2,
    "Herb - Sage - Fresh": 1, "Infant Formula - Dairy": 23, "Infant Formula - Other": 7,
    "Infant Formula - Soy": 9, "Juice - Apple": 2, "Juice - Blend": 25, "Juice - Grapefruit": 1,
    "Juice - Mixed": 4, "Juice - Other": 8, "Juice/Nectar - Other": 3, "Kale": 6, "Lettuce": 3,
    "Lettuce - Leaf - Organic": 1, "Lettuce - Organic": 2, "Meat Alternative": 10, "Mint": 4,
    "Misc Vegetables": 2, "Mixed Vegetables": 10, "Nectar - Apricot": 1, "Nectar - Guava": 1,
    "Oregano": 6, "Parsley": 3, "Pizza Products": 20, "Potato - Fingerling": 2,
    "Potato - New": 1, "Potato - Organic": 2, "Potato - Other": 1, "Potato - Russet": 1,
    "Potato - White": 2, "Potato - Yellow": 1, "Potato Products": 1, "Potatoes": 4, "Prune": 5,
    "Raisin": 5, "Rapini": 1, "Red Potatoes": 9, "Rice Products": 2, "Rosemary": 3,
    "Russet Potatoes": 5, "Sage": 4, "Salsa": 9, "Soup": 15, "Spinach": 2, "Thyme": 5,
    "Tofu": 10, "Wheat Products": 9, "White Potatoes": 5, "Yellow Potatoes": 9, "Yogurt": 10,
    "Yogurt - Frozen": 10, "juice - pineapple": 1}

H = ["﻿Sample No. – No. d’échantillon", "Region - Région", "Function",
     "Fonction", "Origin", "Origine", "Product", "Produit",
     "Date Sampled – Date d’échantillonage", "Type of Test",
     "Type d’analyse", "Component", "Composant", "Result - Résultat",
     "Unit - Unité", "Plan Code - Code du régime"]
H11 = H[:8] + ["DateSample"] + H[9:]


def _csv(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def _row(sid, product, date, value, region="WEST"):
    return [sid, region, "Import", "Import", "USA", "USA", product, product, date,
            "PERCHLORATE", "PERCHLORATE", "Perchlorate", "Perchlorate", value, "ng/g",
            "2013_TS006"]


def _target(raw, n):
    return {"size": len(raw), "md5": hashlib.md5(raw).hexdigest(), "samples": n}


def mk(product, value, year="2011-12", sid=None):
    return {"sample": sid or f"{product}-{value}-{year}", "product": product, "value": value,
            "year": year, "region": "WEST", "origin": "USA", "function": "Import", "date": ""}


class TestMaps(unittest.TestCase):
    def test_base(self):
        self.assertEqual(ps.base("Tomato (GH)"), "Tomato")
        self.assertEqual(ps.base("Juice - Vegetable - ORGANIC"), "Juice - Vegetable")
        self.assertEqual(ps.base("Lettuce - head - Organic"), "Lettuce")
        self.assertEqual(ps.base("Infant Formula - Dairy - Organic"), "Infant Formula - Dairy")
        self.assertEqual(ps.base("Misc - Dairy - Organic"), "Misc - Dairy")

    def test_p10_groups(self):
        sizes = {}
        for lab, n in P10_COUNTS.items():
            g = ps.p10_group(lab)
            sizes[g] = sizes.get(g, 0) + n
        self.assertEqual(sizes, {"fv": 433, "dairy": 89, "formula": 89})

    def test_p11_groups(self):
        sizes, leafy = {}, 0
        for lab, n in P11_COUNTS.items():
            g = ps.p11_group(lab)
            self.assertIsNotNone(g, lab)
            sizes[g] = sizes.get(g, 0) + n
            if ps.base(lab) in ps.P11_LEAFY:
                leafy += n
        self.assertEqual(sizes, {"fruit": 356, "veg": 525, "juice": 225, "dairy": 233,
                                 "formula": 87})
        self.assertEqual(leafy, 342)

    def test_p13_grading_map(self):
        self.assertEqual(sum(P13_COUNTS.values()), 477)
        self.assertEqual(len(P13_COUNTS), 88)
        self.assertEqual(set(ps.P13_MAP), set(P13_COUNTS))
        sizes, unmapped = ps.group_sizes(P13_COUNTS, ps.P13_MAP)
        self.assertEqual(unmapped, {})
        self.assertEqual(sizes, {"fresh": 131, "processed": 97, "dairy": 50, "formula": 39,
                                 "grain": 60, "assorted": 100})


class TestShares(unittest.TestCase):
    def test_pct(self):
        self.assertTrue(ps.pct_ok(21, 39, 54))
        self.assertFalse(ps.pct_ok(16, 30, 54))
        self.assertFalse(ps.pct_ok(17, 30, 54))
        self.assertEqual(ps.feasible(131, 71), [93])
        self.assertEqual(ps.feasible(97, 40), [39])
        self.assertEqual(ps.feasible(60, 30), [18])
        self.assertEqual(ps.feasible(100, 61), [61])
        self.assertEqual(ps.feasible(50, 80), [40])
        self.assertEqual(ps.feasible(39, 54), [21])
        self.assertEqual(ps.feasible(53, 61), [])

    def test_grading_map_pins_every_count(self):
        sizes, _ = ps.group_sizes(P13_COUNTS, ps.P13_MAP)
        ok, bands = ps.shares_feasible(sizes)
        self.assertTrue(ok)
        self.assertEqual(bands, {"fresh": [93, 93], "processed": [39, 39], "dairy": [40, 40],
                                 "formula": [21, 21], "grain": [18, 18],
                                 "assorted": [61, 61]})

    def test_juices_as_processed_cannot_give_61pct(self):
        sizes, _ = ps.group_sizes(P13_COUNTS, ps.p13_map({"juices": "processed"}))
        self.assertEqual(sizes["assorted"], 53)
        self.assertEqual(sizes["processed"], 144)
        ok, bands = ps.shares_feasible(sizes)
        self.assertFalse(ok)
        self.assertIsNone(bands["assorted"])

    def test_open_blocks_have_one_placement(self):
        res = ps.p13_map_search(P13_COUNTS, ps.P13_OPEN_BLOCKS)
        self.assertEqual(len(res), 16)
        good = [r["choice"] for r in res if r["feasible"]]
        self.assertEqual(good, [{"juices": "assorted", "soup": "processed",
                                 "salsa": "processed", "beverage_other": "assorted"}])


class TestReading(unittest.TestCase):
    def test_p11_dates_and_smoke(self):
        rows = [_row("2011PER0001", "Cream", "1/11/2012", "3.0"),
                _row("C2012PERC00003", "Cream", "10/22/2012", "7"),
                _row("2011PER0002", "Infant Formula - Soy", "5/3/2011", "0"),
                _row("2011PER0003", "Lettuce - Leaf - Organic", "6/1/2011", "65")]
        text = _csv(H11, rows)
        raw = text.encode("utf-8")
        rec, preds, samples, g = ps.grade_file("p11", raw, text, _target(raw, 4))
        self.assertTrue(all(rec["gate"].values()), rec["gate"])
        self.assertEqual(samples["2011PER0001"]["year"], "2011-12")
        self.assertEqual(samples["C2012PERC00003"]["year"], "2012-13")
        self.assertEqual(samples["2011PER0002"]["year"], "2011-12")
        self.assertEqual([p["id"] for p in preds], ["V5", "V6", "V7"])
        v6 = preds[1]["observed"]
        self.assertEqual(v6["cream_years"], {"2011-12": 1, "2012-13": 1})
        self.assertEqual(rec["descriptive"]["coding"]["zero"], 1)
        self.assertEqual(rec["census_checks"]["groups"], {"dairy": 2, "formula": 1, "veg": 1})

    def test_p13_smoke(self):
        rows = [_row("1", "Arugula", "13-Jun-13", "3300"),
                _row("2", "Cheese", "5-Jul-13", "3"),
                _row("3", "Infant Formula - Soy", "31-Mar-14", "0", region="ONTARIO")]
        text = _csv(H, rows)
        raw = text.encode("utf-8")
        rec, preds, samples, g = ps.grade_file("p13", raw, text, _target(raw, 3))
        self.assertTrue(all(rec["gate"].values()), rec["gate"])
        self.assertEqual(samples["3"]["year"], "2013-14")
        v8 = preds[0]["observed"]["checks"]
        self.assertTrue(v8["max_3300"])
        self.assertTrue(v8["max_is_arugula"])
        self.assertFalse(v8["none_205"])
        self.assertEqual(len(rec["map_search_open_blocks"]), 16)
        self.assertEqual(rec["descriptive"]["scale"]["fresh"]["WEST"]["max"], 3300.0)

    def test_gate_fails_on_unit_and_unmapped(self):
        rows = [_row("1", "Arugula", "13-Jun-13", "3"), _row("2", "Pasta", "13-Jun-13", "0")]
        rows[0][14] = "ug/g"
        text = _csv(H, rows)
        raw = text.encode("utf-8")
        rec, preds, _, _ = ps.grade_file("p13", raw, text, _target(raw, 2))
        self.assertFalse(rec["gate"]["units"])
        self.assertFalse(rec["gate"]["all_labels_mapped"])
        self.assertTrue(all(not p["graded"] for p in preds))


class TestGraders(unittest.TestCase):
    def test_v2_holds(self):
        g = {"fv": [mk("Cucumber", 48.6), mk("Tomato (GH)", 44.9), mk("Tomato", 44.9),
                    mk("Spinach", 40.0), mk("Carrot", 0)],
             "dairy": [mk("Cheese", 5.0), mk("Milk", 4.0), mk("Yogurt", 4.9)],
             "formula": [mk("Infant Formula - Soy", 16.7), mk("Infant Formula - Dairy", 30.0)]}
        p = ps.grade_v2(g)
        self.assertTrue(p["met"], p["observed"]["checks"])

    def test_v4_dairy_subset(self):
        dairy = [mk("Infant Formula - Dairy", v, sid=f"d{i}")
                 for i, v in enumerate([2.0, 22.0, 7.2] + [0] * 71)]
        soy = [mk("Infant Formula - Soy", 30.0, sid=f"s{i}") for i in range(15)]
        p = ps.grade_v4({"formula": dairy + soy})
        self.assertTrue(p["met"], p["observed"]["checks"])
        self.assertEqual(p["observed"]["all_formulas"]["max"], 30.0)
        self.assertEqual(p["observed"]["dairy_formula"]["n"], 74)

    def test_v6_creams_and_non_soy(self):
        creams = ([mk("Cream", v, "2011-12", f"a{i}") for i, v in enumerate([3.0, 6.0, 4.0, 4.2])]
                  + [mk("Cream", v, "2012-13", f"b{i}")
                     for i, v in enumerate([3.0, 7.0, 3.0, 3.0, 4.0, 0])])
        forms = ([mk("Infant Formula - Dairy", v, "2011-12", f"f{i}")
                  for i, v in enumerate([2.0, 33.0, 8.0, 8.0, 8.0])]
                 + [mk("Infant Formula - Soy", 50.0, "2011-12", "soy")])
        p = ps.grade_v6({"dairy": creams, "formula": forms})
        self.assertTrue(p["met"], p["observed"]["checks"])
        self.assertEqual(p["observed"]["cream_years"], {"2011-12": 4, "2012-13": 6})


if __name__ == "__main__":
    unittest.main()
