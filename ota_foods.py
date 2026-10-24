#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ota_foods 0.1.0: CFIA's open ochratoxin A file (2012-2022) beyond spices, checked against
CFIA's own tables and against today's EU maximum levels.

Grades docs/ota-foods-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) tested 8,384 retail foods for ochratoxin A (OTA) in
2012-2018 and 2019-2022 and released the per-sample file on 2026-10-06 (Open Government Licence -
Canada; open.canada.ca dataset 37300d06-0887-4353-bc9b-4f030f1089a2). ota-spices 0.1.0 read its
778 spices. This reads the other 7,606 samples (cereals and infant cereals, coffee, cocoa, dried
fruit, licorice, nuts, seeds, pulses, soy, infant formula) for the first time. It

  (1) rebuilds every Table 2 figure CFIA printed for a category whose file labels map one to
      one onto it, and asks which mean each printed average is (the table note says positives
      only), plus the coffee rows of Table 5 and the infant formula rows of Tables 2 and 8,
      which contradict each other;
  (2) re-counts Health Canada's proposed maximum levels (grain-based foods 3, infant cereals
      0.5, wheat bran 7 ppb), which CFIA says 119 grain-based foods exceeded;
  (3) counts the samples above the EU maximum levels in force since 1 January 2023
      (Regulation (EU) 2022/1370, now Annex I of Regulation (EU) 2023/915), which CFIA's report
      does not use.

The file is SHA-256 pinned. Standard library only. Code Apache-2.0; derived data CC BY 4.0.
A reference comparison, not a compliance finding (Canada has no OTA limit in force for these
foods), not about any brand, and not individual dietary or medical advice.
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

DATASET = "37300d06-0887-4353-bc9b-4f030f1089a2"
RESOURCE = "ebc03414-5782-48e7-9294-30b37213479e"
FILE = "chem_ts_2012-2018__2019-22_ochratoxin_a_in_selected_foods.csv"
URLS = (
    f"https://open.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILE}",
    f"https://ouvert.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILE}",
)
API = "https://open.canada.ca/data/api/action/resource_show?id=" + RESOURCE
RAW_NAME = "cfia-ota-2012-2022.csv"
# Recorded by the names-only census job ota-census-v1 (2026-10-24) and by ota-spices 0.1.0.
SHA256 = "3d86e455cb3855cdea7fced6f72f30ab5d435467cb242a578d00fa91764fbe82"
N_ROWS = 8384
UNIT = "ng/g"
COMPONENT = "Ochratoxin A"

# Registered non-detect rule: a blank cell, a value starting with "<", a not-detected token or
# the number 0 is a non-detect (read as 0 ppb); any number above 0 is a detection.
ND_TOKENS = ("nd", "n.d.", "n/d", "not detected", "non détecté", "non detecte")

# ---------------------------------------------------------------------------
# CFIA's Table 2 categories, from the exact Product labels of the names-only census.
# ---------------------------------------------------------------------------
COCOA = ("Cocoa Powder",)
COFFEE = ("Coffee", "Coffee - Ground", "Coffee - Instant", "Beverage - Coffee")
SOY = ("Beverage - Soy", "Flour - Soy", "Tofu", "Bean - Soy", "Soy Products")
INFANT_FORMULA = ("Infant Formula - Soy", "Infant Formula - Dairy")
LICORICE = ("Licorice Products",)
NUTS = ("Nut - Pistachio", "Peanut", "Butter - Peanut", "Nut - Almond", "Butter - Blend",
        "Butter - Other Nut", "Nut - Hazelnut/Filbert", "Butter - Almond", "Butter - Cashew",
        "Nut - Walnut", "Nut - Cashew", "Nut - Pecan", "Nutmeats - Other", "Nut - Macadamia Nut",
        "Nut - Brazil Nut", "Nut - Chestnut", "Nut - PINE NUT")
SEEDS = ("Seed - Flax", "Seed - Pumpkin", "Seed - Sunflower", "Seed - Chia", "Seed - Hemp",
         "Seed - Sesame", "Seed - Poppy", "Seed - other")
