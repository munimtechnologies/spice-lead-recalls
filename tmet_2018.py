#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""tmet-2018 0.1.0: CFIA's open 2018-19 "Toxic Metals in Selected Foods" file against every figure
CFIA printed for it (Table 2's arsenic, cadmium, lead and mercury cells per product type, and the
text's counts, shares and maxima).

Grades docs/tmet-2018-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes the survey's per-sample CSV on open.canada.ca
(dataset 2b47b561-..., Open Government Licence - Canada) and a report page with an origin table,
a per-type table for the four toxic metals and text figures. The file is gated on structure facts
taken from a names-only census run before any result value was read: its byte size from the
portal record, its columns, 987 samples x 19 component rows, one unit, one plan code, the 25
known product labels and a value rule. Standard library only. Code Apache-2.0; derived data
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
DATASET = "2b47b561-44dc-4aeb-8a4d-72262f0dfe68"
RESOURCE = "0e040e20-f157-46ce-860b-186b294ce1f7"
PATH = ("cfia-acia-1148_2018-19_toxic_metals_in_selected_foods_-_-2018-2019_metaux-toxiques-"
        "dans-certains.csv")
SIZE = 3221954                                  # portal record "size"
CKAN_MD5 = "57017a0e02e19f4c1c3c9c97f3705e18"   # portal record "hash" (reported, not gated)
N_SAMPLES = 987                                 # names-only census (the report prints 985)
N_ROWS = 18753
PLAN = "2018_TS013"
UNITS = {"µg/g", "μg/g", "ug/g"}      # the file's micro sign is U+00B5 (cp1252)
ID_RE = re.compile(r"^C2018TMET(\d{5})(D?)$")
COMPONENTS = ("Aluminum", "Antimony", "Arsenic", "Beryllium", "Boron", "Cadmium", "Chromium",
              "Copper", "Iron", "Lead", "Magnesium", "Manganese", "Mercury", "Molybdenum",
              "Nickel", "Selenium", "Tin", "Titanium", "Zinc")
COMP_KEY = {c.lower(): c for c in COMPONENTS}
METALS = {"Arsenic": "As", "Cadmium": "Cd", "Lead": "Pb", "Mercury": "Hg"}
TOXIC = ("As", "Cd", "Pb", "Hg")

# English product label -> report product type, fixed from the names-only census before any value
# was read. Labels outside FIXED are bran products, except the pair a reading moves to rice
# products: only two whole-label pairs reproduce Table 1's origin counts (P3 tests which one).
IF_LABELS = ("Infant Formula - Dairy", "Infant Formula - Other", "Infant Formula - Soy")
FIXED = {**{label: "infant-formula" for label in IF_LABELS},
         "Meal Replacement": "meal-replacement", "Protein Powder": "protein-powder",
         "Rice Products": "rice", "Bran - Rice": "rice", "Cereal - Rice": "rice",
         "Grain - Rice": "rice"}
BRAN_LABELS = ("Bakery Product - Cookie", "Baking Mixes", "Bran - Oat", "Bran - Wheat", "Cereal",
               "Cereal - Corn", "Cereal - Mixed Grains", "Cereal - Oat", "Cereal - Wheat",
               "Corn Products", "Crackers", "Granola/Cereal Bar", "Oat Products", "Oil - Other",
               "Popcorn", "Snack Bar")
READINGS = {"R1": ("Oil - Other", "Crackers"), "R2": ("Popcorn", "Snack Bar")}
LABELS = set(FIXED) | set(BRAN_LABELS)
TYPES = ("bran", "infant-formula", "meal-replacement", "protein-powder", "rice")

# Printed Table 1 (origin): type -> (domestic, imported, unspecified, total).
TABLE1 = {"bran": (23, 41, 35, 99), "infant-formula": (0, 386, 9, 395),
          "meal-replacement": (16, 135, 47, 198), "protein-powder": (72, 34, 89, 195),
          "rice": (77, 19, 2, 98)}
# Printed Table 2 (ppm; averages of quantifiable results only): type -> (n, {metal: (% positive,
# average, maximum)}). Strings keep the printed precision.
TABLE2 = {
    "bran": (99, {"As": ("78", "0.024", "0.079"), "Cd": ("71", "0.043", "0.186"),
                  "Pb": ("24", "0.023", "0.130"), "Hg": ("4", "0.0013", "0.002")}),
    "infant-formula": (395, {"As": ("52", "0.016", "0.040"), "Cd": ("9", "0.011", "0.020"),
                             "Pb": ("13", "0.012", "0.020"), "Hg": ("1", "0.002", "0.003")}),
    "meal-replacement": (198, {"As": ("44", "0.022", "0.139"), "Cd": ("31", "0.037", "0.190"),
                               "Pb": ("40", "0.024", "0.231"), "Hg": ("9", "0.002", "0.006")}),
    "protein-powder": (195, {"As": ("84", "0.028", "0.214"), "Cd": ("82", "0.060", "0.219"),
                             "Pb": ("71", "0.035", "0.237"), "Hg": ("50", "0.003", "0.022")}),
    "rice": (98, {"As": ("95", "0.263", "1.130"), "Cd": ("63", "0.016", "0.056"),
                  "Pb": ("37", "0.018", "0.050"), "Hg": ("71", "0.003", "0.006")}),
}
PRINTED_N = 985
# Printed text: 70% with one or more of the four metals, 12% with all four; arsenic in 64%,
# mercury in 19%; cadmium not detected in 596 of 985, lead in 656; mercury in only 2 infant
# formula samples; the highest arsenic 1.12 and 1.13 ppm in brown rice bran and germ powder; the
# highest mercury 0.022 ppm in a brown rice protein powder.
TEXT_PCT = {"any": "70", "all4": "12", "As": "64", "Hg": "19"}
TEXT_ND = {"Cd": 596, "Pb": 656}
ND_SLACK = 2                                    # the file's two samples beyond the printed 985
IF_HG = 2
AS_TOP = ("1.13", "1.12")
HG_MAX = "0.022"
MIN_CELLS = 10                                  # P1/P2: of a row's 12 cells
MIN_SPLIT_CELLS = 20                            # P3: of the bran and rice rows' 24 cells
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


def type_of(product, reading):
    """Report product type of a label under reading 'R1' or 'R2'."""
    if product in FIXED:
        return FIXED[product]
    if product in READINGS[reading]:
        return "rice"
    return "bran" if product in BRAN_LABELS else "unmapped"


def mask(raw):
    return "".join("#" if ch.isdigit() else ch for ch in clean(raw))


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def consistent_counts(pct, n):
    """Every count k of n whose share 100k/n rounds to the printed percentage."""
    return [k for k in range(n + 1) if matches(100 * k / n, pct)]


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
    """Add component values, the four toxic metals, the duplicate flag and the base ID."""
    vals = {c: max(v) for c, v in s["values"].items()}
    s["vals"] = vals
    s["missing"] = [c for c in COMPONENTS if c not in vals]
    s["repeated"] = sorted(c for c, v in s["values"].items() if len(v) > 1)
    for name, sym in METALS.items():
        s[sym] = vals.get(name)
    s["n_toxic"] = sum(1 for m in TOXIC if (s[m] or 0) > 0)
    m = ID_RE.match(s["sample"])
    s["dup"] = bool(m and m.group(2))
    s["base"] = f"C2018TMET{m.group(1)}" if m else s["sample"]
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


def metal_stats(samples, m):
    pos = sorted(s[m] for s in samples if (s[m] or 0) > 0)
    n = len(samples)
    return {"n": n, "k": len(pos), "pct": 100 * len(pos) / n if n else None,
            "mean": sum(pos) / len(pos) if pos else None,
            "min": pos[0] if pos else None, "max": pos[-1] if pos else None}


def empty_row():
    return {"n": 0, **{m: metal_stats([], m) for m in TOXIC}}


def type_table(samples, reading):
    groups = {}
    for s in samples:
        groups.setdefault(type_of(s["product"], reading), []).append(s)
    return {t: {"n": len(g), **{m: metal_stats(g, m) for m in TOXIC}} for t, g in groups.items()}


def check_row(t, row):
    """Table 2's 12 cells of type t (% positive, average, maximum per metal) against a row."""
    out = {}
    for m in TOXIC:
        pct, avg, mx = TABLE2[t][1][m]
        st = row[m]
        out[f"{m}_pct"] = matches(st["pct"], pct)
        out[f"{m}_avg"] = matches(st["mean"], avg)
        out[f"{m}_max"] = matches(st["max"], mx)
    return out


def _count(d):
    return sum(1 for v in d.values() if v)


def origins(samples, reading):
    """type -> [domestic, imported, unspecified, total] from the Function column."""
    out = {}
    for s in samples:
        row = out.setdefault(type_of(s["product"], reading), [0, 0, 0, 0])
        f = s["function"]
        row[0 if f == "Domestic" else 1 if f == "Import" else 2] += 1
        row[3] += 1
    return out


def printed_internal():
    """Checks among the printed figures themselves (no data): for each metal, the smallest and
    largest total of Table 2 counts consistent with the printed percentages."""
    out = {"table1_total": sum(r[3] for r in TABLE1.values()),
           "table2_total": sum(r[0] for r in TABLE2.values()), "counts": {}}
    for m in TOXIC:
        lo = hi = 0
        for t in TYPES:
            n, cells = TABLE2[t]
            ks = consistent_counts(cells[m][0], n)
            lo += ks[0] if ks else 0
            hi += ks[-1] if ks else 0
        out["counts"][m] = {"min": lo, "max": hi}
    for m, nd in TEXT_ND.items():
        c = out["counts"][m]
        c["text_detected"] = PRINTED_N - nd
        c["text_fits"] = c["min"] <= PRINTED_N - nd <= c["max"]
    return out


def analyse(samples):
    ids = {s["sample"] for s in samples}
    a = {"n": len(samples)}
    a["tables"] = {r: type_table(samples, r) for r in READINGS}
    a["cells"] = {r: {t: check_row(t, a["tables"][r].get(t) or empty_row()) for t in TYPES}
                  for r in READINGS}
    keep = [s for s in samples if not (s["dup"] and s["base"] in ids)]
    drop_tables = type_table(keep, "R1")
    a["drop_d"] = {"n": len(keep), "tables": drop_tables,
                   "cells": {t: check_row(t, drop_tables.get(t) or empty_row())
                             for t in TYPES}}
    a["overall"] = {m: metal_stats(samples, m) for m in TOXIC}
    a["nd"] = {m: a["overall"][m]["n"] - a["overall"][m]["k"] for m in TOXIC}
    n = len(samples)
    a["any"] = sum(1 for s in samples if s["n_toxic"] >= 1)
    a["all4"] = sum(1 for s in samples if s["n_toxic"] == 4)
    a["any_pct"] = 100 * a["any"] / n if n else None
    a["all4_pct"] = 100 * a["all4"] / n if n else None
    a["if_hg"] = sum(1 for s in samples if s["product"] in IF_LABELS and (s["Hg"] or 0) > 0)
    top = sorted((s for s in samples if (s["As"] or 0) > 0), key=lambda s: -s["As"])[:2]
    a["as_top"] = [{"sample": s["sample"], "product": s["product"], "As": s["As"]} for s in top]
    hg = [s["Hg"] for s in samples if (s["Hg"] or 0) > 0]
    hg_max = max(hg) if hg else None
    a["hg_top"] = {"max": hg_max, "holders": [{"sample": s["sample"], "product": s["product"]}
                                              for s in samples
                                              if hg_max is not None and s["Hg"] == hg_max]}
    a["dups"] = [{"sample": s["sample"], "base": s["base"], "base_present": s["base"] in ids,
                  "product": s["product"], "function": s["function"]}
                 for s in sorted(samples, key=lambda s: s["sample"]) if s["dup"]]
    a["origins"] = {r: origins(samples, r) for r in READINGS}
    a["labels"] = {}
    for s in samples:
        _bump(a["labels"], s["product"])
    a["lowest_positive"] = {m: a["overall"][m]["min"] for m in TOXIC}
    a["printed_internal"] = printed_internal()
    return a


def grade(a, gate):
    gate_ok = all(gate.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": gate_ok, "observed": gate,
              "text": "byte size as on the portal record; columns; 18,753 rows; 987 samples "
                      "with IDs C2018TMET##### (or a D suffix), each with one row per the 19 "
                      "components; unit ug/g and plan 2018_TS013 on every row; the 25 known "
                      "product labels; every value a number >= 0, a '<' or a not-detected token"}]

    def add(pid, kind, text, observe, met):
        o = observe() if gate_ok else {}
        preds.append({"id": pid, "kind": kind, "graded": gate_ok,
                      "met": bool(gate_ok and met(o)), "text": text, "observed": o})

    def row_obs(t):
        cells = a["cells"]["R1"][t]
        return {"n": (a["tables"]["R1"].get(t) or empty_row())["n"], "cells": cells,
                "matched": _count(cells)}

    add("C1", "consistency", "Table 2, meal replacements (198 samples, Table 1 origins exact): "
        "all 12 cells (% positive, average of positives and maximum for As, Cd, Pb and Hg)",
        lambda: row_obs("meal-replacement"),
        lambda o: o["n"] == TABLE2["meal-replacement"][0] and o["matched"] == 12)
    add("P1", "prediction", "infant formula (396 samples in the file, 395 printed): at least 10 "
        "of Table 2's 12 cells match, and exactly 2 infant formula samples have mercury above 0",
        lambda: {**row_obs("infant-formula"), "if_hg": a["if_hg"]},
        lambda o: o["matched"] >= MIN_CELLS and o["if_hg"] == IF_HG)
    add("P2", "prediction", "protein powders (196 in the file, 195 printed): at least 10 of "
        "Table 2's 12 cells match, and the file's highest mercury value rounds to 0.022 ppm and "
        "belongs only to Protein Powder samples",
        lambda: {**row_obs("protein-powder"), "hg_top": a["hg_top"]},
        lambda o: o["matched"] >= MIN_CELLS and matches(o["hg_top"]["max"], HG_MAX)
        and bool(o["hg_top"]["holders"])
        and all(h["product"] == "Protein Powder" for h in o["hg_top"]["holders"]))

    def p3():
        out = {}
        for r in READINGS:
            c = {t: _count(a["cells"][r][t]) for t in ("bran", "rice")}
            out[r] = {"bran": c["bran"], "rice": c["rice"], "total": c["bran"] + c["rice"],
                      "cells": {t: a["cells"][r][t] for t in ("bran", "rice")}}
        return out

    add("P3", "prediction", "the bran/rice split is reading R1 ('Oil - Other' and 'Crackers' are "
        "rice products): R1 matches at least 20 of the 24 bran and rice cells, and more of them "
        "than reading R2 ('Popcorn' and 'Snack Bar')",
        p3, lambda o: o["R1"]["total"] >= MIN_SPLIT_CELLS and o["R1"]["total"] > o["R2"]["total"])
    add("P4", "prediction", "the file's two highest arsenic values round to 1.13 and 1.12 ppm and "
        "both are 'Bran - Rice' samples (the text's brown rice bran and germ powder)",
        lambda: {"as_top": a["as_top"]},
        lambda o: len(o["as_top"]) == 2 and matches(o["as_top"][0]["As"], AS_TOP[0])
        and matches(o["as_top"][1]["As"], AS_TOP[1])
        and all(x["product"] == "Bran - Rice" for x in o["as_top"]))

    def p5():
        return {"n": a["n"], "As_pct": a["overall"]["As"]["pct"],
                "Hg_pct": a["overall"]["Hg"]["pct"], "any_pct": a["any_pct"],
                "all4_pct": a["all4_pct"], "Cd_nd": a["nd"]["Cd"], "Pb_nd": a["nd"]["Pb"]}

    add("P5", "prediction", "the text over all 987 samples: arsenic in 64%, mercury in 19%, one "
        "or more of the four in 70%, all four in 12%; cadmium not detected in 596-598 samples and "
        "lead in 656-658 (the printed 596 and 656 plus at most the 2 extra samples)",
        p5, lambda o: matches(o["As_pct"], TEXT_PCT["As"]) and matches(o["Hg_pct"], TEXT_PCT["Hg"])
        and matches(o["any_pct"], TEXT_PCT["any"]) and matches(o["all4_pct"], TEXT_PCT["all4"])
        and all(TEXT_ND[m] <= o[f"{m}_nd"] <= TEXT_ND[m] + ND_SLACK for m in TEXT_ND))
    add("P6", "prediction", "the D-suffixed sample IDs explain the two extra samples: at least "
        "one is infant formula and at least one is a Protein Powder",
        lambda: {"dups": a["dups"]},
        lambda o: any(d["product"] in IF_LABELS for d in o["dups"])
        and any(d["product"] == "Protein Powder" for d in o["dups"]))
    return preds


# ---------------------------------------------------------------------------
# Data loading (network only here).
# ---------------------------------------------------------------------------
def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-tmet-2018"})
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
    with open(os.path.join(out_dir, "tmet_2018_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "base", "dup", "product", "type_r1", "type_r2", "function",
                    "origin", "region", "n_toxic"] + [f"{c.lower()}_ppm" for c in COMPONENTS])
        for s in sorted(samples, key=lambda s: s["sample"]):
            w.writerow([s["sample"], s["base"], int(s["dup"]), s["product"],
                        type_of(s["product"], "R1"), type_of(s["product"], "R2"), s["function"],
                        s["origin"], s["region"], s["n_toxic"]]
                       + [_num(s["vals"].get(c)) for c in COMPONENTS])
    result = {"study": "tmet-2018", "version": VERSION, "predictions": preds, "census": census,
              "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "tmet_2018_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the tmet-2018 0.1.0 pre-registration.")
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
