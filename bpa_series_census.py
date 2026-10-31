#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""bpa-series-census 0.1.0: a names-only structure census of seven open CFIA bisphenol A survey
files (2009-10 to 2017-18), run before any result value is read, so the bpa-series 0.1.0
pre-registration (docs/bpa-series-0.1.0-prereg.md) can be graded on counts and labels and a later
grader can map file labels to each report's product types blind.

All seven are on open.canada.ca under the Open Government Licence - Canada. For each file it runs
cfia_census.census (the per-sample census already used for the 2018-21 BPA and 2019-20 PAH files)
and, because the older FSAP files may use other column names, a column-by-column census: for every
column, the shape of every cell (number, '<' number, negative number, text token, blank) and the
counts of its TEXT labels, per row and per sample. Numeric cells are never printed, summed or
compared; in result-like columns (result, amount, value, level, limit...) a text cell that holds a
digit is recorded only as "<text with digits>". Standard library only. Made with AI agents working
in MV2's (Munim, Inc.) name. Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys

import cfia_census as cc

VERSION = "0.1.0"
TARGETS = (
    {"name": "bpa-2009",
     "dataset": "9846894f-16f2-4834-952a-2e66a162719b",
     "resource": "4ff8f342-d0ea-45a4-9cf5-6f5220e84925",
     "path": ("cfia_acia-1329-v2-fsap_chem_ts_-_2009-10_-_bisphenol-a_in_infant_food_and_formula_"
              "-_sb451_bpha_-.csv"),
     "size": 32261, "md5": "7eacc09417bd528dcca26b8009b824f5"},
    {"name": "bpa-2010",
     "dataset": "ee1d2ca0-18a4-457a-9978-59d20cc6e191",
     "resource": "ab208fba-5551-4d16-87a7-b810a73dbcba",
     "path": ("cfia_acia-1330-v2-fsap_chem_ts_-_2010-11_-_bpa_in_infant_formulae_and_foods_-_"
              "sb451_bpha_-_open_.csv"),
     "size": 39475, "md5": "56b061a4596746dc9736afabac5fbc2a"},
    {"name": "bpa-2011",
     "dataset": "3c1749ef-d6a2-400d-a096-8dd5a13507b2",
     "resource": "86eb4b33-11b4-475d-a0ff-3f32a611a73e",
     "path": ("cfia_acia-1331-v2-fsap_chem_ts_-_2011-12_-_bpa_in_canned_foods_-_sb451_bpha_-_"
              "open_data.csv"),
     "size": 69780, "md5": "afae926b6784187c1b15c19f16c928ef"},
    {"name": "bpa-2012",
     "dataset": "d0539c7a-90ea-4874-a66d-7c75f6cd814d",
     "resource": "c2f6fb46-4c3f-4c23-acfb-4badfc70c835",
     "path": ("cfia_acia-1332-v2-fsap_chem_ts_-_2012-13_-_bpa_in_selected_foods_-_sb451_bpha_-_"
              "open_data.csv"),
     "size": 87982, "md5": "5da0bea9d42e56c68b0423b63cfacb96"},
    {"name": "bpa-2013",
     "dataset": "eba65062-23e4-4530-90bd-767d0c04c079",
     "resource": "755045de-88a0-4ad7-8015-e630d9ca8fcd",
     "path": ("cfia_acia-1333-v2-fsap_chem_ts_-_2013-14_-_bpa_in_canned_foods_-_sb451_bpha_-_"
              "open_data.csv"),
     "size": 94214, "md5": ""},
    {"name": "bpa-2016",
     "dataset": "10478dd5-7ce8-4542-887c-572f0bfe0c8c",
     "resource": "26aa5b60-08a4-4bad-bbdc-17527e6698a3",
     "path": ("cfia-acia-1287-open-data-for-chemistry-targeted-surveys-2016-17-bisphenol-and-bpa-"
              "alternatives-i.csv"),
     "size": 395585, "md5": ""},
    {"name": "bpa-2017",
     "dataset": "15b7f392-56ef-4772-a8e5-aba2c3b0b980",
     "resource": "4dfc8b9a-0b97-4c76-b3e4-07879a8e0c88",
     "path": ("cfia_acia-1263-open-data-for-chemistry-targeted-surveys-2017-18-bisphenol-a-and-bpa-"
              "alternatives.csv"),
     "size": 339854, "md5": "12a495421962033f4c723492e49682fa"},
)
MAX_LABELS = 120
VALUE_WORDS = ("result", "amount", "value", "conc", "level", "lod", "loq", "limit", "mdl", "rdl")
MASKED = "<text with digits>"


