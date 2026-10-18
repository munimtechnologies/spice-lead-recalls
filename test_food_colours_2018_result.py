# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes the headline counts in docs/food-colours-2018-0.1.0-result.md from the
# committed sealed sample table, so the published numbers can be checked offline.
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "food_colours_2018_samples.csv")

# West or Central African country names used for P6.
WEST_CENTRAL_AFRICA = {
    "NIGERIA", "GHANA", "SENEGAL", "MALI", "BENIN", "TOGO", "NIGER",
    "BURKINA FASO", "COTE D'IVOIRE", "IVORY COAST", "GUINEA", "SIERRA LEONE",
    "LIBERIA", "GAMBIA", "CAMEROON", "CHAD", "CONGO", "GABON",
    "CENTRAL AFRICAN REPUBLIC",
}


def rows():
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tally(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


class FoodColours2018(unittest.TestCase):
    def test_sample_count(self):
        self.assertEqual(len(rows()), 399)

    def test_category_counts(self):
        self.assertEqual(
            tally(r["category"] for r in rows()),
            {"essences/flavourings": 50, "oils": 74, "processed vegetables": 50,
             "sweets": 87, "unclassified": 138},
        )

    def test_any_colour_matches_cfia_181(self):
        positive = [r for r in rows() if r["positive"]]
        self.assertEqual(len(positive), 181)
        self.assertEqual(
            tally(r["category"] for r in positive),
            {"essences/flavourings": 9, "processed vegetables": 28,
             "sweets": 64, "unclassified": 80},
        )

    def test_non_permitted_samples(self):
        found = {r["sample"]: r["non_permitted"] for r in rows() if r["non_permitted"]}
        self.assertEqual(
            found,
            {"C2018FCOL00263": "rhodamine b", "C2018FCOL00293": "orange ii",
             "C2018FCOL00376": "orange ii"},
        )

    def test_rhodamine_b_sample_p2_p3_p4(self):
        hits = [r for r in rows() if "rhodamine b" in r["non_permitted"].split(";")]
        self.assertEqual(len(hits), 1)
        r = hits[0]
        self.assertEqual(r["sample"], "C2018FCOL00263")
        self.assertEqual(r["product"], "Pickled Vegetable - Misc")
        self.assertEqual(r["origin"], "LEBANON")
        # P3 (a sweet) did not hold.
        self.assertEqual(r["category"], "processed vegetables")
        self.assertEqual(r["positive"], "erythrosin b;rhodamine b")

    def test_other_lebanese_pickles_clean(self):
        leb = [r for r in rows()
               if r["origin"] == "LEBANON" and r["product"] == "Pickled Vegetable - Misc"]
        self.assertEqual(len(leb), 3)
        self.assertEqual([r["sample"] for r in leb if r["positive"]], ["C2018FCOL00263"])

    def test_orange_ii_categories_p5(self):
        cats = sorted(r["category"] for r in rows()
                      if "orange ii" in r["non_permitted"].split(";"))
        self.assertEqual(cats, ["sweets", "unclassified"])

    def test_p6_west_central_african_oils(self):
        oils = [r for r in rows() if r["category"] == "oils"]
        wca = [r for r in oils if r["origin"] in WEST_CENTRAL_AFRICA]
        self.assertEqual(len(oils), 74)
        self.assertEqual(tally(r["origin"] for r in wca), {"TOGO": 3, "GHANA": 2})
        # integer form of 5/74 < 0.05 failing: 100 * 5 >= 5 * 74
        self.assertGreaterEqual(100 * len(wca), 5 * len(oils))
        self.assertTrue(all(not r["positive"] for r in wca))

    def test_palm_oils_all_clean(self):
        palm = [r for r in rows() if r["product"] == "Oil - Palm"]
        self.assertEqual(
            tally(r["origin"] for r in palm),
            {"ECUADOR": 13, "TOGO": 3, "GHANA": 2, "COLOMBIA": 2,
             "MALAYSIA": 2, "UNKNOWN": 1},
        )
        self.assertEqual(sum(1 for r in palm if r["positive"] or r["non_permitted"]), 0)

    def test_permitted_over_300(self):
        high = sorted(float(r["max_permitted_ppm"]) for r in rows()
                      if float(r["max_permitted_ppm"]) > 300)
        self.assertEqual(high, [312.0, 475.0, 539.0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
