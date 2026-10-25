#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""myco_don 0.1.0: deoxynivalenol in CFIA's open infant-cereal and selected-foods files.

Grades docs/myco-don-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) released three per-sample targeted-survey files on
open.canada.ca on 2026-10-06 (Open Government Licence - Canada):

  - don-infant-2018 (resource 7e3c4cf6): DON in infant cereals, Apr 2018-Mar 2019, 286 samples;
  - don-2011 (resource cef65485): DON in selected foods, 2011-2012, 1395 samples;
  - ota-don-2010 (resource b87d36bc): ochratoxin A and DON in selected foods, 2010-2011,
    943 samples, two rows each (one per toxin).

This reads them for the first time to (1) settle the internal contradiction in the 2018-19 infant
cereal report (Table 2's 13 positives vs Table 3's 123 for the same samples), (2) re-count the
figures CFIA printed on the 2010-11 and 2011-12 summary pages, and (3) build the first per-sample
ochratoxin A x deoxynivalenol co-occurrence table from CFIA's open retail data.

Every file is SHA-256 pinned. Standard library only. Code Apache-2.0; derived data CC BY 4.0.
A reference comparison, not a compliance finding (Canada has no DON maximum level for finished
foods), not about any brand, and not individual dietary or medical advice.
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
UNIT = "ng/g"

# (resource id, SHA-256, dataset id, download filename, n_rows, n_samples, rows_per_sample,
#  expected component counts)
FILES = {
    "infant": {
        "resource": "7e3c4cf6-69fa-4931-9f31-cd78225acf01",
        "dataset": "d17f8fe4-1d8b-4d78-8937-5f4f85812e02",
        "file": "chem_ts_2018-2019_deoxynivalenol_in_infant_cereals.csv",
        "sha256": "7427bd2905b8730ffc2403d379fd40549a42297fec0c3fc040d9a65446197583",
        "n_rows": 286, "n_samples": 286, "rows_per_sample": "1",
        "components": {"Deoxynivalenol": 286},
    },
    "don2011": {
        "resource": "cef65485-68e2-4580-8bd4-aa47c5a84c96",
        "dataset": "30484e10-f94e-4580-999f-3dc54eb75106",
        "file": "chem_ts_2011-12_deoxynivalenol_in_selected_foods.csv",
        "sha256": "4d4c90fb4b157bbb4c5a3f9aaf1c47b33b7b00a4d66437e2ea7ee6f5cb8a74ad",
        "n_rows": 1395, "n_samples": 1395, "rows_per_sample": "1",
        "components": {"Deoxynivalenol": 1395},
    },
    "otadon2010": {
        "resource": "b87d36bc-a568-4dc5-8391-9d8afdbf6048",
        "dataset": "4c43a389-245b-4c6c-a28a-c88235064e1b",
        "file": "chem_ts_2010-11_deoxynivalenol_and_ochratoxin_a_in_selected_foods.csv",
        "sha256": "fdd0aec2e70e8cbf0805b8cac5a98c98b48bc86a6ccafd1ce6f1f9d05395102a",
        "n_rows": 1886, "n_samples": 943, "rows_per_sample": "2",
        "components": {"Deoxynivalenol": 943, "Ochratoxin A": 943},
    },
}
ND_TOKENS = ("nd", "n.d.", "n/d", "not detected", "non détecté", "non detecte")

DON = "Deoxynivalenol"
OTA = "Ochratoxin A"

# Product labels (exact, from the names-only census).
WINE = ("Wine",)
DRIED_FRUIT_2010 = ("Raisin", "Fig", "Date", "Apricot", "Prune")
DRIED_FRUIT_2011 = ("Date", "Apricot", "Raisin", "Fig", "Currant", "Mango", "Prune", "Cherry",
                    "Cranberry", "Mixed Fruit", "Papaya", "Blueberry", "Banana", "Apricot - Organic")
INFANT_CEREAL = "Infant Food - Cereal"
# Grain-based labels in ota-don-2010 to which Health Canada's proposed OTA levels apply.
GRAINLIKE_2010 = ("Cereal - Adult", "Cereal - Children", "Infant Food - Cereal", "Flour - Wheat",
                  "Flour - Corn", "Bran - Wheat", "Bran - Oat", "Wheat Products", "Grain - Oat",
                  "Cornmeal", "Chips - Corn", "Oatmeal")
HC_INFANT, HC_BRAN, HC_GRAIN = 0.5, 7.0, 3.0

