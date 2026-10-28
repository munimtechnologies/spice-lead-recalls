#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""aflatoxin-figs-2009 0.1.0: CFIA's open 2009-10 file of aflatoxins in dried figs and dried
dates, against its summary page and the EU's current maximum levels for dried figs.

Grades docs/aflatoxin-figs-2009-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim,
Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes a per-sample file, "2009-2010 Aflatoxin in
Dried Figs and Dried Dates" (AF; 500 rows, five rows per sample: aflatoxins B1, B2, G1, G2 and
"Total Aflatoxins"), on open.canada.ca (Open Government Licence - Canada). Its only public report
is a summary page (100 samples, "49 dried dates, 51 dried figs"; no aflatoxin in any date; four
figs at 7.5 to 78.7 ppb); the full report is available only on request. This reads the result
column for the first time to (a) check the printed figures, (b) test whether "Total Aflatoxins"
is the sum of the four forms, and (c) test blind predictions on which forms and which declared
origins carry the positives, and on how many positives exceed the EU's maximum levels for dried
figs now in force (Regulation (EU) 2023/915: aflatoxin B1 6.0 ug/kg, sum of B1, B2, G1 and G2
10.0 ug/kg; a reference comparison only).

The file is SHA-256 pinned. Value rule (registered): a cell that parses as a number above 0 is a
positive; a literal 0 is a non-detect; any other cell (blank, text, negative, non-finite) fails
the gate. Units go through an explicit table. Standard library only. Code Apache-2.0; derived
data CC BY 4.0. A reference comparison, not a compliance finding (Canada sets no aflatoxin
maximum level for dried fruit), not about any brand, and not individual dietary or medical
advice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

VERSION = "0.1.0"

AF = {
    "key": "AF",
    "dataset": "bfac4a9d-ba2f-433a-8425-9b2fc7689d72",
    "resource": "8339ffec-f854-430c-b3c8-4718e18ed4b2",
    "filename": ("1549-chem_ts_2009-2010_aflatoxin_in_dried_figs_and_dried_dates_open_data_"
                 "portal_excel.csv"),
    "sha256": "5d3300b7de8ab2b5a324bb8aee77ccde0ab497471693c1b44f131806b9bb055d",
    "rows": 500, "samples": 100,
}
FORMS = ("Aflatoxin B1", "Aflatoxin B2", "Aflatoxin G1", "Aflatoxin G2")
B1, G1 = FORMS[0], FORMS[2]
TOTAL = "Total Aflatoxins"
COMPONENTS = FORMS + (TOTAL,)

# Census facts (names-only census, job myco-census-v2, 2026-10-25): row counts per label.
PRODUCT_ROWS = {"DATE": 250, "FIG": 250}
ORIGIN_ROWS = {"IRAN": 100, "TURKEY": 100, "UNITED STATES": 100, "GREECE": 75, "CHINA": 30,
               "TUNISIA": 25, "UNKNOWN": 25, "SAUDI ARABIA": 15, "ALGERIA": 10, "FRANCE": 10,
               "ITALY": 10}
NONZERO_CELLS = 14

# Units -> factor to ug/kg (= ppb). Keys are lower-cased.
UNIT_FACTORS = {"ppb": 1.0, "ng/g": 1.0, "µg/kg": 1.0, "μg/kg": 1.0, "ug/kg": 1.0,
                "ppm": 1000.0, "mg/kg": 1000.0, "µg/g": 1000.0, "μg/g": 1000.0, "ug/g": 1000.0}