DRIED_FRUIT = ("Dried Fruit", "Raisin", "Apricot", "Date", "Prune", "Fig", "Mango", "Currant",
               "Mixed Fruit", "Cranberry - dried", "Pineapple", "Berries - Other", "Blueberry",
               "Papaya", "Cranberry", "Apricot - Organic", "Cherry", "MANGO",
               "Melon - Cantaloupe", "Plantain", "Plum")
PULSES = ("Chickpea", "Pea", "Lentil", "Pea Products", "Lentil Products", "Flour - Chickpea",
          "Flour - Pea", "Bean Products", "Chickpea Products", "Bean - Kidney", "Flour - Lentil",
          "Flour - Bean", "Bean - Lima", "Bean - Pinto", "Bean - Black", "Bean - Other",
          "Chickpea Product - Hummus", "Bean - Fava")
SPICE_EXTRA = ("Pepper", "Pepper - Hot - Fresh", "Herb - Cilantro - Dried",
               "Herb - Marjoram - Fresh", "Celery")
# "Dried mixes" appears in two plans: the 2012 plan's two are soy products, the 2013 plan's one
# is coffee (CFIA's Table 5 lists dried coffee mixes). Everything else is grain-based.
DRIED_MIXES = "Dried mixes"
DRIED_MIXES_SOY_PLAN = "2012_SB447"
CATEGORY_LABELS = (("cocoa", COCOA), ("coffee", COFFEE), ("soy", SOY),
                   ("infant_formula", INFANT_FORMULA), ("licorice", LICORICE), ("nuts", NUTS),
                   ("seeds", SEEDS), ("dried_fruit", DRIED_FRUIT), ("pulses", PULSES))
CATEGORIES = ("cocoa", "coffee", "dried_fruit", "grain", "infant_formula", "licorice", "nuts",
              "pulses", "seeds", "soy", "spices")
# Category sizes under this map, from the names-only census (no value read).
EXPECTED_N = {"cocoa": 242, "coffee": 790, "dried_fruit": 696, "grain": 4124,
              "infant_formula": 192, "licorice": 140, "nuts": 148, "pulses": 635, "seeds": 279,
              "soy": 361, "spices": 777}
# Categories whose size equals CFIA's printed n exactly.
EXACT = ("cocoa", "coffee", "infant_formula", "licorice", "nuts", "seeds", "soy")

# CFIA report, Table 2, as printed: n, positives, minimum, maximum, average (ppb).
PRINTED = {
    "cocoa": (242, 219, "0.070", "6.6", "1.3"),
    "coffee": (790, 190, "0.043", "11", "0.96"),
    "dried_fruit": (695, 224, "0.041", "116", "1.4"),
    "grain": (4112, 2358, "0.040", "65", "0.51"),
    "infant_formula": (192, 13, "0.049", "11", "1.1"),
    "licorice": (140, 111, "0.042", "36", "2.1"),
    "nuts": (148, 31, "0.048", "1.2", "0.20"),
    "pulses": (647, 208, "0.040", "26", "1.2"),
    "seeds": (279, 87, "0.050", "65", "1.1"),
    "soy": (361, 51, "0.040", "3.0", "0.36"),
    "spices": (778, 517, "0.044", "1770", "22"),
}
PRINTED_TOTAL_POSITIVE = 4056
C2_CATS = ("cocoa", "coffee", "licorice", "nuts", "seeds", "soy")
C3_CATS = ("cocoa", "coffee", "dried_fruit", "licorice", "nuts", "seeds", "soy")
V1_CATS = ("coffee", "nuts", "soy")
V2_CATS = ("cocoa", "licorice", "seeds")
# CFIA report, Table 5 (coffee by survey year): plan code -> (n, maximum as printed).
TABLE5 = {"2013_SB447": (199, "11"), "2014_SB447": (141, "6.7"), "2015_SB447": (300, "9.1"),
          "2019_SB447": (150, "1.2")}
# CFIA report, Table 8 (infant formula): plan code -> (n, % positive, maximum as printed).
TABLE8 = {"2012_SB447": (148, 35, "0.89"), "2014_SB447": (44, 18, "0.46")}

# Health Canada's proposed maximum levels as CFIA applied them to grain-based foods (ppb).
HC_INFANT, HC_BRAN, HC_GRAIN = 0.5, 7.0, 3.0
PRINTED_HC_GRAIN = 119
C5_TOL = 3

