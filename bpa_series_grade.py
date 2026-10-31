#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""bpa-series 0.1.0 grader: seven open CFIA bisphenol A files (2009-10 to 2017-18) against the
figures CFIA printed for them (value items V1-V7, D1 and a dates-only item T1 of
docs/bpa-series-0.1.0-prereg.md).

Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes each survey's per-sample CSV on
open.canada.ca (Open Government Licence - Canada) and a report page that gives results in ppb.
The 2009-10 file reports ng/g (already ppb); the six later files report ug/g, so a value x is
1000 * x ppb. Each file is gated on structure facts taken from the names-only census
(docs/bpa-series-0.1.0-census.md) run before any result value was read: byte size, columns, rows,
samples, components per sample, one unit, one plan code, the known product labels and a value
rule. The label-to-category maps below are exactly the ones fixed in that census note. Standard
library only. Code Apache-2.0; derived data CC BY 4.0. Not a compliance finding, not about any
brand, and not dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.request

VERSION = "0.1.0"
COMPONENTS = ("Bisphenol A", "Bisphenol A Diglycidyl Ether", "Bisphenol F", "Bisphenol S")
KEYS = ("bpa", "badge", "bpf", "bps")
SHORT = dict(zip(COMPONENTS, KEYS))
COMP_KEY = {c.lower(): c for c in COMPONENTS}
NG = "ng/g"
UG = "µg/g"
PPB_PER = {NG: 1.0, UG: 1000.0}                 # ng/g is ppb; ug/g -> ppb
ID_RE = re.compile(r"^C?\d{4}[A-Z]+\d{4,6}D?$")
BPA_ONLY = COMPONENTS[:1]
TARGETS = {
    "bpa-2009": {
        "dataset": "9846894f-16f2-4834-952a-2e66a162719b",
        "resource": "4ff8f342-d0ea-45a4-9cf5-6f5220e84925",
        "path": ("cfia_acia-1329-v2-fsap_chem_ts_-_2009-10_-_bisphenol-a_in_infant_food_and_"
                 "formula_-_sb451_bpha_-.csv"),
        "size": 32261, "md5": "7eacc09417bd528dcca26b8009b824f5",
        "rows": 200, "samples": 200, "plan": "2009_SB451", "unit": NG, "components": BPA_ONLY},
    "bpa-2010": {
        "dataset": "ee1d2ca0-18a4-457a-9978-59d20cc6e191",
        "resource": "ab208fba-5551-4d16-87a7-b810a73dbcba",
        "path": ("cfia_acia-1330-v2-fsap_chem_ts_-_2010-11_-_bpa_in_infant_formulae_and_foods_-_"
                 "sb451_bpha_-_open_.csv"),
        "size": 39475, "md5": "56b061a4596746dc9736afabac5fbc2a",
        "rows": 234, "samples": 234, "plan": "2010_SB451", "unit": UG, "components": BPA_ONLY},
    "bpa-2011": {
        "dataset": "3c1749ef-d6a2-400d-a096-8dd5a13507b2",
        "resource": "86eb4b33-11b4-475d-a0ff-3f32a611a73e",
        "path": ("cfia_acia-1331-v2-fsap_chem_ts_-_2011-12_-_bpa_in_canned_foods_-_sb451_bpha_-_"
                 "open_data.csv"),
        "size": 69780, "md5": "afae926b6784187c1b15c19f16c928ef",
        "rows": 403, "samples": 403, "plan": "2011_SB451", "unit": UG, "components": BPA_ONLY},
    "bpa-2012": {
        "dataset": "d0539c7a-90ea-4874-a66d-7c75f6cd814d",
        "resource": "c2f6fb46-4c3f-4c23-acfb-4badfc70c835",
        "path": ("cfia_acia-1332-v2-fsap_chem_ts_-_2012-13_-_bpa_in_selected_foods_-_sb451_bpha_-_"
                 "open_data.csv"),
        "size": 87982, "md5": "5da0bea9d42e56c68b0423b63cfacb96",
        "rows": 576, "samples": 576, "plan": "2012_SB451", "unit": UG, "components": BPA_ONLY},
    "bpa-2013": {
        "dataset": "eba65062-23e4-4530-90bd-767d0c04c079",
        "resource": "755045de-88a0-4ad7-8015-e630d9ca8fcd",
        "path": ("cfia_acia-1333-v2-fsap_chem_ts_-_2013-14_-_bpa_in_canned_foods_-_sb451_bpha_-_"
                 "open_data.csv"),
        "size": 94214, "md5": "",
        "rows": 391, "samples": 391, "plan": "2013_SB451", "unit": UG, "components": BPA_ONLY},
    "bpa-2016": {
        "dataset": "10478dd5-7ce8-4542-887c-572f0bfe0c8c",
        "resource": "26aa5b60-08a4-4bad-bbdc-17527e6698a3",
        "path": ("cfia-acia-1287-open-data-for-chemistry-targeted-surveys-2016-17-bisphenol-and-"
                 "bpa-alternatives-i.csv"),
        "size": 395585, "md5": "",
        "rows": 1964, "samples": 491, "plan": "2016_SB451", "unit": UG,
        "components": COMPONENTS},
    "bpa-2017": {
        "dataset": "15b7f392-56ef-4772-a8e5-aba2c3b0b980",
        "resource": "4dfc8b9a-0b97-4c76-b3e4-07879a8e0c88",
        "path": ("cfia_acia-1263-open-data-for-chemistry-targeted-surveys-2017-18-bisphenol-a-and-"
                 "bpa-alternatives.csv"),
        "size": 339854, "md5": "12a495421962033f4c723492e49682fa",
        "rows": 1872, "samples": 468, "plan": "2017_SB451", "unit": UG,
        "components": COMPONENTS},
}
NAMES = tuple(TARGETS)


# File label -> report category, exactly as fixed in docs/bpa-series-0.1.0-census.md before any
# value was read ("every other label" groups are written out from the census label lists).
def _map(**groups):
    return {label: g for g, labels in groups.items() for label in labels}


FORMULA = ("Infant Formula - Dairy", "Infant Formula - Soy")
PIE = ("Pie Filling - Blueberry", "Pie Filling - Cherry", "Pie Filling - Other",
       "Pie Filling - Pumpkin", "Pie Filling - apple")
