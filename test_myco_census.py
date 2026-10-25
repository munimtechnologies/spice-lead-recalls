# SPDX-License-Identifier: Apache-2.0
"""Offline tests for myco_census: label counts are right and no result value ever leaks."""
import csv
import io
import json
import unittest

import myco_census as mc

HEADER = ["Sample No. – No. d’échantillon", "Function", "Fonction", "Product", "Produit",
          "Date Sampled – Date d’échantillonage", "Type of Test", "Component", "Amount",
          "Unit – Unité", "Plan Code – Code du régime"]
ROWS = [
    ["S1", "Domestic", "Domestique", "Wine", "Vin", "2010-12-14", "VOMITOXIN", "Deoxynivalenol",
     "0", "ng/g", "P1"],
    ["S1", "Domestic", "Domestique", "Wine", "Vin", "2010-12-14", "OCHRATOXIN", "Ochratoxin A",
     "123.456", "ng/g", "P1"],
    ["S2", "Import", "Importé", "Beer", "Bière", "2011-01-05", "VOMITOXIN", "Deoxynivalenol",
     "51", "ng/g", "P1"],
    ["S2", "Import", "Importé", "Beer", "Bière", "2011-01-05", "OCHRATOXIN", "Ochratoxin A",
     "<0.04", "ng/g", "P1"],
]
FEED_HEADER = ["Fiscal Year", "System ID", "Target Species", "Feed Type", "Ingredient Type",
               "Ingredient Common Name", "Sampled at - Province", "Mycotoxin", "Test Result",
               "Unit"]
FEED_ROWS = [
    ["2005-2006", "A1", "Swine", "Complete", "Grain", "Corn", "ON", "Deoxynivalenol", "<0.1",
     "mg/kg"],
    ["2005-2006", "A1", "Swine", "Complete", "Grain", "Corn", "ON", "Zearalenone", "77.7",
     "µg/kg"],
    ["2006-2007", "A2", "Cattle", "Supplement", "Grain", "Wheat", "AB", "Deoxynivalenol", "1.9",
     "mg/kg"],
]


def text_of(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


class TestRoles(unittest.TestCase):
    def test_bilingual_headers(self):
        roles = [mc.role(h) for h in HEADER]
        self.assertEqual(roles, ["sample", "label:Function", "french", "label:Product", "french",
                                 "date", "label:Type of Test", "label:Component", "value",
                                 "label:Unit", "label:Plan Code"])

    def test_feed_headers(self):
        roles = [mc.role(h) for h in FEED_HEADER]
        self.assertEqual(roles, ["label:Fiscal Year", "sample", "label:Target Species",
                                 "label:Feed Type", "label:Ingredient Type",
                                 "label:Ingredient Common Name", "label:Sampled at",
                                 "label:Mycotoxin", "value", "label:Unit"])

    def test_classify(self):
        self.assertEqual(mc.classify(""), "blank")
        self.assertEqual(mc.classify("<0.04"), "lt")
        self.assertEqual(mc.classify("ND"), "nd_token")
        self.assertEqual(mc.classify("0"), "zero")
        self.assertEqual(mc.classify("0,0"), "zero")
        self.assertEqual(mc.classify("1,5"), "numeric_comma")
        self.assertEqual(mc.classify("2.5"), "numeric")
        self.assertEqual(mc.classify("-1"), "bad")
        self.assertEqual(mc.classify("trace"), "bad")


class TestUrlsAndScope(unittest.TestCase):
    def test_relative_url_made_absolute(self):
        rel = "/data/dataset/d17f/resource/7e3c/download/x.csv"
        self.assertEqual(mc.absolute(rel),
                         "https://open.canada.ca/data/dataset/d17f/resource/7e3c/download/x.csv")
        full = "https://active.inspection.gc.ca/opengov/eng/open-data/x.csv"
        self.assertEqual(mc.absolute(full), full)

    def test_scope(self):
        cfia = "Canadian Food Inspection Agency | Agence canadienne d'inspection des aliments"
        self.assertTrue(mc.wanted(cfia, "Food Safety Action Plan Targeted Survey - DON"))
        self.assertFalse(mc.wanted(cfia, "National Chemical Residue Monitoring Program and "
                                         "Chemistry Food Safety Oversight Program Annual Report"))
        self.assertFalse(mc.wanted("Health Canada | Santé Canada", "Total Diet Study - OTA"))


class TestCensus(unittest.TestCase):
    def setUp(self):
        self.c = mc.census_text(text_of(HEADER, ROWS))

    def test_shape(self):
        self.assertEqual(self.c["n_rows"], 4)
        self.assertEqual(self.c["distinct_samples"], 2)
        self.assertEqual(self.c["rows_per_sample"], {"2": 2})
        self.assertEqual(self.c["dates_by_plan"], {"P1": ["2010-12-14", "2011-01-05"]})

    def test_labels(self):
        self.assertEqual(self.c["labels"]["Product"], {"Beer": 2, "Wine": 2})
        self.assertEqual(self.c["labels"]["Unit – Unité"], {"ng/g": 4})
        self.assertEqual(self.c["tuples"]["Wine | P1 | Ochratoxin A"], 1)
        self.assertEqual(self.c["other_columns_distinct"]["Fonction"], 2)

    def test_value_format_only(self):
        (v,) = self.c["value_columns"]
        self.assertEqual(v["non_numeric_kinds"], {"lt": 1})
        self.assertEqual(v["numeric_cells"], 3)
        self.assertTrue(v["literal_zero_present"])
        self.assertEqual(v["distinct_nonzero_strings"], 2)
        self.assertEqual(v["max_rows_sharing_one_nonzero_string"], 1)

    def test_no_value_leaks(self):
        dumped = json.dumps(self.c, ensure_ascii=False)
        self.assertNotIn("123.456", dumped)
        self.assertNotIn("<0.04", dumped)


class TestFeedCensus(unittest.TestCase):
    def setUp(self):
        self.c = mc.census_text(text_of(FEED_HEADER, FEED_ROWS))

    def test_feed_shape(self):
        self.assertEqual(self.c["distinct_samples"], 2)
        self.assertEqual(self.c["rows_per_sample"], {"2": 1, "1": 1})
        self.assertEqual(self.c["labels"]["Mycotoxin"], {"Deoxynivalenol": 2, "Zearalenone": 1})
        self.assertEqual(self.c["tuples"]["Corn | 2005-2006 | Zearalenone"], 1)
        (v,) = self.c["value_columns"]
        self.assertEqual(v["column"], "Test Result")
        self.assertEqual(v["non_numeric_kinds"], {"lt": 1})
        self.assertEqual(v["numeric_cells"], 2)

    def test_feed_no_value_leaks(self):
        dumped = json.dumps(self.c, ensure_ascii=False)
        self.assertNotIn("77.7", dumped)
        self.assertNotIn("<0.1", dumped)
        self.assertNotIn("1.9", dumped)


if __name__ == "__main__":
    unittest.main()
