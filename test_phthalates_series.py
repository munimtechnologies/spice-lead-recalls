#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for phthalates_series.py (no network, no CFIA file).

They check the label maps, the component names of both files, the ID-year and size-band helpers,
parsing (comma decimals, the screen row, every kind of format problem), the gate and amendment A2,
the F grades on a synthetic 599-sample population built to the printed Table 2 (all four items
hold) and on a changed copy, and the P year filter and grades on a small synthetic population.
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import datetime
import io
import unittest

import phthalates_series as ps

HEADER = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Origin",
          "Origine", "Product", "Produit", "Date Sampled – Date d’échantillonage",
          "Type of Test", "Type d’analyse", "Component", "Composant",
          "Result - Résultat", "Unit - Unité", "Plan Code - Code du régime"]
UG = "µg/g"
SCREEN0 = "0 Phthalates detected / Phtalate détecté"
SCREEN1 = "1 Phthalate detected / Phtalate détecté"


def row(sid, product, comp, value, unit, date="14-May-18", function="Domestic"):
    return [sid, function, "", "CANADA", "", product, "", date, "Phthalate", "", comp, "",
            value, unit, "2018_SRDEHP"]


def text_of(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def mk(sid, product, values, kind, date="2018-06-01", function="Domestic"):
    d = datetime.date.fromisoformat(date)
    s = {"id": sid, "product": product, "function": function, "origin": "", "date": date,
         "year": ps.pcen.survey_year(d), "id_year": ps.id_year(sid),
         "screen_n": len(values), "values": dict(values)}
    return ps.finish(s, kind)


F_POS = {"flatbread": ("Bakery Product - Bread - Other", [0.57, 15.00, 2.73] + [2.5] * 51, 208),
         "dairy_alt": ("Dairy Alternative", [0.59, 2.78, 0.9, 0.9, 0.9, 0.95], 76),
         "mayo": ("Mayonnaise - Vegan", [0.72, 1.01, 3.19], 53),
         "meat_alt": ("Meat Alternative", [0.50, 7.57, 3.2, 3.2, 3.2, 3.2, 3.28], 125),
         "tofu": ("Tofu", [0.54, 8.01, 24.00], 137)}


def f_population():
    """599 samples shaped to the printed Table 2: DINP in 51, DEHP in 22, DBP in 4, DIDP in 2,
    six samples with two phthalates."""
    out, i, n = [], 0, 0
    for _, (label, pos, size) in F_POS.items():
        for v in pos:
            if i < 4:
                vals = {"DINP": v / 2, "DBP": v / 2}
            elif i < 6:
                vals = {"DINP": v / 2, "DIDP": v / 2}
            elif i < 51:
                vals = {"DINP": v}
            else:
                vals = {"DEHP": v}
            i += 1
            n += 1
            out.append(mk(f"C2018PHTH{n:05d}", label, vals, "fv18"))
        for _ in range(size - len(pos)):
            n += 1
            out.append(mk(f"C2018PHTH{n:05d}", label, {}, "fv18"))
    return out


class TestHelpers(unittest.TestCase):
    def test_components(self):
        self.assertEqual(ps.component("Bis(2-ethylhexyl) phthalate (DEHP)"), "DEHP")
        self.assertEqual(ps.component("Bis(2-ethylhexyl) phthalate"), "DEHP")
        self.assertEqual(ps.component("Butyl Benzyl Phthalate (BBP)"), "BBP")
        self.assertEqual(ps.component("Dibutylphthalate (DBP)"), "DBP")
        self.assertEqual(ps.component("Diisononyl phthalate"), "DINP")
        self.assertEqual(ps.component("Phthalate Screen"), "SCREEN")
        self.assertIsNone(ps.component("Benzene"))

    def test_numbers(self):
        self.assertEqual(ps.number("0,54"), 0.54)
        self.assertEqual(ps.number("2,608"), 2608.0)
        self.assertEqual(ps.number("1,288.5"), 1288.5)
        self.assertEqual(ps.number("24.00"), 24.0)
        with self.assertRaises(ValueError):
            ps.number("ND")

    def test_id_year(self):
        self.assertEqual(ps.id_year("C2012PHTH00086R"), "2012-13")
        self.assertEqual(ps.id_year("C2018PHTH00652E"), "2018-19")
        self.assertIsNone(ps.id_year("X1"))

    def test_bands(self):
        self.assertEqual(ps.round_kib_band(147), (150016, 151040))
        self.assertEqual(ps.ceil_kib_band(147), (149505, 150528))
        self.assertEqual(ps.ceil_kib_band(1259), (1288193, 1289216))
        # The four portal sizes seen so far: rounding up fits all four, rounding fits two.
        known = ((149790, 147), (1288434, 1259), (117529, 115), (58972, 58))
        for size, kib in known:
            lo, hi = ps.ceil_kib_band(kib)
            self.assertTrue(lo <= size <= hi, size)
        fits_round = [s for s, k in known if ps.round_kib_band(k)[0] <= s <= ps.round_kib_band(k)[1]]
        self.assertEqual(fits_round, [117529, 58972])

    def test_maps(self):
        self.assertEqual(ps.f_sub("Bakery Product - Tortilla/Wrap/Pita"), "flatbread")
        self.assertEqual(ps.f_sub("Tofu"), "tofu")
        self.assertEqual(ps.f_sub("Soup"), "unmapped")
        cases = {"Butter - Almond": "nut_seed", "Butter": "other", "Tahini": "nut_seed",
                 "Infant Food - Cereal": "grain", "Infant Food - Snack": "other",
                 "Cereal - Adult": "grain", "Oatmeal": "grain", "Bakery Product - Bagel": "grain",
                 "Oil - Palm": "oil", "Mayonnaise": "mayo", "Salad Dressing": "dressing",
                 "Vegetable Shortening": "shortening", "Meal - Toddler/Baby": "rte",
                 "Pizza Products": "rte", "Lard": "other"}
        for label, sub in cases.items():
            self.assertEqual(ps.p_sub(label), sub, label)
        self.assertEqual(mk("C2014PHTH00001", "Oil - Palm", {}, "ps12")["group"], "fats_oils")


class TestParse(unittest.TestCase):
    def test_clean_file(self):
        text = text_of([
            row("C2018PHTH00001", "Tofu", "Phthalate Screen", SCREEN1, "n/a"),
            row("C2018PHTH00001", "Tofu", "Diisononyl phthalate", "0,54", UG),
            row("C2018PHTH00002", "Bakery Product - Bread - Other", "Phthalate Screen", SCREEN0,
                "n/a"),
        ])
        samples, problems = ps.parse(text, "fv18")
        self.assertTrue(all(not v for v in problems.values()), problems)
        by = {s["id"]: s for s in samples}
        self.assertEqual(by["C2018PHTH00001"]["values"], {"DINP": 0.54})
        self.assertEqual(by["C2018PHTH00001"]["total"], 0.54)
        self.assertEqual(by["C2018PHTH00001"]["screen_n"], 1)
        self.assertEqual(by["C2018PHTH00001"]["year"], "2018-19")
        self.assertEqual(by["C2018PHTH00001"]["date"], "2018-05-14")
        self.assertEqual(by["C2018PHTH00002"]["group"], "flatbread")
        self.assertEqual(by["C2018PHTH00002"]["total"], 0)

    def test_p_screen_unit_and_names(self):
        text = text_of([
            row("C2014PHTH00001", "Tahini", "Phthalate Screen",
                "1 Phthalate detected/phtalate détecté", "n/a / s.o.", date="09-Apr-14"),
            row("C2014PHTH00001", "Tahini", "Bis(2-ethylhexyl) phthalate (DEHP)", "1.5", UG,
                date="09-Apr-14"),
        ])
        samples, problems = ps.parse(text, "ps12")
        self.assertTrue(all(not v for v in problems.values()), problems)
        s = samples[0]
        self.assertEqual((s["values"], s["year"], s["id_year"], s["sub"]),
                         ({"DEHP": 1.5}, "2014-15", "2014-15", "nut_seed"))

    def test_problems(self):
        text = text_of([
            row("C2018PHTH00001", "Tofu", "Phthalate Screen", SCREEN1, "n/a"),
            row("C2018PHTH00001", "Tofu", "Benzene", "1.0", UG),
            row("C2018PHTH00001", "Tofu", "Diisononyl phthalate", "ND", UG),
            row("C2018PHTH00002", "Tofu", "Phthalate Screen", SCREEN1, "n/a"),
            row("C2018PHTH00002", "Tofu", "Dibutylphthalate", "1.0", "ng/g"),
            row("C2018PHTH00002", "Tofu", "Dibutylphthalate", "2.0", UG),
            row("C2018PHTH00003", "Soup", "Diisodecyl phthalate", "1.0", UG, date="x"),
            row("C2018PHTH00004", "Tofu", "Phthalate Screen", "some phthalates", "n/a"),
            row("C2018PHTH00004", "Meat Alternative", "Phthalate Screen", SCREEN0, "n/a"),
        ])
        _, p = ps.parse(text, "fv18")
        self.assertEqual(p["unknown_component"], ["C2018PHTH00001: Benzene"])
        self.assertEqual(p["non_numeric"], ["C2018PHTH00001: DINP"])
        self.assertEqual(p["bad_unit"], ["C2018PHTH00002: DBP"])
        self.assertEqual(p["repeated"], ["C2018PHTH00002: DBP"])
        self.assertEqual(p["no_screen"], ["C2018PHTH00003"])
        self.assertEqual(p["unmapped_product"], ["C2018PHTH00003: Soup"])
        self.assertEqual(p["bad_date"], ["C2018PHTH00003"])
        self.assertEqual(p["bad_screen"], ["C2018PHTH00004"])
        self.assertEqual(p["mixed_product"], ["C2018PHTH00004"])


class TestGradeF(unittest.TestCase):
    def test_population_shape(self):
        pop = f_population()
        self.assertEqual(len(pop), 599)
        self.assertEqual(len({s["id"] for s in pop}), 599)
        items = ps.census_items_f(pop)
        self.assertTrue(items["F-S1"]["held"])
        self.assertFalse(items["F-S2"]["held"])

    def test_all_hold_on_report_shaped_population(self):
        g = ps.grade_f(f_population())
        for key in ("F-V1", "F-V2", "F-V3", "F-V4"):
            self.assertTrue(g[key]["held"], (key, g[key]))
        self.assertEqual(g["F-V3"]["per_phthalate_positive_samples"],
                         {"BBP": 0, "DBP": 4, "DNOP": 0, "DEHP": 22, "DINP": 51, "DIDP": 2})
        self.assertEqual(g["F-V3"]["multi"], 6)
        self.assertEqual(g["F-V1"]["rows"]["all"]["stats"]["positives"], 73)
        self.assertAlmostEqual(g["F-V1"]["rows"]["vegan"]["stats"]["mean"], 68.64 / 19, places=5)

    def test_changed_copy(self):
        pop = f_population()
        zero_tofu = next(s for s in pop if s["sub"] == "tofu" and s["total"] == 0)
        zero_tofu["values"] = {"DEHP": 30.0}
        ps.finish(zero_tofu, "fv18")
        g = ps.grade_f(pop)
        self.assertFalse(g["F-V1"]["held"])
        self.assertFalse(g["F-V2"]["held"])
        self.assertEqual(g["F-V2"]["negatives"], 525)
        self.assertTrue(g["F-V3"]["held"])
        self.assertFalse(g["F-V4"]["held"])

    def test_gate_and_a2(self):
        pop = f_population()
        clean = {k: [] for k in ("unknown_component", "bad_unit")}
        t = ps.TARGETS["fv18"]
        g = ps.gate(149790, True, pop, clean, t)
        self.assertEqual((g["size_in_band_as_written"], g["size_in_band_A2"], g["G_as_written"],
                          g["A2"]), (False, True, False, True))
        self.assertFalse(ps.gate(149790, False, pop, clean, t)["A2"])
        self.assertFalse(ps.gate(149790, True, pop[:-1], clean, t)["A2"])
        self.assertFalse(ps.gate(149790, True, pop, {"bad_unit": ["x"]}, t)["A2"])


class TestGradeP(unittest.TestCase):
    def pop(self):
        out = [mk("C2014PHTH00001", "Butter - Almond", {"DINP": 0.5}, "ps12", date="2014-06-01"),
               mk("C2014PHTH00002", "Tahini", {}, "ps12", date="2014-07-01"),
               mk("C2015PHTH00001", "Butter - Peanut", {"DINP": 500.0}, "ps12",
                  date="2015-06-01"),
               mk("C2014PHTH00003", "Vegetable Shortening", {}, "ps12", date="2014-08-01")]
        for i, v in enumerate([2.0, 2.77, 3.54] + [0] * 22):
            vals = {"DEHP": v} if v else {}
            out.append(mk(f"C2014PHTH{100 + i:05d}", "Mayonnaise", vals, "ps12",
                          date="2015-01-15"))
        return out

    def test_year_filter_and_rows(self):
        pop = self.pop()
        g = ps.grade_p(pop)
        nut = g["P-V2"]["rows"]["nut_seed"]["stats"]
        self.assertEqual((nut["n"], nut["positives"], nut["max"]), (2, 1, 0.5))
        self.assertFalse(g["P-V2"]["held"])
        self.assertFalse(g["P-V1"]["held"])
        self.assertEqual(g["P-V1"]["stats"]["max"], 500.0)
        self.assertTrue(g["P-V4"]["held"], g["P-V4"])
        self.assertEqual(g["P-V4"]["mayo"]["n"], 25)
        fats = g["P-V3"]["rows"]["fats_oils"]["stats"]
        self.assertEqual((fats["n"], fats["positives"]), (26, 3))

    def test_names_and_readings(self):
        pop = self.pop()
        names = ps.names_p(pop)
        self.assertEqual(names["by_group_date_year"]["nut_seed"], {"2014-15": 2, "2015-16": 1})
        self.assertEqual(names["by_group_id_year"]["nut_seed"], {"2014-15": 2, "2015-16": 1})
        self.assertEqual(names["by_group_date_year"]["fats_oils"], {"2014-15": 26})
        self.assertEqual(names["id_year_vs_date_year"]["2014-15"], {"2014-15": 28})
        r = ps.p_year_stats(pop)
        self.assertEqual(r["2015-16"]["nut_seed"]["max"], 500.0)
        self.assertEqual(r["Y4"]["nut_seed"]["n"], 3)
        self.assertEqual(r["Y3_by_id"]["nut_seed"]["n"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
