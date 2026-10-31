# SPDX-License-Identifier: Apache-2.0
"""Offline tests for bpa_2018_2020.py (no network, no CFIA data). Made with AI agents working in
MV2's (Munim, Inc.) name."""
import csv
import io
import unittest

import bpa_2018_2020 as g

HEADER_2018 = ["Sample No. – No. d’échantillon", "Region - Région",
               "Commodity", "Denrée", "Function", "Fonction", "Origin", "Origine",
               "Product", "Produit", "Date Sampled – Date d’échantillonage",
               "Type of Test", "Type d’analyse", "Component", "Composant", "MaxOfAMOUNT",
               "Report Unit - Unité de rapport", "PLAN_CODE"]
HEADER_2020 = ["Sample No. – No. d’échantillon", "Region - Région",
               "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
               "Date Sampled – Date d’échantillonage", "Type of Test",
               "Type d’analyse", "Component", "Composant", "Result - Résultat",
               "Report Unit - Unité de rapport", "Plan Code - Code du régime"]
UG = "µg/g"

# Per-label sample counts from the published names-only census files.
CENSUS_2018 = {"Coconut Milk": 49, "Infant Formula - Dairy": 104, "Infant Formula - Other": 31,
               "Pie Filling - Blueberry": 30, "Pie Filling - Cherry": 30,
               "Pie Filling - Other": 12, "Pie Filling - Pumpkin": 26, "Sauces": 91,
               "Tomato Sauce": 4}
CENSUS_2020 = {"Apricot": 2, "Artichoke Heart": 8, "Bean - Green/Yellow": 8, "Bean - Kidney": 1,
               "Bean - Pinto": 1, "Beet": 1, "Carrot": 2, "Cherry": 3, "Corn": 7,
               "Cranberry": 2, "Fish/Seafood - Canned": 101, "Grapefruit": 1, "JackFruit": 1,
               "Lentil": 2, "Lychee": 1, "Mango": 3, "Meat - Canned": 100, "Mixed Fruit": 4,
               "Mixed Vegetables": 4, "Mushroom": 8, "Mushroom - Shiitake": 2, "Orange": 4,
               "Pea": 8, "Peach": 11, "Pear": 6, "Pie Filling - Blueberry": 9,
               "Pie Filling - Cherry": 12, "Pie Filling - Other": 10,
               "Pie Filling - Pumpkin": 11, "Pie Filling - apple": 7, "Pineapple": 14,
               "Soup": 2, "Sprout - Bean": 1, "Vegetable Products": 44, "Water Chestnut": 1}


def rows_2020(sample, function, product, values):
    """Four 2020-style rows for one sample; values in ug/g, in COMPONENTS order."""
    return [[sample, "ONTARIO", function, "", "THAILAND", "", product, "", "2020-05-01", "BPA",
             "", comp, "", v, UG, "2020_SB451"] for comp, v in zip(g.COMPONENTS, values)]


def to_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def sample(sid, typ, function, bpa=0.0, badge=0.0, bpf=0.0, bps=0.0):
    return {"sample": sid, "product": typ, "type": typ, "function": function, "origin": "",
            "region": "", "ppb": {"bpa": bpa, "badge": badge, "bpf": bpf, "bps": bps}}


class TestColumns(unittest.TestCase):
    def test_2018_header(self):
        c = g.find_columns(HEADER_2018)
        self.assertEqual((c["sample"], c["region"], c["function"], c["origin"], c["product"]),
                         (0, 1, 4, 6, 8))
        self.assertEqual((c["component"], c["value"], c["unit"], c["plan"]), (13, 15, 16, 17))

    def test_2020_header(self):
        c = g.find_columns(HEADER_2020)
        self.assertEqual((c["sample"], c["region"], c["function"], c["origin"], c["product"]),
                         (0, 1, 2, 4, 6))
        self.assertEqual((c["component"], c["value"], c["unit"], c["plan"]), (11, 13, 14, 15))


