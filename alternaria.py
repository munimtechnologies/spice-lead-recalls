#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""alternaria 0.1.0: CFIA's open Alternaria toxin files against its report and the EU's levels.

Grades docs/alternaria-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes two per-sample files of alternariol (AOH)
and alternariol monomethyl ether (AME) in Canadian retail foods on open.canada.ca (Open
Government Licence - Canada): F1, its 2014-2022 survey (5,190 rows = 2,595 samples x 2), and
F2, its 2018-19 beer, juice, oil and seed survey (798 rows = 399 samples x 2). CFIA's report
prints only AOH + AME sums. This reads the result columns for the first time to (a) reproduce
every report row the product labels identify, (b) settle the report's internal contradictions
(an infant row that matches 2019 alone, a total maximum below a row maximum, a swapped Table 1),
and (c) compare each toxin with the indicative levels of EU Recommendation 2022/553.

Both files are SHA-256 pinned. Value rule (registered): blank, 0, a "<" value or a non-detect
token is a non-detect; a positive is a plain non-negative decimal; any comma or unparseable cell
fails the gate. Units go through an explicit table. Standard library only. Code Apache-2.0;
derived data CC BY 4.0. A reference comparison, not a compliance finding (EU indicative levels
trigger investigation and are not maximum levels; Canada sets no limit for these toxins), not
about any brand, and not individual dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import statistics
import sys
import time
import urllib.request

VERSION = "0.1.0"

F1 = {
    "key": "F1",
    "dataset": "8888649b-c059-4f76-ae0f-30ab6c1159c5",
    "resource": "c93db5ad-283a-45e1-8995-f1dc33c9392c",
    "filename": ("fsap-chem-ts-alternaria-in-selected-foods-2014-2018-and-2019-2022_"
                 "paaspa-chem-ec-alternaria-dans.csv"),
    "sha256": "9b79ec399c2d7e016ee52aef0279767b68e9d09f8fbda3316e772bf1cca3722a",
    "rows": 5190, "samples": 2595,
}
F2 = {
    "key": "F2",
    "dataset": "c97c7e25-7acc-449a-91f1-1ac811490ec4",
    "resource": "7e210ca5-2e37-406c-9144-4d0e055d45fd",
    "filename": ("cfia_acia-1141_2018-19_alternaria_in_beverages__oils_and_seeds_-_2018-2019_"
                 "toxines-dalternaria-d.csv"),
    "sha256": "39ec24c7b20ab71334cf1915ef790a48a3d2a0abf5b9c7068f35a2e6557ac5e8",
    "rows": 798, "samples": 399,
}

AOH, AME = "Alternariol", "Alternariol Monomethyl Ether"

