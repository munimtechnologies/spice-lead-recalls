#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ethyl-carbamate 0.1.0 grader: CFIA's open ethyl carbamate files (2018-19 alcoholic beverages
and vinegars, "ec18"; 2019-20 fermented vegetables and soy products, "ec19") against their printed
reports.

Grades V1-V7 of docs/ethyl-carbamate-0.1.0-prereg.md with the label maps and coding rules of
docs/ethyl-carbamate-0.1.0-census.md, both published before this module reads any value.

Coding (fixed in the pre-registration and the census note): each file has one ethyl carbamate row
per sample and every result cell is a number. A sample is a *detect* when its result is above
zero. Units are ng/g, which is ppb. A printed figure matches when the file's value is within half
a unit of its last printed digit; a derived band (an average pooled from several printed rows) is
inclusive at both ends.

Label maps (census note): ec18 "Beer" and the single "Beef" row (ID 251, inside the beer ID block)
are beer; "Beverage - Alcohol" is sake, spirits and liqueurs, and wine together (the file has no
finer label); "Vinegar" is vinegar. ec19 "Soy Products" and "Tofu" are soy; Cabbage, Cucumber -
Pickled, Fish/Seafood - Frozen/Refrigerated (ID 272, inside the vegetable ID block), Gherkin -
Pickled, Pickled Vegetable - Misc and Sauerkraut are fermented vegetables.

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
UNIT = "ng/g"

TARGETS = {
    "ec18": {"name": "ec18",
             "dataset": "303903b7-91ba-4a79-ad37-7bcd9f0dc8a1",
             "resource": "0a30e00b-9c4b-4402-b329-51565119d767",
             "path": ("cfia-acia-1149_2018-19_ethylcarbamate_in_selected_foods_-_2018-2019_le-"
                      "carbamate-dethyle-dans-le.csv"),
             "size": 71629, "md5": "d7d7bf62a3bb275ccec657fb27501fd8", "samples": 390},
    # The portal lists this file's size as 58; the file served is 58,972 bytes and matches the
    # portal MD5 (census job ethyl-carbamate-census-v1). The gate uses the measured size.
    "ec19": {"name": "ec19",
             "dataset": "920d97a1-b98d-4def-b386-dd234a45f457",
             "resource": "985e3d90-ecbb-4a34-b299-8032627c3c3d",
             "path": ("fsap-chem-ts-ethyl-carbamate-in-fermented-vegetables-and-soy-products-"
                      "2019-2020_paaspa-chem-ec-c.csv"),
             "size": 58972, "md5": "e5aab1da6e57c1afa0536e9d92455a6e", "samples": 300},
}

# --- label maps (docs/ethyl-carbamate-0.1.0-census.md) -------------------------------------------
EC18_TYPE = {"Beer": "beer", "Beef": "beer", "Beverage - Alcohol": "other", "Vinegar": "vinegar"}
EC18_TYPES = ("beer", "other", "vinegar")
EC19_TYPE = {"Soy Products": "soy", "Tofu": "soy"}
for _label in ("Cabbage", "Cucumber - Pickled", "Fish/Seafood - Frozen/Refrigerated",
               "Gherkin - Pickled", "Pickled Vegetable - Misc", "Sauerkraut"):
    EC19_TYPE[_label] = "veg"
EC19_TYPES = ("veg", "soy")
SAUERKRAUT = "Sauerkraut"
KIMCHI_LABELS = ("Cabbage", "Pickled Vegetable - Misc", "Fish/Seafood - Frozen/Refrigerated")

