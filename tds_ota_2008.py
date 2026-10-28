#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""tds-ota-2008 0.1.0: Health Canada's open Total Diet Study ochratoxin A file (2008-09) against
the paper that reports it, Tam et al. 2011 (Food Addit Contam A 28(6):754-761, PMC3118520).

Grades docs/tds-ota-2008-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

The paper reports ochratoxin A (OTA) in 140 Total Diet Study composites, 70 foods bought in
Quebec City (2008) and the same 70 in Calgary (2009). Its Table 3 prints one value per food and
year (or "n.d."), with one LOD and LOQ per food. Its text says 51 of 70 composites had OTA above
the LOD in each year (102/140 in the abstract) and 47 and 43 above the LOQ. Table 3 itself has 49
and 46 entries that are not "n.d." (95 of 140) and 47 and 43 values above the printed LOQ.

The open file (open.canada.ca dataset 71fa9c90-..., Open Government Licence - Canada) is in the
CANLINE layout: "Result Operator" is "=", "<LOD/MDL" or "ND", and "Result Value" is 0 for a
below-limit result. A names-only census (job tds-ota-census-v1) found 137 composites, not 140:
Quebec City lacks the baby-food mixed vegetables and Calgary lacks beer and wine. This compares
the file with Table 3 row by row for the first time: detection pattern, values at the printed
precision, the text's counts and maxima, units, the English/French copies, the top 20 and the
year-to-year ranking.

Both files are SHA-256 pinned. Standard library only. Code Apache-2.0; derived data CC BY 4.0.
Not a compliance finding, not about any brand, and not individual dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import sys
import time
import unicodedata
import urllib.request

VERSION = "0.1.0"
DATASET = "71fa9c90-f690-4928-9239-69b4ecbeccee"
EN = {
    "key": "EN", "resource": "d1cbf697-ff08-4518-b69f-b633efbfb620",
    "filename": "total-diet-study-mycotoxin-results-2008-2009.csv",
    "sha256": "3d80ade4162746fc4afac633951eead03b79a9b77a0bd37500fff7ffc06aaf79",
}
FR = {
    "key": "FR", "resource": "237fe2c2-2f86-4ef4-b11d-485a28f8a57a",
    "filename": ("les-resultats-des-mycotoxines-de-letude-canadienne-sur-lalimentation-totale-"
                 "2008-2009.csv"),
    "sha256": "6fd5a22576fb0d1509712ecb92a6fa477c767ce5097d22e8965ab1fb59cda171",
}

