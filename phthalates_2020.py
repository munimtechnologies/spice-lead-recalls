#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""phthalates-2020 0.1.0 grader: CFIA's open 2020-21 phthalates file (ready-to-eat meals, vegetable
fats and oils) against the predictions of docs/phthalates-2020-0.1.0-prereg.md, with the label map,
coding and gate amendment fixed in docs/phthalates-2020-0.1.0-census.md before any value was read.

Layout (from the census): one 'Phthalate Screen' row per sample whose result is a text count
('0 Phthalates detected / ...', '1 Phthalate detected / ...'), plus one row in ug/g for each
phthalate found in that sample. A phthalate with no row counts as zero. A sample's result is the sum
of its phthalate rows; it is positive when that sum is above zero. Averages are of positives only.
A printed figure matches within half a unit of its last digit; a share matches when it rounds half
up to the printed whole number. The file is on open.canada.ca under the Open Government Licence -
Canada. Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name. Code
Apache-2.0; derived data CC BY 4.0.
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

import cfia_census as cc

VERSION = "0.1.0"
TARGET = {"name": "ph20",
          "dataset": "4ae4c2b3-e1b7-451a-b313-02e51d73da73",
          "resource": "960252a3-4b35-44ef-9e8d-46ed1b0dd61c",
          "path": "fsap-chem-ts-2020-2021-phthalates-in-ready-to-eat-meals-vegetable-fats-and-oils.csv",
          "size": None, "size_band": (113000, 118000),
          "md5": "612780be14a4a571044d93aaa27f99f2", "samples": 500}
ORDER = ("BBP", "DBP", "DNOP", "DEHP", "DINP", "DIDP")
COMPONENTS = {
    "bis(2-ethylhexyl) phthalate": "DEHP",
    "butyl benzyl phthalate": "BBP",
    "di-n-octyl phthalate": "DNOP",
    "dibutylphthalate": "DBP",
    "diisodecyl phthalate": "DIDP",
    "diisononyl phthalate": "DINP",
}
SCREEN = "phthalate screen"
SCREEN_TOKEN = re.compile(r"^(\d+) phthalates? detected\b", re.IGNORECASE)
# Census note map (fixed before values): five labels are the report's ready-to-eat meals.
RTE_LABELS = ("Infant Food - Puree", "Meal - RTE", "Meal - Toddler/Baby", "Pizza Products", "Soup")
FO_LABELS = {"Salad Dressing": "dressing", "Vegetable Shortening": "shortening",
             "Mayonnaise": "mayo"}
CHILDREN_LABEL = "Meal - Toddler/Baby"

# Printed figures (report page, as registered).
T2 = {"rte": (250, 5, 0.3, 4.2, 1.56, 2),
      "fo": (250, 31, 0.2, 3.4, 0.86, 12),
      "all": (500, 36, 0.2, 4.2, 0.96, 7)}
T3 = {"oil": (150, 0.2, 3.4, 0.89), "dressing": (50, 0.3, 0.6, 0.45)}
T1 = {"rte": {"Domestic": 56, "Import": 165, "Unknown": 29},
      "fo": {"Domestic": 27, "Import": 161, "Unknown": 62}}


def subgroup(product):
    p = cc.clean(product)
    if p in RTE_LABELS:
        return "rte"
    if p.startswith("Oil - "):
        return "oil"
    return FO_LABELS.get(p, "unmapped")


def group_of(sub):
    if sub == "rte":
        return "rte"
    if sub in ("oil", "dressing", "shortening", "mayo"):
        return "fo"
    return "unmapped"


def number(cell):
    s = cc.clean(cell)
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    return float(s)


def unit_key(unit):
    return cc.clean(unit).replace("µ", "u").replace("μ", "u").lower()


