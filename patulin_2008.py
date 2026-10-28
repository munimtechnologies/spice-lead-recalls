#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""patulin-2008 0.1.0: CFIA's open 2008-09 file of patulin in apple juice and apple juice
concentrate, against its summary page.

Grades docs/patulin-2008-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

The Canadian Food Inspection Agency (CFIA) publishes a per-sample file, "2008-09 Patulin in Apple
Juice Products" (PA; 104 rows, one patulin result per sample), on open.canada.ca (Open Government
Licence - Canada). Its only public report is a summary page: 104 samples (94 imported, 10
domestic); 88.5% below the 10 ppb reporting limit (37 of 44 juices, 55 of 60 concentrates);
maxima 26.7 ppb (juice) and 24.0 ppb (concentrate); all below the Codex draft level of 50 ppb;
"country of origin" not linked to patulin levels. The full report is available only on request.
This reads the result column for the first time to (a) check the printed figures, (b) test the
page's claim that origin is unrelated to patulin, and (c) test blind predictions on how the open
file records results below the reporting limit and where the quantified results sit.

The file is SHA-256 pinned. Value rule (registered before any AMOUNT cell was read): a cell that
parses as a number above 0 is a number ("num"); a literal 0 is "zero"; "<" followed by a number
or by a limit name is "lt"; ND-type tokens are "nd". Blank, other text, negative or non-finite
cells fail the gate. Units go through an explicit table. Standard library only. Code Apache-2.0;
derived data CC BY 4.0. Not a compliance finding, not about any brand, and not individual
dietary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import sys
import time
import urllib.request

VERSION = "0.1.0"

PA = {
    "key": "PA",
    "dataset": "a3c93b73-f001-47b7-abbd-4df1438a9b06",
    "resource": "60694a95-9060-49e4-b1ec-b61910e4c8c9",
    "filename": ("copy-of-cfia_acia-1483-v1-chem_ts_fsap_2008-09_patulin_in_apple_juices_and_"
                 "apple_juice_concentra.csv"),
    "sha256": "4039e4a8b3e915b329b7e2afd9bc778c4a4707a7b7e5d99bd1319db0a745be66",
    "rows": 104, "samples": 104,
}
JUICE, CONC = "Apple Juice", "Apple Juice Concentrate"

# Census facts (names-only census, job myco-census-v2, 2026-10-25): row counts per label.
PRODUCT_ROWS = {CONC: 60, JUICE: 44}
FUNCTION_ROWS = {"imported": 94, "domestic": 10}
ORIGIN_ROWS = {"CHINA": 42, "UNITED STATES": 23, "CHILE": 17, "CANADA": 10, "SOUTH AFRICA": 5,
               "UNKNOWN": 3, "TURKEY": 2, "JORDAN": 1, "MOLDOVA": 1}
COMPONENT_ROWS = {"Patulin": 104}

# Units -> factor to ug/kg (= ppb). Keys are lower-cased. For juice, 1 ug/L is read as 1 ug/kg.
UNIT_FACTORS = {"ppb": 1.0, "ng/g": 1.0, "µg/kg": 1.0, "μg/kg": 1.0, "ug/kg": 1.0,
                "µg/l": 1.0, "μg/l": 1.0, "ug/l": 1.0, "ng/ml": 1.0,
                "ppm": 1000.0, "mg/kg": 1000.0, "mg/l": 1000.0, "µg/g": 1000.0, "μg/g": 1000.0,
                "ug/g": 1000.0}
ND_TOKENS = {"ND", "NOT DETECTED", "NON DETECTED", "NOTDETECTED", "BRL", "BLQ", "NQ", "<RL",
             "<LOD", "<LOQ", "<MDL", "BELOW RL", "BELOW REPORTING LIMIT"}
OK_KINDS = {"num", "zero", "lt", "nd"}

# Registered thresholds.
RL = 10.0                               # CFIA's reporting limit, ppb
C1_JUICE, C1_CONC = 7, 5                # samples at or above RL (37/44 and 55/60 below)
C2_JUICE, C2_CONC = "26.7", "24.0"      # printed maxima
ML = 50.0                               # Codex draft level quoted by CFIA
C4_ALPHA = 0.05
P3_CUT, P3_MIN = 15.0, 8                # quantified values below 15 ppb
P4_MAX = 1                              # domestic samples at or above RL
P5_ORIGIN, P5_MIN = "CHINA", 3
EU_INFANT = 10.0                        # EU 2023/915, apple products for infants (reference)

