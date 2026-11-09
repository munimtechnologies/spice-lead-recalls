#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""dried-tea-grade 0.1.0: grades the value items of docs/dried-tea-2009-0.1.0-prereg.md (V1, V2,
V4, V5, V6; V3 is not graded because the file has no tea-type field) and items P1-P3 of
docs/dried-tea-2009-0.1.0-census.md on CFIA's open 2009-10 dried-tea file (open.canada.ca dataset
2782dbc5-ebbb-4ef1-a85f-294a5fe60f47).

Rules (fixed in the census note before any value was read):
- named pesticide = a pesticide-group row whose component is not "Pesticide Screen";
- detected = stored value above 0; violation = value above 0.1 ug/g (at-or-above also reported);
- pesticide samples = sample numbers with one trailing "A" removed; metal samples = raw numbers;
- V4 per metal over all metal samples, every metal except beryllium;
- V6 holds if mercury is above 0 in fewer than 87% of the metal samples.
Reuses the published census module (dried_tea_census.py) for parsing. Standard library only.
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys

import dried_tea_census as dc

VERSION = "0.1.0"
THRESHOLD = 0.1          # ug/g = ppm
HG_SHARE = 0.87          # 2010-11 page: 87% of its teas had detectable mercury
HG_MAX_2010 = 0.023      # 2010-11 page: highest mercury value, ppm
SCREEN = "pesticide screen"
# Unit table (prereg C5): factor to ug/g. Only ug/g is expected; others are converted by table.
MICRO = chr(0xB5)        # micro sign; the Greek letter mu (U+03BC) is mapped to it
UNITS = {MICRO + "g/g": 1.0, "ug/g": 1.0, "mg/kg": 1.0, "ppm": 1.0,
         "ng/g": 0.001, MICRO + "g/kg": 0.001, "ug/kg": 0.001, "ppb": 0.001}


def unit_key(unit):
    """Unit cell for the UNITS table: Greek mu read as the micro sign, lower case."""
    return dc.clean(unit).replace(chr(0x3BC), MICRO).lower()
EXPECT = {"V1": 69, "V2": 41}


def number(raw):
    """Float of a number-shaped cell (comma decimal allowed), else None."""
    s = dc.clean(raw)
    if dc.shape(s) not in ("number", "negative-number"):
        return None
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    return float(s)


def tea_number(sid):
    """Sample number with one trailing 'A' or 'B' removed (census item P1)."""
    return sid[:-1] if len(sid) > 1 and sid[-1] in "AB" else sid


def screen_count(text):
    """Leading integer of a screen cell such as '2 Pesticides detected/détectés', else None."""
    m = re.match(r"\s*(\d+)\s+pesticides?\s+detect", dc.clean(text), re.IGNORECASE)
    return int(m.group(1)) if m else None


