#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Checks every names-only figure stated in docs/fumonisin-2010-0.1.0-census.md and
docs/fumonisin-series-0.1.0-census.md against the census records the sealed jobs wrote
(data/fumonisin_2010_census.json, data/fumonisin_fum11_census.json and
data/fumonisin_fum1218_census.json). The records hold labels, counts and cell shapes only; no
result value. Standard library only, no network.
    python -m unittest -v test_fumonisin_census_notes
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def column(rec, name):
    for c in rec["columns"]["columns"]:
        if c["name"] == name:
            return c
    raise KeyError(name)


def add(dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return out


GRAINS = ("amaranth", "arrowroot", "barley", "buckwheat", "corn", "kamut", "millet", "oat",
          "quinoa", "rice", "rye", "spelt", "teff", "triticale", "wheat")


def grain_of(label):
    low = label.lower()
    if low in ("popcorn", "taco"):
        return "corn"
    for g in GRAINS:
        if re.search(r"(?<![a-z])" + g, low):
            return g
    return None


def is_tea(p):
    return p == "Beverage - Tea" or p.startswith("Tea - ")


B_SOY = {"Bean - Soy", "Beverage - Soy", "Flour - Soy", "Infant Formula - Soy", "Soy Products",
         "Tofu", "Meat Alternative"}


class File2010(unittest.TestCase):
    rec = load("fumonisin_2010_census.json")

    def test_gate_and_c1_c3_c4(self):
        g = self.rec["gate_facts"]
        self.assertTrue(g["G"] and g["md5"] and g["size_in_band"])
        self.assertEqual((g["bytes"], g["samples"]), (87748, 277))
        self.assertFalse(g["C1_samples_276"])
        self.assertTrue(g["C3_subset_of_B1_B2_total"] and g["C3_no_B3"] and g["C4_all_ppb_scale"])
        self.assertEqual(self.rec["census"]["units"], {"ng/g": 554})
        self.assertEqual(self.rec["census"]["rows_per_sample"], {"2": 277})

    def test_c2_label_map(self):
        p = self.rec["census"]["products"]
        self.assertEqual(len(p), 9)
        self.assertEqual(sum(p.values()), 277)
        exact = {"Cereal - Corn": 56, "Popcorn": 30, "Corn": 27, "Corn Starch": 23,
                 "Flour - Corn": 21}
        for k, v in exact.items():
            self.assertEqual(p[k], v, k)
        self.assertEqual(p["Cornmeal"], 34 + 7)
        block = p["Chips - Corn"] + p["Bakery Product - Tortilla/Wrap/Pita"] + p["Corn Products"]
        self.assertEqual((p["Chips - Corn"], p["Bakery Product - Tortilla/Wrap/Pita"],
                          p["Corn Products"]), (42, 15, 22))
        self.assertEqual((block, 45 + 21 + 10 + 2), (79, 78))

    def test_function_origin_dates(self):
        self.assertEqual(column(self.rec, "Function")["text_samples"],
                         {"Domestic": 138, "Import": 139})
        o = column(self.rec, "Origin")["text_samples"]
        self.assertEqual((o["CANADA"], o["UNITED STATES"], o["UNKNOWN"], sum(o.values())),
                         (138, 94, 35, 277))
        py = self.rec["product_years"]
        self.assertEqual((py["by_year"], py["first"], py["last"]),
                         ({"2010-11": 277}, "2010-10-03", "2011-03-11"))


class File2011(unittest.TestCase):
    rec = load("fumonisin_fum11_census.json")
    CORN = {"Cereal - Corn", "Chips - Corn", "Corn", "Corn - Sweet - Organic", "Corn Products",
            "Cornmeal", "Flour - Corn"}
    SOY = {"Bean - Soy", "Beverage - Soy", "Flour - Soy", "Infant Formula - Soy", "Misc - Soy",
           "Soy Products"}
    OTHER = {"Cereal - Other", "Misc", "Protein Powder"}

    def test_gate_and_counts(self):
        g = self.rec["gate_facts"]
        self.assertTrue(g["G"])
        self.assertEqual((g["bytes"], g["samples"]), (158076, 498))
        self.assertFalse(g["C1_samples"])
        self.assertTrue(g["C3_subset_of_B1_B2_total"] and g["C3_no_B3"] and g["C4_all_ppb_scale"])

    def test_a_c2_map(self):
        p = self.rec["census"]["products"]
        self.assertEqual(set(p), self.CORN | self.SOY | self.OTHER)
        self.assertEqual(sum(p[k] for k in self.CORN), 262)
        self.assertEqual(sum(p[k] for k in self.SOY), 191)
        self.assertEqual(sum(p[k] for k in self.OTHER), 45)
        self.assertEqual(p["Cereal - Other"], 43)
        self.assertEqual(self.rec["keywords"]["Product"]["corn"], 262)
        self.assertEqual(self.rec["keywords"]["Product"]["soy"], 191)

    def test_years(self):
        py = self.rec["product_years"]
        self.assertEqual(py["by_year"], {"2010-11": 1, "2011-12": 497})
        self.assertEqual(py["by_product"]["Cornmeal"], {"2010-11": 1, "2011-12": 43})
        self.assertEqual((py["first"], py["last"]), ("2011-02-09", "2012-03-28"))


class File2012to2018(unittest.TestCase):
    rec = load("fumonisin_fum1218_census.json")

    def products(self):
        return self.rec["census"]["products"]

    def test_gate_and_counts(self):
        g = self.rec["gate_facts"]
        self.assertTrue(g["G"])
        self.assertEqual((g["bytes"], g["samples"]), (1402889, 4320))
        self.assertFalse(g["C1_samples"])
        self.assertTrue(g["C3_subset_of_B1_B2_total"] and g["C3_no_B3"] and g["C4_all_ppb_scale"])
        self.assertEqual(len(self.rec["census"]["ids_dup_suffix"]), 16)

    def test_b_c2_groups(self):
        p = self.products()
        self.assertEqual(len(p), 66)
        tea = sum(v for k, v in p.items() if is_tea(k))
        soy = sum(p[k] for k in B_SOY)
        self.assertEqual((tea, soy, 4320 - tea - soy), (425, 182, 3713))
        self.assertEqual(p["Tea - White"], 24)
        # Table A2's soy rows that the labels name one to one.
        self.assertEqual([p[k] for k in ("Bean - Soy", "Beverage - Soy", "Flour - Soy",
                                         "Infant Formula - Soy", "Tofu", "Meat Alternative")],
                         [40, 40, 29, 20, 30, 9])
        self.assertEqual(p["Soy Products"], 5 + 1 + 3 + 1 + 4)

    def test_grain_named_labels(self):
        p = self.products()
        named, unnamed = {}, {}
        for k, v in p.items():
            if is_tea(k) or k in B_SOY:
                continue
            g = grain_of(k)
            if g is None:
                unnamed[k] = v
            else:
                named[g] = named.get(g, 0) + v
        self.assertEqual(named, {"amaranth": 55, "arrowroot": 65, "barley": 130, "buckwheat": 128,
                                 "corn": 1230, "kamut": 132, "millet": 135, "oat": 30,
                                 "quinoa": 136, "rice": 108, "rye": 121, "spelt": 121,
                                 "teff": 59, "triticale": 1})
        self.assertEqual(sum(named.values()), 2451)
        self.assertEqual(sum(unnamed.values()), 1262)
        self.assertEqual(len(unnamed), 14)
        kw = self.rec["keywords"]["Product"]
        self.assertEqual(kw["corn"], 1230 - p["Popcorn"] - p["TACO"])
        self.assertNotIn("wheat", kw)
        self.assertNotIn("organic", kw)

    def test_function_split(self):
        pf = self.rec["census"]["product_function"]
        tea = add(v for k, v in pf.items() if is_tea(k))
        soy = add(pf[k] for k in B_SOY)
        grain = add(v for k, v in pf.items() if not is_tea(k) and k not in B_SOY)
        self.assertEqual(tea, {"Domestic": 62, "Import": 207, "Unknown": 156})
        self.assertEqual(soy, {"Domestic": 61, "Import": 83, "Unknown": 38})
        self.assertEqual(grain, {"Domestic": 734, "Import": 1849, "Unknown": 1130})

    def test_years(self):
        py = self.rec["product_years"]
        by = py["by_product"]
        self.assertEqual(py["by_year"], {"2012-13": 605, "2013-14": 715, "2014-15": 750,
                                         "2015-16": 750, "2016-17": 750, "2017-18": 750})
        self.assertEqual(by["Teff Products"],
                         {"2012-13": 7, "2013-14": 7, "2014-15": 10, "2015-16": 35})
        rice = add(by[k] for k in by if grain_of(k) == "rice")
        self.assertEqual(rice, {"2012-13": 9, "2015-16": 99})
        oat = add(by[k] for k in by if grain_of(k) == "oat")
        self.assertNotIn("2017-18", oat)
        soy = add(by[k] for k in B_SOY)
        self.assertEqual(soy, {"2012-13": 91, "2013-14": 91})
        tea = add(v for k, v in by.items() if is_tea(k))
        self.assertEqual(tea, {"2016-17": 425})
        corn = add(v for k, v in by.items()
                   if not is_tea(k) and k not in B_SOY and grain_of(k) == "corn")
        self.assertEqual(corn, {"2012-13": 272, "2013-14": 264, "2014-15": 201, "2017-18": 493})
        self.assertEqual(by["Infant Food - Cereal"]["2012-13"], 4)
        plans = self.rec["census"]["plans"]
        self.assertEqual(plans["2012_TS002"], 2 * 605)

    def test_appendix_b_one_to_one(self):
        p = self.products()
        self.assertEqual((p["Flour - Corn"], p["Corn Starch"], p["Popcorn"], p["Bran - Corn"]),
                         (276, 251, 25, 2))
        self.assertEqual(p["Cornmeal"], 336 + 1)
        self.assertEqual(p["Infant Food (non-cereal)"], 50)


if __name__ == "__main__":
    unittest.main(verbosity=2)
