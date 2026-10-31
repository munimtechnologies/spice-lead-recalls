#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""bpa-2018-2020 0.1.0: CFIA's open 2018-19 and 2020-21 bisphenol files against every figure
CFIA printed for them (value items B2-B6 and C2-C4 of docs/bpa-pah-report-0.1.0-prereg.md).

Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes each survey's per-sample CSV on
open.canada.ca (Open Government Licence - Canada) and a report page that gives results in ppb.
Both files report ug/g, so a file value x is 1000 * x ppb. Each file is gated on structure facts
taken from the names-only census (docs/bpa-pah-report-0.1.0-census.md) run before any result
value was read: its byte size from the portal record, its columns, samples x 4 component rows, one
unit, one plan code, the known product labels and a value rule. The label-to-type maps below are
the ones fixed in that census note. Standard library only. Code Apache-2.0; derived data
CC BY 4.0. Not a compliance finding, not about any brand, and not dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
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
TARGETS = {
    "bpa-2018": {
        "dataset": "b8686c21-a8ef-4037-8478-353ed45a0145",
        "resource": "7a20917c-8aa9-4af6-8ce4-13620ef3af59",
        "path": ("cfia_acia-15084827-v1-chem-ts_2018-19_bpa-and-bpa-alternatives-in-selected-"
                 "foods_data-for-open-d.csv"),
        "size": 289825, "md5": "5cf4d04c1e4db3825dc51cfe09ea6415",
        "rows": 1508, "samples": 377, "plan": "2018_SB451"},
    "bpa-2020": {
        "dataset": "5b36b36d-4f8b-4b0c-b407-42b8076b3730",
        "resource": "df188f89-3dba-4650-bfbb-e4c46f89d21a",
        "path": ("cfia_acia-1351-v1-open_data_for_chem_ts_survey_-_2020-21_-_bisphenol_a_and_bpa_"
                 "alternatives_in_s.csv"),
        "size": 285553, "md5": "31a4ca35a9f46e0d59cc637314c744a9",
        "rows": 1608, "samples": 402, "plan": "2020_SB451"},
}
NAMES = tuple(TARGETS)
UNITS = {"µg/g"}
PPB_PER_UNIT = 1000.0                           # ug/g -> ppb (ng/g)
ID_RE = re.compile(r"^C\d{4}[A-Z]+(\d{4,6})(D?)$")
COMPONENTS = ("Bisphenol A", "Bisphenol A Diglycidyl Ether", "Bisphenol F", "Bisphenol S")
KEYS = ("bpa", "badge", "bpf", "bps")
SHORT = dict(zip(COMPONENTS, KEYS))
COMP_KEY = {c.lower(): c for c in COMPONENTS}

# File label -> report product type, exactly as fixed in docs/bpa-pah-report-0.1.0-census.md
# before any value was read.
PIE = ("Pie Filling - Blueberry", "Pie Filling - Cherry", "Pie Filling - Other",
       "Pie Filling - Pumpkin")
FRUIT_2020 = ("Apricot", "Cherry", "Cranberry", "Grapefruit", "JackFruit", "Lychee", "Mango",
              "Mixed Fruit", "Orange", "Peach", "Pear", "Pineapple")
VEG_2020 = ("Artichoke Heart", "Bean - Green/Yellow", "Bean - Kidney", "Bean - Pinto", "Beet",
            "Carrot", "Corn", "Lentil", "Mixed Vegetables", "Mushroom", "Mushroom - Shiitake",
            "Pea", "Soup", "Sprout - Bean", "Vegetable Products", "Water Chestnut")
TYPE_OF = {
    "bpa-2018": dict([("Coconut Milk", "coconut"), ("Infant Formula - Dairy", "formula"),
                      ("Infant Formula - Other", "formula"), ("Sauces", "sauces"),
                      ("Tomato Sauce", "sauces")] + [(p, "pie") for p in PIE]),
    "bpa-2020": dict([("Fish/Seafood - Canned", "fish"), ("Meat - Canned", "meat")]
                     + [(p, "pie") for p in PIE + ("Pie Filling - apple",)]
                     + [(f, "fruit") for f in FRUIT_2020] + [(v, "veg") for v in VEG_2020]),
}
TYPES = {"bpa-2018": ("coconut", "formula", "pie", "sauces"),
         "bpa-2020": ("fish", "fruit", "meat", "pie", "veg")}