def _col(header, name):
    for i, c in enumerate(header):
        if dc.head(c) == name:
            return i
    return None


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def grade(text):
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    rows = [r for r in reader if any(c.strip() for c in r)]
    col = dc.find_columns(header)
    origin_i = _col(header, "origin")

    def cell(r, i):
        return r[i] if i is not None and i < len(r) else ""

    pest_samples, metal_samples = set(), set()
    named = []          # (sample, method, component, value_ugg)
    named_bad = []      # rows of named pesticides with a non-number shape or unknown unit
    screens = {}        # (sample, method) -> count
    screen_bad = 0
    metal = {}          # symbol -> list of (sample, value or None, raw)
    origin_of = {}
    for r in rows:
        sid = dc.clean(cell(r, col["sample"]))
        comp = dc.clean(cell(r, col["component"]))
        test = dc.clean(cell(r, col["test"]))
        unit = dc.clean(cell(r, col["unit"]))
        raw = cell(r, col["value"])
        sym = dc.metal_symbol(comp)
        if sym:
            metal_samples.add(sid)
            metal.setdefault(sym, []).append((sid, number(raw), dc.clean(raw), unit))
            continue
        s = dc.base_id(sid)
        pest_samples.add(s)
        if origin_i is not None:
            origin_of[s] = dc.clean(cell(r, origin_i))
        if dc.norm_name(comp) == SCREEN:
            n = screen_count(raw)
            if n is None or (s, test) in screens:
                screen_bad += 1
            else:
                screens[(s, test)] = n
            continue
        v = number(raw)
        f = UNITS.get(unit_key(unit))
        if v is None or f is None:
            named_bad.append({"sample": sid, "component": comp, "shape": dc.shape(raw),
                              "unit": unit})
            continue
        named.append((s, test, comp, v * f))

    # Pesticide items
    detected = {s for s, _, _, v in named if v > 0}
    above = {s for s, _, _, v in named if v > THRESHOLD}
    at_or_above = {s for s, _, _, v in named if v >= THRESHOLD}
    over_per_sample = {}
    for s, _, _, v in named:
        if v > THRESHOLD:
            _bump(over_per_sample, s)
    screen_detected = {s for (s, _), n in screens.items() if n > 0}
    rows_per = {}
    for s, t, _, v in named:
        _bump(rows_per, (s, t))
    p2_mismatch = sorted(f"{s} {t}: screen {screens.get((s, t))} rows {rows_per.get((s, t), 0)}"
                         for (s, t) in set(screens) | set(rows_per)
                         if screens.get((s, t)) != rows_per.get((s, t), 0))
    per_pest = {}
    for s, t, c, v in named:
        p = per_pest.setdefault(c, {"rows": 0, "teas": set(), "max_ugg": 0.0, "teas_over_0_1": set(),
                                    "methods": set()})
        p["rows"] += 1
        p["methods"].add(t)
        if v > 0:
            p["teas"].add(s)
        p["max_ugg"] = max(p["max_ugg"], v)
        if v > THRESHOLD:
            p["teas_over_0_1"].add(s)
    per_pest = {c: {"rows": p["rows"], "teas_detected": len(p["teas"]), "max_ugg": p["max_ugg"],
                    "teas_over_0_1": len(p["teas_over_0_1"]), "methods": sorted(p["methods"])}
                for c, p in sorted(per_pest.items())}
    by_origin = {}
    for s in sorted(pest_samples):
        o = origin_of.get(s, "")
        d = by_origin.setdefault(o, {"teas": 0, "detected": 0, "over_0_1": 0})
        d["teas"] += 1
        d["detected"] += s in detected
        d["over_0_1"] += s in above

    # Metal items
    n_metal = len(metal_samples)
    metals = {}
    for sym, items in sorted(metal.items()):
        vals = [v for _, v, _, _ in items if v is not None]
        pos = {sid for sid, v, _, _ in items if v is not None and v > 0}
        zero = sum(1 for _, v, _, _ in items if v == 0)
        other = sorted({raw for _, v, raw, _ in items if v is None})
        metals[sym] = {"rows": len(items), "samples": len({i[0] for i in items}),
                       "above_zero": len(pos), "zero": zero, "not_number": other[:10],
                       "min": min(vals) if vals else None, "max": max(vals) if vals else None,
                       "units": sorted({u for _, _, _, u in items})}
    v4_fail = {k: n_metal - m["above_zero"] for k, m in metals.items()
               if k != "Be" and m["above_zero"] < n_metal}
    be = metals.get("Be")
    hg = metals.get("Hg")
    tea_p = {tea_number(s) for s in pest_samples}
    tea_m = {tea_number(s) for s in metal_samples}

    items = {
        "V1": {"expect": EXPECT["V1"], "found": len(detected),
               "holds": len(detected) == EXPECT["V1"],
               "screen_count_above_zero": len(screen_detected),
               "note": "not fully blind: the census printed the screen counts (bounds 47-94)"},
        "V2": {"expect": EXPECT["V2"], "found": len(above), "holds": len(above) == EXPECT["V2"],
               "at_or_above": len(at_or_above)},
        "V3": {"graded": False, "why": "the file has no tea-type field (census C2)"},
        "V4": {"holds": bool(metals) and not v4_fail and len(metals) == 18,
               "metals_not_above_zero_in_all": v4_fail},
        "V5": {"holds": be is not None and be["above_zero"] < n_metal,
               "beryllium_above_zero": be["above_zero"] if be else None},
        "V6": ({"graded": False, "why": "mercury not named"} if hg is None else
               {"holds": hg["above_zero"] < HG_SHARE * n_metal,
                "mercury_above_zero": hg["above_zero"], "metal_samples": n_metal,
                "share": hg["above_zero"] / n_metal if n_metal else None}),
        "P1": {"holds": tea_p == tea_m and len(tea_p) == len(pest_samples),
               "teas_pesticide": len(tea_p), "teas_metal": len(tea_m),
               "teas_in_both": len(tea_p & tea_m),
               "metal_numbers_ending_B": sum(1 for s in metal_samples if s.endswith("B"))},
        "P2": {"holds": not p2_mismatch and screen_bad == 0 and len(screens) > 0,
               "screen_rows": len(screens), "bad_screen_rows": screen_bad,
               "mismatches": p2_mismatch[:20], "mismatch_count": len(p2_mismatch)},
        "P3": {"holds": not named_bad and len(named) > 0, "named_rows": len(named),
               "bad": named_bad[:20], "bad_count": len(named_bad)},
    }
    r5 = None
    if hg is not None and n_metal:
        r5 = ("file supports the 2010-11 page (mercury detected in fewer than 87%)"
              if items["V6"]["holds"] else
              "file supports the 2009-10 page (mercury detected in at least 87%)")
    return {
        "rows": len(rows), "pesticide_samples": len(pest_samples), "metal_samples": n_metal,
        "named_pesticide_rows": len(named), "items": items, "R5": r5,
        "reported": {
            "teas_with_two_or_more_over_0_1": sum(1 for n in over_per_sample.values() if n >= 2),
            "per_pesticide": per_pest, "by_origin": by_origin, "metals": metals,
            "mercury_max_vs_2010_11": {"max_2009_10": hg["max"] if hg else None,
                                       "max_2010_11_page": HG_MAX_2010},
        },
    }


def load(data_dir):
    """The census job's saved copy if present, else a fresh download."""
    local = os.path.join(data_dir, dc.CSV_TARGET["resource"] + ".csv")
    if os.path.exists(local):
        with open(local, "rb") as fh:
            return fh.read(), "cached " + local
    url = dc.BASE + dc.CSV_TARGET["resource"] + "/download/" + dc.CSV_TARGET["path"]
    return dc._fetch(url), url


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the dried-tea-2009 value items.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    raw, source = load(args.data_dir)
    md5 = hashlib.md5(raw).hexdigest()
    res = {"study": "dried-tea-2009-grade", "version": VERSION, "source": source,
           "bytes": len(raw), "md5": md5, "md5_matches_portal": md5 == dc.CSV_TARGET["portal_md5"],
           "gate_size_band": dc.gate(len(raw))}
    if not (res["md5_matches_portal"] and res["gate_size_band"]):
        res["error"] = "file differs from the one the census read; not graded"
    else:
        text, _ = dc.decode(raw)
        res.update(grade(text))
    with open(os.path.join(args.out_dir, "dried_tea_grade_2009.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps(res, indent=2, sort_keys=True, ensure_ascii=False))
    print("GRADE-DONE", "error" if "error" in res else "ok")
    return 1 if "error" in res else 0


if __name__ == "__main__":
    sys.exit(main())
