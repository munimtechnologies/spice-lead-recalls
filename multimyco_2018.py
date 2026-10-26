#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""multimyco_2018 0.1.0: CFIA's open 2018-19 multi-mycotoxin file against its own report.

Grades docs/multimyco-2018-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

The Canadian Food Inspection Agency (CFIA) released the per-sample file for its 2018-19
"Multi-Mycotoxins in Corn Products, Crackers, Other Grain Products, Pasta and Gluten-Free
Products" targeted survey on open.canada.ca (Open Government Licence - Canada). It holds 18,750
rows: 750 samples x 25 analyte rows each (24 distinct English `Component` labels, with
`?-Zearalenol(ppb)` appearing twice per sample). This reads the AMOUNT column for the first time
to settle five things the report leaves open (the 388-vs-386 detected count, the "17 mycotoxins
detected" claim and its mislabelled zeranols, the uncounted OTA compliance figure, the crackers
OTA gap against CFIA's separate OTA-only survey, and whether the pooled DON x fumonisin
co-occurrence is a commodity effect).

The file is SHA-256 pinned. The AMOUNT parse rule is registered: a cell is a non-detect if it is
blank, "0", starts with "<", or is a non-detect token; a positive is a plain decimal. Any cell
with a comma or otherwise unparseable fails the gate (so an unexpected numeric format is caught,
not silently misread). Standard library only. Code Apache-2.0; derived data CC BY 4.0. A
reference comparison, not a compliance finding (Canada has no mycotoxin maximum level for these
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

RESOURCE = "09a3c285-8552-4a38-b4be-cdf6d5fc3fd2"
DATASET = "03f184ee-e5e0-4e33-a763-fa3e44ed2dc0"
FILENAME = ("cfia_acia-1134_2018-19_multi-mycotoxins_in_selected_foods_-_2019-2019_"
            "presence-de-plusieurs-myco.csv")
SHA256 = "ba5084945f0a0e1fab2b8bab7f8f196a7dd0033d4bdc4e80768f12ec4c553835"

N_ROWS = 18750
N_SAMPLES = 750
ROWS_PER_SAMPLE = 25

# English `Component` labels and their row counts, from the names-only census (job
# myco-census-v2, 2026-10-25). `?-Zearalenol(ppb)` carries two rows per sample (alpha + beta).
COMPONENT_COUNTS = {
    "?-Zearalenol(ppb)": 1500,
    "15-acetyldeoxynivalenol": 750,
    "3-acetyldeoxynivalenol": 750,
    "Aflatoxin B1": 750,
    "Aflatoxin B2": 750,
    "Aflatoxin G1": 750,
    "Aflatoxin G2": 750,
    "Cyclopiazonic acid": 750,
    "Deoxynivalenol": 750,
    "Diacetoxyscirpenol": 750,
    "Ergocristine": 750,
    "Ergocryptine": 750,
    "Ergosine": 750,
    "Fumonisin B1": 750,
    "Fumonisin B2": 750,
    "Fumonisin B3": 750,
    "Fusarenon-X": 750,
    "HT-2 Toxin": 750,
    "Neosolaniol": 750,
    "Nivalenol": 750,
    "Ochratoxin A": 750,
    "Sterigmatocystin": 750,
    "T-2 Toxin": 750,
    "Zearalenone(ppb)": 750,
}

# Per-sample product-label counts (= row count / rows-per-label), from the same census.
PRODUCT_SAMPLES = {
    "Amaranth Products": 14, "Arrowroot Products": 15, "Barley Products": 14, "Bread": 2,
    "Buckwheat Products": 15, "Chips - Corn": 18, "Chips - Other": 1, "Corn Products": 30,
    "Corn Starch": 25, "Cornmeal": 25, "Crackers": 101, "Flour - Corn": 52,
    "Gluten-free Products": 71, "Grain - Barley": 36, "Grain - Buckwheat": 14,
    "Grain - Kamut": 13, "Grain - Other": 15, "Grain - Quinoa": 28, "Grain - Rye": 2,
    "Kamut Products": 15, "Millet Products": 14, "Millet": 15, "Pasta - Dry": 62,
    "Pasta - Fresh": 40, "Pasta": 26, "Quinoa Products": 15, "Rye Products": 26,
    "Spelt Products": 25, "Spelt": 5, "Teff Products": 16,
}
ORIGIN_CANADA, ORIGIN_UNKNOWN, ORIGIN_FOREIGN, ORIGIN_DISTINCT = 155, 291, 304, 30

PLAN = "2018_SB427"

# Toxin groups: a group is "detected" in a sample if any member label is detected. The report
# prints the ZEN group as "ZEN/alpha-ZOL/beta-ZOL" but its zeranols (= the file's zearalenols)
# are listed as never detected, so the registered hypothesis is that Zearalenone alone carries
# the 34 group positives.
GROUPS = {
    "DON": ("Deoxynivalenol",),
    "Fumonisins": ("Fumonisin B1", "Fumonisin B2", "Fumonisin B3"),
    "Ergot": ("Ergocristine", "Ergocryptine", "Ergosine"),
    "Zearalenone": ("Zearalenone(ppb)",),
    "OTA": ("Ochratoxin A",),
    "CPA": ("Cyclopiazonic acid",),
    "STE": ("Sterigmatocystin",),
    "Aflatoxins": ("Aflatoxin B1", "Aflatoxin B2", "Aflatoxin G1"),
    "HT2T2": ("HT-2 Toxin", "T-2 Toxin"),
    "NIV": ("Nivalenol",),
}
TABLE3_SAMPLES = {"DON": 306, "Fumonisins": 105, "Ergot": 46, "Zearalenone": 34, "OTA": 20,
                  "CPA": 18, "STE": 12, "Aflatoxins": 11, "HT2T2": 8, "NIV": 7}
NON_DON_GROUPS = ("Fumonisins", "Ergot", "Zearalenone", "OTA", "CPA", "STE", "Aflatoxins",
                  "HT2T2", "NIV")

# The 7 English labels the report says (reading its "zeranols" as the zearalenols) are never
# detected; 24 labels - 7 = 17 detected analytes.
NEVER_DETECTED = frozenset((
    "?-Zearalenol(ppb)", "15-acetyldeoxynivalenol", "3-acetyldeoxynivalenol", "Aflatoxin G2",
    "Diacetoxyscirpenol", "Fusarenon-X", "Neosolaniol"))
N_DETECTED_ANALYTES = 17

# Printed (max ppb, average-of-positives ppb) for single-analyte groups, from Table 3.
SINGLE_MAXAVG = {"DON": ("2570", "282"), "OTA": ("34", "4.2"), "CPA": ("47", "11"),
                 "STE": ("12", "2.7"), "NIV": ("86", "22")}

CORN_PRODUCTS = frozenset((
    "Flour - Corn", "Corn Products", "Corn Starch", "Cornmeal", "Chips - Corn"))

ND_TOKENS = ("nd", "n.d.", "n/d", "not detected", "non détecté", "non detecte")

ANY_DETECTED_SAMPLES = 386        # P1: Table 2 grand total (text says 388)
OTA_LEVEL, OTA_OVER = 3.0, 7      # P5: proposed OTA level and the 99.1%-implied count
CRACKERS_OTA_MAX_RATE = 0.25      # P6: far below the OTA-only survey's 30/40 = 75%
MAX_GROUPS = 9                    # P8: up to 9 toxin groups in one sample (corn)


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def parse_amount(raw):
    """(ppb, detected, kind) for one AMOUNT cell under the registered rule.

    kind is one of: blank, lt, nd, zero, comma (ambiguous -> gate fails), bad, pos."""
    s = (raw or "").strip()
    if s == "":
        return 0.0, False, "blank"
    if s.startswith("<"):
        return 0.0, False, "lt"
    if s.lower() in ND_TOKENS:
        return 0.0, False, "nd"
    if "," in s:
        return None, False, "comma"
    try:
        v = float(s)
    except ValueError:
        return None, False, "bad"
    if v != v or v < 0:
        return None, False, "bad"
    if v == 0:
        return 0.0, False, "zero"
    return v, True, "pos"


def matches(x, printed):
    """Does x round to the printed figure at the printed precision?"""
    if x is None:
        return False
    d = len(printed.split(".")[1]) if "." in printed else 0
    return abs(x - float(printed)) <= 0.5 * 10 ** (-d) + 1e-9


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
        "amount": first(lambda c: c == "AMOUNT", "amount"),
        "unit": first(lambda c: c.startswith("Report Unit"), "report unit"),
        "plan": first(lambda c: c == "Plan Code", "plan code"),
    }