MONTHS = {m: i for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG",
                                      "SEP", "OCT", "NOV", "DEC"), start=1)}


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def _num(s):
    try:
        v = float(s)
    except ValueError:
        return None
    if v != v or v in (float("inf"), float("-inf")):
        return None
    return v


def parse_amount(raw):
    """(value, kind) for one AMOUNT cell under the registered rule.

    kind is one of: num, zero, lt, nd (pass the gate); blank, text, bad (fail it)."""
    s = (raw or "").strip()
    if s == "":
        return None, "blank"
    key = " ".join(s.upper().replace(".", "").split())
    if key in ND_TOKENS or key.replace(" ", "") in ND_TOKENS:
        return 0.0, "nd"
    if s.startswith("<"):
        rest = s[1:].strip()
        v = _num(rest)
        if v is not None and v > 0:
            return 0.0, "lt"
        return None, "text"
    try:
        v = float(s)
    except ValueError:
        return None, "text"
    if v != v or v < 0 or v == float("inf"):
        return None, "bad"
    if v == 0:
        return 0.0, "zero"
    return v, "num"


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
        "function": first(lambda c: c == "Function", "function"),
        "component": first(lambda c: c == "Component", "component"),
        "value": first(lambda c: c.upper() == "AMOUNT", "value"),
        "unit": first(lambda c: c.startswith("Report Unit") or c.startswith("Unit"), "unit"),
        "region": optional(lambda c: c.startswith("Region")),
        "date": optional(lambda c: c.startswith("Date Sampled")),
        "plan": optional(lambda c: c == "Plan Code"),
    }


def parse_date(text):
    """'7-Nov-08' -> '2008-11-07' (no locale); None if it does not parse."""
    parts = (text or "").strip().split("-")
    if len(parts) != 3 or parts[1].upper() not in MONTHS:
        return None
    try:
        d, y = int(parts[0]), int(parts[2])
    except ValueError:
        return None
    y = y + 2000 if y < 100 else y
    return f"{y:04d}-{MONTHS[parts[1].upper()]:02d}-{d:02d}"


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

    comps, kinds, units, products, origins, functions, plans = {}, {}, {}, {}, {}, {}, {}
    samples = {}
    for r in body:
        sid = clean(cell(r, "sample"))
        unit = clean(cell(r, "unit"))
        raw = clean(cell(r, "value"))
        value, kind = parse_amount(raw)
        factor = UNIT_FACTORS.get(unit.lower())
        _bump(comps, clean(cell(r, "component")))
        _bump(kinds, kind)
        _bump(units, unit)
        _bump(products, clean(cell(r, "product")))
        _bump(origins, clean(cell(r, "origin")))
        _bump(functions, clean(cell(r, "function")))
        _bump(plans, clean(cell(r, "plan")))
        rec = samples.get(sid)
        if rec is None:
            rec = samples[sid] = {"sample": sid, "rows": 0}
        rec["rows"] += 1
        ppb = value * factor if (kind == "num" and factor is not None) else 0.0
        rec.update({"product": clean(cell(r, "product")), "origin": clean(cell(r, "origin")),
                    "function": clean(cell(r, "function")), "region": clean(cell(r, "region")),
                    "date": clean(cell(r, "date")), "raw": raw, "kind": kind, "ppb": ppb})
    rps = {}
    for rec in samples.values():
        _bump(rps, str(rec["rows"]))
    census = {"n_rows": len(body), "distinct_samples": len(samples), "components": comps,
              "products": products, "origins": origins, "functions": functions, "units": units,
              "plans": plans, "value_kinds": kinds, "rows_per_sample": rps}
    return samples, census


def at_or_above(rec, cut):
    return rec["kind"] == "num" and rec["ppb"] >= cut - 1e-9


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def fisher_two_sided(a, b, c, d):
    r1, c1, n = a + b, a + c, a + b + c + d
    if n == 0:
        return 1.0

    def p(k):
        return math.comb(c1, k) * math.comb(n - c1, r1 - k) / math.comb(n, r1)

    obs = p(a)
    ks = range(max(0, c1 - (n - r1)), min(r1, c1) + 1)
    return min(1.0, sum(p(k) for k in ks if p(k) <= obs * (1 + 1e-7)))