# Product-label row counts, from the names-only census (job myco-census-v2, 2026-10-25).
F1_PRODUCT_ROWS = {
    "Wine": 550, "Tomato Sauce": 378, "Flour - Wheat": 376, "Infant Food - Puree": 332,
    "Juice - Other": 198, "Grain - Barley": 194, "Pomegranate": 188,
    "Infant Food (non-cereal)": 184, "Juice - Pomegranate": 180, "Wheat Products": 180,
    "Sorghum Products": 174, "Couscous": 166, "Juice - Blend": 132, "Preserve - Jam/Jelly": 100,
    "Mixed Fruit": 98, "Cereal - Rice": 96, "Cereal - Corn": 88, "Crackers": 88,
    "Beverage - Fruit": 86, "Oil - Sunflower": 82, "Snack Bar": 82, "Pepper - Fresh": 80,
    "Seed - Sunflower": 68, "Grain - Sorghum": 64, "Dried Fruit": 54, "Pepper - Hot - Fresh": 53,
    "Barley Products": 52, "Date": 50, "Fig": 50, "Raisin": 50, "Cranberry - dried": 48,
    "Marmalade": 48, "Prune": 48, "Vegetable Products": 42, "Pepper - Pickled Hot": 40,
    "Protein Bar": 38, "Topping - Dessert/Fruit": 36, "Granola/Cereal Bar": 34, "Pasta - Dry": 34,
    "Juice - Orange": 32, "Juice - Apple": 28, "Baking Mixes": 26, "Strawberry": 26,
    "Juice - Grape": 18, "Cereal - Mixed Grains": 16, "Mango": 16, "Tomato": 16,
    "Pepper (GH)": 15, "Pepper - Pickled": 14, "juice - pineapple": 12,
    "Bakery Product - Cookie": 10, "Beverage - Lemonade": 10, "Pepper - Organic": 10,
    "Juice - Concentrate": 8, "Juice - Lemon": 8, "Raspberry": 8, "Blueberry": 6, "Peach": 6,
    "Strawberry - Organic": 6, "Tomato - Organic": 6, "Cereal": 4, "Cherry": 4,
    "Juice - Pineapple": 4, "Nectar - Mango": 4, "Baked Goods": 2,
    "Bakery Product - Tortilla/Wrap/Pita": 2, "Berries - Other": 2, "Blackberry": 2,
    "Bran - Wheat": 2, "Cereal - Adult": 2, "Crispbread/Crouton": 2, "Juice - Cranberry": 2,
    "Juice/Nectar - Other": 2, "Mango - Organic": 2, "Mixed Fruit & Nuts": 2,
    "Nectar - Apricot": 2, "Nectar - Blend": 2, "Nectar - Other": 2, "Pineapple": 2,
    "Preserve - Raspberry": 2, "Prune - Organic": 2, "Rice Products": 2,
}
F1_PLAN_ROWS = {"2014_TS025": 298, "2015_TS025": 996, "2016_TS025": 986, "2017_TS025": 716,
                "2019_TS025": 770, "2020_TS025": 692, "2021_TS025": 732}
F2_PRODUCT_ROWS = {
    "Beer": 160, "Juice - Blend": 156, "Juice - Orange": 68, "Juice - Apple": 48,
    "Seed - Sunflower": 34, "Seed - Pumpkin": 24, "juice - pineapple": 24, "Oil - Soybean": 22,
    "Juice - Other": 20, "Oil - Olive": 20, "Oil - Palm": 20, "Oil - Sunflower": 20,
    "Seed - Flax": 20, "Oil - Corn": 18, "Oil - Peanut": 18, "Oil - Sesame": 18,
    "Oil - Canola": 16, "Seed - Chia": 16, "Oil - Other": 14, "Oil - Vegetable": 14,
    "Juice - Pomegranate": 10, "Juice - Grape": 8, "Cider - Apple": 6, "Juice - Grapefruit": 6,
    "Seed - Sesame": 6, "Juice - Cranberry": 4, "Beverage - Other": 2, "Juice - Concentrate": 2,
    "Nectar - Mango": 2, "Nectar - Peach": 2,
}

# Units -> factor to ng/g (= ug/kg = ppb). Keys are lower-cased.
UNIT_FACTORS = {"ng/g": 1.0, "ppb": 1.0, "µg/kg": 1.0, "μg/kg": 1.0, "ug/kg": 1.0,
                "ppm": 1000.0, "µg/g": 1000.0, "μg/g": 1000.0, "ug/g": 1000.0,
                "mg/kg": 1000.0}
ND_TOKENS = ("nd", "n.d.", "n/d", "not detected", "non détecté", "non detecte")

# F1 label -> report-row mapping (see docs/alternaria-report-check-0.1.0.md).
FRESH_PEPPER = frozenset(("Pepper - Fresh", "Pepper - Hot - Fresh", "Pepper (GH)",
                          "Pepper - Organic"))
PROCESSED_PEPPER = frozenset(("Pepper - Pickled Hot", "Pepper - Pickled", "Vegetable Products"))
INFANT_PUREE, INFANT_MEAL = "Infant Food - Puree", "Infant Food (non-cereal)"
TOMATO = frozenset(("Tomato Sauce", "Tomato", "Tomato - Organic"))
BARLEY = frozenset(("Grain - Barley", "Barley Products"))
CORN = frozenset(("Cereal - Corn", "Cereal - Mixed Grains"))

