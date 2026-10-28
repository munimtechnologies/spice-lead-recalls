#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""don-grains-2015 0.1.0: CFIA's open 2015-16 deoxynivalenol file for grains, pseudo-cereals
and pulses, against its summary page, and against the 2018-19 multi-mycotoxin survey on the
product labels both share.

Grades docs/don-grains-2015-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

The Canadian Food Inspection Agency (CFIA) publishes a per-sample file, "CFIA 2015/2016
Deoxynivalenol in Selected Foods Data" (DG; 997 rows, one deoxynivalenol (DON) result per
sample), on open.canada.ca (Open Government Licence - Canada). Its only public report is a
summary page ("2015-2016 Deoxynivalenol in Selected Grains and Pulses": 997 products, DON
detected in 46%); the full report is available only on request. This reads the result column
for the first time to (a) check the two printed figures, (b) test blind predictions on how DON
splits between small-grain cereals, pseudo-cereals and pulses, and on how many samples reach
the EU's 2024 DON maximum levels (a reference comparison only), and (c) compare DON detection
on the 18 product labels DG shares with CFIA's 2018-19 multi-mycotoxin file (MM, already graded
in multimyco-2018 0.1.0), at each method's own limit and at MM's 10 ppb limit of detection.

Both files are SHA-256 pinned. Value rule (registered): a cell that parses as a number above 0
is a positive; a literal 0 is a non-detect; any other cell (blank, text, negative, non-finite)
fails the gate. Units go through an explicit table. Standard library only. Code Apache-2.0;
derived data CC BY 4.0. A reference comparison, not a compliance finding (Canada sets no DON
maximum level for these finished foods), not about any brand, and not individual dietary or
medical advice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import statistics
import sys
import time
import urllib.request

VERSION = "0.1.0"

DG = {
    "key": "DG",
    "dataset": "debeebfe-8e35-4914-8ad5-8432340e1e5a",
    "resource": "90b59896-d874-4da5-9c03-580d7ee6c584",
    "filename": ("2015-2016_deoxynivalenol_in_selected_foods_-_2015-2016_donnees_de_"
                 "deoxynivalenol_dans_certains_a.csv"),
    "sha256": "b662d980c6f25d5e3e4814b47c1c1fcb61773aeffa83a8c0fe8ccf62be4912d7",
    "rows": 997, "samples": 997,
}
MM = {
    "key": "MM",
    "dataset": "03f184ee-e5e0-4e33-a763-fa3e44ed2dc0",
    "resource": "09a3c285-8552-4a38-b4be-cdf6d5fc3fd2",
    "filename": ("cfia_acia-1134_2018-19_multi-mycotoxins_in_selected_foods_-_2019-2019_"
                 "presence-de-plusieurs-myco.csv"),
    "sha256": "ba5084945f0a0e1fab2b8bab7f8f196a7dd0033d4bdc4e80768f12ec4c553835",
    "rows": 18750, "samples": 750,
}
DON = "Deoxynivalenol"

