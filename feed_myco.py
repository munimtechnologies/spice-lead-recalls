#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""feed_myco 0.1.0: CFIA's open livestock-feed mycotoxin file (2000-2018) against its own report.

Grades docs/feed-myco-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes, under the Open Government Licence - Canada,
the per-result file of its "Mycotoxin Monitoring Program for Livestock Feeds" for April 1, 2000 -
March 31, 2018 (dataset 2d636f59-5f04-4725-afae-376850bc71d4; English CSV resource
b8cad53e-0a93-4366-a764-246fbc980c1f; 40,862 results on 3,258 samples, 17 analytes). CFIA also
published a summary report of the same program, "National feed inspection program: results for
Program-15B (April 1, 1990 - March 31, 2018)", whose Table 1 prints, for each fiscal year and
each of seven mycotoxins, the share of samples below the lowest action level (AL) and the number
of samples tested.

This reads the file for the first time to (1) rebuild every 2000-2018 cell of that Table 1 from
the open file (6 x 18 sample counts, 7 x 18 percentages), (2) test a registered explanation of
the one place the report and file disagree in size (HT-2: 3,202 samples in the report, 3,243 rows
in the file), and (3) register blind predictions on what the file shows beyond the report:
within-sample co-occurrence of Fusarium toxins, the 3-acetyl-DON versus 15-acetyl-DON split by
region and period (a chemotype proxy), fumonisins in corn, and the drift of the censoring limits.

The file is SHA-256 pinned. Standard library only. Code Apache-2.0; derived data CC BY 4.0.
A reference comparison, not a compliance finding about any feed, mill, brand or farm, and not
individual veterinary advice.
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

DATASET = "2d636f59-5f04-4725-afae-376850bc71d4"
RESOURCE = "b8cad53e-0a93-4366-a764-246fbc980c1f"
FILENAME = ("Mycotoxin_Monitoring_Program_for_Livestock_Feeds_-_Results_from_"
            "April_1_2000_-_March_31_2018.csv")
URLS = (
    "https://active.inspection.gc.ca/opengov/eng/open-data/" + FILENAME,
    f"https://open.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILENAME}",
    f"https://ouvert.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILENAME}",
)
SHA256 = "6de28d69d6d2fe0552aae55720b2b481b6673efafbcccf90dc87f7002a2c1491"

# Gate: facts already known from the names-only census (job feed-myco-census-v1, 2026-10-25).
N_ROWS = 40862
N_SAMPLES = 3258
COLUMNS = ["Fiscal Year", "System ID", "Target Species", "Feed Type", "Ingredient Type",
           "Ingredient Common Name", "Sampled at - Province", "Mycotoxin", "Test Result", "Unit"]
UNITS = {"mg/kg": 32019, "µg/kg": 8843}
LABELS = {
    "15-Acetyldeoxynivalenol": 3244, "3-AcetyldeoxyNivalenol": 184,
    "3-Acetyldeoxynivalenol": 3063, "Aflatoxin B1": 699, "Aflatoxin B2": 699,
    "Aflatoxin G1": 699, "Aflatoxin G2": 697, "Aflatoxins (total)": 713,
    "Deoxynivalenol": 3238, "Diacetoxyscirpenol": 3247, "Fumonisins (total B1 and B2)": 1673,
    "Fusarenon X": 3247, "HT-2": 3243, "Neosolaniol": 3247, "Nivalenol": 3246,
    "Ochratoxin A": 3240, "T-2": 3243, "Zearalenone": 3240,
}
RESULT_KINDS = {"censored": 35368, "numeric": 5494}

# Labels -> analyte codes (case-insensitive: the file spells 3-acetyl-DON two ways).
CANON = {
    "deoxynivalenol": "DON", "3-acetyldeoxynivalenol": "3-ADON",
    "15-acetyldeoxynivalenol": "15-ADON", "nivalenol": "NIV", "fusarenon x": "FUSX",
    "neosolaniol": "NEO", "diacetoxyscirpenol": "DAS", "ht-2": "HT-2", "t-2": "T-2",
    "zearalenone": "ZEA", "ochratoxin a": "OTA", "fumonisins (total b1 and b2)": "FUM",
    "aflatoxin b1": "AFB1", "aflatoxin b2": "AFB2", "aflatoxin g1": "AFG1",
    "aflatoxin g2": "AFG2", "aflatoxins (total)": "AFT",
}
ANALYTES = ("DON", "3-ADON", "15-ADON", "NIV", "FUSX", "NEO", "DAS", "HT-2", "T-2", "ZEA",
            "OTA", "FUM", "AFB1", "AFB2", "AFG1", "AFG2", "AFT")
AFLATOXINS = ("AFB1", "AFB2", "AFG1", "AFG2", "AFT")

