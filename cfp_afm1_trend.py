#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""cfp-afm1-trend 0.1.0: aflatoxin M1 (AFM1) in six open CFIA Children's Food Project files
(2012-13, 2014-15, 2016, 2018, 2020, 2022) against every figure CFIA printed for them.

Grades docs/cfp-afm1-trend-0.1.0-prereg.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

The Canadian Food Inspection Agency (CFIA) publishes one per-sample CSV per Children's Food
Project (CFP) year on open.canada.ca (Open Government Licence - Canada). A names-only census of
all 16 files (job cfp-afm1-years-census-v2, 2026-10-29) found AFM1 rows in six of them. CFIA's
report pages print, for those years: 2012-13 "detectable levels ... in 12% of samples"; 2014-15
4 of 20 formulas at 0.011-0.061 ppb and no yogurt or pudding positive; 2016 7 of 63 formulas at
0.018-0.080 ppb plus one infant biscuit at 0.022 ppb; 2018 10 of 52 formulas at 0.01-0.086 ppb;
2020 0 of 76 yogurts and puddings; 2022 1 of 93 (an infant formula at 0.0566 ppb).

Each year is gated on its own census facts (SHA-256, AFM1 rows and samples, units, product
classes) and a value rule fixed before any value was read. Only years that pass are graded.
Files are SHA-256 pinned. Standard library only. Code Apache-2.0; derived data CC BY 4.0.
Not a compliance finding, not about any brand, and not individual dietary or medical advice.
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
YEARS = ("2012-13", "2014-15", "2016", "2018", "2020", "2022")

# label -> (dataset, resource, download path, SHA-256), from job cfp-afm1-years-census-v2.
FILES = {
    "2012-13": ("abc1b7e7-6fcc-4bd5-a0a9-deac523bee2f", "94d64ebb-83d0-4ca3-8c4f-ff6470dafb24",
                "cfia-acia-1536_2012-13_childrens-food-project.csv",
                "0b0ae681f0224b5602a6b635fb62b33e519733662b7da5d40b131b1730792931"),
    "2014-15": ("e60c218f-01bf-41f5-9237-77be288feecb", "b2a54434-7683-4ea3-bf60-392366153403",
                "cfia-acia-1537_2014-15_childrens-food-project.csv",
                "d2cfa733ff78e3cdc04f92e47a4b9e578e7cab8839fe1778972ecd6f98f7da59"),
    "2016": ("94850076-10c7-43e1-9ee4-b4f602363e4b", "ee83840e-5441-40fe-8d38-37dfe209ef57",
             "cfia-acia-1192-2016_fssd_chem_childrens-food-project_-_projet-sur-les-aliments-"
             "destines-aux-enfa.csv",
             "6a8b9c788e9f07128c4b7313fa4add6e706e7cd0540e7eb59639c1490b1cfdbe"),
    "2018": ("66c8ff38-27e8-4e1a-9270-ebbdede8a2e6", "3ab80a87-25a7-4aea-b510-0301c1232081",
             "cfia_acia-15022622-v2-cfp-2018-fssd-chem-open-data.csv",
             "be6a1d7c1648570f18266af0e31eefc7d4791cfbb82e4f3add45bf0bb4659755"),
    "2020": ("b1974f49-da37-4783-8705-97bfe6720a2c", "feebccc6-1eaf-4a5b-83e7-a3b468a912b8",
             "cfia_acia-1264-v1-cfp2020_open_data.csv",
             "e1c895c55ae52386cdd43898afc236a92086affb6409cd272e7604291eb27b46"),
    "2022": ("11fedc77-176a-4af0-9ddc-1bfa8ae1a894", "517c84f1-d317-4566-b118-b17359919f1f",
             "cfp-pae-2022.csv",
             "14d3712ee0d4b9fcfaefe940670b1f7b352c5c9b249f25190f2cf725eb851c61"),
}