TYPE_OF = {
    "bpa-2009": _map(food=("Infant Food",), formula=("Infant Formula",)),
    "bpa-2010": _map(
        formula=FORMULA, juice=("Juice - Apple", "Juice - Grape", "Nectar - Pear"),
        fruit=("Apricot", "Mixed Fruit", "Peach", "Pear", "Pineapple", "Strawberry"),
        other=("Cereal - Other", "Meat & Vegetable")),
    "bpa-2011": _map(
        pasta=("Pasta - Canned",), soup=("Soup",),
        fruit=("Banana", "Longan", "Lychee", "Mango", "Mixed Fruit", "Orange", "Papaya", "Peach",
               "Pear", "Pineapple", "Plum", "Preserve - Apricot", "Preserve - Blueberry"),
        juice=("Beverage - Fruit", "Beverage - Other", "Beverage - Tea", "Juice - Apple",
               "Juice - Tomato", "Juice/Nectar - Other", "juice - pineapple"),
        veg=("Asparagus", "Bamboo Shoot", "Bean", "Bean - Black", "Bean - Fava",
             "Bean - Green/Yellow", "Bean - Kidney", "Bean - Other", "Bean - wax", "Beet",
             "Carrot", "Chickpea", "Corn", "Kale", "Mixed Vegetables", "Mushroom", "Pea",
             "Pea - Organic", "Pea - Sugar", "Potato", "Sweet Potato", "Tomato",
             "Tomato - Organic")),
    "bpa-2012": _map(
        bev=("Beverage - Fruit", "Juice - Apple", "Juice - Blend", "Juice - Other",
             "Juice - Vegetable", "Juice - other", "Nectar - Mango", "Nectar - Other",
             "juice - pineapple"),
        coconut=("Coconut Milk",),
        fruit=("Apricot", "Grapefruit", "JackFruit", "Longan", "Lychee", "Mango", "Mixed Fruit",
               "Orange", "Orange - Organic", "Papaya", "Peach", "Pear", "Pineapple",
               "Pineapple - Organic", "Strawberry"),
        curry=("Curry",), pasta=("Pasta - Canned",), soup=("Soup",),
        veg=("Artichoke Heart", "Asparagus", "Bamboo Shoot", "Bean", "Bean - Organic", "Beet",
             "Cabbage", "Callaloo", "Chickpea products", "Corn", "Cucumber", "Heart of Palm",
             "Lentils products", "Mixed Vegetables", "Mushroom", "Okra", "Pea", "Pea - Organic",
             "Pea products", "Pepper - Pickled Hot", "Salsa", "Sauces", "Tomatillo", "Tomato",
             "Water Chestnut")),
    "bpa-2013": _map(
        bev=("Beverage - Fruit", "Beverage - Other", "Beverage - Sport", "Energy Drink",
             "Soft Drink", "Juice - Apple", "Juice - Blend", "Juice - Mixed", "Juice - Other",
             "juice - pineapple"),
        coconut=("Coconut Milk",),
        fruit=("Cherry", "Gooseberry", "JackFruit", "Lychee", "Mango", "Mango - Organic",
               "Misc Fruit", "Mixed Fruit", "Orange", "Papaya", "Peach", "Pineapple"),
        formula=FORMULA, pasta=("Pasta - Canned",), pie=PIE, curry=("Sauces",), soup=("Soup",),
        veg=("Artichoke Heart", "Asparagus", "Bamboo Shoot", "Bean Products",
             "Chickpea Products", "Corn", "Heart of Palm", "Misc Vegetables", "Mixed Vegetables",
             "Mushroom")),
    "bpa-2016": _map(
        bev=("Beverage - Fruit", "Beverage - Other", "Beverage - Sport", "Energy Drink",
             "Soft Drink", "Juice - Apple", "Juice - Blend", "Juice - Orange", "Juice - Other",
             "Juice - Tomato", "Juice - Vegetable", "Nectar - Guava", "Nectar - Mango",
             "Nectar - Other", "juice - pineapple"),
        coconut=("Coconut Milk",),
        fruit=("Apricot", "Grapefruit", "JackFruit", "Lychee", "Mango", "Mixed Fruit", "Orange",
               "Peach", "Pear", "Pineapple", "Pineapple - Organic"),
        formula=FORMULA, pasta=("Pasta - Canned",), pie=PIE, sauce=("Sauces", "Tomato Sauce"),
        soup=("Soup",),
        veg=("Artichoke", "Artichoke Heart", "Asparagus", "Bamboo Shoot", "Bean",
             "Bean - Green/Yellow", "Bean - wax", "Beet", "Carrot", "Corn", "Mixed Vegetables",
             "Mushroom", "Pea", "Spinach", "Yam")),
    "bpa-2017": _map(
        meat=("Meat - Canned", "Chicken", "Ham", "Beef", "Pork"),
        fish=("Fish/Seafood - Canned", "Tuna", "Salmon", "Fish", "Mackerel", "Crab", "Herring",
              "Mussel", "Oyster", "Shrimp")),
}
TYPES = {name: tuple(dict.fromkeys(m.values())) for name, m in TYPE_OF.items()}

# Printed figures (ppb; positives only), transcribed in the pre-registration.
# Rows: category -> (n, positive, min, max, average).
V1_2009 = {"k": 82, "food_k": 9, "min": "1.4", "max": "9.6"}
V3_GROUPS = {"pasta": ("Pasta - Canned",), "carrot": ("Carrot",),
             "pea": ("Pea", "Pea - Organic", "Pea - Sugar"), "corn": ("Corn",)}
V3_EXPECTED = {"pasta": 1, "carrot": 3, "pea": 1, "corn": 1}
TABLE5_2012 = {"bev": (72, 2, "5.9", "12.0", "9.0"), "coconut": (46, 17, "5.4", "381", "63.0"),
               "fruit": (73, 1, "8.6", "8.6", "8.6"), "curry": (24, 3, "88.0", "298", "227"),
               "veg": (144, 30, "5.5", "103", "34.0"), "pasta": (52, 52, "5.2", "157", "21.9"),
               "soup": (98, 39, "5.7", "277", "76.2")}
