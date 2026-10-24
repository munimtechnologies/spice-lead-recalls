# SPDX-License-Identifier: Apache-2.0
"""Offline tests for ota_foods 0.1.0 (no network, synthetic rows only)."""
import csv
import io
import os
import tempfile
import unittest
from unittest import mock

import ota_foods as of

D = "–"
HEADER = ["Sample No. %s No. d’échantillon" % D, "Function", "Fonction", "Origin",
          "Origine", "Product", "Produit", "Date Sampled %s Date d’échantillonage" % D,
          "Type of Test", "Type d’analyse", "Component", "Composant",
          "Result %s Résultat" % D, "Unit %s Unité" % D,
          "Plan Code %s Code du Régime" % D]

# (product, plan, result)
SYNTH = [
    ("Infant Food - Cereal", "2013_SB447", "0.6"),
    ("Infant Food - Cereal", "2013_SB447", "0.4"),
    ("Infant Food - Cereal", "2013_SB447", "<0.04"),
    ("Bran - Wheat", "2012_SB447", "5"),
    ("Bran - Wheat", "2012_SB447", "8"),
    ("Flour - Wheat", "2012_SB447", "4"),
    ("Grain - Oat", "2013_SB447", "3.5"),
    ("Cereal - Adult", "2012_SB447", "2.5"),
    ("Coffee - Ground", "2015_SB447", "9.1"),
    ("Coffee", "2013_SB447", "11"),
    ("Coffee - Instant", "2013_SB447", "6"),
    ("Beverage - Coffee", "2019_SB447", "ND"),
    ("Dried mixes", "2012_SB447", "0"),
    ("Dried mixes", "2013_SB447", "0.1"),
    ("Infant Formula - Soy", "2012_SB447", "0.89"),
    ("Infant Formula - Dairy", "2012_SB447", "<0.04"),
    ("Spice - Paprika", "2014_SB447", "1770"),
    ("Cocoa Powder", "2014_SB447", "3.5"),
    ("Fig", "2015_SB447", "9"),
    ("Apricot", "2015_SB447", "2.5"),
    ("Raisin", "2015_SB447", "12"),
    ("Licorice Products", "2014_SB447", "11"),
    ("Seed - Sunflower", "2016_SB447", "6"),
    ("Tofu", "2012_SB447", ""),
]


def synth_text():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for i, (product, plan, result) in enumerate(SYNTH):
        w.writerow([f"S{i}", "Import", "Importé", "CANADA", "CANADA", product, "x",
                    "2013-01-01", "OCHRATOXIN", "OCHRATOXINE", "Ochratoxin A", "Ochratoxine A",
                    result, "ng/g", plan])
    return buf.getvalue()


class TestParse(unittest.TestCase):
    def test_non_detects(self):
        self.assertEqual(of.parse_result("<0.04"), (0.0, False, "lt"))
        self.assertEqual(of.parse_result("ND"), (0.0, False, "nd_token"))
        self.assertEqual(of.parse_result("n.d."), (0.0, False, "nd_token"))
        self.assertEqual(of.parse_result(""), (0.0, False, "blank"))
        self.assertEqual(of.parse_result("   "), (0.0, False, "blank"))
        self.assertEqual(of.parse_result(None), (0.0, False, "blank"))
        self.assertEqual(of.parse_result("0"), (0.0, False, "zero"))
        self.assertEqual(of.parse_result("0.000"), (0.0, False, "zero"))

    def test_detects_and_bad(self):
        self.assertEqual(of.parse_result("0.89"), (0.89, True, "positive"))
        self.assertEqual(of.parse_result(" 1770 "), (1770.0, True, "positive"))
        self.assertEqual(of.parse_result("0,5"), (0.5, True, "positive_comma"))
        self.assertEqual(of.parse_result("abc"), (None, False, "bad"))
        self.assertEqual(of.parse_result("-1"), (None, False, "bad"))
        self.assertEqual(of.parse_result("1,2,3"), (None, False, "bad"))
        self.assertEqual(of.parse_result("nan"), (None, False, "bad"))


