#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for food_colours_census.py (no network, no CFIA file read).
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import json
import unittest

import food_colours_census as fc
from bpa_series_census import columns_census

TOY = ("Sample ID,Product,Colour,Result value,Unit\n"
       "A1,Candy,Tartrazine,ND,ppm\n"
       "A1,Candy,Allura Red,<LOQ 0.13,ppm\n"
       "A2,Oil,Sudan I,1.5,ppm\n")


class TestTargets(unittest.TestCase):
    def test_portal_facts_as_preregistered(self):
        t = {x["name"]: x for x in fc.TARGETS}
        self.assertEqual(set(t), {"c18", "c09"})
        self.assertEqual((t["c18"]["size"], t["c18"]["md5"], t["c18"]["samples"]),
                         (3771543, "7651427618a70aa3ad2a51ab90bcae8c", 399))
        self.assertEqual((t["c09"]["size"], t["c09"]["md5"], t["c09"]["samples"]),
                         (33724, "dc558d850720b90610da2c75424d1cd7", 100))
        self.assertEqual(t["c18"]["max_colours"], 43)
        self.assertIsNone(t["c09"]["max_colours"])


class TestGateFacts(unittest.TestCase):
    def test_c18(self):
        target = fc.TARGETS[0]
        res = {"size_matches_portal": True, "md5_matches_portal": True,
               "columns": {"samples": 399, "rows": 17000},
               "census": {"components": {"colour %d" % i: 1 for i in range(43)}}}
        f = fc.gate_facts(res, target)
        self.assertTrue(f["size"] and f["md5"] and f["samples_match"])
        self.assertEqual(f["colour_labels"], 43)
        self.assertTrue(f["colours_within_max"])
        self.assertNotIn("s3_fewer_than_2000_rows", f)
        res["census"]["components"]["one more"] = 1
        self.assertFalse(fc.gate_facts(res, target)["colours_within_max"])

    def test_c09_and_census_error(self):
        target = fc.TARGETS[1]
        res = {"size_matches_portal": True, "md5_matches_portal": False,
               "columns": {"samples": 99, "rows": 1500},
               "census": {"error": "missing key column"}}
        f = fc.gate_facts(res, target)
        self.assertFalse(f["md5"])
        self.assertFalse(f["samples_match"])
        self.assertIsNone(f["colour_labels"])
        self.assertEqual(f["census_error"], "missing key column")
        self.assertTrue(f["s3_fewer_than_2000_rows"])
        self.assertNotIn("colours_within_max", f)


class TestNamesOnly(unittest.TestCase):
    def test_values_never_appear(self):
        out = columns_census(TOY)
        self.assertEqual((out["rows"], out["samples"]), (3, 2))
        result = out["columns"][3]
        self.assertTrue(result["value_like"])
        self.assertEqual(result["shapes"], {"token": 2, "number": 1})
        self.assertEqual(result["text_rows"], {"<text with digits>": 1, "ND": 1})
        dumped = json.dumps(out)
        self.assertNotIn("0.13", dumped)
        self.assertNotIn("1.5", dumped)
        colour = out["columns"][2]
        self.assertFalse(colour["value_like"])
        self.assertEqual(colour["text_rows"], {"Allura Red": 1, "Sudan I": 1, "Tartrazine": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