# Divisor from the row's unit to mg/kg (= ppm).
TO_PPM = {"mg/kg": 1.0, "µg/kg": 1000.0, "μg/kg": 1000.0, "ug/kg": 1000.0}
EPS = 1e-9

YEARS = tuple(f"{y}-{y + 1}" for y in range(2000, 2018))
WEST = ("Alberta", "British Columbia", "Manitoba", "Saskatchewan")
EARLY, LATE = YEARS[:9], YEARS[9:]                 # 2000-01..2008-09 vs 2009-10..2017-18
LIMIT_EARLY, LIMIT_LATE = YEARS[:4], YEARS[14:]    # 2000-01..2003-04 vs 2014-15..2017-18
HT2_EARLY, HT2_LATER = YEARS[:13], YEARS[13:]      # 2000-01..2012-13 vs 2013-14..2017-18

# CFIA Program-15B report, Table 1: lowest action level (ppm) per mycotoxin, and for each fiscal
# year the printed "% of samples below the lowest AL" with the number of samples tested.
REPORT_ORDER = ("DON", "HT-2", "T-2", "DAS", "FUM", "OTA", "ZEA")
REPORT_AL = {"DON": 1.0, "HT-2": 0.1, "T-2": 1.0, "DAS": 1.0, "FUM": 1.0, "OTA": 0.2, "ZEA": 1.0}
_T1 = {  # year: DON, HT-2, T-2, DAS, FUM, OTA, ZEA as (printed %, n)
    "2000-2001": (("82.25", 169), ("97.63", 169), ("100.00", 169), ("100.00", 169),
                  ("100.00", 80), ("100.00", 169), ("100.00", 169)),
    "2001-2002": (("83.09", 136), ("97.06", 136), ("100.00", 136), ("100.00", 136),
                  ("100.00", 44), ("100.00", 136), ("100.00", 136)),
    "2002-2003": (("91.72", 169), ("98.82", 169), ("100.00", 169), ("100.00", 169),
                  ("90.48", 63), ("100.00", 169), ("100.00", 169)),
    "2003-2004": (("73.80", 187), ("96.26", 187), ("100.00", 187), ("100.00", 187),
                  ("94.52", 73), ("100.00", 187), ("100.00", 187)),
    "2004-2005": (("75.63", 197), ("96.45", 197), ("100.00", 197), ("100.00", 197),
                  ("100.00", 83), ("100.00", 196), ("100.00", 196)),
    "2005-2006": (("85.96", 114), ("94.74", 114), ("100.00", 114), ("100.00", 114),
                  ("91.84", 49), ("100.00", 114), ("100.00", 114)),
    "2006-2007": (("70.62", 194), ("88.66", 194), ("100.00", 194), ("100.00", 194),
                  ("94.79", 96), ("100.00", 193), ("97.41", 193)),
    "2007-2008": (("74.40", 168), ("93.45", 168), ("100.00", 168), ("100.00", 168),
                  ("96.30", 81), ("100.00", 170), ("98.81", 168)),
    "2008-2009": (("71.43", 224), ("95.98", 224), ("100.00", 224), ("100.00", 224),
                  ("96.59", 88), ("100.00", 223), ("99.55", 224)),
    "2009-2010": (("75.60", 209), ("97.13", 209), ("100.00", 209), ("100.00", 209),
                  ("98.02", 101), ("100.00", 210), ("100.00", 209)),
    "2010-2011": (("77.99", 209), ("94.74", 209), ("100.00", 211), ("100.00", 211),
                  ("99.08", 109), ("99.53", 212), ("99.53", 211)),
    "2011-2012": (("68.81", 202), ("96.91", 194), ("100.00", 209), ("100.00", 209),
                  ("94.55", 110), ("100.00", 208), ("100.00", 208)),
    "2012-2013": (("75.25", 198), ("94.65", 187), ("100.00", 198), ("100.00", 198),
                  ("83.33", 78), ("100.00", 197), ("100.00", 198)),
    "2013-2014": (("83.65", 159), ("95.21", 146), ("100.00", 159), ("100.00", 159),
                  ("89.19", 74), ("100.00", 158), ("100.00", 159)),
    "2014-2015": (("81.64", 207), ("98.49", 199), ("100.00", 199), ("100.00", 207),
                  ("100.00", 108), ("100.00", 199), ("100.00", 199)),
    "2015-2016": (("81.94", 144), ("98.61", 144), ("100.00", 144), ("100.00", 144),
                  ("100.00", 85), ("100.00", 143), ("100.00", 144)),
    "2016-2017": (("86.31", 168), ("92.90", 169), ("100.00", 169), ("100.00", 168),
                  ("98.17", 164), ("100.00", 169), ("100.00", 169)),
    "2017-2018": (("83.70", 184), ("92.51", 187), ("100.00", 187), ("100.00", 184),
                  ("98.40", 187), ("100.00", 187), ("100.00", 187)),
}
TABLE1 = {y: dict(zip(REPORT_ORDER, cells)) for y, cells in _T1.items()}

