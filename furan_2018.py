#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""furan-2018 0.1.0: CFIA's open 2018-19 furan, 2-methylfuran and 3-methylfuran file against every
figure CFIA printed for it (Tables 2 and 3, the per-sample Figure 1 values, and the text).

Grades docs/furan-2018-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes the survey's per-sample CSV on open.canada.ca
(dataset 50b2bcf4-..., Open Government Licence - Canada) and a report page with a furans table,
a furan-only table and a figure listing every detected sample's furans level. The file is gated
on structure facts fixed before any result value was summed: its byte size from the portal
record, its columns, 250 samples x 3 analyte rows, one unit, one plan code, known product and
component labels, and a value rule. Standard library only. Code Apache-2.0; derived data
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
import sys
import time
import unicodedata
import urllib.request

VERSION = "0.1.0"
DATASET = "50b2bcf4-becc-493b-b804-88d6fb6f0a84"
RESOURCE = "db10687a-8d0f-45b0-9dea-aee7465d4af6"
PATH = ("cfia-acia-1147_2018-19_furans_in_selected_foods_presence-de-furane-de-2-methylfurane-"
        "et-de-3-met.csv")
SIZE = 133082                                   # portal record "size"
CKAN_MD5 = "fe69bb5a34dcfc5b4f2a4c1774a92dd5"   # portal record "hash" (reported, not gated)
N_SAMPLES = 250
N_ROWS = 750
UNIT = "ng/g"
PLAN = "2018_TS023"
ANALYTES = {"furan": "F", "2-methylfuran": "2MF", "3-methylfuran": "3MF"}

# English product label -> report product type, fixed before any value was read. "Dairy
# Alternative" is split by rule: a sample with furans detected goes to canned milk, one without to
# dried dairy products (the report prints 0 of 42 dried dairy products with furans). P4 tests it.
CATEGORY = {"Fish/Seafood - Canned": "canned-fish", "Meat - Canned": "canned-meat",
            "Sauce - Soy": "soy-sauce", "Evaporated Milk": "canned-milk",
            "Milk Powder": "dried-dairy", "Beverage - Powdered Mixes - Hot": "dried-beverage",
            "Beverage - Powdered Mixes - Cold": "dried-beverage"}
SPLIT_LABEL = "Dairy Alternative"
LABELS = set(CATEGORY) | {SPLIT_LABEL}
CATS = ("canned-fish", "canned-meat", "canned-milk", "dried-beverage", "dried-dairy", "soy-sauce")

# Printed Table 2 (furans = sum of the three; ppb; averages of positives only): category ->
# (samples, detected, minimum, maximum, average). Strings keep the printed precision.
TABLE2 = {"canned-fish": (50, 50, "16.3", "146", "46.6"),
          "canned-meat": (50, 50, "10.8", "64", "31.1"),
          "canned-milk": (16, 10, "13.9", "33.2", "19.8"),
          "dried-beverage": (42, 15, "5.1", "22.5", "9.7"),
          "dried-dairy": (42, 0, "0", "0", "0"),
          "soy-sauce": (50, 50, "1.2", "179", "73.8")}
GRAND = (250, 176, "1.2", "179", "45.5")
# Printed Table 3, CFIA rows (furan only; averages of positives only): (n, min, max, average).
TABLE3 = {"canned-fish": (50, "1.62", "64.4", "16.9"), "canned-meat": (50, "1.19", "40", "14"),
          "canned-milk": (16, "1.27", "20.8", "6.87"),
          "dried-beverage": (43, "2.7", "8.22", "5.43"),
          "dried-dairy": (42, "0", "0", "0"), "soy-sauce": (50, "1.09", "159", "38.5")}
