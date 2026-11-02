#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for perchlorate_census.py (no network, no CFIA file read).
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import datetime
import json
import unittest

import perchlorate_census as pc
from bpa_series_census import columns_census

TOY = ("Sample No.,Product,Date Sampled,Component,Result,Unit\n"
       "C2011PERC0001,Cucumber,05/04/2011,Perchlorate,12.5,ppb\n"
       "C2011PERC0002,Cucumber,03/31/2012,Perchlorate,ND,ppb\n"
       "C2011PERC0003,Cream,2012-04-02,Perchlorate,<2,ppb\n"
       "C2011PERC0003,Cream,2012-04-02,Perchlorate,3.75,ppb\n"
       "C2011PERC0004,Milk,,Perchlorate,4.25,ppb\n")


class TestTargets(unittest.TestCase):
    def test_portal_facts_as_preregistered(self):
        t = {x["name"]: x for x in pc.TARGETS}
        self.assertEqual(set(t), {"p10", "p11", "p13"})
        self.assertEqual((t["p10"]["size"], t["p10"]["md5"], t["p10"]["samples"]),
                         (95033, "f497970ea94e7d4eaf74fdabb9535bca", 611))
        self.assertEqual((t["p11"]["size"], t["p11"]["md5"], t["p11"]["samples"]),
                         (228127, "66a04ce98555c6898c18ebaefc042a96", 1426))
        self.assertEqual((t["p13"]["size"], t["p13"]["md5"], t["p13"]["samples"]),
                         (78310, "05b587cb13f15932894200ba5879445a", 477))
        self.assertTrue(t["p10"]["path"].endswith("2010-11_perchlorate_in_fresh_fruits_and_.csv"))
        self.assertTrue(t["p11"]["path"].endswith("2011-13_perchlorate_in_fresh_fruits_and_.csv"))


class TestDates(unittest.TestCase):
    def test_shapes(self):
        self.assertEqual(pc.date_shape("4-Jun-18"), "9-Aaa-99")
        self.assertEqual(pc.date_shape("2019-04-09"), "9999-99-99")
        self.assertEqual(pc.date_shape("05/04/2011"), "99/99/9999")

    def test_parse_and_survey_year(self):
        d, amb = pc.parse_date("4-Jun-18")
        self.assertEqual((d, amb), (datetime.date(2018, 6, 4), False))
        d, amb = pc.parse_date("05/04/2011")
        self.assertEqual((d, amb), (datetime.date(2011, 5, 4), True))
        d, amb = pc.parse_date("03/31/2012")
        self.assertEqual((d, amb), (datetime.date(2012, 3, 31), False))
        self.assertEqual(pc.parse_date("not a date"), (None, False))
        self.assertEqual(pc.survey_year(datetime.date(2011, 5, 1)), "2011-12")
        self.assertEqual(pc.survey_year(datetime.date(2012, 3, 31)), "2011-12")
        self.assertEqual(pc.survey_year(datetime.date(2012, 4, 1)), "2012-13")


class TestProductYears(unittest.TestCase):
    def test_counts_per_sample_not_per_row(self):
        out = pc.product_years(TOY)
        self.assertNotIn("error", out)
        self.assertEqual(out["by_product"], {"Cucumber": {"2011-12": 2},
                                             "Cream": {"2012-13": 1},
                                             "Milk": {"(unparsed)": 1}})
        self.assertEqual(out["by_year"], {"2011-12": 2, "2012-13": 1, "(unparsed)": 1})
        self.assertEqual((out["unparsed"], out["ambiguous"]), (1, 1))
        self.assertEqual((out["first"], out["last"]), ("2011-05-04", "2012-04-02"))
        self.assertEqual(out["date_shapes"], {"99/99/9999": 2, "9999-99-99": 1, "(blank)": 1})

    def test_values_never_appear(self):
        dumped = json.dumps(pc.product_years(TOY))
        for v in ("12.5", "3.75", "4.25"):
            self.assertNotIn(v, dumped)
        out = columns_census(TOY)
        self.assertEqual((out["rows"], out["samples"]), (5, 4))
        dumped = json.dumps(out)
        for v in ("12.5", "3.75", "4.25"):
            self.assertNotIn(v, dumped)

    def test_missing_date_column(self):
        out = pc.product_years("Sample No.,Product,Result\nA1,Milk,2\n")
        self.assertIn("error", out)


class TestGateFacts(unittest.TestCase):
    def test_all_hold_and_failures(self):
        target = pc.TARGETS[2]
        res = {"bytes": 78310, "size_matches_portal": True, "md5_matches_portal": True,
               "columns": {"samples": 477, "rows": 477},
               "census": {"components": {"Perchlorate": 477}, "units": {"ppb": 477},
                          "rows_per_sample": {"1": 477}}}
        f = pc.gate_facts(res, target)
        self.assertTrue(f["size"] and f["md5"] and f["samples_match"])
        self.assertTrue(f["one_analyte"] and f["one_unit"] and f["one_row_per_sample"])
        bad = {"bytes": 10, "columns": {"error": "x"}, "census": {"error": "missing key column"}}
        g = pc.gate_facts(bad, target)
        self.assertIsNone(g["samples"])
        self.assertFalse(g["samples_match"] or g["one_analyte"] or g["one_unit"]
                         or g["one_row_per_sample"])
        self.assertEqual(g["census_error"], "missing key column")


if __name__ == "__main__":
    unittest.main(verbosity=2)
