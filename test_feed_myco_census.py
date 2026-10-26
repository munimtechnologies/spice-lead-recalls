#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for feed_myco_census: classifier, column finder and the census shape.

Made with AI agents working in MV2's (Munim, Inc.) name. No network, no data file needed.
"""
import unittest

import feed_myco_census as m

HEADER = ("Fiscal year,System ID,Livestock species,Feed type,Sampled at - Province,"
          "Mycotoxin tested,Test result,Unit,Single ingredient type,ingredient common name")
ROWS = [
    "2000-2001,S1,Poultry,Complete,ON,Deoxynivalenol,<200,ng/g,,",
    "2000-2001,S1,Poultry,Complete,ON,Zearalenone,55,ng/g,,",
    "2001-2002,S2,Swine,Mash,QC,Deoxynivalenol,1200,ng/g,Single,Corn",
    "2001-2002,S2,Swine,Mash,QC,Ochratoxin A,<10,ng/g,Single,Corn",
    "2001-2002,S3,Cattle,Silage,AB,Deoxynivalenol,<200,ng/g,,",
]
SAMPLE_CSV = HEADER + "\n" + "\n".join(ROWS) + "\n"


class TestClassifier(unittest.TestCase):
    def test_blank(self):
        self.assertEqual(m.classify_result(""), "blank")
        self.assertEqual(m.classify_result("   "), "blank")

    def test_censored(self):
        self.assertEqual(m.classify_result("<200"), "censored")
        self.assertEqual(m.classify_result("<0.5"), "censored")

    def test_loq_token_not_censored(self):
        # A literal "<LOQ" string is a token, not a numeric censoring cell.
        self.assertEqual(m.classify_result("<LOQ"), "token")
        self.assertEqual(m.classify_result("ND"), "token")

    def test_numeric_and_zero(self):
        self.assertEqual(m.classify_result("12.5"), "numeric")
        self.assertEqual(m.classify_result("150"), "numeric")
        self.assertEqual(m.classify_result("3,5"), "numeric")  # comma decimal
        self.assertEqual(m.classify_result("0"), "zero")

    def test_bad(self):
        self.assertEqual(m.classify_result("abc"), "bad")
        self.assertEqual(m.classify_result("-1"), "bad")


class TestFindCol(unittest.TestCase):
    def setUp(self):
        self.header = [c.strip() for c in HEADER.split(",")]

    def test_single_needle(self):
        self.assertEqual(m.find_col(self.header, "mycotoxin"), 5)
        self.assertEqual(m.find_col(self.header, "province"), 4)
        self.assertEqual(m.find_col(self.header, "result"), 6)

    def test_two_needles_disambiguate(self):
        self.assertEqual(m.find_col(self.header, "feed", "type"), 3)
        self.assertEqual(m.find_col(self.header, "ingredient", "type"), 8)
        self.assertEqual(m.find_col(self.header, "ingredient", "name"), 9)

    def test_missing(self):
        self.assertIsNone(m.find_col(self.header, "nonexistent"))


class TestCensus(unittest.TestCase):
    def setUp(self):
        self.c = m.census(SAMPLE_CSV)

    def test_shape(self):
        self.assertEqual(self.c["n_columns"], 10)
        self.assertEqual(self.c["n_rows"], 5)
        self.assertEqual(self.c["distinct_system_ids"], 3)

    def test_rows_per_sample(self):
        self.assertEqual(self.c["rows_per_sample_distribution"], {"1": 1, "2": 2})

    def test_result_format(self):
        self.assertEqual(self.c["result_format_kinds"], {"censored": 3, "numeric": 2})

    def test_categorical_counts(self):
        cat = self.c["categorical"]
        self.assertEqual(cat["fiscal_year"]["values"], {"2000-2001": 2, "2001-2002": 3})
        self.assertEqual(cat["mycotoxin"]["values"],
                         {"Deoxynivalenol": 3, "Ochratoxin A": 1, "Zearalenone": 1})
        self.assertEqual(cat["species"]["values"], {"Cattle": 1, "Poultry": 2, "Swine": 2})
        self.assertEqual(cat["unit"]["values"], {"ng/g": 5})
        self.assertEqual(cat["ingredient_name"]["values"], {"": 3, "Corn": 2})


if __name__ == "__main__":
    unittest.main()
