#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pinned recompute test for docs/patulin-2008-0.1.0-result.md.

Rebuilds the label counts, the two below-limit forms ('<10' and '<0') and when each was used, the
lower and upper bounds, the exploratory consistency checks C1-C4 (with its own Fisher exact test)
and the registered predictions P1-P5 from the committed per-sample table
data/patulin_2008_samples.csv with its own code (it does not import the grader), and checks them
against the sealed grader record data/patulin_2008_summary.json. Standard library only.

Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0."""
import csv
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SAMPLES = os.path.join(DATA, "patulin_2008_samples.csv")
SUMMARY = os.path.join(DATA, "patulin_2008_summary.json")

RL = 10.0                                 # CFIA's reporting limit, ppb
ML = 50.0                                 # Codex draft level quoted by CFIA; Canada's ML today
EU_INFANT = 10.0                          # EU 2023/915, apple products for infants (reference)
JUICE, CONC = "Apple Juice", "Apple Juice Concentrate"
SHA = "4039e4a8b3e915b329b7e2afd9bc778c4a4707a7b7e5d99bd1319db0a745be66"
MONTHS = {m: i for i, m in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                                      "Sep", "Oct", "Nov", "Dec"), start=1)}


def load_samples():
    with open(SAMPLES, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def measured(r):
    """The AMOUNT as a number, or None for a '<' entry."""
    a = r["amount"]
    return None if a.startswith("<") else float(a)


def stated_limit(r):
    """The limit a '<' entry states: '<10' -> 10.0, '<0' -> 0.0."""
    return float(r["amount"][1:])


def ymd(text):
    """'7-Nov-08' -> (2008, 11, 7), without relying on the locale."""
    d, m, y = text.split("-")
    return 2000 + int(y), MONTHS[m], int(d)


def count(rows, col):
    out = {}
    for r in rows:
        out[r[col]] = out.get(r[col], 0) + 1
    return out


def fisher_p(a, b, c, d):
    """Two-sided Fisher exact p: the summed probability of every table no likelier than this."""
    row, col, n = a + b, a + c, a + b + c + d

    def prob(k):
        return math.comb(col, k) * math.comb(n - col, row - k) / math.comb(n, row)

    seen = prob(a)
    ks = range(max(0, row + col - n), min(row, col) + 1)
    return min(1.0, sum(prob(k) for k in ks if prob(k) <= seen * (1 + 1e-9)))


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_samples()
        with open(SUMMARY, encoding="utf-8") as fh:
            cls.s = json.load(fh)
        cls.a = cls.s["analysis"]
        cls.below = [r for r in cls.rows if measured(r) is None]
        cls.quant = [r for r in cls.rows if measured(r) is not None and measured(r) >= RL]

    def ge(self, rows):
        return sum(1 for r in rows if measured(r) is not None and measured(r) >= RL)


class TestTable(Base):
    def test_shape_and_labels(self):
        self.assertEqual(len(self.rows), 104)
        self.assertEqual(len({r["sample"] for r in self.rows}), 104)
        census = self.s["census"]
        self.assertEqual(count(self.rows, "product"), {CONC: 60, JUICE: 44})
        self.assertEqual(count(self.rows, "product"), census["products"])
        self.assertEqual(count(self.rows, "origin"), census["origins"])
        self.assertEqual(count(self.rows, "function"), {"imported": 94, "domestic": 10})
        self.assertEqual(census["units"], {"ng/g": 104})
        self.assertEqual(census["components"], {"Patulin": 104})

    def test_gate_failed_on_the_value_rule_only(self):
        preds = self.s["predictions"]
        self.assertEqual([p["id"] for p in preds],
                         ["G", "C1", "C2", "C3", "C4", "P1", "P2", "P3", "P4", "P5"])
        gate = preds[0]
        self.assertFalse(gate["met"])
        self.assertEqual(len(gate["observed"]), 10)
        self.assertEqual({k for k, v in gate["observed"].items() if not v}, {"value_kinds"})
        self.assertTrue(all(not p["graded"] and not p["met"] for p in preds[1:]))
        self.assertEqual((self.s["n_graded"], self.s["n_met"]), (1, 0))
        prov = self.s["provenance"]["PA"]
        self.assertEqual((prov["sha256"], prov["bytes"]), (SHA, 372295))

    def test_amount_forms(self):
        self.assertEqual(count(self.below, "amount"), {"<0": 75, "<10": 17})
        self.assertEqual(count(self.below, "amount"), self.a["below_rl_entries"])
        self.assertEqual(len(self.rows) - len(self.below), 12)
        self.assertEqual(len(self.below), 92)               # the page: 92 of 104 below 10 ppb
        # The registered rule accepts a '<' entry only with a limit above 0.
        failing = [r for r in self.below if not stated_limit(r) > 0]
        self.assertEqual(len(failing), 75)
        self.assertEqual(self.s["census"]["value_kinds"], {"lt": 17, "num": 12, "text": 75})
        self.assertEqual(count(self.rows, "kind"), {"lt": 17, "num": 12, "text": 75})


class TestCodingSwitch(Base):
    def test_when_each_form_was_used(self):
        lt10 = [r for r in self.below if r["amount"] == "<10"]
        lt0 = [r for r in self.below if r["amount"] == "<0"]
        self.assertEqual(max(ymd(r["date"]) for r in lt10), (2008, 12, 16))
        self.assertEqual(min(ymd(r["date"]) for r in lt0), (2008, 11, 21))
        self.assertEqual(max(r["sample"] for r in lt10), "FSAP8-00027")
        self.assertTrue(all(ymd(r["date"])[0] == 2008 for r in lt10))
        self.assertEqual(sum(1 for r in lt0 if ymd(r["date"])[0] == 2008), 6)
        self.assertEqual(sum(1 for r in lt0 if ymd(r["date"])[0] == 2009), 69)
        late = [r for r in self.below if ymd(r["date"]) >= (2009, 1, 1)]
        self.assertEqual(len(late), 69)
        self.assertTrue(all(r["amount"] == "<0" for r in late))
        self.assertEqual(count(lt10, "region"),
                         {"WEST": 13, "QUEBEC": 2, "ONTARIO": 1, "ATLANTIC": 1})
        self.assertEqual(set(count(lt0, "region")), {"WEST", "QUEBEC", "ONTARIO"})

    def test_bounds(self):
        nums = [measured(r) for r in self.rows if measured(r) is not None]
        total = sum(nums)
        self.assertAlmostEqual(total, 188.0, places=9)
        n = len(self.rows)
        lower = total / n
        upper_page = (total + RL * len(self.below)) / n
        upper_literal = (total + sum(stated_limit(r) for r in self.below)) / n
        self.assertAlmostEqual(lower, 1.81, delta=0.005)
        self.assertAlmostEqual(upper_page, 10.65, delta=0.005)
        self.assertAlmostEqual(upper_literal, 3.44, delta=0.005)
        self.assertGreater(upper_page / upper_literal, 3.0)


class TestExploratory(Base):
    """The registered items, read after the gate failed with '<0' taken as below the limit."""

    def test_c1_to_c3(self):
        juice = [r for r in self.rows if r["product"] == JUICE]
        conc = [r for r in self.rows if r["product"] == CONC]
        self.assertEqual((self.ge(juice), self.ge(conc)), (7, 5))
        self.assertEqual((self.ge(juice), self.ge(conc)), (self.a["juice_ge"], self.a["conc_ge"]))
        self.assertEqual(round(100 * 92 / 104, 1), 88.5)
        jmax = max(measured(r) for r in juice if measured(r) is not None)
        cmax = max((r for r in conc if measured(r) is not None), key=measured)
        self.assertEqual(jmax, 26.7)
        self.assertEqual((measured(cmax), cmax["amount"]), (24.0, "24"))
        self.assertEqual(sum(1 for r in self.quant if measured(r) >= ML), 0)

    def test_c4_fisher(self):
        def table(in_group):
            a = sum(1 for r in self.quant if in_group(r))
            b = sum(1 for r in self.rows if in_group(r)) - a
            c = sum(1 for r in self.quant if not in_group(r))
            d = sum(1 for r in self.rows if not in_group(r)) - c
            return [a, b, c, d]

        china = table(lambda r: r["origin"] == "CHINA")
        func = table(lambda r: r["function"] == "imported")
        self.assertEqual(china, [3, 39, 9, 53])
        self.assertEqual(func, [11, 83, 1, 9])
        self.assertEqual((china, func), (self.a["china_table"], self.a["function_table"]))
        self.assertAlmostEqual(fisher_p(*china), self.a["china_p"], places=9)
        self.assertAlmostEqual(fisher_p(*china), 0.3525, delta=0.0001)
        self.assertAlmostEqual(fisher_p(*func), 1.0, places=9)

    def test_p1_to_p5(self):
        nums = [measured(r) for r in self.rows if measured(r) is not None]
        self.assertEqual(min(nums), 10.1)                               # P1
        self.assertEqual(sum(1 for v in nums if 0 < v < RL), 0)
        dom = [r for r in self.rows if r["function"] == "domestic"]
        imp = [r for r in self.rows if r["function"] == "imported"]
        self.assertEqual({r["origin"] for r in dom}, {"CANADA"})        # P2
        self.assertEqual(sum(1 for r in imp if r["origin"] == "CANADA"), 0)
        below_15 = sum(1 for r in self.quant if measured(r) < 15.0)     # P3 (registered >= 8)
        self.assertEqual(below_15, 7)
        self.assertEqual(below_15, self.a["below_15"])
        self.assertLess(below_15, 8)
        dom_q = [r for r in self.quant if r["function"] == "domestic"]  # P4
        self.assertEqual([(r["sample"], r["product"], measured(r)) for r in dom_q],
                         [("FSAP8-00032", CONC, 19.9)])
        china_q = sorted(r["sample"] for r in self.quant if r["origin"] == "CHINA")  # P5
        self.assertEqual(china_q, ["FSAP8-00094", "FSAP8-00098", "FSAP8-00117"])
        self.assertEqual(len(self.quant), self.a["n_ge_rl"])
        self.assertEqual(sum(1 for r in self.quant if measured(r) - RL <= 0.5), 4)
        self.assertEqual(sum(1 for v in nums if v > EU_INFANT), 12)
        self.assertEqual(self.a["n_over_eu_infant"], 12)
        by_origin = count(self.quant, "origin")
        self.assertEqual(by_origin, {"UNITED STATES": 4, "CHINA": 3, "CANADA": 1, "CHILE": 1,
                                     "JORDAN": 1, "MOLDOVA": 1, "UNKNOWN": 1})


class TestOther(Base):
    def test_dates(self):
        dates = [r["date"] for r in self.rows]
        self.assertEqual(min(ymd(d) for d in dates), (2008, 11, 3))
        self.assertEqual(max(ymd(d) for d in dates), (2009, 3, 23))
        self.assertEqual((min(dates), max(dates)), ("10-Mar-09", "7-Nov-08"))
        self.assertEqual((self.a["date_min"], self.a["date_max"]), ("2008-11-03", "2009-03-23"))

    def test_suffixed_samples(self):
        ids = {r["sample"] for r in self.rows}
        suffixed = sorted(s for s in ids if s.endswith("A"))
        self.assertEqual(suffixed, ["FSAP8-00012A", "FSAP8-00118A", "FSAP8-00294A"])
        self.assertTrue(all(s[:-1] in ids for s in suffixed))
        by_id = {r["sample"]: r for r in self.rows}
        keys = ("product", "origin", "function", "region")
        same = [s for s in suffixed if all(by_id[s][k] == by_id[s[:-1]][k] for k in keys)]
        self.assertEqual(same, ["FSAP8-00118A"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