# Tam et al. 2011, Table 3: code -> (food, Quebec City 2008, Calgary 2009, LOD, LOQ, ng/ml?).
# Values as printed (ng/g, or ng/ml where starred); "nd" = n.d. Results corrected for recovery.
ND = "nd"
TABLE3 = {
    "KK01": ("Alcoholic drinks, beer", "0.04", "0.01", 0.002, 0.005, True),
    "KK02": ("Alcoholic drinks, wine", "0.02", ND, 0.002, 0.005, True),
    "GG01": ("Baked beans, canned", "0.01", ND, 0.003, 0.009, False),
    "GG02": ("Beans, string", "0.53", ND, 0.002, 0.006, False),
    "HH05": ("Blueberries", ND, ND, 0.002, 0.005, False),
    "FF21": ("Bread, other", "0.45", "0.42", 0.002, 0.006, False),
    "FF03": ("Bread, rye", "1.0", "0.57", 0.003, 0.009, False),
    "FF01": ("Bread, white", "0.77", "0.67", 0.003, 0.010, False),
    "FF02": ("Bread, whole wheat", "1.3", "0.83", 0.004, 0.012, False),
    "FF20": ("Buns and rolls", "1.0", "1.2", 0.003, 0.011, False),
    "FF04": ("Cake", "0.07", "0.04", 0.002, 0.005, False),
    "JJ02": ("Candy", "0.01", ND, 0.003, 0.010, False),
    "FF05": ("Cereals, cooked wheat", "0.04", "0.01", 0.002, 0.009, False),
    "FF06": ("Cereals, corn", "0.01", "0.01", 0.003, 0.010, False),
    "LL01": ("Cereals, mixed", "0.43", "0.01", 0.003, 0.010, False),
    "FF07": ("Cereals, oatmeal", "0.11", "0.11", 0.003, 0.009, False),
    "FF08": ("Cereals, rice and bran", "0.27", "0.26", 0.004, 0.011, False),
    "AA09": ("Cheese", ND, ND, 0.008, 0.025, False),
    "AA11": ("Cheese, processed", ND, ND, 0.006, 0.019, False),
    "NN04": ("Chicken burger", "0.32", "0.23", 0.003, 0.010, False),
    "NN06": ("Chicken nuggets", "0.09", "0.04", 0.003, 0.010, False),
    "JJ01": ("Chocolate bars", "0.30", "0.13", 0.003, 0.009, False),
    "KK04": ("Coffee", "0.02", "0.01", 0.002, 0.008, True),
    "FF09": ("Cookies", "0.21", "0.20", 0.003, 0.008, False),
    "GG27": ("Corn chips", "0.03", ND, 0.003, 0.008, False),
    "FF10": ("Crackers", "0.44", "0.03", 0.003, 0.010, False),
    "FF11": ("Danish, donuts and croissants", "0.24", "0.35", 0.003, 0.008, False),
    "LL02": ("Desserts", ND, ND, 0.006, 0.021, False),
    "LL03": ("Dinners, cereal plus vegetable plus meat", ND, "0.01", 0.002, 0.008, False),
    "CC01": ("Eggs", ND, ND, 0.005, 0.017, False),
    "FF12": ("Flour, white (wheat)", "0.39", "1.7", 0.004, 0.014, False),
    "LL05": ("Formulae, milk base", ND, ND, 0.005, 0.017, True),
    "LL06": ("Formulae, soya base", "0.01", "0.02", 0.002, 0.006, False),
    "MM02": ("Frozen entrees", "0.06", "0.05", 0.002, 0.006, False),
    "HH10": ("Grape juice, bottled", ND, ND, 0.002, 0.006, True),
    "HH11": ("Grapes", ND, ND, 0.002, 0.007, False),
    "NN03": ("Hamburger", "0.44", "0.22", 0.001, 0.003, False),
    "PP06": ("Herbs and spices", "0.08", "0.07", 0.006, 0.021, False),
    "NN05": ("Hot dogs", "0.38", "0.41", 0.004, 0.012, False),
    "AA07": ("Ice cream", "0.02", "0.03", 0.002, 0.007, True),
    "BB07": ("Lamb", ND, ND, 0.004, 0.012, False),
    "BB09": ("Luncheon meats, canned", "0.01", "0.01", 0.002, 0.008, False),
    "LL08": ("Meat, poultry or eggs", ND, ND, 0.002, 0.007, False),
    "AA02": ("Milk, 2%", ND, ND, 0.002, 0.007, True),
    "AA13": ("Milk, chocolate, 1%", "0.02", "0.01", 0.002, 0.006, True),
    "FF13": ("Muffins", "0.20", "0.19", 0.002, 0.007, False),
    "JJ12": ("Nuts", "0.02", "0.03", 0.002, 0.007, False),
    "BB10": ("Organ meats", ND, "0.01", 0.004, 0.015, False),
    "FF14": ("Pancakes and waffles", "0.10", "0.16", 0.003, 0.009, False),
    "FF15": ("Pasta, mixed dishes", "0.13", "0.07", 0.002, 0.005, False),
    "FF16": ("Pasta, plain", "0.34", "0.07", 0.002, 0.005, False),
    "JJ07": ("Peanut butter", "0.04", ND, 0.002, 0.007, False),
    "GG14": ("Peas", ND, ND, 0.003, 0.010, False),
    "FF17": ("Pie, apple", "0.11", "0.13", 0.002, 0.006, False),
    "FF18": ("Pie, other", "0.11", "0.09", 0.001, 0.005, False),
    "NN01": ("Pizza", "0.21", "0.22", 0.002, 0.007, False),
    "MM01": ("Popcorn, microwave", ND, ND, 0.002, 0.007, False),
    "BB05": ("Pork, cured", "0.06", "0.20", 0.003, 0.012, False),
    "BB04": ("Pork, fresh", "0.03", "0.23", 0.004, 0.011, False),
    "JJ08": ("Puddings", "0.03", "0.02", 0.002, 0.005, False),
    "HH17": ("Raisins", "2.3", "0.17", 0.004, 0.013, False),
    "FF19": ("Rice", ND, ND, 0.001, 0.004, False),
    "JJ11": ("Seeds, shelled", "0.07", "0.35", 0.003, 0.008, False),
    "KK07": ("Soy beverage, fortified", "0.05", "0.02", 0.002, 0.006, True),
    "PP07": ("Soya sauce", ND, ND, 0.002, 0.007, True),
    "KK06": ("Tea", ND, ND, 0.002, 0.007, True),
    "PP05": ("Vanilla extract", ND, "0.02", 0.002, 0.006, True),
    "BB06": ("Veal, cutlets", ND, ND, 0.004, 0.012, False),
    "LL09": ("Vegetables, peas", ND, ND, 0.003, 0.008, False),
    "BB11": ("Wieners and sausages", "0.12", "0.06", 0.002, 0.007, False),
}
YEAR_INDEX = {"2008": 1, "2009": 2}
CITY_YEAR = {"Quebec City": "2008", "Calgary": "2009"}

