#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Report arithmetic of docs/fumonisin-series-0.1.0-prereg.md (items R1-R12 and the bounds of
B-V6 and B-V7), from figures copied from two CFIA report pages. No file is read and no network
is used: these checks need only the printed reports.

Sources (inspection.canada.ca): "Fumonisins in grain-based foods, soy products and teas, April 1,
2012 to March 31, 2018" (modified 2024-06-20) and "2011-2012 Fumonisins in Corn-Based and
Soy-Based Products" (modified 2018-09-04).
    python -m unittest -v test_fumonisin_series_prereg
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import unittest

# Table 1: domestic, imported, unspecified, total.
TABLE1 = {"grain": (721, 1770, 1159, 3650), "soy": (64, 83, 38, 185),
          "tea": (61, 171, 194, 426), "total": (846, 2024, 1391, 4261)}
# Table 2: samples, positives, printed share, printed average (ppb).
TABLE2 = {"grain": (3650, 1073, 29, 365), "soy": (185, 2, 1, 36), "tea": (426, 1, 0.2, 43),
          "total": (4261, 1076, 25, 364)}
# Table 3: samples, positives.
TABLE3 = {"amaranth": (88, 2), "arrowroot": (66, 0), "barley": (134, 2), "buckwheat": (131, 2),
          "corn": (1688, 1030), "kamut": (148, 0), "millet": (137, 1), "mixed grains": (5, 0),
          "oat": (124, 14), "quinoa": (141, 1), "rice": (189, 5), "rye": (136, 0),
          "spelt": (129, 2), "teff": (11, 1), "triticale": (1, 0), "wheat": (456, 13)}
# Tables 4-14, CFIA rows only: year -> (samples, positives).
YEARS = {
    "amaranth": {2015: (47, 0), 2014: (17, 0), 2013: (12, 1), 2012: (12, 1)},
    "barley": {2016: (1, 0), 2015: (75, 2), 2014: (30, 0), 2013: (18, 0), 2012: (10, 0)},
    "buckwheat": {2017: (1, 1), 2015: (70, 0), 2014: (30, 0), 2013: (19, 0), 2012: (11, 1)},
    "corn": {2017: (732, 439), 2016: (1, 0), 2014: (320, 163), 2013: (307, 215),
             2012: (328, 213)},
    "millet": {2016: (1, 0), 2015: (76, 0), 2014: (30, 0), 2013: (19, 0), 2012: (11, 1)},
    "oat": {2017: (3, 1), 2016: (1, 0), 2014: (35, 4), 2013: (70, 3), 2012: (15, 6)},
    "quinoa": {2015: (77, 0), 2014: (33, 0), 2013: (16, 0), 2012: (15, 1)},
    "rice": {2017: (5, 1), 2016: (4, 0), 2015: (108, 0), 2014: (22, 1), 2013: (31, 3)},
    "spelt": {2016: (3, 0), 2015: (70, 0), 2014: (26, 0), 2013: (14, 0), 2012: (16, 2)},
    "teff": {2015: (42, 0), 2014: (14, 1), 2013: (8, 0), 2012: (13, 0)},
    "wheat": {2017: (3, 2), 2016: (299, 0), 2014: (54, 5), 2013: (70, 3), 2012: (30, 3)},
}
SOY_YEARS = {2013: (91, 1), 2012: (94, 1)}
TEA_YEARS = {2016: (426, 1)}
# Corn and oat year rows with positives: positives, average.
CORN_AVG = {2017: (439, 412.2), 2014: (163, 326.8), 2013: (215, 355.5), 2012: (213, 357.3)}
OAT_AVG = {2017: (1, 53.0), 2014: (4, 112.0), 2013: (3, 172.3), 2012: (6, 130.3)}
# Appendix B: samples, positives, printed share.
B1 = {"Bakery Product - English Muffin": (1, 0, 0), "Baking Mixes": (12, 10, 83),
      "Breadcrumbs": (1, 1, 100), "Breakfast cereals for adult": (145, 106, 73),
      "Breakfast cereals for children": (214, 167, 68), "Corn bran": (2, 2, 100),
      "Corn flour": (276, 233, 84), "Cornmeal": (336, 255, 76), "Corn starch": (251, 5, 2.0),
      "Corn pasta": (82, 62, 76), "Corn snacks": (13, 3, 23), "Corn/tortilla chips": (175, 93, 53),
      "Crackers": (4, 3, 75), "Creamed corn": (50, 0, 0), "Infant Cereal": (1, 0, 0),
      "Popcorn": (25, 6, 24), "Soup mix": (1, 0, 0), "Tacos/Tortillas": (99, 84, 85)}
# Appendix A: conventional samples, organic samples (None where the page prints N/A).
A1 = {"amaranth": (1, 87), "arrowroot": (66, 0), "barley": (84, 50), "buckwheat": (27, 104),
      "corn": (1386, 302), "kamut": (1, 147), "millet": (76, 61), "mixed grains": (3, 2),
      "oat": (106, 18), "quinoa": (17, 124), "rice": (144, 45), "rye": (38, 98),
      "spelt": (14, 115), "teff": (2, 1), "triticale": (1, 0), "wheat": (426, 30)}