V4_ROWS = ("bev", "coconut", "fruit", "curry", "veg")
V4_MIN_FULL = 4
V4 = {"k": 145, "min": "5.2", "max": "381", "pasta_soup_k": 92}
TABLE5_2013 = {"bev": (97, 34, "1.1", "190", "13.6"), "coconut": (13, 12, "4.8", "253", "84.2"),
               "fruit": (38, 19, "1.0", "53.6", "6.7"), "formula": (55, 28, "1.1", "12.5", "4.8"),
               "pasta": (45, 45, "6.7", "93.0", "19.5"), "pie": (20, 8, "3.4", "47.3", "22.3"),
               "curry": (5, 5, "6.2", "226", "75.5"), "soup": (48, 42, "1.2", "307", "42.6"),
               "veg": (70, 59, "1.1", "565", "31.8")}
V5_MIN_FULL = 7
V5 = {"k": 252, "min": "1.0", "max": "565"}
TABLE2_2016 = {"bev": (135, 91, "1.7", "639", "40.8"), "coconut": (14, 12, "24.2", "1370", "306"),
               "fruit": (50, 34, "2.0", "1160", "62.1"), "formula": (66, 46, "2.3", "44.0", "8.7"),
               "pasta": (48, 39, "1.6", "270", "86.7"), "pie": (20, 16, "8.5", "2240", "281"),
               "sauce": (13, 5, "1.9", "1120", "228"), "soup": (46, 39, "2.5", "410", "107"),
               "veg": (72, 58, "5.3", "751", "139")}
V6_GRADABLE = ("coconut", "fruit", "pie", "veg")
VEG_2016_AVGS = ("139", "138")                  # Table 2 vs the results text; no prediction
V6 = {"k": 361, "avg_all": "87.2"}
V6_UNGRADED = {"canned_k": 340, "canned_avg": "91.6", "other_k": 21, "other_avg": "15.2"}
V6_TOP = {"pie": ("2240", "530", "Pie Filling - Pumpkin"), "coconut": ("1370", "478", None),
          "fruit": ("1160", "186", "Pineapple"), "sauce": ("1120", "7.5", None)}
# Table 4 (canned only; reported over all packaging, descriptive): analyte -> category ->
# (positive, min, max, average).
TABLE4_2016 = {"badge": {"coconut": (4, "16.1", "224", "109"),
                         "sauce": (1, "14.3", "14.3", "14.3")},
               "bpf": {"veg": (3, "2.4", "3.8", "3.3")}, "bps": {}}
TABLE2_2017 = {"meat": (231, 170, "1.20", "407", "35.6"),
               "fish": (237, 159, "1.29", "1480", "54.7"),
               "all": (468, 329, "1.20", "1480", "44.8")}
MEAT_AVG_ALTERNATIVES = ("34.6", "46.6")
ALT_2017 = {"badge": {"meat": (53, "0.98", "46.2", "10.8"), "fish": (19, "0.97", "53.2", "8.02")},
            "bpf": {"meat": (68, "1.01", "63.6", "15.3")},
            "bps": {"meat": (1, "1.79", "1.79", "1.79")}}
V7 = {"top": ("1480", "567"), "bps_k": 1, "bps": "1.79", "badge_k": 72, "badge_with_bpa": 69,
      "bpf_k": 68, "badge_avg": "10.1"}
# D1: categories shared by 2012-13 and 2013-14, cut at a common 5.2 ppb.
D1_CUT = 5.2
D1_RATIO = 1.5
D1_OF = {"veg": "veg", "fruit": "fruit", "bev": "bev", "pasta": "pastasoup",
         "soup": "pastasoup", "coconut": "coconut", "curry": "curry"}
D1_LEFT_OUT_2013 = ("Beverage - Sport", "Energy Drink", "Soft Drink")
T1_START = datetime.date(2009, 10, 1)
COLS = ("sample", "component", "value", "unit", "product")
CELLS = ("detected", "min", "max", "avg")


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def clean(cell):
    """A cell without BOM, edge spaces or repeated inner spaces, in NFC form, with en and em
    dashes read as hyphens."""
    s = unicodedata.normalize("NFC", (cell or "").replace("﻿", ""))
    s = s.replace("–", "-").replace("—", "-")
    return " ".join(s.split())


def head(name):
    """Normalised English part of a header cell: 'PLAN_CODE' -> 'plan code'."""
    h = clean(name).strip('"').lower().replace("_", " ")
    return " ".join(h.split("/")[0].split())


def unit_label(raw):
    """The unit cell, with a Greek mu read as the micro sign."""
    return clean(raw).replace("μ", "µ")


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


ND_TOKENS = {"ND", "NOT DETECTED", "NON DETECTED", "NOTDETECTED", "BRL", "<LOD", "<LOQ",
             "<MDL", "<RL"}


def parse_value(raw):
    """(value, kind) for one result cell. A number above 0 is 'det'. A 0, a '<' with a number
    >= 0 or a not-detected token is 'nd'. Anything else (blank, other text, a negative) is
    'bad' and fails the gate."""
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


def component(text):
    """The canonical component name for a cell (English part), else None."""
    return COMP_KEY.get(clean(text).lower().split("/")[0].strip())


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def parse_date(raw):
    """A date from 'M/D/YYYY' or 'YYYY-MM-DD' (a time part is ignored); None otherwise."""
    s = clean(raw)
    try:
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})\b", s)
        if m:
            return datetime.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})\b", s)
        if m:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
    return None


def id_number(sid):
    """The trailing sample number of an ID ('2009BPA00065' -> 65); None if there is none."""
    m = re.search(r"(\d+)D?$", sid)
    return int(m.group(1)) if m else None