class TestCategories(unittest.TestCase):
    def test_examples(self):
        cases = {("Dried mixes", "2012_SB447"): "soy", ("Dried mixes", "2013_SB447"): "coffee",
                 ("Spice - Paprika", ""): "spices", ("spice - fennel", ""): "spices",
                 ("Pepper", ""): "spices", ("Celery", ""): "spices",
                 ("Herb - Cilantro - Dried", ""): "spices", ("Bean - Soy", ""): "soy",
                 ("Bean - Kidney", ""): "pulses", ("Infant Food - Cereal", ""): "grain",
                 ("Infant Formula - Dairy", ""): "infant_formula", ("Nut - PINE NUT", ""): "nuts",
                 ("Seed - other", ""): "seeds", ("Plantain", ""): "dried_fruit",
                 ("Arrowroot Products", ""): "grain", ("Cocoa Powder", ""): "cocoa",
                 ("Licorice Products", ""): "licorice", ("Beverage - Coffee", ""): "coffee"}
        for (product, plan), want in cases.items():
            self.assertEqual(of.category(product, plan), want, product)

    def test_registered_sizes(self):
        self.assertEqual(sum(of.EXPECTED_N.values()), 8384)
        self.assertEqual(sum(v[0] for v in of.PRINTED.values()), 8384)
        self.assertEqual(set(of.EXPECTED_N), set(of.CATEGORIES))
        self.assertEqual(set(of.PRINTED), set(of.CATEGORIES))
        for c in of.EXACT:
            self.assertEqual(of.EXPECTED_N[c], of.PRINTED[c][0], c)
        for c in of.C2_CATS + of.V1_CATS + of.V2_CATS:
            self.assertIn(c, of.EXACT)

    def test_label_lists_disjoint(self):
        seen = {}
        for name, labels in of.CATEGORY_LABELS:
            for lab in labels:
                self.assertNotIn(lab, seen, lab)
                self.assertFalse(lab.lower().startswith("spice"), lab)
                seen[lab] = name
        for lab in of.SPICE_EXTRA:
            self.assertNotIn(lab, seen)


class TestEUGroups(unittest.TestCase):
    def test_groups_disjoint_and_in_categories(self):
        want = {"infant_cereal": {"grain"}, "breakfast_cereal": {"grain"},
                "bakery_snacks": {"grain"}, "oat": {"grain"}, "wheat": {"grain"},
                "roasted_coffee": {"coffee"}, "instant_coffee": {"coffee"},
                "cocoa_powder": {"cocoa"}, "licorice": {"licorice"},
                "dried_vine_fruit": {"dried_fruit"}, "fig": {"dried_fruit"},
                "other_dried_fruit": {"dried_fruit"},
                "pistachio_seeds_soybean": {"nuts", "seeds", "soy"}}
        seen = set()
        for gid, _, labels, level in of.EU_GROUPS:
            self.assertGreater(level, 0)
            cats = {of.category(lab, "2013_SB447") for lab in labels}
            self.assertTrue(cats <= want[gid], (gid, cats))
            for lab in labels:
                self.assertNotIn(lab, seen, lab)
                seen.add(lab)
        self.assertEqual(set(want), set(of.EU_LEVEL))

    def test_levels(self):
        self.assertEqual(of.EU_LEVEL["infant_cereal"], 0.5)
        self.assertEqual(of.EU_LEVEL["roasted_coffee"], 3.0)
        self.assertEqual(of.EU_LEVEL["instant_coffee"], 5.0)
        self.assertEqual(of.EU_LEVEL["bakery_snacks"], 2.0)
        self.assertEqual(of.EU_LEVEL["dried_vine_fruit"], 8.0)
        self.assertEqual(of.hc_limit("Infant Food - Cereal"), 0.5)
        self.assertEqual(of.hc_limit("Bran - Wheat"), 7.0)
        self.assertEqual(of.hc_limit("Pasta - Dry"), 3.0)