# Printed rows: (samples, detects, minimum, maximum, average). Printed strings are matched within
# half a unit of their last digit; a tuple is an inclusive band.
EC18_TABLE2 = {"beer": (125, 2, "4", "4", "4"), "vinegar": (125, 6, "6", "135", "29.5")}
# Sake (3 detects, 7-33, average 15.7), spirits and liqueurs (23, 4-42, 12.3) and wine (3, 17-86,
# printed "40") pooled: 29 detects, 4-86, average between (3 x 15.65 + 23 x 12.25 + 3 x 39.5) / 29
# = 15.4207 and (3 x 15.75 + 23 x 12.35 + 3 x 40.5) / 29 = 15.6138.
EC18_OTHER = (140, 29, "4", "86", (15.42, 15.62))
EC18_TOTAL = (390, 37, "4", "135", "17.2")
# The later CFIA report's alcoholic-beverage subtotal (beer + sake + spirits + wine).
EC18_SUBTOTAL = (265, 31, "4", "86", (14.75, 14.85))
EC19_TABLE2 = {"veg": (200, 3, "4", "9", (6.25, 6.35)), "soy": (100, 6, "7", "217", (107.5, 108.5))}
EC19_TOTAL = (300, 9, "4", "217", (73.5, 74.5))
EC19_TOTAL_V7 = (74.05, 74.15)
VEG_DETECTS = ("4", "6", "9")
VINEGAR_REST = (5.5, 13.5, 41.0, 43.0)  # each of the other five rounds to 6-13; they sum to 41-43

