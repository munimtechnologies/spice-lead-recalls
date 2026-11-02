#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""food-colours 0.1.0 grader: CFIA's open food-colour files (2018-19 essences/flavourings, oils,
sweets and processed vegetables; 2009-10 manufactured foods) against their printed reports.

Grades V1-V8 of docs/food-colours-0.1.0-prereg.md with the label maps and coding rules of
docs/food-colours-0.1.0-census.md, both published before this module reads any value.

Coding (fixed in the census note): a colour is "detected" in a sample when any of its rows in that
sample has a value above zero; its level is the largest of those rows (Chrysoidine G, Orange II and
Rhodamine B have one row in the water-soluble test and one in the fat-soluble test). A "colour
result" is one (sample, colour) pair that is detected. Units are ug/g, which is ppm. A printed
figure matches when the file's value is within half a unit of its last printed digit.

Uses cfia_census.load / decode (published) to fetch and decode the files; everything else is here.
Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0;
derived data CC BY 4.0. Not a compliance finding, not about any brand, and not dietary or medical
advice.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys

VERSION = "0.1.0"
UNIT = "µg/g"

TARGETS = {
    "c18": {"name": "c18",
            "dataset": "1b0c4141-7a22-4c93-8679-63eb49f7be24",
            "resource": "3006ff94-fa7a-4cc4-8b58-a2164ce6a937",
            "path": ("cfia_acia-1133_2018-19_food_colours_in_selected_foods_-2018-2019_colorants-"
                     "alimentaires-dans-les.csv"),
            "size": 3771543, "md5": "7651427618a70aa3ad2a51ab90bcae8c"},
    "c09": {"name": "c09",
            "dataset": "e750a5e1-40e5-4428-b23f-cc3f613e7f9a",
            "resource": "9c6e2a16-c552-41cb-b95c-240db3c75b8d",
            "path": ("1550-v1-chem_ts_2009-2010_food_colours_used_in_the_production_of_manufactured_"
                     "foods_open_data_po.csv"),
            "size": 33724, "md5": "dc558d850720b90610da2c75424d1cd7"},
}

# --- label maps (docs/food-colours-0.1.0-census.md) ---------------------------------------------
PRODUCT_TYPE = {}
for _label in ("Essence/Flavour",):
    PRODUCT_TYPE[_label] = "essence"
for _label in ("Oil - Blend", "Oil - Olive", "Oil - Other", "Oil - Palm", "Oil - Soybean",
               "Salad Dressing"):
    PRODUCT_TYPE[_label] = "oil"
for _label in ("Beet - Pickled", "Cucumber - Pickled", "Cucumber - Pickled Sweet",
               "Gherkin - Pickled", "Onion - Pickled", "Pepper - Pickled", "Pepper - Pickled Hot",
               "Pickled Vegetable - Misc"):
    PRODUCT_TYPE[_label] = "veg"
for _label in ("Baked Goods", "Bakery Product - Cookie", "Candy - Hard", "Candy - Soft",
               "Fruit Snacks", "Preserve - Jam/Jelly", "Preserve - Raspberry",
               "Preserve - Strawberry", "Pudding"):
    PRODUCT_TYPE[_label] = "sweets"
TYPES = ("essence", "oil", "veg", "sweets")
CANDY = ("Candy - Hard", "Candy - Soft")

# Table 1 (domestic, imported, unspecified) and Table 2 (samples, samples with colours,
# colour detections) of the 2018-19 report.
TABLE1 = {"essence": (10, 14, 26), "oil": (15, 51, 33), "veg": (8, 38, 4), "sweets": (23, 81, 96)}
TABLE2 = {"essence": (50, 9, 23), "oil": (99, 13, 13), "veg": (50, 28, 40),
          "sweets": (200, 131, 260)}
