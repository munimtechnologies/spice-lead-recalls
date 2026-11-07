#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""fumonisin 0.1.0 grader: CFIA's open 2010-11 (fum10), 2011-12 (fum11) and 2012-2018 (fum1218)
fumonisin files against docs/fumonisin-2010-0.1.0-prereg.md and docs/fumonisin-series-0.1.0-prereg.md,
with the label maps and grading rules fixed in docs/fumonisin-2010-0.1.0-census.md,
docs/fumonisin-series-0.1.0-census.md and docs/fumonisin-0.1.0-grader.md before any value was read.

FUMONISIN-GRADE-MODULE 0.1.0

Layout (from the names-only censuses): two rows per sample, 'Fumonisin B1' and 'Fumonisin B2', each a
number in ng/g (ppb). A sample's total is B1 + B2 (no file stores a total); a missing row counts as
zero and is reported as a format problem. A sample is positive when its total is above zero.
Averages are of positives only. A printed figure matches when the value lies in its half-unit band
[printed - 0.5 * 10^-d, printed + 0.5 * 10^-d). Survey years are April-March, from the sampling date.
All three files are on open.canada.ca under the Open Government Licence - Canada. Standard library
only. Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; derived data CC BY 4.0.
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


def kib_band_up(kib):
    """Byte counts whose size in KiB, rounded up, is `kib`: more than (kib-1)*1024, at most kib*1024."""
    return ((kib - 1) * 1024, kib * 1024)


TARGETS = {
    "fum10": {"name": "fum10",
              "dataset": "5ac4ed9e-9dc4-4c3c-9a2b-e99530fbda13",
              "resource": "48123e67-3a23-44f3-8cf1-ef8054ca1766",
              "path": ("chem_ts_2010-2011_fumonisins_in_selected_foods_chem_ec_2010-2011_"
                       "fumonisines_dans_des_aliments_s.csv"),
              "size": None, "portal_kib": 86,
              "md5": "219641dd2317367eb87069eef88a88b6", "samples": 276},
    "fum11": {"name": "fum11",
              "dataset": "e5906422-e8bf-498b-972e-faf2b688aa97",
              "resource": "fe5490e6-35c6-4175-be9d-8b679548784d",
              "path": ("chem_ts_2011-2012_fumonisins_in_selected_foods_chem_ec_2011-2012_"
                       "fumonisines_dans_des_aliments_s.csv"),
              "size": None, "portal_kib": 155,
              "md5": "9f6fddeb2448a199d1beae925a5f3a96", "samples": 454},
    "fum1218": {"name": "fum1218",
                "dataset": "449c63d9-c545-4cce-b907-e32840967873",
                "resource": "df04bd3f-d591-49dc-91c7-0e498b74f22f",
                "path": ("chem_ts_2012-2018_fumonisins_in_selected_foods_chem_ec_2012-2018_"
                         "fumonisines_dans_des_aliments_s.csv"),
                "size": None, "portal_kib": 1371,
                "md5": "6c87fb0bc35b3fc0cea0d3bd2e93e97b", "samples": 4261},
}
COMP = {"fumonisin b1": "B1", "fumonisin b2": "B2"}

# ---- label maps (census notes, fixed before any value was read) ----
F10_GROUP = {"Cereal - Corn": "cereal", "Cornmeal": "cornmeal_grits", "Popcorn": "popcorn",
             "Corn": "canned_corn", "Corn Starch": "starch", "Flour - Corn": "flour",
             # chips 45 + tacos 21 + tortillas 10 + cornbread mix 2 = 78 on the page; 79 in the file
             "Chips - Corn": "block", "Bakery Product - Tortilla/Wrap/Pita": "block",
             "Corn Products": "block"}
F11_CORN = frozenset({"Cereal - Corn", "Chips - Corn", "Corn", "Corn - Sweet - Organic",
                      "Corn Products", "Cornmeal", "Flour - Corn"})
F11_SOY = frozenset({"Bean - Soy", "Beverage - Soy", "Flour - Soy", "Infant Formula - Soy",
                     "Misc - Soy", "Soy Products"})
F11_OTHER = frozenset({"Cereal - Other", "Misc", "Protein Powder"})
B_SOY = frozenset({"Bean - Soy", "Beverage - Soy", "Flour - Soy", "Infant Formula - Soy",
                   "Soy Products", "Tofu", "Meat Alternative"})
GRAINS = ("amaranth", "arrowroot", "barley", "buckwheat", "corn", "kamut", "millet", "oat",
          "quinoa", "rice", "rye", "spelt", "teff", "triticale", "wheat")