MICRO_G = "µg/g"
# Census facts (job cfp-afm1-years-census-v2): AFM1 rows, distinct samples, units (rows), and
# samples per product class (formula / dairy-dessert / other, by the rule in product_class).
CENSUS = {
    "2012-13": {"rows": 101, "samples": 101, "units": {"ng/g": 101},
                "classes": {"formula": 101}},
    "2014-15": {"rows": 32, "samples": 32, "units": {MICRO_G: 32},
                "classes": {"formula": 22, "dairy-dessert": 6, "other": 4}},
    "2016": {"rows": 114, "samples": 114, "units": {"ng/g": 114},
             "classes": {"formula": 63, "dairy-dessert": 19, "other": 32}},
    "2018": {"rows": 52, "samples": 52, "units": {"ng/g": 52}, "classes": {"formula": 52}},
    "2020": {"rows": 152, "samples": 76, "units": {"ng/g": 152},
             "classes": {"dairy-dessert": 76}},
    "2022": {"rows": 93, "samples": 93, "units": {"ng/g": 93},
             "classes": {"formula": 34, "dairy-dessert": 59}},
}

# ppb = ng/g = ug/kg. Units are converted by this table only.
UNIT_TO_PPB = {"ng/g": 1.0, "µg/kg": 1.0, "ug/kg": 1.0, "ppb": 1.0,
               MICRO_G: 1000.0, "ug/g": 1000.0}
# Text that means "not detected" (upper case, dots and extra spaces removed). NA, N/A, NQ, BLQ
# and <LOQ are NOT here: they do not say the toxin was absent, so they fail the value rule.
ND_TOKENS = {"ND", "NOT DETECTED", "NON DETECTED", "NOTDETECTED", "NON DÉTECTÉ", "BRL",
             "BELOW RL", "BELOW REPORTING LIMIT", "<RL", "<LOD", "<MDL", "<LOD/MDL"}

# Registered figures (CFIA report pages, read 2026-10-29).
CODEX = 0.5
C1_DET = 12                                    # 2012-13: "12%" of the 101 AFM1 samples
C1_REPORT_N = 148                              # the report's formula total (reference only)
C2_DET = 4                                     # 2014-15: 4 formulas, none of the others
C3 = {"formula": 7, "range": ("0.018", "0.080"), "other": {"Infant Biscuit": 1},
      "other_value": "0.022"}
C4 = {"det": 10, "range": ("0.01", "0.086")}
C6 = {"det": 1, "value": "0.0566"}
P1_MAX = 0.1
P2_RANGE = ("0.011", "0.061")
P5_CUT = 0.02
EARLIER = ("2012-13", "2014-15", "2016", "2018")
COLS = ("sample", "component", "value", "unit", "product")


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def clean(cell):
    return (cell or "").replace("﻿", "").strip()


def head(name):
    """Normalised English part of a header cell: 'Component/Composante' -> 'component'."""
    h = clean(name).strip('"').lower().replace("_", " ")
    return " ".join(h.split("/")[0].split())


def number(raw):
    """A cell as a float, reading one decimal comma as a point; None if not a finite number."""
    s = (raw or "").strip()
    if not s:
        return None
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def unit_key(unit):
    return clean(unit).lower().replace("μ", "µ").replace(" ", "")


def is_afm1(text):
    """True if a cell names aflatoxin M1 (English or French, any case or hyphenation)."""
    c = clean(text).lower().replace("-", " ").replace("aflatoxine", "aflatoxin")
    c = " ".join(c.split())
    return "aflatoxin m1" in c or c == "afm1"


def product_class(product):
    p = product.lower()
    if "formula" in p:
        return "formula"
    if "yogurt" in p or "yoghurt" in p or "pudding" in p:
        return "dairy-dessert"
    return "other"


def formula_type(product):
    p = product.lower()
    if "formula" not in p:
        return ""
    if "soy" in p:
        return "soy"
    if "special" in p:
        return "specialized"
    if "milk" in p or "dairy" in p:
        return "milk"
    return "other"


def parse_value(raw):
    """(value, kind) for one AFM1 result cell. A number above 0 is 'det'. A 0, a '<' with a
    number >= 0 (including '<0') or a not-detected token is 'nd'. Anything else (blank, other
    text, a negative) is 'bad' and fails that year's gate."""
    s = clean(raw)
    if not s:
        return None, "bad"
    key = " ".join(s.upper().replace(".", "").split())
    if key in ND_TOKENS or key.replace(" ", "") in ND_TOKENS:
        return 0.0, "nd"
    if s.startswith("<"):
        v = number(s[1:])
        return (0.0, "nd") if v is not None and v >= 0 else (None, "bad")
    v = number(s)
    if v is None or v < 0:
        return None, "bad"
    return (0.0, "nd") if v == 0 else (v, "det")


