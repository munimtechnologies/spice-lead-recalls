# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
"""Recompute every number published in docs/coumarin-early-surveys-0.1.0-result.md.

Reads data/coumarin_early_samples.csv (the 139 non-cinnamon samples of CFIA's open 2011-12 and
2012-13 coumarin files, Open Government Licence - Canada; sealed output of job coumarin-early-v1)
and data/coumarin_early_surveys.csv (one line per Product label from the same job; its cinnamon
lines aggregate values published by coumarin-cinnamon 0.1.0). Uses only csv, statistics and
unittest.
"""
import csv
import os
import statistics
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "data", "coumarin_early_samples.csv")
TABLE = os.path.join(HERE, "data", "coumarin_early_surveys.csv")

LABELS = {
    "2011-12": {"Ground Cinnamon": 87, "Cinnamon Sticks": 20, "Spice mix": 24, "Tea": 11,
                "Cereal": 15, "Baked Goods": 20, "Baking mix": 7, "Baby Food": 9},
    "2012-13": {"Cinnamon": 40, "Spice Mixes": 53},
}
CINNAMON = {"2011-12": ("Ground Cinnamon", "Cinnamon Sticks"), "2012-13": ("Cinnamon",)}

# CFIA's printed figures, as registered in docs/coumarin-early-surveys-0.1.0-prereg.md.
PRINTED_MAX_1112 = {"Spice mix": "2014", "Tea": "1040", "Baked Goods": "95.3", "Cereal": "56.7",
                    "Baking mix": "45.8", "Baby Food": "14.9"}
PRINTED_DETECTED_PCT = {"2011-12": 98, "2012-13": 100}
REPRINTS = {"T1": ("2011-12", "Tea", 11, "<0.29", "1040", "380"),
            "T2": ("2011-12", "Spice mix", 24, "<0.29", "2014", "352"),
            "T3": ("2012-13", "Spice Mixes", 53, "30", "3078", "568")}

# The value CFIA prints as "<0.29" is written in the open 2011-12 file as the bare number 0.29.
LOD_1112 = 0.29

PUBLISHED_GRADES = {"E0": True, "C1": True, "C2": False, "C3": False, "V1": False, "V2": False,
                    "V3": True, "R1": True, "R2": True, "R3": True, "R4": True, "R5": True}

# EFSA TDI 0.1 mg/kg bw/day; per-cup scenarios of coumarin-tea 0.1.0 (100% transfer).
TDI = 0.1
CUPS = {"A1": (60.0, 2.0), "A2": (60.0, 4.0), "C1": (15.0, 2.0), "C2": (15.0, 4.0)}


def decimals(printed):
    return len(printed.split(".")[1]) if "." in printed else 0


def matches(value, printed):
    """True when `value` rounds to the printed figure at its printed precision."""
    return abs(value - float(printed)) <= 0.5 * 10 ** (-decimals(printed)) + 1e-9


def verdict(mean_pos, mean_all, printed):
    p, a = matches(mean_pos, printed), matches(mean_all, printed)
    if p and a:
        return "both"
    if p:
        return "positives"
    if a:
        return "all-samples"
    return "neither"


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_table():
    with open(TABLE, newline="", encoding="utf-8") as fh:
        return {(r["survey"], r["product_label"]): r for r in csv.DictReader(fh)}


def values(samples, survey, label):
    return sorted(float(r["coumarin_ppm"]) for r in samples
                  if r["survey"] == survey and r["product_label"] == label)


def is_lod(x):
    return abs(x - LOD_1112) < 1e-9


def lod_read(ppms):
    """The post-hoc reading: a 2011-12 value of exactly 0.29 is a non-detect (0)."""
    return sorted(0.0 if is_lod(p) else p for p in ppms)


def stats(ppms):
    det = [p for p in ppms if p > 0]
    return {"n": len(ppms), "n_detected": len(det), "min": ppms[0],
            "min_detected": det[0] if det else None, "median": statistics.median(ppms),
            "mean_all": statistics.fmean(ppms),
            "mean_positives": statistics.fmean(det) if det else None, "max": ppms[-1]}


def pct_tdi_cup(ppm, bw, grams):
    return 100.0 * ppm * grams / 1000.0 / (TDI * bw)


def unseen():
    return [(s, lab) for s in LABELS for lab in LABELS[s] if lab not in CINNAMON[s]]


class TestTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s, cls.t = load_samples(), load_table()

    def test_labels_and_counts(self):
        self.assertEqual(len(self.s), 139)
        self.assertEqual(set(self.t), {(s, lab) for s in LABELS for lab in LABELS[s]})
        for (s, lab), r in self.t.items():
            self.assertEqual(int(r["n"]), LABELS[s][lab], msg=lab)
            self.assertEqual(int(r["cinnamon"]), int(lab in CINNAMON[s]), msg=lab)
        for s, lab in unseen():
            self.assertEqual(len(values(self.s, s, lab)), LABELS[s][lab], msg=lab)

    def test_unseen_rows_recompute(self):
        for s, lab in unseen():
            st, r = stats(values(self.s, s, lab)), self.t[(s, lab)]
            with self.subTest(row=(s, lab)):
                self.assertEqual(int(r["n_detected"]), st["n_detected"])
                for key in ("min_detected", "median", "mean_positives", "mean_all", "max"):
                    self.assertAlmostEqual(float(r[key]), st[key], places=3, msg=key)

    def test_cinnamon_rows(self):
        for s, labs in CINNAMON.items():
            for lab in labs:
                r = self.t[(s, lab)]
                self.assertEqual(int(r["n_detected"]), int(r["n"]), msg=lab)
        self.assertAlmostEqual(float(self.t[("2011-12", "Ground Cinnamon")]["min_detected"]), 16.2)
        self.assertAlmostEqual(float(self.t[("2011-12", "Ground Cinnamon")]["max"]), 7816.3)
        self.assertAlmostEqual(float(self.t[("2011-12", "Ground Cinnamon")]["mean_all"]), 3594.0,
                               delta=0.05)
        self.assertAlmostEqual(float(self.t[("2011-12", "Cinnamon Sticks")]["min_detected"]), 6.2)
        self.assertAlmostEqual(float(self.t[("2011-12", "Cinnamon Sticks")]["max"]), 6823.2)
        self.assertAlmostEqual(float(self.t[("2012-13", "Cinnamon")]["max"]), 7621.1)

    def test_published_category_table(self):
        want = {("2011-12", "Spice mix"): (75.2, 351.9, 2013.8),
                ("2011-12", "Tea"): (281.2, 379.9, 1040.1),
                ("2011-12", "Cereal"): (6.6, 10.0, 56.7),
                ("2011-12", "Baked Goods"): (9.8, 15.8, 95.3),
                ("2011-12", "Baking mix"): (21.9, 22.9, 45.8),
                ("2011-12", "Baby Food"): (5.2, 6.3, 14.9),
                ("2012-13", "Spice Mixes"): (329.3, 567.7, 3077.6)}
        for key, (med, mean, mx) in want.items():
            st = stats(values(self.s, *key))
            with self.subTest(row=key):
                self.assertAlmostEqual(st["median"], med, places=6)
                self.assertEqual(round(st["mean_all"], 1), mean)
                self.assertAlmostEqual(st["max"], mx)