_GRAIN_RX = [(g, re.compile(r"(?<![a-z])" + g)) for g in GRAINS]
GRAIN_SPECIAL = {"popcorn": "corn", "taco": "corn"}
Y_CORN = ("2012-13", "2013-14", "2014-15", "2015-16", "2016-17", "2017-18")


def f10_group(product):
    return F10_GROUP.get(cc.clean(product), "unmapped")


def f11_group(product):
    p = cc.clean(product)
    if p in F11_CORN:
        return "corn"
    if p in F11_SOY:
        return "soy"
    if p in F11_OTHER:
        return "other"
    return "unmapped"


def b_group(product):
    p = cc.clean(product)
    if p == "Beverage - Tea" or p.startswith("Tea - "):
        return "tea"
    if p in B_SOY:
        return "soy"
    return "grain"


def label_grain(product):
    """The grain a product label names ('Grain - Rice' -> 'rice'), or None if it names none."""
    low = cc.clean(product).lower()
    if low in GRAIN_SPECIAL:
        return GRAIN_SPECIAL[low]
    for g, rx in _GRAIN_RX:
        if rx.search(low):
            return g
    return None


GROUP_OF = {"fum10": f10_group, "fum11": f11_group, "fum1218": b_group}

THOUSANDS = re.compile(r"^[1-9]\d{0,2}(,\d{3})+(\.\d+)?$")


def number(cell):
    """'2,608' -> 2608.0 (thousands separator); '0,54' -> 0.54 (decimal comma); else float()."""
    s = cc.clean(cell)
    if THOUSANDS.match(s):
        return float(s.replace(",", ""))
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    return float(s)


def within(x, lo, hi):
    """lo <= x < hi, with a 1e-9 allowance for binary floating point."""
    return x is not None and lo - 1e-9 <= x < hi - 1e-9


def matches(x, printed, decimals):
    half = 0.5 * 10 ** (-decimals)
    return within(x, printed - half, printed + half)


def round_half_up(x):
    return int(math.floor(x + 0.5 + 1e-9))


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

    problems = {k: [] for k in ("unknown_component", "non_numeric", "bad_unit", "repeated",
                                "mixed_product", "missing_component", "negative", "bad_date",
                                "unmapped_product")}
    group_of = GROUP_OF[kind]
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
                                "year": pcen.survey_year(d) if d else None, "values": {}}
            if d is None:
                problems["bad_date"].append(sid)
        elif cell(r, "product") != s["product"]:
            problems["mixed_product"].append(sid)
        comp = COMP.get(cell(r, "component").lower())
        if comp is None:
            problems["unknown_component"].append(f"{sid}: {cell(r, 'component')}")
            continue
        if comp in s["values"]:
            problems["repeated"].append(f"{sid}: {comp}")
            continue
        val = cell(r, "value")
        try:
            x = number(val)
        except ValueError:
            problems["non_numeric"].append(f"{sid}: {comp}")
            continue
        if cell(r, "unit").lower() != "ng/g":
            problems["bad_unit"].append(f"{sid}: {comp}")
        if x < 0:
            problems["negative"].append(f"{sid}: {comp}")
        if "," in val:
            s.setdefault("comma_cells", []).append(f"{comp}={val}")
        s["values"][comp] = x
    out = []
    for s in samples.values():
        for c in ("B1", "B2"):
            if c not in s["values"]:
                problems["missing_component"].append(f"{s['id']}: {c}")
        s["total"] = round(s["values"].get("B1", 0.0) + s["values"].get("B2", 0.0), 6)
        s["group"] = group_of(s["product"])
        if kind == "fum1218":
            s["grain"] = label_grain(s["product"]) if s["group"] == "grain" else None
        if s["group"] == "unmapped":
            problems["unmapped_product"].append(f"{s['id']}: {s['product']}")
        out.append(s)
    return out, problems


def stats(samples):
    pos = sorted(s["total"] for s in samples if s["total"] > 0)
    return {"n": len(samples), "positives": len(pos),
            "min": pos[0] if pos else None, "max": pos[-1] if pos else None,
            "mean": round(sum(pos) / len(pos), 6) if pos else None}


def by_key(samples, key):
    out = {}
    for s in samples:
        out.setdefault(str(s.get(key)), []).append(s)
    return out


def brief(s):
    return {"id": s["id"], "product": s["product"], "year": s.get("year"), "total": s["total"],
            "B1": s["values"].get("B1"), "B2": s["values"].get("B2")}


def top_of(samples):
    pos = [s for s in samples if s["total"] > 0]
    if not pos:
        return None, 0
    hi = max(s["total"] for s in pos)
    tops = [s for s in pos if s["total"] == hi]
    return tops[0], len(tops)