def mask(raw):
    return "".join("#" if ch.isdigit() else ch for ch in clean(raw))


def half_unit(printed):
    return 0.5 * 10 ** -len(printed.split(".")[1]) if "." in printed else 0.5


def matches(x, printed):
    """True if x rounds to the printed figure at its printed precision."""
    return x is not None and abs(x - float(printed)) <= half_unit(printed) + 1e-9


def wilson(k, n, z=1.959963984540054):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, centre - half), min(1.0, centre + half)]


def fisher_less(k1, n1, k2, n2):
    """One-sided exact P(X <= k1) for k1 of n1 against k2 of n2 (hypergeometric, margins fixed)."""
    k, n = k1 + k2, n1 + n2
    total = math.comb(n, k)
    lo = max(0, k - n2)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(lo, k1 + 1)) / total


def find_columns(header):
    """Map roles to column indexes (None if absent). CFP layouts differ between years."""
    h = [head(c) for c in header]

    def pick(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    return {
        "sample": pick(lambda c: c.startswith("sample") and "type" not in c and "date" not in c),
        "component": pick(lambda c: c.startswith("component")),
        "value": pick(lambda c: c.startswith("amount")
                      or (c.startswith("result") and not c.startswith("result unit"))),
        "unit": pick(lambda c: c.startswith("report unit") or c.startswith("unit")
                     or c.startswith("result unit")),
        "product": pick(lambda c: c.startswith("product")),
        "origin": pick(lambda c: c.startswith("origin")),
    }


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def _cell(r, i):
    return r[i] if i is not None and i < len(r) else ""


def empty_census(col=None):
    return {"columns": col or {}, "rows": 0, "units": {}, "kinds": {}, "bad_shapes": [],
            "samples": 0, "classes": {}}


def parse_year(text):
    """(samples, census) for the AFM1 rows of one decoded CFP CSV. A sample is detected if any
    of its AFM1 rows is detected; its stored value is the largest detected value."""
    rows = csv.reader(io.StringIO(text))
    col = find_columns(next(rows, []))
    census = empty_census(col)
    if any(col[k] is None for k in COLS):
        return [], census
    by = {}
    for r in rows:
        if not any(c.strip() for c in r) or not is_afm1(_cell(r, col["component"])):
            continue
        raw = clean(_cell(r, col["value"]))
        v, kind = parse_value(raw)
        unit = unit_key(_cell(r, col["unit"]))
        census["rows"] += 1
        _bump(census["units"], unit)
        _bump(census["kinds"], kind)
        if kind == "bad" and mask(raw) not in census["bad_shapes"]:
            census["bad_shapes"].append(mask(raw))
        sid = clean(_cell(r, col["sample"]))
        s = by.get(sid)
        if s is None:
            product = clean(_cell(r, col["product"]))
            s = by[sid] = {"sample": sid, "product": product, "class": product_class(product),
                           "type": formula_type(product), "origin": clean(_cell(r, col["origin"])),
                           "unit": unit, "raws": [], "kinds": [], "stored": 0.0}
        s["raws"].append(raw)
        s["kinds"].append(kind)
        if kind == "det":
            s["stored"] = max(s["stored"], v)
    samples = list(by.values())
    for s in samples:
        s["kind"] = "bad" if "bad" in s["kinds"] else ("det" if "det" in s["kinds"] else "nd")
        _bump(census["classes"], s["class"])
    census["samples"] = len(samples)
    return samples, census


def gate_checks(census, sha_ok, expected):
    return {
        "sha256": bool(sha_ok),
        "columns": all(census["columns"].get(k) is not None for k in COLS),
        "rows": census["rows"] == expected["rows"],
        "samples": census["samples"] == expected["samples"],
        "units": census["units"] == expected["units"],
        "classes": census["classes"] == expected["classes"],
        "values": census["rows"] > 0 and census["kinds"].get("bad", 0) == 0,
    }


def year_stats(samples, fac):
    """Counts and detected values (stored value x fac) per product class for one year."""
    out = {"n": len(samples), "det": 0, "by_class": {}}
    for s in samples:
        c = out["by_class"].setdefault(s["class"], {"n": 0, "det": 0, "values": [],
                                                   "det_products": {}})
        c["n"] += 1
        if s["kind"] == "det":
            out["det"] += 1
            c["det"] += 1
            c["values"].append(s["stored"] * fac)
            _bump(c["det_products"], s["product"])
    for c in out["by_class"].values():
        c["values"].sort()
        c["min"] = c["values"][0] if c["values"] else None
        c["max"] = c["values"][-1] if c["values"] else None
    vals = sorted(v for c in out["by_class"].values() for v in c["values"])
    out["max"] = vals[-1] if vals else None
    return out


def cls(stats, c):
    return stats["by_class"].get(c) or {"n": 0, "det": 0, "values": [], "det_products": {},
                                        "min": None, "max": None}


def unit_reading(stats):
    """Which reading of 2014-15's ug/g label reproduces the printed 0.011-0.061 ppb formula range:
    'stored' (the numbers are already ppb, so the label is 1000x off), 'labelled' (ug/g x 1000)
    or None (neither)."""
    f = cls(stats, "formula")
    out = {"formula_min_stored": f["min"], "formula_max_stored": f["max"], "as_stored": False,
           "as_labelled": False, "reading": None}
    if f["min"] is None:
        return out
    fac = UNIT_TO_PPB[MICRO_G]
    out["as_stored"] = matches(f["min"], P2_RANGE[0]) and matches(f["max"], P2_RANGE[1])
    out["as_labelled"] = (matches(f["min"] * fac, P2_RANGE[0])
                          and matches(f["max"] * fac, P2_RANGE[1]))
    out["reading"] = ("stored" if out["as_stored"] else
                      "labelled" if out["as_labelled"] else None)
    return out


def analyse(passing):
    """passing: {year: samples} for the years whose gate passed."""
    stats = {y: year_stats(s, 1.0) for y, s in passing.items()}
    a = {"stats": stats, "unit_2014_15": None}
    factors = {y: 1.0 for y in passing}
    if "2014-15" in passing:
        r = unit_reading(stats["2014-15"])
        a["unit_2014_15"] = r
        if r["reading"] == "labelled":
            factors["2014-15"] = UNIT_TO_PPB[MICRO_G]
        elif r["reading"] is None:
            factors.pop("2014-15")
    a["ppb_factor"] = factors
    cut = {}
    for y, fac in factors.items():
        f = [s for s in passing[y] if s["class"] == "formula"]
        if not f:
            continue
        k = sum(1 for s in f if s["kind"] == "det" and s["stored"] * fac >= P5_CUT - 1e-12)
        cut[y] = {"n": len(f), "k": k, "rate": k / len(f), "ci95": wilson(k, len(f))}
    earlier = [y for y in EARLIER if y in cut]
    pn = sum(cut[y]["n"] for y in earlier)
    pk = sum(cut[y]["k"] for y in earlier)
    p5 = {"cut_ppb": P5_CUT, "earlier_years": earlier, "pooled_n": pn, "pooled_k": pk,
          "pooled_rate": pk / pn if pn else None, "pooled_ci95": wilson(pk, pn),
          "y2022": cut.get("2022"), "fisher_one_sided_p": None}
    if "2022" in cut and pn:
        p5["fisher_one_sided_p"] = fisher_less(cut["2022"]["k"], cut["2022"]["n"], pk, pn)
    a["formula_at_cut"] = cut
    a["p5"] = p5
    dd = {"years": {}, "n": 0, "det": 0}
    for y in sorted(passing):
        d = [s for s in passing[y] if s["class"] == "dairy-dessert"]
        if d:
            k = sum(1 for s in d if s["kind"] == "det")
            dd["years"][y] = {"n": len(d), "det": k}
            dd["n"] += len(d)
            dd["det"] += k
    dd["ci95"] = wilson(dd["det"], dd["n"])
    a["dairy_dessert"] = dd
    ng = sorted(y for y in passing if y != "2014-15")
    mx = [stats[y]["max"] for y in ng if stats[y]["max"] is not None]
    a["p1"] = {"years": ng, "max_ppb": max(mx) if mx else None}
    if "2012-13" in passing:
        types, det_types = {}, {}
        for s in passing["2012-13"]:
            _bump(types, s["type"])
            if s["kind"] == "det":
                _bump(det_types, s["type"])
        a["p4"] = {"types": types, "det_types": det_types}
    return a


def _slim(c):
    return {k: c[k] for k in ("n", "det", "min", "max", "det_products")}


def grade(a, gates):
    ok = {y: all(gates[y].values()) for y in YEARS}
    st = a["stats"]
    preds = [{"id": "G", "kind": "gate", "graded": True, "met": all(ok.values()),
              "observed": {"per_year": gates, "passing": [y for y in YEARS if ok[y]]},
              "text": "per year: SHA-256; AFM1 rows and distinct samples, units and samples per "
                      "product class as in the census; every AFM1 result detected (a number "
                      "above 0) or not detected (0, '<' with a number >= 0, or a not-detected "
                      "token). Each year is graded only if its own gate passes."}]

    def add(pid, kind, text, graded, observe, met):
        o = observe() if graded else {}
        preds.append({"id": pid, "kind": kind, "graded": bool(graded),
                      "met": bool(graded and met(o)), "text": text, "observed": o})

    def yr(y):
        s = st[y]
        return {"n": s["n"], "det": s["det"], "max": s["max"],
                "classes": {c: _slim(v) for c, v in s["by_class"].items()}}

    add("C1", "consistency", "2012-13 report: detectable AFM1 in 12% of samples (12 of the 101 "
        "AFM1 samples; no other count rounds to 12%), all below the Codex 0.5 ppb",
        ok["2012-13"], lambda: {**yr("2012-13"),
                                "pct_of_101": 100 * st["2012-13"]["det"] / st["2012-13"]["n"],
                                "pct_of_148": 100 * st["2012-13"]["det"] / C1_REPORT_N},
        lambda o: o["det"] == C1_DET and (o["max"] is None or o["max"] < CODEX))
    add("C2", "consistency", "2014-15 report: AFM1 in 4 infant formulas and in no yogurt, "
        "pudding or other sample", ok["2014-15"], lambda: yr("2014-15"),
        lambda o: o["det"] == C2_DET and o["classes"].get("formula", {}).get("det") == C2_DET)

    def c3(o):
        f = o["classes"].get("formula", {})
        x = o["classes"].get("other", {})
        d = o["classes"].get("dairy-dessert", {})
        return (f.get("det") == C3["formula"] and matches(f.get("min"), C3["range"][0])
                and matches(f.get("max"), C3["range"][1]) and x.get("det") == 1
                and x.get("det_products") == C3["other"]
                and matches(x.get("max"), C3["other_value"]) and d.get("det", 0) == 0)

    add("C3", "consistency", "2016 report: AFM1 in 7 of 63 formulas at 0.018-0.080 ppb and in 1 "
        "infant biscuit at 0.022 ppb; nothing else", ok["2016"], lambda: yr("2016"), c3)

    def c4(o):
        f = o["classes"].get("formula", {})
        return (o["det"] == C4["det"] and matches(f.get("min"), C4["range"][0])
                and matches(f.get("max"), C4["range"][1]))

    add("C4", "consistency", "2018 report: AFM1 in 10 of 52 formulas at 0.01-0.086 ppb",
        ok["2018"], lambda: yr("2018"), c4)
    add("C5", "consistency", "2020 report: no AFM1 in any of 76 yogurts, yogurt beverages and "
        "puddings", ok["2020"], lambda: yr("2020"), lambda o: o["det"] == 0)
    add("C6", "consistency", "2022 report: AFM1 in 1 of 93 samples, an infant formula, at 0.0566 "
        "ppb", ok["2022"], lambda: yr("2022"),
        lambda o: (o["det"] == C6["det"] and o["classes"].get("formula", {}).get("det") == 1
                   and matches(o["classes"]["formula"].get("max"), C6["value"])))
    add("P1", "prediction", "every detected AFM1 value in the ng/g years is below 0.1 ppb (a "
        "fifth of the Codex 0.5 ppb)", bool(a["p1"]["years"]), lambda: a["p1"],
        lambda o: o["max_ppb"] is None or o["max_ppb"] < P1_MAX)
    add("P2", "prediction", "2014-15's ug/g label is 1000x off: the stored formula positives "
        "already match the printed 0.011-0.061 ppb", ok["2014-15"],
        lambda: a["unit_2014_15"], lambda o: o["reading"] == "stored")
    add("P3", "prediction", "no AFM1 in any yogurt, yogurt beverage or pudding in any graded "
        "year", a["dairy_dessert"]["n"] > 0, lambda: a["dairy_dessert"],
        lambda o: o["det"] == 0)
    add("P4", "prediction", "2012-13: every detection is a milk-based formula (none in the "
        "specialized or soy formulas)", ok["2012-13"], lambda: a["p4"],
        lambda o: bool(o["det_types"]) and set(o["det_types"]) == {"milk"})
    p5 = a["p5"]
    add("P5", "prediction", "infant formula at a common 0.02 ppb cut: the 2022 rate is below the "
        "pooled 2012-13 to 2018 rate (point estimates; Fisher p and Wilson intervals reported)",
        p5["y2022"] is not None and p5["pooled_n"] > 0, lambda: p5,
        lambda o: o["y2022"]["rate"] < o["pooled_rate"])
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
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-cfp-afm1-trend"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(label, data_dir):
    dataset, resource, path, sha = FILES[label]
    local = os.path.join(data_dir, resource + ".csv") if data_dir else ""
    if local and os.path.exists(local):
        with open(local, "rb") as fh:
            raw = fh.read()
        if _sha(raw) == sha:
            return raw, "data-volume"
    errors = []
    for host in ("https://open.canada.ca", "https://ouvert.canada.ca"):
        url = f"{host}/data/dataset/{dataset}/resource/{resource}/download/{path}"
        try:
            raw = _fetch(url)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        if _sha(raw) != sha:
            errors.append(f"{url}: SHA-256 {_sha(raw)} != {sha}")
            continue
        return raw, url
    raise RuntimeError(f"{label}: no verified copy: " + "; ".join(errors))


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
    if isinstance(x, (set, tuple)):
        return sorted(x) if isinstance(x, set) else list(x)
    return "" if x is None else (round(x, 6) if isinstance(x, float) else x)


def write_outputs(out_dir, samples_by, censuses, a, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "cfp_afm1_trend_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "sample", "product", "class", "formula_type", "origin", "unit",
                    "n_rows", "values_raw", "kind", "value_stored", "unit_factor_to_ppb"])
        for y in YEARS:
            for s in sorted(samples_by.get(y, []), key=lambda s: s["sample"]):
                w.writerow([y, s["sample"], s["product"], s["class"], s["type"], s["origin"],
                            s["unit"], len(s["raws"]), ";".join(s["raws"]), s["kind"],
                            repr(s["stored"]), UNIT_TO_PPB.get(s["unit"], "")])
    result = {"study": "cfp-afm1-trend", "version": VERSION, "predictions": preds,
              "census": censuses, "analysis": a, "provenance": provenance,
              "n_graded": sum(1 for p in preds if p["graded"]),
              "n_met": sum(1 for p in preds if p["met"])}
    with open(os.path.join(out_dir, "cfp_afm1_trend_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True, default=_r, ensure_ascii=False)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the cfp-afm1-trend 0.1.0 pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    gates, samples_by, censuses, provenance = {}, {}, {}, {}
    for y in YEARS:
        try:
            raw, src = load(y, args.data_dir)
            text, enc = decode(raw)
            samples, census = parse_year(text)
            sha_ok = _sha(raw) == FILES[y][3]
            provenance[y] = {"resource": FILES[y][1], "sha256": FILES[y][3], "bytes": len(raw),
                             "source": src, "encoding": enc}
            del raw, text
        except Exception as exc:  # noqa: BLE001 - that year's gate fails, with the reason
            samples, census, sha_ok = [], empty_census(), False
            census["error"] = f"{type(exc).__name__}: {exc}"
            provenance[y] = {"resource": FILES[y][1], "error": census["error"]}
        gates[y] = gate_checks(census, sha_ok, CENSUS[y])
        samples_by[y] = samples
        censuses[y] = census
    passing = {y: samples_by[y] for y in YEARS if all(gates[y].values())}
    a = analyse(passing)
    preds = grade(a, gates)
    result = write_outputs(args.out_dir, samples_by, censuses, a, preds, provenance)
    print(json.dumps({"version": VERSION, "gates": gates,
                      "kinds": {y: censuses[y]["kinds"] for y in YEARS},
                      "bad_shapes": {y: censuses[y]["bad_shapes"] for y in YEARS},
                      "predictions": [(p["id"], p["graded"], p["met"]) for p in preds],
                      "n_met": result["n_met"], "n_graded": result["n_graded"]},
                     indent=2, default=_r, ensure_ascii=False))
    return 0 if passing else 1


if __name__ == "__main__":
    sys.exit(main())