# Printed Figure 1: furans (ppb) of every detected sample, in the page's order.
FIGURE = {
    "canned-fish": (
        "16.25 17.13 17.15 20.16 20.36 21.94 23.15 23.63 25.02 25.12 27.02 27.19 27.5 27.78 "
        "27.833 29.71 33.46 34.24 35.06 35.75 35.87 37.43 37.66 38.15 38.25 39.24 40.12 41.56 "
        "45.5 45.6 46.03 46.08 48.44 51.66 53.94 56.45 57.36 61.27 61.61 62.09 62.13 63.9 74.18 "
        "75.58 79.07 81.87 83.76 91.67 112.67 145.51").split(),
    "canned-meat": (
        "10.84 11 16.54 16.81 19.13 19.41 19.52 20.3 21.58 21.62 22.54 22.84 23.39 24.16 24.63 "
        "24.65 24.82 25.91 26.78 27.27 27.32 27.66 28.16 28.56 28.87 28.88 29.07 29.56 30.07 "
        "30.84 31.1 31.63 31.66 33.9 36.35 36.42 36.44 38.17 38 39.67 41.15 41.97 42.38 43.49 "
        "44.32 46.48 53.95 54.02 59.09 63.99").split(),
    "canned-milk": "13.9 15.15 15.84 16.74 17.15 17.92 22.2 23.01 23.31 33.23".split(),
    "dried-beverage": (
        "5.05 5.08 5.4 5.42 5.64 5.89 6.12 8.09 11.38 12.37 12.92 13.08 16.44 19.76 "
        "22.54").split(),
    "soy-sauce": (
        "1.23 7.5 8.46 10.25 11.21 11.93 12.71 13.62 15.07 15.3 15.59 17.42 18.5 24.35 31.57 "
        "45.06 49.84 55.01 64.88 65.03 66.72 67.27 71.54 74.21 78.44 78.83 83.97 85.42 87.48 "
        "91.38 96.16 97.39 98.42 98.6 99.05 99.82 102.05 110.26 112.18 113.16 116.51 117.19 "
        "126.46 126.51 127.69 131.33 145.25 149.18 164.65 179.33").split(),
}
# Printed text: overall range "1.23 ppb to 179 ppb"; "12 samples contained all 3", "11 of which
# were canned meat"; 52% contained a single analogue; 38% furan and 2-methylfuran together.
TEXT_RANGE = ("1.23", "179")
ALL3 = (12, 11)
PCT_ONE, PCT_F2 = "52", "38"
# P1: the lost beverage positive is at most this large (155.18 / 16 must round to 9.7).
P1_MAX_EXTRA = 0.82
P2_RANGE = (45.0, 45.4)
P4_LABELS = {"Evaporated Milk": 15, "Milk Powder": 38, SPLIT_LABEL: 5, "beverage": 42}
COLS = ("sample", "component", "value", "unit", "product")


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def clean(cell):
    """A cell without BOM, edge spaces or repeated inner spaces, in NFC form, with en and em
    dashes read as hyphens (so 'Meat – Canned' equals 'Meat - Canned')."""
    s = unicodedata.normalize("NFC", (cell or "").replace("﻿", ""))
    s = s.replace("–", "-").replace("—", "-")
    return " ".join(s.split())


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


def analyte(text):
    """'F', '2MF' or '3MF' for a component cell (English part), else None."""
    return ANALYTES.get(clean(text).lower().split("/")[0].strip())


def mask(raw):
    return "".join("#" if ch.isdigit() else ch for ch in clean(raw))


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
        "plan": pick(lambda c: c.startswith("plan code") or c == "plan"),
        "date": pick(lambda c: c.startswith("date sampled")),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def _cell(r, i):
    return r[i] if i is not None and i < len(r) else ""


def empty_census(col=None):
    return {"columns": col or {}, "rows": 0, "units": {}, "plans": {}, "kinds": {},
            "components": {}, "bad_shapes": [], "unknown_components": 0, "samples": 0,
            "products": {}, "rows_per_sample": {}, "missing_analyte": {}, "repeated_analyte": {},
            "ids_expected": False}


def expected_ids():
    return {f"C2018FRAN{i:05d}" for i in range(1, N_SAMPLES + 1)}


def parse(text):
    """(samples, census) for the decoded CSV. Each analyte's value is the largest of its rows;
    a sample's furans level is the sum over the analytes it has; it is detected if above 0."""
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
        comp = clean(_cell(r, col["component"]))
        _bump(census["components"], comp)
        a = analyte(comp)
        if a is None:
            census["unknown_components"] += 1
        raw = clean(_cell(r, col["value"]))
        v, kind = parse_value(raw)
        _bump(census["kinds"], kind)
        if kind == "bad" and mask(raw) not in census["bad_shapes"]:
            census["bad_shapes"].append(mask(raw))
        _bump(census["units"], clean(_cell(r, col["unit"])).lower().replace(" ", ""))
        _bump(census["plans"], clean(_cell(r, col["plan"])))
        sid = clean(_cell(r, col["sample"]))
        s = by.get(sid)
        if s is None:
            s = by[sid] = {"sample": sid, "product": clean(_cell(r, col["product"])),
                           "origin": clean(_cell(r, col["origin"])),
                           "function": clean(_cell(r, col["function"])),
                           "date": clean(_cell(r, col["date"])),
                           "raws": [], "analytes": {}, "bad": False}
        s["raws"].append(f"{a or comp}={raw}")
        if kind == "bad":
            s["bad"] = True
        if a is not None:
            s["analytes"].setdefault(a, []).append(v if kind == "det" else 0.0)
    samples = [finish(s) for s in by.values()]
    for s in samples:
        _bump(census["products"], s["product"])
        _bump(census["rows_per_sample"], str(len(s["raws"])))
        if s["missing"]:
            census["missing_analyte"][s["sample"]] = s["missing"]
        if s["repeated"]:
            census["repeated_analyte"][s["sample"]] = s["repeated"]
    census["samples"] = len(samples)
    census["ids_expected"] = {s["sample"] for s in samples} == expected_ids()
    return samples, census


