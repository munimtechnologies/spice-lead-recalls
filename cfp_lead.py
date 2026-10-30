#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""cfp-lead 0.1.0: lead in six open CFIA Children's Food Project files (2017 to 2022) against every
lead figure CFIA printed for them, and against the U.S. FDA's 2025 action levels for baby food.

Grades docs/cfp-lead-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes one per-sample CSV per Children's Food Project
(CFP) year on open.canada.ca (Open Government Licence - Canada), and a report page with a lead
table (tested / negative / positive / minimum / maximum / mean, in ppm). A names-only census of all
16 files (job cfp-metals-census-v1, 2026-10-30) gave each year's lead rows, product labels and
units. Each year is gated on those census facts and a value rule fixed before any lead value was
read; only years that pass are graded. Files are SHA-256 pinned. Standard library only.
Code Apache-2.0; derived data CC BY 4.0. Not a compliance finding, not about any brand, and not
individual dietary or medical advice.
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
YEARS = ("2017", "2018", "2019", "2020", "2021", "2022")

# label -> (dataset, resource, download path, SHA-256), from job cfp-metals-census-v1.
FILES = {
    "2017": ("61a82716-e863-4c20-b1a7-c8e05e70e72d", "3e34dce9-2844-4cc4-8e06-05c45830509c",
             "cfia-acia-1142_2017_fssd_chem_childrens-food-project_projet-sur-les-aliments-"
             "destines-aux-enfant.csv",
             "6fe317c9f791d0e4a893fff2449e2d2fc9c00e90dd77d3df10b285fc5f4c87e7"),
    "2018": ("66c8ff38-27e8-4e1a-9270-ebbdede8a2e6", "3ab80a87-25a7-4aea-b510-0301c1232081",
             "cfia_acia-15022622-v2-cfp-2018-fssd-chem-open-data.csv",
             "be6a1d7c1648570f18266af0e31eefc7d4791cfbb82e4f3add45bf0bb4659755"),
    "2019": ("f60b2eb1-7f25-4c4e-af3f-d3f47928085f", "50fcc8c9-6a62-49d6-92ea-b8a1c8c787c2",
             "cfia-acia-1211-childrens-food-project-projet-sur-les-aliments-destines-aux-enfant_"
             "2019_fssd.csv",
             "6b5b7019494ec36bba593f3e560cab29a38a93c060f9278fd86e73fac94cbce2"),
    "2020": ("b1974f49-da37-4783-8705-97bfe6720a2c", "feebccc6-1eaf-4a5b-83e7-a3b468a912b8",
             "cfia_acia-1264-v1-cfp2020_open_data.csv",
             "e1c895c55ae52386cdd43898afc236a92086affb6409cd272e7604291eb27b46"),
    "2021": ("7b3277b0-739e-4809-9d39-cfc290113d5a", "ba052b71-9000-4fc1-8eb8-de693bb1e606",
             "cfp-pae-2021.csv",
             "5364b9cd385d25428868c3f1354d6f1d5eccf5e4f58a3143e263c10aa7f1c544"),
    "2022": ("11fedc77-176a-4af0-9ddc-1bfa8ae1a894", "517c84f1-d317-4566-b118-b17359919f1f",
             "cfp-pae-2022.csv",
             "14d3712ee0d4b9fcfaefe940670b1f7b352c5c9b249f25190f2cf725eb851c61"),
}

MICRO_G = "µg/g"        # micro sign + g/g (= ppm)
# Census facts (job cfp-metals-census-v1): lead rows per product label. Every year has one lead
# row per sample and the single unit ug/g (= ppm).
PRODUCTS = {
    "2017": {"Juice - Toddler/Infant": 51},
    "2018": {"Infant Formula - Dairy": 52, "Infant Food - Puree": 38, "Pasta - Dry": 19,
             "Pasta - Canned": 16, "Meal - Toddler/Baby": 11, "Infant Formula - Soy": 7},
    "2019": {"Infant Food - Puree": 98, "Infant Food - Snack": 78, "Infant Food - Cereal": 48,
             "Yogurt": 16, "Beverage - Yogurt": 11},
    "2020": {"Cereal - Children": 48, "Pudding": 36, "Granola/Cereal Bar": 29,
             "Fruit Snacks": 16, "Raisin": 4, "Oatmeal": 2},
    "2021": {"Infant Food - Puree": 159, "Pasta - Dry": 36, "Juice - Blend": 28,
             "Beverage - Fruit": 15, "Juice - Apple": 12, "Fruit Purée": 11,
             "Pasta - Canned": 11, "Juice - Orange": 7, "Meal - Toddler/Baby": 5,
             "Fruit & Vegetable Purée": 2, "Juice - Other": 2, "Juice - Cranberry": 1,
             "Juice - Grape": 1, "Juice - Pineapple": 1},
    "2022": {"Infant Food - Cereal": 39, "Crackers": 25, "Cookies": 23, "Infant Food - Snack": 14,
             "Granola/Cereal Bar": 5, "Baking Mixes": 2},
}

