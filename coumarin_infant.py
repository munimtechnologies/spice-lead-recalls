#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""coumarin_infant 0.1.0: how much of the tolerable daily intake (TDI) for coumarin would the
cinnamon-containing infant cereals in CFIA's 2013-14 survey give an infant, per day?

Grades docs/coumarin-infant-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

EFSA's TDI for coumarin is 0.1 mg per kg body weight per day (2004, confirmed 2008). Infants eat
far more food per kg of body weight than adults, so the same coumarin concentration gives them a
larger share of the TDI. This tool converts each CFIA infant-cereal concentration into a daily
intake under fixed, pre-registered scenarios (body weight, grams of dry cereal per day) and
counts how many samples would reach the TDI. It is an exposure screen on open data, not a
compliance finding (Canada sets no coumarin limit), and not individual dietary or medical advice.

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

# Pre-registered exposure scenarios: (body weight in kg, dry infant cereal in g per day).
SCENARIOS = {
    "S1": (8.0, 30.0),   # primary: one Canadian reference amount a day (TRA item W.1, 30 g dry)
    "S2": (8.0, 60.0),   # two Canadian reference amounts a day
    "S3": (8.0, 15.0),   # one US reference amount a day (21 CFR 101.12, 15 g dry); descriptive
}

INFANT_SUBCAT = "infant"                  # coumarin_eu_limits.classify: "Infant Food - Cereal"
CHILD_CEREAL_PRODUCT = "cereal - children"
EU_CEREAL_LIMIT = 20.0                    # EU breakfast-cereal row; descriptive reference only

# Pre-registered gate and prediction thresholds.
G0_N_ROWS = (740, 749)
G0_MAX_PPM = (2200.0, 2800.0)
G0_N_INFANT = 52
G0_INFANT_UNITS = {"ug/g": 52}
P1_SHARE_S1 = (0.0, 0.10)       # share of infant cereals over the TDI under S1
P2_SHARE_S2 = (0.02, 0.30)      # share of infant cereals over the TDI under S2
P4_DETECTED = (0.80, 1.0)       # share of infant cereals with coumarin detected


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def threshold_ppm(bw_kg, dry_g_per_day, tdi=TDI_MG_PER_KG_BW):
    """Concentration (mg/kg) at which `dry_g_per_day` of cereal gives exactly the TDI."""
    return tdi * bw_kg / (dry_g_per_day / 1000.0)


def pct_tdi(ppm, bw_kg, dry_g_per_day, tdi=TDI_MG_PER_KG_BW):
    """Daily coumarin intake from `dry_g_per_day` of cereal at `ppm`, as a percentage of the TDI."""
    return 100.0 * ppm * (dry_g_per_day / 1000.0) / bw_kg / tdi


def nearest_rank(sorted_vals, q):
    """Nearest-rank quantile of an ascending list (q in (0, 1])."""
    if not sorted_vals:
        return None
    k = max(1, math.ceil(q * len(sorted_vals)))
    return sorted_vals[k - 1]


def is_child_cereal(row):
    return (row.get("product") or "").strip().lower() == CHILD_CEREAL_PRODUCT


def summarise(rows):
    """Infant-cereal and comparison stats from coumarin_eu_limits.parse_rows() output."""
    measured = [r for r in rows if r["ppm"] is not None]
    infant_all = [r for r in rows if r["subcat"] == INFANT_SUBCAT]
    infant = [r for r in infant_all if r["ppm"] is not None]
    child = sorted(r["ppm"] for r in measured if is_child_cereal(r))
    ppms = sorted(r["ppm"] for r in infant)
    n = len(ppms)
    det = sum(1 for p in ppms if p > 0)
    units = {}
    for r in infant:
        k = cel.norm_unit(r.get("unit_raw", ""))
        units[k] = units.get(k, 0) + 1
    scen = {}
    for sid, (bw, g) in SCENARIOS.items():
        thr = threshold_ppm(bw, g)
        over = sum(1 for p in ppms if p > thr)
        scen[sid] = {
            "bw_kg": bw, "dry_g_per_day": g, "threshold_ppm": thr,
            "n_over_tdi": over, "share_over_tdi": (over / n) if n else None,
            "median_pct_tdi": pct_tdi(statistics.median(ppms), bw, g) if n else None,
            "max_pct_tdi": pct_tdi(ppms[-1], bw, g) if n else None,
        }
    return {
        "n_rows": len(measured),
        "pooled_max_ppm": max((r["ppm"] for r in measured), default=None),
        "infant_rows": len(infant_all),
        "infant": {
            "n": n, "n_detected": det, "share_detected": (det / n) if n else None,
            "ppm_median": statistics.median(ppms) if n else None,
            "ppm_p90": nearest_rank(ppms, 0.9),
            "ppm_max": ppms[-1] if n else None,
            "n_over_eu_cereal_20": sum(1 for p in ppms if p > EU_CEREAL_LIMIT),
        },
        "infant_units": dict(sorted(units.items())),
        "child_cereal": {"n": len(child),
                         "ppm_median": statistics.median(child) if child else None},
        "scenarios": scen,
    }


