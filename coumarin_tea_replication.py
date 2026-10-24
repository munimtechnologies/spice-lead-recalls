#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""coumarin_tea_replication 0.1.1: does the coumarin-tea per-cup screen replicate in CFIA's two
later tea surveys (2014-15: 210 teas; 2015-16: 297 teas)?

Grades docs/coumarin-tea-replication-0.1.0-prereg.md as amended by
docs/coumarin-tea-replication-0.1.1-amendment.md. Made with AI agents working in MV2's
(Munim, Inc.) name.

coumarin-tea 0.1.0 screened the 115 teas in CFIA's 2013-14 coumarin survey per brewed cup against
EFSA's tolerable daily intake (0.1 mg/kg body weight/day) at a 100% leaf-to-cup transfer upper
bound. This tool applies the SAME published scenarios and functions (coumarin_tea.SCENARIOS,
threshold_ppm, pct_budget, dose_mg) to the "Tea - *" samples of CFIA's 2014-15 and 2015-16
surveys, which were sampled in different years and, in 2015-16, also targeted licorice-flavoured
teas. It also re-selects the 2013-14 teas by the same rule as a reproduction check and writes a
pooled three-survey per-cup table. A bounded exposure screen on open data: not a compliance
finding (Canada sets no coumarin limit), not about any brand, not individual dietary or medical
advice.

0.1.1 (amendment): the 0.1.0 gate failed on one of its 14 checks. CFIA's 2014-15 tea average
(302 mg/kg) is footnoted "only positive results", but the file's positives mean is 356.2 while
its mean over all 210 teas (non-detects as 0) is 301.9. The amended gate compares the 2014-15
headline with the all-sample mean; nothing else changes. Because the 0.1.0 job had already
printed every observed value, P1-P10 graded under this amendment are a verification, not a
blind test.

Data: CFIA FSAP targeted-survey files (Open Government Licence - Canada), SHA-256 pinned, parsed
by coumarin_eu_limits 0.1.1 (explicit unit table). Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
import sys

import coumarin_eu_limits as cel
import coumarin_tea as ct

VERSION = "0.1.1"
GRADING_STATUS = ("verification: the gate was amended (0.1.1) after the 0.1.0 job had printed "
                  "every observed value, so P1-P10 are not a blind test")

_OPEN = "https://open.canada.ca/"
_OUVERT = "https://ouvert.canada.ca/"

# Pinned files. SHA-256 digests were recorded by the coumarin-cinnamon-v1 job (2026-10-18).
SURVEYS = {
    "2014-15": {
        "resource": "85372927-17ac-4958-a66f-fdd278f13f26",
        "dataset": "ecb615ff-504c-4e38-899e-3aeab317fadf",
        "raw_name": "cfia-2014-15-coumarin.csv",
        "sha256": "e418443deb56f7c1269e8c3527ad707788c53d6543c4f6da19d74cca95beec1e",
        "fallback": (_OPEN + "data/dataset/ecb615ff-504c-4e38-899e-3aeab317fadf/resource/"
                     "85372927-17ac-4958-a66f-fdd278f13f26/download/cfia_acia-1337-v1-cfia_acia_-_"
                     "18926143_-_fsap_chem_ts_-_2014-15_coumarin_in_cinnamon-containing_.csv"),
    },
    "2015-16": {
        "resource": "3a9481c9-cf6e-4dd0-8b25-29dd8975aa5e",
        "dataset": "afa33f86-435b-490c-b7c1-31b7ed66c569",
        "raw_name": "cfia-2015-16-coumarin.csv",
        "sha256": "4520863554e06b60092074d91eceff12123f39f4bcc2ce75eea2cdacedc0d30c",
        "fallback": (_OPEN + "data/dataset/afa33f86-435b-490c-b7c1-31b7ed66c569/resource/"
                     "3a9481c9-cf6e-4dd0-8b25-29dd8975aa5e/download/cfia_acia-1338-v1-cfia_acia_-_"
                     "18926158_-_fsap_chem_ts_-_2015-16_coumarin_cinnamon__cinnamon-cont.csv"),
    },
}
LATER = ("2014-15", "2015-16")
ALL = ("2013-14",) + LATER

# A tea is a row whose Product is exactly one of CFIA's six tea labels (not a substring match,
# so no "steak sauce" can leak in).
TEA_TYPES = ("Tea - Black", "Tea - Green", "Tea - Herbal", "Tea - Oolong", "Tea - White",
             "Tea - Other")
