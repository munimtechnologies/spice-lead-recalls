#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""phthalates-series 0.1.0 grader: CFIA's open 2018-19 flatbread and vegan phthalates file (F) and
2012-2018 selected-foods phthalates file (P) against docs/phthalates-series-0.1.0-prereg.md, with
the label maps, coding and gate amendment A2 fixed in docs/phthalates-series-0.1.0-census.md before
any value was read.

Layout (from the census): one 'Phthalate Screen' row per sample whose result is a text count
('0 Phthalates detected / ...'), plus one row in ug/g for each phthalate found in that sample. A
phthalate with no row counts as zero. A sample's result is the sum of its phthalate rows; it is
positive when that sum is above zero. Averages are of positives only. A printed figure matches
within half a unit of its last digit; a share matches when it rounds half up to the printed whole
number. Survey years are April-March, from the sampling date (the registered reading); the year in
each sample ID is reported alongside, descriptively. Both files are on open.canada.ca under the Open
Government Licence - Canada. Standard library only. Made with AI agents working in MV2's (Munim,
Inc.) name. Code Apache-2.0; derived data CC BY 4.0.
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
import perchlorate_census as pcen

VERSION = "0.1.0"
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
ID_YEAR = re.compile(r"^C(\d{4})PHTH")


def round_kib_band(kib):
    """The band as registered: bytes that round to `kib` whole KiB."""
    return (int((kib - 0.5) * 1024), int((kib + 0.5) * 1024))


def ceil_kib_band(kib):
    """Amendment A2: the portal size is the byte count divided by 1,024 and rounded UP, so the
    file has more than (kib - 1) * 1024 and at most kib * 1024 bytes."""
    return ((kib - 1) * 1024 + 1, kib * 1024)


TARGETS = {
    "fv18": {"name": "fv18",
             "dataset": "c4202b90-03d1-4eef-9fcc-0740066fc0c4",
             "resource": "8ce9082f-b339-4e5d-b74a-fa1747d295ac",
             "path": "fsap-chem-ts-2018-2019-phthalates-in-flatbread-and-vegan-products.csv",
             "size": None, "portal_kib": 147,
             "md5": "22dc3074e8e2c55b60fb96a666c5ff16", "samples": 599},
    "ps12": {"name": "ps12",
             "dataset": "ea25d8e4-180c-4f7c-a912-f37381168664",
             "resource": "072329d5-0f9c-4e3f-aae1-c4996ae2b5d5",
             "path": ("fsap-chem-ts-2012-2018-phthalates-in-selected-foods-"
                      "paaspa-chem-ec-2012-2018-phtalates-dans-cert.csv"),
             "size": None, "portal_kib": 1259,
             "md5": "2c80659a91013f3657519375ee33b400", "samples": 4517},
}

# ---- label maps (census note, fixed before values) ----
F_LABELS = {"Dairy Alternative": "dairy_alt", "Mayonnaise - Vegan": "mayo",
            "Meat Alternative": "meat_alt", "Tofu": "tofu"}
Y3 = ("2012-13", "2013-14", "2014-15")
Y4 = Y3 + ("2015-16",)
P_RTE = ("Meal - RTE", "Meal - Toddler/Baby", "Pizza Products")
P_GRAIN = ("Oatmeal", "Infant Food - Cereal")
P_FATS = ("oil", "dressing", "mayo", "shortening")

# ---- printed figures (as registered) ----
# F Table 2: samples, positives, share, (min, max, average), all with two decimals.
F_T2 = {"flatbread": (208, 54, 26, 0.57, 15.00, 2.70),
        "vegan": (391, 19, 5, 0.50, 24.00, 3.61),
        "dairy_alt": (76, 6, 8, 0.59, 2.78, 1.17),
        "mayo": (53, 3, 6, 0.72, 3.19, 1.64),
        "meat_alt": (125, 7, 6, 0.50, 7.57, 3.45),
        "tofu": (137, 3, 2, 0.54, 24.00, 10.85),
        "all": (599, 73, 12, 0.50, 24.00, 2.94)}
# P rows: samples, positives (or None), share (or None), (value, decimals) for min, max, average.
P_V2 = {"grain": (460, 167, 36, (0.27, 2), (23.3, 1), (1.60, 2)),
        "nut_seed": (100, 59, 59, (0.5, 1), (315, 0), (17.2, 1)),
        "rte": (224, 128, None, (0.27, 2), (15.4, 1), (1.46, 2))}