# EU Reg. (EU) 2024/1022 baby-food DON level (ng/g = ppb).
EU_BABY_DON = 150.0

# Pre-registered bounds (inclusive).
P1_DETECTED = (100, 135)
P1_OVER20 = 13
P4_OVER150 = (1, 4)
P5_DON_DETECTED = 555
P6_DON_MAX = 2060.0
P8_N = 93
P8_DETECTED = (73, 77)
P8_MAX = 128.0
P9_OTA_DETECTED = 315
P9_OTA_MIN = "0.040"
P9_OTA_MAX = "6.773"
P10_OVER = 8
P10_INFANT = 5
P11_OR = (0.5, 2.0)
P12_ND_SHARE = 37
P12_MAX = 2460.0


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def parse_result(raw):
    """(ppb, detected, kind) for one result cell under the registered non-detect rule."""
    s = (raw or "").strip()
    if not s:
        return 0.0, False, "blank"
    if s.startswith("<"):
        return 0.0, False, "lt"
    if s.lower() in ND_TOKENS:
        return 0.0, False, "nd_token"
    kind = "positive"
    try:
        v = float(s)
    except ValueError:
        if s.count(",") == 1 and "." not in s:
            try:
                v = float(s.replace(",", "."))
            except ValueError:
                return None, False, "bad"
            kind = "positive_comma"
        else:
            return None, False, "bad"
    if v != v or v < 0:
        return None, False, "bad"
    if v == 0:
        return 0.0, False, "zero"
    return v, True, kind


def matches(x, printed):
    """Does x round to the printed figure at the printed precision?"""
    if x is None:
        return False
    d = len(printed.split(".")[1]) if "." in printed else 0
    return abs(x - float(printed)) <= 0.5 * 10 ** (-d) + 1e-9


def within(x, bounds):
    return x is not None and bounds[0] <= x <= bounds[1]


def clean(cell):
    return (cell or "").replace("﻿", "").strip()


def find_columns(header):
    h = [clean(c) for c in header]

    def first(test, what):
        for i, c in enumerate(h):
            if test(c):
                return i
        raise ValueError(f"no {what} column in {header!r}")

    return {
        "sample": first(lambda c: c.startswith("Sample"), "sample"),
        "function": first(lambda c: c == "Function", "function"),
        "origin": first(lambda c: c == "Origin", "origin"),
        "product": first(lambda c: c == "Product", "product"),
        "component": first(lambda c: c == "Component", "component"),
        "result": first(lambda c: c.startswith("Result") or c == "Amount", "result"),
        "unit": first(lambda c: c.startswith("Unit"), "unit"),
        "plan": first(lambda c: c.startswith("Plan Code"), "plan code"),
    }


def _bump(d, k):
    d[k] = d.get(k, 0) + 1


def parse_text(text):
    """(rows, check) from the decoded CSV text of one file."""
    table = list(csv.reader(io.StringIO(text)))
    header = table[0]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    col = find_columns(header)

    def cell(r, k):
        i = col[k]
        return r[i] if i < len(r) else ""

    rows, kinds, units, comps = [], {}, {}, {}
    per_sample = {}
    for r in body:
        raw = cell(r, "result")
        ppb, det, kind = parse_result(raw)
        _bump(kinds, kind)
        _bump(units, clean(cell(r, "unit")))
        _bump(comps, clean(cell(r, "component")))
        sample = clean(cell(r, "sample"))
        _bump(per_sample, sample)
        rows.append({"sample": sample, "function": clean(cell(r, "function")),
                     "origin": clean(cell(r, "origin")), "product": clean(cell(r, "product")),
                     "component": clean(cell(r, "component")), "plan": clean(cell(r, "plan")),
                     "raw": raw, "ppb": ppb, "detected": det})
    rps = {}
    for v in per_sample.values():
        _bump(rps, str(v))
    check = {"n_rows": len(rows), "distinct_samples": len(per_sample), "units": units,
             "components": comps, "result_kinds": kinds, "rows_per_sample": rps}
    return rows, check


def gate_file(key, rows, check, sha_ok):
    spec = FILES[key]
    kinds = check["result_kinds"]
    only_nd_zero = all(k in ("positive", "zero") for k in kinds)
    checks = {
        "sha256": bool(sha_ok),
        "rows": check["n_rows"] == spec["n_rows"],
        "samples": check["distinct_samples"] == spec["n_samples"],
        "rows_per_sample": check["rows_per_sample"] == {spec["rows_per_sample"]: spec["n_samples"]},
        "units": check["units"] == {UNIT: spec["n_rows"]},
        "components": check["components"] == spec["components"],
        "all_parsed": kinds.get("bad", 0) == 0,
        "format_literal_zero": only_nd_zero and kinds.get("zero", 0) > 0,
    }
    return all(checks.values()), checks