# Printed figures (ppb; positives only), transcribed in the pre-registration.
# Table 2 rows: type -> (n, positive, min, max, average).
TABLE2 = {
    "bpa-2018": {"coconut": (49, 37, "1.42", "367", "47.0"),
                 "formula": (135, 17, "0.92", "2.24", "1.4"),
                 "pie": (98, 62, "0.97", "101", "11.2"),
                 "sauces": (95, 48, "1.01", "95.9", "9.78"),
                 "all": (377, 164, "0.92", "367", "17.8")},
    "bpa-2020": {"fish": (101, 39, "0.91", "395", "43.8"),
                 "fruit": (52, 15, "1.4", "21.4", "6.1"),
                 "meat": (100, 42, "1.2", "479", "43.5"),
                 "pie": (49, 16, "1.1", "7.1", "2.1"),
                 "veg": (100, 51, "0.96", "151", "55.9"),
                 "all": (402, 163, "0.91", "479", "40.0")},
}
TABLE3_FORMULA = (138, 18, "0.92", "5.89", "1.65")     # B2
B3_SAUCES = (96, 48, "1.01", "95.9", "9.78")           # B3
B4_ALL = (381, 165, "0.92", "367", "17.8")             # B4
BADGE_2018 = {"k": 12, "top": ("524", "209"), "others_below": 63.0, "avg": "81.9"}  # B5
PCT_2018 = {"summary_bpa": "43", "table2_bpa": "44", "summary_badge": "12"}
# 2020-21 Tables 3-5: analyte -> type -> (positive, min, max, average). A single positive is
# printed once; it is its own min, max and average.
ALT_2020 = {
    "badge": {"fish": (5, "3.6", "1580", "330"), "meat": (11, "6.5", "372", "66.1"),
              "veg": (1, "14.0", "14.0", "14.0")},
    "bpf": {"fish": (1, "94.8", "94.8", "94.8"), "meat": (1, "19.6", "19.6", "19.6")},
    "bps": {"fish": (1, "46.0", "46.0", "46.0"), "meat": (5, "0.96", "191", "52.1"),
            "veg": (1, "0.98", "0.98", "0.98")},
}
ALT_TOTALS_2020 = {"badge": 17, "bpf": 2, "bps": 7}
C4_2020 = {"badge_with_bpa": 8, "badge_imported": 14, "fish_badge_second": "51",
           "badge_avg": "141", "bpa_fruit_pie": 31}
MIN_FULL_ROWS = 5                               # C2: of Table 2's 6 rows
VEG_POSITIVES = 51                              # C2: not the paragraph's 163
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


def find_columns(header):
    """Map roles to column indexes (None if absent)."""
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


def parse(text, type_of):
    """(samples, census) for the decoded CSV. Values are converted to ppb; a non-detect is 0.
    Each component's value is the largest of its rows (the gate requires one row each)."""
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
        _bump(census["units"], clean(_cell(r, col["unit"])))
        _bump(census["plans"], clean(_cell(r, col["plan"])))
        sid = clean(_cell(r, col["sample"]))
        s = by.get(sid)
        if s is None:
            s = by[sid] = {"sample": sid, "product": clean(_cell(r, col["product"])),
                           "origin": clean(_cell(r, col["origin"])),
                           "function": clean(_cell(r, col["function"])),
                           "region": clean(_cell(r, col["region"])),
                           "n_rows": 0, "values": {}, "bad": False}
        s["n_rows"] += 1
        if kind == "bad":
            s["bad"] = True
        if comp is not None:
            s["values"].setdefault(comp, []).append(v * PPB_PER_UNIT if kind == "det" else 0.0)
    samples = [finish(s, type_of) for s in by.values()]
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