# EU maximum levels for OTA (Reg. (EU) 2022/1370 = Annex I of Reg. (EU) 2023/915), ug/kg = ppb.
INFANT_CEREAL = ("Infant Food - Cereal",)
BREAKFAST = ("Cereal - Adult", "Cereal - Children")
BAKERY = ("Bakery Product - Cookie", "Bakery Product - Bread", "Bakery Product - Bagel",
          "Bakery Product - English Muffin", "Bakery Product - Bread - Other", "Baked Goods",
          "Crackers", "Chips - Corn", "Chips - Other")
OAT = ("Grain - Oat", "Flour - Oat", "Oatmeal", "Bran - Oat")
WHEAT = ("Flour - Wheat", "Bran - Wheat", "Wheat Products", "Couscous")
OTHER_DRIED = ("Dried Fruit", "Apricot", "Date", "Prune", "Mango", "Mixed Fruit",
               "Cranberry - dried", "Pineapple", "Berries - Other", "Blueberry", "Papaya",
               "Apricot - Organic", "Cherry", "MANGO", "Plum")
SEED5 = ("Nut - Pistachio", "Seed - Sunflower", "Seed - Pumpkin", "Seed - Hemp", "Bean - Soy")
# (id, EU entry, labels, maximum level)
EU_GROUPS = (
    ("infant_cereal", "processed cereal-based food for infants and young children",
     INFANT_CEREAL, 0.5),
    ("breakfast_cereal", "breakfast cereals (3.0 if with oilseeds, nuts or dried fruit; "
     "2.0 without)", BREAKFAST, 3.0),
    ("bakery_snacks", "bakery wares and cereal snacks without oilseeds, nuts or dried fruit",
     BAKERY, 2.0),
    ("oat", "products derived from cereals / cereals sold to the final consumer", OAT, 3.0),
    ("wheat", "products derived from cereals / cereals sold to the final consumer", WHEAT, 3.0),
    ("roasted_coffee", "roasted coffee beans and ground roasted coffee",
     ("Coffee", "Coffee - Ground"), 3.0),
    ("instant_coffee", "soluble coffee (instant coffee)", ("Coffee - Instant",), 5.0),
    ("cocoa_powder", "cocoa powder", ("Cocoa Powder",), 3.0),
    ("licorice", "liquorice confectionery (other than >97% extract)", LICORICE, 10.0),
    ("dried_vine_fruit", "dried vine fruit (currants, raisins, sultanas)",
     ("Raisin", "Currant"), 8.0),
    ("fig", "dried figs", ("Fig",), 8.0),
    ("other_dried_fruit", "other dried fruit", OTHER_DRIED, 2.0),
    ("pistachio_seeds_soybean", "pistachios to the final consumer; sunflower, pumpkin and hemp "
     "seeds; soybeans", SEED5, 5.0),
)
EU_LEVEL = {g[0]: g[3] for g in EU_GROUPS}
EU_LABELS = {g[0]: g[2] for g in EU_GROUPS}

# Pre-registered bounds (inclusive).
P1_DETECTED = (55, 65)
P3_INFANT_OVER = (25, 100)
P6_BREAKFAST_OVER = (0, 18)
P7_BAKERY_OVER = (1, 64)
P8_ROASTED_OVER = (1, 30)
P8_INSTANT_OVER = (1, 12)
P9_COCOA_OVER = (5, 45)
P10_LICORICE_OVER = (1, 8)
P11_OTHER_DRIED_SHARE = 0.08
P11_FIG_OVER = (0, 3)
P12_SEED5_OVER = (0, 6)
SPICE_MAX_RANGE = (1700.0, 1850.0)


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def parse_result(raw):
    """(ppb, detected, kind) for one Result cell under the registered non-detect rule."""
    s = (raw or "").strip()
    if not s:
        return 0.0, False, "blank"
    if s.startswith("<"):
        return 0.0, False, "lt"
    if s.lower() in ND_TOKENS:
        return 0.0, False, "nd_token"
    kind = "positive"
    try:
        v = float(s)
    except ValueError:
        if s.count(",") == 1 and "." not in s:
            try:
                v = float(s.replace(",", "."))
            except ValueError:
                return None, False, "bad"
            kind = "positive_comma"
        else:
            return None, False, "bad"
    if v != v or v < 0:
        return None, False, "bad"
    if v == 0:
        return 0.0, False, "zero"
    return v, True, kind


