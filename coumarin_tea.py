#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""coumarin_tea 0.1.0: how much of the coumarin tolerable daily intake (TDI) could a single cup
of the cinnamon-containing teas in CFIA's 2013-14 survey deliver, even if every bit of coumarin
transferred into the cup?

Grades docs/coumarin-tea-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

EFSA's TDI for coumarin is 0.1 mg per kg body weight per day (2004, confirmed 2008; BfR uses the
same value). A 60 kg adult's daily budget is 6 mg; a 15 kg child's is 1.5 mg. This tool converts
each CFIA tea concentration (mg/kg of dry tea) into the coumarin in one brewed cup under fixed,
pre-registered scenarios (grams of dry tea per cup, body weight) at a 100% transfer UPPER BOUND -
"even if all the coumarin ended up in the cup" - and counts how many teas would, in a single cup,
exceed the whole day's TDI. The 100% bound needs no contested extraction figure; the real cup is
lower. It is a bounded exposure screen on open data, not a compliance finding (Canada sets no
coumarin limit), not about any brand, and not individual dietary or medical advice.

Data: CFIA 2013-14 coumarin survey (Open Government Licence - Canada), loaded and parsed by
coumarin_eu_limits 0.1.1 (SHA-256 verified, units converted by an explicit table).
Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys

import coumarin_eu_limits as cel

VERSION = "0.1.0"

TDI_MG_PER_KG_BW = 0.1   # EFSA 2004, confirmed 2008

TEA_SUBCAT = "tea"       # coumarin_eu_limits.classify: "Tea - Herbal", "Tea - Black", ...

# Pre-registered per-cup scenarios: (body weight kg, dry tea g per cup, transfer fraction).
# Transfer is fixed at 1.0 (100%): an explicit upper bound, not a measured extraction yield.
SCENARIOS = {
    "A1": (60.0, 2.0, 1.0),   # adult, one standard 2 g cup           (primary)
    "A2": (60.0, 4.0, 1.0),   # adult, one strong/double 4 g cup      (test)
    "C1": (15.0, 2.0, 1.0),   # child, one standard 2 g cup           (test)
    "C2": (15.0, 4.0, 1.0),   # child, one strong/double 4 g cup      (test)
}

# Pre-registered gate thresholds, tied to CFIA's published 2013 tea headline
# (115 samples, min 0.3, max 2430, avg 500 mg/kg, 99% detected) and survey max 2,510.
G0_N_ROWS = (740, 749)
G0_MAX_PPM = (2200.0, 2800.0)
G0_N_TEA = 115
G0_TEA_MAX = (2300.0, 2500.0)     # CFIA published tea max 2430
G0_TEA_DETECTED = (112, 115)      # CFIA published tea detection 99%
G0_TEA_UNITS = {"ug/g": 115}

# Pre-registered prediction thresholds (fixed before any per-sample tea value was read).
P2_A2_SHARE = (0.005, 0.12)   # adult strong 4 g cup over the TDI
P3_C1_SHARE = (0.07, 0.40)    # child standard 2 g cup over the TDI
P4_C2_SHARE = (0.25, 0.70)    # child strong 4 g cup over the TDI


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def budget_mg(bw_kg, tdi=TDI_MG_PER_KG_BW):
    """A person's daily tolerable coumarin budget (mg) = TDI x body weight."""
    return tdi * bw_kg


def dose_mg(ppm, dry_g, transfer=1.0):
    """Coumarin (mg) in one cup from `dry_g` of tea at `ppm` (mg/kg) with `transfer` fraction."""
    return ppm * (dry_g / 1000.0) * transfer


def threshold_ppm(bw_kg, dry_g, transfer=1.0, tdi=TDI_MG_PER_KG_BW):
    """Concentration (mg/kg) at which one cup delivers exactly the day's TDI budget."""
    return budget_mg(bw_kg, tdi) / ((dry_g / 1000.0) * transfer)


def pct_budget(ppm, bw_kg, dry_g, transfer=1.0, tdi=TDI_MG_PER_KG_BW):
    """One cup's coumarin as a percentage of the drinker's whole-day TDI budget."""
    return 100.0 * dose_mg(ppm, dry_g, transfer) / budget_mg(bw_kg, tdi)