# File "Food Name" (census labels) -> Table 3 code. Registered before any result was read.
# The one judgement call: "Bologna, Chicken" is taken as BB05 "Pork, cured" (the only meat row
# left once the other six are paired by name).
FILE_TO_CODE = {
    "Baby Food, Dinners Cereal, Vegetable, Meat": "LL03",
    "Baby Food, Dinners, Meat Or Poultry Or Eggs": "LL08",
    "Beans, Baked, canned": "GG01",
    "Beans, String": "GG02",
    "Beer & Malt": "KK01",
    "Bologna, Chicken": "BB05",
    "Bread": "FF21",
    "Bread, Rye": "FF03",
    "Bread, White": "FF01",
    "Bread, Whole Wheat": "FF02",
    "Buns & Rolls": "FF20",
    "Cake": "FF04",
    "Canned Luncheon Meat": "BB09",
    "Cereal, Rice, Bran": "FF08",
    "Cheese, Hard": "AA09",
    "Cheese, Processed": "AA11",
    "Chocolate Candy Bars": "JJ01",
    "Chocolate Milk 1%": "AA13",
    "Coffee, Roast & Ground": "KK04",
    "Cold Cereals, Corn Based": "FF06",
    "Cold Cereals, Oat Based": "FF07",
    "Cookies": "FF09",
    "Crackers, other": "FF10",
    "Danish, Donuts, Croissants": "FF11",
    "Dessert, Baby Food": "LL02",
    "Dinners, Frozen Entrées": "MM02",
    "Eggs, fresh": "CC01",
    "Fast Food, Chicken Burgers": "NN04",
    "Fast Food, Chicken Nuggets": "NN06",
    "Fast Food, Hamburgers": "NN03",
    "Fast Food, Hot Dogs": "NN05",
    "Fast Food, Pizza": "NN01",
    "Flour, white (wheat)": "FF12",
    "Fruits, Blueberries": "HH05",
    "Fruits, Grapes, Green & White Seedless": "HH11",
    "Fruits, Raisins, Semi-Moist": "HH17",
    "Herbs & Spices Mixed": "PP06",
    "Hot Cereals, Wheat-Based": "FF05",
    "Ice Cream": "AA07",
    "Infant Formula, Ready To Use, Milk, 0-12": "LL05",
    "Infant Formula, Ready To Use, Soy, 0-12": "LL06",
    "Infant cereals, Mixed Grain Base": "LL01",
    "Juice, Grape": "HH10",
    "Lamb, Ground": "BB07",
    "Milk, 2%": "AA02",
    "Mixed Vegetable, Baby Food": "LL09",
    "Mixes, Pancake & Waffle": "FF14",
    "Muffins, Regular": "FF13",
    "Organ Meat": "BB10",
    "Pasta, Mixed Dishes": "FF15",
    "Pasta, Plain": "FF16",
    "Peanut Butter": "JJ07",
    "Peas, Green": "GG14",
    "Penny Candy": "JJ02",
    "Pie, Other": "FF18",
    "Pies, apple": "FF17",
    "Pork Ground, other": "BB04",
    "Pudding": "JJ08",
    "Snack Food, Corn Chips": "GG27",
    "Snack Foods, Mixed Nuts": "JJ12",
    "Snack Foods, Popcorn, Microwave": "MM01",
    "Snack Foods, Seeds, Shelled": "JJ11",
    "Soya Beverage, fortified": "KK07",
    "Soya Sauce": "PP07",
    "Tea": "KK06",
    "Vanilla": "PP05",
    "Veal Cutlets, Bone-In": "BB06",
    "White Rice (Long, Med, Short Grain)": "FF19",
    "Wieners": "BB11",
    "Wine, Other": "KK02",
}