def finish(s):
    """Add per-analyte values, the furans sum, detection and the report category."""
    vals = {a: max(v) for a, v in s["analytes"].items()}
    s["F"], s["2MF"], s["3MF"] = vals.get("F"), vals.get("2MF"), vals.get("3MF")
    s["missing"] = [a for a in ("F", "2MF", "3MF") if a not in vals]
    s["repeated"] = [a for a, v in sorted(s["analytes"].items()) if len(v) > 1]
    s["sum"] = sum(vals.values())
    s["n_detected"] = sum(1 for v in vals.values() if v > 0)
    s["kind"] = "bad" if s["bad"] else ("det" if s["sum"] > 0 else "nd")
    s["category"] = category(s["product"], s["sum"])
    return s


def category(product, total):
    if product == SPLIT_LABEL:
        return "canned-milk" if total > 0 else "dried-dairy"
    return CATEGORY.get(product, "unmapped")


def gate_checks(census, size):
    return {
        "size": size == SIZE,
        "columns": all(census["columns"].get(k) is not None for k in COLS),
        "rows": census["rows"] == N_ROWS,
        "samples": census["samples"] == N_SAMPLES and census["ids_expected"],
        "components": census["rows"] > 0 and census["unknown_components"] == 0,
        "units": census["units"] == {UNIT: N_ROWS},
        "plan": census["plans"] == {PLAN: N_ROWS},
        "products": bool(census["products"]) and set(census["products"]) <= LABELS,
        "values": census["rows"] > 0 and census["kinds"].get("bad", 0) == 0,
    }


def stats(values):
    v = sorted(values)
    return {"k": len(v), "min": v[0] if v else None, "max": v[-1] if v else None,
            "sum": sum(v), "mean": sum(v) / len(v) if v else None}


def cat_stats(samples):
    out = {}
    for s in samples:
        c = out.setdefault(s["category"], {"n": 0, "sums": [], "furan": []})
        c["n"] += 1
        if s["sum"] > 0:
            c["sums"].append(s["sum"])
        if (s["F"] or 0) > 0:
            c["furan"].append(s["F"])
    for c in out.values():
        c["sums"].sort()
        c["furan"].sort()
        c["furans_stats"] = stats(c["sums"])
        c["furan_stats"] = stats(c["furan"])
    return out


def match_figure(file_values, printed):
    """Pair each printed value with a distinct file value that rounds to it (most precise
    printed values first, closest file value wins). Returns matched count, the printed values
    left unmatched and the file values left over."""
    pool = sorted(file_values)
    used = [False] * len(pool)
    order = sorted(printed, key=lambda p: (-len(p.split(".")[1]) if "." in p else 0, float(p)))
    unmatched = []
    for p in order:
        best = None
        for i, v in enumerate(pool):
            if not used[i] and matches(v, p):
                if best is None or abs(v - float(p)) < abs(pool[best] - float(p)):
                    best = i
        if best is None:
            unmatched.append(p)
        else:
            used[best] = True
    extras = [v for i, v in enumerate(pool) if not used[i]]
    return {"printed": len(printed), "matched": len(printed) - len(unmatched),
            "unmatched": unmatched, "extras": extras}


def printed_internal():
    """Checks among the printed figures themselves (no data)."""
    out = {"table2_detected_sum": sum(r[1] for r in TABLE2.values()),
           "table2_samples_sum": sum(r[0] for r in TABLE2.values()), "figure": {}}
    total = 0.0
    count = 0
    for cat, vals in FIGURE.items():
        s = sum(float(v) for v in vals)
        total += s
        count += len(vals)
        out["figure"][cat] = {"n": len(vals), "sum": s, "mean": s / len(vals),
                              "table2_mean": TABLE2[cat][4],
                              "mean_matches_table2": matches(s / len(vals), TABLE2[cat][4])}
    out["figure_n"] = count
    out["figure_mean_all"] = total / count
    out["figure_sum_over_176"] = total / GRAND[1]
    bev = out["figure"]["dried-beverage"]
    out["beverage_sum_over_16"] = bev["sum"] / 16
    return out


