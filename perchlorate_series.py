#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""perchlorate-series 0.1.0 grader: CFIA's three open perchlorate files (2010-11 "p10", 2011-13
"p11", 2013-14 "p13") against their summary pages and Table 3 of CFIA's 2020-21 dairy and infant
formula report.

Grades V1-V9 of docs/perchlorate-series-0.1.0-prereg.md with the label maps of
docs/perchlorate-series-0.1.0-census.md (p10, p11) and docs/perchlorate-series-0.1.0-grader.md
(p13), all published before this module reads any value.

Coding (pre-registration and census note): one perchlorate row per sample; every result cell is a
number; a sample is a *detect* when its result is above zero. Units are ng/g (ppb). Averages are of
detects only. A printed figure matches when the file's value is within half a unit of its last
printed digit; a printed percentage matches when the share rounds (half up) to it; a derived band
is inclusive at both ends. Survey years run April to March and come from the sampling-date column
(`Date Sampled ...` in p10 and p13, `DateSample` in p11).

Before any grading it reports, from label counts only, which placements of the p13 label blocks
the report's printed shares and its 272-detect total allow (`p13_map_search`). Then it reports,
per file, how many results are exactly zero, the five smallest above zero and, per group and
region, the stored minimum and maximum, so that a scale slip is visible.

Uses cfia_census.load / decode (published) to fetch and decode the files; everything else is here.
Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0;
derived data CC BY 4.0. Not a compliance finding (Health Canada has set no maximum level for
perchlorate in food), not about any brand, and not dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import io
import itertools
import json
import os
import re
import sys

VERSION = "0.1.0"
UNIT = "ng/g"

TARGETS = {
    "p10": {"name": "p10",
            "dataset": "436bec6d-f410-45cc-89ff-f5331cfa663c",
            "resource": "46630289-3b83-4392-b648-da594e5357ce",
            "path": ("cfia_acia-1339-v1-cfia_acia_-_19007386_-_fsap_chem_ts_-_2010-11_perchlorate_in_"
                     "fresh_fruits_and_.csv"),
            "size": 95033, "md5": "f497970ea94e7d4eaf74fdabb9535bca", "samples": 611},
    "p11": {"name": "p11",
            "dataset": "0bdaecc5-805e-4f42-a182-338870635221",
            "resource": "beccac79-f18e-4270-9c2c-c6ce645fc2b4",
            "path": ("cfia_acia-1340-v1-cfia_acia_-_19007867_-_fsap_chem_ts_-_2011-13_perchlorate_in_"
                     "fresh_fruits_and_.csv"),
            "size": 228127, "md5": "66a04ce98555c6898c18ebaefc042a96", "samples": 1426},
    "p13": {"name": "p13",
            "dataset": "79e83e09-be72-4cec-b410-1e69aaa450f7",
            "resource": "7511b1a3-48c7-4386-ae6e-f2c4e87c6e84",
            "path": "2013-14_perchlorate_in_selected_foods_perchlorate-dans-certains-aliments.csv",
            "size": 78310, "md5": "05b587cb13f15932894200ba5879445a", "samples": 477},
}

ROLES = {
    "sample": ("sample no",), "region": ("region",), "function": ("function",),
    "origin": ("origin",), "product": ("product",), "date": ("date sampled", "datesample"),
    "component": ("component",), "value": ("result",), "unit": ("unit",),
}
OPTIONAL = ("region",)

# --- label maps ----------------------------------------------------------------------------------
ORGANIC_RE = re.compile(r"\s*-\s*organic\s*$", re.I)
GH_RE = re.compile(r"\s*\(GH\)\s*$")


def base(label):
    """Census-note commodity rule: '- Organic' (any case) and ' (GH)' join the base product, and
    every lettuce label is 'Lettuce'."""
    b = GH_RE.sub("", (label or "").strip())
    b = ORGANIC_RE.sub("", b)
    if b.lower().startswith("lettuce"):
        return "Lettuce"
    return b


P10_DAIRY = ("Cheese", "Milk", "Yogurt")
SOY_FORMULA = "Infant Formula - Soy"
DAIRY_FORMULA = "Infant Formula - Dairy"


