#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for ethyl_carbamate_census.py (no network, no CFIA file read).
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import json
import unittest

import ethyl_carbamate_census as ec
from bpa_series_census import columns_census

TOY = ("Sample ID,Product,Component,Result value,Unit\n"
       "B1,Beer,Ethyl carbamate,ND,ppb\n"
       "B2,Vinegar,Ethyl carbamate,<LOD 2.5,ppb\n"
       "B3,Sake,Ethyl carbamate,15.7,ppb\n")


class TestTargets(unittest.TestCase):
    def test_portal_facts_as_preregistered(self):
        t = {x["name"]: x for x in ec.TARGETS}
        self.assertEqual(set(t), {"ec18", "ec19"})
        self.assertEqual((t["ec18"]["size"], t["ec18"]["md5"], t["ec18"]["samples"]),
                         (71629, "d7d7bf62a3bb275ccec657fb27501fd8", 390))
        self.assertEqual((t["ec19"]["size"], t["ec19"]["md5"], t["ec19"]["samples"]),
                         (58, "e5aab1da6e57c1afa0536e9d92455a6e", 300))
        self.assertFalse(t["ec18"]["stub_check"])
        self.assertTrue(t["ec19"]["stub_check"])
        self.assertEqual(ec.STUB_BYTES, 58)


class TestGateFacts(unittest.TestCase):
    def test_ec18_all_hold(self):
        target = ec.TARGETS[0]
        res = {"bytes": 71629, "size_matches_portal": True, "md5_matches_portal": True,
               "columns": {"samples": 390, "rows": 390},
               "census": {"components": {"Ethyl carbamate": 390}, "units": {"ppb": 390}}}
        f = ec.gate_facts(res, target)
        self.assertTrue(f["size"] and f["md5"] and f["samples_match"])
        self.assertTrue(f["one_analyte"] and f["one_unit"])
        self.assertEqual(f["unit_labels"], ["ppb"])
        self.assertNotIn("not_stub", f)

    def test_ec19_real_file_and_stub(self):
        target = ec.TARGETS[1]
        res = {"bytes": 60000, "size_matches_portal": False, "md5_matches_portal": False,
               "columns": {"samples": 300, "rows": 300},
               "census": {"components": {"Ethyl carbamate": 300}, "units": {"ppb": 299, "": 1}}}
        f = ec.gate_facts(res, target)
        self.assertTrue(f["not_stub"])
        self.assertTrue(f["samples_match"])
        self.assertFalse(f["one_unit"])
        stub = {"bytes": 58, "size_matches_portal": True, "md5_matches_portal": True,
                "columns": {"samples": 0, "rows": 0}, "census": {"error": "missing key column"}}
        g = ec.gate_facts(stub, target)
        self.assertFalse(g["not_stub"])
        self.assertFalse(g["samples_match"])
        self.assertIsNone(g["analyte_labels"])
        self.assertFalse(g["one_analyte"])
        self.assertFalse(g["one_unit"])
        self.assertEqual(g["census_error"], "missing key column")

    def test_column_census_error_is_tolerated(self):
        target = ec.TARGETS[1]
        res = {"bytes": 10, "columns": {"error": "StopIteration: "}, "census": {"error": "x"}}
        f = ec.gate_facts(res, target)
        self.assertIsNone(f["samples"])
        self.assertFalse(f["not_stub"])


class TestNamesOnly(unittest.TestCase):
    def test_values_never_appear(self):
        out = columns_census(TOY)
        self.assertEqual((out["rows"], out["samples"]), (3, 3))
        result = out["columns"][3]
        self.assertTrue(result["value_like"])
        self.assertEqual(result["shapes"], {"token": 2, "number": 1})
        self.assertEqual(result["text_rows"], {"<text with digits>": 1, "ND": 1})
        dumped = json.dumps(out)
        self.assertNotIn("2.5", dumped)
        self.assertNotIn("15.7", dumped)
        product = out["columns"][1]
        self.assertFalse(product["value_like"])
        self.assertEqual(product["text_rows"], {"Beer": 1, "Sake": 1, "Vinegar": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