def category(product, plan):
    if product == DRIED_MIXES:
        return "soy" if plan == DRIED_MIXES_SOY_PLAN else "coffee"
    if product.lower().startswith("spice") or product in SPICE_EXTRA:
        return "spices"
    for name, labels in CATEGORY_LABELS:
        if product in labels:
            return name
    return "grain"


def matches(x, printed):
    """Does x round to the printed figure at the printed precision?"""
    if x is None:
        return False
    d = len(printed.split(".")[1]) if "." in printed else 0
    return abs(x - float(printed)) <= 0.5 * 10 ** (-d) + 1e-9


def verdict(mean_pos, mean_all, printed):
    p, a = matches(mean_pos, printed), matches(mean_all, printed)
    if p and a:
        return "both"
    if p:
        return "positives"
    if a:
        return "all"
    return "neither"


def within(x, bounds):
    return x is not None and bounds[0] <= x <= bounds[1]


def hc_limit(product):
    if product == "Infant Food - Cereal":
        return HC_INFANT
    if product == "Bran - Wheat":
        return HC_BRAN
    return HC_GRAIN


def n_over(rows, level):
    return sum(1 for r in rows if r["detected"] and r["ppb"] > level)


def with_labels(rows, labels):
    keep = set(labels)
    return [r for r in rows if r["product"] in keep]


def in_category(rows, cat):
    return [r for r in rows if r["category"] == cat]


def stats(rows):
    vals = sorted(r["ppb"] for r in rows if r["ppb"] is not None)
    det = sorted(r["ppb"] for r in rows if r["detected"])
    return {
        "n": len(rows), "n_detected": len(det),
        "min_detected": det[0] if det else None,
        "median_detected": statistics.median(det) if det else None,
        "mean_positives": statistics.fmean(det) if det else None,
        "mean_all": (sum(det) / len(vals)) if vals else None,
        "max": vals[-1] if vals else None,
    }


def top(rows):
    """The row with the highest result (first in file order on a tie), or None."""
    best = None
    for r in rows:
        if r["ppb"] is not None and (best is None or r["ppb"] > best["ppb"]):
            best = r
    return best


def find_columns(header):
    h = [c.replace("﻿", "").strip() for c in header]

    def first(test, what):
        for i, c in enumerate(h):
            if test(c):
                return i
        raise ValueError(f"no {what} column in {header!r}")

    return {
        "sample": first(lambda c: c.startswith("Sample"), "sample"),
        "function": first(lambda c: c == "Function", "function"),
        "origin": first(lambda c: c == "Origin", "origin"),
        "product": first(lambda c: c == "Product", "product"),
        "component": first(lambda c: c == "Component", "component"),
        "result": first(lambda c: c.startswith("Result"), "result"),
        "unit": first(lambda c: c.startswith("Unit"), "unit"),
        "plan": first(lambda c: c.startswith("Plan Code"), "plan code"),
    }


def _bump(d, k):
    d[k] = d.get(k, 0) + 1


def parse_text(text):
    """(rows, check) from the decoded CSV text."""
    table = list(csv.reader(io.StringIO(text)))
    header = table[0]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    col = find_columns(header)

    def cell(r, k):
        i = col[k]
        return r[i] if i < len(r) else ""

    rows, kinds, units, comps, decimals = [], {}, {}, {}, {}
    for r in body:
        raw = cell(r, "result")
        ppb, det, kind = parse_result(raw)
        _bump(kinds, kind)
        if det:
            s = raw.strip()
            _bump(decimals, str(len(s.split(".")[1]) if "." in s else 0))
        _bump(units, cell(r, "unit"))
        _bump(comps, cell(r, "component"))
        product, plan = cell(r, "product"), cell(r, "plan")
        rows.append({"sample": cell(r, "sample"), "function": cell(r, "function"),
                     "origin": cell(r, "origin"), "product": product, "plan": plan,
                     "raw": raw, "ppb": ppb, "detected": det,
                     "category": category(product, plan)})
    check = {"n_rows": len(rows), "distinct_samples": len({r["sample"] for r in rows}),
             "units": units, "components": comps, "result_kinds": kinds,
             "positive_decimals": decimals}
    return rows, check