def p10_group(label):
    b = base(label)
    if b in P10_DAIRY:
        return "dairy"
    if b.startswith("Infant Formula"):
        return "formula"
    return "fv"


P11_FRUIT = ("Blueberry", "Grapefruit", "Lemon", "Melon - Cantaloupe", "Orange", "Strawberry",
             "Watermelon")
P11_LEAFY = ("Arugula", "Chard", "Endive - Broadleaf", "Kale", "Lettuce", "Spinach")
P11_VEG = P11_LEAFY + ("Cucumber", "Tomato")
P11_DAIRY = ("Cheese", "Cream", "Dessert - Frozen", "Dessert - Frozen (Dairy)", "Desserts",
             "Dressing", "Misc - Dairy", "Pudding", "Sauces", "Misc")
P11_JUICE_OTHER = ("Cider - Apple", "Nectar - Other", "Nectar - Prune")


def p11_group(label):
    b = base(label)
    if b in P11_FRUIT:
        return "fruit"
    if b in P11_VEG:
        return "veg"
    if b in P11_DAIRY:
        return "dairy"
    if b.startswith("Infant Formula"):
        return "formula"
    if b.startswith("Juice - ") or b in P11_JUICE_OTHER:
        return "juice"
    return None


# p13 (grader note). Exact labels as they appear in the file.
P13_FRESH_HERBS = ("Herb - Bay Leaves - Fresh", "Herb - Chive - Fresh", "Herb - Cilantro - Fresh",
                   "Herb - Dill - Fresh", "Herb - Oregano - Fresh", "Herb - Parsley - Fresh",
                   "Herb - Rosemary - Fresh", "Herb - Sage - Fresh")
P13_PLAIN_HERBS = ("Basil", "Bay Leaves", "Chive", "Cilantro", "Dill", "Mint", "Oregano",
                   "Parsley", "Rosemary", "Sage", "Thyme")
P13_LEAFY_OTHER = ("Arugula", "Dandelion", "Endive", "Endive - Broadleaf", "Kale", "Lettuce",
                   "Lettuce - Leaf - Organic", "Lettuce - Organic", "Misc Vegetables", "Rapini",
                   "Spinach")
P13_POTATOES = ("Fingerling Potatoes", "Potato - Fingerling", "Potato - New", "Potato - Organic",
                "Potato - Other", "Potato - Russet", "Potato - White", "Potato - Yellow",
                "Potatoes", "Red Potatoes", "Russet Potatoes", "White Potatoes", "Yellow Potatoes")
P13_DRIED_FRUIT = ("Cranberry - dried", "Date", "Dried Fruit", "Fig", "Prune", "Raisin")
P13_GRAIN = ("Couscous", "Flour - Rice", "Flour - Wheat", "Grain - Rice", "Grain - Wheat",
             "Rice Products", "Wheat Products")
P13_JUICES = ("Juice - Apple", "Juice - Blend", "Juice - Grapefruit", "Juice - Mixed",
              "Juice - Other", "Juice/Nectar - Other", "juice - pineapple", "Nectar - Apricot",
              "Nectar - Guava", "Beverage - Fruit")
P13_ASSORTED_FIXED = ("Meat Alternative", "Tofu", "Dessert - Frozen (Dairy)",
                      "Dessert - Frozen (Non-Dairy)")
P13_CHEESES = ("Camembert", "Cheddar", "Cheese", "Feta", "Gouda")
P13_YOGURTS = ("Yogurt", "Yogurt - Frozen", "Beverage - Yogurt")
P13_FORMULAS = ("Infant Formula - Dairy", "Infant Formula - Other", "Infant Formula - Soy")
P13_GROUPS = ("fresh", "processed", "dairy", "formula", "grain", "assorted")