# Product label -> the report table's product type (fixed from the census counts, before any
# value was read). 2021's report splits 177 samples into 124 purees and 53 meals, but the file
# labels only 5 as meals, so the two are graded together as "puree-meal".
CATEGORY = {
    "2017": {"Juice - Toddler/Infant": "juice"},
    "2018": {"Infant Formula - Dairy": "formula-dairy", "Infant Food - Puree": "puree",
             "Pasta - Dry": "pasta", "Pasta - Canned": "pasta", "Meal - Toddler/Baby": "meal",
             "Infant Formula - Soy": "formula-soy"},
    "2019": {"Infant Food - Puree": "puree", "Infant Food - Snack": "snack",
             "Infant Food - Cereal": "infant-cereal", "Yogurt": "yogurt",
             "Beverage - Yogurt": "yogurt-beverage"},
    "2020": {"Cereal - Children": "children-cereal", "Oatmeal": "children-cereal",
             "Pudding": "pudding", "Granola/Cereal Bar": "granola-bar",
             "Fruit Snacks": "fruit-snack", "Raisin": "fruit-snack"},
    "2021": {"Infant Food - Puree": "puree-meal", "Fruit Purée": "puree-meal",
             "Fruit & Vegetable Purée": "puree-meal", "Meal - Toddler/Baby": "puree-meal",
             "Pasta - Dry": "pasta", "Pasta - Canned": "pasta", "Juice - Blend": "juice",
             "Beverage - Fruit": "juice", "Juice - Apple": "juice", "Juice - Orange": "juice",
             "Juice - Other": "juice", "Juice - Cranberry": "juice", "Juice - Grape": "juice",
             "Juice - Pineapple": "juice"},
    "2022": {"Infant Food - Cereal": "infant-cereal", "Crackers": "snack", "Cookies": "snack",
             "Infant Food - Snack": "snack", "Granola/Cereal Bar": "snack",
             "Baking Mixes": "snack"},
}

# Printed lead tables (CFIA report pages, re-read 2026-10-30): category -> (tested, negative,
# positive, maximum, mean). Figures are strings so their printed precision is kept.
TABLE = {
    "2017": {"juice": (51, 49, 2, "0.009", "0.000")},
    "2018": {"puree": (38, 38, 0, None, None), "formula-dairy": (52, 49, 3, "0.019", "0.02"),
             "formula-soy": (7, 7, 0, None, None), "meal": (11, 11, 0, None, None),
             "pasta": (35, 34, 1, "0.03", "0.03")},
    "2019": {"yogurt-beverage": (11, 11, 0, None, None),
             "infant-cereal": (48, 37, 11, "0.093", "0.01"),
             "puree": (98, 97, 1, "0.015", "0.0002"), "snack": (78, 71, 7, "0.04", "0.0025"),
             "yogurt": (16, 16, 0, None, None)},
    "2020": {"children-cereal": (50, 47, 3, "0.10", "0.003"),
             "fruit-snack": (20, 19, 1, "0.03", "0.001"),
             "granola-bar": (29, 28, 1, "0.03", "0.001"), "pudding": (36, 36, 0, None, None)},
    # puree (124/123/1, max 0.02) + meals (53/51/2, max 0.18) combined; maxima graded in P1/P2.
    "2021": {"puree-meal": (177, 174, 3, None, None), "pasta": (47, 44, 3, "0.05", "0.002"),
             "juice": (67, 67, 0, None, None)},
    "2022": {"infant-cereal": (39, 16, 23, "0.0211", "0.0089"),
             "snack": (69, 28, 41, "0.196", "0.0152")},
}
MIN_2022 = "0.0050"          # 2022: "Minimum detected amount" for both rows
# Printed text figures.
TEXT = {
    "2018": {"formula_n": 59, "formula_det": 3, "formula_range": ("0.016", "0.019")},
    "2019": {"det": 19, "n": 251},
    "2020": {"nd": 130, "n": 135},
    "2021": {"nd": 285, "n": 291, "range": ("0.015", "0.047"), "max_category": "pasta"},
    "2022": {"nd": 44, "n": 108, "range": ("0.0050", "0.196"), "max_product": "Crackers"},
}
# P5: which mean reproduces each printed mean ("all" = over all samples, "positives" = over
# detected samples only). 2017's table note says positives only; we predict all-sample.
MEAN_RULE = {"2017": "all", "2018": "positives", "2019": "all", "2020": "all", "2021": "all",
             "2022": "positives"}