AFLA_LEVEL = 0.020  # 20 ppb, the feed aflatoxin level the report cites

# Pre-registered bounds (inclusive unless stated).
C1_MIN, C2_MIN, C3_MIN, C4_MIN, C6_MIN = 107, 17, 16, 85, 16
P2_SHARE = (0.35, 0.75)
P3_OR, P4_OR = 3.0, 10.0
P9_RATIO = 3.0
P12_MAX_SHARE = 0.05
MIN_GROUP = 10
MIN_FUM_GROUP = 30


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def clean(cell):
    return (cell or "").replace("﻿", "").strip()


def _num(s):
    t = s.strip()
    if t.count(",") == 1 and "." not in t:
        t = t.replace(",", ".")
    try:
        v = float(t)
    except ValueError:
        return None
    if v != v or v < 0:
        return None
    return v


def classify_result(raw):
    """FORMAT kind of one Test-result cell, exactly as the names-only census classified it."""
    s = clean(raw)
    if not s:
        return "blank"
    low = s.lower()
    if s.startswith("<") and low not in ("<loq", "< loq"):
        return "censored"
    if low in ("nd", "n.d.", "n/d", "not detected", "<loq", "< loq"):
        return "token"
    v = _num(s)
    if v is None:
        return "bad"
    return "zero" if v == 0 else "numeric"


def parse_result(raw):
    """(value, detected, limit) in the row's own unit under the registered rule.

    "<x" is a below-LOQ non-detect with censoring limit x (None if x does not parse); a number
    above 0 is a detection; 0 is a non-detect without a limit; anything else is unparseable
    (value None).
    """
    s = clean(raw)
    if s.startswith("<"):
        return 0.0, False, _num(s[1:])
    if not s:
        return None, False, None
    v = _num(s)
    if v is None:
        return None, False, None
    return v, v > 0, None


def to_ppm(value, unit):
    div = TO_PPM.get(unit)
    if value is None or div is None:
        return None
    return value / div


def canon(label):
    return CANON.get(clean(label).lower())


def matches(x, printed):
    """Does x round to the printed figure at the printed precision?"""
    if x is None:
        return False
    d = len(printed.split(".")[1]) if "." in printed else 0
    return abs(x - float(printed)) <= 0.5 * 10 ** (-d) + 1e-9


def find_col(header, *needles):
    for i, c in enumerate(header):
        name = clean(c).lower()
        if all(n in name for n in needles):
            return i
    return None


def _bump(d, k):
    d[k] = d.get(k, 0) + 1


def parse_text(text):
    """(rows, check) from the decoded CSV text."""
    table = list(csv.reader(io.StringIO(text)))
    header = [clean(c) for c in table[0]]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    col = {
        "year": find_col(header, "fiscal"), "sid": find_col(header, "system"),
        "species": find_col(header, "species"), "feed_type": find_col(header, "feed", "type"),
        "ingredient_type": find_col(header, "ingredient", "type"),
        "ingredient_name": find_col(header, "ingredient", "name"),
        "province": find_col(header, "province"), "label": find_col(header, "mycotoxin"),
        "result": find_col(header, "result"), "unit": find_col(header, "unit"),
    }

    def cell(r, k):
        i = col[k]
        return clean(r[i]) if i is not None and i < len(r) else ""

    rows, kinds, units, labels, per_sample = [], {}, {}, {}, {}
    for r in body:
        raw = cell(r, "result")
        unit = cell(r, "unit")
        label = cell(r, "label")
        _bump(kinds, classify_result(raw))
        _bump(units, unit)
        _bump(labels, label)
        sid = cell(r, "sid")
        _bump(per_sample, sid)
        value, detected, limit = parse_result(raw)
        rows.append({
            "year": cell(r, "year"), "sid": sid, "species": cell(r, "species"),
            "feed_type": cell(r, "feed_type"), "ingredient_type": cell(r, "ingredient_type"),
            "ingredient_name": cell(r, "ingredient_name"), "province": cell(r, "province"),
            "label": label, "analyte": canon(label), "unit": unit, "raw": raw,
            "value": value, "detected": detected, "limit": limit,
            "ppm": to_ppm(value, unit), "limit_ppm": to_ppm(limit, unit),
        })
    check = {
        "header": header, "n_rows": len(rows), "distinct_samples": len(per_sample),
        "units": units, "labels": labels, "result_kinds": kinds,
        "unparsed": sum(1 for r in rows if r["value"] is None),
        "unknown_analyte": sum(1 for r in rows if r["analyte"] is None),
        "unknown_unit": sum(1 for r in rows if r["unit"] not in TO_PPM),
    }
    return rows, check


