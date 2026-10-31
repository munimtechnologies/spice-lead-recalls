#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""pah-2019 0.1.0: CFIA's open 2019-20 "Polycyclic Aromatic Hydrocarbons in Selected Foods" file
against every figure CFIA printed for it (value items D2-D5 of
docs/bpa-pah-report-0.1.0-prereg.md).

Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes the survey's per-sample CSV on open.canada.ca
(Open Government Licence - Canada) and a report page that gives results as total PAH in ppb TEQ:
benzo[a]pyrene x 1 + benz[a]anthracene x 0.1 + benzo[b]fluoranthene x 0.1 + chrysene x 0.01. The
file reports ng/g (= ppb), so no conversion. It is gated on structure facts from the names-only
census (data/pah-2019_census.json) run before any result value was read: its byte size from the
portal record, its columns, 296 samples x 16 component rows, one unit, one plan code, the 27 known
product labels and a value rule. The label map is the one fixed in
docs/bpa-pah-report-0.1.0-grader.md before any value was read. Standard library only. Code
Apache-2.0; derived data CC BY 4.0. Not a compliance finding, not about any brand, and not dietary
or medical advice.
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
DATASET = "4884f9d1-0a59-4c8e-85ca-157d13411d19"
RESOURCE = "d5b3cca2-4ccf-4aed-a4d1-0af540422575"
PATH = "fsap_chem_ts_2019-2020_pahs_in_selected_foods_-_open_data.csv"
SIZE = 831190                                   # portal record "size"
CKAN_MD5 = "0bb033bbcdab8305839d0a8716def1b3"   # portal record "hash" (reported, not gated)
N_SAMPLES = 296                                 # names-only census (= the report's 296)
N_ROWS = 4736
PLAN = "2019_TS024"
UNITS = {"ng/g"}
ID_RE = re.compile(r"^C2019PAHS(\d{5})A$")
COMPONENTS = ("Acenaphthene", "Acenaphthylene", "Anthracene", "Benz[a]anthracene",
              "Benzo[a]pyrene", "Benzo[b]fluoranthene", "Benzo[g,h,i]perylene",
              "Benzo[k]fluoranthene", "Chrysene", "Dibenz[a,h]anthracene", "Fluoranthene",
              "Fluorene", "Indeno[1,2,3-cd]pyrene", "Naphthalene", "Phenanthrene", "Pyrene")
COMP_KEY = {c.lower(): c for c in COMPONENTS}
# The report's toxic equivalency factors (TEQ = sum of concentration x TEF). PAH4 is the plain sum
# of the same four compounds (the EU's PAH4).
TEF = {"Benzo[a]pyrene": 1.0, "Benz[a]anthracene": 0.1, "Benzo[b]fluoranthene": 0.1,
       "Chrysene": 0.01}
PAH4 = tuple(TEF)

# File label -> report type, exactly as fixed in docs/bpa-pah-report-0.1.0-grader.md before any
# value was read (34 / 114 / 148).
FORMULA = {"Infant Formula - Dairy": "dairy", "Infant Formula - Soy": "soy"}
NUTS = ("Butter - Almond", "Butter - Blend", "Butter - Cashew", "Butter - Hazelnut",
        "Butter - Peanut", "Butter - Pumpkin Seed", "Butter - Soy", "Butter - Sunflower Seed",
        "Butter - Walnut", "Nut - Almond", "Nut - Brazil Nut", "Nut - Cashew", "Nut - Chestnut",
        "Nut - Hazelnut/Filbert", "Nut - Macadamia Nut", "Nut - PINE NUT", "Nut - Pecan",
        "Nut - Walnut", "Peanut", "Seed - Chia", "Seed - Flax", "Seed - Pumpkin",
        "Seed - Sunflower", "Tahini")
OLIVE = "Oil - Olive"
GROUP_OF = dict([(f, "formula") for f in FORMULA] + [(n, "nuts") for n in NUTS]
                + [(OLIVE, "olive")])
LABELS = set(GROUP_OF)
GROUPS = ("formula", "nuts", "olive")