def analyse(samples):
    cats = cat_stats(samples)
    pos = [s for s in samples if s["sum"] > 0]
    a = {"cats": cats, "grand": stats([s["sum"] for s in pos]), "n": len(samples)}
    a["n_one"] = sum(1 for s in pos if s["n_detected"] == 1)
    a["n_f_2mf"] = sum(1 for s in pos if (s["F"] or 0) > 0 and (s["2MF"] or 0) > 0)
    a["n_f_2mf_only"] = sum(1 for s in pos if (s["F"] or 0) > 0 and (s["2MF"] or 0) > 0
                            and not (s["3MF"] or 0) > 0)
    all3 = [s for s in pos if s["n_detected"] == 3]
    a["all3"] = {"n": len(all3), "canned_meat": sum(1 for s in all3
                                                    if s["category"] == "canned-meat")}
    a["figure"] = {cat: match_figure(cats.get(cat, {"sums": []})["sums"], vals)
                   for cat, vals in FIGURE.items()}
    a["labels"] = {}
    for s in samples:
        _bump(a["labels"], s["product"])
    a["split"] = [{"sample": s["sample"], "sum": s["sum"], "category": s["category"]}
                  for s in samples if s["product"] == SPLIT_LABEL]
    a["origin"] = {}
    for s in samples:
        o = a["origin"].setdefault(s["category"], {})
        _bump(o, s["function"] or "(blank)")
    a["printed_internal"] = printed_internal()
    return a


def check_table2(cat, c):
    n, det, mn, mx, avg = TABLE2[cat]
    f = c["furans_stats"]
    ok = {"n": c["n"] == n, "detected": f["k"] == det}
    if det:
        ok.update({"min": matches(f["min"], mn), "max": matches(f["max"], mx),
                   "mean": matches(f["mean"], avg)})
    return ok


def check_table3(cat, c):
    n, mn, mx, avg = TABLE3[cat]
    f = c["furan_stats"]
    if float(mx) == 0:
        return {"n": c["n"] == n, "none_detected": f["k"] == 0}
    return {"n": c["n"] == n, "min": matches(f["min"], mn), "max": matches(f["max"], mx),
            "mean": matches(f["mean"], avg)}


def _all(d):
    return bool(d) and all(d.values())