# Registered label groups (each DG label in exactly one; counts from the names-only census,
# job myco-census-v2, 2026-10-25).
GROUPS = {
    # small-grain cereals: barley, rye and the wheat species kamut (khorasan) and spelt
    "SG": {"Grain - Barley": 51, "Barley Products": 46, "Grain - Rye": 44, "Rye Products": 40,
           "Flour - rye": 6, "Grain - Kamut": 52, "Kamut Products": 41, "Spelt": 44,
           "Spelt Products": 29},
    # pseudo-cereals and arrowroot (not grasses)
    "PS": {"Grain - Buckwheat": 44, "Buckwheat Products": 46, "Grain - Quinoa": 45,
           "Quinoa Products": 37, "Amaranth Products": 41, "Arrowroot Products": 39},
    # other grains: millet, teff and CFIA's catch-all grain and flour labels
    "OG": {"Millet": 45, "Millet Products": 39, "Teff Products": 26, "Grain - Other": 45,
           "Flour - Other": 42},
    # pulses and soy
    "PU": {"Bean - Black": 8, "Bean - Fava": 8, "Bean - Kidney": 8, "Bean - Lima": 8,
           "Bean - Pinto": 8, "Bean - Soy": 8, "Bean - Other": 12, "Bean Products": 8,
           "Beverage - Soy": 8, "Chickpea": 8, "Chickpea Products": 8, "Flour - Bean": 8,
           "Flour - Chickpea": 8, "Flour - Lentil": 8, "Flour - Pea": 8, "Flour - Soy": 8,
           "Infant Formula - Soy": 8, "Lentil": 8, "Lentil Products": 8, "Pea": 8,
           "Pea Products": 8, "Soy Products": 8, "Tofu": 9},
    # meat alternatives (may contain wheat gluten), reported alone
    "MA": {"Meat Alternative": 6},
}
DG_PRODUCT_ROWS = {lab: n for g in GROUPS.values() for lab, n in g.items()}
GRAIN_GROUPS = ("SG", "PS", "OG")
DG_ORIGIN_FACTS = {"CANADA": 254, "UNKNOWN": 407}
# MM facts already published (multimyco-2018 0.1.0 result and detail listing).
MM_DON_POS, MM_DON_MIN = 306, 10.0
SHARED_LABELS = ["Amaranth Products", "Arrowroot Products", "Barley Products",
                 "Buckwheat Products", "Grain - Barley", "Grain - Buckwheat", "Grain - Kamut",
                 "Grain - Other", "Grain - Quinoa", "Grain - Rye", "Kamut Products", "Millet",
                 "Millet Products", "Quinoa Products", "Rye Products", "Spelt",
                 "Spelt Products", "Teff Products"]

# Units -> factor to ng/g (= ug/kg = ppb). Keys are lower-cased.
UNIT_FACTORS = {"ng/g": 1.0, "ppb": 1.0, "µg/kg": 1.0, "μg/kg": 1.0, "ug/kg": 1.0,
                "ppm": 1000.0, "µg/g": 1000.0, "μg/g": 1000.0, "ug/g": 1000.0,
                "mg/kg": 1000.0}

# Registered thresholds.
CUT = 10.0                     # MM's DON limit of detection (CFIA 2015-18 report, Table A1)
C1_POS = (454, 463)            # the only counts that round half up to 46% of 997
P1_MAX_SHARE, P1_LEVEL = 0.15, 100.0
P2_RATIO = 2.0
P3_SG_MIN = 0.60
P4_MAX = 2000.0
EU_HIGH, EU_LOW = 750.0, 400.0          # EU 2023/915 as amended by 2024/1022, rows 1.4.4 / 1.4.7
P5_HIGH_MAX, P5_LOW_MAX = 16, 40
P6_OR_MIN, P6_ALPHA, P6_BELOW_CUT_SHARE = 2.0, 0.05, 0.25
P7_BAND = (0.5, 2.0)


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def parse_amount(raw):
    """(value, detected, kind) for one result cell under the registered rule.

    kind is one of: blank, text, zero, bad, pos. Only zero and pos pass the gate."""
    s = (raw or "").strip()
    if s == "":
        return 0.0, False, "blank"
    try:
        v = float(s)
    except ValueError:
        return 0.0, False, "text"
    if v != v or v < 0 or v == float("inf"):
        return None, False, "bad"
    if v == 0:
        return 0.0, False, "zero"
    return v, True, "pos"


def clean(cell):
    return (cell or "").replace("﻿", "").strip()