def nearest_rank(sorted_vals, q):
    """Nearest-rank quantile of an ascending list (q in (0, 1])."""
    if not sorted_vals:
        return None
    k = max(1, math.ceil(q * len(sorted_vals)))
    return sorted_vals[k - 1]


def summarise(rows):
    """Tea-bucket stats from coumarin_eu_limits.parse_rows() output."""
    measured = [r for r in rows if r["ppm"] is not None]
    tea_all = [r for r in rows if r["subcat"] == TEA_SUBCAT]
    tea = [r for r in tea_all if r["ppm"] is not None]
    ppms = sorted(r["ppm"] for r in tea)
    n = len(ppms)
    det = sum(1 for p in ppms if p > 0)
    units = {}
    for r in tea:
        k = cel.norm_unit(r.get("unit_raw", ""))
        units[k] = units.get(k, 0) + 1
    scen = {}
    for sid, (bw, g, tr) in SCENARIOS.items():
        thr = threshold_ppm(bw, g, tr)
        over = sum(1 for p in ppms if p > thr)
        scen[sid] = {
            "bw_kg": bw, "dry_g_per_cup": g, "transfer": tr, "threshold_ppm": thr,
            "n_over_tdi": over, "share_over_tdi": (over / n) if n else None,
            "median_dose_mg": dose_mg(statistics.median(ppms), g, tr) if n else None,
            "max_dose_mg": dose_mg(ppms[-1], g, tr) if n else None,
            "median_pct_budget": pct_budget(statistics.median(ppms), bw, g, tr) if n else None,
            "max_pct_budget": pct_budget(ppms[-1], bw, g, tr) if n else None,
        }
    return {
        "n_rows": len(measured),
        "pooled_max_ppm": max((r["ppm"] for r in measured), default=None),
        "tea_rows": len(tea_all),
        "tea": {
            "n": n, "n_detected": det, "share_detected": (det / n) if n else None,
            "ppm_min": ppms[0] if n else None,
            "ppm_median": statistics.median(ppms) if n else None,
            "ppm_mean": statistics.fmean(ppms) if n else None,
            "ppm_p90": nearest_rank(ppms, 0.9),
            "ppm_max": ppms[-1] if n else None,
        },
        "tea_units": dict(sorted(units.items())),
        "scenarios": scen,
    }


def _in(x, lo_hi):
    return x is not None and lo_hi[0] <= x <= lo_hi[1]


def grade(s):
    """Grade the pre-registered gate and predictions from a summarise() dict."""
    preds = []
    t = s["tea"]

    g0 = (_in(s["n_rows"], G0_N_ROWS)
          and _in(s["pooled_max_ppm"], G0_MAX_PPM)
          and s["tea_rows"] == G0_N_TEA
          and t["n"] == G0_N_TEA
          and _in(t["ppm_max"], G0_TEA_MAX)
          and _in(t["n_detected"], G0_TEA_DETECTED)
          and s["tea_units"] == G0_TEA_UNITS)
    preds.append({
        "id": "G0", "kind": "gate",
        "text": (f"measured rows in {list(G0_N_ROWS)}, pooled max in {list(G0_MAX_PPM)}, "
                 f"{G0_N_TEA} tea rows all measured, tea max in {list(G0_TEA_MAX)} "
                 f"(CFIA 2430), tea detected in {list(G0_TEA_DETECTED)} (CFIA 99%), "
                 f"tea unit census {G0_TEA_UNITS}"),
        "observed": {"n_rows": s["n_rows"], "pooled_max_ppm": s["pooled_max_ppm"],
                     "tea_rows": s["tea_rows"], "tea_measured": t["n"],
                     "tea_max": t["ppm_max"], "tea_detected": t["n_detected"],
                     "tea_units": s["tea_units"]},
        "met": bool(g0)})

    a1_over = s["scenarios"]["A1"]["n_over_tdi"]
    preds.append({
        "id": "P1", "kind": "primary",
        "text": "no tea cup over the adult TDI at 2 g dry, 100% transfer (A1 count == 0)",
        "observed": {"n_over_tdi": a1_over, "threshold_ppm": s["scenarios"]["A1"]["threshold_ppm"],
                     "n": t["n"]},
        "met": bool(t["n"] is not None and t["n"] > 0 and a1_over == 0)})

    a2 = s["scenarios"]["A2"]["share_over_tdi"]
    preds.append({
        "id": "P2", "kind": "test",
        "text": f"adult strong 4 g cup share over the TDI in {list(P2_A2_SHARE)}",
        "observed": {"share_over_tdi": a2, "n_over_tdi": s["scenarios"]["A2"]["n_over_tdi"],
                     "n": t["n"]},
        "met": bool(_in(a2, P2_A2_SHARE))})

    c1 = s["scenarios"]["C1"]["share_over_tdi"]
    preds.append({
        "id": "P3", "kind": "test",
        "text": f"child standard 2 g cup share over the TDI in {list(P3_C1_SHARE)}",
        "observed": {"share_over_tdi": c1, "n_over_tdi": s["scenarios"]["C1"]["n_over_tdi"],
                     "n": t["n"]},
        "met": bool(_in(c1, P3_C1_SHARE))})

    c2 = s["scenarios"]["C2"]["share_over_tdi"]
    preds.append({
        "id": "P4", "kind": "test",
        "text": f"child strong 4 g cup share over the TDI in {list(P4_C2_SHARE)}",
        "observed": {"share_over_tdi": c2, "n_over_tdi": s["scenarios"]["C2"]["n_over_tdi"],
                     "n": t["n"]},
        "met": bool(_in(c2, P4_C2_SHARE))})

    return preds