# FDA, Action Levels for Lead in Processed Food Intended for Babies and Young Children (final
# guidance, January 2025), in ppm: 0.010 for fruits, vegetables (not single-ingredient root
# vegetables), mixtures, yogurts, custards/puddings and single-ingredient meats; 0.020 for
# single-ingredient root vegetables and dry infant cereals. Snacks, formula and juice excluded.
FDA = (("2018", "puree", 0.010), ("2018", "meal", 0.010), ("2019", "puree", 0.010),
       ("2019", "infant-cereal", 0.020), ("2019", "yogurt", 0.010), ("2020", "pudding", 0.010),
       ("2021", "puree-meal", 0.010), ("2022", "infant-cereal", 0.020))
P3_YEARS = ("2018", "2019", "2020", "2021")
P3_FLOOR = 0.010
P4_MIN_2019 = 6
P4_RANGE_2022 = (1, 3)
P6_CUT = 0.015
COLS = ("sample", "component", "value", "unit", "product")


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def clean(cell):
    """A cell without BOM or edge spaces, in NFC form (so 'Purée' compares equal however the
    file composed its accent)."""
    return unicodedata.normalize("NFC", (cell or "").replace("﻿", "")).strip()


def head(name):
    """Normalised English part of a header cell: 'Component/Composante' -> 'component'."""
    h = clean(name).strip('"').lower().replace("_", " ")
    return " ".join(h.split("/")[0].split())


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


def unit_key(unit):
    # Files write the micro sign or the Greek mu; both mean micro.
    return clean(unit).lower().replace("μ", "µ").replace(" ", "")


def is_lead(text):
    """True if a cell names lead as a total element (English or French)."""
    c = " ".join(clean(text).lower().split())
    return c in ("lead", "plomb", "lead (pb)", "pb", "lead/plomb")


ND_TOKENS = {"ND", "NOT DETECTED", "NON DETECTED", "NOTDETECTED", "NON DÉTECTÉ", "BRL",
             "BELOW RL", "BELOW REPORTING LIMIT", "<RL", "<LOD", "<MDL", "<LOD/MDL"}


def parse_value(raw):
    """(value, kind) for one lead result cell. A number above 0 is 'det'. A 0, a '<' with a
    number >= 0 or a not-detected token is 'nd'. Anything else (blank, other text, a negative)
    is 'bad' and fails that year's gate."""
    s = clean(raw)
    if not s:
        return None, "bad"
    key = " ".join(s.upper().replace(".", "").split())
    if key in ND_TOKENS or key.replace(" ", "") in ND_TOKENS:
        return 0.0, "nd"
    if s.startswith("<"):
        v = number(s[1:])
        return (0.0, "nd") if v is not None and v >= 0 else (None, "bad")
    v = number(s)
    if v is None or v < 0:
        return None, "bad"
    return (0.0, "nd") if v == 0 else (v, "det")


def mask(raw):
    return "".join("#" if ch.isdigit() else ch for ch in clean(raw))


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def wilson(k, n, z=1.959963984540054):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, centre - half), min(1.0, centre + half)]