# Table 3 of the 2018-19 report: file label -> (samples, maximum, average) in ppm.
# Orange II's average is printed as "below LQ (0.13)".
TABLE3 = {"Allura Red": (101, "539", "78.7"), "Tartrazine": (100, "144", "27.1"),
          "Brilliant Blue FCF": (61, "85", "9.5"), "Sunset Yellow FCF": (44, "98.6", "20.5"),
          "Erythrosin B": (13, "124", "39.3"), "Amaranth": (12, "83.5", "26.9"),
          "Indigo Carmine": (3, "50.6", "21.3"), "Orange II": (2, "0.221", None),
          "Rhodamine B": (1, "10.8", "10.8")}
ORANGE_LQ = 0.13
ORANGE_SECOND_BELOW = 0.039
# 2009-10 labels of the five colours named in the 93% sentence, and the fat-soluble row.
C09_FIVE = ("Sunset, yellow", "Tartrazine, yellow", "Brilliant blue", "Allura, red", "Amaranth")
C09_FAT = "Fat-Soluble Dyes"

ROLES = {
    "sample": ("sample no",), "region": ("region",), "function": ("function",),
    "origin": ("origin",), "product": ("product",), "date": ("date sampled",),
    "test": ("type of test",), "component": ("component",), "value": ("amount", "result"),
    "unit": ("report unit", "unit"),
}
LABEL_FIELDS = ("product", "function", "origin", "region", "date")
ID_RE = re.compile(r"^C?(\d{4})[A-Z]+(\d{3,6})([A-Z]?)$")


# --- reading -------------------------------------------------------------------------------------
def _norm(h):
    return h.replace("﻿", "").strip().lower()


def _matches(h, cand):
    return h == cand or h.startswith(cand + " ") or h.startswith(cand + ".")


def find_columns(header):
    """Role -> column index. For each role the first candidate that matches any header wins, and
    within a candidate the leftmost column wins (so 'Origin' beats 'Origine')."""
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
    """A numeric cell -> float >= 0; anything else -> None (counted as bad)."""
    try:
        v = float(cell.strip())
    except (AttributeError, ValueError):
        return None
    if v != v or v < 0:
        return None
    return v


def parse(text):
    """CSV text -> (rows, problems). Each row is a dict of the roles plus 'value' as a float."""
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    cols = find_columns(header)
    problems = {"missing_roles": sorted(r for r in ROLES if r not in cols and r != "region"),
                "bad_values": 0, "bad_units": 0, "short_rows": 0}
    rows = []
    for raw in reader:
        if not any(c.strip() for c in raw):
            continue
        if len(raw) < len(header):
            problems["short_rows"] += 1
            continue
        r = {role: raw[i].strip() for role, i in cols.items()}
        r["value"] = to_value(raw[cols["value"]]) if "value" in cols else None
        if r["value"] is None:
            problems["bad_values"] += 1
        if r.get("unit", "").replace("μ", "µ") != UNIT:
            problems["bad_units"] += 1
        rows.append(r)
    return rows, problems


def samples_of(rows):
    """sample ID -> record with its labels, colours (max value per colour) and row counts."""
    out = {}
    for r in rows:
        s = out.get(r["sample"])
        if s is None:
            s = {"sample": r["sample"], "rows": 0, "colours": {}, "rows_by_colour": {},
                 "rows_above_zero": {}, "labels": [], "tests": {}}
            for f in LABEL_FIELDS:
                s[f] = r.get(f, "")
            out[r["sample"]] = s
        s["rows"] += 1
        lab = tuple(r.get(f, "") for f in LABEL_FIELDS)
        if lab not in s["labels"]:
            s["labels"].append(lab)
        c, v = r["component"], r["value"]
        t = r.get("test", "")
        s["tests"][t] = s["tests"].get(t, 0) + 1
        s["rows_by_colour"][c] = s["rows_by_colour"].get(c, 0) + 1
        if v is None:
            continue
        cur = s["colours"].get(c)
        s["colours"][c] = v if cur is None else max(cur, v)
        if v > 0:
            s["rows_above_zero"][c] = s["rows_above_zero"].get(c, 0) + 1
    return out