HERBAL = "Tea - Herbal"

# Gate G0, from CFIA's published tea headlines and the names-only / zero-token census.
# "mean" = (which dist_stats key CFIA's printed average is compared with, bounds).
# 0.1.1: 2014-15 uses the all-sample mean (see the amendment); 2015-16 is unchanged.
GATE = {
    "2014-15": {
        "n_rows": (730, 739), "n_tea": 210,
        "types": {"Tea - Black": 77, "Tea - Green": 30, "Tea - Herbal": 60, "Tea - Oolong": 7,
                  "Tea - White": 15, "Tea - Other": 21},
        "tea_max": (1910.0, 1930.0),        # CFIA 1920
        "detected": (178, 178),             # CFIA 178 of 210 (85%)
        "mean": ("ppm_mean", (285.0, 320.0)),   # CFIA 302 = mean of all 210 (amendment 0.1.1)
    },
    "2015-16": {
        "n_rows": (740, 747), "n_tea": 297,
        "types": {"Tea - Black": 81, "Tea - Green": 31, "Tea - Herbal": 86, "Tea - Oolong": 32,
                  "Tea - White": 42, "Tea - Other": 25},
        "tea_max": (2220.0, 2240.0),        # CFIA 2230
        "detected": (245, 245),             # CFIA 245 of 297 (82%)
        "mean": ("ppm_mean_detected", (420.0, 465.0)),  # CFIA 442, positives only
    },
}
UNIT = "ug/g"

# Published coumarin-tea 0.1.0 result (2013-14), the replication reference.
REF_1314 = {"n": 115, "A1": 0, "A2": 7, "C1": 33, "C2": 45}

# Pre-registered prediction thresholds (fixed before any 2014-15 or 2015-16 tea value was read;
# unchanged by the amendment).
P3_C1_1415 = (0.04, 0.22)
P4_C1_1516 = (0.10, 0.32)
P5_C2_1415 = (0.12, 0.40)
P6_C2_1516 = (0.18, 0.45)
P7_A2_1415_N = (1, 12)
P8_A2_1516_N = (2, 30)

SIDS = ("A1", "A2", "C1", "C2")


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def swap_host(url):
    """The same path on the other Government of Canada open-data host, or None."""
    for a, b in ((_OPEN, _OUVERT), (_OUVERT, _OPEN)):
        if url and url.startswith(a):
            return b + url[len(a):]
    return None


def candidate_urls(resolved, fallback):
    """Ordered, de-duplicated https URLs to try: the CKAN url, its twin on the other host, then
    the pinned fallback and its twin. A relative CKAN url is taken as ouvert.canada.ca."""
    if resolved and resolved.startswith("/"):
        resolved = _OUVERT.rstrip("/") + resolved
    out = []
    for u in (resolved, fallback):
        for v in (u, swap_host(u)):
            if v and v.startswith("https://") and v not in out:
                out.append(v)
    return out


def tea_rows(rows):
    return [r for r in rows if r["product"] in TEA_TYPES]


def scenario_stats(ppms):
    """Per-scenario over-TDI counts for an ascending list of mg/kg values."""
    n = len(ppms)
    out = {}
    for sid in SIDS:
        bw, g, tr = ct.SCENARIOS[sid]
        thr = ct.threshold_ppm(bw, g, tr)
        over = sum(1 for p in ppms if p > thr)
        out[sid] = {
            "bw_kg": bw, "dry_g_per_cup": g, "transfer": tr, "threshold_ppm": thr,
            "n_over_tdi": over, "share_over_tdi": (over / n) if n else None,
            "median_pct_budget": ct.pct_budget(statistics.median(ppms), bw, g, tr) if n else None,
            "max_pct_budget": ct.pct_budget(ppms[-1], bw, g, tr) if n else None,
        }
    return out


def dist_stats(ppms):
    n = len(ppms)
    det = [p for p in ppms if p > 0]
    return {
        "n": n, "n_detected": len(det), "share_detected": (len(det) / n) if n else None,
        "ppm_min": ppms[0] if n else None,
        "ppm_median": statistics.median(ppms) if n else None,
        "ppm_mean": statistics.fmean(ppms) if n else None,
        "ppm_mean_detected": statistics.fmean(det) if det else None,
        "ppm_p90": ct.nearest_rank(ppms, 0.9),
        "ppm_max": ppms[-1] if n else None,
    }


