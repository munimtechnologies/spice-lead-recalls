#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""pah-2018 0.1.0: CFIA's open 2018-19 "Polycyclic Aromatic Hydrocarbons in Selected Foods" file
against every figure CFIA printed for it (Table 2's rows, Figure 1's per-oil-type lists and the
text's maxima and rates).

Grades docs/pah-2018-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes the survey's per-sample CSV on open.canada.ca
(dataset ec5807a2-..., Open Government Licence - Canada) and a report page that gives results as
total PAH in ppb TEQ: benzo[a]pyrene x 1 + benzo[a]anthracene x 0.1 + benzo[b]fluoranthene x 0.1 +
chrysene x 0.01. The file is gated on structure facts taken from a names-only census run before
any result value was read: its byte size from the portal record, its columns, 287 samples x 16
component rows, one unit, one plan code, the 16 known product labels and a value rule. Standard
library only. Code Apache-2.0; derived data CC BY 4.0. Not a compliance finding, not about any
brand, and not dietary or medical advice.
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
DATASET = "ec5807a2-4b96-48d9-8a8c-1f8f92ca63ad"
RESOURCE = "b39b6b72-a692-4834-b4b8-64de6ce5ed99"
PATH = ("cfia-acia-1146_2018-19_pahs_in_selected_foods_hydrocarbures-aromatiques-polycycliques-"
        "hap-dans-c.csv")
SIZE = 850814                                   # portal record "size"
CKAN_MD5 = "d36ce2a19e82ec0af7aabbe5dc3a1f36"   # portal record "hash" (reported, not gated)
N_SAMPLES = 287                                 # names-only census (= the report's 287)
N_ROWS = 4592
PLAN = "2018_TS024"
UNITS = {"ng/g"}
ID_RE = re.compile(r"^C\d{4}[A-Z]+(\d{4,6})(D?)$")
COMPONENTS = ("Acenaphthene", "Acenaphthylene", "Anthracene", "Benzo[a]anthracene",
              "Benzo[a]pyrene", "Benzo[b]fluoranthene", "Benzo[g,h,i]perylene",
              "Benzo[k]fluoranthene", "Chrysene", "Dibenzo(a,h)anthracene", "Fluoranthene",
              "Fluorene", "Indeno(1,2,3-cd)pyrene", "Naphthalene", "Phenanthrene", "Pyrene")
COMP_KEY = {c.lower(): c for c in COMPONENTS}
# The report's toxic equivalency factors (TEQ = sum of concentration x TEF).
TEF = {"Benzo[a]pyrene": 1.0, "Benzo[a]anthracene": 0.1, "Benzo[b]fluoranthene": 0.1,
       "Chrysene": 0.01}

# English product label -> report group, fixed from the names-only census before any value was
# read (label counts: baked 1 + 71 + 70 = 142, roasted vegetables 59 + 5 + 3 = 67, oils 78).
GROUP_OF = {"Baked Goods": "baked", "Bakery Product - Cookie": "baked", "Crackers": "baked",
            "Pepper (roasted)": "veg", "Tomato (roasted)": "veg",
            "Mixed Vegetable (roasted)": "veg"}
# Oil label -> Figure 1 oil type. Figure 1 has eight types; "Other" takes the three labels it does
# not name (Oil - Other 4, Oil - Coconut 3, Oil - Grapeseed 2).
OIL_TYPE = {"Oil - Canola": "canola", "Oil - Corn": "corn", "Oil - Olive": "olive",
            "Oil - Palm": "palm", "Oil - Peanut": "peanut", "Oil - Soybean": "soybean",
            "Oil - Sunflower": "sunflower", "Oil - Other": "other", "Oil - Coconut": "other",
            "Oil - Grapeseed": "other"}
LABELS = set(GROUP_OF) | set(OIL_TYPE)
GROUPS = ("baked", "oils", "veg")

# Printed Table 1 (origin): group -> (domestic, imported, unspecified, total).
TABLE1 = {"baked": (18, 42, 82, 142), "oils": (9, 59, 10, 78), "veg": (1, 65, 1, 67)}
# Printed Table 2 (ppb TEQ, positives only): group -> (n, detected, min, max, average).
TABLE2 = {"baked": (142, 51, "0.001", "1.68", "0.16"),
          "oils": (78, 55, "0.002", "2.41", "0.27"),
          "veg": (67, 27, "0.004", "9.17", "1.16"),
          "all": (287, 133, "0.001", "9.17", "0.41")}
ALL_PCT = "46"
# Printed Figure 1 (text alternative): the detected TEQ values per oil type, page order kept.
# Each list also carries one "0" for the type's non-detects (olive has none); it is left out.
FIGURE = {
    "canola": ("0.0023", "0.033759"),
    "corn": ("0.002024", "0.002182", "0.03195", "0.032658", "0.034643", "0.045364", "0.3192",
             "0.406165"),
    "olive": ("0.004196", "0.007503", "0.007558", "0.007691", "0.01578", "0.039436", "0.047001",
              "0.056015", "0.377378"),
    "palm": ("0.04904", "0.050362", "0.108161", "0.185301", "0.441651", "0.711076"),
    "peanut": ("0.4505", "0.466762", "0.53933", "0.543899", "0.683588", "0.751593", "0.910249",
               "1.749141", "2.408304"),
    "soybean": ("0.002349", "0.0385", "0.040621", "0.053368", "0.059183", "0.074653",
                "0.459065"),
    "sunflower": ("0.002349", "0.0385", "0.040621", "0.053368", "0.059183", "0.074653",
                  "0.459065"),
    "other": ("0.002667", "0.00325", "0.034017", "0.051609", "0.146624", "0.15509", "0.3548",
              "1.882423"),
}
OIL_TYPES = tuple(FIGURE)
# Text: peanut oil highest average (0.94) and maximum (2.41); canola lowest rate (18%) and lowest
# average and maximum (0.02, 0.03); one roasted red pepper at 9.17, every other roasted vegetable
# below 2.7; one baked good at 1.68, every other below 0.8.
PEANUT_AVG, PEANUT_MAX = "0.94", "2.41"
CANOLA_K, CANOLA_AVG, CANOLA_MAX = 2, "0.02", "0.03"
VEG_TOP, VEG_OTHERS_BELOW = "9.17", 2.7
BAKED_TOP, BAKED_OTHERS_BELOW = "1.68", 0.8
SUNFLOWER_K = 6                                 # P2: 55 detected oils - 49 in the other lists
MIN_FULL_TYPES = 6                              # P1: of the 7 lists other than sunflower
MIN_ROW_CELLS = 7                               # P3: of the baked and vegetable rows' 8 cells
COLS = ("sample", "component", "value", "unit", "product")


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


def group_of(product):
    if product in GROUP_OF:
        return GROUP_OF[product]
    return "oils" if product in OIL_TYPE else "unmapped"


def teq(vals):
    """Total PAH in ppb TEQ from a sample's component values (ng/g = ppb; missing = 0)."""
    return sum(f * (vals.get(c) or 0.0) for c, f in TEF.items())


def mask(raw):
    return "".join("#" if ch.isdigit() else ch for ch in clean(raw))


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def figure_match(values, printed):
    """Pair printed values with file values (each used once). 'full' = same count, all paired."""
    pool = sorted(values)
    matched = 0
    for p in sorted(printed, key=float):
        for i, v in enumerate(pool):
            if matches(v, p):
                matched += 1
                del pool[i]
                break
    return {"n_file": len(values), "n_printed": len(printed), "matched": matched,
            "full": len(values) == len(printed) == matched}


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
        "value": pick(lambda c: c.startswith("maxofamount") or c.startswith("amount")),
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


def empty_census(col=None):
    return {"columns": col or {}, "rows": 0, "units": {}, "plans": {}, "kinds": {},
            "components": {}, "bad_shapes": [], "unknown_components": 0, "samples": 0,
            "products": {}, "rows_per_sample": {}, "missing": {}, "repeated": {},
            "ids_bad": []}


def parse(text):
    """(samples, census) for the decoded CSV. Each component's value is the largest of its
    rows; a non-detect counts as 0."""
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
            s["values"].setdefault(comp, []).append(v if kind == "det" else 0.0)
    samples = [finish(s) for s in by.values()]
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


def finish(s):
    """Add component values, the TEQ, benzo[a]pyrene, the group and the oil type."""
    vals = {c: max(v) for c, v in s["values"].items()}
    s["vals"] = vals
    s["missing"] = [c for c in COMPONENTS if c not in vals]
    s["repeated"] = sorted(c for c, v in s["values"].items() if len(v) > 1)
    s["teq"] = teq(vals)
    s["bap"] = vals.get("Benzo[a]pyrene") or 0.0
    s["n_pah"] = sum(1 for c in COMPONENTS if (vals.get(c) or 0) > 0)
    s["group"] = group_of(s["product"])
    s["oil_type"] = OIL_TYPE.get(s["product"], "")
    return s


def gate_checks(census, size):
    rows = census["rows"]
    return {
        "size": size == SIZE,
        "columns": all(census["columns"].get(k) is not None for k in COLS),
        "rows": rows == N_ROWS,
        "samples": census["samples"] == N_SAMPLES and not census["ids_bad"],
        "per_sample": census["rows_per_sample"] == {str(len(COMPONENTS)): census["samples"]}
        and not census["missing"] and not census["repeated"],
        "components": rows > 0 and census["unknown_components"] == 0
        and set(census["components"]) == set(COMPONENTS),
        "units": rows > 0 and set(census["units"]) <= UNITS,
        "plan": rows > 0 and set(census["plans"]) == {PLAN},
        "products": bool(census["products"]) and set(census["products"]) <= LABELS,
        "values": rows > 0 and census["kinds"].get("bad", 0) == 0,
    }


def stats(values):
    """n, detected count, share, min, max and mean of the positive values."""
    pos = sorted(v for v in values if v > 0)
    n = len(values)
    return {"n": n, "k": len(pos), "pct": 100 * len(pos) / n if n else None,
            "min": pos[0] if pos else None, "max": pos[-1] if pos else None,
            "mean": sum(pos) / len(pos) if pos else None}


def check_row(key, st):
    """Table 2's row `key` (detected, min, max, average) against TEQ stats; n is reported."""
    n, det, mn, mx, avg = TABLE2[key]
    return {"n": st["n"] == n, "detected": st["k"] == det, "min": matches(st["min"], mn),
            "max": matches(st["max"], mx), "avg": matches(st["mean"], avg)}


def _count(d, keys=None):
    return sum(1 for k, v in d.items() if v and (keys is None or k in keys))


CELLS = ("detected", "min", "max", "avg")


def origins(samples, key):
    """key value -> [domestic, imported, unspecified, total] from the Function column."""
    out = {}
    for s in samples:
        row = out.setdefault(key(s), [0, 0, 0, 0])
        f = s["function"]
        row[0 if f == "Domestic" else 1 if f == "Import" else 2] += 1
        row[3] += 1
    return out


def printed_internal():
    """Checks among the printed figures themselves (no data)."""
    pos = {t: [float(v) for v in vals] for t, vals in FIGURE.items()}
    total = sum(sum(v) for v in pos.values())
    n = sum(len(v) for v in pos.values())
    rest = total - sum(pos["sunflower"])
    lo = TABLE2["oils"][1] * (float(TABLE2["oils"][4]) - half_unit(TABLE2["oils"][4]))
    hi = TABLE2["oils"][1] * (float(TABLE2["oils"][4]) + half_unit(TABLE2["oils"][4]))
    weighted = sum(TABLE2[g][1] * float(TABLE2[g][4]) for g in GROUPS) / TABLE2["all"][1]
    return {
        "figure_positives": n, "table2_oils_detected": TABLE2["oils"][1],
        "soybean_list_equals_sunflower_list": FIGURE["soybean"] == FIGURE["sunflower"],
        "figure_sum": total, "figure_mean": total / n,
        "figure_mean_matches_table2": matches(total / n, TABLE2["oils"][4]),
        "sunflower_sum_bounds_if_6": [lo - rest, hi - rest],
        "peanut_mean": sum(pos["peanut"]) / len(pos["peanut"]),
        "canola_mean": sum(pos["canola"]) / len(pos["canola"]),
        "table2_detected_sum": sum(TABLE2[g][1] for g in GROUPS),
        "table2_weighted_mean": weighted,
    }


def analyse(samples):
    a = {"n": len(samples)}
    by_group = {g: [s for s in samples if s["group"] == g] for g in GROUPS}
    a["groups"] = {g: stats([s["teq"] for s in by_group[g]]) for g in GROUPS}
    a["groups"]["all"] = stats([s["teq"] for s in samples])
    a["table2"] = {g: check_row(g, a["groups"][g]) for g in TABLE2}
    a["all_pct_matches"] = matches(a["groups"]["all"]["pct"], ALL_PCT)
    oils = by_group["oils"]
    a["oil_types"] = {t: stats([s["teq"] for s in oils if s["oil_type"] == t]) for t in OIL_TYPES}
    a["figure_values"] = {t: sorted(s["teq"] for s in oils if s["oil_type"] == t and s["teq"] > 0)
                          for t in OIL_TYPES}
    a["figure"] = {t: figure_match(a["figure_values"][t], FIGURE[t]) for t in OIL_TYPES}
    a["sunflower_vs_own_file"] = {
        "soybean_file_values": a["figure_values"]["soybean"],
        "sunflower_file_values": a["figure_values"]["sunflower"]}
    typed = [t for t in OIL_TYPES if a["oil_types"][t]["k"]]
    a["oil_rank"] = {
        "highest_mean": max(typed, key=lambda t: a["oil_types"][t]["mean"]) if typed else None,
        "highest_max": max(typed, key=lambda t: a["oil_types"][t]["max"]) if typed else None,
        "lowest_mean": min(typed, key=lambda t: a["oil_types"][t]["mean"]) if typed else None,
        "lowest_max": min(typed, key=lambda t: a["oil_types"][t]["max"]) if typed else None,
        "lowest_pct": min(OIL_TYPES, key=lambda t: a["oil_types"][t]["pct"] or 0),
    }
    veg = sorted(by_group["veg"], key=lambda s: -s["teq"])
    a["veg_top"] = [{"sample": s["sample"], "product": s["product"], "teq": s["teq"]}
                    for s in veg[:2]]
    a["baked_ge"] = [{"sample": s["sample"], "product": s["product"], "teq": s["teq"]}
                     for s in sorted(by_group["baked"], key=lambda s: -s["teq"])
                     if s["teq"] >= BAKED_OTHERS_BELOW]
    a["origins"] = origins(samples, lambda s: s["group"])
    a["origins_by_label"] = origins(samples, lambda s: s["product"])
    a["bap"] = {g: stats([s["bap"] for s in by_group[g]]) for g in GROUPS}
    a["any_pah"] = {g: sum(1 for s in by_group[g] if s["n_pah"] > 0) for g in GROUPS}
    a["labels"] = {}
    for s in samples:
        _bump(a["labels"], s["product"])
    a["printed_internal"] = printed_internal()
    return a


def grade(a, gate):
    gate_ok = all(gate.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": gate_ok, "observed": gate,
              "text": "byte size as on the portal record; columns; 4,592 rows; 287 samples, each "
                      "with one row per the 16 PAHs; unit ng/g and plan 2018_TS024 on every row; "
                      "the 16 known product labels; every value a number >= 0, a '<' or a "
                      "not-detected token"}]

    def add(pid, text, observe, met):
        o = observe() if gate_ok else {}
        preds.append({"id": pid, "kind": "prediction", "graded": gate_ok,
                      "met": bool(gate_ok and met(o)), "text": text, "observed": o})

    others = [t for t in OIL_TYPES if t != "sunflower"]
    add("P1", "Figure 1 reproduces for the seven oil types other than sunflower: at least 6 of "
        "the 7 lists match in full (same number of detected samples, each value at its printed "
        "precision)",
        lambda: {"figure": {t: a["figure"][t] for t in others},
                 "full": sum(1 for t in others if a["figure"][t]["full"])},
        lambda o: o["full"] >= MIN_FULL_TYPES)
    add("P2", "sunflower: the file has exactly 6 detected sunflower oils, at most 1 of the 7 "
        "printed sunflower values (a copy of the soybean list) is matched, and 55 oils are "
        "detected in all",
        lambda: {"sunflower": a["figure"]["sunflower"], "oils_detected": a["groups"]["oils"]["k"],
                 "values": a["figure_values"]["sunflower"]},
        lambda o: o["sunflower"]["n_file"] == SUNFLOWER_K and o["sunflower"]["matched"] <= 1
        and o["oils_detected"] == TABLE2["oils"][1])
    add("P3", "Table 2, baked goods and roasted vegetable products: at least 7 of the 8 cells "
        "(detected, minimum, maximum, average) match",
        lambda: {"cells": {g: a["table2"][g] for g in ("baked", "veg")},
                 "matched": sum(_count(a["table2"][g], CELLS) for g in ("baked", "veg"))},
        lambda o: o["matched"] >= MIN_ROW_CELLS)
    add("P4", "Table 2, oils: detected 55, minimum 0.002, maximum 2.41 and average 0.27 all match "
        "(the Figure 1 lists as printed would average 0.28)",
        lambda: {"cells": a["table2"]["oils"], "stats": a["groups"]["oils"]},
        lambda o: _count(o["cells"], CELLS) == 4)
    add("P5", "Table 2, grand total: 133 detected (46%), minimum 0.001, maximum 9.17 and average "
        "0.41 all match",
        lambda: {"cells": a["table2"]["all"], "pct": a["all_pct_matches"],
                 "stats": a["groups"]["all"]},
        lambda o: _count(o["cells"], CELLS) == 4 and o["pct"])

    def p6():
        ot = a["oil_types"]
        peanut, canola = ot["peanut"], ot["canola"]
        veg, baked = a["veg_top"], a["baked_ge"]
        checks = {
            "peanut_highest_mean": a["oil_rank"]["highest_mean"] == "peanut"
            and matches(peanut["mean"], PEANUT_AVG),
            "peanut_highest_max": a["oil_rank"]["highest_max"] == "peanut"
            and matches(peanut["max"], PEANUT_MAX),
            "canola_lowest": canola["k"] == CANOLA_K and canola["n"] == 11
            and a["oil_rank"]["lowest_pct"] == "canola"
            and a["oil_rank"]["lowest_mean"] == "canola"
            and a["oil_rank"]["lowest_max"] == "canola"
            and matches(canola["mean"], CANOLA_AVG) and matches(canola["max"], CANOLA_MAX),
            "veg_top_pepper": bool(veg) and veg[0]["product"] == "Pepper (roasted)"
            and matches(veg[0]["teq"], VEG_TOP)
            and (len(veg) < 2 or veg[1]["teq"] < VEG_OTHERS_BELOW),
            "one_baked_high": len(baked) == 1 and matches(baked[0]["teq"], BAKED_TOP),
        }
        return {"checks": checks, "peanut": peanut, "canola": canola, "veg_top": veg,
                "baked_ge_0.8": baked, "rank": a["oil_rank"]}

    add("P6", "the text: peanut oil has the highest average (0.94) and maximum (2.41) of the eight "
        "oil types; canola has 2 detected of 11, the lowest rate, average (0.02) and maximum "
        "(0.03); the survey maximum 9.17 is a roasted pepper and every other roasted vegetable is "
        "below 2.7; exactly one baked good is at 0.8 or more, at 1.68",
        p6, lambda o: all(o["checks"].values()))
    return preds


