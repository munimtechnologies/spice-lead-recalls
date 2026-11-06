# SPDX-License-Identifier: Apache-2.0
"""Offline tests for phthalates_2020.py (no network, no CFIA file). Synthetic data only.
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import io
import unittest

import phthalates_2020 as g

HEADER = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin",
          "Origine", "Product", "Produit",
          "Date Sampled – Date d’échantillonage", "Type of Test",
          "Type d’analyse", "Component", "Composant", "Result - Résultat",
          "Unit - Unité", "Plan Code - Code du régime"]
UG = "µg/g"
DEHP = "Bis(2-ethylhexyl) phthalate"


def screen(n):
    word = "Phthalate" if n == 1 else "Phthalates"
    return f"{n} {word} detected / Phtalate détecté"


def text(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for sid, func, product, comp, result, unit in rows:
        w.writerow([sid, func, "F", "CANADA", "C", product, "P", "2020-06-01", "Phthalate",
                    "Phtalate", comp, "C", result, unit, "2020_SRDEHP"])
    return "﻿" + buf.getvalue()


def sample(i, product, values, function="Import"):
    return g.finish({"id": f"C{i:05d}", "product": product, "function": function, "origin": "",
                     "screen_n": sum(1 for v in values.values() if v > 0),
                     "values": dict(values)})


def population():
    pos = [("Meal - RTE", 0.3), ("Meal - Toddler/Baby", 4.2), ("Meal - RTE", 1.0),
           ("Meal - RTE", 1.1), ("Meal - RTE", 1.2)]
    pos += [("Oil - Canola", 0.2), ("Oil - Canola", 3.4)] + [("Oil - Canola", 0.82)] * 26
    pos += [("Oil - Canola", 0.89), ("Salad Dressing", 0.3), ("Salad Dressing", 0.6)]
    others = ["BBP", "DNOP", "DIDP", "DIDP", "DIDP", "DBP"]
    out = []
    for i, (p, t) in enumerate(pos):
        if i < 23:
            vals = {"DEHP": t}
        elif i < 30:
            vals = {"DBP": t / 2, "DINP": t / 2}
        else:
            vals = {others[i - 30]: t}
        out.append(sample(i, p, vals))
    negs = (["Soup"] * 245 + ["Oil - Canola"] * 121 + ["Salad Dressing"] * 48
            + ["Vegetable Shortening"] * 48 + ["Mayonnaise"] * 2)
    for j, p in enumerate(negs):
        out.append(sample(100 + j, p, {}))
    return out


class TestMap(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(g.subgroup("Infant Food - Puree"), "rte")
        self.assertEqual(g.subgroup("Soup"), "rte")
        self.assertEqual(g.subgroup("Oil - Sesame"), "oil")
        self.assertEqual(g.subgroup("Salad Dressing"), "dressing")
        self.assertEqual(g.subgroup("Vegetable  Shortening"), "shortening")
        self.assertEqual(g.subgroup("Mayonnaise"), "mayo")
        self.assertEqual(g.subgroup("Mustard"), "unmapped")
        self.assertEqual(g.group_of("mayo"), "fo")
        self.assertEqual(g.group_of("rte"), "rte")
        self.assertEqual(g.group_of("unmapped"), "unmapped")

    def test_target(self):
        self.assertEqual(g.TARGET["md5"], "612780be14a4a571044d93aaa27f99f2")
        self.assertEqual(g.TARGET["size_band"], (113000, 118000))
        self.assertEqual(len(g.RTE_LABELS), 5)


class TestParse(unittest.TestCase):
    def test_clean_file(self):
        rows = [("C1", "Import", "Meal - Toddler/Baby", "Phthalate Screen", screen(2), "n/a"),
                ("C1", "Import", "Meal - Toddler/Baby", DEHP, "1.5", UG),
                ("C1", "Import", "Meal - Toddler/Baby", "Dibutylphthalate", "0.3", UG),
                ("C2", "Domestic", "Salad Dressing", "Phthalate Screen", screen(0), "n/a"),
                ("C3", "Unknown", "Oil - Canola", "Phthalate Screen", screen(1), "n/a"),
                ("C3", "Unknown", "Oil - Canola", DEHP, "0,4", UG),
                ("C4", "Import", "Vegetable Shortening", "Phthalate Screen", screen(0), "n/a")]
        samples, problems = g.parse(text(rows))
        self.assertFalse(any(problems.values()), problems)
        by = {s["id"]: s for s in samples}
        self.assertEqual(len(samples), 4)
        self.assertEqual(by["C1"]["total"], 1.8)
        self.assertEqual(by["C1"]["n_pos"], 2)
        self.assertEqual(by["C1"]["screen_n"], 2)
        self.assertEqual(by["C1"]["group"], "rte")
        self.assertEqual(by["C1"]["values"], {"DEHP": 1.5, "DBP": 0.3})
        self.assertEqual(by["C2"]["total"], 0)
        self.assertEqual(by["C2"]["screen_n"], 0)
        self.assertEqual(by["C3"]["total"], 0.4)
        self.assertEqual(by["C3"]["sub"], "oil")
        self.assertEqual(by["C4"]["sub"], "shortening")
        self.assertEqual(by["C4"]["group"], "fo")
        self.assertEqual(by["C2"]["function"], "Domestic")

    def test_problems(self):
        rows = [("X1", "Import", "Soup", "Phthalate Screen", screen(1), "n/a"),
                ("X1", "Import", "Soup", "Diethyl phthalate", "0.5", UG),
                ("X2", "Import", "Soup", "Phthalate Screen", screen(1), "n/a"),
                ("X2", "Import", "Soup", DEHP, "<LOD", UG),
                ("X3", "Import", "Mustard", "Phthalate Screen", screen(1), "n/a"),
                ("X3", "Import", "Mustard", DEHP, "1.0", "ng/g"),
                ("X4", "Import", "Soup", DEHP, "1.0", UG)]
        _, p = g.parse(text(rows))
        self.assertEqual(p["unknown_component"], ["X1: diethyl phthalate"])
        self.assertEqual(p["non_numeric"], ["X2: DEHP"])
        self.assertEqual(p["bad_unit"], ["X3: DEHP"])
        self.assertEqual(p["unmapped_product"], ["X3: Mustard"])
        self.assertEqual(p["no_screen"], ["X4"])
        self.assertEqual(p["bad_screen"], [])
        self.assertEqual(p["repeated"], [])
        self.assertEqual(p["mixed_product"], [])


class TestRules(unittest.TestCase):
    def test_near_and_share(self):
        self.assertTrue(g.near(0.8625, 0.86, 2))
        self.assertFalse(g.near(0.866, 0.86, 2))
        self.assertTrue(g.near(4.24, 4.2, 1))
        self.assertFalse(g.near(None, 4.2, 1))
        self.assertEqual(g.share(31, 250), 12)
        self.assertEqual(g.share(5, 250), 2)
        self.assertEqual(g.share(36, 500), 7)
        self.assertEqual(g.share(1, 8), 13)

    def test_stats(self):
        st = g.stats([sample(1, "Soup", {"DEHP": 1.8}), sample(2, "Soup", {"DEHP": 0.4}),
                      sample(3, "Soup", {})])
        self.assertEqual(st, {"n": 3, "positives": 2, "min": 0.4, "max": 1.8, "mean": 1.1})


class TestGrade(unittest.TestCase):
    def test_all_hold_on_report_shaped_population(self):
        pop = population()
        self.assertEqual(len(pop), 500)
        r = g.grade(pop)
        for key in ("V1", "V2", "V3", "V4", "V5"):
            self.assertTrue(r[key]["held"], (key, r[key]))
        self.assertEqual(r["V3"]["per_phthalate_positive_samples"],
                         {"BBP": 1, "DBP": 8, "DNOP": 1, "DEHP": 23, "DINP": 7, "DIDP": 3})
        self.assertEqual(r["V4"]["dressing_positives"], [0.3, 0.6])
        c = g.census_items(pop)
        self.assertTrue(c["S1"]["held"])
        self.assertTrue(c["S2"]["held"])
        self.assertFalse(c["S3"]["held"])

    def test_a_positive_shortening(self):
        pop = population()
        i = next(k for k, s in enumerate(pop) if s["product"] == "Vegetable Shortening")
        pop[i] = sample(999, "Vegetable Shortening", {"DEHP": 0.5})
        r = g.grade(pop)
        self.assertFalse(r["V5"]["held"])
        self.assertFalse(r["V1"]["held"])
        self.assertFalse(r["V3"]["held"])
        self.assertFalse(r["V2"]["held"])
        self.assertTrue(r["V4"]["held"])
        self.assertEqual(r["V1"]["rows"]["fo"]["stats"]["positives"], 32)

    def test_top_without_children_label(self):
        pop = population()
        i = next(k for k, s in enumerate(pop) if s["total"] == 4.2)
        pop[i] = sample(998, "Meal - RTE", {"DEHP": 4.2})
        r = g.grade(pop)
        self.assertFalse(r["V2"]["held"])
        self.assertFalse(r["V2"]["checks"]["top_children_label"])
        self.assertTrue(r["V1"]["held"])
        self.assertTrue(r["V4"]["held"])


class TestGateAndDescriptive(unittest.TestCase):
    def test_gate(self):
        pop = population()
        empty = {"bad_unit": [], "no_screen": []}
        gt = g.gate(117529, True, pop, empty)
        self.assertTrue(gt["A1"])
        self.assertFalse(gt["G_as_written"])
        self.assertEqual(gt["screen_tokens_that_are_counts"], 36)
        self.assertFalse(g.gate(120000, True, pop, empty)["A1"])
        self.assertFalse(g.gate(117529, True, pop, {"bad_unit": ["x"]})["A1"])

    def test_screen_mismatch(self):
        pop = population()
        self.assertEqual(g.descriptive(pop)["screen_vs_rows_mismatch"], [])
        pop.append(sample(997, "Soup", {"DEHP": 0.0}))
        mm = g.descriptive(pop)["screen_vs_rows_mismatch"]
        self.assertEqual(mm, [{"id": "C00997", "screen_n": 0, "rows": 1, "above_zero": 0}])


if __name__ == "__main__":
    unittest.main()