# ---------------------------------------------------------------------------
# Outputs.
# ---------------------------------------------------------------------------
def write_outputs(out_dir, rows, summary, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    tea = sorted((r for r in rows if r["subcat"] == TEA_SUBCAT),
                 key=lambda r: -(r["ppm"] if r["ppm"] is not None else -1))
    with open(os.path.join(out_dir, "coumarin_tea_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "region", "origin", "coumarin_ppm",
                    "pct_budget_a1", "pct_budget_a2", "pct_budget_c1", "pct_budget_c2",
                    "over_tdi_a1", "over_tdi_a2", "over_tdi_c1", "over_tdi_c2", "unit"])
        for r in tea:
            p = r["ppm"]
            pcts = []
            flags = []
            for sid in ("A1", "A2", "C1", "C2"):
                bw, g, tr = SCENARIOS[sid]
                pcts.append("" if p is None else round(pct_budget(p, bw, g, tr), 2))
                flags.append("" if p is None else ("yes" if p > threshold_ppm(bw, g, tr) else "no"))
            w.writerow([r["product"], r["region"], r["origin"],
                        "" if p is None else round(p, 4)] + pcts + flags
                       + [cel.norm_unit(r["unit_raw"])])
    result = {
        "study": "coumarin-tea", "version": VERSION,
        "tdi_mg_per_kg_bw": TDI_MG_PER_KG_BW,
        "scenarios": {k: {"bw_kg": v[0], "dry_g_per_cup": v[1], "transfer": v[2]}
                      for k, v in SCENARIOS.items()},
        "provenance": provenance, "summary": summary, "predictions": preds,
        "n_predictions": len(preds), "n_met": sum(1 for p in preds if p["met"]),
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the coumarin tea per-cup pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)

    raw, path, source = cel.load_raw(args.data_dir)
    rows = cel.parse_rows(raw)
    summary = summarise(rows)
    preds = grade(summary)
    provenance = {"raw_name": cel.RAW_NAME, "raw_sha256": cel.RAW_SHA256,
                  "raw_bytes": len(raw), "source": source, "path": path,
                  "resource": cel.RESOURCE, "parser": "coumarin_eu_limits " + cel.VERSION}
    result = write_outputs(args.out_dir, rows, summary, preds, provenance)

    print(json.dumps({
        "version": VERSION,
        "n_rows": summary["n_rows"],
        "pooled_max_ppm": summary["pooled_max_ppm"],
        "tea_rows": summary["tea_rows"],
        "tea_units": summary["tea_units"],
        "tea": summary["tea"],
        "scenarios": summary["scenarios"],
        "predictions": [(p["id"], p["met"]) for p in preds],
        "n_met": result["n_met"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
