#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""coumarin_cfia_table_audit 0.1.0: do CFIA's published coumarin summary tables match CFIA's own
open per-sample files?

Grades docs/coumarin-cfia-table-audit-0.1.0-prereg.md. Made with AI agents working in MV2's
(Munim, Inc.) name.

Table 2 of CFIA's 2014-15 and 2015-16 coumarin survey reports gives, per product type, the number
of samples, the number with detected coumarin, the minimum, the maximum and an average that a
table note says uses "only positive results". This tool rebuilds every row from the open files
(Open Government Licence - Canada), SHA-256 pinned and parsed by coumarin_eu_limits 0.1.1, and
asks which mean each printed average equals at its printed precision: the mean of the detected
samples (as footnoted), the mean of all samples with non-detects as 0, both (when every sample is
detected) or neither. Aggregate statistics only; no per-sample values are written.

Code Apache-2.0; derived data CC BY 4.0. An audit of published summary statistics, not a
finding about any product, brand or health risk.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys

import coumarin_eu_limits as cel
import coumarin_tea_replication as ctr

VERSION = "0.1.0"

TEA = ctr.TEA_TYPES

# CFIA Table 2 rows: (row name, Product labels in the open file, n, n detected, min, max, printed
# average as text so its precision is known). Labels come from a names-only census of each file.
TABLES = {
    "2014-15": {
        "report": ("https://inspection.canada.ca/food-safety-for-industry/food-chemistry-and-"
                   "microbiology/food-safety-testing-bulletin-and-reports/coumarin-in-cinnamon-"
                   "containing-foods-and-vanilla-/eng/1560182443441/1560182514985"),
        "rows": [
            ("Cooking sauces", ("Sauces",), 148, 125, "0.2", "50", "4.7"),
            ("Dried beverage mixes", ("Dried mixes",), 38, 24, "0.2", "239", "17.8"),
            ("Oils and extracts", ("Misc",), 239, 46, "0.2", "1000", "46.2"),
            ("Spice mixes", ("Spice - Mixed",), 104, 89, "0.8", "2170", "329"),
            ("Tea", TEA, 210, 178, "0.2", "1920", "302"),
        ],
        "total": ("Grand total", 739, 462, "0.2", "2170", "149"),
    },
    "2015-16": {
        "report": ("https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-"
                   "microbiology/food-safety-testing-reports-and-journal-articles/coumarin"),
        "rows": [
            ("Ground cinnamon", ("Ground cinnamon",), 29, 29, "6.8", "5040", "2839"),
            ("Tea", TEA, 297, 245, "0.2", "2230", "442"),
            ("Spice mixes", ("Spice - Mixed",), 221, 209, "0.2", "3040", "328"),
            ("Baked goods", ("Baked Goods", "Bakery Product - Bagel"), 200, 187, "0.2", "130",
             "18"),
        ],
        "total": ("Grand total", 747, 670, "0.2", "5040", "392"),
    },
}
SURVEYS = tuple(TABLES)

# Pre-registered predictions: (id, survey, row, expected verdict). Rows whose verdict was already
# known when this was written (both Tea rows) or cannot discriminate (2015-16 ground cinnamon,
# 29 of 29 detected) are reported but not graded.
PREDICTIONS = (
    ("Q1", "2014-15", "Cooking sauces", "all-samples"),
    ("Q2", "2014-15", "Dried beverage mixes", "all-samples"),
    ("Q3", "2014-15", "Oils and extracts", "all-samples"),
    ("Q4", "2014-15", "Spice mixes", "all-samples"),
    ("Q5", "2014-15", "Grand total", "all-samples"),
    ("Q6", "2015-16", "Spice mixes", "positives"),
    ("Q7", "2015-16", "Baked goods", "positives"),
    ("Q8", "2015-16", "Grand total", "positives"),
)
NOT_GRADED = {("2014-15", "Tea"): "known before registration (it failed the tea gate)",
              ("2015-16", "Tea"): "known before registration (it passed the tea gate)",
              ("2015-16", "Ground cinnamon"): "29 of 29 detected: both means are equal"}


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def decimals(printed):
    s = str(printed)
    return len(s.split(".")[1]) if "." in s else 0


def matches(value, printed):
    """True when `value` rounds to the printed figure at its printed precision."""
    if value is None:
        return False
    half = 0.5 * 10 ** (-decimals(printed))
    return abs(value - float(printed)) <= half + 1e-9


def verdict(mean_pos, mean_all, printed):
    p, a = matches(mean_pos, printed), matches(mean_all, printed)
    if p and a:
        return "both"
    if p:
        return "positives"
    if a:
        return "all-samples"
    return "neither"


def row_stats(ppms):
    ppms = sorted(ppms)
    det = [p for p in ppms if p > 0]
    return {
        "n": len(ppms), "n_detected": len(det),
        "min_detected": det[0] if det else None,
        "max": ppms[-1] if ppms else None,
        "mean_positives": statistics.fmean(det) if det else None,
        "mean_all": statistics.fmean(ppms) if ppms else None,
    }


def audit_row(name, ppms, n, n_det, pmin, pmax, pavg, n_unmeasured=0):
    s = row_stats(ppms)
    return dict(s, row=name, n_unmeasured=n_unmeasured, cfia={
        "n": n, "n_detected": n_det, "min": pmin, "max": pmax, "average": pavg},
        checks={"n": s["n"] == n, "n_detected": s["n_detected"] == n_det,
                "min": matches(s["min_detected"], pmin), "max": matches(s["max"], pmax)},
        verdict=verdict(s["mean_positives"], s["mean_all"], pavg))


