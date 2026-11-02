#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent test for docs/pah-2019-0.1.0-result.md (CFIA PAH survey 2019-20).

Does not import the grader. From the committed per-sample table data/pah_2019_samples.csv it
recomputes, with its own code: each sample's TEQ (benzo[a]pyrene + 0.1 benz[a]anthracene +
0.1 benzo[b]fluoranthene + 0.01 chrysene) and PAH4 from the 16 PAH columns; Table 2 (n, positives,
minimum, maximum, average per group); Table 3's olive-oil 0.23 as a truncation of the file's
average; the D4 text checks; the D5 lists; the one identical 16-PAH pair; the ID numbers and the two
'AD' IDs; the Function split against Table 1; and the date range. Each is checked against the sealed
records data/pah_2019_summary.json and data/pah_2019_id_amendment.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import datetime
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "pah_2019_samples.csv")
SUMMARY = os.path.join(DATA, "pah_2019_summary.json")
AMEND = os.path.join(DATA, "pah_2019_id_amendment.json")

TEF = {"Benzo[a]pyrene": 1.0, "Benz[a]anthracene": 0.1, "Benzo[b]fluoranthene": 0.1,
       "Chrysene": 0.01}
# Table 2 of the report: (samples, positives, minimum, maximum, average), TEQ in ppb.
TABLE2 = {"formula": (34, 16, "0.001", "0.776", "0.12"),
          "nuts": (114, 44, "0.001", "2.93", "0.17"),
          "olive": (148, 121, "0.002", "3.25", "0.24"),
          "all": (296, 181, "0.001", "3.25", "0.21")}
# Table 1 of the report: (domestic, imported, unspecified).
TABLE1 = {"formula": (0, 31, 3), "nuts": (40, 46, 28), "olive": (1, 133, 14)}
FILE_SPLIT = {"formula": (0, 32, 2), "nuts": (40, 46, 28), "olive": (1, 135, 12)}
MISSING_NUMBERS = {53, 68, 194, 264}
ID_RE = re.compile(r"^C2019PAHS(\d{5})A(D?)$")


