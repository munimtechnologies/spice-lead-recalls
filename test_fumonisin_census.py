#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for fumonisin_census.py (no network, no CFIA file read).
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import json
import unittest

import fumonisin_census as fc

LONG = ("Sample ID,Product,Origin,Date Sampled,Component,Result,Unit\n"
        "C2010FUM0001,Corn Meal,Domestic,2010-05-12,Fumonisin B1,123.456,ppb\n"
        "C2010FUM0001,Corn Meal,Domestic,2010-05-12,Fumonisin B2,78.9012,ppb\n"
        "C2010FUM0002,Popcorn,Import,2011-02-03,Fumonisin B1,ND,ppb\n"
        "C2010FUM0003,Corn Grits,Unknown,2010-11-30,Total Fumonisins,4567.891,ppb\n")


class TestTarget(unittest.TestCase):
    def test_portal_facts_as_preregistered(self):
        t = fc.TARGET
        self.assertEqual((t["dataset"], t["resource"], t["md5"], t["samples"]),
                         ("5ac4ed9e-9dc4-4c3c-9a2b-e99530fbda13",
                          "48123e67-3a23-44f3-8cf1-ef8054ca1766",
                          "219641dd2317367eb87069eef88a88b6", 276))
        self.assertIsNone(t["size"])
        self.assertEqual(t["size_band"], (87040, 88064))
        self.assertTrue(t["path"].startswith("chem_ts_2010-2011_fumonisins_in_selected_foods"))
        self.assertTrue(t["path"].endswith("_fumonisines_dans_des_aliments_s.csv"))

    def test_rounded_up_band_fits_known_files(self):
        # Portal sizes and true byte counts of four files read earlier in the series.
        for kib, size in ((115, 117529), (58, 58972), (147, 149790), (1259, 1288434)):
            lo, hi = fc.kib_band_up(kib)
            self.assertTrue(lo < size <= hi, (kib, size))


class TestKinds(unittest.TestCase):
    def test_analyte_kind(self):
        cases = {"Fumonisin B1": "B1", "Fumonisin B2": "B2", "Fumonisin B3": "B3",
                 "FB1": "B1", "fumonisine B2": "B2", "Total Fumonisins": "total",
                 "Total fumonisins (B1+B2)": "total", "Moisture": "other",
                 "Total": "other"}
        for label, kind in cases.items():
            self.assertEqual(fc.analyte_kind(label), kind, label)

    def test_unit_kind(self):
        cases = {"ppb": "ppb", "PPB": "ppb", "ng/g": "ppb", "µg/kg": "ppb", "ug/kg": "ppb",
                 "ppm": "ppm", "µg/g": "ppm", "mg/kg": "ppm", "%": "other", "n/a": "other"}
        for unit, kind in cases.items():
            self.assertEqual(fc.unit_kind(unit), kind, unit)

    def test_analyte_headers(self):
        header = ["Sample ID", "Product", "Fumonisin B1 (ppb)", "FB2", "Total Fumonisins", "Unit"]
        self.assertEqual(fc.analyte_headers(header),
                         [[2, "Fumonisin B1 (ppb)", "B1"], [3, "FB2", "B2"],
                          [4, "Total Fumonisins", "total"]])


class TestNamesOnly(unittest.TestCase):
    def test_long_layout_and_no_values(self):
        out = fc.run_text(LONG)
        self.assertEqual(out["census"]["components"],
                         {"Fumonisin B1": 2, "Fumonisin B2": 1, "Total Fumonisins": 1})
        self.assertEqual(out["product_years"]["by_product"],
                         {"Corn Meal": {"2010-11": 1}, "Popcorn": {"2010-11": 1},
                          "Corn Grits": {"2010-11": 1}})
        self.assertEqual((out["product_years"]["first"], out["product_years"]["last"]),
                         ("2010-05-12", "2011-02-03"))
        self.assertTrue(all(out["roles"][k] is not None for k in fc.ROLES))
        self.assertEqual(out["analyte_headers"], [])
        dumped = json.dumps(out)
        for v in ("123.456", "78.9012", "4567.891"):
            self.assertNotIn(v, dumped)

    def test_gate_facts(self):
        out = fc.run_text(LONG)
        res = dict(out, bytes=87500, md5_matches_portal=True)
        facts = fc.gate_facts(res)
        self.assertTrue(facts["G"])
        self.assertEqual(facts["component_kinds"],
                         {"Fumonisin B1": "B1", "Fumonisin B2": "B2", "Total Fumonisins": "total"})
        self.assertTrue(facts["C3_subset_of_B1_B2_total"])
        self.assertTrue(facts["C3_no_B3"])
        self.assertEqual(facts["unit_kinds"], {"ppb": "ppb"})
        self.assertTrue(facts["C4_all_ppb_scale"])
        self.assertFalse(facts["C1_samples_276"])
        for size, inside in ((87040, False), (87041, True), (88064, True), (88065, False)):
            self.assertEqual(fc.gate_facts(dict(res, bytes=size))["size_in_band"], inside, size)
        self.assertFalse(fc.gate_facts(dict(res, md5_matches_portal=False))["G"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
