"""Offline tests for red_palm_dyes.py, on synthetic rows only (no CFIA value is used).

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import csv
import io
import unittest

import red_palm_dyes as r

HEADER = ["﻿Sample No. – No. d'échantillon", "Region - Région", "Commodity",
          "Denrée", "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled – Date d'échantillonage", "Component", "Composant", "AMOUNT",
          "Report Unit - Unité de rapport"]
COMPONENTS = ["Chlorophylline", "Citrus Red 2", "Metanil Yellow", "Methyl Yellow", "Orange II",
              "Para Red", "Rhodamine B", "Solvent Blue 59", "Sudan Black B", "Sudan Blue II",
              "Sudan I", "Sudan II", "Sudan III", "Sudan IV", "Sudan Orange G", "Sudan Red 7B",
              "Sudan Red G", "Toluidine Red"]


def make_csv(samples, encoding="utf-8", bom=True):
    """samples: (sample id, origin, {component: amount}); one row per sample and component."""
    header = list(HEADER)
    if not bom:
        header[0] = header[0].replace("﻿", "")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    for sid, origin, amounts in samples:
        for comp in COMPONENTS:
            w.writerow([sid, "ONTARIO - ONTARIO", "IMFD", "DAIM", "Import", "Importation", origin,
                        origin, "Red Palm Oil", "Huile de palme rouge", "1/15/2020", comp, comp,
                        str(amounts.get(comp, 0)), "ug/g"])
    return buf.getvalue().encode(encoding)


def batch(prefix, n, special, default_origin):
    """n samples; special maps a sequence number to (origin, amounts)."""
    out = []
    for i in range(1, n + 1):
        origin, amounts = special.get(i, (default_origin, {}))
        out.append(("%s%05d" % (prefix, i), origin, amounts))
    return out


class ParseTest(unittest.TestCase):
    def test_columns_with_bom_and_accents(self):
        cols = r.find_columns(HEADER)
        self.assertEqual(cols["sample"], 0)
        self.assertEqual(cols["origin"], 6)
        self.assertEqual(cols["component"], 11)
        self.assertEqual(cols["amount"], 13)
        self.assertEqual(cols["unit"], 14)

    def test_duplicates_merge_and_flags(self):
        raw = make_csv([("C2019FFPO00001", "GHANA", {"Sudan IV": 15.6}),
                        ("C2019FFPO00002", "Malaysia", {}),
                        ("C2019FFPO00002D", "Malaysia", {"Sudan III": 0.5})])
        rows, check = r.parse(raw, "2019-20")
        self.assertEqual([s["sample"] for s in rows], ["C2019FFPO00001", "C2019FFPO00002"])
        self.assertEqual(rows[0]["sudan_dyes"], ["sudan iv"])
        self.assertEqual(rows[0]["sudan_max"], 15.6)
        self.assertEqual(rows[0]["origin"], "GHANA")
        self.assertEqual(rows[1]["origin"], "MALAYSIA")
        self.assertEqual(rows[1]["ids"], ["C2019FFPO00002", "C2019FFPO00002D"])
        self.assertEqual(rows[1]["sudan_dyes"], ["sudan iii"])
        self.assertEqual(rows[1]["id_sudan"], {"C2019FFPO00002": False, "C2019FFPO00002D": True})
        self.assertEqual(check["encoding"], "utf-8-sig")
        self.assertEqual(check["data_rows"], 54)
        self.assertEqual(check["samples"], 2)
        self.assertEqual(check["ids"], 3)
        self.assertEqual(check["duplicate_ids"], 1)
        self.assertEqual(check["components"]["sudan iv"], 3)
        self.assertEqual(check["units"], {"ug/g": 54})
        self.assertEqual(check["bad_numbers"], 0)
        self.assertEqual(check["repeats"], 0)
        self.assertEqual(check["unknown_components"], 0)
        self.assertEqual(check["origin_conflicts"], 0)
        self.assertEqual(check["incomplete_samples"], 0)

    def test_sudan_i_is_not_sudan_ii(self):
        rows, _ = r.parse(make_csv([("C2020FFPO00003", "TOGO", {"Sudan II": 1.0})]), "2020-21")
        self.assertEqual(rows[0]["sudan_dyes"], ["sudan ii"])
        self.assertEqual(rows[0]["other_dyes"], [])

    def test_cp1252_file(self):
        raw = make_csv([("C2020FFPO00001", "IVORY COAST", {"Rhodamine B": 0.2})],
                       encoding="cp1252", bom=False)
        rows, check = r.parse(raw, "2020-21")
        self.assertEqual(check["encoding"], "cp1252")
        self.assertEqual(rows[0]["origin"], "IVORY COAST")
        self.assertFalse(rows[0]["sudan_positive"])
        self.assertEqual(rows[0]["other_dyes"], ["rhodamine b"])

    def test_base_id_only_strips_a_trailing_d_after_a_digit(self):
        self.assertEqual(r.base_id("C2019FFPO00019D"), "C2019FFPO00019")
        self.assertEqual(r.base_id("C2019FFPO00019"), "C2019FFPO00019")
        self.assertEqual(r.base_id("ABCD"), "ABCD")


class GradeTest(unittest.TestCase):
    def test_all_met(self):
        primary, check = r.parse(make_csv(batch("C2019FFPO", 60, {
            1: ("GHANA", {"Sudan IV": 3.0}),
            2: ("NIGERIA", {"Sudan III": 1.0, "Sudan IV": 2.0})}, "ECUADOR")), "2019-20")
        second, _ = r.parse(make_csv(batch("C2020FFPO", 32, {
            5: ("UNKNOWN", {"Sudan IV": 15.6})}, "COLOMBIA")), "2020-21")
        g = r.grade(primary, primary + second, check)
        self.assertTrue(g["gradable_parse"])
        self.assertEqual(g["predictions"]["P1"]["value"], 2)
        self.assertEqual(g["predictions"]["P2"]["value"], "2 of 60")
        self.assertEqual(g["predictions"]["P3"]["value"], "0 of 3 outside")
        self.assertEqual(g["predictions"]["P4"]["value"], {"sudan iii": 1, "sudan iv": 3})
        self.assertEqual(g["predictions"]["P5"]["value"], {"GHANA": 1, "NIGERIA": 1})
        self.assertEqual(g["predictions"]["P6"]["value"], 0)
        self.assertEqual({k: v["status"] for k, v in g["predictions"].items()},
                         {k: "met" for k in ("P1", "P2", "P3", "P4", "P5", "P6")})
        self.assertEqual((g["met"], g["gradable"]), (6, 6))
        self.assertEqual(g["pooled_years"], ["2019-20", "2020-21"])

    def test_failures_are_reported(self):
        primary, check = r.parse(make_csv(batch("C2019FFPO", 60, {
            1: ("MALAYSIA", {"Sudan I": 1.0}),
            2: ("NIGERIA", {"Sudan I": 2.0, "Rhodamine B": 0.3})}, "GHANA")), "2019-20")
        g = r.grade(primary, primary, check)
        st = {k: v["status"] for k, v in g["predictions"].items()}
        self.assertEqual(st, {"P1": "met", "P2": "met", "P3": "not met", "P4": "not met",
                              "P5": "not met", "P6": "not met"})
        self.assertEqual(g["predictions"]["P3"]["value"], "1 of 2 outside")
        self.assertEqual((g["met"], g["gradable"]), (2, 6))

    def test_p2_fails_above_ten_percent(self):
        special = {i: ("GHANA", {"Sudan IV": 1.0}) for i in range(1, 8)}
        primary, check = r.parse(make_csv(batch("C2019FFPO", 60, special, "TOGO")), "2019-20")
        g = r.grade(primary, primary, check)
        self.assertEqual(g["predictions"]["P2"]["value"], "7 of 60")
        self.assertEqual(g["predictions"]["P2"]["status"], "not met")

    def test_too_few_samples_is_not_gradable(self):
        primary, check = r.parse(make_csv(batch("C2019FFPO", 10, {}, "GHANA")), "2019-20")
        g = r.grade(primary, primary, check)
        self.assertFalse(g["gradable_parse"])
        self.assertEqual((g["met"], g["gradable"]), (0, 0))

    def test_no_positive_leaves_origin_predictions_ungraded(self):
        primary, check = r.parse(make_csv(batch("C2019FFPO", 60, {}, "GHANA")), "2019-20")
        st = {k: v["status"] for k, v in r.grade(primary, primary, check)["predictions"].items()}
        self.assertEqual(st, {"P1": "not met", "P2": "met", "P3": "not gradable",
                              "P4": "not gradable", "P5": "not gradable", "P6": "met"})


class DescribeTest(unittest.TestCase):
    def test_tables(self):
        rows, _ = r.parse(make_csv([("C2019FFPO00001", "GHANA", {"Sudan IV": 15.6,
                                                                 "Chlorophylline": 2.0}),
                                    ("C2019FFPO00002", "GHANA", {}),
                                    ("C2019FFPO00003", "ECUADOR", {})]), "2019-20")
        d = r.describe({"2019-20": rows})
        self.assertEqual(d["by_year_origin"]["2019-20"]["GHANA"],
                         {"n": 2, "sudan_positive": 1, "sudan_max": 15.6, "other_positive": 0})
        self.assertEqual(d["component_positives"]["2019-20"]["sudan iv"], 1)
        self.assertEqual(d["chlorophylline_nonzero"]["2019-20"], 1)
        self.assertEqual(len(d["positive_rows"]), 1)
        self.assertEqual(d["positive_rows"][0]["amounts_nonzero"],
                         {"chlorophylline": 2.0, "sudan iv": 15.6})
        md = r.summary_md({"grade": r.grade(rows, rows, {"components": {}}), "descriptive": d,
                           "checks": {}})
        self.assertIn("red_palm_dyes", md)


if __name__ == "__main__":
    unittest.main()