class TestGrades(unittest.TestCase):
    """The twelve registered grades, as parsed (every number in the file read as measured)."""

    @classmethod
    def setUpClass(cls):
        cls.s, cls.t = load_samples(), load_table()

    def grades(self):
        g = {"E0": True}
        g["C1"] = all(matches(values(self.s, "2011-12", lab)[-1], pm)
                      for lab, pm in PRINTED_MAX_1112.items())
        c2 = []
        for s in LABELS:
            n = sum(int(self.t[(s, lab)]["n"]) for lab in LABELS[s])
            det = sum(int(self.t[(s, lab)]["n_detected"]) for lab in LABELS[s])
            c2.append(round(100.0 * det / n) == PRINTED_DETECTED_PCT[s])
        g["C2"] = all(c2)
        c3, verdicts = [], {}
        for rid, (s, lab, n, pmin, pmax, pavg) in REPRINTS.items():
            st = stats(values(self.s, s, lab))
            min_ok = (st["n_detected"] < st["n"]) if pmin.startswith("<") \
                else matches(st["min"], pmin)
            c3.append(st["n"] == n and min_ok and matches(st["max"], pmax))
            verdicts[rid] = verdict(st["mean_positives"], st["mean_all"], pavg)
        g["C3"] = all(c3)
        g["V1"] = verdicts["T1"] == "positives"
        g["V2"] = verdicts["T2"] == "positives"
        g["V3"] = verdicts["T3"] == "both"
        baked = values(self.s, "2011-12", "Baked Goods")
        cereal = values(self.s, "2011-12", "Cereal")
        tea = values(self.s, "2011-12", "Tea")
        baby = values(self.s, "2011-12", "Baby Food")
        g["R1"] = sum(p > 15 for p in baked) <= 8
        g["R2"] = sum(p > 50 for p in baked) <= 3
        g["R3"] = 1 <= sum(p > 20 for p in cereal) <= 2
        g["R4"] = 1 <= sum(pct_tdi_cup(p, *CUPS["C1"]) > 100 for p in tea) <= 3
        g["R5"] = statistics.median(baby) < statistics.median(cereal)
        return g, verdicts

    def test_grades_as_published(self):
        g, _ = self.grades()
        self.assertEqual(g, PUBLISHED_GRADES)
        self.assertEqual(sum(g.values()), 8)
        self.assertEqual(sum(v for k, v in g.items() if k != "E0"), 7)

    def test_failures_as_described(self):
        _, verdicts = self.grades()
        self.assertEqual(verdicts, {"T1": "both", "T2": "both", "T3": "both"})
        det = sum(int(self.t[("2011-12", lab)]["n_detected"]) for lab in LABELS["2011-12"])
        self.assertEqual(det, 193)
        t3 = stats(values(self.s, "2012-13", "Spice Mixes"))
        self.assertAlmostEqual(t3["min"], 29.7)
        self.assertEqual(t3["n_detected"], 53)
        self.assertAlmostEqual(t3["mean_all"], 567.74, delta=0.005)

    def test_replication_counts(self):
        baked = values(self.s, "2011-12", "Baked Goods")
        self.assertEqual(sum(p > 15 for p in baked), 4)
        self.assertEqual(sum(p > 50 for p in baked), 2)
        self.assertEqual(sum(p > 20 for p in values(self.s, "2011-12", "Cereal")), 1)
        tea = values(self.s, "2011-12", "Tea")
        self.assertEqual(sum(pct_tdi_cup(p, *CUPS["C1"]) > 100 for p in tea), 2)
        self.assertAlmostEqual(statistics.median(values(self.s, "2011-12", "Baby Food")), 5.2)
        self.assertAlmostEqual(statistics.median(values(self.s, "2011-12", "Cereal")), 6.6)