class TestLabelMaps(unittest.TestCase):
    def totals(self, name, counts):
        out = {}
        for label, n in counts.items():
            t = g.TYPE_OF[name][label]
            out[t] = out.get(t, 0) + n
        return out

    def test_2018_map_gives_tables_1_and_2(self):
        self.assertEqual(self.totals("bpa-2018", CENSUS_2018),
                         {"coconut": 49, "formula": 135, "pie": 98, "sauces": 95})
        self.assertEqual(set(g.TYPE_OF["bpa-2018"]), set(CENSUS_2018))

    def test_2020_map_gives_table_1(self):
        self.assertEqual(self.totals("bpa-2020", CENSUS_2020),
                         {"fish": 101, "fruit": 52, "meat": 100, "pie": 49, "veg": 100})
        self.assertEqual(set(g.TYPE_OF["bpa-2020"]), set(CENSUS_2020))

    def test_printed_rows_add_up(self):
        for name in g.NAMES:
            rows = g.TABLE2[name]
            self.assertEqual(sum(rows[t][0] for t in g.TYPES[name]), rows["all"][0])
            self.assertEqual(sum(rows[t][1] for t in g.TYPES[name]), rows["all"][1])
        self.assertEqual({k: sum(r[0] for r in v.values()) for k, v in g.ALT_2020.items()},
                         g.ALT_TOTALS_2020)