# Blocks whose group the labels alone do not settle. The FIRST option of each is the map used for
# grading (grader note); p13_map_search tries every option.
P13_BLOCKS = (
    ("plain_herbs", P13_PLAIN_HERBS, ("fresh", "processed", "assorted")),
    ("mixed_vegetables", ("Mixed Vegetables",), ("processed", "fresh")),
    ("dried_vegetables", ("Dried Vegetables",), ("processed", "assorted")),
    ("pizza", ("Pizza Products",), ("assorted", "grain")),
    ("juices", P13_JUICES, ("assorted", "processed")),
    ("soup", ("Soup",), ("processed", "assorted")),
    ("salsa", ("Salsa",), ("processed", "assorted")),
    ("beverage_other", ("Beverage - Other",), ("assorted", "processed")),
)
P13_OPEN_BLOCKS = ("juices", "soup", "salsa", "beverage_other")
# Printed 2013-14 shares and the detect total (477 - 205).
P13_SHARES = {"fresh": 71, "processed": 40, "dairy": 80, "formula": 54, "grain": 30,
              "assorted": 61}
P13_DETECTS = 272


def p13_fixed_map():
    m = {}
    for lab in P13_FRESH_HERBS + P13_LEAFY_OTHER + P13_POTATOES:
        m[lab] = "fresh"
    for lab in P13_DRIED_FRUIT + ("Potato Products",):
        m[lab] = "processed"
    for lab in P13_GRAIN:
        m[lab] = "grain"
    for lab in P13_ASSORTED_FIXED:
        m[lab] = "assorted"
    for lab in P13_CHEESES + P13_YOGURTS:
        m[lab] = "dairy"
    for lab in P13_FORMULAS:
        m[lab] = "formula"
    return m


def p13_map(choice=None):
    """label -> group. `choice` maps a block name to its group; missing blocks take the first
    option (the grading map)."""
    m = p13_fixed_map()
    for name, labels, options in P13_BLOCKS:
        g = (choice or {}).get(name, options[0])
        for lab in labels:
            m[lab] = g
    return m


P13_MAP = p13_map()


# --- arithmetic on printed shares (no value) -------------------------------------------------------
def pct_ok(k, n, p):
    """True when k of n rounds half up to p percent."""
    return n > 0 and (2 * p - 1) * n <= 200 * k < (2 * p + 1) * n


def feasible(n, p):
    """Detect counts k (0..n) whose share of n rounds to p percent."""
    return [k for k in range(n + 1) if pct_ok(k, n, p)]


def group_sizes(label_counts, mapping):
    sizes = {g: 0 for g in P13_GROUPS}
    unmapped = {}
    for lab, n in label_counts.items():
        g = mapping.get(lab)
        if g is None:
            unmapped[lab] = unmapped.get(lab, 0) + n
        else:
            sizes[g] += n
    return sizes, unmapped


def shares_feasible(sizes, shares=None, total=P13_DETECTS):
    """Whether detect counts exist that meet every printed share and sum to `total`. Returns
    (ok, {group: [lo, hi] or None})."""
    shares = shares or P13_SHARES
    bands = {}
    lo = hi = 0
    ok = True
    for g in P13_GROUPS:
        ks = feasible(sizes[g], shares[g])
        if not ks:
            bands[g] = None
            ok = False
            continue
        bands[g] = [ks[0], ks[-1]]
        lo += ks[0]
        hi += ks[-1]
    return ok and lo <= total <= hi, bands


def p13_map_search(label_counts, blocks=None):
    """Every placement of the given p13 blocks (others at their grading option) and whether the
    printed shares and the 272 total allow it. Label counts only; never a value."""
    names = [b[0] for b in P13_BLOCKS if blocks is None or b[0] in blocks]
    opts = {b[0]: b[2] for b in P13_BLOCKS}
    out = []
    for combo in itertools.product(*(opts[n] for n in names)):
        choice = dict(zip(names, combo))
        sizes, unmapped = group_sizes(label_counts, p13_map(choice))
        ok, bands = shares_feasible(sizes)
        out.append({"choice": choice, "sizes": sizes, "bands": bands, "feasible": ok,
                    "unmapped": unmapped})
    return out


# --- reading -------------------------------------------------------------------------------------
def clean(cell):
    """As cfia_census.clean: no BOM, no edge spaces, single inner spaces (so labels match the
    census records)."""
    return " ".join((cell or "").replace("﻿", "").split())


def _norm(h):
    return h.replace("﻿", "").strip().lower()


def _matches(h, cand):
    return h == cand or h.startswith(cand + " ") or h.startswith(cand + ".")


