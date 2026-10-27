#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ota-grain-2018 0.1.0: CFIA's open 2018-19 ochratoxin A grain file against its report, and
against the same year's multi-mycotoxin survey at a common reporting cut.

Grades docs/ota-grain-2018-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

The Canadian Food Inspection Agency (CFIA) publishes a per-sample file for its survey
"Ochratoxin A in Wheat Products, Oat Products, Rice Products and Other Grain Products - April 1,
2018 to March 31, 2019" on open.canada.ca (Open Government Licence - Canada): OG, 496 rows, one
ochratoxin A (OTA) result per sample. Its own 2020 report (R20) prints 495 samples; the 2018
rows of Table 7 in CFIA's later "Ochratoxin A in Selected Foods" report (R22) add up to 496. This
reads the result column for the first time to (a) rebuild every row of both reports the product
labels identify, which also settles R20's contradictions (rice 13 or 14 positives; an oat
average of 0.26 or 2.6), (b) test blind predictions on the grain rows the labels only bound, and
(c) ask whether the gap between this survey's OTA detection (crackers 75%) and the same year's
multi-mycotoxin survey (crackers 2 of 101; MM, already graded in multimyco-2018 0.1.0) is only a
reporting-limit effect, by comparing both files on their shared product labels at a common cut.

Both files are SHA-256 pinned. Value rule (registered): a cell that parses as a number above 0
is a positive; a cell that does not parse as a number is a non-detect token; a literal 0 is a
non-detect in MM (its registered coding) and fails the gate in OG; a negative or non-finite
number fails the gate. Units go through an explicit table. Standard library only. Code
Apache-2.0; derived data CC BY 4.0. A reference comparison, not a compliance finding (Health
Canada's OTA levels for these foods are proposed, not in force), not about any brand, and not
individual dietary or medical advice.
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

OG = {
    "key": "OG",
    "dataset": "7296b53e-56fc-41df-82c6-04656422b39e",
    "resource": "d9d79110-e472-4aec-89ee-e51861f4d88d",
    "filename": "1068.csv",
    "sha256": "36dde7d7438fc50d43a22635a5e09deecebd27c301adc24e3e2e2469e7d47403",
    "rows": 496, "samples": 496,
}
MM = {
    "key": "MM",
    "dataset": "03f184ee-e5e0-4e33-a763-fa3e44ed2dc0",
    "resource": "09a3c285-8552-4a38-b4be-cdf6d5fc3fd2",
    "filename": ("cfia_acia-1134_2018-19_multi-mycotoxins_in_selected_foods_-_2019-2019_"
                 "presence-de-plusieurs-myco.csv"),
    "sha256": "ba5084945f0a0e1fab2b8bab7f8f196a7dd0033d4bdc4e80768f12ec4c553835",
    "rows": 18750, "samples": 750,
}
OTA = "Ochratoxin A"

# OG product-label row counts, from the names-only census (job myco-census-v2, 2026-10-25).
OG_PRODUCT_ROWS = {
    "Grain - Rice": 99, "Bakery Product - Cookie": 29, "Crackers": 29, "Wheat Products": 29,
    "Baking Mixes": 28, "Infant Food - Cereal": 28, "Pasta - Dry": 28, "Cereal - Children": 26,
    "Bran - Oat": 25, "Oatmeal": 25, "Kamut Products": 24, "Oat Products": 24,
    "Quinoa Products": 24, "Buckwheat Products": 23, "Flour - Oat": 23, "Rye Products": 21,
    "Flour - rye": 4, "Flour - Other": 3, "Crispbread/Crouton": 2, "Cereal": 1,
    "Grain - Kamut": 1,
}
OG_ORIGIN_FACTS = {"CANADA": 92, "UNKNOWN": 232}
OG_POS_CELLS, OG_TEXT_CELLS, MAX_TOKENS = 220, 276, 10
# MM facts already published (multimyco-2018 0.1.0 result and detail listing).
MM_OTA_POS, MM_OTA_MIN = 20, 0.8
SHARED_LABELS = ["Buckwheat Products", "Crackers", "Grain - Kamut", "Kamut Products",
                 "Pasta - Dry", "Quinoa Products", "Rye Products"]

# Units -> factor to ng/g (= ug/kg = ppb). Keys are lower-cased.
UNIT_FACTORS = {"ng/g": 1.0, "ppb": 1.0, "µg/kg": 1.0, "μg/kg": 1.0, "ug/kg": 1.0,
                "ppm": 1000.0, "µg/g": 1000.0, "μg/g": 1000.0, "ug/g": 1000.0,
                "mg/kg": 1000.0}

# Label families (see docs/ota-grain-2018-report-check-0.1.0.md).
FAMILIES = {
    "rice": ("Grain - Rice",),
    "rye": ("Rye Products", "Flour - rye"),
    "oat": ("Bran - Oat", "Oatmeal", "Oat Products", "Flour - Oat"),
    "kamut": ("Kamut Products", "Grain - Kamut"),
    "buckwheat": ("Buckwheat Products",),
    "quinoa": ("Quinoa Products",),
}

# Rows of the survey's own 2020 report (R20) the labels identify:
# (id, text, labels, n, positives, min, max, avg), printed.
ROWS = (
    ("C1", "R20 rye (Table 2)", FAMILIES["rye"], 25, 15, "0.050", "1.9", "0.24"),
    ("C2", "R20 baking mixes 2018-19 (Table 3)", ("Baking Mixes",), 28, 9, "0.051", "0.46",
     "0.16"),
    ("C3", "R20 infant cereal (wheat) 2018-19 (Table 3)", ("Infant Food - Cereal",), 28, 5,
     "0.050", "0.17", "0.077"),
    ("C4", "R20 pasta 2018-19 (Table 3)", ("Pasta - Dry",), 28, 21, "0.049", "0.34", "0.18"),
)
# The 2018 rows of Table 7 of CFIA's later report "Ochratoxin A in Selected Foods" (R22), which
# prints percent positive, not counts: (id, text, labels, n, percent, min, max, avg), printed.
LESS_COMMON = FAMILIES["rye"] + FAMILIES["kamut"] + FAMILIES["buckwheat"] + FAMILIES["quinoa"] \
    + ("Flour - Other",)
GRAIN_BASED = ("Bakery Product - Cookie", "Crackers", "Baking Mixes", "Infant Food - Cereal",
               "Pasta - Dry", "Cereal - Children", "Crispbread/Crouton", "Cereal")
PCT_ROWS = (
    ("C6", "R22 less commonly consumed grains 2018", LESS_COMMON, 100, 44, "0.05", "7.6", "1.0"),
    ("C7", "R22 oat 2018", FAMILIES["oat"], 97, 54, "0.05", "1.6", "0.26"),
    ("C8", "R22 rice 2018", FAMILIES["rice"], 99, 14, "0.049", "11", "1.1"),
    ("C9", "R22 wheat 2018", ("Wheat Products",), 29, 62, "0.06", "1.5", "0.4"),
    ("C10", "R22 grain-based foods 2018", GRAIN_BASED, 171, 54, "0.042", "2.2", "0.24"),
)

# Registered thresholds.
CUT = 0.8                       # MM's smallest OTA positive (= the method's OTA LOD, 2015-18)
P1_BUCK_POS, P1_QUIN_POS = (9, 11), (7, 8)
P2_POS, P2_MAX = (9, 10), 1.25
P3_LEVEL = 3.0
P4_ALPHA = 0.05
P5_POS_MIN, P5_CUT_MAX = 20, 3
P6_BAND = (10, 39)


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def parse_amount(raw):
    """(value, detected, kind) for one result cell under the registered rule.

    kind is one of: blank, text (a non-detect token), zero, bad, pos."""
    s = (raw or "").strip()
    if s == "":
        return 0.0, False, "blank"
    try:
        v = float(s)
    except ValueError:
        return 0.0, False, "text"
    if v != v or v < 0 or v == float("inf"):
        return None, False, "bad"
    if v == 0:
        return 0.0, False, "zero"
    return v, True, "pos"


def tolerance(printed):
    """Half a unit in the last significant place of a printed figure.

    Decimals use their decimal places ("0.050" -> 0.0005). Whole numbers with trailing zeros are
    read at two significant figures ("870" -> 5); other whole numbers to the unit."""
    s = printed.strip()
    if "." in s:
        return 0.5 * 10 ** (-len(s.split(".")[1]))
    digits = s.lstrip("-")
    stripped = digits.rstrip("0")
    if not stripped:
        return 0.5
    z = len(digits) - len(stripped)
    if len(stripped) < 2:
        z = max(0, z - (2 - len(stripped)))
    return 0.5 * 10 ** z


def matches(x, printed):
    """Does x round to the printed figure at its printed precision?"""
    if x is None:
        return False
    return abs(x - float(printed)) <= tolerance(printed) + 1e-9


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
        "origin": first(lambda c: c == "Origin", "origin"),
        "product": first(lambda c: c == "Product", "product"),
        "component": first(lambda c: c == "Component", "component"),
        "value": first(lambda c: c.startswith("Result") or c == "AMOUNT", "value"),
        "unit": first(lambda c: c.startswith("Unit") or c.startswith("Report Unit")
                      or c == "ReportUnit", "unit"),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def family(product):
    for name, labels in FAMILIES.items():
        if product in labels:
            return name
    return "generic"


def parse_text(text, only_component=None):
    """(samples, census) from one decoded CSV. samples: {id: record}.

    With only_component, rows of other components are counted in the census and skipped."""
    table = list(csv.reader(io.StringIO(text)))
    header = table[0]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    col = find_columns(header)

    def cell(r, k):
        i = col[k]
        return r[i] if i < len(r) else ""

    comps, kinds, units, products, origins, tokens = {}, {}, {}, {}, {}, {}
    per_sample_rows = {}
    samples = {}
    n_rows = 0
    for r in body:
        n_rows += 1
        comp = clean(cell(r, "component"))
        _bump(comps, comp)
        if only_component is not None and comp != only_component:
            continue
        sid = clean(cell(r, "sample"))
        product = clean(cell(r, "product"))
        origin = clean(cell(r, "origin"))
        unit = clean(cell(r, "unit"))
        raw = cell(r, "value")
        value, det, kind = parse_amount(raw)
        factor = UNIT_FACTORS.get(unit.lower())
        _bump(kinds, kind)
        _bump(units, unit)
        _bump(products, product)
        _bump(origins, origin)
        _bump(per_sample_rows, sid)
        if kind == "text":
            _bump(tokens, raw.strip())
        ppb = value * factor if (value is not None and factor is not None) else None
        samples[sid] = {"sample": sid, "product": product, "origin": origin,
                        "family": family(product), "ota": ppb if det else 0.0,
                        "detected": bool(det and ppb is not None), "kind": kind}
    rps = {}
    for v in per_sample_rows.values():
        _bump(rps, str(v))
    census = {"n_rows": n_rows, "n_selected_rows": sum(per_sample_rows.values()),
              "distinct_samples": len(samples), "components": comps, "products": products,
              "origins": origins, "units": units, "value_kinds": kinds, "text_tokens": tokens,
              "rows_per_sample": rps}
    return samples, census


def positives(recs):
    return [r["ota"] for r in recs if r["detected"]]


def row_stats(recs):
    pos = positives(recs)
    return {"n": len(recs), "pos": len(pos),
            "min": min(pos) if pos else None,
            "max": max(pos) if pos else None,
            "avg": statistics.fmean(pos) if pos else None,
            "ge_cut": sum(1 for v in pos if v >= CUT - 1e-9)}


def select(recs, labels):
    ls = set(labels)
    return [r for r in recs if r["product"] in ls]


def check_row(st, n, pos, mn, mx, avg):
    """(ok, detail) for one report row against its statistics."""
    detail = {"n": [st["n"], n], "pos": [st["pos"], pos]}
    ok = st["n"] == n and st["pos"] == pos
    for name, printed in (("min", mn), ("max", mx), ("avg", avg)):
        good = matches(st[name], printed)
        detail[name] = [st[name], printed, good]
        ok = ok and good
    return ok, detail


def percent(pos, n):
    """Percent positive rounded half up to a whole number, as printed."""
    return int(100 * pos / n + 0.5) if n else None


def check_pct_row(st, n, pct, mn, mx, avg):
    """(ok, detail) for a row printed with percent positive instead of a count."""
    got = percent(st["pos"], st["n"])
    detail = {"n": [st["n"], n], "pct": [got, pct], "pos": st["pos"]}
    ok = st["n"] == n and got == pct
    for name, printed in (("min", mn), ("max", mx), ("avg", avg)):
        good = matches(st[name], printed)
        detail[name] = [st[name], printed, good]
        ok = ok and good
    return ok, detail


def mh_or(tabs):
    num = sum(a * d / (a + b + c + d) for a, b, c, d in tabs if a + b + c + d > 0)
    den = sum(b * c / (a + b + c + d) for a, b, c, d in tabs if a + b + c + d > 0)
    return num / den if den > 0 else None


def cmh(tabs):
    """Continuity-corrected Cochran-Mantel-Haenszel chi-square (1 df) and two-sided p."""
    diff = var = 0.0
    for a, b, c, d in tabs:
        n = a + b + c + d
        if n < 2:
            continue
        diff += a - (a + b) * (a + c) / n
        var += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    if var <= 0:
        return 0.0, 1.0
    chi2 = max(0.0, abs(diff) - 0.5) ** 2 / var
    return chi2, math.erfc(math.sqrt(chi2 / 2))


def cross_tables(og, mm, labels, at_cut=True):
    """{label: (OG hit, OG miss, MM hit, MM miss)}; a hit is a positive (at or above CUT)."""
    def hit(r):
        return r["detected"] and (not at_cut or r["ota"] >= CUT - 1e-9)

    out = {}
    for lab in labels:
        a_recs, m_recs = select(og, (lab,)), select(mm, (lab,))
        a = sum(1 for r in a_recs if hit(r))
        c = sum(1 for r in m_recs if hit(r))
        out[lab] = (a, len(a_recs) - a, c, len(m_recs) - c)
    return out


# ---------------------------------------------------------------------------
# Gate, analysis and grading.
# ---------------------------------------------------------------------------
def gate_checks(c_og, c_mm, og, mm, sha_og_ok, sha_mm_ok):
    unit_ok = (len(c_og["units"]) == 1
               and all(u.lower() in UNIT_FACTORS for u in c_og["units"]))
    mm_unit_ok = (len(c_mm["units"]) >= 1
                  and all(u.lower() in UNIT_FACTORS for u in c_mm["units"]))
    mm_pos = positives(mm)
    shared = sorted(set(c_og["products"]) & set(c_mm["products"]))
    return {
        "og_sha256": bool(sha_og_ok),
        "og_rows": c_og["n_rows"] == OG["rows"],
        "og_samples": c_og["distinct_samples"] == OG["samples"],
        "og_rows_per_sample": c_og["rows_per_sample"] == {"1": OG["samples"]},
        "og_component": c_og["components"] == {OTA: OG["rows"]},
        "og_products": c_og["products"] == OG_PRODUCT_ROWS,
        "og_origins": all(c_og["origins"].get(k) == v for k, v in OG_ORIGIN_FACTS.items()),
        "og_unit": unit_ok,
        "og_value_kinds": c_og["value_kinds"] == {"pos": OG_POS_CELLS, "text": OG_TEXT_CELLS},
        "og_tokens": 1 <= len(c_og["text_tokens"]) <= MAX_TOKENS,
        "mm_sha256": bool(sha_mm_ok),
        "mm_rows": c_mm["n_rows"] == MM["rows"],
        "mm_ota_samples": (c_mm["distinct_samples"] == MM["samples"]
                           and c_mm["rows_per_sample"] == {"1": MM["samples"]}),
        "mm_ota_kinds": (set(c_mm["value_kinds"]) <= {"pos", "zero"}
                         and c_mm["value_kinds"].get("pos") == MM_OTA_POS),
        "mm_unit": mm_unit_ok,
        "mm_ota_min": bool(mm_pos) and abs(min(mm_pos) - MM_OTA_MIN) < 1e-9,
        "shared_labels": shared == SHARED_LABELS,
    }


def analyse(og, mm):
    rows = {}
    for rid, text, labels, n, pos, mn, mx, avg in ROWS:
        st = row_stats(select(og, labels))
        ok, detail = check_row(st, n, pos, mn, mx, avg)
        rows[rid] = {"text": text, "ok": ok, "detail": detail}
    for rid, text, labels, n, pct, mn, mx, avg in PCT_ROWS:
        st = row_stats(select(og, labels))
        ok, detail = check_pct_row(st, n, pct, mn, mx, avg)
        rows[rid] = {"text": text, "ok": ok, "detail": detail}
    fam = {name: row_stats([r for r in og if r["family"] == name])
           for name in list(FAMILIES) + ["generic"]}
    labels = {lab: row_stats(select(og, (lab,))) for lab in sorted({r["product"] for r in og})}
    overall = row_stats(og)
    no_limit = set(FAMILIES["buckwheat"] + FAMILIES["quinoa"])
    over3 = sorted(({"sample": r["sample"], "product": r["product"], "ota": r["ota"]}
                    for r in og if r["detected"] and r["ota"] > P3_LEVEL),
                   key=lambda x: -x["ota"])
    infant = select(og, ("Infant Food - Cereal",))
    bran = select(og, ("Bran - Oat",))

    cut_tabs = cross_tables(og, mm, SHARED_LABELS, at_cut=True)
    own_tabs = cross_tables(og, mm, SHARED_LABELS, at_cut=False)
    cut_chi2, cut_p = cmh(list(cut_tabs.values()))
    own_chi2, own_p = cmh(list(own_tabs.values()))

    def pooled(tabs):
        return [sum(t[i] for t in tabs.values()) for i in range(4)]

    return {
        "rows": rows, "families": fam, "labels": labels, "overall": overall,
        "rice_other_pos": overall["pos"] - fam["rice"]["pos"],
        "over_3": over3,
        "over_3_outside_no_limit": [x for x in over3 if x["product"] not in no_limit],
        "infant_over_0_5": sum(1 for r in infant if r["detected"] and r["ota"] > 0.5),
        "bran_oat_over_7": sum(1 for r in bran if r["detected"] and r["ota"] > 7.0),
        "crackers_crispbread": row_stats(select(og, ("Crackers", "Crispbread/Crouton"))),
        "cross": {
            "cut_ppb": CUT, "labels": SHARED_LABELS,
            "at_cut": {k: list(v) for k, v in cut_tabs.items()},
            "own_limits": {k: list(v) for k, v in own_tabs.items()},
            "at_cut_pooled": pooled(cut_tabs), "own_pooled": pooled(own_tabs),
            "at_cut_mh_or": mh_or(list(cut_tabs.values())),
            "at_cut_cmh_chi2": cut_chi2, "at_cut_cmh_p": cut_p,
            "own_mh_or": mh_or(list(own_tabs.values())),
            "own_cmh_chi2": own_chi2, "own_cmh_p": own_p,
        },
    }


def grade(a, gate_obs):
    open_ = all(gate_obs.values())
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": open_, "observed": gate_obs,
              "text": "OG: SHA-256, rows, samples, one OTA row each, product-label counts, origin "
                      "facts, one known unit, 220 positive and 276 token cells, at most 10 "
                      "tokens; MM: SHA-256, rows, 750 OTA rows, 20 OTA positives, minimum 0.8, "
                      "known units; the 7 shared product labels"}]

    def add(pid, kind, text, observed, met):
        preds.append({"id": pid, "kind": kind, "graded": open_, "met": bool(open_ and met),
                      "text": text, "observed": observed})

    for rid, text, _labels, n, pos, mn, mx, avg in ROWS:
        r = a["rows"][rid]
        add(rid, "consistency",
            f"{text}: n {n}, positives {pos}, min {mn}, max {mx}, avg {avg} (printed)",
            r["detail"], r["ok"])
    ov = a["overall"]
    add("C5", "consistency", "the file's smallest positive matches 0.042 and its largest 11",
        {"min": ov["min"], "max": ov["max"]}, matches(ov["min"], "0.042")
        and matches(ov["max"], "11"))

    for rid, text, _labels, n, pct, mn, mx, avg in PCT_ROWS:
        r = a["rows"][rid]
        add(rid, "consistency",
            f"{text}: n {n}, {pct}% positive, min {mn}, max {mx}, avg {avg} (printed)",
            r["detail"], r["ok"])

    bw, qu = a["families"]["buckwheat"], a["families"]["quinoa"]
    add("P1", "prediction",
        "Buckwheat Products: maximum matches 7.6, 9-11 positives; Quinoa Products: maximum "
        "matches 5.8, 7-8 positives",
        {"buckwheat": bw, "quinoa": qu},
        matches(bw["max"], "7.6") and P1_BUCK_POS[0] <= bw["pos"] <= P1_BUCK_POS[1]
        and matches(qu["max"], "5.8") and P1_QUIN_POS[0] <= qu["pos"] <= P1_QUIN_POS[1])

    ka = a["families"]["kamut"]
    add("P2", "prediction", "the 25 kamut-labelled samples: 9-10 positives, maximum at most 1.25",
        ka, P2_POS[0] <= ka["pos"] <= P2_POS[1] and ka["max"] is not None
        and ka["max"] <= P2_MAX)

    out3 = a["over_3_outside_no_limit"]
    add("P3", "prediction",
        "exactly one sample outside the Buckwheat Products and Quinoa Products labels is above "
        "3 ppb, and it is a Grain - Rice sample (CFIA's 99.8% compliance)",
        {"over_3": a["over_3"], "outside": out3},
        len(out3) == 1 and out3[0]["product"] == "Grain - Rice")

    cr = a["cross"]
    add("P4", "prediction",
        "on the 7 shared product labels, at a common 0.8 ppb cut, OTA detection in the OTA-only "
        "file does not differ from the multi-mycotoxin file (CMH two-sided p >= 0.05)",
        {k: cr[k] for k in ("at_cut", "at_cut_pooled", "at_cut_mh_or", "at_cut_cmh_chi2",
                            "at_cut_cmh_p")},
        cr["at_cut_cmh_p"] >= P4_ALPHA)

    ck = a["labels"].get("Crackers", {"n": 0, "pos": 0, "ge_cut": 0})
    add("P5", "prediction",
        "Crackers (29): at least 20 positive, and at most 3 at or above 0.8 ppb",
        ck, ck["n"] == 29 and ck["pos"] >= P5_POS_MIN and ck["ge_cut"] <= P5_CUT_MAX)

    add("P6", "prediction", "10 to 39 of the 496 samples are at or above 0.8 ppb",
        {"ge_cut": ov["ge_cut"], "n": ov["n"]},
        P6_BAND[0] <= ov["ge_cut"] <= P6_BAND[1])
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
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-ota-grain-2018"})
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