def find_columns(header):
    h = [clean(c) for c in header]

    def first(test, what):
        for i, c in enumerate(h):
            if test(c):
                return i
        raise ValueError(f"no {what} column in {header!r}")

    def optional(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    return {
        "sample": first(lambda c: c.startswith("Sample"), "sample"),
        "origin": first(lambda c: c == "Origin", "origin"),
        "product": first(lambda c: c == "Product", "product"),
        "component": first(lambda c: c == "Component", "component"),
        "value": first(lambda c: c.startswith("Result") or c == "AMOUNT", "value"),
        "unit": first(lambda c: c.startswith("Unit") or c.startswith("Report Unit")
                      or c == "ReportUnit", "unit"),
        "function": optional(lambda c: c == "Function"),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def group_of(product):
    for name, labels in GROUPS.items():
        if product in labels:
            return name
    return "none"


def parse_text(text, only_component=None):
    """(samples, census) from one decoded CSV. samples: {id: record}.

    With only_component, rows of other components are counted in the census and skipped."""
    table = list(csv.reader(io.StringIO(text)))
    header = table[0]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    col = find_columns(header)

    def cell(r, k):
        i = col[k]
        if i is None:
            return ""
        return r[i] if i < len(r) else ""

    comps, kinds, units, products, origins, functions = {}, {}, {}, {}, {}, {}
    per_sample_rows = {}
    samples = {}
    n_rows = 0
    for r in body:
        n_rows += 1
        comp = clean(cell(r, "component"))
        _bump(comps, comp)
        if only_component is not None and comp != only_component:
            continue
        sid = clean(cell(r, "sample"))
        product = clean(cell(r, "product"))
        origin = clean(cell(r, "origin"))
        function = clean(cell(r, "function"))
        unit = clean(cell(r, "unit"))
        value, det, kind = parse_amount(cell(r, "value"))
        factor = UNIT_FACTORS.get(unit.lower())
        _bump(kinds, kind)
        _bump(units, unit)
        _bump(products, product)
        _bump(origins, origin)
        _bump(functions, function)
        _bump(per_sample_rows, sid)
        ppb = value * factor if (value is not None and factor is not None) else None
        samples[sid] = {"sample": sid, "product": product, "origin": origin,
                        "function": function, "group": group_of(product),
                        "don": ppb if det and ppb is not None else 0.0,
                        "detected": bool(det and ppb is not None), "kind": kind}
    rps = {}
    for v in per_sample_rows.values():
        _bump(rps, str(v))
    census = {"n_rows": n_rows, "n_selected_rows": sum(per_sample_rows.values()),
              "distinct_samples": len(samples), "components": comps, "products": products,
              "origins": origins, "functions": functions, "units": units,
              "value_kinds": kinds, "rows_per_sample": rps}
    return samples, census


def positives(recs):
    return [r["don"] for r in recs if r["detected"]]


def row_stats(recs):
    pos = positives(recs)
    return {"n": len(recs), "pos": len(pos),
            "rate": len(pos) / len(recs) if recs else None,
            "min": min(pos) if pos else None,
            "max": max(pos) if pos else None,
            "avg": statistics.fmean(pos) if pos else None,
            "median": statistics.median(pos) if pos else None,
            "below_cut": sum(1 for v in pos if v < CUT - 1e-9),
            "ge_cut": sum(1 for v in pos if v >= CUT - 1e-9),
            "ge_400": sum(1 for v in pos if v >= EU_LOW - 1e-9),
            "ge_750": sum(1 for v in pos if v >= EU_HIGH - 1e-9)}


def select(recs, labels):
    ls = set(labels)
    return [r for r in recs if r["product"] in ls]


def percent(pos, n):
    """Percent positive rounded half up to a whole number, as printed."""
    return int(100 * pos / n + 0.5) if n else None


def mh_or(tabs):
    num = sum(a * d / (a + b + c + d) for a, b, c, d in tabs if a + b + c + d > 0)
    den = sum(b * c / (a + b + c + d) for a, b, c, d in tabs if a + b + c + d > 0)
    return num / den if den > 0 else None


def cmh(tabs):
    """Continuity-corrected Cochran-Mantel-Haenszel chi-square (1 df) and two-sided p."""
    diff = var = 0.0
    for a, b, c, d in tabs:
        n = a + b + c + d
        if n < 2:
            continue
        diff += a - (a + b) * (a + c) / n
        var += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    if var <= 0:
        return 0.0, 1.0
    chi2 = max(0.0, abs(diff) - 0.5) ** 2 / var
    return chi2, math.erfc(math.sqrt(chi2 / 2))


def cross_tables(dg, mm, labels, at_cut=True):
    """{label: (DG hit, DG miss, MM hit, MM miss)}; a hit is a positive (at or above CUT)."""
    def hit(r):
        return r["detected"] and (not at_cut or r["don"] >= CUT - 1e-9)

    out = {}
    for lab in labels:
        a_recs, m_recs = select(dg, (lab,)), select(mm, (lab,))
        a = sum(1 for r in a_recs if hit(r))
        c = sum(1 for r in m_recs if hit(r))
        out[lab] = (a, len(a_recs) - a, c, len(m_recs) - c)
    return out


# ---------------------------------------------------------------------------
# Gate, analysis and grading.
# ---------------------------------------------------------------------------
def gate_checks(c_dg, c_mm, dg, mm, sha_dg_ok, sha_mm_ok):
    unit_ok = (len(c_dg["units"]) == 1
               and all(u.lower() in UNIT_FACTORS for u in c_dg["units"]))
    mm_unit_ok = (len(c_mm["units"]) >= 1
                  and all(u.lower() in UNIT_FACTORS for u in c_mm["units"]))
    mm_pos = positives(mm)
    shared = sorted(set(c_dg["products"]) & set(c_mm["products"]))
    return {
        "dg_sha256": bool(sha_dg_ok),
        "dg_rows": c_dg["n_rows"] == DG["rows"],
        "dg_samples": c_dg["distinct_samples"] == DG["samples"],
        "dg_rows_per_sample": c_dg["rows_per_sample"] == {"1": DG["samples"]},
        "dg_component": c_dg["components"] == {DON: DG["rows"]},
        "dg_products": c_dg["products"] == DG_PRODUCT_ROWS,
        "dg_origins": all(c_dg["origins"].get(k) == v for k, v in DG_ORIGIN_FACTS.items()),
        "dg_unit": unit_ok,
        "dg_value_kinds": (set(c_dg["value_kinds"]) == {"pos", "zero"}),
        "mm_sha256": bool(sha_mm_ok),
        "mm_rows": c_mm["n_rows"] == MM["rows"],
        "mm_don_samples": (c_mm["distinct_samples"] == MM["samples"]
                           and c_mm["rows_per_sample"] == {"1": MM["samples"]}),
        "mm_don_kinds": (set(c_mm["value_kinds"]) <= {"pos", "zero"}
                         and c_mm["value_kinds"].get("pos") == MM_DON_POS),
        "mm_unit": mm_unit_ok,
        "mm_don_min": bool(mm_pos) and abs(min(mm_pos) - MM_DON_MIN) < 1e-9,
        "shared_labels": shared == SHARED_LABELS,
    }


def analyse(dg, mm):
    groups = {g: row_stats([r for r in dg if r["group"] == g]) for g in GROUPS}
    grains = [r for r in dg if r["group"] in GRAIN_GROUPS]
    labels = {lab: row_stats(select(dg, (lab,))) for lab in sorted({r["product"] for r in dg})}
    overall = row_stats(dg)
    top = max((r for r in dg if r["detected"]), key=lambda r: r["don"], default=None)
    top10 = sorted(({"sample": r["sample"], "product": r["product"], "group": r["group"],
                     "don": r["don"]} for r in dg if r["detected"]),
                   key=lambda x: -x["don"])[:10]
    pulses_pos = sorted(({"sample": r["sample"], "product": r["product"], "don": r["don"]}
                         for r in dg if r["group"] == "PU" and r["detected"]),
                        key=lambda x: -x["don"])
    by_function = {}
    for g in GRAIN_GROUPS:
        for f in sorted({r["function"] for r in dg}):
            by_function[f"{g}|{f}"] = row_stats([r for r in dg
                                                 if r["group"] == g and r["function"] == f])

    cut_tabs = cross_tables(dg, mm, SHARED_LABELS, at_cut=True)
    own_tabs = cross_tables(dg, mm, SHARED_LABELS, at_cut=False)
    cut_chi2, cut_p = cmh(list(cut_tabs.values()))
    own_chi2, own_p = cmh(list(own_tabs.values()))
    shared_dg = row_stats(select(dg, SHARED_LABELS))

    def pooled(tabs):
        return [sum(t[i] for t in tabs.values()) for i in range(4)]

    return {
        "overall": overall, "groups": groups, "grains": row_stats(grains), "labels": labels,
        "max_sample": ({"sample": top["sample"], "product": top["product"],
                        "group": top["group"], "don": top["don"]} if top else None),
        "top10": top10, "pulses_positive": pulses_pos, "by_function": by_function,
        "shared_dg": shared_dg,
        "cross": {
            "cut_ppb": CUT, "labels": SHARED_LABELS,
            "at_cut": {k: list(v) for k, v in cut_tabs.items()},
            "own_limits": {k: list(v) for k, v in own_tabs.items()},
            "at_cut_pooled": pooled(cut_tabs), "own_pooled": pooled(own_tabs),
            "at_cut_mh_or": mh_or(list(cut_tabs.values())),
            "at_cut_cmh_chi2": cut_chi2, "at_cut_cmh_p": cut_p,
            "own_mh_or": mh_or(list(own_tabs.values())),
            "own_cmh_chi2": own_chi2, "own_cmh_p": own_p,
        },
    }


def grade(a, gate_obs):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "DG: SHA-256, 997 rows and samples, one DON row each, all 44 product-label "
                      "counts, origin facts, one known unit, every cell a number above 0 or a "
                      "literal 0 (both present); MM: SHA-256, rows, 750 DON rows, 306 DON "
                      "positives, minimum 10, known units; the 18 shared product labels"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    ov = a["overall"]
    add("C1", "consistency",
        "the summary page: 997 products, DON detected in 46% (454-463 positives)",
        {"n": ov["n"], "pos": ov["pos"], "pct": percent(ov["pos"], ov["n"])},
        ov["n"] == 997 and C1_POS[0] <= ov["pos"] <= C1_POS[1])

    pu = a["groups"]["PU"]
    add("P1", "prediction",
        "pulses and soy (189): DON detected in at most 15%, and none at or above 100 ppb",
        pu, pu["pos"] <= P1_MAX_SHARE * pu["n"]
        and (pu["max"] is None or pu["max"] < P1_LEVEL))

    sg, ps = a["groups"]["SG"], a["groups"]["PS"]
    add("P2", "prediction",
        "small-grain cereals (353) are DON-positive at least twice as often as pseudo-cereals "
        "and arrowroot (252)",
        {"SG": sg, "PS": ps},
        sg["rate"] is not None and ps["rate"] is not None
        and sg["rate"] >= P2_RATIO * ps["rate"])

    add("P3", "prediction", "at least 60% of the 353 small-grain cereal samples are DON-positive",
        sg, sg["rate"] is not None and sg["rate"] >= P3_SG_MIN)

    mx = a["max_sample"]
    add("P4", "prediction",
        "the file's highest DON result is in a small-grain cereal label and below 2,000 ppb",
        mx, mx is not None and mx["group"] == "SG" and mx["don"] < P4_MAX)

    gr = a["grains"]
    add("P5", "prediction",
        "of the 802 grain-type samples (SG, PS, OG), at most 16 are at or above 750 ppb and at "
        "most 40 at or above 400 ppb",
        gr, gr["ge_750"] <= P5_HIGH_MAX and gr["ge_400"] <= P5_LOW_MAX)

    cr = a["cross"]
    sh = a["shared_dg"]
    add("P6", "prediction",
        "on the 18 shared labels, at each method's own limit, DG detects DON more often than "
        "MM (MH OR >= 2 and CMH p < 0.05), and at least 25% of DG's positives on those labels "
        "are below 10 ppb",
        {"own_pooled": cr["own_pooled"], "own_mh_or": cr["own_mh_or"],
         "own_cmh_chi2": cr["own_cmh_chi2"], "own_cmh_p": cr["own_cmh_p"],
         "shared_pos": sh["pos"], "shared_below_cut": sh["below_cut"]},
        cr["own_mh_or"] is not None and cr["own_mh_or"] >= P6_OR_MIN
        and cr["own_cmh_p"] < P6_ALPHA and sh["pos"] > 0
        and sh["below_cut"] >= P6_BELOW_CUT_SHARE * sh["pos"])

    add("P7", "prediction",
        "on the 18 shared labels, at a common 10 ppb cut, the MH odds ratio (DG vs MM) is "
        "between 0.5 and 2.0",
        {k: cr[k] for k in ("at_cut", "at_cut_pooled", "at_cut_mh_or", "at_cut_cmh_chi2",
                            "at_cut_cmh_p")},
        cr["at_cut_mh_or"] is not None and P7_BAND[0] <= cr["at_cut_mh_or"] <= P7_BAND[1])
    return preds


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-don-grains-2015"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(spec, data_dir):
    path = os.path.join(data_dir, spec["resource"] + ".csv") if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == spec["sha256"]:
            return raw, "data-volume"
    base = f"/data/dataset/{spec['dataset']}/resource/{spec['resource']}/download/{spec['filename']}"
    errors = []
    for host in ("https://open.canada.ca", "https://ouvert.canada.ca"):
        url = host + base
        try:
            raw = _fetch(url)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        if _sha(raw) != spec["sha256"]:
            errors.append(f"{url}: SHA-256 {_sha(raw)} != {spec['sha256']}")
            continue
        if path:
            try:
                os.makedirs(data_dir, exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(raw)
            except OSError:
                pass
        return raw, url
    raise RuntimeError(f"{spec['key']}: no verified copy: " + "; ".join(errors))


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
    if isinstance(x, set):
        return sorted(x)
    return "" if x is None else (round(x, 6) if isinstance(x, float) else x)


def write_outputs(out_dir, dg, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "don_grains_2015_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "group", "origin", "function", "detected", "don_ng_g"])
        for r in sorted(dg, key=lambda x: x["sample"]):
            w.writerow([r["sample"], r["product"], r["group"], r["origin"], r["function"],
                        1 if r["detected"] else 0, repr(r["don"])])
    with open(os.path.join(out_dir, "don_grains_2015_crossmethod.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "dg_n", "dg_detected", "dg_ge_10", "mm_n", "mm_detected"])
        for lab in SHARED_LABELS:
            cut, own = a["cross"]["at_cut"][lab], a["cross"]["own_limits"][lab]
            w.writerow([lab, own[0] + own[1], own[0], cut[0], own[2] + own[3], own[2]])
    result = {"study": "don-grains-2015", "version": VERSION, "predictions": preds,
              "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "don_grains_2015_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the don-grains-2015 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw_dg, src_dg = load(DG, args.data_dir)
    raw_mm, src_mm = load(MM, args.data_dir)
    text_dg, enc_dg = decode(raw_dg)
    text_mm, enc_mm = decode(raw_mm)
    s_dg, c_dg = parse_text(text_dg)
    s_mm, c_mm = parse_text(text_mm, only_component=DON)
    dg, mm = list(s_dg.values()), list(s_mm.values())
    gate_obs = gate_checks(c_dg, c_mm, dg, mm, _sha(raw_dg) == DG["sha256"],
                           _sha(raw_mm) == MM["sha256"])
    a = analyse(dg, mm)
    preds = grade(a, gate_obs)
    provenance = {
        "DG": {"resource": DG["resource"], "sha256": DG["sha256"], "bytes": len(raw_dg),
               "source": src_dg, "encoding": enc_dg},
        "MM": {"resource": MM["resource"], "sha256": MM["sha256"], "bytes": len(raw_mm),
               "source": src_mm, "encoding": enc_mm},
    }
    result = write_outputs(args.out_dir, dg, {"DG": c_dg, "MM": c_mm}, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate_obs,
                      "dg_units": c_dg["units"], "dg_value_kinds": c_dg["value_kinds"],
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
