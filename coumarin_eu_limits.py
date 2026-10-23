#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""coumarin_eu_limits 0.1.1: how often does coumarin in Canadian cinnamon-containing foods
exceed the EU maximum level that would apply to the same food category in Europe?

Grades docs/coumarin-eu-limits-0.1.0-prereg.md as amended by
docs/coumarin-eu-limits-0.1.1-amendment.md. Made with AI agents working in MV2's (Munim, Inc.)
name.

0.1.1 fixes one unit-conversion bug that the pre-registered G0 gate caught in 0.1.0: CFIA's
2013-14 file reports coumarin in micrograms per gram (ug/g, which equals mg/kg), but 0.1.0 divided
any unit containing "ug" by 1000, so every value came out 1000x too small (pooled max 2.51 instead
of CFIA's 2,510 mg/kg). Units are now converted by an explicit table, and the grader reports a
census of the units it saw. Classification, limits and every prediction threshold are unchanged.

The EU sets maximum levels for coumarin in specific finished-food categories (Regulation (EC) No
1334/2008, Annex III Part B). Canada (CFIA) sets none, but publishes per-sample coumarin
concentrations as open data. This tool compares CFIA's 2013-14 survey to the EU limits that would
apply to the same food categories, reproducibly. It is a cross-jurisdiction REFERENCE comparison,
not a compliance finding, and not individual dietary or medical advice.

Data: CFIA 2013-14 coumarin survey (Open Government Licence - Canada), read from the sealed data
volume (/data/cfia-2013-14-coumarin.csv) and verified by SHA-256 before any value is read; if the
copy is absent it is re-downloaded through ouvert.canada.ca's CKAN API and re-checked.
Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import statistics
import sys
import time
import urllib.request

VERSION = "0.1.1"

# CFIA 2013-14 coumarin survey, pinned resource and expected digest (set by the names-only job).
API = "https://ouvert.canada.ca/data/api/action/resource_show?id="
RESOURCE = "66d9cd8f-d44d-4993-8775-65da6857250c"
RAW_NAME = "cfia-2013-14-coumarin.csv"
RAW_SHA256 = "3c8a18c0769d81e9580b9f985722ccd24e9db45c72ea9228f3eda8afd3383f4f"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 coumarin_eu_limits/%s (MV2 of Munim, Inc.; mv2@munimtech.com)"
      % VERSION)

# EU Annex III Part B coumarin maximum levels (mg/kg) for the mapped analogue groups.
LIMITS = {"fine-bakery": 15.0, "breakfast-cereal": 20.0}

# Pre-registered prediction thresholds (unchanged from 0.1.0).
G0_N_ROWS = (740, 749)
G0_MAX_PPM = (2200.0, 2800.0)
P1_FINE_SHARE = (0.20, 0.50)      # fine-bakery share with ppm > 15
P2_CEREAL_SHARE = (0.03, 0.22)    # cereal-core share with ppm > 20

# Non-detect / below-detection tokens -> 0.0 mg/kg (under every EU coumarin limit).
ND_TOKENS = {"nd", "n.d.", "n/d", "n.d", "trace", "<lod", "<loq", "nq", "not detected"}
_NUM_RE = re.compile(r"\d+(?:\.\d+)?")

# Multiplier taking a normalised unit to mg/kg (0.1.1). Both micro signs normalise to "u".
MICRO_SIGNS = ("µ", "μ")
UNIT_FACTORS = {
    "": 1.0, "mg/kg": 1.0, "ppm": 1.0, "ug/g": 1.0, "mcg/g": 1.0,
    "ppb": 0.001, "ug/kg": 0.001, "mcg/kg": 0.001, "ng/g": 0.001,
    "mg/g": 1000.0, "g/kg": 1000.0, "%": 10000.0,
}


# ---------------------------------------------------------------------------
# Pure functions (unit-tested offline).
# ---------------------------------------------------------------------------
def norm_unit(unit):
    """Lower-case a unit, drop spaces and write either micro sign as "u"."""
    u = (unit or "").strip().lower().replace(" ", "")
    for m in MICRO_SIGNS:
        u = u.replace(m, "u")
    return u


