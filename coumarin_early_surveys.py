#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""coumarin_early_surveys 0.1.0: CFIA's first two coumarin surveys (2011-12, 2012-13), read for the
first time beyond their cinnamon.

Grades docs/coumarin-early-surveys-0.1.0-prereg.md. Made with AI agents working in MV2's
(Munim, Inc.) name.

CFIA's 2011-12 survey (193 samples) and 2012-13 survey (93 samples) have open per-sample files
(Open Government Licence - Canada), but their reports are available only on request; the public
summary pages give a detection rate and, for 2011-12, the highest result per product category.
Later CFIA reports (2014-15, 2015-16, 2016-18) reprint a Table 3 row for each survey's tea and
spice mixes under a note that says only positive results were used for the average.
coumarin-cinnamon 0.1.0 already published the 147 cinnamon samples; the other 139 samples
(2011-12 tea, spice mixes, cereals, baked goods, baking mixes and baby food; 2012-13 spice mixes)
had not been read.

This tool (1) checks every figure CFIA printed for these surveys against the files, (2) asks which
mean each reprinted average equals, as coumarin-cfia-table-audit 0.1.0 did for 2014-15 and
2015-16, and (3) replicates the earlier screens (EU coumarin maximum levels, the per-cup tea TDI
screen) on the unseen samples. Files are SHA-256 pinned and parsed by the published
coumarin_cinnamon 0.1.0 parser.

Code Apache-2.0; derived data CC BY 4.0. Not a compliance finding (Canada sets no coumarin
limit), not about any brand, not individual dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
import sys

import coumarin_cfia_table_audit as cta
import coumarin_cinnamon as cc
import coumarin_eu_limits as cel
import coumarin_tea as ct
import coumarin_tea_replication as ctr

VERSION = "0.1.0"

_OPEN = "https://open.canada.ca/"

# Pinned files. SHA-256 digests were recorded by the coumarin-cinnamon-v1 job (2026-10-18).
SURVEYS = {
    "2011-12": {
        "resource": "796ade00-c0cc-4cc6-b05d-cd440ca32dad",
        "dataset": "327a6726-a515-4cf6-b106-0cdb13dd94ba",
        "raw_name": "cfia-2011-12-coumarin.csv",
        "sha256": "10d2a339e13477ac9e3826255f5244cd793806f9915955523bcccff72a53540a",
        "fallback": (_OPEN + "data/dataset/327a6726-a515-4cf6-b106-0cdb13dd94ba/resource/"
                     "796ade00-c0cc-4cc6-b05d-cd440ca32dad/download/cfia_acia-1335_fsap_chem_ts_-_"
                     "2011-12_coumarin_in_cinnamon_and_cinnamon-containing_products_-_ts.csv"),
    },
    "2012-13": {
        "resource": "51630c7f-f1e0-4aff-8f13-f673b64a7888",
        "dataset": "ca2411af-18da-44be-ada1-1592dd7b94b5",
        "raw_name": "cfia-2012-13-coumarin.csv",
        "sha256": "6c155d79ac842f7e136975dd379e3c43685a5e25709d6f6533789c844246bc14",
        "fallback": (_OPEN + "data/dataset/ca2411af-18da-44be-ada1-1592dd7b94b5/resource/"
                     "51630c7f-f1e0-4aff-8f13-f673b64a7888/download/cfia_acia-1336-v1-cfia_acia_-_"
                     "18926108_-_fsap_chem_ts_-_2012-13_coumarin_in_cinnamon_and_cinnamo.csv"),
    },
}
LABELS_ORDER = ("2011-12", "2012-13")

# Names-only census (Product column only, no result read), 2026-10-24.
LABELS = {
    "2011-12": {"Ground Cinnamon": 87, "Cinnamon Sticks": 20, "Spice mix": 24, "Tea": 11,
                "Cereal": 15, "Baked Goods": 20, "Baking mix": 7, "Baby Food": 9},
    "2012-13": {"Cinnamon": 40, "Spice Mixes": 53},
}
CINNAMON = {"2011-12": ("Ground Cinnamon", "Cinnamon Sticks"), "2012-13": ("Cinnamon",)}
UNIT = "mg/kg"