def summarise_survey(rows):
    """Tea stats for one survey from coumarin_eu_limits.parse_rows() output."""
    measured = [r for r in rows if r["ppm"] is not None]
    tea_all = tea_rows(rows)
    tea = [r for r in tea_all if r["ppm"] is not None]
    ppms = sorted(r["ppm"] for r in tea)
    types, units = {}, {}
    for r in tea_all:
        types[r["product"]] = types.get(r["product"], 0) + 1
    for r in tea:
        k = cel.norm_unit(r.get("unit_raw", ""))
        units[k] = units.get(k, 0) + 1
    by_type = {}
    for t in TEA_TYPES:
        tp = sorted(r["ppm"] for r in tea if r["product"] == t)
        if tp:
            by_type[t] = dict(dist_stats(tp), scenarios=scenario_stats(tp))
    return {
        "n_rows": len(measured),
        "tea_rows": len(tea_all),
        "classify_tea_rows": sum(1 for r in rows if r.get("subcat") == "tea"),
        "tea_types": dict(sorted(types.items())),
        "tea_units": dict(sorted(units.items())),
        "tea": dist_stats(ppms),
        "scenarios": scenario_stats(ppms),
        "by_type": by_type,
    }


def pooled(rows_by_survey):
    ppms = sorted(r["ppm"] for rows in rows_by_survey.values() for r in tea_rows(rows)
                  if r["ppm"] is not None)
    return {"surveys": sorted(rows_by_survey), "tea": dist_stats(ppms),
            "scenarios": scenario_stats(ppms)}


def _in(x, lo_hi):
    return x is not None and lo_hi[0] <= x <= lo_hi[1]


def gate_survey(label, s):
    g = GATE[label]
    t = s["tea"]
    mean_key, mean_bounds = g["mean"]
    checks = {
        "n_rows": _in(s["n_rows"], g["n_rows"]),
        "tea_rows": s["tea_rows"] == g["n_tea"] and t["n"] == g["n_tea"],
        "tea_types": s["tea_types"] == dict(sorted(g["types"].items())),
        "tea_units": s["tea_units"] == {UNIT: g["n_tea"]},
        "tea_max": _in(t["ppm_max"], g["tea_max"]),
        "detected": _in(t["n_detected"], g["detected"]),
        "mean": _in(t.get(mean_key), mean_bounds),
    }
    return all(checks.values()), checks


def _share(s, sid):
    return s["scenarios"][sid]["share_over_tdi"]


def _count(s, sid):
    return s["scenarios"][sid]["n_over_tdi"]