def two_by_two(recs, in_group):
    """[a, b, c, d]: group at/above RL, group below, rest at/above, rest below."""
    a = sum(1 for r in recs if in_group(r) and at_or_above(r, RL))
    b = sum(1 for r in recs if in_group(r)) - a
    c = sum(1 for r in recs if not in_group(r) and at_or_above(r, RL))
    d = sum(1 for r in recs if not in_group(r)) - c
    return [a, b, c, d]


# ---------------------------------------------------------------------------
# Gate, analysis and grading.
# ---------------------------------------------------------------------------
def gate_checks(census, sha_ok):
    kinds = set(census["value_kinds"])
    return {
        "sha256": bool(sha_ok),
        "rows": census["n_rows"] == PA["rows"],
        "samples": census["distinct_samples"] == PA["samples"],
        "rows_per_sample": census["rows_per_sample"] == {"1": PA["samples"]},
        "products": census["products"] == PRODUCT_ROWS,
        "functions": census["functions"] == FUNCTION_ROWS,
        "origins": census["origins"] == ORIGIN_ROWS,
        "component": census["components"] == COMPONENT_ROWS,
        "unit": (len(census["units"]) == 1
                 and all(u.lower() in UNIT_FACTORS for u in census["units"])),
        "value_kinds": kinds <= OK_KINDS and "num" in kinds,
    }


def analyse(recs):
    by_product = {}
    for p in sorted({r["product"] for r in recs}):
        rs = [r for r in recs if r["product"] == p]
        q = [r["ppb"] for r in rs if at_or_above(r, RL)]
        by_product[p] = {"n": len(rs), "ge_rl": len(q), "max": max(q) if q else None}
    by_origin = {}
    for o in sorted({r["origin"] for r in recs}):
        rs = [r for r in recs if r["origin"] == o]
        by_origin[o] = {"n": len(rs), "ge_rl": sum(1 for r in rs if at_or_above(r, RL))}
    quantified = []
    for r in sorted((r for r in recs if at_or_above(r, RL)),
                    key=lambda r: (-r["ppb"], r["sample"])):
        quantified.append({k: r[k] for k in ("sample", "product", "origin", "function", "region",
                                             "date", "raw", "ppb")})
    china = two_by_two(recs, lambda r: r["origin"] == P5_ORIGIN)
    func = two_by_two(recs, lambda r: r["function"] == "imported")
    between = [r["ppb"] for r in recs if r["kind"] == "num" and 0 < r["ppb"] < RL - 1e-9]
    domestic = [r for r in recs if r["function"] == "domestic"]
    imported = [r for r in recs if r["function"] == "imported"]
    below_tokens = {}
    for r in recs:
        if r["kind"] != "num":
            _bump(below_tokens, r["raw"])
    dates = sorted(d for d in (parse_date(r["date"]) for r in recs) if d)
    return {
        "by_product": by_product, "by_origin": by_origin, "quantified": quantified,
        "n_ge_rl": len(quantified),
        "juice_ge": by_product.get(JUICE, {}).get("ge_rl"),
        "conc_ge": by_product.get(CONC, {}).get("ge_rl"),
        "juice_max": by_product.get(JUICE, {}).get("max"),
        "conc_max": by_product.get(CONC, {}).get("max"),
        "n_ge_ml": sum(1 for r in recs if at_or_above(r, ML)),
        "n_over_eu_infant": sum(1 for r in recs if r["kind"] == "num"
                                and r["ppb"] > EU_INFANT + 1e-9),
        "china_table": china, "china_p": fisher_two_sided(*china),
        "function_table": func, "function_p": fisher_two_sided(*func),
        "n_between": len(between), "between": sorted(between),
        "domestic_origins": sorted({r["origin"] for r in domestic}),
        "imported_canada": sum(1 for r in imported if r["origin"] == "CANADA"),
        "below_15": sum(1 for q in quantified if q["ppb"] < P3_CUT - 1e-9),
        "domestic_ge": sum(1 for r in domestic if at_or_above(r, RL)),
        "china_ge": china[0],
        "below_rl_entries": below_tokens,
        "date_min": dates[0] if dates else None, "date_max": dates[-1] if dates else None,
        "dates_parsed": len(dates),
    }