# Gate reproduction of values already published by coumarin-cinnamon 0.1.0:
# (survey, label, statistic, value).
KNOWN = (
    ("2011-12", "Ground Cinnamon", "min_detected", 16.2),
    ("2011-12", "Ground Cinnamon", "max", 7816.3),
    ("2011-12", "Cinnamon Sticks", "max", 6823.2),
    ("2012-13", "Cinnamon", "max", 7621.1),
)
KNOWN_TOL = 0.05

# CFIA's 2011-12 summary page: highest result per non-cinnamon category (ppm), as printed.
PRINTED_MAX_1112 = {"Spice mix": "2014", "Tea": "1040", "Baked Goods": "95.3", "Cereal": "56.7",
                    "Baking mix": "45.8", "Baby Food": "14.9"}
# CFIA's summary pages: share of samples with coumarin detected (whole per cent).
PRINTED_DETECTED_PCT = {"2011-12": 98, "2012-13": 100}

# Table 3 rows reprinted in CFIA's 2014-15, 2015-16 and 2016-18 reports (identical in all three):
# (id, survey, file label, n, min, max, average), as printed. A min printed "<x" means at least
# one non-detect.
REPRINTS = (
    ("T1", "2011-12", "Tea", 11, "<0.29", "1040", "380"),
    ("T2", "2011-12", "Spice mix", 24, "<0.29", "2014", "352"),
    ("T3", "2012-13", "Spice Mixes", 53, "30", "3078", "568"),
    ("T0", "2011-12", "Ground Cinnamon", 87, "16.2", "7816", "3594"),
)
REPRINT_NOT_GRADED = {"T0": "its 87 values were published by coumarin-cinnamon 0.1.0"}
VERDICT_PRED = (("V1", "T1", "positives"), ("V2", "T2", "positives"), ("V3", "T3", "both"))

# EU Regulation (EC) No 1334/2008, Annex III Part B: coumarin maximum levels (mg/kg).
EU_FINE_BAKERY = 15.0
EU_SEASONAL_BAKERY = 50.0
EU_CEREALS = 20.0

# Infant screen as in coumarin-infant 0.1.0: 8 kg infant, 30 g/day, EFSA TDI.
INFANT_BW_KG = 8.0
INFANT_G_PER_DAY = 30.0

# Pre-registered replication bounds (counts, inclusive).
R1_BAKED_OVER_15 = (0, 8)
R2_BAKED_OVER_50 = (0, 3)
R3_CEREAL_OVER_20 = (1, 2)
R4_TEA_C1 = (1, 3)


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def cat_stats(ppms):
    v = sorted(ppms)
    det = [p for p in v if p > 0]
    return {
        "n": len(v), "n_detected": len(det),
        "min": v[0] if v else None,
        "min_detected": det[0] if det else None,
        "median": statistics.median(v) if v else None,
        "mean_all": statistics.fmean(v) if v else None,
        "mean_positives": statistics.fmean(det) if det else None,
        "max": v[-1] if v else None,
    }


def by_label(rows):
    """{product label: ascending list of ppm} for rows with a parsed result."""
    out = {}
    for r in rows:
        if r["ppm"] is not None:
            out.setdefault(r["product"], []).append(r["ppm"])
    return {k: sorted(v) for k, v in out.items()}


def census(rows):
    out = {}
    for r in rows:
        out[r["product"]] = out.get(r["product"], 0) + 1
    return out


def n_over(ppms, limit):
    return sum(1 for p in ppms if p > limit)


def pct_detected(n_det, n):
    return round(100.0 * n_det / n) if n else None