def gate(check, sha_ok):
    checks = {
        "sha256": bool(sha_ok),
        "columns": check["header"] == COLUMNS,
        "rows": check["n_rows"] == N_ROWS,
        "samples": check["distinct_samples"] == N_SAMPLES,
        "units": check["units"] == UNITS,
        "labels": check["labels"] == LABELS,
        "result_kinds": check["result_kinds"] == RESULT_KINDS,
    }
    return all(checks.values()), checks


def is_below(r, al, inclusive=False):
    """Below the action level under the registered rule (a non-detect counts as below)."""
    if r["value"] is None:
        return False
    if not r["detected"]:
        return True
    if r["ppm"] is None:
        return False
    return r["ppm"] <= al + EPS if inclusive else r["ppm"] < al - EPS


def is_indeterminate(r, al):
    """A non-detect whose censoring limit lies above the action level."""
    return (r["value"] is not None and not r["detected"] and r["limit_ppm"] is not None
            and r["limit_ppm"] > al + EPS)


def table1_cells(rows):
    """One record per (fiscal year, report mycotoxin): the file beside Table 1's print."""
    groups = {}
    for r in rows:
        if r["analyte"] in REPORT_AL and r["year"] in TABLE1:
            groups.setdefault((r["year"], r["analyte"]), []).append(r)
    out = []
    for year in YEARS:
        for an in REPORT_ORDER:
            pct_s, n_print = TABLE1[year][an]
            al = REPORT_AL[an]
            g = groups.get((year, an), [])
            n = len(g)
            below = sum(1 for r in g if is_below(r, al))
            below_le = sum(1 for r in g if is_below(r, al, inclusive=True))
            indet = sum(1 for r in g if is_indeterminate(r, al))
            pct = 100.0 * below / n if n else None
            n_ex = n - indet
            pct_ex = 100.0 * (below - indet) / n_ex if n_ex else None
            out.append({
                "year": year, "analyte": an, "lowest_al_ppm": al, "printed_pct": pct_s,
                "printed_n": n_print, "file_n": n, "below": below, "below_inclusive": below_le,
                "pct": pct, "indeterminate": indet, "pct_excl_indeterminate": pct_ex,
                "n_match": n == n_print, "pct_match": n == n_print and matches(pct, pct_s),
                "pct_excl_match": n_ex == n_print and matches(pct_ex, pct_s),
            })
    return out


def samples_of(rows):
    """Per-sample records: descriptors from the first row, detection flag per analyte."""
    by = {}
    for r in rows:
        s = by.get(r["sid"])
        if s is None:
            s = by[r["sid"]] = {
                "sid": r["sid"], "year": r["year"], "province": r["province"],
                "species": r["species"], "feed_type": r["feed_type"],
                "ingredient_type": r["ingredient_type"], "ingredient_name": r["ingredient_name"],
                "det": {}, "don_ppm": None, "mixed_descriptors": False}
        elif (r["year"], r["province"]) != (s["year"], s["province"]):
            s["mixed_descriptors"] = True
        an = r["analyte"]
        if an is None or r["value"] is None:
            continue
        s["det"][an] = s["det"].get(an, False) or r["detected"]
        if an == "DON" and r["ppm"] is not None:
            s["don_ppm"] = r["ppm"] if s["don_ppm"] is None else max(s["don_ppm"], r["ppm"])
    return by


def region(province):
    if not province:
        return ""
    return "West" if province in WEST else "East"


def odds_ratio(a, b, c, d):
    """Odds ratio with a Haldane 0.5 correction only if a cell is zero."""
    if 0 in (a, b, c, d):
        return ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5)), True
    return (a * d) / (b * c), False


