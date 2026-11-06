#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for phthalates_series_census.py (no network, no CFIA file read).
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import json
import unittest

import phthalates_series_census as ps

LONG = ("Sample ID,Product,Origin,Date Sampled,Component,Result,Unit\n"
        "C2018PHTH0001,Flatbread - Naan,Domestic,2018-04-03,Phthalate Screen,"
        "1 Phthalate detected,n/a\n"
        "C2018PHTH0001,Flatbread - Naan,Domestic,2018-04-03,Diisononyl phthalate,1.375,ug/g\n"
        "C2018PHTH0002,Tofu,Import,2019-03-21,Phthalate Screen,0 Phthalates detected,n/a\n"
        "C2014PHTH0003,Nut Butter - Peanut,Unknown,2014-06-10,Phthalate Screen,"
        "1 Phthalate detected,n/a\n"
        "C2014PHTH0003,Nut Butter - Peanut,Unknown,2014-06-10,Bis(2-ethylhexyl) phthalate,"
        "2.625,ug/g\n")


class TestTargets(unittest.TestCase):
    def test_portal_facts_as_preregistered(self):
        f, p = ps.TARGETS
        self.assertEqual((f["dataset"], f["resource"], f["md5"], f["samples"]),
                         ("c4202b90-03d1-4eef-9fcc-0740066fc0c4",
                          "8ce9082f-b339-4e5d-b74a-fa1747d295ac",
                          "22dc3074e8e2c55b60fb96a666c5ff16", 599))
        self.assertEqual((p["dataset"], p["resource"], p["md5"], p["samples"]),
                         ("ea25d8e4-180c-4f7c-a912-f37381168664",
                          "072329d5-0f9c-4e3f-aae1-c4996ae2b5d5",
                          "2c80659a91013f3657519375ee33b400", 4517))
        self.assertEqual(f["size_band"], (150016, 151040))
        self.assertEqual(p["size_band"], (1288704, 1289728))
        self.assertIsNone(f["size"])
        self.assertIsNone(p["size"])
        self.assertEqual(len(p["path"]), 100)
        self.assertTrue(p["path"].endswith("-dans-cert.csv"))
        self.assertTrue(f["path"].endswith("flatbread-and-vegan-products.csv"))
        self.assertEqual(p["years"], ("2012-13", "2013-14", "2014-15", "2015-16", "2016-17",
                                      "2017-18"))

    def test_kib_band_matches_known_files(self):
        lo, hi = ps.kib_band(115)
        self.assertTrue(lo <= 117529 <= hi)
        lo, hi = ps.kib_band(58)
        self.assertTrue(lo <= 58972 <= hi)
        self.assertEqual(ps.kib_band(1), (512, 1536))


class TestSurveyYears(unittest.TestCase):
    def test_exact_missing_extra(self):
        py = {"by_year": {"2018-19": 2, "2014-15": 1}}
        out = ps.survey_years(py, ("2018-19",))
        self.assertEqual(out["present"], ["2014-15", "2018-19"])
        self.assertEqual(out["extra"], ["2014-15"])
        self.assertEqual(out["missing"], [])
        self.assertFalse(out["exact"])
        self.assertTrue(ps.survey_years({"by_year": {"2018-19": 599}}, ("2018-19",))["exact"])
        bad = ps.survey_years({"by_year": {"2018-19": 598, "(unparsed)": 1}}, ("2018-19",))
        self.assertEqual(bad["unparsed"], 1)
        self.assertFalse(bad["exact"])
        none = ps.survey_years({"error": "missing"}, ("2012-13", "2013-14"))
        self.assertEqual(none["missing"], ["2012-13", "2013-14"])
        self.assertFalse(none["exact"])


class TestNamesOnly(unittest.TestCase):
    def test_long_layout_and_no_values(self):
        out = ps.pc.run_text(LONG)
        self.assertEqual(out["product_years"]["by_product"],
                         {"Flatbread - Naan": {"2018-19": 1}, "Tofu": {"2018-19": 1},
                          "Nut Butter - Peanut": {"2014-15": 1}})
        self.assertEqual((out["product_years"]["first"], out["product_years"]["last"]),
                         ("2014-06-10", "2019-03-21"))
        self.assertEqual(out["census"]["components"],
                         {"Phthalate Screen": 3, "Diisononyl phthalate": 1,
                          "Bis(2-ethylhexyl) phthalate": 1})
        self.assertEqual(out["analyte_headers"], [])
        res = dict(out, bytes=150500, md5_matches_portal=True)
        facts = ps.pc.gate_facts(res, ps.TARGETS[0])
        self.assertEqual(facts["layout"], "long")
        self.assertTrue(facts["size_in_band"])
        self.assertFalse(ps.pc.gate_facts(dict(res, bytes=151041), ps.TARGETS[0])["size_in_band"])
        dumped = json.dumps(out)
        for v in ("1.375", "2.625"):
            self.assertNotIn(v, dumped)


if __name__ == "__main__":
    unittest.main(verbosity=2)