def fisher_less(k1, n1, k2, n2):
    """One-sided exact P(X <= k1) for k1 of n1 against k2 of n2 (hypergeometric, margins fixed)."""
    k, n = k1 + k2, n1 + n2
    total = math.comb(n, k)
    lo = max(0, k - n2)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(lo, k1 + 1)) / total


def find_columns(header):
    """Map roles to column indexes (None if absent). CFP layouts differ between years."""
    h = [head(c) for c in header]

    def pick(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    return {
        "sample": pick(lambda c: c.startswith("sample") and "type" not in c and "date" not in c),
        "component": pick(lambda c: c.startswith("component")),
        "value": pick(lambda c: c.startswith("amount")
                      or (c.startswith("result") and not c.startswith("result unit"))),
        "unit": pick(lambda c: c.startswith("report unit") or c.startswith("unit")
                     or c.startswith("result unit")),
        "product": pick(lambda c: c.startswith("product")),
        "origin": pick(lambda c: c.startswith("origin")),
        "function": pick(lambda c: c.startswith("function")),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def _cell(r, i):
    return r[i] if i is not None and i < len(r) else ""


def empty_census(col=None):
    return {"columns": col or {}, "rows": 0, "units": {}, "kinds": {}, "bad_shapes": [],
            "samples": 0, "products": {}}


def parse_year(text, year):
    """(samples, census) for the lead rows of one decoded CFP CSV. A sample is detected if any of
    its lead rows is detected; its value is the largest detected value."""
    rows = csv.reader(io.StringIO(text))
    col = find_columns(next(rows, []))
    census = empty_census(col)
    if any(col[k] is None for k in COLS):
        return [], census
    cats = CATEGORY.get(year, {})
    by = {}
    for r in rows:
        if not any(c.strip() for c in r) or not is_lead(_cell(r, col["component"])):
            continue
        raw = clean(_cell(r, col["value"]))
        v, kind = parse_value(raw)
        unit = unit_key(_cell(r, col["unit"]))
        census["rows"] += 1
        _bump(census["units"], unit)
        _bump(census["kinds"], kind)
        if kind == "bad" and mask(raw) not in census["bad_shapes"]:
            census["bad_shapes"].append(mask(raw))
        sid = clean(_cell(r, col["sample"]))
        s = by.get(sid)
        if s is None:
            product = clean(_cell(r, col["product"]))
            s = by[sid] = {"sample": sid, "product": product,
                           "category": cats.get(product, "unmapped"),
                           "origin": clean(_cell(r, col["origin"])),
                           "function": clean(_cell(r, col["function"])),
                           "unit": unit, "raws": [], "kinds": [], "value": 0.0}
        s["raws"].append(raw)
        s["kinds"].append(kind)
        if kind == "det":
            s["value"] = max(s["value"], v)
    samples = list(by.values())
    for s in samples:
        s["kind"] = "bad" if "bad" in s["kinds"] else ("det" if "det" in s["kinds"] else "nd")
        _bump(census["products"], s["product"])
    census["samples"] = len(samples)
    return samples, census


def gate_checks(census, sha_ok, year):
    n = sum(PRODUCTS[year].values())
    return {
        "sha256": bool(sha_ok),
        "columns": all(census["columns"].get(k) is not None for k in COLS),
        "rows": census["rows"] == n,
        "samples": census["samples"] == n,
        "units": census["units"] == {MICRO_G: n},
        "products": census["products"] == PRODUCTS[year],
        "values": census["rows"] > 0 and census["kinds"].get("bad", 0) == 0,
    }


def cat_stats(samples):
    """Per category: n, det, nd, sorted detected values (ppm), min, max, sum, both means."""
    out = {}
    for s in samples:
        c = out.setdefault(s["category"], {"n": 0, "det": 0, "nd": 0, "values": []})
        c["n"] += 1
        if s["kind"] == "det":
            c["det"] += 1
            c["values"].append(s["value"])
        else:
            c["nd"] += 1
    for c in out.values():
        c["values"].sort()
        c["min"] = c["values"][0] if c["values"] else None
        c["max"] = c["values"][-1] if c["values"] else None
        c["sum"] = sum(c["values"])
        c["mean_all"] = c["sum"] / c["n"] if c["n"] else None
        c["mean_positives"] = c["sum"] / c["det"] if c["det"] else None
    return out


def year_summary(samples):
    vals = sorted(s["value"] for s in samples if s["kind"] == "det")
    top = max((s for s in samples if s["kind"] == "det"), key=lambda s: s["value"], default=None)
    return {"n": len(samples), "det": len(vals), "nd": len(samples) - len(vals),
            "min": vals[0] if vals else None, "max": vals[-1] if vals else None,
            "max_product": top["product"] if top else None,
            "max_category": top["category"] if top else None}


def check_table(year, cats):
    """Every printed table row: tested, negative, positive and (if any positives) maximum."""
    rows = {}
    for cat, (n, neg, pos, mx, _mean) in TABLE[year].items():
        c = cats.get(cat, {"n": 0, "det": 0, "nd": 0, "max": None})
        ok = {"tested": c["n"] == n, "negative": c["nd"] == neg, "positive": c["det"] == pos}
        if mx is not None and pos:
            ok["max"] = matches(c["max"], mx)
        rows[cat] = {"ok": ok, "file": {"n": c["n"], "nd": c["nd"], "det": c["det"],
                                        "max": c.get("max")},
                     "printed": {"n": n, "nd": neg, "det": pos, "max": mx}}
    return rows


def check_text(year, cats, ys):
    t = TEXT.get(year)
    if not t:
        return {}
    ok = {}
    if year == "2018":
        f = [cats.get(k, {"n": 0, "det": 0, "values": []}) for k in ("formula-dairy", "formula-soy")]
        vals = sorted(v for c in f for v in c["values"])
        ok["formula_n"] = sum(c["n"] for c in f) == t["formula_n"]
        ok["formula_det"] = sum(c["det"] for c in f) == t["formula_det"]
        ok["formula_range"] = bool(vals) and matches(vals[0], t["formula_range"][0]) \
            and matches(vals[-1], t["formula_range"][1])
    if "det" in t:
        ok["det"] = ys["det"] == t["det"] and ys["n"] == t["n"]
    if "nd" in t:
        ok["nd"] = ys["nd"] == t["nd"] and ys["n"] == t["n"]
    if "range" in t:
        ok["range"] = matches(ys["min"], t["range"][0]) and matches(ys["max"], t["range"][1])
    if "max_category" in t:
        ok["max_category"] = ys["max_category"] == t["max_category"]
    if "max_product" in t:
        ok["max_product"] = ys["max_product"] == t["max_product"]
    if year == "2022":
        for cat in ("infant-cereal", "snack"):
            ok[f"min_{cat}"] = matches(cats.get(cat, {}).get("min"), MIN_2022)
    return ok


def mean_rows(year, cats):
    """P5: for each printed row with positives (2021's combined puree-meal excluded), which mean
    reproduces the printed mean."""
    out = {}
    for cat, (_n, _neg, pos, _mx, mean) in TABLE[year].items():
        if not pos or mean is None:
            continue
        c = cats.get(cat)
        if not c:
            continue
        out[cat] = {"printed": mean, "mean_all": c["mean_all"],
                    "mean_positives": c["mean_positives"],
                    "all_matches": matches(c["mean_all"], mean),
                    "positives_matches": matches(c["mean_positives"], mean),
                    "predicted": MEAN_RULE[year]}
        key = "all_matches" if MEAN_RULE[year] == "all" else "positives_matches"
        out[cat]["met"] = out[cat][key]
    return out


def analyse(passing):
    """passing: {year: samples} for the years whose gate passed."""
    a = {"cats": {}, "years": {}, "table": {}, "text": {}, "means": {}}
    for y, samples in passing.items():
        cats = cat_stats(samples)
        ys = year_summary(samples)
        a["cats"][y] = cats
        a["years"][y] = ys
        a["table"][y] = check_table(y, cats)
        a["text"][y] = check_text(y, cats, ys)
        a["means"][y] = mean_rows(y, cats)
    if "2021" in passing:
        pm = a["cats"]["2021"].get("puree-meal", {"values": [], "max": None})
        a["p1"] = {"puree_meal_values": pm["values"], "puree_meal_max": pm["max"],
                   "any_2021_value_matching_0_18": any(
                       matches(v, "0.18") for c in a["cats"]["2021"].values()
                       for v in c["values"])}
        a["p2"] = {"puree_meal_values": pm["values"],
                   "matching_0_018": [v for v in pm["values"] if matches(v, "0.018")]}
    a["p3"] = {y: a["years"][y]["min"] for y in a["years"]}
    fda = []
    for y, cat, level in FDA:
        if y not in a["cats"]:
            continue
        c = a["cats"][y].get(cat, {"n": 0, "values": []})
        k = sum(1 for v in c["values"] if v > level + 1e-12)
        row = {"year": y, "category": cat, "level_ppm": level, "n": c["n"], "above": k,
               "ci95": wilson(k, c["n"]), "detected": len(c["values"])}
        if cat in ("puree", "puree-meal"):
            row["above_0_020"] = sum(1 for v in c["values"] if v > 0.020 + 1e-12)
        fda.append(row)
    a["fda"] = fda
    cut = {}
    for y in ("2019", "2022"):
        if y not in a["cats"]:
            continue
        for cat in ("infant-cereal", "snack"):
            c = a["cats"][y].get(cat)
            if c:
                k = sum(1 for v in c["values"] if v >= P6_CUT - 1e-12)
                cut[f"{y}/{cat}"] = {"n": c["n"], "k": k, "rate": k / c["n"],
                                     "ci95": wilson(k, c["n"])}
    a["common_cut"] = cut
    if "2019/infant-cereal" in cut and "2022/infant-cereal" in cut:
        early, late = cut["2019/infant-cereal"], cut["2022/infant-cereal"]
        a["p6"] = {"cut_ppm": P6_CUT, "y2019": early, "y2022": late,
                   "fisher_one_sided_p": fisher_less(late["k"], late["n"],
                                                     early["k"], early["n"])}
    if "2019/snack" in cut and "2022/snack" in cut:
        # Reported, not graded: P(2019 at most as high as observed) = 2022 snacks higher.
        early, late = cut["2019/snack"], cut["2022/snack"]
        a["snack_cut_fisher_greater_p"] = fisher_less(early["k"], early["n"],
                                                      late["k"], late["n"])
    return a


def _all(d):
    return bool(d) and all(d.values())


def grade(a, gates):
    ok = {y: all(gates[y].values()) for y in YEARS}
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": all(ok.values()),
              "observed": {"per_year": gates, "passing": [y for y in YEARS if ok[y]]},
              "text": "per year: SHA-256; lead rows and samples, unit ug/g and samples per product "
                      "label as in the census; every lead result detected (a number above 0) or "
                      "not detected (0, '<' with a number >= 0, or a not-detected token). Each "
                      "year is graded only if its own gate passes."}]

    def add(pid, kind, text, graded, observe, met):
        o = observe() if graded else {}
        preds.append({"id": pid, "kind": kind, "graded": bool(graded),
                      "met": bool(graded and met(o)), "text": text, "observed": o})

    for y in YEARS:
        add(f"C{y}", "consistency", f"{y} report: every lead table row (tested, negative, "
            "positive, maximum) and every printed lead text figure", ok[y],
            lambda y=y: {"table": a["table"][y], "text": a["text"][y]},
            lambda o: all(_all(r["ok"]) for r in o["table"].values())
            and all(o["text"].values()))
    add("P1", "prediction", "2021: the appendix's 0.18 ppm meal maximum is not in the file: the "
        "largest puree/meal value is below 0.05 ppm and no 2021 value rounds to 0.18",
        ok["2021"], lambda: a["p1"],
        lambda o: o["puree_meal_max"] is not None and o["puree_meal_max"] < 0.05
        and not o["any_2021_value_matching_0_18"])
    add("P2", "prediction", "2021: one puree/meal positive rounds to 0.018 ppm (0.18 with its "
        "decimal point moved)", ok["2021"], lambda: a["p2"],
        lambda o: len(o["matching_0_018"]) >= 1)
    p3_years = [y for y in P3_YEARS if ok[y]]
    add("P3", "prediction", "the smallest detected lead value is at least 0.010 ppm in each of "
        "2018, 2019, 2020 and 2021 (graded on the years that pass)", bool(p3_years),
        lambda: {"min_detected": {y: a["p3"][y] for y in p3_years},
                 "all_years": a["p3"], "floor": P3_FLOOR},
        lambda o: all(v is not None and v >= P3_FLOOR - 1e-12
                      for v in o["min_detected"].values()))

    def fda_row(y, cat):
        return next((r for r in a["fda"] if r["year"] == y and r["category"] == cat), None)

    add("P4", "prediction", "FDA dry-infant-cereal action level (0.020 ppm): at least 6 of the 48 "
        "2019 infant cereals and 1 to 3 of the 39 2022 infant cereals are above it",
        ok["2019"] and ok["2022"],
        lambda: {"2019": fda_row("2019", "infant-cereal"),
                 "2022": fda_row("2022", "infant-cereal")},
        lambda o: o["2019"]["above"] >= P4_MIN_2019
        and P4_RANGE_2022[0] <= o["2022"]["above"] <= P4_RANGE_2022[1])
    add("P5", "prediction", "each printed mean is reproduced by the predicted convention: all-"
        "sample in 2017, 2019, 2020 and 2021; positives-only in 2018 and 2022",
        any(a["means"].get(y) for y in YEARS),
        lambda: a["means"],
        lambda o: all(r["met"] for y in o.values() for r in y.values()))
    add("P6", "prediction", "infant cereal at a common 0.015 ppm cut: the 2022 rate is below the "
        "2019 rate (point estimates; Fisher p and Wilson intervals reported)",
        "p6" in a, lambda: a["p6"],
        lambda o: o["y2022"]["rate"] < o["y2019"]["rate"])
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
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-cfp-lead"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(label, data_dir):
    dataset, resource, path, sha = FILES[label]
    local = os.path.join(data_dir, resource + ".csv") if data_dir else ""
    if local and os.path.exists(local):
        with open(local, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == sha:
            return raw, "data-volume"
    errors = []
    for host in ("https://open.canada.ca", "https://ouvert.canada.ca"):
        url = f"{host}/data/dataset/{dataset}/resource/{resource}/download/{path}"
        try:
            raw = _fetch(url)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        if _sha(raw) != sha:
            errors.append(f"{url}: SHA-256 {_sha(raw)} != {sha}")
            continue
        return raw, url
    raise RuntimeError(f"{label}: no verified copy: " + "; ".join(errors))


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


def write_outputs(out_dir, samples_by, censuses, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "cfp_lead_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "sample", "product", "category", "origin", "function", "unit",
                    "n_rows", "values_raw", "kind", "value_ppm"])
        for y in YEARS:
            for s in sorted(samples_by.get(y, []), key=lambda s: s["sample"]):
                w.writerow([y, s["sample"], s["product"], s["category"], s["origin"],
                            s["function"], s["unit"], len(s["raws"]), ";".join(s["raws"]),
                            s["kind"], repr(s["value"])])
    result = {"study": "cfp-lead", "version": VERSION, "predictions": preds,
              "census": censuses, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "cfp_lead_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the cfp-lead 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    gates, samples_by, censuses, provenance = {}, {}, {}, {}
    for y in YEARS:
        try:
            raw, src = load(y, args.data_dir)
            text, enc = decode(raw)
            samples, census = parse_year(text, y)
            sha_ok = _sha(raw) == FILES[y][3]
            provenance[y] = {"resource": FILES[y][1], "sha256": FILES[y][3], "bytes": len(raw),
                             "source": src, "encoding": enc}
            del raw, text
        except Exception as exc:  # noqa: BLE001 - that year's gate fails, with the reason
            samples, census, sha_ok = [], empty_census(), False
            census["error"] = f"{type(exc).__name__}: {exc}"
            provenance[y] = {"resource": FILES[y][1], "error": census["error"]}
        gates[y] = gate_checks(census, sha_ok, y)
        samples_by[y] = samples
        censuses[y] = census
    passing = {y: samples_by[y] for y in YEARS if all(gates[y].values())}
    a = analyse(passing)
    preds = grade(a, gates)
    result = write_outputs(args.out_dir, samples_by, censuses, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gates": gates,
                      "kinds": {y: censuses[y]["kinds"] for y in YEARS},
                      "bad_shapes": {y: censuses[y]["bad_shapes"] for y in YEARS},
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if passing else 1


if __name__ == "__main__":
    sys.exit(main())