def unit_factor(unit):
    """Multiplier taking `unit` to mg/kg, or None if the unit is not recognised.

    A trailing parenthetical (e.g. "ug/g (ppm)") is ignored if the full string is unknown.
    """
    u = norm_unit(unit)
    if u in UNIT_FACTORS:
        return UNIT_FACTORS[u]
    head = u.split("(")[0]
    return UNIT_FACTORS.get(head) if head != u else None


def parse_ppm(result, unit=""):
    """Parse a CFIA Result/Unit pair into coumarin mg/kg. Returns float or None.

    Non-detect / below-detection -> 0.0. A blank result -> None (not measured). The value is
    multiplied by unit_factor(unit); an unrecognised unit is taken as mg/kg, as in 0.1.0, and
    shows up in the summary's unit census.
    """
    if result is None:
        return None
    s = str(result).strip()
    if s == "":
        return None
    low = s.lower()
    if low in ND_TOKENS or low.startswith("<") or low.startswith("nd") or "not detect" in low:
        return 0.0
    t = low.lstrip("<>=~≤≥ ").replace(",", ".").replace(" ", "")
    m = _NUM_RE.match(t)
    if not m:
        return None
    val = float(m.group(0))
    f = unit_factor(unit)
    return val * (1.0 if f is None else f)


def classify(product):
    """Map an English CFIA product name to an EU-analogue sub-category token (first rule wins)."""
    p = (product or "").lower()
    if "spice" in p:
        return "spice"            # out-of-scope: EU exempts herbs & spices
    if "tea" in p:
        return "tea"              # out-of-scope: beverage
    if "mix" in p:
        return "mix"              # out-of-scope: dry mix, not "as consumed"
    if "infant" in p:
        return "infant"           # out-of-scope: infant food separately regulated
    if "bar" in p:
        return "bar"              # out-of-scope: snack bar, not breakfast cereal
    if "oatmeal" in p:
        return "oatmeal"          # breakfast-cereal (sub-group oatmeal)
    if "cereal" in p:
        return "cereal"           # breakfast-cereal (sub-group cereal)
    if "bread" in p or "bagel" in p:
        return "bread"            # out-of-scope: bread carries no EU coumarin limit
    if "cookie" in p:
        return "cookie"           # fine-bakery
    if "muffin" in p:
        return "muffin"           # fine-bakery
    if "baked good" in p:
        return "baked-goods"      # fine-bakery
    return "unmapped"             # out-of-scope


GROUP_OF = {
    "oatmeal": "breakfast-cereal", "cereal": "breakfast-cereal",
    "cookie": "fine-bakery", "muffin": "fine-bakery", "baked-goods": "fine-bakery",
}


def group_of(subcat):
    return GROUP_OF.get(subcat, "out-of-scope")


def _stat(rows, limit):
    """Descriptive + over-limit stats for a selection of measured rows."""
    n = len(rows)
    over = sum(1 for r in rows if r["ppm"] > limit)
    det = sum(1 for r in rows if r["ppm"] > 0)
    ppms = sorted(r["ppm"] for r in rows)
    return {
        "n": n, "n_detected": det, "n_over_limit": over, "limit": limit,
        "share_over_all": (over / n) if n else None,
        "share_over_detected": (over / det) if det else None,
        "ppm_min": ppms[0] if n else None,
        "ppm_median": statistics.median(ppms) if n else None,
        "ppm_max": ppms[-1] if n else None,
    }


def summarise(rows):
    """Build per-group stats from parsed rows (each a dict with ppm/group/subcat)."""
    measured = [r for r in rows if r["ppm"] is not None]
    pooled_max = max((r["ppm"] for r in measured), default=None)
    fine = [r for r in measured if r["group"] == "fine-bakery"]
    cereal_core = [r for r in measured if r["subcat"] == "cereal"]
    oatmeal = [r for r in measured if r["subcat"] == "oatmeal"]
    cereal_all = [r for r in measured if r["group"] == "breakfast-cereal"]
    units = {}
    for r in measured:
        k = norm_unit(r.get("unit_raw", ""))
        units[k] = units.get(k, 0) + 1
    return {
        "n_rows": len(measured),
        "pooled_max_ppm": pooled_max,
        "fine_bakery": _stat(fine, LIMITS["fine-bakery"]),
        "cereal_core": _stat(cereal_core, LIMITS["breakfast-cereal"]),
        "oatmeal": _stat(oatmeal, LIMITS["breakfast-cereal"]),
        "cereal_all": _stat(cereal_all, LIMITS["breakfast-cereal"]),
        "units": dict(sorted(units.items())),
        "n_unrecognised_unit": sum(c for k, c in units.items() if unit_factor(k) is None),
    }