# Printed figures, transcribed in the pre-registration.
# Table 1 (origin): type -> (domestic, imported, unspecified, total).
TABLE1 = {"formula": (0, 31, 3, 34), "nuts": (40, 46, 28, 114), "olive": (1, 133, 14, 148)}
# Table 2 (ppb TEQ, positives only): type -> (n, detected, min, max, average).
TABLE2 = {"formula": (34, 16, "0.001", "0.776", "0.12"),
          "nuts": (114, 44, "0.001", "2.93", "0.17"),
          "olive": (148, 121, "0.002", "3.25", "0.24"),
          "all": (296, 181, "0.001", "3.25", "0.21")}
PCT = {"formula": "47", "nuts": "39", "olive": "82", "all": "61"}
OLIVE_AVGS = {"table2": "0.24", "table3": "0.23"}
D2_ROWS = ("formula", "nuts", "all")
MIN_D2_CELLS = 11                               # D2: of the three rows' 12 cells
# Text: milk-based formula 16 of 23 positive, maximum 0.776; no soy formula positive; one pumpkin
# seed butter at 2.93, every other nut sample below 0.773; three olive oils elevated, all others
# below 0.700.
DAIRY_N, DAIRY_K, DAIRY_MAX = 23, 16, "0.776"
NUT_TOP_LABEL, NUT_TOP, NUT_OTHERS_BELOW = "Butter - Pumpkin Seed", "2.93", 0.773
OLIVE_HIGH_AT, OLIVE_HIGH_N = 0.700, 3
# D5 (descriptive): the EU maximum levels for oils the report cites (ng/g).
EU_BAP, EU_PAH4 = 2.0, 10.0
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


def teq(vals):
    """Total PAH in ppb TEQ from a sample's component values (ng/g = ppb; missing = 0)."""
    return sum(f * (vals.get(c) or 0.0) for c, f in TEF.items())


def pah4(vals):
    """The plain sum of the four TEQ compounds (ng/g)."""
    return sum(vals.get(c) or 0.0 for c in PAH4)


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
        "region": pick(lambda c: c.startswith("region")),
        "date": pick(lambda c: c.startswith("date")),
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
                           "date": clean(_cell(r, col["date"])),
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
    """Add component values, the TEQ, PAH4, benzo[a]pyrene, the type and the formula kind."""
    vals = {c: max(v) for c, v in s["values"].items()}
    s["vals"] = vals
    s["missing"] = [c for c in COMPONENTS if c not in vals]
    s["repeated"] = sorted(c for c, v in s["values"].items() if len(v) > 1)
    s["teq"] = teq(vals)
    s["pah4"] = pah4(vals)
    s["bap"] = vals.get("Benzo[a]pyrene") or 0.0
    s["n_pah"] = sum(1 for c in COMPONENTS if (vals.get(c) or 0) > 0)
    s["group"] = GROUP_OF.get(s["product"], "unmapped")
    s["formula"] = FORMULA.get(s["product"], "")
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
    """Table 2's row `key` against TEQ stats."""
    n, det, mn, mx, avg = TABLE2[key]
    return {"n": st["n"] == n, "detected": st["k"] == det, "min": matches(st["min"], mn),
            "max": matches(st["max"], mx), "avg": matches(st["mean"], avg)}


def origins(samples, key):
    """key value -> [domestic, imported, unspecified, total] from the Function column."""
    out = {}
    for s in samples:
        row = out.setdefault(key(s), [0, 0, 0, 0])
        f = s["function"]
        row[0 if f == "Domestic" else 1 if f == "Import" else 2] += 1
        row[3] += 1
    return out


def twins(samples, keys, min_pos):
    """Sets of samples whose values for `keys` are all identical, among samples with at least
    `min_pos` of them above 0 (exploratory: a hint of copied rows)."""
    groups = {}
    for s in samples:
        prof = tuple(s["vals"].get(c) or 0.0 for c in keys)
        if sum(1 for v in prof if v > 0) >= min_pos:
            groups.setdefault(prof, []).append(s["sample"])
    return sorted(sorted(v) for v in groups.values() if len(v) > 1)


def dates(samples):
    """Descriptive facts about the sampling-date column (labels only)."""
    per = {}
    for s in samples:
        _bump(per, s["date"])
    keys = sorted(per)
    return {"distinct": len(per), "blank": per.get("", 0),
            "most_on_one_date": max(per.values()) if per else 0,
            "first": keys[:3], "last": keys[-3:]}


