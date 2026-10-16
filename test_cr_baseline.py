"""Offline tests for cr_baseline.py (standard library only).

Covers the 0.1.0 ceiling logic and the 0.2.0 Cr(VI) speciation gate. The
speciation tests are the pre-registered predictions P0-P4 in
docs/cr-baseline-0.2.0-prereg.md."""
import csv
import json
import os
import tempfile
import unittest

import cr_baseline as cb

HERE = os.path.dirname(os.path.abspath(__file__))

# The seven chromate-like NYC pairs with chromium under 70 ppm, and one high
# pair, as nyc_spice_lead.py 0.3.0 wrote them (run of 2026-10-15).
PAIRS = [
    {"lead_row_id": "2231", "chromium_row_id": "2230", "collection_date": "2017-05-03", "investigation_type": "C",
     "product_name": "Curry Masala", "purchase_country": "PAKISTAN", "lead_ppm": "300.0",
     "chromium_ppm": "69.0", "verdict": "chromate-like"},
    {"lead_row_id": "2156", "chromium_row_id": "2155", "collection_date": "2017-03-23", "investigation_type": "C",
     "product_name": "Spice Mix", "purchase_country": "BANGLADESH", "lead_ppm": "170.0",
     "chromium_ppm": "38.0", "verdict": "chromate-like"},
    {"lead_row_id": "1371", "chromium_row_id": "1370", "collection_date": "2015-03-18", "investigation_type": "A",
     "product_name": "Chili powder", "purchase_country": "BANGLADESH", "lead_ppm": "110.0",
     "chromium_ppm": "34.0", "verdict": "chromate-like"},
    {"lead_row_id": "707", "chromium_row_id": "706", "collection_date": "2013-02-14", "investigation_type": "C",
     "product_name": "Black Pepper", "purchase_country": "BANGLADESH", "lead_ppm": "85.0",
     "chromium_ppm": "21.0", "verdict": "chromate-like"},
    {"lead_row_id": "2290", "chromium_row_id": "2289", "collection_date": "2017-06-07", "investigation_type": "A",
     "product_name": "Coriander Powder", "purchase_country": "BANGLADESH", "lead_ppm": "52.0",
     "chromium_ppm": "12.0", "verdict": "chromate-like"},
    {"lead_row_id": "3282", "chromium_row_id": "3281", "collection_date": "2019-01-22", "investigation_type": "A",
     "product_name": "Coriander", "purchase_country": "GEORGIA", "lead_ppm": "51.0",
     "chromium_ppm": "9.1", "verdict": "chromate-like"},
    {"lead_row_id": "2968", "chromium_row_id": "2967", "collection_date": "2018-09-24", "investigation_type": "A",
     "product_name": "Turmeric", "purchase_country": "ALGERIA", "lead_ppm": "20.0",
     "chromium_ppm": "6.1", "verdict": "chromate-like"},
    {"lead_row_id": "3034", "chromium_row_id": "3033", "collection_date": "2018-10-20", "investigation_type": "C",
     "product_name": "Raz El Hanout", "purchase_country": "ALGERIA", "lead_ppm": "2200.0",
     "chromium_ppm": "310.0", "verdict": "chromate-like"},
    {"lead_row_id": "7615", "chromium_row_id": "7614", "collection_date": "2024-01-10", "investigation_type": "S",
     "product_name": "El Servidor Corp Ground Cinnamon", "purchase_country": "UNITED STATES", "lead_ppm": "23.0",
     "chromium_ppm": "1.8", "verdict": "more lead than chromate"},
]

EXPECTED = {
    "Curry Masala": ("curry", 31.36, "robust"),
    "Spice Mix": ("generic", 16.67, "robust"),
    "Chili powder": ("chili/paprika", 20.20, "robust"),
    "Black Pepper": ("black pepper", 10.33, "robust"),
    "Coriander Powder": ("coriander", 5.48, "unresolved"),
    "Coriander": ("coriander", 2.70, "unresolved"),
    "Turmeric": ("turmeric", 3.59, "robust"),
    "Raz El Hanout": ("generic", 33.96, "robust"),
}