def category_counts(rows):
    out = {}
    for r in rows:
        _bump(out, r["category"])
    return out


def gate(rows, check, sha_ok):
    cats = category_counts(rows)
    smax = top(in_category(rows, "spices"))
    checks = {
        "sha256": bool(sha_ok),
        "rows": check["n_rows"] == N_ROWS and check["distinct_samples"] == N_ROWS,
        "units": check["units"] == {UNIT: N_ROWS},
        "component": check["components"] == {COMPONENT: N_ROWS},
        "all_parsed": check["result_kinds"].get("bad", 0) == 0,
        "categories": cats == EXPECTED_N,
        "known_spice_max": (smax is not None and smax["product"] == "Spice - Paprika"
                            and within(smax["ppb"], SPICE_MAX_RANGE)),
    }
    return all(checks.values()), {"checks": checks, "categories": cats,
                                  "result_kinds": check["result_kinds"]}


def category_table(rows):
    table = {}
    for cat in CATEGORIES:
        s = stats(in_category(rows, cat))
        n, pos, pmin, pmax, pavg = PRINTED[cat]
        s.update({"printed_n": n, "printed_positives": pos, "printed_min": pmin,
                  "printed_max": pmax, "printed_average": pavg,
                  "verdict": verdict(s["mean_positives"], s["mean_all"], pavg)})
        table[cat] = s
    return table


def eu_table(rows):
    out = {}
    for gid, entry, labels, level in EU_GROUPS:
        sub = with_labels(rows, labels)
        s = stats(sub)
        k = n_over(sub, level)
        out[gid] = {"entry": entry, "level": level, "n": s["n"], "n_detected": s["n_detected"],
                    "n_over": k, "share_over": (k / s["n"]) if s["n"] else None,
                    "max": s["max"]}
    return out


def hc_table(rows):
    grain = in_category(rows, "grain")
    over = [r for r in grain if r["detected"] and r["ppb"] > hc_limit(r["product"])]
    infant = sum(1 for r in over if r["product"] == "Infant Food - Cereal")
    bran = sum(1 for r in over if r["product"] == "Bran - Wheat")
    vine = with_labels(rows, ("Raisin", "Currant"))
    return {"n_grain": len(grain), "n_over": len(over), "infant_cereal": infant,
            "wheat_bran": bran, "other_grain": len(over) - infant - bran,
            "n_over_at_or_above": sum(1 for r in grain if r["detected"]
                                      and r["ppb"] >= hc_limit(r["product"])),
            "vine_fruit_over_10": n_over(vine, 10.0),
            "vine_fruit_at_or_above_10": sum(1 for r in vine if r["detected"]
                                             and r["ppb"] >= 10.0)}


def by_plan(rows):
    out = {}
    for r in rows:
        out.setdefault(r["plan"], []).append(r)
    return out