def printed_internal():
    """Checks among the printed figures themselves (no data): the olive-oil averages the total
    row's 0.21 allows, given the formula and nut rows."""
    lo = TABLE2["all"][1] * (float(TABLE2["all"][4]) - half_unit(TABLE2["all"][4]))
    hi = TABLE2["all"][1] * (float(TABLE2["all"][4]) + half_unit(TABLE2["all"][4]))
    for g in ("formula", "nuts"):
        k, avg = TABLE2[g][1], TABLE2[g][4]
        lo -= k * (float(avg) + half_unit(avg))
        hi -= k * (float(avg) - half_unit(avg))
    k = TABLE2["olive"][1]
    return {"olive_avg_bounds": [lo / k, hi / k],
            "detected_sum": sum(TABLE2[g][1] for g in GROUPS),
            "n_sum": sum(TABLE2[g][0] for g in GROUPS)}


def brief(s):
    return {"sample": s["sample"], "product": s["product"], "function": s["function"],
            "origin": s["origin"], "teq": s["teq"], "bap": s["bap"], "pah4": s["pah4"]}


def analyse(samples):
    a = {"n": len(samples)}
    by = {g: [s for s in samples if s["group"] == g] for g in GROUPS}
    a["groups"] = {g: stats([s["teq"] for s in by[g]]) for g in GROUPS}
    a["groups"]["all"] = stats([s["teq"] for s in samples])
    a["table2"] = {g: check_row(g, a["groups"][g]) for g in TABLE2}
    a["pct"] = {g: matches(a["groups"][g]["pct"], p) for g, p in PCT.items()}
    a["olive_avg"] = {k: matches(a["groups"]["olive"]["mean"], v) for k, v in OLIVE_AVGS.items()}
    a["formula_kinds"] = {k: stats([s["teq"] for s in by["formula"] if s["formula"] == k])
                          for k in ("dairy", "soy")}
    nuts = sorted(by["nuts"], key=lambda s: -s["teq"])
    a["nut_top"] = [brief(s) for s in nuts[:3]]
    olive = sorted(by["olive"], key=lambda s: -s["teq"])
    a["olive_top"] = [brief(s) for s in olive[:5]]
    a["olive_high"] = [brief(s) for s in olive if s["teq"] >= OLIVE_HIGH_AT]
    a["eu_bap_over"] = [brief(s) for s in olive if s["bap"] > EU_BAP]
    a["eu_pah4_over"] = [brief(s) for s in olive if s["pah4"] > EU_PAH4]
    a["origins"] = origins(samples, lambda s: s["group"])
    a["origins_table1_diff"] = {g: [x - p for x, p in zip(a["origins"].get(g, [0] * 4),
                                                        TABLE1[g])] for g in GROUPS}
    a["bap"] = {g: stats([s["bap"] for s in by[g]]) for g in GROUPS}
    a["any_pah"] = {g: sum(1 for s in by[g] if s["n_pah"] > 0) for g in GROUPS}
    a["twins_16"] = twins(samples, COMPONENTS, 1)
    a["twins_pah4"] = twins(samples, PAH4, 2)
    a["dates"] = dates(samples)
    a["printed_internal"] = printed_internal()
    return a


