#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for pah_2018.py (no network, no data). Made with AI agents working in MV2's
(Munim, Inc.) name. Code Apache-2.0."""
import csv
import io
import json
import os
import tempfile
import unittest

import pah_2018 as P

# The file's 18 columns, with the French accents left out (the parser reads the English parts).
HEADER = ["Sample No. - No. d'echantillon", "Region - Region", "Commodity", "denree", "Function",
          "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled - Date d'echantillonage", "Type of Test", "Type d'analyse", "Component",
          "Composant", "MaxOfAMOUNT", "Report Unit - Unite de rapport", "PLAN_CODE"]
# Product label counts from the names-only census (they add to 287).
LABEL_COUNTS = (("Baked Goods", 1), ("Bakery Product - Cookie", 71), ("Crackers", 70),
                ("Mixed Vegetable (roasted)", 3), ("Oil - Canola", 11), ("Oil - Coconut", 3),
                ("Oil - Corn", 10), ("Oil - Grapeseed", 2), ("Oil - Olive", 9),
                ("Oil - Other", 4), ("Oil - Palm", 9), ("Oil - Peanut", 10),
                ("Oil - Soybean", 10), ("Oil - Sunflower", 10), ("Pepper (roasted)", 59),
                ("Tomato (roasted)", 5))
# (label, occurrence, component) -> value; every other cell is "0".
SPECIAL = {("Oil - Peanut", 0, "Benzo[a]pyrene"): "2.408304",
           ("Oil - Canola", 0, "Chrysene"): "3.3759",
           ("Pepper (roasted)", 0, "Benzo[a]pyrene"): "9.17",
           ("Crackers", 0, "Benzo[a]anthracene"): "16.8"}


def row(sample, product, comp, value, unit="ng/g", plan="2018_TS024", function="Import"):
    return [sample, "ONTARIO", "IMFD", "x", function, "x", "UNITED STATES", "x", product, "x",
            "1-Apr-18", "BENZOPYRENE (PAH)", "x", comp, "x", value, unit, plan]


def as_csv(rows):
    buf = io.StringIO()
    csv.writer(buf).writerows([HEADER] + rows)
    return buf.getvalue()


def full_file():
    rows, i = [], 0
    for label, n in LABEL_COUNTS:
        for occ in range(n):
            i += 1
            for comp in P.COMPONENTS:
                rows.append(row(f"C2018PAHS{i:05d}", label, comp,
                                SPECIAL.get((label, occ, comp), "0")))
    return as_csv(rows)


def one_sample(sid, product, values, skip=()):
    return [row(sid, product, c, values.get(c, "0")) for c in P.COMPONENTS if c not in skip]


class TestRules(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(P.parse_value("0"), (0.0, "nd"))
        self.assertEqual(P.parse_value("9.17"), (9.17, "det"))
        self.assertEqual(P.parse_value("<0.1")[1], "nd")
        self.assertEqual(P.parse_value("ND")[1], "nd")
        for bad in ("", "-1", "NA", "trace"):
            self.assertEqual(P.parse_value(bad)[1], "bad", bad)

    def test_component(self):
        self.assertEqual(P.component("Benzo[a]pyrene"), "Benzo[a]pyrene")
        self.assertEqual(P.component(" CHRYSENE "), "Chrysene")
        self.assertEqual(P.component("Dibenzo(a,h)anthracene"), "Dibenzo(a,h)anthracene")
        self.assertIsNone(P.component("Benzene"))
        self.assertIsNone(P.component(""))

    def test_teq(self):
        vals = {"Benzo[a]pyrene": 0.5, "Benzo[a]anthracene": 1.0, "Benzo[b]fluoranthene": 2.0,
                "Chrysene": 10.0, "Pyrene": 99.0}
        self.assertAlmostEqual(P.teq(vals), 0.9, places=12)
        self.assertEqual(P.teq({}), 0.0)
        self.assertAlmostEqual(P.teq({"Chrysene": 3.3759}), 0.033759, places=12)

    def test_group_of(self):
        self.assertEqual(P.group_of("Crackers"), "baked")
        self.assertEqual(P.group_of("Oil - Coconut"), "oils")
        self.assertEqual(P.group_of("Tomato (roasted)"), "veg")
        self.assertEqual(P.group_of("Oil - Fish"), "unmapped")
        self.assertEqual(P.OIL_TYPE["Oil - Grapeseed"], "other")

    def test_matches(self):
        self.assertTrue(P.matches(0.0337594, "0.033759"))
        self.assertFalse(P.matches(0.0338, "0.033759"))
        self.assertTrue(P.matches(0.27, "0.27"))
        self.assertTrue(P.matches(0.944818, "0.94"))
        self.assertFalse(P.matches(None, "9.17"))

    def test_figure_match(self):
        self.assertEqual(P.figure_match([0.033759, 0.0023], P.FIGURE["canola"]),
                         {"n_file": 2, "n_printed": 2, "matched": 2, "full": True})
        self.assertEqual(P.figure_match([0.0023], P.FIGURE["canola"]),
                         {"n_file": 1, "n_printed": 2, "matched": 1, "full": False})
        self.assertEqual(P.figure_match([0.03376, 0.0023, 0.5], P.FIGURE["canola"]),
                         {"n_file": 3, "n_printed": 2, "matched": 1, "full": False})

    def test_columns(self):
        c = P.find_columns(HEADER)
        self.assertEqual((c["sample"], c["component"], c["value"], c["unit"], c["product"],
                          c["origin"], c["function"], c["region"], c["plan"]),
                         (0, 13, 15, 16, 8, 6, 4, 1, 17))


class TestPrintedFigures(unittest.TestCase):
    def test_registered_constants(self):
        self.assertEqual(sum(n for _, n in LABEL_COUNTS), P.N_SAMPLES)
        self.assertEqual(P.N_ROWS, len(P.COMPONENTS) * P.N_SAMPLES)
        self.assertEqual(set(P.LABELS), {label for label, _ in LABEL_COUNTS})
        self.assertEqual(len(P.LABELS), 16)
        self.assertEqual(sum(r[3] for r in P.TABLE1.values()), P.N_SAMPLES)
        self.assertEqual([sum(r[i] for r in P.TABLE1.values()) for i in range(3)],
                         [28, 166, 93])
        self.assertEqual(sum(P.TABLE2[g][0] for g in P.GROUPS), P.TABLE2["all"][0])
        self.assertEqual(sum(P.TABLE2[g][1] for g in P.GROUPS), P.TABLE2["all"][1])
        for g in P.GROUPS:
            self.assertEqual(P.TABLE2[g][0], P.TABLE1[g][3], g)

    def test_label_sizes(self):
        groups, types = {}, {}
        for label, n in LABEL_COUNTS:
            g = P.group_of(label)
            groups[g] = groups.get(g, 0) + n
            if label in P.OIL_TYPE:
                t = P.OIL_TYPE[label]
                types[t] = types.get(t, 0) + n
        self.assertEqual(groups, {"baked": 142, "oils": 78, "veg": 67})
        self.assertEqual(types, {"canola": 11, "corn": 10, "olive": 9, "palm": 9, "peanut": 10,
                                 "soybean": 10, "sunflower": 10, "other": 9})
        self.assertEqual(set(types), set(P.OIL_TYPES))

    def test_printed_internal(self):
        p = P.printed_internal()
        self.assertEqual(p["figure_positives"], 56)
        self.assertEqual(p["table2_oils_detected"], 55)
        self.assertTrue(p["soybean_list_equals_sunflower_list"])
        self.assertAlmostEqual(p["figure_sum"], 15.607718, places=6)
        self.assertFalse(p["figure_mean_matches_table2"])
        self.assertTrue(P.matches(p["figure_mean"], "0.28"))
        self.assertAlmostEqual(p["sunflower_sum_bounds_if_6"][0], -0.304979, places=6)
        self.assertAlmostEqual(p["sunflower_sum_bounds_if_6"][1], 0.245021, places=6)
        self.assertAlmostEqual(p["peanut_mean"], 0.944818, places=6)
        self.assertTrue(P.matches(p["peanut_mean"], P.PEANUT_AVG))
        self.assertAlmostEqual(p["canola_mean"], 0.0180295, places=7)
        self.assertTrue(P.matches(p["canola_mean"], P.CANOLA_AVG))
        self.assertEqual(p["table2_detected_sum"], 133)
        self.assertAlmostEqual(p["table2_weighted_mean"], 54.33 / 133, places=9)
        self.assertTrue(P.matches(p["table2_weighted_mean"], "0.41"))


class TestParse(unittest.TestCase):
    def test_small_file(self):
        rows = one_sample("C2018PAHS00001", "Oil - Peanut",
                          {"Benzo[a]pyrene": "2.4", "Chrysene": "0.8"})
        rows += one_sample("C2018PAHS00002", "Crackers", {}, skip=("Pyrene",))
        rows.append(row("C2018PAHS00002", "Crackers", "Chrysene", "<0.1"))
        rows.append([""] * 18)
        samples, census = P.parse(as_csv(rows))
        by = {s["sample"]: s for s in samples}
        a = by["C2018PAHS00001"]
        self.assertAlmostEqual(a["teq"], 2.408, places=12)
        self.assertEqual((a["bap"], a["n_pah"], a["group"], a["oil_type"]),
                         (2.4, 2, "oils", "peanut"))
        b = by["C2018PAHS00002"]
        self.assertEqual((b["teq"], b["group"], b["oil_type"]), (0.0, "baked", ""))
        self.assertEqual(b["missing"], ["Pyrene"])
        self.assertEqual(b["repeated"], ["Chrysene"])
        self.assertEqual(census["rows"], 32)
        self.assertEqual(census["rows_per_sample"], {"16": 2})
        self.assertEqual(census["kinds"], {"nd": 30, "det": 2})
        self.assertEqual(census["units"], {"ng/g": 32})
        self.assertEqual(census["ids_bad"], [])
        g = P.gate_checks(census, P.SIZE)
        self.assertEqual(g, {"size": True, "columns": True, "rows": False, "samples": False,
                             "per_sample": False, "components": True, "units": True,
                             "plan": True, "products": True, "values": True})

    def test_bad_cells_fail_gate(self):
        text = as_csv([row("X1", "Crackers", "Chrysene", "n/a"),
                       row("X1", "Crackers", "Pyrene", "0", unit="ug/kg")])
        _, census = P.parse(text)
        self.assertEqual(census["bad_shapes"], ["n/a"])
        self.assertEqual(census["ids_bad"], ["X1"])
        g = P.gate_checks(census, 1)
        self.assertFalse(g["values"])
        self.assertFalse(g["size"])
        self.assertFalse(g["units"])
        self.assertFalse(g["samples"])


class TestFullRun(unittest.TestCase):
    def test_gate_grade_and_outputs(self):
        samples, census = P.parse(full_file())
        gate = P.gate_checks(census, P.SIZE)
        self.assertTrue(all(gate.values()), gate)
        a = P.analyse(samples)
        self.assertEqual(a["n"], 287)
        self.assertEqual({g: (a["groups"][g]["n"], a["groups"][g]["k"]) for g in P.TABLE2},
                         {"baked": (142, 1), "oils": (78, 2), "veg": (67, 1), "all": (287, 4)})
        self.assertEqual(a["groups"]["all"]["max"], 9.17)
        self.assertAlmostEqual(a["groups"]["baked"]["max"], 1.68, places=12)
        self.assertEqual(a["figure"]["peanut"],
                         {"n_file": 1, "n_printed": 9, "matched": 1, "full": False})
        self.assertEqual(a["figure"]["canola"]["matched"], 1)
        self.assertEqual(a["figure"]["sunflower"]["n_file"], 0)
        self.assertEqual(a["oil_rank"]["highest_mean"], "peanut")
        self.assertEqual(a["oil_rank"]["lowest_pct"], "corn")
        self.assertEqual([v["product"] for v in a["veg_top"]],
                         ["Pepper (roasted)", "Mixed Vegetable (roasted)"])
        self.assertEqual([b["product"] for b in a["baked_ge"]], ["Crackers"])
        self.assertEqual(a["origins"]["oils"], [0, 78, 0, 78])
        self.assertTrue(a["table2"]["oils"]["n"])
        preds = P.grade(a, gate)
        self.assertEqual([p["id"] for p in preds], ["G", "P1", "P2", "P3", "P4", "P5", "P6"])
        by = {p["id"]: p for p in preds}
        self.assertEqual(by["P1"]["observed"]["full"], 0)
        self.assertEqual(by["P3"]["observed"]["matched"], 2)
        self.assertTrue(by["P4"]["observed"]["cells"]["max"])
        self.assertFalse(by["P6"]["observed"]["checks"]["peanut_highest_mean"])
        self.assertTrue(by["P6"]["observed"]["checks"]["one_baked_high"])
        met = {p["id"]: p["met"] for p in preds}
        self.assertEqual(met, {"G": True, "P1": False, "P2": False, "P3": False, "P4": False,
                               "P5": False, "P6": False})
        with tempfile.TemporaryDirectory() as d:
            result = P.write_outputs(d, samples, census, a, preds, {"source": "test"})
            self.assertEqual(result["n_graded"], 7)
            self.assertEqual(result["n_met"], 1)
            with open(os.path.join(d, "pah_2018_summary.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["study"], "pah-2018")
            with open(os.path.join(d, "pah_2018_samples.csv"), encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.reader(fh))), 288)

    def test_failed_gate_grades_nothing(self):
        gate = P.gate_checks(P.empty_census(), -1)
        preds = P.grade({"printed_internal": P.printed_internal()}, gate)
        self.assertEqual(sum(1 for p in preds if p["graded"]), 1)
        self.assertFalse(any(p["met"] for p in preds))


if __name__ == "__main__":
    unittest.main()
