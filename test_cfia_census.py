#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for cfia_census.py (no network, no real data). Made with AI agents working in
MV2's (Munim, Inc.) name. Code Apache-2.0."""
import os
import re
import tempfile
import unittest

import cfia_census as t

HEADER = ("Sample No. - No. d'echantillon,Region - Region,Commodity,denree,Function,Fonction,"
          "Origin,Origine,Product,Produit,Date Sampled - Date d'echantillonage,Type of Test,"
          "Type d'analyse,Component,Composant,MaxOfAMOUNT,Report Unit - Unite de rapport,"
          "PLAN_CODE")
A = "C2018PAH00001,ATLANTIC,FV,FVPR,Domestic,domestique,CANADA,CANADA,Smoked Fish,Poisson,"
B = ('C2018PAH00003,ONTARIO,FV,FVPR,Import,importe,"UNITED STATES, X","ETATS-UNIS, X",'
     "Tea,The,")
C = "C2018PAH00003D,ONTARIO,FV,FVPR,Import,importe,CHINA,CHINE,Tea,The,"
TAIL = ",ng/g,2018_TS022"
FIXTURE = "\n".join([
    "﻿" + HEADER,
    A + "8-May-18,PAH,HAP,Benzo(a)pyrene,Benzo(a)pyrene,0.01" + TAIL,
    A + "8-May-18,PAH,HAP,Chrysene,Chrysene,<0.005" + TAIL,
    B + "9-May-18,PAH,HAP,Benzo(a)pyrene,Benzo(a)pyrene,ND" + TAIL,
    B + "9-May-18,PAH,HAP,Chrysene,Chrysene," + TAIL,
    B + "9-May-18,PAH,HAP,Chrysene,Chrysene,-0.1" + TAIL,
    C + "9-May-18,PAH,HAP,Benzo(a)pyrene,Benzo(a)pyrene,0" + TAIL,
    C + "9-May-18,PAH,HAP,Chrysene,Chrysene,0" + TAIL,
    "",
]) + "\n"


class TestRules(unittest.TestCase):
    def test_columns(self):
        col = t.find_columns(("﻿" + HEADER).split(","))
        self.assertEqual(col, {"sample": 0, "region": 1, "commodity": 2, "function": 4,
                               "origin": 6, "product": 8, "date": 10, "test": 11,
                               "component": 13, "value": 15, "unit": 16, "plan": 17})

    def test_shape(self):
        cases = {"0.013": "number", "0": "number", "0,5": "number", "<0.01": "lt-number",
                 "< 0.01": "lt-number", "<LOD": "token", "ND": "token", "": "blank",
                 "  ": "blank", "-0.5": "negative-number"}
        for raw, want in cases.items():
            self.assertEqual(t.shape(raw), want, raw)

    def test_decode(self):
        self.assertEqual(t.decode("µg/kg".encode("cp1252")), ("µg/kg", "cp1252"))
        self.assertEqual(t.decode("µg/kg".encode("utf-8")), ("µg/kg", "utf-8-sig"))

    def test_ids(self):
        self.assertTrue(t.ID_RE.match("C2018PAH00001"))
        self.assertEqual(t.ID_RE.match("C2018TMET00039D").groups(), ("00039", "D"))
        self.assertIsNone(t.ID_RE.match("X1"))

    def test_targets(self):
        names = [x["name"] for x in t.TARGETS]
        self.assertEqual(names, ["pah-2019", "bpa-2018", "bpa-2020"])
        self.assertEqual(len({x["resource"] for x in t.TARGETS}), 3)
        for x in t.TARGETS:
            self.assertTrue(re.fullmatch(r"[0-9a-f]{32}", x["md5"]), x["name"])
            self.assertGreater(x["size"], 0)
            self.assertTrue(x["path"].endswith(".csv"))


class TestCensus(unittest.TestCase):
    def test_fixture(self):
        c = t.census(FIXTURE)
        self.assertNotIn("error", c)
        self.assertEqual(c["rows"], 7)
        self.assertEqual(c["components"], {"Benzo(a)pyrene": 3, "Chrysene": 4})
        self.assertEqual(c["shapes"], {"number": 3, "lt-number": 1, "token": 1, "blank": 1,
                                       "negative-number": 1})
        self.assertEqual(c["tokens"], {"ND": 1})
        self.assertEqual(c["units"], {"ng/g": 7})
        self.assertEqual(c["plans"], {"2018_TS022": 7})
        self.assertEqual(c["tests"], {"PAH": 7})
        self.assertEqual(c["regions"], {"ATLANTIC": 2, "ONTARIO": 5})
        self.assertEqual(c["samples"], 3)
        self.assertEqual(c["rows_per_sample"], {"2": 2, "3": 1})
        self.assertEqual(c["repeated_component_samples"], {"C2018PAH00003": ["Chrysene"]})
        self.assertEqual(c["missing_component_samples"], {})
        self.assertEqual(c["mixed_label_samples"], [])
        self.assertEqual(c["products"], {"Smoked Fish": 1, "Tea": 2})
        self.assertEqual(c["product_function"], {"Smoked Fish": {"Domestic": 1},
                                                 "Tea": {"Import": 2}})
        self.assertEqual(c["product_origin_top"]["Tea"], {"UNITED STATES, X": 1, "CHINA": 1})
        self.assertEqual((c["ids_bad"], c["ids_bad_count"], c["id_range"], c["id_gaps"]),
                         ([], 0, [1, 3], 1))
        self.assertEqual(c["ids_dup_suffix"], ["C2018PAH00003D"])
        self.assertEqual(c["product_id_runs"], {"Smoked Fish": [[1, 1]], "Tea": [[3, 3], [3, 3]]})

    def test_bad_ids_capped(self):
        lab = ("P", "C", "Import", "CHINA", "ONTARIO", "1-Jan-19")
        by = {f"X{i:02d}": {"labels": {lab}, "components": ["A"]} for i in range(12)}
        c = t.samples_census(by)
        self.assertEqual(c["ids_bad_count"], 12)
        self.assertEqual(c["ids_bad"], [f"X{i:02d}" for i in range(10)])
        self.assertIsNone(c["id_range"])
        self.assertEqual(c["products"], {"P": 12})
        self.assertEqual(c["product_id_runs"], {"P": []})

    def test_missing_value_column(self):
        c = t.census(HEADER.replace("MaxOfAMOUNT", "Amount").replace("Report Unit", "X") + "\n")
        self.assertEqual(c["error"], "missing key column")


class TestLoad(unittest.TestCase):
    def test_data_volume_copy(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "r1.csv"), "wb") as fh:
                fh.write(b"abc")
            target = {"name": "x", "dataset": "d", "resource": "r1", "path": "x.csv",
                      "size": 3, "md5": "0" * 32}
            self.assertEqual(t.load(target, d), (b"abc", "data-volume"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