def don_rows(rows):
    return [r for r in rows if r["component"] == DON]


def ota_rows(rows):
    return [r for r in rows if r["component"] == OTA]


def with_products(rows, products):
    keep = set(products)
    return [r for r in rows if r["product"] in keep]


def n_detected(rows):
    return sum(1 for r in rows if r["detected"])


def min_detected(rows):
    vals = [r["ppb"] for r in rows if r["detected"]]
    return min(vals) if vals else None


def max_value(rows):
    vals = [r["ppb"] for r in rows if r["ppb"] is not None]
    return max(vals) if vals else None


def n_at_or_above(rows, level):
    return sum(1 for r in rows if r["detected"] and r["ppb"] >= level)


def n_over(rows, level):
    return sum(1 for r in rows if r["detected"] and r["ppb"] > level)


def hc_limit(product):
    if product == INFANT_CEREAL:
        return HC_INFANT
    if product == "Bran - Wheat":
        return HC_BRAN
    return HC_GRAIN


def cooccurrence(rows):
    """2x2 OTA x DON detection table over samples in ota-don-2010, with odds ratio and Fisher p."""
    by_sample = {}
    for r in rows:
        s = by_sample.setdefault(r["sample"], {})
        if r["component"] == OTA:
            s["ota"] = r["detected"]
        elif r["component"] == DON:
            s["don"] = r["detected"]
    a = b = c = d = 0  # a=both, b=OTA only, c=DON only, d=neither
    paired = 0
    for s in by_sample.values():
        if "ota" not in s or "don" not in s:
            continue
        paired += 1
        if s["ota"] and s["don"]:
            a += 1
        elif s["ota"] and not s["don"]:
            b += 1
        elif not s["ota"] and s["don"]:
            c += 1
        else:
            d += 1
    # Odds ratio with a Haldane 0.5 correction only if a cell is zero.
    if 0 in (a, b, c, d):
        orr = ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
        corrected = True
    else:
        orr = (a * d) / (b * c)
        corrected = False
    return {"n_pairs": paired, "both": a, "ota_only": b, "don_only": c, "neither": d,
            "odds_ratio": orr, "haldane_corrected": corrected,
            "fisher_p": fisher_two_sided(a, b, c, d)}


def _logfact(n):
    return math.lgamma(n + 1)


def _hyper_logp(a, b, c, d):
    r1, r2, c1, c2, n = a + b, c + d, a + c, b + d, a + b + c + d
    return (_logfact(r1) + _logfact(r2) + _logfact(c1) + _logfact(c2)
            - _logfact(n) - _logfact(a) - _logfact(b) - _logfact(c) - _logfact(d))


def fisher_two_sided(a, b, c, d):
    """Two-sided Fisher exact p-value for a 2x2 table (standard-library only)."""
    r1, c1, n = a + b, a + c, a + b + c + d
    if n == 0:
        return 1.0
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    p_obs = _hyper_logp(a, b, c, d)
    total = 0.0
    for x in range(lo, hi + 1):
        bb, cc, dd = r1 - x, c1 - x, (n - r1) - (c1 - x)
        logp = _hyper_logp(x, bb, cc, dd)
        if logp <= p_obs + 1e-9:
            total += math.exp(logp)
    return min(1.0, total)