A2 = {"infant cereal": (3, 0), "meat alternatives": (9, 0), "miso": (2, 3),
      "soy beverages": (9, 31), "soy flour": (13, 16), "soy infant formula": (16, 4),
      "soy protein": (1, 0), "soybeans": (24, 16), "soybean paste": (3, 0), "soy nuts": (1, 0),
      "tempeh": (4, 0), "tofu": (26, 4)}
A3 = {"beverage": (42, 7), "black": (86, None), "green": (88, 13), "herbal": (88, 12),
      "oolong": (23, 2), "other": (23, 3), "white": (12, 13)}
TEXT_CONVENTIONAL, TEXT_ORGANIC = 2939, 1322
TEXT_TEAS = {"beverage": 49, "black": 100, "green": 101, "herbal": 100, "oolong": 25,
             "other": 26, "white": 25}
# The soy sentence's list, in its order.
SOY_SENTENCE = {"tofu": 26, "soybeans": 24, "soy infant formula": 16, "soy flour": 13,
                "meat alternatives": 9, "soy beverages": 9, "tempeh": 4, "infant cereal": 3,
                "soybean paste": 3, "miso": 2, "soy protein": 1, "soy nuts": 1}


def share(pos, n, printed):
    """Round 100*pos/n to the printed number of decimals."""
    return round(100 * pos / n, 1 if isinstance(printed, float) else 0)