def _bump(d, k):
    d[k] = d.get(k, 0) + 1


def parse_text(text):
    """(rows, census) from the decoded CSV text."""
    table = list(csv.reader(io.StringIO(text)))
    header = table[0]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    col = find_columns(header)

    def cell(r, k):
        i = col[k]
        return r[i] if i < len(r) else ""

    rows = []
    comps, kinds, units, plans = {}, {}, {}, {}
    amount_strings = set()
    sample_product, sample_origin, sample_function = {}, {}, {}
    per_sample_rows = {}
    for r in body:
        raw = cell(r, "amount")
        ppb, det, kind = parse_amount(raw)
        comp = clean(cell(r, "component"))
        sample = clean(cell(r, "sample"))
        product = clean(cell(r, "product"))
        origin = clean(cell(r, "origin"))
        function = clean(cell(r, "function"))
        _bump(comps, comp)
        _bump(kinds, kind)
        _bump(units, clean(cell(r, "unit")))
        _bump(plans, clean(cell(r, "plan")))
        _bump(per_sample_rows, sample)
        amount_strings.add((raw or "").strip())
        sample_product.setdefault(sample, product)
        sample_origin.setdefault(sample, origin)
        sample_function.setdefault(sample, function)
        rows.append({"sample": sample, "product": product, "origin": origin,
                     "function": function, "component": comp, "raw": raw,
                     "ppb": ppb, "detected": det})
    products, origins, functions = {}, {}, {}
    for s in sample_product:
        _bump(products, sample_product[s])
        _bump(origins, sample_origin[s])
        _bump(functions, sample_function[s])
    rps = {}
    for v in per_sample_rows.values():
        _bump(rps, str(v))
    census = {
        "n_rows": len(rows), "distinct_samples": len(per_sample_rows), "components": comps,
        "products": products, "origins": origins, "functions": functions, "plans": plans,
        "units": units, "amount_kinds": kinds, "amount_distinct": len(amount_strings),
        "rows_per_sample": rps,
    }
    return rows, census