def grade(a, gate):
    gate_ok = all(gate.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": gate_ok, "observed": gate,
              "text": "byte size as on the portal record; columns; 750 rows and samples "
                      "C2018FRAN00001-00250; only the three analyte labels; unit ng/g and plan "
                      "2018_TS023 on every row; known product labels; every value a number "
                      ">= 0, a '<' or a not-detected token"}]

    def add(pid, kind, text, observe, met):
        o = observe() if gate_ok else {}
        preds.append({"id": pid, "kind": kind, "graded": gate_ok,
                      "met": bool(gate_ok and met(o)), "text": text, "observed": o})

    empty = {"n": 0, "sums": [], "furan": [], "furans_stats": stats([]),
             "furan_stats": stats([])}
    five = [c for c in CATS if c != "dried-beverage"]
    add("C2", "consistency", "Table 2 (furans), every row but dried beverage mixes: samples, "
        "detected, minimum, maximum and positives-only average",
        lambda: {c: {"ok": check_table2(c, a["cats"].get(c, empty)),
                     "file": a["cats"].get(c, empty)["furans_stats"]} for c in five},
        lambda o: all(_all(r["ok"]) for r in o.values()))
    add("C3", "consistency", "Table 3 (furan only), every CFIA row but dried beverage mixes: "
        "samples, minimum, maximum and positives-only average",
        lambda: {c: {"ok": check_table3(c, a["cats"].get(c, empty)),
                     "file": a["cats"].get(c, empty)["furan_stats"]} for c in five},
        lambda o: all(_all(r["ok"]) for r in o.values()))
    add("CF", "consistency", "Figure 1: each of the 175 printed values is matched by a distinct "
        "detected sample of its product type, with no unprinted detected sample except in dried "
        "beverage mixes (graded in P1)",
        lambda: a["figure"],
        lambda o: all(r["matched"] == r["printed"] for r in o.values())
        and all(not r["extras"] for c, r in o.items() if c != "dried-beverage"))
    add("CT", "consistency", "text: 12 samples with all three analogues, 11 of them canned "
        "meat; overall range 1.23 to 179 ppb",
        lambda: {"all3": a["all3"], "min": a["grand"]["min"], "max": a["grand"]["max"]},
        lambda o: (o["all3"]["n"], o["all3"]["canned_meat"]) == ALL3
        and matches(o["min"], TEXT_RANGE[0]) and matches(o["max"], TEXT_RANGE[1]))

    def p1():
        bev = a["cats"].get("dried-beverage", empty)
        return {"detected_samples": a["grand"]["k"], "beverage_n": bev["n"],
                "beverage_detected": bev["furans_stats"]["k"],
                "beverage_mean": bev["furans_stats"]["mean"],
                "beverage_unprinted": a["figure"]["dried-beverage"]["extras"]}

    add("P1", "prediction", "176 samples have a furans level above 0 (the printed total, not "
        "the 175 its rows add to): one is a dried beverage mix at or below 0.82 ppb that Figure 1 "
        "and the 15-detected count leave out, and that the printed 9.7 ppb average includes",
        p1, lambda o: o["detected_samples"] == GRAND[1] and o["beverage_detected"] == 16
        and len(o["beverage_unprinted"]) == 1 and o["beverage_unprinted"][0] <= P1_MAX_EXTRA
        and matches(o["beverage_mean"], TABLE2["dried-beverage"][4]))
    add("P2", "prediction", "the positives-only average over all detected samples is 45.0 to "
        "45.4 ppb, not the printed 45.5",
        lambda: {"mean": a["grand"]["mean"], "k": a["grand"]["k"]},
        lambda o: o["mean"] is not None and P2_RANGE[0] <= o["mean"] <= P2_RANGE[1]
        and not matches(o["mean"], GRAND[4]))

    def p3():
        k = a["grand"]["k"]
        return {"detected": k, "one": a["n_one"], "f_and_2mf": a["n_f_2mf"],
                "one_pct_of_detected": 100 * a["n_one"] / k if k else None,
                "f_and_2mf_pct_of_detected": 100 * a["n_f_2mf"] / k if k else None,
                "one_pct_of_250": 100 * a["n_one"] / N_SAMPLES,
                "f_and_2mf_pct_of_250": 100 * a["n_f_2mf"] / N_SAMPLES}

    add("P3", "prediction", "the text's '52%' (one analogue only) and '38%' (furan and "
        "2-methylfuran) are shares of the detected samples, not of all 250",
        p3, lambda o: matches(o["one_pct_of_detected"], PCT_ONE)
        and matches(o["f_and_2mf_pct_of_detected"], PCT_F2)
        and not matches(o["one_pct_of_250"], PCT_ONE)
        and not matches(o["f_and_2mf_pct_of_250"], PCT_F2))

    def p4():
        lab = a["labels"]
        bev = lab.get("Beverage - Powdered Mixes - Hot", 0) + \
            lab.get("Beverage - Powdered Mixes - Cold", 0)
        return {"labels": lab, "beverage": bev, "split": a["split"],
                "split_detected": sum(1 for s in a["split"] if s["sum"] > 0)}

    add("P4", "prediction", "labels: 15 Evaporated Milk, 38 Milk Powder, 5 Dairy Alternative and "
        "42 powdered beverage mixes (so Table 3's '43' is a slip); exactly one Dairy Alternative "
        "has furans, making canned milk 16 and dried dairy products 42",
        p4, lambda o: all(o["labels"].get(k, 0) == v for k, v in P4_LABELS.items()
                          if k != "beverage")
        and o["beverage"] == P4_LABELS["beverage"] and o["split_detected"] == 1)
    return preds


# ---------------------------------------------------------------------------
# Data loading (network only here).
# ---------------------------------------------------------------------------
def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-furan-2018"})
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
    with open(os.path.join(out_dir, "furan_2018_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "category", "origin", "function", "date", "n_rows",
                    "values_raw", "furan_ppb", "methylfuran_2_ppb", "methylfuran_3_ppb",
                    "furans_ppb", "n_detected", "kind"])
        for s in sorted(samples, key=lambda s: s["sample"]):
            w.writerow([s["sample"], s["product"], s["category"], s["origin"], s["function"],
                        s["date"], len(s["raws"]), ";".join(s["raws"]), _num(s["F"]),
                        _num(s["2MF"]), _num(s["3MF"]), repr(s["sum"]), s["n_detected"],
                        s["kind"]])
    slim = dict(a)
    slim["cats"] = {c: {k: v for k, v in d.items()} for c, d in a.get("cats", {}).items()}
    result = {"study": "furan-2018", "version": VERSION, "predictions": preds, "census": census,
              "analysis": slim, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "furan_2018_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the furan-2018 0.1.0 pre-registration.")
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
                      "missing_analyte": census["missing_analyte"],
                      "repeated_analyte": census["repeated_analyte"],
                      "provenance": provenance,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if all(gate.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
