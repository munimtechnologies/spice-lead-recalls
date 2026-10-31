#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for pah_2019.py (no network, no CFIA data). Made with AI agents working in
MV2's (Munim, Inc.) name."""
import unittest

import pah_2019 as p

# The file's header, as the names-only census printed it (escapes for the accented letters).
HEADER = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin",
          "Originé", "Product", "Produit",
          "Date Sampled – Date d’échantillonage", "Type of Test",
          "Type d'analyse", "Component", "Composant", "Result - Résultat",
          "Unit - Unité", "Plan Code - Code du régime"]
# Label counts from data/pah-2019_census.json.
CENSUS_PRODUCTS = {
    "Butter - Almond": 7, "Butter - Blend": 7, "Butter - Cashew": 7, "Butter - Hazelnut": 3,
    "Butter - Peanut": 7, "Butter - Pumpkin Seed": 1, "Butter - Soy": 7,
    "Butter - Sunflower Seed": 4, "Butter - Walnut": 1, "Infant Formula - Dairy": 23,
    "Infant Formula - Soy": 11, "Nut - Almond": 1, "Nut - Brazil Nut": 7, "Nut - Cashew": 7,
    "Nut - Chestnut": 1, "Nut - Hazelnut/Filbert": 7, "Nut - Macadamia Nut": 7,
    "Nut - PINE NUT": 3, "Nut - Pecan": 7, "Nut - Walnut": 7, "Oil - Olive": 148, "Peanut": 6,
    "Seed - Chia": 1, "Seed - Flax": 2, "Seed - Pumpkin": 2, "Seed - Sunflower": 5, "Tahini": 7}


def toy_csv(samples):
    """A CSV in the file's layout. `samples` = [(id, product, function, {component: value})];
    components not given are written as 0."""
    out = [",".join('"%s"' % h for h in HEADER)]
    for sid, product, function, vals in samples:
        for c in p.COMPONENTS:
            v = vals.get(c, 0)
            out.append(",".join(['"%s"' % x for x in (
                sid, function, function, "CANADA", "CANADA", product, product, "2019-06-01",
                "BENZOPYRENE (PAH)", "HAP", c, c, str(v), "ng/g", p.PLAN)]))
    return "\n".join(out) + "\n"


def sample(sid, product, teq_bap, function="Import", **extra):
    """A parsed sample whose only TEQ compound is benzo[a]pyrene (so TEQ = teq_bap)."""
    vals = {c: 0.0 for c in p.COMPONENTS}
    vals["Benzo[a]pyrene"] = teq_bap
    vals.update(extra)
    s = {"sample": sid, "product": product, "origin": "CANADA", "function": function,
         "date": "2019-06-01", "n_rows": 16, "values": {c: [v] for c, v in vals.items()},
         "bad": False}
    return p.finish(s)


class TestColumns(unittest.TestCase):
    def test_real_header(self):
        col = p.find_columns(HEADER)
        self.assertEqual(col, {"sample": 0, "component": 10, "value": 12, "unit": 13,
                               "product": 5, "origin": 3, "function": 1, "region": None,
                               "date": 7, "plan": 14})


class TestLabels(unittest.TestCase):
    def test_map_gives_table_counts(self):
        self.assertEqual(set(CENSUS_PRODUCTS), p.LABELS)
        got = {}
        for label, n in CENSUS_PRODUCTS.items():
            got[p.GROUP_OF[label]] = got.get(p.GROUP_OF[label], 0) + n
        self.assertEqual(got, {"formula": 34, "nuts": 114, "olive": 148})
        self.assertEqual({g: p.TABLE2[g][0] for g in p.GROUPS}, got)
        self.assertEqual(len(p.NUTS), 24)
        self.assertEqual(CENSUS_PRODUCTS["Infant Formula - Dairy"], p.DAIRY_N)

    def test_printed_rows_add_up(self):
        pi = p.printed_internal()
        self.assertEqual(pi["n_sum"], 296)
        self.assertEqual(pi["detected_sum"], 181)
        lo, hi = pi["olive_avg_bounds"]
        self.assertAlmostEqual(lo, 0.22649, places=4)
        self.assertAlmostEqual(hi, 0.24641, places=4)
        self.assertTrue(lo <= 0.23 <= hi and lo <= 0.24 <= hi)
        self.assertEqual(tuple(sum(p.TABLE1[g][i] for g in p.GROUPS) for i in range(4)),
                         (41, 210, 45, 296))


