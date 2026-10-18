# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes the counts in docs/raman-reach-0.1.1-result.md from the committed
# sealed sample table, so the published numbers can be checked offline.
import csv
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "raman_reach_samples.csv")


def rows():
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tally(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


class RamanReachResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()
        for r in cls.rows:
            r["pb"] = float(r["pb"])
        cls.E = [r for r in cls.rows if r["pb"] > 10]

    def test_matches_article_tables(self):
        self.assertEqual(len(self.rows), 503)
        self.assertEqual(tally(r["form_code"] for r in self.rows), {"1": 162, "2": 30, "3": 235, "4": 76})
        self.assertEqual(tally(r["state_city_map"] for r in self.rows),
                         {"Bihar": 134, "Jharkhand": 77, "Uttar Pradesh": 200, "West Bengal": 60,
                          "Chhattisgarh": 32})
        agree = sum(1 for r in self.rows if (r["sellstate_bin"] == "1") == (r["state_city_map"] == "Bihar"))
        self.assertEqual(agree, 503)

    def test_values(self):
        self.assertEqual(len(self.E), 152)
        ten = [r for r in self.rows if r["pb"] == 10]
        self.assertEqual([(r["sample"], r["city"]) for r in ten], [("50_KD-1-2-5", "Ambikapur")])
        self.assertEqual(sum(1 for r in self.rows if r["pb"] == 2), 340)
        self.assertEqual(sum(1 for r in self.rows if r["pb"] < 10), 350)
        top = max(self.rows, key=lambda r: r["pb"])
        self.assertEqual((top["sample"], top["city"], top["state_city_map"], top["pb"]),
                         ("36_MC_3_1_1", "Buxar", "Bihar", 6416.0))

    def test_repeated_ids_are_all_non_detects(self):
        counts = tally(r["sample"] for r in self.rows)
        repeated = sorted(k for k, n in counts.items() if n > 1)
        self.assertEqual(repeated, ["18_RG_2_1_1", "18_RG_2_2_4", "18_RG_2_3_5", "18_RG_2_4_6", "53_NG_2_1_1",
                                    "53_NG_3_1_1", "54_SM_1_1_1", "54_UD_1_1_1", "55_CB_1_1_1", "55_CB_1_2_4"])
        self.assertTrue(all(counts[k] == 2 for k in repeated))
        self.assertEqual(set(r["pb"] for r in self.rows if r["sample"] in repeated), {2.0})

    def test_ladder(self):
        for t, n in ((10, 153), (50, 139), (100, 131), (320, 112), (500, 105), (640, 103), (1000, 91),
                     (1500, 70), (2000, 51), (3200, 16), (10000, 0)):
            self.assertEqual(sum(1 for r in self.rows if r["pb"] >= t), n, t)
        self.assertEqual(sum(1 for r in self.E if r["pb"] < 100), 21)

    def test_p4_p5(self):
        reach = sum(1 for r in self.E if r["pb"] >= 3200)
        self.assertEqual(reach, 16)
        self.assertGreater(reach, 0.10 * len(self.E))
        self.assertEqual(statistics.median(r["pb"] for r in self.E), 1294.0)

    def test_p6_p7(self):
        gross = [r for r in self.rows if r["pb"] >= 500]
        self.assertEqual(len(gross), 105)
        self.assertEqual(sum(1 for r in gross if r["state_city_map"] == "Bihar"), 47)
        a = tally(r["form_class_counts"] for r in gross)
        self.assertEqual(a, {"root_double": 74, "root_single": 1, "loose_powder": 30})
        b = tally(r["form_class_caption"] for r in gross)
        self.assertEqual(b, {"unknown": 74, "root_double": 1, "loose_powder": 30})

    def test_p8_packaged(self):
        packaged = [r for r in self.rows if r["form_class_counts"] == "packaged_powder"]
        self.assertEqual(len(packaged), 30)
        self.assertEqual(sum(1 for r in packaged if r["pb"] > 10), 3)
        over = sorted((r["sample"], r["city"], r["pb"]) for r in packaged if r["pb"] > 100)
        self.assertEqual(over, [("42_MB_3_1_2", "Deoghar", 240.0), ("46_RM_4_2_2", "Jamshedpur", 130.0)])

    def test_by_state_and_form(self):
        self.assertEqual(tally(r["state_city_map"] for r in self.E),
                         {"Uttar Pradesh": 32, "Bihar": 72, "Jharkhand": 32, "West Bengal": 8, "Chhattisgarh": 8})
        reach = [r for r in self.E if r["pb"] >= 3200]
        self.assertEqual(tally(r["state_city_map"] for r in reach),
                         {"Bihar": 6, "Uttar Pradesh": 4, "Jharkhand": 3, "Chhattisgarh": 3})
        self.assertEqual(tally(r["form_class_counts"] for r in self.E),
                         {"root_double": 83, "loose_powder": 57, "root_single": 9, "packaged_powder": 3})
        self.assertEqual(tally(r["form_class_counts"] for r in reach),
                         {"root_double": 13, "loose_powder": 2, "root_single": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