# Report rows the labels identify: (id, text, categories, n, positives, min, max, avg).
# Printed figures are strings (precision matters); None = not printed / N/A.
ROWS = (
    ("C1", "fresh pepper 2020 (Table 3)", ("fresh_pepper_2020",), 79, 0, None, "0", None),
    ("C2", "barley-based foods 2021 (Table 4)", ("barley_2021",), 123, 78, "0.093", "240", "5.7"),
    ("C3", "corn-based foods 2020 (Table 4)", ("corn_2020",), 52, 37, "0.20", "6.7", "2.0"),
    ("C4", "wheat-based foods 2017 (Table 4)", ("wheat_2017",), 283, 247, "0.090", "37", "2.2"),
    ("C5", "infant puree 2019 (Table 5)", ("puree_2019",), 108, 94, "0.52", "26", "7.9"),
    ("C6", "infant puree 2016 (Table 5)", ("puree_2016",), 58, 42, "0.20", "37", "4.4"),
    ("C7", "toddler/baby meals 2019 (Table 5)", ("meal_2019",), 90, 60, "0.10", "12", "1.1"),
    ("C8", "toddler/baby meals 2016 (Table 5)", ("meal_2016",), 2, 1, None, "1.2", None),
    ("C9", "sunflower seeds 2017 (Table 7 nut/seed)", ("sunseed_2017",), 34, 31, "0.20", "20",
     "5.6"),
    ("C10", "pomegranate products 2019 (Table 8)", ("pomegranate_2019",), 187, 124, "0.060",
     "870", "160"),
    ("C11", "fruit-based processed 2016 (Table 9)", ("fruit_2016",), 333, 109, "0.050", "150",
     "3.4"),
    ("C12", "tomato-based 2016 (Table 9)", ("tomato_2016",), 100, 41, "0.060", "350", "9.4"),
    ("C13", "sunflower oil 2017 (Table 10)", ("sunoil_2017",), 41, 31, "0.10", "62", "5.9"),
    ("C14", "wine 2014 (Table 11)", ("wine_2014",), 75, 26, "0.50", "11", "2.6"),
    ("C15", "wine 2015 (Table 11)", ("wine_2015",), 200, 141, "0.092", "21", "1.8"),
    ("C16", "F2 juices 2018 without pomegranate juice (Table 6)", ("f2_juice",), 174, 125,
     "0.050", "570", "17"),
)
C17_ROWS = (
    ("seeds", ("f2_seed",), 50, 36, "0.054", "55", "6.0"),
    ("oils", ("f2_oil",), 90, 50, "0.10", "57", "7.1"),
    ("overall", ("f2_seed", "f2_oil", "f2_juice", "f2_pomegranate_juice", "f2_beer"), 399, 232,
     "0.050", "573", None),
)
INFANT_CATS = ("puree_2016", "puree_2019", "meal_2016", "meal_2019")
FRUIT_CATS = ("pomegranate_2019", "wine_2014", "wine_2015", "tomato_2015", "tomato_2016")

# Registered thresholds.
P1_AVG_BAND = (4.95, 5.15)
P2_MAX_CANADA = 24
P3_POM_MAX_BAND = (870.5, 871.5)
P4_POS = (35, 36)
P5_POS_BAND = (1552, 1554)
P6_POM_JUICE_POS, P6_BEER_POS = 5, 16
# EU Recommendation 2022/553 indicative levels, ug/kg (= ng/g): (AOH, AME).
EU_TOMATO, EU_SEED, EU_SUNOIL, EU_INFANT = (10.0, 5.0), (30.0, 30.0), (10.0, 10.0), (2.0, 2.0)
E1_BAND, E2_MAX_SUNSEED, E3_BAND, E5_BAND = (2, 4), 1, (2, 8), (0.25, 0.60)


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def parse_amount(raw):
    """(value, detected, kind) for one result cell under the registered rule.

    kind is one of: blank, lt, nd, zero, comma (ambiguous -> gate fails), bad, pos."""
    s = (raw or "").strip()
    if s == "":
        return 0.0, False, "blank"
    if s.startswith("<"):
        return 0.0, False, "lt"
    if s.lower() in ND_TOKENS:
        return 0.0, False, "nd"
    if "," in s:
        return None, False, "comma"
    try:
        v = float(s)
    except ValueError:
        return None, False, "bad"
    if v != v or v < 0 or v == float("inf"):
        return None, False, "bad"
    if v == 0:
        return 0.0, False, "zero"
    return v, True, "pos"


