#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/tmet-2018-0.1.0-result.md.

Rebuilds the sample counts, the D-suffixed samples, Table 1's origin counts, every printed Table 2
cell under the two registered bran/rice readings, the text's shares and non-detect counts, the
arsenic and mercury maxima, and the exploratory sample-level bran/rice split (with the search over
the 252 candidate picks) from the committed per-sample table data/tmet_2018_samples.csv with its
own code (it does not import the grader), and checks them against the sealed grader record
data/tmet_2018_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import itertools
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "tmet_2018_samples.csv")
SUMMARY = os.path.join(DATA, "tmet_2018_summary.json")

METALS = {"As": "arsenic_ppm", "Cd": "cadmium_ppm", "Pb": "lead_ppm", "Hg": "mercury_ppm"}
IF_LABELS = {"Infant Formula - Dairy", "Infant Formula - Other", "Infant Formula - Soy"}
RICE_LABELS = {"Rice Products", "Bran - Rice", "Cereal - Rice", "Grain - Rice"}
CANDIDATES = {"Oil - Other", "Crackers", "Popcorn", "Snack Bar"}
READINGS = {"R1": {"Oil - Other", "Crackers"}, "R2": {"Popcorn", "Snack Bar"}}
TYPES = ("bran", "infant-formula", "meal-replacement", "protein-powder", "rice")
THAI_SNACK_BAR = "C2018TMET00977"
EMPTY_OIL = "C2018TMET00992"
CRACKER = "C2018TMET00840"
# CFIA's printed Table 1: domestic, imported, unspecified.
TABLE1 = {"bran": (23, 41, 35), "infant-formula": (0, 386, 9), "meal-replacement": (16, 135, 47),
          "protein-powder": (72, 34, 89), "rice": (77, 19, 2)}
# CFIA's printed Table 2 (ppm): % positive, average of positives, maximum.
TABLE2 = {
    "bran": {"As": ("78", "0.024", "0.079"), "Cd": ("71", "0.043", "0.186"),
             "Pb": ("24", "0.023", "0.130"), "Hg": ("4", "0.0013", "0.002")},
    "infant-formula": {"As": ("52", "0.016", "0.040"), "Cd": ("9", "0.011", "0.020"),
                       "Pb": ("13", "0.012", "0.020"), "Hg": ("1", "0.002", "0.003")},
    "meal-replacement": {"As": ("44", "0.022", "0.139"), "Cd": ("31", "0.037", "0.190"),
                         "Pb": ("40", "0.024", "0.231"), "Hg": ("9", "0.002", "0.006")},
    "protein-powder": {"As": ("84", "0.028", "0.214"), "Cd": ("82", "0.060", "0.219"),
                       "Pb": ("71", "0.035", "0.237"), "Hg": ("50", "0.003", "0.022")},
    "rice": {"As": ("95", "0.263", "1.130"), "Cd": ("63", "0.016", "0.056"),
             "Pb": ("37", "0.018", "0.050"), "Hg": ("71", "0.003", "0.006")},
}


def load_rows():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for m, col in METALS.items():
            r[m] = float(r[col])
    return rows


def in_range(x, printed):
    half = 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5
    return x is not None and abs(x - float(printed)) <= half + 1e-9


def fixed_type(product):
    if product in IF_LABELS:
        return "infant-formula"
    if product == "Meal Replacement":
        return "meal-replacement"
    if product == "Protein Powder":
        return "protein-powder"
    if product in RICE_LABELS:
        return "rice"
    return None


def by_reading(r, reading):
    t = fixed_type(r["product"])
    if t:
        return t
    return "rice" if r["product"] in READINGS[reading] else "bran"


def by_rice_set(r, rice_ids):
    t = fixed_type(r["product"])
    if t:
        return t
    return "rice" if r["sample"] in rice_ids else "bran"


def stats(rows, m):
    pos = sorted(r[m] for r in rows if r[m] > 0)
    n = len(rows)
    return {"n": n, "k": len(pos), "pct": 100 * len(pos) / n if n else None,
            "mean": sum(pos) / len(pos) if pos else None, "max": pos[-1] if pos else None}


def cells(rows, t):
    out = {}
    for m, (pct, avg, mx) in TABLE2[t].items():
        st = stats(rows, m)
        out[f"{m}_pct"] = in_range(st["pct"], pct)
        out[f"{m}_avg"] = in_range(st["mean"], avg)
        out[f"{m}_max"] = in_range(st["max"], mx)
    return out


