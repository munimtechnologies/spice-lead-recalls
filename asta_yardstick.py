#!/usr/bin/env python3
"""asta_yardstick 0.1.0: re-score two open spice-lead frames against ASTA's V3
per-category lead guidance levels (voluntary industry guidance, not law).

Pre-registered in docs/asta-yardstick-0.1.0-prereg.md (v0.4.30) before any count.
Reads only committed tables in data/:
  nyc_spice_lead_snapshot_2026-10-17.csv  NYC DOHMH da9u-wz3r, frame S (store survey)
  raman_reach_samples.csv                 Forsyth et al. 2026, Supplementary Table 8

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import json
import os
import re
import sys

VERSION = "0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
NYC_CSV = os.path.join(HERE, "data", "nyc_spice_lead_snapshot_2026-10-17.csv")
RAMAN_CSV = os.path.join(HERE, "data", "raman_reach_samples.csv")

# ASTA V3 (2026-06-08) Table 2/3, lead, ug/g. Blends have no ASTA category; the
# pre-registration counts them separately against a 2.0 bucket.
LEVELS = {"fruit": 0.60, "seed": 0.90, "bud": 1.0, "flower_pistil": 1.0,
          "root_rhizome": 1.50, "bark": 2.0, "herb": 2.0, "blend": 2.0}

# The pre-registered map, in match order: the first keyword found (at a word start,
# case-insensitive) decides. Multi-word names come before the single words they contain.
SINGLE = [
    ("star anise", "fruit"), ("curry leaf", "herb"), ("dill weed", "herb"),
    ("dill seed", "seed"), ("celery seed", "seed"),
    ("saffron", "flower_pistil"),
    ("clove", "bud"),
    ("cinnamon", "bark"), ("cassia", "bark"),
    ("turmeric", "root_rhizome"), ("ginger", "root_rhizome"), ("galangal", "root_rhizome"),
    ("horseradish", "root_rhizome"), ("wasabi", "root_rhizome"),
    ("oregano", "herb"), ("basil", "herb"), ("thyme", "herb"), ("rosemary", "herb"),
    ("sage", "herb"), ("parsley", "herb"), ("bay", "herb"), ("marjoram", "herb"),
    ("mint", "herb"), ("tarragon", "herb"),
    ("cumin", "seed"), ("coriander", "seed"), ("fennel", "seed"), ("fenugreek", "seed"),
    ("mustard", "seed"), ("caraway", "seed"), ("anise", "seed"), ("nigella", "seed"),
    ("sesame", "seed"), ("cardamom", "seed"), ("ajwain", "seed"), ("nutmeg", "seed"),
    ("mace", "seed"),
    ("pepper", "fruit"), ("piper", "fruit"), ("chili", "fruit"), ("chilli", "fruit"),
    ("chilly", "fruit"), ("chile", "fruit"), ("paprika", "fruit"), ("capsicum", "fruit"),
    ("allspice", "fruit"), ("juniper", "fruit"), ("sumac", "fruit"),
]
# Blends: checked only after every single spice, so a brand word ("Masala King
# Spices Turmeric Powder") does not hide the spice. "spice" is the last resort.
BLEND = ["curry", "masala", "mixed spice", "mix", "five spice", "5 spice", "seven spice",
         "seasoning", "khmeli", "humeli", "adjika", "ajika", "spice"]

NYC_FRAME = "S"
RAMAN_ND = 2.0  # half of the 4 ug/g XRF detection limit: the table's non-detect code


def _hit(name, kw):
    return re.search(r"\b" + re.escape(kw), name) is not None


def category(product_name):
    name = (product_name or "").lower()
    for kw, cat in SINGLE:
        if _hit(name, kw):
            return cat
    for kw in BLEND:
        if _hit(name, kw):
            return "blend"
    return "unmapped"


def nyc_store_rows(path=NYC_CSV):
    """Frame S lab lead results in ppm (= ug/g). -1 and 0 are non-detects."""
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for rec in csv.DictReader(fh):
            if (rec.get("product_type") or "").strip() != "Food-Spice":
                continue
            if (rec.get("metal") or "").strip().lower() != "lead":
                continue
            if (rec.get("units") or "").strip().lower() != "ppm":
                continue
            if "xrf" in (rec.get("analysis_type") or "").lower():
                continue
            if (rec.get("investigation_type") or "").strip().upper() != NYC_FRAME:
                continue
            try:
                value = float(rec["concentration"])
            except (TypeError, ValueError):
                continue
            cat = category(rec.get("product_name"))
            detected = value > 0
            level = LEVELS.get(cat)
            out.append({"row_id": rec["row_id"], "product_name": rec["product_name"],
                        "value": value if detected else None, "detected": detected,
                        "category": cat, "level": level,
                        "exceeds": bool(detected and level is not None and value > level)})
    return out


def raman_rows(path=RAMAN_CSV):
    """Every sample is turmeric (root/rhizome, 1.50 ug/g)."""
    out = []
    level = LEVELS["root_rhizome"]
    with open(path, newline="", encoding="utf-8") as fh:
        for rec in csv.DictReader(fh):
            pb = float(rec["pb"])
            detected = pb != RAMAN_ND
            out.append({"sample": rec["sample"], "state": rec["state_city_map"], "value": pb,
                        "detected": detected, "category": "root_rhizome", "level": level,
                        "exceeds": bool(detected and pb > level),
                        "naive_exceeds": pb > level})
    return out


def tally(rows, key):
    counts = {}
    for r in rows:
        counts[r[key]] = counts.get(r[key], 0) + 1
    return counts


def score(nyc, raman):
    n_nyc, n_raman = len(nyc), len(raman)
    ex_all = [r for r in nyc if r["exceeds"]]
    ex_single = [r for r in ex_all if r["category"] != "blend"]
    gross = sum(1 for r in nyc if r["detected"] and r["value"] >= 50)
    raman_ex = sum(1 for r in raman if r["exceeds"])
    raman_naive = sum(1 for r in raman if r["naive_exceeds"])
    rate_all, rate_single = len(ex_all) / n_nyc, len(ex_single) / n_nyc
    rate_raman = raman_ex / n_raman
    low = sum(1 for r in ex_single if r["category"] in ("fruit", "seed"))
    raman_far = sum(1 for r in raman if r["exceeds"] and r["value"] > 10)
    return {
        "version": VERSION,
        "nyc_store": {
            "n": n_nyc, "detected": sum(1 for r in nyc if r["detected"]),
            "rows_by_category": tally(nyc, "category"),
            "detected_by_category": tally([r for r in nyc if r["detected"]], "category"),
            "exceed_with_blends": len(ex_all), "exceed_single_spice": len(ex_single),
            "exceed_by_category": tally(ex_all, "category"),
            "gross_ge50": gross,
            "rate_with_blends": round(rate_all, 4), "rate_single_spice": round(rate_single, 4),
        },
        "raman_reach": {
            "n": n_raman, "non_detects": n_raman - sum(1 for r in raman if r["detected"]),
            "exceed": raman_ex, "exceed_upper_bound": raman_naive,
            "exceed_over_10": raman_far, "rate": round(rate_raman, 4),
        },
        "predictions": {
            "frame3_point_25_in_8_55": {"with_blends": 8 <= len(ex_all) <= 55,
                                        "single_spice": 8 <= len(ex_single) <= 55},
            "frame15_point_175_in_152_210": 152 <= raman_ex <= 210,
            "H1_nyc_at_least_6": {"with_blends": len(ex_all) >= 6,
                                  "single_spice": len(ex_single) >= 6},
            "H2_raman_over_30pct_and_3x_nyc": {
                "with_blends": rate_raman > 0.30 and rate_raman > 3 * rate_all,
                "single_spice": rate_raman > 0.30 and rate_raman > 3 * rate_single},
            "H3_nyc_mostly_fruit_seed": low * 2 > len(ex_single),
            "H3_raman_turmeric_far_above": raman_far * 2 > raman_ex,
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    nyc, raman = nyc_store_rows(), raman_rows()
    fields = ["row_id", "product_name", "value", "detected", "category", "level", "exceeds"]
    with open(os.path.join(args.out_dir, "asta_nyc_store.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(nyc)
    summary = score(nyc, raman)
    with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