CEILINGS = {
    "turmeric": [{"method": "ICP-MS", "ceiling_ppm": 1.9, "n": "", "source": "t"}],
    "chili/paprika": [{"method": "ICP-MS", "ceiling_ppm": 3.17, "n": "", "source": "t"}],
    "curry": [{"method": "ICP-MS", "ceiling_ppm": 3.55, "n": "", "source": "t"}],
    "coriander": [{"method": "ICP-MS", "ceiling_ppm": 0.129, "n": "", "source": "t"},
                  {"method": "ICP-MS", "ceiling_ppm": 0.912, "n": "", "source": "t"},
                  {"method": "ICP-OES", "ceiling_ppm": 12.45, "n": "", "source": "t"},
                  {"method": "FAAS", "ceiling_ppm": 18.93, "n": "", "source": "t"}],
    "black pepper": [{"method": "ICP-MS", "ceiling_ppm": 0.096, "n": "", "source": "t"},
                     {"method": "ICP-MS", "ceiling_ppm": 0.113, "n": "", "source": "t"}],
    "generic": [{"method": "ICP-MS", "ceiling_ppm": 8.59, "n": "", "source": "t"}],
}


def _c(method, ppm, source="test"):
    return {"method": method, "ceiling_ppm": ppm, "n": "", "source": source}


def _pair(name, pb, cr, cr6=None, verdict="chromate-like"):
    p = {"lead_row_id": "x", "chromium_row_id": "y", "collection_date": "2022-01-01",
         "investigation_type": "lit", "product_name": name, "purchase_country": "",
         "lead_ppm": str(pb), "chromium_ppm": str(cr), "verdict": verdict}
    if cr6 is not None:
        p["cr6_result"] = cr6
    return p


class Edge(unittest.TestCase):
    def test_pure_lead_chromate(self):
        # Molar ratio 1: half the chromium can go before the ratio reaches 2.
        self.assertAlmostEqual(cb.edge_ppm(cb.PB * 3, cb.CR * 3), cb.CR * 3 / 2)

    def test_edge_is_where_the_ratio_reaches_the_band_top(self):
        pb, cr = 51.0, 9.1
        e = cb.edge_ppm(pb, cr)
        self.assertAlmostEqual((pb / cb.PB) / ((cr - e) / cb.CR), cb.CHROMATE_BAND[1])

    def test_low_chromium_pairs(self):
        self.assertAlmostEqual(cb.edge_ppm(51, 9.1), 2.70, places=2)
        self.assertAlmostEqual(cb.edge_ppm(20, 6.1), 3.59, places=2)


class Matrix(unittest.TestCase):
    def test_names(self):
        for name, (matrix, _, _) in EXPECTED.items():
            self.assertEqual(cb.matrix_of(name), matrix, name)
        self.assertEqual(cb.matrix_of("Turmeric Spice Powder"), "turmeric")
        self.assertEqual(cb.matrix_of("GEORGIAN CHILLI POWDER"), "chili/paprika")
        self.assertEqual(cb.matrix_of("Corriander"), "coriander")
        self.assertEqual(cb.matrix_of("Cinnamon Powder"), "cinnamon")
        self.assertEqual(cb.matrix_of("Khmeli Suneli"), "generic")


class Judge(unittest.TestCase):
    def test_verdicts(self):
        cs = [_c("ICP-MS", 1.0), _c("FAAS", 10.0)]
        self.assertEqual(cb.judge(51, 20, cs)[1], "robust")             # edge 13.6
        self.assertEqual(cb.judge(51, 9.1, cs)[1], "unresolved")        # edge 2.7
        self.assertEqual(cb.judge(51, 6.6, cs)[1], "background-limited")  # edge 0.2
        e, v, above = cb.judge(51, 9.1, cs)
        self.assertEqual([c["method"] for c in above], ["FAAS"])

    def test_ceiling_equal_to_edge_counts(self):
        e = cb.edge_ppm(100, 30)
        self.assertEqual(cb.judge(100, 30, [_c("ICP-MS", e)])[1], "background-limited")