def tolerance(printed):
    """Half a unit in the last significant place of a printed figure.

    Decimals use their decimal places ("0.090" -> 0.0005). Whole numbers with trailing zeros are
    read at two significant figures ("870" -> 5, "200" -> 5); other whole numbers to the unit."""
    s = printed.strip()
    if "." in s:
        return 0.5 * 10 ** (-len(s.split(".")[1]))
    digits = s.lstrip("-")
    stripped = digits.rstrip("0")
    if not stripped:
        return 0.5
    z = len(digits) - len(stripped)
    if len(stripped) < 2:
        z = max(0, z - (2 - len(stripped)))
    return 0.5 * 10 ** z


def matches(x, printed):
    """Does x round to the printed figure at its printed precision?"""
    if x is None:
        return False
    return abs(x - float(printed)) <= tolerance(printed) + 1e-9


def clean(cell):
    return (cell or "").replace("﻿", "").strip()


def find_columns(header):
    h = [clean(c) for c in header]

    def first(test, what, required=True):
        for i, c in enumerate(h):
            if test(c):
                return i
        if required:
            raise ValueError(f"no {what} column in {header!r}")
        return None

    return {
        "sample": first(lambda c: c.startswith("Sample"), "sample"),
        "origin": first(lambda c: c == "Origin", "origin"),
        "product": first(lambda c: c == "Product", "product"),
        "component": first(lambda c: c == "Component", "component"),
        "value": first(lambda c: c.startswith("Result") or c in ("MaxOfAMOUNT", "AMOUNT"),
                       "value"),
        "unit": first(lambda c: c.startswith("Unit") or c.startswith("Report Unit"), "unit"),
        "plan": first(lambda c: c.startswith("Plan Code") or c == "PLAN_CODE", "plan", False),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def f1_category(product, year):
    """Report row of an F1 sample, from its product label and plan year."""
    if product in FRESH_PEPPER:
        return "fresh_pepper_" + year
    if product == INFANT_PUREE:
        return "puree_" + year
    if product == INFANT_MEAL:
        return "meal_" + year
    if product == "Wine":
        return "wine_" + year
    if product in TOMATO and year in ("2015", "2016"):
        return "tomato_" + year
    if year == "2021":
        return "barley_2021" if product in BARLEY else "wheat_sorghum_2021"
    if year == "2020":
        if product in CORN:
            return "corn_2020"
        if product in PROCESSED_PEPPER:
            return "processed_pepper_2020"
        return "rice_wheat_nutseed_2020"
    if year == "2019":
        return "pomegranate_2019"
    if year == "2017":
        if product == "Seed - Sunflower":
            return "sunseed_2017"
        if product == "Oil - Sunflower":
            return "sunoil_2017"
        return "wheat_2017"
    if year == "2016":
        return "fruit_2016"
    if year in ("2014", "2015"):
        return "juice_pom_2014_15"
    return "unassigned"


def f2_category(product):
    if product == "Beer":
        return "f2_beer"
    if product.startswith("Oil - "):
        return "f2_oil"
    if product.startswith("Seed - "):
        return "f2_seed"
    if product == "Juice - Pomegranate":
        return "f2_pomegranate_juice"
    return "f2_juice"


def parse_text(text, key):
    """(samples, census) from one decoded CSV. samples: {id: record}."""
    table = list(csv.reader(io.StringIO(text)))
    header = table[0]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    col = find_columns(header)

    def cell(r, k):
        i = col[k]
        if i is None:
            return ""
        return r[i] if i < len(r) else ""

    comps, kinds, units, plans, products = {}, {}, {}, {}, {}
    per_sample_rows, per_sample_comp = {}, {}
    samples = {}
    n_rows = 0
    for r in body:
        n_rows += 1
        sid = clean(cell(r, "sample"))
        comp = clean(cell(r, "component"))
        product = clean(cell(r, "product"))
        unit = clean(cell(r, "unit"))
        plan = clean(cell(r, "plan"))
        value, det, kind = parse_amount(cell(r, "value"))
        factor = UNIT_FACTORS.get(unit.lower())
        _bump(comps, comp)
        _bump(kinds, kind)
        _bump(units, unit)
        _bump(plans, plan)
        _bump(products, product)
        _bump(per_sample_rows, sid)
        _bump(per_sample_comp, (sid, comp))
        rec = samples.setdefault(sid, {
            "file": key, "sample": sid, "plan": plan, "product": product,
            "origin": clean(cell(r, "origin")), "aoh": 0.0, "ame": 0.0, "labels": set()})
        rec["labels"].add(product)
        if value is not None and factor is not None:
            if comp == AOH:
                rec["aoh"] = value * factor
            elif comp == AME:
                rec["ame"] = value * factor
    for rec in samples.values():
        rec["total"] = rec["aoh"] + rec["ame"]
        if key == "F1":
            rec["category"] = f1_category(rec["product"], rec["plan"][:4])
        else:
            rec["category"] = f2_category(rec["product"])
    rps = {}
    for v in per_sample_rows.values():
        _bump(rps, str(v))
    one_of_each = all(per_sample_comp.get((s, AOH)) == 1 and per_sample_comp.get((s, AME)) == 1
                      for s in per_sample_rows)
    census = {"n_rows": n_rows, "distinct_samples": len(samples), "components": comps,
              "products": products, "plans": plans, "units": units, "amount_kinds": kinds,
              "rows_per_sample": rps, "one_of_each": one_of_each}
    return samples, census


def gate_checks(c1, c2, sha1_ok, sha2_ok):
    def fmt(c):
        k = c["amount_kinds"]
        return k.get("bad", 0) == 0 and k.get("comma", 0) == 0 and k.get("pos", 0) > 0

    return {
        "f1_sha256": bool(sha1_ok),
        "f1_rows": c1["n_rows"] == F1["rows"],
        "f1_samples": c1["distinct_samples"] == F1["samples"],
        "f1_rows_per_sample": c1["rows_per_sample"] == {"2": F1["samples"]},
        "f1_one_aoh_one_ame": bool(c1["one_of_each"]),
        "f1_components": c1["components"] == {AOH: F1["samples"], AME: F1["samples"]},
        "f1_products": c1["products"] == F1_PRODUCT_ROWS,
        "f1_plans": c1["plans"] == F1_PLAN_ROWS,
        "f1_unit": c1["units"] == {"ng/g": F1["rows"]},
        "f1_value_format": fmt(c1),
        "f2_sha256": bool(sha2_ok),
        "f2_rows": c2["n_rows"] == F2["rows"],
        "f2_samples": c2["distinct_samples"] == F2["samples"],
        "f2_rows_per_sample": c2["rows_per_sample"] == {"2": F2["samples"]},
        "f2_one_aoh_one_ame": bool(c2["one_of_each"]),
        "f2_components": c2["components"] == {AOH: F2["samples"], AME: F2["samples"]},
        "f2_products": c2["products"] == F2_PRODUCT_ROWS,
        "f2_units_known": len(c2["units"]) >= 1
        and all(u.lower() in UNIT_FACTORS for u in c2["units"]),
        "f2_value_format": fmt(c2),
    }


def select(samples, cats):
    cs = set(cats)
    return [s for s in samples if s["category"] in cs]


def row_stats(recs):
    totals = [s["total"] for s in recs]
    pos = [t for t in totals if t > 0]
    return {"n": len(totals), "pos": len(pos),
            "min": min(pos) if pos else None,
            "max": max(totals) if totals else None,
            "avg": statistics.fmean(pos) if pos else None}


def check_row(st, n, pos, mn, mx, avg):
    """(ok, detail) for one report row against its statistics."""
    detail = {"n": [st["n"], n], "pos": [st["pos"], pos]}
    ok = st["n"] == n and st["pos"] == pos
    for name, printed in (("min", mn), ("max", mx), ("avg", avg)):
        if printed is None:
            continue
        x = st[name]
        if pos == 0 and printed == "0":
            good = (x or 0.0) == 0.0
        else:
            good = matches(x, printed)
        detail[name] = [x, printed, good]
        ok = ok and good
    return ok, detail


def exceeds(rec, levels):
    return rec["aoh"] > levels[0] or rec["ame"] > levels[1]


def count_exceed(recs, levels):
    return sum(1 for r in recs if exceeds(r, levels))


def aoh_share(recs):
    a = sum(r["aoh"] for r in recs)
    m = sum(r["ame"] for r in recs)
    return a / (a + m) if (a + m) > 0 else None


def category_table(samples):
    out = {}
    for cat in sorted({s["category"] for s in samples}):
        recs = [s for s in samples if s["category"] == cat]
        st = row_stats(recs)
        st["aoh_share"] = aoh_share(recs)
        st["aoh_pos"] = sum(1 for r in recs if r["aoh"] > 0)
        st["ame_pos"] = sum(1 for r in recs if r["ame"] > 0)
        out[cat] = st
    return out


# ---------------------------------------------------------------------------
# Analysis and grading.
# ---------------------------------------------------------------------------
def analyse(s1, s2):
    """s1, s2: lists of F1 and F2 sample records."""
    allrecs = s1 + s2
    rows = {}
    for rid, text, cats, n, pos, mn, mx, avg in ROWS:
        st = row_stats(select(allrecs, cats))
        ok, detail = check_row(st, n, pos, mn, mx, avg)
        rows[rid] = {"text": text, "ok": ok, "detail": detail}
    c17 = {}
    for name, cats, n, pos, mn, mx, avg in C17_ROWS:
        st = row_stats(select(s2, cats))
        ok, detail = check_row(st, n, pos, mn, mx, avg)
        c17[name] = {"ok": ok, "detail": detail}

    infant = row_stats(select(s1, INFANT_CATS))
    pom = select(s1, ("pomegranate_2019",))
    pom_canada = sum(1 for r in pom if r["origin"] == "CANADA")
    pom_max = max((r["total"] for r in pom), default=None)
    top = max(s1, key=lambda r: r["total"]) if s1 else None
    tom15 = row_stats(select(s1, ("tomato_2015",)))
    f1 = row_stats(s1)
    beer = row_stats(select(s2, ("f2_beer",)))
    pomj = row_stats(select(s2, ("f2_pomegranate_juice",)))

    tomato = select(s1, ("tomato_2015", "tomato_2016"))
    sunseed = select(s1, ("sunseed_2017",)) + [r for r in s2 if r["product"] == "Seed - Sunflower"]
    sesame = [r for r in s2 if r["product"] == "Seed - Sesame"]
    sunoil = select(s1, ("sunoil_2017",)) + [r for r in s2 if r["product"] == "Oil - Sunflower"]
    fruit = select(s1, FRUIT_CATS)
    purees = select(s1, ("puree_2016", "puree_2019"))
    return {
        "rows": rows, "c17": c17,
        "infant_all": infant,
        "pomegranate_2019_canada": pom_canada, "pomegranate_2019_n": len(pom),
        "pomegranate_2019_max": pom_max,
        "f1_top": ({"total": top["total"], "category": top["category"],
                    "product": top["product"], "plan": top["plan"]} if top else None),
        "tomato_2015": tom15, "f1_overall": f1,
        "f2_beer": beer, "f2_pomegranate_juice": pomj,
        "eu": {
            "tomato_n": len(tomato), "tomato_exceed": count_exceed(tomato, EU_TOMATO),
            "tomato_aoh_over": sum(1 for r in tomato if r["aoh"] > EU_TOMATO[0]),
            "tomato_ame_over": sum(1 for r in tomato if r["ame"] > EU_TOMATO[1]),
            "sunseed_n": len(sunseed), "sunseed_exceed": count_exceed(sunseed, EU_SEED),
            "sesame_n": len(sesame), "sesame_exceed": count_exceed(sesame, EU_SEED),
            "sunoil_n": len(sunoil), "sunoil_exceed": count_exceed(sunoil, EU_SUNOIL),
            "sunoil_aoh_over": sum(1 for r in sunoil if r["aoh"] > EU_SUNOIL[0]),
            "sunoil_ame_over": sum(1 for r in sunoil if r["ame"] > EU_SUNOIL[1]),
            "sunflower_aoh_share": aoh_share(sunseed + sunoil),
            "fruit_aoh_share": aoh_share(fruit),
            "puree_n": len(purees), "puree_over_2": count_exceed(purees, EU_INFANT),
        },
        "categories": category_table(allrecs),
    }


def grade(a, gate_obs):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "both files: SHA-256, rows, samples, one AOH + one AME row per sample, "
                      "component and product-label row counts, F1 plan codes and unit, F2 "
                      "units in the unit table, and a clean value format"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    for rid, text, _cats, n, pos, mn, mx, avg in ROWS:
        r = a["rows"][rid]
        add(rid, "consistency",
            f"{text}: n {n}, positives {pos}, min {mn}, max {mx}, avg {avg} (printed)",
            r["detail"], r["ok"])
    add("C17", "consistency",
        "F2 seeds 50/36/0.054-55/6.0, oils 90/50/0.10-57/7.1, overall 399/232/0.050-573",
        a["c17"], all(v["ok"] for v in a["c17"].values()))

    inf = a["infant_all"]
    add("P1", "prediction",
        "all 258 infant samples: 197 positive, max matches 37 (not Table 2's 26), average of "
        "positives in [4.95, 5.15) (not 5.2) -- Table 2's max and average are 2019-only",
        inf, inf["n"] == 258 and inf["pos"] == 197 and matches(inf["max"], "37")
        and inf["avg"] is not None and P1_AVG_BAND[0] <= inf["avg"] < P1_AVG_BAND[1])

    add("P2", "prediction",
        "at most 24 of the 187 pomegranate-label 2019 samples have Origin CANADA (Table 1's "
        "pomegranate and processed-fruit rows are swapped)",
        {"canada": a["pomegranate_2019_canada"], "n": a["pomegranate_2019_n"]},
        a["pomegranate_2019_canada"] <= P2_MAX_CANADA)

    top, pmax = a["f1_top"], a["pomegranate_2019_max"]
    add("P3", "prediction",
        "F1's largest total matches 880 and is a 2015 tomato-label sample; the largest 2019 "
        "pomegranate total is in [870.5, 871.5) (Table 2's 871 is the pomegranate maximum)",
        {"top": top, "pomegranate_max": pmax},
        top is not None and matches(top["total"], "880") and top["category"] == "tomato_2015"
        and pmax is not None and P3_POM_MAX_BAND[0] <= pmax < P3_POM_MAX_BAND[1])

    t = a["tomato_2015"]
    add("P4", "prediction",
        "2015 tomato labels: 100 samples, 35 or 36 positive, min matches 0.080, max matches 880",
        t, t["n"] == 100 and t["pos"] in P4_POS and matches(t["min"], "0.080")
        and matches(t["max"], "880"))

    f = a["f1_overall"]
    add("P5", "prediction",
        "F1 has 1,552-1,554 positive samples and its smallest positive total matches 0.046",
        f, P5_POS_BAND[0] <= f["pos"] <= P5_POS_BAND[1] and matches(f["min"], "0.046"))

    add("P6", "prediction",
        "F2: all 5 pomegranate juices positive and 16 of 80 beers positive",
        {"pomegranate_juice": a["f2_pomegranate_juice"], "beer": a["f2_beer"]},
        a["f2_pomegranate_juice"]["n"] == 5
        and a["f2_pomegranate_juice"]["pos"] == P6_POM_JUICE_POS
        and a["f2_beer"]["n"] == 80 and a["f2_beer"]["pos"] == P6_BEER_POS)

    eu = a["eu"]
    add("E1", "prediction",
        "2 to 4 of the 200 2015-16 tomato-label samples exceed the EU indicative level for "
        "processed tomato products (AOH 10 or AME 5 ug/kg)",
        {k: eu[k] for k in ("tomato_n", "tomato_exceed", "tomato_aoh_over", "tomato_ame_over")},
        eu["tomato_n"] == 200 and E1_BAND[0] <= eu["tomato_exceed"] <= E1_BAND[1])

    add("E2", "prediction",
        "at most 1 of the 51 sunflower-seed samples exceeds AOH 30 or AME 30 ug/kg, and none of "
        "F2's 3 sesame seeds",
        {k: eu[k] for k in ("sunseed_n", "sunseed_exceed", "sesame_n", "sesame_exceed")},
        eu["sunseed_n"] == 51 and eu["sunseed_exceed"] <= E2_MAX_SUNSEED
        and eu["sesame_n"] == 3 and eu["sesame_exceed"] == 0)

    add("E3", "prediction",
        "2 to 8 of the 51 sunflower-oil samples exceed AOH 10 or AME 10 ug/kg",
        {k: eu[k] for k in ("sunoil_n", "sunoil_exceed", "sunoil_aoh_over", "sunoil_ame_over")},
        eu["sunoil_n"] == 51 and E3_BAND[0] <= eu["sunoil_exceed"] <= E3_BAND[1])

    sf, fr = eu["sunflower_aoh_share"], eu["fruit_aoh_share"]
    add("E4", "prediction",
        "AME carries more than half the AOH+AME mass in sunflower seeds and oil (pooled); AOH "
        "carries more than half in the fruit-based rows (2019 pomegranate, wine, 2015-16 tomato)",
        {"sunflower_aoh_share": sf, "fruit_aoh_share": fr},
        sf is not None and fr is not None and sf < 0.5 and fr > 0.5)

    share = (eu["puree_over_2"] / eu["puree_n"]) if eu["puree_n"] else None
    add("E5", "prediction",
        "25-60% of the 166 infant purees have AOH or AME above 2 ug/kg (a benchmark only: the EU "
        "level is for cereal-based infant food)",
        {"puree_n": eu["puree_n"], "puree_over_2": eu["puree_over_2"], "share": share},
        eu["puree_n"] == 166 and share is not None and E5_BAND[0] <= share <= E5_BAND[1])
    return preds


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-alternaria"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(spec, data_dir):
    path = os.path.join(data_dir, spec["resource"] + ".csv") if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == spec["sha256"]:
            return raw, "data-volume"
    base = f"/data/dataset/{spec['dataset']}/resource/{spec['resource']}/download/{spec['filename']}"
    errors = []
    for host in ("https://open.canada.ca", "https://ouvert.canada.ca"):
        url = host + base
        try:
            raw = _fetch(url)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        if _sha(raw) != spec["sha256"]:
            errors.append(f"{url}: SHA-256 {_sha(raw)} != {spec['sha256']}")
            continue
        if path:
            try:
                os.makedirs(data_dir, exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(raw)
            except OSError:
                pass
        return raw, url
    raise RuntimeError(f"{spec['key']}: no verified copy: " + "; ".join(errors))


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


# ---------------------------------------------------------------------------
# Outputs.
# ---------------------------------------------------------------------------
def _r(x):
    if isinstance(x, set):
        return sorted(x)
    return "" if x is None else (round(x, 6) if isinstance(x, float) else x)


def write_outputs(out_dir, s1, s2, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "alternaria_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "sample", "plan", "product", "origin", "category", "aoh_ng_g",
                    "ame_ng_g", "total_ng_g"])
        for r in sorted(s1 + s2, key=lambda x: (x["file"], x["sample"])):
            w.writerow([r["file"], r["sample"], r["plan"], r["product"], r["origin"],
                        r["category"], repr(r["aoh"]), repr(r["ame"]), repr(r["total"])])
    result = {"study": "alternaria", "version": VERSION, "predictions": preds,
              "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "alternaria_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the alternaria 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    loaded = {}
    for spec in (F1, F2):
        raw, source = load(spec, args.data_dir)
        text, enc = decode(raw)
        samples, census = parse_text(text, spec["key"])
        loaded[spec["key"]] = (raw, source, enc, samples, census)
    raw1, src1, enc1, smp1, c1 = loaded["F1"]
    raw2, src2, enc2, smp2, c2 = loaded["F2"]
    gate_obs = gate_checks(c1, c2, _sha(raw1) == F1["sha256"], _sha(raw2) == F2["sha256"])
    s1, s2 = list(smp1.values()), list(smp2.values())
    a = analyse(s1, s2)
    preds = grade(a, gate_obs)
    provenance = {
        "F1": {"resource": F1["resource"], "sha256": F1["sha256"], "bytes": len(raw1),
               "source": src1, "encoding": enc1},
        "F2": {"resource": F2["resource"], "sha256": F2["sha256"], "bytes": len(raw2),
               "source": src2, "encoding": enc2},
    }
    result = write_outputs(args.out_dir, s1, s2, {"F1": c1, "F2": c2}, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate_obs,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