P_V3 = {"fats_oils": (327, None, None, (0.26, 2), (2608, 0), (84.3, 1)),
        "oil": (180, None, None, (0.26, 2), (2608, 0), (107, 0)),
        "dressing": (22, 8, 36, (0.71, 2), (3.75, 2), (2.25, 2))}


def f_sub(product):
    p = cc.clean(product)
    if p.startswith("Bakery Product - "):
        return "flatbread"
    return F_LABELS.get(p, "unmapped")


def p_sub(product):
    p = cc.clean(product)
    if p.startswith("Bakery Product - ") or p.startswith("Cereal - ") or p in P_GRAIN:
        return "grain"
    if p.startswith("Butter - ") or p == "Tahini":
        return "nut_seed"
    if p in P_RTE:
        return "rte"
    if p.startswith("Oil - "):
        return "oil"
    return {"Salad Dressing": "dressing", "Mayonnaise": "mayo",
            "Vegetable Shortening": "shortening"}.get(p, "other")


def component(label):
    """'Bis(2-ethylhexyl) phthalate (DEHP)' -> 'DEHP'; the screen row -> 'SCREEN'; else None."""
    c = cc.clean(label).lower()
    if c == SCREEN:
        return "SCREEN"
    c = re.sub(r"\s*\([a-z]+\)\s*$", "", c)
    return COMPONENTS.get(c)


def id_year(sid):
    m = ID_YEAR.match(sid or "")
    if not m:
        return None
    y = int(m.group(1))
    return f"{y}-{(y + 1) % 100:02d}"


THOUSANDS = re.compile(r"^[1-9]\d{0,2}(,\d{3})+(\.\d+)?$")


def number(cell):
    """'0,54' -> 0.54 (decimal comma); '2,608' or '2,608.0' -> 2608 (thousands separator)."""
    s = cc.clean(cell)
    if THOUSANDS.match(s):
        return float(s.replace(",", ""))
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    return float(s)


def unit_key(unit):
    return cc.clean(unit).replace("µ", "u").replace("μ", "u").lower()


def finish(s, kind):
    s["sub"] = f_sub(s["product"]) if kind == "fv18" else p_sub(s["product"])
    if kind == "fv18":
        s["group"] = ("flatbread" if s["sub"] == "flatbread" else
                      "unmapped" if s["sub"] == "unmapped" else "vegan")
    else:
        s["group"] = "fats_oils" if s["sub"] in P_FATS else s["sub"]
    s["total"] = round(sum(s["values"].values()), 6)
    s["n_pos"] = sum(1 for v in s["values"].values() if v > 0)
    return s


def parse(text, kind):
    """Per-sample records and a dict of format problems (all lists empty when the file is clean)."""
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    cols = cc.find_columns(header)
    missing = [k for k in ("sample", "product", "component", "value", "unit", "function", "date")
               if cols.get(k) is None]
    if missing:
        raise ValueError("missing columns: " + ", ".join(missing))

    def cell(r, key):
        i = cols.get(key)
        return cc.clean(r[i]) if i is not None and i < len(r) else ""

    problems = {k: [] for k in ("unknown_component", "non_numeric", "bad_unit", "bad_screen",
                                "repeated", "mixed_product", "no_screen", "unmapped_product",
                                "bad_date")}
    samples = {}
    for r in body:
        if not any(c.strip() for c in r):
            continue
        sid = cell(r, "sample")
        s = samples.get(sid)
        if s is None:
            d, _ = pcen.parse_date(cell(r, "date"))
            s = samples[sid] = {"id": sid, "product": cell(r, "product"),
                                "function": cell(r, "function"), "origin": cell(r, "origin"),
                                "date": d.isoformat() if d else "",
                                "year": pcen.survey_year(d) if d else None,
                                "id_year": id_year(sid), "screen_n": None, "values": {}}
            if d is None:
                problems["bad_date"].append(sid)
        elif cell(r, "product") != s["product"]:
            problems["mixed_product"].append(sid)
        comp = component(cell(r, "component"))
        val, unit = cell(r, "value"), cell(r, "unit")
        if comp == "SCREEN":
            m = SCREEN_TOKEN.match(val)
            if m is None or s["screen_n"] is not None:
                problems["bad_screen"].append(sid)
            else:
                s["screen_n"] = int(m.group(1))
            if not unit_key(unit).startswith("n/a"):
                problems["bad_unit"].append(f"{sid}: screen")
            continue
        if comp is None:
            problems["unknown_component"].append(f"{sid}: {cell(r, 'component')}")
            continue
        if comp in s["values"]:
            problems["repeated"].append(f"{sid}: {comp}")
            continue
        try:
            x = number(val)
        except ValueError:
            problems["non_numeric"].append(f"{sid}: {comp}")
            continue
        if unit_key(unit) != "ug/g":
            problems["bad_unit"].append(f"{sid}: {comp}")
        if "," in val:
            s.setdefault("comma_cells", []).append(f"{comp}={val}")
        s["values"][comp] = x
    out = [finish(s, kind) for s in samples.values()]
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