def cooccurrence(samples, x, y):
    """2x2 detection table over samples tested for both x and y."""
    a = b = c = d = 0  # a=both, b=x only, c=y only, d=neither
    for s in samples.values():
        if x not in s["det"] or y not in s["det"]:
            continue
        dx, dy = s["det"][x], s["det"][y]
        if dx and dy:
            a += 1
        elif dx:
            b += 1
        elif dy:
            c += 1
        else:
            d += 1
    orr, corrected = odds_ratio(a, b, c, d)
    return {"x": x, "y": y, "n_pairs": a + b + c + d, "both": a, "x_only": b, "y_only": c,
            "neither": d, "odds_ratio": orr, "haldane_corrected": corrected,
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


def adon_split(samples, key):
    """Among samples with 3-ADON or 15-ADON detected: 3-ADON-detected counts by group.

    key(sample) -> group name or None (excluded). Returns {group: [n_adon_pos, n_3adon]}.
    """
    out = {}
    for s in samples.values():
        det = s["det"]
        if not (det.get("3-ADON") or det.get("15-ADON")):
            continue
        g = key(s)
        if g is None:
            continue
        cell = out.setdefault(g, [0, 0])
        cell[0] += 1
        if det.get("3-ADON"):
            cell[1] += 1
    return out


def compare_shares(split, g1, g2):
    """3-ADON share in g1 vs g2 with the Fisher p-value of the 2x2."""
    n1, k1 = split.get(g1, [0, 0])
    n2, k2 = split.get(g2, [0, 0])
    return {"groups": [g1, g2], "n": [n1, n2], "n_3adon": [k1, k2],
            "share": [k1 / n1 if n1 else None, k2 / n2 if n2 else None],
            "fisher_p": fisher_two_sided(k1, n1 - k1, k2, n2 - k2)}


def detection_shares(rows):
    """{analyte: [n_tested, n_detected]} over parseable rows."""
    out = {}
    for r in rows:
        if r["analyte"] is None or r["value"] is None:
            continue
        cell = out.setdefault(r["analyte"], [0, 0])
        cell[0] += 1
        if r["detected"]:
            cell[1] += 1
    return out


def limit_counts(rows, analyte, years):
    """{censoring limit in ppm (rounded to 6 dp): n} over the given years' censored rows."""
    out = {}
    for r in rows:
        if r["analyte"] == analyte and r["year"] in years and not r["detected"] \
                and r["limit_ppm"] is not None:
            _bump(out, round(r["limit_ppm"], 6))
    return out


def modal_limit(rows, analyte, years):
    """Most common censoring limit (ties -> the smaller), with how many rows it rests on."""
    counts = limit_counts(rows, analyte, years)
    if not counts:
        return None, 0
    best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return best, sum(counts.values())


def is_corn(name):
    return "corn" in (name or "").lower()


# ---------------------------------------------------------------------------
# Grading.
# ---------------------------------------------------------------------------
def grade(rows, check, sha_ok):
    open_, gchecks = gate(check, sha_ok)
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "gradable": True,
              "observed": {"checks": gchecks, "result_kinds": check["result_kinds"],
                           "unparsed": check["unparsed"],
                           "unknown_analyte": check["unknown_analyte"],
                           "unknown_unit": check["unknown_unit"]},
              "text": "SHA-256, the 10 column headers, 40,862 rows, 3,258 samples, units "
                      "{mg/kg 32,019, ug/kg 8,843}, the 18 mycotoxin labels with their row counts, "
                      "and result format {censored 35,368, numeric 5,494}"}]

    def add(pid, kind, text, observed, met, gradable=True):
        preds.append({"id": pid, "kind": kind, "gradable": gradable,
                      "graded": bool(open_ and gradable),
                      "met": bool(open_ and gradable and met), "text": text,
                      "observed": observed})

    cells = table1_cells(rows)
    by = {(c["year"], c["analyte"]): c for c in cells}
    six = ("DON", "T-2", "DAS", "FUM", "OTA", "ZEA")
    n_ok = [c for c in cells if c["analyte"] in six and c["n_match"]]
    add("C1", "check", "file sample counts equal Table 1's n in at least 107 of the 108 "
        "year x {DON, T-2, DAS, FUM, OTA, ZEA} cells",
        {"cells": 108, "n_match": len(n_ok),
         "mismatches": [(c["year"], c["analyte"], c["file_n"], c["printed_n"])
                        for c in cells if c["analyte"] in six and not c["n_match"]]},
        len(n_ok) >= C1_MIN)

    ht2_vs_t2 = [(y, by[(y, "HT-2")]["file_n"], TABLE1[y]["T-2"][1]) for y in YEARS]
    add("C2", "check", "in at least 17 of 18 years the file's HT-2 count equals Table 1's T-2 n "
        "(so the 41 extra HT-2 rows sit in 2010-11 to 2013-14)",
        {"by_year": ht2_vs_t2,
         "extra_vs_printed_ht2": {y: by[(y, "HT-2")]["file_n"] - TABLE1[y]["HT-2"][1]
                                  for y in YEARS}},
        sum(1 for _, f, t in ht2_vs_t2 if f == t) >= C2_MIN)

    don_ok = [c for c in cells if c["analyte"] == "DON" and c["pct_match"]]
    add("C3", "check", "DON: the file reproduces Table 1's n and '% below 1 ppm' in at least 16 "
        "of 18 years",
        {"matched": len(don_ok),
         "cells": [(c["year"], c["file_n"], c["printed_n"], _r(c["pct"]), c["printed_pct"])
                   for c in cells if c["analyte"] == "DON"]},
        len(don_ok) >= C3_MIN)

    five = ("T-2", "DAS", "FUM", "OTA", "ZEA")
    five_ok = [c for c in cells if c["analyte"] in five and c["pct_match"]]
    add("C4", "check", "T-2, DAS, FUM, OTA, ZEA: n and % below the lowest AL reproduced in at "
        "least 85 of 90 year cells",
        {"matched": len(five_ok),
         "misses": [(c["year"], c["analyte"], c["file_n"], c["printed_n"], _r(c["pct"]),
                     c["printed_pct"]) for c in cells if c["analyte"] in five
                    and not c["pct_match"]]},
        len(five_ok) >= C4_MIN)

    ht2 = [by[(y, "HT-2")] for y in YEARS]
    mech = [(c["year"], c["indeterminate"], c["file_n"] - c["printed_n"]) for c in ht2]
    add("C5", "check", "HT-2: in every year, the rows the report leaves out (file n minus "
        "printed n) equal the non-detects whose censoring limit is above 0.1 ppm",
        {"by_year": mech}, all(i == g for _, i, g in mech))

    ht2_ok = [c for c in ht2 if c["pct_excl_match"]]
    add("C6", "check", "HT-2: with those indeterminate rows dropped, n and '% below 0.1 ppm' "
        "match Table 1 in at least 16 of 18 years",
        {"matched": len(ht2_ok),
         "cells": [(c["year"], c["file_n"] - c["indeterminate"], c["printed_n"],
                    _r(c["pct_excl_indeterminate"]), c["printed_pct"]) for c in ht2]},
        len(ht2_ok) >= C6_MIN)

    afla_over = [r for r in rows if r["analyte"] in AFLATOXINS and r["detected"]
                 and r["ppm"] is not None and r["ppm"] > AFLA_LEVEL + EPS]
    add("C7", "check", "no aflatoxin result (B1, B2, G1, G2 or total) above 20 ppb",
        {"n_over": len(afla_over),
         "rows": [(r["year"], r["label"], r["raw"], r["unit"]) for r in afla_over[:20]]},
        len(afla_over) == 0)

    censored = [r for r in rows if r["raw"].startswith("<")]
    no_limit = sum(1 for r in censored if r["limit"] is None)
    add("S1", "prediction", "every '<' result carries a numeric censoring limit",
        {"censored": len(censored), "without_numeric_limit": no_limit}, no_limit == 0)

    shares = detection_shares(rows)
    share = {a: (k / n if n else 0.0) for a, (n, k) in shares.items()}
    others = [a for a in share if a != "DON"]
    add("P1", "prediction", "DON is the most frequently detected of the 17 analytes",
        {"shares": {a: _r(v) for a, v in sorted(share.items())},
         "counts": dict(sorted(shares.items()))},
        "DON" in share and all(share["DON"] > share[a] for a in others))
    add("P2", "prediction", "DON is detected in 35-75% of the samples tested for it",
        {"share": _r(share.get("DON")), "counts": shares.get("DON")},
        "DON" in share and P2_SHARE[0] <= share["DON"] <= P2_SHARE[1])

    samples = samples_of(rows)
    co_zea = cooccurrence(samples, "DON", "ZEA")
    add("P3", "prediction", "within-sample DON x zearalenone detection odds ratio >= 3, Fisher "
        "p < 0.001", co_zea, co_zea["odds_ratio"] >= P3_OR and co_zea["fisher_p"] < 0.001)
    co_15 = cooccurrence(samples, "DON", "15-ADON")
    add("P4", "prediction", "within-sample DON x 15-acetyl-DON detection odds ratio >= 10, "
        "Fisher p < 0.001", co_15, co_15["odds_ratio"] >= P4_OR and co_15["fisher_p"] < 0.001)
    co_ota = cooccurrence(samples, "OTA", "DON")
    add("P5", "prediction", "OTA x DON detection odds ratio > 1 with Fisher p < 0.05 "
        "(replicating the retail-food association of myco-don P11); gradable if OTA is "
        "detected in at least 10 paired samples",
        co_ota, co_ota["odds_ratio"] > 1.0 and co_ota["fisher_p"] < 0.05,
        gradable=(co_ota["both"] + co_ota["x_only"]) >= MIN_GROUP)

    n3 = sum(1 for s in samples.values() if s["det"].get("3-ADON"))
    n15 = sum(1 for s in samples.values() if s["det"].get("15-ADON"))
    add("P6", "prediction", "15-acetyl-DON is detected in more samples than 3-acetyl-DON",
        {"samples_3adon": n3, "samples_15adon": n15}, n15 > n3)

    reg = adon_split(samples, lambda s: region(s["province"]) or None)
    rcmp = compare_shares(reg, "West", "East")
    add("P7", "prediction", "among samples with any acetyl-DON detected, the 3-ADON share is "
        "higher in the West (AB, BC, MB, SK) than in the East, Fisher p < 0.05; gradable if each "
        "region has at least 10 such samples",
        rcmp, rcmp["share"][0] is not None and rcmp["share"][1] is not None
        and rcmp["share"][0] > rcmp["share"][1] and rcmp["fisher_p"] < 0.05,
        gradable=min(rcmp["n"]) >= MIN_GROUP)

    per = adon_split(samples, lambda s: "late" if s["year"] in LATE
                     else ("early" if s["year"] in EARLY else None))
    pcmp = compare_shares(per, "late", "early")
    add("P8", "prediction", "the 3-ADON share among acetyl-DON-positive samples is higher in "
        "2009-10..2017-18 than in 2000-01..2008-09; gradable if each period has at least 10",
        pcmp, pcmp["share"][0] is not None and pcmp["share"][1] is not None
        and pcmp["share"][0] > pcmp["share"][1],
        gradable=min(pcmp["n"]) >= MIN_GROUP)

    fum = [r for r in rows if r["analyte"] == "FUM" and r["value"] is not None]
    corn = [r for r in fum if is_corn(r["ingredient_name"])]
    other = [r for r in fum if r["ingredient_name"] and not is_corn(r["ingredient_name"])]
    s_corn = sum(1 for r in corn if r["detected"]) / len(corn) if corn else None
    s_other = sum(1 for r in other if r["detected"]) / len(other) if other else None
    add("P9", "prediction", "fumonisins are detected at least 3x as often in corn-named "
        "ingredients as in other named ingredients; gradable if each group has >= 30 results",
        {"corn": [len(corn), sum(1 for r in corn if r["detected"])],
         "other_named": [len(other), sum(1 for r in other if r["detected"])],
         "share_corn": _r(s_corn), "share_other": _r(s_other)},
        s_corn is not None and s_other is not None and s_corn > 0
        and s_corn >= P9_RATIO * s_other,
        gradable=min(len(corn), len(other)) >= MIN_FUM_GROUP)

    early_mode, early_n = modal_limit(rows, "DON", LIMIT_EARLY)
    late_mode, late_n = modal_limit(rows, "DON", LIMIT_LATE)
    add("P10", "prediction", "the modal DON censoring limit in 2014-15..2017-18 is lower than in "
        "2000-01..2003-04; gradable if each period has at least 10 censored DON results",
        {"early": [early_mode, early_n], "late": [late_mode, late_n],
         "early_counts": _keys(limit_counts(rows, "DON", LIMIT_EARLY)),
         "late_counts": _keys(limit_counts(rows, "DON", LIMIT_LATE))},
        early_mode is not None and late_mode is not None and late_mode < early_mode - EPS,
        gradable=min(early_n, late_n) >= MIN_GROUP)

    ht2_modes = {y: modal_limit(rows, "HT-2", (y,)) for y in YEARS}
    early_ok = [y for y in HT2_EARLY if ht2_modes[y][0] is not None]
    later_low = [y for y in HT2_LATER if ht2_modes[y][0] is not None
                 and ht2_modes[y][0] < 0.1 - EPS]
    add("P11", "prediction", "the modal HT-2 censoring limit is 0.1 ppm in every year 2000-01.."
        "2012-13, and below 0.1 ppm in at least one year 2013-14..2017-18",
        {"modal_by_year": {y: list(m) for y, m in ht2_modes.items()},
         "later_years_below_0.1": later_low},
        bool(early_ok) and all(abs(ht2_modes[y][0] - 0.1) <= EPS for y in early_ok)
        and len(early_ok) == len(HT2_EARLY) and bool(later_low))

    afb1 = shares.get("AFB1", [0, 0])
    add("P12", "prediction", "aflatoxin B1 is detected in at most 5% of the samples tested for it",
        {"counts": afb1, "share": _r(afb1[1] / afb1[0]) if afb1[0] else None},
        afb1[0] > 0 and afb1[1] / afb1[0] <= P12_MAX_SHARE)
    return preds, cells, samples, {"DON x ZEA": co_zea, "DON x 15-ADON": co_15,
                                   "OTA x DON": co_ota, "3-ADON share by region": rcmp,
                                   "3-ADON share by period": pcmp,
                                   "3-ADON split by region": reg, "3-ADON split by period": per}