def gate_checks(census, sha_ok):
    kinds = census["amount_kinds"]
    origins = census["origins"]
    foreign = sum(n for o, n in origins.items() if o not in ("CANADA", "UNKNOWN"))
    return {
        "sha256": bool(sha_ok),
        "rows": census["n_rows"] == N_ROWS,
        "samples": census["distinct_samples"] == N_SAMPLES,
        "rows_per_sample": census["rows_per_sample"] == {str(ROWS_PER_SAMPLE): N_SAMPLES},
        "components": census["components"] == COMPONENT_COUNTS,
        "products": census["products"] == PRODUCT_SAMPLES,
        "one_plan": census["plans"] == {PLAN: N_ROWS},
        "one_unit": len(census["units"]) == 1,
        "origin_canada": origins.get("CANADA") == ORIGIN_CANADA,
        "origin_unknown": origins.get("UNKNOWN") == ORIGIN_UNKNOWN,
        "origin_foreign": foreign == ORIGIN_FOREIGN,
        "origin_distinct": len(origins) == ORIGIN_DISTINCT,
        "amount_format": kinds.get("bad", 0) == 0 and kinds.get("comma", 0) == 0
        and kinds.get("pos", 0) > 0,
    }


def sample_detections(rows):
    """{sample: set(detected English component labels)}."""
    dets = {}
    for r in rows:
        s = dets.setdefault(r["sample"], set())
        if r["detected"]:
            s.add(r["component"])
    return dets


def any_detected_count(dets):
    return sum(1 for s in dets.values() if s)


def group_count(dets, labels):
    L = set(labels)
    return sum(1 for s in dets.values() if s & L)


def detected_labels(dets):
    out = set()
    for s in dets.values():
        out |= s
    return out