def finish(s, type_of):
    """Add the per-analyte ppb values and the report type."""
    s["ppb"] = {SHORT[c]: max(v) for c, v in s["values"].items()}
    for k in KEYS:
        s["ppb"].setdefault(k, 0.0)
    s["missing"] = [c for c in COMPONENTS if c not in s["values"]]
    s["repeated"] = sorted(c for c, v in s["values"].items() if len(v) > 1)
    s["type"] = type_of.get(s["product"], "unmapped")
    return s


def gate_checks(census, size, name):
    t = TARGETS[name]
    rows = census["rows"]
    return {
        "size": size == t["size"],
        "columns": all(census["columns"].get(k) is not None for k in COLS),
        "rows": rows == t["rows"],
        "samples": census["samples"] == t["samples"] and not census["ids_bad"],
        "per_sample": census["rows_per_sample"] == {str(len(COMPONENTS)): census["samples"]}
        and not census["missing"] and not census["repeated"],
        "components": rows > 0 and census["unknown_components"] == 0
        and set(census["components"]) == set(COMPONENTS),
        "units": rows > 0 and set(census["units"]) <= UNITS,
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


def col(samples, key):
    return [s["ppb"][key] for s in samples]


def of_type(samples, t):
    return [s for s in samples if s["type"] == t]


def alt_rows(samples, key, printed, types):
    """Tables 3-5: per type, the positive count, min, max and average of one analyte. A type
    the table does not print must have no positive."""
    out = {}
    for t in types:
        st = stats(col(of_type(samples, t), key))
        if t in printed:
            k, mn, mx, avg = printed[t]
            out[t] = {"k": st["k"], "printed_k": k, "detected": st["k"] == k,
                      "min": matches(st["min"], mn), "max": matches(st["max"], mx),
                      "avg": matches(st["mean"], avg)}
        else:
            out[t] = {"k": st["k"], "printed_k": 0, "detected": st["k"] == 0,
                      "min": True, "max": True, "avg": True}
    return out


def brief(s):
    return {"sample": s["sample"], "product": s["product"], "type": s["type"],
            "function": s["function"], "origin": s["origin"],
            "ppb": {k: round(s["ppb"][k], 6) for k in KEYS}}


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
    """type -> [domestic, imported, unspecified, total] from the Function column."""
    out = {}
    for s in samples:
        row = out.setdefault(s["type"], [0, 0, 0, 0])
        f = s["function"]
        row[0 if f == "Domestic" else 1 if f == "Import" else 2] += 1
        row[3] += 1
    return out


def bpa_stats(samples, types):
    out = {t: stats(col(of_type(samples, t), "bpa")) for t in types}
    out["all"] = stats(col(samples, "bpa"))
    return out


def analyse_2018(samples):
    types = TYPES["bpa-2018"]
    a = {"n": len(samples), "bpa": bpa_stats(samples, types)}
    a["table2"] = {t: check_row(TABLE2["bpa-2018"][t], a["bpa"][t]) for t in TABLE2["bpa-2018"]}
    a["table3_formula"] = check_row(TABLE3_FORMULA, a["bpa"]["formula"])
    a["b3_sauces"] = check_row(B3_SAUCES, a["bpa"]["sauces"])
    a["b4_all"] = check_row(B4_ALL, a["bpa"]["all"])
    badge = sorted((s for s in samples if s["ppb"]["badge"] > 0), key=lambda s: -s["ppb"]["badge"])
    by_type = {}
    for s in badge:
        _bump(by_type, s["type"])
    n_coconut = len(of_type(samples, "coconut"))
    a["badge"] = {"k": len(badge), "by_type": by_type, "stats": stats(col(samples, "badge")),
                  "values": [s["ppb"]["badge"] for s in badge],
                  "all_with_bpa": all(s["ppb"]["bpa"] > 0 for s in badge),
                  "pct_of_all": 100 * len(badge) / len(samples) if samples else None,
                  "pct_of_coconut": 100 * len(badge) / n_coconut if n_coconut else None,
                  "pct_of_bpa_positive": (100 * len(badge) / a["bpa"]["all"]["k"]
                                          if a["bpa"]["all"]["k"] else None)}
    a["bpf"] = stats(col(samples, "bpf"))
    a["bps"] = stats(col(samples, "bps"))
    formula = sorted(of_type(samples, "formula"), key=lambda s: -s["ppb"]["bpa"])
    a["formula_top"] = [brief(s) for s in formula[:3]]
    a["pct"] = {k: matches(a["bpa"]["all"]["pct"], v) for k, v in PCT_2018.items()
                if k.endswith("bpa")}
    a["origins"] = origins(samples)
    a["twins"] = twins(samples)
    return a


def c4_checks(samples):
    badge = [s for s in samples if s["ppb"]["badge"] > 0]
    with_bpa = [s for s in badge if s["ppb"]["bpa"] > 0]
    bps_meat = [s for s in of_type(samples, "meat") if s["ppb"]["bps"] > 0]
    fish_badge = sorted((s["ppb"]["badge"] for s in of_type(samples, "fish")
                         if s["ppb"]["badge"] > 0), reverse=True)
    fruit_pie = [s for s in samples if s["type"] in ("fruit", "pie") and s["ppb"]["bpa"] > 0]
    checks = {
        "badge_with_bpa_8": len(with_bpa) == C4_2020["badge_with_bpa"],
        "with_bpa_all_imported_meat_or_fish": bool(with_bpa) and all(
            s["function"] == "Import" and s["type"] in ("meat", "fish") for s in with_bpa),
        "badge_imported_14": sum(1 for s in badge if s["function"] == "Import")
        == C4_2020["badge_imported"],
        "bps_meat_all_with_bpa": bool(bps_meat) and all(s["ppb"]["bpa"] > 0 for s in bps_meat),
        "fish_badge_second_51": len(fish_badge) >= 2
        and matches(fish_badge[1], C4_2020["fish_badge_second"]),
        "bpa_fruit_pie_all_imported": bool(fruit_pie) and all(
            s["function"] == "Import" for s in fruit_pie),
    }
    observed = {
        "badge_k": len(badge), "badge_with_bpa": [brief(s) for s in with_bpa],
        "badge_imported": sum(1 for s in badge if s["function"] == "Import"),
        "bps_meat": [brief(s) for s in bps_meat], "fish_badge_desc": fish_badge,
        "bpa_fruit_pie_k": len(fruit_pie),
        "bpa_fruit_pie_functions": sorted({s["function"] for s in fruit_pie}),
    }
    return checks, observed


def analyse_2020(samples):
    types = TYPES["bpa-2020"]
    a = {"n": len(samples), "bpa": bpa_stats(samples, types)}
    a["table2"] = {t: check_row(TABLE2["bpa-2020"][t], a["bpa"][t]) for t in TABLE2["bpa-2020"]}
    a["alt"] = {key: alt_rows(samples, key, ALT_2020[key], types) for key in ALT_2020}
    a["alt_totals"] = {key: stats(col(samples, key))["k"] for key in ALT_2020}
    a["alt_stats"] = {key: stats(col(samples, key)) for key in ALT_2020}
    a["badge_avg_matches_141"] = matches(a["alt_stats"]["badge"]["mean"], C4_2020["badge_avg"])
    a["c4"], a["c4_observed"] = c4_checks(samples)
    a["bpf_positives"] = [brief(s) for s in samples if s["ppb"]["bpf"] > 0]
    a["origins"] = origins(samples)
    a["twins"] = twins(samples)
    return a


def _full(cells, keys=("n",) + CELLS):
    return all(cells[k] for k in keys)


def grade(a18, a20, gates):
    ok = {name: all(gates[name].values()) for name in NAMES}
    preds = []
    for gid, name in (("G18", "bpa-2018"), ("G20", "bpa-2020")):
        preds.append({"id": gid, "kind": "gate", "graded": True, "met": ok[name],
                      "observed": gates[name],
                      "text": f"{name}: byte size as on the portal record; columns; "
                              f"{TARGETS[name]['rows']} rows; {TARGETS[name]['samples']} samples, "
                              "each with one row per the 4 bisphenols; unit ug/g and plan "
                              f"{TARGETS[name]['plan']} on every row; the census labels; every "
                              "value a number >= 0, a '<' or a not-detected token"})

    def add(pid, name, text, observe, met):
        o = observe() if ok[name] else {}
        preds.append({"id": pid, "kind": "prediction", "graded": ok[name],
                      "met": bool(ok[name] and met(o)), "text": text, "observed": o})

    add("B2", "bpa-2018", "infant formula reproduces Table 3's row: 138 samples, 18 positives, "
        "min 0.92, max 5.89, average 1.65",
        lambda: {"cells": a18["table3_formula"], "stats": a18["bpa"]["formula"],
                 "top": a18["formula_top"]},
        lambda o: _full(o["cells"]))
    add("B3", "bpa-2018", "tomato-based sauces: 96 samples, 48 positive, min 1.01, max 95.9, "
        "average 9.78",
        lambda: {"cells": a18["b3_sauces"], "stats": a18["bpa"]["sauces"]},
        lambda o: _full(o["cells"]))
    add("B4", "bpa-2018", "all samples: BPA positive in 165 of 381, min 0.92, max 367, average "
        "17.8; coconut milk and pie filling reproduce Table 2 in full",
        lambda: {"cells": a18["b4_all"], "stats": a18["bpa"]["all"],
                 "coconut": a18["table2"]["coconut"], "pie": a18["table2"]["pie"]},
        lambda o: _full(o["cells"]) and _full(o["coconut"]) and _full(o["pie"]))

    def b5():
        b = a18["badge"]
        vals = b["values"]
        checks = {
            "k_12": b["k"] == BADGE_2018["k"],
            "all_coconut": b["by_type"] == {"coconut": b["k"]} and b["k"] > 0,
            "top_two": len(vals) >= 2 and matches(vals[0], BADGE_2018["top"][0])
            and matches(vals[1], BADGE_2018["top"][1]),
            "others_below_63": all(v < BADGE_2018["others_below"] for v in vals[2:]),
            "avg_81.9": matches(b["stats"]["mean"], BADGE_2018["avg"]),
            "all_with_bpa": b["all_with_bpa"] and b["k"] > 0,
            "no_count_gives_12pct": not any(
                matches(b[k], PCT_2018["summary_badge"])
                for k in ("pct_of_all", "pct_of_coconut", "pct_of_bpa_positive")),
        }
        return {"checks": checks, "badge": b}

    add("B5", "bpa-2018", "BADGE: exactly 12 positives, all coconut milk, top two 524 and 209, "
        "the other ten below 63, average 81.9, every one also BPA-positive; no count in the "
        "file gives 12%", b5, lambda o: all(o["checks"].values()))
    add("B6", "bpa-2018", "BPF and BPS: no positive sample",
        lambda: {"bpf_k": a18["bpf"]["k"], "bps_k": a18["bps"]["k"]},
        lambda o: o["bpf_k"] == 0 and o["bps_k"] == 0)

    rows20 = ("fish", "fruit", "meat", "pie", "veg", "all")
    add("C2", "bpa-2020", "Table 2 reproduces: at least 5 of its 6 rows match all four of "
        "positive count, min, max and average; vegetables has 51 positives (not 163)",
        lambda: {"cells": {t: a20["table2"][t] for t in rows20}, "stats": a20["bpa"],
                 "full": sum(1 for t in rows20 if _full(a20["table2"][t], CELLS))},
        lambda o: o["full"] >= MIN_FULL_ROWS and o["stats"]["veg"]["k"] == VEG_POSITIVES)
    add("C3", "bpa-2020", "Tables 3-5 reproduce: 17 BADGE, 2 BPF and 7 BPS positives in the "
        "printed product rows, every printed min, max and average matching",
        lambda: {"rows": a20["alt"], "totals": a20["alt_totals"]},
        lambda o: o["totals"] == ALT_TOTALS_2020 and all(
            all(r[c] for c in CELLS) for rows in o["rows"].values() for r in rows.values()))
    add("C4", "bpa-2020", "the co-occurrence text: 8 of 17 BADGE positives have BPA and all 8 "
        "are imported meat or fish; 14 of 17 BADGE positives are imported; every BPS-positive "
        "meat has BPA; the second-highest fish BADGE value is 51; every BPA-positive fruit or "
        "pie filling is imported",
        lambda: {"checks": a20["c4"], "observed": a20["c4_observed"]},
        lambda o: all(o["checks"].values()))
    return preds


# ---------------------------------------------------------------------------
# Data loading (network only here).
# ---------------------------------------------------------------------------
def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-bpa-2018-2020"})
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
    return "" if x is None else (round(x, 6) if isinstance(x, float) else x)


def write_samples(path, samples):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "type", "function", "origin", "region"]
                   + [f"{k}_ppb" for k in KEYS])
        for s in sorted(samples, key=lambda s: s["sample"]):
            w.writerow([s["sample"], s["product"], s["type"], s["function"], s["origin"],
                        s["region"]] + [repr(s["ppb"][k]) for k in KEYS])


