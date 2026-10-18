# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Recomputes the counts in docs/coumarin-cinnamon-0.1.0-result.md from the committed
# sealed sample table, so the published numbers can be checked offline.
import csv
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "coumarin_samples.csv")
PRIMARY = ("2012-13", "2014-15", "2015-16")
CASSIA_COUNTRIES = ("INDONESIA", "CHINA", "VIETNAM")


def rows():
    with open(CSV, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["cinnamon"] == "1"]


def tally(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


class CoumarinCinnamonResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()
        cls.primary = [r for r in cls.rows if r["file"] in PRIMARY]
        cls.rep = [r for r in cls.rows if r["file"] == "2011-12"]

    def test_counts_by_file(self):
        self.assertEqual(len(self.rows), 176)
        self.assertEqual(tally(r["file"] for r in self.rows),
                         {"2011-12": 107, "2012-13": 40, "2015-16": 29})

    def test_no_vanilla(self):
        with open(CSV, newline="", encoding="utf-8") as f:
            self.assertEqual(sum(1 for r in csv.DictReader(f) if r["vanilla"] == "1"), 0)

    def test_p1_p3_p4_classes(self):
        self.assertEqual(len(self.primary), 69)
        self.assertEqual(tally(r["class"] for r in self.primary),
                         {"cassia-type": 68, "verum-type": 1})
        # integer forms: 68/69 >= 0.80 and 0/69 < 0.10
        self.assertGreaterEqual(100 * 68, 80 * 69)

    def test_p2_maxima(self):
        top = max(self.primary, key=lambda r: float(r["coumarin_ppm"]))
        self.assertEqual((top["file"], float(top["coumarin_ppm"]), top["origin"]),
                         ("2012-13", 7621.1, "INDONESIA"))
        top16 = max((r for r in self.primary if r["file"] == "2015-16"),
                    key=lambda r: float(r["coumarin_ppm"]))
        self.assertEqual((float(top16["coumarin_ppm"]), top16["origin"]), (5040.0, "VIETNAM"))

    def test_p5_p6_no_claims(self):
        self.assertEqual(set(r["claim"] for r in self.rows), {"none"})

    def test_replication_classes(self):
        self.assertEqual(tally(r["class"] for r in self.rep),
                         {"cassia-type": 100, "verum-type": 4, "intermediate": 3})

    def test_pooled_classes(self):
        self.assertEqual(tally(r["class"] for r in self.rows),
                         {"cassia-type": 168, "verum-type": 5, "intermediate": 3})
        cassia = [float(r["coumarin_ppm"]) for r in self.rows if r["class"] == "cassia-type"]
        self.assertEqual((min(cassia), max(cassia)), (1267.6, 7816.3))

    def test_cassia_countries_all_cassia_type(self):
        sel = [r for r in self.rows if r["origin"] in CASSIA_COUNTRIES]
        self.assertEqual(tally(r["origin"] for r in sel),
                         {"INDONESIA": 10, "VIETNAM": 5, "CHINA": 2})
        self.assertTrue(all(r["class"] == "cassia-type" for r in sel))
        # primary set alone has only 3, below P7's minimum of 5
        self.assertEqual(sum(1 for r in self.primary if r["origin"] in CASSIA_COUNTRIES), 3)

    def test_sri_lanka_declared(self):
        sl = {r["sample"]: (r["class"], float(r["coumarin_ppm"]))
              for r in self.rows if r["origin"] == "SRI LANKA"}
        self.assertEqual(sl, {
            "2011COU0012": ("verum-type", 17.5),
            "2011COU0016": ("verum-type", 16.2),
            "2011COU0024": ("cassia-type", 4717.4),
            "2011COU0073": ("verum-type", 6.2),
            "2011COU0084": ("intermediate", 859.7),
            "C2015COUM00513": ("verum-type", 6.8),
        })
        self.assertEqual(sum(1 for r in self.primary if r["origin"] == "SRI LANKA"), 1)

    def test_verum_type_origins(self):
        self.assertEqual(tally(r["origin"] for r in self.rows if r["class"] == "verum-type"),
                         {"SRI LANKA": 4, "CANADA": 1})

    def test_no_country_count(self):
        self.assertEqual(sum(1 for r in self.rows if r["origin"] == "UNKNOWN"), 118)


if __name__ == "__main__":
    unittest.main(verbosity=2)
