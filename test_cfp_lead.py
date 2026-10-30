#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for cfp_lead.py (no network, no data). Made with AI agents working in MV2's
(Munim, Inc.) name. Code Apache-2.0."""
import csv
import io
import unittest

import cfp_lead as L

HEADER_2021 = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin", "Origine",
               "Product", "Produit", "Organic – Biologique", "Date Sampled – Date d’échantillonage",
               "Type of test", "Type d’analyse", "Component", "Composant", "Result – Résultat",
               "Unit – Unité", "Plan Code – Code du régime"]
HEADER_2019 = ["Sample No. – No. d’échantillon", "Region - Région", "Commodity", "denrée",
               "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
               "Date Sampled – Date d’échantillonage", "Component", "Composant", "AMOUNT",
               "Report Unit - Unité de rapport"]


def row_2021(sample, product, component, value, unit="µg/g"):
    return [sample, "Import", "Importation", "CANADA", "Canada", product, "x", "No",
            "2021-01-01", "METALS", "Métaux", component, "x", value, unit, "P"]


def as_csv(rows):
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue()


def sample(sid, category, value, product="p"):
    return {"sample": sid, "product": product, "category": category,
            "kind": "det" if value > 0 else "nd", "value": value}


class TestRules(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(L.parse_value("0"), (0.0, "nd"))
        self.assertEqual(L.parse_value("0.015"), (0.015, "det"))
        self.assertEqual(L.parse_value("0,02"), (0.02, "det"))
        self.assertEqual(L.parse_value("<0.01")[1], "nd")
        self.assertEqual(L.parse_value("<0")[1], "nd")
        self.assertEqual(L.parse_value("ND")[1], "nd")
        for bad in ("", "-1", "NA", "<LOQ", "trace"):
            self.assertEqual(L.parse_value(bad)[1], "bad", bad)

    def test_is_lead(self):
        for yes in ("Lead", " lead ", "Plomb", "LEAD"):
            self.assertTrue(L.is_lead(yes), yes)
        for no in ("Lead acetate", "Leader", "Arsenic", ""):
            self.assertFalse(L.is_lead(no), no)

    def test_matches(self):
        self.assertTrue(L.matches(0.0795, "0.080"))
        self.assertTrue(L.matches(0.047, "0.05"))
        self.assertTrue(L.matches(0.00015, "0.0002"))
        self.assertFalse(L.matches(0.18, "0.018"))
        self.assertFalse(L.matches(0.0185, "0.0211"))
        self.assertFalse(L.matches(None, "0.1"))
        self.assertTrue(L.matches(0.000255, "0.000"))

    def test_stats_helpers(self):
        self.assertAlmostEqual(L.fisher_less(0, 2, 2, 2), 1 / 6, places=12)
        self.assertAlmostEqual(L.wilson(0, 160)[1], 0.02344619517150519, places=12)
        self.assertIsNone(L.wilson(0, 0))

    def test_columns(self):
        c = L.find_columns(HEADER_2021)
        self.assertEqual((c["sample"], c["component"], c["value"], c["unit"], c["product"],
                          c["origin"], c["function"]), (0, 11, 13, 14, 5, 3, 1))
        c = L.find_columns(HEADER_2019)
        self.assertEqual((c["sample"], c["component"], c["value"], c["unit"], c["product"],
                          c["origin"], c["function"]), (0, 11, 13, 14, 8, 6, 4))


class TestRegisteredFigures(unittest.TestCase):
    def test_census_totals(self):
        self.assertEqual({y: sum(p.values()) for y, p in L.PRODUCTS.items()},
                         {"2017": 51, "2018": 143, "2019": 251, "2020": 135, "2021": 291,
                          "2022": 108})

    def test_categories_match_printed_tables(self):
        for y in L.YEARS:
            by = {}
            for label, n in L.PRODUCTS[y].items():
                cat = L.CATEGORY[y][label]
                by[cat] = by.get(cat, 0) + n
            self.assertEqual(by, {c: row[0] for c, row in L.TABLE[y].items()}, y)
            for c, (n, neg, pos, _mx, _mean) in L.TABLE[y].items():
                self.assertEqual(neg + pos, n, (y, c))

    def test_text_totals_agree_with_tables(self):
        pos = {y: sum(r[2] for r in L.TABLE[y].values()) for y in L.YEARS}
        neg = {y: sum(r[1] for r in L.TABLE[y].values()) for y in L.YEARS}
        self.assertEqual(pos["2019"], L.TEXT["2019"]["det"])
        self.assertEqual(neg["2020"], L.TEXT["2020"]["nd"])
        self.assertEqual(neg["2021"], L.TEXT["2021"]["nd"])
        self.assertEqual(neg["2022"], L.TEXT["2022"]["nd"])


class TestParse(unittest.TestCase):
    def test_parse_year_2021_layout(self):
        text = as_csv([HEADER_2021,
                       row_2021("S1", "Pasta - Dry", "Lead", "0.047"),
                       row_2021("S1", "Pasta - Dry", "Arsenic", "0.2"),
                       row_2021("S2", "Fruit Purée", "Lead", "0"),
                       row_2021("S3", "Meal - Toddler/Baby", "Lead", "0.018", unit="μg/g"),
                       row_2021("S4", "Juice - Apple", "Lead", "")])
        samples, census = L.parse_year(text, "2021")
        self.assertEqual(census["rows"], 4)
        self.assertEqual(census["samples"], 4)
        self.assertEqual(census["units"], {L.MICRO_G: 4})
        self.assertEqual(census["kinds"], {"det": 2, "nd": 1, "bad": 1})
        self.assertEqual(census["bad_shapes"], [""])
        cats = {s["sample"]: s["category"] for s in samples}
        self.assertEqual(cats, {"S1": "pasta", "S2": "puree-meal", "S3": "puree-meal",
                                "S4": "juice"})
        kinds = {s["sample"]: s["kind"] for s in samples}
        self.assertEqual(kinds, {"S1": "det", "S2": "nd", "S3": "det", "S4": "bad"})

    def test_gate(self):
        census = {"columns": {k: 0 for k in L.COLS}, "rows": 51, "samples": 51,
                  "units": {L.MICRO_G: 51}, "products": {"Juice - Toddler/Infant": 51},
                  "kinds": {"nd": 49, "det": 2}}
        self.assertTrue(all(L.gate_checks(census, True, "2017").values()))
        census["units"] = {"ng/g": 51}
        g = L.gate_checks(census, True, "2017")
        self.assertFalse(g["units"])
        self.assertTrue(g["rows"] and g["products"] and g["values"])


def juice_2017():
    return ([sample(f"N{i}", "juice", 0.0) for i in range(49)]
            + [sample("D1", "juice", 0.004), sample("D2", "juice", 0.009)])


def fail_gates(passing):
    keys = ("sha256", "columns", "rows", "samples", "units", "products", "values")
    return {y: {k: y in passing for k in keys} for y in L.YEARS}


class TestGrade(unittest.TestCase):
    def test_2017_only(self):
        a = L.analyse({"2017": juice_2017()})
        rows = a["table"]["2017"]["juice"]["ok"]
        self.assertEqual(rows, {"tested": True, "negative": True, "positive": True,
                                "max": True})
        m = a["means"]["2017"]["juice"]
        self.assertTrue(m["all_matches"])
        self.assertFalse(m["positives_matches"])
        self.assertTrue(m["met"])
        preds = {p["id"]: p for p in L.grade(a, fail_gates({"2017"}))}
        self.assertFalse(preds["G"]["met"])
        self.assertTrue(preds["C2017"]["graded"] and preds["C2017"]["met"])
        self.assertFalse(preds["C2018"]["graded"])
        for pid in ("P1", "P2", "P3", "P4", "P6"):
            self.assertFalse(preds[pid]["graded"], pid)
        self.assertTrue(preds["P5"]["graded"] and preds["P5"]["met"])
        self.assertEqual(sum(1 for p in preds.values() if p["graded"]), 3)

    def test_2021_slip(self):
        s = ([sample(f"N{i}", "puree-meal", 0.0) for i in range(174)]
             + [sample("A", "puree-meal", 0.018), sample("B", "puree-meal", 0.02),
                sample("C", "puree-meal", 0.03)]
             + [sample(f"Q{i}", "pasta", 0.0) for i in range(44)]
             + [sample("P1", "pasta", 0.015), sample("P2", "pasta", 0.03),
                sample("P3", "pasta", 0.047)]
             + [sample(f"J{i}", "juice", 0.0) for i in range(67)])
        a = L.analyse({"2021": s})
        self.assertAlmostEqual(a["p1"]["puree_meal_max"], 0.03, places=12)
        self.assertFalse(a["p1"]["any_2021_value_matching_0_18"])
        self.assertEqual(a["p2"]["matching_0_018"], [0.018])
        fda = [r for r in a["fda"] if r["category"] == "puree-meal"][0]
        self.assertEqual((fda["n"], fda["above"], fda["above_0_020"]), (177, 3, 1))
        ys = a["years"]["2021"]
        self.assertEqual((ys["n"], ys["det"], ys["nd"]), (291, 6, 285))
        self.assertEqual(ys["max_category"], "pasta")
        self.assertTrue(all(a["text"]["2021"].values()))
        preds = {p["id"]: p for p in L.grade(a, fail_gates({"2021"}))}
        self.assertTrue(preds["C2021"]["met"])
        self.assertTrue(preds["P1"]["met"] and preds["P2"]["met"])
        self.assertTrue(preds["P3"]["graded"] and preds["P3"]["met"])
        # 2021 pasta all-sample mean = 0.092 / 47 = 0.00196 -> "0.002".
        self.assertTrue(a["means"]["2021"]["pasta"]["met"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
