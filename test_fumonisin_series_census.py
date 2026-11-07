#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for fumonisin_series_census.py (no network, no CFIA file read).
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import json
import unittest

import fumonisin_series_census as fs

TEXT = ("Sample ID,Product,Grain,Organic,Origin,Date Sampled,Component,Result,Unit\n"
        "S1,Teff Flour,Teff,Organic,Imported,2015-06-01,Fumonisin B1,12.5,ppb\n"
        "S1,Teff Flour,Teff,Organic,Imported,2015-06-01,Fumonisin B2,ND,ppb\n"
        "S2,Rice Cereal,Rice,Conventional,Domestic,2012-05-01,Fumonisin B1,ND,ppb\n"
        "S3,Black Tea,,Conventional,Unknown,2016-07-01,Fumonisin B1,43.21,ppb\n")


class TestTargets(unittest.TestCase):
    def test_portal_facts_as_preregistered(self):
        a, b = fs.TARGETS
        self.assertEqual((a["name"], a["dataset"], a["resource"], a["md5"], a["samples"]),
                         ("fum11", "e5906422-e8bf-498b-972e-faf2b688aa97",
                          "fe5490e6-35c6-4175-be9d-8b679548784d",
                          "9f6fddeb2448a199d1beae925a5f3a96", 454))
        self.assertEqual((b["name"], b["dataset"], b["resource"], b["md5"], b["samples"]),
                         ("fum1218", "449c63d9-c545-4cce-b907-e32840967873",
                          "df04bd3f-d591-49dc-91c7-0e498b74f22f",
                          "6c87fb0bc35b3fc0cea0d3bd2e93e97b", 4261))
        self.assertEqual(a["size_band"], (157696, 158720))
        self.assertEqual(b["size_band"], (1402880, 1403904))
        for t, years in ((a, "2011-2012"), (b, "2012-2018")):
            self.assertIsNone(t["size"])
            self.assertTrue(t["path"].startswith(f"chem_ts_{years}_fumonisins_in_selected_foods"))
            self.assertTrue(t["path"].endswith("_fumonisines_dans_des_aliments_s.csv"))


class TestNamesOnly(unittest.TestCase):
    def test_keyword_samples(self):
        ks = fs.keyword_samples(TEXT)
        self.assertEqual(ks["Product"]["teff"], 1)
        self.assertEqual(ks["Grain"]["teff"], 1)
        self.assertEqual(ks["Product"]["rice"], 1)
        self.assertEqual(ks["Product"]["cereal"], 1)
        self.assertEqual(ks["Product"]["black tea"], 1)
        self.assertEqual(ks["Product"]["tea"], 1)
        self.assertEqual(ks["Organic"], {"conventional": 2, "organic": 1})
        self.assertNotIn("Sample ID", ks)
        self.assertNotIn("Result", ks)
        self.assertNotIn("Origin", ks)

    def test_keyword_boundaries(self):
        text = ("Sample ID,Product,Component,Result,Unit\n"
                "S1,Goat Cheese,Fumonisin B1,1,ppb\n"
                "S2,Oatmeal,Fumonisin B1,1,ppb\n"
                "S3,Price Check,Fumonisin B1,1,ppb\n")
        ks = fs.keyword_samples(text)
        self.assertEqual(ks["Product"], {"oat": 1})

    def test_run_text_reads_no_values(self):
        out = fs.run_text(TEXT)
        self.assertTrue(all(out["roles"][k] is not None for k in fs.ROLES))
        self.assertEqual(out["census"]["components"], {"Fumonisin B1": 3, "Fumonisin B2": 1})
        dumped = json.dumps(out)
        for v in ("12.5", "43.21"):
            self.assertNotIn(v, dumped)

    def test_gate_facts(self):
        out = fs.run_text(TEXT)
        a, b = fs.TARGETS
        res = dict(out, bytes=158000, md5_matches_portal=True)
        facts = fs.gate_facts(res, a)
        self.assertTrue(facts["G"])
        self.assertFalse(facts["C1_samples"])
        self.assertTrue(facts["C3_subset_of_B1_B2_total"])
        self.assertTrue(facts["C3_no_B3"])
        self.assertTrue(facts["C4_all_ppb_scale"])
        for size, inside in ((157696, False), (157697, True), (158720, True), (158721, False)):
            self.assertEqual(fs.gate_facts(dict(res, bytes=size), a)["size_in_band"], inside)
        for size, inside in ((1402880, False), (1402881, True), (1403904, True),
                             (1403905, False)):
            self.assertEqual(fs.gate_facts(dict(res, bytes=size), b)["size_in_band"], inside)
        self.assertFalse(fs.gate_facts(dict(res, md5_matches_portal=False), a)["G"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