def find_columns(header):
    """Role -> column index; for each role the first candidate that matches wins, leftmost
    column first (so 'Origin' beats 'Origine')."""
    names = [_norm(h) for h in header]
    cols = {}
    for role, cands in ROLES.items():
        for cand in cands:
            hit = next((i for i, h in enumerate(names) if _matches(h, cand)), None)
            if hit is not None:
                cols[role] = hit
                break
    return cols


def to_value(cell):
    try:
        v = float(cell.strip())
    except (AttributeError, ValueError):
        return None
    if v != v or v < 0:
        return None
    return v


def parse(text):
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    cols = find_columns(header)
    problems = {"missing_roles": sorted(r for r in ROLES if r not in cols and r not in OPTIONAL),
                "bad_values": 0, "bad_units": 0, "short_rows": 0, "columns": cols}
    rows = []
    for raw in reader:
        if not any(c.strip() for c in raw):
            continue
        if len(raw) < len(header):
            problems["short_rows"] += 1
            continue
        r = {role: clean(raw[i]) for role, i in cols.items()}
        r["value"] = to_value(raw[cols["value"]]) if "value" in cols else None
        if r["value"] is None:
            problems["bad_values"] += 1
        if r.get("unit", "") != UNIT:
            problems["bad_units"] += 1
        rows.append(r)
    return rows, problems


def parse_date(text):
    for fmt in ("%d-%b-%y", "%m/%d/%Y", "%Y-%m-%d", "%d-%b-%Y"):
        try:
            return datetime.datetime.strptime((text or "").strip(), fmt).date()
        except ValueError:
            pass
    return None


def survey_year(d):
    if d is None:
        return "(unparsed)"
    y = d.year if d.month >= 4 else d.year - 1
    return f"{y}-{(y + 1) % 100:02d}"


def samples_of(rows):
    out = {}
    for r in rows:
        s = out.get(r["sample"])
        if s is None:
            s = {"sample": r["sample"], "rows": 0, "value": None}
            for f in ("product", "function", "origin", "region", "date"):
                s[f] = r.get(f, "")
            s["year"] = survey_year(parse_date(s["date"]))
            out[r["sample"]] = s
        s["rows"] += 1
        v = r["value"]
        if v is not None:
            s["value"] = v if s["value"] is None else max(s["value"], v)
    return out