def _r(x):
    return None if x is None else (round(x, 6) if isinstance(x, float) else x)


def _keys(d):
    return {f"{k:g}": v for k, v in sorted(d.items())}


def descriptive(rows, check, samples):
    years = {}
    for r in rows:
        if r["analyte"] is None or r["value"] is None:
            continue
        cell = years.setdefault(r["analyte"], {}).setdefault(r["year"] or "(blank)", [0, 0])
        cell[0] += 1
        if r["detected"]:
            cell[1] += 1
    units = {}
    for r in rows:
        units.setdefault(r["analyte"] or "?", {}).setdefault(r["year"] or "(blank)", {})
        _bump(units[r["analyte"] or "?"][r["year"] or "(blank)"], r["unit"])
    don = [r for r in rows if r["analyte"] == "DON" and r["value"] is not None]
    thresholds = {}
    for t in (1.0, 2.0, 5.0, 10.0):
        thresholds[f">={t:g} ppm"] = sum(1 for r in don if r["detected"] and r["ppm"] is not None
                                         and r["ppm"] >= t - EPS)
    variant = {}
    for r in rows:
        if r["label"] == "3-AcetyldeoxyNivalenol":
            _bump(variant, r["year"])
    return {
        "detection_by_analyte_year": years,
        "units_by_analyte_year": units,
        "don_results": len(don),
        "don_at_or_above": thresholds,
        "label_variant_3-AcetyldeoxyNivalenol_by_year": dict(sorted(variant.items())),
        "blank_year_rows": [(r["sid"], r["label"], r["raw"], r["unit"]) for r in rows
                            if not r["year"]],
        "samples_with_mixed_year_or_province": sum(1 for s in samples.values()
                                                   if s["mixed_descriptors"]),
        "result_kinds": check["result_kinds"],
    }


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _fetch(url, tries=3, pause=8):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-feed-myco"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(data_dir):
    """Return (raw_bytes, source): the data-volume copy if its SHA-256 matches, else download."""
    path = os.path.join(data_dir, RESOURCE + ".csv") if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == SHA256:
            return raw, "data-volume"
    errors = []
    for url in URLS:
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
    raise RuntimeError("no verified copy of the livestock-feed file: " + "; ".join(errors))


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
TABLE1_FIELDS = ["year", "analyte", "lowest_al_ppm", "printed_pct", "printed_n", "file_n",
                 "below", "below_inclusive", "pct", "indeterminate", "pct_excl_indeterminate",
                 "n_match", "pct_match", "pct_excl_match"]
