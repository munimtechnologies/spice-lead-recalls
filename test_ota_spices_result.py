# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes the counts in docs/ota-spices-0.1.0-result.md from the committed sealed
# sample table: the failed pre-registered gate, and the exploratory Rule B regrade
# (product name begins with "Spice", CFIA's own label).
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "ota_samples.csv")


def rows():
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rule_b(all_rows):
    return [r for r in all_rows if r["product"].lower().startswith("spice")]


def tally(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


class OtaSpicesResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()
        cls.spices = rule_b(cls.rows)
        cls.over = [r for r in cls.spices if r["over_eu"] == "1"]

    def test_gate_failed_under_preregistered_rule(self):
        self.assertEqual(len(self.rows), 8384)
        n = sum(1 for r in self.rows if r["spice"] == "1")
        self.assertEqual(n, 1024)
        self.assertFalse(700 <= n <= 860)

    def test_keyword_rule_swept_in_non_spices(self):
        swept = tally(r["product"] for r in self.rows
                      if r["spice"] == "1" and not r["product"].lower().startswith("spice"))
        self.assertEqual(swept["Baking Mixes"], 254)
        self.assertEqual(swept["Mixed Fruit"], 14)
        self.assertEqual(swept["Dried mixes"], 3)
        self.assertEqual(swept["Herb - Marjoram - Fresh"], 1)
        self.assertEqual(sum(swept.values()), 1024 - 714)

    def test_rule_b_gate(self):
        self.assertEqual(len(self.spices), 714)
        self.assertTrue(all(r["spice"] == "1" for r in self.spices))

    def test_rule_b_types(self):
        self.assertEqual(
            tally(r["spice_type"] for r in self.spices),
            {"paprika": 122, "chili": 97, "nutmeg": 96, "mixture": 53, "pepper": 36,
             "ginger": 40, "turmeric": 63, "other": 207},
        )
        self.assertEqual(
            tally(r["spice_type"] for r in self.over),
            {"paprika": 53, "nutmeg": 33, "chili": 17, "ginger": 2, "mixture": 1},
        )

    def test_p2_p4_maximum(self):
        top = max(self.spices, key=lambda r: float(r["ota_ppb"]))
        self.assertEqual(top["sample"], "C2014OCTA00093")
        self.assertEqual(float(top["ota_ppb"]), 1770.0)
        self.assertEqual(top["spice_type"], "paprika")
        self.assertEqual(top["origin"], "HUNGARY")

    def test_p3_share(self):
        self.assertEqual(len(self.over), 106)
        # integer form of 0.05 <= 106/714 < 0.15
        self.assertTrue(5 * 714 <= 100 * 106 < 15 * 714)

    def test_p5_declared_origins_over_limit(self):
        declared = tally(r["origin"] for r in self.over if r["origin"] != "UNKNOWN")
        self.assertEqual(declared,
                         {"INDIA": 8, "SPAIN": 6, "CANADA": 5, "HUNGARY": 4, "GRENADA": 1})
        self.assertEqual(sum(1 for r in self.over if r["origin"] == "UNKNOWN"), 82)

    def test_p6_canada_not_lower(self):
        dom = [r for r in self.spices if r["origin"] == "CANADA"]
        foreign = [r for r in self.spices if r["origin"] not in ("UNKNOWN", "", "CANADA")]
        dom_over = sum(1 for r in dom if r["over_eu"] == "1")
        for_over = sum(1 for r in foreign if r["over_eu"] == "1")
        self.assertEqual((dom_over, len(dom)), (5, 34))
        self.assertEqual((for_over, len(foreign)), (19, 199))
        # 5/34 > 19/199, so P6 is not met
        self.assertGreater(dom_over * len(foreign), for_over * len(dom))

    def test_p7_raisins(self):
        high = [r for r in self.rows if r["vine_fruit"] == "1" and float(r["ota_ppb"]) > 10]
        self.assertEqual(len(high), 4)
        self.assertEqual(tally(r["origin"] for r in high),
                         {"UNKNOWN": 3, "IRAN, ISLAMIC REPUBLIC OF": 1})

    def test_p8_nutmeg(self):
        nut = tally(r["origin"] for r in self.over
                    if r["spice_type"] == "nutmeg" and r["origin"] != "UNKNOWN")
        self.assertEqual(nut, {"INDIA": 3, "CANADA": 1, "GRENADA": 1})

    def test_paprika_by_origin(self):
        pap = [r for r in self.spices if r["spice_type"] == "paprika"]
        n = tally(r["origin"] for r in pap)
        o = tally(r["origin"] for r in pap if r["over_eu"] == "1")
        self.assertEqual((o["HUNGARY"], n["HUNGARY"]), (4, 4))
        self.assertEqual((o["SPAIN"], n["SPAIN"]), (6, 15))
        self.assertEqual((o["INDIA"], n["INDIA"]), (2, 6))
        self.assertEqual((o["CANADA"], n["CANADA"]), (2, 5))
        self.assertEqual((o["UNKNOWN"], n["UNKNOWN"]), (39, 86))

    def test_no_country_share(self):
        self.assertEqual(sum(1 for r in self.spices if r["origin"] == "UNKNOWN"), 481)
        us = [r for r in self.spices if r["origin"] == "UNITED STATES"]
        self.assertEqual((len(us), sum(1 for r in us if r["over_eu"] == "1")), (21, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