def audit_survey(label, rows):
    """Rebuild one survey's Table 2 from coumarin_eu_limits.parse_rows() output."""
    spec = TABLES[label]
    out, used = [], set()
    for name, labels, n, n_det, pmin, pmax, pavg in spec["rows"]:
        sel = [r for r in rows if r["product"] in labels]
        used.update(labels)
        ppms = [r["ppm"] for r in sel if r["ppm"] is not None]
        out.append(audit_row(name, ppms, n, n_det, pmin, pmax, pavg,
                             sum(1 for r in sel if r["ppm"] is None)))
    name, n, n_det, pmin, pmax, pavg = spec["total"]
    allp = [r["ppm"] for r in rows if r["ppm"] is not None]
    out.append(audit_row(name, allp, n, n_det, pmin, pmax, pavg,
                         sum(1 for r in rows if r["ppm"] is None)))
    unmapped = {}
    for r in rows:
        if r["product"] not in used:
            unmapped[r["product"]] = unmapped.get(r["product"], 0) + 1
    return {"rows": out, "unmapped_labels": unmapped, "n_file_rows": len(rows),
            "units": _units(rows)}


def _units(rows):
    u = {}
    for r in rows:
        k = cel.norm_unit(r.get("unit_raw", ""))
        u[k] = u.get(k, 0) + 1
    return dict(sorted(u.items()))


def gate(audits):
    """A0: every file row maps to exactly one Table 2 row, each row's n equals CFIA's, the file
    has no unmeasured rows, and every unit is ug/g (= mg/kg)."""
    checks = {}
    for label, a in audits.items():
        checks[label] = {
            "all_labels_mapped": not a["unmapped_labels"],
            "row_counts": all(r["checks"]["n"] for r in a["rows"]),
            "no_unmeasured": all(r["n_unmeasured"] == 0 for r in a["rows"]),
            "units": a["units"] == {"ug/g": a["n_file_rows"]},
        }
    ok = all(all(c.values()) for c in checks.values())
    return ok, checks


def _row(audits, label, name):
    for r in audits[label]["rows"]:
        if r["row"] == name:
            return r
    raise KeyError((label, name))


def grade(audits):
    ok, checks = gate(audits)
    preds = [{"id": "A0", "kind": "gate", "met": ok, "graded": True, "observed": checks,
              "text": "every file row maps to one CFIA Table 2 row, row sizes equal CFIA's, no "
                      "unmeasured rows, units all ug/g"}]
    for pid, label, name, want in PREDICTIONS:
        r = _row(audits, label, name)
        preds.append({"id": pid, "kind": "verdict", "graded": ok,
                      "met": bool(ok and r["verdict"] == want),
                      "text": f"{label} {name}: CFIA's printed average equals the {want} mean",
                      "observed": {"verdict": r["verdict"], "printed": r["cfia"]["average"],
                                   "mean_positives": r["mean_positives"],
                                   "mean_all": r["mean_all"]}})
    return preds


def descriptive(audits):
    out = []
    for (label, name), why in NOT_GRADED.items():
        r = _row(audits, label, name)
        out.append({"survey": label, "row": name, "verdict": r["verdict"], "why_not_graded": why})
    return out


# ---------------------------------------------------------------------------
# Outputs.
# ---------------------------------------------------------------------------
TABLE_FIELDS = ["survey", "row", "n", "cfia_n", "n_detected", "cfia_n_detected", "min_detected",
                "cfia_min", "max", "cfia_max", "mean_positives", "mean_all", "cfia_average",
                "verdict"]


def write_outputs(out_dir, audits, preds, extra):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "coumarin_cfia_table_audit.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(TABLE_FIELDS)
        for label in SURVEYS:
            for r in audits[label]["rows"]:
                c = r["cfia"]
                w.writerow([label, r["row"], r["n"], c["n"], r["n_detected"], c["n_detected"],
                            _r(r["min_detected"]), c["min"], _r(r["max"]), c["max"],
                            _r(r["mean_positives"]), _r(r["mean_all"]), c["average"],
                            r["verdict"]])
    result = {"study": "coumarin-cfia-table-audit", "version": VERSION, "audits": audits,
              "predictions": preds, "not_graded": descriptive(audits),
              "n_predictions": len(preds), "n_met": sum(1 for p in preds if p["met"])}
    result.update(extra)
    with open(os.path.join(out_dir, "audit_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "audit_grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def _r(x):
    return "" if x is None else round(x, 4)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit CFIA coumarin Table 2 against the open files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    audits, provenance = {}, {}
    for label in SURVEYS:
        raw, path, source = ctr.load_survey(label, args.data_dir)
        audits[label] = audit_survey(label, cel.parse_rows(raw))
        provenance[label] = {"resource": ctr.SURVEYS[label]["resource"],
                             "sha256": ctr.SURVEYS[label]["sha256"], "bytes": len(raw),
                             "source": source, "report": TABLES[label]["report"]}
    preds = grade(audits)
    result = write_outputs(args.out_dir, audits, preds,
                           {"provenance": provenance, "parser": "coumarin_eu_limits " + cel.VERSION})
    print(json.dumps({
        "version": VERSION,
        "rows": [[label, r["row"], r["verdict"], r["checks"]] for label in SURVEYS
                 for r in audits[label]["rows"]],
        "unmapped": {k: v["unmapped_labels"] for k, v in audits.items()},
        "predictions": [(p["id"], p["met"]) for p in preds],
        "n_met": result["n_met"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
