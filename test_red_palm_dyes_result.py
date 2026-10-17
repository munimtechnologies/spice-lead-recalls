"""Recompute the provisional red-palm-dyes 0.1.0 grade from the committed transcription.

This is the pinned test for docs/red-palm-dyes-0.1.0-result.md. It reads
data/red_palm_dyes_transcribed_samples.csv (one row per CFIA sample number, its declared
origin and every non-zero colour, transcribed from CFIA's two open red palm oil files),
rebuilds the 18-colour long format CFIA publishes, and runs the committed, pre-registered
grader red_palm_dyes.py on it. It pins the six predictions, the two positives, the
origin table and the Ghana bound quoted in the result. No network.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import csv
import io
import os
import unittest

import red_palm_dyes as r

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "red_palm_dyes_transcribed_samples.csv")
HEADER = ["Sample No. – No. d'échantillon", "Region - Région", "Commodity", "Denrée",
          "Function", "Fonction", "Origin", "Origine", "Product", "Produit",
          "Date Sampled – Date d'échantillonage", "Component", "Composant", "AMOUNT",
          "Report Unit - Unité de rapport"]
COMPONENTS = ["Chlorophylline", "Citrus Red 2", "Metanil Yellow", "Methyl Yellow", "Orange II",
              "Para Red", "Rhodamine B", "Solvent Blue 59", "Sudan Black B", "Sudan Blue II",
              "Sudan I", "Sudan II", "Sudan III", "Sudan IV", "Sudan Orange G", "Sudan Red 7B",
              "Sudan Red G", "Toluidine Red"]
FDA_GHANA_2019 = 0.266   # Osei Tutu et al., share of Ghana market samples dyed in 2019


def _load():
    with open(CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _amounts(cell):
    out = {}
    for part in cell.split(";"):
        if part.strip():
            comp, value = part.split("=")
            out[comp.strip()] = float(value)
    return out


def _long_csv(rows):
    """CFIA's layout: one row per sample and colour, a bare 0 where nothing was found."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for comp in COMPONENTS:
        for row in rows:
            amount = _amounts(row["nonzero"]).get(comp, 0)
            w.writerow([row["sample_id"], "", "IMFD", "DAIM", "Import", "importé", row["origin"],
                        row["origin"], "Red Palm Oil", "Huile de palme rouge", "", comp, comp,
                        str(amount), "ug/g"])
    return buf.getvalue().encode("utf-8")


def _tally(samples):
    out = {}
    for s in samples:
        t = out.setdefault(s["origin"], [0, 0])
        t[0] += 1
        t[1] += int(s["sudan_positive"])
    return out


class TranscriptionTest(unittest.TestCase):
    def test_rows(self):
        rows = _load()
        self.assertEqual(len(rows), 104)
        self.assertEqual(sum(1 for x in rows if x["year"] == "2019-20"), 72)
        self.assertEqual(sum(1 for x in rows if x["year"] == "2020-21"), 32)
        self.assertEqual(len({x["sample_id"] for x in rows}), 104)
        nonzero = [(x["sample_id"], _amounts(x["nonzero"])) for x in rows if x["nonzero"]]
        self.assertEqual(nonzero, [("C2019FFPO00009", {"Sudan IV": 47.5}),
                                   ("C2020FFPO00041", {"Sudan IV": 15.61})])


class GradeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = _load()
        cls.by_year, cls.checks = {}, {}
        for year in ("2019-20", "2020-21"):
            part = [x for x in rows if x["year"] == year]
            cls.by_year[year], cls.checks[year] = r.parse(_long_csv(part), year)
        cls.pooled = cls.by_year["2019-20"] + cls.by_year["2020-21"]
        cls.g = r.grade(cls.by_year["2019-20"], cls.pooled, cls.checks["2019-20"])

    def test_parse(self):
        c19, c20 = self.checks["2019-20"], self.checks["2020-21"]
        self.assertEqual((c19["data_rows"], c19["samples"], c19["duplicate_ids"]), (1296, 72, 2))
        self.assertEqual((c20["data_rows"], c20["samples"], c20["duplicate_ids"]), (576, 32, 0))
        for c in (c19, c20):
            self.assertEqual((c["unknown_components"], c["bad_numbers"], c["repeats"],
                              c["incomplete_samples"]), (0, 0, 0, 0))

    def test_predictions(self):
        p = self.g["predictions"]
        self.assertTrue(self.g["gradable_parse"])
        self.assertEqual(p["P1"]["value"], 1)
        self.assertEqual(p["P2"]["value"], "1 of 72")
        self.assertEqual(p["P3"]["value"], "0 of 2 outside")
        self.assertEqual(p["P4"]["value"], {"sudan iv": 2})
        self.assertEqual(p["P5"]["value"], {"NIGERIA": 2})
        self.assertEqual(p["P6"]["value"], 0)
        self.assertEqual({k: v["status"] for k, v in p.items()},
                         {"P1": "met", "P2": "met", "P3": "met", "P4": "met",
                          "P5": "not met", "P6": "met"})
        self.assertEqual((self.g["met"], self.g["gradable"]), (5, 6))

    def test_positives(self):
        pos = [(s["year"], s["sample"], s["origin"], s["sudan_dyes"], s["sudan_max"])
               for s in self.pooled if s["sudan_positive"]]
        self.assertEqual(pos, [("2019-20", "C2019FFPO00009", "NIGERIA", ["sudan iv"], 47.5),
                               ("2020-21", "C2020FFPO00041", "NIGERIA", ["sudan iv"], 15.61)])

    def test_origin_table(self):
        self.assertEqual(_tally(self.by_year["2019-20"]), {
            "ECUADOR": [47, 0], "GHANA": [10, 0], "SENEGAL": [1, 0], "NIGERIA": [3, 1],
            "MALAYSIA": [6, 0], "UNKNOWN": [2, 0], "COLOMBIA": [2, 0], "TOGO": [1, 0]})
        pooled = _tally(self.pooled)
        self.assertEqual(pooled, {
            "ECUADOR": [60, 0], "GHANA": [14, 0], "SENEGAL": [1, 0], "NIGERIA": [8, 2],
            "MALAYSIA": [10, 0], "UNKNOWN": [3, 0], "COLOMBIA": [3, 0], "TOGO": [3, 0],
            "IVORY COAST": [1, 0], "CAMEROON": [1, 0]})
        africa = [pooled[o] for o in r.AFRICA if o in pooled]
        self.assertEqual((sum(t[0] for t in africa), sum(t[1] for t in africa)), (28, 2))
        elsewhere = [t for o, t in pooled.items() if o not in r.AFRICA + (r.UNKNOWN,)]
        self.assertEqual((sum(t[0] for t in elsewhere), sum(t[1] for t in elsewhere)), (73, 0))

    def test_ghana_bound(self):
        n19 = _tally(self.by_year["2019-20"])["GHANA"][0]
        n_all = _tally(self.pooled)["GHANA"][0]
        # exact one-sided 95% upper bound for 0 positives in n: 1 - 0.05 ** (1 / n)
        self.assertAlmostEqual(1 - 0.05 ** (1.0 / n19), 0.259, places=3)
        self.assertAlmostEqual(1 - 0.05 ** (1.0 / n_all), 0.193, places=3)
        # chance of 0 dyed in 10 if Ghana-declared oil were dyed at FDA Ghana's 2019 market rate
        self.assertAlmostEqual((1 - FDA_GHANA_2019) ** n19, 0.045, places=3)


if __name__ == "__main__":
    unittest.main()
