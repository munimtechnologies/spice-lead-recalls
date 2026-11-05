#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for phthalates_census.py (no network, no CFIA file read).
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import json
import unittest

import phthalates_census as pc

WIDE = ("Sample ID,Product,Origin,Date Sampled,BBP (ppm),DBP (ppm),DNOP (ppm),DEHP (ppm),"
        "DINP (ppm),DIDP (ppm),Total Phthalates (ppm)\n"
        "C2020PHTH001,Oil - Olive,Import,2020-05-04,ND,ND,ND,1.375,ND,ND,1.375\n"
        "C2020PHTH002,Salad Dressing,Domestic,2021-03-31,ND,2.625,ND,ND,ND,ND,2.625\n"
        "C2020PHTH003,RTE Meal - Children,Unknown,2020-04-01,ND,ND,ND,ND,ND,ND,ND\n")


class TestTargets(unittest.TestCase):
    def test_portal_facts_as_preregistered(self):
        (t,) = pc.TARGETS
        self.assertEqual(t["dataset"], "4ae4c2b3-e1b7-451a-b313-02e51d73da73")
        self.assertEqual(t["resource"], "960252a3-4b35-44ef-9e8d-46ed1b0dd61c")
        self.assertEqual((t["md5"], t["samples"], t["size_band"]),
                         ("612780be14a4a571044d93aaa27f99f2", 500, (113000, 118000)))
        self.assertIsNone(t["size"])
        self.assertTrue(t["path"].endswith("vegetable-fats-and-oils.csv"))
        self.assertEqual(pc.PHTHALATES, ("BBP", "DBP", "DNOP", "DEHP", "DINP", "DIDP"))


class TestHeaders(unittest.TestCase):
    def test_wide_header(self):
        found = pc.analyte_headers(pc.header_of(WIDE))
        self.assertEqual([i for i, _, _ in found], [4, 5, 6, 7, 8, 9, 10])
        self.assertEqual([n for _, _, n in found][:6],
                         [["BBP"], ["DBP"], ["DNOP"], ["DEHP"], ["DINP"], ["DIDP"]])
        self.assertEqual(found[6], [10, "Total Phthalates (ppm)", []])

    def test_no_false_names(self):
        self.assertEqual(pc.analyte_headers(["Sample No.", "Product", "Date Sampled",
                                             "Result", "Unit", "DBPX", "ADEHP"]), [])
        self.assertEqual(pc.analyte_headers(["di-isobutyl phthalate (DIBP)"]),
                         [[0, "di-isobutyl phthalate (DIBP)", ["DIBP"]]])
        self.assertEqual(pc.analyte_headers(["Phtalates totaux / Total"]),
                         [[0, "Phtalates totaux / Total", []]])


class TestLayout(unittest.TestCase):
    def test_kinds(self):
        hdr = pc.analyte_headers(pc.header_of(WIDE))
        self.assertEqual(pc.layout({"error": "missing key column"}, hdr), "wide")
        self.assertEqual(pc.layout({"components": {"DEHP": 500, "DBP": 500}}, []), "long")
        self.assertEqual(pc.layout({"components": {"Total phthalates": 500}}, []), "single")
        self.assertEqual(pc.layout({"error": "missing key column"}, []), "unknown")


class TestGateFacts(unittest.TestCase):
    def test_all_hold_and_failures(self):
        target = pc.TARGETS[0]
        hdr = pc.analyte_headers(pc.header_of(WIDE))
        res = {"bytes": 115321, "md5_matches_portal": True,
               "columns": {"samples": 500, "rows": 500},
               "census": {"error": "missing key column"}, "analyte_headers": hdr}
        f = pc.gate_facts(res, target)
        self.assertTrue(f["size_in_band"] and f["md5"] and f["samples_match"])
        self.assertEqual(f["layout"], "wide")
        self.assertTrue(f["six_named_in_header"])
        self.assertEqual(f["header_phthalates"], ["BBP", "DBP", "DEHP", "DIDP", "DINP", "DNOP"])
        self.assertIsNone(f["component_labels"])
        self.assertEqual(f["census_error"], "missing key column")
        bad = {"bytes": 120000, "columns": {"error": "x"}, "census": {"error": "x"}}
        g = pc.gate_facts(bad, target)
        self.assertFalse(g["size_in_band"] or g["samples_match"] or g["six_named_in_header"])
        self.assertIsNone(g["samples"])
        self.assertEqual(g["layout"], "unknown")
        self.assertFalse(pc.gate_facts({"bytes": None}, target)["size_in_band"])


class TestRunText(unittest.TestCase):
    def test_names_only(self):
        out = pc.run_text(WIDE)
        self.assertEqual(out["product_years"]["by_product"],
                         {"Oil - Olive": {"2020-21": 1}, "Salad Dressing": {"2020-21": 1},
                          "RTE Meal - Children": {"2020-21": 1}})
        self.assertEqual((out["product_years"]["first"], out["product_years"]["last"]),
                         ("2020-04-01", "2021-03-31"))
        self.assertEqual((out["columns"]["rows"], out["columns"]["samples"]), (3, 3))
        dumped = json.dumps(out)
        for v in ("1.375", "2.625"):
            self.assertNotIn(v, dumped)


if __name__ == "__main__":
    unittest.main(verbosity=2)