class TestValues(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(p.parse_value("0"), (0.0, "nd"))
        self.assertEqual(p.parse_value("0.0123"), (0.0123, "det"))
        self.assertEqual(p.parse_value("<0.05"), (0.0, "nd"))
        self.assertEqual(p.parse_value("ND"), (0.0, "nd"))
        self.assertEqual(p.parse_value("-1"), (None, "bad"))
        self.assertEqual(p.parse_value(""), (None, "bad"))
        self.assertEqual(p.parse_value("n/a"), (None, "bad"))

    def test_teq_and_pah4(self):
        vals = {"Benzo[a]pyrene": 1.0, "Benz[a]anthracene": 2.0, "Benzo[b]fluoranthene": 3.0,
                "Chrysene": 4.0, "Pyrene": 100.0}
        self.assertAlmostEqual(p.teq(vals), 1.54)
        self.assertAlmostEqual(p.pah4(vals), 10.0)
        self.assertEqual(p.component("Benz[a]anthracene"), "Benz[a]anthracene")
        self.assertEqual(p.component(" Indeno[1,2,3-cd]pyrene "), "Indeno[1,2,3-cd]pyrene")
        self.assertIsNone(p.component("Benzo[a]anthracene"))

    def test_matches(self):
        self.assertTrue(p.matches(0.2349, "0.23"))
        self.assertFalse(p.matches(0.2351, "0.23"))
        self.assertTrue(p.matches(3.245, "3.25"))
        self.assertTrue(p.matches(0.0014, "0.001"))
        self.assertFalse(p.matches(None, "0.001"))


class TestParse(unittest.TestCase):
    def test_toy_file(self):
        text = toy_csv([("C2019PAHS00001A", "Oil - Olive", "Import",
                         {"Benzo[a]pyrene": 0.5, "Chrysene": 1.0}),
                        ("C2019PAHS00002A", "Tahini", "Domestic", {})])
        samples, census = p.parse(text)
        self.assertEqual((census["rows"], census["samples"]), (32, 2))
        self.assertEqual(census["rows_per_sample"], {"16": 2})
        self.assertEqual(census["units"], {"ng/g": 32})
        self.assertEqual(census["kinds"], {"det": 2, "nd": 30})
        self.assertEqual(census["ids_bad"], [])
        by = {s["sample"]: s for s in samples}
        self.assertAlmostEqual(by["C2019PAHS00001A"]["teq"], 0.51)
        self.assertAlmostEqual(by["C2019PAHS00001A"]["pah4"], 1.5)
        self.assertEqual(by["C2019PAHS00001A"]["group"], "olive")
        self.assertEqual(by["C2019PAHS00002A"]["group"], "nuts")
        self.assertEqual(by["C2019PAHS00002A"]["n_pah"], 0)
        self.assertEqual(by["C2019PAHS00001A"]["date"], "2019-06-01")
        gate = p.gate_checks(census, len(text))
        for key in ("columns", "per_sample", "components", "units", "plan", "products",
                    "values"):
            self.assertTrue(gate[key], key)
        for key in ("size", "rows", "samples"):
            self.assertFalse(gate[key], key)

    def test_bad_cell_and_bad_id(self):
        text = toy_csv([("C2019PAHS00001", "Oil - Olive", "Import", {"Pyrene": "trace"})])
        _, census = p.parse(text)
        self.assertEqual(census["kinds"].get("bad"), 1)
        self.assertEqual(census["ids_bad"], ["C2019PAHS00001"])
        gate = p.gate_checks(census, p.SIZE)
        self.assertFalse(gate["values"])
        self.assertFalse(gate["samples"])


class TestAnalysis(unittest.TestCase):
    def toy(self):
        return [sample("C2019PAHS00001A", "Infant Formula - Dairy", 0.776),
                sample("C2019PAHS00002A", "Infant Formula - Soy", 0.0),
                sample("C2019PAHS00003A", "Butter - Pumpkin Seed", 2.93, "Domestic"),
                sample("C2019PAHS00004A", "Nut - Pecan", 0.5, "Unknown"),
                sample("C2019PAHS00005A", "Oil - Olive", 3.25,
                       **{"Chrysene": 8.0, "Benzo[b]fluoranthene": 1.0}),
                sample("C2019PAHS00006A", "Oil - Olive", 0.9),
                sample("C2019PAHS00007A", "Oil - Olive", 0.7),
                sample("C2019PAHS00008A", "Oil - Olive", 0.002),
                sample("C2019PAHS00009A", "Oil - Olive", 0.002)]

    def test_analyse_and_grade(self):
        a = p.analyse(self.toy())
        self.assertEqual(a["formula_kinds"]["dairy"]["k"], 1)
        self.assertEqual(a["formula_kinds"]["soy"]["k"], 0)
        self.assertEqual(a["nut_top"][0]["product"], "Butter - Pumpkin Seed")
        self.assertEqual(len(a["olive_high"]), 3)
        self.assertEqual([s["sample"] for s in a["eu_bap_over"]], ["C2019PAHS00005A"])
        self.assertEqual([s["sample"] for s in a["eu_pah4_over"]], ["C2019PAHS00005A"])
        self.assertAlmostEqual(a["groups"]["olive"]["max"], 3.25 + 0.1 + 0.08)
        self.assertEqual(a["origins"]["nuts"], [1, 0, 1, 2])
        self.assertEqual(a["origins_table1_diff"]["olive"], [-1, -128, -14, -143])
        self.assertEqual(a["twins_16"], [["C2019PAHS00008A", "C2019PAHS00009A"]])
        self.assertEqual(a["twins_pah4"], [])
        self.assertEqual(a["dates"]["distinct"], 1)
        gate = {k: True for k in ("size", "columns", "rows")}
        preds = {q["id"]: q for q in p.grade(a, gate)}
        self.assertEqual(list(preds), ["G", "D2", "D3", "D4", "D5"])
        self.assertTrue(preds["D2"]["graded"])
        self.assertFalse(preds["D2"]["met"])
        checks = preds["D4"]["observed"]["checks"]
        self.assertEqual(checks, {"dairy_16_of_23_max_0.776": False, "soy_none": True,
                                  "nut_top_pumpkin_seed_butter": True,
                                  "olive_three_at_0.700": True})
        self.assertFalse(preds["D5"]["graded"])
        self.assertIsNone(preds["D5"]["met"])

    def test_grade_without_data_grades_nothing(self):
        preds = p.grade({}, {"size": False})
        self.assertFalse(preds[0]["met"])
        for q in preds[1:]:
            self.assertFalse(q["graded"])
            self.assertEqual(q["observed"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