def grade(rows, check, sha_ok):
    ok, gobs = gate(rows, check, sha_ok)
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": ok, "observed": gobs,
              "text": "SHA-256, 8,384 rows and distinct samples, unit ng/g and component "
                      "Ochratoxin A on every row, every result parsed, category sizes as "
                      "registered, and the published spice maximum (a paprika, 1,700-1,850 ppb)"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": ok, "met": bool(ok and met),
                      "text": text, "observed": observed})

    ct = category_table(rows)
    eu = eu_table(rows)
    hc = hc_table(rows)

    # C1-C6: CFIA's printed figures.
    n_det = sum(1 for r in rows if r["detected"])
    add("C1", "consistency", "4,056 of the 8,384 samples are detected under the registered "
        "non-detect rule", {"n_detected": n_det, "printed": PRINTED_TOTAL_POSITIVE},
        n_det == PRINTED_TOTAL_POSITIVE)
    c2 = {c: {"file": ct[c]["n_detected"], "printed": ct[c]["printed_positives"]}
          for c in C2_CATS}
    add("C2", "consistency", "positives equal Table 2 for cocoa, coffee, licorice, nuts, seeds "
        "and soy", c2, all(v["file"] == v["printed"] for v in c2.values()))
    c3 = {c: {"file": ct[c]["max"], "printed": ct[c]["printed_max"],
              "match": matches(ct[c]["max"], ct[c]["printed_max"])} for c in C3_CATS}
    add("C3", "consistency", "maxima equal Table 2 at printed precision for cocoa, coffee, dried "
        "fruit, licorice, nuts, seeds and soy", c3, all(v["match"] for v in c3.values()))
    c4 = {c: {"file": ct[c]["min_detected"], "printed": ct[c]["printed_min"],
              "match": matches(ct[c]["min_detected"], ct[c]["printed_min"])} for c in C3_CATS}
    add("C4", "consistency", "lowest detected values equal Table 2 minima at printed precision "
        "for the same seven categories", c4, all(v["match"] for v in c4.values()))
    add("C5", "consistency", "Health Canada's proposed levels (infant cereal 0.5, wheat bran 7, "
        "other grain-based foods 3 ppb; above the level) flag 116-122 grain-based foods "
        "(CFIA: 119)", hc, abs(hc["n_over"] - PRINTED_HC_GRAIN) <= C5_TOL)
    plans = by_plan(in_category(rows, "coffee"))
    c6 = {}
    for plan, (n, pmax) in TABLE5.items():
        s = stats(plans.get(plan, []))
        c6[plan] = {"n": s["n"], "printed_n": n, "max": s["max"], "printed_max": pmax,
                    "match": s["n"] == n and matches(s["max"], pmax)}
    extra = sorted(p for p in plans if p not in TABLE5)
    add("C6", "consistency", "coffee by plan year equals Table 5 (n and maximum for 2013, 2014, "
        "2015, 2019) and no coffee sits in another plan", {"years": c6, "other_plans": extra},
        all(v["match"] for v in c6.values()) and not extra)

    # V1-V2: which mean each printed average is.
    v1 = {c: {"verdict": ct[c]["verdict"], "mean_positives": ct[c]["mean_positives"],
              "mean_all": ct[c]["mean_all"], "printed": ct[c]["printed_average"]}
          for c in V1_CATS}
    add("V1", "verdict", "the printed coffee, nuts and soy averages are positives-only means",
        v1, all(v["verdict"] in ("positives", "both") for v in v1.values()))
    v2 = {c: {"verdict": ct[c]["verdict"], "mean_positives": ct[c]["mean_positives"],
              "mean_all": ct[c]["mean_all"], "printed": ct[c]["printed_average"]}
          for c in V2_CATS}
    add("V2", "verdict", "the printed cocoa, licorice and seeds averages are positives-only "
        "means", v2, all(v["verdict"] in ("positives", "both") for v in v2.values()))

    # P1-P12: blind predictions.
    inf = in_category(rows, "infant_formula")
    s_inf = stats(inf)
    dairy_det = sum(1 for r in inf if r["product"] == "Infant Formula - Dairy" and r["detected"])
    inf_plans = {p: stats(v) for p, v in by_plan(inf).items()}
    add("P1", "prediction", "infant formula follows Table 8, not Table 2: 55-65 detected, "
        "maximum 0.89 at printed precision, no dairy formula detected",
        {"n": s_inf["n"], "n_detected": s_inf["n_detected"], "max": s_inf["max"],
         "dairy_detected": dairy_det, "by_plan": inf_plans, "table8": TABLE8,
         "table2": PRINTED["infant_formula"]},
        within(s_inf["n_detected"], P1_DETECTED) and matches(s_inf["max"], "0.89")
        and dairy_det == 0)
    t15 = top(plans.get("2015_SB447", []))
    tall = top(in_category(rows, "coffee"))
    add("P2", "prediction", "CFIA's sentence about a 9.1 ppb ground coffee is the 2015 survey's "
        "maximum: the 2015 top coffee is 'Coffee - Ground' at 9.1, and the overall coffee maximum "
        "is a 2013 sample",
        {"top_2015": None if t15 is None else {"product": t15["product"], "ppb": t15["ppb"]},
         "top_all": None if tall is None else {"product": tall["product"], "ppb": tall["ppb"],
                                               "plan": tall["plan"]}},
        t15 is not None and t15["product"] == "Coffee - Ground" and matches(t15["ppb"], "9.1")
        and tall is not None and tall["plan"] == "2013_SB447")
    add("P3", "prediction", "25-100 of the 409 infant cereals exceed the EU and Health Canada "
        "level of 0.5 ppb", eu["infant_cereal"], within(eu["infant_cereal"]["n_over"],
                                                         P3_INFANT_OVER))
    add("P4", "prediction", "infant cereals are more than half of the grain-based foods over "
        "Health Canada's proposed levels", hc, hc["infant_cereal"] * 2 > hc["n_over"])
    so = eu["oat"]["share_over"] or 0.0
    sw = eu["wheat"]["share_over"] or 0.0
    add("P5", "prediction", "a larger share of oat products than of wheat products exceeds "
        "3 ppb", {"oat": eu["oat"], "wheat": eu["wheat"]}, so > sw)
    add("P6", "prediction", "at most 18 of the 609 breakfast cereals exceed 3 ppb",
        eu["breakfast_cereal"], within(eu["breakfast_cereal"]["n_over"], P6_BREAKFAST_OVER))
    add("P7", "prediction", "1-64 of the 1,274 bakery wares and cereal snacks exceed the EU's "
        "2 ppb", eu["bakery_snacks"], within(eu["bakery_snacks"]["n_over"], P7_BAKERY_OVER))
    add("P8", "prediction", "1-30 of the 601 roasted coffees exceed the EU's 3 ppb and 1-12 of "
        "the 56 instant coffees exceed its 5 ppb",
        {"roasted": eu["roasted_coffee"], "instant": eu["instant_coffee"]},
        within(eu["roasted_coffee"]["n_over"], P8_ROASTED_OVER)
        and within(eu["instant_coffee"]["n_over"], P8_INSTANT_OVER))
    add("P9", "prediction", "5-45 of the 242 cocoa powders exceed the EU's 3 ppb",
        eu["cocoa_powder"], within(eu["cocoa_powder"]["n_over"], P9_COCOA_OVER))
    add("P10", "prediction", "1-8 of the 140 licorice products exceed the EU's 10 ppb for "
        "liquorice confectionery", eu["licorice"],
        within(eu["licorice"]["n_over"], P10_LICORICE_OVER))
    od = eu["other_dried_fruit"]
    add("P11", "prediction", "at most 8% of the 441 other dried fruits exceed the EU's 2 ppb, "
        "and at most 3 of the 48 dried figs exceed 8 ppb", {"other": od, "fig": eu["fig"]},
        od["share_over"] is not None and od["share_over"] <= P11_OTHER_DRIED_SHARE
        and within(eu["fig"]["n_over"], P11_FIG_OVER))
    add("P12", "prediction", "at most 6 of the 214 pistachios, sunflower, pumpkin and hemp seeds "
        "and soybeans exceed the EU's 5 ppb", eu["pistachio_seeds_soybean"],
        within(eu["pistachio_seeds_soybean"]["n_over"], P12_SEED5_OVER))
    return preds, ct, eu, hc