def label(cell):
    """A cell without BOM, edge spaces or repeated inner spaces."""
    return cc.clean((cell or "").replace("﻿", ""))


def sample_column(header):
    """Index of the sample-number column (None if absent)."""
    for i, name in enumerate(header):
        h = cc.head(label(name))
        if h.startswith("sample") and "type" not in h and "date" not in h:
            return i
    return None


def is_value_column(name):
    h = cc.head(label(name))
    return any(w in h for w in VALUE_WORDS)


def columns_census(text, top=MAX_LABELS):
    """Per column: cell shapes and counts of TEXT labels per row and per sample (never a number)."""
    rows = csv.reader(io.StringIO(text))
    header = [label(c) for c in next(rows, [])]
    si = sample_column(header)
    masked = [is_value_column(h) for h in header]
    shapes = [{} for _ in header]
    per_row = [{} for _ in header]
    per_sample = [set() for _ in header]
    widths, sids, n = {}, set(), 0
    for r in rows:
        if not any(c.strip() for c in r):
            continue
        n += 1
        cc._bump(widths, str(len(r)))
        sid = label(r[si]) if si is not None and si < len(r) else None
        if sid is not None:
            sids.add(sid)
        for i in range(len(header)):
            raw = r[i] if i < len(r) else ""
            sh = cc.shape(raw)
            cc._bump(shapes[i], sh)
            if sh != "token" or i == si:
                continue
            text_label = label(raw)
            if masked[i] and any(ch.isdigit() for ch in text_label):
                text_label = MASKED
            cc._bump(per_row[i], text_label)
            if sid is not None:
                per_sample[i].add((sid, text_label))
    cols = []
    for i, name in enumerate(header):
        ranked = sorted(per_row[i].items(), key=lambda kv: (-kv[1], kv[0]))[:top]
        by_sample = {}
        for _sid, text_label in per_sample[i]:
            cc._bump(by_sample, text_label)
        cols.append({"name": name, "sample_column": i == si, "value_like": masked[i],
                     "shapes": shapes[i], "distinct_text": len(per_row[i]),
                     "text_rows": dict(ranked),
                     "text_samples": ({k: by_sample[k] for k, _ in ranked}
                                      if si is not None else None)})
    return {"rows": n, "row_widths": widths, "header_width": len(header),
            "samples": len(sids) if si is not None else None, "columns": cols}


def run_target(target, data_dir):
    res = {"study": f"{target['name']}-census", "version": VERSION,
           "dataset": target["dataset"], "resource": target["resource"],
           "portal_size": target["size"], "portal_md5": target["md5"] or None}
    try:
        raw, src = cc.load(target, data_dir)
    except Exception as exc:  # noqa: BLE001 - recorded, the other files still run
        res["error"] = f"{type(exc).__name__}: {exc}"
        return res
    text, enc = cc.decode(raw)
    md5 = hashlib.md5(raw).hexdigest()
    res.update({"source": src, "bytes": len(raw), "size_matches_portal": len(raw) == target["size"],
                "encoding": enc, "sha256": hashlib.sha256(raw).hexdigest(), "md5": md5,
                "md5_matches_portal": (md5 == target["md5"]) if target["md5"] else None})
    try:
        res["census"] = cc.census(text)
    except Exception as exc:  # noqa: BLE001 - the column census below still runs
        res["census"] = {"error": f"{type(exc).__name__}: {exc}"}
    res["columns"] = columns_census(text)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of seven CFIA BPA survey files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    ok = 0
    for target in TARGETS:
        res = run_target(target, args.data_dir)
        if "error" not in res:
            ok += 1
        with open(os.path.join(args.out_dir, f"{target['name']}_census.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
        cols = res.get("columns", {})
        print(json.dumps({"name": target["name"], "error": res.get("error"),
                          "bytes": res.get("bytes"), "size_matches_portal":
                          res.get("size_matches_portal"), "rows": cols.get("rows"),
                          "samples": cols.get("samples"),
                          "header": [c["name"] for c in cols.get("columns", [])],
                          "census_error": res.get("census", {}).get("error")},
                         ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
