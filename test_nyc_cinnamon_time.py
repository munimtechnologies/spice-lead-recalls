# Apache-2.0. Made by MV2 of Munim, Inc. with AI agents.
# Offline checks of nyc_cinnamon_time on synthetic rows, then every count in
# docs/nyc-cinnamon-time-0.1.0-result.md recomputed from the committed snapshot in data/.
import csv
import os
import tempfile
import unittest

import nyc_cinnamon_time as nct


def rec(name, conc, frame="C", date="2020-05-01", country="INDIA", row_id="1", **kw):
    r = {"product_type": "Food-Spice", "metal": "Lead", "units": "ppm", "analysis_type": "Laboratory",
         "investigation_type": frame, "concentration": str(conc), "product_name": name,
         "collection_date": date + "T00:00:00.000", "purchase_country": country, "row_id": row_id}
    r.update(kw)
    return r


class Names(unittest.TestCase):
    def test_whole_words(self):
        for name in ("Ground Cinnamon", "CASSIA BARK", "Canela Molida", "Dalchini", "Darchin powder",
                     "TARÇIN", "tarçın toz", "Kayu Manis", "Bột Quế"):
            self.assertEqual(nct.kind(name), "cinnamon", name)
        for name in ("Queso seasoning", "Cassiano Chili", "Canelones", "Turmeric", "Que rico mix"):
            self.assertIsNone(nct.kind(name), name)

    def test_blends(self):
        for name in ("Cinnamon Sugar", "Garam Masala with Cinnamon", "Cinnamon Tea", "Five Spices Cassia",
                     "Mixed spice cinnamon"):
            self.assertEqual(nct.kind(name), "blend", name)