SAMPLE_FIELDS = (["sid", "year", "province", "region", "species", "feed_type", "ingredient_type",
                  "ingredient_name", "don_ppm"] + [f"det_{a}" for a in ANALYTES])


def write_outputs(out_dir, rows, preds, cells, samples, co, desc, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "feed_myco_table1.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(TABLE1_FIELDS)
        for c in cells:
            w.writerow([_csv(c[k]) for k in TABLE1_FIELDS])
    with open(os.path.join(out_dir, "feed_myco_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(SAMPLE_FIELDS)
        for s in sorted(samples.values(), key=lambda s: (s["year"], s["sid"])):
            flags = ["" if a not in s["det"] else int(s["det"][a]) for a in ANALYTES]
            w.writerow([s["sid"], s["year"], s["province"], region(s["province"]), s["species"],
                        s["feed_type"], s["ingredient_type"], s["ingredient_name"],
                        _csv(s["don_ppm"])] + flags)
    with open(os.path.join(out_dir, "feed_myco_limits.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["analyte", "year", "limit_ppm", "n"])
        for a in ANALYTES:
            for y in YEARS:
                for lim, n in sorted(limit_counts(rows, a, (y,)).items()):
                    w.writerow([a, y, f"{lim:g}", n])
    with open(os.path.join(out_dir, "feed_myco_cooccurrence.json"), "w", encoding="utf-8") as fh:
        json.dump(co, fh, indent=2, sort_keys=True)
    result = {"study": "feed-myco", "version": VERSION, "predictions": preds,
              "descriptive": desc, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "feed_myco_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "feed_myco_grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def _csv(x):
    if x is None:
        return ""
    if isinstance(x, bool):
        return int(x)
    if isinstance(x, float):
        return round(x, 6)
    return x


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the feed-myco pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw, source = load(args.data_dir)
    text, enc = decode(raw)
    rows, check = parse_text(text)
    sha_ok = _sha(raw) == SHA256
    preds, cells, samples, co = grade(rows, check, sha_ok)
    desc = descriptive(rows, check, samples)
    provenance = {"dataset": DATASET, "resource": RESOURCE, "sha256": SHA256, "bytes": len(raw),
                  "source": source, "encoding": enc}
    result = write_outputs(args.out_dir, rows, preds, cells, samples, co, desc, provenance)
    print(json.dumps({"version": VERSION,
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_graded": result["n_graded"], "n_met": result["n_met"],
                      "gate": preds[0]["observed"]["checks"]}, indent=2))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