def grade(a, gate_obs):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "SHA-256; 104 rows and samples, one row each; product, function and origin "
                      "row counts; one component (Patulin); one known unit; every AMOUNT cell a "
                      "number, a literal 0, a '<' entry or an ND-type token, with numbers present"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    add("C1", "consistency",
        "the summary page: 7 of 44 apple juices and 5 of 60 concentrates at or above the 10 ppb "
        "reporting limit (37/44 and 55/60 below; 88.5% overall)",
        {"juice_ge": a["juice_ge"], "conc_ge": a["conc_ge"], "n_ge_rl": a["n_ge_rl"]},
        a["juice_ge"] == C1_JUICE and a["conc_ge"] == C1_CONC)
    add("C2", "consistency",
        "the summary page: maxima 26.7 ppb (apple juice) and 24.0 ppb (concentrate)",
        {"juice_max": a["juice_max"], "conc_max": a["conc_max"]},
        matches(a["juice_max"], C2_JUICE) and matches(a["conc_max"], C2_CONC))
    add("C3", "consistency", "the summary page: no sample at or above 50 ppb",
        {"n_ge_ml": a["n_ge_ml"]}, a["n_ge_ml"] == 0)
    add("C4", "consistency",
        "the summary page: origin not linked to patulin; Fisher two-sided p >= 0.05 for China "
        "against all other origins and for imported against domestic (at or above 10 ppb)",
        {"china_table": a["china_table"], "china_p": a["china_p"],
         "function_table": a["function_table"], "function_p": a["function_p"]},
        a["china_p"] >= C4_ALPHA and a["function_p"] >= C4_ALPHA)
    add("P1", "prediction",
        "no AMOUNT cell holds a number above 0 and below 10 ppb (the open file is censored at "
        "the reporting limit)",
        {"n_between": a["n_between"], "between": a["between"]}, a["n_between"] == 0)
    add("P2", "prediction",
        "every domestic sample declares CANADA, and no imported sample does",
        {"domestic_origins": a["domestic_origins"], "imported_canada": a["imported_canada"]},
        a["domestic_origins"] == ["CANADA"] and a["imported_canada"] == 0)
    add("P3", "prediction",
        "at least 8 of the quantified (>= 10 ppb) results are below 15 ppb",
        {"below_15": a["below_15"], "n_ge_rl": a["n_ge_rl"]}, a["below_15"] >= P3_MIN)
    add("P4", "prediction", "at most 1 of the 10 domestic samples is at or above 10 ppb",
        {"domestic_ge": a["domestic_ge"]}, a["domestic_ge"] <= P4_MAX)
    add("P5", "prediction", "at least 3 of the quantified samples declare China as origin",
        {"china_ge": a["china_ge"]}, a["china_ge"] >= P5_MIN)
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
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-patulin-2008"})
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
    with open(os.path.join(out_dir, "patulin_2008_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "origin", "function", "region", "date", "amount",
                    "kind", "ppb"])
        for r in sorted(recs, key=lambda x: x["sample"]):
            w.writerow([r["sample"], r["product"], r["origin"], r["function"], r["region"],
                        r["date"], r["raw"], r["kind"], repr(r["ppb"])])
    result = {"study": "patulin-2008", "version": VERSION, "predictions": preds,
              "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "patulin_2008_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the patulin-2008 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw, src = load(PA, args.data_dir)
    text, enc = decode(raw)
    samples, census = parse_text(text)
    recs = list(samples.values())
    gate_obs = gate_checks(census, _sha(raw) == PA["sha256"])
    a = analyse(recs)
    preds = grade(a, gate_obs)
    provenance = {"PA": {"resource": PA["resource"], "sha256": PA["sha256"], "bytes": len(raw),
                         "source": src, "encoding": enc}}
    result = write_outputs(args.out_dir, recs, census, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate_obs, "units": census["units"],
                      "value_kinds": census["value_kinds"],
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
