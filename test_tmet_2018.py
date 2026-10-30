#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for tmet_2018.py (no network, no data). Made with AI agents working in MV2's
(Munim, Inc.) name. Code Apache-2.0."""
import csv
import io
import json
import os
import tempfile
import unittest

import tmet_2018 as T

# The file's 18 columns, with the French accents left out (the parser reads the English parts).
HEADER = ["Sample No. - No. d'echantillon", "Region - Region", "Commodity", "denree", "Function",
          "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled - Date d'echantillonage", "Type of Test", "Type d'analyse", "Component",
          "Composant", "MaxOfAMOUNT", "Report Unit - Unite de rapport", "PLAN_CODE"]
UG = "µg/g"
# Product label counts from the names-only census (they add to 987).
LABEL_COUNTS = (("Bakery Product - Cookie", 2), ("Baking Mixes", 2), ("Bran - Oat", 22),
                ("Bran - Rice", 2), ("Bran - Wheat", 8), ("Cereal", 1), ("Cereal - Corn", 22),
                ("Cereal - Mixed Grains", 5), ("Cereal - Oat", 1), ("Cereal - Rice", 6),
                ("Cereal - Wheat", 20), ("Corn Products", 3), ("Crackers", 1),
                ("Grain - Rice", 3), ("Granola/Cereal Bar", 7), ("Infant Formula - Dairy", 177),
                ("Infant Formula - Other", 86), ("Infant Formula - Soy", 133),
                ("Meal Replacement", 198), ("Oat Products", 1), ("Oil - Other", 4),
                ("Popcorn", 3), ("Protein Powder", 196), ("Rice Products", 82), ("Snack Bar", 2))
# (label, occurrence, component) -> value; every other cell is "0".
SPECIAL = {("Bran - Rice", 0, "Arsenic"): "1.13", ("Bran - Rice", 1, "Arsenic"): "1.121",
           ("Protein Powder", 0, "Mercury"): "0.022",
           ("Infant Formula - Soy", 0, "Mercury"): "0.001",
           ("Infant Formula - Soy", 1, "Mercury"): "0.003"}
# (label, occurrence) -> a D-suffixed ID whose base (samples 1 and 2) is also in the file.
DUPS = {("Infant Formula - Dairy", 0): "C2018TMET00001D", ("Protein Powder", 0): "C2018TMET00002D"}


def row(sample, product, comp, value, unit=UG, plan="2018_TS013", function="Import"):
    return [sample, "ONTARIO", "IMFD", "x", function, "x", "UNITED STATES", "x", product, "x",
            "1-Apr-18", "METALS", "x", comp, "x", value, unit, plan]


def as_csv(rows):
    buf = io.StringIO()
    csv.writer(buf).writerows([HEADER] + rows)
    return buf.getvalue()


def full_file():
    rows, i = [], 0
    for label, n in LABEL_COUNTS:
        for occ in range(n):
            i += 1
            sid = DUPS.get((label, occ), f"C2018TMET{i:05d}")
            for comp in T.COMPONENTS:
                rows.append(row(sid, label, comp, SPECIAL.get((label, occ, comp), "0")))
    return as_csv(rows)


def one_sample(sid, product, values, skip=()):
    return [row(sid, product, c, values.get(c, "0")) for c in T.COMPONENTS if c not in skip]


class TestRules(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(T.parse_value("0"), (0.0, "nd"))
        self.assertEqual(T.parse_value("0.237"), (0.237, "det"))
        self.assertEqual(T.parse_value("<0.01")[1], "nd")
        self.assertEqual(T.parse_value("ND")[1], "nd")
        for bad in ("", "-1", "NA", "trace"):
            self.assertEqual(T.parse_value(bad)[1], "bad", bad)

    def test_component(self):
        self.assertEqual(T.component("Arsenic"), "Arsenic")
        self.assertEqual(T.component(" MERCURY "), "Mercury")
        self.assertEqual(T.component("lead/plomb"), "Lead")
        self.assertIsNone(T.component("Uranium"))
        self.assertIsNone(T.component(""))

    def test_type_of(self):
        self.assertEqual(T.type_of("Oil - Other", "R1"), "rice")
        self.assertEqual(T.type_of("Oil - Other", "R2"), "bran")
        self.assertEqual(T.type_of("Popcorn", "R2"), "rice")
        self.assertEqual(T.type_of("Crackers", "R2"), "bran")
        self.assertEqual(T.type_of("Rice Products", "R2"), "rice")
        self.assertEqual(T.type_of("Protein Powder", "R1"), "protein-powder")
        self.assertEqual(T.type_of("Infant Formula - Soy", "R1"), "infant-formula")
        self.assertEqual(T.type_of("Something else", "R1"), "unmapped")

    def test_matches(self):
        self.assertTrue(T.matches(0.0795, "0.079"))
        self.assertTrue(T.matches(0.0013, "0.0013"))
        self.assertFalse(T.matches(0.0014, "0.0013"))
        self.assertTrue(T.matches(0.505, "1"))
        self.assertFalse(T.matches(None, "0.022"))
        self.assertTrue(T.matches(1.13, "1.130"))

    def test_columns(self):
        c = T.find_columns(HEADER)
        self.assertEqual((c["sample"], c["component"], c["value"], c["unit"], c["product"],
                          c["origin"], c["function"], c["region"], c["plan"]),
                         (0, 13, 15, 16, 8, 6, 4, 1, 17))


class TestPrintedFigures(unittest.TestCase):
    def test_registered_constants(self):
        self.assertEqual(sum(n for _, n in LABEL_COUNTS), T.N_SAMPLES)
        self.assertEqual(T.N_ROWS, len(T.COMPONENTS) * T.N_SAMPLES)
        self.assertEqual(set(T.LABELS), {label for label, _ in LABEL_COUNTS})
        self.assertEqual(len(T.LABELS), 25)
        self.assertEqual(sum(r[3] for r in T.TABLE1.values()), T.PRINTED_N)
        self.assertEqual(sum(r[0] for r in T.TABLE2.values()), T.PRINTED_N)
        self.assertEqual([sum(r[i] for r in T.TABLE1.values()) for i in range(3)],
                         [188, 615, 182])
        for t, (n, cells) in T.TABLE2.items():
            self.assertEqual(n, T.TABLE1[t][3], t)
            self.assertEqual(set(cells), set(T.TOXIC), t)

    def test_readings_sizes(self):
        counts = dict(LABEL_COUNTS)
        for r in T.READINGS:
            sizes = {}
            for label, n in counts.items():
                t = T.type_of(label, r)
                sizes[t] = sizes.get(t, 0) + n
            self.assertEqual(sizes, {"bran": 99, "infant-formula": 396, "meal-replacement": 198,
                                     "protein-powder": 196, "rice": 98}, r)

    def test_consistent_counts(self):
        self.assertEqual(T.consistent_counts("71", 99), [70])
        self.assertEqual(T.consistent_counts("9", 395), [34, 35, 36, 37])
        self.assertEqual(T.consistent_counts("37", 98), [36])

    def test_printed_internal(self):
        p = T.printed_internal()
        self.assertEqual((p["table1_total"], p["table2_total"]), (985, 985))
        self.assertEqual((p["counts"]["Cd"]["min"], p["counts"]["Cd"]["max"]), (386, 391))
        self.assertEqual((p["counts"]["Pb"]["min"], p["counts"]["Pb"]["max"]), (327, 332))
        self.assertTrue(p["counts"]["Cd"]["text_fits"])
        self.assertTrue(p["counts"]["Pb"]["text_fits"])
        self.assertEqual(p["counts"]["Cd"]["text_detected"], 389)


class TestParse(unittest.TestCase):
    def test_small_file(self):
        rows = one_sample("C2018TMET00001", "Protein Powder", {"Lead": "0.237", "Mercury": "0.022"})
        rows += one_sample("C2018TMET00001D", "Infant Formula - Soy", {}, skip=("Zinc",))
        rows.append(row("C2018TMET00001D", "Infant Formula - Soy", "Arsenic", "0.01"))
        rows.append([""] * 18)
        samples, census = T.parse(as_csv(rows))
        by = {s["sample"]: s for s in samples}
        a = by["C2018TMET00001"]
        self.assertEqual((a["Pb"], a["Hg"], a["As"], a["n_toxic"], a["dup"]),
                         (0.237, 0.022, 0.0, 2, False))
        b = by["C2018TMET00001D"]
        self.assertEqual((b["As"], b["n_toxic"], b["dup"], b["base"]),
                         (0.01, 1, True, "C2018TMET00001"))
        self.assertEqual(b["missing"], ["Zinc"])
        self.assertEqual(b["repeated"], ["Arsenic"])
        self.assertEqual(census["rows"], 38)
        self.assertEqual(census["rows_per_sample"], {"19": 2})
        self.assertEqual(census["kinds"], {"nd": 35, "det": 3})
        self.assertEqual(census["units"], {UG: 38})
        self.assertEqual(census["ids_bad"], [])
        g = T.gate_checks(census, T.SIZE)
        self.assertEqual(g, {"size": True, "columns": True, "rows": False, "samples": False,
                             "per_sample": False, "components": True, "units": True,
                             "plan": True, "products": True, "values": True})

    def test_bad_cells_fail_gate(self):
        text = as_csv([row("X1", "Meal Replacement", "Lead", "n/a"),
                       row("X1", "Meal Replacement", "Arsenic", "0", unit="mg/kg")])
        _, census = T.parse(text)
        self.assertEqual(census["bad_shapes"], ["n/a"])
        self.assertEqual(census["ids_bad"], ["X1"])
        g = T.gate_checks(census, 1)
        self.assertFalse(g["values"])
        self.assertFalse(g["size"])
        self.assertFalse(g["units"])
        self.assertFalse(g["samples"])


class TestFullRun(unittest.TestCase):
    def test_gate_grade_and_outputs(self):
        samples, census = T.parse(full_file())
        gate = T.gate_checks(census, T.SIZE)
        self.assertTrue(all(gate.values()), gate)
        a = T.analyse(samples)
        self.assertEqual(a["n"], 987)
        self.assertEqual(a["tables"]["R1"]["rice"]["n"], 98)
        self.assertEqual(a["tables"]["R2"]["bran"]["n"], 99)
        self.assertEqual(a["drop_d"]["n"], 985)
        self.assertEqual(a["drop_d"]["tables"]["infant-formula"]["n"], 395)
        self.assertEqual(a["drop_d"]["tables"]["protein-powder"]["n"], 195)
        self.assertEqual(a["if_hg"], 2)
        self.assertEqual([x["As"] for x in a["as_top"]], [1.13, 1.121])
        self.assertEqual(a["hg_top"]["max"], 0.022)
        self.assertEqual([h["product"] for h in a["hg_top"]["holders"]], ["Protein Powder"])
        self.assertEqual([d["sample"] for d in a["dups"]], ["C2018TMET00001D", "C2018TMET00002D"])
        self.assertTrue(all(d["base_present"] for d in a["dups"]))
        self.assertEqual(a["nd"]["Cd"], 987)
        self.assertEqual((a["any"], a["all4"]), (5, 0))
        self.assertEqual(a["origins"]["R1"]["rice"], [0, 98, 0, 98])
        preds = T.grade(a, gate)
        self.assertEqual([p["id"] for p in preds],
                         ["G", "C1", "P1", "P2", "P3", "P4", "P5", "P6"])
        by = {p["id"]: p for p in preds}
        self.assertEqual(by["P1"]["observed"]["matched"], 3)
        self.assertEqual(by["P2"]["observed"]["matched"], 1)
        self.assertEqual(by["C1"]["observed"]["matched"], 0)
        self.assertEqual((by["P3"]["observed"]["R1"]["total"], by["P3"]["observed"]["R2"]["total"]),
                         (1, 1))
        met = {p["id"]: p["met"] for p in preds}
        self.assertEqual(met, {"G": True, "C1": False, "P1": False, "P2": False, "P3": False,
                               "P4": True, "P5": False, "P6": True})
        with tempfile.TemporaryDirectory() as d:
            result = T.write_outputs(d, samples, census, a, preds, {"source": "test"})
            self.assertEqual(result["n_graded"], 8)
            self.assertEqual(result["n_met"], 3)
            with open(os.path.join(d, "tmet_2018_summary.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["study"], "tmet-2018")
            with open(os.path.join(d, "tmet_2018_samples.csv"), encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.reader(fh))), 988)

    def test_failed_gate_grades_nothing(self):
        gate = T.gate_checks(T.empty_census(), -1)
        preds = T.grade({"printed_internal": T.printed_internal()}, gate)
        self.assertEqual(sum(1 for p in preds if p["graded"]), 1)
        self.assertFalse(any(p["met"] for p in preds))


if __name__ == "__main__":
    unittest.main()