class Assess(unittest.TestCase):
    CEILINGS = {
        "turmeric": [_c("ICP-MS", 1.9)],
        "chili/paprika": [_c("ICP-MS", 3.17)],
        "curry": [_c("ICP-MS", 3.55)],
        "coriander": [_c("ICP-MS", 0.129), _c("ICP-MS", 0.912), _c("ICP-OES", 12.45), _c("FAAS", 18.93)],
        "black pepper": [_c("ICP-MS", 0.096), _c("ICP-MS", 0.113)],
        "generic": [_c("ICP-MS", 8.59)],
    }

    def _check(self, rows):
        self.assertEqual(len(rows), 8)  # the "more lead than chromate" pair is left out
        for r in rows:
            matrix, edge, verdict = EXPECTED[r["product_name"]]
            self.assertEqual(r["matrix"], matrix, r["product_name"])
            self.assertAlmostEqual(r["edge_ppm"], edge, places=2, msg=r["product_name"])
            self.assertEqual(r["baseline_verdict"], verdict, r["product_name"])
        self.assertEqual([r["edge_ppm"] for r in rows], sorted(r["edge_ppm"] for r in rows))

    def test_inline_ceilings(self):
        rows = cb.assess(PAIRS, self.CEILINGS)
        self._check(rows)
        cor = [r for r in rows if r["matrix"] == "coriander"]
        for r in cor:
            self.assertIn("ICP-OES 12.45", r["ceilings_at_or_above_edge"])
            self.assertIn("FAAS 18.93", r["ceilings_at_or_above_edge"])
            self.assertNotIn("ICP-MS", r["ceilings_at_or_above_edge"])

    def test_generic_never_replaces_a_matrix_ceiling(self):
        rows = cb.assess(PAIRS, self.CEILINGS)
        turmeric = [r for r in rows if r["product_name"] == "Turmeric"][0]
        self.assertEqual(turmeric["ceilings_used"], "turmeric")
        self.assertEqual(turmeric["baseline_verdict"], "robust")  # the generic 8.59 would say otherwise
        self.assertEqual(cb.judge(20, 6.1, self.CEILINGS["generic"])[1], "background-limited")

    def test_needs_generic_row(self):
        with self.assertRaises(ValueError):
            cb.assess(PAIRS, {"turmeric": [_c("ICP-MS", 1.9)]})

    def test_shipped_ceilings(self):
        path = os.path.join(HERE, "data", "natural_cr_ceilings.csv")
        if not os.path.exists(path):
            self.skipTest("data/natural_cr_ceilings.csv not present")
        ceilings = cb.read_ceilings(path)
        for c in sum(ceilings.values(), []):
            self.assertTrue(c["source"], c)
        self._check(cb.assess(PAIRS, ceilings))


