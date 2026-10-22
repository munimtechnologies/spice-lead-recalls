# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes the numbers in docs/coumarin-tdi-0.1.0-result.md from the committed
# sealed sample table, so the published figures can be checked offline.
import csv
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "coumarin_tdi_samples.csv")


def rows():
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def serving(ppm, bw_kg):
    """Grams reaching the EFSA TDI (0.1 mg/kg bw/day): (0.1 * bw) / (ppm / 1000)."""
    return 100.0 * bw_kg / ppm


def tally(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


class CoumarinTdiResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()
        cls.ppm = [float(r["coumarin_ppm"]) for r in cls.rows]
        cls.ground = [float(r["coumarin_ppm"]) for r in cls.rows if r["form"] == "ground"]

    def test_counts_by_file(self):
        self.assertEqual(len(self.rows), 176)
        self.assertEqual(tally(r["file"] for r in self.rows),
                         {"2011-12": 107, "2012-13": 40, "2015-16": 29})

    def test_g0_gate(self):
        self.assertEqual((min(self.ppm), max(self.ppm)), (6.2, 7816.3))
        top = max(self.rows, key=lambda r: float(r["coumarin_ppm"]))
        self.assertEqual((top["file"], top["origin"]), ("2011-12", "VIETNAM"))

    def test_p1_medians(self):
        self.assertAlmostEqual(statistics.median(self.ppm), 3339.9, places=6)
        self.assertAlmostEqual(statistics.median(serving(p, 60) for p in self.ppm), 1.79646, places=4)
        self.assertAlmostEqual(statistics.median(serving(p, 15) for p in self.ppm), 0.44912, places=4)
        self.assertAlmostEqual(min(serving(p, 60) for p in self.ppm), 0.76763, places=4)

    def test_p2_under_2g(self):
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 60) < 2.0), 122)
        self.assertEqual(sum(1 for p in self.ppm if p > 3000), 122)

    def test_teaspoon_counts(self):
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 15) < 2.6), 170)  # P3
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 60) < 2.6), 155)

    def test_csv_servings_match_formula(self):
        for r in self.rows:
            p = float(r["coumarin_ppm"])
            self.assertAlmostEqual(float(r["adult_serving_g"]), serving(p, 60), places=3)
            self.assertAlmostEqual(float(r["child_serving_g"]), serving(p, 15), places=3)

    def test_classes(self):
        self.assertEqual(tally(r["class"] for r in self.rows),
                         {"cassia-type": 168, "intermediate": 3, "verum-type": 5})

        def adult_range(cls):
            s = [serving(float(r["coumarin_ppm"]), 60) for r in self.rows if r["class"] == cls]
            return round(min(s), 2), round(max(s), 2)

        self.assertEqual(adult_range("cassia-type"), (0.77, 4.73))
        self.assertEqual(adult_range("intermediate"), (6.98, 11.36))
        self.assertEqual(adult_range("verum-type"), (292.68, 967.74))

    def test_sensitivity_70kg(self):
        self.assertAlmostEqual(statistics.median(serving(p, 70) for p in self.ppm), 2.09587, places=4)
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 70) < 2.0), 78)

    def test_sensitivity_teaspoon_mass(self):
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 60) < 2.3), 150)
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 60) < 2.8), 157)
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 15) < 2.3), 169)
        self.assertEqual(sum(1 for p in self.ppm if serving(p, 15) < 2.8), 170)

    def test_ground_only(self):
        self.assertEqual(tally(r["form"] for r in self.rows), {"ground": 156, "stick": 20})
        self.assertAlmostEqual(statistics.median(serving(p, 60) for p in self.ground), 1.75055, places=4)
        self.assertEqual(sum(1 for p in self.ground if serving(p, 60) < 2.0), 116)
        self.assertEqual(sum(1 for p in self.ground if serving(p, 15) < 2.6), 152)

    def test_no_country_count(self):
        self.assertEqual(sum(1 for r in self.rows if r["origin"] == "UNKNOWN"), 118)


if __name__ == "__main__":
    unittest.main(verbosity=2)