def reprint_checks(stats, n, pmin, pmax):
    """Do the file's n, minimum and maximum match a reprinted Table 3 row?"""
    if pmin.startswith("<"):
        min_ok = stats["n_detected"] < stats["n"]
    else:
        min_ok = cta.matches(stats["min"], pmin)
    return {"n": stats["n"] == n, "min": bool(min_ok), "max": cta.matches(stats["max"], pmax)}


def infant_pct_tdi(ppm):
    budget = ct.budget_mg(INFANT_BW_KG)
    return 100.0 * ppm * (INFANT_G_PER_DAY / 1000.0) / budget


def within(x, bounds):
    return bounds[0] <= x <= bounds[1]


def gate(parsed):
    """E0. `parsed` = {survey: {"rows": [...], "check": {...}, "sha_ok": bool}}."""
    checks = {}
    for label in LABELS_ORDER:
        p = parsed[label]
        rows, chk = p["rows"], p["check"]
        stats = {k: cat_stats(v) for k, v in by_label(rows).items()}
        known = {}
        for s, lab, key, val in KNOWN:
            if s == label:
                got = stats.get(lab, {}).get(key)
                known[f"{lab} {key}"] = got is not None and abs(got - val) <= KNOWN_TOL
        checks[label] = {
            "sha256": bool(p["sha_ok"]),
            "labels": census(rows) == LABELS[label],
            "units": chk.get("units") == {UNIT: len(rows)},
            "bad_numbers": chk.get("bad_numbers") == 0,
            "other_components": chk.get("other_component_rows") == 0,
            "all_parsed": all(r["ppm"] is not None for r in rows),
            "known_values": bool(known) and all(known.values()),
        }
    ok = all(all(c.values()) for c in checks.values())
    return ok, checks


def survey_stats(parsed):
    return {label: {k: cat_stats(v) for k, v in by_label(parsed[label]["rows"]).items()}
            for label in LABELS_ORDER}