def load():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        comps = [c for c in reader.fieldnames if c.startswith("ppb:")]
        rows = list(reader)
    for r in rows:
        r["v"] = {c[4:]: float(r[c]) for c in comps}
        r["my_teq"] = sum(f * r["v"][c] for c, f in TEF.items())
        r["my_pah4"] = sum(r["v"][c] for c in TEF)
    return rows, [c[4:] for c in comps]


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def in_range(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def stats(rows):
    pos = [r["my_teq"] for r in rows if r["my_teq"] > 0]
    return {"n": len(rows), "k": len(pos), "min": min(pos) if pos else None,
            "max": max(pos) if pos else None, "mean": sum(pos) / len(pos) if pos else None}


def day(text):
    return datetime.datetime.strptime(text, "%d-%b-%y").date()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.comps = load()
        cls.by = {r["sample"]: r for r in cls.rows}
        cls.groups = {"all": cls.rows}
        for g in ("formula", "nuts", "olive"):
            cls.groups[g] = [r for r in cls.rows if r["group"] == g]
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        with open(AMEND, encoding="utf-8") as fh:
            cls.a = json.load(fh)
        cls.preds = {p["id"]: p for p in cls.s["predictions"]}


class TestStructure(Base):
    def test_samples_groups_and_columns(self):
        self.assertEqual(len(self.rows), 296)
        self.assertEqual(len(self.by), 296)
        self.assertEqual(len(self.comps), 16)
        self.assertEqual(set(self.comps), set(self.s["census"]["components"]))
        self.assertEqual({g: len(v) for g, v in self.groups.items()},
                         {"all": 296, "formula": 34, "nuts": 114, "olive": 148})
        kinds = {}
        for r in self.groups["formula"]:
            kinds[r["formula"]] = kinds.get(r["formula"], 0) + 1
        self.assertEqual(kinds, {"dairy": 23, "soy": 11})
        products = {}
        for r in self.rows:
            products[r["product"]] = products.get(r["product"], 0) + 1
        self.assertEqual(products, self.s["census"]["products"])

    def test_teq_pah4_and_counts_recomputed(self):
        for r in self.rows:
            self.assertAlmostEqual(r["my_teq"], float(r["teq_ppb"]), places=9, msg=r["sample"])
            self.assertAlmostEqual(r["my_pah4"], float(r["pah4_ppb"]), places=9, msg=r["sample"])
            self.assertEqual(sum(1 for v in r["v"].values() if v > 0), int(r["n_pah"]),
                             r["sample"])
            self.assertTrue(all(v >= 0 for v in r["v"].values()), r["sample"])


class TestTable2(Base):
    def test_all_twenty_cells(self):
        for g, (n, k, pmin, pmax, pavg) in TABLE2.items():
            st = stats(self.groups[g])
            self.assertEqual((st["n"], st["k"]), (n, k), g)
            self.assertTrue(in_range(st["min"], pmin), (g, st["min"]))
            self.assertTrue(in_range(st["max"], pmax), (g, st["max"]))
            self.assertTrue(in_range(st["mean"], pavg), (g, st["mean"]))
            rec = self.s["analysis"]["groups"][g]
            self.assertEqual(rec["k"], st["k"], g)
            self.assertAlmostEqual(rec["mean"], st["mean"], places=9)
            self.assertAlmostEqual(rec["max"], st["max"], places=9)

    def test_table3_olive_average_is_a_truncation(self):
        mean = stats(self.groups["olive"])["mean"]
        self.assertTrue(0.2373 <= mean < 0.2374, mean)
        self.assertTrue(in_range(mean, "0.24"))
        self.assertFalse(in_range(mean, "0.23"))
        self.assertEqual(int(mean * 100), 23)
        self.assertEqual(self.s["analysis"]["olive_avg"], {"table2": True, "table3": False})


class TestText(Base):
    def test_d4_checks(self):
        dairy = [r for r in self.groups["formula"] if r["formula"] == "dairy"]
        soy = [r for r in self.groups["formula"] if r["formula"] == "soy"]
        st = stats(dairy)
        self.assertEqual((st["n"], st["k"]), (23, 16))
        self.assertTrue(in_range(st["max"], "0.776"))
        self.assertEqual(stats(soy)["k"], 0)
        nuts = sorted(self.groups["nuts"], key=lambda r: -r["my_teq"])
        self.assertEqual((nuts[0]["sample"], nuts[0]["product"], nuts[0]["origin"]),
                         ("C2019PAHS00183A", "Butter - Pumpkin Seed", "CANADA"))
        self.assertTrue(in_range(nuts[0]["my_teq"], "2.93"))
        self.assertEqual(nuts[1]["product"], "Tahini")
        self.assertLess(nuts[1]["my_teq"], 0.773)
        olive = sorted(self.groups["olive"], key=lambda r: -r["my_teq"])
        high = [r["sample"] for r in olive if r["my_teq"] >= 0.700]
        self.assertEqual(high, ["C2019PAHS00056A", "C2019PAHS00048A", "C2019PAHS00104A"])
        self.assertLess(olive[3]["my_teq"], 0.700)
        self.assertAlmostEqual(olive[3]["my_teq"], 0.699623, places=6)
        for pid in ("D2", "D3", "D4"):
            self.assertTrue(self.preds[pid]["met"], pid)

    def test_d5_descriptive(self):
        olive = self.groups["olive"]
        bap_over = sorted(r["sample"] for r in olive if r["v"]["Benzo[a]pyrene"] > 2.0)
        self.assertEqual(bap_over, ["C2019PAHS00056A"])
        self.assertEqual(self.by["C2019PAHS00056A"]["origin"], "GREECE")
        self.assertEqual(self.by["C2019PAHS00048A"]["v"]["Benzo[a]pyrene"], 2.0)
        pah4_over = sorted(r["sample"] for r in olive if r["my_pah4"] > 10.0)
        self.assertEqual(pah4_over, ["C2019PAHS00104A", "C2019PAHS00115A"])
        leb = self.by["C2019PAHS00115A"]
        self.assertEqual((leb["origin"], leb["v"]["Benzo[a]pyrene"]), ("LEBANON", 0.0))
        self.assertAlmostEqual(leb["v"]["Chrysene"], 7.6846, places=6)
        obs = self.preds["D5"]["observed"]
        self.assertEqual([x["sample"] for x in obs["bap_over_2"]], bap_over)
        self.assertEqual(sorted(x["sample"] for x in obs["pah4_over_10"]), pah4_over)
        for g, (k, mx) in {"olive": (32, 3.1), "nuts": (8, 2.45), "formula": (4, 0.4408)}.items():
            bap = [r["v"]["Benzo[a]pyrene"] for r in self.groups[g]
                   if r["v"]["Benzo[a]pyrene"] > 0]
            self.assertEqual((len(bap), max(bap)), (k, mx), g)
            self.assertEqual(self.s["analysis"]["bap"][g]["k"], k, g)


class TestTwinsIdsOrigins(Base):
    def test_one_identical_pair(self):
        groups = {}
        for r in self.rows:
            prof = tuple(r["v"][c] for c in self.comps)
            if any(v > 0 for v in prof):
                groups.setdefault(prof, []).append(r["sample"])
        pairs = sorted(sorted(v) for v in groups.values() if len(v) > 1)
        self.assertEqual(pairs, [["C2019PAHS00123A", "C2019PAHS00147A"]])
        self.assertEqual(self.s["analysis"]["twins_16"], pairs)
        a, b = self.by["C2019PAHS00123A"], self.by["C2019PAHS00147A"]
        self.assertEqual((a["origin"], a["date"]), ("UNKNOWN", "15-Apr-19"))
        self.assertEqual((b["origin"], b["date"]), ("ARGENTINA", "07-Apr-19"))
        self.assertEqual((a["product"], b["product"]), ("Oil - Olive", "Oil - Olive"))
        self.assertEqual(sum(1 for v in a["v"].values() if v > 0), 7)
        self.assertEqual(a["v"]["Naphthalene"], 16.4111)

    def test_id_numbers_and_ad_samples(self):
        nums, ad = set(), []
        for r in self.rows:
            m = ID_RE.match(r["sample"])
            self.assertIsNotNone(m, r["sample"])
            nums.add(int(m.group(1)))
            if m.group(2):
                ad.append(r["sample"])
        self.assertEqual(nums, set(range(1, 301)) - MISSING_NUMBERS)
        self.assertEqual(sorted(ad), ["C2019PAHS00037AD", "C2019PAHS00040AD"])
        for sid, origin in (("C2019PAHS00037AD", "TUNISIA"), ("C2019PAHS00040AD", "MOROCCO")):
            r = self.by[sid]
            self.assertNotIn(sid[:-1], self.by)
            self.assertEqual((r["product"], r["function"], r["origin"], r["date"]),
                             ("Oil - Olive", "Import", origin, "04-Sep-19"))
            self.assertEqual(r["my_teq"], 0.0)
        self.assertEqual(self.a["old_pattern_rejects"], sorted(ad))
        self.assertEqual([p["base_present"] for p in self.a["suffix_pairs"]], [False, False])
        self.assertEqual(self.a["ids_bad"], [])

    def test_function_split_vs_table1(self):
        for g, want in FILE_SPLIT.items():
            got = [0, 0, 0]
            for r in self.groups[g]:
                got[{"Domestic": 0, "Import": 1}.get(r["function"], 2)] += 1
            self.assertEqual(tuple(got), want, g)
            self.assertEqual(self.s["analysis"]["origins"][g], list(want) + [sum(want)], g)
            self.assertEqual(sum(want), sum(TABLE1[g]), g)
        self.assertEqual(FILE_SPLIT["nuts"], TABLE1["nuts"])
        self.assertNotEqual(FILE_SPLIT["formula"], TABLE1["formula"])
        self.assertNotEqual(FILE_SPLIT["olive"], TABLE1["olive"])

    def test_dates(self):
        days = [day(r["date"]) for r in self.rows]
        self.assertEqual((min(days), max(days)),
                         (datetime.date(2019, 4, 7), datetime.date(2020, 3, 11)))
        per = {}
        for d in days:
            per[d] = per.get(d, 0) + 1
        self.assertEqual((len(per), max(per.values())), (132, 9))
        self.assertEqual(day(self.by["C2019PAHS00001A"]["date"]), datetime.date(2020, 1, 7))
        self.assertEqual(day(self.by["C2019PAHS00003A"]["date"]), datetime.date(2019, 6, 9))


class TestRecord(Base):
    def test_gate_and_three_of_three(self):
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (3, 3))
        self.assertTrue(self.preds["G"]["met"])
        self.assertTrue(all(self.preds["G"]["observed"].values()))
        self.assertFalse(self.preds["D5"]["graded"])
        self.assertIsNone(self.preds["D5"]["met"])
        prov = self.s["provenance"]
        self.assertEqual(prov["md5"], "0bb033bbcdab8305839d0a8716def1b3")
        self.assertTrue(prov["md5_matches_portal"])
        self.assertEqual(self.a["pattern"], "^C2019PAHS(\\d{5})AD?$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