# Registered thresholds.
C1_FIG_POS, C1_DATE_POS = 4, 0
C2_MIN, C2_MAX = "7.5", "78.7"          # printed range of the positive figs
P1_TOL = 0.25                           # |Total - (B1 + B2 + G1 + G2)| allowed, ppb
P3_MIN = 3                              # positives whose largest form is B1
P4_ORIGIN, P4_MIN = "TURKEY", 2
EU_B1, EU_SUM = 6.0, 10.0               # EU 2023/915, dried figs
P5_MIN = 3                              # positives above at least one EU level
P6_MIN = 2                              # positives with aflatoxin G1 detected


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
        "value": first(lambda c: c.startswith("Result"), "value"),
        "unit": first(lambda c: c.startswith("Unit"), "unit"),
        "function": optional(lambda c: c == "Function"),
        "region": optional(lambda c: c.startswith("Region")),
        "date": optional(lambda c: c.startswith("Date Sampled")),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def parse_text(text):
    """(samples, census) from one decoded CSV. samples: {id: record}."""
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
    samples = {}
    nonzero = 0
    for r in body:
        sid = clean(cell(r, "sample"))
        comp = clean(cell(r, "component"))
        product = clean(cell(r, "product"))
        origin = clean(cell(r, "origin"))
        unit = clean(cell(r, "unit"))
        value, det, kind = parse_amount(cell(r, "value"))
        factor = UNIT_FACTORS.get(unit.lower())
        _bump(comps, comp)
        _bump(kinds, kind)
        _bump(units, unit)
        _bump(products, product)
        _bump(origins, origin)
        _bump(functions, clean(cell(r, "function")))
        if kind == "pos":
            nonzero += 1
        rec = samples.get(sid)
        if rec is None:
            rec = samples[sid] = {"sample": sid, "product": product, "origin": origin,
                                  "region": clean(cell(r, "region")),
                                  "date": clean(cell(r, "date")),
                                  "values": {}, "rows": 0, "duplicate": False,
                                  "mixed_labels": False}
        rec["rows"] += 1
        if (product, origin) != (rec["product"], rec["origin"]):
            rec["mixed_labels"] = True
        if comp in rec["values"]:
            rec["duplicate"] = True
        ppb = value * factor if (det and value is not None and factor is not None) else 0.0
        rec["values"][comp] = ppb
    rps = {}
    for rec in samples.values():
        _bump(rps, str(rec["rows"]))
    census = {"n_rows": len(body), "distinct_samples": len(samples), "components": comps,
              "products": products, "origins": origins, "functions": functions, "units": units,
              "value_kinds": kinds, "nonzero_cells": nonzero, "rows_per_sample": rps}
    return samples, census


def is_positive(rec):
    return any(v > 0 for v in rec["values"].values())


def form_sum(rec):
    return sum(rec["values"].get(f, 0.0) for f in FORMS)


def largest_form(rec):
    """The form with the largest value; B1 wins ties."""
    best = B1
    for f in FORMS:
        if rec["values"].get(f, 0.0) > rec["values"].get(best, 0.0):
            best = f
    return best


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def eu_flags(rec):
    b1, s = rec["values"].get(B1, 0.0), form_sum(rec)
    return {"over_b1": b1 > EU_B1 + 1e-9, "over_sum": s > EU_SUM + 1e-9}


# ---------------------------------------------------------------------------
# Gate, analysis and grading.
# ---------------------------------------------------------------------------
def gate_checks(census, recs, sha_ok):
    return {
        "sha256": bool(sha_ok),
        "rows": census["n_rows"] == AF["rows"],
        "samples": census["distinct_samples"] == AF["samples"],
        "rows_per_sample": census["rows_per_sample"] == {"5": AF["samples"]},
        "components": census["components"] == {c: AF["samples"] for c in COMPONENTS},
        "one_row_per_component": all(not r["duplicate"] and set(r["values"]) == set(COMPONENTS)
                                     for r in recs),
        "labels_per_sample": all(not r["mixed_labels"] for r in recs),
        "products": census["products"] == PRODUCT_ROWS,
        "origins": census["origins"] == ORIGIN_ROWS,
        "unit": (len(census["units"]) == 1
                 and all(u.lower() in UNIT_FACTORS for u in census["units"])),
        "value_kinds": set(census["value_kinds"]) == {"pos", "zero"},
        "nonzero_cells": census["nonzero_cells"] == NONZERO_CELLS,
    }


def analyse(recs):
    by_product = {}
    for p in sorted({r["product"] for r in recs}):
        rs = [r for r in recs if r["product"] == p]
        by_product[p] = {"n": len(rs), "pos": sum(1 for r in rs if is_positive(r))}
    product_origin = {}
    for r in recs:
        _bump(product_origin, f"{r['product']}|{r['origin']}")
    positives = []
    for r in sorted((r for r in recs if is_positive(r)),
                    key=lambda r: (-r["values"].get(TOTAL, 0.0), r["sample"])):
        v = r["values"]
        positives.append({"sample": r["sample"], "product": r["product"], "origin": r["origin"],
                          "region": r["region"], "date": r["date"],
                          "b1": v.get(B1, 0.0), "b2": v.get(FORMS[1], 0.0),
                          "g1": v.get(G1, 0.0), "g2": v.get(FORMS[3], 0.0),
                          "total": v.get(TOTAL, 0.0), "form_sum": form_sum(r),
                          "largest": largest_form(r), **eu_flags(r)})
    gaps = [abs(r["values"].get(TOTAL, 0.0) - form_sum(r)) for r in recs]
    totals = [p["total"] for p in positives if p["total"] > 0]
    return {
        "by_product": by_product, "product_origin": product_origin, "positives": positives,
        "n_positive": len(positives),
        "fig_pos": sum(1 for p in positives if p["product"] == "FIG"),
        "date_pos": sum(1 for p in positives if p["product"] == "DATE"),
        "total_min": min(totals) if totals else None,
        "total_max": max(totals) if totals else None,
        "max_sum_gap": max(gaps) if gaps else None,
        "b1_in_all": bool(positives) and all(p["b1"] > 0 for p in positives),
        "b1_largest": sum(1 for p in positives if p["largest"] == B1),
        "origin_hits": sum(1 for p in positives if p["origin"] == P4_ORIGIN),
        "eu_any": sum(1 for p in positives if p["over_b1"] or p["over_sum"]),
        "eu_b1": sum(1 for p in positives if p["over_b1"]),
        "eu_sum": sum(1 for p in positives if p["over_sum"]),
        "g1_pos": sum(1 for p in positives if p["g1"] > 0),
    }