# Census facts (job tds-ota-census-v1, 2026-10-28).
N_ROWS = 137
CITY_ROWS = {"Quebec City": 69, "Calgary": 68}
UNIT_ROWS = {"ng/g": 113, "ng/ml": 24}
MISSING = {("LL09", "2008"), ("KK01", "2009"), ("KK02", "2009")}
EXPECTED_PAIRS = {(c, y) for c in TABLE3 for y in YEAR_INDEX} - MISSING
EQ, BELOW = "=", ("<LOD/MDL", "ND")

# Registered thresholds.
C3_MAX = {"2008": ("HH17", "2.3"), "2009": ("FF12", "1.7")}
C4_DET = {"2008": 51, "2009": 51}
C5_LOQ = {"2008": 47, "2009": 43}
P1_DET = {"2008": 49, "2009": 45}
P2_EXTRA = {"LL06"}
P4_MIN = 16
P5_MIN = 0.7
CEREAL = {c for c in TABLE3 if c.startswith("FF")} | {"LL01", "LL03", "NN01", "NN03", "NN04",
                                                      "NN05", "NN06"}
# Reference only (not graded): EU Regulation 2023/915 OTA levels, ug/kg, for the rows they fit.
EU_REF = {"HH17": 8.0, "KK02": 2.0, "HH10": 2.0, "LL01": 0.5, "LL02": 0.5, "LL03": 0.5,
          "LL08": 0.5, "LL09": 0.5, **{c: 3.0 for c in TABLE3 if c.startswith("FF")}}


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def clean(cell):
    return (cell or "").replace("﻿", "").strip()


def key(name):
    """Food-name key: accents stripped (NFKD), then ASCII letters and digits only, lower case."""
    flat = unicodedata.normalize("NFKD", name.lower())
    return "".join(ch for ch in flat if ch.isascii() and ch.isalnum())


CODE_BY_KEY = {key(k): v for k, v in FILE_TO_CODE.items()}


def number(raw):
    """A cell as a float, reading one decimal comma as a point; None if not a finite number."""
    s = (raw or "").strip()
    if not s:
        return None
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def parse_result(op, raw):
    """(value, kind): '=' with a number above 0 is 'det'; a below-limit operator with 0 is
    'below'; anything else is 'bad' (fails the gate)."""
    v = number(raw)
    if op == EQ and v is not None and v > 0:
        return v, "det"
    if op in BELOW and v == 0:
        return 0.0, "below"
    return None, "bad"


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def table3(code, year):
    return TABLE3[code][YEAR_INDEX[year]]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def top20(pairs):
    """pairs: {code: (v2008, v2009)} -> the 20 codes with the highest two-year mean."""
    return sorted(pairs, key=lambda c: (-(pairs[c][0] + pairs[c][1]) / 2, c))[:20]


def find_columns(header):
    h = [clean(c) for c in header]

    def first(name):
        if name not in h:
            raise ValueError(f"no {name!r} column in {header!r}")
        return h.index(name)

    return {"food": first("Food Name"), "sample": first("Sample Code"),
            "city": first("Sampling Location City Name"), "op": first("Result Operator"),
            "value": first("Result Value"), "unit": first("Units of measurement"),
            "analyte": first("Analyte Name"), "lod": first("LOD"), "loq": first("LOQ")}


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def read_table(text):
    table = list(csv.reader(io.StringIO(text)))
    return table[0], [r for r in table[1:] if any(c.strip() for c in r)]