class TestNonDetectReading(unittest.TestCase):
    """Post hoc: the four 2011-12 values of exactly 0.29 read as non-detects."""

    @classmethod
    def setUpClass(cls):
        cls.s, cls.t = load_samples(), load_table()

    def test_the_four_lod_rows(self):
        rows = [r for r in self.s if r["survey"] == "2011-12" and is_lod(float(r["coumarin_ppm"]))]
        self.assertEqual(sorted(r["product_label"] for r in rows),
                         ["Baked Goods", "Cereal", "Spice mix", "Tea"])
        two_dp = [r["coumarin_ppm"] for r in self.s
                  if "." in r["coumarin_ppm"] and len(r["coumarin_ppm"].split(".")[1]) == 2]
        self.assertEqual(two_dp, ["0.29"] * 4)
        rest = [float(r["coumarin_ppm"]) for r in self.s if not is_lod(float(r["coumarin_ppm"]))]
        self.assertAlmostEqual(min(rest), 1.2)
        self.assertFalse(any(is_lod(float(r["coumarin_ppm"])) for r in self.s
                             if r["survey"] == "2012-13"))
        self.assertGreater(min(float(self.t[(s, lab)]["min_detected"])
                               for s, labs in CINNAMON.items() for lab in labs), 6.0)

    def test_detection_rate_reproduces_cfia(self):
        n = sum(int(self.t[("2011-12", lab)]["n"]) for lab in LABELS["2011-12"])
        n_lod = sum(1 for r in self.s
                    if r["survey"] == "2011-12" and is_lod(float(r["coumarin_ppm"])))
        det = n - n_lod
        self.assertEqual((n, det), (193, 189))
        self.assertEqual(round(100.0 * det / n), PRINTED_DETECTED_PCT["2011-12"])
        self.assertAlmostEqual(100.0 * det / n, 97.9, delta=0.05)

    def test_reprinted_rows(self):
        want = {"T1": (10, 379.84, 379.86, 417.82, "all-samples"),
                "T2": (23, 351.92, 351.93, 367.22, "all-samples"),
                "T3": (53, 567.74, 567.74, 567.74, "both")}
        for rid, (n_det, m0, mlod, mpos, v) in want.items():
            s, lab, n, pmin, pmax, pavg = REPRINTS[rid]
            raw = values(self.s, s, lab)
            st = stats(lod_read(raw))
            with self.subTest(row=rid):
                self.assertEqual(st["n"], n)
                self.assertEqual(st["n_detected"], n_det)
                if pmin.startswith("<"):
                    self.assertLess(st["n_detected"], st["n"])
                else:
                    self.assertTrue(matches(st["min"], pmin))
                self.assertTrue(matches(st["max"], pmax))
                self.assertAlmostEqual(st["mean_all"], m0, delta=0.005)
                self.assertAlmostEqual(statistics.fmean(raw), mlod, delta=0.005)
                self.assertAlmostEqual(st["mean_positives"], mpos, delta=0.005)
                self.assertEqual(verdict(st["mean_positives"], st["mean_all"], pavg), v)
                # All-sample mean matches whether a non-detect counts as 0 or as 0.29.
                self.assertTrue(matches(statistics.fmean(raw), pavg))

    def test_positives_basis_and_margin(self):
        tea = stats(lod_read(values(self.s, "2011-12", "Tea")))
        spice = stats(lod_read(values(self.s, "2011-12", "Spice mix")))
        self.assertEqual(round(tea["mean_positives"]), 418)
        self.assertEqual(round(spice["mean_positives"]), 367)
        self.assertGreater((tea["mean_positives"] - 380) / 0.5, 75)
        self.assertAlmostEqual((tea["mean_positives"] - 380) / 0.5, 76, delta=0.5)
        self.assertGreater((spice["mean_positives"] - 352) / 0.5, 30)
        self.assertAlmostEqual((spice["mean_positives"] - 352) / 0.5, 30, delta=0.5)

    def test_reading_changes_no_replication(self):
        for lab, limit in (("Baked Goods", 15), ("Baked Goods", 50), ("Cereal", 20)):
            raw = values(self.s, "2011-12", lab)
            self.assertEqual(sum(p > limit for p in raw), sum(p > limit for p in lod_read(raw)))
        for lab in ("Cereal", "Tea", "Spice mix", "Baked Goods", "Baby Food"):
            raw = values(self.s, "2011-12", lab)
            self.assertAlmostEqual(statistics.median(raw), statistics.median(lod_read(raw)))
            self.assertAlmostEqual(raw[-1], lod_read(raw)[-1])


class TestDescriptive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = load_samples()

    def test_tea_per_cup(self):
        tea = values(self.s, "2011-12", "Tea")
        counts = {k: sum(pct_tdi_cup(p, bw, g) > 100 for p in tea) for k, (bw, g) in CUPS.items()}
        self.assertEqual(counts, {"A1": 0, "A2": 0, "C1": 2, "C2": 4})
        self.assertEqual(round(pct_tdi_cup(tea[-1], *CUPS["A1"]), 1), 34.7)
        self.assertEqual(round(pct_tdi_cup(tea[-1], *CUPS["A2"]), 1), 69.3)
        self.assertEqual(round(100.0 * counts["C1"] / len(tea), 1), 18.2)
        # 115 (2013-14) + 210 (2014-15) + 297 (2015-16) published teas + these 11.
        self.assertEqual(115 + 210 + 297 + len(tea), 633)

    def test_baby_food(self):
        baby = values(self.s, "2011-12", "Baby Food")
        pct30 = [100.0 * p * 30 / 1000.0 / (TDI * 8.0) for p in baby]
        self.assertEqual(sum(x > 100 for x in pct30), 0)
        self.assertEqual(round(max(pct30), 1), 55.9)
        self.assertEqual(sum(2 * x > 100 for x in pct30), 1)

    def test_spice_mix_maxima(self):
        m12 = values(self.s, "2012-13", "Spice Mixes")[-1]
        m11 = values(self.s, "2011-12", "Spice mix")[-1]
        self.assertAlmostEqual(m12, 3077.6)
        self.assertAlmostEqual(m11, 2013.8)
        self.assertGreater(m12, m11)


if __name__ == "__main__":
    unittest.main()