class TestValues(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(g.parse_value("0"), (0.0, "nd"))
        self.assertEqual(g.parse_value("0.00142"), (0.00142, "det"))
        self.assertEqual(g.parse_value("<0.001"), (0.0, "nd"))
        self.assertEqual(g.parse_value("ND"), (0.0, "nd"))
        self.assertEqual(g.parse_value(""), (None, "bad"))
        self.assertEqual(g.parse_value("-1"), (None, "bad"))
        self.assertEqual(g.parse_value("trace"), (None, "bad"))

    def test_matches(self):
        self.assertTrue(g.matches(9.165, "9.17"))
        self.assertFalse(g.matches(9.16, "9.17"))
        self.assertTrue(g.matches(366.6, "367"))
        self.assertFalse(g.matches(None, "1"))
        self.assertTrue(g.matches(0.00092 * 1000, "0.92"))

    def test_stats_and_row(self):
        st = g.stats([0.0, 1.0, 3.0])
        self.assertEqual((st["n"], st["k"], st["min"], st["max"]), (3, 2, 1.0, 3.0))
        self.assertAlmostEqual(st["mean"], 2.0)
        self.assertAlmostEqual(st["pct"], 200 / 3)
        self.assertEqual(g.check_row((3, 2, "1.0", "3.0", "2.0"), st),
                         {"n": True, "detected": True, "min": True, "max": True, "avg": True})
        empty = g.stats([0.0])
        self.assertIsNone(empty["mean"])
        self.assertFalse(g.check_row((1, 0, "1", "1", "1"), empty)["avg"])


class TestParse(unittest.TestCase):
    def setUp(self):
        rows = (rows_2020("C2020BPHA00001", "Import", "Fish/Seafood - Canned",
                          ["0.0438", "0.0051", "0", "0"])
                + rows_2020("C2020BPHA00001D", "Domestic", "Meat - Canned",
                            ["0", "0", "0.0196", "<0.0005"]))
        self.samples, self.census = g.parse(to_text(HEADER_2020, rows), g.TYPE_OF["bpa-2020"])
        self.by = {s["sample"]: s for s in self.samples}

    def test_ppb_and_types(self):
        fish = self.by["C2020BPHA00001"]
        self.assertEqual(fish["type"], "fish")
        self.assertAlmostEqual(fish["ppb"]["bpa"], 43.8)
        self.assertAlmostEqual(fish["ppb"]["badge"], 5.1)
        self.assertEqual(fish["ppb"]["bpf"], 0.0)
        meat = self.by["C2020BPHA00001D"]
        self.assertEqual((meat["type"], meat["function"]), ("meat", "Domestic"))
        self.assertAlmostEqual(meat["ppb"]["bpf"], 19.6)
        self.assertEqual(meat["ppb"]["bps"], 0.0)

    def test_census(self):
        c = self.census
        self.assertEqual((c["rows"], c["samples"]), (8, 2))
        self.assertEqual(c["units"], {UG: 8})
        self.assertEqual(c["rows_per_sample"], {"4": 2})
        self.assertEqual(c["kinds"], {"det": 3, "nd": 5})
        self.assertEqual(c["ids_bad"], [])
        self.assertEqual(c["missing"], {})

    def test_gate_on_a_toy_file(self):
        gate = g.gate_checks(self.census, 1234, "bpa-2020")
        self.assertFalse(gate["size"])
        self.assertFalse(gate["rows"])
        self.assertFalse(gate["samples"])
        for k in ("columns", "per_sample", "components", "units", "plan", "products", "values"):
            self.assertTrue(gate[k], k)
        self.assertFalse(g.gate_checks(self.census, 1234, "bpa-2018")["plan"])

    def test_bad_cell_fails_the_value_gate(self):
        rows = rows_2020("C2020BPHA00002", "Import", "Pear", ["n/a", "0", "0", "0"])
        samples, census = g.parse(to_text(HEADER_2020, rows), g.TYPE_OF["bpa-2020"])
        self.assertEqual(census["bad_shapes"], ["n/a"])
        self.assertFalse(g.gate_checks(census, 0, "bpa-2020")["values"])
        self.assertEqual(samples[0]["type"], "fruit")


class TestAnalysis(unittest.TestCase):
    def test_alt_rows(self):
        ss = [sample("a", "fish", "Import", badge=3.6), sample("b", "fish", "Import", badge=10.0),
              sample("c", "meat", "Import")]
        rows = g.alt_rows(ss, "badge", {"fish": (2, "3.6", "10.0", "6.8")}, ("fish", "meat"))
        self.assertEqual(rows["fish"], {"k": 2, "printed_k": 2, "detected": True, "min": True,
                                        "max": True, "avg": True})
        self.assertTrue(rows["meat"]["detected"])
        ss.append(sample("d", "meat", "Import", badge=1.0))
        self.assertFalse(g.alt_rows(ss, "badge", {}, ("meat",))["meat"]["detected"])

    def test_c4_checks(self):
        ss = [sample("f1", "fish", "Import", bpa=5.0, badge=1580.0),
              sample("f2", "fish", "Import", badge=51.2),
              sample("m1", "meat", "Import", bpa=9.0, bps=191.0),
              sample("p1", "pie", "Import", bpa=2.0),
              sample("v1", "veg", "Domestic", bpa=3.0)]
        checks, obs = g.c4_checks(ss)
        self.assertTrue(checks["with_bpa_all_imported_meat_or_fish"])
        self.assertTrue(checks["fish_badge_second_51"])
        self.assertTrue(checks["bps_meat_all_with_bpa"])
        self.assertTrue(checks["bpa_fruit_pie_all_imported"])
        self.assertFalse(checks["badge_with_bpa_8"])
        self.assertEqual((obs["badge_k"], obs["badge_imported"], obs["bpa_fruit_pie_k"]),
                         (2, 2, 1))

    def test_twins(self):
        ss = [sample("a", "fish", "Import", bpa=1.0, badge=2.0),
              sample("b", "meat", "Import", bpa=1.0, badge=2.0),
              sample("c", "meat", "Import", bpa=1.0),
              sample("d", "meat", "Import", bpa=1.0)]
        self.assertEqual(g.twins(ss), [["a", "b"]])
        self.assertEqual(g.twins(ss, min_pos=1), [["a", "b"], ["c", "d"]])

    def test_grade_without_data_grades_nothing(self):
        bad = {k: False for k in ("size", "columns")}
        preds = g.grade({}, {}, {"bpa-2018": bad, "bpa-2020": bad})
        self.assertEqual([p["id"] for p in preds],
                         ["G18", "G20", "B2", "B3", "B4", "B5", "B6", "C2", "C3", "C4"])
        self.assertFalse(any(p["met"] for p in preds))
        self.assertFalse(any(p["graded"] for p in preds if p["kind"] == "prediction"))


if __name__ == "__main__":
    unittest.main()
