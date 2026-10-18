# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes the counts in docs/alternaria-eu-0.1.0-result.md from the committed
# sealed sample table, so the published numbers can be checked offline.
import csv
import os
import re
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "alternaria_eu_samples.csv")
NO_COUNTRY = ("UNKNOWN", "IMPORTED (NO COUNTRY)")
CEREAL = (r"cereal|c[ée]r[ée]ale|\boat|avoine|\brice\b|\briz\b|barley|\borge\b|wheat|\bbl[ée]\b|grain|biscuit"
          r"|cracker|puff|rusk|pasta|p[âa]tes")


def rows():
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    return float(x) if x != "" else None


def tally(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


class AlternariaEuResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()

    def test_records(self):
        self.assertEqual(len(self.rows), 2596)
        # one sample number carries two product names (one per toxin), so it is two records
        split = [r for r in self.rows if r["sample"] == "C2020ALTN00315"]
        self.assertEqual(sorted(r["product"] for r in split), ["Pepper (GH)", "Pepper - Hot - Fresh"])

    def test_classes_as_frozen(self):
        self.assertEqual(tally(r["category"] for r in self.rows if r["category"]),
                         {"processed tomato": 200, "sunflower seeds": 34, "sunflower oil": 41,
                          "infant cereal": 92})

    def test_infant_cereal_class_is_a_rule_defect(self):
        infant = [r for r in self.rows if r["category"] == "infant cereal"]
        self.assertEqual(set(r["product"] for r in infant), {"Infant Food (non-cereal)"})
        corrected = [r for r in self.rows
                     if "infant" in r["product"].lower()
                     and re.search(CEREAL, r["product"].lower().replace("non-cereal", ""))]
        self.assertEqual(corrected, [])

    def test_above_as_frozen_and_corrected(self):
        above = [r for r in self.rows if r["state"] == "above"]
        self.assertEqual(tally(r["category"] for r in above), {"sunflower oil": 3, "infant cereal": 4})
        oil = [r for r in above if r["category"] == "sunflower oil"]
        self.assertEqual(set(r["origin"] for r in oil), {"CANADA"})
        self.assertEqual(sum(1 for r in self.rows
                             if r["category"] == "sunflower oil" and r["origin"] == "CANADA"), 4)
        # P9 as frozen: 1 of 4 country-declaring above-level samples is foreign
        declared = [r for r in above if r["origin"] not in NO_COUNTRY]
        self.assertEqual((sum(1 for r in declared if r["origin"] != "CANADA"), len(declared)), (1, 4))

    def test_tomato(self):
        tom = [r for r in self.rows if r["category"] == "processed tomato"]
        self.assertTrue(all(r["state"] == "within" for r in tom))
        top = max(tom, key=lambda r: float(r["total_ppb"]))
        self.assertEqual((top["sample"], top["origin"], float(top["total_ppb"])),
                         ("C2016ALTN00051", "ITALY", 6.72))
        self.assertEqual(max(float(r["aoh_ppb"]) for r in tom), 6.22)
        self.assertEqual(max(float(r["ame_ppb"]) for r in tom), 0.9)
        for year, n, pos, low in (("2015", 100, 36, 0.08), ("2016", 100, 40, 0.06)):
            ys = [float(r["total_ppb"]) for r in tom if r["sample"].startswith("C" + year)]
            positives = [x for x in ys if x > 0]
            self.assertEqual((len(ys), len(positives), min(positives)), (n, pos, low))

    def test_sunflower_seeds(self):
        seeds = [r for r in self.rows if r["category"] == "sunflower seeds"]
        self.assertTrue(all(r["state"] == "within" for r in seeds))
        self.assertEqual(max(float(r["total_ppb"]) for r in seeds), 20.46)

    def test_top_sample(self):
        top = max((r for r in self.rows if r["total_ppb"]), key=lambda r: float(r["total_ppb"]))
        self.assertEqual((top["sample"], top["product"], top["origin"], float(top["total_ppb"])),
                         ("C2019ALTN00289", "Juice - Pomegranate", "UNKNOWN", 871.0))

    def test_pomegranate(self):
        pom = [r for r in self.rows if r["pomegranate"] == "1" and r["total_ppb"]]
        self.assertEqual(len(pom), 184)
        high = [r for r in pom if float(r["total_ppb"]) >= 100]
        self.assertEqual(tally(r["origin"] for r in high), {"UNKNOWN": 38, "UNITED STATES": 11, "CANADA": 1})
        canada = [float(r["total_ppb"]) for r in pom if r["origin"] == "CANADA"]
        foreign = [float(r["total_ppb"]) for r in pom if r["origin"] not in NO_COUNTRY + ("CANADA",)]
        self.assertEqual((len(canada), len(foreign)), (8, 121))
        self.assertAlmostEqual(statistics.median(canada), 46.75, places=6)
        self.assertAlmostEqual(statistics.median(foreign), 0.208, places=6)
        for origin, n, top in (("TURKEY", 7, 46.3), ("AZERBAIJAN", 11, 72.2)):
            xs = [float(r["total_ppb"]) for r in pom if r["origin"] == origin]
            self.assertEqual((len(xs), max(xs)), (n, top))
        unknown = [float(r["total_ppb"]) for r in pom if r["origin"] == "UNKNOWN"]
        self.assertEqual(len(unknown), 55)
        self.assertAlmostEqual(statistics.median(unknown), 308.2, places=6)

    def test_infant_puree_max(self):
        puree = [r for r in self.rows if r["product"] == "Infant Food - Puree"]
        top = max(puree, key=lambda r: float(r["total_ppb"]))
        self.assertEqual((top["sample"], top["origin"], float(top["total_ppb"])),
                         ("C2016ALTN00443", "UNITED STATES", 37.1))

    def test_ame_over_aoh(self):
        both = [r for r in self.rows if r["aoh_ppb"] and r["ame_ppb"] and float(r["total_ppb"]) > 0]
        self.assertEqual((sum(1 for r in both if float(r["ame_ppb"]) > float(r["aoh_ppb"])), len(both)),
                         (189, 1551))


if __name__ == "__main__":
    unittest.main(verbosity=2)