def parse_text(text):
    """(records, census, columns) from the decoded English CSV."""
    header, body = read_table(text)
    col = find_columns(header)

    def cell(r, k):
        i = col[k]
        return clean(r[i]) if i < len(r) else ""

    recs, census = [], {"n_rows": len(body), "cities": {}, "units": {}, "analytes": {},
                        "operators": {}, "kinds": {}, "unmapped_foods": [], "samples": {}}
    for r in body:
        food, city, op = cell(r, "food"), cell(r, "city"), cell(r, "op")
        value, kind = parse_result(op, cell(r, "value"))
        code = CODE_BY_KEY.get(key(food))
        if code is None and food not in census["unmapped_foods"]:
            census["unmapped_foods"].append(food)
        rec = {"sample": cell(r, "sample"), "food": food, "code": code, "city": city,
               "year": CITY_YEAR.get(city), "op": op, "raw": cell(r, "value"), "kind": kind,
               "value": value if value is not None else 0.0, "unit": cell(r, "unit"),
               "lod": number(cell(r, "lod")), "loq": number(cell(r, "loq"))}
        recs.append(rec)
        for k, v in (("cities", city), ("units", rec["unit"]), ("analytes", cell(r, "analyte")),
                     ("operators", op), ("kinds", kind), ("samples", rec["sample"])):
            _bump(census[k], v)
    per = {}
    for n in census.pop("samples").values():
        _bump(per, str(n))
    census["distinct_samples"] = sum(per.values())
    census["rows_per_sample"] = per
    census["pairs"] = sorted({(r["code"], r["year"]) for r in recs if r["code"] and r["year"]})
    census["distinct_pairs"] = len(census["pairs"])
    return recs, census, col


def compare_fr(recs, fr_text, col):
    """Pair English and French rows by sample code; compare operator class and value."""
    _, body = read_table(fr_text)
    fr = {}
    for r in body:
        sid = clean(r[col["sample"]]) if col["sample"] < len(r) else ""
        fr.setdefault(sid, []).append(r)
    out = {"paired": 0, "unpaired_en": [], "duplicate_fr": 0, "op_disagree": [],
           "value_disagree": [], "n_fr_rows": len(body)}
    for rec in recs:
        rows = fr.get(rec["sample"], [])
        if not rows:
            out["unpaired_en"].append(rec["sample"])
            continue
        if len(rows) > 1:
            out["duplicate_fr"] += 1
            continue
        out["paired"] += 1
        r = rows[0]
        op = clean(r[col["op"]]) if col["op"] < len(r) else ""
        v = number(r[col["value"]] if col["value"] < len(r) else "")
        if (op == EQ) != (rec["op"] == EQ):
            out["op_disagree"].append(rec["sample"])
        if v is None or abs(v - rec["value"]) > 1e-9:
            out["value_disagree"].append(rec["sample"])
    out["all_agree"] = (out["paired"] == len(recs) == out["n_fr_rows"]
                        and not out["op_disagree"] and not out["value_disagree"])
    return out


# ---------------------------------------------------------------------------
# Gate, analysis and grading.
# ---------------------------------------------------------------------------
def gate_checks(census, sha_ok):
    return {
        "sha256": bool(sha_ok),
        "rows": census["n_rows"] == N_ROWS,
        "samples": census["rows_per_sample"] == {"1": N_ROWS},
        "cities": census["cities"] == CITY_ROWS,
        "foods_mapped": not census["unmapped_foods"],
        "pairs": (set(map(tuple, census["pairs"])) == EXPECTED_PAIRS
                  and census["distinct_pairs"] == census["n_rows"]),
        "analyte": census["analytes"] == {"Ochratoxin A": N_ROWS},
        "units": census["units"] == UNIT_ROWS,
        "results": set(census["kinds"]) == {"det", "below"},
    }