def find_columns(header):
    """Map roles to column indexes by the English header (None if absent)."""
    h = [head(c) for c in header]

    def pick(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    return {
        "sample": pick(lambda c: c.startswith("sample") and "type" not in c and "date" not in c),
        "component": pick(lambda c: c.startswith("component")),
        "value": pick(lambda c: c.startswith("maxofamount") or c.startswith("amount")
                      or c.startswith("result")),
        "unit": pick(lambda c: c.startswith("report unit") or c.startswith("unit")),
        "product": pick(lambda c: c.startswith("product")),
        "origin": pick(lambda c: c.startswith("origin")),
        "function": pick(lambda c: c.startswith("function")),
        "region": pick(lambda c: c.startswith("region")),
        "date": pick(lambda c: c.startswith("date sampled")),
        "plan": pick(lambda c: c.startswith("plan code") or c == "plan"),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def _cell(r, i):
    return r[i] if i is not None and i < len(r) else ""


def mask(raw):
    return "".join("#" if ch.isdigit() else ch for ch in clean(raw))


def empty_census(col=None):
    return {"columns": col or {}, "rows": 0, "units": {}, "plans": {}, "kinds": {},
            "components": {}, "bad_shapes": [], "unknown_components": 0, "samples": 0,
            "products": {}, "rows_per_sample": {}, "missing": {}, "repeated": {},
            "ids_bad": []}


def parse(text, name):
    """(samples, census) for the decoded CSV. Values are converted to ppb by each row's unit; a
    non-detect is 0. Each component's value is the largest of its rows (the gate requires one
    row each)."""
    rows = csv.reader(io.StringIO(text))
    col = find_columns(next(rows, []))
    census = empty_census(col)
    if any(col[k] is None for k in COLS):
        return [], census
    by = {}
    for r in rows:
        if not any(c.strip() for c in r):
            continue
        census["rows"] += 1
        comp = component(_cell(r, col["component"]))
        _bump(census["components"], comp or clean(_cell(r, col["component"])))
        if comp is None:
            census["unknown_components"] += 1
        raw = clean(_cell(r, col["value"]))
        v, kind = parse_value(raw)
        _bump(census["kinds"], kind)
        if kind == "bad" and mask(raw) not in census["bad_shapes"]:
            census["bad_shapes"].append(mask(raw))
        unit = unit_label(_cell(r, col["unit"]))
        _bump(census["units"], unit)
        _bump(census["plans"], clean(_cell(r, col["plan"])))
        sid = clean(_cell(r, col["sample"]))
        s = by.get(sid)
        if s is None:
            s = by[sid] = {"sample": sid, "order": len(by),
                           "product": clean(_cell(r, col["product"])),
                           "origin": clean(_cell(r, col["origin"])),
                           "function": clean(_cell(r, col["function"])),
                           "region": clean(_cell(r, col["region"])),
                           "date": clean(_cell(r, col["date"])),
                           "n_rows": 0, "values": {}, "bad": False}
        s["n_rows"] += 1
        if kind == "bad":
            s["bad"] = True
        if comp is not None:
            ppb = v * PPB_PER.get(unit, 1.0) if kind == "det" else 0.0
            s["values"].setdefault(comp, []).append(ppb)
    samples = [finish(s, name) for s in by.values()]
    for s in samples:
        _bump(census["products"], s["product"])
        _bump(census["rows_per_sample"], str(s["n_rows"]))
        if s["missing"]:
            census["missing"][s["sample"]] = s["missing"]
        if s["repeated"]:
            census["repeated"][s["sample"]] = s["repeated"]
        if not ID_RE.match(s["sample"]):
            census["ids_bad"].append(s["sample"])
    census["samples"] = len(samples)
    return samples, census


def finish(s, name):
    """Add the per-analyte ppb values (0 for an analyte the file does not test) and the
    category."""
    comps = TARGETS[name]["components"]
    s["ppb"] = {SHORT[c]: max(v) for c, v in s["values"].items()}
    for k in KEYS:
        s["ppb"].setdefault(k, 0.0)
    s["missing"] = [c for c in comps if c not in s["values"]]
    s["repeated"] = sorted(c for c, v in s["values"].items() if len(v) > 1)
    s["type"] = TYPE_OF[name].get(s["product"], "unmapped")
    return s


def gate_checks(census, size, name):
    t = TARGETS[name]
    comps = t["components"]
    rows = census["rows"]
    return {
        "size": size == t["size"],
        "columns": all(census["columns"].get(k) is not None for k in COLS),
        "rows": rows == t["rows"],
        "samples": census["samples"] == t["samples"] and not census["ids_bad"],
        "per_sample": census["rows_per_sample"] == {str(len(comps)): census["samples"]}
        and not census["missing"] and not census["repeated"],
        "components": rows > 0 and census["unknown_components"] == 0
        and set(census["components"]) == set(comps),
        "units": rows > 0 and set(census["units"]) == {t["unit"]},
        "plan": rows > 0 and set(census["plans"]) == {t["plan"]},
        "products": bool(census["products"]) and set(census["products"]) <= set(TYPE_OF[name]),
        "values": rows > 0 and census["kinds"].get("bad", 0) == 0,
    }


def stats(values):
    """n, positive count, share, min, max and mean of the positive values."""
    pos = sorted(v for v in values if v > 0)
    n = len(values)
    return {"n": n, "k": len(pos), "pct": 100 * len(pos) / n if n else None,
            "min": pos[0] if pos else None, "max": pos[-1] if pos else None,
            "mean": sum(pos) / len(pos) if pos else None}


def check_row(printed, st):
    """A printed (n, positive, min, max, average) row against stats."""
    n, k, mn, mx, avg = printed
    return {"n": st["n"] == n, "detected": st["k"] == k, "min": matches(st["min"], mn),
            "max": matches(st["max"], mx), "avg": matches(st["mean"], avg)}


def _full(cells, keys=("n",) + CELLS):
    return all(cells[k] for k in keys)


def col(samples, key):
    return [s["ppb"][key] for s in samples]


def of_type(samples, t):
    return [s for s in samples if s["type"] == t]


def brief(s):
    return {"sample": s["sample"], "product": s["product"], "type": s["type"],
            "function": s["function"], "origin": s["origin"], "date": s["date"],
            "ppb": {k: round(s["ppb"][k], 6) for k in KEYS}}


def ranked(samples, key="bpa"):
    """Positive samples for one analyte, highest first."""
    return sorted((s for s in samples if s["ppb"][key] > 0), key=lambda s: -s["ppb"][key])


def alt_rows(samples, key, printed, types):
    """Per category, the positive count, min, max and average of one analyte. A category the
    table does not print must have no positive."""
    out = {}
    for t in types:
        st = stats(col(of_type(samples, t), key))
        if t in printed:
            k, mn, mx, avg = printed[t]
            out[t] = {"k": st["k"], "printed_k": k, "detected": st["k"] == k,
                      "min": matches(st["min"], mn), "max": matches(st["max"], mx),
                      "avg": matches(st["mean"], avg), "stats": st}
        else:
            out[t] = {"k": st["k"], "printed_k": 0, "detected": st["k"] == 0,
                      "min": True, "max": True, "avg": True, "stats": st}
    return out


def twins(samples, min_pos=2):
    """Sets of samples whose four values are identical, among samples with at least `min_pos`
    positive analytes (exploratory: a hint of copied rows)."""
    groups = {}
    for s in samples:
        prof = tuple(s["ppb"][k] for k in KEYS)
        if sum(1 for v in prof if v > 0) >= min_pos:
            groups.setdefault(prof, []).append(s["sample"])
    return sorted(sorted(v) for v in groups.values() if len(v) > 1)


def origins(samples):
    """category -> [domestic, imported, unspecified, total] from the Function column."""
    out = {}
    for s in samples:
        row = out.setdefault(s["type"], [0, 0, 0, 0])
        f = s["function"]
        row[0 if f == "Domestic" else 1 if f == "Import" else 2] += 1
        row[3] += 1
    return out


def dates_summary(samples):
    """Labels-and-dates facts: how many dates parse, how many differ, the span, and the most
    common date."""
    ds = [parse_date(s["date"]) for s in samples]
    ok = [d for d in ds if d is not None]
    by = {}
    for d in ok:
        _bump(by, d.isoformat())
    top = sorted(by.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    return {"n": len(samples), "parsed": len(ok), "distinct": len(by),
            "first": min(ok).isoformat() if ok else None,
            "last": max(ok).isoformat() if ok else None,
            "top": top, "unparsed_examples": sorted({s["date"] for s, d in zip(samples, ds)
                                                     if d is None})[:5]}


def date_order(samples, start=T1_START):
    """T1: are the dates a calendar sequence that follows the sample numbers? Counts how many
    samples sit on first-date + rank days when ranked by sample number, by file row order and by
    ID text, and how many sit on `start` + (number - 1) days."""
    ok = [(s, parse_date(s["date"])) for s in samples]
    ok = [(s, d) for s, d in ok if d is not None]
    out = {"n": len(samples), "parsed": len(ok), "distinct": len({d for _, d in ok})}
    if not ok:
        return out
    first, last = min(d for _, d in ok), max(d for _, d in ok)
    out["first"], out["last"] = first.isoformat(), last.isoformat()
    out["span_days"] = (last - first).days + 1
    out["consecutive"] = out["distinct"] == len(samples) == out["span_days"]
    orders = {
        "number": sorted(ok, key=lambda p: (id_number(p[0]["sample"]) or 0, p[0]["sample"])),
        "row": sorted(ok, key=lambda p: p[0]["order"]),
        "text": sorted(ok, key=lambda p: p[0]["sample"]),
    }
    out["rank_fits"] = {k: sum(1 for i, (_, d) in enumerate(v)
                               if d == first + datetime.timedelta(days=i))
                        for k, v in orders.items()}
    out["start_plus_number_fits"] = sum(
        1 for s, d in ok if id_number(s["sample"]) is not None
        and d == start + datetime.timedelta(days=id_number(s["sample"]) - 1))
    weekdays = {}
    for _, d in ok:
        _bump(weekdays, d.strftime("%a"))
    out["weekdays"] = weekdays
    out["long_ids"] = sorted((s["sample"], d.isoformat()) for s, d in ok
                             if len(re.sub(r"\D", "", s["sample"][4:])) > 4)
    return out


# ---------------------------------------------------------------------------
# Per-file analysis.
# ---------------------------------------------------------------------------
def base(samples, name):
    types = TYPES[name]
    a = {"n": len(samples), "bpa": {t: stats(col(of_type(samples, t), "bpa")) for t in types}}
    a["bpa"]["all"] = stats(col(samples, "bpa"))
    pos = ranked(samples)
    a["lowest"] = [brief(s) for s in pos if pos and s["ppb"]["bpa"] == pos[-1]["ppb"]["bpa"]]
    a["highest"] = [brief(s) for s in pos[:3]]
    a["origins"] = origins(samples)
    a["dates"] = dates_summary(samples)
    a["unmapped"] = sorted({s["product"] for s in samples if s["type"] == "unmapped"})
    return a


def analyse_2009(samples):
    a = base(samples, "bpa-2009")
    a["positives"] = [brief(s) for s in ranked(samples)]
    a["t1"] = date_order(samples)
    return a


def analyse_2010(samples):
    a = base(samples, "bpa-2010")
    a["positives"] = [brief(s) for s in ranked(samples)]
    return a


def analyse_2011(samples):
    a = base(samples, "bpa-2011")
    pos = ranked(samples)
    a["positives"] = [brief(s) for s in pos]
    a["v3"] = {g: sum(1 for s in pos if s["product"] in labels)
               for g, labels in V3_GROUPS.items()}
    return a


def analyse_2012(samples):
    a = base(samples, "bpa-2012")
    a["table5"] = {t: check_row(TABLE5_2012[t], a["bpa"][t]) for t in TABLE5_2012}
    a["v4_full"] = [t for t in V4_ROWS if _full(a["table5"][t])]
    a["pasta_soup_k"] = a["bpa"]["pasta"]["k"] + a["bpa"]["soup"]["k"]
    curry_x = of_type(samples, "curry") + [s for s in samples if s["product"] == "Salsa"]
    veg_x = [s for s in of_type(samples, "veg") if s["product"] != "Salsa"]
    sx = {"curry": stats(col(curry_x, "bpa")), "veg": stats(col(veg_x, "bpa"))}
    a["salsa_map"] = {t: {"stats": sx[t], "cells": check_row(TABLE5_2012[t], sx[t])} for t in sx}
    a["curry_positives"] = [brief(s) for s in ranked(curry_x)]
    return a


def analyse_2013(samples):
    a = base(samples, "bpa-2013")
    a["table5"] = {t: check_row(TABLE5_2013[t], a["bpa"][t]) for t in TABLE5_2013}
    a["v5_full"] = [t for t in TABLE5_2013 if _full(a["table5"][t])]
    a["d_suffixed"] = [brief(s) for s in samples if s["sample"].endswith("D")]
    return a


def analyse_2016(samples):
    name = "bpa-2016"
    a = base(samples, name)
    a["table2"] = {t: check_row(TABLE2_2016[t], a["bpa"][t]) for t in TABLE2_2016}
    veg_mean = a["bpa"]["veg"]["mean"]
    a["veg_avg"] = {p: matches(veg_mean, p) for p in VEG_2016_AVGS}
    rows = {}
    for t in V6_GRADABLE:
        cells = dict(a["table2"][t])
        if t == "veg":
            cells["avg"] = any(a["veg_avg"].values())
        rows[t] = cells
    a["v6_rows"] = rows
    a["tops"] = {}
    for t in V6_TOP:
        pos = ranked(of_type(samples, t))
        a["tops"][t] = {"values": [s["ppb"]["bpa"] for s in pos[:2]],
                        "top": [brief(s) for s in pos[:2]]}
    a["alt"] = {k: alt_rows(samples, k, TABLE4_2016[k], TYPES[name]) for k in TABLE4_2016}
    badge = ranked(samples, "badge")
    a["badge_top"] = brief(badge[0]) if badge else None
    a["bpf_positives"] = [brief(s) for s in ranked(samples, "bpf")]
    a["bps_positives"] = [brief(s) for s in ranked(samples, "bps")]
    a["twins"] = twins(samples)
    return a


def analyse_2017(samples):
    name = "bpa-2017"
    a = base(samples, name)
    a["table2"] = {t: check_row(TABLE2_2017[t], a["bpa"][t]) for t in TABLE2_2017}
    a["meat_avg_alternatives"] = {p: matches(a["bpa"]["meat"]["mean"], p)
                                  for p in MEAT_AVG_ALTERNATIVES}
    pos = ranked(samples)
    a["top_two"] = [brief(s) for s in pos[:2]]
    a["alt"] = {k: alt_rows(samples, k, ALT_2017[k], TYPES[name]) for k in ALT_2017}
    badge = [s for s in samples if s["ppb"]["badge"] > 0]
    bpf = [s for s in samples if s["ppb"]["bpf"] > 0]
    a["badge"] = {"k": len(badge), "with_bpa": sum(1 for s in badge if s["ppb"]["bpa"] > 0),
                  "stats": stats(col(samples, "badge"))}
    a["bpf"] = {"k": len(bpf), "with_bpa": sum(1 for s in bpf if s["ppb"]["bpa"] > 0)}
    a["bps_positives"] = [brief(s) for s in ranked(samples, "bps")]
    a["twins"] = twins(samples)
    return a


ANALYSE = {"bpa-2009": analyse_2009, "bpa-2010": analyse_2010, "bpa-2011": analyse_2011,
           "bpa-2012": analyse_2012, "bpa-2013": analyse_2013, "bpa-2016": analyse_2016,
           "bpa-2017": analyse_2017}


def d1_group(name, s):
    if name == "bpa-2013" and s["product"] in D1_LEFT_OUT_2013:
        return None
    return D1_OF.get(s["type"])


def cut_share(samples, name, cut=D1_CUT):
    """Per shared category: [n, positive, at or above the cut]; and the pooled share at the
    cut."""
    groups = {}
    for s in samples:
        g = d1_group(name, s)
        if g is None:
            continue
        row = groups.setdefault(g, [0, 0, 0])
        v = s["ppb"]["bpa"]
        row[0] += 1
        row[1] += int(v > 0)
        row[2] += int(v >= cut - 1e-6)
    n = sum(r[0] for r in groups.values())
    k = sum(r[2] for r in groups.values())
    return {"groups": groups, "n": n, "k_cut": k, "share": k / n if n else None}


def d1_analysis(s12, s13):
    a, b = cut_share(s12, "bpa-2012"), cut_share(s13, "bpa-2013")
    ratio = b["share"] / a["share"] if a["share"] and b["share"] is not None else None
    return {"2012-13": a, "2013-14": b, "ratio": ratio}


# ---------------------------------------------------------------------------
# Grading.
# ---------------------------------------------------------------------------
def grade(an, gates):
    ok = {name: bool(gates.get(name)) and all(gates[name].values()) for name in NAMES}
    preds = []
    for name in NAMES:
        t = TARGETS[name]
        preds.append({"id": "G" + name[-2:], "kind": "gate", "graded": True, "met": ok[name],
                      "observed": gates.get(name, {}),
                      "text": f"{name}: byte size as on the portal record; columns; {t['rows']} "
                              f"rows; {t['samples']} samples, each with one row per component "
                              f"({len(t['components'])}); unit {t['unit']} and plan {t['plan']} "
                              "on every row; only the census labels; every value a number >= 0, "
                              "a '<' or a not-detected token"})

    def add(pid, names, text, observe, met=None, kind="prediction"):
        g = all(ok[n] for n in names)
        o = observe() if g else {}
        if kind == "descriptive":
            preds.append({"id": pid, "kind": kind, "graded": False, "met": None, "text": text,
                          "observed": o})
        else:
            preds.append({"id": pid, "kind": kind, "graded": g, "met": bool(g and met(o)),
                          "text": text, "observed": o})

    def v1():
        a = an["bpa-2009"]
        b = a["bpa"]
        return {"checks": {"k_82": b["all"]["k"] == V1_2009["k"],
                           "food_9": b["food"]["k"] == V1_2009["food_k"],
                           "min_1.4": matches(b["all"]["min"], V1_2009["min"]),
                           "max_9.6": matches(b["all"]["max"], V1_2009["max"])},
                "stats": b, "nd_pct": 100 - b["all"]["pct"],
                "ungraded": "package splits (70 of 89 metal, 12 of 32 glass), powdered formula, "
                            "cereal and 'all infant-food positives in glass jars': no label"}

    add("V1", ["bpa-2009"], "2009-10: 82 positives; 9 infant-food positives; range 1.4 to 9.6 "
        "ppb (the package, powder and cereal clauses are ungraded: no label)", v1,
        lambda o: all(o["checks"].values()))
    add("V2", ["bpa-2010"], "2010-11: no positive sample",
        lambda: {"stats": an["bpa-2010"]["bpa"], "positives": an["bpa-2010"]["positives"]},
        lambda o: o["stats"]["all"]["k"] == 0)

    def v3():
        a = an["bpa-2011"]
        checks = {"k_6": a["bpa"]["all"]["k"] == 6}
        checks.update({f"{g}_{n}": a["v3"][g] == n for g, n in V3_EXPECTED.items()})
        return {"checks": checks, "counts": a["v3"], "positives": a["positives"],
                "stats": a["bpa"]}

    add("V3", ["bpa-2011"], "2011-12: exactly 6 positives: one pasta, three carrots, one peas, "
        "one corn (so none in fruit, juices, beverages or soups)", v3,
        lambda o: all(o["checks"].values()))

    def v4():
        a = an["bpa-2012"]
        b = a["bpa"]
        checks = {
            "k_145": b["all"]["k"] == V4["k"],
            "min_5.2_pasta": matches(b["all"]["min"], V4["min"])
            and any(s["type"] == "pasta" for s in a["lowest"]),
            "max_381_coconut": matches(b["all"]["max"], V4["max"])
            and bool(a["highest"]) and a["highest"][0]["product"] == "Coconut Milk",
            "rows_full_4_of_5": len(a["v4_full"]) >= V4_MIN_FULL,
            "pasta_soup_92": a["pasta_soup_k"] == V4["pasta_soup_k"],
        }
        return {"checks": checks, "table5": a["table5"], "full_rows": a["v4_full"],
                "stats": b, "lowest": a["lowest"], "highest": a["highest"],
                "pasta_soup_k": a["pasta_soup_k"], "exploratory_salsa_map": a["salsa_map"],
                "curry_positives": a["curry_positives"]}

    add("V4", ["bpa-2012"], "2012-13: 145 positives; minimum 5.2 (a pasta), maximum 381 (a "
        "coconut milk); at least 4 of Table 5's five non-pasta/soup rows reproduce in full; the "
        "pasta and soup samples hold 92 positives", v4, lambda o: all(o["checks"].values()))

    def v5():
        a = an["bpa-2013"]
        b = a["bpa"]
        checks = {
            "k_252": b["all"]["k"] == V5["k"],
            "min_1.0_fruit": matches(b["all"]["min"], V5["min"])
            and any(s["type"] == "fruit" for s in a["lowest"]),
            "max_565_corn": matches(b["all"]["max"], V5["max"])
            and bool(a["highest"]) and a["highest"][0]["product"] == "Corn",
            "rows_full_7_of_9": len(a["v5_full"]) >= V5_MIN_FULL,
        }
        return {"checks": checks, "table5": a["table5"], "full_rows": a["v5_full"],
                "stats": b, "lowest": a["lowest"], "highest": a["highest"],
                "d_suffixed": a["d_suffixed"]}

    add("V5", ["bpa-2013"], "2013-14: 252 positives of 391; minimum 1.0 (a fruit), maximum 565 "
        "(a corn); at least 7 of Table 5's nine 2013 rows reproduce in full, pasta as 45 of 45",
        v5, lambda o: all(o["checks"].values()))

    def v6():
        a = an["bpa-2016"]
        b = a["bpa"]
        checks = {"rows_4_gradable_full": all(_full(a["v6_rows"][t]) for t in V6_GRADABLE),
                  "k_361": b["all"]["k"] == V6["k"],
                  "avg_all_87.2": matches(b["all"]["mean"], V6["avg_all"])}
        for t, (top, nxt, label) in V6_TOP.items():
            vals = a["tops"][t]["values"]
            good = len(vals) >= 2 and matches(vals[0], top) and matches(vals[1], nxt)
            if label is not None:
                good = good and a["tops"][t]["top"][0]["product"] == label
            checks[f"{t}_top_{top}_next_{nxt}"] = good
        return {"checks": checks, "rows": a["v6_rows"], "veg_avg": a["veg_avg"],
                "table2_all_packaging": a["table2"], "stats": b, "tops": a["tops"],
                "ungraded": V6_UNGRADED}

    add("V6", ["bpa-2016"], "2016-17: Table 2's coconut milk, fruit, pie filling and vegetable "
        "rows reproduce in full (vegetables at 139 or 138); 361 positives in all 491 samples; "
        "the all-products average 87.2; the text's maxima and next-highest values (pie filling "
        "2240 pumpkin / 530, coconut milk 1370 / 478, fruit 1160 pineapple / 186, sauces 1120 / "
        "7.5). The other five rows, the 340 canned positives and the 91.6 canned average are "
        "ungraded: the file has no packaging label", v6, lambda o: all(o["checks"].values()))

    def v7():
        a = an["bpa-2017"]
        top = a["top_two"]
        bps = a["bps_positives"]
        checks = {
            "meat_row": _full(a["table2"]["meat"]),
            "fish_row": _full(a["table2"]["fish"]),
            "total_row": _full(a["table2"]["all"]),
            "top_1480_imported_fish_next_567": len(top) == 2
            and matches(top[0]["ppb"]["bpa"], V7["top"][0])
            and top[0]["type"] == "fish" and top[0]["function"] == "Import"
            and matches(top[1]["ppb"]["bpa"], V7["top"][1]),
            "one_bps_meat_1.79": len(bps) == V7["bps_k"] and bps[0]["type"] == "meat"
            and matches(bps[0]["ppb"]["bps"], V7["bps"]),
            "badge_72_of_which_69_with_bpa": a["badge"]["k"] == V7["badge_k"]
            and a["badge"]["with_bpa"] == V7["badge_with_bpa"],
            "bpf_68_all_with_bpa": a["bpf"]["k"] == V7["bpf_k"]
            and a["bpf"]["with_bpa"] == V7["bpf_k"],
        }
        return {"checks": checks, "table2": a["table2"], "stats": a["bpa"],
                "meat_avg_alternatives": a["meat_avg_alternatives"], "top_two": top,
                "bps_positives": bps, "badge": a["badge"], "bpf": a["bpf"]}

    add("V7", ["bpa-2017"], "2017-18: Table 2's BPA rows reproduce (meat average 35.6, not 34.6 "
        "or 46.6); the top value 1480 is an imported fish and the next is 567; one BPS positive "
        "(a meat, 1.79); 69 of 72 BADGE positives and all 68 BPF positives also contain BPA",
        v7, lambda o: all(o["checks"].values()))

    def d1():
        d = an["d1"]
        rates = {n: {"k": an[n]["bpa"]["all"]["k"], "n": an[n]["bpa"]["all"]["n"],
                     "pct": an[n]["bpa"]["all"]["pct"], "min": an[n]["bpa"]["all"]["min"]}
                 for n in ("bpa-2011", "bpa-2012", "bpa-2013") if an.get(n)}
        return {"cut_ppb": D1_CUT, "shares": d, "ratio": d["ratio"], "rates": rates,
                "nd_coding": "every result cell is a plain number; non-detects are 0; no "
                             "limit is printed in any of the three files"}

    add("D1", ["bpa-2012", "bpa-2013"], "exploratory, directional: at a common 5.2 ppb cut in the "
        "categories shared by 2012-13 and 2013-14 (vegetables, fruit, juices/beverages without "
        "energy, sports and soft drinks, pastas/soups, coconut milk, curry), the 2013-14 share is "
        "at least 1.5 times the 2012-13 share", d1,
        lambda o: o["ratio"] is not None and o["ratio"] >= D1_RATIO)

    add("T1", ["bpa-2009"], "descriptive (labels and dates only): are the 2009-10 sampling "
        "dates a calendar sequence that follows the sample numbers (date = 2009-10-01 + "
        "(number - 1) days)?", lambda: an["bpa-2009"]["t1"], kind="descriptive")

    def x6():
        a = an["bpa-2016"]
        return {"table4_all_packaging": a["alt"], "badge_top": a["badge_top"],
                "bpf_positives": a["bpf_positives"], "bps_positives": a["bps_positives"],
                "twins": a["twins"], "origins": a["origins"]}

    add("X6", ["bpa-2016"], "descriptive: 2016-17 Table 4 (BADGE, BPF, BPS) over all packaging; "
        "the text's 'highest BADGE (224) is a coconut milk without BPA' and 'the three BPF "
        "positives are bamboo shoots that also contain BPA'; twin scan", x6, kind="descriptive")

    def x7():
        a = an["bpa-2017"]
        return {"alt_rows": a["alt"], "badge_avg_10.1": matches(a["badge"]["stats"]["mean"],
                                                                V7["badge_avg"]),
                "badge_stats": a["badge"]["stats"], "twins": a["twins"], "origins": a["origins"]}

    add("X7", ["bpa-2017"], "descriptive: 2017-18 Table 2's BADGE, BPF and BPS rows and the "
        "text's BADGE average 10.1; twin scan", x7, kind="descriptive")
    return preds


# ---------------------------------------------------------------------------
# Data loading (network only here).
# ---------------------------------------------------------------------------
def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-bpa-series"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(name, data_dir, rounds=4, pause=90):
    """The file from the data volume (cached there by the census job) or the portal, trying both
    hosts for up to `rounds` rounds `pause` seconds apart."""
    t = TARGETS[name]
    local = os.path.join(data_dir, t["resource"] + ".csv") if data_dir else ""
    if local and os.path.exists(local):
        with open(local, "rb") as fh:
            raw = fh.read()
        if len(raw) == t["size"]:
            return raw, "data-volume"
    errors = []
    for attempt in range(rounds):
        for host in ("https://open.canada.ca", "https://ouvert.canada.ca"):
            url = f"{host}/data/dataset/{t['dataset']}/resource/{t['resource']}/download/{t['path']}"
            try:
                raw = _fetch(url)
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))
                continue
            try:
                if local:
                    with open(local, "wb") as fh:
                        fh.write(raw)
            except OSError:
                pass
            return raw, url
        if attempt + 1 < rounds:
            time.sleep(pause)
    raise RuntimeError("no copy: " + "; ".join(errors[-2:]))


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
    if isinstance(x, datetime.date):
        return x.isoformat()
    return "" if x is None else (round(x, 6) if isinstance(x, float) else x)


def write_samples(path, samples, name):
    keys = [SHORT[c] for c in TARGETS[name]["components"]]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "type", "function", "origin", "region", "date"]
                   + [f"{k}_ppb" for k in keys])
        for s in sorted(samples, key=lambda s: s["sample"]):
            w.writerow([s["sample"], s["product"], s["type"], s["function"], s["origin"],
                        s["region"], s["date"]] + [repr(s["ppb"][k]) for k in keys])


