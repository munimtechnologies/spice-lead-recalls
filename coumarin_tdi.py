#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""coumarin_tdi 0.1.0: how small a serving of Canadian retail cinnamon reaches the EFSA
tolerable daily intake (TDI) for coumarin?

Grades docs/coumarin-tdi-0.1.0-prereg.md, which was committed before any row of the grading
data was read. Made with AI agents working in MV2's (Munim, Inc.) name.

Coumarin has an EFSA tolerable daily intake of 0.1 mg per kg body weight per day (EFSA 2004,
reaffirmed 2008). CFIA measured coumarin in retail cinnamon (ppm = mg/kg, 2011-2016) but its
reports deliberately do not translate those levels into a dietary-exposure figure. This tool
does, reproducibly: for each cinnamon sample it computes the serving in grams that reaches
the TDI for a 60 kg adult and a 15 kg child, and summarises the per-sample distribution.

Data: the same four CFIA open.canada.ca CSVs the companion study coumarin_cinnamon.py
downloads, reused through that module (Open Government Licence - Canada). This tool adds only
the exposure arithmetic on top of the already-published `ppm` field. Code Apache-2.0; derived
data CC BY 4.0. This is an information/research tool, not individual dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys

VERSION = "0.1.0"

# Health-based guidance value and reference bodies / serving (fixed in the pre-registration).
TDI = 0.1          # mg coumarin per kg body weight per day (EFSA 2004/2008)
ADULT_KG = 60.0    # reference adult body weight
CHILD_KG = 15.0    # reference young-child body weight (~3 yr; Norwegian porridge scenario)
TEASPOON_G = 2.6   # grams of ground cinnamon per level teaspoon

# Pre-registered prediction thresholds.
G0_MIN_SAMPLES = 120
G0_MAX_PPM_RANGE = (7000.0, 8200.0)
P1_MEDIAN_ADULT_BELOW_G = 3.0
P2_FRAC_UNDER_2G_ATLEAST = 0.25   # fraction of samples with adult serving < 2.0 g (ppm > 3000)
P2_ADULT_SERVING_G = 2.0
P3_CHILD_TEASPOON_FRAC_ATLEAST = 0.80


# ---------------------------------------------------------------------------
# Exposure arithmetic (pure functions; unit-tested offline).
# ---------------------------------------------------------------------------
def serving_to_tdi_g(ppm, bw_kg, tdi=TDI):
    """Grams of a product at `ppm` coumarin (mg/kg) that deliver one TDI to a `bw_kg` person.

    serving = (tdi * bw_kg) / (ppm / 1000). Returns None for a missing or non-positive ppm.
    """
    if ppm is None or ppm <= 0:
        return None
    dose_mg_per_g = ppm / 1000.0          # ppm = mg/kg = 0.001 mg per g of product
    tdi_mg_per_day = tdi * bw_kg
    return tdi_mg_per_day / dose_mg_per_g


def dose_mg(grams, ppm):
    """Coumarin in `grams` of a product at `ppm` (mg/kg), in mg."""
    return grams * ppm / 1000.0


def child_teaspoon_ppm_threshold(tdi=TDI, child_kg=CHILD_KG, teaspoon_g=TEASPOON_G):
    """ppm at which one level teaspoon reaches the child's TDI."""
    return (tdi * child_kg) / (teaspoon_g / 1000.0)


# ---------------------------------------------------------------------------
# Sample selection and grading.
# ---------------------------------------------------------------------------
def select_cinnamon(rows):
    """Rows that are cinnamon itself with a numeric positive coumarin ppm."""
    out = []
    for r in rows:
        if not r.get("cinnamon"):
            continue
        ppm = r.get("ppm")
        if isinstance(ppm, (int, float)) and not isinstance(ppm, bool) and ppm > 0:
            out.append(r)
    return out


def summarise(samples):
    """Descriptive stats over the graded cinnamon samples."""
    ppms = sorted(s["ppm"] for s in samples)
    adult = [serving_to_tdi_g(p, ADULT_KG) for p in ppms]
    child = [serving_to_tdi_g(p, CHILD_KG) for p in ppms]
    tsp_ppm = child_teaspoon_ppm_threshold()
    n = len(ppms)
    n_under_2g = sum(1 for p in ppms if serving_to_tdi_g(p, ADULT_KG) < P2_ADULT_SERVING_G)
    n_child_tsp = sum(1 for p in ppms if p > tsp_ppm)
    return {
        "n_samples": n,
        "ppm_min": ppms[0] if n else None,
        "ppm_median": statistics.median(ppms) if n else None,
        "ppm_max": ppms[-1] if n else None,
        "adult_serving_g_median": statistics.median(adult) if n else None,
        "adult_serving_g_min": min(adult) if n else None,   # most concentrated sample
        "child_serving_g_median": statistics.median(child) if n else None,
        "frac_adult_under_2g": (n_under_2g / n) if n else None,
        "frac_child_teaspoon_over_tdi": (n_child_tsp / n) if n else None,
        "child_teaspoon_ppm_threshold": tsp_ppm,
        "constants": {"TDI": TDI, "ADULT_KG": ADULT_KG, "CHILD_KG": CHILD_KG,
                      "TEASPOON_G": TEASPOON_G},
    }


