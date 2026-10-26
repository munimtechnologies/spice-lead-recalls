#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""cooc_strata 0.1.0: is the ochratoxin A x deoxynivalenol co-occurrence a commodity effect?

Grades docs/cooc-strata-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

Two published per-sample tables in this repository give opposite pooled answers. In CFIA's
2010-11 retail-food file (myco-don 0.1.0; data/myco_don_2010_samples.csv, 943 samples) a sample
with detected ochratoxin A (OTA) is far more likely to carry detected deoxynivalenol (DON): odds
ratio 8.54. In CFIA's 2000-2018 livestock-feed file (feed-myco 0.1.0;
data/feed_myco_samples.csv, 3,219 samples tested for both) the pooled odds ratio is 0.70. Both
notes suggested the pooled figure mostly reflects which commodities carry which toxin. This
tests that directly: a Mantel-Haenszel odds ratio and a Cochran-Mantel-Haenszel test within
commodity strata (retail: CFIA's product label; feed: the ingredient common name).

Reads only the two committed tables, fetched from the public repository after the
pre-registration is public. Standard library only. Code Apache-2.0; derived data CC BY 4.0.
Not a finding about any product, feed, mill or farm.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import sys
import time
import urllib.request

VERSION = "0.1.0"
RAW = "https://raw.githubusercontent.com/munimtechnologies/spice-lead-recalls/main/"
RETAIL_PATH = "data/myco_don_2010_samples.csv"
FEED_PATH = "data/feed_myco_samples.csv"

# Gate: facts already published in myco-don 0.1.0 and feed-myco 0.1.0.
RETAIL_ROWS, RETAIL_SAMPLES = 1886, 943
RETAIL_POOLED = (275, 40, 280, 348)    # OTA&DON, OTA only, DON only, neither
FEED_SAMPLES = 3258
FEED_POOLED = (136, 60, 2312, 711)

OTA_LABEL, DON_LABEL = "Ochratoxin A", "Deoxynivalenol"
BLANK = "(blank)"

# Pre-registered bounds.
M3_BAND = (0.5, 1.5)
ALPHA = 0.05
MIN_STRATUM_REPORT = 10


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def retail_items(text):
    """[(stratum, ota_detected, don_detected)] per sample with both toxins, and the row count."""
    rows = list(csv.DictReader(io.StringIO(text)))
    by = {}
    for r in rows:
        s = by.setdefault(r["sample"], {"stratum": r["product"].strip() or BLANK})
        det = r["detected"].strip() == "1"
        if r["component"] == OTA_LABEL:
            s["ota"] = det
        elif r["component"] == DON_LABEL:
            s["don"] = det
    items = [(s["stratum"], s["ota"], s["don"]) for s in by.values() if "ota" in s and "don" in s]
    return items, len(rows), len(by)


def feed_items(text, key="ingredient_name"):
    """[(stratum, ota_detected, don_detected)] per sample tested for both, and the sample count."""
    rows = list(csv.DictReader(io.StringIO(text)))
    items = []
    for r in rows:
        ota, don = r["det_OTA"].strip(), r["det_DON"].strip()
        if ota == "" or don == "":
            continue
        items.append(((r[key] or "").strip() or BLANK, ota == "1", don == "1"))
    return items, len(rows)


def cells(items):
    """Pooled (a, b, c, d) with x = OTA, y = DON."""
    a = b = c = d = 0
    for _, ota, don in items:
        if ota and don:
            a += 1
        elif ota:
            b += 1
        elif don:
            c += 1
        else:
            d += 1
    return a, b, c, d


def strata_tables(items):
    """{stratum: (a, b, c, d)}."""
    groups = {}
    for it in items:
        groups.setdefault(it[0], []).append(it)
    return {k: cells(v) for k, v in sorted(groups.items())}


def odds_ratio(a, b, c, d):
    """Odds ratio with a Haldane 0.5 correction only if a cell is zero."""
    if 0 in (a, b, c, d):
        return ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
    return (a * d) / (b * c)


def mantel_haenszel(tables):
    """Mantel-Haenszel common odds ratio over 2x2 tables (None if undefined)."""
    num = den = 0.0
    for a, b, c, d in tables:
        n = a + b + c + d
        if n == 0:
            continue
        num += a * d / n
        den += b * c / n
    return (num / den if den > 0 else None), num, den


def cmh_test(tables):
    """Cochran-Mantel-Haenszel chi-square (1 df, continuity-corrected) and its p-value.

    Strata with fewer than 2 samples or a constant margin add nothing (zero variance)."""
    diff = var = 0.0
    for a, b, c, d in tables:
        n = a + b + c + d
        if n < 2:
            continue
        r1, r2, c1, c2 = a + b, c + d, a + c, b + d
        diff += a - r1 * c1 / n
        var += r1 * r2 * c1 * c2 / (n * n * (n - 1))
    if var <= 0:
        return 0.0, 1.0
    chi2 = max(0.0, abs(diff) - 0.5) ** 2 / var
    return chi2, math.erfc(math.sqrt(chi2 / 2.0))


def informative(tables):
    """Strata that contribute to the MH estimate (both exposures and both outcomes present)."""
    return [t for t in tables if (t[0] + t[1]) and (t[2] + t[3]) and (t[0] + t[2]) and (t[1] + t[3])]


def analyse(items):
    st = strata_tables(items)
    tabs = list(st.values())
    pooled = cells(items)
    mh, num, den = mantel_haenszel(tabs)
    chi2, p = cmh_test(tabs)
    return {
        "pooled": list(pooled), "pooled_or": odds_ratio(*pooled), "n": sum(pooled),
        "n_strata": len(st), "n_informative": len(informative(tabs)),
        "n_in_informative": sum(sum(t) for t in informative(tabs)),
        "mh_or": mh, "mh_num": num, "mh_den": den, "cmh_chi2": chi2, "cmh_p": p,
        "strata": {k: list(v) for k, v in st.items()},
    }


# ---------------------------------------------------------------------------
# Grading.
# ---------------------------------------------------------------------------
def grade(retail, feed, feed_type, gate_obs):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "retail table 1,886 rows / 943 samples with pooled OTA x DON (275, 40, 280, "
                      "348); feed table 3,258 samples with pooled (136, 60, 2,312, 711)"}]

    def add(pid, text, observed, met):
        preds.append({"id": pid, "kind": "prediction", "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    bound = math.sqrt(retail["pooled_or"])
    add("M1", "retail: the within-product Mantel-Haenszel OR is at most sqrt(8.54) = 2.92 (more "
        "than half of the pooled log-odds ratio lies between products)",
        {"mh_or": retail["mh_or"], "bound": bound},
        retail["mh_or"] is not None and retail["mh_or"] <= bound)
    add("M2", "retail: a positive association remains within products (MH OR > 1, CMH p < 0.05)",
        {"mh_or": retail["mh_or"], "cmh_p": retail["cmh_p"]},
        retail["mh_or"] is not None and retail["mh_or"] > 1 and retail["cmh_p"] < ALPHA)
    add("M3", "feed: within ingredients the MH OR lies in [0.5, 1.5] and the CMH p >= 0.05",
        {"mh_or": feed["mh_or"], "cmh_p": feed["cmh_p"]},
        feed["mh_or"] is not None and M3_BAND[0] <= feed["mh_or"] <= M3_BAND[1]
        and feed["cmh_p"] >= ALPHA)
    add("M4", "feed: the within-ingredient MH OR is closer to 1 than the pooled 0.70 "
        "(|ln MH OR| < |ln pooled OR|)",
        {"mh_or": feed["mh_or"], "pooled_or": feed["pooled_or"]},
        feed["mh_or"] is not None and feed["mh_or"] > 0
        and abs(math.log(feed["mh_or"])) < abs(math.log(feed["pooled_or"])))
    return preds


def gate_checks(retail_rows, retail_n, retail, feed_n, feed):
    return {
        "retail_rows": retail_rows == RETAIL_ROWS,
        "retail_samples": retail_n == RETAIL_SAMPLES,
        "retail_pooled": tuple(retail["pooled"]) == RETAIL_POOLED,
        "feed_samples": feed_n == FEED_SAMPLES,
        "feed_pooled": tuple(feed["pooled"]) == FEED_POOLED,
    }


# ---------------------------------------------------------------------------
# I/O.
# ---------------------------------------------------------------------------
def fetch(path, tries=4, pause=10):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(RAW + path, headers={"User-Agent": "mv2-cooc-strata"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read().decode("utf-8-sig")
        except Exception as exc:  # noqa: BLE001 - retry
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{path}: {last}")


def write_strata(path, res):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["stratum", "n", "ota_and_don", "ota_only", "don_only", "neither",
                    "odds_ratio", "haldane_corrected", "informative"])
        for k, t in sorted(res["strata"].items(), key=lambda kv: (-sum(kv[1]), kv[0])):
            a, b, c, d = t
            w.writerow([k, a + b + c + d, a, b, c, d, round(odds_ratio(a, b, c, d), 6),
                        int(0 in t), int(bool(informative([tuple(t)])))])


def _round(res):
    out = dict(res)
    for k in ("pooled_or", "mh_or", "mh_num", "mh_den", "cmh_chi2", "cmh_p"):
        if isinstance(out.get(k), float):
            out[k] = round(out[k], 12)
    out["large_strata"] = {k: v for k, v in res["strata"].items() if sum(v) >= MIN_STRATUM_REPORT}
    del out["strata"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the cooc-strata pre-registration.")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    retail_text, feed_text = fetch(RETAIL_PATH), fetch(FEED_PATH)
    r_items, r_rows, r_n = retail_items(retail_text)
    f_items, f_n = feed_items(feed_text)
    ft_items, _ = feed_items(feed_text, key="ingredient_type")
    retail, feed, feed_type = analyse(r_items), analyse(f_items), analyse(ft_items)
    gate_obs = gate_checks(r_rows, r_n, retail, f_n, feed)
    preds = grade(retail, feed, feed_type, gate_obs)
    os.makedirs(args.out_dir, exist_ok=True)
    write_strata(os.path.join(args.out_dir, "cooc_strata_retail.csv"), retail)
    write_strata(os.path.join(args.out_dir, "cooc_strata_feed.csv"), feed)
    write_strata(os.path.join(args.out_dir, "cooc_strata_feed_by_type.csv"), feed_type)
    result = {"study": "cooc-strata", "version": VERSION, "predictions": preds,
              "retail_by_product": _round(retail), "feed_by_ingredient": _round(feed),
              "feed_by_ingredient_type (sensitivity, not graded)": _round(feed_type),
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(args.out_dir, "cooc_strata_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    print(json.dumps({"version": VERSION, "gate": gate_obs,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"]}, indent=2))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