def group(rows, key):
    out = {t: [] for t in TYPES}
    for r in rows:
        out[key(r)].append(r)
    return out


def origin(rows):
    c = [0, 0, 0]
    for r in rows:
        c[0 if r["function"] == "Domestic" else 1 if r["function"] == "Import" else 2] += 1
    return tuple(c)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_rows()
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a = cls.s["analysis"]
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}
        cls.oils = sorted(r["sample"] for r in cls.rows if r["product"] == "Oil - Other")
        cls.split = set(cls.oils) | {THAI_SNACK_BAR}


class TestShape(Base):
    def test_counts(self):
        self.assertEqual(len(self.rows), 987)
        self.assertEqual(len({r["sample"] for r in self.rows}), 987)
        products = {}
        for r in self.rows:
            products[r["product"]] = products.get(r["product"], 0) + 1
        self.assertEqual(products, self.s["census"]["products"])
        self.assertEqual(sum(1 for r in self.rows if r["product"] in IF_LABELS), 396)
        self.assertEqual(products["Protein Powder"], 196)
        for r in self.rows:
            self.assertEqual(int(r["n_toxic"]), sum(1 for m in METALS if r[m] > 0), r["sample"])
        self.assertEqual(len(self.oils), 4)

    def test_d_samples(self):
        ids = {r["sample"] for r in self.rows}
        d = sorted((r["sample"], r["product"]) for r in self.rows if r["dup"] == "1")
        self.assertEqual(d, [("C2018TMET00039D", "Protein Powder"),
                             ("C2018TMET00113D", "Protein Powder"),
                             ("C2018TMET00183D", "Protein Powder"),
                             ("C2018TMET00191D", "Protein Powder")])
        self.assertFalse(any(s[:-1] in ids for s, _ in d))
        self.assertEqual([x["sample"] for x in self.a["dups"]], [s for s, _ in d])
        self.assertFalse(any(x["base_present"] for x in self.a["dups"]))

    def test_gate_and_tally(self):
        self.assertTrue(self.preds["G"]["met"])
        self.assertTrue(all(self.preds["G"]["observed"].values()))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (8, 5))
        met = {p["id"]: p["met"] for p in self.s["predictions"]}
        self.assertEqual(list(met), ["G", "C1", "P1", "P2", "P3", "P4", "P5", "P6"])
        self.assertEqual({k for k, v in met.items() if v}, {"G", "C1", "P1", "P2", "P4"})
        prov = self.s["provenance"]
        self.assertEqual(prov["sha256"],
                         "5eedfe002aecec4ffa8bd65850ec6b9de6fab4d03dc2b037636c207997e332a8")
        self.assertEqual(prov["bytes"], 3221954)
        self.assertTrue(prov["md5_matches_portal"])


class TestTable2(Base):
    def test_cells_both_readings(self):
        for reading in READINGS:
            g = group(self.rows, lambda r: by_reading(r, reading))
            for t in TYPES:
                self.assertEqual(cells(g[t], t), self.a["cells"][reading][t], (reading, t))
                for m in METALS:
                    st = stats(g[t], m)
                    ref = self.a["tables"][reading][t][m]
                    self.assertEqual((st["n"], st["k"], st["max"]), (ref["n"], ref["k"], ref["max"]))
                    self.assertAlmostEqual(st["mean"], ref["mean"], places=9)

    def test_matched_counts(self):
        g = group(self.rows, lambda r: by_reading(r, "R1"))
        self.assertTrue(all(cells(g["meal-replacement"], "meal-replacement").values()))
        self.assertTrue(all(cells(g["infant-formula"], "infant-formula").values()))
        pp = cells(g["protein-powder"], "protein-powder")
        self.assertEqual([k for k, v in pp.items() if not v], ["Hg_pct"])
        hg = stats(g["protein-powder"], "Hg")
        self.assertEqual((hg["k"], hg["n"]), (99, 196))
        self.assertFalse(in_range(100 * 99 / 196, "50"))
        self.assertTrue(in_range(100 * 98 / 195, "50"))
        totals = {}
        for reading in READINGS:
            g = group(self.rows, lambda r: by_reading(r, reading))
            totals[reading] = sum(sum(cells(g[t], t).values()) for t in ("bran", "rice"))
        self.assertEqual(totals, {"R1": 10, "R2": 11})
        self.assertEqual(totals["R1"], self.preds["P3"]["observed"]["R1"]["total"])


