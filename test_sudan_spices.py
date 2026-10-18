# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes the headline counts in docs/sudan-spices-0.1.0-result.md from the
# committed sealed sample table, so the published numbers can be checked offline.
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "sudan_spices_samples.csv")

# West or Central African country names used for the frame-coverage check (P4).
WEST_CENTRAL_AFRICA = {
    "NIGERIA", "GHANA", "SENEGAL", "MALI", "BENIN", "TOGO", "NIGER",
    "BURKINA FASO", "COTE D'IVOIRE", "IVORY COAST", "GUINEA", "SIERRA LEONE",
    "LIBERIA", "GAMBIA", "CAMEROON", "CHAD", "CONGO", "GABON",
    "CENTRAL AFRICAN REPUBLIC",
}


def rows():
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class SudanSpices(unittest.TestCase):
    def test_sample_count(self):
        self.assertEqual(len(rows()), 63)

    def test_no_sudan_dye_positive(self):
        # P2 consistency check: CFIA reported none of the 63 carried a Sudan dye.
        self.assertEqual(sum(int(r["sudan_positive"]) for r in rows()), 0)

    def test_origin_counts(self):
        counts = {}
        for r in rows():
            counts[r["origin"]] = counts.get(r["origin"], 0) + 1
        self.assertEqual(
            counts,
            {"UNKNOWN": 54, "LEBANON": 3, "CANADA": 2, "TURKEY": 2,
             "INDIA": 1, "IRAN": 1},
        )

    def test_p3_india_not_most_common_declared(self):
        # P3 (India most common declared origin) did not hold: Lebanon led the
        # declared origins. India had 1 declared sample.
        declared = {}
        for r in rows():
            if r["origin"] != "UNKNOWN":
                declared[r["origin"]] = declared.get(r["origin"], 0) + 1
        top = max(declared, key=declared.get)
        self.assertEqual(top, "LEBANON")
        self.assertEqual(declared["INDIA"], 1)

    def test_p4_no_west_central_african_origin(self):
        n = sum(1 for r in rows() if r["origin"] in WEST_CENTRAL_AFRICA)
        self.assertEqual(n, 0)

    def test_p5_no_georgia(self):
        self.assertEqual(sum(1 for r in rows() if r["origin"] == "GEORGIA"), 0)

    def test_p6_at_least_quarter_undeclared(self):
        undeclared = sum(1 for r in rows() if r["origin"] == "UNKNOWN")
        self.assertEqual(undeclared, 54)
        # integer form of 54/63 >= 0.25
        self.assertGreaterEqual(100 * undeclared, 25 * 63)

    def test_by_product(self):
        by = {}
        for r in rows():
            by[r["product"]] = by.get(r["product"], 0) + 1
        self.assertEqual(
            by,
            {"Cayenne Pepper": 18, "Chili Powder": 16,
             "Paprika": 16, "Sumac": 13},
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