def analyse(recs):
    ok = [r for r in recs if r["code"] and r["year"]]
    c1_bad, c2_bad, c2_n = [], [], 0
    for r in ok:
        printed = table3(r["code"], r["year"])
        if (r["kind"] == "det") != (printed != ND):
            c1_bad.append({"sample": r["sample"], "code": r["code"], "year": r["year"],
                           "file": r["raw"], "op": r["op"], "table3": printed})
        elif r["kind"] == "det":
            c2_n += 1
            if not matches(r["value"], printed):
                c2_bad.append({"sample": r["sample"], "code": r["code"], "year": r["year"],
                               "file": r["value"], "table3": printed})
    det, above_loq, above_paper_loq, maxima = {}, {}, {}, {}
    for y in YEAR_INDEX:
        rs = [r for r in ok if r["year"] == y]
        d = [r for r in rs if r["kind"] == "det"]
        det[y] = len(d)
        above_loq[y] = sum(1 for r in d if r["loq"] is not None and r["value"] > r["loq"] + 1e-12)
        above_paper_loq[y] = sum(1 for r in d if r["value"] > TABLE3[r["code"]][4] + 1e-12)
        top = max(d, key=lambda r: r["value"]) if d else None
        maxima[y] = {"code": top["code"], "food": top["food"], "value": top["value"]} if top else None
    ng_ml = sorted({(r["code"], r["year"]) for r in ok if r["unit"] == "ng/ml"})
    expected_ml = sorted({(r["code"], r["year"]) for r in ok
                          if TABLE3[r["code"]][5] or r["code"] in P2_EXTRA})
    by = {}
    for r in ok:
        by.setdefault(r["code"], {})[r["year"]] = r["value"]
    pairs = {c: (v["2008"], v["2009"]) for c, v in by.items() if len(v) == 2}
    top = top20(pairs)
    codes = sorted(pairs)
    rho = spearman([pairs[c][0] for c in codes], [pairs[c][1] for c in codes])
    eu_over = sorted({(r["code"], r["year"]) for r in ok if r["code"] in EU_REF
                      and r["value"] > EU_REF[r["code"]] + 1e-9})
    lods = {}
    for r in ok:
        _bump(lods, "missing" if r["lod"] is None else
              ("in 0.001-0.008" if 0.001 - 1e-12 <= r["lod"] <= 0.008 + 1e-12 else "outside"))
    return {
        "c1_mismatch": c1_bad, "c2_checked": c2_n, "c2_mismatch": c2_bad,
        "detected": det, "above_file_loq": above_loq, "above_paper_loq": above_paper_loq,
        "maxima": maxima, "ng_ml": ng_ml, "expected_ng_ml": expected_ml,
        "n_shared_foods": len(pairs), "top20": [{"code": c, "food": TABLE3[c][0],
                                                 "y2008": pairs[c][0], "y2009": pairs[c][1],
                                                 "cereal": c in CEREAL} for c in top],
        "top20_cereal": sum(1 for c in top if c in CEREAL),
        "spearman_2008_2009": rho, "eu_reference_over": eu_over, "lod_vs_paper_range": lods,
    }