def grade(parsed):
    ok, gchecks = gate(parsed)
    st = survey_stats(parsed)
    s11 = st["2011-12"]
    preds = [{"id": "E0", "kind": "gate", "graded": True, "met": ok, "observed": gchecks,
              "text": "both files: SHA-256, exact label census, units all mg/kg, every result "
                      "parsed, and the published cinnamon values reproduced"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": ok, "met": bool(ok and met),
                      "text": text, "observed": observed})

    # C1-C3: CFIA's printed figures.
    c1 = {lab: {"printed": pm, "file": s11.get(lab, {}).get("max"),
                "match": cta.matches(s11.get(lab, {}).get("max"), pm)}
          for lab, pm in PRINTED_MAX_1112.items()}
    add("C1", "consistency", "each 2011-12 non-cinnamon category's maximum equals the maximum "
        "CFIA's summary page prints for it", c1, all(v["match"] for v in c1.values()))
    c2 = {}
    for label in LABELS_ORDER:
        rows = parsed[label]["rows"]
        n_det = sum(1 for r in rows if (r["ppm"] or 0) > 0)
        c2[label] = {"n": len(rows), "n_detected": n_det,
                     "pct": pct_detected(n_det, len(rows)),
                     "printed_pct": PRINTED_DETECTED_PCT[label]}
    add("C2", "consistency", "the detection rate rounds to CFIA's printed 98% (2011-12) and "
        "100% (2012-13)", c2, all(v["pct"] == v["printed_pct"] for v in c2.values()))
    c3, reprints = {}, {}
    for rid, label, lab, n, pmin, pmax, pavg in REPRINTS:
        s = st[label].get(lab) or cat_stats([])
        chk = reprint_checks(s, n, pmin, pmax)
        reprints[rid] = {"survey": label, "label": lab, "stats": s, "checks": chk,
                         "printed": {"n": n, "min": pmin, "max": pmax, "average": pavg},
                         "verdict": cta.verdict(s["mean_positives"], s["mean_all"], pavg)}
        if rid not in REPRINT_NOT_GRADED:
            c3[rid] = chk
    add("C3", "consistency", "the reprinted Table 3 rows T1-T3 match the files' n, minimum and "
        "maximum", c3, all(all(v.values()) for v in c3.values()))

    # V1-V3: which mean each reprinted average equals.
    for pid, rid, want in VERDICT_PRED:
        r = reprints[rid]
        add(pid, "verdict", f"{r['survey']} {r['label']}: CFIA's reprinted average "
            f"{r['printed']['average']} equals the {want} mean",
            {"verdict": r["verdict"], "mean_positives": r["stats"]["mean_positives"],
             "mean_all": r["stats"]["mean_all"]}, r["verdict"] == want)

    # R1-R5: replications on unseen samples.
    baked = by_label(parsed["2011-12"]["rows"]).get("Baked Goods", [])
    cereal = by_label(parsed["2011-12"]["rows"]).get("Cereal", [])
    tea = by_label(parsed["2011-12"]["rows"]).get("Tea", [])
    baby = by_label(parsed["2011-12"]["rows"]).get("Baby Food", [])
    b15, b50, c20 = n_over(baked, EU_FINE_BAKERY), n_over(baked, EU_SEASONAL_BAKERY), \
        n_over(cereal, EU_CEREALS)
    add("R1", "replication", "at most 8 of the 20 baked goods exceed the EU's 15 mg/kg "
        "fine-bakery level", {"n_over": b15, "n": len(baked)}, within(b15, R1_BAKED_OVER_15))
    add("R2", "replication", "at most 3 of the 20 baked goods exceed the EU's 50 mg/kg "
        "seasonal-bakery level", {"n_over": b50, "n": len(baked)}, within(b50, R2_BAKED_OVER_50))
    add("R3", "replication", "1 or 2 of the 15 cereals exceed the EU's 20 mg/kg cereal level",
        {"n_over": c20, "n": len(cereal)}, within(c20, R3_CEREAL_OVER_20))
    tea_sc = ctr.scenario_stats(tea) if tea else {}
    c1n = tea_sc.get("C1", {}).get("n_over_tdi", -1)
    add("R4", "replication", "1 to 3 of the 11 teas put a 15 kg child over the coumarin TDI in "
        "one 2 g cup at 100% transfer", {"n_over": c1n, "n": len(tea)}, within(c1n, R4_TEA_C1))
    mb = statistics.median(baby) if baby else None
    mc = statistics.median(cereal) if cereal else None
    add("R5", "replication", "the baby-food median is below the 2011-12 cereal median",
        {"baby_food_median": mb, "cereal_median": mc},
        mb is not None and mc is not None and mb < mc)
    return preds, st, reprints, tea_sc


