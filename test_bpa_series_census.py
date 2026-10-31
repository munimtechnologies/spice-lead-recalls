#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for bpa_series_census.py (no network, no real data). Made with AI agents working
in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import os
import re
import tempfile
import unittest

import bpa_series_census as t

HEADER = "﻿Sample ID,Product Name,Packaging,Result (ppb),Units"
FIXTURE = "\n".join([
    HEADER,
    "S1,Pasta in tomato sauce,Metal can,5.2,ppb",
    "S1,Pasta in tomato sauce,Metal can,ND,ppb",
    "S2,Cream-style corn,Metal can,<1.0,ppb",
    "S3,Apple juice,Plastic,nd 1.0,ppb",
    "S4,Apple juice,,-1,ppb",
    "",
    "S5,V8 juice,Glass,0,ppb,extra",
]) + "\n"


class TestRules(unittest.TestCase):
    def test_targets(self):
        names = [x["name"] for x in t.TARGETS]
        self.assertEqual(names, ["bpa-2009", "bpa-2010", "bpa-2011", "bpa-2012", "bpa-2013",
                                 "bpa-2016", "bpa-2017"])
        self.assertEqual(len({x["resource"] for x in t.TARGETS}), 7)
        self.assertEqual(len({x["dataset"] for x in t.TARGETS}), 7)
        for x in t.TARGETS:
            self.assertTrue(x["md5"] == "" or re.fullmatch(r"[0-9a-f]{32}", x["md5"]), x["name"])
            self.assertGreater(x["size"], 0)
            self.assertTrue(x["path"].endswith(".csv"))
            self.assertNotIn(" ", x["path"])

    def test_sample_column(self):
        self.assertEqual(t.sample_column(HEADER.split(",")), 0)
        self.assertEqual(t.sample_column(["Sample Type", "Date Sampled", "Sample No."]), 2)
        self.assertIsNone(t.sample_column(["Product", "Result"]))

    def test_value_columns(self):
        self.assertTrue(t.is_value_column("Result (ppb)"))
        self.assertTrue(t.is_value_column("LOD"))
        self.assertTrue(t.is_value_column("MaxOfAMOUNT"))
        self.assertFalse(t.is_value_column("Product Name"))
        self.assertFalse(t.is_value_column("Packaging"))


class TestColumns(unittest.TestCase):
    def test_fixture(self):
        c = t.columns_census(FIXTURE)
        self.assertEqual((c["rows"], c["samples"], c["header_width"]), (6, 5, 5))
        self.assertEqual(c["row_widths"], {"5": 5, "6": 1})
        cols = {x["name"]: x for x in c["columns"]}
        self.assertEqual(list(cols), ["Sample ID", "Product Name", "Packaging", "Result (ppb)",
                                      "Units"])
        sid = cols["Sample ID"]
        self.assertTrue(sid["sample_column"])
        self.assertEqual(sid["shapes"], {"token": 6})
        self.assertEqual((sid["text_rows"], sid["distinct_text"]), ({}, 0))
        prod = cols["Product Name"]
        self.assertEqual(prod["text_rows"], {"Pasta in tomato sauce": 2, "Cream-style corn": 1,
                                             "Apple juice": 2, "V8 juice": 1})
        self.assertEqual(prod["text_samples"], {"Pasta in tomato sauce": 1, "Cream-style corn": 1,
                                                "Apple juice": 2, "V8 juice": 1})
        pack = cols["Packaging"]
        self.assertEqual(pack["shapes"], {"token": 5, "blank": 1})
        self.assertEqual(pack["text_rows"], {"Metal can": 3, "Plastic": 1, "Glass": 1})
        self.assertEqual(pack["text_samples"], {"Metal can": 2, "Plastic": 1, "Glass": 1})
        res = cols["Result (ppb)"]
        self.assertTrue(res["value_like"])
        self.assertEqual(res["shapes"], {"number": 2, "token": 2, "lt-number": 1,
                                         "negative-number": 1})
        self.assertEqual(res["text_rows"], {"ND": 1, t.MASKED: 1})
        self.assertEqual(res["text_samples"], {"ND": 1, t.MASKED: 1})
        self.assertEqual(cols["Units"]["text_rows"], {"ppb": 6})
        self.assertEqual(cols["Units"]["text_samples"], {"ppb": 5})

    def test_no_number_is_recorded(self):
        c = t.columns_census(FIXTURE)
        dumped = repr(c)
        for value in ("5.2", "1.0", "-1"):
            self.assertNotIn(value, dumped)

    def test_top_cap_and_no_sample_column(self):
        text = "Product,Result\n" + "".join(f"P{i:03d},ND\n" for i in range(5))
        c = t.columns_census(text, top=3)
        self.assertIsNone(c["samples"])
        prod = c["columns"][0]
        self.assertEqual(prod["distinct_text"], 5)
        self.assertEqual(prod["text_rows"], {"P000": 1, "P001": 1, "P002": 1})
        self.assertIsNone(prod["text_samples"])


class TestRunTarget(unittest.TestCase):
    def test_data_volume_copy(self):
        raw = FIXTURE.encode("utf-8")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "r1.csv"), "wb") as fh:
                fh.write(raw)
            target = {"name": "x", "dataset": "d", "resource": "r1", "path": "x.csv",
                      "size": len(raw), "md5": ""}
            res = t.run_target(target, d)
        self.assertNotIn("error", res)
        self.assertEqual(res["source"], "data-volume")
        self.assertTrue(res["size_matches_portal"])
        self.assertIsNone(res["md5_matches_portal"])
        self.assertIsNone(res["portal_md5"])
        self.assertEqual(res["census"]["error"], "missing key column")
        self.assertEqual(res["columns"]["samples"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