def held(item):
    item["held"] = all(item["checks"].values())
    return item


# ---------------- 2010-11 ----------------

def grade_f10(samples):
    st = stats(samples)
    pos = [s for s in samples if s["total"] > 0]
    out = {"V1": held({"stats": st, "checks": {"positives_157": st["positives"] == 157}})}
    mn = st["min"]
    at_min = [s for s in pos if round_half_up(s["total"]) == round_half_up(mn)] if pos else []
    out["V2"] = held({"min": mn, "at_min": [brief(s) for s in at_min],
                      "chips_label_at_min": any(s["product"] == "Chips - Corn" for s in at_min),
                      "checks": {"min_rounds_to_20": within(mn, 19.5, 20.5),
                                 "chip_block_at_min": any(s["group"] == "block" for s in at_min),
                                 "cornmeal_label_at_min": any(s["group"] == "cornmeal_grits"
                                                              for s in at_min)}})
    top, n_top = top_of(samples)
    tv = top["total"] if top else None
    out["V3"] = held({"top": brief(top) if top else None, "tied_tops": n_top,
                      "looser_6645_6655": within(tv, 6645, 6655),
                      "checks": {"top_rounds_to_6650": within(tv, 6649.5, 6650.5),
                                 "top_is_cornmeal_label": bool(top) and
                                 top["group"] == "cornmeal_grits"}})
    above = [s for s in samples if s["total"] > 800]
    groups = {}
    for s in above:
        groups[s["group"]] = groups.get(s["group"], 0) + 1
    out["V4"] = held({"above_800": [brief(s) for s in sorted(above, key=lambda x: -x["total"])],
                      "by_group": groups,
                      "checks": {"eight": len(above) == 8, "cereal_4": groups.get("cereal") == 4,
                                 "cornmeal_label_3": groups.get("cornmeal_grits") == 3,
                                 "block_1": groups.get("block") == 1,
                                 "nothing_else": sum(groups.values()) == 8 and
                                 set(groups) <= {"cereal", "cornmeal_grits", "block"}}})
    out["2010-V5"] = held({"mean": st["mean"],
                           "checks": {"mean_rounds_to_268": within(st["mean"], 267.5, 268.5)}})
    return out


# ---------------- 2011-12 ----------------

def grade_f11(samples):
    pos = [s for s in samples if s["total"] > 0]
    soy = [s for s in pos if s["group"] == "soy"]
    corn = [s for s in samples if s["group"] == "corn"]
    corn_other = [s for s in samples if s["group"] in ("corn", "other")]
    one = soy[0] if len(soy) == 1 else None
    out = {"A-V1": held({"positives": len(pos), "soy_positives": [brief(s) for s in soy],
                         "by_group": {g: stats(v) for g, v in sorted(by_key(samples, "group").items())},
                         "checks": {"positives_162": len(pos) == 162, "one_soy": len(soy) == 1,
                                    "soy_is_flour": bool(one) and one["product"] == "Flour - Soy",
                                    "soy_rounds_to_22_4": bool(one) and
                                    within(one["total"], 22.35, 22.45),
                                    "corn_or_other_161": sum(1 for s in pos if s["group"] in
                                                             ("corn", "other")) == 161}})}
    sc, sco = stats(corn), stats(corn_other)
    out["A-V2"] = held({"corn": sc, "corn_or_other": sco,
                        "corn_min_rounds_to_23_1": within(sc["min"], 23.05, 23.15),
                        "checks": {"corn_min_rounds_to_20_8": within(sc["min"], 20.75, 20.85)}})
    top, n_top = top_of(samples)
    out["A-V3"] = held({"top": brief(top) if top else None, "tied_tops": n_top,
                        "checks": {"top_rounds_to_4442_5": bool(top) and
                                   within(top["total"], 4442.45, 4442.55),
                                   "top_is_cornmeal": bool(top) and top["product"] == "Cornmeal"}})
    out["A-V4"] = held({"corn": sc, "corn_or_other": sco,
                        "checks": {"corn_mean_rounds_to_253_2": within(sc["mean"], 253.15, 253.25)}})
    return out


# ---------------- 2012-2018 ----------------