def grade(s):
    """Grade the pre-registered predictions from a summarise() dict."""
    preds = []

    g0 = (s["pooled_max_ppm"] is not None
          and G0_N_ROWS[0] <= s["n_rows"] <= G0_N_ROWS[1]
          and G0_MAX_PPM[0] <= s["pooled_max_ppm"] <= G0_MAX_PPM[1])
    preds.append({
        "id": "G0", "kind": "gate",
        "text": f"measured rows in {list(G0_N_ROWS)} and pooled max ppm in {list(G0_MAX_PPM)}",
        "observed": {"n_rows": s["n_rows"], "pooled_max_ppm": s["pooled_max_ppm"]},
        "met": bool(g0)})

    fs = s["fine_bakery"]["share_over_all"]
    p1 = fs is not None and P1_FINE_SHARE[0] <= fs <= P1_FINE_SHARE[1]
    preds.append({
        "id": "P1", "kind": "primary",
        "text": f"fine-bakery share with ppm>15 in {list(P1_FINE_SHARE)}",
        "observed": {"share_over_all": fs, "n": s["fine_bakery"]["n"],
                     "n_over_limit": s["fine_bakery"]["n_over_limit"]},
        "met": bool(p1)})

    cs = s["cereal_core"]["share_over_all"]
    p2 = cs is not None and P2_CEREAL_SHARE[0] <= cs <= P2_CEREAL_SHARE[1]
    preds.append({
        "id": "P2", "kind": "test",
        "text": f"breakfast-cereal-core share with ppm>20 in {list(P2_CEREAL_SHARE)}",
        "observed": {"share_over_all": cs, "n": s["cereal_core"]["n"],
                     "n_over_limit": s["cereal_core"]["n_over_limit"]},
        "met": bool(p2)})

    p3 = fs is not None and cs is not None and fs > cs
    preds.append({
        "id": "P3", "kind": "direction",
        "text": "fine-bakery share-over-15 > breakfast-cereal-core share-over-20",
        "observed": {"fine_share": fs, "cereal_core_share": cs}, "met": bool(p3)})

    return preds


# ---------------------------------------------------------------------------
# Data loading (SHA-256 verified; network only here).
# ---------------------------------------------------------------------------
def _fetch(url, tries=4, pause=10):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as e:  # noqa: BLE001 - retried, then raised
            last = e
            time.sleep(pause * (k + 1))
    raise last


def _resolve(resource=RESOURCE):
    meta = json.loads(_fetch(API + resource).decode("utf-8"))
    if not meta.get("success"):
        raise RuntimeError("resource_show failed for %s" % resource)
    url = meta["result"]["url"]
    if not url.startswith("https://"):
        raise RuntimeError("refusing non-https resource url: %r" % url)
    return url


def load_raw(data_dir):
    """Return the raw CFIA bytes, verified against RAW_SHA256. Re-downloads if absent/stale."""
    path = os.path.join(data_dir, RAW_NAME) if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            raw = f.read()
        if hashlib.sha256(raw).hexdigest() == RAW_SHA256:
            return raw, path, "data-volume"
    raw = _fetch(_resolve())
    got = hashlib.sha256(raw).hexdigest()
    if got != RAW_SHA256:
        raise RuntimeError("SHA-256 mismatch: got %s expected %s" % (got, RAW_SHA256))
    if path:
        try:
            os.makedirs(data_dir, exist_ok=True)
            with open(path, "wb") as f:
                f.write(raw)
        except OSError:
            pass
    return raw, path, "re-download"