def gate(raw_len, md5_ok, samples, problems, target):
    """Gate as written (round-KiB band) and amendment A2 (rounded-up KiB band). Both also need the
    MD5, the sample count and no format problem. Only A2 decides whether values are graded."""
    lo, hi = round_kib_band(target["portal_kib"])
    clo, chi = ceil_kib_band(target["portal_kib"])
    as_written = lo <= raw_len <= hi
    a2 = clo <= raw_len <= chi
    n_ok = len(samples) == target["samples"]
    clean = not any(problems.values())
    return {"md5": md5_ok, "size_band_as_written": [lo, hi], "size_in_band_as_written": as_written,
            "size_band_A2": [clo, chi], "size_in_band_A2": a2, "samples_ok": n_ok,
            "problems": problems,
            "G_as_written": md5_ok and as_written and n_ok and clean,
            "A2": md5_ok and a2 and n_ok and clean}


# ---------------- F ----------------

def grade_f(samples):
    groups = {"all": list(samples)}
    for s in samples:
        groups.setdefault(s["group"], []).append(s)
        if s["group"] == "vegan":
            groups.setdefault(s["sub"], []).append(s)
    v1 = {}
    for g, (n, k, pct, lo, hi, avg) in F_T2.items():
        st = stats(groups.get(g, []))
        v1[g] = {"stats": st,
                 "checks": {"n": st["n"] == n, "positives": st["positives"] == k,
                            "share": share(st["positives"], st["n"]) == pct,
                            "min": near(st["min"], lo, 2), "max": near(st["max"], hi, 2),
                            "mean": near(st["mean"], avg, 2)}}
    out = {"F-V1": {"rows": v1, "held": all(all(r["checks"].values()) for r in v1.values())}}

    negatives = sum(1 for s in samples if s["total"] == 0)
    top_total = max((s["total"] for s in samples), default=None)
    tops = [s for s in samples if s["total"] == top_total]
    top = tops[0] if tops else None
    out["F-V2"] = {"negatives": negatives,
                   "top": None if top is None else {"id": top["id"], "product": top["product"],
                                                     "total": top["total"],
                                                     "values": top["values"]},
                   "checks": {"negatives_526": negatives == 526, "single_top": len(tops) == 1,
                              "top_24_00": top is not None and near(top["total"], 24.00, 2),
                              "top_tofu": top is not None and top["sub"] == "tofu"}}

    per = {a: sum(1 for s in samples if s["values"].get(a, 0) > 0) for a in ORDER}
    multi = sum(1 for s in samples if s["n_pos"] >= 2)
    out["F-V3"] = {"per_phthalate_positive_samples": per, "multi": multi,
                   "checks": {"dinp_51_56": 51 <= per["DINP"] <= 56,
                              "dehp_21_26": 21 <= per["DEHP"] <= 26,
                              "dbp_4": per["DBP"] == 4, "didp_2": per["DIDP"] == 2,
                              "bbp_dnop_0": per["BBP"] == 0 and per["DNOP"] == 0,
                              "multi_at_least_5": multi >= 5}}

    def three(sub):
        return sorted(s["total"] for s in samples if s["sub"] == sub and s["total"] > 0)

    tofu, mayo = three("tofu"), three("mayo")
    out["F-V4"] = {"tofu_positives": tofu, "mayo_positives": mayo,
                   "checks": {"tofu": (len(tofu) == 3 and near(tofu[0], 0.54, 2)
                                       and 7.985 - 1e-9 <= tofu[1] <= 8.035 + 1e-9
                                       and near(tofu[2], 24.00, 2)),
                              "mayo": (len(mayo) == 3 and near(mayo[0], 0.72, 2)
                                       and 0.985 - 1e-9 <= mayo[1] <= 1.035 + 1e-9
                                       and near(mayo[2], 3.19, 2))}}
    for key in ("F-V2", "F-V3", "F-V4"):
        out[key]["held"] = all(out[key]["checks"].values())
    return out