def descriptive(rows, check):
    grain = in_category(rows, "grain")
    other_cereal = [r for r in grain
                    if r["product"] not in set(INFANT_CEREAL + BREAKFAST + BAKERY)]
    bk = with_labels(rows, BREAKFAST)
    coffee_plans = {}
    for p, v in by_plan(in_category(rows, "coffee")).items():
        s = stats(v)
        s["pct_detected"] = round(100.0 * s["n_detected"] / s["n"]) if s["n"] else None
        coffee_plans[p] = s
    non_spice = [r for r in rows if r["category"] != "spices"]
    eu_rows = []
    for gid, _, labels, level in EU_GROUPS:
        eu_rows.extend((r, level) for r in with_labels(rows, labels))
    return {
        "format_census": {"result_kinds": check["result_kinds"],
                          "positive_decimals": check["positive_decimals"]},
        "breakfast_cereal_over_2": n_over(bk, 2.0),
        "other_cereal_products_over_3": {"n": len(other_cereal),
                                         "n_over": n_over(other_cereal, 3.0)},
        "coffee_by_plan": coffee_plans,
        "non_spice": {"n": len(non_spice),
                      "n_detected": sum(1 for r in non_spice if r["detected"])},
        "eu_all_groups": {"n": len(eu_rows),
                          "n_over": sum(1 for r, lv in eu_rows if r["detected"] and r["ppb"] > lv)},
    }


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _fetch(url, tries=3, pause=10):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-ota-foods"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(data_dir):
    """Raw bytes of the pinned file, verified against its SHA-256 before any parse."""
    path = os.path.join(data_dir, RAW_NAME) if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == SHA256:
            return raw, "data-volume"
    urls = list(URLS)
    try:
        meta = json.loads(_fetch(API, tries=2, pause=5).decode("utf-8"))
        if meta.get("success") and meta["result"].get("url"):
            urls.insert(0, meta["result"]["url"])
    except Exception as exc:  # noqa: BLE001 - fall back to the pinned urls
        print(f"  resource_show failed: {exc}")
    errors = []
    for url in urls:
        try:
            raw = _fetch(url, tries=2, pause=5)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        if _sha(raw) != SHA256:
            errors.append(f"{url}: SHA-256 {_sha(raw)} != {SHA256}")
            continue
        if path:
            try:
                os.makedirs(data_dir, exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(raw)
            except OSError:
                pass
        return raw, url
    raise RuntimeError("no verified copy: " + "; ".join(errors))


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
CAT_FIELDS = ["category", "n", "n_detected", "min_detected", "median_detected",
              "mean_positives", "mean_all", "max", "printed_n", "printed_positives",
              "printed_min", "printed_max", "printed_average", "verdict"]
EU_FIELDS = ["group", "entry", "level", "n", "n_detected", "n_over", "share_over", "max"]
SAMPLE_FIELDS = ["sample", "plan", "function", "origin", "product", "category", "eu_group",
                 "eu_level", "result_raw", "ota_ppb", "detected"]


def _r(x):
    return "" if x is None else (round(x, 4) if isinstance(x, float) else x)


def eu_group_of(product):
    for gid, _, labels, level in EU_GROUPS:
        if product in labels:
            return gid, level
    return "", ""


def write_outputs(out_dir, rows, preds, ct, eu, hc, desc, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "ota_foods_categories.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(CAT_FIELDS)
        for cat in CATEGORIES:
            w.writerow([cat] + [_r(ct[cat][k]) for k in CAT_FIELDS[1:]])
    with open(os.path.join(out_dir, "ota_foods_eu.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(EU_FIELDS)
        for gid, _, _, _ in EU_GROUPS:
            w.writerow([gid] + [_r(eu[gid][k]) for k in EU_FIELDS[1:]])
    # Per-sample values for the non-spice samples (spices were published by ota-spices 0.1.0).
    with open(os.path.join(out_dir, "ota_foods_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SAMPLE_FIELDS)
        for r in rows:
            if r["category"] == "spices":
                continue
            gid, level = eu_group_of(r["product"])
            w.writerow([r["sample"], r["plan"], r["function"], r["origin"], r["product"],
                        r["category"], gid, level, r["raw"], _r(r["ppb"]), int(r["detected"])])
    result = {"study": "ota-foods", "version": VERSION, "predictions": preds,
              "categories": ct, "eu": eu, "health_canada": hc, "descriptive": desc,
              "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "ota_foods_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "ota_foods_grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the ota-foods pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw, source = load(args.data_dir)
    text, enc = decode(raw)
    rows, check = parse_text(text)
    preds, ct, eu, hc = grade(rows, check, _sha(raw) == SHA256)
    desc = descriptive(rows, check)
    provenance = {"dataset": DATASET, "resource": RESOURCE, "sha256": SHA256, "bytes": len(raw),
                  "source": source, "encoding": enc}
    result = write_outputs(args.out_dir, rows, preds, ct, eu, hc, desc, provenance)
    print(json.dumps({"version": VERSION,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "gate": preds[0]["observed"]["checks"],
                      "format_census": desc["format_census"]}, indent=2))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