ROLES = {
    "sample": ("sample no",), "region": ("region",), "function": ("function",),
    "origin": ("origin",), "product": ("product",), "date": ("date sampled",),
    "test": ("type of test",), "component": ("component",),
    "value": ("maxofamount", "amount", "result"), "unit": ("report unit", "unit"),
}
OPTIONAL = ("region",)
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
    problems = {"missing_roles": sorted(r for r in ROLES if r not in cols and r not in OPTIONAL),
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
        if r.get("unit", "") != UNIT:
            problems["bad_units"] += 1
        rows.append(r)
    return rows, problems


def samples_of(rows):
    """sample ID -> {labels, value (largest row), rows}."""
    out = {}
    for r in rows:
        s = out.get(r["sample"])
        if s is None:
            s = {"sample": r["sample"], "rows": 0, "value": None}
            for f in ("product", "function", "origin", "region", "date"):
                s[f] = r.get(f, "")
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


# --- summaries -----------------------------------------------------------------------------------
def summarise(group):
    """A list of samples -> samples, detects, minimum, maximum, average (detects only), values."""
    vals = sorted(s["value"] for s in group if is_detect(s))
    return {"n": len(group), "detects": len(vals), "min": vals[0] if vals else None,
            "max": vals[-1] if vals else None,
            "mean": sum(vals) / len(vals) if vals else None, "values": vals}


def groups(samples, type_of, types):
    out = {t: [] for t in types}
    unmapped = {}
    for s in samples.values():
        t = type_of.get(s["product"])
        if t is None:
            _bump(unmapped, s["product"])
        else:
            out[t].append(s)
    return out, unmapped


def check_row(summ, spec):
    n, det, pmin, pmax, avg = spec
    avg_ok = in_band(summ["mean"], avg) if isinstance(avg, tuple) else in_range(summ["mean"], avg)
    return {"samples": summ["n"] == n, "detects": summ["detects"] == det,
            "min": in_range(summ["min"], pmin), "max": in_range(summ["max"], pmax),
            "average": avg_ok}


def _public(summ):
    return {k: summ[k] for k in ("n", "detects", "min", "max", "mean")}


def function_split(grouped):
    return {t: [sum(1 for s in g if s["function"] == "Domestic"),
                sum(1 for s in g if s["function"] == "Import"),
                sum(1 for s in g if s["function"] not in ("Domestic", "Import"))]
            for t, g in grouped.items()}


# --- ec18 ----------------------------------------------------------------------------------------
def grade_v1(g18):
    rows = {"beer": (summarise(g18["beer"]), EC18_TABLE2["beer"]),
            "vinegar": (summarise(g18["vinegar"]), EC18_TABLE2["vinegar"]),
            "other_pooled": (summarise(g18["other"]), EC18_OTHER),
            "total": (summarise(g18["beer"] + g18["other"] + g18["vinegar"]), EC18_TOTAL)}
    cells = {k: check_row(s, spec) for k, (s, spec) in rows.items()}
    met = all(all(c.values()) for c in cells.values())
    return {"id": "V1", "kind": "prediction", "graded": True, "met": met,
            "observed": {"rows": {k: _public(s) for k, (s, _) in rows.items()}, "cells": cells,
                         "ungraded_part": "sake, spirits and wine rows separately (no label)"},
            "text": "ec18 Table 2: beer, vinegar and grand-total rows in full; sake + spirits + "
                    "wine as one pooled row (29 detects, 4-86, average 15.42-15.62)"}


def grade_v2(g18):
    beer = summarise(g18["beer"])["values"]
    vin = summarise(g18["vinegar"])["values"]
    beer_ok = len(beer) == 2 and all(in_range(v, "4") for v in beer)
    lo, hi, smin, smax = VINEGAR_REST
    rest = vin[:-1]
    vin_ok = (len(vin) == 6 and in_range(vin[-1], "135")
              and all(lo - 1e-9 <= v <= hi + 1e-9 for v in rest)
              and smin - 1e-9 <= sum(rest) <= smax + 1e-9)
    return {"id": "V2", "kind": "prediction", "graded": True, "met": beer_ok and vin_ok,
            "observed": {"beer_detects": beer, "vinegar_detects": vin,
                         "vinegar_rest_sum": sum(rest) if rest else None,
                         "beer_ok": beer_ok, "vinegar_ok": vin_ok,
                         "ungraded_part": "sake 7 / 7 / 33 and wine 17 / 17 / 86 (no label)"},
            "text": "ec18 hidden values: both beer detects round to 4; one vinegar is 135 and the "
                    "other five each round to 6-13 and sum to 41-43"}


def grade_v3(g18):
    summ = summarise(g18["beer"] + g18["other"])
    cells = check_row(summ, EC18_SUBTOTAL)
    return {"id": "V3", "kind": "prediction", "graded": True, "met": all(cells.values()),
            "observed": {"subtotal": _public(summ), "cells": cells},
            "text": "later report's alcoholic subtotal: 265 samples, 31 detects, 4-86, average "
                    "14.75-14.85"}


def grade_v4():
    return {"id": "V4", "kind": "prediction", "graded": False, "met": None,
            "observed": {"reason": "the file labels every sake, spirit, liqueur and wine "
                                   "'Beverage - Alcohol'; no label names the wine (census note)"},
            "text": "the 86 ppb wine is fortified, sweet or 20-year (ungraded)"}


def other_top(g18, n=5):
    """The largest pooled sake/spirits/wine detects, for the record."""
    vals = sorted(((s["value"], s["sample"], s["origin"], s["function"]) for s in g18["other"]
                   if is_detect(s)), key=lambda x: (-x[0], x[1]))
    return [{"ppb": v, "sample": sid, "origin": o, "function": f} for v, sid, o, f in vals[:n]]


# --- ec19 ----------------------------------------------------------------------------------------
def grade_v5(g19):
    veg, soy = summarise(g19["veg"]), summarise(g19["soy"])
    tot = summarise(g19["veg"] + g19["soy"])
    cells = {"veg": check_row(veg, EC19_TABLE2["veg"]), "soy": check_row(soy, EC19_TABLE2["soy"]),
             "total": check_row(tot, EC19_TOTAL)}
    veg_vals = veg["values"]
    cells["veg"]["values_4_6_9"] = (len(veg_vals) == 3 and
                                    all(in_range(v, p) for v, p in zip(veg_vals, VEG_DETECTS)))
    met = all(all(c.values()) for c in cells.values())
    return {"id": "V5", "kind": "prediction", "graded": True, "met": met,
            "observed": {"veg": _public(veg), "veg_detects": veg_vals, "soy": _public(soy),
                         "soy_detects": soy["values"], "total": _public(tot), "cells": cells},
            "text": "ec19 Table 2: vegetables 3 detects rounding to 4, 6, 9 (average 6.25-6.35); "
                    "soy 6 detects, 7-217, average 107.5-108.5; total 9, 4-217, 73.5-74.5"}


def grade_v6(g19):
    soy_none = sum(1 for s in g19["soy"] if not is_detect(s))
    veg_det = sorted((s for s in g19["veg"] if is_detect(s)), key=lambda s: s["value"])
    labels = [s["product"] for s in veg_det]
    kraut = labels.count(SAUERKRAUT)
    others = [x for x in labels if x != SAUERKRAUT]
    veg_ok = len(labels) == 3 and kraut == 2 and len(others) == 1 and others[0] in KIMCHI_LABELS
    soy_det = sorted((s for s in g19["soy"] if is_detect(s)), key=lambda s: -s["value"])
    return {"id": "V6", "kind": "prediction", "graded": True,
            "met": soy_none == 94 and veg_ok,
            "observed": {"soy_without_ec": soy_none, "veg_detect_labels": labels,
                         "veg_detects": [{"sample": s["sample"], "product": s["product"],
                                          "origin": s["origin"], "ppb": s["value"]}
                                         for s in veg_det],
                         "soy_detects": [{"sample": s["sample"], "product": s["product"],
                                          "origin": s["origin"], "ppb": s["value"]}
                                         for s in soy_det],
                         "ungraded_part": "5 bean curds and 1 miso (labels are 'Soy Products' "
                                          "and 'Tofu' only)"},
            "text": "ec19 text: 94 of 100 soy samples without EC (not 93); vegetable detects are "
                    "2 sauerkrauts and 1 other fermented cabbage or vegetable (the kimchi)"}


def grade_v7(g19):
    soy = summarise(g19["soy"])
    tot = summarise(g19["veg"] + g19["soy"])
    checks = {"soy_min_7": in_range(soy["min"], "7"),
              "soy_average_107.5_108.5": in_band(soy["mean"], EC19_TABLE2["soy"][4]),
              "total_average_74.05_74.15": in_band(tot["mean"], EC19_TOTAL_V7)}
    return {"id": "V7", "kind": "prediction", "graded": True, "met": all(checks.values()),
            "observed": {"checks": checks, "soy_min": soy["min"], "soy_mean": soy["mean"],
                         "total_mean": tot["mean"], "total_min": tot["min"]},
            "text": "the later report's 2019 soy row (4.0 / 74.1) carries the Total row: soy "
                    "minimum 7, soy average 107.5-108.5, all-products average 74.05-74.15"}


# --- descriptive ---------------------------------------------------------------------------------
def coding(samples):
    vals = [s["value"] for s in samples.values() if s["value"] is not None]
    pos = sorted(v for v in vals if v > 0)
    return {"zero": sum(1 for v in vals if v == 0), "above_zero": len(pos),
            "smallest_above_zero": pos[:5], "distinct_values": len(set(vals))}


def parse_date(text):
    for fmt in ("%d-%b-%y", "%Y-%m-%d", "%m/%d/%Y"):
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
    dates = [parse_date(s["date"]) for s in samples.values()]
    good = sorted(d for d in dates if d)
    return {"id_range": [lo, hi], "gaps": gaps, "bad_ids": sorted(bad),
            "suffixed": [{"sample": sid, "base": sid[:-1], "base_present": sid[:-1] in samples}
                         for sid in sorted(suffixed)],
            "shared_numbers": {str(n): v for n, v in nums.items() if len(v) > 1},
            "dates_unparsed": sum(1 for d in dates if d is None),
            "first": good[0].isoformat() if good else None,
            "last": good[-1].isoformat() if good else None}


def special_rows(samples, labels):
    return [{"sample": s["sample"], "product": s["product"], "function": s["function"],
             "origin": s["origin"], "detect": is_detect(s)}
            for s in sorted(samples.values(), key=lambda s: s["sample"]) if s["product"] in labels]


# --- gate ----------------------------------------------------------------------------------------
def gate(raw, target, problems, samples):
    md5 = hashlib.md5(raw).hexdigest()
    per = {}
    for s in samples.values():
        _bump(per, s["rows"])
    checks = {"size": len(raw) == target["size"], "md5": md5 == target["md5"],
              "roles": not problems["missing_roles"], "values": problems["bad_values"] == 0,
              "units": problems["bad_units"] == 0, "short_rows": problems["short_rows"] == 0,
              "samples": len(samples) == target["samples"],
              "one_row_per_sample": per == {1: target["samples"]}}
    return checks, {"md5": md5, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                    "samples": len(samples),
                    "rows_per_sample": {str(k): v for k, v in sorted(per.items())}}


def _ungraded(ids, reason):
    return [{"id": i, "kind": "prediction", "graded": False, "met": None,
             "observed": {"reason": reason}, "text": ""} for i in ids]


def grade_ec18(raw, text, target=None):
    target = target or TARGETS["ec18"]
    rows, problems = parse(text)
    samples = samples_of(rows)
    checks, facts = gate(raw, target, problems, samples)
    g18, unmapped = groups(samples, EC18_TYPE, EC18_TYPES)
    rec = {"gate": checks, "facts": facts, "problems": problems,
           "census_checks": {"types": {t: len(g) for t, g in g18.items()}, "unmapped": unmapped,
                             "function_split": function_split(g18)}}
    if all(checks.values()) and not unmapped:
        preds = [grade_v1(g18), grade_v2(g18), grade_v3(g18), grade_v4()]
    else:
        preds = _ungraded(("V1", "V2", "V3"), "ec18 gate failed") + [grade_v4()]
    rec["descriptive"] = {"coding": coding(samples), "ids_dates": ids_and_dates(samples),
                          "beef_row": special_rows(samples, ("Beef",)),
                          "other_alcohol_top": other_top(g18)}
    return rec, preds, samples


def grade_ec19(raw, text, target=None):
    target = target or TARGETS["ec19"]
    rows, problems = parse(text)
    samples = samples_of(rows)
    checks, facts = gate(raw, target, problems, samples)
    g19, unmapped = groups(samples, EC19_TYPE, EC19_TYPES)
    rec = {"gate": checks, "facts": facts, "problems": problems,
           "census_checks": {"types": {t: len(g) for t, g in g19.items()}, "unmapped": unmapped,
                             "function_split": function_split(g19)}}
    if all(checks.values()) and not unmapped:
        preds = [grade_v5(g19), grade_v6(g19), grade_v7(g19)]
    else:
        preds = _ungraded(("V5", "V6", "V7"), "ec19 gate failed")
    rec["descriptive"] = {"coding": coding(samples), "ids_dates": ids_and_dates(samples),
                          "fish_seafood_row": special_rows(
                              samples, ("Fish/Seafood - Frozen/Refrigerated",))}
    return rec, preds, samples


# --- outputs -------------------------------------------------------------------------------------
def write_samples(all_samples, out_dir):
    with open(os.path.join(out_dir, "ethyl_carbamate_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "sample", "product", "type", "function", "origin", "region", "date",
                    "ec_ppb"])
        for name, samples, type_of in all_samples:
            for sid in sorted(samples):
                s = samples[sid]
                w.writerow([name, sid, s["product"], type_of.get(s["product"], ""), s["function"],
                            s["origin"], s["region"], s["date"], s["value"]])


def load_text(target, data_dir):
    import cfia_census as cc  # published module; only its download and decoding are used
    raw, src = cc.load(target, data_dir)
    text, enc = cc.decode(raw)
    return raw, text, {"source": src, "encoding": enc}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the ethyl-carbamate 0.1.0 predictions.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    summary = {"study": "ethyl-carbamate", "grader": "ethyl_carbamate", "version": VERSION,
               "files": {}, "predictions": []}
    gates_ok = True
    tables = []
    plan = (("ec18", grade_ec18, EC18_TYPE, ("V1", "V2", "V3")),
            ("ec19", grade_ec19, EC19_TYPE, ("V5", "V6", "V7")))
    for name, fn, type_of, ids in plan:
        try:
            raw, text, prov = load_text(TARGETS[name], args.data_dir)
            rec, preds, samples = fn(raw, text)
            rec["provenance"] = dict(prov, dataset=TARGETS[name]["dataset"],
                                     resource=TARGETS[name]["resource"],
                                     portal_md5=TARGETS[name]["md5"])
            tables.append((name, samples, type_of))
        except Exception as exc:  # noqa: BLE001 - recorded; the other file still runs
            rec = {"error": f"{type(exc).__name__}: {exc}", "gate": {"loaded": False}}
            preds = _ungraded(ids, rec["error"])
            if name == "ec18":
                preds.append(grade_v4())
        gates_ok = gates_ok and all(rec["gate"].values())
        summary["files"][name] = rec
        summary["predictions"].extend(preds)
    write_samples(tables, args.out_dir)
    graded = [p for p in summary["predictions"] if p["graded"]]
    summary["n_graded"] = len(graded)
    summary["n_met"] = sum(1 for p in graded if p["met"])
    with open(os.path.join(args.out_dir, "ethyl_carbamate_summary.json"), "w",
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