def finish(s):
    """Derived fields of one sample record (sub, group, total, n_pos)."""
    s["sub"] = subgroup(s["product"])
    s["group"] = group_of(s["sub"])
    s["total"] = round(sum(s["values"].values()), 6)
    s["n_pos"] = sum(1 for v in s["values"].values() if v > 0)
    return s


def parse(text):
    """Per-sample records and a dict of format problems (all lists empty when the file is clean)."""
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    cols = cc.find_columns(header)
    missing = [k for k in ("sample", "product", "component", "value", "unit", "function")
               if cols.get(k) is None]
    if missing:
        raise ValueError("missing columns: " + ", ".join(missing))

    def cell(r, key):
        i = cols.get(key)
        return cc.clean(r[i]) if i is not None and i < len(r) else ""

    problems = {k: [] for k in ("unknown_component", "non_numeric", "bad_unit", "bad_screen",
                                "repeated", "mixed_product", "no_screen", "unmapped_product")}
    samples = {}
    for r in body:
        if not any(c.strip() for c in r):
            continue
        sid = cell(r, "sample")
        s = samples.get(sid)
        if s is None:
            s = samples[sid] = {"id": sid, "product": cell(r, "product"),
                                "function": cell(r, "function"), "origin": cell(r, "origin"),
                                "screen_n": None, "values": {}}
        elif cell(r, "product") != s["product"]:
            problems["mixed_product"].append(sid)
        comp = cell(r, "component").lower()
        val, unit = cell(r, "value"), cell(r, "unit")
        if comp == SCREEN:
            m = SCREEN_TOKEN.match(val)
            if m is None or s["screen_n"] is not None:
                problems["bad_screen"].append(sid)
            else:
                s["screen_n"] = int(m.group(1))
            if unit_key(unit) != "n/a":
                problems["bad_unit"].append(f"{sid}: screen")
            continue
        abbr = COMPONENTS.get(comp)
        if abbr is None:
            problems["unknown_component"].append(f"{sid}: {comp}")
            continue
        if abbr in s["values"]:
            problems["repeated"].append(f"{sid}: {abbr}")
            continue
        try:
            x = number(val)
        except ValueError:
            problems["non_numeric"].append(f"{sid}: {abbr}")
            continue
        if unit_key(unit) != "ug/g":
            problems["bad_unit"].append(f"{sid}: {abbr}")
        s["values"][abbr] = x
    out = [finish(s) for s in samples.values()]
    for s in out:
        if s["screen_n"] is None:
            problems["no_screen"].append(s["id"])
        if s["group"] == "unmapped":
            problems["unmapped_product"].append(f"{s['id']}: {s['product']}")
    return out, problems


def stats(samples):
    pos = sorted(s["total"] for s in samples if s["total"] > 0)
    return {"n": len(samples), "positives": len(pos),
            "min": pos[0] if pos else None, "max": pos[-1] if pos else None,
            "mean": round(sum(pos) / len(pos), 6) if pos else None}


def near(x, printed, decimals):
    return x is not None and abs(x - printed) <= 0.5 * 10 ** (-decimals) + 1e-9


def share(k, n):
    return int(math.floor(100.0 * k / n + 0.5)) if n else None


def _t2_checks(st, printed):
    n, k, lo, hi, avg, pct = printed
    return {"n": st["n"] == n, "positives": st["positives"] == k, "min": near(st["min"], lo, 1),
            "max": near(st["max"], hi, 1), "mean": near(st["mean"], avg, 2),
            "share": share(st["positives"], st["n"]) == pct}