def detected(s):
    """{colour: level} for the colours above zero in sample s."""
    return {c: v for c, v in s["colours"].items() if v > 0}


def half(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def in_range(x, printed):
    return x is not None and abs(x - float(printed)) <= half(printed) + 1e-9


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


# --- census-level checks (label only; graded in the census note, recomputed here) ---------------
def type_counts(samples):
    counts, unmapped = {t: 0 for t in TYPES}, {}
    for s in samples.values():
        t = PRODUCT_TYPE.get(s["product"])
        if t is None:
            _bump(unmapped, s["product"])
        else:
            counts[t] += 1
    return counts, unmapped


def function_split(samples):
    out = {t: [0, 0, 0] for t in TYPES}
    for s in samples.values():
        t = PRODUCT_TYPE.get(s["product"])
        if t is None:
            continue
        out[t][{"Domestic": 0, "Import": 1}.get(s["function"], 2)] += 1
    return out


# --- 2018-19 value grading ------------------------------------------------------------------------
def by_type(samples):
    """type -> (samples, samples with a colour, colour detections), plus oil colour counts."""
    out = {t: [0, 0, 0] for t in TYPES}
    oil_colours = []
    for s in samples.values():
        t = PRODUCT_TYPE.get(s["product"])
        if t is None:
            continue
        det = detected(s)
        out[t][0] += 1
        if det:
            out[t][1] += 1
            out[t][2] += len(det)
            if t == "oil":
                oil_colours.append(len(det))
    return {t: tuple(v) for t, v in out.items()}, oil_colours


def colour_stats(samples):
    """colour -> {n, max, mean, min} over samples where it is detected."""
    levels = {}
    for s in samples.values():
        for c, v in detected(s).items():
            levels.setdefault(c, []).append(v)
    return {c: {"n": len(v), "max": max(v), "min": min(v), "mean": sum(v) / len(v)}
            for c, v in levels.items()}


def grade_v1(samples):
    got, oil_colours = by_type(samples)
    cells = {}
    for t, (n, k, d) in TABLE2.items():
        gn, gk, gd = got[t]
        cells[t] = {"samples": gn == n, "with_colour": gk == k, "detections": gd == d}
    oil_one = bool(oil_colours) and all(x == 1 for x in oil_colours)
    met = all(all(c.values()) for c in cells.values()) and oil_one
    return {"id": "V1", "kind": "prediction", "graded": True, "met": met,
            "observed": {"by_type": {t: list(v) for t, v in got.items()}, "cells": cells,
                         "oil_colours_per_positive": sorted(oil_colours),
                         "with_colour_total": sum(v[1] for v in got.values()),
                         "detections_total": sum(v[2] for v in got.values())},
            "text": "Table 2: samples with a colour 9 / 13 / 28 / 131 (181); colour detections "
                    "23 / 13 / 40 / 260 (336); each oil positive carries exactly one colour"}


def grade_v2(samples):
    st = colour_stats(samples)
    rows, ok = {}, True
    for c, (n, pmax, pavg) in TABLE3.items():
        g = st.get(c)
        if g is None:
            rows[c] = {"n": 0, "n_ok": False, "max_ok": False, "avg_ok": False}
            ok = False
            continue
        avg_ok = (g["mean"] < ORANGE_LQ) if pavg is None else in_range(g["mean"], pavg)
        r = {"n": g["n"], "max": g["max"], "mean": g["mean"], "n_ok": g["n"] == n,
             "max_ok": in_range(g["max"], pmax), "avg_ok": avg_ok}
        rows[c] = r
        ok = ok and r["n_ok"] and r["max_ok"] and r["avg_ok"]
    others = {c: g["n"] for c, g in st.items() if c not in TABLE3}
    met = ok and not others
    return {"id": "V2", "kind": "prediction", "graded": True, "met": met,
            "observed": {"colours": rows, "other_colours_detected": others},
            "text": "Table 3: for each of the nine colours, samples and maximum match, averages "
                    "within rounding (Orange II below LQ 0.13); no other colour above zero"}


def grade_v3_v4_v5(samples):
    got, _ = by_type(samples)
    total = sum(v[2] for v in got.values())
    st = colour_stats(samples)
    orange = sorted(v for s in samples.values() for c, v in detected(s).items()
                    if c == "Orange II")
    low = [s["sample"] for s in samples.values()
           if 0 < s["colours"].get("Orange II", 0) < ORANGE_SECOND_BELOW]
    over = {t: got[t][2] - TABLE2[t][2] for t in TYPES if got[t][2] != TABLE2[t][2]}
    low_types = sorted({PRODUCT_TYPE.get(samples[x]["product"], "") for x in low})
    v3 = {"id": "V3", "kind": "prediction", "graded": True,
          "met": total == 337 and bool(low),
          "observed": {"detections": total, "orange_ii_levels": orange, "orange_ii_low": low,
                       "orange_ii_low_types": low_types, "type_cells_off": over,
                       "orange_ii_n": st.get("Orange II", {}).get("n", 0)},
          "text": "R1 settled: 337 colour detections (Table 3), with one Orange II result under "
                  "0.039 ppm that Table 2's 336 leaves out"}
    none = sum(1 for s in samples.values() if not detected(s))
    v4 = {"id": "V4", "kind": "prediction", "graded": True, "met": none == 218,
          "observed": {"without_colour": none, "with_colour": len(samples) - none},
          "text": "218 samples without any colour above zero (not 219)"}
    hist = {}
    for s in samples.values():
        k = len(detected(s))
        if k:
            _bump(hist, k)
    one_to_four = sum(n for k, n in hist.items() if k <= 4)
    v5 = {"id": "V5", "kind": "prediction", "graded": True, "met": one_to_four in (177, 178),
          "observed": {"colours_per_positive": {str(k): hist[k] for k in sorted(hist)},
                       "one_to_four": one_to_four,
                       "five_or_more": sum(n for k, n in hist.items() if k >= 5)},
          "text": "177 or 178 of the samples with colours carry one to four colours"}
    return v3, v4, v5


def top_levels(samples, n=5):
    allv = [(v, c, s["sample"]) for s in samples.values() for c, v in detected(s).items()]
    allv.sort(key=lambda x: (-x[0], x[1], x[2]))
    return [{"ppm": v, "colour": c, "sample": sid, "product": samples[sid]["product"],
             "function": samples[sid]["function"], "origin": samples[sid]["origin"]}
            for v, c, sid in allv[:n]]


def grade_v6_v7(samples):
    top = top_levels(samples)
    t0 = top[0] if top else None
    v6 = {"id": "V6", "kind": "prediction", "graded": True,
          "met": bool(t0) and t0["colour"] == "Allura Red" and in_range(t0["ppm"], "539")
          and t0["product"] in CANDY,
          "observed": {"top": top},
          "text": "the highest level of any colour is Allura Red at 539 ppm, in a candy"}
    rb = [(s["sample"], v) for s in samples.values() for c, v in detected(s).items()
          if c == "Rhodamine B"]
    v7 = {"id": "V7", "kind": "prediction", "graded": True,
          "met": len(rb) == 1 and in_range(rb[0][1], "10.8"),
          "observed": {"rhodamine_b": [{"sample": sid, "ppm": v,
                                        "product": samples[sid]["product"],
                                        "function": samples[sid]["function"],
                                        "origin": samples[sid]["origin"]} for sid, v in rb]},
          "text": "Rhodamine B in exactly one sample, at 10.8 ppm"}
    return v6, v7


# --- 2009-10 value grading ------------------------------------------------------------------------
def grade_v8(samples):
    pos = [s for s in samples.values() if detected(s)]
    fat = [s["sample"] for s in samples.values() if s["colours"].get(C09_FAT, 0) > 0]
    results = {}
    for s in samples.values():
        for c in detected(s):
            _bump(results, c)
    total = sum(results.values())
    five = sum(results.get(c, 0) for c in C09_FIVE)
    share = five / total if total else None
    checks = {"forty_one_with_colour": len(pos) == 41, "no_fat_soluble": not fat,
              "five_share_92.5_93.5": share is not None and 0.925 <= share <= 0.935}
    return {"id": "V8", "kind": "prediction", "graded": True, "met": all(checks.values()),
            "observed": {"checks": checks, "with_colour": len(pos), "fat_soluble_above_zero": fat,
                         "results_by_colour": dict(sorted(results.items())), "results": total,
                         "five_colours": five, "five_share": share},
            "text": "2009-10: 41 of 100 with a colour, no fat-soluble colour, the five colours "
                    "are 92.5-93.5% of colour results"}


def grade_v9():
    return {"id": "V9", "kind": "prediction", "graded": False, "met": None,
            "observed": {"reason": "the file has seven product categories, not product names, "
                                   "and no compliance column (census note)"},
            "text": "2009-10 named non-compliant samples (ungraded)"}


# --- descriptive -----------------------------------------------------------------------------------
def coding(rows):
    zero = sum(1 for r in rows if r["value"] == 0)
    pos = sum(1 for r in rows if r["value"] is not None and r["value"] > 0)
    mins = {}
    for r in rows:
        v = r["value"]
        if v is not None and v > 0:
            c = r["component"]
            mins[c] = v if c not in mins else min(mins[c], v)
    return {"rows_zero": zero, "rows_above_zero": pos, "smallest_above_zero": mins}


def double_rows(samples, colours=("Chrysoidine G", "Orange II", "Rhodamine B")):
    out = {}
    for c in colours:
        both = one = 0
        for s in samples.values():
            k = s["rows_above_zero"].get(c, 0)
            if k >= 2:
                both += 1
            elif k == 1:
                one += 1
        out[c] = {"both_rows": both, "one_row": one}
    return out


def twins(samples, min_colours=2):
    groups = {}
    for s in samples.values():
        det = detected(s)
        if len(det) >= min_colours:
            groups.setdefault(tuple(sorted(det.items())), []).append(s["sample"])
    return sorted(sorted(v) for v in groups.values() if len(v) > 1)


def mixed(samples):
    out = []
    for s in samples.values():
        if len(s["labels"]) > 1:
            diff = [f for i, f in enumerate(LABEL_FIELDS)
                    if len({lab[i] for lab in s["labels"]}) > 1]
            out.append({"sample": s["sample"], "fields": diff,
                        "values": {f: sorted({lab[LABEL_FIELDS.index(f)] for lab in s["labels"]})
                                   for f in diff}})
    return sorted(out, key=lambda x: x["sample"])


def parse_date(text):
    for fmt in ("%d-%b-%y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def ids_and_dates(samples):
    nums, suffixed, bad = {}, [], []
    for sid in samples:
        m = ID_RE.match(sid)
        if not m:
            bad.append(sid)
            continue
        nums.setdefault(int(m.group(2)), []).append(sid)
        if m.group(3):
            suffixed.append(sid)
    lo, hi = (min(nums), max(nums)) if nums else (None, None)
    gaps = [n for n in range(lo, hi + 1) if n not in nums] if nums else []
    dates = {sid: parse_date(s["date"]) for sid, s in samples.items()}
    good = sorted(d for d in dates.values() if d)
    per = {}
    for d in good:
        _bump(per, d)
    order = sorted(samples)
    rank_fits = (sum(1 for i, sid in enumerate(order)
                     if dates[sid] and dates[sid] == good[0] + datetime.timedelta(days=i))
                 if good else 0)
    return {"id_range": [lo, hi], "gaps": gaps, "bad_ids": sorted(bad),
            "suffixed": [{"sample": sid, "base": sid[:-1], "base_present": sid[:-1] in samples}
                         for sid in sorted(suffixed)],
            "shared_numbers": {str(n): v for n, v in nums.items() if len(v) > 1},
            "dates_unparsed": sum(1 for d in dates.values() if d is None),
            "first": good[0].isoformat() if good else None,
            "last": good[-1].isoformat() if good else None,
            "distinct": len(per), "most_on_one_date": max(per.values()) if per else 0,
            "text_rank_fits": rank_fits}


# --- gate -----------------------------------------------------------------------------------------
def gate(raw, target, rows, problems, samples, want_samples, want_rows_per_sample=None,
         want_colours=None):
    md5 = hashlib.md5(raw).hexdigest()
    per = {}
    for s in samples.values():
        _bump(per, s["rows"])
    checks = {"size": len(raw) == target["size"], "md5": md5 == target["md5"],
              "roles": not problems["missing_roles"], "values": problems["bad_values"] == 0,
              "units": problems["bad_units"] == 0, "short_rows": problems["short_rows"] == 0,
              "samples": len(samples) == want_samples}
    if want_rows_per_sample is not None:
        checks["rows_per_sample"] = per == {want_rows_per_sample: want_samples}
    if want_colours is not None:
        checks["colour_labels"] = len({r["component"] for r in rows}) == want_colours
    return checks, {"md5": md5, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                    "rows": len(rows), "samples": len(samples),
                    "rows_per_sample": {str(k): v for k, v in sorted(per.items())}}


# --- outputs --------------------------------------------------------------------------------------
def write_c18_tables(samples, out_dir):
    with open(os.path.join(out_dir, "food_colours_c18_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "type", "function", "origin", "region", "date",
                    "n_colours", "top_colour", "top_ppm"])
        for sid in sorted(samples):
            s = samples[sid]
            det = detected(s)
            top = max(det.items(), key=lambda kv: (kv[1], kv[0])) if det else ("", "")
            w.writerow([sid, s["product"], PRODUCT_TYPE.get(s["product"], ""), s["function"],
                        s["origin"], s["region"], s["date"], len(det), top[0], top[1]])
    with open(os.path.join(out_dir, "food_colours_c18_detections.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "type", "function", "origin", "region", "date",
                    "colour", "ppm", "rows_above_zero"])
        for sid in sorted(samples):
            s = samples[sid]
            for c, v in sorted(detected(s).items()):
                w.writerow([sid, s["product"], PRODUCT_TYPE.get(s["product"], ""), s["function"],
                            s["origin"], s["region"], s["date"], c, v,
                            s["rows_above_zero"].get(c, 0)])


def write_c09_rows(rows, out_dir):
    with open(os.path.join(out_dir, "food_colours_c09_rows.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "function", "origin", "region", "date", "test",
                    "colour", "ppm"])
        for r in sorted(rows, key=lambda r: (r["sample"], r.get("test", ""), r["component"])):
            w.writerow([r["sample"], r.get("product", ""), r.get("function", ""),
                        r.get("origin", ""), r.get("region", ""), r.get("date", ""),
                        r.get("test", ""), r["component"], r["value"]])


# --- main -----------------------------------------------------------------------------------------
def load_text(target, data_dir):
    import cfia_census as cc  # published module; only its download and decoding are used
    raw, src = cc.load(target, data_dir)
    text, enc = cc.decode(raw)
    return raw, text, {"source": src, "encoding": enc}


def grade_c18(raw, text):
    rows, problems = parse(text)
    samples = samples_of(rows)
    checks, facts = gate(raw, TARGETS["c18"], rows, problems, samples, 399, 46, 43)
    types, unmapped = type_counts(samples)
    rec = {"gate": checks, "facts": facts, "problems": problems,
           "census_checks": {"S1": types, "S1_unmapped": unmapped,
                             "S2b": function_split(samples)}}
    preds = []
    if all(checks.values()) and not unmapped:
        preds.append(grade_v1(samples))
        preds.append(grade_v2(samples))
        preds.extend(grade_v3_v4_v5(samples))
        preds.extend(grade_v6_v7(samples))
    else:
        for pid in ("V1", "V2", "V3", "V4", "V5", "V6", "V7"):
            preds.append({"id": pid, "kind": "prediction", "graded": False, "met": None,
                          "observed": {"reason": "c18 gate failed"}, "text": ""})
    rec["descriptive"] = {"coding": coding(rows), "double_rows": double_rows(samples),
                          "twins": twins(samples), "mixed": mixed(samples),
                          "ids_dates": ids_and_dates(samples),
                          "colour_stats": colour_stats(samples)}
    return rec, preds, rows, samples


def grade_c09(raw, text):
    rows, problems = parse(text)
    samples = samples_of(rows)
    checks, facts = gate(raw, TARGETS["c09"], rows, problems, samples, 100)
    rec = {"gate": checks, "facts": facts, "problems": problems}
    if all(checks.values()):
        preds = [grade_v8(samples), grade_v9()]
    else:
        preds = [{"id": "V8", "kind": "prediction", "graded": False, "met": None,
                  "observed": {"reason": "c09 gate failed"}, "text": ""}, grade_v9()]
    rec["descriptive"] = {"coding": coding(rows), "twins": twins(samples, 2),
                          "mixed": mixed(samples), "ids_dates": ids_and_dates(samples)}
    return rec, preds, rows, samples


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the food-colours 0.1.0 predictions.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    summary = {"study": "food-colours", "grader": "food_colours", "version": VERSION,
               "files": {}, "predictions": []}
    gates_ok = True
    for name, fn in (("c18", grade_c18), ("c09", grade_c09)):
        try:
            raw, text, prov = load_text(TARGETS[name], args.data_dir)
            rec, preds, rows, samples = fn(raw, text)
            rec["provenance"] = dict(prov, dataset=TARGETS[name]["dataset"],
                                     resource=TARGETS[name]["resource"],
                                     portal_md5=TARGETS[name]["md5"])
            if name == "c18":
                write_c18_tables(samples, args.out_dir)
            else:
                write_c09_rows(rows, args.out_dir)
        except Exception as exc:  # noqa: BLE001 - recorded; the other file still runs
            rec = {"error": f"{type(exc).__name__}: {exc}", "gate": {"loaded": False}}
            ids = ("V1", "V2", "V3", "V4", "V5", "V6", "V7") if name == "c18" else ("V8",)
            preds = [{"id": i, "kind": "prediction", "graded": False, "met": None,
                      "observed": {"reason": rec["error"]}, "text": ""} for i in ids]
            if name == "c09":
                preds.append(grade_v9())
        gates_ok = gates_ok and all(rec["gate"].values())
        summary["files"][name] = rec
        summary["predictions"].extend(preds)
    graded = [p for p in summary["predictions"] if p["graded"]]
    summary["n_graded"] = len(graded)
    summary["n_met"] = sum(1 for p in graded if p["met"])
    with open(os.path.join(args.out_dir, "food_colours_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True, ensure_ascii=False, default=str)
    print(json.dumps({"gates": {n: f["gate"] for n, f in summary["files"].items()},
                      "predictions": [[p["id"], p["graded"], p["met"]]
                                      for p in summary["predictions"]],
                      "n_graded": summary["n_graded"], "n_met": summary["n_met"]},
                     indent=2, ensure_ascii=False))
    return 0 if gates_ok else 1


if __name__ == "__main__":
    sys.exit(main())