class Speciation(unittest.TestCase):
    """Pre-registered predictions P0-P4 for the 0.2.0 Cr(VI) gate."""

    def test_speciation_of_normalises_and_validates(self):
        self.assertEqual(cb.speciation_of("Positive"), "positive")
        self.assertEqual(cb.speciation_of(" negative "), "negative")
        self.assertEqual(cb.speciation_of(""), "")
        self.assertEqual(cb.speciation_of(None), "")
        with self.assertRaises(ValueError):
            cb.speciation_of("maybe")

    def test_final_of(self):
        self.assertEqual(cb.final_of("robust", "positive"), "cr6-confirmed")
        self.assertEqual(cb.final_of("unresolved", "positive"), "cr6-confirmed")
        self.assertEqual(cb.final_of("background-limited", "positive"), "cr6-confirmed")
        self.assertEqual(cb.final_of("unresolved", "negative"), "unresolved")
        self.assertEqual(cb.final_of("robust", ""), "robust")

    def test_backward_compat_no_cr6_column(self):
        # P0: no cr6_result column -> every row untested, final == baseline,
        # and the baseline counts are exactly the 0.1.0 result.
        rows = cb.assess(PAIRS, CEILINGS)
        for r in rows:
            self.assertEqual(r["speciation"], "untested", r["product_name"])
            self.assertEqual(r["final_verdict"], r["baseline_verdict"], r["product_name"])
        s = cb.summarize(rows, {})
        self.assertEqual(s["verdicts"], {"robust": 6, "unresolved": 2})
        self.assertEqual(s["final_verdicts"], {"robust": 6, "unresolved": 2})
        self.assertEqual(s["speciation"], {"untested": 8})

    def test_positive_overrides_each_baseline(self):
        # P1: positive -> cr6-confirmed for a robust, an unresolved and a
        # background-limited baseline.
        pairs = [
            _pair("Curry Masala", 300, 69, cr6="positive"),      # curry, edge 31.36 -> robust
            _pair("Coriander", 51, 9.1, cr6="positive"),         # coriander, edge 2.70 -> unresolved
            _pair("Khmeli Suneli", 20, 6.1, cr6="positive"),     # generic 8.59, edge 3.59 -> background-limited
        ]
        rows = {r["product_name"]: r for r in cb.assess(pairs, CEILINGS)}
        self.assertEqual(rows["Curry Masala"]["baseline_verdict"], "robust")
        self.assertEqual(rows["Coriander"]["baseline_verdict"], "unresolved")
        self.assertEqual(rows["Khmeli Suneli"]["baseline_verdict"], "background-limited")
        for name in ("Curry Masala", "Coriander", "Khmeli Suneli"):
            self.assertEqual(rows[name]["speciation"], "positive", name)
            self.assertEqual(rows[name]["final_verdict"], "cr6-confirmed", name)

    def test_negative_not_exculpatory(self):
        # P2: negative keeps the baseline verdict and records speciation.
        rows = {r["product_name"]: r for r in cb.assess(
            [_pair("Coriander", 51, 9.1, cr6="negative")], CEILINGS)}
        r = rows["Coriander"]
        self.assertEqual(r["baseline_verdict"], "unresolved")
        self.assertEqual(r["speciation"], "negative")
        self.assertEqual(r["final_verdict"], "unresolved")

    def test_lopez_coriander_example(self):
        # P3: the Lopez et al. 2022 Patna coriander powder (Pb 87, Cr 13),
        # Cr(VI)-positive by DPC, is unresolved by ceilings but cr6-confirmed.
        rows = {r["product_name"]: r for r in cb.assess(
            [_pair("Patna coriander powder (Lopez 2022)", 87, 13, cr6="positive")], CEILINGS)}
        r = rows["Patna coriander powder (Lopez 2022)"]
        self.assertEqual(r["matrix"], "coriander")
        self.assertAlmostEqual(r["edge_ppm"], 2.08, places=2)
        self.assertAlmostEqual(r["molar_ratio_pb_cr"], 1.679, places=2)
        self.assertEqual(r["baseline_verdict"], "unresolved")
        self.assertEqual(r["final_verdict"], "cr6-confirmed")

    def test_bad_cr6_value_errors(self):
        with self.assertRaises(ValueError):
            cb.assess([_pair("Coriander", 51, 9.1, cr6="yes please")], CEILINGS)


class EndToEnd(unittest.TestCase):
    def test_main(self):
        with tempfile.TemporaryDirectory() as d:
            pairs = os.path.join(d, "pairs.csv")
            with open(pairs, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(PAIRS[0]))
                w.writeheader()
                w.writerows(PAIRS)
            ceilings = os.path.join(d, "ceilings.csv")
            with open(ceilings, "w", newline="", encoding="utf-8") as fh:
                fh.write("matrix,method,ceiling_ppm,n,source,note\n"
                         "coriander,ICP-MS,0.129,1,a,\ncoriander,FAAS,18.93,3,b,\n"
                         "turmeric,ICP-MS,1.9,10,c,\ngeneric,ICP-MS,8.59,,d,\n")
            out = os.path.join(d, "out")
            self.assertEqual(cb.main(["--pairs", pairs, "--ceilings", ceilings, "--data-dir", d,
                                      "--out-dir", out]), 0)
            for name in ("cr_baseline.csv", "cr_baseline.json", "cr_baseline.md"):
                self.assertTrue(os.path.exists(os.path.join(out, name)), name)
            with open(os.path.join(out, "cr_baseline.json"), encoding="utf-8") as fh:
                s = json.load(fh)
            self.assertEqual(s["chromate_like_pairs"], 8)
            # Black pepper and chili fall back to the generic 8.59 here: both edges are above it.
            self.assertEqual(s["verdicts"], {"unresolved": 2, "robust": 6})
            # No cr6_result column -> final verdicts equal baseline verdicts.
            self.assertEqual(s["final_verdicts"], {"unresolved": 2, "robust": 6})
            self.assertEqual(s["speciation"], {"untested": 8})
            with open(os.path.join(out, "cr_baseline.md"), encoding="utf-8") as fh:
                md = fh.read()
            self.assertIn("| 3282 | 3281 | 2019-01-22 | Coriander |", md)


if __name__ == "__main__":
    unittest.main()
