#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for alternaria.py (no network, no data files).

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import unittest

import alternaria as ab

# Headers as in the two CFIA files (F1: 15 columns, F2: 18 columns).
F1_HEAD = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin", "Origine",
           "Product", "Produit", "Date Sampled – Date d’échantillonage", "Type of Test",
           "Type d’analyse", "Component", "Composant", "Result - Résultat", "Unit - Unité",
           "Plan Code - Code du Régime"]
F2_HEAD = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "denrée",
           "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
           "Date Sampled – Date d’échantillonage", "Type of Test", "Type d’analyse", "Component",
           "Composant", "MaxOfAMOUNT", "Report Unit - Unité de rapport", "PLAN_CODE"]


def f1_row(sample, origin, product, comp, value, plan):
    cols = ["x"] * 15
    cols[0], cols[3], cols[5], cols[10], cols[12], cols[13], cols[14] = (
        sample, origin, product, comp, value, "ng/g", plan)
    return ",".join(cols)


def f2_row(sample, origin, product, comp, value, unit="ppb"):
    cols = ["x"] * 18
    cols[0], cols[6], cols[8], cols[13], cols[15], cols[16], cols[17] = (
        sample, origin, product, comp, value, unit, "")
    return ",".join(cols)


A, M = ab.AOH, ab.AME
MINI_F1 = "\n".join([
    ",".join(F1_HEAD),
    f1_row("S1", "FRANCE", "Wine", A, "1.5", "2014_TS025"),
    f1_row("S1", "FRANCE", "Wine", M, "0", "2014_TS025"),
    f1_row("S2", "ITALY", "Tomato Sauce", A, "12", "2015_TS025"),
    f1_row("S2", "ITALY", "Tomato Sauce", M, "0.5", "2015_TS025"),
    f1_row("S3", "MEXICO", "Pepper (GH)", A, "0", "2020_TS025"),
    f1_row("S3", "MEXICO", "Pepper - Hot - Fresh", M, "0", "2020_TS025"),
    f1_row("S4", "UNKNOWN", "Infant Food - Puree", A, "<0.1", "2019_TS025"),
    f1_row("S4", "UNKNOWN", "Infant Food - Puree", M, "3", "2019_TS025"),
]) + "\n"

MINI_F2 = "\n".join([
    ",".join(F2_HEAD),
    f2_row("T1", "CANADA", "Beer", A, "0"),
    f2_row("T1", "CANADA", "Beer", M, "0"),
    f2_row("T2", "UNKNOWN", "Oil - Sunflower", A, "0.012", "ppm"),
    f2_row("T2", "UNKNOWN", "Oil - Sunflower", M, "0", "ppm"),
    f2_row("T3", "TURKEY", "Juice - Pomegranate", A, "50"),
    f2_row("T3", "TURKEY", "Juice - Pomegranate", M, "2"),
    f2_row("T4", "CANADA", "Juice - Orange", A, "ND"),
    f2_row("T4", "CANADA", "Juice - Orange", M, ""),
]) + "\n"