class Report2012to2018(unittest.TestCase):
    def test_r1_table1_adds_up(self):
        for d, i, u, t in TABLE1.values():
            self.assertEqual(d + i + u, t)
        for col in range(4):
            self.assertEqual(sum(TABLE1[g][col] for g in ("grain", "soy", "tea")),
                             TABLE1["total"][col])

    def test_r2_table2(self):
        self.assertEqual(sum(TABLE2[g][1] for g in ("grain", "soy", "tea")), 1076)
        for n, pos, pct, _ in TABLE2.values():
            self.assertEqual(share(pos, n, pct), pct)
        avg = (1073 * 365 + 2 * 36 + 1 * 43) / 1076
        self.assertEqual(round(avg), 364)
        self.assertEqual((27 + 45) / 2, 36)

    def test_r3_table3_is_66_short_and_teff_77_closes_it(self):
        n = sum(v[0] for v in TABLE3.values())
        pos = sum(v[1] for v in TABLE3.values())
        self.assertEqual((n, pos), (3584, 1073))
        self.assertEqual(n - TABLE3["teff"][0] + sum(v[0] for v in YEARS["teff"].values()), 3650)
        self.assertEqual(round(100 * 1 / 77), 1)
        self.assertEqual(round(100 * 1 / 11), 9)

    def test_r4_year_rows(self):
        bad_n = {g for g, ys in YEARS.items() if sum(v[0] for v in ys.values()) != TABLE3[g][0]}
        bad_pos = {g for g, ys in YEARS.items() if sum(v[1] for v in ys.values()) != TABLE3[g][1]}
        self.assertEqual(bad_n, {"rice", "teff"})
        self.assertEqual(bad_pos, set())
        self.assertEqual(sum(v[0] for v in YEARS["teff"].values()), 77)
        self.assertEqual(sum(v[0] for v in YEARS["rice"].values()), 170)
        self.assertEqual(TABLE3["rice"][0] - 170, 19)
        self.assertNotIn(2012, YEARS["rice"])
        self.assertEqual(tuple(map(sum, zip(*SOY_YEARS.values()))), (185, 2))
        self.assertEqual(tuple(map(sum, zip(*TEA_YEARS.values()))), (426, 1))

    def test_r5_impossible_rows(self):
        # Wheat 2012: positives 28.8, x >= 28.8, 393 cannot average 99.7.
        least = (28.8 + 28.8 + 393) / 3
        self.assertEqual(round(least, 1), 150.2)
        self.assertGreater(least, 99.7)
        # Rice 2014: one positive, yet min 33 and max 249 are printed.
        self.assertEqual(YEARS["rice"][2014][1], 1)
        self.assertNotEqual(33, 249)
        # Oat 2017: 1 of 3 is 33%, not 67%; wheat 2017's 2 of 3 is 67%.
        self.assertEqual(round(100 * 1 / 3), 33)
        self.assertEqual(round(100 * 2 / 3), 67)

    def test_r6_appendix_b(self):
        self.assertEqual(sum(v[0] for v in B1.values()), TABLE3["corn"][0])
        self.assertEqual(sum(v[1] for v in B1.values()), TABLE3["corn"][1])
        bad = {k for k, (n, pos, pct) in B1.items() if share(pos, n, pct) != pct}
        self.assertEqual(bad, {"Breakfast cereals for children"})
        self.assertEqual(round(100 * 167 / 214), 78)

    def test_r7_weighted_year_averages(self):
        corn = sum(p * a for p, a in CORN_AVG.values()) / sum(p for p, _ in CORN_AVG.values())
        oat = sum(p * a for p, a in OAT_AVG.values()) / sum(p for p, _ in OAT_AVG.values())
        self.assertEqual(sum(p for p, _ in CORN_AVG.values()), 1030)
        self.assertEqual(sum(p for p, _ in OAT_AVG.values()), 14)
        self.assertAlmostEqual(corn, 375.50, places=2)
        self.assertAlmostEqual(oat, 128.55, places=2)
        self.assertLessEqual(abs(corn - 375.5), 0.05)
        self.assertLessEqual(abs(oat - 128.5), 0.1)

    def test_r8_conventional_and_organic(self):
        mismatch = {g for g, (c, o) in A1.items() if c + o != TABLE3[g][0]}
        self.assertEqual(mismatch, {"teff"})
        self.assertEqual(sum(c + o for c, o in A2.values()), 185)
        organic_black = TEXT_TEAS["black"] - A3["black"][0]
        self.assertEqual(organic_black, 14)
        for k, (c, o) in A3.items():
            if o is not None:
                self.assertEqual(c + o, TEXT_TEAS[k], k)
        conv = (sum(c for c, _ in A1.values()) + sum(c for c, _ in A2.values())
                + sum(c for c, _ in A3.values()))
        org = (sum(o for _, o in A1.values()) + sum(o for _, o in A2.values())
               + sum(o for _, o in A3.values() if o is not None) + organic_black)
        self.assertEqual((conv, org), (2865, TEXT_ORGANIC))
        self.assertEqual(TEXT_CONVENTIONAL - conv, 74)
        # 76 conventional teff (not 2) closes the gap and gives 77 teff in all.
        self.assertEqual(conv - A1["teff"][0] + 76, TEXT_CONVENTIONAL)
        self.assertEqual(76 + A1["teff"][1], 77)
        self.assertEqual(conv + org, 4261 - 74)

    def test_r9_soy_sentence_is_the_conventional_column(self):
        self.assertEqual(sum(SOY_SENTENCE.values()), 111)
        for k, n in SOY_SENTENCE.items():
            self.assertEqual(A2[k][0], n, k)
        self.assertEqual(sum(c for c, _ in A2.values()), 111)
        self.assertEqual(sum(A2["tofu"]), 30)

    def test_r10_one_tofu_one_soy_flour(self):
        # A2: 1 of 26 conventional tofu (3.8%), 1 of 16 organic soy flour (6.2%).
        self.assertAlmostEqual(100 / 26, 3.8, delta=0.05)
        self.assertAlmostEqual(100 / 16, 6.2, delta=0.05 + 1e-9)
        self.assertEqual(sum(p for _, p in SOY_YEARS.values()), 2)

    def test_v6_wheat_2012_bounds(self):
        lo = 122.75 * 13 - (27 + 30) - 137.5 * 5 - 99.75 * 3
        hi = 122.85 * 13 - (27 + 30) - 136.5 * 5 - 99.65 * 3
        self.assertEqual((round(lo, 2), round(hi, 2)), (552.0, 558.6))
        self.assertEqual((round(lo / 3, 2), round(hi / 3, 2)), (184.0, 186.2))
        self.assertEqual((round(lo - 421.8, 2), round(hi - 421.8, 2)), (130.2, 136.8))

    def test_v7_rice_bounds(self):
        known = 33 + 47 + 249 + 42
        self.assertEqual(known, 371)
        lo = max(83.15 * 5 - known, 41.65 * 3 - (33 + 47))
        hi = min(83.25 * 5 - known, 41.75 * 3 - (33 + 47))
        self.assertEqual((round(lo, 2), round(hi, 2)), (44.95, 45.25))
        # Table 3's maximum 249 can only be the 2014 positive (2013 tops out at 47, 2017 is 42).
        self.assertGreater(249, max(47, 42))


class Report2011(unittest.TestCase):
    def test_page_arithmetic(self):
        self.assertEqual(274 + 180, 454)
        self.assertEqual(161 + 1, 162)
        self.assertEqual(round(100 * 162 / 454), 36)
        self.assertEqual(round(100 * 161 / 274), 59)

    def test_r12_table7_restates_2011_and_2010(self):
        table7 = {2011: (274, 161, 23.1, 4442.5, 253.2), 2010: (276, 157, 20, 6650, 268)}
        page = {2011: (274, 161, 20.8, 4442.5), 2010: (276, 157, 20, 6650)}
        self.assertEqual(table7[2011][:2] + table7[2011][3:4], page[2011][:2] + page[2011][3:4])
        self.assertNotEqual(table7[2011][2], page[2011][2])
        self.assertEqual(table7[2010][:4], page[2010])


if __name__ == "__main__":
    unittest.main(verbosity=2)