def analyte_detected_values(rows, comp):
    return [r["ppb"] for r in rows if r["component"] == comp and r["detected"]]


def analyte_all_values(rows, comp):
    return [r["ppb"] for r in rows if r["component"] == comp and r["ppb"] is not None]


def groups_in_sample(detset):
    return sum(1 for labs in GROUPS.values() if detset & set(labs))


def cooc_items(rows, xlabels, ylabels):
    """[(product, x_detected, y_detected)] one entry per sample."""
    xs, ys = set(xlabels), set(ylabels)
    by = {}
    for r in rows:
        s = by.setdefault(r["sample"], {"product": r["product"], "x": False, "y": False})
        if r["detected"]:
            if r["component"] in xs:
                s["x"] = True
            if r["component"] in ys:
                s["y"] = True
    return [(v["product"], v["x"], v["y"]) for v in by.values()]


def cells(items):
    """Pooled (a, b, c, d): a = x&y, b = x only, c = y only, d = neither."""
    a = b = c = d = 0
    for _, x, y in items:
        if x and y:
            a += 1
        elif x:
            b += 1
        elif y:
            c += 1
        else:
            d += 1
    return a, b, c, d


def odds_ratio(a, b, c, d):
    if 0 in (a, b, c, d):
        return ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
    return (a * d) / (b * c)


def strata_tables(items):
    groups = {}
    for it in items:
        groups.setdefault(it[0], []).append(it)
    return {k: cells(v) for k, v in sorted(groups.items())}


def mantel_haenszel(tables):
    num = den = 0.0
    for a, b, c, d in tables:
        n = a + b + c + d
        if n == 0:
            continue
        num += a * d / n
        den += b * c / n
    return (num / den if den > 0 else None), num, den


def cmh_test(tables):
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


def cooc_analysis(rows, xlabels, ylabels):
    items = cooc_items(rows, xlabels, ylabels)
    pooled = cells(items)
    st = strata_tables(items)
    mh, num, den = mantel_haenszel(list(st.values()))
    chi2, p = cmh_test(list(st.values()))
    return {"pooled": list(pooled), "pooled_or": odds_ratio(*pooled), "mh_or": mh,
            "cmh_chi2": chi2, "cmh_p": p, "n_strata": len(st)}


def analyse(rows):
    dets = sample_detections(rows)
    labels_det = detected_labels(dets)
    groups = {g: group_count(dets, labs) for g, labs in GROUPS.items()}
    analytes = {}
    for name in ("DON", "OTA", "CPA", "STE", "NIV"):
        comp = GROUPS[name][0]
        det_vals = analyte_detected_values(rows, comp)
        all_vals = analyte_all_values(rows, comp)
        analytes[name] = {
            "n_detected": len(det_vals),
            "max": max(det_vals) if det_vals else None,
            "avg_pos": statistics.fmean(det_vals) if det_vals else None,
            "avg_all": statistics.fmean(all_vals) if all_vals else None,
        }
    cr_samples = {r["sample"] for r in rows if r["product"] == "Crackers"}
    cr_ota = {r["sample"] for r in rows
              if r["product"] == "Crackers" and r["component"] == "Ochratoxin A" and r["detected"]}
    ota_over = sum(1 for r in rows if r["component"] == "Ochratoxin A"
                   and r["ppb"] is not None and r["ppb"] > OTA_LEVEL)
    per_sample_groups = {s: groups_in_sample(d) for s, d in dets.items()}
    max_g = max(per_sample_groups.values()) if per_sample_groups else 0
    sample_product = {}
    for r in rows:
        sample_product.setdefault(r["sample"], r["product"])
    max_g_products = sorted({sample_product[s] for s, g in per_sample_groups.items() if g == max_g})
    return {
        "any_detected": any_detected_count(dets),
        "groups": groups,
        "n_detected_analytes": len(labels_det),
        "detected_analytes": sorted(labels_det),
        "never_detected": sorted(set(COMPONENT_COUNTS) - labels_det),
        "analytes": analytes,
        "crackers_n": len(cr_samples), "crackers_ota_n": len(cr_ota),
        "crackers_ota_rate": (len(cr_ota) / len(cr_samples)) if cr_samples else None,
        "ota_over_3": ota_over,
        "max_groups": max_g, "max_groups_products": max_g_products,
        "don_fumonisin": cooc_analysis(rows, GROUPS["DON"], GROUPS["Fumonisins"]),
    }