def grade(summ):
    """Grade G0 and P1-P10 from {"2014-15": summarise_survey(...), "2015-16": ...}."""
    a, b = summ["2014-15"], summ["2015-16"]
    preds = []

    ok_a, chk_a = gate_survey("2014-15", a)
    ok_b, chk_b = gate_survey("2015-16", b)
    gate_ok = ok_a and ok_b
    preds.append({
        "id": "G0", "kind": "gate",
        "text": ("both later surveys parse to CFIA's published tea headline: measured rows, exact "
                 "tea count and six-type census, unit census all ug/g, tea max, detected count "
                 "and CFIA's printed average within the registered bounds (amended 0.1.1: the "
                 "2014-15 average is compared with the mean of all 210 teas)"),
        "observed": {"2014-15": {"checks": chk_a, "n_rows": a["n_rows"], "tea": a["tea"],
                                 "tea_types": a["tea_types"], "tea_units": a["tea_units"]},
                     "2015-16": {"checks": chk_b, "n_rows": b["n_rows"], "tea": b["tea"],
                                 "tea_types": b["tea_types"], "tea_units": b["tea_units"]}},
        "met": bool(gate_ok), "graded": True})

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "text": text, "observed": observed,
                      "met": bool(gate_ok and met), "graded": gate_ok,
                      "blind": False})

    ref_c1 = REF_1314["C1"] / REF_1314["n"]
    add("P1", "check",
        "no tea in either later survey exceeds an adult's whole-day TDI in one standard 2 g cup "
        "(A1 count = 0; implied by CFIA's published maxima 1,920 and 2,230 < 3,000)",
        {"2014-15": _count(a, "A1"), "2015-16": _count(b, "A1")},
        _count(a, "A1") == 0 and _count(b, "A1") == 0)
    add("P2", "primary",
        "child standard 2 g cup: share over the TDI is LOWER in each later survey than "
        "2013-14's published 33/115 (0.287)",
        {"2014-15": _share(a, "C1"), "2015-16": _share(b, "C1"), "ref_2013_14": ref_c1},
        _share(a, "C1") is not None and _share(b, "C1") is not None
        and _share(a, "C1") < ref_c1 and _share(b, "C1") < ref_c1)
    add("P3", "test", f"2014-15 child 2 g cup share over the TDI in {list(P3_C1_1415)}",
        {"share": _share(a, "C1"), "n_over": _count(a, "C1"), "n": a["tea"]["n"]},
        _in(_share(a, "C1"), P3_C1_1415))
    add("P4", "test", f"2015-16 child 2 g cup share over the TDI in {list(P4_C1_1516)}",
        {"share": _share(b, "C1"), "n_over": _count(b, "C1"), "n": b["tea"]["n"]},
        _in(_share(b, "C1"), P4_C1_1516))
    add("P5", "test", f"2014-15 child strong 4 g cup share over the TDI in {list(P5_C2_1415)}",
        {"share": _share(a, "C2"), "n_over": _count(a, "C2"), "n": a["tea"]["n"]},
        _in(_share(a, "C2"), P5_C2_1415))
    add("P6", "test", f"2015-16 child strong 4 g cup share over the TDI in {list(P6_C2_1516)}",
        {"share": _share(b, "C2"), "n_over": _count(b, "C2"), "n": b["tea"]["n"]},
        _in(_share(b, "C2"), P6_C2_1516))
    add("P7", "test", f"2014-15 adult strong 4 g cup: number of teas over the TDI in "
        f"{list(P7_A2_1415_N)}", {"n_over": _count(a, "A2"), "n": a["tea"]["n"]},
        _in(_count(a, "A2"), P7_A2_1415_N))
    add("P8", "test", f"2015-16 adult strong 4 g cup: number of teas over the TDI in "
        f"{list(P8_A2_1516_N)}", {"n_over": _count(b, "A2"), "n": b["tea"]["n"]},
        _in(_count(b, "A2"), P8_A2_1516_N))
    add("P9", "direction", "child 2 g cup share over the TDI is higher in 2015-16 than in 2014-15",
        {"2014-15": _share(a, "C1"), "2015-16": _share(b, "C1")},
        _share(a, "C1") is not None and _share(b, "C1") is not None
        and _share(b, "C1") > _share(a, "C1"))
    meds = {t: v["ppm_median"] for t, v in b["by_type"].items()}
    herbal = meds.get(HERBAL)
    add("P10", "test", "in 2015-16, Tea - Herbal has the strictly highest median coumarin of the "
        "six tea types", {"medians": meds},
        herbal is not None and all(herbal > m for t, m in meds.items() if t != HERBAL))
    return preds


def reproduction_check(s1314):
    """Does the exact-label rule reproduce the published 2013-14 counts? (descriptive)"""
    got = {"n": s1314["tea"]["n"]}
    got.update({sid: _count(s1314, sid) for sid in SIDS})
    return {"expected": REF_1314, "observed": got, "match": got == REF_1314}


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_survey(label, data_dir):
    """Raw bytes of a pinned later survey, verified against its SHA-256 before any parse."""
    spec = SURVEYS[label]
    path = os.path.join(data_dir, spec["raw_name"]) if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == spec["sha256"]:
            return raw, path, "data-volume"
    resolved = None
    try:
        meta = json.loads(cel._fetch(cel.API + spec["resource"], tries=2, pause=5)
                          .decode("utf-8"))
        if meta.get("success"):
            resolved = meta["result"].get("url")
    except Exception as exc:  # noqa: BLE001 - fall back to the pinned url
        print(f"  resource_show failed for {label}: {exc}")
    errors = []
    for url in candidate_urls(resolved, spec["fallback"]):
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
        return raw, path, url
    raise RuntimeError(f"no verified copy of {label}: " + "; ".join(errors))


# ---------------------------------------------------------------------------
# Outputs.
# ---------------------------------------------------------------------------
SAMPLE_FIELDS = (["survey", "tea_type", "region", "origin", "coumarin_ppm"]
                 + ["pct_budget_" + s.lower() for s in SIDS]
                 + ["over_tdi_" + s.lower() for s in SIDS] + ["unit"])