def descriptive(parsed, st, tea_sc):
    rows11 = by_label(parsed["2011-12"]["rows"])
    baby = rows11.get("Baby Food", [])
    return {
        "eu": {"Baked Goods": {"n": len(rows11.get("Baked Goods", [])),
                               "over_15": n_over(rows11.get("Baked Goods", []), EU_FINE_BAKERY),
                               "over_50": n_over(rows11.get("Baked Goods", []),
                                                 EU_SEASONAL_BAKERY)},
               "Cereal": {"n": len(rows11.get("Cereal", [])),
                          "over_20": n_over(rows11.get("Cereal", []), EU_CEREALS)}},
        "tea_scenarios": tea_sc,
        "baby_food": {"n": len(baby),
                      "max_pct_tdi_30g_8kg": infant_pct_tdi(baby[-1]) if baby else None,
                      "n_over_tdi_30g": sum(1 for p in baby if infant_pct_tdi(p) > 100.0),
                      "n_over_tdi_60g": sum(1 for p in baby if 2 * infant_pct_tdi(p) > 100.0)},
        "unseen_labels": {label: sorted(k for k in LABELS[label] if k not in CINNAMON[label])
                          for label in LABELS_ORDER},
    }


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_survey(label, data_dir):
    """Raw bytes of a pinned survey, verified against its SHA-256 before any parse."""
    spec = SURVEYS[label]
    path = os.path.join(data_dir, spec["raw_name"]) if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == spec["sha256"]:
            return raw, "data-volume"
    resolved = None
    try:
        meta = json.loads(cel._fetch(cel.API + spec["resource"], tries=2, pause=5)
                          .decode("utf-8"))
        if meta.get("success"):
            resolved = meta["result"].get("url")
    except Exception as exc:  # noqa: BLE001 - fall back to the pinned url
        print(f"  resource_show failed for {label}: {exc}")
    errors = []
    for url in ctr.candidate_urls(resolved, spec["fallback"]):
        try:
            raw = cel._fetch(url, tries=2, pause=5)
        except Exception as exc:  # noqa: BLE001 - try the next host
            errors.append(f"{url}: {exc}")
            continue
        got = _sha(raw)
        if got != spec["sha256"]:
            errors.append(f"{url}: SHA-256 {got} != {spec['sha256']}")
            continue
        if path:
            try:
                os.makedirs(data_dir, exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(raw)
            except OSError:
                pass
        return raw, url
    raise RuntimeError(f"no verified copy of {label}: " + "; ".join(errors))


# ---------------------------------------------------------------------------
# Outputs.
# ---------------------------------------------------------------------------
TABLE_FIELDS = ["survey", "product_label", "cinnamon", "n", "n_detected", "min_detected",
                "median", "mean_positives", "mean_all", "max"]
SAMPLE_FIELDS = ["survey", "sample", "product_label", "origin", "coumarin_ppm"]


def _r(x):
    return "" if x is None else round(x, 4)


def write_outputs(out_dir, parsed, st, preds, reprints, desc, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "coumarin_early_surveys.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(TABLE_FIELDS)
        for label in LABELS_ORDER:
            for lab in LABELS[label]:
                s = st[label].get(lab) or cat_stats([])
                w.writerow([label, lab, int(lab in CINNAMON[label]), s["n"], s["n_detected"],
                            _r(s["min_detected"]), _r(s["median"]), _r(s["mean_positives"]),
                            _r(s["mean_all"]), _r(s["max"])])
    # Per-sample values for the samples not published before (no cinnamon rows).
    with open(os.path.join(out_dir, "coumarin_early_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SAMPLE_FIELDS)
        for label in LABELS_ORDER:
            for r in parsed[label]["rows"]:
                if r["product"] not in CINNAMON[label]:
                    w.writerow([label, r["sample"], r["product"], r["origin"], _r(r["ppm"])])
    result = {"study": "coumarin-early-surveys", "version": VERSION, "predictions": preds,
              "reprints": reprints, "not_graded": REPRINT_NOT_GRADED, "descriptive": desc,
              "provenance": provenance, "parser": "coumarin_cinnamon " + cc.VERSION,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "early_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "early_grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the coumarin-early-surveys pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    parsed, provenance = {}, {}
    for label in LABELS_ORDER:
        raw, source = load_survey(label, args.data_dir)
        rows, check = cc.parse(raw, label)
        parsed[label] = {"rows": rows, "check": check,
                         "sha_ok": _sha(raw) == SURVEYS[label]["sha256"]}
        provenance[label] = {"resource": SURVEYS[label]["resource"],
                             "dataset": SURVEYS[label]["dataset"],
                             "sha256": SURVEYS[label]["sha256"], "bytes": len(raw),
                             "source": source, "units": check["units"],
                             "encoding": check["encoding"]}
    preds, st, reprints, tea_sc = grade(parsed)
    desc = descriptive(parsed, st, tea_sc)
    result = write_outputs(args.out_dir, parsed, st, preds, reprints, desc, provenance)
    print(json.dumps({"version": VERSION,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "gate": preds[0]["observed"]}, indent=2))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