def grade(a, gate_obs, enfr):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "SHA-256; 137 rows, one per sample; 69 Quebec City and 68 Calgary rows; every "
                      "food name mapped to Table 3 and the 137 food-year pairs as in the census; "
                      "one analyte; units ng/g 113 and ng/ml 24; every result '=' with a number "
                      "above 0 or a below-limit operator with 0, both present"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    mx = a["maxima"]
    add("C1", "consistency", "Table 3: each file row is detected exactly when Table 3 prints a "
        "value (not n.d.) for that food and year", {"mismatch": a["c1_mismatch"]},
        not a["c1_mismatch"])
    add("C2", "consistency", "Table 3: every detected value rounds to Table 3's figure at its "
        "printed precision", {"checked": a["c2_checked"], "mismatch": a["c2_mismatch"]},
        not a["c2_mismatch"])
    add("C3", "consistency", "the text: the highest value is raisins at 2.3 ng/g in 2008 (Quebec "
        "City) and white wheat flour at 1.7 ng/g in 2009 (Calgary)", {"maxima": mx},
        all(mx.get(y) and mx[y]["code"] == c and matches(mx[y]["value"], p)
            for y, (c, p) in C3_MAX.items()))
    add("C4", "consistency", "the text: 51 composites above the LOD in each year (102/140)",
        {"detected": a["detected"]}, a["detected"] == C4_DET)
    add("C5", "consistency", "the text: 47 (2008) and 43 (2009) composites above the LOQ, using "
        "the file's own LOQ for each row", {"above_file_loq": a["above_file_loq"],
                                            "above_paper_loq": a["above_paper_loq"]},
        a["above_file_loq"] == C5_LOQ)
    add("P1", "prediction", "the file follows Table 3, not the text: 49 of 69 Quebec City and 45 "
        "of 68 Calgary rows detected", {"detected": a["detected"]}, a["detected"] == P1_DET)
    add("P2", "prediction", "the ng/ml rows are exactly Table 3's starred foods plus the soy "
        "infant formula", {"ng_ml": a["ng_ml"], "expected": a["expected_ng_ml"]},
        a["ng_ml"] == a["expected_ng_ml"])
    add("P3", "prediction", "the English and French files agree: all 137 rows pair by sample "
        "code, with the same operator class and value", enfr,
        bool(enfr) and enfr.get("all_agree") is True)
    add("P4", "prediction", "at least 16 of the top 20 foods by two-year mean are "
        "cereal-containing (the paper's Table 4: 16/20)", {"top20_cereal": a["top20_cereal"]},
        a["top20_cereal"] >= P4_MIN)
    add("P5", "prediction", "food rankings hold across city-years: Spearman rho between the 2008 "
        "and 2009 values of the foods in both cities is at least 0.7",
        {"rho": a["spearman_2008_2009"], "n": a["n_shared_foods"]},
        a["spearman_2008_2009"] is not None and a["spearman_2008_2009"] >= P5_MIN)
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
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-tds-ota-2008"})
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
    base = f"/data/dataset/{DATASET}/resource/{spec['resource']}/download/{spec['filename']}"
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
    if isinstance(x, (set, tuple)):
        return sorted(x) if isinstance(x, set) else list(x)
    return "" if x is None else (round(x, 6) if isinstance(x, float) else x)


def write_outputs(out_dir, recs, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "tds_ota_2008_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "food", "code", "city", "year", "operator", "value_raw", "kind",
                    "value", "unit", "lod", "loq", "table3"])
        for r in sorted(recs, key=lambda x: (x["code"] or "", x["year"] or "", x["sample"])):
            t3 = table3(r["code"], r["year"]) if r["code"] and r["year"] else ""
            w.writerow([r["sample"], r["food"], r["code"] or "", r["city"], r["year"] or "",
                        r["op"], r["raw"], r["kind"], repr(r["value"]), r["unit"],
                        "" if r["lod"] is None else repr(r["lod"]),
                        "" if r["loq"] is None else repr(r["loq"]), t3])
    result = {"study": "tds-ota-2008", "version": VERSION, "predictions": preds,
              "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "tds_ota_2008_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the tds-ota-2008 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw, src = load(EN, args.data_dir)
    text, enc = decode(raw)
    recs, census, col = parse_text(text)
    gate_obs = gate_checks(census, _sha(raw) == EN["sha256"])
    provenance = {"EN": {"resource": EN["resource"], "sha256": EN["sha256"], "bytes": len(raw),
                         "source": src, "encoding": enc}}
    try:
        fr_raw, fr_src = load(FR, args.data_dir)
        fr_text, fr_enc = decode(fr_raw)
        enfr = compare_fr(recs, fr_text, col)
        provenance["FR"] = {"resource": FR["resource"], "sha256": FR["sha256"],
                            "bytes": len(fr_raw), "source": fr_src, "encoding": fr_enc}
    except Exception as exc:  # noqa: BLE001 - P3 then fails, with the reason recorded
        enfr = {"error": str(exc)}
    a = analyse(recs)
    preds = grade(a, gate_obs, enfr)
    result = write_outputs(args.out_dir, recs, census, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate_obs, "units": census["units"],
                      "operators": census["operators"],
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