def grade(samples):
    """Grade the pre-registered predictions. Returns a list of prediction dicts."""
    s = summarise(samples)
    n = s["n_samples"]
    preds = []

    g0 = (n >= G0_MIN_SAMPLES
          and s["ppm_max"] is not None
          and G0_MAX_PPM_RANGE[0] <= s["ppm_max"] <= G0_MAX_PPM_RANGE[1])
    preds.append({
        "id": "G0", "kind": "gate",
        "text": f"n>={G0_MIN_SAMPLES} and pooled max ppm in {list(G0_MAX_PPM_RANGE)}",
        "observed": {"n": n, "ppm_max": s["ppm_max"]}, "met": bool(g0)})

    p1 = s["adult_serving_g_median"] is not None and s["adult_serving_g_median"] < P1_MEDIAN_ADULT_BELOW_G
    preds.append({
        "id": "P1", "kind": "primary",
        "text": f"median adult (60 kg) serving-to-TDI < {P1_MEDIAN_ADULT_BELOW_G} g",
        "observed": {"adult_serving_g_median": s["adult_serving_g_median"]}, "met": bool(p1)})

    p2 = s["frac_adult_under_2g"] is not None and s["frac_adult_under_2g"] >= P2_FRAC_UNDER_2G_ATLEAST
    preds.append({
        "id": "P2", "kind": "test",
        "text": f">= {P2_FRAC_UNDER_2G_ATLEAST:.0%} of samples reach adult TDI in < {P2_ADULT_SERVING_G} g (ppm>3000)",
        "observed": {"frac_adult_under_2g": s["frac_adult_under_2g"]}, "met": bool(p2)})

    p3 = s["frac_child_teaspoon_over_tdi"] is not None and s["frac_child_teaspoon_over_tdi"] > P3_CHILD_TEASPOON_FRAC_ATLEAST
    preds.append({
        "id": "P3", "kind": "anticipated",
        "text": f"> {P3_CHILD_TEASPOON_FRAC_ATLEAST:.0%} of samples put a 15 kg child over TDI at one teaspoon",
        "observed": {"frac_child_teaspoon_over_tdi": s["frac_child_teaspoon_over_tdi"]}, "met": bool(p3)})

    return preds


# ---------------------------------------------------------------------------
# Data loading (reuses the proven companion pipeline; network only here).
# ---------------------------------------------------------------------------
def load_rows():
    """Download + parse all four CFIA files via coumarin_cinnamon, returning pooled rows."""
    import coumarin_cinnamon as cc  # lazy: tests do not need network or this module
    rows = []
    provenance = []
    for entry in cc.FILES:
        # FILES entries are (label, role, dataset, url) tuples.
        label = entry[0]
        url = entry[-1]
        raw = cc.fetch(url)
        parsed, _check = cc.parse(raw, label=label)
        rows.extend(parsed)
        provenance.append({"label": label, "url": url, "rows": len(parsed)})
    return rows, provenance


def write_outputs(out_dir, samples, summary, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "coumarin_tdi_samples.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "product", "origin", "form", "claim", "class", "coumarin_ppm",
                    "adult_serving_g", "child_serving_g"])
        for r in sorted(samples, key=lambda x: -x["ppm"]):
            w.writerow([r.get("file", ""), r.get("product", ""), r.get("origin", ""),
                        r.get("form", ""), r.get("claim", ""), r.get("class", ""),
                        round(r["ppm"], 3),
                        round(serving_to_tdi_g(r["ppm"], ADULT_KG), 4),
                        round(serving_to_tdi_g(r["ppm"], CHILD_KG), 4)])
    result = {
        "study": "coumarin-tdi", "version": VERSION,
        "tdi_mg_per_kg_bw_day": TDI, "provenance": provenance,
        "summary": summary, "predictions": preds,
        "n_predictions": len(preds), "n_met": sum(1 for p in preds if p["met"]),
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the coumarin serving-to-TDI pre-registration.")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)

    rows, provenance = load_rows()
    samples = select_cinnamon(rows)
    summary = summarise(samples)
    preds = grade(samples)
    result = write_outputs(args.out_dir, samples, summary, preds, provenance)

    print(json.dumps({"n_samples": summary["n_samples"],
                      "ppm_median": summary["ppm_median"],
                      "ppm_max": summary["ppm_max"],
                      "adult_serving_g_median": summary["adult_serving_g_median"],
                      "predictions": [(p["id"], p["met"]) for p in preds],
                      "n_met": result["n_met"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