def _in(x, lo_hi):
    return x is not None and lo_hi[0] <= x <= lo_hi[1]


def grade(s):
    """Grade the pre-registered gate and predictions from a summarise() dict."""
    preds = []

    g0 = (_in(s["n_rows"], G0_N_ROWS)
          and _in(s["pooled_max_ppm"], G0_MAX_PPM)
          and s["infant_rows"] == G0_N_INFANT
          and s["infant"]["n"] == G0_N_INFANT
          and s["infant_units"] == G0_INFANT_UNITS)
    preds.append({
        "id": "G0", "kind": "gate",
        "text": (f"measured rows in {list(G0_N_ROWS)}, pooled max ppm in {list(G0_MAX_PPM)}, "
                 f"{G0_N_INFANT} infant-cereal rows all measured, unit census {G0_INFANT_UNITS}"),
        "observed": {"n_rows": s["n_rows"], "pooled_max_ppm": s["pooled_max_ppm"],
                     "infant_rows": s["infant_rows"], "infant_measured": s["infant"]["n"],
                     "infant_units": s["infant_units"]},
        "met": bool(g0)})

    s1 = s["scenarios"]["S1"]["share_over_tdi"]
    preds.append({
        "id": "P1", "kind": "primary",
        "text": f"share of infant cereals over the TDI under S1 (8 kg, 30 g/day) in {list(P1_SHARE_S1)}",
        "observed": {"share_over_tdi": s1, "n_over_tdi": s["scenarios"]["S1"]["n_over_tdi"],
                     "n": s["infant"]["n"]},
        "met": bool(_in(s1, P1_SHARE_S1))})

    s2 = s["scenarios"]["S2"]["share_over_tdi"]
    preds.append({
        "id": "P2", "kind": "test",
        "text": f"share of infant cereals over the TDI under S2 (8 kg, 60 g/day) in {list(P2_SHARE_S2)}",
        "observed": {"share_over_tdi": s2, "n_over_tdi": s["scenarios"]["S2"]["n_over_tdi"],
                     "n": s["infant"]["n"]},
        "met": bool(_in(s2, P2_SHARE_S2))})

    im = s["infant"]["ppm_median"]
    cm = s["child_cereal"]["ppm_median"]
    preds.append({
        "id": "P3", "kind": "direction",
        "text": "median infant-cereal coumarin < median children's breakfast-cereal coumarin",
        "observed": {"infant_median_ppm": im, "child_cereal_median_ppm": cm},
        "met": bool(im is not None and cm is not None and im < cm)})

    sd = s["infant"]["share_detected"]
    preds.append({
        "id": "P4", "kind": "test",
        "text": f"share of infant cereals with coumarin detected in {list(P4_DETECTED)}",
        "observed": {"share_detected": sd, "n_detected": s["infant"]["n_detected"],
                     "n": s["infant"]["n"]},
        "met": bool(_in(sd, P4_DETECTED))})

    return preds


# ---------------------------------------------------------------------------
# Outputs.
# ---------------------------------------------------------------------------
def write_outputs(out_dir, rows, summary, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    infant = sorted((r for r in rows if r["subcat"] == INFANT_SUBCAT),
                    key=lambda r: -(r["ppm"] if r["ppm"] is not None else -1))
    with open(os.path.join(out_dir, "coumarin_infant_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "region", "origin", "coumarin_ppm", "pct_tdi_s1", "pct_tdi_s2",
                    "pct_tdi_s3", "over_tdi_s1", "over_tdi_s2", "unit"])
        for r in infant:
            p = r["ppm"]
            cells = []
            for sid in ("S1", "S2", "S3"):
                bw, g = SCENARIOS[sid]
                cells.append("" if p is None else round(pct_tdi(p, bw, g), 2))
            flags = []
            for sid in ("S1", "S2"):
                bw, g = SCENARIOS[sid]
                flags.append("" if p is None else ("yes" if p > threshold_ppm(bw, g) else "no"))
            w.writerow([r["product"], r["region"], r["origin"],
                        "" if p is None else round(p, 4)] + cells + flags
                       + [cel.norm_unit(r["unit_raw"])])
    result = {
        "study": "coumarin-infant", "version": VERSION,
        "tdi_mg_per_kg_bw": TDI_MG_PER_KG_BW,
        "scenarios": {k: {"bw_kg": v[0], "dry_g_per_day": v[1]} for k, v in SCENARIOS.items()},
        "provenance": provenance, "summary": summary, "predictions": preds,
        "n_predictions": len(preds), "n_met": sum(1 for p in preds if p["met"]),
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the coumarin infant-cereal pre-registration.")
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
        "infant_rows": summary["infant_rows"],
        "infant_units": summary["infant_units"],
        "infant": summary["infant"],
        "child_cereal": summary["child_cereal"],
        "scenarios": summary["scenarios"],
        "predictions": [(p["id"], p["met"]) for p in preds],
        "n_met": result["n_met"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