def grade(samples):
    """The five value items (V1-V5) on parsed samples."""
    by_group = {"rte": [s for s in samples if s["group"] == "rte"],
                "fo": [s for s in samples if s["group"] == "fo"], "all": list(samples)}
    v1 = {}
    for g, rows in by_group.items():
        st = stats(rows)
        v1[g] = {"stats": st, "checks": _t2_checks(st, T2[g])}
    held1 = all(all(r["checks"].values()) for r in v1.values())

    negatives = sum(1 for s in samples if s["total"] == 0)
    top_total = max((s["total"] for s in samples), default=None)
    tops = [s for s in samples if s["total"] == top_total]
    top = tops[0] if tops else None
    v2_checks = {"negatives_464": negatives == 464,
                 "single_top": len(tops) == 1,
                 "top_4_2": top is not None and near(top["total"], 4.2, 1),
                 "top_rte": top is not None and top["group"] == "rte",
                 "top_children_label": top is not None and top["product"] == CHILDREN_LABEL}
    v2 = {"negatives": negatives,
          "top": None if top is None else {"id": top["id"], "product": top["product"],
                                            "total": top["total"], "values": top["values"]},
          "checks": v2_checks}

    per = {a: sum(1 for s in samples if s["values"].get(a, 0) > 0) for a in ORDER}
    multi = sum(1 for s in samples if s["n_pos"] >= 2)
    v3_checks = {"dehp_23": per["DEHP"] == 23,
                 "others_1_to_9": all(1 <= per[a] <= 9 for a in ORDER if a != "DEHP"),
                 "multi_7": multi == 7}
    v3 = {"per_phthalate_positive_samples": per, "multi": multi, "checks": v3_checks}

    v4 = {}
    v4_checks = {}
    for sub, (n, lo, hi, avg) in T3.items():
        st = stats([s for s in samples if s["sub"] == sub])
        v4[sub] = st
        v4_checks[sub] = (st["n"] == n and near(st["min"], lo, 1) and near(st["max"], hi, 1)
                          and near(st["mean"], avg, 2))
    v4_checks["oil_29_positive"] = v4["oil"]["positives"] == 29
    dress = sorted(s["total"] for s in samples if s["sub"] == "dressing" and s["total"] > 0)
    v4_checks["dressing_0_3_and_0_6"] = (len(dress) == 2 and near(dress[0], 0.3, 1)
                                         and near(dress[1], 0.6, 1))
    v4["dressing_positives"] = dress
    v4["checks"] = v4_checks

    bad5 = [s["id"] for s in samples if s["sub"] in ("mayo", "shortening") and s["total"] > 0]
    v5 = {"positive_mayo_or_shortening": bad5, "checks": {"none": not bad5}}

    out = {"V1": {"rows": v1}, "V2": v2, "V3": v3, "V4": v4, "V5": v5}
    out["V1"]["held"] = held1
    for key in ("V2", "V3", "V4", "V5"):
        out[key]["held"] = all(out[key]["checks"].values())
    return out


def census_items(samples):
    """S1-S3 and S5 recomputed from the parsed samples (the census note grades them first)."""
    groups = {"rte": 0, "fo": 0, "unmapped": 0}
    subs = {}
    origin = {"rte": {}, "fo": {}}
    for s in samples:
        groups[s["group"]] = groups.get(s["group"], 0) + 1
        subs[s["sub"]] = subs.get(s["sub"], 0) + 1
        if s["group"] in origin:
            d = origin[s["group"]]
            d[s["function"]] = d.get(s["function"], 0) + 1
    s2 = (subs.get("oil", 0), subs.get("dressing", 0),
          subs.get("shortening", 0) + subs.get("mayo", 0))
    return {"S1": {"counts": groups, "held": groups["rte"] == 250 and groups["fo"] == 250},
            "S2": {"counts": subs, "held": s2 == (150, 50, 50)},
            "S3": {"counts": origin, "printed": T1,
                   "held": all(origin[g] == T1[g] for g in T1)}}