def run_one(name, data_dir):
    try:
        raw, src = load(name, data_dir)
        text, enc = decode(raw)
        samples, census = parse(text, TYPE_OF[name])
        md5 = hashlib.md5(raw).hexdigest()
        provenance = {"dataset": TARGETS[name]["dataset"], "resource": TARGETS[name]["resource"],
                      "source": src, "bytes": len(raw), "encoding": enc,
                      "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                      "portal_md5": TARGETS[name]["md5"],
                      "md5_matches_portal": md5 == TARGETS[name]["md5"]}
        size = len(raw)
    except Exception as exc:  # noqa: BLE001 - the gate fails, with the reason
        samples, census, size = [], empty_census(), -1
        census["error"] = f"{type(exc).__name__}: {exc}"
        provenance = {"dataset": TARGETS[name]["dataset"], "error": census["error"]}
    return samples, census, size, provenance


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade bpa-pah-report 0.1.0 items B2-B6, C2-C4.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    got, gates = {}, {}
    for name in NAMES:
        samples, census, size, prov = run_one(name, args.data_dir)
        got[name] = (samples, census, prov)
        gates[name] = gate_checks(census, size, name)
    a18 = analyse_2018(got["bpa-2018"][0]) if all(gates["bpa-2018"].values()) else {}
    a20 = analyse_2020(got["bpa-2020"][0]) if all(gates["bpa-2020"].values()) else {}
    preds = grade(a18, a20, gates)
    for name in NAMES:
        if all(gates[name].values()):
            write_samples(os.path.join(args.out_dir, f"{name.replace('-', '_')}_samples.csv"),
                          got[name][0])
    result = {"study": "bpa-pah-report", "grader": "bpa_2018_2020", "version": VERSION,
              "predictions": preds, "analysis": {"bpa-2018": a18, "bpa-2020": a20},
              "census": {n: got[n][1] for n in NAMES},
              "provenance": {n: got[n][2] for n in NAMES},
              "n_graded": sum(1 for p in preds if p["graded"] and p["kind"] == "prediction"),
              "n_met": sum(1 for p in preds if p["met"] and p["kind"] == "prediction")}
    with open(os.path.join(args.out_dir, "bpa_2018_2020_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    print(json.dumps({"version": VERSION, "gates": gates,
                      "kinds": {n: got[n][1]["kinds"] for n in NAMES},
                      "bad_shapes": {n: got[n][1]["bad_shapes"] for n in NAMES},
                      "provenance": {n: got[n][2] for n in NAMES},
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if all(all(g.values()) for g in gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