# ---------------------------------------------------------------------------
# Grading.
# ---------------------------------------------------------------------------
def grade(parsed):
    """parsed = {key: (rows, check, sha_ok)} for the three files."""
    gates, all_open = {}, True
    for key, (rows, check, sha_ok) in parsed.items():
        ok, checks = gate_file(key, rows, check, sha_ok)
        gates[key] = {"met": ok, "checks": checks,
                      "result_kinds": check["result_kinds"],
                      "rows_per_sample": check["rows_per_sample"]}
        all_open = all_open and ok
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": all_open, "observed": gates,
              "text": "SHA-256, row and sample counts, rows per sample, unit ng/g, component "
                      "split and non-detect-as-literal-0 format for all three files"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": all_open,
                      "met": bool(all_open and met), "text": text, "observed": observed})

    inf = parsed["infant"][0]
    d2011 = parsed["don2011"][0]
    d2010 = parsed["otadon2010"][0]
    inf_don = don_rows(inf)
    det = n_detected(inf_don)
    over20 = n_at_or_above(inf_don, 20.0)
    add("P1", "prediction", "infant cereals follow Table 3 (100-135 detected), with exactly 13 at "
        "or above the 20 ppb reporting limit of Table 2",
        {"n_detected": det, "n_at_or_above_20": over20, "table2": 13, "table3": 123},
        within(det, P1_DETECTED) and over20 == P1_OVER20)
    inf_max = max_value(inf_don)
    inf_min = min_detected(inf_don)
    add("P2", "prediction", "infant-cereal maximum 250 ppb and minimum detected below 1 ppb",
        {"max": inf_max, "min_detected": inf_min},
        inf_max is not None and matches(inf_max, "250") and inf_min is not None and inf_min < 1.0)
    ge20 = sorted(r["ppb"] for r in inf_don if r["detected"] and r["ppb"] >= 20.0)
    smallest_ge20 = ge20[0] if ge20 else None
    add("P3", "prediction", "the smallest value at or above 20 ppb is 22 (the text's 44.1 is wrong)",
        {"smallest_at_or_above_20": smallest_ge20, "text_min": 44.1},
        smallest_ge20 is not None and matches(smallest_ge20, "22"))
    over150 = n_over(inf_don, EU_BABY_DON)
    add("P4", "prediction", "1-4 infant cereals exceed the EU 2024/1022 baby-food DON level of 150",
        {"n_over_150": over150}, within(over150, P4_OVER150))

    don2010 = don_rows(d2010)
    don_det = n_detected(don2010)
    add("P5", "prediction", "DON detected in exactly 555 of 943 samples (2010-11)",
        {"n_detected": don_det, "printed_nd": 388}, don_det == P5_DON_DETECTED)
    don_min = min_detected(don2010)
    don_max = max_value(don2010)
    add("P6", "prediction", "2010-11 DON minimum rounds to 1 and maximum is 2060 ng/g",
        {"min_detected": don_min, "max": don_max},
        don_min is not None and matches(don_min, "1") and don_max is not None
        and matches(don_max, "2060"))
    wine_det = n_detected(with_products(don2010, WINE))
    dried_det = n_detected(with_products(don2010, DRIED_FRUIT_2010))
    add("P7", "prediction", "no 2010-11 wine or dried-fruit sample has detected DON",
        {"wine_detected": wine_det, "dried_fruit_detected": dried_det,
         "wine_n": len(with_products(don2010, WINE)),
         "dried_fruit_n": len(with_products(don2010, DRIED_FRUIT_2010))},
        wine_det == 0 and dried_det == 0)
    inf_cereal_2010 = with_products(don2010, (INFANT_CEREAL,))
    ic_det = n_detected(inf_cereal_2010)
    ic_max = max_value(inf_cereal_2010)
    ic_min = min_detected(inf_cereal_2010)
    add("P8", "prediction", "2010-11 infant cereals (n 93): DON detected 73-77, max 128, min ~1.1",
        {"n": len(inf_cereal_2010), "n_detected": ic_det, "max": ic_max, "min_detected": ic_min,
         "table3_n": 91},
        len(inf_cereal_2010) == P8_N and within(ic_det, P8_DETECTED)
        and ic_max is not None and matches(ic_max, "128")
        and ic_min is not None and matches(ic_min, "1.1"))

    ota2010 = ota_rows(d2010)
    ota_det = n_detected(ota2010)
    ota_min = min_detected(ota2010)
    ota_max = max_value(ota2010)
    add("P9", "prediction", "OTA detected in exactly 315 of 943, min 0.040, max 6.773 ppb",
        {"n_detected": ota_det, "min_detected": ota_min, "max": ota_max},
        ota_det == P9_OTA_DETECTED and ota_min is not None and matches(ota_min, P9_OTA_MIN)
        and ota_max is not None and matches(ota_max, P9_OTA_MAX))
    grain_ota = with_products(ota2010, GRAINLIKE_2010)
    over_hc = [r for r in grain_ota if r["detected"] and r["ppb"] > hc_limit(r["product"])]
    over_infant = sum(1 for r in over_hc if r["product"] == INFANT_CEREAL)
    add("P10", "prediction", "8 grain-based samples exceed Health Canada's proposed OTA levels, "
        "5 of them infant cereals",
        {"n_over": len(over_hc), "infant_cereal_over": over_infant,
         "by_product": _counts([r["product"] for r in over_hc])},
        len(over_hc) == P10_OVER and over_infant == P10_INFANT)
    co = cooccurrence(d2010)
    add("P11", "prediction", "within-sample OTA x DON detection odds ratio in [0.5, 2.0]",
        co, within(co["odds_ratio"], P11_OR))

    d2011_don = don_rows(d2011)
    nd_share = round(100.0 * (len(d2011_don) - n_detected(d2011_don)) / len(d2011_don)) \
        if d2011_don else None
    d2011_min = min_detected(d2011_don)
    d2011_max = max_value(d2011_don)
    dried2011_det = n_detected(with_products(d2011_don, DRIED_FRUIT_2011))
    add("P12", "prediction", "2011-12: ND share rounds to 37%, min ~1.0, max 2460, no dried fruit "
        "detected",
        {"nd_share": nd_share, "min_detected": d2011_min, "max": d2011_max,
         "dried_fruit_detected": dried2011_det,
         "dried_fruit_n": len(with_products(d2011_don, DRIED_FRUIT_2011))},
        nd_share == P12_ND_SHARE and d2011_min is not None and matches(d2011_min, "1.0")
        and d2011_max is not None and matches(d2011_max, "2460") and dried2011_det == 0)
    return preds, co