def grade(a, gate):
    gate_ok = all(gate.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": gate_ok, "observed": gate,
              "text": "byte size as on the portal record; columns; 4,736 rows; 296 samples, each "
                      "with one row per the 16 PAHs; unit ng/g and plan 2019_TS024 on every row; "
                      "the 27 known product labels; every value a number >= 0, a '<' or a "
                      "not-detected token"}]

    def add(pid, text, observe, met, kind="prediction"):
        o = observe() if gate_ok else {}
        graded = gate_ok and kind == "prediction"
        preds.append({"id": pid, "kind": kind, "graded": graded,
                      "met": bool(graded and met(o)) if kind == "prediction" else None,
                      "text": text, "observed": o})

    def d2():
        cells = {g: a["table2"][g] for g in D2_ROWS}
        return {"cells": cells, "stats": {g: a["groups"][g] for g in D2_ROWS},
                "matched": sum(1 for g in D2_ROWS for c in CELLS if cells[g][c]),
                "all_detected": a["groups"]["all"]["k"]}

    add("D2", "Table 2's infant formula, nuts and total rows reproduce: at least 11 of their 12 "
        "cells (detected, minimum, maximum, average) match; 181 of 296 detected",
        d2, lambda o: o["matched"] >= MIN_D2_CELLS and o["all_detected"] == TABLE2["all"][1])

    def d3():
        cells = a["table2"]["olive"]
        return {"cells": cells, "stats": a["groups"]["olive"], "average_matches": a["olive_avg"]}

    add("D3", "olive oil: 121 detected, minimum 0.002, maximum 3.25 (no prediction on Table 2's "
        "0.24 against Table 3's 0.23; the result reports which the file gives)",
        d3, lambda o: o["cells"]["detected"] and o["cells"]["min"] and o["cells"]["max"])

    def d4():
        dairy, soy = a["formula_kinds"]["dairy"], a["formula_kinds"]["soy"]
        top = a["nut_top"]
        checks = {
            "dairy_16_of_23_max_0.776": dairy["n"] == DAIRY_N and dairy["k"] == DAIRY_K
            and matches(dairy["max"], DAIRY_MAX),
            "soy_none": soy["n"] > 0 and soy["k"] == 0,
            "nut_top_pumpkin_seed_butter": bool(top) and top[0]["product"] == NUT_TOP_LABEL
            and matches(top[0]["teq"], NUT_TOP)
            and (len(top) < 2 or top[1]["teq"] < NUT_OTHERS_BELOW),
            "olive_three_at_0.700": len(a["olive_high"]) == OLIVE_HIGH_N,
        }
        return {"checks": checks, "dairy": dairy, "soy": soy, "nut_top": top,
                "olive_high": a["olive_high"],
                "ungraded": "four pomace oils, average 0.19, maximum 0.569: no label separates "
                            "pomace oil"}

    add("D4", "the text: 16 of 23 milk-based formulas positive with maximum 0.776 and no soy "
        "formula positive; the 2.93 maximum among nuts is a pumpkin seed butter and the next nut "
        "is below 0.773; exactly 3 olive oils at 0.700 or more (the pomace clause is ungraded)",
        d4, lambda o: all(o["checks"].values()))
    add("D5", "descriptive, no prediction: olive oils with benzo[a]pyrene above 2.0 ng/g and with "
        "PAH4 above 10.0 ng/g",
        lambda: {"bap_over_2": a["eu_bap_over"], "pah4_over_10": a["eu_pah4_over"],
                 "olive_bap": a["bap"]["olive"]},
        lambda o: True, kind="descriptive")
    return preds


# ---------------------------------------------------------------------------
# Data loading (network only here).
# ---------------------------------------------------------------------------
def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-pah-2019"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(data_dir, rounds=4, pause=90):
    """The file from the data volume (cached there by the census job) or the portal, trying both
    hosts for up to `rounds` rounds `pause` seconds apart."""
    local = os.path.join(data_dir, RESOURCE + ".csv") if data_dir else ""
    if local and os.path.exists(local):
        with open(local, "rb") as fh:
            raw = fh.read()
        if len(raw) == SIZE:
            return raw, "data-volume"
    errors = []
    for attempt in range(rounds):
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


def _num(x):
    return "" if x is None else repr(x)


def write_outputs(out_dir, samples, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "pah_2019_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "group", "formula", "function", "origin", "date",
                    "teq_ppb", "pah4_ppb", "n_pah"] + [f"ppb:{c}" for c in COMPONENTS])
        for s in sorted(samples, key=lambda s: s["sample"]):
            w.writerow([s["sample"], s["product"], s["group"], s["formula"], s["function"],
                        s["origin"], s["date"], repr(s["teq"]), repr(s["pah4"]), s["n_pah"]]
                       + [_num(s["vals"].get(c)) for c in COMPONENTS])
    result = {"study": "bpa-pah-report", "grader": "pah_2019", "version": VERSION,
              "predictions": preds, "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"] and p["kind"] == "prediction"),
              "n_met": sum(1 for p in preds if p["met"] and p["kind"] == "prediction")}
    with open(os.path.join(out_dir, "pah_2019_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade bpa-pah-report 0.1.0 items D2-D5.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    try:
        raw, src = load(args.data_dir)
        text, enc = decode(raw)
        samples, census = parse(text)
        md5 = hashlib.md5(raw).hexdigest()
        provenance = {"dataset": DATASET, "resource": RESOURCE, "source": src, "bytes": len(raw),
                      "encoding": enc, "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                      "portal_md5": CKAN_MD5, "md5_matches_portal": md5 == CKAN_MD5}
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
                      "ids_bad": census["ids_bad"][:10], "provenance": provenance,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if all(gate.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