def grade(a, gate_obs):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "SHA-256; 500 rows, 100 samples, five rows each (B1, B2, G1, G2, Total "
                      "Aflatoxins) with one product and origin per sample; product and origin "
                      "row counts; one known unit; every cell a number above 0 or a literal 0 "
                      "(both present); exactly 14 non-zero cells"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    add("C1", "consistency",
        "the summary page: no dried date carries aflatoxin and four dried figs do",
        {"fig_pos": a["fig_pos"], "date_pos": a["date_pos"], "by_product": a["by_product"]},
        a["fig_pos"] == C1_FIG_POS and a["date_pos"] == C1_DATE_POS)
    add("C2", "consistency",
        "the summary page: the positive figs range from 7.5 to 78.7 ppb (Total Aflatoxins)",
        {"total_min": a["total_min"], "total_max": a["total_max"]},
        matches(a["total_min"], C2_MIN) and matches(a["total_max"], C2_MAX))
    add("P1", "prediction",
        "in every sample, Total Aflatoxins equals B1 + B2 + G1 + G2 within 0.25 ppb",
        {"max_sum_gap": a["max_sum_gap"]},
        a["max_sum_gap"] is not None and a["max_sum_gap"] <= P1_TOL + 1e-9)
    add("P2", "prediction", "aflatoxin B1 is detected in every positive sample",
        {"b1": [p["b1"] for p in a["positives"]]}, a["b1_in_all"])
    add("P3", "prediction", "B1 is the largest single form in at least 3 positive samples",
        {"b1_largest": a["b1_largest"], "largest": [p["largest"] for p in a["positives"]]},
        a["b1_largest"] >= P3_MIN)
    add("P4", "prediction", "at least 2 positive samples declare Turkey as origin",
        {"origin_hits": a["origin_hits"], "origins": [p["origin"] for p in a["positives"]]},
        a["origin_hits"] >= P4_MIN)
    add("P5", "prediction",
        "at least 3 positive samples exceed at least one EU level for dried figs now in force "
        "(B1 > 6.0 or B1 + B2 + G1 + G2 > 10.0 ug/kg)",
        {"eu_any": a["eu_any"], "eu_b1": a["eu_b1"], "eu_sum": a["eu_sum"]},
        a["eu_any"] >= P5_MIN)
    add("P6", "prediction", "aflatoxin G1 is detected in at least 2 positive samples",
        {"g1_pos": a["g1_pos"], "g1": [p["g1"] for p in a["positives"]]},
        a["g1_pos"] >= P6_MIN)
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
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-aflatoxin-figs-2009"})
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


def write_outputs(out_dir, recs, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "aflatoxin_figs_2009_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "origin", "region", "date", "b1", "b2", "g1", "g2",
                    "total"])
        for r in sorted(recs, key=lambda x: x["sample"]):
            v = r["values"]
            w.writerow([r["sample"], r["product"], r["origin"], r["region"], r["date"]]
                       + [repr(v.get(c, 0.0)) for c in COMPONENTS])
    result = {"study": "aflatoxin-figs-2009", "version": VERSION, "predictions": preds,
              "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "aflatoxin_figs_2009_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the aflatoxin-figs-2009 0.1.0 "
                                             "pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw, src = load(AF, args.data_dir)
    text, enc = decode(raw)
    samples, census = parse_text(text)
    recs = list(samples.values())
    gate_obs = gate_checks(census, recs, _sha(raw) == AF["sha256"])
    a = analyse(recs)
    preds = grade(a, gate_obs)
    provenance = {"AF": {"resource": AF["resource"], "sha256": AF["sha256"], "bytes": len(raw),
                         "source": src, "encoding": enc}}
    result = write_outputs(args.out_dir, recs, census, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate_obs, "units": census["units"],
                      "value_kinds": census["value_kinds"],
                      "nonzero_cells": census["nonzero_cells"],
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
