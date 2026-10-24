# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Recompute every number published in docs/ota-foods-0.1.0-result.md.

Reads the sealed output of job ota-foods-v1 (CFIA's open 2012-2022 ochratoxin A file, Open
Government Licence - Canada):
  data/ota_foods_samples.csv   one row per non-spice sample (7,607 rows),
  data/ota_foods_categories.csv the 11 Table 2 categories,
  data/ota_foods_eu.csv        the 13 EU maximum-level groups.
Uses only csv, statistics and unittest. The per-sample table is the source of truth; the two
aggregate tables are recomputed from it (the spice rows of the category table were published by
ota-spices 0.1.0 and are taken as given where a non-spice recompute cannot reach them).
"""
import csv
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "data", "ota_foods_samples.csv")
CATS = os.path.join(HERE, "data", "ota_foods_categories.csv")
EU = os.path.join(HERE, "data", "ota_foods_eu.csv")

NON_SPICE_CATS = ("cocoa", "coffee", "dried_fruit", "grain", "infant_formula", "licorice",
                  "nuts", "pulses", "seeds", "soy")
# Category sizes registered in the pre-registration (label counts, no value read).
EXPECTED_N = {"cocoa": 242, "coffee": 790, "dried_fruit": 696, "grain": 4124,
              "infant_formula": 192, "licorice": 140, "nuts": 148, "pulses": 635, "seeds": 279,
              "soy": 361, "spices": 777}
V1_CATS = ("coffee", "nuts", "soy")
V2_CATS = ("cocoa", "licorice", "seeds")
# Health Canada's proposed levels as CFIA applied them to grain-based foods (ppb).
HC_INFANT, HC_BRAN, HC_GRAIN = 0.5, 7.0, 3.0

PUBLISHED_GRADES = {"G": True, "C1": True, "C2": True, "C3": True, "C4": True, "C5": False,
                    "C6": True, "V1": True, "V2": True, "P1": True, "P2": True, "P3": True,
                    "P4": True, "P5": True, "P6": True, "P7": True, "P8": True, "P9": True,
                    "P10": True, "P11": True, "P12": True}


def decimals(printed):
    return len(printed.split(".")[1]) if "." in printed else 0


def matches(value, printed):
    """True when value rounds to the printed figure at its printed precision (grader rule)."""
    if value is None:
        return False
    return abs(value - float(printed)) <= 0.5 * 10 ** (-decimals(printed)) + 1e-9


def verdict(mean_pos, mean_all, printed):
    p, a = matches(mean_pos, printed), matches(mean_all, printed)
    if p and a:
        return "both"
    if p:
        return "positives"
    if a:
        return "all"
    return "neither"


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["ppb"] = float(r["ota_ppb"]) if r["ota_ppb"] != "" else 0.0
        r["det"] = int(r["detected"])
    return rows


def load_table(path, key):
    with open(path, newline="", encoding="utf-8") as fh:
        return {r[key]: r for r in csv.DictReader(fh)}


def cat_stats(rows):
    det = sorted(r["ppb"] for r in rows if r["det"])
    n = len(rows)
    return {
        "n": n, "n_detected": len(det),
        "min_detected": det[0] if det else None,
        "median_detected": statistics.median(det) if det else None,
        "mean_positives": statistics.fmean(det) if det else None,
        "mean_all": (sum(det) / n) if n else None,
        "max": max((r["ppb"] for r in rows), default=None),
    }


class TestSamplesTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = load_samples()

    def test_shape_and_no_spices(self):
        self.assertEqual(len(self.s), 7607)
        self.assertEqual(len({r["sample"] for r in self.s}), 7607)
        self.assertFalse(any(r["category"] == "spices" for r in self.s))

    def test_category_sizes_match_registered(self):
        counts = {}
        for r in self.s:
            counts[r["category"]] = counts.get(r["category"], 0) + 1
        for cat in NON_SPICE_CATS:
            self.assertEqual(counts[cat], EXPECTED_N[cat], msg=cat)

    def test_non_detects_are_literal_zero(self):
        # The file writes no "<" value and no ND token; every non-detect is a bare 0.
        for r in self.s:
            if r["det"]:
                self.assertGreater(r["ppb"], 0.0, msg=r["sample"])
                self.assertFalse(r["result_raw"].startswith("<"), msg=r["sample"])
            else:
                self.assertEqual(r["ppb"], 0.0, msg=r["sample"])


class TestCategoryTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = load_samples()
        cls.ct = load_table(CATS, "category")

    def test_recompute_non_spice_rows(self):
        for cat in NON_SPICE_CATS:
            st = cat_stats([r for r in self.s if r["category"] == cat])
            row = self.ct[cat]
            with self.subTest(cat=cat):
                self.assertEqual(st["n"], int(row["n"]))
                self.assertEqual(st["n_detected"], int(row["n_detected"]))
                self.assertAlmostEqual(st["min_detected"], float(row["min_detected"]), places=4)
                self.assertAlmostEqual(st["median_detected"], float(row["median_detected"]),
                                       places=3)
                self.assertAlmostEqual(st["mean_positives"], float(row["mean_positives"]),
                                       places=3)
                self.assertAlmostEqual(st["mean_all"], float(row["mean_all"]), places=3)
                self.assertAlmostEqual(st["max"], float(row["max"]), places=4)

    def test_c2_positives_match_table2(self):
        want = {"cocoa": 219, "coffee": 190, "licorice": 111, "nuts": 31, "seeds": 87, "soy": 51}
        for cat, pos in want.items():
            st = cat_stats([r for r in self.s if r["category"] == cat])
            self.assertEqual(st["n_detected"], pos, msg=cat)
            self.assertEqual(int(self.ct[cat]["printed_positives"]), pos, msg=cat)

    def test_c3_c4_maxima_and_minima(self):
        for cat in ("cocoa", "coffee", "dried_fruit", "licorice", "nuts", "seeds", "soy"):
            row = self.ct[cat]
            st = cat_stats([r for r in self.s if r["category"] == cat])
            with self.subTest(cat=cat):
                self.assertTrue(matches(st["max"], row["printed_max"]))
                self.assertTrue(matches(st["min_detected"], row["printed_min"]))

    def test_v1_v2_are_positives_means(self):
        for cat in V1_CATS + V2_CATS:
            row = self.ct[cat]
            st = cat_stats([r for r in self.s if r["category"] == cat])
            v = verdict(st["mean_positives"], st["mean_all"], row["printed_average"])
            with self.subTest(cat=cat):
                self.assertEqual(v, "positives")
                self.assertEqual(row["verdict"], "positives")
                # Clearly positives, not the all-sample mean.
                self.assertTrue(matches(st["mean_positives"], row["printed_average"]))
                self.assertFalse(matches(st["mean_all"], row["printed_average"]))

    def test_c1_detection_total(self):
        non_spice_det = sum(r["det"] for r in self.s)
        self.assertEqual(non_spice_det, 3540)
        spice_det = int(self.ct["spices"]["n_detected"])
        self.assertEqual(spice_det, 516)
        self.assertEqual(non_spice_det + spice_det, 4056)


class TestInfantFormula(unittest.TestCase):
    """P1: the file follows Table 8, not Table 2."""

    @classmethod
    def setUpClass(cls):
        cls.inf = [r for r in load_samples() if r["category"] == "infant_formula"]

    def test_overall(self):
        det = sum(r["det"] for r in self.inf)
        self.assertEqual(len(self.inf), 192)
        self.assertEqual(det, 60)
        self.assertTrue(55 <= det <= 65)
        self.assertTrue(matches(max(r["ppb"] for r in self.inf), "0.89"))
        dairy = sum(1 for r in self.inf if r["product"] == "Infant Formula - Dairy" and r["det"])
        self.assertEqual(dairy, 0)

    def test_table8_by_plan(self):
        want = {"2012_SB447": (148, 52, 35, "0.89"), "2014_SB447": (44, 8, 18, "0.46")}
        for plan, (n, det, pct, pmax) in want.items():
            sub = [r for r in self.inf if r["plan"] == plan]
            with self.subTest(plan=plan):
                self.assertEqual(len(sub), n)
                d = sum(r["det"] for r in sub)
                self.assertEqual(d, det)
                self.assertEqual(round(100.0 * d / n), pct)
                self.assertTrue(matches(max(r["ppb"] for r in sub), pmax))

    def test_contradicts_table2(self):
        # Table 2 prints 13 positives, maximum 11, average 1.1 -- none of which the file shows.
        det = sum(r["det"] for r in self.inf)
        self.assertNotEqual(det, 13)
        self.assertFalse(matches(max(r["ppb"] for r in self.inf), "11"))


class TestEuGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = load_samples()
        cls.eu = load_table(EU, "group")

    def test_recompute_each_group(self):
        total_n = total_over = 0
        for gid, row in self.eu.items():
            level = float(row["level"])
            sub = [r for r in self.s if r["eu_group"] == gid]
            n_over = sum(1 for r in sub if r["det"] and r["ppb"] > level)
            with self.subTest(group=gid):
                self.assertEqual(len(sub), int(row["n"]))
                self.assertEqual(sum(r["det"] for r in sub), int(row["n_detected"]))
                self.assertEqual(n_over, int(row["n_over"]))
                self.assertTrue(matches(max((r["ppb"] for r in sub), default=0.0), row["max"]))
            total_n += len(sub)
            total_over += n_over
        self.assertEqual(total_n, 4851)
        self.assertEqual(total_over, 158)

    def test_key_counts(self):
        want = {"infant_cereal": (409, 95), "breakfast_cereal": (609, 3),
                "bakery_snacks": (1274, 9), "oat": (320, 8), "wheat": (294, 6),
                "roasted_coffee": (601, 4), "instant_coffee": (56, 4), "cocoa_powder": (242, 10),
                "licorice": (140, 6), "other_dried_fruit": (441, 7), "fig": (48, 0),
                "pistachio_seeds_soybean": (214, 2)}
        for gid, (n, over) in want.items():
            self.assertEqual(int(self.eu[gid]["n"]), n, msg=gid)
            self.assertEqual(int(self.eu[gid]["n_over"]), over, msg=gid)
        # P5: a larger share of oat products than wheat products over 3 ppb.
        oat = int(self.eu["oat"]["n_over"]) / int(self.eu["oat"]["n"])
        wheat = int(self.eu["wheat"]["n_over"]) / int(self.eu["wheat"]["n"])
        self.assertGreater(oat, wheat)


class TestHealthCanada(unittest.TestCase):
    """C5 (miss) and P4."""

    @classmethod
    def setUpClass(cls):
        cls.grain = [r for r in load_samples() if r["category"] == "grain"]

    @staticmethod
    def hc_limit(product):
        if product == "Infant Food - Cereal":
            return HC_INFANT
        if product == "Bran - Wheat":
            return HC_BRAN
        return HC_GRAIN

    def test_split_and_total(self):
        over = [r for r in self.grain if r["det"] and r["ppb"] > self.hc_limit(r["product"])]
        infant = sum(1 for r in over if r["product"] == "Infant Food - Cereal")
        bran = sum(1 for r in over if r["product"] == "Bran - Wheat")
        self.assertEqual(infant, 95)
        self.assertEqual(bran, 0)
        self.assertEqual(len(over) - infant - bran, 30)
        self.assertEqual(len(over), 125)           # strictly over
        at_or_above = sum(1 for r in self.grain
                          if r["det"] and r["ppb"] >= self.hc_limit(r["product"]))
        self.assertEqual(at_or_above, 126)
        # C5 fails: 125 is outside the registered 116-122 band around CFIA's printed 119.
        self.assertFalse(116 <= len(over) <= 122)
        self.assertNotEqual(len(over), 119)
        # P4 holds: infant cereals are more than half of those over.
        self.assertGreater(infant * 2, len(over))

    def test_label_ambiguous_samples_explain_at_most_one(self):
        # CFIA counts 12 grain-labelled samples (Grain - Other, Flour - Other, Pasta in the pulse
        # surveys) under pulses. Only one of these exceeds the 3.0 ppb level, so reclassifying
        # them removes at most one over-level sample: the count stays above CFIA's 119.
        amb = [r for r in self.grain
               if r["product"] in ("Grain - Other", "Flour - Other", "Pasta")]
        over3 = [r for r in amb if r["det"] and r["ppb"] > HC_GRAIN]
        self.assertEqual(len(over3), 1)
        self.assertEqual(over3[0]["product"], "Flour - Other")
        self.assertEqual(over3[0]["plan"], "2017_SB447")
        self.assertAlmostEqual(over3[0]["ppb"], 3.34, places=4)
        self.assertGreater(125 - len(over3), 119)


class TestGradePattern(unittest.TestCase):
    def test_twenty_of_twenty_one(self):
        self.assertEqual(sum(PUBLISHED_GRADES.values()), 20)
        self.assertEqual(len(PUBLISHED_GRADES), 21)
        self.assertFalse(PUBLISHED_GRADES["C5"])
        self.assertTrue(all(v for k, v in PUBLISHED_GRADES.items() if k != "C5"))


if __name__ == "__main__":
    unittest.main()