def _decode(raw):
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def _find_header(rows):
    for i, r in enumerate(rows):
        if sum(1 for c in r if c.strip()) >= 5:
            return i
    raise ValueError("no header row with at least 5 named columns")


def parse_rows(raw):
    """Parse the raw CSV bytes into classified, concentration-parsed row dicts."""
    text = _decode(raw)
    table = list(csv.reader(io.StringIO(text)))
    h = _find_header(table)
    header = [c.strip() for c in table[h]]
    idx = {name: i for i, name in enumerate(header)}

    def col(*names):
        for n in names:
            if n in idx:
                return idx[n]
        for n in names:
            for name, i in idx.items():
                if name.lower().startswith(n.lower()):
                    return i
        raise KeyError(names)

    ci_prod = col("Product")
    ci_res = col("Result - Résultat", "Result")
    ci_unit = col("Unit - Unité", "Unit")
    ci_reg = col("Region - Région", "Region")
    ci_org = col("Origin")

    out = []
    for r in table[h + 1:]:
        if not any(c.strip() for c in r):
            continue
        cells = [c.strip() for c in r]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        product = cells[ci_prod]
        subcat = classify(product)
        out.append({
            "product": product,
            "region": cells[ci_reg] if ci_reg < len(cells) else "",
            "origin": cells[ci_org] if ci_org < len(cells) else "",
            "result_raw": cells[ci_res],
            "unit_raw": cells[ci_unit],
            "ppm": parse_ppm(cells[ci_res], cells[ci_unit]),
            "subcat": subcat,
            "group": group_of(subcat),
        })
    return out


def write_outputs(out_dir, rows, summary, preds, provenance):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "coumarin_eu_limits_samples.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "subcat", "product", "region", "origin", "coumarin_ppm",
                    "eu_limit", "over_limit", "unit"])
        for r in sorted(rows, key=lambda x: (x["group"], -(x["ppm"] if x["ppm"] is not None else -1))):
            limit = LIMITS.get(r["group"], "")
            over = ""
            if r["ppm"] is not None and r["group"] in LIMITS:
                over = "yes" if r["ppm"] > LIMITS[r["group"]] else "no"
            w.writerow([r["group"], r["subcat"], r["product"], r["region"], r["origin"],
                        "" if r["ppm"] is None else round(r["ppm"], 4), limit, over,
                        norm_unit(r["unit_raw"])])
    result = {
        "study": "coumarin-eu-limits", "version": VERSION,
        "eu_limits_mg_per_kg": LIMITS, "provenance": provenance,
        "summary": summary, "predictions": preds,
        "n_predictions": len(preds), "n_met": sum(1 for p in preds if p["met"]),
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    with open(os.path.join(out_dir, "grades.json"), "w", encoding="utf-8") as fh:
        json.dump({"predictions": preds}, fh, indent=2, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the coumarin EU-limits pre-registration.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)

    raw, path, source = load_raw(args.data_dir)
    rows = parse_rows(raw)
    summary = summarise(rows)
    preds = grade(summary)
    provenance = {"raw_name": RAW_NAME, "raw_sha256": RAW_SHA256,
                  "raw_bytes": len(raw), "source": source, "path": path,
                  "resource": RESOURCE}
    result = write_outputs(args.out_dir, rows, summary, preds, provenance)

    print(json.dumps({
        "version": VERSION,
        "n_rows": summary["n_rows"],
        "pooled_max_ppm": summary["pooled_max_ppm"],
        "units": summary["units"],
        "n_unrecognised_unit": summary["n_unrecognised_unit"],
        "fine_bakery": {k: summary["fine_bakery"][k]
                        for k in ("n", "n_over_limit", "share_over_all", "ppm_median", "ppm_max")},
        "cereal_core": {k: summary["cereal_core"][k]
                        for k in ("n", "n_over_limit", "share_over_all", "ppm_median", "ppm_max")},
        "oatmeal": {k: summary["oatmeal"][k]
                    for k in ("n", "n_over_limit", "share_over_all")},
        "cereal_all": {k: summary["cereal_all"][k]
                       for k in ("n", "n_over_limit", "share_over_all")},
        "predictions": [(p["id"], p["met"]) for p in preds],
        "n_met": result["n_met"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