def run_one(name, data_dir):
    try:
        raw, src = load(name, data_dir)
        text, enc = decode(raw)
        samples, census = parse(text, name)
        md5 = hashlib.md5(raw).hexdigest()
        provenance = {"dataset": TARGETS[name]["dataset"], "resource": TARGETS[name]["resource"],
                      "source": src, "bytes": len(raw), "encoding": enc,
                      "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                      "portal_md5": TARGETS[name]["md5"] or None,
                      "md5_matches_portal": (md5 == TARGETS[name]["md5"])
                      if TARGETS[name]["md5"] else None}
        size = len(raw)
    except Exception as exc:  # noqa: BLE001 - the gate fails, with the reason
        samples, census, size = [], empty_census(), -1
        census["error"] = f"{type(exc).__name__}: {exc}"
        provenance = {"dataset": TARGETS[name]["dataset"], "error": census["error"]}
    return samples, census, size, provenance


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade bpa-series 0.1.0 items V1-V7, D1, T1.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    got, gates, an = {}, {}, {}
    for name in NAMES:
        samples, census, size, prov = run_one(name, args.data_dir)
        got[name] = (samples, census, prov)
        gates[name] = gate_checks(census, size, name)
        an[name] = ANALYSE[name](samples) if all(gates[name].values()) else {}
    if an["bpa-2012"] and an["bpa-2013"]:
        an["d1"] = d1_analysis(got["bpa-2012"][0], got["bpa-2013"][0])
    preds = grade(an, gates)
    for name in NAMES:
        if all(gates[name].values()):
            write_samples(os.path.join(args.out_dir, f"{name.replace('-', '_')}_samples.csv"),
                          got[name][0], name)
    result = {"study": "bpa-series", "grader": "bpa_series_grade", "version": VERSION,
              "predictions": preds, "analysis": an,
              "census": {n: got[n][1] for n in NAMES},
              "provenance": {n: got[n][2] for n in NAMES},
              "n_graded": sum(1 for p in preds if p["graded"] and p["kind"] == "prediction"),
              "n_met": sum(1 for p in preds if p["met"] and p["kind"] == "prediction")}
    with open(os.path.join(args.out_dir, "bpa_series_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    print(json.dumps({"version": VERSION, "gates": gates,
                      "kinds": {n: got[n][1]["kinds"] for n in NAMES},
                      "bad_shapes": {n: got[n][1]["bad_shapes"] for n in NAMES},
                      "unknown_products": {n: sorted(set(got[n][1]["products"])
                                                     - set(TYPE_OF[n])) for n in NAMES},
                      "provenance": {n: got[n][2] for n in NAMES},
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "checks": {p["id"]: p["observed"].get("checks") for p in preds
                                 if p["kind"] == "prediction" and p["observed"]},
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if all(all(g.values()) for g in gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