def grade_b(samples):
    g = by_key(samples, "group")
    st = {k: stats(g.get(k, [])) for k in ("grain", "soy", "tea")}
    st["total"] = stats(samples)
    out = {"B-V1": held({"stats": st, "checks": {
        "positives_1076": st["total"]["positives"] == 1076,
        "grain_1073": st["grain"]["positives"] == 1073, "soy_2": st["soy"]["positives"] == 2,
        "tea_1": st["tea"]["positives"] == 1}})}
    top, n_top = top_of(samples)
    out["B-V2"] = held({"min": st["total"]["min"], "top": brief(top) if top else None,
                        "tied_tops": n_top, "checks": {
                            "min_rounds_to_20": within(st["total"]["min"], 19.5, 20.5),
                            "max_rounds_to_7790": bool(top) and within(top["total"], 7789.5, 7790.5),
                            "top_is_cornmeal": bool(top) and top["product"] == "Cornmeal"}})
    soy = sorted((s for s in g.get("soy", []) if s["total"] > 0), key=lambda s: s["total"])
    tofu = [s for s in soy if s["product"] == "Tofu" and s["year"] == "2012-13"
            and within(s["total"], 26.5, 27.5)]
    flour = [s for s in soy if s["product"] == "Flour - Soy" and s["year"] == "2013-14"
             and within(s["total"], 44.5, 45.5)]
    out["B-V3"] = held({"soy_positives": [brief(s) for s in soy], "checks": {
        "two": len(soy) == 2, "tofu_2012_27": len(tofu) == 1, "soy_flour_2013_45": len(flour) == 1}})
    tea = [s for s in g.get("tea", []) if s["total"] > 0]
    one = tea[0] if len(tea) == 1 else None
    out["B-V4"] = held({"tea_positives": [brief(s) for s in tea], "checks": {
        "one": len(tea) == 1, "black": bool(one) and one["product"] == "Tea - Black",
        "rounds_to_43": bool(one) and within(one["total"], 42.5, 43.5)}})
    out["B-V11"] = held({"means": {k: v["mean"] for k, v in st.items()}, "checks": {
        "grain_365": within(st["grain"]["mean"], 364.5, 365.5),
        "soy_36": within(st["soy"]["mean"], 35.5, 36.5),
        "total_364": within(st["total"]["mean"], 363.5, 364.5)}})
    for k in ("B-V5", "B-V6", "B-V9"):
        out[k] = {"status": "not gradable from labels (census note)", "held": None}
    for k in ("B-V7", "B-V8", "B-V10"):
        out[k] = {"status": "failed on the label map at census (census note)", "held": False}
    return out


# Exploratory, not registered: positives whose total matches a printed figure at its precision.
LOOKUPS = {"wheat 2012 min 28.8": (28.8, 1), "wheat 2012 max 393": (393, 0),
           "rice 33": (33, 0), "rice 47": (47, 0), "rice 249": (249, 0), "rice 42": (42, 0),
           "oat 2017 53": (53, 0), "corn 2012 max 7711": (7711, 0), "text max 7710": (7710, 0)}


def lookups(samples, table=None):
    out = {}
    for name, (v, d) in (table or LOOKUPS).items():
        hits = [brief(s) for s in samples if s["total"] > 0 and matches(s["total"], v, d)]
        out[name] = hits[:20]
    return out


def dup_suffix(samples):
    """IDs ending in 'D' after a digit, and whether the same ID without the 'D' is in the file."""
    ids = {s["id"]: s for s in samples}
    out = []
    for sid, s in sorted(ids.items()):
        m = re.match(r"^(.*\d)D$", sid)
        if not m:
            continue
        base = ids.get(m.group(1))
        out.append({"id": sid, "stem": m.group(1), "stem_in_file": base is not None,
                    "product": s["product"], "stem_product": base["product"] if base else None,
                    "total": s["total"], "stem_total": base["total"] if base else None,
                    "year": s["year"], "stem_year": base["year"] if base else None})
    return out


def names_b(samples):
    """Group and label-grain figures by survey year (reported, not graded)."""
    out = {"group_year": {}, "grain_label": {}, "grain_label_year": {}, "corn_label_year": {}}
    for k, v in sorted(by_key(samples, "group").items()):
        out["group_year"][k] = {y: stats(w) for y, w in sorted(by_key(v, "year").items())}
    grain = [s for s in samples if s["group"] == "grain"]
    for k, v in sorted(by_key(grain, "grain").items()):
        out["grain_label"][k] = stats(v)
        out["grain_label_year"][k] = {y: stats(w) for y, w in sorted(by_key(v, "year").items())}
    corn = [s for s in grain if s["grain"] == "corn"]
    out["corn_label_year"] = {y: stats(w) for y, w in sorted(by_key(corn, "year").items())}
    out["no_d_suffix"] = stats([s for s in samples if not re.match(r"^.*\dD$", s["id"])])
    return out