def write_outputs(out_dir, og, census, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "ota_grain_2018_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "product", "family", "origin", "detected", "ota_ng_g"])
        for r in sorted(og, key=lambda x: x["sample"]):
            w.writerow([r["sample"], r["product"], r["family"], r["origin"],
                        1 if r["detected"] else 0, repr(r["ota"])])
    with open(os.path.join(out_dir, "ota_grain_2018_crossmethod.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["product", "og_n", "og_detected", "og_ge_0_8", "mm_n", "mm_detected"])
        for lab in SHARED_LABELS:
            cut, own = a["cross"]["at_cut"][lab], a["cross"]["own_limits"][lab]
            w.writerow([lab, own[0] + own[1], own[0], cut[0], own[2] + own[3], own[2]])
    result = {"study": "ota-grain-2018", "version": VERSION, "predictions": preds,
              "census": census, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "ota_grain_2018_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the ota-grain-2018 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    raw_og, src_og = load(OG, args.data_dir)
    raw_mm, src_mm = load(MM, args.data_dir)
    text_og, enc_og = decode(raw_og)
    text_mm, enc_mm = decode(raw_mm)
    s_og, c_og = parse_text(text_og)
    s_mm, c_mm = parse_text(text_mm, only_component=OTA)
    og, mm = list(s_og.values()), list(s_mm.values())
    gate_obs = gate_checks(c_og, c_mm, og, mm, _sha(raw_og) == OG["sha256"],
                           _sha(raw_mm) == MM["sha256"])
    a = analyse(og, mm)
    preds = grade(a, gate_obs)
    provenance = {
        "OG": {"resource": OG["resource"], "sha256": OG["sha256"], "bytes": len(raw_og),
               "source": src_og, "encoding": enc_og},
        "MM": {"resource": MM["resource"], "sha256": MM["sha256"], "bytes": len(raw_mm),
               "source": src_mm, "encoding": enc_mm},
    }
    result = write_outputs(args.out_dir, og, {"OG": c_og, "MM": c_mm}, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gate": gate_obs,
                      "og_tokens": c_og["text_tokens"], "og_units": c_og["units"],
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if preds[0]["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