class TestMatching(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(of.matches(0.96, "0.96"))
        self.assertTrue(of.matches(0.9649, "0.96"))
        self.assertFalse(of.matches(0.9651, "0.96"))
        self.assertTrue(of.matches(11.4, "11"))
        self.assertFalse(of.matches(11.6, "11"))
        self.assertTrue(of.matches(0.0704, "0.070"))
        self.assertTrue(of.matches(3.04, "3.0"))
        self.assertFalse(of.matches(None, "1"))

    def test_verdict(self):
        self.assertEqual(of.verdict(0.96, 0.23, "0.96"), "positives")
        self.assertEqual(of.verdict(1.44, 1.30, "1.3"), "all")
        self.assertEqual(of.verdict(1.0, 1.0, "1.0"), "both")
        self.assertEqual(of.verdict(None, None, "1"), "neither")

    def test_within(self):
        self.assertTrue(of.within(0, (0, 18)))
        self.assertTrue(of.within(18, (0, 18)))
        self.assertFalse(of.within(19, (0, 18)))
        self.assertFalse(of.within(None, (0, 18)))


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.rows, self.check = of.parse_text(synth_text())

    def test_parse_and_census(self):
        self.assertEqual(self.check["n_rows"], 24)
        self.assertEqual(self.check["distinct_samples"], 24)
        self.assertEqual(self.check["units"], {"ng/g": 24})
        self.assertEqual(self.check["components"], {"Ochratoxin A": 24})
        self.assertEqual(self.check["result_kinds"],
                         {"positive": 19, "lt": 2, "nd_token": 1, "zero": 1, "blank": 1})
        self.assertEqual(of.category_counts(self.rows),
                         {"grain": 8, "coffee": 5, "soy": 2, "infant_formula": 2, "spices": 1,
                          "cocoa": 1, "dried_fruit": 3, "licorice": 1, "seeds": 1})

    def test_stats(self):
        s = of.stats(of.in_category(self.rows, "infant_formula"))
        self.assertEqual((s["n"], s["n_detected"]), (2, 1))
        self.assertAlmostEqual(s["max"], 0.89)
        self.assertAlmostEqual(s["mean_positives"], 0.89)
        self.assertAlmostEqual(s["mean_all"], 0.445)

    def test_health_canada(self):
        hc = of.hc_table(self.rows)
        self.assertEqual((hc["n_grain"], hc["n_over"], hc["infant_cereal"], hc["wheat_bran"],
                          hc["other_grain"]), (8, 4, 1, 1, 2))
        self.assertEqual(hc["vine_fruit_over_10"], 1)

    def test_eu(self):
        eu = of.eu_table(self.rows)
        got = {g: (eu[g]["n"], eu[g]["n_over"]) for g in eu}
        self.assertEqual(got["infant_cereal"], (3, 1))
        self.assertEqual(got["wheat"], (3, 3))
        self.assertEqual(got["oat"], (1, 1))
        self.assertEqual(got["breakfast_cereal"], (1, 0))
        self.assertEqual(got["bakery_snacks"], (0, 0))
        self.assertIsNone(eu["bakery_snacks"]["share_over"])
        self.assertEqual(got["roasted_coffee"], (2, 2))
        self.assertEqual(got["instant_coffee"], (1, 1))
        self.assertEqual(got["cocoa_powder"], (1, 1))
        self.assertEqual(got["licorice"], (1, 1))
        self.assertEqual(got["dried_vine_fruit"], (1, 1))
        self.assertEqual(got["fig"], (1, 1))
        self.assertEqual(got["other_dried_fruit"], (1, 1))
        self.assertEqual(got["pistachio_seeds_soybean"], (1, 1))

    def test_gate_fails_on_synthetic(self):
        preds, _, _, _ = of.grade(self.rows, self.check, True)
        ids = [p["id"] for p in preds]
        self.assertEqual(ids, ["G", "C1", "C2", "C3", "C4", "C5", "C6", "V1", "V2"]
                         + [f"P{i}" for i in range(1, 13)])
        self.assertFalse(preds[0]["met"])
        self.assertTrue(preds[0]["observed"]["checks"]["known_spice_max"])
        self.assertTrue(preds[0]["observed"]["checks"]["all_parsed"])
        self.assertFalse(preds[0]["observed"]["checks"]["rows"])
        self.assertTrue(all(not p["graded"] and not p["met"] for p in preds[1:]))

    def test_grades_when_gate_open(self):
        opened = (True, {"checks": {}, "categories": {}, "result_kinds": {}})
        with mock.patch.object(of, "gate", return_value=opened):
            preds, _, _, _ = of.grade(self.rows, self.check, True)
        met = {p["id"]: p["met"] for p in preds}
        self.assertTrue(all(p["graded"] for p in preds))
        self.assertEqual(met, {"G": True, "C1": False, "C2": False, "C3": False, "C4": False,
                               "C5": False, "C6": False, "V1": False, "V2": False,
                               "P1": False, "P2": True, "P3": False, "P4": False, "P5": False,
                               "P6": True, "P7": False, "P8": True, "P9": False, "P10": True,
                               "P11": False, "P12": True})

    def test_outputs(self):
        preds, ct, eu, hc = of.grade(self.rows, self.check, False)
        desc = of.descriptive(self.rows, self.check)
        self.assertEqual(desc["breakfast_cereal_over_2"], 1)
        self.assertEqual(desc["non_spice"], {"n": 23, "n_detected": 18})
        with tempfile.TemporaryDirectory() as tmp:
            res = of.write_outputs(tmp, self.rows, preds, ct, eu, hc, desc, {"sha256": "x"})
            self.assertEqual(res["n_met"], 0)
            for name in ("ota_foods_categories.csv", "ota_foods_eu.csv",
                         "ota_foods_samples.csv", "ota_foods_summary.json",
                         "ota_foods_grades.json"):
                self.assertTrue(os.path.exists(os.path.join(tmp, name)), name)
            with open(os.path.join(tmp, "ota_foods_samples.csv"), encoding="utf-8") as fh:
                lines = list(csv.reader(fh))
            self.assertEqual(len(lines), 24)
            self.assertEqual(lines[0], of.SAMPLE_FIELDS)


if __name__ == "__main__":
    unittest.main()