def census_items_f(samples):
    """F-S1 and F-S2 recomputed from the parsed samples (the census note grades them first)."""
    subs, origin = {}, {"flatbread": {}, "vegan": {}}
    for s in samples:
        subs[s["sub"]] = subs.get(s["sub"], 0) + 1
        if s["group"] in origin:
            d = origin[s["group"]]
            d[s["function"]] = d.get(s["function"], 0) + 1
    t1 = {"flatbread": {"Domestic": 97, "Import": 38, "Unknown": 73},
          "vegan": {"Domestic": 121, "Import": 156, "Unknown": 114}}
    want = {"flatbread": 208, "dairy_alt": 76, "mayo": 53, "meat_alt": 125, "tofu": 137}
    return {"F-S1": {"counts": subs, "held": all(subs.get(k, 0) == v for k, v in want.items())},
            "F-S2": {"counts": origin, "printed": t1, "held": origin == t1}}


# ---------------- P ----------------

def _row_checks(st, printed):
    n, k, pct, (lo, dlo), (hi, dhi), (avg, davg) = printed
    c = {"n": st["n"] == n, "min": near(st["min"], lo, dlo), "max": near(st["max"], hi, dhi),
         "mean": near(st["mean"], avg, davg)}
    if k is not None:
        c["positives"] = st["positives"] == k
    if pct is not None:
        c["share"] = share(st["positives"], st["n"]) == pct
    return c


def in_years(samples, years, key="year"):
    return [s for s in samples if s[key] in years]


def p_groups(samples):
    out = {}
    for s in samples:
        out.setdefault(s["sub"], []).append(s)
        if s["sub"] in P_FATS:
            out.setdefault("fats_oils", []).append(s)
    return out


def grade_p(samples):
    st_all = stats(samples)
    out = {"P-V1": {"stats": st_all,
                    "checks": {"positives_977": st_all["positives"] == 977,
                               "min_0_26": near(st_all["min"], 0.26, 2),
                               "max_2608": near(st_all["max"], 2608, 0)}}}
    g3 = p_groups(in_years(samples, Y3))
    for item, table in (("P-V2", P_V2), ("P-V3", P_V3)):
        rows = {}
        for g, printed in table.items():
            st = stats(g3.get(g, []))
            rows[g] = {"stats": st, "checks": _row_checks(st, printed)}
        out[item] = {"rows": rows, "held": all(all(r["checks"].values()) for r in rows.values())}
    mayo = stats(g3.get("mayo", []))
    short = stats(g3.get("shortening", []))
    out["P-V4"] = {"mayo": mayo, "shortening": short,
                   "checks": {"mayo_share_12": share(mayo["positives"], mayo["n"]) == 12,
                              "mayo_mean_2_77": near(mayo["mean"], 2.77, 2),
                              "no_shortening": short["positives"] == 0}}
    for key in ("P-V1", "P-V4"):
        out[key]["held"] = all(out[key]["checks"].values())
    return out


def names_p(samples):
    """Names only: group x survey year (from the date and from the ID), ID year x date year, and
    the 2012-2015 groups by origin label."""
    by_date, by_id, cross, func = {}, {}, {}, {}
    for s in samples:
        year, idy = str(s["year"]), str(s["id_year"])
        for g in ([s["sub"], "fats_oils"] if s["sub"] in P_FATS else [s["sub"]]):
            d = by_date.setdefault(g, {})
            d[year] = d.get(year, 0) + 1
            d = by_id.setdefault(g, {})
            d[idy] = d.get(idy, 0) + 1
            if s["year"] in Y3:
                d = func.setdefault(g, {})
                d[s["function"]] = d.get(s["function"], 0) + 1
        d = cross.setdefault(idy, {})
        d[year] = d.get(year, 0) + 1
    return {"by_group_date_year": by_date, "by_group_id_year": by_id,
            "id_year_vs_date_year": cross, "by_group_function_Y3": func}