# ---------------------------------------------------------------------------
# Data loading (network only here).
# ---------------------------------------------------------------------------
def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-pah-2018"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(data_dir):
    local = os.path.join(data_dir, RESOURCE + ".csv") if data_dir else ""
    if local and os.path.exists(local):
        with open(local, "rb") as fh:
            raw = fh.read()
        if len(raw) == SIZE:
            return raw, "data-volume"
    errors = []
    for host in ("https://open.canada.ca", "https://ouvert.canada.ca"):
        url = f"{host}/data/dataset/{DATASET}/resource/{RESOURCE}/download/{PATH}"
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
    raise RuntimeError("no copy: " + "; ".join(errors))


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


def _num(x):
    return "" if x is None else repr(x)


def write_outputs(out_dir, samples, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "pah_2018_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "group", "oil_type", "function", "origin", "region",
                    "teq_ppb", "n_pah"] + [f"ppb:{c}" for c in COMPONENTS])
        for s in sorted(samples, key=lambda s: s["sample"]):
            w.writerow([s["sample"], s["product"], s["group"], s["oil_type"], s["function"],
                        s["origin"], s["region"], repr(s["teq"]), s["n_pah"]]
                       + [_num(s["vals"].get(c)) for c in COMPONENTS])
    result = {"study": "pah-2018", "version": VERSION, "predictions": preds, "census": census,
              "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "pah_2018_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the pah-2018 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    try:
        raw, src = load(args.data_dir)
        text, enc = decode(raw)
        samples, census = parse(text)
        provenance = {"dataset": DATASET, "resource": RESOURCE, "source": src, "bytes": len(raw),
                      "encoding": enc, "sha256": hashlib.sha256(raw).hexdigest(),
                      "md5": hashlib.md5(raw).hexdigest(), "portal_md5": CKAN_MD5,
                      "md5_matches_portal": hashlib.md5(raw).hexdigest() == CKAN_MD5}
        size = len(raw)
    except Exception as exc:  # noqa: BLE001 - the gate fails, with the reason
        samples, census, size = [], empty_census(), -1
        census["error"] = f"{type(exc).__name__}: {exc}"
        provenance = {"dataset": DATASET, "resource": RESOURCE, "error": census["error"]}
    gate = gate_checks(census, size)
    a = analyse(samples) if all(gate.values()) else {"printed_internal": printed_internal()}
    preds = grade(a, gate)
    result = write_outputs(args.out_dir, samples, census, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate, "kinds": census["kinds"],
                      "bad_shapes": census["bad_shapes"], "products": census["products"],
                      "ids_bad": census["ids_bad"], "provenance": provenance,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if all(gate.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