def _counts(seq):
    out = {}
    for x in seq:
        _bump(out, x)
    return dict(sorted(out.items()))


def descriptive(parsed, co):
    out = {}
    for key, (rows, check, _sha) in parsed.items():
        dr = don_rows(rows)
        out[key] = {"n_samples": check["distinct_samples"], "result_kinds": check["result_kinds"],
                    "don_detected": n_detected(dr), "don_min": min_detected(dr),
                    "don_max": max_value(dr)}
    out["otadon2010"]["ota_detected"] = n_detected(ota_rows(parsed["otadon2010"][0]))
    out["cooccurrence"] = co
    return out


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _fetch(url, tries=3, pause=8):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-myco-don"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load_one(key, data_dir):
    spec = FILES[key]
    path = os.path.join(data_dir, spec["resource"] + ".csv") if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == spec["sha256"]:
            return raw, "data-volume"
    urls = (
        f"https://open.canada.ca/data/dataset/{spec['dataset']}/resource/{spec['resource']}"
        f"/download/{spec['file']}",
        f"https://ouvert.canada.ca/data/dataset/{spec['dataset']}/resource/{spec['resource']}"
        f"/download/{spec['file']}",
    )
    errors = []
    for url in urls:
        try:
            raw = _fetch(url, tries=2, pause=5)
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
    raise RuntimeError(f"no verified copy of {key}: " + "; ".join(errors))


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
SAMPLE_FIELDS = ["sample", "plan", "function", "origin", "product", "component", "result_raw",
                 "ppb", "detected"]


def _r(x):
    return "" if x is None else (round(x, 4) if isinstance(x, float) else x)


def write_outputs(out_dir, parsed, preds, co, desc, provenance):
    os.makedirs(out_dir, exist_ok=True)
    # Per-sample values for the 2010-11 file (both toxins), so the co-occurrence is reproducible.
    with open(os.path.join(out_dir, "myco_don_2010_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SAMPLE_FIELDS)
        for r in parsed["otadon2010"][0]:
            w.writerow([r["sample"], r["plan"], r["function"], r["origin"], r["product"],
                        r["component"], r["raw"], _r(r["ppb"]), int(r["detected"])])
    with open(os.path.join(out_dir, "myco_don_cooccurrence.json"), "w", encoding="utf-8") as fh:
        json.dump(co, fh, indent=2, sort_keys=True)
    result = {"study": "myco-don", "version": VERSION, "predictions": preds,
              "descriptive": desc, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "myco_don_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "myco_don_grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the myco-don pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    parsed, provenance = {}, {}
    for key in FILES:
        raw, source = load_one(key, args.data_dir)
        text, enc = decode(raw)
        rows, check = parse_text(text)
        parsed[key] = (rows, check, _sha(raw) == FILES[key]["sha256"])
        provenance[key] = {"resource": FILES[key]["resource"], "sha256": FILES[key]["sha256"],
                           "bytes": len(raw), "source": source, "encoding": enc}
    preds, co = grade(parsed)
    desc = descriptive(parsed, co)
    result = write_outputs(args.out_dir, parsed, preds, co, desc, provenance)
    print(json.dumps({"version": VERSION,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"],
                      "gate": {k: v["met"] for k, v in preds[0]["observed"].items()},
                      "cooccurrence": co}, indent=2))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