# ---------------------------------------------------------------------------
# Grading.
# ---------------------------------------------------------------------------
def grade(a, gate_obs):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "SHA-256, 18,750 rows / 750 samples / 25 rows each, the 24 component "
                      "labels and 30 product labels by count, one plan code, one report unit, "
                      "origin split (CANADA 155, UNKNOWN 291, 304 foreign over 30 origins), and "
                      "a clean AMOUNT format (no comma or unparseable cell)"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    add("P1", "prediction",
        "exactly 386 of 750 samples carry >=1 detected mycotoxin (Table 2's grand total), not the "
        "388 the summary text prints",
        {"any_detected": a["any_detected"], "table2": 386, "text": 388},
        a["any_detected"] == ANY_DETECTED_SAMPLES)

    don = a["analytes"]["DON"]
    add("P2", "prediction",
        "DON detected in 306 of 750 samples; maximum 2570 and average-of-positives 282 ppb",
        {"n_detected": a["groups"]["DON"], "max": don["max"], "avg_pos": don["avg_pos"],
         "avg_all": don["avg_all"]},
        a["groups"]["DON"] == TABLE3_SAMPLES["DON"] and matches(don["max"], "2570")
        and matches(don["avg_pos"], "282"))

    add("P3", "prediction",
        "exactly 17 of the 24 English component labels are detected in >=1 sample; the 7 never "
        "detected are the two zearalenols (one `?-Zearalenol(ppb)` label), 3- and "
        "15-acetyl-DON, aflatoxin G2, diacetoxyscirpenol, fusarenon-X and neosolaniol -- so the "
        "report's 'alpha-/beta-zeranol' are its zearalenols and Zearalenone alone carries the 34 "
        "ZEN-group positives",
        {"n_detected_analytes": a["n_detected_analytes"], "never_detected": a["never_detected"]},
        a["n_detected_analytes"] == N_DETECTED_ANALYTES
        and frozenset(a["never_detected"]) == NEVER_DETECTED)

    groups_ok = {g: (a["groups"][g], TABLE3_SAMPLES[g]) for g in NON_DON_GROUPS}
    add("P4", "prediction",
        "the nine non-DON toxin groups reproduce CFIA's Table 3 positive counts exactly "
        "(fumonisins 105, ergot 46, Zearalenone 34, OTA 20, CPA 18, sterigmatocystin 12, "
        "aflatoxins 11, HT-2/T-2 8, nivalenol 7)",
        {g: {"file": a["groups"][g], "table3": TABLE3_SAMPLES[g]} for g in NON_DON_GROUPS},
        all(a["groups"][g] == TABLE3_SAMPLES[g] for g in NON_DON_GROUPS))

    c1 = {}
    c1_ok = True
    for name in ("OTA", "CPA", "STE", "NIV"):
        mx, av = SINGLE_MAXAVG[name]
        an = a["analytes"][name]
        ok = matches(an["max"], mx) and matches(an["avg_pos"], av)
        c1_ok = c1_ok and ok
        c1[name] = {"max": an["max"], "printed_max": mx, "avg_pos": an["avg_pos"],
                    "printed_avg": av, "ok": ok}
    add("C1", "consistency",
        "the four single-analyte groups match Table 3's max and average-of-positives (OTA 34/4.2, "
        "CPA 47/11, sterigmatocystin 12/2.7, nivalenol 86/22 ppb)", c1, c1_ok)

    add("P5", "prediction",
        "exactly 7 of 750 samples carry OTA above the proposed 3 ppb level (CFIA prints only a "
        "99.1% compliance rate, no count)",
        {"ota_over_3": a["ota_over_3"], "implied": OTA_OVER}, a["ota_over_3"] == OTA_OVER)

    add("P6", "prediction",
        "OTA is detected in fewer than 25% of the 101 crackers, far below the 75% (30 of 40) "
        "CFIA reported for the same year's OTA-only crackers survey -- pointing to a higher "
        "detection limit in this multi-toxin method",
        {"crackers_n": a["crackers_n"], "crackers_ota_n": a["crackers_ota_n"],
         "crackers_ota_rate": a["crackers_ota_rate"]},
        a["crackers_ota_rate"] is not None and a["crackers_ota_rate"] < CRACKERS_OTA_MAX_RATE)

    df = a["don_fumonisin"]
    attenuated = (df["mh_or"] is not None and df["mh_or"] > 0 and df["pooled_or"] > 0
                  and abs(math.log(df["mh_or"])) < abs(math.log(df["pooled_or"])))
    add("P7", "prediction",
        "the pooled DON x fumonisin co-occurrence (odds ratio > 1) is mostly composition: within "
        "the finest product label the Mantel-Haenszel odds ratio is pulled toward 1 "
        "(|ln MH| < |ln pooled|), as cooc-strata found for OTA x DON",
        {"pooled": df["pooled"], "pooled_or": df["pooled_or"], "mh_or": df["mh_or"],
         "cmh_p": df["cmh_p"], "n_strata": df["n_strata"]},
        df["pooled_or"] > 1 and attenuated)

    add("P8", "prediction",
        "the most toxin groups detected in any one sample is 9 (of 10), and that sample is a "
        "corn-type product",
        {"max_groups": a["max_groups"], "max_groups_products": a["max_groups_products"]},
        a["max_groups"] == MAX_GROUPS
        and any(p in CORN_PRODUCTS for p in a["max_groups_products"]))
    return preds


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _fetch(url, tries=3, pause=8):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-multimyco-2018"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(data_dir):
    path = os.path.join(data_dir, RESOURCE + ".csv") if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == SHA256:
            return raw, "data-volume"
    urls = (
        f"https://open.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILENAME}",
        f"https://ouvert.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILENAME}",
        (f"https://active.inspection.gc.ca/opengov/{RESOURCE}/{FILENAME}"),
    )
    errors = []
    for url in urls:
        try:
            raw = _fetch(url, tries=2, pause=5)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        if _sha(raw) != SHA256:
            errors.append(f"{url}: SHA-256 {_sha(raw)} != {SHA256}")
            continue
        if path:
            try:
                os.makedirs(data_dir, exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(raw)
            except OSError:
                pass
        return raw, url
    raise RuntimeError("no verified copy: " + "; ".join(errors))


def decode(raw):
    for enc in ("cp1252", "utf-8-sig"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


# ---------------------------------------------------------------------------
# Outputs.
# ---------------------------------------------------------------------------
def _r(x):
    return "" if x is None else (round(x, 4) if isinstance(x, float) else x)


def write_outputs(out_dir, rows, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    # Per-sample detection matrix (one row per sample, one column per toxin group), so the counts
    # and the co-occurrence are reproducible without re-reading the raw file.
    dets = sample_detections(rows)
    sample_meta = {}
    for r in rows:
        sample_meta.setdefault(r["sample"], (r["product"], r["origin"]))
    with open(os.path.join(out_dir, "multimyco_2018_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "origin", "n_groups"] + list(GROUPS))
        for s in sorted(dets):
            dset = dets[s]
            prod, orig = sample_meta[s]
            flags = [int(bool(dset & set(labs))) for labs in GROUPS.values()]
            w.writerow([s, prod, orig, groups_in_sample(dset)] + flags)
    result = {"study": "multimyco-2018", "version": VERSION, "predictions": preds,
              "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "multimyco_2018_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the multimyco-2018 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw, source = load(args.data_dir)
    text, enc = decode(raw)
    rows, census = parse_text(text)
    sha_ok = _sha(raw) == SHA256
    gate_obs = gate_checks(census, sha_ok)
    a = analyse(rows)
    preds = grade(a, gate_obs)
    provenance = {"resource": RESOURCE, "sha256": SHA256, "bytes": len(raw), "source": source,
                  "encoding": enc}
    result = write_outputs(args.out_dir, rows, census, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate_obs,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"]}, indent=2, default=_r))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