def p_year_stats(samples):
    """Also reported, not graded: each group's figures for every single date year, Y3 and Y4, and
    for the ID-year readings of Y3 and Y4."""
    out = {}
    readings = {y: ("year", (y,)) for y in Y4}
    readings.update({"Y3": ("year", Y3), "Y4": ("year", Y4),
                     "Y3_by_id": ("id_year", Y3), "Y4_by_id": ("id_year", Y4)})
    for name, (key, years) in readings.items():
        g = p_groups(in_years(samples, years, key))
        out[name] = {k: stats(v) for k, v in sorted(g.items())}
    return out


# ---------------- shared descriptive ----------------

def descriptive(samples):
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
    twins = {str(k): v for k, v in sorted(seen.items()) if len(v) > 1}
    top = sorted(positives, key=lambda s: -s["total"])[:10]
    mismatch = [{"id": s["id"], "screen_n": s["screen_n"], "rows": len(s["values"]),
                 "above_zero": s["n_pos"]} for s in samples
                if s["screen_n"] != len(s["values"]) or s["screen_n"] != s["n_pos"]]
    zero_rows = [f"{s['id']}: {a}" for s in samples for a, v in s["values"].items() if v <= 0]
    return {"per_phthalate": per,
            "per_phthalate_share_of_all": {a: round(100.0 * per[a]["samples"] / len(samples), 3)
                                           for a in ORDER} if samples else {},
            "smallest_stored": [list(x) for x in stored[:5]],
            "largest": [[s["total"], s["id"], s["product"], s.get("year")] for s in top],
            "positives_by_product": dict(sorted(by_product.items())),
            "positives_by_function": dict(sorted(by_function.items())),
            "identical_nonzero_totals_count": len(twins),
            "identical_nonzero_totals": dict(list(twins.items())[:40]),
            "stored_zero_or_negative": zero_rows,
            "cells_with_a_comma": [f"{s['id']}: {c}" for s in samples
                                   for c in s.get("comma_cells", [])][:50],
            "screen_vs_rows_mismatch": mismatch}


def write_csv(path, samples):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "group", "subgroup", "function", "origin", "date",
                    "survey_year", "id_year", "screen_n"] + list(ORDER) + ["total"])
        for s in sorted(samples, key=lambda x: x["id"]):
            w.writerow([s["id"], s["product"], s["group"], s["sub"], s["function"], s["origin"],
                        s["date"], s["year"], s["id_year"], s["screen_n"]]
                       + [s["values"].get(a, "") for a in ORDER] + [s["total"]])


def run(kind, data_dir, out_dir):
    target = TARGETS[kind]
    raw, src = cc.load(target, data_dir)
    md5 = hashlib.md5(raw).hexdigest()
    text, enc = cc.decode(raw)
    samples, problems = parse(text, kind)
    rec = {"study": f"phthalates-series-{kind}", "version": VERSION, "source": src,
           "bytes": len(raw), "encoding": enc, "md5": md5,
           "sha256": hashlib.sha256(raw).hexdigest()}
    rec["gate"] = gate(len(raw), md5 == target["md5"], samples, problems, target)
    if kind == "fv18":
        rec["census_items"] = census_items_f(samples)
    else:
        rec["names"] = names_p(samples)
    if rec["gate"]["A2"]:
        rec["grades"] = grade_f(samples) if kind == "fv18" else grade_p(samples)
        rec["held"] = sorted(k for k, v in rec["grades"].items() if v["held"])
        if kind == "ps12":
            rec["year_readings"] = p_year_stats(samples)
    else:
        rec["grades"] = None
        rec["held"] = []
    rec["descriptive"] = descriptive(samples)
    with open(os.path.join(out_dir, f"phthalates_{kind}_record.json"), "w",
              encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True, ensure_ascii=False)
    write_csv(os.path.join(out_dir, f"phthalates_{kind}_samples.csv"), samples)
    print(json.dumps({"file": kind,
                      "gate": {k: v for k, v in rec["gate"].items() if k != "problems"},
                      "held": rec["held"]}))
    for k, v in (rec["grades"] or {}).items():
        checks = v.get("checks") or {g: r["checks"] for g, r in v.get("rows", {}).items()}
        print(k, "HELD" if v["held"] else "FAILED", json.dumps(checks))
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade CFIA's 2018-19 and 2012-2018 phthalates files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    for kind in ("fv18", "ps12"):
        run(kind, args.data_dir, args.out_dir)
    print("GRADE-DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