TYPE_FIELDS = (["survey", "tea_type", "n", "n_detected", "ppm_median", "ppm_mean", "ppm_max"]
               + ["n_over_tdi_" + s.lower() for s in SIDS])


def write_outputs(out_dir, rows_by_survey, summ, preds, extra):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "coumarin_tea_replication_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SAMPLE_FIELDS)
        for label in ALL:
            tea = sorted(tea_rows(rows_by_survey[label]),
                         key=lambda r: (TEA_TYPES.index(r["product"]),
                                        -(r["ppm"] if r["ppm"] is not None else -1)))
            for r in tea:
                p = r["ppm"]
                pcts, flags = [], []
                for sid in SIDS:
                    bw, g, tr = ct.SCENARIOS[sid]
                    pcts.append("" if p is None else round(ct.pct_budget(p, bw, g, tr), 2))
                    flags.append("" if p is None else
                                 ("yes" if p > ct.threshold_ppm(bw, g, tr) else "no"))
                w.writerow([label, r["product"], r["region"], r["origin"],
                            "" if p is None else round(p, 4)] + pcts + flags
                           + [cel.norm_unit(r["unit_raw"])])
    with open(os.path.join(out_dir, "coumarin_tea_replication_by_type.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(TYPE_FIELDS)
        for label in ALL:
            for t, v in summ[label]["by_type"].items():
                w.writerow([label, t, v["n"], v["n_detected"], round(v["ppm_median"], 4),
                            round(v["ppm_mean"], 4), round(v["ppm_max"], 4)]
                           + [v["scenarios"][s]["n_over_tdi"] for s in SIDS])
    result = {
        "study": "coumarin-tea-replication", "version": VERSION,
        "grading_status": GRADING_STATUS,
        "tdi_mg_per_kg_bw": ct.TDI_MG_PER_KG_BW,
        "scenarios": {k: {"bw_kg": v[0], "dry_g_per_cup": v[1], "transfer": v[2]}
                      for k, v in ct.SCENARIOS.items()},
        "summary": summ, "predictions": preds,
        "n_predictions": len(preds), "n_met": sum(1 for p in preds if p["met"]),
    }
    result.update(extra)
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"grading_status": GRADING_STATUS, "predictions": preds}, fh, indent=2,
                  sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the coumarin tea replication pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)

    rows_by_survey, provenance = {}, {}
    raw, path, source = cel.load_raw(args.data_dir)
    rows_by_survey["2013-14"] = cel.parse_rows(raw)
    provenance["2013-14"] = {"resource": cel.RESOURCE, "sha256": cel.RAW_SHA256,
                             "bytes": len(raw), "source": source}
    for label in LATER:
        raw, path, source = load_survey(label, args.data_dir)
        rows_by_survey[label] = cel.parse_rows(raw)
        provenance[label] = {"resource": SURVEYS[label]["resource"],
                             "dataset": SURVEYS[label]["dataset"],
                             "sha256": SURVEYS[label]["sha256"], "bytes": len(raw),
                             "source": source}

    summ = {label: summarise_survey(rows) for label, rows in rows_by_survey.items()}
    summ["pooled_three_surveys"] = pooled(rows_by_survey)
    summ["pooled_later_two"] = pooled({k: rows_by_survey[k] for k in LATER})
    preds = grade(summ)
    repro = reproduction_check(summ["2013-14"])
    result = write_outputs(args.out_dir, rows_by_survey, summ, preds,
                           {"provenance": provenance, "reproduction_2013_14": repro,
                            "parser": "coumarin_eu_limits " + cel.VERSION,
                            "method": "coumarin_tea " + ct.VERSION})

    print(json.dumps({
        "version": VERSION,
        "grading_status": GRADING_STATUS,
        "reproduction_2013_14": repro,
        "surveys": {k: {"n_rows": summ[k]["n_rows"], "tea_rows": summ[k]["tea_rows"],
                        "tea_types": summ[k]["tea_types"], "tea_units": summ[k]["tea_units"],
                        "tea": summ[k]["tea"],
                        "over_tdi": {s: summ[k]["scenarios"][s]["n_over_tdi"] for s in SIDS}}
                    for k in ALL},
        "pooled_three_surveys": summ["pooled_three_surveys"],
        "predictions": [(p["id"], p["met"]) for p in preds],
        "n_met": result["n_met"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