def is_detect(s):
    return s["value"] is not None and s["value"] > 0


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def in_range(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def in_band(x, band):
    return x is not None and band[0] - 1e-9 <= x <= band[1] + 1e-9


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def summarise(group):
    vals = sorted(s["value"] for s in group if is_detect(s))
    return {"n": len(group), "detects": len(vals), "min": vals[0] if vals else None,
            "max": vals[-1] if vals else None,
            "mean": sum(vals) / len(vals) if vals else None}


def check_row(summ, n, pmin, pmax, avg):
    avg_ok = in_band(summ["mean"], avg) if isinstance(avg, tuple) else in_range(summ["mean"], avg)
    return {"samples": summ["n"] == n, "min": in_range(summ["min"], pmin),
            "max": in_range(summ["max"], pmax), "average": avg_ok}


def grouped(samples, group_of):
    out, unmapped = {}, {}
    for s in samples.values():
        g = group_of(s["product"])
        if g is None:
            _bump(unmapped, s["product"])
        else:
            out.setdefault(g, []).append(s)
    return out, unmapped


def by_base(group):
    out = {}
    for s in group:
        out.setdefault(base(s["product"]), []).append(s)
    return out


def ranked_means(named):
    """{name: [samples]} -> [(name, mean of detects)] highest first; names without detects are
    left out."""
    rows = [(k, summarise(v)["mean"]) for k, v in named.items()]
    rows = [(k, m) for k, m in rows if m is not None]
    return sorted(rows, key=lambda x: (-x[1], x[0]))


def _pred(vid, checks, observed, text):
    return {"id": vid, "kind": "prediction", "graded": True, "met": all(checks.values()),
            "observed": dict(observed, checks=checks), "text": text}


def _ungraded(ids, reason):
    return [{"id": i, "kind": "prediction", "graded": False, "met": None,
             "observed": {"reason": reason}, "text": ""} for i in ids]


# --- p10 -----------------------------------------------------------------------------------------
def grade_v1(g):
    fv, d, f = (summarise(g.get(k, [])) for k in ("fv", "dairy", "formula"))
    allv = summarise(g.get("fv", []) + g.get("dairy", []) + g.get("formula", []))
    checks = {"fv_detects_280_283": 280 <= fv["detects"] <= 283,
              "dairy_detects_77": d["detects"] == 77, "formula_detects_56": f["detects"] == 56,
              "min_2": in_range(allv["min"], "2"), "max_540": in_range(allv["max"], "540")}
    return _pred("V1", checks, {"fv": fv, "dairy": d, "formula": f, "all": allv},
                 "p10 detects 280-283 / 77 / 56; minimum rounds to 2; maximum 540")


def grade_v2(g):
    ranks = ranked_means(by_base(g.get("fv", [])))
    means = dict(ranks)
    dairy = by_base(g.get("dairy", []))
    dm = {k: summarise(dairy.get(k, []))["mean"] for k in P10_DAIRY}
    soy = summarise([s for s in g.get("formula", []) if base(s["product"]) == SOY_FORMULA])
    milk = dm["Milk"]
    checks = {"cucumber_48.6": in_range(means.get("Cucumber"), "48.6"),
              "tomato_44.9": in_range(means.get("Tomato"), "44.9"),
              "top_two_cucumber_tomato": {k for k, _ in ranks[:2]} == {"Cucumber", "Tomato"},
              "cheese_5": in_range(dm["Cheese"], "5"), "yogurt_4.9": in_range(dm["Yogurt"], "4.9"),
              "milk_below_both": (milk is not None and dm["Cheese"] is not None
                                  and dm["Yogurt"] is not None
                                  and milk < dm["Cheese"] and milk < dm["Yogurt"]),
              "soy_formula_16.7": in_range(soy["mean"], "16.7")}
    return _pred("V2", checks, {"commodity_means": ranks, "dairy_means": dm, "soy_formula": soy},
                 "p10: cucumber 48.6 and tomato 44.9 top the commodity averages; cheese 5 and "
                 "yogurt 4.9 above milk; soy formula 16.7")


P10_TABLE3 = {"Cheese": (23, "24"), "Milk": (42, "9"), "Yogurt": (24, "12")}


def grade_v3(g):
    dairy = by_base(g.get("dairy", []))
    rows = {k: summarise(dairy.get(k, [])) for k in P10_DAIRY}
    checks = {}
    for k, (n, pmax) in P10_TABLE3.items():
        checks[f"{k.lower()}_n_{n}"] = rows[k]["n"] == n
        checks[f"{k.lower()}_max_{pmax}"] = in_range(rows[k]["max"], pmax)
        checks[f"{k.lower()}_min_2"] = in_range(rows[k]["min"], "2")
    near = [k for k in P10_DAIRY if in_band(rows[k]["mean"], (5.05, 5.15))]
    checks["at_most_one_average_5.1"] = len(near) <= 1
    wide = summarise(g.get("dairy", []))
    checks["dairy_wide_average_5.05_5.15"] = in_band(wide["mean"], (5.05, 5.15))
    return _pred("V3", checks, {"rows": rows, "averages_at_5.1": near, "dairy_wide": wide},
                 "Table 3's 2010 dairy rows: counts, maxima and minima hold; at most one average "
                 "is 5.1; the dairy-wide average is 5.05-5.15")


def grade_v4(g):
    forms = g.get("formula", [])
    sub = summarise([s for s in forms if base(s["product"]) == DAIRY_FORMULA])
    allf = summarise(forms)
    checks = check_row(sub, 74, "2", "22", (10.35, 10.45))
    return _pred("V4", checks, {"dairy_formula": sub, "all_formulas": allf},
                 "Table 3's 2010 formula row (74; 2-22; 10.4) is Infant Formula - Dairy")


# --- p11 -----------------------------------------------------------------------------------------
def grade_v5(g):
    allg = [s for k in ("fruit", "veg", "juice", "dairy", "formula") for s in g.get(k, [])]
    sm = {k: summarise(g.get(k, [])) for k in ("fruit", "veg", "juice", "dairy", "formula")}
    allv = summarise(allg)
    checks = {"none_637": allv["n"] - allv["detects"] == 637,
              "juice_51_52": sm["juice"]["detects"] in (51, 52),
              "dairy_139_140": sm["dairy"]["detects"] in (139, 140),
              "formula_49": sm["formula"]["detects"] == 49,
              "fruit_44pct": pct_ok(sm["fruit"]["detects"], sm["fruit"]["n"], 44),
              "veg_74pct": pct_ok(sm["veg"]["detects"], sm["veg"]["n"], 74),
              "min_2": in_range(allv["min"], "2"), "max_2400": in_range(allv["max"], "2400")}
    return _pred("V5", checks, {"groups": sm, "all": allv},
                 "p11: 637 without; juice 51-52, dairy-based 139-140, formula 49 detects; fruit "
                 "44%, vegetables 74%; minimum 2, maximum 2400")


def year_split(group):
    out = {}
    for s in group:
        _bump(out, s["year"])
    return dict(sorted(out.items()))


def grade_v6(g):
    creams = [s for s in g.get("dairy", []) if base(s["product"]) == "Cream"]
    c11 = summarise([s for s in creams if s["year"] == "2011-12"])
    c12 = summarise([s for s in creams if s["year"] == "2012-13"])
    non_soy = [s for s in g.get("formula", []) if base(s["product"]) != SOY_FORMULA]
    f68 = summarise(non_soy)
    checks = {"cream_2011_min_3": in_range(c11["min"], "3"),
              "cream_2011_max_6": in_range(c11["max"], "6"),
              "cream_2011_avg_4.25_4.35": in_band(c11["mean"], (4.25, 4.35)),
              "cream_2012_min_3": in_range(c12["min"], "3"),
              "cream_2012_max_7": in_range(c12["max"], "7"),
              "cream_2012_avg_3.95_4.05": in_band(c12["mean"], (3.95, 4.05)),
              "formula_min_2": in_range(f68["min"], "2"),
              "formula_max_33": in_range(f68["max"], "33"),
              "formula_avg_11.75_11.85": in_band(f68["mean"], (11.75, 11.85))}
    return _pred("V6", checks, {"cream_2011_12": c11, "cream_2012_13": c12,
                                "cream_years": year_split(creams), "non_soy_formulas": f68,
                                "non_soy_formula_years": year_split(non_soy)},
                 "Table 3's p11 rows: creams 2011 (3, 6, 4.25-4.35) and 2012 (3, 7, 3.95-4.05); "
                 "formulas (68 non-soy) 2, 33, 11.75-11.85")


def grade_v7(g):
    named = {"Cucumber": [], "Tomato": [], "Leafy": []}
    for s in g.get("veg", []):
        b = base(s["product"])
        if b in P11_LEAFY:
            named["Leafy"].append(s)
        elif b in named:
            named[b].append(s)
    for b, v in by_base(g.get("fruit", [])).items():
        named[b] = v
    ranks = ranked_means(named)
    m = dict(ranks)
    checks = {"cucumber_106": in_range(m.get("Cucumber"), "106"),
              "leafy_65": in_range(m.get("Leafy"), "65"),
              "tomato_57": in_range(m.get("Tomato"), "57"),
              "top_three": {k for k, _ in ranks[:3]} == {"Cucumber", "Leafy", "Tomato"}}
    return _pred("V7", checks, {"ranked_means": ranks},
                 "p11: cucumber 106, leafy greens 65 and tomato 57 are the three highest averages")


# --- p13 -----------------------------------------------------------------------------------------
def p13_group(label):
    return P13_MAP.get(label)


def grade_v8(g):
    sm = {k: summarise(g.get(k, [])) for k in P13_GROUPS}
    allg = [s for k in P13_GROUPS for s in g.get(k, [])]
    allv = summarise(allg)
    top = max((s for s in allg if is_detect(s)), key=lambda s: s["value"], default=None)
    checks = {"none_205": allv["n"] - allv["detects"] == 205}
    for k in ("fresh", "processed", "dairy", "grain", "assorted"):
        checks[f"{k}_{P13_SHARES[k]}pct"] = pct_ok(sm[k]["detects"], sm[k]["n"], P13_SHARES[k])
    for k, p in (("fresh", "130"), ("processed", "23"), ("grain", "5"), ("dairy", "6")):
        checks[f"{k}_avg_{p}"] = in_range(sm[k]["mean"], p)
    checks["min_2"] = in_range(allv["min"], "2")
    checks["max_3300"] = in_range(allv["max"], "3300")
    checks["max_is_arugula"] = top is not None and "arugula" in top["product"].lower()
    return _pred("V8", checks, {"groups": sm, "all": allv,
                                "max_sample": None if top is None else
                                {"sample": top["sample"], "product": top["product"],
                                 "origin": top["origin"], "ppb": top["value"]},
                                "formula_share_not_graded": [sm["formula"]["detects"],
                                                             sm["formula"]["n"]]},
                 "p13: 205 without; shares 71/40/80/30/61; averages 130/23/5/6; min 2; max 3300 "
                 "(arugula)")


def grade_v9(g):
    dairy = g.get("dairy", [])
    cheese = [s for s in dairy if s["product"] in P13_CHEESES]
    yogurt = [s for s in dairy if s["product"] in P13_YOGURTS]
    non_soy = [s for s in g.get("formula", []) if s["product"] != SOY_FORMULA]
    ch, yo, fo = summarise(cheese), summarise(yogurt), summarise(non_soy)
    checks = {}
    for key, summ, spec in (("cheese", ch, (20, "3", "42", (8.95, 9.05))),
                            ("formula", fo, (30, "2", "64", (16.45, 16.55))),
                            ("yogurt", yo, (30, "2", "11", (4.85, 4.95)))):
        for k, v in check_row(summ, *spec).items():
            checks[f"{key}_{k}"] = v
    checks["dairy_detects_40"] = summarise(dairy)["detects"] == 40
    checks["cheese_detects_10_16"] = 10 <= ch["detects"] <= 16
    return _pred("V9", checks, {"cheese": ch, "yogurt": yo, "non_soy_formula": fo,
                                "all_formulas": summarise(g.get("formula", []))},
                 "Table 3's p13 rows: cheese 3-42 (9.0), formula 2-64 (16.5), yogurt 2-11 (4.9); "
                 "10-16 of 40 dairy detects are cheeses")


# --- descriptive ---------------------------------------------------------------------------------
def coding(samples):
    vals = [s["value"] for s in samples.values() if s["value"] is not None]
    pos = sorted(v for v in vals if v > 0)
    return {"zero": sum(1 for v in vals if v == 0), "above_zero": len(pos),
            "smallest_above_zero": pos[:5], "distinct_values": len(set(vals))}


def scale_table(groups):
    """Stored minimum and maximum of detects per group and region (scale check)."""
    out = {}
    for g, members in sorted(groups.items()):
        regions = {}
        for s in members:
            regions.setdefault(s["region"] or "(blank)", []).append(s)
        out[g] = {r: {k: summarise(v)[k] for k in ("n", "detects", "min", "max")}
                  for r, v in sorted(regions.items())}
    return out


def label_counts(samples):
    out = {}
    for s in samples.values():
        _bump(out, s["product"])
    return out


def gate(raw, target, problems, samples, unmapped):
    md5 = hashlib.md5(raw).hexdigest()
    per = {}
    for s in samples.values():
        _bump(per, s["rows"])
    checks = {"size": len(raw) == target["size"], "md5": md5 == target["md5"],
              "roles": not problems["missing_roles"], "values": problems["bad_values"] == 0,
              "units": problems["bad_units"] == 0, "short_rows": problems["short_rows"] == 0,
              "samples": len(samples) == target["samples"],
              "one_row_per_sample": per == {1: target["samples"]},
              "all_labels_mapped": not unmapped}
    return checks, {"md5": md5, "bytes": len(raw), "samples": len(samples),
                    "rows_per_sample": {str(k): v for k, v in sorted(per.items())}}


PLAN = {"p10": (p10_group, ("V1", "V2", "V3", "V4"), (grade_v1, grade_v2, grade_v3, grade_v4)),
        "p11": (p11_group, ("V5", "V6", "V7"), (grade_v5, grade_v6, grade_v7)),
        "p13": (p13_group, ("V8", "V9"), (grade_v8, grade_v9))}


def grade_file(name, raw, text, target=None):
    target = target or TARGETS[name]
    group_of, ids, fns = PLAN[name]
    rows, problems = parse(text)
    samples = samples_of(rows)
    g, unmapped = grouped(samples, group_of)
    checks, facts = gate(raw, target, problems, samples, unmapped)
    rec = {"gate": checks, "facts": facts, "problems": problems,
           "census_checks": {"groups": {k: len(v) for k, v in sorted(g.items())},
                             "unmapped": unmapped,
                             "years": {k: year_split(v) for k, v in sorted(g.items())}}}
    if name == "p13":
        lc = label_counts(samples)
        rec["map_search_open_blocks"] = p13_map_search(lc, P13_OPEN_BLOCKS)
        rec["map_search_all_blocks_feasible"] = [r for r in p13_map_search(lc) if r["feasible"]]
    if all(checks.values()):
        preds = [fn(g) for fn in fns]
    else:
        preds = _ungraded(ids, f"{name} gate failed")
    rec["descriptive"] = {"coding": coding(samples), "scale": scale_table(g)}
    if name == "p13":
        alt, _ = grouped(samples, p13_map({"juices": "processed"}).get)
        rec["descriptive"]["juices_as_processed"] = {
            k: summarise(v) for k, v in sorted(alt.items())}
    return rec, preds, samples, g


# --- outputs -------------------------------------------------------------------------------------
def write_samples(tables, out_dir):
    with open(os.path.join(out_dir, "perchlorate_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "sample", "product", "group", "commodity", "function", "origin",
                    "region", "date", "survey_year", "perchlorate_ppb"])
        for name, samples in tables:
            group_of = PLAN[name][0]
            for sid in sorted(samples):
                s = samples[sid]
                w.writerow([name, sid, s["product"], group_of(s["product"]) or "",
                            base(s["product"]), s["function"], s["origin"], s["region"],
                            s["date"], s["year"], s["value"]])


def load_text(target, data_dir):
    import cfia_census as cc  # published module; only its download and decoding are used
    raw, src = cc.load(target, data_dir)
    text, enc = cc.decode(raw)
    return raw, text, {"source": src, "encoding": enc}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the perchlorate-series 0.1.0 predictions.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    summary = {"study": "perchlorate-series", "grader": "perchlorate_series", "version": VERSION,
               "files": {}, "predictions": []}
    gates_ok = True
    tables = []
    for name in ("p10", "p11", "p13"):
        try:
            raw, text, prov = load_text(TARGETS[name], args.data_dir)
            rec, preds, samples, _ = grade_file(name, raw, text)
            rec["provenance"] = dict(prov, dataset=TARGETS[name]["dataset"],
                                     resource=TARGETS[name]["resource"],
                                     portal_md5=TARGETS[name]["md5"])
            tables.append((name, samples))
        except Exception as exc:  # noqa: BLE001 - recorded; the other files still run
            rec = {"error": f"{type(exc).__name__}: {exc}", "gate": {"loaded": False}}
            preds = _ungraded(PLAN[name][1], rec["error"])
        gates_ok = gates_ok and all(rec["gate"].values())
        summary["files"][name] = rec
        summary["predictions"].extend(preds)
    write_samples(tables, args.out_dir)
    graded = [p for p in summary["predictions"] if p["graded"]]
    summary["n_graded"] = len(graded)
    summary["n_met"] = sum(1 for p in graded if p["met"])
    with open(os.path.join(args.out_dir, "perchlorate_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True, ensure_ascii=False, default=str)
    p13 = summary["files"].get("p13", {})
    print(json.dumps({"p13_open_block_placements": [
        [r["choice"], r["feasible"]] for r in p13.get("map_search_open_blocks", [])],
        "p13_all_block_feasible": [r["choice"] for r in
                                   p13.get("map_search_all_blocks_feasible", [])]},
        ensure_ascii=False))
    print(json.dumps({"gates": {n: f["gate"] for n, f in summary["files"].items()},
                      "predictions": [[p["id"], p["graded"], p["met"]]
                                      for p in summary["predictions"]],
                      "n_graded": summary["n_graded"], "n_met": summary["n_met"]},
                     indent=2, ensure_ascii=False))
    return 0 if gates_ok else 1


if __name__ == "__main__":
    sys.exit(main())