class TestParseAmount(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(ab.parse_amount(""), (0.0, False, "blank"))
        self.assertEqual(ab.parse_amount("<0.1"), (0.0, False, "lt"))
        self.assertEqual(ab.parse_amount("ND"), (0.0, False, "nd"))
        self.assertEqual(ab.parse_amount("0"), (0.0, False, "zero"))
        self.assertEqual(ab.parse_amount("0.000"), (0.0, False, "zero"))
        self.assertEqual(ab.parse_amount("0,5"), (None, False, "comma"))
        self.assertEqual(ab.parse_amount("trace"), (None, False, "bad"))
        self.assertEqual(ab.parse_amount("-1"), (None, False, "bad"))
        self.assertEqual(ab.parse_amount("0.046"), (0.046, True, "pos"))


class TestPrecision(unittest.TestCase):
    def test_tolerance(self):
        self.assertAlmostEqual(ab.tolerance("0.090"), 0.0005, places=12)
        self.assertAlmostEqual(ab.tolerance("5.7"), 0.05, places=12)
        self.assertAlmostEqual(ab.tolerance("37"), 0.5, places=12)
        self.assertAlmostEqual(ab.tolerance("573"), 0.5, places=12)
        self.assertAlmostEqual(ab.tolerance("870"), 5.0, places=12)
        self.assertAlmostEqual(ab.tolerance("200"), 5.0, places=12)
        self.assertAlmostEqual(ab.tolerance("20"), 0.5, places=12)
        self.assertAlmostEqual(ab.tolerance("0"), 0.5, places=12)

    def test_matches(self):
        self.assertTrue(ab.matches(871.0, "870"))
        self.assertTrue(ab.matches(875.0, "880"))
        self.assertFalse(ab.matches(864.0, "870"))
        self.assertTrue(ab.matches(0.0904, "0.090"))
        self.assertFalse(ab.matches(0.0906, "0.090"))
        self.assertTrue(ab.matches(572.6, "573"))
        self.assertFalse(ab.matches(570.0, "573"))
        self.assertFalse(ab.matches(None, "1.0"))


class TestCategories(unittest.TestCase):
    def test_f1(self):
        cases = {
            ("Seed - Sunflower", "2017"): "sunseed_2017",
            ("Oil - Sunflower", "2017"): "sunoil_2017",
            ("Couscous", "2017"): "wheat_2017",
            ("Couscous", "2021"): "wheat_sorghum_2021",
            ("Grain - Barley", "2021"): "barley_2021",
            ("Cereal - Mixed Grains", "2020"): "corn_2020",
            ("Vegetable Products", "2020"): "processed_pepper_2020",
            ("Snack Bar", "2020"): "rice_wheat_nutseed_2020",
            ("Pepper (GH)", "2020"): "fresh_pepper_2020",
            ("Juice - Blend", "2019"): "pomegranate_2019",
            ("Infant Food (non-cereal)", "2019"): "meal_2019",
            ("Infant Food - Puree", "2016"): "puree_2016",
            ("Juice - Blend", "2015"): "juice_pom_2014_15",
            ("Tomato", "2016"): "tomato_2016",
            ("Tomato - Organic", "2015"): "tomato_2015",
            ("Mixed Fruit", "2016"): "fruit_2016",
            ("Wine", "2015"): "wine_2015",
        }
        for (product, year), cat in cases.items():
            self.assertEqual(ab.f1_category(product, year), cat, (product, year))

    def test_f2(self):
        self.assertEqual(ab.f2_category("Seed - Chia"), "f2_seed")
        self.assertEqual(ab.f2_category("Oil - Canola"), "f2_oil")
        self.assertEqual(ab.f2_category("Cider - Apple"), "f2_juice")
        self.assertEqual(ab.f2_category("juice - pineapple"), "f2_juice")
        self.assertEqual(ab.f2_category("Beer"), "f2_beer")
        self.assertEqual(ab.f2_category("Juice - Pomegranate"), "f2_pomegranate_juice")


class TestParsing(unittest.TestCase):
    def test_f1(self):
        samples, census = ab.parse_text(MINI_F1, "F1")
        self.assertEqual(census["n_rows"], 8)
        self.assertEqual(census["distinct_samples"], 4)
        self.assertEqual(census["components"], {A: 4, M: 4})
        self.assertEqual(census["rows_per_sample"], {"2": 4})
        self.assertTrue(census["one_of_each"])
        self.assertEqual(census["units"], {"ng/g": 8})
        self.assertEqual(census["amount_kinds"], {"pos": 4, "zero": 3, "lt": 1})
        self.assertEqual(census["products"], {"Wine": 2, "Tomato Sauce": 2, "Pepper (GH)": 1,
                                              "Pepper - Hot - Fresh": 1,
                                              "Infant Food - Puree": 2})
        self.assertEqual(census["plans"], {"2014_TS025": 2, "2015_TS025": 2, "2020_TS025": 2,
                                           "2019_TS025": 2})
        self.assertEqual(samples["S1"]["category"], "wine_2014")
        self.assertAlmostEqual(samples["S1"]["total"], 1.5, places=12)
        self.assertEqual(samples["S2"]["category"], "tomato_2015")
        self.assertAlmostEqual(samples["S2"]["total"], 12.5, places=12)
        self.assertEqual(samples["S3"]["category"], "fresh_pepper_2020")
        self.assertEqual(samples["S3"]["labels"], {"Pepper (GH)", "Pepper - Hot - Fresh"})
        self.assertEqual(samples["S3"]["total"], 0.0)
        self.assertEqual(samples["S4"]["category"], "puree_2019")
        self.assertEqual((samples["S4"]["aoh"], samples["S4"]["ame"]), (0.0, 3.0))
        self.assertEqual(samples["S4"]["origin"], "UNKNOWN")

    def test_f2_units_and_tokens(self):
        samples, census = ab.parse_text(MINI_F2, "F2")
        self.assertEqual(census["n_rows"], 8)
        self.assertEqual(census["units"], {"ppb": 6, "ppm": 2})
        self.assertEqual(census["amount_kinds"], {"zero": 3, "pos": 3, "nd": 1, "blank": 1})
        self.assertTrue(census["one_of_each"])
        self.assertEqual(samples["T1"]["category"], "f2_beer")
        self.assertEqual(samples["T2"]["category"], "f2_oil")
        self.assertAlmostEqual(samples["T2"]["aoh"], 12.0, places=9)   # 0.012 ppm -> ng/g
        self.assertEqual(samples["T3"]["category"], "f2_pomegranate_juice")
        self.assertAlmostEqual(samples["T3"]["total"], 52.0, places=12)
        self.assertEqual(samples["T4"]["category"], "f2_juice")
        self.assertEqual(samples["T4"]["total"], 0.0)

    def test_missing_component_breaks_one_of_each(self):
        text = "\n".join([",".join(F1_HEAD),
                          f1_row("S1", "CANADA", "Wine", A, "1", "2014_TS025"),
                          f1_row("S1", "CANADA", "Wine", A, "2", "2014_TS025")]) + "\n"
        _, census = ab.parse_text(text, "F1")
        self.assertFalse(census["one_of_each"])


def rec(total, aoh=None, ame=0.0, cat="x", product="p", origin="CANADA"):
    aoh = total - ame if aoh is None else aoh
    return {"total": total, "aoh": aoh, "ame": ame, "category": cat, "product": product,
            "origin": origin}


class TestStatistics(unittest.TestCase):
    def test_row_stats_and_check(self):
        recs = [rec(0.0), rec(0.5), rec(2.0), rec(3.5)]
        st = ab.row_stats(recs)
        self.assertEqual((st["n"], st["pos"], st["min"], st["max"]), (4, 3, 0.5, 3.5))
        self.assertAlmostEqual(st["avg"], 2.0, places=12)
        ok, _ = ab.check_row(st, 4, 3, "0.50", "3.5", "2.0")
        self.assertTrue(ok)
        ok, detail = ab.check_row(st, 4, 3, "0.51", "3.5", "2.0")
        self.assertFalse(ok)
        self.assertFalse(detail["min"][2])
        ok, _ = ab.check_row(st, 4, 3, None, "3.5", None)
        self.assertTrue(ok)

    def test_all_zero_row(self):
        st = ab.row_stats([rec(0.0), rec(0.0)])
        self.assertEqual((st["pos"], st["min"], st["max"], st["avg"]), (0, None, 0.0, None))
        self.assertTrue(ab.check_row(st, 2, 0, None, "0", None)[0])
        st = ab.row_stats([rec(0.0), rec(0.1)])
        self.assertFalse(ab.check_row(st, 2, 0, None, "0", None)[0])

    def test_exceeds_and_share(self):
        self.assertFalse(ab.exceeds({"aoh": 10.0, "ame": 5.0}, (10.0, 5.0)))
        self.assertTrue(ab.exceeds({"aoh": 10.01, "ame": 0.0}, (10.0, 5.0)))
        self.assertTrue(ab.exceeds({"aoh": 0.0, "ame": 5.2}, (10.0, 5.0)))
        recs = [{"aoh": 3.0, "ame": 1.0}, {"aoh": 0.0, "ame": 0.0}]
        self.assertAlmostEqual(ab.aoh_share(recs), 0.75, places=12)
        self.assertEqual(ab.count_exceed(recs, (2.0, 2.0)), 1)
        self.assertIsNone(ab.aoh_share([{"aoh": 0.0, "ame": 0.0}]))

    def test_analyse_small(self):
        s1, _ = ab.parse_text(MINI_F1, "F1")
        s2, _ = ab.parse_text(MINI_F2, "F2")
        a = ab.analyse(list(s1.values()), list(s2.values()))
        self.assertEqual(a["f1_top"]["category"], "tomato_2015")
        self.assertAlmostEqual(a["f1_top"]["total"], 12.5, places=12)
        self.assertEqual(a["eu"]["tomato_exceed"], 1)        # AOH 12 > 10
        self.assertEqual(a["eu"]["sunoil_n"], 1)             # the F2 sunflower oil
        self.assertEqual(a["eu"]["sunoil_exceed"], 1)        # 12 ng/g AOH > 10
        self.assertEqual(a["eu"]["puree_over_2"], 1)         # AME 3 > 2
        self.assertEqual(a["f2_beer"]["n"], 1)
        self.assertEqual(a["f2_pomegranate_juice"]["pos"], 1)
        self.assertFalse(a["rows"]["C1"]["ok"])              # n 1, not 79
        self.assertIn("wine_2014", a["categories"])


def fake_analysis():
    return {
        "rows": {r[0]: {"text": r[1], "ok": True, "detail": {}} for r in ab.ROWS},
        "c17": {k: {"ok": True, "detail": {}} for k in ("seeds", "oils", "overall")},
        "infant_all": {"n": 258, "pos": 197, "min": 0.1, "max": 37.0, "avg": 5.05},
        "pomegranate_2019_canada": 10, "pomegranate_2019_n": 187,
        "pomegranate_2019_max": 871.0,
        "f1_top": {"total": 880.0, "category": "tomato_2015", "product": "Tomato",
                   "plan": "2015_TS025"},
        "tomato_2015": {"n": 100, "pos": 36, "min": 0.08, "max": 880.0, "avg": 25.0},
        "f1_overall": {"n": 2595, "pos": 1553, "min": 0.046, "max": 880.0, "avg": 23.0},
        "f2_beer": {"n": 80, "pos": 16, "min": 0.1, "max": 2.0, "avg": 0.5},
        "f2_pomegranate_juice": {"n": 5, "pos": 5, "min": 1.0, "max": 500.0, "avg": 100.0},
        "eu": {"tomato_n": 200, "tomato_exceed": 2, "tomato_aoh_over": 2, "tomato_ame_over": 2,
               "sunseed_n": 51, "sunseed_exceed": 0, "sesame_n": 3, "sesame_exceed": 0,
               "sunoil_n": 51, "sunoil_exceed": 4, "sunoil_aoh_over": 3, "sunoil_ame_over": 2,
               "sunflower_aoh_share": 0.4, "fruit_aoh_share": 0.7, "puree_n": 166,
               "puree_over_2": 70},
        "categories": {},
    }


OPEN_GATE = {k: True for k in (
    "f1_sha256", "f1_rows", "f1_samples", "f1_rows_per_sample", "f1_one_aoh_one_ame",
    "f1_components", "f1_products", "f1_plans", "f1_unit", "f1_value_format", "f2_sha256",
    "f2_rows", "f2_samples", "f2_rows_per_sample", "f2_one_aoh_one_ame", "f2_components",
    "f2_products", "f2_units_known", "f2_value_format")}


class TestGrading(unittest.TestCase):
    def test_all_met(self):
        preds = ab.grade(fake_analysis(), OPEN_GATE)
        ids = ["G"] + [f"C{i}" for i in range(1, 18)] + [f"P{i}" for i in range(1, 7)] \
            + [f"E{i}" for i in range(1, 6)]
        self.assertEqual([p["id"] for p in preds], ids)
        self.assertTrue(all(p["met"] for p in preds), [p["id"] for p in preds if not p["met"]])

    def test_misses(self):
        a = fake_analysis()
        a["infant_all"] = dict(a["infant_all"], max=26.0)
        a["pomegranate_2019_canada"] = 156
        a["pomegranate_2019_max"] = 870.0
        a["eu"] = dict(a["eu"], sunflower_aoh_share=0.6, tomato_exceed=5)
        a["rows"]["C10"] = dict(a["rows"]["C10"], ok=False)
        preds = {p["id"]: p for p in ab.grade(a, OPEN_GATE)}
        for pid in ("P1", "P2", "P3", "E1", "E4", "C10"):
            self.assertFalse(preds[pid]["met"], pid)
        for pid in ("P4", "P5", "P6", "E2", "E3", "E5", "C9", "C17"):
            self.assertTrue(preds[pid]["met"], pid)

    def test_gate_closed_grades_nothing(self):
        preds = ab.grade(fake_analysis(), dict(OPEN_GATE, f2_value_format=False))
        self.assertFalse(preds[0]["met"])
        self.assertTrue(all(not p["graded"] and not p["met"] for p in preds[1:]))


class TestGate(unittest.TestCase):
    def _censuses(self):
        c1 = {"n_rows": 5190, "distinct_samples": 2595, "rows_per_sample": {"2": 2595},
              "one_of_each": True, "components": {A: 2595, M: 2595},
              "products": dict(ab.F1_PRODUCT_ROWS), "plans": dict(ab.F1_PLAN_ROWS),
              "units": {"ng/g": 5190}, "amount_kinds": {"pos": 3000, "zero": 2190}}
        c2 = {"n_rows": 798, "distinct_samples": 399, "rows_per_sample": {"2": 399},
              "one_of_each": True, "components": {A: 399, M: 399},
              "products": dict(ab.F2_PRODUCT_ROWS), "plans": {"": 798},
              "units": {"ppb": 798}, "amount_kinds": {"pos": 400, "zero": 398}}
        return c1, c2

    def test_open(self):
        c1, c2 = self._censuses()
        checks = ab.gate_checks(c1, c2, True, True)
        self.assertEqual(set(checks), set(OPEN_GATE))
        self.assertTrue(all(checks.values()), [k for k, v in checks.items() if not v])

    def test_failures(self):
        c1, c2 = self._censuses()
        c1["amount_kinds"] = {"pos": 3000, "zero": 2189, "comma": 1}
        c2["units"] = {"furlongs": 798}
        checks = ab.gate_checks(c1, c2, True, False)
        self.assertFalse(checks["f1_value_format"])
        self.assertFalse(checks["f2_units_known"])
        self.assertFalse(checks["f2_sha256"])
        self.assertTrue(checks["f1_products"])

    def test_census_tables_add_up(self):
        self.assertEqual(sum(ab.F1_PRODUCT_ROWS.values()), 5190)
        self.assertEqual(sum(ab.F1_PLAN_ROWS.values()), 5190)
        self.assertEqual(sum(ab.F2_PRODUCT_ROWS.values()), 798)
        self.assertEqual(len(ab.F2_PRODUCT_ROWS), 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