def descriptive(samples):
    """Also reported, not graded."""
    per = {}
    for a in ORDER:
        vals = sorted(s["values"][a] for s in samples if s["values"].get(a, 0) > 0)
        per[a] = {"samples": len(vals), "min": vals[0] if vals else None,
                  "max": vals[-1] if vals else None}
    stored = sorted((v, s["id"], a, s["product"]) for s in samples for a, v in s["values"].items())
    positives = [s for s in samples if s["total"] > 0]
    by_product, by_function = {}, {}
    for s in positives:
        by_product[s["product"]] = by_product.get(s["product"], 0) + 1
        by_function[s["function"]] = by_function.get(s["function"], 0) + 1
    seen = {}
    for s in positives:
        seen.setdefault(s["total"], []).append(s["id"])
    screen_mismatch = [{"id": s["id"], "screen_n": s["screen_n"], "rows": len(s["values"]),
                        "above_zero": s["n_pos"]} for s in samples
                       if s["screen_n"] != len(s["values"]) or s["screen_n"] != s["n_pos"]]
    return {"per_phthalate": per,
            "smallest_stored": [list(x) for x in stored[:5]],
            "positives_by_product": dict(sorted(by_product.items())),
            "positives_by_function": dict(sorted(by_function.items())),
            "identical_nonzero_totals": {str(k): v for k, v in sorted(seen.items()) if len(v) > 1},
            "screen_vs_rows_mismatch": screen_mismatch}


def gate(raw_len, md5_ok, samples, problems):
    """Gate as written (G) and the census-note amendment A1 (cell and unit checks on phthalate rows
    only). Only A1 decides whether the value items are graded."""
    band = TARGET["size_band"][0] <= raw_len <= TARGET["size_band"][1]
    n_ok = len(samples) == TARGET["samples"]
    count_tokens = sum(1 for s in samples if s["screen_n"])
    a1 = md5_ok and band and n_ok and not any(problems.values())
    g_written = md5_ok and band and n_ok and count_tokens == 0 and not any(problems.values())
    return {"md5": md5_ok, "size_in_band": band, "samples_500": n_ok,
            "screen_tokens_that_are_counts": count_tokens, "problems": problems,
            "G_as_written": g_written, "A1": a1}


def write_csv(path, samples):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "group", "subgroup", "function", "origin", "screen_n"]
                   + list(ORDER) + ["total"])
        for s in sorted(samples, key=lambda x: x["id"]):
            w.writerow([s["id"], s["product"], s["group"], s["sub"], s["function"], s["origin"],
                        s["screen_n"]] + [s["values"].get(a, "") for a in ORDER] + [s["total"]])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade CFIA's 2020-21 phthalates file.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    raw, src = cc.load(TARGET, args.data_dir)
    md5 = hashlib.md5(raw).hexdigest()
    text, enc = cc.decode(raw)
    samples, problems = parse(text)
    rec = {"study": "phthalates-2020", "version": VERSION, "source": src, "bytes": len(raw),
           "encoding": enc, "md5": md5, "sha256": hashlib.sha256(raw).hexdigest()}
    rec["gate"] = gate(len(raw), md5 == TARGET["md5"], samples, problems)
    rec["census_items"] = census_items(samples)
    if rec["gate"]["A1"]:
        rec["grades"] = grade(samples)
        rec["held"] = sorted(k for k, v in rec["grades"].items() if v["held"])
    else:
        rec["grades"] = None
        rec["held"] = []
    rec["descriptive"] = descriptive(samples)
    with open(os.path.join(args.out_dir, "phthalates_2020_record.json"), "w",
              encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True, ensure_ascii=False)
    write_csv(os.path.join(args.out_dir, "phthalates_2020_samples.csv"), samples)
    print(json.dumps({"gate": {k: v for k, v in rec["gate"].items() if k != "problems"},
                      "held": rec["held"],
                      "census_items": {k: v["held"] for k, v in rec["census_items"].items()}}))
    if rec["grades"]:
        for k, v in rec["grades"].items():
            print(k, "HELD" if v["held"] else "FAILED",
                  json.dumps(v.get("checks", {k2: r["checks"] for k2, r in v.get("rows", {}).items()})))
    print("GRADE-DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