class TestText(Base):
    def test_shares_and_counts(self):
        n = len(self.rows)
        k = {m: sum(1 for r in self.rows if r[m] > 0) for m in METALS}
        self.assertEqual(k, {m: self.a["overall"][m]["k"] for m in METALS})
        self.assertEqual((k["As"], k["Hg"], n - k["Cd"], n - k["Pb"]), (627, 193, 597, 657))
        nt = [sum(1 for m in METALS if r[m] > 0) for r in self.rows]
        anyk, all4 = sum(1 for x in nt if x >= 1), sum(1 for x in nt if x == 4)
        self.assertEqual((anyk, all4), (687, 120))
        self.assertEqual((anyk, all4), (self.a["any"], self.a["all4"]))
        self.assertTrue(in_range(100 * k["As"] / n, "64"))
        self.assertTrue(in_range(100 * anyk / n, "70"))
        self.assertTrue(in_range(100 * all4 / n, "12"))
        self.assertFalse(in_range(100 * k["Hg"] / n, "19"))
        self.assertTrue(in_range(100 * (k["Hg"] - 1) / 985, "19"))
        self.assertTrue(596 <= n - k["Cd"] <= 598 and 656 <= n - k["Pb"] <= 658)

    def test_maxima(self):
        top = sorted(self.rows, key=lambda r: -r["As"])[:2]
        self.assertEqual([(r["As"], r["sample"], r["product"], r["function"]) for r in top],
                         [(1.13, "C2018TMET00945", "Bran - Rice", "Import"),
                          (1.12, "C2018TMET00934", "Bran - Rice", "Import")])
        hg = max(r["Hg"] for r in self.rows)
        holders = [(r["sample"], r["product"]) for r in self.rows if r["Hg"] == hg]
        self.assertEqual((hg, holders), (0.0219, [("C2018TMET00200", "Protein Powder")]))
        self.assertTrue(in_range(hg, "0.022"))
        self.assertEqual(sum(1 for r in self.rows if r["product"] in IF_LABELS and r["Hg"] > 0), 2)
        low = {m: min(r[m] for r in self.rows if r[m] > 0) for m in METALS}
        self.assertEqual(low, {"As": 0.01, "Cd": 0.01, "Pb": 0.01, "Hg": 0.001})


class TestOrigin(Base):
    def test_table1(self):
        g = group(self.rows, lambda r: by_reading(r, "R1"))
        diff = {}
        for t in TYPES:
            got = origin(g[t])
            self.assertEqual(list(got) + [len(g[t])], self.a["origins"]["R1"][t])
            d = tuple(x - p for x, p in zip(got, TABLE1[t]))
            if any(d):
                diff[t] = d
        self.assertEqual(diff, {"infant-formula": (0, 1, 0), "protein-powder": (0, 0, 1)})


class TestExploratorySplit(Base):
    def test_split_reproduces_all_24_cells(self):
        g = group(self.rows, lambda r: by_rice_set(r, self.split))
        self.assertEqual((len(g["rice"]), len(g["bran"])), (98, 99))
        for t in ("bran", "rice"):
            self.assertTrue(all(cells(g[t], t).values()), (t, cells(g[t], t)))
            self.assertEqual(origin(g[t]), TABLE1[t], t)
        thai = [r for r in self.rows if r["sample"] == THAI_SNACK_BAR][0]
        self.assertEqual((thai["product"], thai["origin"], thai["As"]),
                         ("Snack Bar", "THAILAND", 0.158))
        self.assertEqual(stats(g["bran"], "As")["max"], 0.0788)

    def test_only_two_picks_fit(self):
        cand = sorted(r["sample"] for r in self.rows if r["product"] in CANDIDATES)
        self.assertEqual(len(cand), 10)
        fits = []
        for pick in itertools.combinations(cand, 5):
            g = group(self.rows, lambda r: by_rice_set(r, set(pick)))
            if all(all(cells(g[t], t).values()) for t in ("bran", "rice")):
                fits.append(frozenset(pick))
        alt = (self.split - {EMPTY_OIL}) | {CRACKER}
        self.assertEqual(set(fits), {frozenset(self.split), frozenset(alt)})
        for sid in (EMPTY_OIL, CRACKER):
            r = [x for x in self.rows if x["sample"] == sid][0]
            self.assertEqual([r[m] for m in METALS], [0.0, 0.0, 0.0, 0.0], sid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