def descriptive(samples):
    pos = [s for s in samples if s["total"] > 0]
    zeros = {c: sum(1 for s in samples if s["values"].get(c) == 0) for c in ("B1", "B2")}
    small = {c: sorted({s["values"][c] for s in samples if s["values"].get(c, 0) > 0})[:5]
             for c in ("B1", "B2")}
    only_b2 = sum(1 for s in pos if s["values"].get("B1", 0) == 0)
    by_product, by_function, by_year = {}, {}, {}
    for s in samples:
        d = by_product.setdefault(s["product"], [0, 0])
        d[0] += 1
        d[1] += 1 if s["total"] > 0 else 0
    for s in pos:
        by_function[s["function"]] = by_function.get(s["function"], 0) + 1
        by_year[str(s["year"])] = by_year.get(str(s["year"]), 0) + 1
    top = sorted(pos, key=lambda s: -s["total"])[:10]
    return {"zero_rows": zeros, "smallest_nonzero": small, "positives_with_b1_zero": only_b2,
            "products_n_positives": dict(sorted(by_product.items())),
            "positives_by_function": dict(sorted(by_function.items())),
            "positives_by_year": dict(sorted(by_year.items())),
            "by_group": {k: stats(v) for k, v in sorted(by_key(samples, "group").items())},
            "by_product": {k: stats(v) for k, v in sorted(by_key(samples, "product").items())},
            "largest": [brief(s) for s in top],
            "cells_with_a_comma": [f"{s['id']}: {c}" for s in samples
                                   for c in s.get("comma_cells", [])][:50]}


def gate(raw_len, md5_ok, samples, problems, target):
    lo, hi = kib_band_up(target["portal_kib"])
    return {"md5": md5_ok, "size_band": [lo, hi], "size_in_band": lo < raw_len <= hi,
            "samples": len(samples), "samples_as_printed": len(samples) == target["samples"],
            "problems": problems, "G": bool(md5_ok and lo < raw_len <= hi)}


def write_csv(path, samples, kind):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "group", "label_grain", "function", "origin", "date",
                    "survey_year", "B1_ng_g", "B2_ng_g", "total_ng_g"])
        for s in sorted(samples, key=lambda x: x["id"]):
            w.writerow([s["id"], s["product"], s["group"], s.get("grain") or "", s["function"],
                        s["origin"], s["date"], s["year"], s["values"].get("B1", ""),
                        s["values"].get("B2", ""), s["total"]])


GRADERS = {"fum10": grade_f10, "fum11": grade_f11, "fum1218": grade_b}


def run(kind, data_dir, out_dir):
    target = TARGETS[kind]
    raw, src = cc.load(target, data_dir)
    md5 = hashlib.md5(raw).hexdigest()
    text, enc = cc.decode(raw)
    samples, problems = parse(text, kind)
    rec = {"study": f"fumonisin-{kind}", "version": VERSION, "source": src, "bytes": len(raw),
           "encoding": enc, "md5": md5, "sha256": hashlib.sha256(raw).hexdigest()}
    rec["gate"] = gate(len(raw), md5 == target["md5"], samples, problems, target)
    if rec["gate"]["G"]:
        rec["grades"] = GRADERS[kind](samples)
        rec["held"] = sorted(k for k, v in rec["grades"].items() if v.get("held") is True)
        rec["failed"] = sorted(k for k, v in rec["grades"].items() if v.get("held") is False)
    else:
        rec["grades"], rec["held"], rec["failed"] = None, [], []
    rec["descriptive"] = descriptive(samples)
    rec["lookups_exploratory"] = lookups(samples)
    rec["d_suffix"] = dup_suffix(samples)
    if kind == "fum1218":
        rec["names"] = names_b(samples)
    with open(os.path.join(out_dir, f"fumonisin_{kind}_record.json"), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True, ensure_ascii=False)
    write_csv(os.path.join(out_dir, f"fumonisin_{kind}_samples.csv"), samples, kind)
    print(json.dumps({"file": kind,
                      "gate": {k: v for k, v in rec["gate"].items() if k != "problems"},
                      "problems": {k: len(v) for k, v in problems.items()},
                      "held": rec["held"], "failed": rec["failed"]}))
    for k, v in (rec["grades"] or {}).items():
        print(k, {True: "HELD", False: "FAILED", None: "NOT GRADED"}[v.get("held")],
              json.dumps(v.get("checks") or v.get("status")))
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade CFIA's 2010-11, 2011-12 and 2012-2018 "
                                             "fumonisin files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    for kind in ("fum10", "fum11", "fum1218"):
        run(kind, args.data_dir, args.out_dir)
    print("GRADE-DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
