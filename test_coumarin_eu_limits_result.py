# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Recompute every number published in docs/coumarin-eu-limits-0.1.1-result.md.

Reads data/coumarin_eu_limits_samples.csv (the sealed per-sample output of job
coumarin-eu-limits-v2, CFIA 2013-14 coumarin survey, Open Government Licence - Canada) and
data/coumarin-eu-limits.csv (the published group table), using only csv + unittest.
"""
import csv
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "data", "coumarin_eu_limits_samples.csv")
TABLE = os.path.join(HERE, "data", "coumarin-eu-limits.csv")

# Pre-registered thresholds (docs/coumarin-eu-limits-0.1.0-prereg.md, unchanged in 0.1.1).
G0_N_ROWS = (740, 749)
G0_MAX_PPM = (2200.0, 2800.0)
P1_FINE_SHARE = (0.20, 0.50)
P2_CEREAL_SHARE = (0.03, 0.22)


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        v = r["coumarin_ppm"].strip()
        r["ppm"] = float(v) if v else None
    return rows


def load_table():
    with open(TABLE, newline="", encoding="utf-8") as fh:
        return {(r["group"], r["subcat"]): r for r in csv.DictReader(fh)}


def select(rows, group, subcat):
    """The sample selection behind each row of the group table."""
    m = [r for r in rows if r["ppm"] is not None and r["group"] == group]
    if subcat in ("all", "all-at-50", "cereal-and-oatmeal"):
        return m
    if subcat == "cereal-core":
        return [r for r in m if r["subcat"] == "cereal"]
    if subcat == "cereal-adult":
        return [r for r in m if r["subcat"] == "cereal" and r["product"] == "Cereal - Adult"]
    if subcat == "cereal-children":
        return [r for r in m if r["subcat"] == "cereal" and r["product"] == "Cereal - Children"]
    return [r for r in m if r["subcat"] == subcat]


def stats(sel, limit):
    ppms = sorted(r["ppm"] for r in sel)
    n = len(ppms)
    over = sum(1 for p in ppms if p > limit)
    return {"n": n, "n_detected": sum(1 for p in ppms if p > 0), "n_over": over,
            "share": over / n, "median": statistics.median(ppms), "max": ppms[-1]}


class TestSamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        cls.measured = [r for r in cls.rows if r["ppm"] is not None]

    def test_g0_gate(self):
        self.assertEqual(len(self.measured), 749)
        self.assertEqual(max(r["ppm"] for r in self.measured), 2510.0)
        self.assertTrue(G0_N_ROWS[0] <= len(self.measured) <= G0_N_ROWS[1])

    def test_unit_census(self):
        self.assertEqual({r["unit"] for r in self.measured}, {"ug/g"})

    def test_over_limit_column(self):
        for r in self.measured:
            if r["group"] in ("fine-bakery", "breakfast-cereal"):
                want = "yes" if r["ppm"] > float(r["eu_limit"]) else "no"
                self.assertEqual(r["over_limit"], want, r)

    def test_grades(self):
        fine = stats(select(self.rows, "fine-bakery", "all"), 15.0)
        core = stats(select(self.rows, "breakfast-cereal", "cereal-core"), 20.0)
        self.assertEqual((fine["n_over"], fine["n"]), (42, 100))
        self.assertEqual((core["n_over"], core["n"]), (3, 136))
        self.assertTrue(P1_FINE_SHARE[0] <= fine["share"] <= P1_FINE_SHARE[1])          # P1 met
        self.assertFalse(P2_CEREAL_SHARE[0] <= core["share"] <= P2_CEREAL_SHARE[1])     # P2 failed
        self.assertLess(core["share"], P2_CEREAL_SHARE[0])                              # below range
        self.assertGreater(fine["share"], core["share"])                                # P3 met


class TestTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        cls.table = load_table()

    def test_every_row_recomputes(self):
        self.assertEqual(len(self.table), 10)
        for (group, subcat), t in self.table.items():
            s = stats(select(self.rows, group, subcat), float(t["limit"]))
            with self.subTest(group=group, subcat=subcat):
                self.assertEqual(int(t["n"]), s["n"])
                self.assertEqual(int(t["n_detected"]), s["n_detected"])
                self.assertEqual(int(t["n_over"]), s["n_over"])
                self.assertAlmostEqual(float(t["share"]), round(s["share"], 4), places=9)
                self.assertAlmostEqual(float(t["median"]), round(s["median"], 2), places=9)
                self.assertAlmostEqual(float(t["max"]), s["max"], places=9)

    def test_parts_add_up(self):
        t = self.table
        n = lambda k: int(t[k]["n"])
        over = lambda k: int(t[k]["n_over"])
        fb = [("fine-bakery", s) for s in ("baked-goods", "cookie", "muffin")]
        self.assertEqual(sum(n(k) for k in fb), n(("fine-bakery", "all")))
        self.assertEqual(sum(over(k) for k in fb), over(("fine-bakery", "all")))
        ac = [("breakfast-cereal", s) for s in ("cereal-adult", "cereal-children")]
        self.assertEqual(sum(n(k) for k in ac), n(("breakfast-cereal", "cereal-core")))
        self.assertEqual(n(("breakfast-cereal", "cereal-core")) + n(("breakfast-cereal", "oatmeal")),
                         n(("breakfast-cereal", "cereal-and-oatmeal")))

    def test_headline_numbers(self):
        t = self.table
        self.assertEqual(t[("fine-bakery", "all")]["n_over"], "42")
        self.assertEqual(t[("fine-bakery", "baked-goods")]["n_over"], "39")
        self.assertEqual(t[("fine-bakery", "cookie")]["n_over"], "2")
        self.assertEqual(t[("fine-bakery", "all-at-50")]["n_over"], "11")
        self.assertEqual(t[("breakfast-cereal", "cereal-core")]["n_over"], "3")
        self.assertEqual(t[("breakfast-cereal", "cereal-children")]["n_over"], "0")
        self.assertEqual(t[("breakfast-cereal", "oatmeal")]["n_over"], "3")
        self.assertEqual(t[("breakfast-cereal", "cereal-and-oatmeal")]["n_over"], "6")


if __name__ == "__main__":
    unittest.main()