class Periods(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(nct.period_of("2018-12-31T00:00:00"), "before-2019")
        self.assertEqual(nct.period_of("2019-01-01"), "2019-2022")
        self.assertEqual(nct.period_of("2023-10-31"), "2023-to-oct")
        self.assertEqual(nct.period_of("2023-11-01"), "post-recall")
        self.assertEqual(nct.period_of("2024-12-31"), "post-recall")
        self.assertEqual(nct.period_of("2025-01-01"), "2025-on")
        self.assertEqual(nct.period_of(""), "no-date")
        self.assertEqual(nct.period_of("unknown"), "no-date")


class Filter(unittest.TestCase):
    def test_nyc_rows_filter(self):
        recs = [rec("Cinnamon", 3), rec("Cinnamon", 3, metal="Arsenic"), rec("Cinnamon", 3, units="ug/g"),
                rec("Cinnamon", 3, analysis_type="XRF"), rec("Cinnamon", 3, product_type="Food-Other"),
                rec("Cinnamon", -1), rec("Cinnamon", ""), rec("Paprika", 80)]
        rows = nct.cinnamon_rows(recs)
        self.assertEqual([r["status"] for r in rows], ["value", "nd", "missing"])
        self.assertEqual(nct.counts(rows), {"rows": 2, "detected": 1, "over_2": 1, "ge_50": 0, "missing": 1})

    def test_groups(self):
        self.assertEqual(nct.purchase_group("United States"), "US")
        self.assertEqual(nct.purchase_group("UNKNOWN OR NOT STATED"), "unknown")
        self.assertEqual(nct.purchase_group(""), "unknown")
        self.assertEqual(nct.purchase_group("Georgia"), "abroad")


class Score(unittest.TestCase):
    def test_levels_are_strict_and_inclusive(self):
        rows = nct.cinnamon_rows([rec("Cinnamon", 2.0), rec("Cinnamon", 2.01), rec("Cinnamon", 50)])
        self.assertEqual(nct.counts(rows)["over_2"], 2)
        self.assertEqual(nct.counts(rows)["ge_50"], 1)

    def test_underpowered(self):
        s = nct.score(nct.cinnamon_rows([rec("Cinnamon", 5)] * 14))
        self.assertTrue(s["underpowered"])
        self.assertFalse(s["predictions"]["P1_rows_45_in_15_120"])
        self.assertEqual(s["predictions"]["P2_over2_40pct_in_15_65"], "not scorable")
        self.assertEqual(s["predictions"]["P4_ratio_ge_2"], "not scorable")

    def test_full_grade(self):
        recs = []
        # 2019-2022: 8 case rows (2 per year), 2 over 2.0
        for i in range(8):
            recs.append(rec("Cinnamon", 3 if i < 2 else 1, date="2020-03-0%d" % (i + 1)))
        # post-recall: 7 case rows (6 per year), 1 over 2.0 (at 60 ppm)
        for i in range(6):
            recs.append(rec("Cinnamon", 1, date="2024-02-0%d" % (i + 1)))
        recs.append(rec("Cinnamon", 60, date="2024-03-01"))
        # 5 more case rows before 2019, 2 over 2.0, plus 2 non-detects
        recs += [rec("Cassia", 4, date="2015-01-01"), rec("Cassia", 4, date="2015-01-02"),
                 rec("Cassia", 1, date="2015-01-03"), rec("Cassia", -1, date="2015-01-04"),
                 rec("Cassia", 0, date="2015-01-05")]
        # store: January 2024 (ignored for H2) and outside, 1 of 4 detected over 2.0
        recs += [rec("Cinnamon", 9, frame="S", date="2024-01-10")]
        recs += [rec("Cinnamon", v, frame="S", date="2022-06-01") for v in (3, 1, 1, 1)]
        s = nct.score(nct.cinnamon_rows(recs))
        self.assertEqual(s["case"], {"rows": 20, "detected": 18, "over_2": 5, "ge_50": 1, "missing": 0})
        self.assertEqual(s["case_over_2_rate_detected"], 0.2778)
        self.assertEqual(s["case_ge_50_rate_all"], 0.05)
        self.assertEqual(s["P4_ratio"], 3.0)
        self.assertEqual(s["store_outside_jan2024_rate"], 0.25)
        self.assertEqual(s["predictions"], {"P1_rows_45_in_15_120": True, "P2_over2_40pct_in_15_65": True,
                                            "P3_ge50_4pct_in_0_12": True, "P4_ratio_ge_2": True,
                                            "P4_ratio_in_0.8_5": True})
        self.assertEqual(s["hypotheses"], {"H1_gross_below_11pct": True,
                                           "H2_case_rate_ge_store_outside_jan2024": True,
                                           "H3_post_recall_not_majority": True})


class Snapshot(unittest.TestCase):
    """The graded counts, from data/nyc_spice_lead_snapshot_2026-10-17.csv (committed v0.4.33)."""

    @classmethod
    def setUpClass(cls):
        cls.rows = nct.cinnamon_rows(nct.read_snapshot())
        cls.s = nct.score(cls.rows)

    def ids(self, frame, test):
        return sorted(int(r["row_id"]) for r in self.rows
                      if r["kind"] == "cinnamon" and r["frame"] == frame and r["status"] == "value"
                      and test(r["value"]))

    def test_case_frame(self):
        self.assertEqual(self.s["case"], {"rows": 45, "detected": 26, "over_2": 8, "ge_50": 1, "missing": 0})
        self.assertEqual(self.ids("C", lambda v: v > nct.BARK_LEVEL),
                         [665, 702, 1253, 3725, 5525, 7833, 8278, 8429])
        self.assertEqual(self.ids("C", lambda v: v >= nct.GROSS), [702])
        self.assertEqual(self.ids("C", lambda v: v == nct.BARK_LEVEL), [765])  # at the level: not counted

    def test_store_frame_matches_asta_yardstick(self):
        self.assertEqual(self.s["store"], {"rows": 25, "detected": 22, "over_2": 11, "ge_50": 0, "missing": 0})
        self.assertEqual(self.ids("S", lambda v: v > nct.BARK_LEVEL),
                         [7584, 7588, 7590, 7592, 7611, 7613, 7615, 7622, 7628, 7630, 8705])
        jan24 = [r for r in self.rows if r["kind"] == "cinnamon" and r["frame"] == "S" and nct.is_jan_2024(r)]
        self.assertEqual((len(jan24), nct.counts(jan24)["over_2"]), (21, 10))
        self.assertEqual(self.s["store_outside_jan2024"],
                         {"rows": 4, "detected": 2, "over_2": 1, "ge_50": 0, "missing": 0})

    def test_case_by_period(self):
        got = {k: (v["rows"], v["detected"], v["over_2"], v["ge_50"])
               for k, v in self.s["case_by_period"].items()}
        self.assertEqual(got, {"before-2019": (9, 7, 3, 1), "2019-2022": (12, 7, 2, 0),
                               "2023-to-oct": (2, 2, 0, 0), "post-recall": (11, 4, 3, 0),
                               "2025-on": (11, 6, 0, 0), "no-date": (0, 0, 0, 0)})

    def test_case_by_group(self):
        got = {k: (v["rows"], v["detected"], v["over_2"], v["ge_50"])
               for k, v in self.s["case_by_group"].items()}
        self.assertEqual(got, {"US": (23, 13, 4, 0), "abroad": (13, 9, 4, 1), "unknown": (9, 4, 0, 0)})

    def test_set_apart(self):
        self.assertEqual(self.s["other_frames"], {"rows": 3, "detected": 3, "over_2": 0, "ge_50": 0,
                                                  "missing": 0})
        self.assertEqual([r["row_id"] for r in self.rows if r["kind"] == "blend"], ["2390"])

    def test_grades(self):
        self.assertEqual(self.s["case_over_2_rate_detected"], 0.3077)
        self.assertEqual(self.s["case_ge_50_rate_all"], 0.0222)
        self.assertEqual(self.s["P4_ratio"], 3.1429)
        self.assertEqual(self.s["store_outside_jan2024_rate"], 0.5)
        self.assertFalse(self.s["underpowered"])
        self.assertEqual(self.s["predictions"], {"P1_rows_45_in_15_120": True, "P2_over2_40pct_in_15_65": True,
                                                 "P3_ge50_4pct_in_0_12": True, "P4_ratio_ge_2": True,
                                                 "P4_ratio_in_0.8_5": True})
        self.assertEqual(self.s["hypotheses"], {"H1_gross_below_11pct": True,
                                                "H2_case_rate_ge_store_outside_jan2024": False,
                                                "H3_post_recall_not_majority": True})

    def test_committed_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "t.csv")
            nct.write_rows(self.rows, path)
            with open(path, newline="", encoding="utf-8") as fh:
                fresh = list(csv.DictReader(fh))
        with open(os.path.join(nct.HERE, "data", "nyc_cinnamon_time.csv"), newline="", encoding="utf-8") as fh:
            committed = list(csv.DictReader(fh))
        self.assertEqual(len(fresh), 74)
        self.assertEqual(fresh, committed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
